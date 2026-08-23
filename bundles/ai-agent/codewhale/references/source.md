---
type: reference
scope: codewhale
name: source
description: "CodeWhale 关键源文件索引，按 crate 组织，标注对应的事实 ID"
---

# CodeWhale 源文件参考

本索引按 crate 组织 CodeWhale 的关键源文件，标注每个文件相关的事实 ID，便于从概念文档追溯到源码。

## 工作区根目录

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `Cargo.toml` | Workspace 定义、21 个成员、版本 0.9.10、edition 2024、profile 配置 | F-001 ~ F-007 |
| `README.md` | 项目介绍、安装方式、功能特性、项目历史 | F-104, F-105 |
| `AGENTS.md` | Agent 工作规则、当前契约、BASE_PROMPT 位置、subagent 工具名 | F-079, F-095 |

## crates/core（核心运行时）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/core/Cargo.toml` | Core crate 依赖：agent, config, execpolicy, hooks, mcp, protocol, state, tools | F-008 |
| `crates/core/src/lib.rs` | Runtime 结构体、ThreadManager、JobManager、线程/任务生命周期 | F-026, F-031, F-032, F-033, F-034, F-035 |
| `crates/core/src/session.rs` | Thread/Session 分离、Journal 游标、messages_revision | F-027 |
| `crates/core/src/engine/mod.rs` | EngineHandle、EngineConfig、spawn_engine、Op/EventMsg channel | F-028, F-029, F-030, F-083 |
| `crates/core/src/journal.rs` | Append-only Journal，分支只移动 leaf | F-027 |
| `crates/core/src/request.rs` | Prompt 请求构建 | F-026 |
| `crates/core/src/tool_parser.rs` | 工具调用解析 | F-026 |

## crates/agent（模型注册）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/agent/Cargo.toml` | 仅依赖 config 和 serde | F-009 |
| `crates/agent/src/lib.rs` | ModelFamily、ModelInfo、ModelRegistry、内置模型目录 | F-080, F-081, F-082, F-083 |

## crates/mcp（MCP 协议）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/mcp/Cargo.toml` | MCP crate 依赖 | F-011 |
| `crates/mcp/src/lib.rs` | McpServerConfig、ToolFilter、McpManager、McpManagedClient、stdio JSON-RPC 服务器、qualify_tool_name、sanitize_component | F-036 ~ F-044 |
| `crates/mcp/src/stdio_client.rs` | ChildProcessMcpClient 子进程 MCP 客户端 | F-038 |

## crates/tools（工具系统）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/tools/Cargo.toml` | Tools crate 依赖 protocol, async-trait, tokio, uuid | F-012 |
| `crates/tools/src/lib.rs` | ToolCapability、ToolRegistry、ToolHandler、ToolCallRuntime、ToolDescriptor、FunctionCallError、参数提取器 | F-046 ~ F-053 |
| `crates/tools/src/outcome.rs` | ToolExecutionOutcome、ToolTerminalStatus | F-046 |
| `crates/tools/src/prepared.rs` | PreparedToolCall | F-046 |
| `crates/tools/src/resources.rs` | ResourceClaim、schedule_non_conflicting | F-046 |

## crates/execpolicy（执行策略）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/execpolicy/Cargo.toml` | 依赖 protocol 和 serde | F-016 |
| `crates/execpolicy/src/lib.rs` | RulesetLayer、PermissionAction、ToolAskRule、AskForApproval、ExecPolicyEngine、denied_prefix_matches、shell_expand | F-059 ~ F-064 |
| `crates/execpolicy/src/approval_mode.rs` | ApprovalMode 定义 | F-059 |
| `crates/execpolicy/src/bash_arity.rs` | BashArityDict 参数数量感知匹配 | F-063 |
| `crates/execpolicy/src/shell_expand.rs` | Shell 命令展开检测绕过 | F-064 |

## crates/hooks（Hook 系统）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/hooks/Cargo.toml` | 依赖 protocol, release, reqwest, async-trait, tokio | F-017 |
| `crates/hooks/src/lib.rs` | HookEvent、HookSink trait、StdoutHookSink、JsonlHookSink、WebhookHookSink、UnixSocketHookSink、HookDispatcher | F-054 ~ F-057 |

