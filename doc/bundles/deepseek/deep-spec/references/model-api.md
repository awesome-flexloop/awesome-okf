---
type: api-reference
scope: deep-spec
name: DeepSpec 模型 API 参考
version: "1.0.0"
source: deepspec/modeling/dspark/, deepspec/modeling/eagle3/, deepspec/modeling/dspark/loss.py, deepspec/modeling/eagle3/loss.py
description: DeepSpec DSpark/Eagle3/DFlash 模型类、Markov 头、FusedLogSoftmaxLoss 完整 API 参考
---

# DeepSpec 模型 API 参考

DeepSpec 的模型层包含 DSpark 和 Eagle3 两大草稿模型家族，各自提供 Qwen3 和 Gemma4 两个后端实现。模型核心包括 DSpark 的块级预测 + Markov 头机制，以及 Eagle3 的 TTT 自回归 + 融合损失机制。

---

## 一、模型输出数据类

### 1.1 `DSparkForwardOutput`

```python
@dataclass
class DSparkForwardOutput:
    draft_logits: torch.Tensor           # [B, num_anchors, block_size, V] 草稿 logits
    target_ids: torch.Tensor             # [B, num_anchors, block_size] 目标 token ID
    eval_mask: torch.Tensor              # [B, num_anchors, block_size] 评估 mask
    block_keep_mask: torch.Tensor        # [B, num_anchors] block 有效 mask
    confidence_pred: torch.Tensor | None # [B, num_anchors, block_size] 置信度预测（可选）
    aligned_target_logits: torch.Tensor | None  # [B, num_anchors, block_size, V] 对齐的目标 logits（可选）
```

### 1.2 `Eagle3ForwardOutput`

```python
@dataclass
class Eagle3ForwardOutput:
    hidden_states: torch.Tensor          # 模型输出隐状态
    draft_logits: torch.Tensor           # 草稿 logits
    target_logits: torch.Tensor | None   # 目标 logits（可选，用于快速计算）
```

---

## 二、DSpark 模型

### 2.1 `Qwen3DSparkModel`

```python
class Qwen3DSparkModel(Qwen3PreTrainedModel):
    def __init__(self, config):
        """
        Qwen3 版本 DSpark 草稿模型。
        
        组件：
        - embed_tokens: nn.Embedding（从目标模型拷贝，冻结）
        - fc: nn.Linear（投影拼接的多层 target hidden）
        - layers: ModuleList[Qwen3DSparkDecoderLayer]（草稿 transformer 层）
        - norm: Qwen3RMSNorm
        - rotary_emb: Qwen3RotaryEmbedding
        - lm_head: nn.Linear（从目标模型拷贝，冻结）
        - markov_head: VanillaMarkov | GatedMarkovHead | RNNHead | None
        - confidence_head: AcceptRatePredictor | None
        """
        ...
    
    def initialize_embeddings_and_head(self, embed_tokens, lm_head, freeze=True):
        """从目标模型拷贝嵌入层和 lm_head 权重，可选冻结"""
        ...
    
    def forward(
        self,
        input_ids: torch.Tensor,
        target_hidden_states: torch.Tensor,
        loss_mask: torch.Tensor,
        target_last_hidden_states: torch.Tensor | None = None,
    ) -> DSparkForwardOutput:
        """
        前向传播：
        1. sample_anchor_positions：采样锚点位置
        2. create_noise_embed：构造噪声嵌入
        3. 构造 position_ids 和 attention mask
        4. _forward_backbone：transformer 前向
        5. reshape 输出，gather target_ids
        6. markov_head 修正 logits
        7. confidence_head 预测接受率
        """
        ...
```

### 2.2 `Gemma4DSparkModel`

