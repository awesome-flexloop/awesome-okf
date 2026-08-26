---
type: Example
title: 端到端字幕生成完整流程
description: 演示如何为一个视频生成英文字幕并翻译为中文/其他语言字幕，涵盖从音频下载、本地转录、人工审核、翻译、SRT生成到时间轴调整的完整流程，诚实标注哪些步骤需要API密钥，给出纯本地faster-whisper方案。
tags: [caption-ops, workflow, end-to-end, transcription, translation, srt, faster-whisper, whisper, youtube, 3blue1brown]
generated:
  at: 2026-08-26
  by: source-code-to-okf-wiki skill
verified:
  at: 2026-08-26
  by: grep-api-verification
status: stable
stale_after: 2027-08-26
sources:
  - /spec/facts.md
  - /spec/insights.md
  - /references/dependencies.md
  - /references/scripts-reference.md
---

# 端到端字幕生成完整流程

> 本示例演示如何使用 caption-ops 工具集为一个 YouTube 视频从零开始生成英文字幕，并翻译为中文（及其他语言）字幕。教程明确标注每个步骤是否需要 API 密钥，同时提供纯本地 faster-whisper 离线方案，无需任何云端服务也能完成核心字幕生成工作流。

## 概述

caption-ops 的字幕生成不是一步完成的，而是一个**多阶段管线**（I-01），每一步都产生可检查、可人工修改的中间文件：

```
原始音频
  ↓ 步骤1：下载/准备音频
音频文件 (.mp3/.wav)
  ↓ 步骤2：转录（本地 faster-whisper 或 OpenAI API）
word_timings.json（词级时间戳）
  ↓ 步骤3：人工审核修正
transcript.txt（修正后的纯文本）
  ↓ 步骤4：重新对齐时间轴（模糊匹配自动完成）
sentence_timings.json（句级时间戳）
  ↓ 步骤5：翻译（DeepL/Google/GPT，需要API密钥）
sentence_translations.json（各语言翻译JSON）
  ↓ 步骤6：生成SRT文件
各语言 .srt 字幕文件
  ↓ 步骤7：时间轴调整与质量检查
最终可上传的SRT字幕
```

---

## 前置准备

### 安装依赖

按照 [/references/dependencies.md](/references/dependencies.md) 安装所需 Python 包。

**最小本地安装（无需任何API密钥，可完成转录+SRT生成）：**

```bash
pip install faster-whisper pysrt Levenshtein pytube youtube-transcript-api pycountry regex numpy tqdm pandas
```

**完整安装（包含翻译和上传功能）：**

如需翻译到其他语言或上传到 YouTube，还需配置以下 API 密钥（详见 [/references/dependencies.md](/references/dependencies.md)）：

| API 服务 | 环境变量 | 是否必须 |
|----------|----------|:---:|
| OpenAI API | `OPENAI_KEY` | 可选（Whisper API转录+GPT翻译用） |
| DeepL API | `DEEPL_KEY_FILE` | 可选（高质量翻译用） |
| Google Cloud Translation | `GOOGLE_TRANSLATION_SERVICE_ACCOUNT` | 可选（翻译回退用） |
| YouTube Data API | `YOUTUBE_UPLOADING_KEY` + `YOUTUBE_CREDENTIALS_FILE` | 可选（上传字幕到YouTube用） |

> ⚠️ **路径配置注意**：`helpers.py` 中硬编码了字幕根目录 `CAPTIONS_DIRECTORY` 和音频目录 `AUDIO_DIRECTORY`（F-003、F-004），使用前需根据你的实际环境修改这两个常量。

---

## 步骤1：下载视频音频

你有两种方式获取音频：使用 caption-ops 内置的下载脚本，或手动准备音频文件。

### 方式A：使用 download.py 从YouTube下载（无需API密钥）

`download.py` 使用 pytube 从 YouTube 下载最高码率纯音频流（F-056），无需任何 API 密钥：

