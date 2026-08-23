---
type: api-reference
scope: tile-kernels
name: TileKernels MoE 核函数参考
version: "0.1.0"
source: tile_kernels/moe/
description: TileKernels MoE 核函数详细参考（topk gate、expand/reduce、fused mapping、group_count）
---

# TileKernels MoE 核函数参考

本章节详细描述 TileKernels 的 MoE（Mixture of Experts）核函数实现，涵盖路由门控、映射构建、dispatch（expand）、combine（reduce）以及辅助算子。

---

## 一、MoE 计算流水线

MoE 层的标准计算流水线如下：

```
scores = gate(hidden)                    # 计算专家评分
→ topk_gate / top2_sum_gate              # 选择 top-k 专家
→ get_fused_mapping                      # 构建 dispatch/combine 映射
→ expand_to_fused (dispatch)             # 按专家排列 token
→ [DeepGEMM expert GEMM + SwiGLU+cast]   # 专家计算（由 DeepGEMM 执行）
→ reduce_fused (combine)                 # 加权归约回原 token 顺序
```

TileKernels 覆盖除核心 GEMM 之外的所有 MoE 算子。GEMM 由 [DeepGEMM](/ai/deepseek/deep-gemm/) 执行，跨节点通信由 [DeepEP](/ai/deepseek/deep-ep/) 执行。

---

## 二、路由门控（Gate）

### 2.1 topk_gate

基础 top-k 选择核函数。

**JIT kernel 工厂**：`get_topk_gate_kernel(num_experts: int, num_topk: int)`。

```python
def topk_gate(
    scores: torch.Tensor,     # (num_tokens, num_experts) float32
    num_topk: int,
) -> torch.Tensor:            # (num_tokens, num_topk) int64
```

**实现细节**：
- 使用 warp shuffle 在 warp 内做规约 topk 选择
- 稳定排序：当评分相等时返回较小索引
- 输出 contiguous

### 2.2 topk_sum_and_topk_group_idx

组内 top-k sum 后选 top-k groups，用于 DeepSeek-V3/V4 的 group-gated routing。

**JIT kernel 工厂**：`get_topk_sum_and_topk_group_idx_kernel(...)`。

```python
def topk_sum_and_topk_group_idx(
    scores: torch.Tensor,          # (num_tokens, num_groups, num_experts_per_group) float32
    num_topk_sum: int,             # 组内求和的 topk 数，仅支持 1 或 2
    num_topk_groups: int,          # 选择的组数
) -> torch.Tensor:                 # (num_tokens, num_topk_groups) int64
```

### 2.3 top2_sum_gate

端到端 Top2-Sum 门控，是生产环境使用的完整路由核函数。

**JIT kernel 工厂**：`get_top2_sum_gate_kernel(...)`。

```python
def top2_sum_gate(
    logits: torch.Tensor,                    # (num_tokens, num_routed_experts) float32
    bias: torch.Tensor,
    num_topk: int,
    num_topk_groups: int,
    num_groups: int,
    use_shared_as_routed: bool,
    num_shared_experts: int,
    routed_scaling_factor: float,
    ep_rank: int,
    num_ep_ranks: int,
    tp_rank: int,
    num_tp_ranks: int,
    scoring_func: str,                        # 'sigmoid' | 'sqrtsoftplus' | 'softmax'
    mask: torch.Tensor | None = None,
    fix_routing_mask: torch.Tensor | None = None,
    to_physical_map: torch.Tensor | None = None,
    logical_count: torch.Tensor | None = None,
    unmapped_topk_idx: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    # 返回 (topk_idx, topk_weights)
    # topk_idx:    (num_tokens, num_physical_topk) int64
    # topk_weights: (num_tokens, num_physical_topk) float32
```

**功能特性**：

| 特性 | 说明 |
|---|---|
| 三种评分函数 | sigmoid、sqrtsoftplus（`log(1+exp(x))` 的平方根）、softmax |
| Shared expert | 支持将 shared expert 追加到路由列表 |
| EP masking | 根据 ep_rank/num_ep_ranks 屏蔽非本 rank 的专家 |
| TP masking | 根据 tp_rank/num_tp_ranks 做 TP 维度的专家掩码 |
| Logical→Physical 映射 | 支持 logical expert ID 到 physical expert ID 的映射 |
| 固定路由 | fix_routing_mask 支持强制路由指定专家 |
| Routed scaling | routed_scaling_factor 控制路由专家权重缩放 |

