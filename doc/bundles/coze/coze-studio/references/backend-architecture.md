---
type: reference
title: "后端架构参考"
description: "Coze Studio 后端 DDD 五层架构、路由注册、中间件链、错误码体系与初始化顺序的完整技术参考"
tags: [后端, DDD, Hertz, 中间件, Go]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-011
    resource: /references/backend-architecture.md
    title: "后端 DDD 五层架构"
  - id: F-cs-012
    resource: /references/backend-architecture.md
    title: "HTTP 框架 Hertz v0.10.2"
  - id: F-cs-013
    resource: /references/backend-architecture.md
    title: "DDD 五层目录结构"
---

# 后端架构参考

## 启动入口

后端入口文件为 `backend/main.go`，启动顺序为：

1. `setCrashOutput()` — 设置崩溃输出
2. `loadEnv()` — 加载环境变量
3. `setLogLevel()` — 设置日志级别
4. `application.Init` — 初始化应用
5. `startHttpServer` — 启动 HTTP 服务器

HTTP 框架使用 **cloudwego/hertz v0.10.2**，代码由 hz (Hertz code gen tool) v0.9.7 生成，生成配置为：
- `handlerDir=api/handler`
- `modelDir=api/model`
- `routerDir=api/router`

构建脚本 `backend/build.sh` 为 Hertz 标准构建脚本，编译输出到 `output/bin/hertz_service`。

## DDD 五层架构

```
backend/
├── api/              # 接口层
│   ├── handler/coze/ # 请求处理器
│   ├── middleware/    # 中间件
│   ├── model/         # 请求/响应模型（hz 生成）
│   └── router/        # 路由注册（hz 生成）
├── application/       # 应用层（20+ 模块编排）
├── domain/            # 领域层（限界上下文）
├── infra/             # 基础设施层（可插拔组件）
├── crossdomain/       # 跨域契约层（接口 + 实现）
├── bizpkg/            # 业务包（配置、LLM、文件工具）
├── pkg/               # 通用工具包
└── types/             # 类型定义（常量、错误码、DDL）
```

### api/ 层

| 子目录 | 说明 |
|--------|------|
| `handler/coze/` | 请求处理器，含 `base.go` 基础处理器 |
| `middleware/` | 7 个中间件 |
| `model/` | hz 生成的请求/响应结构体 |
| `router/` | 路由注册，`register.go` 注册生成路由和静态文件路由 |

路由注册文件 `api/router/coze/api.go` 共 1761 行，定义的主要 API 路由组：

| 路由前缀 | 说明 |
|----------|------|
| `/api/conversation` | 会话管理 |
| `/api/draftbot` | 智能体草稿 |
| `/api/knowledge` | 知识库 |
| `/api/workflow` | 工作流 |
| `/api/passport` | 认证登录 |
| `/api/playground` | 调试游乐场 |
| `/api/resource` | 资源管理 |
| `/api/upload` | 文件上传 |
| `/api/plugin` | 插件管理 |
| `/api/config` | 配置管理 |
| `/api/memory` | 记忆管理 |

### application/ 层

包含 20+ 应用服务模块：

`app`, `connector`, `conversation`, `knowledge`, `memory`, `modelmgr`, `openauth`, `permission`, `plugin`, `prompt`, `search`, `shortcutcmd`, `singleagent`, `template`, `upload`, `user`, `workflow`, `base`

- App 应用服务（1443 行）：项目创建/更新/删除/发布/复制
- User 应用服务：注册、登录、登出、更新资料、验证会话

初始化顺序（`application.go`）：
1. **基础服务**：infra → eventbus → modelMgr → connector → user → prompt → template → openAuth → upload → permission
2. **主服务**
3. **复杂服务**
4. 设置 crossdomain 默认实现

### domain/ 层

每个限界上下文包含 `entity/`、`repository/`、`service/`、`internal/dal/`（含 `gen.go` 和 `query/`）。

限界上下文列表：

`agent/singleagent`, `app`, `connector`, `conversation`（agentrun/conversation/message）, `datacopy`, `knowledge`, `memory`（database/variables）, `openauth`, `permission`, `plugin`, `prompt`, `search`, `shortcutcmd`, `template`, `upload`, `user`, `workflow`

核心实体：
- **App 实体**：APP、PublishRecord 结构体
- **User 实体**：session、space、user 结构体

### infra/ 层

可插拔基础设施模块：

