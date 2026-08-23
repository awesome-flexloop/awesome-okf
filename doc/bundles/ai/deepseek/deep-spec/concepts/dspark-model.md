---
type: concept
scope: deep-spec
name: DSpark 模型架构
version: "1.0.0"
source: deepspec/modeling/dspark/common.py, deepspec/modeling/dspark/markov_head.py, deepspec/modeling/dspark/loss.py, deepspec/modeling/dspark/qwen3/modeling.py, deepspec/modeling/dspark/gemma4/modeling.py
description: DSpark 草稿模型的块级锚点采样、噪声嵌入、Markov 头（vanilla/gated/rnn）三种变体与多任务损失设计
---

# DSpark 模型架构

DSpark（DeepSeek Speculative）是 DeepSpec 框架的核心草稿模型架构之一，采用**块级锚点采样**（Block-level Anchor Sampling）+ **噪声嵌入**（Noise Embedding）+ **Markov 头**的设计，实现高效的并行块级预测。DSpark 支持 Qwen3 和 Gemma4 两大模型系列，并提供 vanilla、gated、rnn 三种 Markov 头变体。

---

## 一、核心设计思想

传统投机解码的草稿模型（如标准自回归 draft model）在训练时需要逐 token 自回归预测，训练效率受限。DSpark 的关键洞察是：**以块为单位进行并行预测，再通过 Markov 头捕捉块内 token 间的顺序依赖**。

这带来了两个核心优势：
1. **训练并行度高**：多个锚点块的前向计算完全并行，不需要顺序展开
2. **推理效率高**：Markov 头的计算量远小于完整 Transformer 层，块内自回归修正成本低

---

## 二、模型结构

### 2.1 整体架构

```
输入: input_ids, target_hidden_states, loss_mask
  │
  ├── 1. 锚点采样: sample_anchor_positions()
  │     从有效位置随机采样 num_anchors 个锚点
  │
  ├── 2. 噪声嵌入构造: create_noise_embed()
  │     block 起始=真实token embedding, 其余位置=[MASK] embedding
  │     形状: [B, num_anchors*block_size, hidden_size]
  │
  ├── 3. 目标隐状态投影
  │     extract_context_feature() → 多层target hidden拼接
  │     fc() → 投影到 hidden_size
  │     与噪声嵌入相加
  │
  ├── 4. Transformer Backbone
  │     embed_tokens → [fc投影 + 噪声嵌入]
  │     → N层 Qwen3DSparkDecoderLayer (flex_attention)
  │     → norm
  │     → lm_head → base_logits [B, num_anchors*block_size, V]
  │
  ├── 5. Markov 头修正
  │     markov_head.apply_block_logits(base_logits, token_ids, hidden_states)
  │     → draft_logits [B, num_anchors, block_size, V]
  │
  ├── 6. 置信度预测（可选）
  │     confidence_head(hidden_states) → confidence_pred [B, num_anchors, block_size]
  │
  └── 输出: DSparkForwardOutput
```

### 2.2 模型组件

```python
class Qwen3DSparkModel(Qwen3PreTrainedModel):
    def __init__(self, config):
        self.embed_tokens = nn.Embedding(...)       # 从目标模型拷贝，冻结
        self.fc = nn.Linear(...)                   # 投影拼接的多层 target hidden
        self.layers = nn.ModuleList([...])         # num_draft_layers 个 DecoderLayer
        self.norm = Qwen3RMSNorm(...)
        self.rotary_emb = Qwen3RotaryEmbedding(...)
        self.lm_head = nn.Linear(...)              # 从目标模型拷贝，冻结
        self.markov_head = build_markov_head(config)  # Markov 头（可能为None）
        self.confidence_head = AcceptRatePredictor(...) if enable_confidence_head else None
```

### 2.3 初始化策略

```python
def initialize_embeddings_and_head(self, embed_tokens, lm_head, freeze=True):
    """从目标模型拷贝嵌入层和lm_head权重"""
    self.embed_tokens.weight.copy_(embed_tokens.weight)
    self.lm_head.weight.copy_(lm_head.weight)
    if freeze:
        self.embed_tokens.requires_grad_(False)
        self.lm_head.requires_grad_(False)
```

- **embed_tokens 和 lm_head 直接从目标模型拷贝**，确保草稿模型和目标模型共享词表空间
- 默认冻结这两个参数，减少训练参数量
- Gemma4 版本使用 `Gemma4TextScaledWordEmbedding`（带 `embed_scale=sqrt(hidden_size)`）

---

## 三、块级锚点采样

### 3.1 采样算法

```python
def sample_anchor_positions(*, seq_len, loss_mask, num_anchors, device):
    # 1. 找出有效锚点位置：loss_mask[i] > 0.5 & loss_mask[i+1] > 0.5
    valid_positions = where(loss_mask[:-1] & loss_mask[1:])[0]
    
    # 2. 随机采样 num_anchors 个（有放回）
    anchor_positions = random.choice(valid_positions, size=(B, num_anchors))
    
    # 3. block_keep_mask 标记哪些 block 是完整的
    # （最后一个 anchor 可能因为序列不足 block_size 而被 mask 掉）
    return anchor_positions, block_keep_mask
```

