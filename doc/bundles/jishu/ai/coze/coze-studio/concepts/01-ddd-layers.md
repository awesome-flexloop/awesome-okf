---
type: concept
title: "DDD 分层架构详解"
description: "Coze Studio 后端 DDD 五层架构：api 接口层、application 应用层、crossdomain 契约层、domain 领域层、infra 基础设施层的职责与协作"
tags: [DDD, 分层架构, 领域驱动设计, Go, Hertz]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-013
    resource: /references/backend-architecture.md
    title: "DDD 五层目录结构"
  - id: F-cs-014
    resource: /references/backend-architecture.md
    title: "api 层目录结构"
  - id: F-cs-015
    resource: /references/backend-architecture.md
    title: "application 层 20+ 模块"
  - id: F-cs-019
    resource: /references/backend-architecture.md
    title: "crossdomain 层 16 模块"
---

# DDD 分层架构详解

Coze Studio 后端采用严格的 DDD（领域驱动设计）五层架构，层与层之间遵循依赖倒置原则：上层依赖下层的抽象，而非具体实现。五个层次从外到内依次是 api（接口层）、application（应用层）、crossdomain（跨域契约层）、domain（领域层）和 infra（基础设施层）。其中 crossdomain 层是 Coze Studio 在经典 DDD 四层架构基础上的创新，专门用于定义跨限界上下文的通信契约。

## 五层架构图

