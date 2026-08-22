---
type: reference
scope: lplb
name: api
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 公共 API 参考——Planner 类与 EPLB 集成函数
---

# API 参考

## Planner 类

LPLB 的唯一公共入口类，负责专家负载均衡的完整流程：负载统计 → LP 求解 → token 路由。

### 构造函数

```python
Planner(
    redundant_to_original: torch.Tensor,
    n_routed_experts: int,
    n_logical_routed_experts: int,
    ep_size: int | None = None,
    group: torch.distributed.ProcessGroup | None = None,
)
```

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `redundant_to_original` | `torch.Tensor` int32, CUDA, 形状 `[group_size, num_redundants]` | 冗余专家到原始专家的映射矩阵。`r2o[i][j]` 表示 rank i 的第 j 个冗余专家是 rank `r2o[i][j]` 上原始专家的副本。约束：每个 rank 的冗余数量相同，每个冗余边恰好连接两个 rank。 |
| `n_routed_experts` | `int` | 物理路由专家总数（含冗余副本）。 |
| `n_logical_routed_experts` | `int` | 逻辑路由专家总数（不含冗余副本）。 |
| `ep_size` | `int \| None` | EP 总 rank 数。当 `group` 为 None 时必须提供。 |
| `group` | `ProcessGroup \| None` | EP 通信组。默认为 None，表示不执行 workload 归约。 |

**实例属性（初始化后可用）：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `r2o` | `torch.Tensor` int32, CUDA | redundant_to_original 的 CUDA 副本。 |
| `o2r` | `torch.Tensor` int32, CUDA | r2o 的 argsort，提供原始到冗余的反向映射。 |
| `group_size` | `int` | 冗余拓扑组大小（r2o.shape[0]）。 |
| `num_redundants` | `int` | 每个 rank 的冗余专家数（r2o.shape[1]）。 |
| `n_group` | `int` | 冗余组数（ep_size // group_size）。 |
| `n_local_routed_experts` | `int` | 每个 rank 的物理专家数（n_routed_experts // ep_size）。 |
| `n_local_logical_routed_experts` | `int` | 每个 rank 的逻辑专家数（n_logical_routed_experts // ep_size）。 |
| `combined_redundant_experts` | `int` | 合并后的冗余专家组数，用于 LP 求解的批量分配。 |
| `phy2log` | `torch.Tensor` int32, CUDA | 物理专家到逻辑专家的映射，由 `update_redundancy_mapping()` 设置。 |
| `solver` | `CompiledSolver` | JIT 编译的 C++/CUDA 求解器实例（通过 `_get_solver` 缓存）。 |

### init_from_deep_ep

```python
init_from_deep_ep(buffer: Buffer) -> None
```

从 DeepEP Buffer 初始化 NVSHMEM 通信器。首次调用时触发 `solver.init_comm()`，设置节点内/跨节点通信缓冲区。后续调用幂等返回。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `buffer` | `deep_ep.Buffer` | DeepEP 通信缓冲区实例。通过 `buffer.low_latency_mode` 决定 NVSHMEM multiplane 模式，通过 `buffer.num_rdma_bytes` 决定是否初始化 NVSHMEM。 |

**前置条件**：需要安装 `deep_ep` 包并在编译时启用 `USE_NVSHMEM`。

### update_redundancy_mapping

```python
update_redundancy_mapping(
    workload: torch.Tensor | None = None
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]
```

更新专家冗余映射。基于 EPLB 算法选择要复制的专家，并构建物理到逻辑的映射关系。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `workload` | `torch.Tensor \| None` | 形状 `(n_logical_routed_experts,)` 的历史负载统计。为 None 时使用恒等映射（无重排序）。 |

**返回值：**

| 返回值 | 形状 | 类型 | 说明 |
|---|---|---|---|
| `phy2log` | `(n_routed_experts,)` | int32 | 每个物理专家对应的逻辑专家 ID。 |
| `log2phy` | `(n_logical_routed_experts, max_logcnt)` | int32 | 每个逻辑专家的物理位置列表，填充 -1（max_logcnt 当前固定为 2）。 |
| `logcnt` | `(n_logical_routed_experts,)` | int32 | 每个逻辑专家的副本数量。 |

