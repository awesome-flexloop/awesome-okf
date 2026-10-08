---
type: Reference
title: Zleap-Agent 源码信源登记
description: Zleap-Agent v0.3.3 TypeScript monorepo 源码路径、版本信息、12 packages 目录结构与关键文件清单
tags: [zleap-agent, source, reference, v0.3, typescript, monorepo, ai-agent]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: zleap-agent-local
    resource: d:\spaces\SpecWeave\external\libs\models\ai\Zleap-Agent\
    title: Zleap-Agent 本地源码镜像
---

# Zleap-Agent 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Zleap-Agent |
| 版本 | **0.3.3** |
| 描述 | 多渠道 AI Agent 平台——支持 CLI、Web UI、桌面端（Tauri）和 IM 网关（飞书/微信）的通用智能代理运行时 |
| 包名 | `zleap-agent`（根），12 个子包使用 `@zleap/*` 和 `@zleap-ai/*` 命名空间 |
| 私有包 | `"private": true` |
| 模块系统 | ESM（`"type": "module"`） |
| 包管理器 | pnpm@9.15.0（workspace 协议） |
| 语言 | TypeScript 5.7+（主体），Rust（桌面端 Tauri 后端） |
| 前端框架 | Next.js 16（App Router）+ React 19 + Tailwind CSS v4 |
| CLI 框架 | Ink 5（React 终端 UI）+ cac |
| 数据库 | PostgreSQL + pgvector（向量召回） |
| 许可证 | 未在 package.json 中声明（私有项目） |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\Zleap-Agent\` |

## 版本标识

版本号定义于根目录 package.json：

```json
{
  "name": "zleap-agent",
  "version": "0.3.3"
}
```

## 源码位置

Zleap-Agent 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/Zleap-Agent/
```

根目录关键文件：

| 文件 | 用途 |
|------|------|
| `package.json` | 根工作区配置，定义 scripts 和 devDependencies |
| `docker-compose.yml` | 本地 PostgreSQL（pgvector）+ Worker + Gateway 容器编排 |
| `commitlint.config.js` | Conventional Commits 提交规范配置 |
| `.env.example` | 环境变量模板（数据库 URL、模型 API Key 等） |
| `.npmrc` | npm/pnpm 配置 |
| `distribution.json` | 发行版配置 |

## Packages 目录结构

Zleap-Agent 采用 pnpm workspace monorepo 架构，共 **12 个 packages**（含 1 个 runtime 重导出壳）：

```
packages/
├── core/          # @zleap/core      — 核心类型、运行时、注册中心（零依赖，基础层）
├── ai/            # @zleap/ai        — AI Provider 抽象层（Anthropic/OpenAI兼容/SSE）
├── store/         # @zleap/store     — PostgreSQL + pgvector 持久化层
├── agent/         # @zleap/agent     — Agent 引擎（对话服务、内置工具、MCP、记忆）
├── avatar/        # @zleap/avatar    — 输入组装层（入站/定时/Web聊天运行输入构建）
├── tasks/         # @zleap/tasks     — 定时任务（cron解析、队列、执行、pg-boss）
├── host/          # @zleap/host      — 宿主生命周期（PG管理、服务编排、安装升级）
├── gateway/       # @zleap/gateway   — IM 网关（飞书/微信/飞书CLI 多平台适配）
├── cli/           # @zleap-ai/cli    — 终端 CLI（Ink TUI、命令路由、聊天模式）
├── web/           # @zleap/web       — Web UI（Next.js 16 App Router，前端+API Route）
├── desktop/       # @zleap/desktop   — 桌面端（Tauri 2.x / Rust + WebView）
└── runtime/       # @zleap/runtime   — 聚合重导出壳（re-export @zleap/host，无独立逻辑）
```

### 各包概览

