---
type: concept
title: "LLM 模型集成"
description: "Coze Studio 基于 Eino 框架的 LLM 集成体系、6 种协议支持、序号后缀多模型配置与模型构建器"
tags: [LLM, Eino, 模型集成, ChatModel, 多模型]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-009
    resource: /references/backend-architecture.md
    title: "Eino 框架 v0.4.8"
  - id: F-cs-122
    resource: /references/deployment-infrastructure.md
    title: "7 个 Eino 模型扩展"
---

# LLM 模型集成

Coze Studio 使用 cloudwego/eino v0.4.8 作为 Agent 和 Workflow 运行时的底层 LLM 框架。Eino 是 CloudWeGo 开源的 Go 语言大模型应用开发框架，提供统一的模型抽象、流式通信原语和组件编排能力。Coze Studio 通过 Eino 扩展支持 6 种 ChatModel 协议和 7 种模型集成，配合序号后缀配置模式实现多模型管理。

## Eino 框架在架构中的位置

```
┌───────────────────────────────────────────────────────┐
│                  应用层 (application/)                 │
│   SingleAgent StreamExecute │ Workflow 编排            │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────┐
│              crossdomain/ 契约层                       │
│   StreamReader │ Message 类型 (eino/schema)            │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────┐
│                  Eino 框架 v0.4.8                      │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐  │
│  │ChatModel│ │ Callback │ │ Stream  │ │ Component  │  │
│  │  抽象   │ │  机制    │ │  原语   │ │  编排      │  │
│  └────┬────┘ └──────────┘ └─────────┘ └────────────┘  │
│       │                                                │
│  ┌────┴─────────────────────────────────────────────┐  │
│  │           Eino Extensions (7个)                   │  │
│  │  ark │ claude │ deepseek │ gemini │ ollama │     │  │
│  │  openai │ qwen                                    │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

Eino 的 `schema.StreamReader` 和 `schema.Message` 类型是跨域通信的基础数据结构。`StreamReader` 支持流式数据读取，是 Agent 流式输出的底层机制。在 crossdomain 层的 SingleAgent 契约中，`StreamExecute` 方法返回 `schema.StreamReader[*schema.Message]` 类型的流式结果。

## 支持的 ChatModel 协议

ChatModel 支持 6 种协议：

| 协议 | 标识 | 适用场景 | Eino 扩展 |
|------|------|----------|-----------|
| **OpenAI** | `openai` | OpenAI API 兼容服务 | eino-ext/openai |
| **Ark** | `ark` | 火山引擎方舟大模型平台 | eino-ext/ark |
| **DeepSeek** | `deepseek` | DeepSeek 模型 | eino-ext/deepseek |
| **Ollama** | `ollama` | 本地 Ollama 模型 | eino-ext/ollama |
| **Qwen** | `qwen` | 阿里通义千问 | eino-ext/qwen |
| **Gemini** | `gemini` | Google Gemini | eino-ext/gemini |

此外 Eino 扩展还包含 **Claude**（`eino-ext/claude`）集成，可用于 Anthropic Claude 模型。所有协议在 `bizpkg/llm/modelbuilder/` 中通过模型构建器统一管理。

## 序号后缀配置模式

采用序号后缀模式配置多个 LLM 模型，每组相同序号的环境变量定义一个模型：

```bash
MODEL_PROTOCOL_0=openai
MODEL_ID_0=gpt-4o
MODEL_API_KEY_0=sk-xxxxxxxxxxxxxxxx
MODEL_NAME_0=GPT-4o
MODEL_BASE_URL_0=https://api.openai.com/v1

MODEL_PROTOCOL_1=ollama
MODEL_ID_1=llama3
MODEL_API_KEY_1=
MODEL_NAME_1=Llama3 Local
MODEL_BASE_URL_1=http://localhost:11434/v1
```

配置从序号 `0` 开始递增，系统按序号依次加载。优势包括：多模型并存、模型选择灵活、配置简洁、热扩展。

| 变量 | 说明 |
|------|------|
| `MODEL_PROTOCOL_N` | 模型协议标识（openai/ark/deepseek/ollama/qwen/gemini） |
| `MODEL_ID_N` | 模型 ID（如 gpt-4o、ep-xxx、llama3） |
| `MODEL_API_KEY_N` | API 密钥（本地 Ollama 可留空） |
| `MODEL_NAME_N` | 模型显示名称（UI 展示） |
| `MODEL_BASE_URL_N` | API 基础 URL（支持自定义端点） |

## 流式通信与 SSE

LLM 流式输出通过 Eino 的 `StreamReader` 实现，后端通过 SSE（Server-Sent Events）将流式响应推送给前端。`infra/sse/` 模块封装了 SSE 通信能力，`infra/sse/impl/sse/` 提供基于 Hertz SSE 中间件的实现。

## 本地开发配置（Ollama）

```bash
# 安装启动 Ollama 后拉取模型
ollama pull llama3

# .env 配置（Docker 中访问宿主机需用 host.docker.internal）
MODEL_PROTOCOL_0=ollama
MODEL_ID_0=llama3
MODEL_API_KEY_0=
MODEL_NAME_0=Llama3 8B Local
MODEL_BASE_URL_0=http://host.docker.internal:11434/v1
```

## 相关概念

- [整体架构概览](00-overview-ddd-architecture.md)
- [可插拔基础设施](04-pluggable-infrastructure.md)
- [添加 LLM 模型示例](../examples/add-llm-model.md)
- [部署与运维](08-deployment-operations.md)