```
                         ┌─────────────────────┐
                         │     HTTP Request    │
                         └──────────┬──────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        api/ 层 (接口层)                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────┐  ┌───────────────┐  │
│  │ handler/ │  │  middleware/  │  │model/ │  │   router/     │  │
│  │  (coze/) │  │ (7个中间件)   │  │(hz生成)│  │ (1761行路由)  │  │
│  └────┬─────┘  └──────┬───────┘  └───────┘  └───────────────┘  │
│       └───────────────┼────────────────────────────────────────┘
└───────────────────────┼─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  application/ 层 (应用服务层)                    │
│  编排业务流程，协调多个领域对象完成用例                           │
│  ┌─────┬──────┬──────────┬─────────┬──────┬────────┬────────┐   │
│  │app  │ user │workflow  │knowledge│plugin│memory  │single- │   │
│  │     │      │          │         │      │        │agent   │   │
│  └─────┴──────┴──────────┴─────────┴──────┴────────┴────────┘   │
│  20+ 模块: connector/conversation/modelmgr/openauth/permission  │
│           prompt/search/shortcutcmd/template/upload/base        │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼  通过接口调用
┌─────────────────────────────────────────────────────────────────┐
│                crossdomain/ 层 (跨域契约层)                      │
│  定义跨限界上下文通信的接口契约（contract.go）                    │
│  ┌────────┬─────────┬──────────┬─────────┬──────────────────┐   │
│  │ agent  │agentrun │   app    │connector│  conversation    │   │
│  │contract│ contract│ contract │contract │   contract       │   │
│  ├────────┼─────────┼──────────┼─────────┼──────────────────┤   │
│  │database│datacopy │knowledge │ message │  permission      │   │
│  │plugin  │ search  │  upload  │  user   │  variables/workflow │
│  └────────┴─────────┴──────────┴─────────┴──────────────────┘   │
│  通信类型: Eino StreamReader / Message (流式)                    │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼  通过 impl/ 实现
┌─────────────────────────────────────────────────────────────────┐
│                    domain/ 层 (领域层)                          │
│  核心业务逻辑，每个限界上下文独立自治                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  限界上下文 (17个):                                      │    │
│  │  agent/singleagent │ app │ connector │ conversation     │    │
│  │  datacopy │ knowledge │ memory(database/variables)      │    │
│  │  openauth │ permission │ plugin │ prompt │ search       │    │
│  │  shortcutcmd │ template │ upload │ user │ workflow      │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  每个上下文内部结构:                                      │    │
│  │  entity/        → 领域实体 (充血模型)                     │    │
│  │  repository/    → 仓储接口                               │    │
│  │  service/       → 领域服务                               │    │
│  │  internal/dal/  → 数据访问层 (gen.go + query/)           │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼  依赖倒置，通过接口调用
┌─────────────────────────────────────────────────────────────────┐
│                    infra/ 层 (基础设施层)                        │
│  技术实现细节，可插拔组件                                        │
│  ┌──────┬──────┬──────────┬─────┬──────────┬──────────┐        │
│  │cache │check-│coderunner│ doc │ dynconf  │embedding │        │
│  │      │point │          │(ocr/│          │          │        │
│  │      │      │          │nl2sql│         │          │        │
│  │      │      │          │parse)│         │          │        │
│  ├──────┼──────┼──────────┼─────┼──────────┼──────────┤        │
│  │ es   │event-│  idgen   │imagex│oceanbase │  orm     │        │
│  │(ES7/8│bus   │          │     │          │(GORM)    │        │
│  ├──────┼──────┼──────────┼─────┼──────────┼──────────┤        │
│  │ rdb  │sql-  │   sse    │storage(MinIO/  │          │        │
│  │      │parser│          │  TOS/S3)       │          │        │
│  └──────┴──────┴──────────┴────────────────┴──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## api/ 层 — 接口适配层

api 层负责 HTTP 协议的适配，将外部 HTTP 请求转换为内部应用服务调用。该层包含四个子目录：

- **handler/coze/**：请求处理器，接收 HTTP 请求、参数校验、调用应用服务、构造响应。`base.go` 提供 `invalidParam` 和 `internalError` 等基础响应函数
- **middleware/**：7 个中间件组成处理链（host → i18n → log → session/openapi_auth → request_inspector → ctx_cache）
- **model/**：由 hz 工具从 Thrift IDL 自动生成的请求/响应结构体
- **router/**：由 hz 生成的路由注册代码，`api.go`（1761 行）定义了 `/api/conversation`、`/api/workflow`、`/api/knowledge`、`/api/passport` 等所有 API 路由

路由注册在 `register.go` 中完成，包括 hz 生成的 API 路由和静态文件路由。

## application/ 层 — 应用服务层

应用层是业务用例的编排者，负责协调多个领域对象完成一个完整的业务流程。它不包含业务规则，而是组织和委托领域层来完成工作。

Coze Studio 的 application 层包含 20+ 应用服务模块：

| 模块 | 职责 |
|------|------|
| `app` | 项目创建/更新/删除/发布/复制（1443 行，最大模块） |
| `user` | 用户注册、登录、登出、资料更新、会话验证 |
| `workflow` | 工作流编排管理 |
| `knowledge` | 知识库管理 |
| `plugin` | 插件开发与认证 |
| `memory` | 记忆管理（database/variables） |
| `singleagent` | 单智能体管理 |
| `connector` | 连接器管理 |
| `conversation` | 会话管理 |
| `modelmgr` | 模型管理 |
| `openauth` | OAuth 认证 |
| `permission` | 权限控制 |
| `prompt` | 提示词管理 |
| `search` | 搜索服务 |
| `template` | 模板管理 |
| `upload` | 文件上传 |
| `base` | 基础服务 |

初始化顺序遵循依赖关系：先基础服务（infra、eventbus、modelMgr、connector、user、prompt、template、openAuth、upload、permission），再主服务，最后复杂服务。初始化末尾设置 crossdomain 的默认实现。

## crossdomain/ 层 — 跨域契约层

crossdomain 是 Coze Studio 架构中一个独特的层次，用于解决跨限界上下文通信的问题。在经典 DDD 中，跨域通信通常通过领域事件或应用服务直接调用来实现，但这会导致层与层之间的紧耦合。

crossdomain 层的设计：
- 每个跨域模块定义 `contract.go` 接口文件，声明该领域对外暴露的能力
- `impl/` 子目录包含接口的具体实现
- 跨域通信使用 `cloudwego/eino/schema` 的 `StreamReader` 和 `Message` 类型，天然支持流式数据传输
- 共 16 个跨域模块：agent、agentrun、app、connector、conversation、database、datacopy、knowledge、message、permission、plugin、search、upload、user、variables、workflow

以 SingleAgent 为例，`crossdomain/agent/contract.go` 定义了三个核心方法：
- `StreamExecute`：流式执行智能体
- `ObtainAgentByIdentity`：按身份标识获取智能体
- `GetSingleAgentDraft`：获取智能体草稿

## domain/ 层 — 领域核心层

领域层是业务逻辑的核心，包含所有业务规则和领域概念。每个限界上下文（Bounded Context）是一个独立的业务边界，内部按照标准结构组织：

- **entity/**：领域实体，如 App 实体包含 `APP` 和 `PublishRecord` 结构体；User 实体包含 `session`、`space`、`user` 结构体
- **repository/**：仓储接口，定义数据持久化的抽象
- **service/**：领域服务，包含不适合放在实体中的业务逻辑
- **internal/dal/**：数据访问层，通过 GORM gen 生成查询代码（`gen.go` + `query/`）

17 个限界上下文覆盖了 Coze Studio 的全部业务领域：智能体（agent/singleagent）、应用（app）、连接器（connector）、会话（conversation，含 agentrun/conversation/message）、数据复制（datacopy）、知识库（knowledge）、记忆（memory，含 database/variables）、开放认证（openauth）、权限（permission）、插件（plugin）、提示词（prompt）、搜索（search）、快捷命令（shortcutcmd）、模板（template）、上传（upload）、用户（user）、工作流（workflow）。

## infra/ 层 — 基础设施层

基础设施层提供技术能力的实现，包括数据持久化、缓存、消息队列、搜索引擎、对象存储等。这一层的设计高度可插拔，通过工厂模式支持多种后端：

| 模块 | 功能 | 可选后端 |
|------|------|----------|
| `orm` | 数据库 ORM | GORM + MySQL/SQLite |
| `cache` | 缓存 | Redis |
| `es` | 搜索引擎 | ES7/ES8 双版本 |
| `eventbus` | 消息队列 | NSQ/Kafka/RocketMQ/Pulsar/NATS |
| `storage` | 对象存储 | MinIO/TOS/S3 |
| `embedding` | 向量嵌入 | Ark/OpenAI/Ollama/Gemini/HTTP |
| `sse` | 服务端推送 | Hertz SSE |
| `checkpoint` | 检查点 | 内存/Redis |

## 辅助包

除了五层核心架构，后端还有三个辅助包：

- **bizpkg/**：业务相关工具包（config/ 配置管理、llm/modelbuilder/ 模型构建器、fileutil/ 文件工具含 pyutil）
- **pkg/**：通用工具包（ctxcache、errorx、safego、sonic、i18n、logs、lang/ 语言基础库等 18 个子包）
- **types/**：类型定义（consts/ 常量、errno/ 模块错误码、ddl/ 数据定义）

其中 `safego` 提供带 panic 恢复的安全 goroutine 启动方法，`errorx` 提供带错误码和堆栈追踪的 `StatusError` 接口。

## 相关概念

- [整体架构概览](00-overview-ddd-architecture.md)
- [Thrift IDL 与代码生成](02-thrift-idl-codegen.md)
- [认证与中间件](03-auth-middleware.md)
- [可插拔基础设施](04-pluggable-infrastructure.md)
- [后端架构参考](../references/backend-architecture.md)
