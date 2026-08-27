---
okf_version: "0.2"
type: index
title: "Anthropic 提示词工程教程 Wiki"
description: "Anthropic官方9章提示词工程交互式教程中文整理——基础结构、清晰直接、角色分配、数据分离、格式化输出、思维链、示例使用、防幻觉、复杂提示词构建、链式提示与工具增强。"
tags: [prompt-engineering, prompts, few-shot, chain-of-thought, hallucination, xml-tags, role-prompting]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Anthropic 提示词工程教程 Wiki

**提示词工程（Prompt Engineering）** 是与 Claude 等大语言模型有效沟通的核心技能。本 Wiki 是 Anthropic 官方 9 章交互式提示词工程教程的中文结构化整理，聚焦 80/20 核心技巧——掌握 20% 的关键方法，解决 80% 的常见提示词失败模式。

本教程使用 Claude Haiku 模型教学，适合从入门到进阶的所有开发者。

## 课程特点

- **交互式学习**：源自 Anthropic 官方交互式教程，强调实践而非纯理论
- **9章+附录完整覆盖**：从基础结构到复杂Agent系统，循序渐进
- **Haiku模型教学**：用快速、低成本的Haiku模型学习技巧，所有技巧适用于全系列模型
- **80/20导向**：聚焦最高杠杆的核心技巧，不堆砌零散知识点
- **正反示例对比**：每个技巧都有"好vs坏"提示词对比，直观理解差异
- **失败模式诊断**：不仅讲怎么做，还讲常见错误和修复方法

## 学习路径

| 阶段 | 章节 | 主题 | 核心收获 |
|------|------|------|---------|
| **入门** | Ch1-3 | 基础结构 | 任务+上下文+约束公式、清晰直接、角色分配 |
| **中级** | Ch4-7 | 结构化技巧 | XML标签分离、格式化输出、思维链、Few-shot示例 |
| **高级** | Ch8-9 | 高可靠模式 | 防幻觉、复杂提示词构建（Chatbot/法律/金融/编程） |
| **附录** | 附录 | 系统级模式 | 链式提示、工具调用、RAG检索增强、Agent演进 |

### 📚 概念文档

| 文档 | 说明 |
|------|------|
| [概览与学习路径](concepts/00-overview.md) | 提示词工程是什么、Claude特点、课程目标、环境准备 |
| [基础结构（入门Ch1-3）](concepts/01-basic-structure.md) | 三要素公式、清晰直接原则、角色分配Persona、80/20总结 |
| [中级技巧（Ch4-7）](concepts/02-intermediate-techniques.md) | XML标签数据分离、格式化输出、思维链CoT、Few-shot示例 |
| [高级模式（Ch8-9）](concepts/03-advanced-patterns.md) | 防幻觉策略、Chatbot/法律/金融/编程提示词模板、迭代优化流程 |
| [进阶：链式提示与工具增强（附录）](concepts/04-beyond-standard.md) | 链式提示模式、Tool Use最佳实践、RAG检索、Agent演进路径 |

## 交叉链接

提示词工程不是孤立技能，与以下文档配合使用效果更佳：

### 与 Python SDK 配合
提示词最终要通过代码调用：
- [Python SDK 概览](/python-sdk/concepts/00-overview.md) — SDK 安装与初始化
- [消息基础](/python-sdk/concepts/02-messages-basics.md) — Messages API 基本用法（提示词放在哪里）
- [工具使用](/python-sdk/concepts/04-tool-use.md) — Function Calling 完整代码教程

### 与 Cookbook 配合
学习实战模式：
- [工具使用模式](/cookbooks/concepts/01-tool-use-patterns.md) — 工具调用的常见设计模式
- [RAG 模式](/cookbooks/concepts/03-rag-patterns.md) — 检索增强生成的提示词与架构
- [高级技巧](/cookbooks/concepts/04-advanced-techniques.md) — 更多高级提示词模式

### 相关产品
- [Claude Code Wiki](/claude-code/) — Anthropic 终端编码Agent，观察提示词工程在产品中的应用

## 更新日志

完整变更记录见 [log.md](log.md)。

```{toctree}
:maxdepth: 2

concepts/index
log
```
