---
type: reference
scope: lplb
name: topology
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 拓扑配置参考——Cube/Hypercube/Ring/Torus 拓扑与冗余副本组
---

# 拓扑配置参考

## 概述

LPLB 通过 `redundant_to_original`（r2o）矩阵定义冗余专家的拓扑结构。该矩阵形状为 `[group_size, num_redundants]`，其中 `r2o[i][j]` 表示第 i 个 rank 上的第 j 个冗余专家是 rank `r2o[i][j]` 上某个原始专家的副本。这个矩阵在 GPU 之间定义了一个图结构：每条边连接两个 rank，表示这两个 rank 之间可以互相分流 token。

### 拓扑约束

r2o 矩阵必须满足以下结构约束：

1. **均匀冗余**：每个 rank 拥有相同数量的冗余专家（`num_redundants`），即每列长度相同。
2. **边对称**：第 i 个 rank 的第 j 个冗余是 rank r 的副本，则 rank r 上必须有一个冗余是 rank i 的副本。这保证了冗余边是双向的。
3. **i-th 约定**：所有 rank 的第 i 个冗余专家必须是另一个 rank 上第 i 个专家的副本。这确保了冗余结构在 LP 中的规律性，使得每个冗余边恰好被两个 rank 各引用一次。
4. **组合冗余**：实际冗余专家数可以是 `num_redundants` 的倍数（`combined_redundant_experts` 组），允许多个冗余专家被分组进行批量权重分配。

### 拓扑规模关系

```
n_routed_experts = n_logical_routed_experts + n_redundants_per_rank * ep_size
n_local_routed_experts = n_routed_experts // ep_size
n_local_logical_routed_experts = n_logical_routed_experts // ep_size
combined_redundant_experts = (n_local_routed_experts - n_local_logical_routed_experts) // num_redundants
n_group = ep_size // group_size
```

LP 问题的编译期维度：
- 约束数 `NC = group_size + group_size * num_redundants`
- 变量数 `NV = group_size * num_redundants * 2 + group_size + 2`

## 内置拓扑

LPLB 测试用例中提供了四种预定义拓扑，位于 tests/utils.py。

### Cube（立方体拓扑）

**常量**：`CUBE_8P2E`
**形状**：(8, 2) — 8 个 rank，每个 rank 2 个冗余专家
**适用场景**：单节点 8 GPU（NVLink 全互联），EP 子组内负载均衡

```python
CUBE_8P2E = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T
# 结果（转置后）：
# r2o[0] = [3, 6]  — rank 0 的冗余是 rank 3 和 rank 6 的副本
# r2o[1] = [0, 7]  — rank 1 的冗余是 rank 0 和 rank 7 的副本
# r2o[2] = [1, 4]  — rank 2 的冗余是 rank 1 和 rank 4 的副本
# r2o[3] = [2, 5]  — rank 3 的冗余是 rank 2 和 rank 5 的副本
# r2o[4] = [7, 0]  — rank 4 的冗余是 rank 7 和 rank 0 的副本
# r2o[5] = [4, 1]  — rank 5 的冗余是 rank 4 和 rank 1 的副本
# r2o[6] = [5, 2]  — rank 6 的冗余是 rank 5 和 rank 2 的副本
# r2o[7] = [6, 3]  — rank 7 的冗余是 rank 6 和 rank 3 的副本
```

**拓扑图**：8 个 rank 构成立方体，第一个冗余连接到立方体同一面的对角邻居（步长 3），第二个冗余连接到立方体另一面的对角邻居（步长 6，即反向步长 2 模 8）。形成 3-正则图中的立方体结构，包含 NVLink 域内的直接连接和跨立方体对角线。

**特点**：
- 每个 GPU 至少 2 个专家槽位用于冗余。
- 不牺牲跨节点通信效率（冗余边在节点内闭合）。
- 测试中 max/mean 负载比控制在 1.07~1.10。

### Ring（环形拓扑）

**常量**：`RING_8P`
**形状**：(8, 1) — 8 个 rank，每个 rank 1 个冗余专家
**适用场景**：简单链式拓扑，每个 rank 仅与下一个邻居形成冗余边

```python
RING_8P = torch.tensor([
    [1, 2, 3, 4, 5, 6, 7, 0],
]).T
# r2o[i] = [(i+1) % 8]  — 每个 rank 的冗余是下一个 rank 的副本
```

**特点**：
- 最基础的拓扑，每个 rank 仅有 1 条冗余边。
- DUP_PER_RANK=1，LP 规模最小（NC=16, NV=26）。
- 适合验证 LP 求解器正确性。

### Hypercube（超立方体拓扑）

**常量**：`HYPERCUBE_16P2E`
**形状**：(16, 2) — 16 个 rank，每个 rank 2 个冗余专家
**适用场景**：16 GPU 跨节点 EP，排除对角线边的超立方体结构

```python
HYPERCUBE_16P2E = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6, 11, 8, 9, 10, 15, 12, 13, 14],
    [12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
]).T
```

**结构**：16 个 rank 分为两个 8-rank 组（0-7 和 8-15）。
- 第一个冗余（列 0）：组内连接（同 Cube 模式的前 8 个）+ 跨组映射（8-15 映射到 11-14）。
- 第二个冗余（列 1）：跨组连接（0-7 映射到 12-15 和 0-3，8-15 映射到 4-11）。