```bash
# 在Python中调用下载功能
python -c "
from download import download_youtube_audio
download_youtube_audio('https://www.youtube.com/watch?v=VIDEO_ID', 'path/to/audio.mp4')
"
```

下载的文件是 `.mp4` 格式（纯音频流），faster-whisper 可以直接处理。

### 方式B：手动准备音频文件

如果你已经有音频文件（.mp3/.wav/.m4a等格式均可），可以跳过下载步骤，直接将音频文件放到你指定的目录即可。

> 💡 **提示**：3Blue1Brown 的工作流中，优先寻找 `only_narration.mp3/wav`（纯人声旁白），其次才是 `original_audio.mp3/wav`（含背景音乐的原始音频）（F-064）。如果你能分离出纯人声，转录准确率会更高。

---

## 步骤2：本地转录（纯本地方案，无需API密钥）

使用 `scripts/transcribe.py` 对单个音频文件进行转录（F-066），该脚本默认使用 faster-whisper 本地模型，完全离线运行，不需要 OpenAI API 密钥。

```bash
python scripts/transcribe.py path/to/your/audio.mp3
```

### 转录过程说明

首次运行时，faster-whisper 会自动下载 `medium.en` 模型（约 1.5GB），后续运行使用本地缓存。默认配置为（F-022）：
- 模型：`medium.en`（英文中等模型）
- 设备：`cpu`
- 计算精度：`int8`（CPU量化加速）

转录过程中会显示 tqdm 进度条（F-024），按音频秒数更新进度。

### 转录生成的文件

转录完成后会在**音频文件所在目录**生成三个文件（F-066）：

| 文件名 | 说明 |
|--------|------|
| `word_timings.json` | 词级时间戳，格式为 `[[word, start, end], ...]` |
| `transcription_sentences.srt` | 句子级 SRT 字幕（经过自然句子边界对齐） |
| `captions.srt` | 分段 SRT（`max_chars_per_segment=50`，适合屏幕显示） |

> 🔍 **为什么不直接用 Whisper 原生分段？** Whisper 输出的 segments 分段并不对应自然句子边界，经常把两句话切在一起或把一句话拆成多段（I-03）。caption-ops 先获取全量词级时间戳，再按标点正则重新分句、通过 Levenshtein 模糊匹配对齐时间轴，得到更符合人类阅读习惯的字幕分段。

### 备选：使用 OpenAI API 转录（需要API密钥）

如果你配置了 `OPENAI_KEY`，可以使用 Whisper API 获得更高质量的转录结果：

```python
from transcribe_video import transcribe_file_api, save_word_timings, words_with_timings_to_srt
import json

# API转录
result = transcribe_file_api("path/to/audio.mp3", word_timestamps=True)
save_word_timings(result, "path/to/word_timings.json")
words_with_timings_to_srt(json.load(open("path/to/word_timings.json")), "path/to/captions.srt")
```

自动回退机制：如果配置了API密钥但API调用失败，`transcribe_file_with_fallback()` 会自动回退到本地faster-whisper模型（F-026）。

---

## 步骤3：审核转录结果（人工修正）

自动转录不可能100%准确，特别是专业术语、数学符号、人名等。caption-ops 的多阶段中间产物设计让人工修正变得非常简单——你不需要重新转录，只需编辑纯文本文件即可。

### 推荐审核流程

1. **打开生成的 `transcript.txt`**（如果使用 `auto_caption.py` 会自动生成，也可以从 SRT 中提取纯文本）
2. **逐句检查修正**：修改识别错误的单词、标点、大小写
3. **保存修改后的文件**

### 修正后重新对齐时间轴

修改完文本后，使用 `scripts/sync_transcription_update.py` 自动重新对齐所有时间轴（F-068）：