| 模块 | 说明 |
|------|------|
| `cache` | 缓存 |
| `checkpoint` | 检查点（mem/redis） |
| `coderunner` | 代码运行器 |
| `document` | 文档处理（messages2query/nl2sql/ocr/parser/progressbar/rerank/searchstore） |
| `dynconf` | 动态配置 |
| `embedding` | 向量嵌入 |
| `es` | Elasticsearch（支持 ES7/ES8 双版本） |
| `eventbus` | 事件总线 |
| `idgen` | ID 生成 |
| `imagex` | 图片处理 |
| `oceanbase` | OceanBase 数据库 |
| `orm` | ORM（GORM，MySQL/SQLite） |
| `rdb` | 关系数据库 |
| `sqlparser` | SQL 解析器 |
| `sse` | Server-Sent Events |
| `storage` | 对象存储（S3/TOS/MinIO） |

### crossdomain/ 层

每个领域包含 `contract.go` 接口定义和 `impl/` 实现，共 16 个模块：

`agent`, `agentrun`, `app`, `connector`, `conversation`, `database`, `datacopy`, `knowledge`, `message`, `permission`, `plugin`, `search`, `upload`, `user`, `variables`, `workflow`

`crossdomain/agent/contract.go` 定义 SingleAgent 接口：
- `StreamExecute` — 流式执行
- `ObtainAgentByIdentity` — 按身份获取智能体
- `GetSingleAgentDraft` — 获取智能体草稿

跨域通信使用 `cloudwego/eino/schema` 的 `StreamReader` 和 `Message` 类型。

## 中间件链

共 7 个中间件：

| 中间件文件 | 功能 |
|------------|------|
| `host.go` | 注入请求 Host 和 Scheme 到上下文 |
| `i18n.go` | 从请求头或参数提取语言，i18n 国际化 |
| `log.go` | 记录访问日志，设置 LogID 到上下文 |
| `session.go` | Session 认证（SessionAuthMW） |
| `openapi_auth.go` | OpenAPI 认证 |
| `request_inspector.go` | 请求检查 |
| `ctx_cache.go` | 上下文缓存 |

### SessionAuthMW

- 通过 `SessionKey` Cookie 验证会话
- 白名单路径（无需认证）：
  - `/api/passport/web/email/login/`
  - `/api/passport/web/email/register/v2/`

### AdminAuthMW

- 通过 `AdminEmails` 配置验证管理员
- 配置来源：`baseConf.AdminEmails` 或环境变量 `ALLOW_REGISTRATION_EMAIL`

## 错误码体系

- 使用 `code.Register()` 注册错误码
- 支持 `WithAffectStability(bool)` 标记是否影响稳定性
- `errorx` 包提供 `StatusError` 接口，包含错误码、键值参数、堆栈追踪
- 每个模块有独立错误码文件（`types/errno/` 下）：
  `agent.go`, `app.go`, `connector.go`, `conversation.go`, `knowledge.go`, `memory.go`, `modelmgr.go`, `permission.go`, `plugin.go`, `prompt.go`, `search.go`, `shortcutcmd.go`, `upload.go`, `user.go`, `workflow.go`
- Knowledge 模块错误码范围：105000000~105999999，定义 38 个错误码

## 工具包

### bizpkg/

| 子包 | 说明 |
|------|------|
| `config/` | 配置管理（含 base/ 基础配置） |
| `llm/modelbuilder/` | LLM 模型构建器 |
| `fileutil/` | 文件工具（含 pyutil） |
| `debugutil/` | 调试工具 |

### pkg/

| 子包 | 说明 |
|------|------|
| `ctxcache` | 上下文缓存 |
| `envkey` | 环境变量键定义 |
| `errorx/code` | 错误码注册 |
| `execute` | 执行器 |
| `goutil` | Go 工具函数 |
| `hertzutil` | Hertz 工具 |
| `i18n` | 国际化 |
| `kvstore` | KV 存储 |
| `lang/` | 语言基础库（conv/crypto/maps/ptr/sets/signal/slices/sqlutil/ternary） |
| `logs` | 日志 |
| `saasapi` | SaaS API 客户端 |
| `safego` | 安全 goroutine（panic 恢复） |
| `sonic` | 高性能 JSON 序列化 |
| `taskgroup` | 任务组 |
| `urltobase64url` | URL 转 Base64URL |

### safego

安全 goroutine 封装，通过 `Go()` 方法启动 goroutine 并自动 panic 恢复。

### types/

| 子目录 | 说明 |
|--------|------|
| `consts/` | 常量定义（运行模式、DB 连接、缓存地址、SessionKey 等，146 行） |
| `errno/` | 各模块错误码 |
| `ddl/` | 数据定义语言 |

## 基础处理器

`api/handler/coze/base.go` 提供基础响应函数：
- `invalidParam` — 无效参数响应
- `internalError` — 内部错误响应
