---
type: Example
title: "示例 04：吞吐与延迟基准测试（vllm bench）"
description: "用 vllm bench 量化 vLLM 性能——bench serve/throughput/latency/sweep 子命令、ShareGPT/Random/Spec-Bench 等数据集、TTFT/TPOT/吞吐指标解读与参数扫描调优，附 GuideLLM 生产压测建议
tags: [vllm, example, benchmarking, vllm-bench, throughput, latency, ttft, sharegpt, guidellm]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-bench
    resource: /references/source-map.md
    title: vllm/entrypoints/cli/benchmark/ 与 docs/benchmarking/（本地检出）
---

# 示例 04：吞吐与延迟基准测试（vllm bench）

没有度量的优化是盲调。vLLM 自带 `vllm bench` 工具族（`vllm/entrypoints/cli/benchmark/`），覆盖离线吞吐、在线服务压测、单请求延迟与参数扫描四类基准（F-147）。

## 工具族总览

| 子命令 | 源码文件 | 测什么 |
|--------|---------|--------|
| `vllm bench serve` | `benchmark/serve.py` | 在线服务端到端压测（原 `benchmark_serving.py`） |
| `vllm bench throughput` | `benchmark/throughput.py` | 离线批量吞吐 |
| `vllm bench latency` | `benchmark/latency.py` | 单请求/批量延迟 |
| `vllm bench sweep` | `benchmark/sweep.py` | 多配置自动扫描 |
| `vllm bench startup` | `benchmark/startup.py` | 启动时间分解 |

注：`vllm bench serve` 在开启 `VLLM_USE_RUST_BENCH` 时会委托给 Rust 版 CLI（F-148），行为兼容。

## 在线压测：bench serve

先起服务（见 [02 OpenAI 兼容服务](02-openai-serving.md)），再压测：

```bash
# ShareGPT 真实对话分布
wget https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json

vllm bench serve \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --dataset-name sharegpt \
  --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
  --num-prompts 500 \
  --request-rate 10 \
  --max-concurrency 64
```

常用数据集（docs/benchmarking/cli.md 口径）：`sharegpt`（真实对话）、`random`（合成，控制输入/输出长度）、`spec-bench`（投机解码专用，需下载 question.jsonl）、`burstgpt`（突发流量）、多模态 `sharegpt4v`/`random-mm` 等。

核心输出指标：

| 指标 | 含义 | 关注点 |
|------|------|--------|
| **TTFT** | 首 token 时间（Time To First Token） | 交互体验；prefill 主导 |
| **TPOT** | 每输出 token 时间 | 流式速度；decode 主导 |
| **吞吐**（output tok/s） | 系统总产出 | 容量规划 |
| **P50/P99 延迟** | 分位延迟 | 尾部体验 |

## 离线吞吐：bench throughput

```bash
vllm bench throughput \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --dataset-name random \
  --input-len 1024 \
  --output-len 128 \
  --num-prompts 1000
```

输出请求吞吐 + token 吞吐，适合快速对比量化、并行度、投机解码等配置的相对收益（实验对照见 [10 量化](../concepts/10-quantization.md)、[11 投机解码](../concepts/11-speculative-decoding.md)、[12 分布式](../concepts/12-distributed.md)）。

## 参数扫描：bench sweep

```bash
vllm bench sweep serve \
  --serve-cmd "vllm serve $MODEL --max-model-len {max_model_len}" \
  --bench-cmd "vllm bench serve --model $MODEL --num-prompts 200" \
  --max-model-len 4096 8192 16384
```

花括号占位符自动枚举组合，结果落盘对比——「优化与调优」的官方推荐姿势（docs/benchmarking/sweeps.md）。

## 生产压测：GuideLLM

官方明确建议：**生产级压测用 GuideLLM**（vllm-project/guidellm），它在 `vllm bench serve` 之上提供实时进度、自动报告、更灵活的数据集与负载模式（F-150）。`vllm bench` 更适合特性验证与回归测试。

## 建立度量基线

任何调优前后各跑一轮，固定条件：同数据集、同 `--num-prompts`、同并发、greedy 采样。对比时至少看三个数：TTFT P50、output tok/s、P99 延迟——只看平均吞吐会掩盖尾部恶化。

## 相关阅读

- [01 离线批量推理](01-offline-inference.md)：被测的离线模式
- [04 调度与批处理](../concepts/04-scheduling.md)：continuous batching 与指标的关系
- [07 配置体系](../concepts/07-configuration.md)：被扫描的常用参数
