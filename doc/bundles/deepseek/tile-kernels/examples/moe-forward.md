---
type: example
scope: tile-kernels
name: MoE 前向计算
version: "0.1.0"
source: tile-kernels-spec-facts
description: 使用 TileKernels MoE 核函数构建完整的 MoE 前向计算流水线
---

# MoE 前向计算

本示例展示如何使用 TileKernels 的 MoE 核函数构建完整的 MoE 层前向计算流水线，包括路由门控、映射构建、dispatch、expert 计算和 combine。

---

## 环境准备

```python
import torch
import tile_kernels

device = 'cuda'
torch.manual_seed(42)
```

---

## MoE 参数设置

```python
# MoE 配置
num_tokens = 4096
hidden_size = 4096
num_experts = 64
num_topk = 8
topk_group = 4
num_groups = 8
num_experts_per_group = num_experts // num_groups  # 8
num_shared_experts = 2
routed_scaling_factor = 1.0

# Expert FFN 配置
ffn_hidden = 1024  # 每个 expert 的中间层维度
```

---

## Step 1: Gate 计算

```python
# 模拟 gate 线性层输出（logits）
gate_logits = torch.randn(num_tokens, num_experts, device=device, dtype=torch.float32)
gate_bias = torch.zeros(num_experts, device=device, dtype=torch.float32)

# 使用 top2_sum_gate 进行路由
# 单 GPU 场景：ep_rank=0, num_ep_ranks=1, tp_rank=0, num_tp_ranks=1
topk_idx, topk_weights = tile_kernels.moe.top2_sum_gate(
    logits=gate_logits,
    bias=gate_bias,
    num_topk=num_topk,
    num_topk_groups=topk_group,
    num_groups=num_groups,
    use_shared_as_routed=False,
    num_shared_experts=num_shared_experts,
    routed_scaling_factor=routed_scaling_factor,
    ep_rank=0,
    num_ep_ranks=1,
    tp_rank=0,
    num_tp_ranks=1,
    scoring_func='sigmoid',  # sigmoid / sqrtsoftplus / softmax
    mask=None,
    fix_routing_mask=None,
    to_physical_map=None,
    logical_count=None,
    unmapped_topk_idx=None,
)

print(f"topk_idx shape: {topk_idx.shape}, dtype: {topk_idx.dtype}")
print(f"topk_weights shape: {topk_weights.shape}, dtype: {topk_weights.dtype}")
print(f"Top-1 expert 分布（前5个expert）: "
      f"{[(topk_idx[:,0]==i).sum().item() for i in range(5)]}")
```

---

## Step 2: 基础 TopK Gate（简化场景）

如果不需要 group routing 和各种 mask，可以使用简单的 `topk_gate`：

```python
# 简单 topk gate
scores = torch.randn(num_tokens, num_experts, device=device, dtype=torch.float32)
simple_topk_idx = tile_kernels.moe.topk_gate(scores, num_topk=num_topk)
print(f"简单 topk_idx shape: {simple_topk_idx.shape}")
```

---

## Step 3: 构建 Fused Mapping

`get_fused_mapping` 构建 dispatch 和 combine 所需的全部索引映射：

```python
alignment = 128  # 对齐要求

# 自动估算 expanded tokens 数量
mapping = tile_kernels.moe.get_fused_mapping(
    topk_idx=topk_idx,
    num_experts=num_experts,
    num_expanded_tokens=0,  # 0=自动估算
    alignment=alignment,
    force_no_sync=False,
)

(pos_to_expert, pos_to_token, pos_to_token_topk,
 token_topk_to_pos, expert_start, expert_end,
 num_tokens_per_expert, num_tokens_per_expert_list) = mapping

num_expanded = pos_to_expert.shape[0]
print(f"Expanded tokens: {num_expanded}")
print(f"平均每 expert token 数: {num_tokens_per_expert.float().mean().item():.1f}")
print(f"Expert token 数（前5个）: {num_tokens_per_expert[:5].tolist()}")
```

---

## Step 4: Dispatch（Expand to Fused）

将 token 数据按 expert 顺序排列到连续缓冲区：

