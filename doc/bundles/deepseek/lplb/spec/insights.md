---
type: spec
scope: lplb
name: insights
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 深度洞察——从源码中提炼的设计决策、实现机制与关键约束
---

# LPLB 深度洞察

## 1. 核心设计理念：静态拓扑 + 动态求解

LPLB 解决 MoE 训练中专家负载不均衡问题的核心思路是**两层分离**：

- **静态层（拓扑）**：通过 `redundant_to_original`（r2o）矩阵预定义冗余专家的复制拓扑。每个冗余专家被约束为"恰好共享于两个 rank 之间"（`r2o[i][j]` 表示 rank i 的第 j 个冗余专家是 rank `r2o[i][j]` 的原始专家的副本），从而在 GPU 间形成图结构边。这种设计保证了 LP 问题的规模固定且可在编译期确定。
- **动态层（求解）**：每个 batch 到来时，实时统计各专家的 token 负载，在 GPU 上用内点法（IPM）求解 LP，得到最优的 token 分配比例，再通过加权哈希将 token 路由到原始专家或其副本。

## 2. 编译期特化的 CUDA LP 求解器

LPLB 最显著的工程特征是**运行时 JIT 编译 CUDA 内核**：

- `compiled_solver` 构造时，NVRTC 动态编译 `minilp.cu` 模板，将 `GROUP_SIZE`、`DUP_PER_RANK`、`BLOCK_DIM`、`SM_Ver` 作为宏注入，生成针对当前拓扑和 GPU 架构高度特化的 cubin。
- 编译结果通过源码哈希缓存到 `LPLB_CACHE_PATH`（或默认缓存目录），避免重复编译。
- 在线编译的 LTO IR 与离线 fatbin（`libcusolverdx.fatbin`）通过 nvJitLink 链接，cuSolverDx 的 Cholesky 求解（`posv`）和 cuBLASDx 的矩阵乘法直接在设备端执行，**全程无需 CPU 回传**。

这意味着 LP 的约束矩阵维度 `NC = GROUP_SIZE + GROUP_SIZE*DUP_PER_RANK` 和变量维度 `NV = GROUP_SIZE*DUP_PER_RANK*2 + GROUP_SIZE + 2` 在编译期即为常量，共享内存布局 `smem_variables` 也完全静态确定，单个 SM block 即可完成一次 LP 求解。

## 3. LP 问题建模

以 Cube8P2E（GROUP_SIZE=8, DUP_PER_RANK=2）为例：

- **约束数 NC = 24**：8 个负载均衡约束（每个 rank 的总负载 ≤ 最大值变量）+ 16 个流量守恒约束（每个冗余边的分配比例在 [0,1]，原始+副本之和=1）。
- **变量数 NV = 42**：16 个原始分配比例 + 16 个副本分配比例 + 8 个松弛变量 + 1 个最大值变量 + 1 个人工变量（Big M 法，M=1000）。
- **目标函数**：最小化最大值变量（系数 1），人工变量惩罚项（系数 1000）。
- **求解算法**：5 步内点法迭代，每步涉及矩阵乘法（cuBLASDx）和 Cholesky 求解（cuSolverDx），收敛判据为 `d_max < 0.1 && x[人工变量] < 1e-4 && max_residual < 0.05`。

当 LP 不可行时，退化为均匀分配（所有比例设为 0.5）。

## 4. 三层通信架构

| 模式 | 通信方式 | 适用场景 |
|---|---|---|
| 无 DeepEP | `torch.distributed.all_reduce` | 单节点或简单部署 |
| DeepEP + NVSHMEM（节点内） | CUDA IPC + `cuda::atomic` signal | 节点内 NVLink 高速通信 |
| DeepEP + NVSHMEM（跨节点） | `nvshmem_putmem_signal_nbi` + signal wait | 多节点 RDMA 通信 |

NVSHMEM 模式下，workload 同步分四步：(1) 跨节点 allgather（put+signal），(2) 节点内求和，(3) IPC 原子信号同步，(4) 节点内 allreduce。这比 `torch.distributed` 的默认 allreduce 显著降低延迟。

## 5. EPLB 层次化重平衡

`lplb/eplb.py` 实现了 DeepSeek EPLB 算法的嵌入式版本，提供静态的专家重排序和复制规划：

1. **Step 1**：`balanced_packing` 将 expert groups 按 token 负载打包到节点（贪心装箱）。
2. **Step 2**：`replicate_experts` 在节点内逐个复制负载/副本数比值最大的专家（贪心复制）。
3. **Step 3**：`balanced_packing` 将物理专家打包到 GPU。

当 `num_groups % num_nodes != 0` 时退化为全局策略（单节点等效）。EPLB 负责"哪些专家应该被复制"，LPLB 负责"每个 batch 的 token 如何在原始和副本间分配"。

## 6. Token 路由机制（加权哈希）

`kernel_map_idx` 使用**确定性加权哈希**进行 token 路由：

1. 共享内存中构建 `smem_total_count`（总负载）、`smem_expected_count`（期望分配到原始专家的 token 数 = o_weight × total_count）、`smem_current_count`（当前已分配计数）。
2. 每个 token 到来时，`atomicAdd` 递增当前计数，通过 `(computed_count * 499 + 41) % smem_total_count[idx]` 哈希决定路由：哈希值 < 期望值则路由到原始专家，否则路由到副本。
3. 乘数 499 和偏移 41 是经验选择的哈希参数，提供近似均匀分布。

这种设计保证了路由决策完全在 GPU 上完成，无需排序或前缀和扫描，且每个 SM 独立处理分片数据。

## 7. 拓扑结构与副本组

| 拓扑 | r2o 形状 | 约束 | 典型场景 |
|---|---|---|---|
| Cube | (8, 2) | 每 rank 2 冗余，立方体对角线 | 8-GPU 节点内 EP |
| Ring | (8, 1) | 每 rank 1 冗余，环形连接 | 简单链式拓扑 |
| Hypercube | (16, 2) | 每 rank 2 冗余，超立方体无对角 | 16-GPU 跨节点 EP |
| Torus 2D | (m×n, 2) | 每 rank 2 冗余，二维环面 | 全局均衡，含跨节点边 |

拓扑约束：r2o 必须满足对称结构——每个冗余边恰好连接两个 rank，且每个 rank 的冗余数量相同。`o2r` 是 r2o 的 argsort，提供从"对端 rank 的原始视角"到"本端冗余索引"的反向映射。

## 8. 关键性能特征

- **求解耗时**：节点内约 100µs，跨节点更长；对小 batch 可能不可忽略。
- **均衡效果**：测试中 max/mean 负载比控制在 1.01~1.10 之间（随拓扑和配置变化）。
- **编译开销**：首次运行触发 NVRTC 编译，后续通过哈希缓存命中。
- **限制**：仅平衡 token 数量，不考虑 grouped GEMM 的非线性时间开销；极端全局不均衡时可能不如纯 EPLB。

## 9. 与 DeepEP/DeepGEMM 的协作关系

- **DeepEP**（[/deepseek/deep-ep/](/deepseek/deep-ep/)）：提供高效的 EP 通信原语（all-to-all、dispatch/combine），LPLB 通过 `init_from_deep_ep(buffer)` 获取 NVSHMEM team 和低延迟模式配置，复用 DeepEP 的通信缓冲区。
- **DeepGEMM**（[/deepseek/deep-gemm/](/deepseek/deep-gemm/)）：提供 MoE 中的 grouped GEMM 计算内核，LPLB 的负载均衡直接影响 DeepGEMM 的计算效率——均衡的专家负载意味着更短的 grouped GEMM 尾延迟。
