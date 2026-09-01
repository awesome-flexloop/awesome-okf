# Concepts

- [00 - CodeWhale 简介](00-introduction.md) — CodeWhale 是什么、功能特性、安装方式
- [01 - 工作区架构](01-workspace-architecture.md) — Cargo workspace 21 个 crate、依赖关系图、核心分层
- [02 - Agent 核心](02-agent-core.md) — core crate、Runtime、Thread/Session 分离、Engine、JobManager
- [03 - MCP 协议](03-mcp-protocol.md) — mcp crate、MCP 客户端/服务端、工具注册、stdio JSON-RPC
- [04 - 工具系统](04-tool-system.md) — tools crate、ToolRegistry、ToolHandler、并行调度、参数验证
- [05 - Fleet 多 Agent](05-fleet-subagents.md) — Fleet 控制平面、角色分类、权限 clamp、Workflow 集成
- [06 - 技能与 Hooks](06-skills-hooks.md) — Skills 四层架构、Hooks 生命周期、插件系统
- [07 - 沙箱与执行策略](07-sandbox-execpolicy.md) — execpolicy 引擎、三层规则、Shell 展开防护、Seatbelt/bwrap

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-workspace-architecture
02-agent-core
03-mcp-protocol
04-tool-system
05-fleet-subagents
06-skills-hooks
07-sandbox-execpolicy
```
