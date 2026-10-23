---
type: Concept
title: "模型支持：架构注册表与 Transformers 后端"
description: "vLLM 模型接入机制——ModelRegistry 分类注册表（121 文本生成/124 多模态/33 embedding/65 投机解码/3 reward）、model-impl 选择、Transformers modeling backend 兜底、自定义模型接入路径与任务类型（生成/池化/嵌入/跨编码器/奖励）"
tags: [vllm, model-registry, transformers-backend, custom-model, multimodal, embedding, model-support]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-registry
    resource: /references/source-map.md
    title: vllm/model_executor/models/registry.py（本地检出）
  - id: website-models
    url: https://docs.vllm.ai/en/latest/models/supported_models/
    title: Supported Models（官网文档）
---

# 模型支持：架构注册表与 Transformers 后端

vLLM 对模型的接入靠**一张分类注册表 + 一个兜底后端**：注册表按「架构」登记（不是按模型），未登记的 Transformers 模型可由 modeling backend 直接跑起来。这决定了「你的模型能不能用 vLLM」以及「以什么代价用」。

## 架构注册表

注册表在 `vllm/model_executor/models/registry.py`，按任务类型分字典登记，用 `@_ModelRegistry.register_model` 装饰器把 `architectures` 字段映射到具体实现类（F-080）。本地检出（2026-10-22）的计数：

| 分类 | 注册表变量 | 架构数 | 说明 |
|------|-----------|--------|------|
| 文本生成 | `_TEXT_GENERATION_MODELS` | 121 | CausalLM 类，主力 |
| 多模态 | `_MULTIMODAL_MODELS` | 124 | VLM/音频类 |
| 投机解码 | `_SPECULATIVE_DECODING_MODELS` | 65 | 可作 draft/aux 的架构 |
| Embedding | `_EMBEDDING_MODELS` | 33 | 池化模型 |
| Reward | `_REWARD_MODELS` | 3 | 奖励模型（RLHF） |

合计 346 条**架构**（F-081）。注意这与官网口径 "200+ model architectures"（docs/models/supported_models.md）并不矛盾——官网数字是**可运行**架构的对外表述，且统计时点不同（F-082）。

## model-impl 与 Transformers 后端

`--model-impl` 选择模型实现后端，v0.32 默认 `auto`：注册表命中走 vLLM 原生实现，未命中则回退到 **Transformers modeling backend**（F-083）。该后端位于 `vllm/model_executor/models/transformers/`（`causal.py`、`moe.py`、`multimodal.py`、`pooling.py` 等），官方口径其性能与专用 vLLM 实现**一致**（docs/models/supported_models.md），代价是首次加载稍慢、部分融合算子不可用（F-084）。

判断当前加载走的是哪条路：

```python
from vllm import LLM
llm = LLM(model="...")
print(llm.llm_engine.vllm_config.model_config.model_impl)  # 'vllm' 或 'transformers'
```

## 自定义模型接入

三条路径，成本递增：

1. **注册表路径**：在 `vllm/model_executor/models/` 新增实现类，`@_ModelRegistry.register_model("XxxForCausalLM")` 装饰——适合新架构的长期支持（F-085）。
2. **Transformers 路径**：HuggingFace 模型若遵循自定义模型规范（`vllm_config` 参数传递、`weights` 加载约定），无需改 vLLM 代码即可跑（F-086）。
3. **外挂插件**：树外模型通过插件机制注册，避免 fork vLLM。

## 任务类型与 API 面

不同任务类型对应不同注册表字典与不同服务端点：

| 任务 | 入口 | 服务端点 |
|------|------|---------|
| 文本生成 | `LLM(...).generate()` | `/v1/completions`、`/v1/chat/completions` |
| 池化/嵌入 | `LLM(task="embed")` 等 | `/v1/embeddings` |
| 奖励/分类 | pooling 任务 | `/v1/score`、`/v1/classification` |
| 多模态 | 注册表 `_MULTIMODAL_MODELS` | chat completions 传 image/video/audio |

详见 [08 在线服务与 API](08-online-serving.md) 与 [13 进阶主题](13-advanced.md)（LoRA 动态加载）。

## 选型建议

- **新开源模型**：先查注册表是否命中；命中即最优路径，未命中先试 `--model-impl transformers` 兜底，再决定是否贡献原生实现。
- **自研模型**：优先按 Transformers 自定义模型规范改造，接入成本最低。
- **生产环境**：确认 `model_config.model_impl == 'vllm'`，原生实现才享受全部融合算子与 CUDA Graph 优化（F-084）。

## 相关阅读

- [03 架构总览](03-architecture.md)：模型运行器如何加载这些架构
- [10 量化](10-quantization.md)：量化与模型实现的交互
- [11 投机解码](11-speculative-decoding.md)：`_SPECULATIVE_DECODING_MODELS` 的用途
