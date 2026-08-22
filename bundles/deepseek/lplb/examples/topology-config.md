---
type: example
scope: lplb
name: topology-config
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 拓扑配置示例——Cube/Hypercube/Ring/Torus 拓扑的使用与自定义
---

# 拓扑感知配置

本示例演示 LPLB 中各种预定义拓扑的使用方法，以及如何配置自定义拓扑。

## 预定义拓扑常量

LPLB 测试中提供了四种预定义拓扑（位于 `tests/utils.py`），可以直接参考使用。

### Cube8P2E：8 GPU 立方体拓扑

适用于单节点 8 GPU（NVLink 全互联）场景，每个 GPU 有 2 个冗余邻居。

```python
import torch
from lplb import Planner

CUBE_8P2E = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T  # shape: (8, 2)

# 参数计算
group_size, num_redundants = CUBE_8P2E.shape  # 8, 2
ep_size = 32  # 总 GPU 数，需是 group_size 的倍数
n_logical_experts = 256
n_routed_experts = n_logical_experts + num_redundants * ep_size  # 320

planner = Planner(
    redundant_to_original=CUBE_8P2E.int().cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
)
print(f"n_group={planner.n_group}, combined_redundant_experts={planner.combined_redundant_experts}")
# n_group=4（32/8=4 个冗余组），每 group_size=8 个 rank 构成一个 Cube
```

**拓扑图示**（8 个 rank 的立方体连接）：

```
rank 0 ──冗余0──> rank 3    rank 0 ──冗余1──> rank 6
rank 1 ──冗余0──> rank 0    rank 1 ──冗余1──> rank 7
rank 2 ──冗余0──> rank 1    rank 2 ──冗余1──> rank 4
rank 3 ──冗余0──> rank 2    rank 3 ──冗余1──> rank 5
rank 4 ──冗余0──> rank 7    rank 4 ──冗余1──> rank 0
rank 5 ──冗余0──> rank 4    rank 5 ──冗余1──> rank 1
rank 6 ──冗余0──> rank 5    rank 6 ──冗余1──> rank 2
rank 7 ──冗余0──> rank 6    rank 7 ──冗余1──> rank 3
```

### RING_8P：8 GPU 环形拓扑

最简单的拓扑，每个 GPU 仅有 1 个冗余邻居（下一个 rank），适合调试和最小化验证。

```python
RING_8P = torch.tensor([
    [1, 2, 3, 4, 5, 6, 7, 0],
]).T  # shape: (8, 1)

group_size, num_redundants = RING_8P.shape  # 8, 1
ep_size = 32
n_logical_experts = 256
n_routed_experts = n_logical_experts + num_redundants * ep_size  # 288

planner = Planner(
    redundant_to_original=RING_8P.int().cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
)
# DUP_PER_RANK=1，LP 规模最小：NC=16, NV=26
```

### HYPERCUBE_16P2E：16 GPU 超立方体拓扑

适用于双节点 16 GPU 场景，排除对角线边。

```python
HYPERCUBE_16P2E = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6, 11, 8, 9, 10, 15, 12, 13, 14],
    [12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
]).T  # shape: (16, 2)

group_size, num_redundants = HYPERCUBE_16P2E.shape  # 16, 2
ep_size = 16
n_logical_experts = 256
n_routed_experts = n_logical_experts + num_redundants * ep_size  # 288

planner = Planner(
    redundant_to_original=HYPERCUBE_16P2E.int().cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
)
# group_size=16, n_group=1
# 测试中 max/mean 负载比可达 1.03
```

### Torus 2D：二维环面拓扑

适用于多节点全局均衡，每个 rank 有两个邻居（一个行方向、一个列方向）。

```python
def torus_2d(m: int, n: int) -> torch.Tensor:
    """生成 m×n 二维 Torus 拓扑的 r2o 矩阵。
    返回形状 (m*n, 2) 的张量。
    rank (i,j) 的冗余0 = ((i+1)%m)*n + j（行方向，通常跨节点）
    rank (i,j) 的冗余1 = i*n + (j+1)%n（列方向，通常节点内）
    """
    return torch.tensor(
        [[(i + 1) % m * n + j, i * n + (j + 1) % n]
         for i in range(m) for j in range(n)]
    )

# 32 GPU: 8 节点 × 4 GPU/节点
m, n = 8, 4
r2o_torus = torus_2d(m, n)  # shape: (32, 2)

group_size, num_redundants = r2o_torus.shape  # 32, 2
ep_size = 32
n_logical_experts = 256
n_routed_experts = n_logical_experts + num_redundants * ep_size  # 320

planner = Planner(
    redundant_to_original=r2o_torus.int().cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
)
# 测试中 max/mean 负载比可达 1.01（最均衡）
# 注意：因含跨节点边，需要 NVSHMEM 通信获得最佳性能
```

## 拓扑选择指南

| 场景 | 拓扑 | group_size | num_redundants | 均衡效果 | 通信模式 |
|---|---|---|---|---|---|
| 单节点 8 GPU | Cube8P2E | 8 | 2 | <1.07~1.10 | NVLink 域内 |
| 调试/验证 | Ring8P | 8 | 1 | <1.07 | 最小 LP |
| 双节点 16 GPU | Hypercube16P2E | 16 | 2 | <1.03 | NVLink+NVSHMEM |
| 多节点 32+ GPU | Torus2D(8,4) | 32 | 2 | <1.01 | 含跨节点边 |

