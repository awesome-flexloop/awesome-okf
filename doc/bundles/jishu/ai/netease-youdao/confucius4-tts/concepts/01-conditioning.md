---
type: Concept
title: 条件化机制：prompt 掩码、说话人与风格嵌入
description: S2A 训练期 prompt 0–30% 随机掩码、prompt_cond 可学习参数、Qwen3-TTS 说话人编码器与 CAMPPlus 风格编码器如何共同构成声学条件。
tags: [confucius4-tts, tts, conditioning, prompt-masking, speaker-encoder]
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

# 条件化机制：prompt 掩码、说话人与风格嵌入

零样本声音克隆的本质问题是：**模型只能见到一次参考音频，就要在任意文本上复现其音色**。Confucius4-TTS 的答案是"训练期随机掩码 + 推理期全量提供"的不对称条件化设计。本篇拆解构成声学条件的全部构件。

## 条件构件全景

| 构件 | 类型 | 维度 | 来源 |
|---|---|---|---|
| prompt 参考 mel 特征（prompt_feat） | 训练期 0–30% 随机掩码 | — | 参考音频前端 |
| prompt_cond | nn.Parameter，形状 1×1×512 | 512 | `MaskedDiffWithXvec.__init__` 内创建，std=0.02 初始化 |
| 说话人嵌入（embedding） | Qwen3TTSSpeakerEncoder 输出，L2 归一化 | 192 | 参考音频 |
| 风格嵌入（style_embedding） | CAMPPlus（external.campplus.CAMPPlus） | 192 | 参考音频，仅 S2A 训练配置含此段 |
| 语义条件（semantic_token + lm_latent） | Text2Semantic 输出 | 8192 词表 + 1280 维 | T2S 段 |

S2A 模块 `MaskedDiffWithXvec` 的组件清单（F-c4t-022）揭示了条件注入的结构：InterpolateRegulator、ConditionalCFM、SemanticTokenEmbedding、encoder_proj（Linear，把 lm_latent_dim+semantic_embed_dim 投影到 lr_in_channels=1024）、以及 prompt_cond（形状 1×1×lr_out_channels=512，初始化 std=0.02 的可学习参数）。

## prompt 0–30% 随机掩码

训练前向时，S2A 对 prompt 特征按**随机比例 0–30% 掩码**（代码中随机比例上界为 0.3）（F-c4t-023）。这与 ConditionalCFM 的训练 CFG 条件丢弃率 `cfm_training_cfg_rate=0.2`（F-c4t-021、F-c4t-025）构成双重退化路径：模型必须在 prompt 信息残缺时，退化为仅靠语义 token + 说话人向量生成合理声学。

这一设计的反常识之处在于：**主动丢信息恰恰是泛化能力的来源**。模型无法过拟合特定 prompt，被迫学会保底路径，因此推理期即使参考音频较短或质量一般也能工作。掩码上界 0.3 是硬编码的经验值而非调度策略，微调时应与训练 CFG 率 0.2 作为一组联动超参处理。

## 说话人编码器：Qwen3TTSSpeakerEncoder

说话人条件由 `Qwen3TTSSpeakerEncoder` 提供，文件标注 "Modified from Qwen3-TTS"（F-c4t-019）。其结构为 TDNN + SE-Res2Net blocks + MFA + AttentiveStatisticsPooling + fc；`extract_embedding` 内含 L2 归一化。配置类 `Qwen3TTSSpeakerEncoderConfig` 默认值（F-c4t-018）：

| 键 | 默认值 |
|---|---|
| mel_dim | 128 |
| enc_dim | 1024 |
| enc_channels | [512, 512, 512, 512, 1536] |
| enc_kernel_sizes | [5, 3, 3, 3, 1] |
| enc_dilations | [1, 2, 3, 4, 1] |
| enc_res2net_scale | 8 |
| sample_rate | 24000 |

在 Text2Semantic（T2S）内部，它还充当条件向量来源之一：T2S 的子模块清单包含 Qwen3TTSSpeakerEncoder（F-c4t-014）。

## 风格编码器：CAMPPlus

风格条件来自 CAMPPlus：`style_encoder` 段声明 target=external.campplus.CAMPPlus、feat_dim=80、embedding_size=192、checkpoint=campplus_cn_common.bin（F-c4t-060），S2A 训练配置同样含此段，checkpoint 指向 ./pretrained/campplus/campplus_cn_common.bin（F-c4t-049）。值得注意的是 CAMPPlus 在 S2A 训练时被冻结（详见下文与 [06 两阶段训练](/concepts/06-training.md)）。

## T2S 侧的条件化：文本与位置

T2S 的文本侧条件化由 `TextEmbeddingProjector` 承担（F-c4t-017）：内部 nn.Embedding 冻结（requires_grad=False），结构为 Embedding → fc1(embed→embed) → SiLU → fc2(embed→output_size)，并提供 `load_pretrained_embeddings` 以载入预训练文本嵌入。配置默认 text_embedding_dim=4096、speaker_embedding_dim=1024（F-c4t-012）。

位置编码方面，Text2Semantic 基于 GPT2Model 改造：删除 wpe、换 DummyPositionEmbedding、删除 wte（F-c4t-014）；`llm/position_embeddings.py` 定义 DummyPositionEmbedding 与 LearnedPositionalEmbedding 两个类（F-c4t-020），text 与 semantic 各用一个 LearnedPositionalEmbedding。

## 训练-推理不对称

推理时 `MaskedDiffWithXvec.inference(semantic_token, lm_latent, prompt_feat, embedding, target_feat_len, n_timesteps=25, inference_cfg_rate=0.7)` 接受完整 prompt（F-c4t-024），并以 `cfm_inference_cfg_rate` 默认 0.7（F-c4t-021）做推理期 CFG——ConditionalCFM 采样时将 batch 翻倍拼接 conditional/unconditional 两支（F-c4t-025）。训练期 0.2 的丢弃率与推理期 0.7 的引导率构成"训练-推理不对称"，这是 CFG 生效的前提；改训练丢弃率时须同步重估推理率。

## 相关概念

- [00 仓库全景与推理链路总览](/concepts/00-overview.md)
- [03 声学生成：flow matching 与 DiT 估计器](/concepts/03-flow-matching.md)
- [06 两阶段训练与微调体系](/concepts/06-training.md)
