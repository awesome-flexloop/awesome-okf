---
type: concept
scope: deep-spec
name: Eagle3 模型架构
version: "1.0.0"
source: deepspec/modeling/eagle3/common.py, deepspec/modeling/eagle3/loss.py, deepspec/modeling/eagle3/qwen3/modeling.py, deepspec/modeling/eagle3/gemma4/modeling.py
description: Eagle3 草稿模型的5层目标隐状态拼接、单层draft架构、TTT自回归训练、FusedLogSoftmaxLoss与KV cache复用机制
---

# Eagle3 模型架构

Eagle3 是 DeepSpec 框架中基于 EAGLE-3 风格设计的草稿模型架构。与 DSpark 的块级并行预测不同，Eagle3 采用 **TTT（Test-Time Training）自回归** 范式，通过单层 Transformer draft 模型在目标隐状态特征上做多步自回归预测，配合 Triton 融合的 soft 交叉熵损失实现高效训练。

---

## 一、核心设计思想

Eagle3 的设计基于以下关键洞察：

1. **目标隐状态是强特征**：目标模型中间层的 hidden states 包含了预测下一个 token 的丰富信息，直接利用这些特征可以大幅降低草稿模型的复杂度
2. **单层 draft 足够**：在目标隐状态的基础上，仅需 1 层 Transformer 即可达到高接受率
3. **训练时模拟推理**：TTT（Test-Time Training）范式让训练过程与推理过程一致——都在 block 内自回归生成，减小训练-推理差距
4. **软标签蒸馏**：使用目标模型的完整概率分布（软标签）而非硬标签，提供更丰富的监督信号

---

## 二、模型结构

### 2.1 整体架构

```
输入: hidden_states (目标隐状态), input_ids
  │
  ├── 1. 特征提取: extract_eagle3_context_feature()
  │     从5个指定 decoder 层提取 hidden states
  │     在特征维度拼接 → [B, seq_len, 5*hidden_size]
  │
  ├── 2. 特征投影: fc()
  │     5*hidden_size → hidden_size
  │
  ├── 3. Token 嵌入: embed_tokens(input_ids)
  │     从目标模型拷贝，冻结
  │
  ├── 4. 输入拼接
  │     [token_embed; projected_hidden] → hidden_size*2
  │
  ├── 5. Draft Transformer（1层）
  │     Qwen3Eagle3DecoderLayer / Gemma4Eagle3DecoderLayer
  │     输入/输出维度: hidden_size*2 → hidden_size
  │     使用 flex_attention
  │
  ├── 6. 输出归一化: norm()
  │
  ├── 7. LM Head: lm_head()
  │     从目标模型拷贝，冻结
  │     → draft_logits [B, seq_len, V]
  │
  └── 输出: Eagle3ForwardOutput(hidden_states, draft_logits, target_logits)
```

### 2.2 关键组件

```python
class Qwen3Eagle3Model(Qwen3PreTrainedModel):
    def __init__(self, config):
        self.embed_tokens = nn.Embedding(...)       # 从目标模型拷贝，冻结
        self.fc = nn.Linear(5 * hidden_size, hidden_size, bias=False)  # 5层隐状态投影
        self.layers = nn.ModuleList([...])          # draft_num_hidden_layers 层（典型1层）
        self.norm = Qwen3RMSNorm(...)
        self.rotary_emb = Qwen3RotaryEmbedding(...)
        self.lm_head = nn.Linear(...)               # 从目标模型拷贝，冻结
```

### 2.3 与 DSpark 的结构差异

| 方面 | DSpark | Eagle3 |
|---|---|---|
| 目标层数 | 可配置（含 -1 embedding 层） | 固定 5 层（decoder 层，不含 embedding） |
| 输入构造 | 噪声嵌入（mask token） | token embedding + 目标隐状态拼接 |
| 草稿层数 | 可配置（典型5层） | 固定1层 |
| 注意力输入维度 | hidden_size | hidden_size × 2 |
| 自回归机制 | Markov 头（Transformer 外） | TTT（Transformer 内自回归展开） |
| 损失函数 | CE + L1 + BCE | TTT 多步 soft CE（FusedLogSoftmaxLoss） |

---

## 三、目标隐状态拼接

### 3.1 层级选择

Eagle3 要求从目标模型提取**恰好5个** decoder 层的 hidden states：

```python
def validate_eagle3_target_layer_ids(layer_ids, num_target_layers):
    assert len(layer_ids) == 5, "Eagle3 requires exactly 5 target layers"
    assert all(0 <= lid < num_target_layers for lid in layer_ids), "No -1 embedding layer"
    assert layer_ids == sorted(layer_ids), "Must be strictly increasing"
```

典型配置（Qwen3-8B，共36层）：`target_layer_ids = [1, 9, 17, 25, 33]`
- 均匀分布在模型深度上，捕获不同抽象层级的特征
- 不包含最后一层（避免与 lm_head 冗余）
- 不支持 -1（embedding 层），与 DSpark 不同

### 3.2 特征提取与投影

