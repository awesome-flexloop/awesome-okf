# 核心概念

本目录包含 Octop 项目的 7 个核心概念文档，按学习路径排列：从架构总览到具体机制逐步深入。

* [00 - Octop 四层架构与依赖禁令](00-architecture.md) — dashboard→api→infra→utils 四层架构、六条依赖方向硬禁令、launch.py 独占组合根、单进程 asyncio 模型、frozen dataclass 配置、SharedServices 手动 DI。
* [01 - 服务器生命周期：OctopServer](01-server-lifecycle.md) — OctopServer 三种状态、start() 完整流程、Greenfield 延迟绑定、bind_control_plane() 热绑定、_boot_runtime() 12 步装配顺序、AppRuntime 五个运行时单例、stop() 逆序关闭、JWT 密钥与日志系统。
* [02 - Agent 运行时：AgentManager 与 HarnessAgent](02-agent-runtime.md) — AgentManager 进程级单例、HarnessAgent/HarnessAgentManager 委托、Agent CRUD 与生命周期、stream/call/HITL、三种热重载粒度、Provider 变更影响分析、MCP 工具缓存、MBTI 16 种人格、专家库/子代理/插件目录、安全审批 guardrails。
* [03 - Gateway 与通道：IM 消息路由](03-gateway-channels.md) — Gateway 全局交互入口、GlobalProcessor 消息处理、ChannelManager（harness-gateway）、WebSocket/CLI 内置 Hub、飞书/钉钉/QQ/Discord/企微等 IM 通道、ChannelRuntimeStatus、Cron 投递、Slash 抢占式取消、ThreadRegistry、media backend 延迟设置。
* [04 - 数据库层与 DI](04-db-di.md) — DatabasePool Protocol、SqlitePool（WAL+RLock+foreign_keys）、PostgresPool（psycopg_pool min1/max8）、RepoBundle 22 个 Repository、SharedServices DI 容器、open_database 工厂、Greenfield 延迟绑定、数据库迁移（schema v7）、资源表 id/{entity}_id 约定。
* [05 - ACP 双向集成](05-acp-protocol.md) — ACP 入站（octop acp stdio 服务器，Zed 等 IDE 驱动）与出站（acp_runner 工具委托）、四个内置 runner（opencode/codebuddy/claude_code/codex）、per-user runner 配置 + per-agent tool_enabled、六种 action、HTTP API、Zed 配置示例。
* [06 - CLI 命令体系](06-cli-commands.md) — _LazyCLI Click Group 延迟加载、COMMANDS 注册表 20 子命令、全局选项（--user/--agent/--json/-v）、Windows UTF-8 兼容、Offline/Embedded/External 三层传输、octop run 选项与自签名证书、CLI 状态文件 cli_state.json。
