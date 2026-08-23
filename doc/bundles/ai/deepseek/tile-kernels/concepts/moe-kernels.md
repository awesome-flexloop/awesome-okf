---
type: concept
scope: tile-kernels
name: MoE 核函数流水线
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels MoE 核函数流水线详解——gate 路由、fused mapping、expand dispatch、reduce combine、辅助算子
---

# MoE 核函数流水线

MoE（Mixture of Experts）是大语言模型扩展模型容量的核心技术。在 MoE 层中，每个 token 只被路由到少数几个 expert（通常是 top-2）进行计算，从而在不增加计算量的情况下大幅增加模型参数量。TileKernels 提供了 MoE 流水线中除核心 GEMM 之外的所有高性能 CUDA 核函数。

---

## 一、MoE 完整流水线

DeepSeek MoE 层的前向计算流水线如下：

```
                             ┌──────────────────────────────────────────┐
                             │             MoE Layer Forward             │
                             └──────────────────────────────────────────┘

  hidden_states (B*S, D)
        │
        ▼
  ┌─────────────┐
  │ Gate Linear │ → logits (B*S, num_routed_experts)
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │ top2_sum_gate                                       │
  │  · score = scoring_func(logits + bias)              │
  │  · group_scores = topk_sum(scores, groups)          │
  │  · selected_groups = topk_groups(group_scores)      │
  │  · topk_weights, topk_idx = select_experts(...)     │
  │  · EP/TP masking, shared expert, routing mask       │
  └──────┬──────────────────────────────────────────────┘
         │  topk_idx (B*S, topk), topk_weights (B*S, topk)
         ▼
  ┌─────────────────────────────────────────────────────┐
  │ get_fused_mapping                                   │
  │  · 统计每个 expert 的 token 数                      │
  │  · 构建 pos_to_expert / pos_to_token /              │
  │    token_topk_to_pos / expert_start/end 等映射      │
  └──────┬──────────────────────────────────────────────┘
         │  8-tuple mapping
         ▼
  ┌──────────────────┐    ┌──────────────────┐
  │ DeepEP all-to-all│◄──►│ dispatch (跨节点) │
  └──────┬───────────┘    └──────────────────┘
         │  (跨节点通信后，token 到达目标 EP rank)
         ▼
  ┌──────────────────┐
  │ expand_to_fused  │ → expanded_x (num_expanded, D)
  │ (本地 dispatch)  │
  └──────┬───────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │ DeepGEMM: gate_proj + up_proj (grouped GEMM)        │
  │ → intermediate (num_expanded, 2*D_ffn)              │
  └──────┬──────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │ swiglu_forward_and_per_token_cast                   │
  │  · silu(gate) * up                                  │
  │  · * topk_weights                                   │
  │  · FP8 量化                                         │
  │ → (activated_fp8, sf)                               │
  └──────┬──────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │ DeepGEMM: down_proj (grouped GEMM)                  │
  │ → expert_out (num_expanded, D)                      │
  └──────┬──────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────┐
  │ reduce_fused     │ → output (B*S, D)
  │ (本地 combine)   │
  └──────┬───────────┘
         │
         ▼
  ┌──────────────────┐    ┌──────────────────┐
  │ DeepEP all-to-all│◄──►│ combine (跨节点)  │
  └──────┬───────────┘    └──────────────────┘
         │
         ▼
     output (B*S, D)
```

---

## 二、路由门控（Gate）

### 2.1 基础 TopK（topk_gate）

最基础的 top-k 选择：给定评分矩阵 `(num_tokens, num_experts)`，为每个 token 选择得分最高的 k 个 expert。

**实现特点**：
- 使用 warp shuffle 在 warp 内做并行规约 top-k 选择
- 稳定排序：当两个 expert 得分相等时，选择索引较小的
- 输出 contiguous int64 张量

### 2.2 Group TopK（topk_sum_and_topk_group_idx）