```python
def extract_eagle3_context_feature(hidden_states, layer_ids):
    # hidden_states 是 tuple，包含 embedding 输出 + 每层输出
    # index 0 = embedding, index 1 = layer 0, index N+1 = layer N-1
    features = []
    for lid in layer_ids:
        features.append(hidden_states[lid + 1])  # +1 因为 index 0 是 embedding
    return torch.cat(features, dim=-1)  # [B, seq_len, 5*hidden_size]
```

投影层 `fc: 5*hidden_size → hidden_size` 将拼接的多层特征映射到模型维度。这是 Eagle3 中**唯一需要从头训练的投影层**之一。

---

## 四、双维度输入与注意力

### 4.1 输入拼接

Eagle3 的注意力层输入维度是 `hidden_size × 2`：

```python
# hidden_states: 来自 fc 投影的目标隐状态 [B, seq_len, hidden_size]
# input_embeds: token embedding [B, seq_len, hidden_size]
attn_input = torch.cat([input_embeds, hidden_states], dim=-1)  # [B, seq_len, 2*hidden_size]
```

这种设计让 draft 模型同时看到：
- **Token 身份**（通过 input_embeds）：当前 token 是什么
- **目标模型语义**（通过 projected_hidden）：目标模型认为当前位置的语义表示是什么

### 4.2 Eagle3 Attention

```python
class Qwen3Eagle3Attention(nn.Module):
    def __init__(self, config, layer_idx):
        # 输入维度为 hidden_size * 2
        self.q_proj = nn.Linear(2 * hidden_size, num_heads * head_dim, bias=True)
        self.k_proj = nn.Linear(2 * hidden_size, num_kv_heads * head_dim, bias=True)
        self.v_proj = nn.Linear(2 * hidden_size, num_kv_heads * head_dim, bias=True)
        self.o_proj = nn.Linear(num_heads * head_dim, hidden_size, bias=False)
        # Qwen3RMSNorm 对 q/k 归一化
        self.q_norm = Qwen3RMSNorm(head_dim)
        self.k_norm = Qwen3RMSNorm(head_dim)
```

输出维度为 `hidden_size`（而非 2×hidden_size），因为 draft 模型只需要输出下一个 token 的隐状态表示。

### 4.3 注意力后端

Eagle3 支持三种注意力实现：
- **flex_attention**（默认）：q_len ≤ 128 用原生实现，否则使用编译版本（推荐）
- **SDPA**：PyTorch 原生 scaled dot-product attention（评估时使用）
- **eager**：纯 PyTorch 实现（调试用）

---

## 五、TTT（Test-Time Training）自回归

### 5.1 TTT 核心思想

TTT 的核心是**训练和推理使用相同的自回归过程**：

- **推理时**：draft 模型自回归生成 γ 个候选 token，每个 token 都经过 draft 模型的 Transformer 层
- **训练时**：模拟这个过程——在 block 内逐步自回归，每步都计算损失，使模型适应自回归生成

这与 DSpark 的"Transformer 一次出全部 base logits + Markov 头修正"方式截然不同。

### 5.2 TTT 注意力掩码（BlockMask）

TTT 自回归需要特殊的注意力掩码：

```
位置:     [前缀]  [d_0]  [d_1]  [d_2]  ...  [d_{γ-1}]
前缀:     [████████████████████████████████████]
d_0:      [████████]
d_1:      [███████████]       (可见前缀 + d_0 suffix 位置)
d_2:      [████████████████]  (可见前缀 + d_0,d_1 suffix 位置)
...
```

- **Causal 部分**：所有位置可见前缀（prompt 部分）
- **Suffix 部分**：第 t 步 draft token 可见前 t 个 draft 位置的 key-value
- 这通过 `create_eagle3_attention_mask` 创建 BlockMask 实现

```python
def create_eagle3_attention_mask(*, attention_mask, q_len, kv_len, lck, device):
    # lck = length of cached key-value (前缀长度)
    # 创建 BlockMask:
    # - [0:lck, 0:kv_len] 完全可见（前缀的causal注意力）
    # - [lck:, 0:lck] 可见（draft看前缀）
    # - [lck+i, lck+i] draft位置的对角线可见（每步看自己位置）
    ...
```

### 5.3 TTT 训练循环

```python
def compute_eagle3_loss(*, model, batch, ttt_length, step_loss_decay):
    total_loss = 0
    # 初始隐状态：从目标模型隐状态投影
    hidden = model.fc(extract_eagle3_context_feature(...))
    
    for step in range(ttt_length):
        # 1. 前向计算 draft logits（使用 KV cache 复用）
        outputs = model(
            hidden_states=hidden,
            input_ids=current_ids,
            past_key_values=past_kv,
            use_cache=True,
            return_logits=True,
        )
        
        # 2. 计算 soft CE loss（FusedLogSoftmaxLoss）
        target_p = softmax(target_logits[step] / temperature)
        step_loss = FusedLogSoftmaxLoss.apply(outputs.draft_logits, target_p, normalizer)
        
        # 3. 指数衰减加权
        total_loss += step_loss * (step_loss_decay ** step)
        
        # 4. 准备下一步输入（使用目标token做teacher forcing）
        hidden = outputs.hidden_states
        current_ids = target_ids[step]
        
        # 5. 记录指标
        record_accuracy(...)
        record_accept_rate(...)
    
    return total_loss
```

