---
type: Reference
title: Caption Ops CLI 脚本参数速查表
description: caption-ops 字幕工具集所有命令行脚本的完整参数速查，按功能分组，含常用命令示例。
tags: [caption-ops, cli, scripts, parameters, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26T00:00:00Z" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: caption-ops 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: caption-ops 架构洞察
  - id: self
    resource: /references/scripts-reference.md
    title: Caption Ops CLI 脚本参数速查表
---

# Caption Ops CLI 脚本参数速查表

本文档基于 caption-ops 源码事实采集（F-063~F-070），整理 `scripts/` 目录下所有 CLI 脚本及根目录独立工具脚本的参数说明与典型用法。

## 目录概览

caption-ops 工具集包含两类可执行脚本（F-001）：

| 位置 | 脚本数量 | 说明 |
|------|----------|------|
| `scripts/` 目录 | 8个 | 面向完整工作流的 CLI 脚本 |
| 根目录 | 若干 | 独立功能工具（SRT时间调整、贡献者追踪等） |

---

## 一、端到端自动字幕管线

### scripts/auto_caption.py — 一键自动字幕管线（转录→翻译→上传）

端到端自动字幕处理脚本，是最常用的入口命令。

**位置参数**（F-065）：

| 参数名 | 类型 | 说明 | 事实依据 |
|--------|------|------|----------|
| `video` | 字符串 | YouTube URL 或包含 URL 列表的 txt 文件路径 | F-065 |

**可选参数**（F-065）：

| 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|------|--------|------|----------|
| `--languages` | 字符串 | | 目标语言列表，传 `all` 表示翻译到全部 19 种目标语言 | F-065、F-033 |
| `--no-upload` | 布尔标志 | `False` | 禁用自动上传到 YouTube，仅生成本地文件 | F-065 |

**核心处理流程**（F-064）：

1. 定位本地音频文件（优先 `only_narration.mp3/wav`，其次 `original_audio.mp3/wav`）
2. 调用 `write_whisper_transcription_files()` 生成英文转录产物（F-063）
3. 翻译到指定语言
4. 上传不匹配的字幕（未指定 `--no-upload` 时）

**生成的英文转录产物**（F-063）：

| 文件名 | 说明 |
|--------|------|
| `word_timings.json` | 词级时间戳 |
| `sentence_timings.json` | 句级时间戳 |
| `full_sentences.srt` | 完整句子 SRT |
| `captions.srt` | 分段 SRT（适合字幕显示） |
| `transcript.txt` | 纯文本转录稿 |

**典型用法示例**：

```bash
# 单个视频：英文转录 + 翻译到中文 + 自动上传
python scripts/auto_caption.py https://www.youtube.com/watch?v=VIDEO_ID --languages Chinese

# 单个视频：翻译到所有支持语言 + 自动上传
python scripts/auto_caption.py https://www.youtube.com/watch?v=VIDEO_ID --languages all

# 批量处理：从txt文件读取URL列表，仅生成本地文件不上传
python scripts/auto_caption.py video_urls.txt --languages Spanish,French,German --no-upload
```

---

## 二、转录相关脚本

### scripts/transcribe.py — 单个音频文件转录

单文件转录工具，不依赖视频 URL，直接处理本地音频文件。

**位置参数**（F-066）：

| 参数名 | 类型 | 说明 | 事实依据 |
|--------|------|------|----------|
| `audio_file` | 路径 | 本地音频文件路径（支持 mp3/wav 格式） | F-066 |

**输出产物**（F-066）：

| 文件名 | 说明 |
|--------|------|
| `transcription_sentences.srt` | 句子级 SRT |
| `captions.srt` | 分段 SRT（`max_chars_per_segment=50`，适合短字幕） |
| `word_timings.json` | 词级时间戳 JSON |

**典型用法示例**：

```bash
# 转录单个音频文件
python scripts/transcribe.py path/to/audio.mp3
```

---

## 三、SRT 处理与同步脚本

### scripts/sync_all_captions.py — 全量字幕同步生成与上传

从翻译 JSON 文件重新生成各语言 SRT，处理审核状态。

**核心功能**（F-067）：
- 从翻译 JSON 重新生成 SRT 文件
- 当审核比例 > 50% 时，将旧的 `community.srt` 重命名为 `community_old.srt`
- 遇到空翻译条目自动跳过

**典型用法示例**：

```bash
# 从指定翻译文件重新同步SRT
python scripts/sync_all_captions.py path/to/sentence_translations.json
```

### scripts/sync_transcription_update.py — 转录更新后同步翻译

人工修改转录文本后，自动重新对齐时间轴并同步所有语言的翻译。

**核心功能**（F-068）：
- 接受修改后的 `transcript.txt` 或 `captions.srt`
- 重新分句并更新 `sentence_timings.json`
- 使用模糊匹配算法更新各语言 `sentence_translations.json` 中的 input 字段
- 可选上传更新后的字幕

**典型用法示例**：

```bash
# 人工编辑transcript.txt后，同步更新所有语言翻译
python scripts/sync_transcription_update.py path/to/transcript.txt

# 从captions.srt同步
python scripts/sync_transcription_update.py path/to/captions.srt
```

### scripts/generate_missing_srt_files.py — 批量生成缺失 SRT

从已有的 `word_timings.json` 批量生成缺失的 SRT 文件（F-001）。

**典型用法示例**：

```bash
# 批量扫描并生成所有缺失的SRT文件
python scripts/generate_missing_srt_files.py
```

### retime_srt.py — SRT 时间戳整体偏移（根目录独立工具）

独立命令行工具，将 SRT 文件中所有字幕时间戳向前回退指定秒数。

**位置参数**（F-049）：

| 参数名 | 类型 | 说明 | 事实依据 |
|--------|------|------|----------|
| `input_file` | 路径 | 输入 SRT 文件路径 | F-049 |
| `output_file` | 路径 | 输出 SRT 文件路径 | F-049 |
| `seconds` | 浮点数 | 时间偏移秒数（正数表示向前回退） | F-049 |

**约束**（F-048）：禁止产生负时间戳，时间戳小于偏移量时自动钳位到 0。

**典型用法示例**：

```bash
# 将SRT整体向前回退2.5秒
python retime_srt.py input.srt output.srt 2.5
```

---

## 四、上传与批量处理脚本

### scripts/upload_all_new_languages.py — 批量上传所有新语言字幕

遍历所有视频，上传新增语言的字幕，自动处理 YouTube API 配额限制。

**核心机制**（F-069）：
- 遍历所有视频 URL
- 上传新语言字幕
- 遇到配额超时时，自动休眠 12 小时后重试（将当前 URL 放回队列尾部）

**典型用法示例**：

```bash
# 批量上传所有新语言字幕
python scripts/upload_all_new_languages.py
```

### scripts/sync_captions.py — 单视频单语言字幕同步上传

单个视频单个语言的字幕同步与上传工具（F-001）。

**典型用法示例**：

```bash
# 同步并上传指定视频的指定语言字幕
python scripts/sync_captions.py VIDEO_ID LANGUAGE_CODE
```

### scripts/copy_transcriptions_to_audio_tracks.py — 转录文件复制到音频目录

将转录生成的文件复制到音频轨道目录（F-001）。

**典型用法示例**：

```bash
# 复制转录文件到音频目录
python scripts/copy_transcriptions_to_audio_tracks.py
```

---

## 五、辅助工具

### track_contributors.py — 贡献者追踪（根目录独立工具）

通过 git log 提取字幕贡献者名单。

**核心功能**（F-070）：
- 通过 `git -C {LOCAL_REPO} log {folder}` 提取提交者（Author 行）
- 提取网页编辑者（Edit ... by 行）
- 自动排除 "Grant Sanderson" 本人

**数据文件**（F-001）：`data/manually-added-contributors.csv` 存储手动补充的贡献者名单。

**典型用法示例**：

```bash
# 提取指定目录的贡献者名单
python track_contributors.py path/to/caption/folder
```

---

## 相关概念

- [00 caption-ops 工具集总览](../concepts/00-caption-ops-overview.md)
- [01 音频转录：faster-whisper本地/API双模式](../concepts/01-transcription.md)
- [02 多语言翻译：DeepL/Google/GPT多后端](../concepts/02-translation.md)
- [03 SRT操作：时间轴与智能分段](../concepts/03-srt-operations.md)
- [04 完整管线：从视频到多语言字幕](../concepts/04-pipeline-workflow.md)
