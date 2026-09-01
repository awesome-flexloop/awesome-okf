---
type: concept
scope: lplb
name: lp-solver-design
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB CUDA LP 求解器设计——基于 cuSolverDx 的 GPU 端内点法实现
---

# LP 求解器设计

## 设计目标

LPLB 的 LP 求解器满足以下约束：

1. **零 CPU 回传**：从负载统计到分配比例输出，全程在 GPU 上完成。
2. **极低延迟**：单次求解 ~100µs，不成为训练瓶颈。
3. **小规模高频**：每个 EP 冗余组独立求解（约束数 8~24，变量数 18~42），每步训练都需求解。
4. **多 GPU 协同**：支持跨节点 workload 聚合，NVSHMEM 通信与计算融合。

## 内点法选择

选择内点法（Interior Point Method）而非单纯形法：

1. **固定迭代次数**：内点法迭代次数可预设（LPLB 使用 5 步），单纯形法迭代次数不可预测。
2. **GPU 友好**：每步核心操作是矩阵乘法和 Cholesky 分解，GPU 上高效实现。
3. **共享内存适配**：24×42 规模的 LP 完全放入 SM 共享内存，无需全局内存访问。

### 迭代步骤

对 LP 问题 $\min\{c^T x : Ax = b, x \geq 0\}$，每步：

1. 计算 $X^2 = \text{diag}(x^2)$（逐元素平方）
2. 形成正规方程 $A X^2 A^T \cdot \Delta y = A X^2 c$
3. Cholesky 求解 $\Delta y$（cuSolverDx POSV）
4. 计算方向 $\Delta x = X^2 (c - A^T \Delta y)$（cuBLASDx 矩阵乘）
5. 更新 $x \leftarrow x \cdot (1 - \alpha \Delta x)$，$\alpha = 0.999 / \max(\Delta x)$

## JIT 编译架构

LP 维度（NC、NV）由拓扑参数 GROUP_SIZE 和 DUP_PER_RANK 决定，而 cuSolverDx/cuBLASDx 的矩阵维度必须是编译期常量。因此 LPLB 采用 NVRTC 运行时编译：

```
minilp.cu（模板，含宏占位符）
    │ NVRTC: -DGROUP_SIZE=N -DDUP_PER_RANK=N -DSM_Ver=N -DBLOCK_DIM=N
    ▼
LTO IR（在线编译）
    │ nvJitLink 链接
    ├── libcusolverdx.fatbin（离线 cuSolverDx/cuBLASDx 设备代码）
    ├── libnvshmem_device.a（可选）
    └── LTO IR（在线）
    ▼
cubin → cudaLibraryLoadFromFile → 获取 kernel 句柄 → 启动
```

编译结果通过源码+选项的哈希值缓存到磁盘（`LPLB_CACHE_PATH` 或默认目录），相同配置直接加载。

## cuSolverDx/cuBLASDx 集成

### POSV（Cholesky 求解）

```cpp
cusolverdx::Size<N>() + Function<posv>() +    // N = NC，编译期常量
Arrangement<row_major, row_major>() +
SM<SM_Ver>() + Block() + FillMode<lower>() +
BlockDim<BLOCK_DIM>()
```

用于求解正规方程 $A X^2 A^T \cdot \Delta y = A X^2 c$。内点法中 $X^2$ 正定保证 $A X^2 A^T$ 正定。

### 矩阵乘法

- **matmulNT**（C = A × B^T）：A 行主序、B 列主序，计算 $A X^2 A^T$ 和 $A X^2 c$。
- **matmulNN**（C = A × B）：行主序，计算 $r = \Delta y^T A$。

均使用 cuBLASDx Block 级 GEMM，BLOCK_DIM 线程协作。

## 共享内存布局

所有 LP 数据在 `smem_variables` 结构体中，完全驻留共享内存：

```
dup_workload[G][D]   // 冗余专家组负载
b[NC]                // 约束右端向量
a[NC][NV]            // 约束矩阵（最大占用）
c[NV]                // 目标函数系数
ax2[NC][NV]          // A * diag(x²)
ax2a[NC][NC]         // 正规方程矩阵
x[NV]                // 当前解
ax2c[NC]             // A * diag(x²) * c
r[NV], d[NV]         // 残差、步长方向
alpha, avail_flag    // 步长系数、可行标志
```

以 Cube8P2E（NC=24, NV=42）为例，共享内存约 5KB，远小于 Hopper SM 的 228KB 共享内存容量。

## Workload 同步

### 非 NVSHMEM 模式
Python 层通过 `torch.distributed.all_reduce` 聚合 workload，kernel 内仅做归一化（除以最大值缩放至 [0,1]）。

### NVSHMEM 模式（DeepEP 集成）
同步完全在 kernel_solve 内完成：

1. **跨节点**：Block 0 将 workload 写入 NVSHMEM symmetric buffer → `nvshmem_putmem_signal_nbi` 向所有远程节点 put+signal → `nvshmem_signal_wait_until` 等待 → 节点内求和。
2. **节点内**：`cuda::atomic<uint32_t>::fetch_add` 通过 CUDA IPC 共享内存发送信号 → 自旋等待 → 对节点内所有 GPU 的 buffer 求和。

分层同步减少跨节点 RDMA 次数，节点内使用 IPC + 原子，延迟远低于 `torch.distributed`。

## 收敛判据

5 步迭代后同时满足：
1. `d_max < 0.1`：步长方向最大分量足够小（近 KKT 条件）
2. `x[人工变量] < 1e-4`：Big M 人工变量接近 0
3. `max_residual < 0.05`：约束残差 $\|Ax - b\|_\infty < 0.05$

可行时输出 x 前 G×D 个分量（原始分配比例）；不可行输出 0.5（均匀分配），`avail_counter` 不增加。

## Token 路由（kernel_map_idx）

LP 得到比例后，加权哈希路由：

1. 共享内存加载：总 token 数、期望阈值（o_weight × total）、SM 前缀计数、log2r 映射。
2. 每个 SM 独立分片处理 token，使用 `split_and_align` 对齐。
3. 原子计数 + 哈希决策：
   ```cpp
   computed = atomicAdd(&smem_current_count[idx], 1);
   hash = (computed * 499 + 41) % smem_total_count[idx];
   idx_out = (hash < expected) ? original : replica;
   ```
4. -1 保持映射为 -1。

哈希参数 499 和 41 提供近似均匀分布，实际分配误差 < 5%。

## 性能特征

- **延迟**：节点内约 100µs，跨节点因 NVSHMEM 通信稍长。
- **并行度**：n_group 个 block 在不同 SM 上并行求解。
- **编译开销**：首次 JIT 编译数秒，后续缓存命中。
- **精度**：float32，5 步迭代，小规模 LP 通常收敛。

详见 LP 求解器 API 参考。