| 包名 | NPM 包名 | 语言 | 行数级别 | 核心职责 |
|------|---------|------|---------|---------|
| core | `@zleap/core` | TS | ~2500 | 类型系统、AgentRuntime、注册中心、钩子、记忆接口 |
| ai | `@zleap/ai` | TS | ~800 | ProviderAdapter 接口、Anthropic/OpenAI 兼容实现、流式抽象 |
| store | `@zleap/store` | TS | ~1500 | PgStore、Schema 迁移、RRF 排序、抽取管线、记忆适配 |
| agent | `@zleap/agent` | TS | ~4000 | ConversationService、内置工具集、MCP运行时、workspace turn循环 |
| avatar | `@zleap/avatar` | TS | ~200 | 四种运行输入构建器（inbound/scheduled/webChat/runAssembly） |
| tasks | `@zleap/tasks` | TS | ~500 | Cron 解析、任务队列（pg-boss）、定时执行 Worker |
| host | `@zleap/host` | TS | ~2500 | 服务编排（runServe）、PG 自动管理、安装/升级/路径解析 |
| gateway | `@zleap/gateway` | TS | ~1500 | 平台适配器（Feishu/WeChat/FeishuCli）、ChannelSupervisor |
| cli | `@zleap-ai/cli` | TS/TSX | ~3000 | Ink TUI、命令路由、聊天模式、UI 组件库 |
| web | `@zleap/web` | TS/TSX | ~5000+ | Next.js App Router、API Routes、React 组件、lib/services |
| desktop | `@zleap/desktop` | Rust/HTML | ~1400 | Tauri 窗口管理、子进程编排、自动更新、系统托盘 |
| runtime | `@zleap/runtime` | TS | ~50 | 重导出壳，`export * from '@zleap/host'` |

## 关键文件清单

### 核心类型与运行时（@zleap/core）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| core/src/types.ts | 全局类型系统（713行） | `RunStatus`、`WorkStatus`、`WorkStepStatus`、`ToolDefinition`、`SkillDefinition`、`AgentDefinition`、`AgentRuntimeHook`、`AgentEvent`、`Run/Work/WorkStep`、`WorkspaceDelta` |
| core/src/runtime.ts | AgentRuntime 核心类（~800行） | `AgentRuntime` 类：`runAgent()`、`run()`、`work()`、`callTool()`、8个注册中心成员 |
| core/src/agents.ts | Agent 注册中心 | `AgentRegistry` 类：`register()`、`get()`、`list()` |
| core/src/tools.ts | Tool 注册中心 | `ToolRegistry` 类：`register()`、`get()`、`list()` |
| core/src/skills.ts | Skill 注册中心 | `SkillRegistry` 类 |
| core/src/events.ts | 事件总线 | `AgentEventBus` 类 |
| core/src/hooks.ts | 生命周期钩子注册 | `AgentHookRegistry` 类 |
| core/src/actor.ts | Actor 角色与权限 | `ActorRole`、`ActorPermission`、`ActorContext` |
| core/src/memory/orchestrator.ts | 记忆编排器 | 记忆投影、笔记、人际策略编排 |
| core/src/context/assembly.ts | 上下文组装 | 系统提示、工具描述、技能指令组装 |
| core/src/workspace.ts | Workspace 注册中心 | `WorkSpaceRegistry`、`WorkSpaceDefinition`、`WorkSpaceHandler` |
| core/src/toolPolicy.ts | 工具策略 | 工具调用审批/拦截策略 |
| core/src/toolRecovery.ts | 工具参数恢复 | JSON 修复、参数形状校验与恢复 |
| core/src/traces.ts | Trace 存储 | `TraceStore`，运行追踪记录 |
| core/src/store-ports.ts | 存储端口接口 | `RecordMemoryPort`、`RuntimeCacheStore` 等端口定义 |

### AI Provider 层（@zleap/ai）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| ai/src/types.ts | AI 层类型系统（155行） | `ProviderAdapter` 接口、`Message`、`AssistantStreamEvent`、`Model`、`ProviderCapabilities` |
| ai/src/providers/anthropic.ts | Anthropic Provider（~315行） | `AnthropicProvider` 类，实现 `ProviderAdapter` |
| ai/src/providers/openai-compatible.ts | OpenAI 兼容 Provider | OpenAI Compatible 适配器 |
| ai/src/providers/sse.ts | SSE 流式解析 | Server-Sent Events 解析器 |
| ai/src/registry.ts | Provider 注册中心 | AI Provider 注册与查找 |
| ai/src/create.ts | Provider 工厂 | `createProvider()` 创建入口 |
| ai/src/stream.ts | 统一流式抽象 | 流式事件处理 |

