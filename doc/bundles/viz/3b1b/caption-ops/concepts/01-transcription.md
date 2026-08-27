---
type: Concept
title: 音频转录模块
description: caption-ops 的音频转录模块支持 faster-whisper 本地转录与 OpenAI API 云端转录双模式，采用云端优先、本地兜底的回退策略，核心输出词级时间戳而非直接生成 SRT，为后续句子对齐和智能分段提供基础数据。
tags: [caption-ops, transcription, whisper, faster-whisper, word-timestamps, asr, speech-to-text]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: caption-ops 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: caption-ops 源码架构洞察
---

# 音频转录模块

音频转录（Audio Transcription）是字幕管线的第一个核心环节，负责将音频中的语音转换为带时间戳的文本。caption-ops 的转录模块最反直觉的设计是：**它不直接输出最终可用的 SRT 字幕**，而是输出**词级时间戳（word-level timestamps）**——即每个单词在音频中开始和结束的精确时间（F-023、F-027）。

为什么要"多此一举"拿到词级时间再自己重新分段？因为 Whisper 原生输出的 segment 分段是基于音频停顿的，并不对应自然语言的句子边界——经常把两句话切在一起，或者一句话拆成多段，而且单段长度不受控。拿到全量词级时间戳后，caption-ops 可以自己按语言标点分句、按字符数限制智能分段，这是生成高质量字幕的基础（洞察 I-01）。

本模块覆盖事实 F-021~F-030。

## 转录功能概述

转录模块实现在 `transcribe_video.py` 文件中，提供三种转录方式：

1. **本地 faster-whisper 转录**：使用 CTranslate2 引擎的本地模型，无需 API 密钥，CPU 即可运行（F-021~F-024）
2. **OpenAI API 云端转录**：调用 OpenAI Whisper API，转录质量更高，需要 `OPENAI_KEY` 环境变量（F-025）
3. **双轨自动回退**：优先尝试云端 API，失败时自动回退到本地模型，保证工作流不中断（F-026、洞察 I-02）

无论哪种模式，输出格式统一兼容 OpenAI Whisper 格式：包含 `text`（完整文本）、`segments`（分段列表）、`language`（语言代码，固定为 `"en"`）三个字段；开启词级时间戳时，每个 segment 额外包含 `words` 列表，每一项有 `word`、`start`、`end` 三个字段（F-023）。

> ⚠️ **注意**：转录模块目前硬编码为英文转录（`language="en"`），因为 3Blue1Brown 视频都是英文旁白。如果你需要处理其他语言，需要修改代码中 `language` 参数。

## faster-whisper 本地转录模式

本地转录使用 **faster-whisper** 库——这不是 OpenAI 官方的 whisper 实现，而是基于 CTranslate2 推理引擎的优化版本，速度比官方实现快 4 倍以上，且支持 int8 量化在 CPU 上高效运行（F-021）。

### 模型加载

模型加载通过 `load_whisper_model()` 函数实现，带有 `@lru_cache()` 装饰器，同一进程内只加载一次（F-022）：

```python
from faster_whisper import WhisperModel

@lru_cache()
def load_whisper_model(model_name="medium.en"):
    return WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8"
    )
```

默认参数说明：
- `model_name="medium.en"`：默认加载英文专用 medium 模型，这是质量和速度的平衡点
- `device="cpu"`：强制使用 CPU 运行，不依赖 GPU——这是为个人工作流设计的务实选择："没有 GPU 也能跑"比"有 GPU 时更快"更重要（洞察 I-02）
- `compute_type="int8"`：使用 8 位整数量化，大幅降低内存占用和推理速度，精度损失极小

### 模型大小选择

faster-whisper 提供多种模型大小，你可以根据自己的硬件和质量需求选择：

| 模型 | 参数量 | 内存占用（int8） | 速度 | 质量 | 推荐场景 |
|------|--------|-----------------|------|------|----------|
| `tiny.en` | 39M | ~100MB | 极快 | 一般 | 快速预览、草稿字幕 |
| `base.en` | 74M | ~150MB | 很快 | 还行 | 简单场景 |
| `small.en` | 244M | ~400MB | 快 | 良好 | 日常使用 |
| `medium.en` | 769M | ~1GB | 中等 | 优秀 | **默认推荐**，平衡之选 |
| `large-v2`/`large-v3` | 1550M | ~2GB | 慢 | 最佳 | 有 GPU、追求最高质量 |

> 💡 对于 3Blue1Brown 这类发音清晰、背景噪音小的教育类视频，`medium.en` 的质量已经足够好，在现代 CPU 上转录 10 分钟视频大约需要 1-2 分钟。

