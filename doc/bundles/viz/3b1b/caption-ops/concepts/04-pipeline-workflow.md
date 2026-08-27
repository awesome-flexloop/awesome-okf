---
type: Concept
title: 端到端字幕工作流
description: caption-ops 的端到端工作流串联了音频下载、转录、翻译、SRT生成、YouTube上传等所有环节，通过中间产物文件实现可中断、可审核、可修改的非破坏性管线，支持单视频一键处理和批量多视频处理，提供人工修正后的自动同步机制。
tags: [caption-ops, workflow, pipeline, end-to-end, youtube, automation, batch-processing, contributor-tracking]
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

# 端到端字幕工作流

前面三个模块（转录、翻译、SRT操作）分别解决了字幕生成中的单个问题，而端到端工作流（End-to-End Pipeline）则是将这些模块串联起来的完整生产流程。caption-ops 最有价值的设计不是某个算法有多精妙，而是它构建了一条**可中断、可审核、可修改的非破坏性管线**——每一步都产生可人工检查的中间文件，你可以在任何环节停下来修正，然后从断点继续，不需要从头重来。

本模块覆盖事实 F-055~F-070，包括：
- `download.py`：YouTube 音频与现有字幕下载（F-055~F-057）
- `upload.py`：YouTube Data API 字幕上传与视频本地化更新（F-058~F-062）
- `scripts/auto_caption.py`：一键端到端自动字幕脚本（F-063~F-065）
- `scripts/*.py`：批量处理、同步、转录更新等工具脚本（F-066~F-069）
- `track_contributors.py`：字幕贡献者追踪（F-070）

## 完整字幕生成管线串联

回顾洞察 I-01：字幕生成不是"语音转文字"一步完成的，而是至少五个阶段的管线处理，每一步都有可检查、可人工修改的中间产物。端到端工作流正是将这些阶段串联起来的执行流程。

### 管线全景图

```
┌─────────────┐
│  输入源     │ YouTube URL / 本地音频文件
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段 1：音频下载（download.py）                             │
│  - YouTube 最高码率纯音频流（pytube）                        │
│  - 或使用本地已有音频文件（only_narration.mp3 优先）         │
│  输出：音频文件到 AUDIO_DIRECTORY                            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段 2：词级转录（transcribe_video.py）                     │
│  - OpenAI API 优先，失败回退本地 faster-whisper              │
│  输出：word_timings.json（词级时间戳）                       │
│       └─► 这是所有后续处理的基础，人工修正从这里下游开始      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段 3：句子对齐 + 智能分段（sentence_timings + srt_ops）   │
│  - Levenshtein 模糊匹配：词级时间 → 句级时间                 │
│  - 标点优先智能分段，线性插值时间                            │
│  输出：sentence_timings.json（句级时间）                     │
│       full_sentences.srt（完整句子SRT）                      │
│       captions.srt（分段英文字幕）                           │
│       transcript.txt（纯文本，【人工修正入口】）              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段 4：多语言翻译（translate.py + gpt_translate.py）       │
│  - DeepL 优先 → Google 回退 → GPT-4o 可选                   │
│  - 19 种目标语言，批量翻译，断点续传                         │
│  输出：{language}/sentence_translations.json（翻译结果）    │
│       {language}/auto_generated.srt（翻译SRT）              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段 5：YouTube 上传（upload.py）                           │
│  - OAuth2 认证，字幕上传，支持替换旧版本                     │
│  - 同时更新视频本地化标题和描述                              │
│  输出：YouTube 字幕发布                                      │
└─────────────────────────────────────────────────────────────┘
```

（洞察 I-01、F-063、F-064）

### 中间产物与人工干预点

中间产物的存在不是"冗余"，而是允许人工介入审核修改的关键设计。以下是每个中间文件的用途和是否建议人工编辑：