### Agent 引擎层（@zleap/agent）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| agent/src/conversation/service.ts | 对话服务（~430行） | `ConversationService` 类：入站消息处理、模型解析、会话管理 |
| agent/src/tools.ts | 内置工具集（~1150行） | ls/read/write/edit/bash 等文件系统和命令行工具定义 |
| agent/src/kernel/kernel.ts | Agent 内核 | L2 核心逻辑 |
| agent/src/mcpRuntime.ts | MCP 运行时 | MCP 服务器管理 |
| agent/src/soul.ts | Agent 人格配置 | "灵魂"/人格定义 |
| agent/src/memoryDream.ts | 记忆梦境整理 | 记忆整理/压缩功能 |
| agent/src/permissions.ts | 权限模式 | 工具调用权限策略 |
| agent/src/compaction/service.ts | 对话压缩 | 对话历史压缩服务 |
| agent/src/workspace-turn/turnLoop.ts | Workspace Turn 循环 | workspace 级别 turn 执行循环 |

### 持久化层（@zleap/store）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| store/src/store.ts | PgStore 主类（~1000行） | `PgStore`、`ZleapStore` 接口、`createStore()`、`sanitizeMcpConfigForStorage()` |
| store/src/core/schema.ts | 核心表 Schema（~100行） | source_group、source、event、entity、event_entity 五张核心表 |
| store/src/core/rrf.ts | RRF 融合排序（60行） | Reciprocal Rank Fusion 算法实现，默认 k=60 |
| store/src/core/extract.ts | 抽取管线（~280行） | 会话→event+entity 抽取、contentHash(SHA-256)、`topKeywords()`、记忆调和器 |
| store/src/core/record-memory.ts | 记忆适配器（~210行） | RecordMemoryPort 适配，ingest/recall/listRecent 方法 |
| store/src/schema.ts | 外层 Schema | 完整 DDL（含 notes、scheduled_tasks 等） |
| store/src/migrate.ts | 数据库迁移 | Schema 迁移执行 |

### 宿主与服务编排（@zleap/host）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| host/src/supervisor.ts | 服务主管（~150行） | `runServe()`：PG确保→构建→迁移→启动Web/Worker/Gateway |
| host/src/postgres.ts | PostgreSQL 管理 | `ensurePostgres()`：自定义URL→bundled→本地→Docker 四级回退 |
| host/src/config.ts | 配置管理 | `CliConfig`、CONFIG_ENV_MAP（9个映射）、TRACKED_ENV_KEYS（15个）、`formatConfigValue()` |
| host/src/constants.ts | 默认常量 | 默认DB URL、Web端口(4789)、嵌入维度(1536) |
| host/src/paths.ts | 路径解析 | `resolveRuntimeRoot()`、`isBundledInstall()` |
| host/src/lifecycle.ts | 安装生命周期 | `finishInstall()`：目录确保→状态写入→detached serve→健康检查→打开浏览器 |
| host/src/lock.ts | 运行时锁 | `acquireRuntimeLock()` 防止多实例并发 |

### IM 网关（@zleap/gateway）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| gateway/src/runner.ts | Gateway 运行器（~80行） | `GatewayRunner` 类：适配器→ConversationService 桥接、权限策略 |
| gateway/src/supervisor.ts | 渠道控制平面（~120行） | `ChannelSupervisor` 类：2500ms reconcile 循环 |
| gateway/src/types.ts | 网关类型 | `PlatformAdapter` 接口、`PlatformMessageEvent` |
| gateway/src/config.ts | 渠道配置 | Feishu/WeChat/FeishuCli 配置、`GroupPolicy`、`GatewayPermissionMode` |
| gateway/src/platforms/base.ts | 平台基类（~90行） | `BasePlatformAdapter`：消息分割（safeCut）、指数退避重试 |
| gateway/src/worker.ts | Worker 入口（~100行） | 独立进程入口：加载→初始化→注册渠道→启动 |

### 定时任务（@zleap/tasks）

| 文件 | 内容 | 关键导出 |
|------|------|---------|
| tasks/src/service.ts | 任务服务 | 定时任务调度服务 |
| tasks/src/cron.ts | Cron 解析 | Cron 表达式解析 |
| tasks/src/queue.ts | 任务队列 | pg-boss 队列管理 |
| tasks/src/worker.ts | Task Worker 入口 | 独立 worker 进程 |