```python
class Gemma4DSparkModel(Gemma4PreTrainedModel):
    def __init__(self, config):
        """
        Gemma4 版本 DSpark 草稿模型。
        结构与 Qwen3DSparkModel 类似，使用 Gemma4 特有组件：
        - Gemma4TextScaledWordEmbedding（embed_scale=sqrt(hidden_size)）
        - Gemma4RMSNorm
        - Gemma4 特有 attention 配置（num_global_key_value_heads, global_head_dim 等）
        """
        ...
    
    def forward(
        self,
        input_ids: torch.Tensor,
        target_hidden_states: torch.Tensor,
        loss_mask: torch.Tensor,
        target_last_hidden_states: torch.Tensor | None = None,
    ) -> DSparkForwardOutput:
        """与 Qwen3DSparkModel 前向逻辑一致"""
        ...
```

### 2.3 `Qwen3DSparkDecoderLayer`

```python
class Qwen3DSparkDecoderLayer(nn.Module):
    """DSpark 专用 Transformer 解码层，使用 flex_attention 实现"""
    ...
```

### 2.4 `Qwen3DSparkAttention`

```python
class Qwen3DSparkAttention(nn.Module):
    """DSpark 注意力层，支持 flex_attention 后端"""
    ...
```

---

## 三、Eagle3 模型

### 3.1 `Qwen3Eagle3Model`

```python
class Qwen3Eagle3Model(Qwen3PreTrainedModel):
    def __init__(self, config):
        """
        Qwen3 版本 Eagle3 草稿模型。
        
        必需配置字段：
        - target_layer_ids: list[int]（恰好5个目标层）
        - ttt_length: int（TTT 自回归步数）
        - step_loss_decay: float（步间损失衰减系数）
        
        组件：
        - embed_tokens: nn.Embedding（从目标模型拷贝，冻结）
        - fc: nn.Linear（投影5层拼接 hidden → hidden_size）
        - layers: ModuleList[Qwen3Eagle3DecoderLayer]（通常1层）
        - norm: Qwen3RMSNorm
        - rotary_emb: Qwen3RotaryEmbedding
        - lm_head: nn.Linear（从目标模型拷贝，冻结）
        """
        ...
    
    def initialize_embeddings_and_head(self, embed_tokens, lm_head, freeze=True):
        """从目标模型拷贝嵌入层和 lm_head 权重"""
        ...
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        input_ids: torch.Tensor,
        position_ids: torch.Tensor | None = None,
        attention_mask=None,
        past_key_values=None,
        use_cache: bool = False,
        return_logits: bool = False,
        rope_cache_step_offset: int | bool = False,
        target_logits_only: bool = False,
    ) -> Eagle3ForwardOutput | tuple:
        """
        前向传播支持三种模式：
        1. target_logits_only=True：快速计算目标 logits（仅投影+lm_head）
        2. return_logits=True：完整前向，返回 Eagle3ForwardOutput
        3. 训练模式：TTT 自回归循环
        """
        ...
```

### 3.2 `Gemma4Eagle3Model`

```python
class Gemma4Eagle3Model(Gemma4PreTrainedModel):
    def __init__(self, config):
        """
        Gemma4 版本 Eagle3 草稿模型。
        特有组件：
        - Gemma4TextScaledWordEmbedding（embed_scale=sqrt(hidden_size)）
        - Gemma4TextRotaryEmbedding
        - Gemma4RMSNorm
        - final_logit_softcapping 支持（通过 _softcap_logits 应用 tanh 缩放）
        - DecoderLayer 包含 pre_feedforward_layernorm/post_feedforward_layernorm
        - 可学习的 layer_scalar
        - v_proj 在 attention_k_eq_v=True 时为 None（v=k）
        """
        ...
```

### 3.3 `Qwen3Eagle3Attention`

```python
class Qwen3Eagle3Attention(nn.Module):
    def __init__(self, config, layer_idx: int):
        """
        Eagle3 注意力层。
        
        关键特征：
        - 输入维度为 hidden_size * 2（拼接 input_embeds 和 hidden_states）
        - q/k/v 投影输入维度均为 hidden_size * 2
        - 支持 flex_attention（q_len ≤ 128 用原生，否则编译）和 SDPA/eager 后端
        - 使用 Qwen3RMSNorm 对 q/k 归一化
        """
        ...
```

---

## 四、Markov 头

### 4.1 `VanillaMarkov`

