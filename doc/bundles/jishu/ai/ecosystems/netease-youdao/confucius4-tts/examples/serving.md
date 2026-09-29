---
type: Example
title: 服务化启动与请求（server.py / webui.py）
description: 启动 vLLM 后端 FastAPI 服务并调用 /api/tts 与 /api/tts/stream，以及 Gradio WebUI 的启动方式；含接口约束与流式客户端示例。
tags: [confucius4-tts, tts, example, serving, fastapi, vllm, streaming]
generated: { by: "reference_agent/trae-solo", at: "2026-09-09T00:00:00Z" }
verified: { by: "process:source-reading-v", at: "2026-09-09T00:00:00Z" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: Confucius4-TTS 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: Confucius4-TTS 核心洞察与知识地图
---

# 服务化启动与请求（server.py / webui.py）

本例演示两条服务化路径：FastAPI 服务（vLLM 后端，面向集成方）与 Gradio WebUI（HF 后端，面向人工体验）。接口与常量均忠实于 server.py / webui.py 源码（F-c4t-040~044）。

## 路径一：FastAPI 服务（vLLM 后端）

### 启动

```bash
# 默认 --host 0.0.0.0 --port 8000 --gpu_memory_utilization 0.4（F-c4t-040）
python server.py
# 或显式指定
python server.py --host 0.0.0.0 --port 8000 --gpu_memory_utilization 0.4
```

依赖 requirements_vllm_add.txt（vllm==0.16.0、fastapi==0.136.3、uvicorn==0.49.0，F-c4t-055）。server.py **只挂 vLLM 后端**，uvicorn workers=1（F-c4t-040）。

### 就绪探针

```bash
curl http://localhost:8000/health
# 模型加载完成返回 {"status": "ok", "sample_rate": 22050}；加载中返回 "loading"（F-c4t-042）
```

### 整句合成：POST /api/tts

接口参数为 multipart 表单：`text`（必填）、`lang`（默认 "zh"）、`reference`（参考音频文件，必填）。服务端约束：语言须在 LANGUAGES 14 元组内，参考音频扩展名限 {.wav,.flac,.mp3,.m4a,.ogg}、大小 ≤ 50MB，文本长度 ≤ 1024 字符（F-c4t-041）。

```bash
curl -X POST http://localhost:8000/api/tts \
  -F "text=支持多种语言，轻松实现跨语种朗读。" \
  -F "lang=zh" \
  -F "reference=@reference.wav" \
  -o output.wav -D headers.txt

# 响应体：WAV PCM_16 文件（F-c4t-042）
# 响应头含 X-Sample-Rate / X-Duration-Sec / X-Elapsed-Sec（F-c4t-042）
cat headers.txt
```

Python 客户端：

```python
import requests

with open("reference.wav", "rb") as f:
    resp = requests.post(
        "http://localhost:8000/api/tts",
        data={"text": "支持多种语言，轻松实现跨语种朗读。", "lang": "zh"},
        files={"reference": f},
    )
resp.raise_for_status()
with open("output.wav", "wb") as f:
    f.write(resp.content)
print(resp.headers["X-Sample-Rate"], resp.headers["X-Duration-Sec"])
```

### 流式合成：POST /api/tts/stream

表单参数与 /api/tts 相同，响应为**原始 int16-LE PCM 流**（非 WAV 容器），响应头含 X-Sample-Rate / X-Channels / X-Encoding（F-c4t-042）。内部对应 vLLM 后端的 `generate_stream`，按 chunk 产出（first_chunk_size_tokens=25、chunk_size_tokens=50、overlap_tokens=10，F-c4t-037）。

```python
import requests

url = "http://localhost:8000/api/tts/stream"
with open("reference.wav", "rb") as f:
    resp = requests.post(
        url,
        data={"text": "这是一段需要边下边播的长文本。", "lang": "zh"},
        files={"reference": f},
        stream=True,
    )
resp.raise_for_status()
sample_rate = int(resp.headers["X-Sample-Rate"])  # 22050
with open("stream.pcm", "wb") as out:
    for chunk in resp.iter_content(chunk_size=4096):
        if chunk:
            out.write(chunk)  # int16-LE PCM，可直接送声卡或 ffmpeg 封装
```

## 路径二：Gradio WebUI（HF 后端）

```bash
# 默认 --port 7860 --host 0.0.0.0（F-c4t-044）
python webui.py
```

webui.py 基于 Gradio Blocks（theme Soft），走 **HF 后端**：`build_demo` 内新建 event loop 驱动 async `model.generate`（F-c4t-044）。适合调参与人工试听；注意它与 server.py 是两个后端实现，输出可能有系统性差异（F-c4t-035~039，详见 [05 vLLM 加速路径与服务化](/concepts/05-vllm-serving.md)）。

## 选型速查

| 需求 | 路径 |
|---|---|
| HTTP 集成、高并发、流式播放 | server.py（vLLM） |
| 人工试听、调采样参数 | webui.py（HF） |
| 离线批处理、研究语义生成 | example.py（HF，见 [单次推理全流程](single-inference.md)） |

## 相关概念

- [05 vLLM 加速路径与服务化](/concepts/05-vllm-serving.md)
- [02 长度调节与时长启发式](/concepts/02-length-regulation.md)