### 输入组装层（@zleap/avatar）

| 文件 | 内容 |
|------|------|
| avatar/src/inboundRun.ts | IM 入站运行输入构建（`buildInboundRunInput`） |
| avatar/src/scheduledRun.ts | 定时任务运行输入构建 |
| avatar/src/webChatRun.ts | Web 聊天运行输入构建 |
| avatar/src/runAssembly.ts | 通用运行组装 |

### CLI（@zleap-ai/cli）

| 文件 | 内容 |
|------|------|
| cli/src/app.tsx | Ink TUI 主组件（~860行）：终端聊天界面 |
| cli/src/cli/router.ts | 命令路由：channels/config/doctor/init/models/serve/sessions/setup 等 |
| cli/src/chat/mode.tsx | 交互聊天模式组件 |
| cli/src/index.tsx | CLI 入口 |

### Web UI（@zleap/web）

| 文件 | 内容 |
|------|------|
| web/app/layout.tsx | Next.js 根布局（字体加载、主题、i18n） |
| web/app/page.tsx | 首页/聊天页 |
| web/app/globals.css | 全局样式与设计 token（颜色/圆角/阴影/字号/动效） |
| web/app/api/chat/route.ts | 聊天 API 端点 |
| web/lib/server/sharedStore.ts | 共享 Store 工厂（服务端） |
| web/lib/sseEngine.ts | SSE 流式引擎（服务端推送） |

### 桌面端（@zleap/desktop，Rust）

| 文件 | 内容 |
|------|------|
| desktop/src-tauri/src/main.rs | Rust 入口：release 模式隐藏控制台窗口 |
| desktop/src-tauri/src/lib.rs | Tauri 主逻辑（~1350行）：窗口管理、bootstrap、自动更新、系统托盘、Node.js 管理 |
| desktop/src-tauri/Cargo.toml | Rust 依赖配置（tauri 2.x、updater、dialog、shell 插件） |
| desktop/src-tauri/tauri.conf.json | Tauri 应用配置 |

## 核心类/函数/接口索引

### 核心类

| 类名 | 所在包 | 文件 | 职责 |
|------|-------|------|------|
| `AgentRuntime` | @zleap/core | `runtime.ts` | 运行时核心：聚合8个注册中心，提供 run/work/callTool 主流程 |
| `AgentRegistry` | @zleap/core | `agents.ts` | Agent 定义注册（Map 存储） |
| `ToolRegistry` | @zleap/core | `tools.ts` | Tool 定义注册（Map 存储） |
| `SkillRegistry` | @zleap/core | `skills.ts` | Skill 定义注册 |
| `AgentEventBus` | @zleap/core | `events.ts` | 事件发布/订阅总线 |
| `AgentHookRegistry` | @zleap/core | `hooks.ts` | 生命周期钩子管理 |
| `MemoryRegistry` | @zleap/core | `memory.ts` | 内存中记忆注册（遗留） |
| `SessionRegistry` | @zleap/core | `sessions.ts` | 会话管理 |
| `WorkSpaceRegistry` | @zleap/core | `workspace.ts` | Workspace Handler 注册 |
| `TraceStore` | @zleap/core | `traces.ts` | 运行追踪记录存储 |
| `ConversationService` | @zleap/agent | `conversation/service.ts` | L2 对话服务：入站消息→模型调用→回复 |
| `PgStore` | @zleap/store | `store.ts` | PostgreSQL 持久化实现（含向量召回、笔记、定时任务、缓存） |
| `AnthropicProvider` | @zleap/ai | `providers/anthropic.ts` | Anthropic Messages API 适配器 |
| `GatewayRunner` | @zleap/gateway | `runner.ts` | 平台适配器到对话服务的桥接运行器 |
| `ChannelSupervisor` | @zleap/gateway | `supervisor.ts` | 渠道生命周期控制平面（reconcile 循环） |
| `BasePlatformAdapter` | @zleap/gateway | `platforms/base.ts` | 平台适配器抽象基类（消息分割/重试） |
| `ConnectionsService` | @zleap/agent | `conversation/connections.ts` | 连接管理服务 |

### 核心接口

