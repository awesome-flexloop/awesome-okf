---
type: ExampleIndex
title: "Examples 索引：vLLM 四类典型场景"
description: "vLLM 实战示例集——离线批量推理、OpenAI 兼容在线服务、结构化输出与吞吐基准测试，覆盖 LLM 离线 API、vllm serve、guided decoding 与 benchmark_serving 四类高频用法"
tags: [vllm, examples, offline-inference, openai-serving, structured-output, benchmarking]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-quickstart
    resource: /references/source-map.md
    title: docs/getting_started/quickstart.md（本地检出）
---

# Examples 索引：vLLM 四类典型场景

本目录包含 vLLM v0.32.x 的实践示例，按「离线 → 在线 → 约束解码 → 压测」组织，覆盖四个最高频使用场景。所有命令与代码可在 v0.32.x 环境复现；模型以官方 quickstart 常用的 `facebook/opt-125m`（离线入门）与真实尺寸模型（在线/压测）为例。

## 示例列表

| 示例 | 场景 | 涵盖主题 |
|------|------|---------|
| [01 离线批量推理](01-offline-inference.md) | 离线 LLM 类 | `LLM().generate()`、`SamplingParams`、chat 模式、流式 print、FP8 量化加载 |
| [02 OpenAI 兼容服务](02-openai-serving.md) | `vllm serve` | 启动参数、`/v1/chat/completions` 客户端调用、`--api-key` 鉴权、chat 模板 |
| [03 结构化输出](03-structured-output.md) | guided decoding | `--structured-outputs-config`、`guided_json` 请求参数、四后端选择 |
| [04 吞吐基准测试](04-benchmarking.md) | `benchmark_serving` | 离线 benchmark + 在线压测、核心指标解读 |

## 按场景分类

### 入门闭环

- [01 离线批量推理](01-offline-inference.md)：从 `LLM` 类出发，跑通 install → generate → 采样参数调优的最小闭环，理解 offline 模式与 online 服务的分工。

### 服务化

- [02 OpenAI 兼容服务](02-openai-serving.md)：一条命令起 OpenAI 兼容服务，用官方 OpenAI SDK 直连，验证 API 面与鉴权。
- [03 结构化输出](03-structured-output.md)：在服务上开启 JSON schema 约束，演示 xgrammar 后端与请求级覆盖。

### 性能验证

- [04 吞吐基准测试](04-benchmarking.md)：用官方 benchmark 工具量化吞吐/延迟/首 token 时间，建立选型与调优的度量基线。

## 前置知识

建议先阅读：

- [01 快速开始](../concepts/01-quickstart.md)：安装与最小闭环
- [08 在线服务与 API](../concepts/08-online-serving.md)：API 面全谱
- [04 调度与批处理](../concepts/04-scheduling.md)：continuous batching 对吞吐的影响

## 运行环境

- vLLM v0.32.x（本地检出 v0.32.1rc0-283，2026-10-22）
- Python 3.11–3.14（本地 quickstart 口径；官网 3.10+）
- 至少一张 16GB+ 显存的 GPU（示例 02–04 建议 24GB+；小模型可用 CPU/Colab 变通）

```{toctree}
:maxdepth: 2

01-offline-inference
02-openai-serving
03-structured-output
04-benchmarking
```
