---
type: concept
title: "整体架构概览"
description: "Coze Studio 整体架构：前后端分离、DDD 五层架构、双端代码生成、Eino Agent 运行时与 FlowGram 工作流引擎"
tags: [架构概览, DDD, Eino, FlowGram, 前后端分离]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-001
    resource: /references/backend-architecture.md
    title: "Coze Studio 全栈 AI Agent 开发平台"
  - id: F-cs-004
    resource: /references/backend-architecture.md
    title: "后端 Go + Hertz + DDD 架构"
  - id: F-cs-005
    resource: /references/frontend-architecture.md
    title: "前端 React 18 + TypeScript + Rush.js"
  - id: F-cs-009
    resource: /references/backend-architecture.md
    title: "Eino Agent/Workflow 运行时"
  - id: F-cs-010
    resource: /references/frontend-architecture.md
    title: "FlowGram 工作流编辑器引擎"
---

# 整体架构概览

Coze Studio 是一个开源的一站式 AI Agent 开发平台，源自字节跳动 Coze 平台，服务于数万企业和数百万开发者。平台采用前后端分离架构，后端基于 Go 语言和 Hertz HTTP 框架实现 DDD（领域驱动设计）分层架构，前端使用 React 18 + TypeScript 构建 Rush.js monorepo。Agent 与工作流运行时基于 Eino 框架，前端工作流编辑器基于 FlowGram 引擎。

## 系统全局视图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Frontend)                          │
│  React 18 + TypeScript + Semi Design + Tailwind CSS + Zustand  │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Agent IDE│  │ Workflow  │  │ Studio   │  │  Apps (主应用) │  │
│  │ (agent-  │  │ Editor    │  │ (studio) │  │ @coze-studio/ │  │
│  │  ide/)   │  │ (FlowGram)│  │          │  │     app       │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └──────────────┴─────────────┴────────────────┘          │
│                         │              ▲                        │
│                   arch/ (level-1)  common/ (level-2)           │
│              api-schema/bot-http/bot-store/i18n/idl/...         │
│                        │  idl2ts 代码生成 ▲                      │
└────────────────────────┼────────────────┼───────────────────────┘
                         │                │
                   HTTP/WebSocket    流式响应 (SSE)
                         │                │
┌────────────────────────┼────────────────┼───────────────────────┐
│                        ▼                │       后端 (Backend)   │
│  ┌──────────────────────────────────────┴────────────────────┐  │
│  │                     api/ 层 (Hertz)                        │  │
│  │   handler/coze/  │  middleware/ (7个)  │  router/  │ model/│  │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              application/ 层 (20+ 应用服务模块)            │   │
│  │  app │ user │ workflow │ knowledge │ plugin │ memory ...  │   │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            crossdomain/ 层 (契约接口层)                    │   │
│  │   contract.go 接口定义 + impl/ 实现，16个跨域模块          │   │
│  │   使用 Eino StreamReader/Message 进行跨域通信              │   │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              domain/ 层 (领域层)                          │   │
│  │  entity/ │ repository/ │ service/ │ dal/ (17个限界上下文)  │   │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              infra/ 层 (基础设施层)                        │   │
│  │  cache │ es │ eventbus │ orm │ storage │ embedding │ sse  │   │
│  │  MySQL │ Redis │ MinIO │ Milvus │ NSQ │ ES (可插拔)       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Agent 运行时: Eino v0.4.8 (StreamReader/Message 流式通信)       │
└──────────────────────────────────────────────────────────────────┘
```

## 核心架构特征

### 前后端分离

前端和后端是完全独立的工程：
- **后端**：Go 1.24+、Hertz v0.10.2 HTTP 框架、DDD 五层架构、Eino Agent 框架
- **前端**：React 18 + TypeScript 5.8、Rush.js 5.147.1 monorepo、Rsbuild 构建、Semi Design UI

开发时前端通过 dev proxy 将 `/api` 和 `/v1` 代理到 `http://localhost:8888` 后端服务。

### 双端代码生成

Coze Studio 使用 Thrift IDL 作为 API 契约的单一事实来源，通过代码生成同时产出前后端代码：
- **后端**：hz (Hertz code gen) v0.9.7 从 Thrift IDL 生成 Go 语言的 handler、model、router 代码
- **前端**：idl2ts 工具链从 Thrift IDL 生成 TypeScript 类型定义

这确保了前后端接口的一致性，避免了手动维护 API 类型带来的错误。i64 类型字段使用 `js_conv` 注解处理 JavaScript 大整数精度问题。

### 两大核心引擎

- **Eino 框架**（cloudwego/eino v0.4.8）：后端 Agent 和 Workflow 的运行时引擎，提供 `StreamReader` 流式读取和 `Message` 消息类型，支持 7 种模型集成扩展（ark、claude、deepseek、gemini、ollama、openai、qwen）
- **FlowGram 引擎**（@flowgram.ai）：前端工作流编辑器的可视化渲染引擎，workflow/ 包基于 FlowGram 构建节点编辑能力

### 可插拔基础设施

后端 infra/ 层设计为高度可插拔，通过工厂模式支持多种基础设施后端切换：
- 消息队列：NSQ（默认）、Kafka、RocketMQ、Pulsar、NATS JetStream
- 向量数据库：Milvus（默认）、VikingDB、OceanBase
- 对象存储：MinIO（默认）、TOS、S3
- 嵌入模型：Ark（默认）、OpenAI、Ollama、Gemini、自定义 HTTP
- LLM 协议：OpenAI、Ark、DeepSeek、Ollama、Qwen、Gemini

## 部署模式

Coze Studio 支持两种主要部署方式：

1. **Docker Compose 一键部署**（`make web`）：编排 11 个服务（MySQL、Redis、Elasticsearch、MinIO、etcd、Milvus、NSQ 三件套、后端服务、前端 nginx），最低 2 CPU 核、4GB 内存即可运行
2. **Helm Chart K8s 部署**：适用于生产环境，coze-server 通过 LoadBalancer 暴露服务，支持 MySQL/OceanBase 切换

## 技术栈版本

| 组件 | 版本/技术 |
|------|-----------|
| Go | >= 1.23.4（go.mod 声明 1.24.0） |
| Hertz | v0.10.2 |
| Eino | v0.4.8 |
| React | ~18.2.0 |
| TypeScript | ~5.8.2 |
| Rush.js | 5.147.1 |
| Rsbuild | ~1.1.0 |
| Node.js | lts/iron (20.x) / rush.json >=21 |
| License | Apache 2.0 |

## 相关概念

- [DDD 分层详解](01-ddd-layers.md)
- [Thrift IDL 与代码生成](02-thrift-idl-codegen.md)
- [认证与中间件](03-auth-middleware.md)
- [可插拔基础设施](04-pluggable-infrastructure.md)
