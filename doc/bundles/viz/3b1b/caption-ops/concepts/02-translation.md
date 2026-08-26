---
type: Concept
title: 多语言翻译模块
description: caption-ops 的多语言翻译模块支持 DeepL、Google Translate、GPT-4o 三种翻译后端，采用 DeepL 优先、Google 回退的策略路由，提供批量翻译、进度保存、上下文感知翻译等功能，支持 19 种目标语言，专门针对数学科普视频的术语一致性做了优化。
tags: [caption-ops, translation, deepl, google-translate, gpt-4o, multilingual, localization]
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

# 多语言翻译模块

多语言翻译（Translation）是字幕管线中连接英文转录与最终多语言字幕的核心环节。caption-ops 的翻译模块支持三种翻译后端：DeepL API、Google Cloud Translation API、OpenAI GPT-4o，采用统一接口封装和智能策略路由，支持批量翻译、断点续传、上下文感知翻译等功能，覆盖 19 种目标语言（F-031~F-041）。

与通用文本翻译不同，教育视频字幕翻译有其特殊挑战：
- **数学术语一致性**："linear transformation"、"eigenvalue"、"derivative" 这类术语必须在整个视频甚至整个系列中保持译法一致
- **口语化风格**：字幕是旁白，不是书面文章，需要非正式的第二人称语气
- **长度控制**：翻译后句子长度变化大（如德语文本通常比英文长 30%），需要配合 SRT 智能分段
- **公式保留**：LaTeX 公式、数学符号不应被翻译

本模块正是为解决这些问题而设计。本模块覆盖事实 F-031~F-041。

## 翻译功能概述

翻译模块由两个核心文件组成：
- `translate.py`：标准机器翻译接口，封装 DeepL 和 Google Translate 两种后端，提供批量翻译和策略路由（F-031~F-039）
- `gpt_translate.py`：基于 GPT-4o 的高质量上下文感知翻译，适合对翻译质量要求高的场景（F-040~F-041）

设计哲学同样遵循"云端服务+多后端回退"的鲁棒性原则（洞察 I-02）：不依赖单一翻译服务，DeepL 支持的语言优先用 DeepL（质量最高），DeepL 不支持或调用失败时自动回退到 Google Translate，需要更高质量或上下文一致性时可以使用 GPT-4o。

## 三种翻译后端对比

| 后端 | 质量 | 速度 | 成本 | 上下文感知 | 支持语言 | 需要配置 |
|------|------|------|------|------------|----------|----------|
| **DeepL** | ⭐⭐⭐⭐⭐ 最佳 | 快 | 中等（有免费额度） | ❌ 单句翻译 | 约 30 种语言 | `DEEPL_KEY_FILE` |
| **Google Translate** | ⭐⭐⭐⭐ 良好 | 很快 | 低（每月前 50 万字符免费） | ❌ 单句翻译 | 100+ 种语言 | `GOOGLE_TRANSLATION_SERVICE_ACCOUNT` |
| **GPT-4o** | ⭐⭐⭐⭐✨ 优秀 | 较慢 | 较高（按 token 计费） | ✅ 保留前后文 | 所有主流语言 | `OPENAI_KEY` |

### 1. DeepL API 翻译

DeepL 是目前公认质量最高的机器翻译服务，尤其在欧洲语言之间表现出色，也是 caption-ops 的默认首选后端（F-034、F-036）。

客户端通过 `get_deepl_translator()` 函数创建，带有 LRU 缓存避免重复初始化：

```python
import deepl
import os
from functools import lru_cache

@lru_cache()
def get_deepl_translator():
    key_file = os.environ["DEEPL_KEY_FILE"]
    with open(key_file, "r") as f:
        api_key = f.read().strip()
    return deepl.Translator(api_key)
```

翻译句子使用 `deepl_translate_sentences()` 函数：

```python
def deepl_translate_sentences(src_sentences, target_language_code, src_language_code="en"):
    translator = get_deepl_translator()
    results = translator.translate_text(
        src_sentences,
        source_lang=src_language_code,
        target_lang=target_language_code,
        formality="prefer_less",  # 非正式语体，适合旁白
    )
    return [
        {
            "input": src,
            "translatedText": result.text,
            "model": "DeepL",
            "n_reviews": 0,
        }
        for src, result in zip(src_sentences, results)
    ]
```

