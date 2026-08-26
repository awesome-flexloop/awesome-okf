---
okf_version: "0.2"
type: group-index
title: "🤖 AgnesAI 大模型生态"
description: "AgnesAI全模态AI平台OKF知识包索引——多模态大模型API、Agent框架、垂直研究项目"
total_bundles: 2
completed_bundles: 2
groups: "AgnesAI生态"
---

# 🤖 AgnesAI 大模型生态

> **Agnes AI** 是一家专注于全模态基础模型的前沿AI公司，提供文本对话、图像生成、视频生成、Agent工具调用等多模态AI能力，通过OpenAI兼容的统一API网关对外开放服务。本分组收录AgnesAI生态相关的OKF知识包。

---

## 生态全景

```
┌──────────────────────────────────────────────────────────────┐
│                🤖 AgnesAI 大模型生态                          │
├──────────────────────────────────────────────────────────────┤
│  🎯 API服务层                                                 │
│  └─ agnes-ai-models/  统一API网关（OpenAI兼容）✅ 已完成      │
│     ├─ 文本模型：agnes-2.5-flash / agnes-2.0-flash            │
│     ├─ 图像模型：agnes-image-2.1-flash / agnes-image-2.0-flash│
│     └─ 视频模型：agnes-video-v2.0                             │
├──────────────────────────────────────────────────────────────┤
│  🖥️ 产品与工具层                                               │
│  ├─ AgnesCode/          桌面端AI工作台（未开源，待补充）       │
│  └─ ...更多产品待补充                                         │
├──────────────────────────────────────────────────────────────┤
│  🧪 研究与框架层                                               │
│  ├─ GodeAgents/        多Agent系统框架 ✅ 已完成               │
│  ├─ DEAL-SQL/          Text-to-SQL持续学习（论文+代码）       │
│  ├─ DSPO/              模型对齐优化（arXiv论文）              │
│  ├─ AskRAG-Bench/      RAG基准测试                            │
│  └─ AIGC/              AIGC内容生成研究                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 知识包清单

| 知识包 | 状态 | 简介 |
|--------|------|------|
| [agnes-ai-models](agnes-ai-models/index.md) | ✅ stable | AgnesAI统一API网关教程——OpenAI兼容接口、对话/图像/视频生成、工具调用、速率限制、错误处理、生产最佳实践。共17个文档（8概念+5示例+2信源+索引） |
| [gode-agents](gode-agents/index.md) | ✅ stable | GodeAgents (codified-smolagents v1.14.0) 编码式多智能体推理框架教程——双智能体范式（ToolCallingAgent/CodeAgent）、工具系统、8种模型后端、AST安全Python执行器、多智能体协作。共35个文档（15概念+7示例+7信源+4索引+facts/insights） |
| deal-sql | 📋 planned | DEAL-SQL: 多方言Text-to-SQL持续学习框架（NeurIPS 2026论文） |
| dspo | 📋 planned | DSPO: 大模型对齐优化方法（arXiv:2510.09255） |
| agnes-code | 📋 planned | AgnesCode桌面工作台产品文档（无源码，待官方开放文档后补充） |

---

## 快速开始

**第一次使用AgnesAI API？** 推荐学习路径：

```
1. 📖 [AgnesAI 简介](agnes-ai-models/concepts/00-introduction.md)（10分钟）
   ↓
2. 🚀 [5分钟快速开始](agnes-ai-models/concepts/01-getting-started.md)（5分钟跑通第一个调用）
   ↓
3. 🔑 [API认证与安全](agnes-ai-models/concepts/02-api-authentication.md)（了解密钥管理）
   ↓
4. 💬 [对话补全API](agnes-ai-models/concepts/03-chat-completions.md) → 🎨 [图像生成](agnes-ai-models/concepts/04-image-generation.md) → 🎬 [视频生成](agnes-ai-models/concepts/05-video-generation.md)
   ↓
5. ⚙️ 生产环境：[速率限制](agnes-ai-models/concepts/06-rate-limits.md) → [错误处理](agnes-ai-models/concepts/07-error-handling.md)
   ↓
6. 💻 动手实践：examples/ 目录下5个可运行示例
```

**要构建Agent应用？** 学习完基础API后，直接看 [Agent工具调用工作流示例](agnes-ai-models/examples/agent-workflow.md)。

**要深入多智能体框架？** 学习 [GodeAgents 教程](gode-agents/index.md)：
```
1. 📖 [GodeAgents 简介](gode-agents/concepts/00-introduction.md) → [快速开始](gode-agents/concepts/01-getting-started.md)
   ↓
2. 🤖 [第一个 ToolCallingAgent](gode-agents/examples/01-first-agent.md) → [CodeAgent 代码执行](gode-agents/examples/02-code-agent-basic.md)
   ↓
3. 🏗️ 核心架构：[MultiStepAgent](gode-agents/concepts/03-multi-step-agent.md) → [记忆系统](gode-agents/concepts/04-memory-system.md)
   ↓
4. 🔧 两种范式：[ToolCallingAgent](gode-agents/concepts/05-tool-calling-agent.md) vs [CodeAgent](gode-agents/concepts/06-code-agent.md)
   ↓
5. 🛠️ 工具开发：[工具系统](gode-agents/concepts/07-tool-system.md) → [@tool自定义工具](gode-agents/examples/03-custom-tool.md)
   ↓
6. 🚀 高级：[多智能体协作](gode-agents/examples/07-multi-agent-collab.md) → [Plan-and-Execute](gode-agents/examples/06-planning-interval.md)
```

---

## 核心模型速查表

| 模型 | 类型 | 上下文 | 核心能力 | 推荐场景 |
|------|------|--------|---------|---------|
| `agnes-2.5-flash` | 文本/视觉 | 512K | 编码、推理、工具调用、图像理解 | Agent系统、编码助手、复杂工作流 ✅ 推荐 |
| `agnes-2.0-flash` | 文本/视觉 | 256K | 对话、工具调用、流式输出 | 稳定生产环境、通用对话 |
| `agnes-1.5-flash` | 文本/视觉 | 256K | 快速响应、低延迟 | 高吞吐聊天、简单任务 |
| `agnes-image-2.1-flash` | 图像 | - | 文生图、图生图、灵活尺寸 | 创意设计、营销素材、图像编辑 ✅ 推荐 |
| `agnes-image-2.0-flash` | 图像 | - | 快速文生图 | 快速图像生成 |
| `agnes-video-v2.0` | 视频 | - | 文生视频、图生视频、异步 | 短视频制作、产品演示 |

---

## 版本信息

- 初始知识包生成日期：2026-08-22
- 基于官方文档版本：2026.07.30
- API Base URL：`https://apihub.agnes-ai.com/v1`
- 官方站点：https://agnes-ai.com/（国际）/ https://agnes-ai.cn/（中国）
- API平台：https://platform.agnes-ai.com/

```{toctree}
:maxdepth: 7

agnes-ai-models/index
gode-agents/index
```
