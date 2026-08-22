---
type: concept
title: "Thrift IDL 与双端代码生成"
description: "Coze Studio 基于 Thrift IDL 的 API 契约体系、hz 后端代码生成、idl2ts 前端代码生成与 18 个服务聚合机制"
tags: [Thrift, IDL, 代码生成, hz, idl2ts, API契约]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-071
    resource: /references/idl-api-contracts.md
    title: "Thrift IDL 12 个子目录"
  - id: F-cs-072
    resource: /references/idl-api-contracts.md
    title: "api.thrift 聚合 18 个服务"
  - id: F-cs-078
    resource: /references/idl-api-contracts.md
    title: "BigInt js_conv 处理"
---

# Thrift IDL 与双端代码生成

Coze Studio 使用 Apache Thrift 作为接口定义语言（IDL），建立前后端之间的 API 契约。所有 API 接口首先在 `.thrift` 文件中定义，然后通过代码生成工具同时产出后端 Go 代码和前端 TypeScript 代码。这种"契约优先"的开发模式确保了前后端接口的一致性，极大减少了因类型不匹配导致的联调问题。

## IDL 目录组织

Thrift IDL 文件位于项目根目录的 `idl/` 目录下，按业务领域组织为 12 个子目录：

```
idl/
├── admin/           # 管理配置服务
├── app/             # 应用/智能体/项目（含 bot_common、developer_api、publish 等 8 个文件）
├── conversation/    # 会话/消息/智能体运行（agentrun_service、message_service 等）
├── data/            # 数据层
│   ├── database/    # 数据库服务
│   ├── knowledge/   # 知识库（文档处理、切片、审核）
│   └── variable/    # 变量与 KV 记忆
├── marketplace/     # 市场服务
├── passport/        # 认证（邮箱/密码注册登录）
├── permission/      # 权限与 OpenAPI 认证
├── playground/      # 调试场与提示词资源
├── plugin/          # 插件开发
├── resource/        # 资源管理
├── upload/          # 文件上传
├── workflow/        # 工作流与追踪
├── api.thrift       # 🔑 服务聚合入口
└── base.thrift       # 🔑 基础类型定义
```

每个领域目录内包含多个 `.thrift` 文件，定义该领域的请求/响应结构体、异常和服务接口。例如 `idl/data/knowledge/` 包含 `common.thrift`、`document.thrift`、`knowledge.thrift`、`knowledge_svc.thrift`、`review.thrift`、`slice.thrift` 六个文件，完整覆盖知识库的文档上传、解析、切片、索引、审核全流程。

## api.thrift — 服务聚合

`idl/api.thrift` 是所有服务的聚合入口。它通过 Thrift 的 `include` 指令引入各领域的 thrift 文件，然后使用 service extends 语法将 18 个独立服务聚合为一个统一的 API 服务：

```thrift
// 伪代码示意结构
include "app/intelligence.thrift"
include "conversation/conversation_service.thrift"
include "conversation/message_service.thrift"
// ... 更多 include

service CozeService
  extends IntelligenceService
  extends ConversationService
  extends MessageService
  extends AgentRunService
  extends OpenAPIAuthService
  extends MemoryService
  extends PluginDevelopService
  extends PublicProductService
  extends DeveloperApiService
  extends PlaygroundService
  extends DatabaseService
  extends ResourceService
  extends PassportService
  extends WorkflowService
  extends KnowledgeService
  extends BotOpenApiService
  extends UploadService
  extends ConfigService
{}
```

这 18 个服务覆盖了 Coze Studio 的全部 API 能力：

| 服务 | 职责领域 |
|------|----------|
| IntelligenceService | 智能对话与推理 |
| ConversationService / MessageService | 会话与消息管理 |
| AgentRunService | 智能体运行时 |
| PassportService | 用户认证（注册/登录/登出） |
| WorkflowService / KnowledgeService | 工作流与知识库 |
| PluginDevelopService / BotOpenApiService | 插件开发与开放 API |
| UploadService / ResourceService | 文件上传与资源管理 |
| MemoryService / DatabaseService | 记忆与数据库 |
| ConfigService / PlaygroundService | 配置与调试 |
| DeveloperApiService / PublicProductService / OpenAPIAuthService | 开发者 API 与开放认证 |

## base.thrift — 基础类型体系

`idl/base.thrift` 定义了所有 API 共用的基础结构体，构成了 Coze Studio API 的统一通信协议。

