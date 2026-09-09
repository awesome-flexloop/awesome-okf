---
type: concept
title: PromptTTS 风格条件注入
description: 剖析 StyleEncoder「多任务头训练、单嵌入推理」的非对称机制：simbert 底座、4 个分类头、768→128 维投影，以及 7 类情绪/3 类 pitch-energy-speed 标签体系。
tags: [emotivoice, tts, prompttts, style-encoder, emotion-control]
generated: { by: "reference_agent/trae-solo", at: 2026-09-09T00:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T00:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: EmotiVoice 源码事实清单（v0.3 @ 59f0f36）
  - id: insights
    resource: /references/insights.md
    title: EmotiVoice 架构洞察与知识地图（v0.3 @ 59f0f36）
---

# PromptTTS 风格条件注入

EmotiVoice 的名字来自其招牌能力：用一句**风格提示文本**（prompt）控制合成语音的情感与韵律。这一能力的核心件是 `models/prompt_tts_modified/simbert.py` 中的 `StyleEncoder`，其机制可概括为一句话——**多任务头训练、单嵌入推理**。

## StyleEncoder 的结构

`StyleEncoder(nn.Module)` 由三部分组成（F-ev-024）：

```
prompt 文本
   │
   ▼
self.bert = AutoModel.from_pretrained(config.bert_path)
   │  WangZeJun/simbert-base-chinese（F-ev-029）
   ▼
┌─────────────────────────────────────────────┐
│ 4 个 ClassificationHead（hidden → num_labels）│
│   pitch_outputs / speed_outputs /           │
│   energy_outputs / emotion_outputs           │  ← 训练期监督用
├─────────────────────────────────────────────┤
│ pooled_output                                 │
│   │                                          │
│   ▼                                          │
│ self.style_embed_proj = nn.Linear(           │  ← 推理期唯一出口
│     config.bert_hidden_size, config.style_dim)│
│   768 → 128（F-ev-029）                       │
└─────────────────────────────────────────────┘
   │
   ▼
style_embedding（128 维）
```

forward 返回一个 dict，键含 `pooled_output`、`pitch_outputs`、`speed_outputs`、`energy_outputs`、`emotion_outputs`（F-ev-024）。

## 非对称路径：训练与推理各取所需

**训练期**，4 个分类头对 simbert 表征施加有监督约束：pitch/speed/energy/emotion 四类风格因子各有标注数据，分类损失迫使 `pooled_output` 所在的表征空间把韵律与情感信息组织成可分的样子。README 的 ROADMAP 明确 style factors 仅用 pitch/speed/energy/emotion，**不使用 gender**（F-ev-042）。

**推理期**，分类头被完全旁路。`inference_tts.py` 的 `get_style_embedding(prompt, tokenizer, style_encoder)` 只取 `output["pooled_output"].cpu().squeeze().numpy()`——返回的是投影前的池化向量（F-ev-025）。联合训练时 StyleEncoder 以冻结方式加载（`load_state_dict(..., strict=False)` 且 key 经 `key[7:]` 去 `module.` 前缀），不参与梯度更新（F-ev-031，训练细节见 [04](/concepts/04-jets-joint-training.md)）。

换言之，分类头只是**训练期的监督脚手架**：它们塑造了嵌入空间，却在推理时零开销、零参与。

## 标签体系

风格监督信号来自 `data/youdao/text/` 下的标签文件（已逐文件计数，F-ev-027）：

| 标签文件 | 类别数 | 说明 |
|----------|--------|------|
| `emotion` | **7 类** | 普通/生气/开心/惊讶/悲伤/厌恶/恐惧 |
| `pitch` | 3 类 | 音高档位 |
| `energy` | 3 类 | 能量档位 |
| `speed` | 3 类 | 语速档位 |
| `speaker2` | 2014 行 | 说话人计数 |
| `tokenlist` | 502 行 | 词表符号数（n_symbols） |

`config/joint/config.py` 的 `get_labels_length` 直接从这些文件计数得到 `n_symbols`、`speaker_n_labels`、`emotion_n_labels` 等维度（F-ev-029），避免标签集变动时手工改配置。音色主要来自 LibriTTS/HiFiTTS 数据集，`data/youdao/text/README.md` 是完整的 voice wiki 表格（F-ev-028）。

## 风格嵌入的两路输入

推理调用中 `style_embedding` 与 `content_embedding` 都由同一个 `get_style_embedding` 计算（F-ev-020、F-ev-025）：

- **style_embedding**：prompt 文本（如 `Happy`）的嵌入，携带情感/韵律控制信号；
- **content_embedding**：原始 content 文本的嵌入，提供内容语义上下文。

二者在数据集侧也是对称设计：batch 键 `style_embedding` 与 `content_embedding` 分别由 prompt 与 original_text 计算（F-ev-026，数据工程见 [05](/concepts/05-labels-dataset-mfa.md)）。

## 实践含义

1. **自定义风格无需重训分类头**：新 prompt 文本经同一 simbert 底座计算 `pooled_output` 再过 `style_embed_proj` 即得风格嵌入；想改造风格空间，优先替换 `style_encoder_ckpt`（config 中为 `outputs/style_encoder/ckpt/checkpoint_163431`，F-ev-029），而非触碰联合训练主链路。
2. **prompt 不是魔法咒语**：源码中固定 prompts 列表仅 `['Happy', 'Excited', 'Sad', 'Angry']` 四个英文词，并注释 `# prompt is not efficient.`（F-ev-025）——prompt 对声学风格的控制粒度有限，精细控制仍依赖标签监督所覆盖的四类风格因子。
3. **评估风格保真度**应回到 7 类情绪 × 3 类 pitch/energy/speed 的标签空间（F-ev-027），而非仅凭听感。

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)
- [05 标签体系、数据集与 MFA 对齐流水线](/concepts/05-labels-dataset-mfa.md)