## crates/workflow（工作流 IR）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/workflow/Cargo.toml` | 依赖 serde, serde_json, sha2, thiserror, toml | F-018 |
| `crates/workflow/src/lib.rs` | WorkflowSpec、WorkflowNode（8 种）、AgentType、IsolationMode、WorkflowPlan、PromotionGate | F-066 ~ F-070 |
| `crates/workflow/src/gates.rs` | GateSpec、LaneGateBoard、stopship_gate_pipeline | F-066 |
| `crates/workflow/src/replay.rs` | 工作流回放 | F-072 |
| `crates/workflow/src/js_authoring.rs` | JS/TS 工作流编译 | F-071 |

## crates/workflow-js（JS 工作流运行时）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/workflow-js/Cargo.toml` | 使用 rquickjs 0.12，Android/FreeBSD/NetBSD/OpenHarmony 使用 bindgen | F-019 |
| `crates/workflow-js/src/lib.rs` | WorkflowDriver trait、WorkflowVm、VmLimits、WORKFLOW_LIFETIME_CAP=1000、JS 全局函数文档 | F-071, F-072, F-073 |
| `crates/workflow-js/src/vm.rs` | QuickJS VM 实现、task/parallel/pipeline 全局函数 | F-071, F-072 |
| `crates/workflow-js/src/driver.rs` | WorkflowDriver、TaskRequest、TaskCompletion、BudgetSnapshot | F-072 |
| `crates/workflow-js/src/schema.rs` | JSON Schema 验证 | F-072 |

## crates/protocol（协议层）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/protocol/Cargo.toml` | 仅依赖 chrono, serde, serde_json, uuid | F-013 |
| `crates/protocol/src/lib.rs` | Status trait、ThreadStatus、SessionSource、Thread、Envelope | F-109, F-110 |
| `crates/protocol/src/op.rs` | Op 枚举、OpEnvelope（Engine 输入） | F-028 |
| `crates/protocol/src/event_msg.rs` | EventMsg 枚举（Engine 输出） | F-028 |
| `crates/protocol/src/fleet.rs` | Fleet 协议类型 | F-074 |
| `crates/protocol/src/ids.rs` | ThreadId、SessionId 类型 | F-027 |
| `crates/protocol/src/journal.rs` | Journal 协议类型 | F-027 |
| `crates/protocol/src/workroom.rs` | Workroom 协议类型 | F-110 |

## crates/state（状态持久化）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/state/Cargo.toml` | 使用 rusqlite (bundled)、fd-lock | F-015 |
| `crates/state/src/lib.rs` | StateStore、ThreadMetadata、SessionSource、SESSION_INDEX_LOCK、消息树 | F-084 ~ F-087 |

## crates/config（配置）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/config/Cargo.toml` | 依赖 execpolicy, paths, secrets, fd-lock, toml, toml_edit | F-014 |
| `crates/config/src/lib.rs` | ConfigToml、ProviderKind、CliRuntimeOverrides、DEFAULT_SPAWN_DEPTH | F-014, F-077 |
| `crates/config/src/provider.rs` | Provider 配置 | F-082 |
| `crates/config/src/route/` | 模型路由配置模块 | F-014 |

## crates/tui（终端 UI）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/tui/Cargo.toml` | ratatui 0.30.2、crossterm 0.29、rmcp 2.2.0、schemaui、16 语言 | F-020, F-093 |
| `crates/tui/src/lib.rs` | TUI 库入口 | F-020 |
| `crates/tui/src/main.rs` | TUI 二进制入口 | F-020 |
| `crates/tui/src/core/engine.rs` | TUI 引擎（turn loop 当前所在） | F-026 |
| `crates/tui/src/prompts/text.rs` | BASE_PROMPT 唯一基础 prompt | F-095 |
| `crates/tui/src/fleet/` | Fleet TUI 模块：manager, roster, executor, profile 等 | F-074 |
| `crates/tui/src/skills/` | Skills TUI 模块：audit, install, roots, system | F-096 |
| `crates/tui/src/hooks/` | Hooks TUI 配置和执行器 | F-058 |
| `crates/tui/src/sandbox/` | Sandbox TUI：bwrap, policy | F-065 |
| `crates/tui/src/mcp/` | MCP TUI：stdio, http, sse, oauth, wire | F-045 |
| `crates/tui/locales/` | 16 种语言 JSON 翻译文件 | F-093 |

