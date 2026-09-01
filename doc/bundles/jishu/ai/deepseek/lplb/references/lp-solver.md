---
type: reference
scope: lplb
name: lp-solver
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB CUDA LP 求解器参考——cuSolverDx 内点法实现与 minilp CUDA 内核
---

# LP 求解器参考

## 概述

LPLB 内嵌了一个完全在 GPU 上运行的线性规划求解器，使用**内点法（Interior Point Method, IPM）**求解小型 LP 问题。求解器通过 NVRTC 运行时编译（JIT），将拓扑参数（`GROUP_SIZE`、`DUP_PER_RANK`）作为编译期常量注入，生成高度特化的 CUDA 内核，结合 NVIDIA cuSolverDx（Cholesky 求解）和 cuBLASDx（矩阵乘法）设备端库，实现单 SM block 级别的 LP 求解，**全程无 CPU 回传**。

## 编译期参数

内核源码 `lplb/resources/csrc-tmpl/minilp.cu` 通过宏定义接收编译期参数：

| 宏 | 默认值 | 说明 |
|---|---|---|
| `GROUP_SIZE` | 8 | 冗余拓扑组大小（每个 NVLink 组内的 rank 数）。 |
| `DUP_PER_RANK` | 2 | 每个 rank 的冗余专家数（即每个 rank 在拓扑图中的度数）。 |
| `SM_Ver` | 900 | GPU 架构版本（如 900=Hopper SM90，800=Ampere SM80）。运行时自动检测。 |
| `BLOCK_DIM` | 128（默认模板）/ 256（Python 层实际使用） | CUDA block 线程数。 |

这些参数决定了 LP 问题的维度：

```cpp
constexpr int NC = GROUP_SIZE + GROUP_SIZE * DUP_PER_RANK;  // 约束数
constexpr int NV = GROUP_SIZE * DUP_PER_RANK * 2 + GROUP_SIZE + 2;  // 变量数
```

以 Cube8P2E 为例（GROUP_SIZE=8, DUP_PER_RANK=2）：NC=24, NV=42。

## JIT 编译流程

JIT 编译在 `compiled_solver::compile_cubin()` 中实现（csrc/plugin.cpp）：

1. **架构检测**：通过 `cudaGetDeviceProperties` 获取当前 GPU 的 `arch = major*10 + minor`。
2. **源码读取**：读取 `resources/csrc-tmpl/minilp.cu` 作为内核模板。
3. **NVRTC 编译**：使用以下选项编译为 LTO IR：
   - `-dlto --relocatable-device-code=true`：生成 LTO 可重定位设备代码。
   - `-I` mathdx include 路径、CUTLASS include 路径、CUDA include 路径。
   - `-DGROUP_SIZE=N -DDUP_PER_RANK=N -DSM_Ver=N -DBLOCK_DIM=N`：注入拓扑参数。
   - `-arch=sm_<arch>`：目标架构。
   - `-DUSE_NVSHMEM`（条件编译）：启用 NVSHMEM 支持。
4. **nvJitLink 链接**：
   - 链入离线 fatbin：`resources/mathdx/lib/libcusolverdx.fatbin`（含 cuSolverDx/cuBLASDx 设备代码）。
   - 条件链入 `libnvshmem_device.a`。
   - 链入在线编译的 LTO IR。
5. **缓存**：编译结果通过源码+选项哈希缓存到 `LPLB_CACHE_PATH` 或默认目录，避免重复编译。缓存目录结构为 `cache/<name>_<hash>/`，包含 `cubin`、`cu`（源码副本）、`options`（编译选项）。

## 内核函数

### kernel_solve

```cpp
extern "C" __global__ void kernel_solve(
    const int *workload, float *global_workload, const int *r2o,
    const int *phy2log, int n_experts_per_var, int n_experts_fixed,
    int *avail_num, float *result
#ifdef USE_NVSHMEM
    , float *workload_buf_inter, uint64_t *workload_sig_inter,
    float **workload_buf_intra,
    cuda::atomic<uint32_t, cuda::thread_scope_system> **workload_sig_intra,
    nvshmem_team_t internode_team, int self_device, int node_size
#endif
)
```

LP 求解的主内核。Grid 维度为 `{n_group, 1, 1}`（每个冗余组一个 block），Block 维度为 `{BLOCK_DIM, 1, 1}`，使用动态共享内存（大小由 `get_solve_smem_size` 内核查询）。

**执行流程：**