锚点采样的设计原则：
- **锚点必须是有效 token**：锚点位置和其下一个位置都必须在 loss mask 内（即都是需要预测的 token）
- **随机采样**：每个训练步随机选择不同锚点，增加训练数据多样性
- **block_keep_mask**：当序列末尾不足一个完整 block 时，该 block 的 loss 被 mask 掉

### 3.2 采样数量

`num_anchors` 控制每个样本采样的锚点数量（典型值 512），决定了训练的并行度：
- 每个 anchor 对应一个 block，每个 block 预测 `block_size` 个 token
- 总预测 token 数 = `num_anchors × block_size`
- 更多锚点 → 更高并行度，但需要更多显存

---

## 四、噪声嵌入

### 4.1 构造方法

```python
def create_noise_embed(embed_tokens, input_ids, anchor_positions, block_keep_mask,
                       *, mask_token_id, block_size):
    B = anchor_positions.shape[0]
    num_anchors = anchor_positions.shape[1]
    
    # 1. 初始化所有位置为 mask_token_id
    noise_ids = full([B, num_anchors * block_size], mask_token_id)
    
    # 2. 每个 block 的起始位置替换为 anchor token
    for b in range(B):
        for a in range(num_anchors):
            pos = anchor_positions[b, a]
            noise_ids[b, a * block_size] = input_ids[b, pos]
    
    # 3. 通过 embed_tokens 获取嵌入
    noise_embed = embed_tokens(noise_ids)
    return noise_embed
```

### 4.2 设计直觉

噪声嵌入的设计灵感来自 masked language modeling（MLM）：
- block 起始位置是**已知的锚点 token**，模型从这个已知点开始预测后续 token
- 其余位置被替换为 `[MASK]`，模型需要根据锚点和上下文预测这些位置的 token
- 与 MLM 不同的是，DSpark 的目标是预测连续 block 内的所有 token（而非随机位置），并且有 Markov 头建模顺序依赖

---

## 五、Markov 头

Markov 头是 DSpark 的关键组件，用于捕捉块内 token 间的顺序依赖。它利用前一个 token 的低维嵌入来修正当前位置的 logits。

### 5.1 VanillaMarkov（基础版）

```python
class VanillaMarkov(nn.Module):
    def __init__(self, vocab_size, markov_rank):
        self.markov_w1 = nn.Embedding(vocab_size, markov_rank)  # 前一token → 低维嵌入
        self.markov_w2 = nn.Linear(markov_rank, vocab_size, bias=False)  # 低维嵌入 → vocab偏置
```

**工作原理**：
1. 获取前一个 token 的低维嵌入：`prev_emb = markov_w1(prev_token_id)`
2. 投影为 vocab 维偏置：`bias = markov_w2(prev_emb)`
3. 将偏置加到 base logits 上：`corrected_logits = base_logits + bias`

**Block 级修正（teacher forcing）**：
- 训练时，使用真实 token 作为 prev_token，teacher forcing 方式依次修正所有位置
- 从 base_logits 和真实 token_ids 出发，逐步为每个位置加上 Markov 偏置

**自回归采样（推理）**：
- 采样第一个 token 后，用该 token 的 embedding 修正第二个位置的 logits
- 再采样第二个 token，依此类推
- 这是一个轻量级的 RNN 式展开，计算量远小于 Transformer 层

### 5.2 GatedMarkovHead（门控版）

```python
class GatedMarkovHead(VanillaMarkov):
    def __init__(self, vocab_size, markov_rank, hidden_size):
        super().__init__(vocab_size, markov_rank)
        self.gate_proj = nn.Linear(hidden_size + markov_rank, markov_rank)
```

**工作原理**：
- 在 vanilla 基础上增加门控机制，融合隐状态和前一 token 嵌入
- `gate = sigmoid(gate_proj([hidden_states, prev_emb]))`
- `gated_emb = gate * prev_emb`
- 用门控后的嵌入计算偏置：`bias = markov_w2(gated_emb)`
- 门控允许模型根据当前隐状态动态调节 Markov 偏置的强度

### 5.3 RNNHead（RNN 版）

```python
class RNNHead(VanillaMarkov):
    def __init__(self, vocab_size, markov_rank, hidden_size):
        super().__init__(vocab_size, markov_rank)
        # GRU 风格循环
        self.joint_proj = nn.Linear(2 * markov_rank + hidden_size, 3 * markov_rank)
```

**工作原理**：
- 维护一个 RNN 状态（维度 = markov_rank），在 block 内逐步更新
- 每步输入：前一 token 嵌入（markov_rank）+ 当前 RNN 状态（markov_rank）+ 当前隐状态（hidden_size）
- 通过 GRU 门控（reset gate, update gate, new state）更新状态
- 从新状态投影得到 vocab 偏置
- RNN 状态携带了块内更早 token 的信息，建模更长距离的块内依赖

