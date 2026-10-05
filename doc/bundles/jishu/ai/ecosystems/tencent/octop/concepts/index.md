# 核心概念

本目录包含 Octop 项目的 22 个核心概念文档（00-06 基于 v0.9.25，07-21 为 2026-10-04 v1.0.2b5 增量轮新增），按学习路径排列：从架构总览到具体机制逐步深入。

* [00 - Octop 四层架构与依赖禁令](00-architecture.md) — dashboard→api→infra→utils 四层架构、六条依赖方向硬禁令、launch.py 独占组合根、单进程 asyncio 模型、frozen dataclass 配置、SharedServices 手动 DI。
* [01 - 服务器生命周期：OctopServer](01-server-lifecycle.md) — OctopServer 三种状态、start() 完整流程、Greenfield 延迟绑定、bind_control_plane() 热绑定、_boot_runtime() 12 步装配顺序、AppRuntime 五个运行时单例、stop() 逆序关闭、JWT 密钥与日志系统。
* [02 - Agent 运行时：AgentManager 与 HarnessAgent](02-agent-runtime.md) — AgentManager 进程级单例、HarnessAgent/HarnessAgentManager 委托、Agent CRUD 与生命周期、stream/call/HITL、三种热重载粒度、Provider 变更影响分析、MCP 工具缓存、MBTI 16 种人格、专家库/子代理/插件目录、安全审批 guardrails。
* [03 - Gateway 与通道：IM 消息路由](03-gateway-channels.md) — Gateway 全局交互入口、GlobalProcessor 消息处理、ChannelManager（harness-gateway）、WebSocket/CLI 内置 Hub、飞书/钉钉/QQ/Discord/企微等 IM 通道、ChannelRuntimeStatus、Cron 投递、Slash 抢占式取消、ThreadRegistry、media backend 延迟设置。
* [04 - 数据库层与 DI](04-db-di.md) — DatabasePool Protocol、SqlitePool（WAL+RLock+foreign_keys）、PostgresPool（psycopg_pool min1/max8）、RepoBundle 22 个 Repository、SharedServices DI 容器、open_database 工厂、Greenfield 延迟绑定、数据库迁移（schema v7）、资源表 id/{entity}_id 约定。
* [05 - ACP 双向集成](05-acp-protocol.md) — ACP 入站（octop acp stdio 服务器，Zed 等 IDE 驱动）与出站（acp_runner 工具委托）、四个内置 runner（opencode/codebuddy/claude_code/codex）、per-user runner 配置 + per-agent tool_enabled、六种 action、HTTP API、Zed 配置示例。
* [06 - CLI 命令体系](06-cli-commands.md) — _LazyCLI Click Group 延迟加载、COMMANDS 注册表 20 子命令、全局选项（--user/--agent/--json/-v）、Windows UTF-8 兼容、Offline/Embedded/External 三层传输、octop run 选项与自签名证书、CLI 状态文件 cli_state.json。

**v1.0.2b5 增量轮（2026-10-04，F-134~F-592）新增：**