关键设计：
- **KV cache 复用**：每步复用前几步的 KV，避免重复计算前缀注意力
- **Teacher forcing**：训练时每步输入使用真实的目标 token（而非模型自己采样的 token）
- **指数衰减加权**：`step_loss_decay^step` 使得越靠后的步权重越低（越难预测，降低对训练早期的干扰）
- **FusedLogSoftmaxLoss**：使用 Triton 融合的 soft CE 损失，前向反向都高效

---

## 六、FusedLogSoftmaxLoss

### 6.1 设计动机

标准 PyTorch 的 `cross_entropy` 有两个局限：
1. 只支持硬标签（one-hot），不支持软标签（概率分布）
2. 没有融合 log_softmax 和 cross-entropy 的 backward，产生额外的内存开销

Eagle3 需要软标签（目标模型完整概率分布），因此使用自定义 Triton 核函数。

### 6.2 实现

```python
class FusedLogSoftmaxLoss(torch.autograd.Function):
    @staticmethod
    def forward(ctx, logits, targets, normalizer):
        """
        logits: [N, V] - draft 模型输出的 logits
        targets: [N, V] - 目标模型的概率分布（软标签）
        normalizer: float - 归一化因子
        
        计算: -sum(targets * log_softmax(logits)) / normalizer
              = -sum(targets * (logits - logsumexp(logits))) / normalizer
        """
        # Triton kernel:
        # 1. 计算 log_softmax: logits - max_logit - log(sum(exp(logits - max_logit)))
        # 2. 点乘 targets 并求和
        # 3. 保存 log_softmax 输出用于 backward
        ...
    
    @staticmethod
    def backward(ctx, grad_output):
        """
        梯度: (softmax(logits) - targets) / normalizer * grad_output
        原地写入 logits 的 grad 存储
        """
        ...
```

### 6.3 Triton 核参数

- **BLOCK_SIZE**：根据 vocab 大小动态选择（最大 131072），确保一个 block 能覆盖整个 vocab 维度
- **num_warps**：根据 BLOCK_SIZE 自动调整
- **原地梯度写入**：backward 直接将梯度写入 logits 张量的存储，减少内存分配

---

## 七、Gemma4 特有特性

Gemma4 版本的 Eagle3 模型有以下差异：

| 特性 | Qwen3 版本 | Gemma4 版本 |
|---|---|---|
| Embedding | nn.Embedding | Gemma4TextScaledWordEmbedding（embed_scale=√h） |
| RoPE | Qwen3RotaryEmbedding | Gemma4TextRotaryEmbedding |
| Norm | Qwen3RMSNorm | Gemma4RMSNorm |
| Logit capping | 无 | `final_logit_softcapping`（tanh 缩放） |
| FFN norms | 后置 LayerNorm | pre_feedforward + post_feedforward layernorm |
| Layer scalar | 无 | 可学习的 `layer_scalar` |
| K/V 共享 | 独立 k_proj/v_proj | `attention_k_eq_v=True` 时 v_proj=None（v=k） |
| MoE 支持 | 无 | `enable_moe_block` 配置 |

---

## 八、Eagle3 推理流程

```
1. 预填充阶段：
   - 将 prompt 输入目标模型和 draft 模型
   - 缓存 draft 模型的 KV cache（shifted prompt ids）
   - 提取目标模型隐状态

2. Draft 生成阶段（TTT 自回归）:
   for step in range(ttt_length):
       a. 将当前 token embedding + 目标隐状态输入 draft 模型
       b. 使用 KV cache 避免重复计算
       c. 获取 draft logits，采样一个 token
       d. 更新 KV cache
       e. 如果所有 token 生成完毕，break

3. 构造 DraftProposal
   - draft_token_count = 生成的 token 数
   - verify_input_ids = [前缀 + draft_tokens]
   - draft_probs = 每步的采样概率

4. 目标模型验证（拒绝采样，同 DSpark）

5. 更新阶段：
   - 裁剪 draft KV cache 到接受位置
   - Extend 已接受 token 的 KV
   - 更新目标隐状态
```

---

## 九、相关链接

- [/deepseek/deep-spec/concepts/overview](/ai/deepseek/deep-spec/concepts/overview) — DeepSpec 整体概述
- [/deepseek/deep-spec/concepts/speculative-decoding-training](/ai/deepseek/deep-spec/concepts/speculative-decoding-training) — 投机解码训练方法论
- [/deepseek/deep-spec/concepts/dspark-model](/ai/deepseek/deep-spec/concepts/dspark-model) — DSpark 架构对比
- [/deepseek/deep-spec/references/model-api](/ai/deepseek/deep-spec/references/model-api) — 模型 API 参考（FusedLogSoftmaxLoss、模型类完整签名）
- [/deepseek/deep-spec/concepts/training-pipeline](/ai/deepseek/deep-spec/concepts/training-pipeline) — 训练管线详解
