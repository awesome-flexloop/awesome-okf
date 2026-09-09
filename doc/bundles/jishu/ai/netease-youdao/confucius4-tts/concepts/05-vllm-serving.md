---
type: Concept
title: vLLM 加速路径与服务化
description: 双后端分治（HF vs vLLM）、patch_vllm 自定义架构注册、generate_stream 流式切块，以及 FastAPI server.py 与 Gradio webui.py 的服务化形态。
tags: [confucius4-tts, tts, vllm, streaming, fastapi, gradio, serving]
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

# vLLM 加速路径与服务化

Confucius4-TTS 提供两套并行维护的 T2S 实现：普通路径以 Hugging Face 方式加载 `Text2Semantic`（见 [00 总览](/concepts/00-overview.md)）；vLLM 路径把 T2S 重新实现为 vLLM 自定义多模态架构，以获得 LLM 级的解码加速与流式输出能力。本篇说明双后端的差异、vLLM 适配层机制，以及两种服务化形态。

## 双后端分治

| 维度 | HF 后端 `ConfuciusTTS` | vLLM 后端 `ConfuciusTTSVLLM` |
|---|---|---|
| 入口 | confuciustts/cli/inference.py | confuciustts/cli/inference_vllm.py |
| 构造签名 | `__init__(config_path="config/inference_config.yaml", t2s_checkpoint=None, device="cuda")`（F-c4t-005） | `__init__(config_path, gpu_memory_utilization=0.4, device="cuda", model_dir=None)`（F-c4t-035） |
| generate | 同步 | `async def generate(...)`（F-c4t-036） |
| 采样参数 | 全量暴露（temperature/top_p/top_k/num_beams/repetition_penalty 等） | 仅保留 n_timesteps、inference_cfg_rate 等少数扩散参数 |
| 流式 | 不支持 | `generate_stream`，返回 AsyncIterator[torch.Tensor]（F-c4t-037） |
| 使用场景 | example.py、webui.py、调参与研究 | server.py、高并发服务、流式播放 |

关键认知：**"vLLM 加速"不是透明切换，而是两套实现**。功能集并不对齐——HF 路径的采样控制粒度在 vLLM 路径不可用；且加速收益仅限 T2S 段，S2A 的 25 步欧拉求解与 BigVGAN 在两路径中完全相同。部署前应做 A/B 行为对齐验证。

## vLLM 适配层

T2S 能被 vLLM 加速的根本原因是语义 token 的**离散词表**（semantic_vocab_size=8194，F-c4t-012）——对 vLLM 而言这就是一个普通 LLM。适配工作由 confuciustts/llm/llm_vllm.py 完成（F-c4t-038）：

- 常量 `PLACEHOLDER_TOKEN = "!"`、`PLACEHOLDER_TOKEN_ID = 0`：多模态占位符（条件向量以图像槽位方式注入）；
- `class Text2SemanticVLLM(nn.Module, SupportsPP, SupportsMultiModal)`：vLLM 自定义架构本体，支持流水线并行；
- 配套类：ConfuciusTTSProcessingInfo、ConfuciusTTSDummyInputsBuilder、ConfuciusTTSDataParser、ConfuciusTTSMultiModalProcessor、_TransformerBackbone。

注册机制：inference_vllm.py 顶层 `import confuciustts.llm.patch_vllm` 即完成自定义架构注册（F-c4t-039）——该 patch 模块在 vLLM 的架构表中登记 Confucius4-TTS。升级 vLLM 版本（锁定 0.16.0，F-c4t-055）时须回归 patch 注册兼容性。

另外 `model_dir` 参数或 MODEL_DIR 环境变量可重写 "./checkpoints" 前缀（F-c4t-035），便于把检查点放到自定义路径。

## 流式输出：generate_stream

```python
async def generate_stream(..., first_chunk_size_tokens=25,
                          chunk_size_tokens=50, overlap_tokens=10, ...)
```

返回 AsyncIterator[torch.Tensor]（F-c4t-037）。内部以 `_synth_segment_stream`（流式）与 `_synth_segment`（非流式）分别合成各段：段内按 chunk 切块产出音频，相邻 chunk 以 overlap_tokens=10 重叠保证连续性。chunk 粒度（50 token）与 [02 长度调节](/concepts/02-length-regulation.md) 中的段切分（80 token/段）是两个独立层次：段间靠 cross_fade 拼接，chunk 间靠 overlap 衔接。

## 服务化形态一：server.py（FastAPI）

server.py 基于 FastAPI，**只挂 vLLM 后端**（F-c4t-040）：

- 命令行默认 `--host 0.0.0.0 --port 8000 --gpu_memory_utilization 0.4`，uvicorn workers=1；
- 模块常量：LANGUAGES 为 14 元组（zh/en/ja/ko/de/fr/th/id/vi/es/pt/it/ru/ms）、ALLOWED_AUDIO_EXTENSIONS={.wav,.flac,.mp3,.m4a,.ogg}、MAX_REFERENCE_AUDIO_BYTES=50MB、MAX_TEXT_LENGTH=1024（F-c4t-041）；
- 路由：`GET /health` 就绪探针；`POST /api/tts` 整句合成，返回 WAV PCM_16，响应头含 X-Sample-Rate / X-Duration-Sec / X-Elapsed-Sec；`POST /api/tts/stream` 原始 int16-LE PCM 流，响应头含 X-Sample-Rate / X-Channels / X-Encoding（F-c4t-042）；
- 上传的参考音频暂存于 `/tmp/confucius4_upload_<uuid>`（F-c4t-043）。

## 服务化形态二：webui.py（Gradio）

webui.py 基于 Gradio Blocks（theme Soft），默认 `--port 7860 --host 0.0.0.0`（F-c4t-044）。与 server.py 不同，webui 走 **HF 后端**：`build_demo` 内新建 event loop 驱动 async `model.generate`——把同步 HF 接口包装成异步供 Gradio 调用。

## 选型决策

需要流式 / 高并发 / 服务化 → vLLM 路径 + server.py；需要调采样参数、研究语义生成行为 → HF 路径（example.py / webui.py）。两者输出存在系统性差异的可能（采样控制粒度不同），切换路径前应以固定文本与参考音频做 A/B 验证。

## 相关概念

- [00 仓库全景与推理链路总览](/concepts/00-overview.md)
- [02 长度调节与时长启发式](/concepts/02-length-regulation.md)
- [04 声码器与 BigVGAN 集成](/concepts/04-bigvgan-vocoder.md)