| 文件 | 阶段 | 格式 | 用途 | 人工干预建议 |
|------|------|------|------|-------------|
| 音频文件（.mp3/.wav） | 1 | 二进制 | 转录输入 | 如有干净旁白版优先用 `only_narration.mp3` |
| `word_timings.json` | 2 | JSON | 词级原始时间数据 | 一般不直接编辑，这是时间基准 |
| `sentence_timings.json` | 3 | JSON | 句级时间范围 | 一般不直接编辑 |
| `transcript.txt` | 3 | 纯文本 | 完整英文转录文本 | **✅ 主要人工修正入口**，直接编辑修正转录错误 |
| `full_sentences.srt` | 3 | SRT | 完整句子 SRT | 可以检查句子分割是否合理 |
| `captions.srt` | 3 | SRT | 英文分段字幕 | ✅ 可以直接编辑后上传 |
| `sentence_translations.json` | 4 | JSON | 翻译结果 | ✅ 可以编辑修正翻译错误，`n_reviews` 计数审核次数 |
| `auto_generated.srt` | 4 | SRT | 翻译后 SRT | ✅ 人工审核后重命名再上传 |
| `title.json` / `description.json` | 4 | JSON | 本地化标题/描述 | ✅ 可以编辑后上传更新视频元数据 |

（F-063）

**最重要的人工干预点是 `transcript.txt`**：自动转录（尤其是数学专有名词）不可能 100% 正确，你应该在转录完成后打开这个文件，用文本编辑器修正所有识别错误，然后运行同步脚本自动更新所有语言的时间轴和翻译，不需要重新转录或重新翻译（F-068）。这是 caption-ops 相比其他一键工具的最大优势。

## 从 YouTube 下载音频：download.py

`download.py` 模块负责从 YouTube 获取音频和现有字幕（F-055~F-057）。

### YouTube 音频下载

`download_youtube_audio(url, file_path)` 使用 `pytube` 库下载 YouTube 视频的最高码率纯音频流（F-056）：

```python
from pytube import YouTube

def download_youtube_audio(url, file_path):
    yt = YouTube(url)
    # 选择纯音频流，按 abr（平均码率）降序，取最高码率
    audio_stream = yt.streams.filter(
        only_audio=True,
        file_extension="mp4"
    ).order_by("abr").desc().first()
    audio_stream.download(filename=file_path)
```

下载的是 WebM/MP4 格式的纯音频，faster-whisper 和 OpenAI API 都支持直接处理这种格式。

### 现有社区字幕下载

`download_captions(video_id, directory, suffix="community")` 使用 `youtube_transcript_api` 库获取 YouTube 上已有的非英语社区字幕，保存为 `{language}_{suffix}.srt` 格式（F-057）：

```python
from youtube_transcript_api import YouTubeTranscriptApi

def download_captions(video_id, directory, suffix="community"):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    for transcript in transcript_list:
        if transcript.language_code != "en":  # 跳过英语
            srt_data = transcript.fetch().to_srt()
            lang = transcript.language_code
            with open(f"{directory}/{lang}_{suffix}.srt", "w", encoding="utf-8") as f:
                f.write(srt_data)
```

这个功能的作用是：如果社区志愿者已经上传了某语言的字幕，你可以下载下来作为参考，或者在其基础上改进，而不是从零开始自动翻译。

### 本地音频文件优先级

端到端脚本在查找音频文件时遵循以下优先级（F-064）：
1. `only_narration.mp3` / `only_narration.wav`：只包含人声旁白、去除背景音的干净音频（转录质量最高）
2. `original_audio.mp3` / `original_audio.wav`：原始音频轨
3. 从 YouTube 下载音频流

如果你有视频工程文件，导出干净的旁白音轨能显著提升转录准确率。

## 转录与生成英文字幕产物

`write_whisper_transcription_files()` 函数负责从音频生成全套英文字幕产物（F-063）：