```python
class VanillaMarkov(nn.Module):
    def __init__(self, vocab_size: int, markov_rank: int):
        """
        基础 Markov 头：
        - markov_w1: nn.Embedding(vocab_size, markov_rank) — 前一token低维嵌入
        - markov_w2: nn.Linear(markov_rank, vocab_size, bias=False) — 投影为vocab维偏置
        """
        ...
    
    def get_prev_embeddings(self, token_ids: torch.Tensor) -> torch.Tensor:
        """返回前一token的低维 markov 嵌入"""
        ...
    
    def apply_step_logits(
        self,
        logits: torch.Tensor,
        token_ids: torch.Tensor,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """将 markov 偏置加到单步 logits 上"""
        ...
    
    def apply_block_logits(
        self,
        base_logits: torch.Tensor,
        token_ids: torch.Tensor,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """对 block 内所有位置应用 markov 偏置（teacher forcing）"""
        ...
    
    def sample_block_tokens(
        self,
        base_logits: torch.Tensor,
        first_prev_token_ids: torch.Tensor,
        hidden_states: torch.Tensor,
        temperature: float,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """自回归采样 block 内 token，返回 (sampled_tokens, corrected_logits)"""
        ...
```

### 4.2 `GatedMarkovHead`

```python
class GatedMarkovHead(VanillaMarkov):
    def __init__(self, vocab_size: int, markov_rank: int, hidden_size: int):
        """
        门控 Markov 头：
        - 额外 gate_proj: nn.Linear(hidden_size + markov_rank, markov_rank)
        - 通过 sigmoid 门控融合前一token嵌入和隐状态
        """
        ...
    
    def compute_gate(self, token_ids, hidden_states):
        """计算门控值：sigmoid(gate_proj([hidden, prev_embed]))"""
        ...
    
    def compute_step_bias(self, token_ids, hidden_states):
        """使用门控后的嵌入计算偏置"""
        ...
```

### 4.3 `RNNHead`

```python
class RNNHead(VanillaMarkov):
    def __init__(self, vocab_size: int, markov_rank: int, hidden_size: int):
        """
        RNN 风格 Markov 头：
        - joint_proj: nn.Linear(2*markov_rank + hidden_size, 3*markov_rank)
        - 实现 GRU 风格循环：reset gate, update gate, new state
        """
        ...
    
    def _rnn_step(
        self,
        state: torch.Tensor,
        prev_embeddings: torch.Tensor,
        hidden_states: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """单步 RNN 更新，返回 (new_state, bias)"""
        ...
    
    def apply_block_logits(self, base_logits, token_ids, hidden_states):
        """block 内展开 RNN 逐步应用偏置（teacher forcing）"""
        ...
    
    def sample_block_tokens(self, base_logits, first_prev_token_ids, hidden_states, temperature):
        """自回归采样时维护 RNN 状态"""
        ...
```

### 4.4 `build_markov_head`

```python
def build_markov_head(config) -> nn.Module | None:
    """
    根据配置构建 Markov 头：
    - markov_rank == 0 → 返回 None（DFlash 模式）
    - markov_head_type == "vanilla" → VanillaMarkov
    - markov_head_type == "gated" → GatedMarkovHead
    - markov_head_type == "rnn" → RNNHead
    """
    ...
```

---

## 五、公共工具模块

### 5.1 `AcceptRatePredictor`

```python
class AcceptRatePredictor(nn.Module):
    def __init__(self, input_dim: int):
        """置信度/接受率预测头：单个 nn.Linear(input_dim, 1) 投影层"""
        self.proj = nn.Linear(input_dim, 1)
    
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """返回 squeeze(-1) 后的置信度预测"""
        ...
```

### 5.2 `extract_context_feature`

```python
def extract_context_feature(
    hidden_states: tuple[torch.Tensor],
    layer_ids: list[int],
) -> torch.Tensor:
    """
    从 hidden_states 元组中按 layer_ids 选择指定层，在最后一维拼接。
    -1 表示 embedding 输出（index 0），其他 layer_id 使用 index+1。
    """
    ...
```

