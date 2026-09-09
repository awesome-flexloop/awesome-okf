---
type: concept
title: EmotiVoice 整体架构与推理入口
description: 从推理主入口 inference_am_vocoder_joint.py 与测试文本四段格式出发，建立「文本前端 → PromptTTS 声学模型 → HiFiGAN 声码器」三段式整体认知，并了解批量推理入口 inference_tts.py。
tags: [emotivoice, tts, architecture, inference]
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

# EmotiVoice 整体架构与推理入口

EmotiVoice 是网易有道开源的多音色、富情感文本转语音（TTS）系统，许可证为 Apache-2.0（F-ev-042）。本文从推理主入口出发，建立对系统整体数据通路的认知，是学习本 bundle 其余概念文档的起点。

## 推理主入口

仓库的联合推理主入口是 `inference_am_vocoder_joint.py`（F-ev-001）。README 给出的标准推理命令为（F-ev-002）：

```bash
python inference_am_vocoder_joint.py \
    --logdir prompt_tts_open_source_joint \
    --config_folder config/joint \
    --checkpoint g_00140000 \
    --test_file $TEXT
```

输出写入 `outputs/prompt_tts_open_source_joint/test_audio` 目录（F-ev-002）。

## 三段式数据通路

一次推理在概念上分为三段，前段产出音素序列，后两段由单个 `JETSGenerator` 内联完成：

```
原始文本
   │  ① 文本前端（frontend.py 等）
   ▼
音素序列（<sos/eos> 包裹，含 sp 停顿与跨界标记）
   │  ② PromptTTS 声学模型（JETSGenerator.am）
   ▼
声学特征（mel 谱）
   │  ③ HiFiGAN 声码器（JETSGenerator.generator）
   ▼
16 kHz 波形（int16）
```

- 前端负责把中英混合文本转成模型可读的特殊 token 序列，详见 [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)；
- `JETSGenerator` 在单个 `nn.Module` 中内联 `PromptTTS` 声学模型与 HiFiGAN 生成器，一次 forward 从音素直达波形（F-ev-018），详见 [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)；
- 推理输出经 `infer_output["wav_predictions"].squeeze() * MAX_WAV_VALUE`（即 32768.0，F-ev-022）转 `int16`，再由 `soundfile` 以 `config.sampling_rate`（16 000 Hz，F-ev-029）写出（F-ev-020）。注意采样率为 16 kHz，低于常见的 22.05/24 kHz 惯例。

## 测试文本格式

主入口按行读取测试文件，每一行按 `|` split 为 4 段：speaker、prompt、phoneme text、content（F-ev-001）。README 定义的格式为（F-ev-003）：

```
<speaker>|<style_prompt/emotion_prompt/content>|<phoneme>|<content>
```

| 字段 | 含义 | 取值来源 |
|------|------|----------|
| speaker | 说话人标识 | `data/youdao/text/speaker2` 中的音色名（如 `8051`） |
| prompt | 风格提示文本 | 自由文本，如 `Happy`；也会被用作风格嵌入输入 |
| phoneme | 音素序列 | 由前端（`frontend.py`）对 content 处理得到 |
| content | 原始文本 | 人类可读的中英混合文本 |

输出音频按行号命名，写入 `root_path + "/test_audio/audio/" + checkpoint_name + "/{i+1}.wav"`（F-ev-001）。

## 推理时的模型装配

主入口在 `main(args, config)` 中完成以下装配（可从推理命令的参数与 checkpoint 命名反推，细节见 [04](/concepts/04-jets-joint-training.md)）：

1. 从 `ckpt` 目录选出目标 checkpoint（如 `g_00140000`）；
2. 构造 `StyleEncoder` 并加载风格编码器 checkpoint（F-ev-001 隐含的装配步骤，风格机制详见 [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)）；
3. 构造 `JETSGenerator` 并加载 `checkpoint['generator']` 权重（F-ev-020 的同构调用见 `inference_tts.py`）；
4. 读入 `token2id` 与 `speaker2id` 映射，把音素序列与说话人名转为整数 id；
5. 对每行文本计算风格嵌入与内容嵌入，调用生成器并写出波形。

核心推理调用签名（F-ev-020）：

```python
generator(
    inputs_ling=sequence,                 # 音素 id 序列
    inputs_style_embedding=style_embedding,
    input_lengths=sequence_len,
    inputs_content_embedding=content_embedding,
    inputs_speaker=speaker,
    alpha=1.0,                            # 语速因子，推理期写死
)
```

注意 `alpha=1.0` 在推理中写死——速度控制并非模型内生能力，服务层的 `speed` 参数走的是外部后处理，详见 [06 服务化部署](/concepts/06-serving-api.md)。

## 批量推理入口 inference_tts.py

`inference_tts.py` 是面向批量评测的入口：入口函数签名为 `main(args, config, gpu_id, start_idx, chunk_num)`，按 `gpu_ids` 与 `num_thread` 对测试文件分块，多进程并行推理（F-ev-021）。与主入口不同，它直接用 `g2p_cn_en` 对每行原始文本现场做 g2p（F-ev-021），并内置固定风格列表 `['Happy', 'Excited', 'Sad', 'Angry']` 供轮换取样——源码注释直言 `# prompt is not efficient.`（F-ev-025）。

## 学习路径建议

- 想理解音素序列如何生成 → [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- 想理解 prompt 如何影响情感 → [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)
- 想动手跑一次推理 → [联合推理完整流程示例](/examples/joint-inference-workflow.md)

## 相关概念

- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)
- [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)
- [06 服务化部署](/concepts/06-serving-api.md)