```bash
# 使用修改后的 transcript.txt 重新对齐
python scripts/sync_transcription_update.py path/to/transcript.txt

# 或者使用修改后的 captions.srt
python scripts/sync_transcription_update.py path/to/captions.srt
```

该脚本使用与转录时相同的 Levenshtein 模糊匹配算法（F-051），自动找到修改后文本在词级时间戳中的对应位置，更新 `sentence_timings.json` 和各语言翻译文件中的 `input` 字段，无需重新转录音频。

---

## 步骤4：翻译为目标语言（需要API密钥）

翻译功能需要配置至少一个翻译后端（DeepL/Google/GPT）。

### 翻译策略说明

caption-ops 的翻译策略是（F-038、I-02）：
1. DeepL 支持的语言（西班牙语、中文、法语、俄语、德语、意大利语、葡萄牙语、日语、韩语、乌克兰语、土耳其语、匈牙利语）**优先使用 DeepL**
2. DeepL 调用失败则**自动回退到 Google Translate**
3. DeepL 不支持的语言（印地语、阿拉伯语、泰语、波斯语、印尼语、希伯来语、越南语）**直接使用 Google Translate**
4. 另外提供 GPT-4o 上下文感知翻译作为高质量选项

### 批量翻译

使用 `scripts/auto_caption.py` 进行端到端处理（包含翻译）：

```bash
# 单个视频：英文转录 + 翻译到中文 + 不上传（仅生成本地文件）
python scripts/auto_caption.py https://www.youtube.com/watch?v=VIDEO_ID --languages Chinese --no-upload

# 翻译到所有19种支持语言
python scripts/auto_caption.py https://www.youtube.com/watch?v=VIDEO_ID --languages all --no-upload

# 翻译到西班牙语、法语、德语三种语言
python scripts/auto_caption.py https://www.youtube.com/watch?v=VIDEO_ID --languages Spanish,French,German --no-upload
```

翻译完成后会在各语言子目录（如 `Chinese/`、`Spanish/`）生成 `sentence_translations.json` 文件，包含原文和译文的对照。

### 使用 GPT-4o 高质量翻译（需要OPENAI_KEY）

GPT-4o 翻译的优势是具备上下文感知能力（F-040），翻译时会保留前后 `2*n_context_sentences` 条句子作为上下文，风格更统一：

```python
from gpt_translate import gpt4_translate

sentences = ["First sentence here.", "Second sentence here.", "..."]
translations = gpt4_translate(sentences, "Chinese", formality="informal", n_context_sentences=2)
```

---

## 步骤5：生成SRT文件

翻译完成后，从翻译 JSON 生成各语言的 SRT 字幕文件。

### 从词级时间戳生成英文SRT

转录完成后已经生成了基础 SRT，如果需要重新生成：

```python
import json
from transcribe_video import words_with_timings_to_srt

words = json.load(open("path/to/word_timings.json"))
words_with_timings_to_srt(words, "path/to/english_captions.srt")
```

该函数内部会（F-029）：
1. 拼接单词为全文
2. 按多语言标点正则分割为自然句子（F-005）
3. 调用模糊对齐算法获取句子时间范围（F-052）
4. 调用智能分段函数写SRT（F-047）

### 从翻译JSON生成多语言SRT

```python
from translate import sentence_translations_to_srt

# 从中文翻译JSON生成SRT
sentence_translations_to_srt("path/to/Chinese/sentence_translations.json")
```

生成的 SRT 文件名为 `auto_generated.srt`。智能分段规则（F-039、F-047）：
- 中日韩等字符型语言：每段最多 **30 字符**
- 其他语言：每段最多 **90 字符**
- 优先在标点处切割，其次在空格处切割，字符型语言直接硬切
- 切割点时间使用线性插值（F-009）
- 自动排序防止时间重叠

### 批量生成所有缺失SRT

```bash
python scripts/generate_missing_srt_files.py
```

该脚本会扫描所有 `word_timings.json` 文件，批量生成缺失的 SRT 文件。