```python
def write_whisper_transcription_files(audio_file, directory, ...):
    # 1. 转录音频（API 优先，本地兜底）
    transcription = transcribe_file_with_fallback(audio_file)
    
    # 2. 保存词级时间戳
    save_word_timings(transcription, f"{directory}/word_timings.json")
    
    # 3. 词级→句级时间对齐
    words = get_words_with_timings(transcription)
    sentences, time_ranges = get_sentences_with_timings(words)
    
    # 4. 保存句级时间
    json_dump({
        "sentences": sentences,
        "time_ranges": time_ranges
    }, f"{directory}/sentence_timings.json")
    
    # 5. 生成完整句子 SRT
    write_srt_from_sentences_and_time_ranges(
        sentences, time_ranges,
        f"{directory}/full_sentences.srt",
        max_chars_per_segment=10**9  # 超大值 = 不限制，一句一段
    )
    
    # 6. 生成智能分段 SRT
    write_srt_from_sentences_and_time_ranges(
        sentences, time_ranges,
        f"{directory}/captions.srt",
        max_chars_per_segment=90
    )
    
    # 7. 保存纯文本 transcript（人工修正入口）
    with open(f"{directory}/transcript.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(sentences))
```

这一套文件生成完成后，你应该先打开 `transcript.txt` 检查和修正转录错误，然后再继续翻译步骤。

## auto_caption.py：端到端一键脚本

`scripts/auto_caption.py` 是一键完成从音频到上传全流程的脚本，也是最常用的入口（F-064、F-065）。

### 核心函数 auto_caption()

```python
def auto_caption(video_url, upload=True, languages=None):
    # 1. 定位/创建视频字幕目录
    directory = url_to_directory(video_url)  # F-020
    
    # 2. 查找本地音频文件（only_narration 优先）
    audio_file = find_local_audio(directory)
    if audio_file is None:
        # 本地没有则从 YouTube 下载
        audio_file = f"{directory}/original_audio.mp4"
        download_youtube_audio(video_url, audio_file)
    
    # 3. 如果还没有英文字幕产物，生成之
    if not os.path.exists(f"{directory}/word_timings.json"):
        write_whisper_transcription_files(audio_file, directory)
    
    # 4. 翻译到指定语言（跳过已翻译的，断点续传）
    if languages is None:
        languages = []  # 默认不翻译
    for lang in languages:
        lang_dir = ensure_exists(f"{directory}/{lang}")
        trans_file = f"{lang_dir}/sentence_translations.json"
        if not os.path.exists(trans_file):
            # 读取英文句子
            with open(f"{directory}/sentence_timings.json") as f:
                data = json.load(f)
            sentences = data["sentences"]
            # 翻译
            translations = translate_sentences(sentences, lang)
            json_dump(translations, trans_file)
            # 生成 SRT
            sentence_translations_to_srt(trans_file)
    
    # 5. 上传到 YouTube
    if upload:
        youtube_api = get_youtube_api()
        video_id = extract_video_id(video_url)
        # 上传英文字幕
        upload_caption(youtube_api, video_id, f"{directory}/captions.srt",
                      language_code="en", replace=True)
        # 上传各语言字幕
        for lang in languages:
            lang_code = get_language_code(lang)
            srt_file = f"{directory}/{lang}/auto_generated.srt"
            if os.path.exists(srt_file):
                upload_caption(youtube_api, video_id, srt_file,
                              language_code=lang_code, replace=True)
        # 更新视频本地化标题/描述
        upload_video_localizations(youtube_api, directory, video_id, languages)
```

（F-064）

设计特点：
- **断点续传**：每一步都检查文件是否存在，已完成的步骤跳过，中断后重新运行不会重复工作
- **非破坏性**：不删除任何已有文件，翻译过的内容不会被覆盖
- **本地音频优先**：有本地音频就不下载，节省带宽和时间

### 命令行参数

CLI 入口使用 argparse 解析参数（F-065）：

```bash
# 基本用法：给一个 YouTube 视频生成字幕（默认只生成英文，不上传）
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 生成多语言字幕并上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --languages chinese,japanese,korean \
    --upload  # 注意：原代码是默认upload=True，有--no-upload参数

# 生成所有支持语言的字幕但不上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --languages all \
    --no-upload

# 批量处理：从 txt 文件读取 URL 列表，每行一个 URL
python scripts/auto_caption.py video_list.txt --languages all --upload
```

参数说明：
- `video`：位置参数，可以是单个 YouTube URL，也可以是包含 URL 列表的 `.txt` 文件路径
- `--languages`：逗号分隔的语言名称列表，`all` 表示所有 19 种目标语言
- `--no-upload`：禁用上传，只生成本地文件