**内部实现**：
- `warp_reduce_sum(x)` 宏：warp 级求和规约
- `softplus(x)` 宏：TileLang 宏实现 softplus，threshold=20（x>20 时直接返回 x）
- `get_topk_group_idx(...)` 宏：warp 内规约 topk group 选择，支持 num_topk_sum=1 或 2

### 2.4 ScoringFunc 枚举

```python
class ScoringFunc(IntEnum):
    SIGMOID = 0
    SQRTSOFTPLUS = 1
    SOFTMAX = 2
    IDENTITY = 3
```

支持 `from_str(label)` 类方法从字符串构造，`__str__` 返回小写名称。

---

## 三、融合映射构建（Fused Mapping）

### get_fused_mapping

构建 dispatch/combine 所需的全部索引映射，是 MoE 流水线中的关键编排核函数。

**JIT kernel 工厂**：`get_get_fused_mapping_kernel(...)`。

```python
def get_fused_mapping(
    topk_idx: torch.Tensor,          # (num_tokens, num_topk) int64
    num_experts: int,
    num_expanded_tokens: int,        # 0 时自动估算
    alignment: int,                  # 对齐要求
    force_no_sync: bool = False,
) -> tuple:
```

**返回 8 元组**：

| 返回值 | Shape | dtype | 说明 |
|---|---|---|---|
| `pos_to_expert` | (num_expanded_tokens,) | int32 | 每个 expanded position 属于哪个 expert |
| `pos_to_token` | (num_expanded_tokens,) | int32 | 每个 expanded position 对应哪个 token |
| `pos_to_token_topk` | (num_expanded_tokens,) | int32 | 每个 expanded position 对应 token 的第几个 topk slot |
| `token_topk_to_pos` | (num_tokens, num_topk) | int32 | 每个 (token, topk_slot) 映射到哪个 expanded position |
| `expert_start` | (num_experts,) | int32 | 每个 expert 在 expanded buffer 中的起始位置 |
| `expert_end` | (num_experts,) | int32 | 每个 expert 在 expanded buffer 中的结束位置 |
| `num_tokens_per_expert` | (num_experts,) | int32 | 每个 expert 分配到的 token 数 |
| `num_tokens_per_expert_list` | Python list | int | Python 端的 expert token 数列表 |

**自动估算模式**：当 `num_expanded_tokens=0` 且 `force_no_sync=False` 时：
1. 先启动 kernel 统计每个 expert 的 token 数
2. 做 host sync 读取 num_tokens_per_expert
3. 计算所需 expanded buffer 大小
4. 重新启动 kernel 生成完整映射

**内部宏**：`divide_task(length, num_tasks, task_id, start, end)` 实现任务划分。

---

## 四、Dispatch（Expand）

### expand_to_fused

将 token 数据按专家路由顺序排列到连续缓冲区（本地 dispatch 操作）。

**JIT kernel 工厂**：`get_expand_to_fused_kernel(...)`。

```python
def expand_to_fused(
    x: torch.Tensor,                     # (num_tokens, hidden)
    token_topk_to_pos: torch.Tensor,     # (num_tokens, num_topk) int32
    pos_to_expert: torch.Tensor,         # (num_expanded_tokens,) int32
) -> torch.Tensor:                       # (num_expanded_tokens, hidden)
```

**操作**：对每个 (token, topk_slot)，将 x[token] 拷贝到 expanded 缓冲区的 token_topk_to_pos[token, slot] 位置。

### expand_to_fused_with_sf

同时扩展 activation 和缩放因子（用于 QuantTensor）。

```python
def expand_to_fused_with_sf(
    x: QuantTensor,                      # (data, sf) 元组
    num_per_channels: int,
    token_topk_to_pos: torch.Tensor,
    pos_to_expert: torch.Tensor,
    use_tma_aligned_col_major_sf: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:  # (expanded_data, expanded_sf)
```

---

## 五、Combine（Reduce）

### reduce_fused

将 expert 输出加权归约回原始 token 顺序（本地 combine 操作）。

**JIT kernel 工厂**：`get_reduce_fused_kernel(...)`。

```python
def reduce_fused(
    x: torch.Tensor | QuantTensor,       # (num_expanded_tokens, hidden) 或 QuantTensor
    topk_weights: torch.Tensor | None,   # (num_tokens, num_topk) float32
    token_topk_to_pos: torch.Tensor,     # (num_tokens, num_topk) int32
    fp8_format: str = '',                # '' 或 'e4m3'
    sf: torch.Tensor | None = None,      # 可选缩放因子
    out: torch.Tensor | None = None,     # 可选输出张量
) -> torch.Tensor:                       # (num_tokens, hidden)
```