**特点**：
- 类似 Cube 但排除对角线边。
- 适合 16 GPU 的专家并行。
- 测试中 max/mean 负载比可达 1.03（最优）。

### Torus（二维环面拓扑）

**函数**：`torus_2d(m: int, n: int)` → `torch.Tensor` 形状 (m*n, 2)
**适用场景**：全局负载均衡，每个 rank 在同一节点有一个邻居冗余、在邻接节点有另一个邻居冗余

```python
def torus_2d(m: int, n: int) -> torch.Tensor:
    return torch.tensor(
        [[(i + 1) % m * n + j, i * n + (j + 1) % n] for i in range(m) for j in range(n)]
    )
```

**结构**：m×n 个 rank 排列为二维网格，每个 rank (i,j) 有两个冗余邻居：
- 列 0：`((i+1) % m, j)` — 行方向的下一个邻居（跨节点边）
- 列 1：`(i, (j+1) % n)` — 列方向的下一个邻居（节点内边）

测试中使用 `torus_2d(8, 4)` 生成 32 个 rank 的拓扑。

**特点**：
- 每个 GPU 至少 2 个专家槽位。
- 有效实现全局均衡，但因包含跨节点通信边，效率略低于 Cube。
- 测试中 max/mean 负载比可达 1.01（最均衡）。

## 副本组（Replica Groups）

在 LPLB 的 LP 模型中，冗余专家按"副本组"组织：

### 物理专家布局

每个 rank 上的物理专家按以下顺序排列：

```
[n_local_routed_experts 个物理专家]
├── [combined_redundant_experts * num_redundants 个原始冗余专家槽位]
│   └── 每组 combined_redundant_experts 个专家，共 num_redundants 组
│       这些是"主动分流"的候选专家
├── [n_local_logical_routed_experts - combined_redundant_experts * num_redundants 个固定专家]
│   └── 这些专家不参与 LP 分流，其负载直接计入 rank 总负载
└── [combined_redundant_experts * num_redundants 个副本冗余专家槽位]
    └── 从对端 rank 复制过来的专家，接收从原始专家分流来的 token
```

### phy2log 映射构建

`update_redundancy_mapping()` 方法构建物理到逻辑的映射：

1. **无重排序**（workload=None）：`phy2log = arange(n_logical_routed_experts)`，逻辑专家顺序不变。
2. **有重排序**（workload≠None）：调用 EPLB `rebalance_experts` 进行层次化重平衡，然后按负载降序排列每个设备上的专家。
3. 选取前 `combined_redundant_experts * num_redundants` 个专家作为冗余候选。
4. 通过 `r2o` 映射在对端 rank 上创建冗余副本。
5. 最终 `phy2log` 长度为 `n_routed_experts`，`assert phy2log.shape[0] == n_routed_experts`。

### log2phy 与 logcnt

- `logcnt[i]`：逻辑专家 i 的副本数（当前实现中 max_logcnt 固定为 2，即每个专家最多一个副本）。
- `log2phy[i]`：逻辑专家 i 的物理位置列表，`[原始物理位置, 副本物理位置]`，无副本时填充 -1。
- 构建时遍历 phy2log 的转置，确保原始专家排在副本之前。

## 自定义拓扑

用户可以通过修改 r2o 矩阵探索自定义拓扑。自定义拓扑需满足：

1. **对称约束**：若 `r2o[i][j] = r`，则存在某个 k 使得 `r2o[r][k] = i`。
2. **度一致**：所有 rank 的冗余数量相同（列数一致）。
3. **i-th 约定**：第 j 列的冗余连接应构成闭合的置换或对合（involution）。即若 `r2o[:, j]` 定义了一个映射 f，则 f(f(i)) 应能正确闭合。
4. **LP 可解**：拓扑应确保 LP 约束矩阵的秩充分，内点法能在 5 步迭代内收敛。

### 拓扑选择建议

| 场景 | 推荐拓扑 | 原因 |
|---|---|---|
| 单节点 8 GPU | Cube8P2E | NVLink 域内闭合，无跨节点开销 |
| 双节点 16 GPU（同构） | Hypercube16P2E | 跨节点但无对角边，均衡性好 |
| 多节点大规模 EP | Torus 2D | 包含节点内/跨节点边，全局均衡 |
| 调试/最小化验证 | Ring8P | LP 规模最小，便于验证正确性 |

## 与 DeepEP 通信域的关系

拓扑的 `group_size` 应与 DeepEP 的通信域配置匹配：

- **NVLink 域（intranode）**：`group_size` 通常设为节点内 GPU 数（如 8），此域内通过 NVLink/CUDA IPC 高速通信。
- **RDMA 域（internode）**：跨节点时 `n_group = ep_size // group_size > 1`，需要 NVSHMEM 进行 RDMA 通信。
- 当 `planner.init_from_deep_ep(buffer)` 被调用时，LPLB 根据 `buffer.low_latency_mode` 决定是否使用 DeepEP 的 `cpu_rdma_team`（multi-plane 模式）或 `NVSHMEM_TEAM_WORLD`（单 plane 模式）。