> ⚠️ **API 密钥提示**：完整端到端流程需要配置以下环境变量：
> - `OPENAI_KEY`：OpenAI API 密钥（转录 + GPT 翻译）
> - `DEEPL_KEY_FILE`：DeepL API 密钥文件路径（翻译）
> - `GOOGLE_TRANSLATION_SERVICE_ACCOUNT`：Google 服务账号 JSON（翻译回退）
> - `YOUTUBE_UPLOADING_KEY`：YouTube OAuth 客户端密钥（上传）
>
> 只生成本地文件不上传可以不需要 `YOUTUBE_UPLOADING_KEY`；纯本地转录可以不需要任何 API 密钥（用 faster-whisper）。

## 上传到 YouTube：upload.py

`upload.py` 模块通过 YouTube Data API v3 实现字幕上传和视频本地化更新，这是管线中唯一需要 OAuth 认证的环节（F-058~F-062）。

### OAuth2 认证流程

`get_youtube_api()` 函数实现了完整的 OAuth2 认证流程，带 LRU 缓存（F-060）：

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtubepartner"]

@lru_cache()
def get_youtube_api():
    # 1. 尝试从凭证文件加载已保存的 token
    creds = None
    token_file = os.environ["YOUTUBE_CREDENTIALS_FILE"]
    client_secret = os.environ["YOUTUBE_UPLOADING_KEY"]
    
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    
    # 2. 如果凭证过期，刷新
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    # 3. 如果没有有效凭证，启动 OAuth 流程
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret, SCOPES
        )
        # 启动本地服务器接收回调
        creds = flow.run_local_server(port=0)
        
        # 4. 保存凭证供下次使用
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    
    # 5. 返回 API 客户端
    return build("youtube", "v3", credentials=creds)
```

认证流程说明：
1. 首次运行时会打开浏览器，让你登录 Google 账号并授权
2. 授权成功后凭证保存在 `YOUTUBE_CREDENTIALS_FILE` 指定的文件中
3. 后续运行会自动加载凭证，过期则自动刷新，不需要重复授权
4. 需要你在 Google Cloud Console 创建项目并启用 YouTube Data API v3，获取客户端密钥文件（F-059）

### 字幕上传

`upload_caption()` 函数上传 SRT 文件到指定视频（F-061）：

```python
def upload_caption(youtube_api, video_id, caption_file, 
                   name="", replace=False, language_code=None):
    # 如果需要替换，先删除现有字幕
    if replace:
        try:
            captions = youtube_api.captions().list(
                part="id",
                videoId=video_id
            ).execute()
            for cap in captions.get("items", []):
                if cap["snippet"]["language"] == language_code:
                    youtube_api.captions().delete(id=cap["id"]).execute()
        except:
            pass
    
    # 上传新字幕
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(caption_file, mimetype="text/plain")
    
    request = youtube_api.captions().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "language": language_code,
                "name": name,
                "isDraft": False
            }
        },
        media_body=media
    )
    response = request.execute()
    return response
