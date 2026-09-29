---
type: concept
scope: lplb
name: load-balancing-problem
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: MoE 专家负载均衡问题的数学形式化——从热专家现象到 LP 模型
---

# MoE 专家负载均衡问题

## 问题背景

在 Mixture-of-Experts（MoE）模型的专家并行（Expert Parallelism, EP）训练中，每个 GPU 只存储部分专家。Router 网络为每个 token 选择 top-k 个专家进行计算，token 通过 all-to-all 通信被发送到对应专家所在的 GPU。

由于以下原因，专家间的负载分布天然不均匀：

1. **Router 动态性**：Router 的决策依赖于当前 batch 的数据分布，不同 batch 中各专家的受欢迎程度不同。
2. **数据偏斜**：训练数据中存在模式聚集，某些语义概念对应特定专家，导致这些专家长期过载。
3. **Top-k 路由的随机性**：即使在均衡的 router 设计下，小 batch 的随机波动也会造成 per-batch 负载不均。

负载不均的直接后果是 **GPU 利用率下降**：grouped GEMM 的计算时间由负载最重的专家决定，all-to-all 通信时间由通信量最大的 GPU 决定，其他 GPU 空等。

## 形式化定义

### 基本符号

| 符号 | 含义 |
|---|---|
| $P$ | EP 并行组中的 GPU（rank）总数 |
| $E$ | 逻辑专家总数 |
| $E_p$ | 每个 rank 上的本地专家数（$E = P \times E_p$） |
| $w_e$ | 专家 $e$ 在当前 batch 中的负载（分配到的 token 数） |
| $x_{i,j}$ | 从 rank $i$ 分流到其第 $j$ 个冗余副本的 token 比例 |

### 问题目标

最小化所有 rank 上的最大总负载：

$$\min_{x} \max_{p \in [0,P)} L_p(x)$$

其中 $L_p(x)$ 是 rank $p$ 在分配比例 $x$ 下的总负载。

### 负载构成

每个 rank 的负载由两部分组成：

1. **固定负载**：不参与分流的专家负载，直接累加到 rank 总负载。
2. **可分流负载**：被选中的"热专家"可以将部分 token 分流到其在邻接 rank 上的副本。

设 rank $p$ 上有 $k$ 个可分流专家组（每组含 `num_redundants` 个冗余槽位），第 $j$ 个冗余边连接 rank $p$ 和 rank $r2o[p][j]$，该边上专家组的原始负载为 $W_{p,j}$：

- 留在原始专家上的负载：$x_{p,j} \cdot W_{p,j}$
- 分流到副本的负载：$(1 - x_{p,j}) \cdot W_{p,j}$（由对端 rank 接收）
- 从对端分流过来的负载：$(1 - x_{r2o[p][j],j}) \cdot W_{r2o[p][j],j}$（r2o[p][j] 是对端 rank，其第 j 个冗余是 p 的原始专家的副本）

因此 rank $p$ 的总负载为：

$$L_p = F_p + \sum_j x_{p,j} \cdot W_{p,j} + \sum_j (1 - x_{r2o[p][j],j}) \cdot W_{r2o[p][j],j}$$

其中 $F_p$ 是 rank $p$ 上固定专家的负载。

## LP 模型

LPLB 将上述 min-max 问题转化为线性规划问题。引入最大值变量 $M$，目标变为最小化 $M$，约束为每个 rank 的总负载不超过 $M$。

### 变量

以 Cube8P2E 为例（GROUP_SIZE=8, DUP_PER_RANK=2），每个冗余组独立求解一个 LP：

| 变量 | 数量 | 含义 |
|---|---|---|
| $x_j$（原始分配） | GROUP_SIZE × DUP_PER_RANK | 每个冗余边上留在原始专家的 token 比例 |
| $x'_j$（副本分配） | GROUP_SIZE × DUP_PER_RANK | 每个冗余边分配到副本的比例（$x_j + x'_j = 1$） |
| $s_p$（松弛变量） | GROUP_SIZE | 每个 rank 的松弛变量 |
| $M$（最大值） | 1 | 所有 rank 的最大负载 |
| $a$（人工变量） | 1 | Big M 法人工变量 |

总计 $NV = 2 \times G \times D + G + 2$ 个变量。

### 约束

1. **负载约束**（GROUP_SIZE 个）：每个 rank 的总负载 + 松弛变量 - 最大值 = -固定负载。
   $$\sum_j W_{p,j} \cdot x_{p,j} + \sum_j W_{r2o[p][j],j} \cdot x'_{p,j} + s_p - M = -F_p$$

2. **流量守恒约束**（GROUP_SIZE × DUP_PER_RANK 个）：每个冗余边的原始和副本分配之和为 1。
   $$x_j + x'_j = 1$$

3. **非负约束**：所有 $x_j, x'_j, s_p \geq 0$（内点法天然处理）。

总计 $NC = G + G \times D$ 个约束。

### 目标函数

$$\min c^T x = M + 1000 \cdot a$$

- $M$ 的系数为 1（最小化最大负载）。
- 人工变量 $a$ 的系数为 1000（Big M 惩罚，确保初始可行解趋向人工变量为 0）。
- 其余变量系数为 0。

### Big M 初始解

LPLB 使用 Big M 法构造初始可行解：添加一列人工变量使得 $x = \vec{1}$ 时 $A\vec{1} = b$。内点法从 $x = \vec{1}$ 开始迭代，若收敛后人工变量接近 0（$x[NV-1] < 10^{-4}$）则判定可行。

## 为什么在 GPU 上求解

传统方案将负载统计传回 CPU，用 SciPy/HiGHS 等求解器求解 LP，再将结果传回 GPU。这带来：

1. **PCIe 传输开销**：每个 batch 都要做 CPU↔GPU 数据传输。
2. **CPU 求解延迟**：通用 LP 求解器对小规模问题启动开销大。
3. **同步阻塞**：GPU 需要等待 CPU 求解完成才能继续路由。

LPLB 的 GPU 端求解器：

- 利用编译期特化，LP 规模为编译期常量（如 Cube8P2E 的 24×42），避免动态内存分配。
- 所有矩阵运算（矩阵乘、Cholesky 分解）通过 cuSolverDx/cuBLASDx 在共享内存中完成。
- 单次求解约 100µs（节点内），与 dispatch kernel 的延迟在同一量级。
- 支持 NVSHMEM 直接在 GPU 上完成跨节点 workload 聚合，无需 CPU 参与。

## 与 EPLB 的分工

| 维度 | EPLB（静态层） | LPLB（动态层） |
|---|---|---|
| 时间尺度 | 每 N 步（慢） | 每个 batch（快） |
| 决策内容 | 哪些专家需要复制、如何放置 | 每个 token 路由到原始还是副本 |
| 优化目标 | 复制策略最小化最大期望负载 | 分配比例最小化当前 batch 最大负载 |
| 算法 | 贪心装箱 + 贪心复制 | 内点法 LP 求解 |
| 执行位置 | CPU（Python） | GPU（CUDA kernel） |

EPLB 在慢时间尺度调整专家布局（重排+复制），LPLB 在快时间尺度微调 token 分配。两者配合实现分层负载均衡。