### 5.3 `validate_target_layer_ids`

```python
def validate_target_layer_ids(
    layer_ids: list[int],
    num_target_layers: int,
):
    """校验 layer_ids：非空、严格递增、在 {-1} ∪ [0, num_target_layers-1] 范围内"""
    ...
```

### 5.4 `validate_eagle3_target_layer_ids`

```python
def validate_eagle3_target_layer_ids(
    layer_ids: list[int],
    num_target_layers: int,
):
    """Eagle3 版本：要求恰好5个目标层，严格递增，在 [0, num_target_layers-1] 范围内（不支持 -1）"""
    ...
```

### 5.5 `sample_anchor_positions`

```python
def sample_anchor_positions(
    *,
    seq_len: int,
    loss_mask: torch.Tensor,
    num_anchors: int,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    从满足 loss_mask[i] > 0.5 & loss_mask[i+1] > 0.5 的有效锚点位置中
    随机采样 num_anchors 个，返回 (anchor_positions, block_keep_mask)。
    anchor_positions: [B, num_anchors]
    block_keep_mask: [B, num_anchors]
    """
    ...
```

### 5.6 `create_noise_embed`

```python
def create_noise_embed(
    embed_tokens: nn.Embedding,
    input_ids: torch.Tensor,
    anchor_positions: torch.Tensor,
    block_keep_mask: torch.Tensor,
    *,
    mask_token_id: int,
    block_size: int,
) -> torch.Tensor:
    """
    构造噪声嵌入：
    - 形状 [B, num_anchors*block_size] 的 noise_ids
    - 初始填充 mask_token_id
    - 每个 block 起始位置替换为 anchor token
    - 通过 embed_tokens 得到噪声嵌入
    """
    ...
```

### 5.7 `create_eagle3_attention_mask`

```python
def create_eagle3_attention_mask(
    *,
    attention_mask: torch.Tensor,
    q_len: int,
    kv_len: int,
    lck: int,
    device: torch.device,
):
    """
    创建 Eagle3 TTT 专用 BlockMask：
    - causal 部分可见前文
    - suffix 部分每 TTT 步可见对应位置的 draft token
    - q_len ≤ 128 时使用 eager create_block_mask，否则使用编译版本
    """
    ...
```

---

## 六、损失函数

### 6.1 `compute_dspark_loss`

```python
def compute_dspark_loss(
    *,
    outputs: DSparkForwardOutput,
    loss_decay_gamma: float,
    ce_loss_alpha: float,
    l1_loss_alpha: float,
    confidence_head_alpha: float,
) -> torch.Tensor:
    """
    计算 DSpark 训练损失：
    
    1. CE Loss：交叉熵损失，可选指数衰减权重 exp(-pos/gamma)
       - loss_decay_gamma > 0 时，位置 i 的权重为 exp(-(i+1)/loss_decay_gamma)
    2. L1 Loss（可选）：draft_probs 与 target_probs 的 L1 距离
       - 需要 outputs.aligned_target_logits 不为 None
    3. Confidence BCE Loss（可选）：置信度预测的二元交叉熵
       - 需要 outputs.confidence_pred 不为 None
    
    通过 all_reduce 同步分母，返回加权总和 × world_size 作为反向传播损失。
    """
    ...
```

### 6.2 `FusedLogSoftmaxLoss`

```python
class FusedLogSoftmaxLoss(torch.autograd.Function):
    """
    Triton 融合的 soft 交叉熵损失（自定义 autograd Function）。
    
    Forward：计算 -sum(target_p * log_softmax(logits)) / normalizer
    Backward：原地写入梯度到 logits 存储，减少内存占用
    
    Triton 内核参数：
    - BLOCK_SIZE：根据 vocab 大小动态选择（最大 131072）
    - num_warps：根据 BLOCK_SIZE 调整
    """
    
    @staticmethod
    def forward(ctx, logits, targets, normalizer):
        """
        logits: [N, V] 输入 logits
        targets: [N, V] 目标概率分布（软标签）
        normalizer: float 归一化因子
        返回: scalar loss
        """
        ...
    
    @staticmethod
    def backward(ctx, grad_output):
        """原地计算梯度，写入 logits 存储"""
        ...
```