```

### 视频本地化更新

`upload_video_localizations()` 从各语言目录的 `title.json` 和 `description.json` 读取翻译后的标题和描述，调用 YouTube API 更新视频的本地化元数据（F-062）。这样其他语言的用户在 YouTube 上看到的视频标题和描述就是他们自己的语言。

## 中间产物审核与人工修正工作流

自动生成的字幕不可能完美，caption-ops 专门设计了支持人工修正后重新同步的脚本。这是生产环境中最常用的工作流。

### 场景：人工修正转录错误后同步

1. **自动转录**：运行 `auto_caption.py` 生成全套英文产物
2. **人工修正**：打开 `transcript.txt`，修正转录错误（尤其是数学专有名词）
3. **同步更新**：运行 `scripts/sync_transcription_update.py`，自动：
   - 重新按标点分句
   - 更新 `sentence_timings.json` 时间轴（通过模糊匹配定位修改后的句子位置）
   - 更新各语言 `sentence_translations.json` 中的 `input` 字段（原英文句子）
   - 标记需要重新翻译的句子（F-068）
4. **重新翻译/审核**：模糊匹配算法能匹配上的句子复用原有翻译，匹配不上的标记为需要重新翻译
5. **重新生成 SRT 并上传**（F-068）

这个流程的核心价值是：你不需要重新转录音频（节省时间和 API 费用），也不需要重新翻译所有内容（未修改的句子翻译保持不变）。模糊匹配算法容忍文本的微小修改，这是洞察 I-03 在生产工作流中的实际应用。

### 场景：翻译质量人工审核

1. 打开 `{language}/sentence_translations.json`
2. 检查每条 `translatedText` 是否准确，修正错误
3. 将修正后的条目的 `n_reviews` 计数 +1
4. 运行 `scripts/sync_all_captions.py` 重新生成 SRT
5. 当某语言 `n_reviews > 0` 的比例超过 50% 时，脚本会自动将旧的社区字幕重命名为 `community_old.srt` 备份，表示人工审核版本已大幅改进自动版本（F-067）
6. 上传审核后的字幕

## 批量处理多视频

caption-ops 提供了多个批量处理脚本，用于管理整个频道的字幕工作。

### 批量上传所有新语言：upload_all_new_languages.py

`scripts/upload_all_new_languages.py` 实现了带配额管理的批量上传循环（F-069）：

```python
def upload_all_new_languages(video_urls):
    queue = list(video_urls)
    while queue:
        url = queue.pop(0)
        try:
            # 上传该视频的所有新语言字幕
            upload_new_captions_for_video(url)
        except HttpError as e:
            if "quota" in str(e).lower():
                # 配额超时时，将当前 URL 放回队列尾部，休眠 12 小时
                print("Quota exceeded, sleeping 12 hours...")
                queue.append(url)
                time.sleep(12 * 3600)
            else:
                raise  # 其他错误直接抛出
```

这个脚本的处理方式非常直接（甚至有点"粗暴"）：遇到 YouTube API 配额超限，直接 `sleep(12*3600)` 休眠 12 小时，然后把当前视频放回队列尾部重试。没有复杂的任务队列、没有调度系统——这是典型的个人工作流工具设计：简单、够用、不需要额外依赖（洞察 I-04）。

### 批量生成缺失 SRT：generate_missing_srt_files.py

遍历所有视频目录，从已有的 `sentence_translations.json` 生成缺失的 `auto_generated.srt` 文件（F-023）。

### 批量同步转录更新：sync_transcription_update.py

接受修改后的 `transcript.txt` 或 `captions.srt`，同步更新对应视频所有语言的翻译文件（F-068）。

### 全量字幕同步：sync_all_captions.py

从翻译 JSON 重新生成所有 SRT 文件，处理备份逻辑（F-067）。

## track_contributors.py：贡献者追踪

`track_contributors.py` 用于从 git log 中提取字幕贡献者名单，给社区志愿者署名（F-070）。

### 从 git log 提取贡献者

`get_contributor_names(folder)` 函数解析指定目录的 git 提交历史：

```python
import subprocess
import re

def get_contributor_names(folder):
    # 获取该目录的所有 git log
    result = subprocess.run(
        ["git", "-C", LOCAL_REPO, "log", folder],
        capture_output=True,
        text=True
    )
    log = result.stdout
    
    contributors = set()
    
    # 提取 Author: 行（git 提交者）
    for match in re.finditer(r"^Author:\s*(.+?)\s*<", log, re.MULTILINE):
        name = match.group(1).strip()
        if name != "Grant Sanderson":  # 排除作者本人
            contributors.add(name)
    
    # 提取 "Edit ... by" 行（YouTube 网页编辑者，从提交信息中提取）
    for match in re.finditer(r"Edit.*?by\s*(.+)", log):
        name = match.group(1).strip()
        contributors.add(name)
    
    return sorted(contributors)
