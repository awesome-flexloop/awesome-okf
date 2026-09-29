---
type: reference
scope: engram
name: module-api
description: Engram 模块 API 参考——配置类、核心组件、前向传播接口
---

# 模块 API 参考

本文档基于仓库提供的 `engram_demo_v1.py` 演示实现，介绍 Engram 模块的核心 API。

> ⚠️ 注意：`engram_demo_v1.py` 是演示版本，对 Attention/MoE/mHC 等组件做了简化（mock），仅展示 Engram 模块的核心数据流。

## 配置类

### EngramConfig

```python
@dataclass
class EngramConfig:
    tokenizer_name_or_path: str = "deepseek-ai/DeepSeek-V3"
    engram_vocab_size: List[int] = field(default_factory=lambda: [129280*5, 129280*5])
    max_ngram_size: int = 3
    n_embed_per_ngram: int = 512
    n_head_per_ngram: int = 8
    layer_ids: List[int] = field(default_factory=lambda: [1, 15])
    pad_id: int = 2
    seed: int = 0
    kernel_size: int = 4
```

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `tokenizer_name_or_path` | str | `"deepseek-ai/DeepSeek-V3"` | 分词器名称或路径 |
| `engram_vocab_size` | List[int] | `[646400, 646400]` | 各 n-gram 阶的词表大小（bigram/trigram 各 5 倍词表） |
| `max_ngram_size` | int | `3` | 最大 n-gram 阶数（支持 2-gram 和 3-gram） |
| `n_embed_per_ngram` | int | `512` | 每个 n-gram 的嵌入维度 |
| `n_head_per_ngram` | int | `8` | 每个 n-gram 的哈希头数（多头哈希减少碰撞） |
| `layer_ids` | List[int] | `[1, 15]` | Engram 模块插入的 Transformer 层 ID |
| `pad_id` | int | `2` | 填充 token ID |
| `seed` | int | `0` | 随机种子（用于生成哈希乘数） |
| `kernel_size` | int | `4` | ShortConv 卷积核大小 |

### BackBoneConfig（演示用）

```python
@dataclass
class BackBoneConfig:
    hidden_size: int = 1024       # 隐藏层维度
    hc_mult: int = 4              # Hyper-connection 倍数
    vocab_size: int = 129280      # 词表大小
    num_layers: int = 30          # Transformer 层数
```

## 核心组件

### CompressedTokenizer

分词器压缩层，将原始 token ID 映射到归一化后的压缩 ID 空间：

```python
class CompressedTokenizer:
    def __init__(self, tokenizer_name_or_path: str): ...
    def __call__(self, input_ids) -> np.ndarray: ...  # 压缩 token IDs
    def __len__(self) -> int: ...                     # 返回压缩后词表大小
```

- 内部使用 NFKC/NFD 归一化、去除重音、小写化、空白规范化
- 处理包含 `�` 替换字符的 token（使用原始 token 字符串作为 key）
- 输出 `lookup_table`：`old_id → new_id` 的 numpy 数组映射

### NgramHashMapping

N-gram 哈希映射模块，将 token 序列映射为确定性哈希地址：

```python
class NgramHashMapping:
    def __init__(self, engram_vocab_size, max_ngram_size, n_embed_per_ngram,
                 n_head_per_ngram, layer_ids, tokenizer_name_or_path, pad_id, seed): ...
    def hash(self, input_ids: np.ndarray) -> Dict[int, np.ndarray]: ...
```

核心方法 `hash(input_ids)`：
1. 先通过 `CompressedTokenizer` 压缩 token IDs
2. 对每个目标层计算 n-gram 哈希：
   - Bigram（n=2）：`hash = (t0 * m0) XOR (t1 * m1) % prime_head_j`
   - Trigram（n=3）：`hash = (t0 * m0) XOR (t1 * m1) XOR (t2 * m2) % prime_head_j`
3. 每层使用不同的随机乘数（基于 seed + layer_id 生成）
4. 每个 n-gram 使用 `n_head_per_ngram` 个不同质数作为模，实现多头哈希

哈希特性：
- **确定性寻址**：相同 n-gram 始终映射到相同地址，O(1) 查找
- **质数模**：每个哈希头使用不同质数作为模，减少碰撞
- **层特定乘数**：每层使用不同随机乘数，不同层的 Engram 表不冲突

### ShortConv

短卷积模块，对 Engram 检索结果进行局部上下文融合：

```python
class ShortConv:
    def __init__(self, hidden_size, kernel_size=4, dilation=1,
                 norm_eps=1e-5, hc_mult=4, activation=True): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...  # (B,L,HC_MULT,D) → (B,L,HC_MULT,D)
```

- 深度可分离卷积（`groups=total_channels`）
- 输入形状：`(B, L, hc_mult, D)`，对每个 hyper-connection 通道独立归一化和卷积
- 膨胀率设为 `max_ngram_size`（3），配合 kernel_size=4 覆盖局部 n-gram 上下文
- 使用 SiLU 激活

### MultiHeadEmbedding

多头嵌入表，将哈希地址映射为嵌入向量：

```python
class MultiHeadEmbedding:
    def __init__(self, list_of_N: List[int], D: int): ...
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor: ...
```

- 将多个哈希头的嵌入表合并为一个大 Embedding，通过 offset 区分不同头
- 输入形状：`(B, L, num_heads)`
- 输出形状：`(B, L, num_heads, D)`

### Engram（主模块）

```python
class Engram(nn.Module):
    def __init__(self, layer_id: int): ...
    def forward(self, hidden_states: torch.Tensor, input_ids: torch.Tensor) -> torch.Tensor: ...
```

**前向传播流程**：

1. **哈希寻址**：`hash_mapping.hash(input_ids)[layer_id]` 获取当前层的 n-gram 哈希 ID
2. **嵌入检索**：`multi_head_embedding(hash_ids).flatten(-2)` 获取嵌入并展平多头
3. **门控融合**：对每个 hyper-connection 通道计算 gate：
   - `key = key_proj(embeddings)` → RMSNorm
   - `query = hidden_states[:, :, hc_idx, :]` → RMSNorm
   - `gate = sigmoid(sqrt(abs(q·k/√D)) * sign(q·k/√D))`
4. **值投影**：`value = gate * value_proj(embeddings).unsqueeze(2)`
5. **残差卷积**：`output = value + short_conv(value)`
6. 返回形状：`(B, L, hc_mult, D)`

### TransformerBlock（集成方式）

```python
class TransformerBlock(nn.Module):
    def __init__(self, layer_id: int): ...
    def forward(self, input_ids, hidden_states):
        if self.engram is not None:
            hidden_states = self.engram(hidden_states, input_ids) + hidden_states
        hidden_states = self.attn(hidden_states) + hidden_states
        hidden_states = self.moe(hidden_states) + hidden_states
        return hidden_states
```

Engram 在指定层（`layer_ids`）中以残差方式插入，位于 Attention 和 MoE 之前。

## 运行演示

```bash
pip install torch numpy transformers sympy
python engram_demo_v1.py
```

演示输出：
```
✅ Forward Complete!
input_ids.shape=torch.Size([1, L])
output.shape=torch.Size([1, L, 129280])
```
