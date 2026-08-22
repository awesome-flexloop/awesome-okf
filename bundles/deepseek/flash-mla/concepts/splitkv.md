---
type: concept
scope: flash-mla
name: SplitKV 长序列注意力技术
version: "1.0.0"
source: csrc/smxx/decode/, csrc/params.h, csrc/api/dense_decode.h, docs/20250422-new-kernel-deep-dive.md
description: SplitKV 分块 KV 并行计算技术，用于长上下文 MLA 解码的调度与合并
---

# SplitKV 长序列注意力技术

SplitKV 是 FlashMLA 实现长上下文高效解码的核心技术。其核心思想是将长序列的 KV cache 沿序列维度切分为多个 split（分片），由不同的 SM（Streaming Multiprocessor）并行处理，最后通过 online softmax 的数学性质将各分片结果合并。

---

## 一、为什么需要 SplitKV

### 1.1 解码阶段的并行性挑战

在 MLA 解码阶段，query 长度 s_q 通常为 1（自回归生成单 token），这意味着：

- **并行维度有限**：QK 点积的形状为 `[h_q, d] × [d, s_kv]`，仅沿 h_q 和 s_kv 方向有并行性
- **KV 加载主导**：当 s_kv 很长（如 32K+）时，单个 SM 需要加载全部 KV 数据，成为内存带宽瓶颈
- **SM 利用率不足**：h_q=128 时，SM90 最多只能有效利用约 128 个 SM（每 SM 处理 1 个头），而 H800 有 132 个 SM；当 h_q=64 时，仅 64 个 SM 被利用

### 1.2 SplitKV 的解决方案

SplitKV 通过沿 KV 序列维度切分，将"读全部 KV"的任务分配给多个 SM 并行执行：

```
KV 序列: [0, 1, 2, ..., s_kv-1]
                    ↓ 按 SplitKV 切分
Split 0: [0, n_0)         → SM 0 处理
Split 1: [n_0, n_1)       → SM 1 处理
Split 2: [n_1, n_2)       → SM 2 处理
...
Split K-1: [n_{K-2}, s_kv) → SM K-1 处理
                    ↓ 各 SM 独立计算 online softmax
部分结果: (m_i, l_i, o_i)  for i = 0..K-1
                    ↓ Combine 内核合并
最终结果: (m_final, l_final, o_final)
```

这样，即使 h_q 较小（如 64），也能通过多 SM 并行处理长序列充分利用 GPU 算力。

---

## 二、SplitKV 调度机制

### 2.1 调度元数据

SplitKV 的核心数据结构是 `DecodingSchedMeta`（定义在 [csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h)）：

```cpp
struct DecodingSchedMeta {
    int begin_req_idx, end_req_idx;      // 请求索引范围（inclusive）
    int begin_block_idx, end_block_idx;  // KV block 范围（inclusive, exclusive）
    int begin_split_idx;                 // 起始 split 索引
    int is_first_req_splitted;           // 第一个请求是否被跨 split 切分
    int is_last_req_splitted;            // 最后一个请求是否被跨 split 切分
    int _pad[1];                         // 对齐填充
};
```

每个 SM part（即参与 SplitKV 的每个 CTA）分配一个 `DecodingSchedMeta`，描述它需要处理的请求范围和 KV block 范围。

### 2.2 调度元数据张量

| 张量 | 形状 | dtype | 说明 |
|---|---|---|---|
| `tile_scheduler_metadata` | `(num_sm_parts, DecodingSchedMetaSize/4)` | int32 | 调度元数据数组，每行一个 SM part |
| `num_splits` | `(b+1,)` | int32 | 前缀和形式记录每个 batch 的 split 数 |

`num_sm_parts` 的计算根据 kernel 类型和头数动态确定：

| 内核 | num_sm_parts 计算公式 |
|---|---|
| SM90 Dense Decode | `max(num_sms / h_k / ceil_div(s_q*h_q/h_k, 64), 1)` |
| SM90 Sparse Decode | `max(num_sms / s_q / (h_q/64), 1)` |
| SM100 Sparse Decode Head64 | `max(num_sms / s_q, 1)` |
| SM100 Sparse Decode Head128 | `max(num_sms / s_q / 2, 1)` |

### 2.3 调度参数

| 参数 | 值 | 说明 |
|---|---|---|
| `block_size_n` | 64 | KV 方向的 tile 大小（token 数） |
| `page_block_size` | 64 | KV cache 页块大小（token 数） |
| `fixed_overhead_num_blocks` | 5（dense/sparse head64）/ 3（head128 small_topk） | 调度固定开销块数 |

### 2.4 延迟初始化

FlashMLA 采用延迟初始化策略：
1. `get_mla_metadata()` 返回空的 `FlashMLASchedMeta`
2. 首次调用 `flash_mla_with_kvcache` 时，C++ 层分配 `tile_scheduler_metadata` 和 `num_splits` 张量
3. 调用 `smxx::decode::run_get_decoding_sched_meta_kernel()` 生成调度元数据
4. 后续调用复用已生成的调度元数据，并检查输入参数一致性

---

## 三、SplitKV 执行流程

### 3.1 分块计算阶段（主内核）

每个 CTA（SM part）独立执行以下流程：