注意 `formality="prefer_less"` 参数——这是特意设置的，因为 3Blue1Brown 的旁白风格是亲切的对话式（"你会发现..."、"让我们来看..."），而不是正式的学术语气，DeepL 默认可能翻译成过于正式的书面语（F-036）。

### 2. Google Cloud Translation API

Google Translate 是覆盖语言最广的翻译服务，作为 DeepL 的回退方案使用（F-035、F-037）。对于 DeepL 不支持的语言（如乌克兰语、泰语、波斯语、印尼语、希伯来语、匈牙利语、越南语等），直接使用 Google 翻译。

```python
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

@lru_cache()
def get_google_translate_client(service_account_file=None):
    if service_account_file is None:
        service_account_file = os.environ["GOOGLE_TRANSLATION_SERVICE_ACCOUNT"]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    return translate.Client(credentials=credentials)
```

Google 翻译按 50 句一批分批调用，避免单次请求过长（F-037）：

```python
def google_translate_sentences(src_sentences, target_language_code, src_language_code="en", chunk_size=50):
    client = get_google_translate_client()
    results = []
    for i in range(0, len(src_sentences), chunk_size):
        chunk = src_sentences[i:i+chunk_size]
        translations = client.translate(
            chunk,
            source=src_language_code,
            target=target_language_code,
        )
        for src, t in zip(chunk, translations):
            results.append({
                "input": src,
                "translatedText": t["translatedText"],
                "model": "google_nmt",
                "n_reviews": 0,
            })
    return results
```

### 3. GPT-4o 上下文感知翻译

标准机器翻译（DeepL/Google）都是逐句独立翻译的，不考虑上下文，这可能导致：
- 同一个术语在不同句子中翻译不一致
- 代词指代不清（"它"指什么？）
- 语气和风格不统一

`gpt_translate.py` 中的 `gpt4_translate()` 函数使用 GPT-4o 进行上下文感知翻译，翻译每条句子时会保留前后各 `n_context_sentences` 条句子作为对话历史，让模型理解上下文（F-040）：

```python
from openai import OpenAI

def gpt4_translate(sentences, language, formality="informal", n_context_sentences=2):
    client = OpenAI(api_key=os.environ["OPENAI_KEY"])
    
    system_prompt = f"""You are translating educational math video subtitles from English to {language}.
Rules:
- Use informal, second-person tone ("you") like a friendly teacher explaining concepts
- Keep mathematical terms consistent throughout
- Keep LaTeX formulas and mathematical notation unchanged
- Do NOT add explanations, only output the translation
- Match the length of the original as closely as possible"""
    
    all_translations = []
    messages = [{"role": "system", "content": system_prompt}]
    
    for i, sentence in enumerate(sentences):
        # 保留最近 n_context_sentences*2 条对话作为上下文
        context_messages = messages[-(2*n_context_sentences):]
        messages = [{"role": "system", "content": system_prompt}] + context_messages
        messages.append({"role": "user", "content": sentence})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,  # 低随机性，保证一致性
            max_tokens=2 * len(sentence),  # 输出长度限制
        )
        
        translation = response.choices[0].message.content.strip()
        all_translations.append({
            "input": sentence,
            "translatedText": translation,
            "model": "gpt-4o",
            "n_reviews": 0,
        })
        messages.append({"role": "assistant", "content": translation})
    
    return all_translations
```

关键参数说明：
- `temperature=0.3`：较低的温度值，减少随机性，保证术语和风格一致性
- `n_context_sentences=2`：默认保留前后各 2 条句子作为上下文
- `max_tokens=2*len(sentence)`：防止模型输出过长的解释
- System prompt 明确要求非正式第二人称、教育视频旁白风格、保留公式（F-040）

GPT-4o 翻译质量最高但成本也最高，适合：
- 系列视频第一集，用于建立术语基准
- 之前翻译问题较多的语言
- 关键视频需要高质量翻译

## translators.py 统一接口与策略路由

`translate.py` 中的 `translate_sentences()` 函数是统一入口，实现了智能后端选择策略（F-038）：

```python
def translate_sentences(en_sentences, target_language):
    language_code = get_language_code(target_language)
    
    # DeepL 支持的语言列表（简化示意）
    deepl_supported = {"es", "de", "fr", "it", "ja", "ko", "pt", "ru", "zh", ...}
    
    try:
        if language_code in deepl_supported:
            return deepl_translate_sentences(en_sentences, language_code.upper())
        else:
            return google_translate_sentences(en_sentences, language_code)
    except Exception:
        # DeepL 失败自动回退到 Google
        return google_translate_sentences(en_sentences, language_code)
```