**算法流程：**
1. 无 workload 时创建 `arange(n_logical_routed_experts)` 作为基础映射。
2. 有 workload 时调用 [`rebalance_experts`](#rebalance_experts) 获取层次化重平衡结果，并按负载降序排列每个设备上的专家。
3. 选取每个设备上 top-K 专家作为冗余候选（K = `combined_redundant_experts * num_redundants`）。
4. 通过 `r2o` 映射在对端 rank 上创建冗余副本，拼接为完整的 phy2log。
5. 构建 log2phy 和 logcnt 索引。

### count_workload

```python
count_workload(idx: torch.Tensor, n_sms: int) -> tuple[torch.Tensor, torch.Tensor]
```

统计 token 分配到各逻辑专家的次数（GPU 端原子计数）。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `idx` | `torch.Tensor` int64, CUDA | 模型选中的逻辑专家索引，值范围 `[-1, n_logical_routed_experts)`，-1 表示忽略。 |
| `n_sms` | `int` | 使用的 CUDA SM 数量。 |

**返回值：**

| 返回值 | 形状 | 说明 |
|---|---|---|
| 第一个元素 | `(n_logical_routed_experts,)` int32 | 各专家的 token 总数（汇总结果）。 |
| 第二个元素 | `(n_sms, n_logical_routed_experts)` int32 | 按 SM 分片的前缀和计数，供 `weighted_select_target` 使用。 |

### solve_probs

```python
solve_probs(
    workload: torch.Tensor,
    avail_counter: torch.Tensor
) -> torch.Tensor
```

运行 LP 求解器，计算冗余专家的负载分配比例。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `workload` | `torch.Tensor` int32 | 负载统计，numel = `n_experts`。内部 reshape 为 `(n_group, group_size, n_local_logical_routed_experts)`。 |
| `avail_counter` | `torch.Tensor` int32, numel=1 | 可行解计数器，LP 可行时原子加 1。 |

**返回值：**

| 返回值 | 形状 | 说明 |
|---|---|---|
| `o_weight` | `(num_redundants, combined_redundant_experts)` float32 | 冗余专家的负载分配比例（分配到原始专家的比例）。 |

**通信行为：** 若 `ep_group is not None` 且未初始化 DeepEP 通信，则调用 `torch.distributed.all_reduce` 聚合跨 rank 的 workload。若已初始化 DeepEP NVSHMEM 通信，则在 CUDA kernel 内部通过 NVSHMEM 完成 allreduce。

### weighted_select_target

```python
weighted_select_target(
    idx: torch.Tensor,
    o_weight: torch.Tensor,
    local_workload_by_sm: torch.Tensor,
    n_sms: int
) -> torch.Tensor
```

基于 LP 求解的分配比例，通过加权哈希将逻辑专家索引映射到物理专家索引。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `idx` | `torch.Tensor` int64, CUDA | 逻辑专家索引，值范围 `[-1, n_logical_routed_experts)`。 |
| `o_weight` | `torch.Tensor` float32, CUDA | LP 求解得到的分配比例，形状 `(num_redundants, combined_redundant_experts)`。 |
| `local_workload_by_sm` | `torch.Tensor` int32, CUDA | `count_workload` 返回的第二个元素（按 SM 前缀和）。 |
| `n_sms` | `int` | CUDA SM 数量。 |

**返回值：**

| 返回值 | 形状 | 说明 |
|---|---|---|
| `mapped_idx` | 与 `idx` 相同 | 物理专家索引，值范围 `[-1, n_routed_experts)`。-1 保持映射为 -1。 |

### run

```python
run(
    idx: torch.Tensor,
    avail_counter: torch.Tensor,
    n_sms: int | None = None
) -> torch.Tensor
```

一站式接口：依次执行 `count_workload` → `solve_probs` → `weighted_select_target`。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `idx` | `torch.Tensor` int64, CUDA | 模型选中的逻辑专家索引。 |
| `avail_counter` | `torch.Tensor` int32, CUDA, shape () | 可行解计数器。 |
| `n_sms` | `int \| None` | CUDA SM 数量。为 None 时自动查询当前设备的 `multi_processor_count`。 |

**返回值：** 映射后的物理专家索引（与 `idx` 同形状）。

---

## EPLB 集成函数（lplb/eplb.py）

### balanced_packing

```python
balanced_packing(
    weight: torch.Tensor,
    num_packs: int
) -> tuple[torch.Tensor, torch.Tensor]
```

将 n 个带权对象打包到 m 个 pack 中，使每个 pack 包含恰好 n/m 个对象且各 pack 权重尽可能均衡（贪心装箱）。

**参数：**
- `weight`: 形状 `[X, n]`，每项权重。
- `num_packs`: pack 数量。

**返回值：**
- `pack_index`: 形状 `[X, n]` int64，每项所属 pack 索引。
- `rank_in_pack`: 形状 `[X, n]` int64，项在 pack 内的 rank。

### replicate_experts

```python
replicate_experts(
    weight: torch.Tensor,
    num_phy: int
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]
```

将 `num_log` 个专家复制到 `num_phy` 个副本，最小化所有副本的最大负载。贪心策略：从 `num_log` 个专家开始，逐个复制 `weight/logcnt` 比值最大的专家。

**参数：**
- `weight`: 形状 `[X, num_log]`。
- `num_phy`: 复制后的总专家数。

**返回值：**
- `phy2log`: 形状 `[X, num_phy]` int64，每个物理专家对应的逻辑专家 ID。
- `rank`: 形状 `[X, num_phy]` int64，副本序号。
- `logcnt`: 形状 `[X, num_log]` int64，每个逻辑专家的副本数。

### rebalance_experts_hierarchical

```python
rebalance_experts_hierarchical(
    weight: torch.Tensor,
    num_physical_experts: int,
    num_groups: int,
    num_nodes: int,
    num_gpus: int
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]
```

层次化专家重平衡。三步流程：
1. 将 groups 打包到 nodes（`balanced_packing`）。
2. 在节点内构造冗余专家（`replicate_experts`）。
3. 将物理专家打包到 GPUs（`balanced_packing`）。

**参数：**
- `weight`: 形状 `[num_moe_layers, num_logical_experts]`。
- `num_physical_experts`: 复制后的物理专家总数。
- `num_groups`: expert group 数量。
- `num_nodes`: 服务器节点数（节点内 NVLink 更快）。
- `num_gpus`: GPU 总数，必须是 `num_nodes` 的倍数。

### rebalance_experts

```python
rebalance_experts(
    weight: torch.Tensor,
    num_replicas: int,
    num_groups: int,
    num_nodes: int,
    num_gpus: int
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]
```

EPLB 入口函数。当 `num_groups % num_nodes == 0` 时使用层次化策略，否则退化为全局策略（等效单节点）。

**参数：**
- `weight`: 形状 `[layers, num_logical_experts]`，所有逻辑专家的负载统计。
- `num_replicas`: 物理专家（副本）总数，必须是 `num_gpus` 的倍数。
- `num_groups`: expert group 数量。
- `num_nodes`: 节点数。
- `num_gpus`: GPU 总数。

**返回值：**
- `phy2log`: 形状 `[layers, num_replicas]` int64。
- `log2phy`: 形状 `[layers, num_logical_experts, X]` int64，填充 -1。
- `logcnt`: 形状 `[layers, num_logical_experts]` int64。

---

## CompiledSolver（C++ 扩展，内部类）

通过 `lplb._cpp.CompiledSolver` 访问，通常不需要直接使用。主要方法：

| 方法 | 说明 |
|---|---|
| `solve(local_workload, r2o, phy2log, avail_num)` | CUDA LP 求解，返回 `(result, global_workload)`。 |
| `count_idx(idx, n_sms, block_dim)` | GPU 端索引计数，返回 `(汇总计数, 按SM分片计数)`。 |
| `map_idx(mapping_idx, o_weight, local_workload_split_by_sm, o2r, phy2log, n_sms, block_dim)` | 加权哈希路由，返回映射后的物理索引。 |
| `init_comm(device, nvshmem_multiplane, do_nvshmem_init)` | 初始化 NVSHMEM 通信（条件编译）。 |

构造函数参数为 `(resource_path, n_group, group_size, dup_per_rank, block_dim, n_local_experts, n_combined_experts, process_group)`，首次构造时触发 NVRTC JIT 编译。
