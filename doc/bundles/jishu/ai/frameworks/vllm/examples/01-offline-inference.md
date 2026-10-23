---
type: Example
title: "示例 01：离线批量推理（LLM 类）"
description: "使用 vllm.LLM 与 SamplingParams 演示离线推理全流程——文本生成、chat 模式、采样参数调优、FP8 量化加载与批处理，全部基于官方 quickstart 与 vllm/entrypoints/llm.py 真实 API
tags: [vllm, example, offline-inference, llm-class, sampling-params, fp8, chat]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-llm-entry
    resource: /references/source-map.md
    title: vllm/entrypoints/llm.py 与 docs/getting_started/quickstart.md（本地检出）
---

# 示例 01：离线批量推理（LLM 类）

离线推理是 vLLM 的「库模式」：在自有进程内构造 `LLM` 对象，批量处理请求，不起 HTTP 服务（F-060）。适合批处理、评测、数据合成等场景。入口类在 `vllm/entrypoints/llm.py`，构造参数即 `EngineArgs` 的数据类化（见 [07 配置体系](../concepts/07-configuration.md)）。

## 环境要求

- `pip install vllm==0.32.*`（或本地检出安装）
- 本示例用官方 quickstart 同款小模型 `facebook/opt-125m`，CPU 可跑最小流程；完整体验建议 GPU。

## 最小闭环：generate

```python
from vllm import LLM, SamplingParams

llm = LLM(model="facebook/opt-125m")

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=100)

outputs = llm.generate(prompts, sampling_params)
for out in outputs:
    prompt = out.prompt
    text = out.outputs[0].text
    print(f"Prompt: {prompt!r}\nGenerated: {text!r}\n")
```

关键点：

- `llm.generate(prompts, params)` 接受 prompt 列表，**一次调用完成批处理**——continuous batching 在引擎内部混合调度（F-034）。
- 返回 `RequestOutput`：`prompt`、`outputs`（每个含 `text`/`token_ids`/`cumulative_logprob` 等）、`finished` 标志（F-061）。

## 采样参数：SamplingParams

`SamplingParams`（`vllm/sampling_params.py`）是离线模式的调优面：

```python
sp = SamplingParams(
    temperature=0.7,        # 0 = greedy
    top_p=0.9,
    top_k=50,
    max_tokens=256,
    stop=["\n\n", "END"],   # 停止序列
    presence_penalty=0.1,
    frequency_penalty=0.1,
    n=2,                    # 每 prompt 采 n 个样本
    seed=42,                # 固定种子复现
)
```

- `n > 1` 时 `out.outputs` 含多个候选；`logprobs=5` 可返回 top-5 token 对数概率（F-061）。
- greedy（`temperature=0`）是可复现基线，压测与对比实验默认用它。

## chat 模式

对话模型用 `llm.chat()`，内部按模型 tokenizer 的 chat 模板拼装（F-062 的同源机制，在线侧见 [08 在线服务](../concepts/08-online-serving.md)）：

```python
from vllm import LLM

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain PagedAttention in one sentence."},
]
outputs = llm.chat(conversation, SamplingParams(max_tokens=128, temperature=0.7))
print(outputs[0].outputs[0].text)
```

## 量化加载（FP8）

Hopper/Ada 上直接加载官方 FP8 权重（方法细节见 [10 量化](../concepts/10-quantization.md)）：

```bash
vllm serve neuralmagic/Meta-Llama-3-8B-Instruct-FP8  # 服务模式
```

```python
llm = LLM(model="neuralmagic/Meta-Llama-3-8B-Instruct-FP8")  # 离线同理，quantization_config 自动识别
```

`--quantization` 缺省读模型目录的 `quantization_config`；显存不足时 INT4（GPTQ/AWQ）是更通用的选择（F-102）。

## 批处理与吞吐提示

- 把请求攒批后一次 `generate`，比逐条调用快一个量级——引擎的 continuous batching 按令牌预算组批（F-034）。
- 长文档场景开启 chunked prefill（v0.32 默认开）避免单条长 prompt 阻塞整批（F-019）。
- 大量重复前缀（如同一 system prompt）依赖 prefix caching 自动复用 KV（F-033）。

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 首条请求慢、后续快 | CUDA Graph 预热/编译 | 正常；`--enforce-eager` 可关图换启动速度 |
| 显存 OOM | 模型+KV 超限 | 降 `--gpu-memory-utilization`、用量化、加 TP |
| 输出被截断 | `max_tokens` 到顶 | 调大或设 `stop` |

## 相关阅读

- [02 OpenAI 兼容服务](02-openai-serving.md)：同一模型的在线模式
- [04 吞吐基准测试](04-benchmarking.md)：如何量化本示例的吞吐
- [03 架构总览](../concepts/03-architecture.md)：`llm.generate` 之下的引擎旅程