### 本地转录函数

核心转录函数是 `transcribe_file()`（F-023）：

```python
def transcribe_file(model, audio_file, word_timestamps=True):
    segments, info = model.transcribe(
        audio_file,
        language="en",
        beam_size=1,
        word_timestamps=word_timestamps,
    )
    
    # tqdm 进度条按音频秒数更新（F-024）
    with tqdm(total=info.duration, desc="Transcribing") as pbar:
        result_segments = []
        for segment in segments:
            segment_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
            if word_timestamps:
                segment_dict["words"] = [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in segment.words
                ]
            result_segments.append(segment_dict)
            pbar.update(segment.end - segment.start)
    
    return {
        "text": " ".join(s["text"].strip() for s in result_segments),
        "segments": result_segments,
        "language": "en",
    }
```

注意参数 `beam_size=1` 使用贪心解码而非束搜索——这又是一个务实的工程选择：束搜索（beam_size=5）能略微提升质量但速度慢很多，对于教育视频这种清晰语音场景，贪心解码已经足够。

## OpenAI API 云端转录模式

如果你配置了 `OPENAI_KEY` 环境变量，转录模块可以调用 OpenAI 的 Whisper API 进行云端转录（F-025）：

```python
from openai import OpenAI
import os

def transcribe_file_api(audio_file, word_timestamps=True):
    client = OpenAI(api_key=os.environ["OPENAI_KEY"])
    
    with open(audio_file, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"] if word_timestamps else [],
        )
    
    # 返回格式与本地转录统一
    return {
        "text": result.text,
        "segments": result.segments,
        "language": result.language,
    }
```

### 云端转录的优缺点

| 维度 | OpenAI API 转录 | 本地 faster-whisper 转录 |
|------|----------------|-------------------------|
| 质量 | 更高（Whisper 大模型+持续优化） | 良好（medium 模型足够） |
| 速度 | 快（云端并行） | 中等（取决于 CPU/GPU） |
| 网络要求 | 需要联网 | 完全离线可用 |
| 成本 | 按音频时长计费（$0.006/分钟） | 免费 |
| 隐私 | 音频需上传到 OpenAI | 音频完全本地处理 |
| 配置 | 需要 `OPENAI_KEY` | 无需配置 |

## 双轨回退策略

caption-ops 默认使用 `transcribe_file_with_fallback()` 函数，自动在两种模式间切换（F-026、洞察 I-02）：

```python
def transcribe_file_with_fallback(audio_file, word_timestamps=True):
    try:
        return transcribe_file_api(audio_file, word_timestamps)
    except Exception:
        model = load_whisper_model()
        return transcribe_file(model, audio_file, word_timestamps)
```

策略逻辑很简单：
1. **云端优先**：先尝试 OpenAI API——质量更高、速度更快
2. **本地兜底**：API 调用失败（网络问题、密钥未配置、配额用完、API 故障等）时，自动回退到本地 faster-whisper
3. **对用户透明**：调用方不需要关心底层用的是哪个，返回格式完全统一

这种"云端优先+本地兜底"的混合策略是 caption-ops 鲁棒性设计的核心：它不强迫你在"质量"和"可用性"之间二选一——API 可用时享受高质量，API 不可用时工作也不会卡住。本地模型特意选择 CPU int8 量化，不是为了极致性能，而是为了"在任何环境下都能完成工作"（洞察 I-02）。

## 词级时间戳（Word-level Timestamps）核心机制

词级时间戳是整个转录模块最重要的输出，也是后续所有处理（句子对齐、智能分段、人工修正同步）的基础。

### 为什么不用 Whisper 直接分段？

这是初学者最常问的问题：Whisper 已经输出了带时间的 segments，为什么不直接用它生成 SRT？答案是：**Whisper 的分段是按音频停顿切的，不是按语言结构切的**（洞察 I-01）。

举个例子，Whisper 可能输出这样的分段：

```
[0.0s - 3.2s] "Today I want to talk about linear algebra, which is"
[3.2s - 7.1s] "the branch of mathematics concerning vectors and matrices."
```

第一句结尾落在"which is"，第二句开头才是完整的句子——这不符合自然阅读习惯，字幕突然断掉会让观众很不舒服。更糟糕的是，当你把这样的分段翻译成中文/日文时，句子长度变化可能导致某段特别长或特别短，直接用 Whisper 分段无法控制。

而词级时间戳给你的是：