DeepSeek-V3/V4 引入的组路由策略：将 experts 分为若干组，先在组内取 top-k sum 得到组评分，再选择得分最高的若干组。这种策略可以避免所有 token 集中到少数几个 expert。

**约束**：`num_topk_sum` 仅支持 1 或 2（即组内 top-1 sum 或 top-2 sum）。

### 2.3 Top2-Sum Gate（top2_sum_gate）

端到端的生产级路由核函数，整合了所有路由逻辑：

1. **评分计算**：支持三种评分函数
   - Sigmoid：`score = sigmoid(logit + bias)`
   - SqrtSoftplus：`score = sqrt(softplus(logit + bias))`，softplus(x) = log(1+exp(x))
   - Softmax：`score = softmax(logit + bias)`

2. **组选择**：top-2 sum 策略选择 expert groups

3. **Expert 选择**：在选中的组内选择 top-k experts

4. **Shared Expert 追加**：如果 `use_shared_as_routed=True`，将 shared experts 追加到路由列表

5. **EP Masking**：根据 `ep_rank/num_ep_ranks` 过滤非本 rank 的 expert

6. **TP Masking**：根据 `tp_rank/num_tp_ranks` 做 TP 维度的掩码和重映射

7. **Logical→Physical 映射**：支持 logical expert ID 到 physical ID 的映射

8. **路由缩放**：`routed_scaling_factor` 控制路由专家的权重缩放

9. **固定路由**：`fix_routing_mask` 支持强制路由到指定 expert

### 2.4 评分函数

```python
class ScoringFunc(IntEnum):
    SIGMOID = 0        # score = 1/(1+exp(-x))
    SQRTSOFTPLUS = 1   # score = sqrt(log(1+exp(x)))
    SOFTMAX = 2        # score = exp(x)/sum(exp(x))
    IDENTITY = 3       # score = x
```

Softplus 在 TileLang 中使用 `@T.macro` 实现，threshold=20（x>20 时直接返回 x 避免数值不稳定）。

---

## 三、融合映射（Fused Mapping）

`get_fused_mapping` 是 MoE 流水线的"编排器"，它一次性构建 dispatch 和 combine 所需的全部索引映射。

### 3.1 为什么需要映射？

MoE 中 token 到 expert 的分配是动态的。每个 token 被路由到 k 个 expert，因此一个 token 可能出现在 expanded buffer 的多个位置；每个 expert 处理不定数量的 token。映射表记录了"expanded buffer 的第 i 个位置对应哪个 token 的哪个 top-k slot，属于哪个 expert"。

### 3.2 映射表详解

假设 3 个 token，2 个 expert，top-2 路由：

```
topk_idx:
  token 0 → [expert 0, expert 1]
  token 1 → [expert 1, expert 0]
  token 2 → [expert 0, expert 1]

expand 后 expanded buffer 的排列（按 expert 分组）：
  position 0: token 0, slot 0 → expert 0
  position 1: token 1, slot 1 → expert 0
  position 2: token 2, slot 0 → expert 0
  position 3: token 0, slot 1 → expert 1
  position 4: token 1, slot 0 → expert 1
  position 5: token 2, slot 1 → expert 1
```

对应的映射表：

| 映射 | 值 | 说明 |
|---|---|---|
| `pos_to_expert` | [0,0,0,1,1,1] | 每个位置属于哪个 expert |
| `pos_to_token` | [0,1,2,0,1,2] | 每个位置对应哪个 token |
| `pos_to_token_topk` | [0,1,0,1,0,1] | 每个位置对应 token 的第几个 slot |
| `token_topk_to_pos` | [[0,3],[4,1],[2,5]] | (token,slot)→position 反查 |
| `expert_start` | [0, 3] | 每个 expert 在 buffer 中的起始位置 |
| `expert_end` | [3, 6] | 每个 expert 在 buffer 中的结束位置 |

### 3.3 自动估算模式

