---
okf_version: "0.2"
type: index
title: "Coze Studio"
description: "Coze Studio 开源 AI Agent 开发平台 OKF 知识库 — DDD 后端架构、Rush.js 前端、Thrift IDL、可插拔基础设施与部署运维"
tags: [coze-studio, AI Agent, DDD, Go, React, Docker]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:15:00Z" }
status: stable
stale_after: 2027-08-23
---

# Coze Studio

**Coze Studio** 是开源的一站式 AI Agent 开发平台，源自字节跳动 Coze 平台，服务数万企业和数百万开发者。平台采用 Go + Hertz DDD 后端与 React 18 + Rush.js 前端架构，基于 Eino 框架运行 Agent/Workflow，通过 Thrift IDL 实现前后端双端代码生成，支持 Docker Compose 一键部署和 Helm K8s 部署。

- **License**: Apache 2.0
- **后端**: Go >= 1.23.4, Hertz v0.10.2, Eino v0.4.8
- **前端**: React 18, TypeScript 5.8, Rush.js 5.147.1, Rsbuild ~1.1.0
- **最低配置**: 2 CPU 核, 4GB 内存, Docker + Docker Compose

## 概念文档

理解 Coze Studio 的核心架构与设计理念。

### 架构核心

| 文档 | 说明 |
|------|------|
| [整体架构概览](/concepts/00-overview-ddd-architecture.md) | 前后端分离、DDD 五层、双端代码生成、Eino+FlowGram 引擎 |
| [DDD 分层架构详解](/concepts/01-ddd-layers.md) | api/application/crossdomain/domain/infra 五层职责与协作 |
| [Thrift IDL 与双端代码生成](/concepts/02-thrift-idl-codegen.md) | 契约优先开发、hz/idl2ts 代码生成、18 服务聚合 |
| [认证与中间件体系](/concepts/03-auth-middleware.md) | SessionAuthMW/AdminAuthMW 双层认证、7 中间件链 |
| [可插拔基础设施架构](/concepts/04-pluggable-infrastructure.md) | 工厂模式多后端、云端/私有部署适配 |

### 特性与运维

| 文档 | 说明 |
|------|------|
| [LLM 模型集成](/concepts/05-llm-integration.md) | Eino 框架、6 协议支持、序号后缀多模型配置 |
| [Rush.js Monorepo 前端架构](/concepts/06-rushjs-monorepo.md) | 四级包层次、Rsbuild 构建、Semi+Zustand 技术栈 |
| [工作流与智能体编辑器](/concepts/07-workflow-editor.md) | FlowGram 引擎、workflow/agent-ide 包结构 |
| [部署与运维](/concepts/08-deployment-operations.md) | Docker Compose、Helm K8s、Makefile、数据库迁移 |

## 实践示例

| 示例 | 说明 |
|------|------|
| [Docker Compose 快速入门](/examples/docker-quickstart.md) | 一键部署、环境准备、服务验证、首次注册 |
| [添加自定义 LLM 模型](/examples/add-llm-model.md) | Ollama 本地模型、OpenAI 兼容 API、多模型混合配置 |
| [配置基础设施后端](/examples/configure-infrastructure.md) | 切换向量库、存储、嵌入、MQ 等可插拔组件 |

## 技术参考

| 参考 | 说明 |
|------|------|
| [后端架构参考](/references/backend-architecture.md) | DDD 五层目录、路由注册、中间件、错误码、初始化顺序 |
| [前端架构参考](/references/frontend-architecture.md) | Rush.js 配置、四级包层次、20+ arch 包、Rsbuild |
| [IDL 与 API 契约参考](/references/idl-api-contracts.md) | Thrift IDL 组织、18 服务、Base/BaseResp、bigint 处理 |
| [部署与基础设施参考](/references/deployment-infrastructure.md) | 11 Docker 服务、270+ 环境变量、可插拔选项、Helm Chart |

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