1. **Workload 同步与归一化**：
   - NVSHMEM 模式：跨节点 allgather（`nvshmem_putmem_signal_nbi` + signal wait）→ 节点内求和 → IPC 原子信号同步 → 节点内 allreduce。
   - 非 NVSHMEM 模式：仅归一化（除以最大值）。若未初始化 DeepEP 通信，Python 层在调用前通过 `torch.distributed.all_reduce` 聚合 workload。

2. **计算冗余专家组负载**：
   ```cpp
   dup_workload[rank][dup] = Σ_j global_workload[phy2log[...]] 
   ```
   对每个 rank 的每个冗余专家，累加其对应的组合专家组负载。

3. **构建 LP 约束矩阵 A 和右端向量 b**：
   - **负载约束**（前 GROUP_SIZE 行）：`Σ_j dup_workload[rank][j] * x[原始分配] + Σ_j dup_workload[对端rank][j] * x[副本分配] + 松弛变量 - 最大值变量 = -固定专家负载`
   - **流量守恒约束**（后 GROUP_SIZE*DUP_PER_RANK 行）：`x[原始分配] + x[副本分配] = 1`（每个冗余边的分配比例之和为 1）
   - **Big M 人工变量**：最后一列系数设为 `b[i] - Σ_j a[i][j]`，保证初始解 x=1 时 A·x = b。

4. **设置目标函数 c**：
   - 最大值变量系数为 1（最小化最大负载）。
   - 人工变量系数为 1000（Big M 惩罚）。
   - 其余变量系数为 0。

5. **内点法迭代（5 步）**：
   ```cpp
   for step in 0..4:
     ax2 = A * x²           // 对角加权矩阵
     ax2a = ax2 @ A^T       // 正规方程矩阵 (NC×NC)
     ax2c = ax2 @ c         // 右端向量
     gaussian_elimination_solve<NC>(ax2a, ax2c)  // Cholesky 求解
     r = ax2c @ A           // 对偶残差方向
     d = x * (c - r)        // 原始-对偶步长方向
     alpha = 0.999 / max(d) // 步长
     x *= 1 - alpha * d     // 更新解
   ```

6. **可行性检验与输出**：
   - 收敛判据：`d_max < 0.1 && x[人工变量] < 1e-4 && max_residual < 0.05`
   - 可行：输出 x 的前 GROUP_SIZE*DUP_PER_RANK 个分量到 result（原始分配比例）。
   - 不可行：输出 0.5（均匀分配），`avail_num` 不增加。

### gaussian_elimination_solve

```cpp
template <int N>
__device__ void gaussian_elimination_solve(float a[N][N], float b[N])
```

使用 cuSolverDx 的 Cholesky 分解（`cusolverdx::function::posv`）求解正定线性方程组 Ax=b。配置为行主序、下三角填充、Block 级执行、BLOCK_DIM 线程。

### matmulNT / matmulNN

```cpp
template <int M, int N, int K> __device__ void matmulNT(float *a, float *b, float *c)  // C = A * B^T
template <int M, int N, int K> __device__ void matmulNN(float *a, float *b, float *c)  // C = A * B
```

使用 cuBLASDx 执行设备端矩阵乘法。`matmulNT` 用于计算 A·X²·A^T（A 行主序 × A^T 列主序），`matmulNN` 用于向量-矩阵乘法。

### kernel_count_idx

```cpp
extern "C" __global__ void kernel_count_idx(
    const long *idx, const int n_elements, const int n_experts, int *counts)
```

GPU 端专家索引计数内核。Grid 维度 `{n_sms, 1, 1}`，每个 SM 处理一段 `[start, end)` 范围的 idx 元素，使用共享内存 `atomicAdd` 计数，同步后写入全局内存，最后通过 grid-wide sync 和 warp 级前缀和累加各 SM 的计数结果。

共享内存布局：前 16 个 int 为偏移区（允许 `smem_counts[-1]` 安全访问），后续为 `n_experts` 个计数槽位。

### kernel_map_idx

```cpp
extern "C" __global__ void kernel_map_idx(
    const long *mapping_idx, const float *o_weight,
    const int *local_workload_by_sm, const int *o2r,
    const int *phy2log, const int n_elements, const int n_group,
    const int n_combined_experts, const int n_local_experts,
    long *mapping_idx_out)
```

加权哈希路由内核。Grid 维度 `{n_sms, 1, 1}`。