### 5.4 构建函数

```python
def build_markov_head(config):
    if config.markov_rank == 0:
        return None  # DFlash 模式
    if config.markov_head_type == "vanilla":
        return VanillaMarkov(config.vocab_size, config.markov_rank)
    elif config.markov_head_type == "gated":
        return GatedMarkovHead(config.vocab_size, config.markov_rank, config.hidden_size)
    elif config.markov_head_type == "rnn":
        return RNNHead(config.vocab_size, config.markov_rank, config.hidden_size)
```

---

## 六、多任务损失函数

DSpark 的总损失由三部分加权组成：

```
loss = ce_loss_alpha × CE_loss + l1_loss_alpha × L1_loss + confidence_head_alpha × Confidence_loss
```

### 6.1 CE Loss（交叉熵损失）

```python
# 可选指数衰减权重
weights = exp(-(position + 1) / loss_decay_gamma)  # 靠近锚点的位置权重更高

ce_loss = cross_entropy(
    draft_logits.reshape(-1, V),
    target_ids.reshape(-1),
    weight=weights,
    reduction="sum",
)
```

- 当 `loss_decay_gamma > 0` 时，靠近锚点的位置（block 前部）权重更高
- 这反映了直觉：越靠近已知锚点，预测应该越准确
- 典型配置：`ce_loss_alpha=0.1, loss_decay_gamma=4.0`

### 6.2 L1 Loss（分布对齐损失）

```python
draft_probs = softmax(draft_logits / temperature)
target_probs = softmax(aligned_target_logits / temperature)
l1_loss = |draft_probs - target_probs|.mean()
```

- 需要 `aligned_target_logits`（对齐的目标模型 logits），这需要额外缓存
- L1 损失鼓励 draft 模型的整个概率分布接近目标模型，而不仅仅是 argmax 正确
- 分布对齐对拒绝采样的接受率至关重要——即使 draft 的 top-1 预测正确，如果概率分布形状差异大，仍可能被拒绝
- 典型配置：`l1_loss_alpha=0.9`（比 CE 权重更高）

### 6.3 Confidence BCE Loss（置信度损失）

```python
# 置信度头预测每个 token 是否被接受
confidence_target = (draft_argmax == target_token).float()
confidence_loss = binary_cross_entropy_with_logits(confidence_pred, confidence_target)
```

- 训练一个二分类头预测每个位置的 token 是否会被目标模型接受
- 用于推理时的早停策略：当置信度低于阈值时，停止生成后续 draft token
- 典型配置：`confidence_head_alpha=1.0`

---

## 七、DSpark 推理流程

```
1. 从当前前缀出发，使用锚点 token 作为 block 起点
2. 构造噪声输入（第一个位置是已知 token，后续为 MASK）
3. Draft Transformer 前向 → base logits + hidden states
4. Markov 头自回归采样：
   for pos in range(block_size):
       corrected_logits = base_logits[pos] + markov_bias(prev_token, hidden_states[pos])
       draft_token[pos] = sample(corrected_logits, temperature)
       if confidence_head and confidence(pred) < threshold:
           break  # 早停
5. 构造 DraftProposal（token_ids + probs）
6. 目标模型验证（拒绝采样）
7. 接受的 token 追加到输出，更新 KV cache 和 target_hidden_states
```

---

## 八、DFlash 变体

DFlash 是 DSpark 的纯 CE 损失简化版，通过配置实现：
- `markov_rank = 0`：不构建 Markov 头（`build_markov_head` 返回 None）
- `confidence_head_alpha = 0.0`：无置信度头
- `ce_loss_alpha = 1.0, l1_loss_alpha = 0.0`：纯 CE 损失
- 训练器复用 `Qwen3DSparkTrainer`/`Gemma4DSparkTrainer`
- 推理时模型直接输出 base logits，无 Markov 修正

---

## 九、相关链接

- [/deepseek/deep-spec/concepts/overview](/ai/deepseek/deep-spec/concepts/overview) — DeepSpec 整体概述
- [/deepseek/deep-spec/concepts/speculative-decoding-training](/ai/deepseek/deep-spec/concepts/speculative-decoding-training) — 投机解码训练方法论
- [/deepseek/deep-spec/concepts/eagle3-model](/ai/deepseek/deep-spec/concepts/eagle3-model) — Eagle3 架构对比
- [/deepseek/deep-spec/concepts/training-pipeline](/ai/deepseek/deep-spec/concepts/training-pipeline) — 训练管线详解
- [/deepseek/deep-spec/references/model-api](/ai/deepseek/deep-spec/references/model-api) — 模型 API 参考（Markov 头、损失函数完整签名）
- [/deepseek/deep-spec/examples/training-dspark](/ai/deepseek/deep-spec/examples/training-dspark) — DSpark 训练示例