策略逻辑总结：
1. DeepL 支持的语言优先使用 DeepL（质量更高）
2. DeepL 不支持的语言直接使用 Google Translate（覆盖更广）
3. 任何后端调用失败时自动回退到 Google（鲁棒性）
4. 每条翻译结果标记 `model` 字段，记录使用的后端，便于质量追踪

## 目标语言列表

caption-ops 支持 19 种目标语言，覆盖了 3Blue1Brown 观众的主要语言区域（F-033）：

| 语言 | ISO 代码 | DeepL 支持 | 备注 |
|------|----------|------------|------|
| Spanish（西班牙语） | es | ✅ | |
| Hindi（印地语） | hi | ❌ | Google 翻译 |
| Chinese（中文） | zh | ✅ | |
| French（法语） | fr | ✅ | |
| Russian（俄语） | ru | ✅ | |
| German（德语） | de | ✅ | |
| Arabic（阿拉伯语） | ar | ❌ | Google 翻译 |
| Italian（意大利语） | it | ✅ | |
| Portuguese（葡萄牙语） | pt | ✅ | |
| Japanese（日语） | ja | ✅ | |
| Korean（韩语） | ko | ✅ | |
| Ukrainian（乌克兰语） | uk | ❌ | Google 翻译 |
| Thai（泰语） | th | ❌ | Google 翻译 |
| Persian（波斯语） | fa | ❌ | Google 翻译 |
| Indonesian（印尼语） | id | ❌ | Google 翻译 |
| Hebrew（希伯来语） | he/iw | ❌ | 代码特殊映射为 `iw`（F-014） |
| Turkish（土耳其语） | tr | ✅ | |
| Hungarian（匈牙利语） | hu | ❌ | Google 翻译 |
| Vietnamese（越南语） | vi | ❌ | Google 翻译 |

语言名称和 ISO 639-1 代码之间的转换通过 `helpers.py` 中的 `get_language_code()` 和 `get_language_from_code()` 函数实现（F-014、F-015），其中希伯来语特殊映射为 `'iw'`（这是 Google 翻译的历史遗留代码），希腊语映射为 `'el'`，其他语言通过 `pycountry` 库查询。

## 批量翻译与进度保存

翻译是按句子批量进行的，结果保存在 JSON 文件中，支持断点续传——如果翻译到一半中断了，下次运行时已经翻译过的句子不需要重新翻译（这在处理长视频批量翻译时非常重要，可以节省 API 费用和时间）。

翻译结果的 JSON 格式（`sentence_translations.json`）如下：

```json
[
  {
    "input": "Today I want to talk about linear algebra.",
    "translatedText": "今天我想谈谈线性代数。",
    "model": "DeepL",
    "n_reviews": 0
  },
  {
    "input": "It's the branch of math about vectors and matrices.",
    "translatedText": "它是关于向量和矩阵的数学分支。",
    "model": "DeepL",
    "n_reviews": 1
  }
]
```

`n_reviews` 字段记录人工审核次数，当审核比例超过 50% 时，同步脚本会将旧的 community 字幕重命名备份（F-067）。

## 句子缩写功能

不同语言表达相同意思所需的字符数差异很大：德语、俄语通常比英文长，中文、日文通常比英文短。当翻译后的句子过长导致 SRT 一行放不下太多字时，可以使用 `gpt_translate.py` 中的 `gpt4_abbreviate()` 函数将句子缩写到指定比例（F-041）：

```python
def gpt4_abbreviate(sentence, language, proportion):
    """将句子缩写到原长度的 proportion 比例（0-1）"""
    client = OpenAI(api_key=os.environ["OPENAI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Abbreviate the following {language} subtitle sentence to {int(proportion*100)}% of its length while preserving meaning. Output ONLY the abbreviated sentence."},
            {"role": "user", "content": sentence},
        ],
        temperature=0.0,  # 零温度，确定性输出
    )
    return response.choices[0].message.content.strip()
```

这个功能通常在 SRT 智能分段之后使用：如果某段翻译后实在太长无法合理分段，可以先缩写再重新分段。

## 翻译质量注意事项

机器翻译不可能 100% 正确，尤其是数学科普内容。以下是需要特别注意人工审核的点：

### 1. 数学术语一致性

这是最重要的审核点。常见容易翻译不一致的术语示例：

