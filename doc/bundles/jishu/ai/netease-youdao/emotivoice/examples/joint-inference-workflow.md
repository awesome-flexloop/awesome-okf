---
type: example
title: 联合推理完整流程示例
description: 基于 inference_am_vocoder_joint.py 演练一次完整 TTS 推理：准备四段式测试文件、执行推理命令、拆解内部装配与生成调用、定位输出音频。
tags: [emotivoice, tts, inference, example]
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

# 联合推理完整流程示例

本例基于推理主入口 `inference_am_vocoder_joint.py`，从零演练一次完整的 TTS 推理：从准备测试文件到拿到 `1.wav`。概念背景见 [00 整体架构与推理入口](/concepts/00-architecture.md)。

## 第 1 步：准备测试文件

主入口按行读取测试文件，每行按 `|` split 为 4 段：speaker、prompt、phoneme text、content（F-ev-001），格式为 `<speaker>|<style_prompt/emotion_prompt/content>|<phoneme>|<content>`（F-ev-003）。创建 `data/test.txt`：

```
8051|Happy|<sos/eos> jin1 tian1 tian1 qi4 zhen1 hao3 <sos/eos>|今天天气真好
```

四个字段的取值来源：

- `8051`：说话人标识，须存在于 `data/youdao/text/speaker2`（2014 个音色之一，F-ev-027）；
- `Happy`：风格提示文本，进入风格嵌入计算（F-ev-025）；
- `<sos/eos> ... <sos/eos>`：音素序列，由前端生成——实际使用中**不需要手敲**，用 [中英混读文本处理示例](/examples/mixed-lingual-g2p.md) 中的命令从 content 生成；
- `今天天气真好`：原始文本，作为 content 嵌入的输入。

## 第 2 步：执行推理命令

README 给出的推理命令（F-ev-002）：

```bash
python inference_am_vocoder_joint.py \
    --logdir prompt_tts_open_source_joint \
    --config_folder config/joint \
    --checkpoint g_00140000 \
    --test_file data/test.txt
```

- `--checkpoint g_00140000` 对应 checkpoint 命名规则 `g_{:08d}`（F-ev-032）；
- 若省略 `--checkpoint`，入口会遍历 `ckpt` 目录下全部 checkpoint 逐个推理（F-ev-001 的逐文件循环逻辑）。

## 第 3 步：理解内部装配（等价代码）

推理命令背后，`main(args, config)` 对每一行文本执行如下关键步骤（F-ev-001、F-ev-020）：

```python
# (a) 风格嵌入与内容嵌入：同一 get_style_embedding，两个文本输入（F-ev-025）
style_embedding   = get_style_embedding(prompt,  tokenizer, style_encoder)
content_embedding = get_style_embedding(content, tokenizer, style_encoder)

# (b) 说话人与音素序列转 id（token2id 来自 502 行 tokenlist，F-ev-027）
speaker  = speaker2id[speaker]                    # '8051' → int
text_int = [token2id[ph] for ph in text]          # 音素 → id

# (c) 组 batch（单条样本，unsqueeze(0) 补 batch 维）
sequence        = torch.from_numpy(np.array(text_int)).to(device).long().unsqueeze(0)
sequence_len    = torch.from_numpy(np.array([len(text_int)])).to(device)
style_embedding = torch.from_numpy(style_embedding).to(device).unsqueeze(0)
content_embedding = torch.from_numpy(content_embedding).to(device).unsqueeze(0)
speaker         = torch.from_numpy(np.array([speaker])).to(device)

# (d) 生成器调用（F-ev-020）
with torch.no_grad():
    infer_output = generator(
        inputs_ling=sequence,
        inputs_style_embedding=style_embedding,
        input_lengths=sequence_len,
        inputs_content_embedding=content_embedding,
        inputs_speaker=speaker,
        alpha=1.0,                                # 语速写死，speed 走服务层后处理
    )

# (e) 波形后处理与写出（F-ev-020、F-ev-022）
audio = infer_output["wav_predictions"].squeeze() * MAX_WAV_VALUE  # 32768.0
audio = audio.cpu().numpy().astype('int16')
sf.write(file=output_path, data=audio, samplerate=config.sampling_rate)  # 16000 Hz
```

## 第 4 步：定位输出

输出按行号命名，写入（F-ev-001）：

```
outputs/prompt_tts_open_source_joint/test_audio/audio/g_00140000/1.wav
```

其中 `1.wav` 的 `1` 来自 `{i+1}` 行号（F-ev-001），输出根目录与 README 记载一致（F-ev-002）。采样率为 16 kHz 单声道 int16（F-ev-029）。

## 常见错误排查

| 现象 | 原因 | 对策 |
|------|------|------|
| 某行无对应输出 | speaker 不在 `speaker2id` 中，入口 `continue` 跳过（F-ev-001） | 核对音色名拼写 |
| `KeyError` 于 token2id | 音素序列含未登记符号 | 先用 `python frontend.py` dump 音素核对（F-ev-005） |
| 情感无变化 | prompt 控制粒度有限（源码注释 `# prompt is not efficient.`，F-ev-025） | 尝试 `Happy/Excited/Sad/Angry` 四个固定词对比 |

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)
- [中英混读文本处理示例](/examples/mixed-lingual-g2p.md)