### 请求/响应元数据

```thrift
struct Base {
    1: optional string LogID        // 请求追踪 ID
    2: optional string Caller       // 调用方标识
    3: optional string Addr         // 客户端地址
    4: optional string Client       // 客户端类型
    5: optional string TrafficEnv   // 流量环境
    255: optional map<string, string> Extra  // 扩展字段
}

struct BaseResp {
    1: optional string StatusMessage  // 状态消息
    2: optional i32 StatusCode        // 状态码
    255: optional map<string, string> Extra
}
```

### 空类型与 RPC 包装

```thrift
struct EmptyReq {}
struct EmptyData {}
struct EmptyResp {}

// RPC 请求/响应自动包装 Base/BaseResp 到 field 255
struct EmptyRpcReq { 255: optional Base base }
struct EmptyRpcResp { 255: optional BaseResp base_resp }
```

Thrift 的 field 编号约定：业务字段从 1 开始编号，框架元数据使用高位编号（253=code, 254=msg, 255=Base/BaseResp），避免与业务字段冲突。

### 响应约定

所有 API 响应遵循统一约定：
- **field 253**：`code`（i32 类型状态码）
- **field 254**：`msg`（string 类型状态消息）

### 跨语言命名空间

```thrift
namespace py base
namespace go base/coze/passport
namespace java com.bytedance.thrift.base
```

## BigInt 精度处理

Thrift 的 `i64` 类型在 Go 中映射为 `int64`，可以精确表示大整数。但 JavaScript 的 `number` 类型只能安全表示 2^53 以内的整数，超过此范围的 i64（如用户 ID `user_id`）会丢失精度。

Coze Studio 使用 Thrift 注解解决此问题：

```thrift
struct User {
    1: required i64 user_id (agw.js_conv="str", api.js_conv="true")
}
```

`agw.js_conv="str"` 和 `api.js_conv="true"` 注解告知代码生成器和 API 网关：在序列化为 JSON 时，将该 i64 字段转为字符串类型。前端 idl2ts 生成的 TypeScript 类型中，`user_id` 将被定义为 `string` 而非 `number`，从根本上避免大整数精度丢失。

## 后端代码生成：hz

后端使用 Hertz 框架官方代码生成工具 **hz v0.9.7**，从 Thrift IDL 生成三类代码：

```bash
# hz 生成配置（.hz 文件）
handlerDir=api/handler
modelDir=api/model
routerDir=api/router
```

生成产物：
- **api/model/**：请求/响应 Go 结构体，对应 Thrift struct 定义
- **api/handler/coze/**：handler 骨架代码，开发者在其中填充业务逻辑
- **api/router/coze/**：路由注册代码（`api.go` 1761 行），自动注册所有服务端点

路由注册文件 `api/router/register.go` 除了注册 hz 生成的 API 路由外，还注册静态文件路由。Handler 文件与 18 个服务一一对应，如 `conversation_service.go`、`workflow_service.go`、`knowledge_service.go` 等。

## 前端代码生成：idl2ts

前端使用自研的 **idl2ts 工具链**（6 个包）从 Thrift IDL 生成 TypeScript 代码：

| 工具包 | 职责 |
|--------|------|
| `idl-parser` | 解析 Thrift IDL 语法，构建 AST |
| `idl2ts-generator` | 核心生成逻辑，AST → TS 代码 |
| `idl2ts-cli` | 命令行入口 |
| `idl2ts-helper` | 生成辅助函数 |
| `idl2ts-plugin` | 插件系统，支持自定义生成逻辑 |
| `idl2ts-runtime` | 运行时库，提供序列化/反序列化 |

生成的 TypeScript 类型确保前端调用 API 时获得完整的类型提示和编译期检查，与后端 Go 结构体保持严格一致。

## 认证 IDL 示例

Passport 服务展示了完整的 IDL 定义模式：

```thrift
// passport/passport.thrift 中定义的核心方法
PassportWebEmailRegisterV2Post  // 邮箱注册
PassportWebEmailLoginPost        // 邮箱登录
PassportWebLogoutGet             // 登出
// 以及密码重置、账户信息、头像更新等
```

## 相关概念

- [整体架构概览](/concepts/00-overview-ddd-architecture.md)
- [DDD 分层详解](/concepts/01-ddd-layers.md)
- [认证与中间件](/concepts/03-auth-middleware.md)
- [IDL 与 API 契约参考](/references/idl-api-contracts.md)
