---
title: code-your-own-llm GitHub 仓库
type: reference
bundle: /datawhale/code-your-own-llm
description: Datawhale 出品的动手训练大语言模型全栈式参考指南，基于 nanochat 深度扩展，覆盖从数据到安全的完整 LLM 生命周期。
sources:
  - id: github-repo
    resource: https://github.com/datawhalechina/code-your-own-llm
    title: datawhalechina/code-your-own-llm GitHub 仓库
---

# code-your-own-llm GitHub 仓库

## 基本信息

- **仓库地址**：https://github.com/datawhalechina/code-your-own-llm
- **出品方**：Datawhale
- **在线阅读**：https://datawhalechina.github.io/code-your-own-llm/
- **当前版本**：Alpha 内测版
- **Python 要求**：3.10+
- **开源协议**：CC BY-NC-SA 4.0

## 仓库内容概述

该仓库是一份全栈式大语言模型参考指南，基于 Andrej Karpathy 的 [nanochat](https://github.com/karpathy/nanochat) 深度扩展。项目以最简洁的代码、扁平化结构和极简依赖，实现大语言模型从零训练到工程落地的完整流程。

## 核心文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目简介、章节结构预览、成员与致谢 |
| `AGENTS.md` | 第零章：格式模板和规范指南（所有 Markdown 文档的写作规范） |
| `docs/Chapter01/` ~ `docs/Chapter12/` | 各章内容目录 |
| `docs/Appendix/` | 附录：数学基础与前沿论文解读 |

## 章节完成状态

- ✅ 已完成：第1章引言、第2章环境配置、第3章数据、第5章模型架构、第8章有监督微调、第9章强化学习
- 🚧 在建中：第4章分词、第6章预训练、第7章中期训练、第10章模型推理、第11章模型评估、第12章模型安全与红队测试、附录

## 致谢项目

本项目受益于以下开源项目：

- [nanochat](https://github.com/karpathy/nanochat)
- [nanoGPT](https://github.com/karpathy/nanoGPT)
- [transformers](https://github.com/huggingface/transformers)
- [pytorch](https://github.com/pytorch/pytorch)
- [llms-from-scratch](https://github.com/rasbt/LLMs-from-scratch)
