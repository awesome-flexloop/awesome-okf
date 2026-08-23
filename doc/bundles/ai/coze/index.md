---
type: category
title: "Coze 扣子开发平台生态"
okf_version: "0.2"
description: "Coze（扣子）开发平台生态源码级中文教程——3个核心知识束、46篇内容文档（含24概念+10示例+12信源），覆盖Python SDK、开源开发平台、LLM可观测性SDK"
total_bundles: 3
total_content_docs: 46
total_md_files: 63
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:15:00Z" }
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
status: stable
tags: [coze, AI-Agent, Python-SDK, observability, LLM]
stale_after: 2027-08-23
---

# Coze 扣子开发平台生态知识库

本知识包分组收录 [Coze（扣子）](https://www.coze.cn) 开发平台生态各核心项目的系统化中文源码教程。Coze 是字节跳动推出的一站式 AI Agent 开发平台，提供 Bot 构建、工作流编排、知识库、多模态能力、实时语音等完整的智能体开发工具链。

所有知识束遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，所有 API 引用均经 Grep 级源码验证。

## 📊 知识束概览

| 层次 | 知识束 | 概念 | 示例 | 信源 | 内容文档 |
|------|--------|------|------|------|---------|
| Python SDK | [coze-py](coze-py/index.md) | 10 | 4 | 5 | 19 |
| 开源平台 | [coze-studio](coze-studio/index.md) | 9 | 3 | 4 | 16 |
| 可观测性 | [cozeloop-python](cozeloop-python/index.md) | 5 | 3 | 3 | 11 |
| **合计** | **3 知识束** | **24** | **10** | **12** | **46** |

> 注："内容文档"指 concepts/examples/references 目录下的实质性文档（不含各目录 index.md 导航页）。含导航索引、日志文件共 **63 个 .md 文件**。

## SDK层：Python 客户端

| 知识束 | 简介 |
|--------|------|
| [coze-py](coze-py/index.md) | Coze 官方 Python SDK v0.20.0——同步/异步双客户端架构、懒加载服务组合、20个服务模块（Chat/Bots/Workflows/Conversations/WebSockets/Audio/Files/Datasets等）、SSE流式事件模型、WebSocket Build模式实时通信、三种分页策略、Token/JWT/OAuth四种认证、音频语音合成与识别 |

## 平台层：开源开发平台

| 知识束 | 简介 |
|--------|------|
| [coze-studio](coze-studio/index.md) | Coze Studio 开源版一站式 AI Agent 开发平台——Go+Hertz后端DDD五层架构（api/application/crossdomain/domain/infra）、React 18+Rush.js前端单仓库（四级包层次）、Thrift IDL双端代码生成（hz+idl2ts）、18个IDL服务聚合、可插拔基础设施（5种MQ/3种向量库/5种Embedding/6种LLM协议）、11服务Docker Compose一键部署、Eino Agent引擎+FlowGram工作流画布、Helm K8s生产部署 |

## 可观测性层：Tracing SDK

| 知识束 | 简介 |
|--------|------|
| [cozeloop-python](cozeloop-python/index.md) | CozeLoop LLM可观测性Python SDK——OpenTelemetry兼容的Trace/Span模型、三种埋点方式（装饰器/自动注入/手动Span）、ContextVar上下文传播、OpenAI/LangChain等框架零侵入集成、批量上报与采样配置 |

## 推荐学习路径

### 路径一：SDK 使用（快速上手 Coze API）
```
🐍 coze-py/00-overview-architecture（双客户端架构概览）
  → 🐍 coze-py/01-auth-system（认证体系）
    → 🐍 coze-py/02-client-init（客户端初始化）
      → 🐍 coze-py/examples/basic-chat（基础对话示例）
        → 🐍 coze-py/03-chat-streaming（流式对话深入）
```

### 路径二：平台部署（私有化搭建 Coze Studio）
```
🏗️ coze-studio/00-overview-ddd-architecture（架构概览）
  → 🏗️ coze-studio/08-deployment-operations（部署运维）
    → 🏗️ coze-studio/examples/docker-quickstart（Docker快速开始）
      → 🏗️ coze-studio/05-llm-integration（配置LLM模型）
        → 🏗️ coze-studio/04-pluggable-infrastructure（基础设施配置）
```

### 路径三：全栈理解（SDK+平台+可观测性）
```
🐍 coze-py（理解SDK如何与平台API交互）
  → 🏗️ coze-studio（理解平台服务端架构与API契约）
    → 🔍 cozeloop-python（为LLM应用添加可观测性）
```

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────────┐
│              🏗️ coze-studio（开源 AI Agent 开发平台）              │
│  Go+Hertz DDD后端 · React+Rush.js前端 · Thrift IDL契约           │
│  Eino Agent引擎 · FlowGram工作流画布 · 18个微服务API              │
│  可插拔基础设施(MQ/VectorDB/Storage/Embedding/LLM)               │
│  Docker Compose 11服务 · Helm K8s部署                           │
└────────────────────────┬─────────────────────────────────────────┘
                         │ REST API / WebSocket / SSE
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼──────────┐     ┌────────────▼─────────────────────┐
│ 🐍 coze-py         │     │ 🔍 cozeloop-python               │
│ Python SDK v0.20.0 │     │ LLM 可观测性 SDK                 │
│ 同步/异步双客户端   │     │ Span/Trace 埋点模型              │
│ 20个服务模块       │     │ 装饰器/自动注入/手动三种方式      │
│ SSE流式+WS实时通信 │     │ OpenAI/LangChain 零侵入集成      │
│ 4种认证+3种分页    │     │ 批量上报·ContextVar传播          │
└────────────────────┘     └──────────────────────────────────┘
```

## 信源与验证

- **源码根目录**：`external/libs/ai/coze-dev/`
- **子项目**：coze-py（Python SDK）、coze-studio（Go+React全栈平台）、cozeloop-python（可观测性SDK）、cozeloop-examples（示例代码，已整合入cozeloop-python）
- **生成方法**：source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）
- **方法论指导**：seven-concepts-cmd（R→I→E 知识沉淀）
- **API验证**：120条coze-py事实+125条coze-studio事实+110条cozeloop-python事实，共355条可验证源码事实
- **frontmatter**：63个文件YAML元数据完整
