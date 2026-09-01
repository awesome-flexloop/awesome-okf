---
type: Reference
title: DeepSeek Harness 源码信源登记
description: deepseek-harness 0.1.0-rc.5 源码路径、版本信息、Cordis 插件架构、核心目录与关键文件清单
tags: [deepseek-harness, source, reference, v0.1, ai-agent, cordis, typescript]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deepseek-harness-internal
    resource: d:\spaces\SpecWeave\external\libs\models\ai\deepseek-harness\
    title: deepseek-harness 源码树（SpecWeave 外部依赖镜像）
---

# DeepSeek Harness 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | DeepSeek Harness（dsh） |
| 版本 | **0.1.0-rc.5**（Release Candidate 5） |
| 描述 | 基于 Cordis 插件框架的 TypeScript AI Agent 运行时，提供 LLM 抽象、工具系统、会话管理、MCP/ACP 协议桥接、文件系统/Shell/LSP 工具、Web 客户端与 SDK 等完整能力 |
| 组织 | DeepSeek AI（@deepseek-ai） |
| 许可证 | MIT |
| 语言 | TypeScript（ESM） |
| 运行时要求 | Node.js ^22.19.0 \|\| >=24.0.0 |
| 包管理器 | pnpm@11.7.0（workspaces + pnpm-link） |
| 构建工具 | tsc（类型检查）+ tsdown（打包）+ Vite（Web 客户端） |
| 测试框架 | Vitest |
| 插件框架 | [Cordis](https://github.com/shigma/cordis)（Context/Service/Plugin/Fiber 模型） |
| Schema 校验 | @deepseek-ai/schemastery（vendored Zod 变体） |
| 工具命名空间前缀 | `@deepseek-ai/dsh-*` |

## 源码位置

deepseek-harness 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/deepseek-harness/
```

源码根目录下的关键顶层项：

| 路径 | 用途 |
|------|------|
| `packages/` | 核心包组（两层嵌套：`<group>/<package>`），工作区 glob 为 `packages/*/*` |
| `apps/cli/` | CLI 入口（`dsh` 命令），负责参数解析、Profile 启动 |
| `apps/web/` | Web 前端应用（Vite + React） |
| `vendor/` | Vendored 框架：cosmokit、schemastery（pnpm link 覆盖） |
| `native/landlock-run/` | Linux Landlock 沙箱原生启动器（独立工作区） |
| `python/sdk/` | Python SDK（pyproject.toml + uv） |
| `python/sdk-runtime/` | Python 运行时部署清单（单 exe 构建依赖闭包） |
| `docs/` | 文档源（VitePress），含 cordis-api、subsystems、architecture 等 |
| `examples/` | 可运行示例（acp-agent、mcp-memory、web-cordis） |
| `scripts/` | 工程脚本（gen-cordis-catalog、gen-tool-catalog、verify-* 等 60+） |
| `patches/` | pnpm patch（node-pty@1.1.0.patch） |
| `package.json` | 根工作区清单（私有包 @deepseek-ai/dsh-root） |
| `pnpm-workspace.yaml` | 工作区配置与 allowBuilds 白名单 |

---

## 项目概览：TS Monorepo Cordis 插件架构

deepseek-harness 是一个高度模块化的 TypeScript monorepo，采用 **Cordis 插件框架** 作为核心架构。整个系统由 **200+ 个 npm 包**组成（远超 50 个），按照"能力缝"（capability seam）原则组织——每个包声明自己提供的 Service、依赖的 Service（inject），以及可选的配置 Schema，由 Cordis 容器负责按需装配、生命周期管理和热替换。

### 架构核心概念

| 概念 | 说明 |
|------|------|
| **Context** | Cordis 依赖注入容器，持有 Service 注册表、事件总线、Fiber 生命周期 |
| **Service** | 挂载在 Context 上的单例能力（如 `ctx.llm`、`ctx.tools`、`ctx.shell`），继承 `cordis/Service` |
| **Plugin** | 命名导出模块 `{ name, inject?, Config?, apply(ctx, config) }`，通过 `cordis.yml` 声明装配 |
| **Fiber** | 插件的生命周期作用域，支持 dispose（清理）和 effect（自动清理资源） |
| **声明合并** | 通过 `declare module '@deepseek-ai/cordis' { interface Context { ... } }` 扩展类型 |
| **Bundle** | 预打包的插件组合配置（`cordis.patch.yml`），如 `bundle/base` 提供核心能力基线 |
| **Events** | 瀑布式（waterfall）事件拦截链，支持 `next()` 调用链传递，如 `llm/stream` |

### 工作区配置

工作区定义于 `pnpm-workspace.yaml`，glob 模式：

- `packages/*/*` — 两层嵌套的功能包组
- `vendor/*` — Vendored 框架
- `apps/*` — 应用入口
- `native/landlock-run` + `native/landlock-run/packages/*` — 原生组件
- `examples` — 示例（仅依赖解析，非构建目标）
- `python/sdk-runtime` — Python 运行时部署清单

---

## Packages 分类列表

> 包路径格式：`packages/<group>/<package>/`，npm 名称为 `@deepseek-ai/dsh-<package>`（去组名）。
> 以下列出主要包组和代表包，总计 200+ 包。

### core/ — 核心运行时

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `core/agent` | `@deepseek-ai/dsh-agent` | Agent 注册中心（`AgentRegistry`）、Agent 生命周期、Inbox 消息队列、事件总线 |
| `core/agent-loop` | `@deepseek-ai/dsh-agent-loop` | Agent 主循环驱动（LLM 调用→工具执行→结果回填） |
| `core/agent-default-model` | — | 默认模型选择策略 |
| `core/agent-tool-presentation` | — | 工具结果呈现层 |
| `core/session` | `@deepseek-ai/dsh-session` | 会话管理（`Session`、`SessionStore`）、事件追加、消息派生、JSON 序列化 |
| `core/scope` | `@deepseek-ai/dsh-scope` | 作用域上下文（`Scoped`）、分层注册（NamedEntries/AnonymousEntries/ScopedLayers） |
| `core/tools` | `@deepseek-ai/dsh-tools` | 工具运行时（`ToolRuntime`）、工具定义（`defineTool`）、Schema 校验、Code Mode |
| `core/system-prompt` | `@deepseek-ai/dsh-system-prompt` | 系统提示词组装 |

### llm/ — LLM 抽象与 Provider 适配

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `llm/llm` | `@deepseek-ai/dsh-llm` | LLM 运行时（`LlmRuntime`）、适配器抽象（`LlmAdapter`）、消息类型、流式块组装（`BlockAssembler`）、错误分类（`HarnessError`/`LlmError`）、重试策略 |
| `llm/llm-pi-ai` | — | PI-AI Provider 适配器（@earendil-works/pi-ai 后端），SSE 流转换、错误映射 |
| `llm/llm-deepseek` | — | DeepSeek 官方 API Provider 适配器 |
| `llm/llm-retry` | `@deepseek-ai/dsh-llm-retry` | LLM 重试策略中间件 |
| `llm/token-meter` | — | Token 用量计量 |

### mcp/ — Model Context Protocol

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `mcp/mcp-client` | `@deepseek-ai/dsh-mcp-client` | MCP 客户端桥接插件，stdio/HTTP 传输，工具名命名空间 `mcp__<server>__<tool>` |

### acp/ — Agent Client Protocol

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `acp/acp` | `@deepseek-ai/dsh-acp` | ACP 服务端（JSON-RPC over stdio），暴露 initialize/newSession/prompt/cancel，面向自动化客户端 |

### sdk/ — 软件开发工具包

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `sdk/protocol` | `@deepseek-ai/dsh-sdk-protocol` | SDK 协议层：`JsonRpcLineTransport`（换行分隔 JSON-RPC）、请求/通知类型定义 |
| `sdk/client` | `@deepseek-ai/dsh-sdk-client` | TypeScript 客户端 SDK：`HarnessClient`（子进程管理）、`DeepSeekHarness`/`HarnessSession` 高层 API |
| `sdk/server` | `@deepseek-ai/dsh-sdk-jsonrpc-server` | SDK JSON-RPC 服务端插件，shutdown→dispose→exit(0) 优雅关闭 |

### fs/ — 文件系统

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `fs/fs` | `@deepseek-ai/dsh-fs` | 文件系统抽象接口（`ctx.fs` Service 定义） |
| `fs/fs-local` | — | 本地文件系统实现 |
| `fs/fs-sandbox` | — | 文件系统沙箱控制器 |
| `fs/fs-observation-policy` | — | 文件变更观察策略 |
| `fs/tool-fs` | `@deepseek-ai/dsh-tool-fs` | 文件系统工具套件（read/write/edit/read_image），FsSandboxController 变更审批 |
| `fs/tool-fs-search` | — | 文件搜索工具（grep/glob） |
| `fs/tool-str-replace-editor` | — | 字符串替换编辑器工具 |

### shell/ — Shell 执行

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `shell/shell` | `@deepseek-ai/dsh-shell` | Shell 执行器抽象（`ShellExecutor` Service），声明 resolve/run/start 抽象方法 |
| `shell/bash-local` | — | 本地 Bash 执行实现 |
| `shell/pwsh-local` | — | 本地 PowerShell 执行实现 |
| `shell/bash-sandbox` | — | Bash 沙箱执行（Landlock 等） |
| `shell/pwsh-sandbox` | — | PowerShell 沙箱执行 |
| `shell/shell-env` | — | Shell 环境变量管理 |
| `shell/tool-bash` | — | Bash 执行工具 |
| `shell/tool-pwsh` | — | PowerShell 执行工具 |
| `shell/tool-bash-persistent` | — | 持久化 Bash 会话工具 |

### lsp/ — 语言服务协议

| 包 | npm 名称 | 职责 |
|----|---------|------|
| `lsp/lsp` | `@deepseek-ai/dsh-lsp` | LSP 服务注册中心（`Lsp` Service），按文件扩展名路由、Provider 原子注册 |
| `lsp/lsp-stdio` | — | LSP stdio 传输实现 |
| `lsp/tool-lsp` | — | LSP 查询工具（goToDefinition/findReferences/hover） |

### client/ — Web 客户端（30+ UI 包）

| 包组 | 代表包 | 职责 |
|------|--------|------|
| `client/web` | `@deepseek-ai/dsh-client-web` | Web 启动内核（`AppWebEntry`）、两阶段启动流程 |
| `client/web-react` | — | React 绑定层 |
| `client/runtime` | — | 客户端运行时环境 |
| `client/modules` | — | 客户端模块系统（`ClientModuleSystem`） |
| `client/hmr` | — | 热模块替换支持 |
| `client/connection` | — | 服务端连接管理 |
| `client/locale` | — | 国际化（i18n） |
| `client/ui-*`（30+） | ui-layout/ui-sidebar/ui-conversation/ui-plan/ui-goal/ui-tool/ui-skill/ui-jobs/ui-settings/ui-theme/... | 按功能域拆分的 React UI 组件包 |

### 其他重要包组

| 包组 | 代表包 | 职责 |
|------|--------|------|
| `subagent/` | subagent、subagent-acp、subagent-codex、subagent-claude-code、subagent-dsh-sdk、tool-subagent | 子 Agent 派生与多种后端驱动 |
| `goal/` | goal、goal-round-driver、command-goal、tool-goal | 目标管理与轮次驱动 |
| `plan/` | plan-mode | 规划模式 |
| `compaction/` | compaction、compaction-basic、command-compact | 上下文压缩 |
| `context/` | time-context、agent-instructions、session-reference、tmux-context | 上下文注入 |
| `storage/` | storage、storage-json、storage-sqlite、storage-domain | 持久化存储抽象 |
| `spill/` | spill、spill-local、spill-policy | 输出溢出管理 |
| `jobs/` | jobs、jobs-local、tool-jobs | 后台任务管理 |
| `terminal/` | terminal、terminal-bash、tool-terminal | 终端交互 |
| `credentials/` | credentials、credentials-local | API 凭证管理 |
| `feedback/` | message-feedback、command-feedback | 用户反馈收集 |
| `interaction/` | user-approval、user-questions、permission-presets、tool-ask-user | 用户交互审批 |
| `hooks/` | hook-protocol、hooks-codex、hooks-claude-code | 外部 Agent Hook 协议 |
| `skill/` | skill、skill-filesystem、tool-skill、skill-badge | 技能系统 |
| `settings/` | settings、settings-file | 设置持久化 |
| `schedule/` | schedule | 调度系统 |
| `extensions/` | cordis-client-runner、cordis-host-runner、tool-cordis、ui-cordis | 扩展运行器 |
| `e2b/` | e2b、fs-e2b、subprocess-e2b | E2B 云沙箱集成 |
| `workflow/` | workflow、workflow-worker-thread、tool-workflow、tool-ralph | 工作流执行 |
| `guard/` | timeout-policy、repeat-tool-reminder | 安全防护策略 |
| `web/` | web、web-fetch-http、web-search-* | Web 抓取与搜索 |
| `session/`（子包） | session-persistence、session-title、session-telemetry、session-projection、session-stats | 会话扩展能力 |
| `session-query/` | session-query、session-query-sqlite、tool-session-query、session-log-export | 会话查询 |
| `code-runtime/` | code-runtime、code-runtime-worker-thread | 代码运行时（TypeScript/Python SDK 执行） |
| `subprocess/` | subprocess、subprocess-local | 子进程管理（node-pty） |
| `identity/` | anonymous-user-id | 用户身份 |
| `host/` | webserver、apiproxy、frontend-static、directory-picker-* | 宿主服务（HTTP 代理、静态资源、目录选择） |
| `api/` | gateway、remotes | API 网关 |
| `attachment/` | — | 附件管理 |
| `workspace/` | workspace | 工作区管理 |
| `todo/` | tool-todo | 待办事项工具 |
| `boot/` | app-boot、cmdline | 应用启动引导 |
| `bundle/` | base、headless、web-app | 预配置 Bundle（cordis.patch.yml 组合） |
| `typert/` | typert-registry、typert-protocol、typert-loader、typert-generator | 类型运行时系统 |
| `util/` | timeout、brand、atomic-write、home-paths、output-retention、native-command、launch-environment | 通用工具 |
| `preset/` | persona | 预设（人格等） |
| `sandbox/` | sandbox-policy、sandbox-windows-acl | 沙箱策略 |
| `test-support/` | llm-mock-server、llm-replay、client-runtime、acp-snapshot、agent-loop-testkit、loader-smoke | 测试支持工具 |
| `examples/` | acp-demo、jsonrpc-demo、agent-spine-demo | 示例 |

---

## 关键文件清单

> 以下列出核心源码文件（≥25 个），按功能域分组。所有路径相对于源码根 `external/libs/models/ai/deepseek-harness/`。

### 项目配置与构建

| 文件 | 内容 |
|------|------|
| package.json | 根工作区配置，定义所有脚本命令（build/test/lint/gen-*/verify-*）和 devDependencies |
| pnpm-workspace.yaml | pnpm 工作区 glob、overrides、allowBuilds 白名单、patchedDependencies |

### Core — Agent 核心

| 文件 | 内容 |
|------|------|
| packages/core/agent/src/index.ts | `AgentRegistry` Cordis Service（agent 创建/注册/生命周期），Context 声明合并（`ctx.agents`/`ctx.agent`），`CreateAgentOptions`/`AgentSetup` 接口 |
| packages/core/agent/src/runtime-types.ts | `Agent` 接口、`AgentOptions` 接口、`AgentStatus` 类型枚举，Events 声明合并（agent/error、agent/inbox/claimed） |
| packages/core/agent/src/inbox.ts | `Inbox` 类（消息队列管理：append/prepend/replace/remove/splice） |
| packages/core/agent/src/dispatch.ts | `AgentSubjectEvent`/`AgentEventDispatch` 接口，`agentEvents`/`agentCarrier`/`emitAgentEvent` 事件总线 |
| packages/core/agent/src/types.ts | `InboxTarget` 类型，`SessionEventMap` 声明合并（agent/inbox/spliced 事件） |

### Core — 工具系统

| 文件 | 内容 |
|------|------|
| packages/core/tools/src/index.ts | `ToolRuntime` Cordis Service（工具注册/执行/呈现管道：pre/guard/around/post/result），工具命名空间作用域 |
| packages/core/tools/src/schema.ts | `defineTool` 函数、`validateArgs` 函数、`ValueSchemaSpec`/`ParameterSchemaSpec` 接口（工具参数 Schema 描述） |
| packages/core/tools/src/code-mode.ts | `createRunCodeTool` 函数（Code Mode 执行器），`RUN_CODE_NAME` 常量，SDK section 渲染器映射（TypeScript/Python） |
| packages/core/tools/src/types.ts | `CodeDispatchStartEventData`/`CodeDispatchEventData` 接口，SessionEventMap 扩展（tool/code-dispatch 事件） |

### Core — 会话与作用域

| 文件 | 内容 |
|------|------|
| packages/core/session/src/index.ts | `Session` 类和 `SessionStore` 类（会话创建、事件追加、派生消息生成） |
| packages/core/session/src/types.ts | `SessionId`/`SessionHeader` 类型、`SessionEventMap` 接口（session 全生命周期事件） |
| packages/core/scope/src/index.ts | `ScopeKey` 类型、`Scoped` 接口，scoped context/carrier 创建函数 |
| packages/core/scope/src/store.ts | `NamedEntries`/`AnonymousEntries`/`ScopedLayers` 类（作用域内注册条目分层管理） |

### LLM 抽象层

| 文件 | 内容 |
|------|------|
| packages/llm/llm/src/index.ts | `LlmRuntime` Cordis Service 和 `LlmAdapter` 抽象类，瀑布式 `llm/stream` 事件、`LlmError` 类 |
| packages/llm/llm/src/types.ts | `ContentBlock` 联合类型（text/reasoning/tool-call/tool-result/image）、`StreamChunk` 联合类型、`GenerateOptions` 接口、`TokenUsage`/`FinishReason` |
| packages/llm/llm/src/assembler.ts | `BlockAssembler` 类（增量组装 StreamChunk→ContentBlock→assistant Message，处理 6 种 chunk 类型） |
| packages/llm/llm/src/message.ts | `Message`/`UserMessage`/`AssistantMessage`/`ToolResultMessage` 接口，`MessageSource` 判别联合，消息工厂函数（freeze/create） |
| packages/llm/llm/src/error.ts | `HarnessError` 类（机器可路由 code 字段），错误码常量（CONTEXT_WINDOW_EXCEEDED/QUOTA/EMPTY_RESPONSE/INVALID_CREDENTIAL），`errorChain` 函数 |
| packages/llm/llm/src/call-config.ts | `LlmCallConfig` 接口、`callConfigEquals` 函数、`deepFreeze` 函数、agent loop 请求标记 |
| packages/llm/llm/src/retry-policy.ts | 重试策略（BackoffConfig/RetryPolicyConfig）、默认常量、`RetryPolicySchema`/`resolveRetryPolicy` |
| packages/llm/llm-pi-ai/src/index.ts | PI-AI 适配器插件（name='llm-pi-ai', inject=['llm']），memoized profiles、热更新、API Key 解析 |
| packages/llm/llm-pi-ai/src/stream.ts | PI-AI SSE 流转换：`toStreamChunks` async generator、错误分类、stop reason 映射、usage 映射 |
| packages/llm/llm-pi-ai/src/config.ts | `PiAiProviderProfile` 接口（20+ 字段）、Config schema、`resolveProfiles` 验证函数 |

### MCP / ACP / SDK 协议层

| 文件 | 内容 |
|------|------|
| packages/mcp/mcp-client/src/index.ts | MCP 客户端插件（name='mcp-client', inject=['tools']），stdio/HTTP 传输配置、serverName 命名空间防冲突 |
| packages/acp/acp/src/index.ts | ACP 服务端插件（name='acp', inject=['agents']），AcpAgent、SessionRecord、quiesce 关闭、JSON-RPC over stdio |
| packages/sdk/protocol/src/index.ts | `JsonRpcLineTransport` 类（换行分隔 JSON-RPC over stdio）、`JsonRpcResponseError` 类 |
| packages/sdk/protocol/src/types.ts | SDK 协议类型：InitializeParams/Result、SessionPromptParams/Result、4 种服务端通知、Request/Notification Map |
| packages/sdk/client/src/client.ts | `HarnessClient` 类（子进程 spawn、stdio 传输、通知分发、stderr 缓冲、shutdown→SIGTERM→SIGKILL dispose ladder） |
| packages/sdk/client/src/api.ts | `DeepSeekHarness` 和 `HarnessSession` 高层 API |
| packages/sdk/server/src/index.ts | SDK JSON-RPC 服务端插件（name='sdk-jsonrpc-server', inject=['agents']），shutdown→flush→dispose→exit(0) 优雅关闭 |

### 文件系统 / Shell / LSP

| 文件 | 内容 |
|------|------|
| packages/fs/tool-fs/src/index.ts | FS 工具插件（name='tool-fs', inject=['tools','fs','systemPrompt']），read/write/edit/read_image 工具注册、FsSandboxController |
| packages/fs/fs/src/index.ts | `ctx.fs` 文件系统 Service 定义 |
| packages/shell/shell/src/index.ts | `ShellExecutor` 抽象类（abstract resolve/run/start）、SHELL_SETTINGS_NAMESPACE、Context 声明合并 |
| packages/lsp/lsp/src/index.ts | `Lsp` Service 类（provider 原子注册、扩展名路由、finalExtension 辅助函数）、`LspError` |

### Web 客户端

| 文件 | 内容 |
|------|------|
| packages/client/web/src/boot.tsx | `AppWebEntry` 启动内核（两阶段启动、模块系统、prefetch、Loader、assertEntriesActive） |
| packages/client/web/src/AppRoot.tsx | `AppRoot` React 组件（boot gate、useSyncExternalStore 订阅 signal、失败报告） |
| packages/client/web/src/app.tsx | `buildRenderApp` 渲染工厂（slots.renderSlot('root')） |

---

## 核心类 / 接口 / 插件定义索引

### Cordis Service 类（挂载在 Context 上）

| 类名 | 所在包 | Context 属性 | 核心方法 |
|------|--------|-------------|---------|
| `AgentRegistry` | core/agent | `ctx.agents` | create()、register 生命周期管理 |
| `Agent`（接口） | core/agent | `ctx.agent`（可选） | — |
| `ToolRuntime` | core/tools | `ctx.tools` | defineTool 注册、execute 执行、工具呈现管道 |
| `Session` / `SessionStore` | core/session | —（由 Agent 持有） | 事件追加、派生消息、JSON 序列化 |
| `LlmRuntime` | llm/llm | `ctx.llm` | generate（流式）、adapter 注册、waterfall 事件链 |
| `LlmAdapter`（抽象类） | llm/llm | — | stream() 抽象方法，Provider 后端实现 |
| `Lsp` | lsp/lsp | `ctx.lsp` | registerProvider()、query() |
| `ShellExecutor`（抽象类） | shell/shell | `ctx.shell` | abstract resolve()、run()、start() |
| `FsService` | fs/fs | `ctx.fs` | 文件读写抽象 |

### 核心数据类

| 类名 | 所在文件 | 职责 |
|------|---------|------|
| `Inbox` | core/agent/src/inbox.ts | 待处理消息队列管理（append/prepend/replace/remove/splice） |
| `BlockAssembler` | llm/llm/src/assembler.ts | 流式块增量组装（StreamChunk→ContentBlock→Message） |
| `HarnessError` | llm/llm/src/error.ts | 错误基类（code 字段机器可路由，支持 cause 链） |
| `LlmError` | llm/llm/src/index.ts | LLM 特化错误（含 HTTP status、retryAfter、requestId） |
| `LspError` | lsp/lsp/src/index.ts | LSP 错误（LSP_INVALID_PROVIDER/LSP_CONFLICT/LSP_UNAVAILABLE 等） |
| `HarnessClient` | sdk/client/src/client.ts | TypeScript SDK 客户端（子进程+stdio+JSON-RPC） |
| `JsonRpcLineTransport` | sdk/protocol/src/index.ts | 换行分隔 JSON-RPC 传输 |
| `AppWebEntry` | client/web/src/boot.tsx | Web 启动内核 |
| `ScopedLayers` / `NamedEntries` / `AnonymousEntries` | core/scope/src/store.ts | 作用域分层注册 |

### 核心接口与类型

| 接口/类型 | 所在文件 | 关键字段 |
|-----------|---------|---------|
| `Message` | llm/llm/src/message.ts | id, role, content: ContentBlock[], source: MessageSource |
| `ContentBlock`（联合） | llm/llm/src/types.ts | text \| reasoning \| tool-call \| tool-result \| image |
| `StreamChunk`（联合） | llm/llm/src/types.ts | block-start \| *-delta \| block-end \| usage \| finish |
| `GenerateOptions` | llm/llm/src/types.ts | messages, config, signal, ... |
| `LlmCallConfig` | llm/llm/src/call-config.ts | provider, model, reasoningEffort, temperature, maxTokens, stop |
| `AgentOptions` | core/agent/src/runtime-types.ts | sessionId, cwd, model 配置等 |
| `ValueSchemaSpec` / `ParameterSchemaSpec` | core/tools/src/schema.ts | 工具参数 JSON Schema 描述 |
| `ShellExecRequest` / `ShellExecSpec` / `ShellRunResult` | shell/shell/src/types.ts | Shell 执行请求/结果类型 |
| `LspQueryRequest` / `LspQueryResult` | lsp/lsp/src/types.ts | LSP 查询（goToDefinition/findReferences/hover/implementation） |
| `LspProvider` | lsp/lsp/src/types.ts | id, extensionToLanguage, query() |

### Cordis 插件定义索引

| 插件 name | inject | 所在包 | 职责 |
|-----------|--------|--------|------|
| `llm-pi-ai` | `['llm']` | llm/llm-pi-ai | 注册 PI-AI Provider 适配器 |
| `mcp-client` | `['tools']` | mcp/mcp-client | 连接 MCP 服务器并桥接工具 |
| `acp` | `['agents']` | acp/acp | 启动 ACP JSON-RPC stdio 服务端 |
| `sdk-jsonrpc-server` | `['agents']` | sdk/server | 启动 SDK JSON-RPC stdio 服务端 |
| `tool-fs` | `['tools','fs','systemPrompt']` | fs/tool-fs | 注册 read/write/edit/read_image 工具 |
| （Shell 实现插件） | `['shell']` | shell/bash-local, shell/pwsh-local 等 | 提供具体 Shell 执行器实现 |
| （LSP stdio 插件） | `['lsp']` | lsp/lsp-stdio | 启动 LSP stdio 子进程 |
| （tool-lsp） | `['tools','lsp']` | lsp/tool-lsp | 注册 LSP 查询工具 |
| （tool-bash/tool-pwsh） | `['tools','shell',...]` | shell/tool-bash, shell/tool-pwsh | 注册 Shell 执行工具 |

---

## Cordis 插件注册模式说明

deepseek-harness 的所有功能包都遵循统一的 **Cordis 插件导出模式**。这是理解整个项目架构的关键。

### 插件导出契约

每个功能插件包的 `src/index.ts` 使用**命名导出**（**不使用 default export**），导出以下固定成员：

```typescript
// 1. 插件名（用于加载器诊断和 HMR）
export const name = 'plugin-name'

// 2. 依赖声明（该插件运行需要的 Context Service）
export const inject = ['required-service-a', 'required-service-b']

// 3. 配置 Schema（可选，使用 @deepseek-ai/schemastery 定义）
export interface Config {
  someOption?: string
}
export const Config: Schema<Config> = Schema.object({
  someOption: Schema.string().default('default-value'),
})

// 4. 插件入口函数（同步或异步）
export function apply(ctx: Context, config: Config): void {
  // 在这里执行：注册 Service、注册工具、监听事件、创建子 Fiber、注册清理 effect
  const resolved = config as Required<Config>

  // 注册 Service 到 Context（会自动处理重复注册错误）
  ctx.service('myService', MyServiceClass)

  // 使用 ctx.effect 管理资源生命周期
  ctx.effect(() => {
    // setup: 注册监听器、启动连接等
    const handler = ctx.on('some/event', () => { ... })
    return () => {
      // cleanup: 取消监听、关闭连接等（Fiber dispose 时自动调用）
      handler.dispose()
    }
  }, 'effect-description')

  // 条件注入：可选依赖仅在挂载时生效
  ctx.inject(['optionalService'], (optCtx) => {
    // optCtx.optionalService 一定可用
  })
}
```

### Context 声明合并模式

Service 包通过 TypeScript **declaration merging** 在 `@deepseek-ai/cordis` 模块上扩展 Context 类型，使得 `ctx.xxx` 获得类型安全：

```typescript
declare module '@deepseek-ai/cordis' {
  interface Context {
    myService: MyServiceClass  // ctx.myService 可被类型检查
  }
  interface Events {
    // 瀑布事件：this 绑定到 Service，next() 调用链
    'my/stream'(this: MyServiceClass, options: Opts, next: () => AsyncIterable<Chunk>): AsyncIterable<Chunk>
    // 普通事件：观察者模式
    'my/event'(data: EventData): void
  }
}
```

### Service 定义模式

抽象能力缝（如 shell、fs、lsp）使用**抽象 Service 类**，具体实现作为插件注册：

```typescript
export abstract class MyService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'myService')  // 注册名为 'myService'
  }
  abstract doSomething(): Promise<Result>
}
```

具体实现插件在 `apply()` 中通过 `ctx.service('myService', ConcreteImpl, true)` 注册为该抽象 Service 的实例。

### 事件总线模式

- **瀑布事件（waterfall）**：如 `llm/stream`，通过 `next()` 传递控制，可短路或包装下游结果
- **普通事件**：如 `session/event`、`agent/error`，多播观察者模式
- **Scoped Events**：Agent 级别的事件通过 `agentEvents`/`agentCarrier` 限定在 Agent 作用域内，避免全局污染

### Bundle 组合模式

Bundle 包（如 `bundle/base`、`bundle/headless`、`bundle/web-app`）通过 `cordis.patch.yml` 声明一组预配置的插件组合，其 `src/index.ts` 仅做 `export {}` 占位：

```yaml
# cordis.patch.yml
plugins:
  - name: @deepseek-ai/dsh-agent
  - name: @deepseek-ai/dsh-session
  - name: @deepseek-ai/dsh-scope
  - name: @deepseek-ai/dsh-tools
  - name: @deepseek-ai/dsh-llm
  # ...更多插件
```

### 生命周期模式

1. **加载（Load）**：Cordis Loader 读取 `cordis.yml`，解析插件依赖拓扑
2. **应用（Apply）**：按拓扑顺序调用各插件的 `apply(ctx, config)`，config 经过 schemastery 默认值填充和校验
3. **Effect 注册**：`apply` 中通过 `ctx.effect()` 注册资源清理函数
4. **运行（Run）**：所有插件就绪后触发就绪事件，应用开始服务
5. **销毁（Dispose）**：Fiber dispose 时逆序调用所有 effect 清理函数（连接关闭、监听器移除、子进程终止）

### 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| npm 包名 | `@deepseek-ai/dsh-<kebab-case>` | `@deepseek-ai/dsh-mcp-client` |
| 插件 name | kebab-case，与包名对应 | `mcp-client` |
| Service 名 | camelCase | `ctx.llm`, `ctx.tools`, `ctx.shell` |
| 事件名 | `<domain>/<action>` | `llm/stream`, `tool/code-dispatch`, `agent/error` |
| 工具名 | 下划线或命名空间前缀 | `mcp__<server>__<tool>`, `read`, `write`, `run_code` |
| 设置命名空间 | `settingsNamespace('name')` | `SHELL_SETTINGS_NAMESPACE = settingsNamespace('shell')` |

---

## 构建与验证

| 命令 | 用途 |
|------|------|
| `pnpm build:lib:host` | 构建 Host 端（tsc + tsdown） |
| `pnpm build:lib:client` | 构建 Client 端（tsc + tsdown） |
| `pnpm build:web` | 构建 Web 前端（Vite） |
| `pnpm test` | 运行所有 Vitest 单元测试 |
| `pnpm test:e2e` | 运行 E2E 测试 |
| `pnpm typecheck` | 类型检查 |
| `pnpm lint` | OxLint 代码检查 |
| `pnpm check:ci` | CI 综合检查 |
| `pnpm gen-cordis-catalog` | 生成 Cordis 插件目录 |
| `pnpm gen-tool-catalog` | 生成工具目录 |
| `pnpm dsh` | 运行 CLI（`node --import tsx apps/cli/src/bin.ts`） |
