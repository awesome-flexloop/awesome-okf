---
type: Concept
title: 长度调节与时长启发式
description: InterpolateRegulator 的 nearest 上采样机制、int(T*1.72) 目标帧数启发式、cross_fade/edge_fade 段间拼接与文本分段策略——系统没有独立时长预测模块。
tags: [confucius4-tts, tts, length-regulation, duration, cross-fade]
generated: { by: "reference_agent/trae-solo", at: "2026-09-09T00:00:00Z" }
verified: { by: "process:source-reading-v", at: "2026-09-09T00:00:00Z" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: Confucius4-TTS 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: Confucius4-TTS 核心洞察与知识地图
---

# 长度调节与时长启发式

主流非自回归 TTS 通常显式建模时长（duration predictor 或单调对齐搜索），Confucius4-TTS 却**没有独立的时长预测模块**：语义 token 与 mel 帧的对应关系被压缩为一个标量系数 `1.72`，段间误差靠淡入淡出拼接掩盖。本篇拆解这一"估不准就拼接"的工程方案。

## 目标帧数启发式：int(T * 1.72)

段级 mel 目标长度由推理 CLI 层的启发式给出：`int(T * 1.72)`，其中 T 为该段文本的 token 数，位于 `ConfuciusTTS._synth_segment` 内（F-c4t-009）。该启发式**不在模型内部**——改写 `_synth_segment` 即可注入自定义长度源。

这一设计隐含强假设：训练数据的说话速率集中在一个较窄分布，系数 1.72 即平均 token→帧比。其代价是对快语速/慢语速文本的时长估计存在系统性偏差，且无 per-phoneme 级时长可控性；优点是链路极短、无可学习对齐模块。S2A 推理配置仅 6 键（input_size/output_size/spk_embed_dim/semantic_embed_dim/lm_latent_dim/estimator_mlp_ratio），无任何时长/韵律相关键（F-c4t-061），从配置层面印证了时长职责不在模型内。

## InterpolateRegulator：长度调节但不预测长度

`InterpolateRegulator`（confuciustts/flow/length_regulator.py）的职责是把条件序列**重采样**到目标长度，而非预测长度（F-c4t-026）：

- 入口投影 `content_in_proj`；
- 每层 Conv1d(kernel=3) + GroupNorm + Mish；
- 末端 Conv1d(kernel=1)；
- 以 `F.interpolate(mode="nearest")` 上采样至 `ylens.max()`。

nearest 插值是零开销的保持型上采样：它把每个语义 token 对应的条件"复制"到目标帧数。因此目标帧数必须外部给定——在推理中由 `int(T * 1.72)` 给出，在训练中由真实 mel 长度给出。

## 文本分段策略

长文本并非一次性送入，而是按 `max_text_tokens_per_segment=80` 切段（F-c4t-006）。分段长度与 1.72 系数联动决定单段音频时长上限：80 token × 1.72 ≈ 138 帧 mel，按 22050 Hz / hop_length=256 折算约 1.6 秒/段。vLLM 流式路径的段内还有进一步切块：first_chunk_size_tokens=25、chunk_size_tokens=50、overlap_tokens=10（F-c4t-037），切块粒度与段级启发式独立，详见 [05 vLLM 加速路径与服务化](/concepts/05-vllm-serving.md)。

## 段间拼接：cross_fade 与 edge_fade

各段音频经三段淡化处理后拼接（F-c4t-006、F-c4t-010）：

| 参数 | 默认值 | 作用 |
|---|---|---|
| cross_fade_duration | 0.3 s | 相邻段之间的交叉淡化，掩盖段边界 |
| edge_fade_duration | 0.1 s | 每段音频边缘的淡入淡出，避免爆音 |
| edge_pad_duration | 0.1 s | 段边缘的额外补零 |

当 `raw=True` 时，`generate` 跳过拼接，返回各段音频列表（F-c4t-007），调用者可自行实现拼接逻辑——这是注入自定义时长/韵律控制的另一个挂接点。

## 适配新语言时的注意事项

若把系统适配到新语言或新语速分布的数据，**必须重新标定 1.72 系数**：从训练集统计 token 数与 mel 帧数的平均比值，否则会整体语速偏移。若需字/词级时长控制，可在推理 CLI 层替换 `_synth_segment` 内的启发式，以外部长度源（如强制对齐结果）驱动 InterpolateRegulator 的目标帧数。

## 相关概念

- [00 仓库全景与推理链路总览](/concepts/00-overview.md)
- [03 声学生成：flow matching 与 DiT 估计器](/concepts/03-flow-matching.md)
- [05 vLLM 加速路径与服务化](/concepts/05-vllm-serving.md)
