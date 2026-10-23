---
type: Concept
title: "投机解码：方法谱系与 speculative-config"
description: "vLLM 投机解码全谱——EAGLE/EAGLE3、MTP、draft model、PARD 并行草稿、ngram/ngram_gpu、suffix decoding、dflash/gemma4/step3p5 等 proposer 家族，--speculative-config 公共键、接受率指标、Adaptive Verification 与选型表"
tags: [vllm, speculative-decoding, eagle, mtp, draft-model, ngram, suffix-decoding, speculative-config, latency]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-spec
    resource: /references/source-map.md
    title: vllm/v1/spec_decode/（本地检出）
  - id: website-spec
    url: https://docs.vllm.ai/en/latest/features/speculative_decoding/
    title: Speculative Decoding（官网文档）
---

# 投机解码：方法谱系与 speculative-config

投机解码用小模型/廉价方法先猜若干 token，再由目标模型一次前向批量验证——猜中的部分免去多次串行解码，是降延迟的核心手段（F-111）。vLLM V1 引擎把 proposer 做成可插拔组件，位于 `vllm/v1/spec_decode/`。

## 方法谱系与选型

官方选型表（docs/features/speculative_decoding，2026-10 时点）：

| 方法 | 延迟收益 | 吞吐影响 | 适用条件 |
|------|---------|---------|---------|
| EAGLE | 高 | 中~高 | 通用首选，需 EAGLE head |
| MTP | 高 | 中~高 | 目标模型原生支持 MTP 最佳 |
| Draft model | 高 | 中 | 需单独草稿模型 |
| Parallel Draft Model (PARD) | 高 | 中~高 | 草稿延迟低，支持并行起草 |
| n-gram / ngram_gpu | 中 | 无额外模型 | 适合重复性高的负载 |
| Suffix decoding | 低~中 | 中 | 无需草稿模型，推测深度动态 |
| Adaptive Verification | 高 | 高于基础 SD | 按草稿置信度定验证量（当前 DSpark） |

实践口径：**模型类方法（EAGLE/MTP/draft）延迟收益最大；n-gram/suffix 零模型成本，适合峰值流量时不增负载的场景**（F-155）。

## proposer 家族（源码）

`vllm/v1/spec_decode/` 本地检出的 proposer 实现：

| 文件 | 方法 |
|------|------|
| `eagle.py` | EAGLE / EAGLE3 |
| `mtp`（经 gemma4.py 等承接） | Multi-Token Prediction；Gemma 4 assistant checkpoint 按 `method: mtp` 接入 |
| `draft_model.py` / `dflash.py` / `fly.py` / `step3p5.py` | 独立草稿模型家族 |
| `ngram_proposer.py` / `ngram_proposer_gpu.py` | n-gram（CPU/GPU 两版） |
| `suffix_decoding.py` | 后缀解码 |
| `custom_class_proposer.py` | 自定义 proposer 注册点 |

模型类方法共享 `llm_base_proposer.py` 基类；`metadata.py`/`metrics.py` 负责逐请求元数据与接受率统计（F-151）。

## 配置：`--speculative-config`

```bash
vllm serve <model> --speculative-config '{
  "method": "eagle3",
  "model": "<eagle-head-or-draft-model>",
  "num_speculative_tokens": 3,
  "draft_tensor_parallel_size": 1
}'
```

公共键（docs 口径，F-114）：

| 键 | 类型 | 默认 | 说明 |
|----|------|------|------|
| `method` | string | 推断 | `draft_model`/`ngram`/`ngram_gpu`/`suffix`/`mtp`/`eagle3`/`dflash` 等 |
| `model` | string | None | 草稿模型/EAGLE head 标识；ngram/suffix/mtp 常可省 |
| `draft_tensor_parallel_size` | int ≥1 | None | 草稿模型 TP 度 |
| `max_model_len` | int ≥1 | None | 草稿模型上下文上限 |
| `parallel_drafting` | bool | false | 并行起草（仅 EAGLE/draft-model） |
| `draft_sample_method` | string | greedy | greedy/probabilistic（概率比接受） |
| `use_heterogeneous_vocab` | bool | false | 异构词表草稿（仅 draft_model） |

`num_speculative_tokens` 控制每轮投机深度；Gemma 4 assistant checkpoint 必须走 `method: mtp`，误配 draft_model 会触发启动告警（F-154）。

## 观测：接受率

投机解码的调优指标是**接受率**（acceptance rate）：验证阶段被接受 token 占比，直接决定实际加速比。源码 `vllm/v1/spec_decode/metrics.py` 与 docs/features/speculative_decoding/acceptance_metrics.md 给出采集口径（F-116）。经验法则：接受率 < 40% 时应减小 `num_speculative_tokens` 或更换方法——投机深度超过模型「可预测性」后吞吐反降（F-117）。

## 训练自有草稿模型

EAGLE/draft 类方法可用 `vllm-project/speculators` 库训练草稿模型并无缝接入（F-118）；`extract_hidden_states.py` 负责从目标模型提取隐藏状态喂给草稿头。

## 相关阅读

- [04 调度与批处理](04-scheduling.md)：投机 token 如何参与调度与令牌预算
- [12 分布式推理](12-distributed.md)：`draft_tensor_parallel_size` 与 TP 体系
- [03 架构总览](03-architecture.md)：proposer 在请求生命周期中的位置
