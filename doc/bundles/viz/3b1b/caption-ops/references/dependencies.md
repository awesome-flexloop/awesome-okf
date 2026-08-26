---
type: Reference
title: 依赖安装与 API 配置说明
description: caption-ops 字幕工具集的完整依赖清单、Python包安装、API密钥配置、环境变量设置说明。
tags: [caption-ops, dependencies, installation, api-keys, configuration, reference]
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
    resource: /references/dependencies.md
    title: 依赖安装与 API 配置说明
---

# 依赖安装与 API 配置说明

本文档基于 caption-ops 源码事实采集（F-007、F-021、F-031、F-042、F-050、F-055、F-058、F-071、F-072），完整列出工具集所需的 Python 依赖包、外部 API 服务、环境变量配置方式，以及本地可用功能与需要 API 密钥功能的区分。

## 依赖总览

caption-ops 采用「本地优先 + 云端回退」的混合依赖策略（I-02）：核心转录和 SRT 处理功能完全可以在本地离线运行，翻译和 YouTube 上传功能需要相应的 API 密钥。

| 类别 | 数量 | 是否需要 API 密钥 |
|------|------|:---:|
| 本地可运行 Python 包 | 10个 | ❌ 不需要 |
| 外部 API 服务 | 4类 | ✅ 需要 |

---

## 一、本地可运行依赖（无需 API 密钥）

以下 Python 包安装后即可在本地离线使用，无需任何 API 密钥或网络连接（F-071）。

| 包名 | 用途 | 使用模块 | 事实依据 |
|------|------|----------|----------|
| `faster-whisper` | 本地语音转录引擎（基于 CTranslate2 的快速 Whisper 实现） | `transcribe_video.py` | F-021、F-071 |
| `pysrt` | SRT 字幕文件读写库 | `srt_ops.py`、`sentence_timings.py` | F-042、F-050、F-071 |
| `Levenshtein` | 编辑距离计算，用于模糊字符串匹配 | `helpers.py`、`sentence_timings.py` | F-007、F-050、F-071 |
| `pytube` | YouTube 视频/音频下载 | `helpers.py`、`download.py` | F-007、F-055、F-071 |
| `youtube_transcript_api` | YouTube 已有字幕下载 | `download.py` | F-055、F-071 |
| `pycountry` | ISO 639-1 语言代码与名称互转 | `helpers.py` | F-007、F-071 |
| `regex` | 第三方高级正则库（支持复杂 Unicode 匹配） | `srt_ops.py` | F-042、F-071 |
| `numpy` | 数值计算（线性插值等） | `helpers.py`、`srt_ops.py`、`sentence_timings.py` | F-007、F-042、F-050、F-071 |
| `tqdm` | 进度条显示 | `transcribe_video.py` | F-024、F-071 |
| `pandas` | CSV 文件读取（贡献者追踪） | `track_contributors.py` | F-071 |

### faster-whisper 本地模型配置（F-022）

faster-whisper 默认配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 模型名称 | `medium.en` | 英文中等模型，平衡速度与精度 |
| 运行设备 | `cpu` | CPU 运行，无需 GPU |
| 计算精度 | `int8` | 8位整数量化，加速 CPU 推理 |

> **设计意图**（I-02）：默认选择 CPU int8 量化不是为了极致性能，而是为了"没有 GPU 也能跑"——这是面向个人工作流的务实设计，保证在任何环境下都能完成转录工作。

---

## 二、外部 API 依赖（需要密钥/凭证）

以下功能需要配置相应的 API 密钥或 OAuth 凭证才能使用（F-072）。

### 2.1 OpenAI API

| 项 | 说明 |
|----|------|
| 环境变量 | `OPENAI_KEY` |
| 用途 | Whisper API 转录、GPT-4o 上下文感知翻译、句子缩写 |
| 使用模块 | `transcribe_video.py`、`gpt_translate.py` |
| 事实依据 | F-025、F-040、F-041、F-072 |

**功能说明**：
- **Whisper API 转录**（F-025）：调用 `client.audio.transcriptions.create(model="whisper-1", response_format="verbose_json")`，返回含词级时间戳的详细转录结果
- **GPT-4o 翻译**（F-040）：上下文感知翻译，保留最近 `2*n_context_sentences` 条对话历史，`temperature=0.3`，要求非正式第二人称、教育视频旁白风格
- **GPT-4o 句子缩写**（F-041）：将过长句子缩写到指定比例，`temperature=0.0`

### 2.2 DeepL API

| 项 | 说明 |
|----|------|
| 环境变量 | `DEEPL_KEY_FILE` |
| 用途 | 高质量机器翻译（优先选择） |
| 使用模块 | `translate.py` |
| 事实依据 | F-032、F-034、F-036、F-072 |

