---
type: concept
scope: lplb
name: topology-aware-routing
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 拓扑感知路由——Cube/Hypercube/Torus 拓扑设计与副本组机制
---

# 拓扑感知路由

## 为什么需要拓扑

LPLB 通过复制热专家到邻接 GPU 来分流过载 token。但"哪些 GPU 之间可以互相分流"受硬件互连拓扑约束：

1. **NVLink 域内**：同一节点 GPU 通过 NVLink 全互联，带宽高（~900GB/s）、延迟低，适合细粒度分流。
2. **跨节点（RDMA）**：不同节点 GPU 通过 InfiniBand/RoCE 互连，带宽较低（~400Gbps），应减少跨节点分流。
3. **通信对称性**：冗余边必须双向，才能保证 token 互相分流而不破坏 LP 流量守恒约束。

LPLB 通过 `redundant_to_original`（r2o）矩阵静态定义冗余拓扑，编码 GPU 间图结构，LP 在此图上优化 token 路由。

## r2o 矩阵语义

r2o 是形状 `[group_size, num_redundants]` 的 int32 张量（CUDA）：

```
r2o[i][j] = k  表示 rank i 的第 j 个冗余专家是 rank k 上原始专家的副本
```

关键约束：
1. **i-th 约定**：所有 rank 的第 j 个冗余专家，必须是另一个 rank 上第 j 个冗余槽位对应原始专家的副本。
2. **双向边**：若 rank i 的第 j 个冗余指向 rank k，则 LP 中 rank k 的负载约束也通过 r2o 反向引用 rank i 的副本。

### o2r 反向映射

`o2r = r2o.argsort(dim=0)` 提供反向查找：当 rank k 从第 j 条冗余边接收分流 token 时，需知道来自哪个 rank 的哪个冗余槽位。o2r 用于 `kernel_map_idx` 中构建物理专家索引。

## 预定义拓扑

### Cube（立方体）

```
CUBE_8P2E: shape (8, 2)
r2o[0]=[3,6]  r2o[1]=[0,7]  r2o[2]=[1,4]  r2o[3]=[2,5]
r2o[4]=[7,0]  r2o[5]=[4,1]  r2o[6]=[5,2]  r2o[7]=[6,3]
```

8 个 rank 构成立方体图，每 rank 2 条边。第一条边连接同面邻居（步长 3 mod 8），第二条连接对角线邻居（步长 6 = -2 mod 8）。所有边在 NVLink 域内闭合，**不涉及跨节点通信**。

- **场景**：单节点 8 GPU EP 子组均衡
- **LP 规模**：NC=24, NV=42
- **均衡效果**：max/mean < 1.07~1.10
- **要求**：每 GPU 至少 2 个冗余专家槽位

### Hypercube（超立方体）

```
HYPERCUBE_16P2E: shape (16, 2)
```

16 个 rank 构成超立方体（排除对角线）。0-7 和 8-15 各自形成 Cube 子图，两组间有跨组边。

- **场景**：16 GPU 双节点 EP
- **LP 规模**：NC=48, NV=82
- **均衡效果**：max/mean < 1.03（测试最优）

### Ring（环形）

```
RING_8P: shape (8, 1)
r2o[i] = [(i+1) % 8]
```

8 rank 连成环形，每 rank 1 条边。最简单拓扑，DUP_PER_RANK=1。

- **场景**：最小 LP 规模（NC=16, NV=26），用于调试验证
- **均衡效果**：max/mean < 1.07

### Torus 2D（二维环面）

```python
torus_2d(m, n): shape (m*n, 2)
# rank (i,j): r2o[i*n+j][0] = ((i+1)%m)*n + j  (行方向，跨节点)
#             r2o[i*n+j][1] = i*n + (j+1)%n     (列方向，节点内)
```

m×n 个 rank 排列为二维环面，每 rank 两条边：行方向（跨节点）和列方向（节点内）。测试用 `torus_2d(8,4)` 生成 32 rank。

- **场景**：多节点全局均衡
- **均衡效果**：max/mean < 1.01（最均衡）
- **注意**：含跨节点边，通信效率低于 Cube

## 物理专家布局

每个 rank 上物理专家内存布局：

```
n_local_routed_experts 个物理专家槽位
│
├── 原始冗余专家区 [combined_redundant_experts * num_redundants]
│   └── 按 num_redundants 分组，每组 combined_redundant_experts 个
│       本地"热专家"，token 可分流到邻接 rank
│
├── 固定专家区 [n_local_logical - combined * num_redundants]
│   └── 不参与 LP 分流，token 全部本地处理
│
└── 副本冗余专家区 [combined_redundant_experts * num_redundants]
    └── 从邻接 rank 复制的槽位，接收分流 token
```

### phy2log 构建

`update_redundancy_mapping()` 构建流程：
1. **基础映射**（无 workload）：`arange(n_logical_routed_experts)` 顺序排列。
2. **EPLB 重排序**（有 workload）：调用 `rebalance_experts()` 层次化重平衡，按负载降序排列。
3. **冗余选择**：取前 `combined * num_redundants` 个专家为冗余候选。
4. **副本创建**：通过 r2o 映射在邻接 rank 上创建副本。
5. **索引构建**：遍历 phy2log 转置构建 log2phy 和 logcnt，保证原始专家在副本前记录。

## n_group：冗余组划分

`ep_size > group_size` 时，EP 域划分为 `n_group = ep_size // group_size` 个冗余组。每组是独立拓扑实例，LP 在组内独立求解：

- `kernel_solve` grid = `{n_group, 1, 1}`，每 block 处理一组。
- 组内独立均衡，组间不直接分流（EPLB 重平衡在全局操作）。

### 与 DeepEP 通信域对应

| 层级 | group_size | 通信方式 |
|---|---|---|
| 单节点 Cube | 8 | NVLink（CUDA IPC + 原子信号） |
| 双节点 Hypercube | 16 | NVLink + NVSHMEM 跨节点 |
| 多节点 Torus | m*n | NVLink + NVSHMEM RDMA |

`init_from_deep_ep(buffer)` 根据 buffer 配置自动选择：
- `buffer.low_latency_mode=True`：使用 `deep_ep::internode::cpu_rdma_team`（multi-plane）。
- `buffer.low_latency_mode=False`：使用 `NVSHMEM_TEAM_WORLD`（单 plane）。
- `buffer.num_rdma_bytes==0`：不初始化 NVSHMEM。

## 自定义拓扑

自定义 r2o 需满足：
1. **结构**：形状 `[group_size, num_redundants]`，值在 `[0, group_size)`，第 j 列构成置换/对合。
2. **性能**：group_size 不宜过大（共享内存 O(NC×NV)）；优先 NVLink 域内连接；图应有良好连通性避免 LP 不可行。
3. **编译匹配**：不同 group_size/num_redundants 触发不同 JIT 编译（通过 `_get_solver` LRU 缓存）。
