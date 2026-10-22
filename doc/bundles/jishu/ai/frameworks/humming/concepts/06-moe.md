---
type: Concept
title: "MoE 路径：四种 GEMM 形态的取舍"
description: "Humming 的 MoE 支持——DENSE/INDEXED/GROUPED_CONTIGUOUS/GROUPED_MASKED 四种 GEMM 类型的语义差异、MoE 专属参数、vLLM 侧 MoE 激活表达式翻译与 kernel 选择优先级"
tags: [humming, moe, grouped-gemm, indexed-gemm, routing, vllm, 核心]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
---

# MoE 路径：四种 GEMM 形态的取舍

> 核心层。MoE（Mixture of Experts）是 Humming 性能优势最集中的场景——官方数据里 MoE W4A16 的加速比普遍高于 Dense（F-083）。

## 一、四种 GEMM 类型

`GemmType` 枚举四态（F-036，`humming/config/enum.py:69-73`）：

```mermaid
flowchart LR
    A["DENSE<br/>标准稠密"] 
    B["INDEXED<br/>按索引取权重行"]
    C["GROUPED_CONTIGUOUS<br/>分组连续"]
    D["GROUPED_MASKED<br/>分组 + 掩码"]
    A --> B
    B --> C
    C --> D
```

| 类型 | 语义 | 适用场景 |
|------|------|---------|
| `DENSE` | 标准稠密矩阵乘 | 常规 FFN / Attention 投影层 |
| `INDEXED` | 按索引数组取出权重行再相乘 | 动态路由：每个 token 的权重行索引由 router 决定 |
| `GROUPED_CONTIGUOUS` | 多个专家权重连续排布，按分组偏移量切分 | MoE 专家权重已按 token 分组重排的布局 |
| `GROUPED_MASKED` | 分组 + 掩码，部分 token 被丢弃 | MoE 专家容量受限，需要丢 token 的场景 |

**派生属性自动推导**（F-033）：`is_indexed_gemm` / `is_grouped_contiguous_gemm` / `is_grouped_masked_gemm` / `is_grouped_gemm` 全部由 `gemm_type` 自动推出，**不需要手工设置**。

**indexed GEMM 的额外约束**：不支持 m-major input scale（F-034，`assert not self.use_m_major_input_scale`）。

## 二、MoE 专属参数

`humming_gemm()` 的 MoE 相关入参（F-049）：

| 参数 | 含义 |
|------|------|
| `sorted_ids` | 按专家分好组的 token ID 序列 |
| `expert_ids` | 每个分组的专家 ID |
| `num_tokens_padded` | 补齐后的 token 数（分组边界对齐用） |
| `expert_layout` | 专家权重的排布方式 |
| `locks` | **stream-k 累加锁**（非专家级锁，详见下） |

**`num_tokens_padded` 的存在说明了分组的不规则性**：不同专家分到的 token 数不同，为了让 kernel 能按统一 tile 处理，分组边界需要补齐。补齐部分通过掩码排除在计算之外。

**`locks` 是 stream-k 累加锁**（F-101）：stream-k 是一种把同一个输出 tile 的计算拆分到多个 CTA、由各 CTA 累加部分和的调度策略——分片之间需要同步，因此用锁保护累加缓冲。锁容量必须为 `max_stream_k_tiles * num_stream_k_locks_per_tile`，**仅在 `use_stream_k` 开启时必需**。batch-invariant 模式强制关闭 stream-k（`use_stream_k=False`），此时不需要 locks。vLLM 侧由 `create_humming_locks` 创建（F-076）。

## 三、MoE 的性能特征

官方 MoE W4A16 数据（F-083）：

| 硬件 | 对比基线 | 数据 |
|------|---------|------|
| H20 / H200 | vLLM Marlin W4A16 | MXFP4 多个中大 batch 约 **2×** |
| B300 | vLLM Marlin | MXINT4 / NVFP4 的 grouped 路径约 **5×** |
| SM120 / SM121 | Marlin 与对应 FlashInfer 实现 | 一系列 workload 优于两者 |

**为什么 MoE 加速比更高**：MoE 的 GEMM 天然是 grouped 形态，token 分组后每个分组的 M 较小且不规则——正是 Marlin 这类「为单一 shape 优化的固定内核」最不擅长的区间。而 Humming 的 JIT 可以为每个分组规模生成贴合的 kernel，加上栅格化调度改善 L2 命中（F-060）。

## 四、vLLM 侧的 MoE 集成