## crates/cli（命令行入口）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/cli/Cargo.toml` | 二进制 `codewhale`，mimalloc，父进程死亡清理 | F-010, F-107, F-108 |
| `crates/cli/src/main.rs` | CLI 主入口 | F-010 |
| `crates/cli/src/lib.rs` | CLI 库逻辑 | F-010 |

## crates/lane（Lane 注册）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/lane/Cargo.toml` | Lane registry 和 Runtime backends | F-021 |
| `crates/lane/src/lib.rs` | Lane 注册和运行时后端 | F-021 |
| `crates/lane/src/runtime.rs` | Runtime 后端实现 | F-021 |
| `crates/lane/src/worktree.rs` | Worktree 管理 | F-069 |

## crates/app-server（应用服务器）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/app-server/Cargo.toml` | axum, tower-http, 依赖 core/mcp/hooks/tools 等 | F-023 |
| `crates/app-server/src/lib.rs` | App-server 传输层 | F-023 |

## crates/secrets（密钥存储）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/secrets/Cargo.toml` | OS keyring 后端（macOS/Windows/Linux） | F-024 |
| `crates/secrets/src/lib.rs` | 密钥存储后端，keyring + 文件回退 | F-024 |

## crates/telemetry（遥测）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/telemetry/Cargo.toml` | 匿名使用计数，用户可禁用 | F-022 |
| `crates/telemetry/src/lib.rs` | 遥测事件和客户端 | F-022 |

## crates/paths（路径权威）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/paths/Cargo.toml` | 仅依赖 dirs | F-090 |
| `crates/paths/src/lib.rs` | CODEWHALE_APP_DIR、LEGACY_APP_DIR、路径解析 | F-090 |

## crates/release（版本发布）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/release/Cargo.toml` | 版本发现和比较 | F-022 相关 |
| `crates/release/src/install.rs` | 安装逻辑 | F-104 |
| `crates/release/src/tls.rs` | TLS 配置 | F-023 |

## crates/build-support（构建支持）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/build-support/Cargo.toml` | 共享构建脚本助手 | F-022 相关 |
| `crates/build-support/src/lib.rs` | 构建元数据嵌入 | F-022 相关 |

## crates/command-contract（命令契约）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `crates/command-contract/Cargo.toml` | 原型命令能力和调度形状 | F-025 |
| `crates/command-contract/src/lib.rs` | 命令契约定义 | F-025 |

## 关键文档

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `docs/GUIDE.md` | 用户指南、首次启动、doctor 命令 | F-088, F-089 |
| `docs/MCP.md` | MCP 配置、管理命令、插件 MCP | F-045 |
| `docs/FLEET.md` | Fleet 控制平面、CLI、profile 向导 | F-074, F-075 |
| `docs/MODES.md` | TUI 模式（Plan/Work/Operate）、权限姿态 | F-091, F-092 |
| `docs/HOOKS.md` | Hook 配置、11 个事件名、超时行为 | F-058 |
| `docs/SKILLS.md` | Skills 四层架构、根目录、slash 命令 | F-096, F-097 |
| `docs/SUBAGENTS.md` | 角色分类、权限 clamp、深度限制 | F-076, F-077, F-078 |
| `docs/SANDBOX.md` | Seatbelt/bwrap 沙箱、平台支持 | F-065 |
| `docs/PLUGINS.md` | 插件安装、trust/enable 生命周期 | F-098, F-099 |
| `docs/PROVIDERS.md` | 42 个 ProviderKind、选择方式 | F-082 |
| `docs/WEB.md` | 本地浏览器客户端、认证边界 | F-094 |
| `docs/CACHE.md` | KV-cache 前缀稳定性、PrefixStabilityManager | F-100, F-101 |
| `docs/MEMORY.md` | 原生记忆系统、Markdown + FTS5 | F-102, F-103 |
| `docs/INSTALL.md` | 平台支持矩阵、安装方式 | F-104 |
| `docs/DOCKER.md` | Docker 镜像、非 root 用户 | F-106 |
| `docs/RECEIPTS.md` | 运行时回执、review receipt | F-106 相关 |
| `docs/AGENT_RUNTIME.md` | Agent 运行时模型 | F-074 |
| `docs/WORKFLOW_AUTHORING.md` | 工作流编写指南 | F-066 |
| `docs/AUTHORIZATION_ORDER.md` | 授权策略栈 | F-065 |
| `docs/CONFIGURATION.md` | 配置参考 | F-088 |
