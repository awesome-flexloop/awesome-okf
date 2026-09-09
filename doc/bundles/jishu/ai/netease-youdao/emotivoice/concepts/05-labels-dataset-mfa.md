---
type: concept
title: 标签体系、数据集与 MFA 对齐流水线
description: 从 data/youdao/text 标签文件到 mfa/ 八步脚本，理解训练数据如何被制备、对齐与插桩，以及 sp 标记家族贯穿前端与数据的隐形契约。
tags: [emotivoice, tts, dataset, mfa, alignment, data-pipeline]
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

# 标签体系、数据集与 MFA 对齐流水线

多数 TTS 教程把注意力放在模型结构上，而 EmotiVoice 源码里**训练数据准备是与模型同等篇幅的工程**：`mfa/` 下 8 个 step 脚本，与模型目录 11 个 `.py` 文件相当（F-ev-037）。本文从标签文件出发，走完数据从原始语料到可训练清单的完整旅程。

## 标签体系与词表

训练监督所需的全部标签集中存放在 `data/youdao/text/` 下（已逐文件计数，F-ev-027）：

| 文件 | 实测规模 | 用途 |
|------|----------|------|
| `speaker2` | 2014 行 | 说话人列表，推理时的音色名（如 `8051`）来源 |
| `tokenlist` | 502 行 | 词表（n_symbols），构建 token2id 映射 |
| `emotion` | 7 类 | 普通/生气/开心/惊讶/悲伤/厌恶/恐惧 |
| `pitch` / `energy` / `speed` | 各 3 类 | 风格因子档位标注 |

`config/joint/config.py` 的 `get_labels_length` 从上述文件**计数**得出 `n_symbols`、`speaker_n_labels`、`emotion_n_labels` 等模型维度（F-ev-029），标签集扩展无需手工改配置。音色主要来自 LibriTTS/HiFiTTS 数据集，`data/youdao/text/README.md` 是完整的 voice wiki 表格（F-ev-028）。

## 数据集与风格嵌入缓存

`models/prompt_tts_modified/prompt_dataset.py` 的 `Dataset_PromptTTS(torch.utils.data.Dataset)` 定义了 `get_style_embedding(self, uttid, prompt, dir)`（L106）：风格嵌入以 **npy 文件离线缓存**——存在则 `np.load` 直接读入，不存在则现场计算后 `np.save`（F-ev-026）。由于 StyleEncoder 在联合训练中是冻结的（见 [04](/concepts/04-jets-joint-training.md)），嵌入只与文本有关、与模型参数无关，离线缓存完全安全，避免了训练时反复跑 simbert。

collate 由 `TextMelCollate(self, data)` 完成（L179；另有一个同名方法在 `Dataset_Prompt_Pretrain` 的 L292）（F-ev-026）。batch 键含 `style_embedding` 与 `content_embedding`，分别由 prompt 与 original_text 计算（F-ev-026）——与推理侧的两路嵌入对称（见 [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)）。

## MFA 对齐流水线：八步脚本

`mfa/` 目录共 8 个 step 脚本（编号**无 step6**，已 Glob 计数，F-ev-037）：

| 脚本 | 职责 |
|------|------|
| `step1_create_dataset.py` | datalist.jsonl → `text_sp1-sp4` 与 `wav.scp`，做 `cn_eng_sp→cnengsp` 等特殊标记转换 |
| `step2_prepare_data.py` | 数据准备 |
| `step3_prepare_special_tokens.py` | 特殊 token 准备 |
| `step4_convert_text_to_phn.py` | 文本转音素 |
| `step5_prepare_alignment.py` | 对齐输入准备 |
| `step7_gen_alignment_from_textgrid.py` | 读 TextGrid 生成对齐，向对齐音素序列插入 special tokens |
| `step8_make_data_list.py` | 生成数据清单 |
| `step9_datalist_from_mfa.py` | 由 MFA 结果产出最终 datalist |

两个关键实现细节：

1. **特殊标记转换**：step1 把前端的 `cn_eng_sp` 等跨界标记规范为 `cnengsp` 形式（F-ev-038），与 [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md) 的输出约定对接；
2. **MFA 版本兼容**：step7 用 `praatio.textgrid.openTextgrid` 读 TextGrid，对 MFA 1.x / 2.x 的空标签行为差异做了显式兼容，并负责向对齐后的音素序列插入 special tokens（F-ev-038）。

## sp 标记家族：贯穿全链路的隐形契约

把前端与数据工程串起来看，`sp` 标记家族在**三处**必须保持一致：

```
① 前端生成    g2p_cn_en 输出 sp0/sp1/sp3、engsp1/engsp4、cn_eng_sp/eng_cn_sp
                    │
                    ▼（step1 转换）
② MFA 转换    cn_eng_sp → cnengsp，text_sp1-sp4 进入对齐
                    │
                    ▼（step7 插桩）
③ 对齐插桩    special tokens 按对齐时序插入最终音素序列
```

任何一处约定不一致（比如前端改了标记名而 step1 未同步），对齐插桩位置就会错位，训练数据随之损坏。这就是「新建语料的 sp 标记约定必须与 `frontend.py` 输出严格对齐」的原因（F-ev-004、F-ev-038）。

## 复刻训练流程的行动清单

1. **先跑通 MFA 对齐链路再谈训练**：8 个 step 脚本是数据进入训练前的唯一通道（F-ev-037）；
2. **风格嵌入离线缓存**：复用 `Dataset_PromptTTS` 的 npy 缓存模式，避免训练时重复计算 simbert（F-ev-026）；
3. **标签扩展走文件**：新增情绪/说话人时改 `data/youdao/text/` 下对应文件，`get_labels_length` 会自动更新模型维度（F-ev-029）；
4. **对齐质量直接决定 special token 插桩的正确性**：step7 对 MFA 大版本差异的兼容逻辑（F-ev-038）提示我们，升级 MFA 工具版本前须先验证空标签行为。

## 相关概念

- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)
- [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)
