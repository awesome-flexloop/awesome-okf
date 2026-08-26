---
title: 大模型白盒子构建指南
type: index
bundle: tiny-universe
description: Datawhale 出品的"白盒"导向大模型全链路手搓指南，从 PyTorch 层从零实现 Transformer、LLM、Diffusion、RAG、GraphRAG、Agent 与 Eval 等核心模块，帮助学习者脱离封装框架理解大模型原理。
concepts:
  - /datawhale/tiny-universe/concepts/white-box-philosophy
  - /datawhale/tiny-universe/concepts/tiny-diffusion
  - /datawhale/tiny-universe/concepts/tiny-rag
  - /datawhale/tiny-universe/concepts/tiny-agent
  - /datawhale/tiny-universe/concepts/tiny-llm
references:
  - /datawhale/tiny-universe/references/readme-overview
  - /datawhale/tiny-universe/references/readme-modules
  - /datawhale/tiny-universe/references/readme-news
examples:
  - /datawhale/tiny-universe/examples/module-roadmap
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# 大模型白盒子构建指南（tiny-universe）

tiny-universe 是 Datawhale 发起的开源学习项目，以"白盒"为导向，围绕大模型全链路提供从零手搓的代码与教程。项目覆盖模型基础（Transformer）、模型训练（TinyLLM/TinyLlama3、TinyDiffusion）、检索增强（TinyRAG、TinyGraphRAG）、智能体（TinyAgent）与评估体系（TinyEval），所有实现尽量下沉到 PyTorch/NumPy 层，避免高度封装框架对原理的遮蔽。

## 核心理念

- **从零手搓**：从论文公式直接映射到代码，不依赖 LangChain 等封装框架。
- **最小可运行**：每个模块控制在个人学习者可复现的资源规模（2G 显存、数小时训练）。
- **全栈覆盖**：Model → RAG → Agent → Eval，形成完整能力闭环。

详见 [白盒构建理念](/ai/datawhale/tiny-universe/concepts/white-box-philosophy)。

## 模块地图

项目主体部分包含八个经典技术从零实现模块：

1. [TinyDiffusion](/ai/datawhale/tiny-universe/concepts/tiny-diffusion) — 手写 DDPM 图像生成模型
2. Qwen-Blog — 以 Qwen2 为例解剖 LLM 内部结构（GQA、RoPE、Attention Mask）
3. TinyLlama3 — 逐步预训练手搓大模型（2G 显存）
4. TinyEval — 大模型评测体系（含高考数学评测）
5. [TinyRAG](/ai/datawhale/tiny-universe/concepts/tiny-rag) — 纯手工搭建 RAG 框架
6. [TinyAgent](/ai/datawhale/tiny-universe/concepts/tiny-agent) — 基于 ReAct 的最小 Agent 系统
7. TinyTransformer — 基于《Attention is All You Need》手工搭建 Transformer
8. TinyGraphRAG — 手搓基本 GraphRAG 系统（图构建/检索/推理/生成）

探索部分包含 CDDRS (ADVEI25) 等前沿学术作品复现。

完整模块清单与事实记录见 [spec/facts.md](spec/facts.md)。

## 推荐阅读路径

- **初学者**：TinyTransformer → Qwen-Blog → TinyLLM
- **应用方向**：TinyRAG → TinyGraphRAG → TinyAgent → TinyEval
- **生成模型方向**：TinyDiffusion → TinyLLM
- **教学者**：先读 [白盒构建理念](/ai/datawhale/tiny-universe/concepts/white-box-philosophy) 与 [洞察笔记](spec/insights.md)

## 参考资料

- [项目总览与意义](/ai/datawhale/tiny-universe/references/readme-overview)
- [模块结构详述](/ai/datawhale/tiny-universe/references/readme-modules)
- [发布时间线](/ai/datawhale/tiny-universe/references/readme-news)
- [模块路线图示例](/ai/datawhale/tiny-universe/examples/module-roadmap)

```{toctree}
:maxdepth: 7

concepts/tiny-agent
concepts/tiny-diffusion
concepts/tiny-llm
concepts/tiny-rag
concepts/white-box-philosophy
examples/module-roadmap
references/readme-modules
references/readme-news
references/readme-overview
spec/facts
spec/insights
log
```