### 6.3 `compute_eagle3_loss`

```python
def compute_eagle3_loss(
    *,
    model: nn.Module,
    batch: dict,
    ttt_length: int,
    step_loss_decay: float,
) -> torch.Tensor:
    """
    计算 Eagle3 TTT 训练损失：
    
    1. TTT 自回归训练循环（ttt_length 步）
    2. 每步调用 model forward 得到 draft_logits
    3. 使用 FusedLogSoftmaxLoss 计算与 target_probs 的 soft CE loss
    4. 按 step_loss_decay^step_idx 指数衰减加权求和
    5. 支持 KV cache 复用加速多步推理
    6. 记录每步 accuracy/accept_rate/valid_tokens 指标
    7. 记录前缀 tau_greedy/tau_probabilistic 指标
    """
    ...
```

---

## 七、配置构建函数

### 7.1 DSpark 配置

```python
# Qwen3
def build_qwen3_draft_config(target_config, model_args) -> PretrainedConfig:
    """
    深度拷贝 target_config，设置：
    - architectures=["Qwen3DSparkModel"]
    - num_hidden_layers=num_draft_layers
    - layer_types=["full_attention"]*num_draft_layers
    - block_size, mask_token_id, target_layer_ids, num_anchors
    - enable_confidence_head, markov_rank, markov_head_type, confidence_head_with_markov
    - attn_implementation="flex_attention"
    """
    ...

# Gemma4
def build_gemma4_draft_config(target_config, model_args) -> PretrainedConfig:
    """
    从 Gemma4 统一模型提取 text_config，设置与 Qwen3 相同的字段，
    额外处理 num_global_key_value_heads, global_head_dim, attention_k_eq_v, enable_moe_block。
    """
    ...
```

### 7.2 Eagle3 配置

```python
# Qwen3
def build_qwen3_eagle3_config(*, target_config, model_args) -> PretrainedConfig:
    """
    深度拷贝 target_config，设置：
    - architectures=["Qwen3Eagle3Model"]
    - num_target_layers, num_hidden_layers=draft_num_hidden_layers
    - layer_types=["full_attention"]*draft_num_hidden_layers
    - target_layer_ids, ttt_length, step_loss_decay
    - tie_word_embeddings=False
    - _attn_implementation="flex_attention"
    """
    ...

# Gemma4
def build_gemma4_eagle3_config(*, target_config, model_args) -> PretrainedConfig:
    """
    从 Gemma4 统一模型提取 text_config，校验25个必需字段后设置 draft config，
    额外包含 target_model_type, target_text_model_type, num_global_key_value_heads, global_head_dim。
    """
    ...
```

---

## 八、DFlash 变体

DFlash 没有独立的模型类，通过配置实现：
- 使用 `Qwen3DSparkTrainer` / `Gemma4DSparkTrainer` 作为训练器
- 设置 `markov_rank=0`（不构建 Markov 头）
- 设置 `confidence_head_alpha=0.0`、`ce_loss_alpha=1.0`、`l1_loss_alpha=0.0`
- 即纯 CE 损失、无 Markov 头、无置信度头的简化 DSpark

---

## 九、相关链接

- [/deepseek/deep-spec/concepts/dspark-model](/deepseek/deep-spec/concepts/dspark-model) — DSpark 架构详解
- [/deepseek/deep-spec/concepts/eagle3-model](/deepseek/deep-spec/concepts/eagle3-model) — Eagle3 架构详解
- [/deepseek/deep-spec/concepts/speculative-decoding-training](/deepseek/deep-spec/concepts/speculative-decoding-training) — 投机解码训练方法论
- [/deepseek/deep-spec/references/training-api](/deepseek/deep-spec/references/training-api) — 训练 API 参考
- [/deepseek/deep-spec/references/eval-api](/deepseek/deep-spec/references/eval-api) — 评估 API 参考