* [07 - 连接器系统：25 连接器与 MCP 三模式网关](07-connector-system.md) — remote/gateway/internal 三模式、25 项目录（13/1/11）、AuthKind 8 与分类 7、OAuth2 PKCE+DCR+RFC9728、13 进程内适配器、凭证 Fernet、MCP 协议 2024-11-05、工具缓存与探测。
* [08 - 知识库 RAG：每库 SQLite 与全表内存余弦](08-knowledge-rag.md) — knowledge_dir/{kb_id}/index.sqlite、chunks 6 列、float32 struct.pack 全表余弦、100 文档/20 库/10000 上限、chunk800/overlap120/top-k 8、ONNX 三预置 embedding、引用标记契约。
* [09 - 消息网关进阶：slash/处理流水线/HITL/语音/cron](09-gateway-advanced.md) — slash 25 命令（core8/session10/system7）、GlobalProcessor 42 方法、入站 142 扩展名+37 别名、HITL TTL 1800s、voice 5 kind/6 预设、cron 6 工具与双默认值口径。
* [10 - 专家团队：主持人剥权隔离与派工](10-agent-teams.md) — kind="team"/team-host 模板、≥2 成员、HOST_TOOLS_ALLOWED 5 工具、45 秒空闲收尾、派工回复 IM 同步、8 中间件链。
* [11 - 专家市场、子代理库与 MBTI 人格](11-agent-marketplace.md) — experts 九文件分工、18 内置专家 manifest、子代理 zh 272/en 217、MBTI 16、唯一内置技能 skill-manager。
* [12 - Agent 运行时内部：Manager 装配、会话模式、模型与工具供给](12-agent-runtime-internals.md) — ask/plan/craft 三模式、reasoning 8 适配、ONNX 3 预置+9 扩展、BUILTIN_TOOL_CATALOG 42、memory slim、threads artifact、workspace 执行环境。
* [13 - 插件与技能包：双扩展体系](13-plugin-system.md) — PluginManager 装载/seed/legacy 兼容、plugin.yaml 清单、ctx 三 API 官方仅用 tool、26 官方插件 8 分组、SkillHub 与 2000 文件/64MiB 上限。
* [14 - Octop↔Octop 联邦桥接](14-bridge-federation.md) — ASGI 隧道 http://bridge.local、Fernet peer auth、5 次退避(2,4,8,16,30)、影子 ID 重写、28 子路径白名单、link-local SSRF 黑名单。
* [15 - 自动备份、归档与存储后端](15-backup-and-storage.md) — tar.gz 六内容、system 跳过 13 目录、pg_dump -Fc/SQLite online backup、octop_auto_backup 4 点定时/保留 7、存储 10 kind、docker 透传 18 键。
* [16 - 版本化历史与轨迹流](16-history-trajectory.md) — history_v2 三触发、6 表 3 索引、内容寻址 bodies/body_refs、TrajectoryKind 7、LiveBus 实时轨迹、50 轮热窗、不可逆服务。
* [17 - 用户、RBAC、SSO 与验证码](17-users-auth-security.md) — 26 权限三组（4+4+18）、邀请码 11 字符/1-90 天、Argon2id/弱口令 14、SSO 四 provider、captcha 7 provider、审计 11 动作。
* [18 - 云手机、桌面会话与主动关怀](18-mobile-desktop-proactive.md) — physical/redroid/emulator、H264 4Mbps、容器 5555、VNC 5900/会话上限 3、SetupState 6、proactive 10 情绪权重。
* [19 - Dashboard 前端架构](19-dashboard-frontend.md) — React18/Vite6.3/antd5.29、api 77 ts、pathToKey 41/routeConfigs 63、12 页面域、hooks 56、locales 80 键、PWA。
* [20 - API 装配面与 CLI 22 命令新口径](20-api-cli-surface.md) — 60 挂载（59+mobile）、472 HTTP+9 WS、40 声明 tag、JWT 豁免 5+15、COMMANDS 22、REPL 7/support 13。
* [21 - 打包与部署：Wails 桌面/便携 runtime/Docker/FnOS](21-packaging-deployment.md) — Go 1.25 Wails beta.13、1200x800 Frameless、便携 launch.py runpy、两阶段镜像 8088、三套 compose、FnOS 0.9.15。

```{toctree}
:hidden:
:maxdepth: 7

00-architecture
01-server-lifecycle
02-agent-runtime
03-gateway-channels
04-db-di
05-acp-protocol
06-cli-commands
07-connector-system
08-knowledge-rag
09-gateway-advanced
10-agent-teams
11-agent-marketplace
12-agent-runtime-internals
13-plugin-system
14-bridge-federation
15-backup-and-storage
16-history-trajectory
17-users-auth-security
18-mobile-desktop-proactive
19-dashboard-frontend
20-api-cli-surface
21-packaging-deployment
```
