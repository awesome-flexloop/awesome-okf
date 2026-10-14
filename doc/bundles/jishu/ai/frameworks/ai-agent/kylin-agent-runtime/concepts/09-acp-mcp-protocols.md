---
type: Concept
title: 三大对外协议——ACP 编辑器代理、MCP 服务器与 LSP 诊断
description: HermesACPAgent 的 stdio-only ACP 服务、FastMCP 暴露的 10 个网关工具与 EventBridge 轮询、26 个内置 LSP ServerDef 的单例诊断服务及对比。
tags: [kylin-agent-runtime, acp, mcp, lsp, protocols]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 三大对外协议：ACP / MCP / LSP

> 术语速记：**ACP**（Agent Client Protocol，编辑器/IDE 与编码代理之间的协议）、**MCP**（Model Context Protocol，把外部能力暴露给模型客户端的工具协议）、**LSP**（Language Server Protocol，编程语言诊断协议）。

Kylin Agent Runtime 在对话 CLI 之外还说三种"外语"：作为 **ACP 代理**接入编辑器、作为 **MCP 服务器**把网关会话暴露给任意 MCP 客户端、作为 **LSP 客户端**拉起语言服务器为编辑动作提供诊断。三者方向不同、传输不同、入口也不同，本文逐一拆解并在末尾对比。

## ACP：stdio-only 的编辑器代理

**代理主类与信任模型。**

ACP 服务端代理 `class HermesACPAgent(acp.Agent)` 位于 acp_adapter/server.py:445，构造器 `__init__(self, session_manager=None)`（:516）（F-118）。模块注释明示该适配**仅支持 stdio 传输**（"ACP is stdio-only, local-trust"，server.py:860 附近注释）——即编辑器以子进程方式拉起代理，经标准输入输出通信，信任边界是本机用户，不做网络监听。

关键回调（F-118）：

- `on_connect`（:523）：客户端连入；
- `async initialize(...)`（:821）：初始化握手；
- `async authenticate(method_id, **kwargs)`（:855）：按方法 ID 返回认证方式；
- `_register_session_mcp_servers`（:750）：为会话登记可用的 MCP 服务器，使 ACP 会话内还能挂接 MCP 工具。

**会话、审批与事件。**

`acp_adapter/session.py` 提供 `SessionState`（:170）与 `SessionManager`（:186），并以 `_register_task_cwd`（:123）/ `_clear_task_cwd`（:158）登记每个任务的工作目录（F-120）。认证侧由 auth 模块的 `detect_provider` / `has_provider` / `build_auth_methods` 探测本机已有凭证；授权侧 `permissions.make_approval_callback` 生成审批回调，`edit_approval` 模块以 `EditProposal` / `maybe_require_edit_approval` 实现"编辑前审批"（F-120）；tools.py 负责会话级工具注册，配合 `_register_session_mcp_servers`，编辑器会话可以同时消费内置工具与外部 MCP 服务器（F-120）。事件回推有四个回调工厂（acp_adapter/events.py）：`make_tool_progress_cb`（:114）、`make_thinking_cb`（:189）、`make_step_cb`（:209）、`make_message_cb`（:266），分别推送工具进度、思考过程、步骤与消息。

**入口与注册清单。**

命令行入口 `hermes-acp` 指向 `acp_adapter.entry:main`（F-005）。`entry.main(argv=None)`（acp_adapter/entry.py:212）最终调用 `acp.run_agent(agent, use_unstable_protocol=True)`（:257）；参数解析支持 `--version`、`--check`（环境自检）、`--setup`、`--setup-browser`（entry.py:118-128）（F-119）。

分发注册文件 `acp_registry/agent.json` 声明（F-015）：

```json
{
  "id": "kylin-agent",
  "name": "KylinAgent",
  "version": "0.9.3",
  "distribution": {
    "uvx": {
      "package": "kylin-agent-runtime[acp]==0.9.3",
      "args": ["hermes-acp"]
    }
  }
}
```

即编辑器可用 uvx 按包串 `kylin-agent-runtime[acp]==0.9.3` 拉起，启动参数固定为 `hermes-acp`；license 为 MIT、authors 仍署 Nous Research——这是分发层品牌（KylinAgent）与符号层 Hermes 血缘并存的又一例证（洞察 I-3）。

## MCP：两个方向不同的 MCP 服务器

仓内有两个 MCP 服务器，不要混淆：

**1. 网关桥接服务器 mcp_serve.py（向外暴露网关能力）。**

`mcp_serve.py` 基于 `mcp.server.fastmcp.FastMCP`（:51 导入），工厂函数 `create_mcp_server(event_bridge=None)`（:450）创建服务器并注册 **10 个 `@mcp.tool()`**（行 471/528/561/618/670/699/733/769/823/839，计数见 Q-004）（F-121）。按源码函数名，10 个工具为：

| 工具 | 用途（函数名与 docstring 语义，mcp_serve.py:471-839） |
|---|---|
| `conversations_list` | 按平台列出会话 |
| `conversation_get` | 按 session_key 取单个会话详情 |
| `messages_read` | 读取会话消息 |
| `attachments_fetch` | 拉取附件 |
| `events_poll` / `events_wait` | 轮询/等待新事件（增量游标） |
| `messages_send` | 向目标会话发消息 |
| `channels_list` | 列出可用频道与投递目标 |
| `permissions_list_open` / `permissions_respond` | 列出/应答待审批请求 |