---

## 步骤6：时间轴调整和质量检查

### 时间偏移调整

如果发现字幕整体比视频早/晚若干秒，可以使用 `retime_srt.py` 进行整体时间偏移（F-048、F-049）：

```bash
# 将SRT整体向前回退1.5秒（字幕出现得更早）
python retime_srt.py input.srt output.srt 1.5

# 将SRT整体向后延迟0.8秒（字幕出现得更晚）
python retime_srt.py input.srt output.srt -0.8
```

> 注意：该工具禁止产生负时间戳，时间戳小于偏移量时自动钳位到 0（F-048）。

### 质量检查清单

生成SRT后建议进行以下检查：

1. **时间轴连续性**：检查是否有字幕时间重叠或长时间无字幕的空隙
2. **单段长度**：确保单段字幕不会过长（影响阅读），中文一般不超过20字，英文不超过60字符
3. **标点一致性**：检查标点是否正确、是否有乱码
4. **术语统一**：专业术语翻译是否前后一致
5. **观影测试**：在视频播放器中加载SRT，实际观看检查字幕与语音同步情况

### 重新同步SRT

如果审核修改了超过50%的翻译内容，`sync_all_captions.py` 会自动将旧的社区字幕备份为 `community_old.srt`（F-067）：

```bash
python scripts/sync_all_captions.py path/to/sentence_translations.json
```

---

## 完整命令行示例

### 示例1：纯本地英文转录（无API密钥，完全离线）

```bash
# 1. 准备好音频文件（或用pytube下载）
# 2. 转录单个音频
python scripts/transcribe.py my_video_audio.mp3

# 3. 检查生成的文件：
#    - word_timings.json
#    - transcription_sentences.srt
#    - captions.srt
# 4. 手动编辑修正transcript.txt（需要从SRT提取文本）
# 5. 修正后重新对齐时间轴
# python scripts/sync_transcription_update.py path/to/transcript.txt
# 6. 如有需要调整时间轴
# python retime_srt.py captions.srt captions_fixed.srt 1.2
```

### 示例2：端到端含翻译（需要DeepL/Google API密钥，不上传YouTube）

```bash
# 1. 设置API密钥环境变量（见dependencies.md）
# 2. 一键处理：转录+翻译中文/西班牙语+生成本地文件
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --languages Chinese,Spanish \
  --no-upload
```

### 示例3：端到端含翻译和YouTube上传（需要完整API配置）

```bash
# 翻译到所有支持语言并自动上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" --languages all
```

---

## 不使用API的纯本地方案说明

如果你**完全没有任何API密钥**，也不想使用任何云端服务，可以完成以下工作：

| 功能 | 纯本地方案 | 说明 |
|------|-----------|------|
| 音频下载 | ✅ pytube下载YouTube音频 | 无需API（F-056） |
| 语音转录 | ✅ faster-whisper本地模型 | CPU int8量化，无需GPU（F-021~F-024） |
| 词级时间戳 | ✅ 本地生成 | faster-whisper支持word_timestamps（F-023） |
| 自然句子分割 | ✅ 本地正则分句 | 支持多语言标点（F-005、F-013） |
| 模糊对齐 | ✅ Levenshtein编辑距离 | 本地算法，无网络请求（F-012、F-051） |
| SRT生成 | ✅ pysrt本地读写 | 智能分段本地算法（F-046、F-047） |
| 时间轴调整 | ✅ retime_srt.py | 完全独立离线工具（F-048、F-049） |
| 机器翻译 | ❌ 需要API | 纯本地无翻译功能，可手动翻译或接入其他本地翻译模型 |
| YouTube上传 | ❌ 需要API | YouTube Data API必须OAuth认证 |

### 纯本地faster-whisper完整工作流代码

以下是一个不依赖caption-ops内部脚本的纯本地转录示例，你可以在任意Python环境中运行：