```

除了自动从 git log 提取外，`data/manually-added-contributors.csv` 文件可以手动补充无法通过 git log 追踪的贡献者（F-070）。

这个功能体现了 caption-ops 对社区贡献者的尊重——字幕是社区协作的成果，每个贡献者都应该被署名。

## 典型使用场景

### 场景一：新视频首发多语言字幕

```bash
# 1. 视频发布后，一键生成所有语言字幕并上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=NEW_VIDEO_ID" \
    --languages all \
    --upload

# 2. 等待自动转录和翻译完成（可能需要几十分钟到几小时，取决于语言数量）

# 3. 人工修正英文 transcript.txt
vim /path/to/captions/NEW_VIDEO/transcript.txt

# 4. 同步更新翻译和时间轴
python scripts/sync_transcription_update.py /path/to/captions/NEW_VIDEO/transcript.txt

# 5. 审核各语言翻译，修正错误后上传最终版本
```

### 场景二：老视频补充多语言字幕

```bash
# 1. 批量处理一个 URL 列表文件
# 先创建 video_urls.txt，每行一个老视频 URL

# 2. 批量生成所有语言字幕（不上传，先审核）
python scripts/auto_caption.py video_urls.txt --languages all --no-upload

# 3. 审核后批量上传
python scripts/upload_all_new_languages.py
```

### 场景三：本地音频文件生成字幕（纯离线，无 API 密钥）

```bash
# 使用本地 faster-whisper 转录单个音频，生成英文字幕
python scripts/transcribe.py /path/to/your/audio.mp3

# 输出：word_timings.json、transcription_sentences.srt、captions.srt
```

（F-066）

## 常见问题排查

### 1. pytube 下载失败

pytube 经常因为 YouTube 接口变化而失效，这是 youtube-dl 类工具的通病。解决方案：
- 升级 pytube 到最新版本：`pip install --upgrade pytube`
- 如果还是不行，手动用其他工具（如 yt-dlp）下载音频，放到对应目录命名为 `original_audio.mp4`，脚本会优先使用本地文件跳过下载

### 2. 翻译 API 配额用完

- DeepL/Google 翻译有月度免费额度，超额会报错
- 脚本没有复杂的配额管理，批量翻译大量视频时建议分批次运行
- 可以只翻译几个主要语言，而不是 `--languages all`

### 3. YouTube 上传配额超限

YouTube Data API 每日有配额限制（默认约 100 次请求/天），字幕上传是配额消耗大户。
- `upload_all_new_languages.py` 遇到配额超时时会自动休眠 12 小时重试（F-069）
- 建议分批次上传，不要一次上传太多视频
- 可以先用 `--no-upload` 生成所有文件，再分批上传

### 4. OAuth 认证失败

- 确认 `YOUTUBE_UPLOADING_KEY` 指向的客户端密钥文件是正确的
- 第一次认证需要浏览器弹出授权窗口，确保你的运行环境可以访问浏览器
- 如果凭证损坏，删除 `YOUTUBE_CREDENTIALS_FILE` 文件，重新运行触发授权流程
- 确认你的 Google 账号有该 YouTube 频道的编辑权限

### 5. 句子对齐不准（时间轴错位）

模糊对齐算法虽然鲁棒，但在以下情况可能不准：
- 人工修正 transcript.txt 时做了大幅改写（不只是修正错别字）
- 转录文本缺失了大段内容
- 解决方案：尽量保持修正后的文本与原始转录内容接近，只修正错误的单词；如果改动很大，建议重新运行 `write_whisper_transcription_files()` 从头生成。

### 6. 翻译质量差

- DeepL 质量通常最好，确认你的 DeepL 密钥配置正确
- 对于 DeepL 不支持的语言（如乌克兰语、泰语），只能用 Google 翻译，质量可能略差，建议人工审核
- 数学术语是重灾区，建议首次处理新语言时建立术语表，用 GPT-4o 翻译能改善一致性

## 相关概念

- [00 caption-ops 工具集总览](00-caption-ops-overview.md)
- [01 音频转录模块](01-transcription.md)
- [02 多语言翻译模块](02-translation.md)
- [03 SRT字幕操作](03-srt-operations.md)
- [CLI 脚本参考](../references/scripts-reference.md)
- [依赖与 API 配置](../references/dependencies.md)