```python
# 模拟输入 hidden states
hidden_states = torch.randn(num_tokens, hidden_size, device=device, dtype=torch.bfloat16)

# FP8 量化后 dispatch（更实际的场景）
num_per_channels = 128
hidden_fp8, hidden_sf = tile_kernels.quant.per_token_cast(
    hidden_states, fmt='e4m3', num_per_channels=num_per_channels
)

# Dispatch 普通 tensor
expanded = tile_kernels.moe.expand_to_fused(
    hidden_states, token_topk_to_pos, pos_to_expert
)
print(f"Expanded shape: {expanded.shape}")  # (num_expanded, hidden_size)

# Dispatch QuantTensor（同时展开 data 和 sf）
expanded_fp8, expanded_sf = tile_kernels.moe.expand_to_fused_with_sf(
    (hidden_fp8, hidden_sf),
    num_per_channels=num_per_channels,
    token_topk_to_pos=token_topk_to_pos,
    pos_to_expert=pos_to_expert,
)
print(f"Expanded FP8 shape: {expanded_fp8.shape}")
print(f"Expanded SF shape: {expanded_sf.shape}")
```

---

## Step 5: Expert 计算（示例）

Expert 计算通常使用 DeepGEMM 的 grouped GEMM。这里用 PyTorch 模拟：

```python
# 模拟 expert 权重（实际中使用 DeepGEMM grouped GEMM）
# gate_proj + up_proj
gate_up_weight = torch.randn(
    num_experts, hidden_size, ffn_hidden * 2,
    device=device, dtype=torch.bfloat16
)
down_weight = torch.randn(
    num_experts, ffn_hidden, hidden_size,
    device=device, dtype=torch.bfloat16
)

# 方法1：按 expert 分块计算（示意，实际用 DeepGEMM grouped GEMM）
expert_output_list = []
for eid in range(num_experts):
    start = expert_start[eid].item()
    end = expert_end[eid].item()
    if start == end:
        continue
    expert_input = expanded[start:end]  # 该 expert 的 tokens

    # gate+up proj (模拟 GEMM)
    gate_up = expert_input @ gate_up_weight[eid]  # (tokens_e, 2*ffn)

    # SwiGLU + FP8 量化（使用 TileKernels 融合算子）
    # 注意：swiglu_forward_and_per_token_cast 支持 pos_to_token_topk 和 topk_weights
    # 这里简化处理
    swiglu_out = torch.nn.functional.silu(gate_up[:, :ffn_hidden]) * gate_up[:, ffn_hidden:]
    expert_output_list.append((swiglu_out.to(torch.bfloat16), start, end))

# 将 expert 输出放入 expanded 输出缓冲区
expanded_output = torch.zeros(
    num_expanded, hidden_size, device=device, dtype=torch.bfloat16
)
for expert_out, start, end in expert_output_list:
    # down proj（模拟）
    eid = pos_to_expert[start].item()
    down_out = expert_out @ down_weight[eid]
    expanded_output[start:end] = down_out

print(f"Expert 输出 shape: {expanded_output.shape}")
```

---

## Step 6: Combine（Reduce Fused）

将 expert 输出加权归约回原始 token 顺序：

```python
# BF16 combine
output = tile_kernels.moe.reduce_fused(
    expanded_output,
    topk_weights=topk_weights,
    token_topk_to_pos=token_topk_to_pos,
)
print(f"Combine 输出 shape: {output.shape}")  # (num_tokens, hidden_size)

# FP8 combine（直接输出 FP8）
expanded_output_fp8, expanded_output_sf = tile_kernels.quant.per_token_cast(
    expanded_output.float(), fmt='e4m3',
    num_per_channels=num_per_channels
)
output_fp8, output_sf = tile_kernels.moe.reduce_fused(
    expanded_output_fp8,
    topk_weights=topk_weights,
    token_topk_to_pos=token_topk_to_pos,
    fp8_format='e4m3',
    sf=expanded_output_sf,
)
print(f"FP8 Combine 输出: {output_fp8.shape}")
```

---

## Step 7: 辅助算子

