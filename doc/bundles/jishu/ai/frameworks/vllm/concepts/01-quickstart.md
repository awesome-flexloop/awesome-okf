---
type: Concept
title: "快速开始：从安装到首个 token"
description: "vLLM 最小闭环——uv/pip 安装、LLM 离线批量推理、vllm serve 在线服务、curl 与 openai SDK 验证首 token，附生成配置与 chat 模板两条注意"
tags: [vllm, quickstart, install, offline-inference, online-serving, 入门]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-quickstart
    resource: /references/source-map.md
    title: docs/getting_started/quickstart.md（本地检出）
  - id: website-home
    url: https://vllm.ai/
---

# 快速开始：从安装到首个 token

本文用最小步骤跑通 vLLM 的两个入口：先离线推理验证引擎，再起在线服务验证 API。全部命令在 vLLM v0.32.x + NVIDIA CUDA 环境实测口径整理（F-002、F-008）。

## 1. 安装

官网首页的交互式 Quick Start 会按 Build（Stable/Nightly）× Platform（CUDA/ROCm/XPU/CPU）× Package（uv/Python/Docker）生成安装命令；默认组合为 CUDA + uv（F-003）：

```bash
# 推荐：uv 自动按驱动版本选择 PyTorch 后端
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto

# 安装预编译内核，避免 Hopper 及以上 GPU 启动时现场编译（省数分钟）
vllm download-kernels
```

要点（F-003、F-120）：

- **Python 版本**：官网要求 3.10+、推荐 3.12+；本地 quickstart 的 prerequisites 标注 3.11–3.14。生产环境取交集 **3.12**。
- `--torch-backend=auto` 让 uv 读取 CUDA 驱动版本自动选择 `cu126`/`cu130` 等 PyTorch index；也可显式指定。
- 免安装试用：`uv run --with vllm vllm --help`。
- macOS Apple Silicon 走独立项目 vLLM-Metal（MLX 后端，非本主仓库路径，F-121）。

完整平台矩阵（ROCm/XPU/TPU/CPU/昇腾）见 [02 安装与硬件平台](02-installation.md)。

## 2. 离线批量推理（LLM 类）

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(model="facebook/opt-125m")
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

三个注意点：

1. **`generation_config.json` 默认生效**：模型仓库自带生成配置时，vLLM 默认采用模型作者推荐参数；想用 vLLM 默认值，创建实例时传 `generation_config="vllm"`（F-070）。
2. **`llm.generate` 不自动套 chat 模板**：Instruct/Chat 模型要么手动 `tokenizer.apply_chat_template(...)`，要么用 `llm.chat(messages_list, sampling_params)`（F-060）。
3. **模型来源默认 HuggingFace**：换 ModelScope 设环境变量 `VLLM_USE_MODELSCOPE=True`（F-060）。

## 3. 在线服务（vllm serve）

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct
```

默认监听 `http://localhost:8000`（`--host`/`--port` 可改），单服务单模型（F-064）。验证三连：

```bash
# 1) 模型清单
curl http://localhost:8000/v1/models

# 2) 文本补全
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "Qwen/Qwen2.5-1.5B-Instruct", "prompt": "San Francisco is a", "max_tokens": 7, "temperature": 0}'

# 3) 对话补全
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "Qwen/Qwen2.5-1.5B-Instruct", "messages": [{"role": "user", "content": "Tell me a joke."}]}'
```

用 `openai` Python SDK 只需改 `base_url`（F-062）：

```python
from openai import OpenAI

client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")
completion = client.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    prompt="San Francisco is a",
)
print("Completion result:", completion)
```

鉴权：传 `--api-key sk-xxx`（可多个，支持轮换）或环境变量 `VLLM_API_KEY`（F-064）。

## 4. 启动时都发生了什么

理解启动顺序有助于排障（细节见 [03 架构总览](03-architecture.md) 与 [06 执行层](06-execution.md)）：

1. `EngineArgs` 解析参数 → 生成 `VllmConfig`（F-013）；
2. 启动 API server 进程（DP>1 时每 rank 一个，F-010）；
3. EngineCore 进程拉起 GPU Worker 进程（每 GPU 一个，F-010）；
4. Worker 初始化设备 → 加载模型权重（初始化时即按 TP 切分，F-015）→ profiling 前向测定 KV cache 容量 → 分配 block 池（F-053）；
5. 捕获 CUDA graph（warmup，除 `--enforce-eager`，F-052）；
6. 服务就绪，`/health` 返回 200。

## 延伸阅读

- [02 安装与硬件平台](02-installation.md)：非 CUDA 平台与 Docker 路径
- [07 配置体系](07-configuration.md)：常用启动参数分组速查
- [examples/01 离线批量推理](../examples/01-offline-inference.md)：带 SamplingParams 细节的完整场景
