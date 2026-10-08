---
title: README 模块结构详述
type: reference
bundle: /datawhale/tiny-universe
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# 参考：README 模块结构详述

本页登记 README"主体部分""探索部分""项目结构"章节中各模块的描述与路径。

## 主体部分（8 个模块）

面向经典技术的从零实现，带领学习者深度掌握经典工作的实现细节。

| 序号 | 模块名 | README 描述 |
|------|--------|-------------|
| 1 | TinyDiffusion | 手写图像生成模型 |
| 2 | Qwen-Blog | 深入剖析大模型原理 |
| 3 | TinyLlama3 | 逐步预训练一个手搓大模型 |
| 4 | TinyEval | 如何评估你的大模型 |
| 5 | TinyRAG | 纯手工搭建 RAG 框架 |
| 6 | TinyAgent | 手搓一个最小的 Agent 系统 |
| 7 | TinyTransformer | 深入理解大模型基础 |
| 8 | TinyGraphRAG | 手搓一个基本的 GraphRAG 系统 |

## 探索部分（1 个模块）

面向新颖学术作品/生产阶段优秀作品的从零复现，带领学习者从"会做"走向"创新"。

| 序号 | 模块名 | README 描述 |
|------|--------|-------------|
| 1 | CDDRS (ADVEI25) | 使用细粒度语义元素指导增强的 RAG 检索方法 |

## 项目结构章节详述

### TinyGraphRAG（`./content/TinyGraphRAG/`）

- GraphRAG 将图结构与 LLM 结合，在复杂关系推理、知识关联检索中能力强大。
- 概念体系庞杂：图数据库、向量检索、图算法与 LLM 协同。
- 本项目手工搭建最简化 GraphRAG，从原理公式与架构图出发，对应图构建、检索、推理与生成代码。
- 帮助学习者理解数据准备、查询处理、生成整合的完整流程。
- 配图：`workflow.png`

### TinyDiffusion（`./content/TinyDiffusion/`）

- Diffusion 是当下最流行的图像生成模型，效果优秀、训练稳定。
- 公式原理复杂，从公式到代码的映射令人困惑。
- 手工搭建最简化 DDPM，从论文公式到训练与采样代码。
- 帮助理解原理，熟悉训练、推理、评估整套流程。
- 配图：`ddpm.png`

### Qwen-Blog（`./content/Qwen-blog/`）

- 初学者面对庞大代码与封装功能"谈码色变"。
- 以 Qwen2 为例，以输入 tensor 为第一视角，经过 Model 各操作块，点亮 LLM"黑匣子"。
- 包含 GQA、RoPE、Attention Mask 等机制的细致讲解。
- 有对应讲解视频。
- 配图：`framework.JPG`

### TinyRAG（`./content/TinyRAG/`）

- LLM 存在幻觉、信息过时、专业领域洞察不足、推理能力欠缺等问题。
- RAG 在生成前从文档库检索相关信息引导生成，提升准确性与相关性。
- 其他 RAG 项目基于封装框架，隐藏底层原理、难以魔改。
- 本项目抛弃封装框架，手搓从零开始的 RAG。
- 有讲解视频与 GPU 镜像。
- 配图：`RAG.png`

### TinyAgent（`./content/TinyAgent/`）

- 大模型在逻辑推理、现实事件、垂直领域存在薄弱环节。
- Agent 通过工具赋能，将 LLM 打造为能自主理解、规划决策、执行复杂任务的智能体。
- 基于 ReAct 方式手动制作最小 Agent 结构，重点是调用工具。
- 计划将 ReAct 改为 SOP 结构。
- 暂无录播，Datawhale 视频号可搜索。
- 配图：`React.png`

### TinyEval（`./content/TinyEval`）

- 微调后如何判断模型在数据集上的表现是待解决问题。
- 选择式、判别式、生成式任务需要不同的客观评价方法。
- 搭建完善的评测体系，帮助学习者量身定做评测指标。
- 有讲解视频。
- 选修内容：高考数学评测。
- 配图：`compass.png`

### TinyLLM（`./content/TinyLLM`）

- 实现简单大语言模型：训练 tokenizer → 训练模型 → 文本生成。
- 仅使用 NumPy 和 PyTorch。
- 显存 2G 左右，单显卡即可，训练数小时。
- 配图：`model_show.png`
- 注：主体部分中称为 TinyLlama3。

### TinyTransformer（`./content/TinyTransformer`）

- 所有 LLM 几乎都以 Transformer 的 Attention 机制为基础。
- 基于《Attention is All You Need》在 PyTorch 层手工搭建完整、可复现、可运行的 Transformer。
- 帮助打牢 LLM 基础。
