# 信源登记簿

本目录登记 Octop 知识包所有内容据以派生的源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源条目。信源基于 `external/libs/ai/Tencent/WorkBuddy/Octop/` 源码核心文件。

* [服务器启动与组合根（OctopServer / launch.py）](server-launch.md) — `src/octop/infra/server.py`、`src/octop/launch.py`：OctopServer 进程编排器、AppRuntime 五个运行时单例、start/stop/_boot_runtime 装配顺序、Greenfield 延迟绑定、bind_control_plane 热绑定、日志轮转、JWT 密钥、Wizard 密码、launch.py 组合根（run_foreground/run_foreground_blocking）、TLS 双端口模式。
* [AgentManager：Agent 生命周期与 Harness 委托](agent-manager.md) — `src/octop/infra/agents/manager.py`：AgentManager 进程级单例、HarnessAgent/HarnessAgentManager 委托、AgentCreateSpec、CRUD 与生命周期、stream/call/resume_hitl、三种热重载粒度、Provider 变更影响分析（有界并行 6）、MCP 工具缓存（user/server/fingerprint）、settings stores（Langfuse/Security/ACP/ToolGuard/Provider）、MBTI 人格、ExpertCatalog/SubagentCatalog/PluginManager。
* [Gateway：全局 AI 交互入口与通道管理](gateway.md) — `src/octop/infra/gateway/gateway.py`：Gateway 类、ChannelRuntimeStatus、GlobalProcessor、ChannelManager（harness-gateway）、WebSocketChannel/CliChannel 内置通道、IM 通道注册、push_text_from_session Cron 投递、Slash 抢占式取消、通道探测、refresh_media_backends、reload_channels_from_db。
* [数据库层：Pool Protocol、RepoBundle 与 SharedServices DI](db-layer.md) — `src/octop/infra/db/pool.py`、`services.py`、`factory.py`：DatabasePool Protocol、SqlitePool（WAL+RLock）、PostgresPool（psycopg_pool）、RepoBundle 22 个 Repository、SharedServices DI 容器、open_database 工厂、resolve_sqlite_db_path、should_defer_control_plane_db、数据库迁移（schema v7）。
* [CLI 与 HTTP API：_LazyCLI、20 子命令、FastAPI 工厂](cli-api.md) — `src/octop/cli/main.py`、`registry.py`、`commands/run.py`、`src/octop/api/app.py`：_LazyCLI 延迟加载、COMMANDS 注册表 20 子命令、UTF-8 stdio 兼容、三层传输（Offline/Embedded/External）、octop run 选项与自签名证书、build_app FastAPI 工厂、50+ 路由挂载、OctopError 异常处理、Dashboard SPA fallback。
* [Harness 技术栈：外部包依赖与 PathLayout](harness-stack.md) — `pyproject.toml`、`src/octop/config.py`、`src/octop/infra/utils/paths.py`、`AGENTS.md`：orcakit-harness-agent/harness-gateway/harness-memory/harness-browser 四个外部包、OctopConfig/DatabaseConfig/TlsConfig/BackupConfig frozen dataclass、load_config 环境变量覆盖、PathLayout 文件系统布局（~/.octop/）、模块边界硬禁令、i18n/时区、前端技术栈。

**v1.0.2b5 增量轮（2026-10-04）新增**——信源 `external/dao/runtime/tencent/Octop/`（v1.0.2b5 / commit e473dd3c，F-134~F-592；旧信源 `external/libs/ai/Tencent/WorkBuddy/Octop/` 已失效）：

* [Octop v1.0.2b5 源码地图与构建清单](source-v1-map.md) — 版本与分发面（octop-harness/memory/gateway/browser>=1.0.0、extras 5 组、hatch include）、仓库顶层地图、infra 二十子域逐域计数、api/cli 子树、dashboard 构建链、Go/Wails 桌面、Docker 三套 compose、FnOS 0.9.15（F-134~F-205、F-556~F-565、F-576~F-592）。
* [HTTP API 挂载总表与端点计数 v1.0.2b5](api-surface.md) — build_app 装配、60 router 挂载完整总表（59 常挂+mobile 条件）、472 HTTP 装饰器+9 WS、OpenAPI 40 声明 tag（另 4 使用未声明）、JWT 豁免 5 前缀+15 精确、chat/browser/desktop/mobile 子包（F-503~F-555）。
* [连接器目录与 MCP 三模式网关信源登记](connectors-catalog.md) — ConnectorCatalog 25 项逐行总表、AuthKind 8/McpMode 3/ConnectorCategory 7、OAuth2 PKCE+DCR+PRM、13 进程内适配器 49 工具、内部 MCP 路径与协议版本 2024-11-05、凭证 Fernet、企查查特例（F-276~F-315、F-382~F-383）。
* [Octop↔Octop 桥接协议信源登记](bridge-protocol.md) — 协议常量、5 次退避重连、帧超时表（20/20/30/120/600s）、关闭码 4000/4002/4003、28 子路径白名单 9+9+10 逐字、影子 ID 键表、SSRF link-local 黑名单、bridge.py 19 端点（F-384~F-401）。

```{toctree}
:hidden:
:maxdepth: 7

agent-manager
api-surface
bridge-protocol
cli-api
connectors-catalog
db-layer
gateway
harness-stack
server-launch
source-v1-map
```