**操作**：
1. 初始化输出为 0
2. 对每个 expanded position，根据 pos_to_token 和 pos_to_token_topk 找到目标 (token, slot)
3. 如果有 topk_weights，乘以对应权重
4. 累加到输出 tensor

**FP8 输出模式**：`fp8_format='e4m3'` 时，输出直接量化为 FP8 格式。

**约束**：`hidden % 256 == 0`。

---

## 六、辅助算子

### 6.1 aux_fi

辅助负载均衡频率指示器（Auxiliary Frequency Indicator）。

```python
def aux_fi(
    topk_idx: torch.Tensor,     # (num_tokens, num_topk) int64
    num_experts: int,
    num_aux_topk: int,
) -> torch.Tensor:              # (num_experts,) float32
```

计算 `f_i[e] = count[e] * num_experts / (num_tokens * num_aux_topk)`，用于负载均衡损失。理想情况下每个 expert 的 f_i 接近 1.0。

**JIT kernel 工厂**：`get_aux_fi_kernel(num_topk, num_experts, num_sms)`。

### 6.2 group_count

统计每个 group 的 token 数量。

```python
def group_count(
    group_idx: torch.Tensor,    # (...) int32/int64
    num_groups: int,
) -> torch.Tensor:              # (num_groups,) int32
```

**JIT kernel 工厂**：`get_group_count_kernel(num_topk, num_groups, num_sms)`。

### 6.3 normalize_weight

归一化 topk 权重，使每个 token 的 topk 权重和为 1。

```python
def normalize_weight(
    topk_weights: torch.Tensor,     # (num_tokens, num_topk) float32
) -> tuple[torch.Tensor, torch.Tensor]:
    # (denominator, normalized_weights)
    # denominator: (num_tokens,) float32
    # normalized_weights: (num_tokens, num_topk) float32
```

**约束**：输入必须为 float32。

**JIT kernel 工厂**：`get_normalize_weight_kernel(num_topk)`。

### 6.4 inplace_unique_group_indices

原地去重 group 索引：每行中重复出现的 group 索引（非首次出现）设为 -1。

```python
def inplace_unique_group_indices(
    group_indices: torch.Tensor,    # (num_tokens, num_topk) int32，原地修改
    num_groups: int,
) -> None
```

**约束**：`num_groups <= 128`。

**JIT kernel 工厂**：`get_inplace_unique_group_indices_kernel(num_topk, num_groups_aligned, num_sms)`。

### 6.5 mask_indices_by_tp

TP（Tensor Parallelism）掩码：非本 TP rank 的 expert 索引设为 -1，本地索引重映射。

```python
def mask_indices_by_tp(
    indices: torch.Tensor,      # (...) int64
    n: int,
    num_ep_ranks: int,
    tp_rank: int,
    num_tp_ranks: int,
) -> torch.Tensor:              # 同 shape，非本地 expert 设为 -1
```

**JIT kernel 工厂**：`get_mask_indices_by_tp_kernel(num_topk, dtype)`。

---

## 七、MoE 公共宏

`moe/common.py` 中定义的可复用 TileLang 宏：

### get_topk_group_idx

```python
@T.macro
def get_topk_group_idx(
    scores_shared,              # shared memory 中的评分
    topk_group_idx_shared,      # shared memory 中的 topk group 索引输出
    num_groups,
    num_experts_per_group,
    num_topk_groups,
    num_topk_sum,               # 1 或 2
    num_vectorize_for_grouped_expert,
):
```

Warp 内规约 topk group 选择，使用 warp shuffle 进行 warp 级 reduce。

---

## 八、与 DeepGEMM / DeepEP 的协同

| 阶段 | 算子 | 负责库 |
|---|---|---|
| 路由评分 | gate linear | PyTorch/DeepGEMM |
| Top-k 选择 | top2_sum_gate | TileKernels |
| 跨节点 dispatch | all-to-all | [DeepEP](/ai/deepseek/deep-ep/) |
| 映射构建 | get_fused_mapping | TileKernels |
| 本地 dispatch | expand_to_fused | TileKernels |
| Expert GEMM | m_grouped_fp8_gemm | [DeepGEMM](/ai/deepseek/deep-gemm/) |
| SwiGLU+量化 | swiglu_forward_and_per_token_cast | TileKernels |
| Expert GEMM (2nd) | m_grouped_fp8_gemm | [DeepGEMM](/ai/deepseek/deep-gemm/) |
| 本地 combine | reduce_fused | TileKernels |
| 跨节点 combine | all-to-all | [DeepEP](/ai/deepseek/deep-ep/) |
