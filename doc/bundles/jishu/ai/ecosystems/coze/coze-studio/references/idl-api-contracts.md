---
type: reference
title: "IDL 与 API 契约参考"
description: "Coze Studio Thrift IDL 组织方式、18 个服务聚合、Base/BaseResp 模式、bigint 处理与各领域 IDL 结构参考"
tags: [IDL, Thrift, API, 代码生成, hz, idl2ts]
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
---

# IDL 与 API 契约参考

## IDL 目录组织

Thrift IDL 文件位于 `idl/` 目录下，按领域分为 12 个子目录：

```
idl/
├── admin/           # 管理配置
├── app/             # 应用/项目/智能体
├── conversation/    # 会话/消息/运行
├── data/            # 数据（数据库/知识库/变量）
├── marketplace/     # 市场
├── passport/        # 认证
├── permission/      # 权限
├── playground/      # 调试场
├── plugin/          # 插件
├── resource/        # 资源
├── upload/          # 上传
├── workflow/        # 工作流
├── api.thrift       # 服务聚合入口
└── base.thrift      # 基础类型定义
```

## api.thrift 服务聚合

`api.thrift` 通过 include 引入各领域 thrift 文件，service 使用 extends 聚合 **18 个服务**：

| 服务名 | 说明 | 对应 Handler 文件 |
|--------|------|-------------------|
| IntelligenceService | 智能服务 | `intelligence_service.go` |
| ConversationService | 会话服务 | `conversation_service.go` |
| MessageService | 消息服务 | `message_service.go` |
| AgentRunService | 智能体运行服务 | `agent_run_service.go` |
| OpenAPIAuthService | OpenAPI 认证服务 | `open_apiauth_service.go` |
| MemoryService | 记忆服务 | `memory_service.go` |
| PluginDevelopService | 插件开发服务 | — |
| PublicProductService | 公共产品服务 | — |
| DeveloperApiService | 开发者 API 服务 | `developer_api_service.go` |
| PlaygroundService | 调试场服务 | `playground_service.go` |
| DatabaseService | 数据库服务 | `database_service.go` |
| ResourceService | 资源服务 | `resource_service.go` |
| PassportService | 认证服务 | `passport_service.go` |
| WorkflowService | 工作流服务 | `workflow_service.go` |
| KnowledgeService | 知识库服务（→DatasetService） | `knowledge_service.go` |
| BotOpenApiService | Bot OpenAPI 服务 | `bot_open_api_service.go` |
| UploadService | 上传服务 | `upload_service.go` |
| ConfigService | 配置服务 | `config_service.go` |

## base.thrift 基础类型

### Base 结构体

```thrift
struct Base {
    1: optional string LogID
    2: optional string Caller
    3: optional string Addr
    4: optional string Client
    5: optional string TrafficEnv
    255: optional map<string, string> Extra
}
```

### BaseResp 结构体

```thrift
struct BaseResp {
    1: optional string StatusMessage
    2: optional i32 StatusCode
    255: optional map<string, string> Extra
}
```

### 空请求/响应

| 类型 | 说明 |
|------|------|
| `EmptyReq` | 空请求 |
| `EmptyData` | 空数据 |
| `EmptyResp` | 空响应 |
| `EmptyRpcReq` | 空 RPC 请求（含 optional Base field 255） |
| `EmptyRpcResp` | 空 RPC 响应（含 optional BaseResp field 255） |

### Thrift 命名空间

```
py base
go base/coze/passport
java com.bytedance.thrift.base
```

## 响应约定

- **field 253**：`code`（i32，状态码）
- **field 254**：`msg`（string，状态消息）

## BigInt 处理

由于 JavaScript 中 number 类型精度限制，i64 类型的用户 ID 使用 `js_conv` 注解确保在前端正确转为字符串：

```thrift
struct User {
    1: required i64 user_id (agw.js_conv="str", api.js_conv="true")
}
```

## 各领域 IDL 详情

### app/ 应用领域

| 文件 | 说明 |
|------|------|
| `bot_common.thrift` | Bot 公共结构 |
| `bot_open_api.thrift` | Bot OpenAPI |
| `developer_api.thrift` | 开发者 API |
| `intelligence.thrift` | 智能服务 |
| `project.thrift` | 项目管理 |
| `publish.thrift` | 发布管理 |
| `search.thrift` | 搜索 |
| `task.thrift` | 任务管理 |
| `common_struct/` | 公共结构体 |

### conversation/ 会话领域

| 文件 | 说明 |
|------|------|
| `agentrun_service.thrift` | 智能体运行服务 |
| `common.thrift` | 公共结构 |
| `conversation.thrift` | 会话定义 |
| `conversation_service.thrift` | 会话服务 |
| `message.thrift` | 消息定义 |
| `message_service.thrift` | 消息服务 |
| `run.thrift` | 运行定义 |

### data/ 数据领域

#### data/database/ 数据库

| 文件 | 说明 |
|------|------|
| `database_svc.thrift` | 数据库服务 |
| `table.thrift` | 表结构定义 |

#### data/knowledge/ 知识库

| 文件 | 说明 |
|------|------|
| `common.thrift` | 公共结构 |
| `document.thrift` | 文档处理 |
| `knowledge.thrift` | 知识库定义 |
| `knowledge_svc.thrift` | 知识库服务 |
| `review.thrift` | 审核 |
| `slice.thrift` | 切片 |

#### data/variable/ 变量

| 文件 | 说明 |
|------|------|
| `kvmemory.thrift` | KV 记忆 |
| `project_memory.thrift` | 项目记忆 |
| `variable_svc.thrift` | 变量服务 |

### passport/ 认证领域

支持邮箱/密码认证：
- **注册**：`PassportWebEmailRegisterV2Post`
- **登录**：`PassportWebEmailLoginPost`
- **登出**：`PassportWebLogoutGet`
- 密码重置
- 账户信息查询
- 头像更新

### workflow/ 工作流领域

| 文件 | 说明 |
|------|------|
| `workflow.thrift` | 工作流定义 |
| `workflow_svc.thrift` | 工作流服务 |
| `trace.thrift` | 追踪定义 |

## 代码生成

双端代码生成基于同一份 Thrift IDL：

| 方向 | 工具 | 输出 |
|------|------|------|
| 后端（Go） | hz (Hertz code gen) v0.9.7 | `api/handler/`、`api/model/`、`api/router/` |
| 前端（TypeScript） | idl2ts 工具链 | 各 packages 中的 TypeScript 类型 |
