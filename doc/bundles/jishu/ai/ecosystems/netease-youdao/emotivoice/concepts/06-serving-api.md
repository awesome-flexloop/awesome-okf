---
type: concept
title: 服务化部署：OpenAI 兼容 API 与 Streamlit Demo
description: 讲解 openaiapi.py 的 FastAPI OpenAI 兼容层、SpeechRequest 字段、speed 波形级后处理真相与 demo_page.py 交互形态，以及两套分离的依赖清单。
tags: [emotivoice, tts, serving, fastapi, openai-api, streamlit]
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

# 服务化部署：OpenAI 兼容 API 与 Streamlit Demo

EmotiVoice 提供两种开箱即用的服务化形态：一个 **OpenAI 兼容的 FastAPI 服务**（`openaiapi.py`），和一个 **Streamlit 交互页**（`demo_page.py`）。本文讲清二者的结构、能力边界与部署要点。

## openaiapi.py：薄封装 + 外部后处理

`openaiapi.py` 在模块级完成全部装配：`config = Config()`、`models = get_models()`、`app = FastAPI()`（F-ev-033）。`get_models()` 返回五元组 `(style_encoder, generator, tokenizer, token2id, speaker2id)`，经 `scan_checkpoint(cp_dir, prefix, c=8)` 自动挑选最新 checkpoint（F-ev-033）。

### 路由与请求模型

唯一的路由为（F-ev-033）：

```
POST /v1/audio/speech
```

请求体 `SpeechRequest(BaseModel)` 字段与 OpenAI TTS API 对齐（F-ev-034）：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input` | `str` | —（必填） | 待合成文本 |
| `voice` | `str` | `'8051'` | 说话人标识（speaker2 中的音色名） |
| `prompt` | `Optional[str]` | `''` | 风格提示文本 |
| `language` | `Optional[str]` | `'zh_us'` | 语言标记 |
| `model` | `Optional[str]` | `'emoti-voice'` | 模型名（占位） |
| `response_format` | `Optional[str]` | `'mp3'` | 输出音频格式 |
| `speed` | `Optional[float]` | `1.0` | 语速 |

### 推理链路

路由处理函数内部：原始文本先经 `g2p_cn_en` 转音素（F-ev-012 的再导出在此发挥作用），然后调 `emotivoice_tts(text, prompt, content, speaker, models)` 完成嵌入计算与生成器推理（F-ev-033）。

### speed 的真相：波形级后处理

这是最容易被 API 形态误导的一点——`speed` **不是模型内生的时长控制**：

- 模型推理中 `alpha=1.0` 写死（F-ev-020），只产出 16 kHz 单速波形；
- `speed≠1.0` 时调用 `pyrubberband.time_stretch` 对已合成波形做时域拉伸（F-ev-035）；
- WAV 经 `soundfile` 写入 BytesIO，非 wav 的 `response_format` 再经 `pydub.AudioSegment` 转码，最终以 `Response(content=..., media_type=f"audio/{response_format}")` 返回（F-ev-035）。

时域拉伸会引入相位失真与音质损耗。实践建议：**音质敏感场景显式保持 `speed=1.0`**；需要调节奏优先在文本侧增减标点/停顿标记（sp1-sp4 家族，见 [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)），而非依赖 time_stretch。

## demo_page.py：Streamlit 交互页

`demo_page.py` 是面向体验与调试的图形界面：`get_models()` 带 `@st.cache_resource` 装饰避免重复加载模型；推理函数为 `tts(name, text, prompt, content, speaker, models)`；语言下拉仅 `["zh_us"]` 一项；speaker 下拉来自 `config.speakers`（F-ev-036）。它与服务层共享同一套模型装配逻辑，适合本地快速试听不同 prompt/音色组合。

## 依赖分装

部署时必须按形态分装依赖（F-ev-039、F-ev-040）：

| 依赖清单 | 数量 | 内容 |
|----------|------|------|
| `requirements.txt` | 13 项 | torch、torchaudio、numpy、numba、scipy、transformers、soundfile、yacs、g2p_en、jieba、pypinyin、pypinyin_dict、streamlit |
| `requirements.openaiapi.txt` | 5 项 | fastapi、python-multipart、uvicorn[standard]、pydub、pyrubberband |

推理核心依赖与服务化依赖分离：仅跑推理主入口不需要 fastapi/pydub/pyrubberband；起 OpenAI 兼容服务则需在核心依赖之上追加 5 项服务化依赖。README 的安装命令还包含 `python -m nltk.downloader "averaged_perceptron_tagger_eng"`（g2p_en 的词性标注数据，F-ev-039）。

## 部署要点小结

1. 服务进程启动即完成全部模型加载（模块级 `get_models()`，F-ev-033），首请求无冷启动；
2. checkpoint 由 `scan_checkpoint` 自动选择最新（F-ev-033），升级模型只需替换 ckpt 目录文件；
3. `voice` 取值须在 `data/youdao/text/speaker2` 的 2014 个音色名之内（F-ev-027），默认 `'8051'`（F-ev-034）；
4. 调用演练见 [OpenAI 兼容 API 调用示例](/examples/openai-compatible-api.md)。

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)