vLLM 侧的 humming MoE 代码主要在两处（F-076 所列五处中的 MoE 主实现）：

- `vllm/model_executor/layers/quantization/humming.py` → `HummingMoEMethod`
- `vllm/model_executor/layers/fused_moe/experts/fused_humming_moe.py` → 融合执行路径

配套工具在 `vllm/model_executor/layers/quantization/utils/humming/`：`moe.py`、`linear.py`、`activation.py`、`priority.py`、`schema.py`。

此外 `--linear-backend humming` 的实际落点在 `vllm/model_executor/kernels/linear/*/humming.py`（`mixed_precision`、`mxfp4`、`mxfp6`、`mxfp8`、`nvfp4`、`scaled_mm` 六个子目录各一份，F-076）。

### 激活表达式翻译（12 种）

Humming 的内核不认识 vLLM 的激活函数名——它需要**可执行的表达式**。vLLM 侧的 `utils/humming/activation.py` 负责翻译（F-078，`activation.py:28-100`）：

| 族 | 变体 |
|----|------|
| SwiGLU 系 | `SILU`、`SWIGLUOAI`、`SWIGLUOAI_UNINTERLEAVE`、`SWIGLUSTEP` |
| GELU 系 | `GELU`、`GELU_TANH` |
| 其他 | `RELU2`、`SITU` |
| NO_MUL 变体 | `SILU_NO_MUL`、`GELU_NO_MUL`、`GELU_TANH_NO_MUL`、`RELU2_NO_MUL` |

共 **12 种**激活被翻译为 humming 可执行表达式（源码 `_HUMMING_ACTIVATIONS` 字典实测 12 个 key）。

**「NO_MUL」是什么**：某些路径下乘法由别处完成（如与 scale 融合），所以激活只输出未乘的部分。这是内核内部优化细节，但对上层是可见的语义差异——翻译表必须正确区分，否则数值会错。

### Kernel 选择优先级

`utils/humming/priority.py`（F-078，`priority.py:3-26`）提供两个函数：

| 函数 | 作用 |
|------|------|
| `prefers_humming()` | 判断当前场景是否**应当**优先用 Humming |
| `prioritize_humming()` | 在候选后端中把 Humming 提到优先位 |

这说明 **Humming 并非在所有场景下自动胜出**——vLLM 侧有一套判定逻辑决定何时用它。

## 五、端到端实测：把 MoE 执行换成 Humming

官方博客给出的唯一端到端样本（F-089）：

| 项 | 值 |
|----|----|
| 模型 | DeepSeek-V4.1-Flash |
| 硬件 | 8×H20，TP=8 |
| 保持不变 | 模型原有的 MXFP4 权重 |
| 改动 | MoE 执行从 **vLLM Marlin W4A16（BF16 激活）** 切到 **Humming W4A8（tokenwise FP8 激活）** |
| 吞吐提升 | **14%–43%** |
| TTFT 降低 | **25%–32%** |
| 并发 64 输出吞吐 | 442.37 → **633.94 tokens/s** |
| TPOT | 约降 **31%** |

**这个实验的设计值得注意**：它不只换了内核，还**把激活从 BF16 换成了 FP8**。所以 14%–43% 的提升是「Humming 内核 + FP8 激活」的综合效果，不能归因给其中任一项。

> ⚠️ **样本量提醒**：这是官方给出的唯一一个端到端样本，不能据此推断所有模型/负载的性能表现。性能数字一律带测试条件（F-079）。

## 六、MoE 场景下的实践建议

1. **先确认 GEMM 形态**：`GROUPED_CONTIGUOUS` 与 `GROUPED_MASKED` 的差别在于是否丢 token。若你的 MoE 实现有 capacity factor 限制，需用 masked 形态。
2. **关注专家负载均衡**：`expert_probability_cv` 波动大时，栅格化调度的收益更明显（F-059、F-060）。
3. **对齐约束不能绕过**：`pad_shape_n % 64 == 0`、`pad_shape_k % (512 / kNumBitsA) == 0` 是 kernel 的 assert 条件（F-054 上下文）。
4. **vLLM 集成优先走 `--moe-backend humming`**：这是官方明确推荐的方式（F-077）。

## 七、延伸阅读

- [03 架构总览](03-architecture.md)：GEMM 类型与派生属性
- [05 调优与启发式](05-tuning.md)：MoE 的 M 维上限（65536）与栅格化
- [07 vLLM 集成](07-vllm-integration.md)：三条接入路径的完整对比
- 实战：[02 MoE GEMM](../examples/02-moe-gemm.md)
