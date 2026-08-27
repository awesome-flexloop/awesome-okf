---
type: concept
scope: flash-mla
name: MLA 解码算法
version: "1.0.0"
source: docs/20250422-new-kernel-deep-dive.md, README.md, flash_mla/flash_mla_interface.py
description: MLA (Multi-head Latent Attention) 解码算法原理、低秩 KV 压缩与在线 softmax 计算
---

# MLA 解码算法

MLA（Multi-head Latent Attention）是 DeepSeek 提出的一种高效注意力架构，通过低秩压缩大幅减少 KV cache 的内存占用，是 FlashMLA 优化的核心算法基础。MLA 解码特指自回归生成阶段（decoding），即每次仅处理 1 个（或 MTP 下少数几个）query token，从已有的 KV cache 中计算注意力输出。

---

## 一、MLA 的核心思想

### 1.1 标准 MHA 的 KV Cache 瓶颈

在标准 Multi-Head Attention（MHA）中，KV cache 的内存占用为：

```
KV_cache_memory = 2 × num_layers × num_kv_heads × head_dim × seq_len × sizeof(dtype)
```

对于 DeepSeek-V3 规模的模型（61 层，128 个 Q 头，1 个 KV 头即 MQA，head_dim=512），BF16 精度下 32K 序列长度的 KV cache 约为：

```
2 × 61 × 1 × 512 × 32768 × 2 bytes ≈ 3.9 GB
```

虽然 MQA/GQA 已大幅压缩了头维度，但 KV cache 仍然是长上下文推理的主要内存瓶颈。

### 1.2 MLA 低秩压缩

MLA 的核心创新是将 KV 矩阵进行低秩分解，将键值对压缩为一个共享的潜在向量（latent vector）：

```
标准 MHA:
  K = W_k @ X    (num_heads × head_dim)
  V = W_v @ X    (num_heads × head_dim)

MLA:
  c = W_dk @ X                  # 压缩到潜在空间 (d_c,)
  k^R = W_kr @ RoPE(X)          # 旋转位置编码部分 (d_R,)，不压缩
  k^C = W_uk @ c                # 解压回注意力维度
  v = W_uv @ c                  # V 从同一个 c 解压
  q^R = W_qr @ RoPE(X)          # Q 也分为 RoPE 和 NoPE 部分
  q^C = W_uq @ (W_dq @ X)       # Q 的 NoPE 部分
```

关键设计：
- **NoPE 部分**（不参与位置编码）：K 和 V 共享同一个压缩向量 `c`，维度为 d_noPE=512（V32）或 448（MODEL1），实现 KV 的联合压缩
- **RoPE 部分**：64 维，保持不压缩以保留位置信息精度
- **上行投影**：在注意力计算时，通过 `W_uk` 和 `W_uv` 将压缩向量投影回所需维度，与 Q 进行标准的点积注意力

### 1.3 推理时的 KV Cache

推理阶段，MLA 只需要缓存压缩后的潜在向量 `c` 和 RoPE 部分 `k^R`，而非完整的 K 和 V：

| 组件 | V32 维度 | MODEL1 维度 | 精度 | 说明 |
|---|---|---|---|---|
| NoPE 潜在向量 | 512 | 448 | FP8 (E4M3) | 可量化压缩 |
| RoPE 键向量 | 64 | 64 | BF16 | 不量化，保持精度 |
| **每 token 合计** | **656 B** | **576 B** | — | 对比 BF16 MQA 的 2304 B |

相比 BF16 标准 MQA（head_dim=576, 2×576×2=2304 字节/token），V32 模式的 FP8 KV cache 实现了 **3.5×** 的内存压缩比。

---

## 二、MLA 解码计算流程

### 2.1 Decoding 阶段特征

自回归解码（decoding）与预填充（prefill）的关键区别：

| 属性 | Decoding | Prefill |
|---|---|---|
| Query 长度 (s_q) | 1（或 MTP 的少数 token） | 通常 1K~128K |
| KV 长度 (s_kv) | 持续增长 | 已知固定 |
| 计算特征 | 内存带宽受限（短 Q 读长 KV） | 计算密集（长 Q 长 KV） |
| GEMM 形状 | QK: [h_q, d] × [d, s_kv] → [h_q, s_kv] | QK: [s_q, d] × [d, s_kv] → [s_q, s_kv] |
| 优化重点 | KV 加载带宽、在线 softmax | Tiling、流水线 |

### 2.2 MLA Decode 计算步骤

