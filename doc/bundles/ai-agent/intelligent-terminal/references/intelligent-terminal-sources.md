---
type: Reference
title: Intelligent Terminal (Windows Terminal Agent) 源码信源登记
description: Windows Terminal AI Agent 集成双进程架构、ACP 协议、COM 服务器、WTA 编排器源码路径与关键文件清单
tags: [intelligent-terminal, windows-terminal, wta, acp, agent, com, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: intelligent-terminal-github
    resource: https://github.com/microsoft/terminal (fork: intelligent-terminal)
    title: Intelligent Terminal GitHub 仓库
---

# Intelligent Terminal 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Intelligent Terminal（Windows Terminal AI Agent 集成） |
| 描述 | Windows Terminal 中集成 AI Agent Pane 的双进程架构实现，包含 C++ 宿主端（Terminal 集成 + COM 服务器）和 Rust WTA 编排器（master/helper/CLI） |
| 技术栈 | C++/WinRT（Terminal 宿主）、Rust（WTA 编排器 + TUI）、COM（经典接口）、JSON-RPC 2.0（ACP 协议） |
| 核心协议 | ACP (Agent Control Protocol) v1.3.0，基于 JSON-RPC 2.0 |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\intelligent-terminal\` |

## 架构概览

项目采用**双进程三角色**架构：

```
Windows Terminal 进程 (C++/WinRT)
├── N × Agent Pane (ConptyConnection)
│   └── N × wta-helper (Rust, TUI via Ratatui)
│       └── 命名管道 (\\.\pipe\wta-master-<GUID>)
└── 1 × SharedWta 单例
    └── 1 × wta-master (Rust, ACP 多路复用器)
        └── stdio ──→ 1+ × Agent CLI (copilot/claude/codex/gemini/opencode)
```

- **wta-master**：单例，由 SharedWta 通过 Job Object 管理，拥有 agent CLI 子进程，在命名管道上监听 helper 连接
- **wta-helper**：每个 Agent Pane 一个，作为 conpty 子进程运行，TUI 渲染 + ACP client
- **wtcli.exe**：C++ CLI 工具，通过 COM 接口控制 WT，由 wta 作为子进程调用

## 核心目录结构

| 目录/文件 | 用途 | 语言 |
|-----------|------|------|
| `src/cascadia/TerminalApp/` | Terminal 主应用 Agent 集成（AgentPane、SharedWta、Tab、CommandPalette） | C++/XAML |
| `src/cascadia/TerminalProtocol/` | WinRT IDL 定义 + 协议解析 | C++/IDL |
| `src/cascadia/WindowsTerminal/` | COM 服务器实现、窗口管理 | C++ |
| `src/cascadia/TerminalSettingsModel/` | Agent 相关设置宏定义 | C++ |
| `src/cascadia/inc/` | 公共头文件（WtaProcess、IntelligentTerminalPaths、BoundedDispatchQueue） | C++ |
| `src/host/proxy/` | 经典 COM 接口 IDL（ITerminalProtocol） | IDL |
| `src/tools/wtcli/` | wtcli.exe CLI 工具 | C++ |
| `src/cascadia/CascadiaPackage/AgentIcons/` | Agent Logo SVG 资源 | SVG |
| `tools/wta/src/` | Rust WTA 编排器源码 | Rust |
| `tools/wta/src/master/` | wta-master ACP 多路复用器 | Rust |
| `tools/wta/src/helper/` | wta-helper TUI 运行时 | Rust |
| `tools/wta/src/protocol/acp/` | ACP 协议实现（client/conn/spawn） | Rust |
| `tools/wta/src/shell/wt_channel/` | wtcli COM 通道封装 | Rust |
| `tools/wta/src/cli/` | CLI 参数定义（clap） | Rust |
| `tools/wta/wt-agent-hooks/` | Shell hooks 插件（PowerShell） | PowerShell |
| `doc/specs/` | 设计文档（Multi-window-agent-pane 等） | Markdown |

## 关键文件清单

### C++ 宿主端（Terminal 集成）

| 文件 | 内容 |
|------|------|
| `src/cascadia/TerminalApp/SharedWta.h` | wta-master 进程生命周期管理单例（引用计数、Job Object、崩溃检测） |
| `src/cascadia/TerminalApp/SharedWta.cpp` | SharedWta 实现：spawn master、CREATE_SUSPENDED+ResumeThread、崩溃锁存、管道名生成 |
| `src/cascadia/TerminalApp/AgentPaneContent.idl/.h/.cpp` | Agent Pane XAML 控件（logo、名称/版本/状态顶栏） |
| `src/cascadia/TerminalApp/AgentPaneDragStash.h` | 跨窗口拖拽 agent pane 桥接机制 |
| `src/cascadia/TerminalApp/AgentPaneLog.h` | C++ 端 agent pane 诊断日志（header-only，原子追加） |
| `src/cascadia/TerminalApp/Tab.h/.cpp` | StashAgentPane/RestoreStashedAgentPane/HasStashedAgentPane |
| `src/cascadia/TerminalApp/TerminalPage.h/.cpp` | 主页面 Agent 集成、ProtocolVtSequenceReceived 事件、配置热重载 |
| `src/cascadia/TerminalApp/CommandPalette.cpp` | `?<prompt>` 命令面板委托分发 |
| `src/cascadia/TerminalSettingsModel/MTSMSettings.h` | 所有 Agent 相关设置宏（acpAgent、autoFixEnabled、agentPanePosition 等） |
| `src/cascadia/inc/WtaProcess.h` | wta.exe 路径解析、进程 spawn、PATH 刷新 |
| `src/cascadia/inc/IntelligentTerminalPaths.h` | 日志/数据目录解析（打包/未打包双路径） |
| `src/cascadia/inc/BoundedDispatchQueue.h` | COM 事件投递有界 FIFO 队列 |

### COM 协议层

| 文件 | 内容 |
|------|------|
| `src/cascadia/WindowsTerminal/TerminalProtocolComServer.h/.cpp` | COM 服务器实现：类厂注册、事件队列、SendEvent 路由 |
| `src/host/proxy/ITerminalProtocol.idl` | 经典 COM 接口定义（ITerminalProtocol + ITerminalProtocolEventSink） |
| `src/cascadia/TerminalProtocol/TerminalProtocol.idl` | WinRT IDL 数据结构（WindowInfo/TabInfo/PaneInfo/PaneOutput/ProcessStatus） |
| `src/cascadia/TerminalProtocol/ProtocolParsing.h` | 纯解析函数：SendEvent 路由分类、SplitDirection 映射 |

### Rust WTA 编排器

| 文件 | 内容 |
|------|------|
| `tools/wta/src/main.rs` | 入口点，CLI 模式分发 |
| `tools/wta/src/cli/args.rs` | clap CLI 参数定义（--master/--connect-master/--agent/--acp-model 等） |
| `tools/wta/src/master/mod.rs` | wta-master 核心：ACP 多路复用、session 路由、notif 反压、多 agent CLI 支持 |
| `tools/wta/src/helper/mod.rs` + `helper/runtime.rs` | wta-helper TUI 运行时、Pane 身份发现（PID 匹配） |
| `tools/wta/src/protocol/acp/client.rs` | ACP 客户端（管道连接重试、指数退避） |
| `tools/wta/src/protocol/acp/conn.rs` | ACP 连接兼容层（ClientLink/AgentLink 请求方法定义） |
| `tools/wta/src/protocol/acp/spawn.rs` | Agent CLI 进程 spawn 逻辑 |
| `tools/wta/src/agent_registry.rs` | 内置 Agent 配置表（copilot/claude/codex/gemini/opencode/custom） |
| `tools/wta/src/agent_hooks_installer.rs` | Hooks 插件自动安装/升级 |
| `tools/wta/src/shell/wt_channel/cli_channel.rs` | CliChannel：通过 wtcli.exe 子进程执行 WT 操作 |
| `tools/wta/src/app.rs` | Ratatui TUI 应用（~7000+ 行 reducer） |
| `tools/wta/src/app_contracts/event.rs` | AppEvent 枚举（UI 事件、连接事件、消息流、权限、WT 事件等） |
| `tools/wta/src/runtime_paths.rs` | 运行时路径解析（STATE root / LOCAL cache root） |
| `tools/wta/src/logging.rs` | 结构化日志初始化 |
| `tools/wta/src/session_registry.rs` + `agent_sessions.rs` | 会话注册/管理 |

### wtcli CLI 工具

| 文件 | 内容 |
|------|------|
| `src/tools/wtcli/main.cpp` | wtcli 入口 |
| `src/tools/wtcli/wtcli_functions.h` | wtcli 命令实现、键名翻译（TranslateKeys）、SendEvent JSON 封装 |

## 核心概念与关键数据结构索引

### 双进程架构

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| `SharedWta` 单例 | `TerminalApp/SharedWta.h` | 引用计数管理 wta-master 生命周期，AcquirePane/ReleasePane |
| `wta-master` 角色 | `tools/wta/src/master/mod.rs` | ACP 多路复用器，拥有 agent CLI，路由 helper 请求/通知 |
| `wta-helper` 角色 | `tools/wta/src/helper/mod.rs` | 每个 Agent Pane 一个，TUI 渲染，通过命名管道连接 master |
| Job Object 容器 | `SharedWta.cpp:361-387` | `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`，退出时自动终止后代 |
| 崩溃锁存 | `SharedWta.h:122-133` | `_degraded = true`，防止裂脑，需 `/restart` 恢复 |
| Pre-warm 机制 | `AGENTS.md:74-85` | 隐藏 stashed agent pane，后台完成 ACP 握手 |

### ACP 协议

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| ACP v1.3.0 | `tools/wta/Cargo.toml` | 基于 JSON-RPC 2.0 |
| 两跳传输 | `master/mod.rs:21-37` | master↔agent(stdio) + helper↔master(命名管道) |
| `session_to_helper` 映射 | `master/mod.rs:70-143` | HashMap<SessionId, HelperRoute>，含 notif_tx 有界通道(1024) |
| ClientLink 方法 | `protocol/acp/conn.rs:117-150` | initialize/authenticate/new_session/load_session/prompt/set_session_model |
| AgentLink 转发方法 | `protocol/acp/conn.rs:30-42` | request_permission/create_terminal/terminal_output/read_text_file/write_text_file 等 |
| 多 Agent CLI | `master/mod.rs:185-200` | AgentCmdKey 映射，支持同一窗口不同 agent |
| `AgentProfile` 结构 | `agent_registry.rs:29-81` | Agent 配置：id/display_name/exe/acp_flags/auth_flow 等 |
| `AgentFailure` 类型 | `protocol/acp/failure.rs` | 认证/握手/连接失败分类 |

### COM 协议

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| `ITerminalProtocol` | `host/proxy/ITerminalProtocol.idl` | 经典 COM 接口，IID: `9C7E2A14-3B5D-4F8A-A2C9-1E4F6B8D0A3C` |
| `ITerminalProtocolEventSink` | `host/proxy/ITerminalProtocol.idl` | OnEvent 回调，IID: `3D8F4B26-5C7E-4A9B-B1D0-2F5A7C9E1B4D` |
| CLSID 按 branding 区分 | `TerminalProtocolComServer.h:17-27` | Release/Preview/Canary/Dev 各有独立 CLSID |
| COM 发现机制 | `AGENTS.md:9` | 环境变量 `WT_COM_CLSID` 注入 pane shells |
| 事件投递异步化 | `TerminalProtocolComServer.h:78-118` | 每 Subscriber 有界 FIFO 队列(4096) + 专用 MTA worker |
| SendEvent 路由分类 | `TerminalProtocol/ProtocolParsing.h:32-122` | autofix_state/agent_status/switch_agent/close_agent_pane 等 10 类 |

### UI 集成

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| `AgentPaneContent` | `TerminalApp/AgentPaneContent.idl` | XAML UserControl，36px 顶部栏 + TerminalPaneContent |
| Agent Logo 匹配 | `AgentPaneContent.cpp:23-46` | 大小写不敏感子串匹配：Copilot/Claude/Gemini/Codex/OpenCode |
| Stash/Restore 模式 | `Tab.h:105-123` | Toggle 时 stash 而非销毁，保留 session/chat history |
| `AutofixState` 枚举 | `AgentPaneContent.h:37-53` | Idle/Detected/Pending/Executing |
| AppEvent 枚举 | `app_contracts/event.rs:5-185` | Rust TUI reducer 事件类型（20+ 变体） |

### 运行时数据

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| STATE root | `IntelligentTerminalPaths.h:26-102` | `%LOCALAPPDATA%\...\LocalState\IntelligentTerminal\`（持久化） |
| LOCAL/cache root | 同上 | `%LOCALAPPDATA%\...\LocalCache\Local\IntelligentTerminal\`（临时） |
| master-pipe.txt | `master/mod.rs:52` | STATE root 下的管道名发现文件 |
| 日志文件清单 | `AGENTS.md:264-288` | wta-main_master.log、wta-main_helper-{pid}.log 等 10 种日志 |
| Hooks 自动升级 | `agent_hooks_installer.rs` | 启动时检查 bundle 版本，仅升级已安装 hooks |

## ACP 请求方法一览

**Helper → Agent（经 Master 转发）**：
`initialize`、`authenticate`、`new_session`、`load_session`、`prompt`、`set_session_model`

**Agent → Helper（经 Master 路由）**：
`request_permission`、`create_terminal`、`terminal_output`、`wait_for_terminal_exit`、`release_terminal`、`kill_terminal`、`read_text_file`、`write_text_file`

## ITerminalProtocol COM 方法分类

| 分类 | 方法 |
|------|------|
| Meta | `Authenticate(token)`、`GetCapabilities()` |
| Queries | `GetActivePane()`、`ListWindows()`、`ListTabs()`、`ListPanes()`、`ReadPaneOutput()`、`GetProcessStatus()`、`GetSessionVariable()`、`GetSettings()` |
| Mutations | `CreateTab()`、`SplitPane()`、`ClosePane()`、`SendInput()`、`FocusPane()`、`SetSessionVariable()` |
| Events | `Subscribe(sink)`、`Unsubscribe()`、`SendEvent(eventJson)` |

## 内置 Agent 注册表

| Agent ID | 启动命令 | Auth |
|----------|---------|------|
| copilot | `copilot --acp --stdio` | External |
| claude | `npx -y @agentclientprotocol/claude-agent-acp` | ACP adapter |
| codex | `npx -y @agentclientprotocol/codex-acp@1.1.4` | ACP adapter |
| gemini | `gemini --experimental-acp` | — |
| opencode | plugin.json 配置 | — |
| custom | `custom:<cmd>` 用户自定义 | — |