```
for each request in [begin_req_idx, end_req_idx]:
    初始化 online softmax 状态: m = -∞, l = 0, o = 0

    for each KV block in assigned range:
        if is_first_req_splitted and first request:
            从 begin_split_idx 开始处理（跳过前几个 token）
        if is_last_req_splitted and last request:
            处理到 cache_seqlens 为止（不超出实际长度）

        1. 加载 KV block 数据
           - Dense: 通过 TMA 从 k_cache[block_table[req][block]] 加载
           - Sparse: 通过 indices 定位物理地址加载，FP8 反量化

        2. QK 矩阵乘
           s = q @ k.T * scale    # (BLOCK_M, block_size_n)

        3. Causal mask（如需要）
           对超出 cache_seqlens 的位置设为 -inf

        4. Online softmax 更新
           m_new = max(m, row_max(s))
           s_exp = exp(s - m_new)
           l_new = l * exp(m - m_new) + row_sum(s_exp)
           o = o * exp(m - m_new) + s_exp @ v
           m = m_new
           l = l_new

    将部分结果写入全局内存:
    softmax_lseaccum[part_idx] = m + log(l)   # 部分 LSE
    oaccum[part_idx] = o * l                   # 部分输出（未归一化）
```

### 3.2 Combine 阶段

主内核完成后，调用架构无关的 `run_flash_mla_combine_kernel` 合并所有 split 的部分结果：

```
for each request:
    num_splits = num_splits[req+1] - num_splits[req]
    m_final = -∞
    l_final = 0
    o_final = 0

    # 第一步：找到全局最大值
    for i in range(num_splits):
        m_final = max(m_final, softmax_lseaccum[i])

    # 第二步：累加所有 split 的贡献
    for i in range(num_splits):
        alpha = exp(softmax_lseaccum[i] - m_final)
        l_final += alpha
        o_final += oaccum[i] * alpha  # oaccum[i] = o_i * l_i，已经乘过 l_i

    # 第三步：归一化
    out = o_final / l_final
    lse = m_final + log(l_final)

    # 第四步：attention sink（如果提供）
    if attn_sink is not None:
        out = out * exp(lse) / (exp(lse) + exp(attn_sink))
```

Combine 内核是轻量级的，仅做逐元素的 exp 和加法，计算量很小。

---

## 四、Ring Buffer 流水线

SM90 sparse decode 内核使用 `RingBufferState` 实现多阶段流水线，重叠 KV 加载和计算：

```cpp
struct RingBufferState {
    uint32_t cur_block_idx;
    // get<NUM_STAGES>() 返回 {stage_idx, phase} 用于双/多缓冲选择
    // update() 前进到下一 block
    // offset_by(offset) 返回偏移后的状态
};
```

双缓冲（NUM_K_BUFS=2）流程：
1. Stage 0：加载 K block 0 到 smem_sK0
2. 计算 K block 0 的 QK/PV，同时加载 K block 1 到 smem_sK1
3. 计算 K block 1 的 QK/PV，同时加载 K block 2 到 smem_sK0（覆盖）
4. 循环直到所有 block 处理完毕

---

## 五、SplitKV 与 FlashAttention 的关系

SplitKV 的思想与 FlashAttention 系列中的 split-KV/parallel attention 一脉相承：

| 技术 | 出处 | 应用场景 |
|---|---|---|
| FlashAttention | Dao et al., 2022 | IO-aware exact attention，tiling + online softmax |
| FlashAttention-2 | Dao, 2023 | 优化并行策略，split 沿 batch/head 维度 |
| FlashDecoding | Tri Dao, 2023 | SplitKV 专门针对 decoding 阶段 |
| **FlashMLA SplitKV** | DeepSeek, 2025 | 针对 MLA 格式优化，paged KV cache + FP8，Hopper/Blackwell 专用 |

FlashMLA SplitKV 的独特之处：
- 原生支持 MLA 压缩 KV 格式（NoPE + RoPE 分离，FP8 量化）
- 与分页 KV cache（block_table）深度集成
- 利用 Hopper DSM 和 Blackwell tmem 加速跨 split/head 的协作
- 同时支持 dense 和 sparse（DSA）两种注意力模式
- 针对 MQA/GQA 模式优化了 num_sm_parts 计算

---

## 六、性能影响

SplitKV 对解码性能的影响因场景而异：

- **内存受限场景**（短上下文、小 batch）：SplitKV 通过多 SM 并行加载 KV 提升带宽利用率，接近 3000 GB/s（H800 HBM 带宽上限）
- **计算受限场景**（长上下文、大 batch、FP8 sparse）：SplitKV 增加有效 SM 数量，h_q=64 时从 64 个 SM 扩展到全部 132 个 SM，达到 410 TFLOPS
- **额外开销**：需要额外的全局内存存储部分结果（oaccum 和 lseaccum），以及 combine 内核的 launch 开销，但通常被并行收益覆盖

---

## 七、相关链接

- [/deepseek/flash-mla/concepts/mla-decoding](/deepseek/flash-mla/concepts/mla-decoding) — MLA 解码算法原理
- [/deepseek/flash-mla/concepts/hopper-blackwell-kernels](/deepseek/flash-mla/concepts/hopper-blackwell-kernels) — Hopper/Blackwell 硬件特性利用
- [/deepseek/flash-mla/references/kernel-architecture](/deepseek/flash-mla/references/kernel-architecture) — 内核架构详解（调度参数、num_sm_parts 计算）
- [/deepseek/flash-mla/references/api](/deepseek/flash-mla/references/api) — FlashMLASchedMeta API 参考
