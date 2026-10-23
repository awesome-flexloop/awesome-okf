---
type: Concept
title: "进阶主题：PD 分离、结构化输出、LoRA、RL 与插件"
description: "vLLM 进阶面——Prefill/Decode 分离部署、结构化输出四后端（xgrammar/guidance/outlines/lm-format-enforcer）、LoRA 动态加载与多 LoRA、RL 训练接口（RLHF/async_rl/weight transfer）、io_processor/lora_resolver/endpoint 插件、Prometheus 可观测性与 Docker/K8s/Nginx 部署"
tags: [vllm, pd-disaggregation, structured-output, xgrammar, lora, rl, plugins, observability, deployment]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-advanced
    resource: /references/source-map.md
    title: vllm/v1/structured_output/、vllm/lora/、vllm/plugins/（本地检出）
  - id: website-deploy
    url: https://docs.vllm.ai/en/latest/deployment/
    title: Deployment Frameworks（官网文档）
---

# 进阶主题：PD 分离、结构化输出、LoRA、RL 与插件

这一页把 vLLM 的「第二梯队」能力集中起来：它们不改变核心架构，但在生产与训练场景里频繁用到。

## PD 分离（Prefill/Decode Disaggregation）

prefill（计算密集）与 decode（显存带宽密集）对硬件的诉求不同，PD 分离把两者拆到不同实例/节点，各自独立扩缩（F-141）。vLLM 的 PD 分离基于 KV cache 传输层（NIXL 等后端）在 prefill 实例与 decode 实例间搬移 KV block；v0.32 的官方文档与源码以 `vllm/v1/` 内的 KV 传输器承接（`vllm/distributed/kv_transfer/`）。适用场景：超长上下文、prefill 与 decode 负载比例悬殊的在线服务（F-142）。

## 结构化输出

`--structured-outputs-config` 选择后端，约束解码过程产生合法 JSON/schema：

| 后端 | 文件 | 特点 |
|------|------|------|
| xgrammar | `backend_xgrammar.py` | 默认推荐，编译为 mask，开销低 |
| guidance | `backend_guidance.py` | Guidance 生态 |
| outlines | `backend_outlines.py` | Outlines 生态 |
| lm-format-enforcer | `backend_lm_format_enforcer.py` | 轻量格式强制 |

```bash
vllm serve <model> --structured-outputs-config '{"backend": "xgrammar"}'
```

四后端在 `vllm/v1/structured_output/` 实现统一接口（`backend_types.py`），请求级参数为 `structured_outputs`（json/regex/choice/grammar/structural_tag；v0.12 起取代 guided_* 字段，F-143）。

## LoRA

`vllm/lora/` 提供 LoRA 全链路：`model_manager.py`/`worker_manager.py` 管理加载与分发，`punica_wrapper` 是 Punica 算法的打包内核（多 LoRA 批处理），`peft_helper.py` 对接 PEFT 生态（F-144）。在线服务可动态增删 LoRA 适配器（`/v1/load_lora_adapter`、`/v1/unload_lora_adapter`，见 [08 在线服务](08-online-serving.md)），无需重启。

## RL 与训练接口

vLLM 同时是 RLHF/在线 RL 的 rollout 引擎（docs/training/）：

- **RLHF**：`docs/training/rlhf.md`——奖励模型打分、拒绝采样等 rollouts 用法。
- **async_rl**：异步 RL 训练框架集成。
- **weight transfer**：训练侧权重与推理侧同步机制。
- 配套能力：`layerwise`（逐层流水）、`routed_experts`（MoE 路由记录）、`sampling_mask`、`prompt_token_id_logprobs`、`weight_checker`、`trl`（TRL 集成）（F-145）。

## 插件系统

`vllm/plugins/` 定义三类树外扩展点（F-136）：

| 目录 | 扩展点 |
|------|--------|
| `io_processors` | 自定义 I/O 处理（多模态输入预处理等） |
| `lora_resolvers` | 自定义 LoRA 适配器解析 |
| `endpoint_plugins` | 自定义 HTTP 端点 |

加上 [10 量化](10-quantization.md) 的 `@register_quantization_config` 与 [09 模型支持](09-model-support.md) 的模型注册，vLLM 的扩展面覆盖：模型、量化、I/O、LoRA、端点五类。

## 可观测性与部署

- **指标**：`vllm/v1/metrics/` 含 Prometheus 导出（`prometheus.py`）、日志器（`loggers.py`）、缓存命中来源统计（`cache_hit_source.py`）——prefix cache 命中率、投机解码接受率（见 [11](11-speculative-decoding.md)）均可观测。
- **部署**：docs/deployment/ 提供 Docker、K8s、Nginx 三种官方路径，另有 frameworks/integrations 收录 KServe、Ray Serve、SGLang Router 等生态集成。

## 相关阅读

- [08 在线服务与 API](08-online-serving.md)：LoRA 端点与结构化输出请求级参数
- [12 分布式推理](12-distributed.md)：PD 分离与多维并行的关系
- [03 架构总览](03-architecture.md)：各进阶能力挂接的引擎位置
