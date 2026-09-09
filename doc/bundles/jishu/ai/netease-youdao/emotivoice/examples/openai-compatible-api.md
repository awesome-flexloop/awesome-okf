---
type: example
title: OpenAI 兼容 API 调用示例
description: 基于 openaiapi.py 演练 OpenAI 兼容 TTS 服务的启动与调用：curl 与 Python 客户端两种形态、SpeechRequest 字段语义、speed 后处理注意事项与依赖分装。
tags: [emotivoice, tts, serving, fastapi, openai-api, example]
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

# OpenAI 兼容 API 调用示例

本例基于 `openaiapi.py` 演练 EmotiVoice 的 OpenAI 兼容 TTS 服务：安装依赖、启动服务、用 curl 与 Python 客户端调用，并厘清 `speed` 字段的真实行为。服务结构背景见 [06 服务化部署](/concepts/06-serving-api.md)。

## 第 1 步：安装依赖

服务化依赖与推理核心依赖分装两份清单（F-ev-039、F-ev-040）：

```bash
# 推理核心依赖（13 项，含 g2p 前端与模型栈）
pip install torch torchaudio numpy numba scipy transformers soundfile yacs g2p_en jieba pypinyin pypinyin_dict
python -m nltk.downloader "averaged_perceptron_tagger_eng"

# OpenAI 兼容服务追加依赖（5 项）
pip install -r requirements.openaiapi.txt   # fastapi python-multipart "uvicorn[standard]" pydub pyrubberband
```

## 第 2 步：启动服务

`openaiapi.py` 在模块级完成 `Config()`、`get_models()` 与 `FastAPI()` 装配（F-ev-033），模型加载发生在进程启动阶段：

```bash
uvicorn openaiapi:app --host 0.0.0.0 --port 8000
```

`get_models()` 内部经 `scan_checkpoint(cp_dir, prefix, c=8)` 自动选择最新 `g_` 与 `checkpoint_` 前缀 checkpoint（F-ev-033），无需手动指定。

## 第 3 步：调用服务

### curl 形态

唯一路由为 `POST /v1/audio/speech`（F-ev-033），请求体字段与 OpenAI TTS API 对齐（F-ev-034）：

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "今天天气真好，适合去 park 散步。",
    "voice": "8051",
    "prompt": "Happy",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### Python 客户端形态

因路由与字段均对齐 OpenAI TTS API（F-ev-033、F-ev-034），可直接使用 OpenAI SDK：

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
response = client.audio.speech.create(
    model="emoti-voice",        # SpeechRequest 默认值（F-ev-034）
    voice="8051",               # 说话人，须存在于 speaker2（F-ev-027）
    input="今天天气真好，适合去 park 散步。",
    speed=1.0,
    response_format="wav",      # 非 wav 将经 pydub 转码（F-ev-035）
)
with open("speech.wav", "wb") as f:
    f.write(response.content)
```

请求进入后的处理链：原始文本经 `g2p_cn_en` 转音素 → `emotivoice_tts(text, prompt, content, speaker, models)` 完成嵌入计算与生成 → 波形写出（F-ev-033）。

## 第 4 步：理解 speed 字段

`SpeechRequest.speed` 默认 `1.0`（F-ev-034），但它**不是模型内生的时长控制**：

- 生成器推理中 `alpha=1.0` 写死（F-ev-020），模型只产出 16 kHz 单速波形；
- 仅当 `speed≠1.0` 时，服务端对已合成波形调用 `pyrubberband.time_stretch` 做时域拉伸（F-ev-035）；
- 时域拉伸引入相位失真与音质损耗。

```bash
# 不推荐：音质敏感场景避免 speed != 1.0
curl -X POST http://localhost:8000/v1/audio/speech \
  -d '{"input": "...", "speed": 1.5}' --output fast.mp3
```

需要调节奏时，优先在文本侧增减标点（前端会转成 `sp3` 等停顿标记，F-ev-006），让模型自己学出韵律变化，而非事后拉伸波形。

## 字段速查

| 字段 | 默认值 | 调用建议 |
|------|--------|----------|
| `input` | —（必填） | 中英混合直接写，前端自动处理（F-ev-004） |
| `voice` | `'8051'` | 2014 个音色名之一（F-ev-027），错误值将被拒 |
| `prompt` | `''` | 情感控制粒度有限，推荐 `Happy/Excited/Sad/Angry`（F-ev-025） |
| `response_format` | `'mp3'` | wav 免转码；其余格式经 pydub（F-ev-035） |
| `speed` | `1.0` | 保持默认，非 1.0 走外部后处理（F-ev-035） |

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [06 服务化部署](/concepts/06-serving-api.md)