**功能说明**：
- 环境变量指向包含 DeepL API 密钥的文件路径（F-032）
- 翻译时使用 `formality="prefer_less"`（非正式语体），适配视频旁白风格（F-036）
- DeepL 支持的语言优先使用 DeepL，失败时自动回退到 Google Translate（F-038）

### 2.3 Google Cloud Translation API

| 项 | 说明 |
|----|------|
| 环境变量 | `GOOGLE_TRANSLATION_SERVICE_ACCOUNT` |
| 用途 | 机器翻译回退方案（DeepL 不支持的语言或失败时） |
| 使用模块 | `translate.py` |
| 事实依据 | F-032、F-035、F-037、F-072 |

**功能说明**：
- 环境变量指向 Google Cloud 服务账号 JSON 文件路径（F-032）
- 按每批 50 句调用 API，避免单次请求过长（F-037）
- 翻译结果标记 `model: "google_nmt"`（Google 神经机器翻译）

### 2.4 YouTube Data API v3

| 项 | 说明 |
|----|------|
| 环境变量 | `YOUTUBE_UPLOADING_KEY`、`YOUTUBE_CREDENTIALS_FILE` |
| 用途 | 字幕上传、视频本地化标题/描述更新 |
| 使用模块 | `upload.py` |
| OAuth Scope | `https://www.googleapis.com/auth/youtubepartner` |
| 事实依据 | F-059、F-060、F-061、F-062、F-072 |

**认证流程**（F-060）：
1. 优先从 `YOUTUBE_CREDENTIALS_FILE` 加载已有凭证
2. 凭证过期则自动刷新
3. 无有效凭证时启动本地服务器进行 OAuth2 授权流程
4. 授权成功后保存凭证供下次使用

**功能说明**：
- **字幕上传**（F-061）：通过 `captions().insert()` 上传 SRT 文件，`replace=True` 时先删除现有字幕
- **视频本地化**（F-062）：从各语言目录的 `title.json` 和 `description.json` 读取翻译，更新 YouTube 视频的多语言标题和描述

---

## 三、目标语言支持（F-033）

工具集支持翻译到 19 种目标语言：

| 语言 | 语言名 | 备注 |
|------|--------|------|
| Spanish | 西班牙语 | DeepL 支持 |
| Hindi | 印地语 | Google Translate |
| Chinese | 中文 | DeepL 支持 |
| French | 法语 | DeepL 支持 |
| Russian | 俄语 | DeepL 支持 |
| German | 德语 | DeepL 支持 |
| Arabic | 阿拉伯语 | Google Translate |
| Italian | 意大利语 | DeepL 支持 |
| Portuguese | 葡萄牙语 | DeepL 支持 |
| Japanese | 日语 | DeepL 支持 |
| Korean | 韩语 | DeepL 支持 |
| Ukrainian | 乌克兰语 | DeepL 支持 |
| Thai | 泰语 | Google Translate |
| Persian | 波斯语 | Google Translate |
| Indonesian | 印尼语 | Google Translate |
| Hebrew | 希伯来语 | Google Translate（特殊映射为 `'iw'`，F-014） |
| Turkish | 土耳其语 | DeepL 支持 |
| Hungarian | 匈牙利语 | DeepL 支持 |
| Vietnamese | 越南语 | Google Translate |

---

## 四、环境变量配置方式

### 4.1 Linux/macOS（bash/zsh）

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
# OpenAI API
export OPENAI_KEY="sk-your-openai-key-here"

# DeepL API（指向包含密钥的文件）
export DEEPL_KEY_FILE="/path/to/your/deepl_key.txt"

# Google Cloud Translation（指向服务账号JSON）
export GOOGLE_TRANSLATION_SERVICE_ACCOUNT="/path/to/your/service-account.json"

# YouTube Data API
export YOUTUBE_UPLOADING_KEY="/path/to/your/youtube_client_secret.json"
export YOUTUBE_CREDENTIALS_FILE="/path/to/your/youtube_credentials.json"
```

然后执行 `source ~/.bashrc`（或 `source ~/.zshrc`）使配置生效。

### 4.2 Windows（PowerShell）

在 PowerShell 配置文件（`$PROFILE`）中添加：

```powershell
# OpenAI API
$env:OPENAI_KEY = "sk-your-openai-key-here"

# DeepL API
$env:DEEPL_KEY_FILE = "C:\path\to\your\deepl_key.txt"

# Google Cloud Translation
$env:GOOGLE_TRANSLATION_SERVICE_ACCOUNT = "C:\path\to\your\service-account.json"

