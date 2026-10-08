---
type: concept
scope: engram
name: ngram-hashing-and-gating
description: Engram 的 N-gram 哈希寻址、多头嵌入、门控融合与短卷积机制详解
---

# N-gram 哈希与门控融合机制

本文详细阐述 Engram 模块的核心技术机制——N-gram 哈希寻址、多头嵌入检索、门控融合和短卷积上下文扩展。

## N-gram 哈希寻址

### 基本思想

Engram 的核心是通过哈希函数将 N-gram token 序列映射到嵌入表中的确定性地址：

```
token 序列:  [t0, t1, t2, t3, ...]
                ↓
bigram:     hash(t0,t1) → row_id_0
            hash(t1,t2) → row_id_1
            hash(t2,t3) → row_id_2
                ↓
trigram:    hash(t0,t1,t2) → row_id_0'
            hash(t1,t2,t3) → row_id_1'
                ↓
O(1) 查表 → 嵌入向量
```

### 哈希函数设计

对于 n-gram `(t_{k-n+1}, ..., t_k)`，哈希计算为：

```
mix = t_{k-n+1} * m_0
mix = mix XOR (t_{k-n+2} * m_1)
mix = mix XOR (t_{k-n+3} * m_2)
...
mix = mix XOR (t_k * m_{n-1})

hash_j = mix % p_j   (j = 0, ..., num_heads-1)
```

其中：
- `m_i` 是每层独立的随机奇数乘数（通过 seed + layer_id 生成）
- `p_j` 是互不相同的质数（通过 `find_next_prime` 动态查找）
- 使用 XOR 而非加法避免溢出，乘法确保哈希分布均匀
- 移位使用 pad token 填充，确保序列长度不变

### 多头哈希减少碰撞

单一哈希函数可能导致不同 n-gram 映射到同一地址（碰撞）。Engram 使用**多头哈希**：
- 每个 n-gram 阶使用 `n_head_per_ngram=8` 个独立哈希头
- 每个头使用不同的质数模 `p_j`
- 8 个头的嵌入被拼接，形成最终的 n-gram 表示
- 碰撞概率指数级降低：8 个头同时碰撞的概率约为 `(1/vocab)^8`

### 压缩分词器

在哈希之前，token IDs 经过 `CompressedTokenizer` 预处理：

1. **NFKC 归一化**：统一 Unicode 表示
2. **NFD + 去重音**：分解字符并去除重音符号
3. **小写化**：大小写不敏感
4. **空白规范化**：连续空白合并
5. **特殊字符处理**：包含 `�` 的 token 使用原始 token 字符串作为 key

这确保了语义等价的 token（如 "Hello" 和 "hello"）映射到同一压缩 ID，提高 n-gram 匹配率。

## 嵌入表结构

### 扁平化多头嵌入

`MultiHeadEmbedding` 将多个哈希头的嵌入表合并为单一 Embedding 层：

```
Bigram 头0: [0, N0)
Bigram 头1: [N0, N0+N1)
...
Bigram 头7: [...]
Trigram 头0: [...]
...
Trigram 头7: [...]
```

通过 `offsets` 缓冲区自动偏移索引，实现高效的批量查找。

### 嵌入维度计算

- 每个 n-gram 阶总维度：`n_embed_per_ngram = 512`
- 每个头维度：`512 / 8 = 64`
- Bigram + Trigram 总维度：`(3-1) * 512 = 1024`

## 门控融合机制

检索到的 n-gram 嵌入并非直接注入隐藏状态，而是通过**门控机制**自适应融合：

```
对于每个 hyper-connection 通道 g:
  key   = RMSNorm(W_k · engram_embedding)      # (B, L, D)
  query = RMSNorm(hidden_states[:, :, g, :])   # (B, L, D)
  
  raw_gate = sum(key * query) / sqrt(D)        # 点积注意力分数
  gate = sigmoid(sqrt(|raw_gate| + ε) * sign(raw_gate))  # 平滑门控
  
  value_g = gate * W_v · engram_embedding      # 门控值
```

### 门控设计特点

1. **Query 来自动态隐藏状态**：gate 由当前 token 的动态表示（query）和 n-gram 记忆（key）的相似度决定
2. **非对称门控**：`sqrt(|x|) * sign(x)` 变换使得：
   - 强匹配（高 gate）和强不匹配（低 gate）都被放大
   - 不确定区域过渡平滑
3. **每个 hyper-connection 通道独立门控**：与 mHC 机制兼容，不同子空间有独立的记忆融合决策
4. **RMSNorm 归一化**：确保 key 和 query 的尺度一致，门控值稳定

## 短卷积上下文扩展

门控后的值经过 `ShortConv` 进行局部上下文扩展：

```
output = value + short_conv(value)
```

### ShortConv 设计

- **深度可分离卷积**：每个通道独立卷积，参数少、计算高效
- **kernel_size=4**：覆盖局部 4 个位置
- **dilation=3**（= max_ngram_size）：膨胀卷积使得感受野覆盖 n-gram 上下文
- **分组 RMSNorm**：卷积前对每个 hc 通道独立归一化
- **SiLU 激活**：引入非线性

短卷积的作用：纯 n-gram 查找只提供当前位置的记忆，短卷积让相邻位置的记忆信息相互交流，增强局部一致性。

## 完整数据流

```
input_ids (B, L)
    ↓
[CompressedTokenizer] → compressed_ids (B, L)
    ↓
[Shift + Hash] for each n ∈ {2,3}, each head j
    ↓
hash_ids (B, L, num_ngrams * num_heads)
    ↓
[MultiHeadEmbedding] → embeddings (B, L, num_heads, head_dim)
    ↓
[Flatten] → engram_embedding (B, L, 1024)
    ↓
[Gate Fusion] per hc channel
    key = RMSNorm(W_k · emb) → (B,L,D)
    query = RMSNorm(hidden[:,:,g,:]) → (B,L,D)
    gate = σ(√|q·k/√D|·sgn(q·k/√D))
    value = gate * W_v(emb) → (B,L,D)
    ↓
[ShortConv]
    output = value + DepthwiseConv(SiLU(Conv1d(RMSNorm(value))))
    ↓
output (B, L, hc_mult, D) → 残差连接到 hidden_states
```

## 为什么插入浅层

Engram 只在浅层（第1层和第15层）插入，原因：
1. 浅层负责局部模式识别，n-gram 记忆在这里最有效
2. 深层负责全局推理和抽象，不需要 n-gram 查找
3. 早期层获得静态记忆帮助后，可以"腾出"计算能力给深层
4. 这与机制分析结论一致：Engram 减轻了早期层重建静态模式的负担