`class EventBridge`（mcp_serve.py:204）通过**轮询 SessionDB** 获取网关侧的新消息与事件，再经 `events_poll` / `events_wait` 分发给 MCP 客户端。启动函数是 `run_mcp_server(verbose=False)`（:866），**文件没有顶层 `main()`**（F-121）——它由其他入口（如 CLI/ACP 会话）装配调用，而非直接 `python mcp_serve.py`。

**2. Hermes 工具服务器 hermes_tools_mcp_server（向内暴露 Agent 工具）。**

`agent/transports/hermes_tools_mcp_server.py` 提供 `_build_server`（:108）与 `main`（:197），方向与前者相反：把 Hermes 自身的工具集包装成 MCP，供外部 MCP 客户端把这套 Agent 工具当后端调用（F-122）。它与 Codex app server 三件套同属 `agent/transports/` 传输适配层。

## LSP：26 个内置语言服务器的诊断服务

LSP 子系统位于 `agent/lsp/`（11 个 py，Q-001），定位是 Agent 的"代码诊断外援"（F-123）：

- **进程级单例**：`get_service()`（agent/lsp/__init__.py:45）返回可选的 `LSPService`，`shutdown_service()`（:80）统一回收，避免同一语言服务器被重复拉起。
- **协议与客户端**：`LSPClient` 按标准 LSP 的 **JSON-RPC Content-Length 分帧**通信（分帧原语在 protocol.py），提供 `start` / `shutdown` / `open_file` / `save_file` / `wait_for_diagnostics`；manager.py 的 `LSPService` 管理多服务器生命周期，`create_from_config` 与 `get_diagnostics_sync` 做同步诊断封装，workspace.py 维护打开的工作区与文件状态。
- **服务器目录**：`SERVERS` 是 **26 个 `ServerDef`** 的列表（servers.py:831 起，Q-004 计数 26），覆盖 pyright、typescript、gopls、rust_analyzer、clangd、bash、yaml、lua 等；`LANGUAGE_BY_EXT`（servers.py:35）提供 **69 条扩展名→语言映射**，决定打开某文件时拉起哪个 server。
- **安装三策略**：`try_install(pkg, strategy="auto")`（install.py:143）按服务器配方走 **npm / go / pip** 三种安装策略（npm 配方如 pyright 等，install.py:52 起）。
- **CLI 子命令**：`status` / `list` / `install` / `install-all` / `restart` / `which`（lsp/cli.py:34-59；lsp 命令经主 CLI 外挂注册），其中 install-all 安装全部有配方的服务器、restart 拆除运行中客户端使下次编辑重拉、which 打印解析后的二进制路径。

诊断配套（F-124）：range_shift 处理编辑后的行号漂移；reporter 限制单次输出 `MAX_TOTAL_CHARS = 4000`；eventlog 提供 11 个 `log_*` 记录函数。

## 使用与排障提示

- **ACP 接入失败先自检**：运行 `hermes-acp --check` 检查凭证与运行环境，首次使用可走 `--setup`（交互配置）与 `--setup-browser`（浏览器能力准备）（F-119）。
- **MCP 无事件时检查 EventBridge**：事件类工具依赖对 SessionDB 的轮询；网关上没有会话活动时 `events_wait` 只是正常挂起，而非故障（F-121）。
- **不要直接 `python mcp_serve.py`**：该文件没有顶层 `main()`，应由装配方调用 `run_mcp_server()`（F-121）。
- **LSP 诊断不出结果**：先用 `lsp status` 看服务状态、`lsp which <server_id>` 确认二进制可解析；缺二进制时按 `lsp install` 的 npm/go/pip 配方安装（F-123）。
- **文件改动后诊断行号错位**：range_shift 负责编辑后的行号漂移修正，单次诊断输出超 4000 字符会被 reporter 截断（F-124）。

## 三协议对比

| 维度 | ACP | MCP（mcp_serve） | LSP |
|---|---|---|---|
| 用途 | 让编辑器把本运行时当作编码代理驱动 | 把网关会话/消息/审批暴露给 MCP 客户端 | Agent 调语言服务器取代码诊断 |
| 方向 | 本运行时作 Agent（服务端） | 本运行时作工具服务器 | 本运行时作 LSP 客户端 |
| 传输 | **stdio-only**，本地信任 | FastMCP（由 EventBridge 轮询 SessionDB 供数） | JSON-RPC Content-Length 分帧，子进程 |
| 入口 | `hermes-acp` → `acp_adapter.entry:main`（--check/--setup）（F-005/F-119） | `create_mcp_server` / `run_mcp_server`，无顶层 main()（F-121） | `get_service()` 单例 + `lsp` CLI 子命令（F-123） |
| 注册/规模 | agent.json：id `kylin-agent`、uvx 包串 `kylin-agent-runtime[acp]==0.9.3`（F-015） | 10 个 @mcp.tool（Q-004） | 26 ServerDef / 69 扩展名映射（Q-004） |

## 相关概念

- [03-cli-and-tui](/concepts/03-cli-and-tui.md)：console_scripts 四个入口与 lsp/acp 等外挂子命令的注册方式。
- [08-gateway-and-cron](/concepts/08-gateway-and-cron.md)：MCP 工具所暴露的 SessionDB、审批与频道目录的来源。
- [04-tool-system](/concepts/04-tool-system.md)：mcp_tool.py 让 Agent 反向作为 MCP 客户端消费外部工具。
- 上游协议适配可对照跨束的 [hermes-agent](../../hermes-agent/index.md) 文档。