**共享内存布局（5 * n_logical_experts 个 int）：**
- `smem_total_count`：每个逻辑专家的总 token 数。
- `smem_expected_count`：期望分配到原始专家的 token 数阈值（= o_weight × total_count）。
- `smem_current_count`：当前已分配计数（每个 SM 维护自己的前缀）。
- `smem_log2r`：每个逻辑专家的两个物理位置槽位（原始和副本）。

**路由算法：**
1. 初始化阶段：从 `local_workload_by_sm` 加载总计数和各 SM 前缀计数，构建 log2r 映射。
2. 主循环：对每个 idx，通过 `atomicAdd` 递增当前计数，使用 `(computed_count * 499 + 41) % total_count` 哈希决定路由：哈希值 < expected_count 则选原始专家，否则选副本。-1 保持 -1。

### get_solve_smem_size

```cpp
extern "C" __global__ void get_solve_smem_size(int *size_output)
```

辅助内核，返回 `sizeof(smem_variables)` 以确定 `kernel_solve` 所需的动态共享内存大小。在 `prepare_module()` 中启动一次获取 `smem_size`。

## 共享内存结构体

```cpp
struct smem_variables {
  float dup_workload[GROUP_SIZE][DUP_PER_RANK];  // 冗余专家组负载
  float b[NC];                                    // 约束右端向量
  float a[NC][NV];                                // 约束矩阵
  float c[NV];                                    // 目标函数系数
  float ax2[NC][NV];                              // A * diag(x²)
  float ax2a[NC][NC];                             // A * diag(x²) * A^T
  float x[NV];                                    // 当前解向量
  float ax2c[NC];                                 // A * diag(x²) * c
  float r[NV];                                    // 残差/步长方向
  float d[NV];                                    // 步长
  float alpha;                                    // 步长系数
  bool avail_flag;                                // 可行标志
};
```

所有 LP 求解的中间结果完全在共享内存中，不访问全局内存（除了初始加载和最终结果写回）。

## C++ 绑定层（compiled_solver）

`compiled_solver` 结构体（csrc/plugin.cpp）通过 Pybind11 暴露为 Python 类 `CompiledSolver`：

| 方法 | 启动方式 | 说明 |
|---|---|---|
| `solve` | `cudaLaunchCooperativeKernel` / `nvshmemx_collective_launch` | 启动 kernel_solve，grid={n_group,1,1} |
| `count_idx` | `cudaLaunchCooperativeKernel` | 启动 kernel_count_idx，grid={n_sms,1,1} |
| `map_idx` | `cudaLaunchKernel` | 启动 kernel_map_idx，grid={n_sms,1,1} |
| `init_comm` | — | NVSHMEM 条件编译，分配 internode/intranode 缓冲区，通过 CUDA IPC 在节点内共享内存 |

### NVSHMEM 通信初始化（init_comm）

当使用 DeepEP 且启用 NVSHMEM 时：
1. 可选初始化 NVSHMEM（`nvshmemx_init_attr`）。
2. 同步 DeepEP 的 NVSHMEM 全局符号到当前编译模块（`sync_current_to_module`：通过 `dlopen` 加载 `libdeep_ep.so`，`dlsym` 获取符号，`cudaMemcpyDeviceToDevice` 复制）。
3. 根据 `nvshmem_multiplane` 选择使用 `NVSHMEM_TEAM_WORLD` 或 `deep_ep::internode::cpu_rdma_team`。
4. 分配 internode 缓冲区（nvshmem_align）和 intranode 缓冲区（cudaMalloc + CUDA IPC 共享）。
5. 通过 `cudaIpcGetMemHandle` + `ProcessGroup::_allgather_base` 在节点内交换 IPC 句柄，`cudaIpcOpenMemHandle` 打开对端内存。

## 数学依赖

| 库 | 用途 | 链接方式 |
|---|---|---|
| cuSolverDx | Cholesky 求解（`posv`），用于内点法正规方程 | 离线 fatbin（`libcusolverdx.fatbin`），nvJitLink 链入 |
| cuBLASDx | 设备端矩阵乘法（`MM`），行主序/列主序 | 同上，包含在 mathdx 包中 |
| CUTLASS | cuSolverDx/cuBLASDx 的底层依赖 | 头文件（`resources/mathdx/external/cutlass/include`） |
| NVRTC | 运行时 CUDA C++ 编译 | 系统 CUDA 工具链 |
| nvJitLink | LTO IR 链接 | 系统 CUDA 工具链 |
| NVSHMEM | 跨节点/节点内 one-sided 通信（可选） | 系统安装，`-DUSE_NVSHMEM` 条件编译 |