```json
[
  ["Today", 0.0, 0.2],
  ["I", 0.2, 0.3],
  ["want", 0.3, 0.5],
  ["to", 0.5, 0.6],
  ["talk", 0.6, 0.9],
  ["about", 0.9, 1.1],
  ["linear", 1.1, 1.5],
  ["algebra,", 1.5, 2.0],
  ["which", 2.0, 2.2],
  ["is", 2.2, 2.4],
  ["the", 2.4, 2.5],
  ...
]
```

有了每个词的精确时间，caption-ops 就可以：
1. 把所有词拼接成完整文本
2. 按句号、问号、感叹号等自然句末标点分割成句子（支持多语言标点，F-005）
3. 在全文中定位每个句子的位置，映射回最近的词时间戳得到句子起止时间
4. 按每行字符数限制（非中日韩 90 字符，中日韩 30 字符）智能分段，优先在标点/空格处切割
5. 人工修正转录文本后，通过模糊匹配自动重新对齐时间轴，不需要重新转录

### 提取词级时间戳

`get_words_with_timings()` 函数从 Whisper 转录结果中提取统一格式的词级时间列表（F-027）：

```python
def get_words_with_timings(whisper_segments, precision=2):
    words = []
    for segment in whisper_segments["segments"]:
        for word_info in segment.get("words", []):
            words.append([
                word_info["word"].strip(),
                round(word_info["start"], precision),
                round(word_info["end"], precision),
            ])
    return words
```

返回格式是 `[[word, start, end], ...]` 的二维列表，时间戳保留 `precision` 位小数（默认 2 位，即 10 毫秒精度）。

### 保存词级时间戳

`save_word_timings()` 函数将词级时间戳保存为无缩进 JSON 文件（F-028）：

```python
def save_word_timings(whisper_transcription, file_path):
    words = get_words_with_timings(whisper_transcription)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
```

这个 `word_timings.json` 是字幕管线中最重要的中间产物——所有后续处理都基于它，人工修正转录后也只需要重新生成它下游的产物，不需要重新跑转录。

## 转录输出格式

一次完整的转录会生成多个产物文件，每个文件有不同的用途（F-063）：

| 文件 | 格式 | 用途 | 是否可人工编辑 |
|------|------|------|----------------|
| `word_timings.json` | JSON 数组 `[[word, start, end], ...]` | 词级原始时间数据，所有后续处理的基础 | 一般不直接编辑 |
| `sentence_timings.json` | JSON `{sentences: [...], time_ranges: [...]}` | 按自然句子对齐后的时间 | 一般不直接编辑 |
| `transcript.txt` | 纯文本 | 完整转录文本，**人工修正的主要入口** | ✅ 推荐直接编辑 |
| `full_sentences.srt` | SRT | 按完整句子分割的 SRT（可能很长） | 可以编辑 |
| `captions.srt` | SRT | 按字符数智能分段的最终字幕 | ✅ 可以编辑后直接上传 |

## 命令行用法示例

### 示例 1：单文件快速转录（纯本地）

给本地音频文件生成英文字幕，不需要任何 API 密钥：

```bash
# 进入 caption_ops 目录
cd path/to/caption_ops

# 转录单个音频文件（使用本地 medium.en 模型）
python scripts/transcribe.py /path/to/your/audio.mp3
```

运行完成后，在音频文件同目录生成：
- `word_timings.json` - 词级时间戳
- `transcription_sentences.srt` - 句子级 SRT
- `captions.srt` - 分段后的字幕（每行最多 50 字符，F-066）

### 示例 2：使用 Python API 转录

如果你想在自己的脚本中调用转录功能：

```python
from transcribe_video import (
    transcribe_file_with_fallback,
    save_word_timings,
    words_with_timings_to_srt,
)

# 自动选择云端/本地模式转录
audio_path = "/path/to/audio.mp3"
result = transcribe_file_with_fallback(audio_path)

# 保存词级时间戳
save_word_timings(result, "word_timings.json")

# 直接从词级时间生成 SRT
words_with_timings_to_srt(
    get_words_with_timings(result),
    "output.srt"
)
```

### 示例 3：指定模型大小转录本地文件

```python
from transcribe_video import load_whisper_model, transcribe_file, save_word_timings

# 使用 small 模型（更快，质量略低）
model = load_whisper_model("small.en")
result = transcribe_file(model, "/path/to/audio.mp3")
save_word_timings(result, "word_timings_small.json")
```

## 相关概念

- [00 caption-ops 工具集总览](00-caption-ops-overview.md)
- [02 多语言翻译模块](02-translation.md)
- [句子时间对齐机制](03-srt-operations.md)
- [CLI 脚本参考](../references/scripts-reference.md)
- [依赖与 API 配置](../references/dependencies.md)