```python
# 归一化权重
denom, norm_weights = tile_kernels.moe.normalize_weight(topk_weights.float())
print(f"权重和（应接近1）: {norm_weights.sum(-1)[:5]}")

# Group count（统计每组 token 数）
# 需要先有 group_idx
group_scores = scores.view(num_tokens, num_groups, num_experts_per_group)
group_idx = tile_kernels.moe.topk_sum_and_topk_group_idx(
    group_scores, num_topk_sum=2, num_topk_groups=topk_group
)
group_counts = tile_kernels.moe.group_count(group_idx, num_groups)
print(f"各 group token 数: {group_counts.tolist()}")

# 原地去重 group 索引
tile_kernels.moe.inplace_unique_group_indices(group_idx, num_groups)
print(f"去重后 group_idx: {group_idx[:5]}")

# Auxiliary load balancing loss
fi = tile_kernels.moe.aux_fi(topk_idx, num_experts, num_aux_topk=num_topk)
print(f"Load balance f_i (前5个): {fi[:5].tolist()}")
# aux_loss = fi * num_experts / num_topk (常用的负载均衡损失)
aux_loss = (fi * fi).sum() * num_experts / (num_topk * num_topk)
print(f"Aux loss: {aux_loss.item():.4f}")
```

---

## 完整 MoE 前向（简化版）

```python
def moe_forward(hidden_states, gate_weight, expert_weights, config):
    """
    简化版 MoE 前向计算
    hidden_states: (num_tokens, hidden_size) bf16
    gate_weight: (hidden_size, num_experts) fp32
    expert_weights: dict of gate_proj/up_proj/down_proj weights
    """
    num_tokens = hidden_states.shape[0]
    num_experts = config['num_experts']
    num_topk = config['num_topk']

    # 1. Gate
    logits = hidden_states.float() @ gate_weight.float()
    topk_idx, topk_weights = tile_kernels.moe.top2_sum_gate(
        logits, torch.zeros(num_experts, device=device),
        num_topk=num_topk,
        num_topk_groups=config.get('num_topk_groups', 4),
        num_groups=config.get('num_groups', 8),
        use_shared_as_routed=False,
        num_shared_experts=config.get('num_shared_experts', 0),
        routed_scaling_factor=config.get('routed_scaling_factor', 1.0),
        ep_rank=0, num_ep_ranks=1,
        tp_rank=0, num_tp_ranks=1,
        scoring_func='sigmoid',
    )

    # 2. Mapping
    mapping = tile_kernels.moe.get_fused_mapping(
        topk_idx, num_experts, num_expanded_tokens=0, alignment=128
    )
    (pos_to_expert, pos_to_token, pos_to_token_topk,
     token_topk_to_pos, expert_start, expert_end,
     num_tokens_per_expert, _) = mapping
    num_expanded = pos_to_expert.shape[0]

    # 3. Dispatch
    expanded = tile_kernels.moe.expand_to_fused(
        hidden_states, token_topk_to_pos, pos_to_expert
    )

    # 4. Expert FFN（使用 DeepGEMM grouped GEMM 替代此处模拟）
    expanded_output = torch.zeros_like(expanded)
    for eid in range(num_experts):
        s, e = expert_start[eid].item(), expert_end[eid].item()
        if s == e:
            continue
        x = expanded[s:e]
        # gate_up = x @ gate_up_weight[eid]  # DeepGEMM
        # act = silu(gate_up[:,:ffn]) * gate_up[:,ffn:]
        # out = act @ down_weight[eid]        # DeepGEMM
        # expanded_output[s:e] = out

    # 5. Combine
    output = tile_kernels.moe.reduce_fused(
        expanded_output, topk_weights, token_topk_to_pos
    )

    return output, topk_idx
```

---

## 性能提示

1. **使用 FP8**：dispatch 和 combine 都支持 QuantTensor，配合 DeepGEMM FP8 GEMM 可实现极致性能
2. **SwiGLU 融合**：使用 `swiglu_forward_and_per_token_cast` 融合 SwiGLU 激活和量化，减少一次显存读写
3. **SM 控制**：`tile_kernels.set_num_sms()` 控制 kernel 使用的 SM 数量，在多实例部署时有用
4. **对齐要求**：hidden_size 需满足各 kernel 的对齐约束（通常 64 或 256 对齐）
5. **与 DeepEP 配合**：多节点场景下，在 `get_fused_mapping` 之前使用 DeepEP 做跨节点 all-to-all dispatch，之后做 all-to-all combine