| 英文术语 | 常见中文译法 | 注意事项 |
|----------|-------------|----------|
| linear transformation | 线性变换 | 不要翻译成"线性转换" |
| eigenvalue / eigenvector | 特征值 / 特征向量 | 不要翻译成"本征值"（物理圈用法） |
| derivative | 导数 | 不要翻译成"微商" |
| integral | 积分 | 一般没问题 |
| span | 张成（空间） | 容易直译为"跨度" |
| basis | 基 | 容易直译为"基础" |
| determinant | 行列式 | 不要翻译成"决定因素" |

使用 GPT-4o 上下文翻译能大幅改善术语一致性，但首次处理新语言时还是建议人工建立术语表。

### 2. 公式与数学符号

LaTeX 公式（如 `$\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$`）、变量名（如 `$v$`、`$A$`）、数字不应被翻译。DeepL 和 Google 通常能正确处理，但偶尔会把公式中的字母当成普通单词翻译，需要注意。

### 3. 口语化与语气

3Blue1Brown 的旁白是对话式的，不是教科书式的。要避免：
- 过于正式的书面语（"综上所述"→"所以你看"）
- 生硬的被动语态（"它被定义为"→"我们把它定义为"）
- 丢失第二人称亲切感（"人们可以发现"→"你会发现"）

GPT-4o 在这方面表现最好，DeepL 次之（需要设置 `formality="prefer_less"`），Google 翻译有时会过于正式。

### 4. 文化梗与双关

Grant 偶尔会在视频中加入一些英语双关或文化梗，机器翻译通常无法处理，需要人工意译或加注释。

## 从翻译生成 SRT

翻译完成后，使用 `sentence_translations_to_srt()` 函数从翻译 JSON 生成标准 SRT 文件（F-039）：

```python
def sentence_translations_to_srt(sentence_translation_file):
    with open(sentence_translation_file, "r", encoding="utf-8") as f:
        translations = json.load(f)
    
    # 中日韩等字符型语言每段最多 30 字符，其他语言 90 字符
    target_language = detect_language(translations)
    max_chars = 30 if target_language in ["zh", "ja", "ko"] else 90
    
    # 读取句子时间轴，配合智能分段生成 SRT
    # 输出文件名为 auto_generated.srt
    ...
```

字符数限制是字幕可读性的关键：
- 中文/日文/韩文：每个字符是一个方块字，阅读速度快，每行最多 30 字符
- 英文/法文/德文等拼音文字：单词较长，每行最多 90 字符

生成的 SRT 文件默认命名为 `auto_generated.srt`，表示是自动生成的，人工审核后可以重命名为其他名字（F-039）。

## 命令行用法

翻译通常不是单独运行的，而是作为端到端管线的一部分。但你也可以单独调用翻译功能：

### 示例 1：在端到端管线中指定翻译语言

```bash
# 翻译到所有支持的 19 种语言并上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" --languages all

# 只翻译到中文、日文、韩文
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" --languages chinese,japanese,korean

# 只生成翻译和 SRT，不上传
python scripts/auto_caption.py "https://www.youtube.com/watch?v=VIDEO_ID" --languages chinese --no-upload
```

### 示例 2：Python API 批量翻译

```python
from translate import translate_sentences
from helpers import json_dump

sentences = [
    "Today I want to talk about linear algebra.",
    "It's all about vectors and how they transform.",
    "The key concept is the linear transformation.",
]

# 翻译到中文
translations = translate_sentences(sentences, "Chinese")

# 保存结果
json_dump(translations, "chinese_translations.json")
```

### 示例 3：使用 GPT-4o 高质量翻译

```python
from gpt_translate import gpt4_translate

sentences = [
    "If you look at this matrix, what do you notice?",
    "The columns tell you where the basis vectors land.",
    "That's the key insight behind all of linear algebra.",
]

# GPT-4o 上下文感知翻译，保留前后 2 句上下文
translations = gpt4_translate(sentences, "Chinese", n_context_sentences=2)
```

## 相关概念

- [00 caption-ops 工具集总览](/concepts/00-caption-ops-overview.md)
- [01 音频转录模块](/concepts/01-transcription.md)
- [SRT 操作与智能分段](/concepts/03-srt-operations.md)
- [完整管线工作流](/concepts/04-pipeline-workflow.md)
- [CLI 脚本参考](/references/scripts-reference.md)
- [依赖与 API 配置](/references/dependencies.md)