## 自定义拓扑

### 约束条件

自定义 r2o 矩阵必须满足：

1. **形状**：`[group_size, num_redundants]`，int32，CUDA 张量。
2. **值域**：所有元素在 `[0, group_size)` 范围内。
3. **对称性（i-th 约定）**：对于每列 j，映射 `f(i) = r2o[i][j]` 必须构成一个置换的集合，且冗余边双向可达。即如果 r2o[i][j] = k，那么 r2o 中必须存在从 k 回到 i 的路径（在同一列 j 中）。
4. **均匀度**：每列的度数一致（每个 rank 在第 j 列恰好指向一个对端 rank）。

### 自定义示例：4 GPU Ring

```python
# 最简单的自定义拓扑：4 GPU 环形
r2o_ring4 = torch.tensor([
    [1],   # rank 0 → rank 1
    [2],   # rank 1 → rank 2
    [3],   # rank 2 → rank 3
    [0],   # rank 3 → rank 0
], dtype=torch.int32)  # shape: (4, 1)

planner = Planner(r2o_ring4.cuda(),
                  n_routed_experts=64,      # 例如 64 物理专家
                  n_logical_routed_experts=60,  # 60 逻辑专家
                  ep_size=4)
```

### 自定义示例：4 GPU 完全二分图

```python
# 4 GPU 两两互联（完全图 K4 的一种 2-正则分解）
r2o_k4 = torch.tensor([
    [1, 2],  # rank 0 → rank 1, 2
    [0, 3],  # rank 1 → rank 0, 3
    [3, 0],  # rank 2 → rank 3, 0
    [2, 1],  # rank 3 → rank 2, 1
], dtype=torch.int32)  # shape: (4, 2)
```

### 验证拓扑有效性

```python
def validate_topology(r2o: torch.Tensor) -> bool:
    """验证 r2o 矩阵的基本约束。"""
    assert r2o.dim() == 2, "r2o 必须是 2D 张量"
    group_size, num_redundants = r2o.shape
    assert r2o.dtype in (torch.int32, torch.int64), "dtype 必须是 int32 或 int64"

    for j in range(num_redundants):
        col = r2o[:, j].tolist()
        # 检查值域
        assert all(0 <= x < group_size for x in col), f"列 {j} 有值越界"
        # 检查 i-th 约定：每列应构成一个对合（f(f(i)) 可以通过其他列回到 i）
        # 这里仅做基本检查：每个 rank 在列中恰好被指向一次（置换性质）
        assert sorted(col) == list(range(group_size)), \
            f"列 {j} 不是置换，r2o={col}"

    print(f"拓扑验证通过: group_size={group_size}, num_redundants={num_redundants}")
    return True

# 使用
validate_topology(CUBE_8P2E)
validate_topology(r2o_torus)
```

## 与 DeepEP 集成的拓扑配置

当使用 DeepEP NVSHMEM 通信时，拓扑的 `group_size` 应与 DeepEP 的 low-latency 配置匹配：

```python
from lplb import Planner

# 初始化 DeepEP buffer（参考 DeepEP 文档）
# buffer = deep_ep.Buffer(...)

planner = Planner(
    redundant_to_original=CUBE_8P2E.int().cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
    group=ep_group,
)

# 从 DeepEP buffer 初始化 NVSHMEM 通信
planner.init_from_deep_ep(buffer)
# 此后 solve_probs 内部将使用 NVSHMEM 进行 workload 同步，
# 而非 torch.distributed.all_reduce
```

`init_from_deep_ep` 根据 buffer 配置自动选择：
- `buffer.low_latency_mode=True`：使用 DeepEP 的 `cpu_rdma_team`（multi-plane 模式，适用于 normal 模式 dispatch）。
- `buffer.low_latency_mode=False`：使用 `NVSHMEM_TEAM_WORLD`（low-latency 模式）。
- `buffer.num_rdma_bytes==0`：跳过 NVSHMEM 初始化（无 RDMA 缓冲区配置）。

## n_group 的影响

当 `ep_size > group_size` 时，EP 域被划分为 `n_group = ep_size // group_size` 个独立的冗余组：

```python
# 64 GPU，使用 Cube8P2E（group_size=8）
ep_size = 64
planner = Planner(CUBE_8P2E.int().cuda(),
                  n_routed_experts=640,
                  n_logical_routed_experts=512,
                  ep_size=ep_size)
print(f"n_group = {planner.n_group}")  # 8 个冗余组
# LP 求解时 grid = {8, 1, 1}，每个 block 处理一组
# 组间独立均衡，组内通过 Cube 拓扑分流
```

选择 group_size 时需注意：
- group_size 决定了 LP 问题规模（NC=G+G*D, NV=2*G*D+G+2），影响共享内存占用和求解时间。
- group_size 应与硬件拓扑匹配（如 8 表示单节点内 NVLink 域）。
- n_group 越大，可并行的 LP 求解 block 越多，但跨组分流需要通过 EPLB 静态层处理。

相关参考：
- [API 参考](/deepseek/lplb/references/api)
- [拓扑配置参考](/deepseek/lplb/references/topology)
- [拓扑感知路由概念](/deepseek/lplb/concepts/topology-aware-routing)
- [基础使用示例](/deepseek/lplb/examples/basic-planning)