```python
from faster_whisper import WhisperModel
import json

# 1. 加载本地模型（首次运行自动下载约1.5GB）
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

# 2. 转录音频，启用词级时间戳
segments, info = model.transcribe(
    "audio.mp3",
    language="en",
    beam_size=1,
    word_timestamps=True,
)

# 3. 提取词级时间戳
words_with_timings = []
for segment in segments:
    for word in segment.words:
        words_with_timings.append([
            word.word.strip(),
            round(word.start, 2),
            round(word.end, 2),
        ])

# 4. 保存词级时间戳
with open("word_timings.json", "w", encoding="utf-8") as f:
    json.dump(words_with_timings, f, ensure_ascii=False)

print(f"转录完成，共 {len(words_with_timings)} 个词")
```

纯本地模式的局限：
- faster-whisper `medium.en` 模型在 CPU 上的转录速度约为实时的 1-2 倍（即10分钟音频需要5-10分钟处理）
- 英文转录质量较好，小语种需要下载对应语言的模型（如 `medium` 多语言模型）
- 没有自动机器翻译功能，需手动翻译或接入其他开源翻译模型

---

## 运行说明

### 环境要求

- Python 3.8+
- 足够的磁盘空间（faster-whisper 模型约 1.5GB）
- 纯本地转录不需要网络（首次下载模型除外）
- 翻译和上传功能需要相应的 API 密钥和网络连接

### 目录结构

处理完一个视频后，caption-ops 会创建如下目录结构（F-019）：

```
CAPTIONS_DIRECTORY/
└── 2024/
    └── Video Title First Three Long Words/
        ├── video_url.txt          # 原始YouTube URL
        ├── word_timings.json      # 词级时间戳
        ├── sentence_timings.json  # 句级时间戳
        ├── full_sentences.srt     # 完整句子SRT
        ├── captions.srt           # 分段SRT（英文）
        ├── transcript.txt         # 纯文本转录
        ├── Chinese/
        │   ├── sentence_translations.json
        │   └── auto_generated.srt
        ├── Spanish/
        │   ├── sentence_translations.json
        │   └── auto_generated.srt
        └── ...
```

shorts 视频会额外放入 `shorts/` 子目录。

---

## 预期输出

### 成功运行英文转录后

你将在输出目录看到：
1. `word_timings.json` — 词级时间戳 JSON 数组
2. `transcription_sentences.srt` — 句子对齐的 SRT 文件
3. `captions.srt` — 适合屏幕显示的分段 SRT 文件

### 成功运行翻译后

你将在各语言子目录看到：
1. `sentence_translations.json` — 包含原文和译文的 JSON 文件
2. `auto_generated.srt` — 该语言的 SRT 字幕文件

### 成功上传到YouTube后（需要YouTube API）

对应视频的 YouTube 字幕管理页面将出现新增的语言字幕，视频本地化标题和描述也会同步更新。

---

## 相关概念

- [00 caption-ops 工具集总览](/concepts/00-caption-ops-overview.md) — 工具集定位、设计哲学、目录结构
- [01 音频转录：faster-whisper本地/API双模式](/concepts/01-transcription.md) — 转录引擎原理、词级时间戳、自动回退机制
- [02 多语言翻译：DeepL/Google/GPT多后端](/concepts/02-translation.md) — 翻译策略、GPT上下文翻译、目标语言列表
- [03 SRT操作：时间轴与智能分段](/concepts/03-srt-operations.md) — SRT格式、智能分段算法、模糊对齐原理、时间偏移工具
- [04 完整管线：从视频到多语言字幕](/concepts/04-pipeline-workflow.md) — CLI脚本详解、中间产物作用、批量处理、人工审核流程
- [依赖安装与 API 配置说明](/references/dependencies.md) — 完整依赖清单、环境变量配置
- [Caption Ops CLI 脚本参数速查表](/references/scripts-reference.md) — 所有命令行脚本参数说明
