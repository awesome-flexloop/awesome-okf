# Concepts

- [00 - 总览：从 Hermes 到麒麟智能体运行时](00-overview.md) — 项目定位、自进化三回路、版本血缘、openKylin 增量与 SIG 归属
- [01 - 整体架构与模块地图](01-architecture-module-map.md) — 遗产脚本/agent 内核/CLI 前端三代同层、入口依赖链与技术栈
- [02 - Agent 核心对话环](02-agent-core-loop.md) — 转发壳到 init_agent、Think-Act 迭代、预算、护栏、重试与安全纵深
- [03 - CLI、TUI 与 Web 控制台](03-cli-and-tui.md) — 双 CLI、48 内置子命令、setup、dashboard 9119 与 Ink TUI 链路
- [04 - 工具系统](04-tool-system.md) — AST 预判+导入自注册发现链、31 工具集、8 个终端环境与 computer_use
- [05 - 模型与 Provider 体系](05-model-providers.md) — 4 类传输、中央路由、凭证池、懒安装、元数据与定价限流
- [06 - 技能与插件体系](06-skills-and-plugins.md) — 技能树/curator 策展、17 钩插件、四类能力 Provider 注册
- [07 - 记忆与上下文](07-memory-and-context.md) — SessionDB 双 FTS5、上下文压缩、@引用、记忆 ABC 与用户画像治理
- [08 - 消息网关与定时调度](08-gateway-and-cron.md) — GatewayRunner、21 平台适配器双轨制、会话存储与函数式 cron
- [09 - ACP / MCP / LSP 协议](09-acp-mcp-protocols.md) — stdio ACP 服务器、FastMCP 10 工具与 26 个 LSP 服务器

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-architecture-module-map
02-agent-core-loop
03-cli-and-tui
04-tool-system
05-model-providers
06-skills-and-plugins
07-memory-and-context
08-gateway-and-cron
09-acp-mcp-protocols
```