| 接口名 | 所在包 | 文件 | 职责 |
|--------|-------|------|------|
| `ProviderAdapter` | @zleap/ai | `types.ts` | AI Provider 统一接口：`id`、`capabilities`、`stream()` |
| `PlatformAdapter` | @zleap/gateway | `types.ts` | IM 平台统一接口：`connect/send/disconnect/setMessageHandler` |
| `ZleapStore` | @zleap/store | `store.ts` | 存储层统一接口（notes/core/integrations/runtimeCache/tasks） |
| `WorkSpaceHandler` | @zleap/core | `types.ts` | Workspace 处理器函数签名 |
| `ToolHandler` | @zleap/core | `types.ts` | 工具执行器函数签名 |
| `AgentRuntimeHook` | @zleap/core | `types.ts` | 运行时生命周期钩子（beforeRun/afterRun/beforeToolCall/afterToolCall 等9个） |
| `MemoryReader` | @zleap/core | `types.ts` | 记忆查询函数签名 |
| `WorkspaceEmitter` | @zleap/core | `types.ts` | Workspace 进度事件发射器 |

### 核心类型/枚举

| 类型名 | 所在包 | 值/字段 |
|--------|-------|--------|
| `RunStatus` | @zleap/core | `created`→`session_assembling`→`planning`→`working`→`integrating`→`delivering`→`idle`/`completed`/`aborted`/`failed`（10种） |
| `WorkStatus` | @zleap/core | `created/queued/loading/active/producing/curating/exited/suspended/failed/aborted`（10种） |
| `WorkStepStatus` | @zleap/core | `loading/active/producing/curating/exited/failed/aborted`（7种） |
| `ToolDefinition` | @zleap/core | id/description/parameters/describe/promptSnippet/handler/executionMode/requiresReason/recovery/cache |
| `SkillDefinition` | @zleap/core | id/version/label/instructions/toolIds/lifecycle/tokenBudget/trustStatus/riskAudit/schemaHash |
| `AgentDefinition` | @zleap/core | id/label/description/avatar/instructions/model/defaultSpaces/defaultSkillIds/defaultToolIds |
| `WorkspaceDelta` | @zleap/core | text/tool/approval/provider_lifecycle/turn_lifecycle 五种联合类型 |
| `AgentEvent` | @zleap/core | agent_start/agent_end/run_status/work_status/tool_execution_start/tool_execution_end/artifact_produced/error 等13种事件 |
| `Message` | @zleap/ai | UserMessage/AssistantMessage/ToolResultMessage 联合类型 |
| `AssistantStreamEvent` | @zleap/ai | text_start/text_delta/text_end/thinking_start/toolcall_start/toolcall_delta/toolcall_end/done/error |
| `ProviderCapabilities` | @zleap/ai | toolCalling/cacheBreakpoints/thinking/tokenizer/maxOutputTokens |
| `RuntimeCacheKind` | @zleap/core | search_result/webpage/file_output/workspace_result/tool_result/note（6种） |
| `GroupPolicy` | @zleap/gateway | open/allowlist/blacklist/admin_only/disabled（5种） |
| `GatewayPermissionMode` | @zleap/gateway | request_approval/full_access |
| `AgentErrorCode` | @zleap/core | agent_not_found/tool_not_found/tool_not_allowed/tool_reason_required/workspace_failed 等13种错误码 |

### 核心工厂函数

| 函数名 | 所在包 | 文件 | 职责 |
|--------|-------|------|------|
| `createStore()` | @zleap/store | `store.ts` | 创建 PgStore 实例（advisory lock 序列化 schema 初始化，失败返回 null 降级） |
| `ensurePostgres()` | @zleap/host | `postgres.ts` | 四级回退确保 PostgreSQL 可用 |
| `runServe()` | @zleap/host | `supervisor.ts` | 启动完整服务栈 |
| `buildInboundRunInput()` | @zleap/avatar | `inboundRun.ts` | 构建 IM 入站运行输入 |
| `sanitizeMcpConfigForStorage()` | @zleap/store | `store.ts` | 敏感字段正则过滤（secret/token/password/credential/key） |
| `topKeywords()` | @zleap/store | `core/extract.ts` | 关键词提取（≥4字符，内置25个停用词） |

### 关键算法