```
输入：
  q_nope: (b, s_q, h_q, d_noPE)   # Q 的 NoPE 部分，BF16
  q_rope: (b, s_q, h_q, d_R)       # Q 的 RoPE 部分，BF16
  k_cache: FP8 压缩格式             # KV cache
  block_table: (b, max_blocks)      # 页表
  cache_seqlens: (b,)               # 各序列长度

步骤：
1. 拼接 Q: q = concat(q_nope, q_rope)  # (b, s_q, h_q, d)

2. 沿 KV 序列分块计算（SplitKV）:
   对每个 split（由调度器分配）:
     对 KV 序列中的每个 block (block_size_n=64 tokens):
       a. 从 KV cache 加载 k_nope (FP8)、scales (FP32)、k_rope (BF16)
       b. FP8 反量化：k_nope_bf16 = dequant(k_nope, scales)
       c. 拼接 k = concat(k_nope_bf16, k_rope)  # BF16
       d. QK 点积：s = q @ k.T * softmax_scale   # (b*s_q*h_q, block_n)
       e. 因果掩码：如 causal=True，mask 掉未来位置
       f. Online softmax：更新 m_i (max)、l_i (sum_exp)
       g. PV 乘加：o += softmax(s) @ v           # v = k_nope_bf16 或含 RoPE

3. SplitKV Combine:
   合并多个 split 的部分结果（m, l, o），得到最终输出
```

### 2.3 Online Softmax

FlashMLA 使用 online softmax（也称为 streaming softmax）避免在 shared memory 中存储完整的 attention score 矩阵：

```
初始化：m = -∞, l = 0, o = 0

对每个 KV block:
  s = q @ k.T * scale                     # 当前 block 的注意力分数
  m_new = max(m, max(s))                  # 新的全局最大值
  l = l * exp(m - m_new) + sum(exp(s - m_new))  # 更新 sum(exp)
  o = o * exp(m - m_new) + softmax(s) @ v       # 更新输出
  m = m_new

最终：o = o / l                            # 归一化
```

这种方法只需维护 `m`（最大值）、`l`（指数和）、`o`（输出累加）三个状态向量，不需要存储完整的 S 矩阵，内存开销为 O(N) 而非 O(N×block_size)。

---

## 三、MQA/GQA 支持

MLA 天然采用 MQA（Multi-Query Attention）模式，即 KV 头数 h_kv=1，所有查询头共享同一份 KV cache。FlashMLA 也支持 GQA（Grouped-Query Attention），h_kv > 1 但 h_q % h_kv == 0。

在 kernel 实现中，GQA 通过以下方式处理：

**SM90 Dense Decode：**
- Q reshape：`(b, s_q, h_q, d)` → `(b, q_seq_per_hk, h_k, d)`，其中 `q_seq_per_hk = s_q * h_q/h_k`
- Thread Block Cluster（CLUSTER_SIZE = NUM_M_BLOCKS = h_q/64）协作处理多个 Q 头
- DSM（Distributed Shared Memory）实现跨 CTA 的 P（attention scores）共享

**SM100 Sparse Decode：**
- h_q=64：单个 CTA 处理 64 头
- h_q=128（V32/d_qk=576）：双次 head64 kernel 调用
- h_q=128（MODEL1/d_qk=512）：专用 head128 small_topk kernel

---

## 四、Dense vs Sparse 解码

FlashMLA 支持两种解码模式：

### 4.1 Dense Decoding

- 所有历史 token 参与注意力计算
- 使用 paged KV cache（block_table 索引）
- KV cache 格式：BF16（或 FP16），无量化
- 架构支持：仅 SM90（Hopper）
- 适用于：无稀疏模式的标准推理
- 因果掩码：通过 `causal=True` 参数控制

### 4.2 Sparse Decoding（DSA）

- 仅计算 `indices` 指定的 top-k token（DeepSeek Sparse Attention）
- 不使用 block_table，indices 直接编码物理位置
- KV cache 格式：FP8 量化（NoPE 部分 FP8，RoPE 部分 BF16）
- 架构支持：SM90 和 SM100
- 适用于：DeepSeek-V3.2 的稀疏注意力推理
- 必须设置 `causal=False` 和 `is_fp8_kvcache=True`

---

## 五、Attention Sink 机制

FlashMLA 支持可选的 `attn_sink` 参数，用于注意力 sink 机制：

```
output = output * exp(lse) / (exp(lse) + exp(attn_sink))
```

- `attn_sink` 形状为 `(h_q,)`，float32
- 当 `attn_sink[h] = -inf` 时，对该头无影响（正常输出）
- 当 `attn_sink[h] = +inf` 时，该头输出为零
- 不影响返回的 softmax_lse 值
- 常用于实现注意力 sink token 或门控机制

---

## 六、相关链接

- /deepseek/flash-mla/concepts/overview — FlashMLA 整体概述
- /deepseek/flash-mla/concepts/splitkv — SplitKV 长序列技术
- /deepseek/flash-mla/concepts/kv-cache-quantization — FP8 KV cache 量化
- /deepseek/flash-mla/concepts/hopper-blackwell-kernels — Hopper/Blackwell 内核设计
- /deepseek/flash-mla/references/api — Python API 参考
- /deepseek/flash-mla/examples/basic-decoding — 基础解码使用示例