# YouTube Data API
$env:YOUTUBE_UPLOADING_KEY = "C:\path\to\your\youtube_client_secret.json"
$env:YOUTUBE_CREDENTIALS_FILE = "C:\path\to\your\youtube_credentials.json"
```

### 4.3 密钥文件格式

- **DeepL 密钥文件**：纯文本文件，第一行即为 DeepL API 密钥
- **Google 服务账号 JSON**：从 Google Cloud Console 下载的标准服务账号密钥 JSON 文件
- **YouTube 客户端密钥**：从 Google Cloud Console 创建 OAuth 2.0 客户端后下载的 JSON 文件
- **YouTube 凭证文件**：首次 OAuth 授权后自动生成，无需手动创建

---

## 五、本地可用 vs 需要 API 的功能区分

| 功能类别 | 具体功能 | 本地可用 | 需要 API | 说明 |
|----------|----------|:---:|:---:|------|
| **转录** | faster-whisper 本地转录 | ✅ | ❌ | CPU int8 量化，无需网络 |
| | OpenAI Whisper API 转录 | ❌ | ✅ | 需要 `OPENAI_KEY`，质量更高 |
| | 自动回退（API→本地） | ✅ | 可选 | API 失败自动用本地模型（F-026） |
| **翻译** | DeepL 翻译 | ❌ | ✅ | 需要 `DEEPL_KEY_FILE` |
| | Google Translate | ❌ | ✅ | 需要 `GOOGLE_TRANSLATION_SERVICE_ACCOUNT` |
| | GPT-4o 上下文翻译 | ❌ | ✅ | 需要 `OPENAI_KEY` |
| | 翻译策略（DeepL→Google回退） | ❌ | ✅ | 自动选择可用后端（F-038） |
| **SRT 处理** | SRT 文件读写/格式化 | ✅ | ❌ | pysrt 本地处理 |
| | 时间戳偏移调整 | ✅ | ❌ | retime_srt.py 完全离线 |
| | 智能分段（按字符数切割） | ✅ | ❌ | 本地算法（F-047） |
| | 词级→句级时间模糊对齐 | ✅ | ❌ | Levenshtein 本地匹配（F-051） |
| **YouTube** | 音频下载（pytube） | ✅ | ❌ | 无需 API 密钥 |
| | 已有字幕下载 | ✅ | ❌ | youtube_transcript_api（F-057） |
| | 字幕上传 | ❌ | ✅ | 需要 YouTube Data API OAuth（F-061） |
| | 视频本地化更新 | ❌ | ✅ | 需要 YouTube Data API（F-062） |
| **工具** | 贡献者追踪（git log） | ✅ | ❌ | 本地 git 历史分析 |

> **最小可用配置**：只安装本地依赖即可完成「音频下载→本地转录→SRT生成→时间轴调整」的完整本地工作流；翻译和 YouTube 上传是可选的增值功能。

---

## 六、安装步骤说明

### 6.1 基础安装（本地功能）

```bash
# 1. 克隆或进入 caption_ops 目录
cd caption_ops

# 2. 安装本地依赖包
pip install faster-whisper pysrt Levenshtein pytube youtube-transcript-api pycountry regex numpy tqdm pandas
```

### 6.2 验证本地安装

```bash
# 测试单个音频文件转录（无需任何API密钥）
python scripts/transcribe.py path/to/your/audio.mp3

# 测试SRT时间偏移
python retime_srt.py input.srt output.srt 1.5
```

### 6.3 配置 API（可选，翻译和上传功能）

1. 获取 OpenAI API Key：https://platform.openai.com/api-keys
2. 获取 DeepL API Key：https://www.deepl.com/pro-api
3. 获取 Google Cloud 服务账号：https://console.cloud.google.com/（启用 Cloud Translation API）
4. 获取 YouTube Data API 凭证：https://console.cloud.google.com/（启用 YouTube Data API v3，创建 OAuth 2.0 客户端）
5. 按上文「环境变量配置方式」设置对应环境变量

### 6.4 注意事项

- **路径硬编码**（F-003、F-004）：`helpers.py` 中硬编码了字幕根目录 `CAPTIONS_DIRECTORY` 和音频目录 `AUDIO_DIRECTORY`，使用前需根据实际环境修改这两个常量
- **faster-whisper 模型下载**：首次运行时会自动下载 `medium.en` 模型（约 1.5GB），需保持网络连接；后续运行使用本地缓存
- **YouTube OAuth 授权**：首次上传字幕时会自动打开浏览器进行 Google 账号授权，授权成功后凭证自动保存

---

## 相关概念

- [00 caption-ops 工具集总览](/concepts/00-caption-ops-overview.md)
- [01 音频转录：faster-whisper本地/API双模式](/concepts/01-transcription.md)
- [02 多语言翻译：DeepL/Google/GPT多后端](/concepts/02-translation.md)
- [03 SRT操作：时间轴与智能分段](/concepts/03-srt-operations.md)
- [04 完整管线：从视频到多语言字幕](/concepts/04-pipeline-workflow.md)
- [Caption Ops CLI 脚本参数速查表](/references/scripts-reference.md)