当 `num_expanded_tokens=0` 时，kernel 自动执行两步流程：
1. 第一次启动仅统计每个 expert 的 token 数（不需要输出缓冲区）
2. Host 端读取统计结果，计算所需缓冲区大小
3. 第二次启动生成完整映射

---

## 四、Dispatch（Expand）

`expand_to_fused` 执行本地 dispatch 操作：将 token 数据从 `(num_tokens, hidden)` 排列到 `(num_expanded_tokens, hidden)`，每个 token 在其被路由到的 expert 位置复制一份。

```python
expanded = torch.zeros(num_expanded_tokens, hidden, dtype=x.dtype, device=x.device)
for pos in range(num_expanded_tokens):
    token_idx = pos_to_token[pos]
    expanded[pos] = x[token_idx]
```

实际 kernel 使用并行 gather 实现，比纯 PyTorch 循环快得多。

`expand_to_fused_with_sf` 同时处理量化数据的 data 和 scale factors 两部分。

---

## 五、Combine（Reduce）

`reduce_fused` 执行本地 combine 操作：将 expert 输出加权归约回原始 token 顺序。

```python
output = torch.zeros(num_tokens, hidden, dtype=expanded.dtype, device=expanded.device)
for pos in range(num_expanded_tokens):
    token_idx = pos_to_token[pos]
    slot = pos_to_token_topk[pos]
    weight = topk_weights[token_idx, slot]  # 路由权重
    output[token_idx] += expanded[pos] * weight
```

关键特性：
- **加权归约**：每个 expert 输出乘以对应的 topk 权重后累加
- **FP8 输出**：`fp8_format='e4m3'` 时直接输出 FP8 量化结果
- **原子累加**：kernel 内使用原子加或分块归约实现高效累加
- **约束**：hidden 维度需 256 对齐

---

## 六、辅助算子

| 算子 | 功能 | 使用场景 |
|---|---|---|
| `aux_fi` | 计算 expert 频率指示器 f_i = count[e] * N / (T * topk) | 辅助负载均衡损失 |
| `group_count` | 统计每个 group 的 token 数 | group 级负载均衡 |
| `normalize_weight` | 归一化 topk 权重使和为 1 | 路由权重后处理 |
| `inplace_unique_group_indices` | 去除每行重复的 group 索引 | 避免重复路由到同一 group |
| `mask_indices_by_tp` | TP 掩码：非本 rank expert 设为 -1 | 张量并行 |

---

## 七、Warp 级原语

MoE kernel 大量使用 warp 级原语做高效规约：

- **warp shuffle（`T.shfl_sync`）**：在 warp 内的线程间交换数据，用于 warp 内 top-k 和 reduce
- **warp reduce**：`warp_reduce_sum` 宏实现 warp 内求和规约
- **`get_topk_group_idx` 宏**：warp 内规约 topk group 选择，支持 top-1 sum 和 top-2 sum

这些 warp 级操作避免了使用 shared memory 做跨线程通信，延迟更低。

---

## 八、与 DeepGEMM/DeepEP 的协同

MoE 是一个系统级问题，需要计算核函数（GEMM）、通信（all-to-all）和数据编排（expand/reduce）三者紧密配合：

| 阶段 | TileKernels | DeepGEMM | DeepEP |
|---|---|---|---|
| 路由 | top2_sum_gate | gate linear | — |
| 跨节点 dispatch | — | — | all-to-all dispatch |
| 映射构建 | get_fused_mapping | — | — |
| 本地 dispatch | expand_to_fused | — | — |
| Expert GEMM 1 | — | m_grouped_gemm (gate+up) | — |
| 激活+量化 | swiglu_forward_and_per_token_cast | — | — |
| Expert GEMM 2 | — | m_grouped_gemm (down) | — |
| 本地 combine | reduce_fused | — | — |
| 跨节点 combine | — | — | all-to-all combine |
| 辅助 | aux_fi, group_count, normalize_weight | — | — |