| 算法/机制 | 文件 | 说明 |
|-----------|------|------|
| RRF 融合排序 | `store/src/core/rrf.ts` | Reciprocal Rank Fusion，默认 k=60，合并向量/词法/实体/图多路召回 |
| contentHash 幂等 | `store/src/core/extract.ts` | SHA-256，parts 数组 `\0` 分隔 + trim + toLowerCase |
| safeCut 消息分割 | `gateway/src/platforms/base.ts` | 代码块感知的长消息分割（4000字符阈值，8000硬上限） |
| 指数退避重试 | `gateway/src/platforms/base.ts` | 默认3次重试（SEND_ATTEMPTS=3） |
| 笔记 FIFO 归档 | `store/src/store.ts` | 超过 DEFAULT_AGENT_NOTE_LIMIT 的旧笔记自动 archived |
| A/B 双线记忆 | `store/src/store.ts` | A线 agent_memory（人笔记）+ B线 core 事件图引擎（通用事件记忆） |

## 包间依赖映射

基于各包 `package.json` 中的 `dependencies` 字段（`workspace:*` 协议）：

### 依赖矩阵

| 包 | 依赖的内部包 | 外部关键依赖 |
|----|------------|-------------|
| **@zleap/core** | _（无，基础层）_ | jsonrepair, yaml |
| **@zleap/ai** | _（无，独立 Provider 层）_ | _（零运行时依赖）_ |
| **@zleap/store** | @zleap/core | pg（PostgreSQL 驱动） |
| **@zleap/avatar** | @zleap/core | _（无外部依赖）_ |
| **@zleap/agent** | @zleap/ai, @zleap/core, @zleap/store | @modelcontextprotocol/sdk, js-tiktoken |
| **@zleap/tasks** | @zleap/avatar, @zleap/agent, @zleap/core, @zleap/host, @zleap/store | pg-boss, dotenv |
| **@zleap/host** | @zleap/agent, @zleap/ai, @zleap/core, @zleap/store | pg, dotenv |
| **@zleap/gateway** | @zleap/avatar, @zleap/ai, @zleap/agent, @zleap/core, @zleap/host, @zleap/store | @larksuiteoapi/node-sdk, @larksuite/cli, qrcode, dotenv |
| **@zleap-ai/cli** | @zleap/ai, @zleap/agent, @zleap/core, @zleap/host, @zleap/store | ink, react, cac, @modelcontextprotocol/sdk, qrcode, js-tiktoken, dotenv |
| **@zleap/web** | @zleap/agent, @zleap/ai, @zleap/avatar, @zleap/core, @zleap/host, @zleap/store, @zleap/tasks | next, react, react-dom, tailwindcss, shadcn, radix-ui, framer-motion, react-markdown, i18next |
| **@zleap/desktop** | _（Rust 独立，通过子进程调用 Node.js CLI）_ | tauri 2.x, tauri_plugin_updater, tauri_plugin_shell, tauri_plugin_dialog |
| **@zleap/runtime** | @zleap/agent, @zleap/gateway, @zleap/host, @zleap/store, @zleap/tasks, @zleap-ai/cli | _（聚合壳）_ |

### 分层架构图（依赖方向自下而上）

