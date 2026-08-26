# 概念文档

Coze Studio 核心架构与设计概念文档。

## 架构核心

- [整体架构概览](/concepts/00-overview-ddd-architecture.md) — 前后端分离、DDD 五层、双端代码生成、Eino+FlowGram 引擎
- [DDD 分层架构详解](/concepts/01-ddd-layers.md) — api/application/crossdomain/domain/infra 五层职责与协作
- [Thrift IDL 与双端代码生成](/concepts/02-thrift-idl-codegen.md) — 契约优先开发、hz/idl2ts 代码生成、18 服务聚合
- [认证与中间件体系](/concepts/03-auth-middleware.md) — SessionAuthMW/AdminAuthMW 双层认证、7 中间件链
- [可插拔基础设施架构](/concepts/04-pluggable-infrastructure.md) — 工厂模式多后端、云端/私有部署适配

## 特性与运维

- [LLM 模型集成](/concepts/05-llm-integration.md) — Eino 框架、6 协议支持、序号后缀多模型配置
- [Rush.js Monorepo 前端架构](/concepts/06-rushjs-monorepo.md) — 四级包层次、Rsbuild 构建、Semi+Zustand 技术栈
- [工作流与智能体编辑器](/concepts/07-workflow-editor.md) — FlowGram 引擎、workflow/agent-ide 包结构
- [部署与运维](/concepts/08-deployment-operations.md) — Docker Compose、Helm K8s、Makefile、数据库迁移

```{toctree}
:maxdepth: 7

00-overview-ddd-architecture
01-ddd-layers
02-thrift-idl-codegen
03-auth-middleware
04-pluggable-infrastructure
05-llm-integration
06-rushjs-monorepo
07-workflow-editor
08-deployment-operations
```