```
┌─────────────────────────────────────────────────────────────┐
│  入口层 (Entry Points)                                       │
│  ┌─────────┐  ┌─────┐  ┌─────────────────┐  ┌───────────┐  │
│  │   CLI    │  │ Web │  │ Desktop (Rust)  │  │  runtime  │  │
│  │(Ink TUI) │  │(Next)│  │  (Tauri 2.x)   │  │ (聚合壳)  │  │
│  └────┬─────┘  └──┬──┘  └────────┬────────┘  └─────┬─────┘  │
│       │           │              │                  │        │
├───────┼───────────┼──────────────┼──────────────────┼────────┤
│       │           │              │                  │        │
│  ┌────┴───────────┴──────────────┴──────────────────┴─────┐  │
│  │  服务编排层 (Orchestration)                             │  │
│  │  ┌──────────┐  ┌───────────┐  ┌───────┐               │  │
│  │  │   host   │  │  gateway  │  │ tasks │               │  │
│  │  │(supervisor│  │(Feishu/   │  │(cron/ │               │  │
│  │  │ /postgres│  │ WeChat)   │  │queue) │               │  │
│  │  └────┬─────┘  └─────┬─────┘  └───┬───┘               │  │
│  │       │              │            │                    │  │
│  └───────┼──────────────┼────────────┼────────────────────┘  │
│          │              │            │                       │
│  ┌───────┴──────────────┴────────────┴────────────────────┐  │
│  │  引擎层 (Engine)        ┌────────┐                      │  │
│  │  ┌─────────────────┐    │ avatar │                      │  │
│  │  │      agent      │◄───┤(输入  │                      │  │
│  │  │ (Conversation/  │    │ 组装) │                      │  │
│  │  │  Tools/MCP/WS)  │    └────────┘                      │  │
│  │  └────────┬────────┘                                     │  │
│  │           │                                              │  │
│  └───────────┼──────────────────────────────────────────────┘  │
│              │                                                 │
│  ┌───────────┴──────────────────────────────────────────────┐  │
│  │  Provider 层  ┌────────┐                                  │  │
│  │  ┌────────┐   │ store  │  (PostgreSQL/pgvector 持久化)    │  │
│  │  │   ai   │   └───┬────┘                                  │  │
│  │  │(Anthro/│       │                                       │  │
│  │  │OpenAI) │       │                                       │  │
│  │  └───┬────┘       │                                       │  │
│  │      │            │                                       │  │
│  └──────┼────────────┼───────────────────────────────────────┘  │
│         │            │                                          │
│  ┌──────┴────────────┴──────────────────────────────────────┐  │
│  │  核心层 (Core) — 零依赖                                   │  │
│  │  types / runtime / registries / hooks / events / memory  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 依赖方向说明

1. **core + ai** 是双基础层：core 提供纯类型+运行时抽象（零外部运行时依赖，仅 jsonrepair/yaml）；ai 提供 Provider 抽象（零运行时依赖）。两者互不依赖。
2. **store** 仅依赖 core，实现 `store-ports` 中定义的持久化端口，是唯一直接依赖 `pg` 的包。
3. **avatar** 仅依赖 core，是薄的输入组装层，被 gateway/tasks/web 消费。
4. **agent** 依赖 core + ai + store，是核心业务引擎（对话、工具、MCP、workspace）。
5. **host** 依赖 agent + ai + core + store，负责进程编排和基础设施管理（PG、迁移、服务启停）。
6. **tasks** 在 host 之上，额外依赖 avatar（定时任务需要构建运行输入）。
7. **gateway** 依赖最广（avatar + ai + agent + core + host + store），需要接入 IM 平台并驱动完整运行时。
8. **cli** 和 **web** 是终端用户界面，依赖核心服务包但互不依赖。
9. **desktop**（Rust）通过子进程调用 Node.js（desktop-bootstrap-cli），不直接引用 npm 包。
10. **runtime** 是聚合重导出壳，依赖几乎所有包，主要用于简化外部消费方的导入路径（实际代码仅 `export * from '@zleap/host'`）。

## 构建与开发

### 构建命令

```bash
pnpm build                    # 构建所有 packages
pnpm dev                      # 开发模式（Web + Worker + Gateway）
pnpm dev:web                  # 仅 Web 开发
pnpm dev:tasks                # 仅 Task Worker
pnpm dev:gateway              # 仅 Gateway Worker
pnpm serve                    # 生产模式启动
pnpm cli                      # 启动 CLI
pnpm desktop:build            # 构建桌面端（Tauri）
pnpm test                     # 运行所有包测试
```

### 数据库

默认连接 `postgres://zleap:zleap@127.0.0.1:5433/zleap`，使用 pgvector 扩展支持向量相似度搜索。支持自动启动：
- 自定义连接 URL →  bundled PostgreSQL → 本地安装（homebrew/PATH）→ Docker Compose

### 环境变量

主要环境变量通过 `ZLEAP_*` 前缀配置，共追踪 15 个关键变量，包括：
- `ZLEAP_DATABASE_URL` — 数据库连接
- `ZLEAP_MODEL_BASE_URL` / `ZLEAP_MODEL_API_KEY` / `ZLEAP_MODEL` — 模型配置
- `ZLEAP_302_API_KEY` — 302.AI 平台集成
- `ZLEAP_GATEWAY_MAX_CONCURRENT` — 网关并发上限
