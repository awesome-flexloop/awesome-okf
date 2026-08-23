---
type: spec-facts
title: Octop 源码事实清单
---

# Octop 源码事实清单

> R阶段产出：编号事实清单 F-001~F-120，零推测纯客观描述，全部基于 `external/libs/ai/Tencent/WorkBuddy/Octop/` 源码。

## 项目元信息

- F-001: 包名 `octop`，版本 `0.9.25`（`src/octop/__init__.py:5`、`pyproject.toml:7`）
- F-002: 许可证为 MIT（`pyproject.toml:10`）
- F-003: `requires-python = ">=3.12"`（`pyproject.toml:11`）
- F-004: 构建后端为 `hatchling>=1.18`，wheel 包路径 `src/octop`（`pyproject.toml:1-3,86-87`）
- F-005: 控制台入口 `octop = "octop.cli.main:cli"`（`pyproject.toml:83-84`）
- F-006: 包描述为 "Smarter self-hosted AI assistant for multiple users and agents, built on harness-agent"（`pyproject.toml:8`）
- F-007: 核心运行时依赖包含 `orcakit-harness-agent[all]>=0.9.23`、`harness-memory>=0.9.7`、`harness-gateway>=0.9.3`、`harness-browser>=0.7.5`（`pyproject.toml:24-26,35`）
- F-008: Web 框架依赖为 `fastapi>=0.110` + `uvicorn[standard]>=0.27`（`pyproject.toml:14-15`）
- F-009: 数据库依赖为 `psycopg[binary]>=3.2`（PostgreSQL）+ 标准库 `sqlite3`（SQLite），另含 `langgraph-checkpoint-postgres>=2.0`（`pyproject.toml:37-38`）
- F-010: 安全依赖为 `argon2-cffi>=23.1`（密码哈希）+ `pyjwt>=2.8`（JWT）（`pyproject.toml:22-23`）
- F-011: CLI 依赖为 `click>=8.1`、`rich>=13.7`、`questionary>=2.0`（`pyproject.toml:18-20`）
- F-012: MCP 依赖为 `mcp>=1.9,<2`（`pyproject.toml:39`）
- F-013: TLS/ACME 依赖为 `cryptography>=41`、`acme>=5.6.0`、`josepy>=2.2.0`（`pyproject.toml:27,32-33`）
- F-014: 前端技术栈为 React 18 + TypeScript + Vite + Ant Design（AGENTS.md §3），构建产物位于 `src/octop/dashboard/`，源码位于 `dashboard/`
- F-015: AGENTS.md 声明"One Python wheel: FastAPI backend + React dashboard + Click CLI. No external queue. No required services beyond an LLM provider."

## 配置层（config.py）

- F-016: `OctopConfig` 为 `@dataclass(frozen=True)`，字段含 `bind_host: str = "127.0.0.1"`、`port: int = 8088`、`log_level: str = "info"`、`access_token_ttl_seconds: int = 86400`、`login_max_attempts: int = 5`、`login_lockout_seconds: int = 900`、`cors_origins: list[str]`、`default_timezone: str = "Asia/Shanghai"`、`enable_dashboard: bool = True`、`enable_api_docs: bool = False`、`require_setup_password: bool = True`、`database: DatabaseConfig`、`database_in_file: bool = False`、`tls: TlsConfig`、`backup: BackupConfig`（`config.py:96-112`）
- F-017: `DatabaseConfig` 为 frozen dataclass，字段含 `driver: str = "sqlite"`、`sqlite_path: str = "octop.db"`、`host: str = "127.0.0.1"`、`port: int = 5432`、`database: str = "octop"`、`user: str = "octop"`、`password: str | None = None`、`url: str | None = None`；提供 `is_sqlite`/`is_postgresql` 属性、`resolve_sqlite_path(octop_root)`、`postgresql_conninfo()` 方法（`config.py:34-68`）
- F-018: `TlsConfig` 为 frozen dataclass，字段含 `enabled`、`mode`、`domains: list[str]`、`cert_file`、`key_file`、`issued_at`、`expires_at`、`acme_staging: bool = False`、`http_port: int = 80`（`config.py:71-83`）
- F-019: `BackupConfig` 为 frozen dataclass，字段含 `auto_enabled: bool = False`、`schedule: str = "cron:0 4 * * *"`、`retention_count: int = 7`（`config.py:86-92`）
- F-020: 合法数据库驱动集合 `_VALID_DRIVERS = frozenset({"sqlite", "postgresql"})`（`config.py:15`）
- F-021: `load_config(path: Path) -> OctopConfig` 读取 `config.json`，文件不存在时写入默认值；支持环境变量覆盖（`OCTOP_BIND_HOST`、`OCTOP_PORT`、`OCTOP_LOG_LEVEL`、`OCTOP_DATABASE_*`、`OCTOP_BACKUP_*` 等）（`config.py:289-394`）
- F-022: `database_env_configured() -> bool` 检测是否设置了任意 `OCTOP_DATABASE_*` 环境变量（`config.py:29-31`）
- F-023: 环境变量 `OCTOP_DATABASE_URL` 支持 `postgresql://` 或 `postgres://` scheme，通过 `_parse_database_url` 解析（`config.py:189-209`）

## 组合根（launch.py）

- F-024: `run_foreground(*, host, port, reload, workers, log_level, ssl_certfile, ssl_keyfile) -> None` 为 async 函数，是组合根：构造 `OctopServer()` → `await srv.start()` → `build_app(srv)` → 启动 uvicorn（`launch.py:18-111`）
- F-025: `run_foreground_blocking(**kwargs) -> None` 为同步入口，通过 `asyncio.run(run_foreground(**kwargs))` 包装，供 Click 命令和测试使用（`launch.py:114-116`）
- F-026: 支持 TLS 双端口模式（dual listeners）：HTTPS + HTTP companion（ACME challenge + redirect），此时强制 `workers=1` 且禁用 reload（`launch.py:54-59,64-94`）
- F-027: 单端口模式使用单个 `uvicorn.Config`，支持 `reload` 和多 `workers`（`launch.py:95-106`）
- F-028: `finally` 块中调用 `await srv.stop()` 保证干净关闭（`launch.py:108-111`）
- F-029: launch.py 导入 `build_app`（来自 `octop.api.app`）、`OctopServer`（来自 `octop.infra.server`），是唯一同时导入 `infra/server` 和 `api/app` 的模块（AGENTS.md §5）

## 服务器编排（infra/server.py）

- F-030: `OctopServer` 类为进程级编排器，`__init__(self, home: Path | None = None)` 通过 `PathLayout.from_env().root` 解析 home 目录（`server.py:104-117`）
- F-031: `OctopServer` 持有属性：`paths: PathLayout`、`config: OctopConfig | None`、`services: SharedServices | None`、`app_runtime: AppRuntime | None`、`expert_catalog`、`subagent_catalog`、`plugin_manager`、`wizard_tokens`、`_sso_service`（`server.py:106-117`）
- F-032: `AppRuntime` 为 `@dataclass`，包含 `agent_registry: AgentManager`、`gateway: Gateway`、`cron_manager: CronManager`、`user_manager: UserManager`、`proactive_scheduler: ProactiveCareScheduler` 五个运行时单例（`server.py:78-86`）
- F-033: `AppRuntime.replace_services(services, config)` 方法将所有运行时单例重定向到新的 SharedServices/config，用于 setup wizard 热交换控制面 DB（`server.py:88-101`）
- F-034: `OctopServer.database_bound` 属性返回 `self.services is not None and self.app_runtime is not None`（`server.py:139-141`）
- F-035: `OctopServer.start()` 流程：`paths.ensure_root()` → 加载 `.env` → `_setup_logging()` → `load_config()` → 构造 `ExpertCatalog`/`SubagentCatalog`/`PluginManager` → 判断 `should_defer_control_plane_db` → 若延迟则仅生成 wizard 密码后返回；否则 `open_database()` → `run_migrations()` → `build_shared_services()` → `_ensure_jwt_secret()` → `_boot_runtime()`（`server.py:143-185`）
- F-036: `OctopServer.bind_control_plane()` 为 async 方法，首次运行向导绑定控制面 DB：重新 `load_config` → `open_database` → `run_migrations` → `build_shared_services` → `_ensure_jwt_secret` → `_boot_runtime`；幂等（`server.py:187-210`）
- F-037: `_boot_runtime(config)` 按序构造：`AgentManager` → `Gateway`（`await gateway.boot()`）→ `CronManager`（`await cron_mgr.boot()`）→ 安装 TLS 自动续期 job → 安装自动备份 job → `registry.set_cron_manager`/`set_team_processor` → `ProactiveCareService`/`ProactiveCareScheduler` → `await registry.boot()` → `await gateway.refresh_media_backends()` → `UserManager` → `await proactive_scheduler.start_all()` → 组装 `AppRuntime` → `resume_pending_index_jobs`（`server.py:212-287`）
- F-038: `OctopServer.stop()` 按序关闭：`proactive_scheduler.shutdown()` → `cron_manager.shutdown()` → `gateway.shutdown()` → `agent_registry.shutdown()` → `user_manager.shutdown_all()` → `services.db.close()`（`server.py:319-336`）
- F-039: `_ensure_jwt_secret()` 通过 `secret_repo.get_or_create("jwt", lambda: os.urandom(32))` 确保 JWT 密钥存在（`server.py:368-370`）
- F-040: 日志使用 `TimedRotatingFileHandler`（每日轮转），默认保留 14 天（`OCTOP_LOG_RETENTION_DAYS`），日志文件 `~/.octop/logs/octop.log`（`server.py:38-66,340-366`）
- F-041: `sso_service` 属性懒加载 `SsoService`，缓存进程级实例以便 JWKS 缓存跨请求存活（`server.py:124-137`）
- F-042: `_emit_wizard_password(user_count)` 在 `require_setup_password=True` 时生成一次性向导密码，写入 `~/octop-login.txt` 并在终端打印黄色 banner（`server.py:289-317`）
- F-043: `WizardTokenStore(ttl_seconds=300)` 在 `OctopServer.__init__` 中创建（`server.py:114`）

## 错误体系（infra/errors.py）

- F-044: `ErrorCode(StrEnum)` 定义 83 个错误码枚举值（`errors.py:13-96`）
- F-045: 错误码按领域分类：认证（AUTH_FAILED/TOKEN_EXPIRED/SETUP_REQUIRED/LOGIN_LOCKED 等）、用户（USER_DISABLED/USERNAME_TAKEN/PASSWORD_*）、Agent（AGENT_NOT_FOUND/AGENT_NOT_RUNNING/AGENT_FAILED/AGENT_BUSY/AGENT_NAME_TAKEN/AGENT_ID_INVALID/AGENT_ID_TAKEN）、Provider（PROVIDER_NAME_TAKEN/PROVIDER_NOT_VISIBLE/PROVIDER_REFERENCED/PROVIDER_LOCAL_PROTECTED）、Channel（CHANNEL_KIND_UNSUPPORTED/CHANNEL_INVALID_CREDENTIALS/CHANNEL_NAME_TAKEN）、Connector（CONNECTOR_NOT_FOUND/CONNECTOR_INVALID_CREDENTIALS/CONNECTOR_OAUTH_HTTPS_REQUIRED/CONNECTOR_KIND_UNSUPPORTED/CONNECTOR_NOT_BOUND/CONNECTOR_ALREADY_BOUND/CONNECTOR_MCP_LOAD_FAILED）、Cron（CRON_TRIGGER_INVALID）、Slash（SLASH_UNKNOWN/SLASH_BAD_ARGS）、Voice（VOICE_BROWSER_ONLY/VOICE_KIND_UNSUPPORTED/VOICE_CAPABILITY_MISMATCH/VOICE_PROVIDER_DISABLED）、TLS（TLS_NOT_ELIGIBLE/TLS_ISSUE_IN_PROGRESS/TLS_DOMAIN_MISMATCH）、Skill（SKILL_IMPORT_*/SKILL_ALREADY_EXISTS/SKILL_PACKAGE_*）、Knowledge（KNOWLEDGE_FEATURE_DISABLED/KNOWLEDGE_PREREQUISITES_FAILED/KNOWLEDGE_NOT_FOUND/KNOWLEDGE_FORBIDDEN/KNOWLEDGE_DOC_LIMIT/KNOWLEDGE_DOC_TOO_LARGE/KNOWLEDGE_BASE_LIMIT/KNOWLEDGE_UNSUPPORTED_TYPE/KNOWLEDGE_NAME_TAKEN）、Plugin（PLUGIN_INVALID_ARCHIVE/PLUGIN_INSTALL_FAILED/PLUGIN_ALREADY_EXISTS）、Invite（INVITE_INVALID/INVITE_USED/INVITE_EXPIRED/INVITE_REVOKED/INVITE_RATE_LIMITED）、Avatar（AVATAR_INVALID/AVATAR_TOO_LARGE）、Desktop（DESKTOP_SESSION_LIMIT/DESKTOP_CAPTURE_FAILED）、Storage（STORAGE_BACKEND_NAME_TAKEN/STORAGE_BACKEND_REFERENCED）、Backup（BACKUP_DRIVER_MISMATCH/BACKUP_IN_PROGRESS）、通用（FORBIDDEN/NOT_FOUND/INTERNAL_ERROR）
- F-046: `_DEFAULT_STATUS: dict[ErrorCode, int]` 将每个错误码映射到 HTTP 状态码（401/403/404/409/400/429/500/502/422/413/410 等）（`errors.py:99-183`）
- F-047: `OctopError(Exception)` 为 `@dataclass`，字段：`code: ErrorCode`、`message: str`、`status: int = 0`、`details: dict[str, Any]`；`__post_init__` 中 status 为 0 时从 `_DEFAULT_STATUS` 填充（`errors.py:186-196`）
- F-048: `OctopError.localized_message(locale, **kwargs)` 通过 `i18n_error_message` 本地化错误消息，KeyError 时回退到原始 message（`errors.py:198-203`）
- F-049: `OctopError.localized(code, locale="en", *, message=None, status=0, details=None, **kwargs)` classmethod 构造本地化异常（`errors.py:205-221`）
- F-050: `to_envelope(*, locale=None) -> dict` 返回 `{"error": {"code", "message", "details"}}` JSON 信封结构（`errors.py:223-231`）

## AgentManager（infra/agents/manager.py）

- F-051: `AgentManager` 类为进程级单例，管理所有 `HarnessAgent` 实例；`__init__(*, repos: RepoBundle, paths: PathLayout, config: OctopConfig | None = None, expert_catalog: ExpertCatalog | None = None, plugin_manager: PluginManager | None = None)`（`manager.py:282-354`）
- F-052: AgentManager 从 `harness_agent` 导入 `HarnessAgent`、`HarnessAgentConfig`、`HarnessAgentManager`、`SecurityPolicy`（`manager.py:15-16`）
- F-053: AgentManager 持有 settings stores：`_langfuse`（LangfuseSettingsStore）、`_security`（SecuritySettingsStore）、`_acp_settings`（ACPSettingsStore）、`_tool_guard_rules`（ToolGuardRulesStore）、`_providers`（ProviderStore）、`_connector_svc`（ConnectorService）（`manager.py:330-348`）
- F-054: `AgentCreateSpec` 为 `@dataclass`，字段含 `name`、`agent_id`、`user_id`、`description`、`persona_mbti`、`default_model`、`system_prompt`、`icon`、`template_name`、`is_shared`、`icon_name`、`icon_url`、`color`、`skill_package_ids`、`published_expert_id`、`welcome_message`、`runtime_config`、`config`（`manager.py:253-274`）
- F-055: 自定义 agent ID 校验正则 `_CUSTOM_AGENT_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$")`，保留 ID 集合 `_RESERVED_AGENT_IDS = frozenset({"api", "admin", "agents", "experts"})`（`manager.py:231,250`）
- F-056: `boot()` 方法：seed tool guard rules → `_providers.build_harness_configs()` → 构造 `HarnessAgentManager(providers, langfuse, team_processor)` → 设置 security policy → 从 DB 加载所有 enabled agent（跳过 `last_state=="stopped"`）→ `_start_agent(row)`（`manager.py:385-400`）
- F-057: `shutdown()` 关闭 harness_manager（`manager.py:402-409`）
- F-058: `create(spec, *, defer_bootstrap=False) -> AgentRow`：校验名称/ID → 合并 runtime config → 处理 persona_mbti（写入 `config["persona"]`）→ seed workspace dir → extract/strip profile → 写入 DB → 可选 set_shared → 可选 seed expert template → 同步启动或异步 bootstrap → 写审计日志（`manager.py:447-536`）
- F-059: `update(agent_id, **kwargs) -> AgentRow`：分离 `AGENT_RUNTIME_CONFIG_KEYS` → 合并 config_json → preserve system_files_path → extract profile → 更新 DB → `_schedule_reload(agent_id)`（`manager.py:553-599`）
- F-060: `delete(agent_id)`：从 harness 移除 → 删除 workspace 目录 → 删除 DB 行 → 写审计日志（`manager.py:620-635`）
- F-061: `start(agent_id)` / `stop(agent_id)` 控制单个 agent 运行时；stop 设置 `last_state="stopped"`（`manager.py:637-652`）
- F-062: `get_agent(agent_id) -> HarnessAgent`：从 harness_manager 获取 live agent，缺失时根据 row 状态抛出 AGENT_NOT_FOUND/AGENT_FAILED/AGENT_NOT_RUNNING（`manager.py:788-811`）
- F-063: `stream(agent_id, request) -> AsyncIterator` / `call(agent_id, request) -> dict` / `resume_hitl(agent_id, thread_id, decisions)` 委托给 harness_manager（`manager.py:848-883`）
- F-064: `cancel_stream(agent_id, thread_id)` 调用 `harness_manager.cancel()`（`manager.py:885-888`）
- F-065: Thread model 覆盖：`get_thread_model`/`set_thread_model`/`clear_thread_model`（`manager.py:890-901`）
- F-066: `on_provider_changed(*, provider_name=None, active_model_changed=False)`：同步 providers 到 harness → 计算影响 agent 集合 → 有界并行 reload（并发上限 `_PROVIDER_RELOAD_CONCURRENCY = 6`）（`manager.py:72,986-1013`）
- F-067: `reload_all()` / `reload(agent_id)` / `reload_harness_agents()` 三种热重载方式（`manager.py:916-933`）
- F-068: MCP 工具缓存：`_mcp_tool_cache: dict[tuple[int, str, str], list[Any]]`，key 为 `(user_id, server_name, fingerprint)`，通过 `aload_mcp_tools` 加载并 `wrap_tools_for_shared_use` 包装（`manager.py:350-351,1110-1169`）
- F-069: `prepare_chat_mcp(agent_id, names, *, connector_user_id=None) -> list[str]`：确保 MCP servers 已配置且工具已加载，返回加载失败的 server 名列表（`manager.py:1183-1203`）
- F-070: `replace_persistence(repos, config)` 在控制面 DB 重绑定后重建所有 settings stores（`manager.py:356-375`）
- F-071: `resolve_workspace_dir(agent_id, *, persist_if_missing=True) -> Path`：解析 agent 工作区目录，支持 config 中的 `workspace_dir` 或默认 `~/.octop/agents/<agent_id>/`（`manager.py:728-750`）
- F-072: `delete_thread_checkpoint(agent_id, thread_id) -> bool`：最佳努力删除 LangGraph checkpointer 中的对话数据（`manager.py:813-842`）

## Gateway（infra/gateway/gateway.py）

- F-073: `Gateway` 类为全局 AI 交互入口，`__init__(*, agent_manager: AgentManager, repos: RepoBundle)`（`gateway.py:87-114`）
- F-074: Gateway 从 `harness_gateway` 导入 `ChannelCredentialsError`、`ChannelKind`、`ChannelManager`、`ChannelSubject`（`gateway.py:12-15`）
- F-075: Gateway 持有 `_thread_registry: ThreadRegistry`、`_channel_manager: ChannelManager | None`、`_processor: GlobalProcessor | None`、`_dispatcher: SlashDispatcher`、`_ws_hub: WebSocketHub`、`_cli_hub: CliHub`、`_ws_channel: WebSocketChannel | None`、`_cli_channel: CliChannel | None`、`_runtime_status: dict[str, ChannelRuntimeStatus]`（`gateway.py:102-114`）
- F-076: `ChannelRuntimeStatus` 为 frozen dataclass，字段 `connected: bool`、`reason: str | None`、`detail: str | None`、`updated_at: int = 0`；reason 为 locale-neutral 代码（`disabled`/`unregistered`/`error`）（`gateway.py:56-68`）
- F-077: `SlashRuntimeMeta` 为 frozen dataclass，字段 `version: str`、`started_at: int`（`gateway.py:50-53`）
- F-078: `ChannelCreateSpec` 为 dataclass，字段 `channel_id`、`agent_id`、`user_id`、`kind: ChannelKind | str`、`name`、`config: dict`（`gateway.py:71-78`）
- F-079: `boot()` 方法：构造 `GlobalProcessor`（传入 agent_manager/thread_registry/多个 repos/dispatcher/gateway）→ 构造 `ChannelManager(channels={})` → 设置 `_preempt_cancel_on_stop` pre-lock handler → `start()` → 添加 WebSocketChannel（ID=`WS_CHANNEL_ID`）和 CliChannel（ID=`CLI_CHANNEL_ID`）→ 从 DB 加载所有 enabled IM channels 并 `_safe_register_channel`（`gateway.py:185-223`）
- F-080: `refresh_media_backends()` 在 agent 启动完成后为所有已注册 channel 设置 media backend（`gateway.py:225-240`）
- F-081: `reload_channels_from_db()` 丢弃并重新注册 DB 中的 enabled IM channels（用于备份恢复后），保留内置 WS/CLI channels（`gateway.py:242-266`）
- F-082: `create_channel(spec) -> ChannelRow`：若同名同 kind 已存在则更新，否则创建并注册（`gateway.py:283-316`）
- F-083: `push_text_from_session(agent_id, session_key, text, *, task_type="agent", model=None, mcp_servers=None)`：Cron 投递入口，task_type="text" 直接推送，否则通过 agent_manager.stream 运行 LLM 后推送；支持 dashboard WS/CLI 虚拟流和 IM channel（`gateway.py:361-466`）
- F-084: `push_text(channel_type, channel_id, subject, text)` 通过 ChannelManager 主动推送文本到 IM 用户（`gateway.py:509-517`）
- F-085: `probe_channel(channel_id)` / `probe_config(*, agent_id, kind, config)` 通过临时 channel 实例验证凭证（`gateway.py:519-581`）
- F-086: `_preempt_cancel_on_stop` 是 ChannelManager pre-lock handler：解析 `/stop`/`/cancel` slash 命令，在 session 锁获取前调用 `agent_manager.cancel_stream()` 实现抢占式取消（`gateway.py:477-507`）
- F-087: `_register_channel(row)`：解析 config JSON → 规范化 response_mode → 选择 processor → `manager.add_channel(kind, config, tenant_id=row.agent_id, channel_id, processor)` → 设置 media backend → 更新 runtime status（`gateway.py:619-638`）
- F-088: `replace_repos(repos)` 在控制面 DB 重绑定后重定向 thread_registry（`gateway.py:116-122`）

## 数据库层（infra/db/）

- F-089: `DatabasePool` 为 `@runtime_checkable Protocol`，声明 `dialect: str`、`connect()` contextmanager、`transaction()` contextmanager、`close()`（`pool.py:20-30`）
- F-090: `SqlitePool`：单共享连接 + `threading.RLock`，`check_same_thread=False`、`isolation_level=None`（autocommit），启用 `PRAGMA foreign_keys = ON` 和 `PRAGMA journal_mode = WAL`，POSIX 下 chmod 0o600（`pool.py:33-71`）
- F-091: `PostgresPool`：基于 `psycopg_pool.ConnectionPool`（min_size=1, max_size=8），使用 `_compat_row_factory` 产生同时支持 `row["col"]` 和 `row[0]` 的 `_CompatRow`；`_PgConnectionProxy` 将 `?` 占位符改写为 `%s`（`pool.py:74-169`）
- F-092: `qmark_to_pyformat(sql)` 将 `?` 替换为 `%s`（`pool.py:15-17`）
- F-093: `RepoBundle` 为 `@dataclass(frozen=True)`，包含 `db: DatabasePool` + 22 个 Repo 字段：user_repo、invite_repo、agent_repo、provider_repo、channel_repo、cron_repo、session_repo、thread_repo、secret_repo、audit_repo、usage_repo、settings_repo、storage_backend_repo、connector_repo、skill_package_repo、published_expert_repo、knowledge_repo、voice_provider_repo、care_push_repo、proactive_care_config_repo、sso_repo（`services.py:33-84`）
- F-094: `RepoBundle.from_pool(cls, db) -> RepoBundle` classmethod 用同一个 db pool 构造全部 22 个 Repo（`services.py:59-84`）
- F-095: `SharedServices` 为 `@dataclass(frozen=True)`，字段 `paths: PathLayout`、`config: OctopConfig`、`repos: RepoBundle`；提供 `db` 属性和 22 个 repo 委托属性（`services.py:87-179`）
- F-096: `build_shared_services(*, db, paths, config) -> SharedServices` 工厂函数（`services.py:182-189`）
- F-097: `open_database(config, paths) -> DatabasePool`：PostgreSQL 返回 `PostgresPool(conninfo)`，SQLite 返回 `SqlitePool(resolve_sqlite_db_path(...))`（`factory.py:34-44`）
- F-098: `resolve_sqlite_db_path(config, paths) -> Path`：若 `database_in_file` 或环境变量配置了 database，则用 `DatabaseConfig.resolve_sqlite_path(paths.root)`；否则用 `paths.db`（`~/.octop/octop.db`）（`factory.py:12-17`）
- F-099: `should_defer_control_plane_db(config, paths) -> bool`：仅对全新 SQLite 安装（无 DB 文件、无 PostgreSQL 配置、无 `OCTOP_DATABASE_*` 环境变量）返回 True（`factory.py:20-31`）
- F-100: 迁移通过 `run_migrations(db)` 执行，SQLite 和 PostgreSQL 共享同一 schema，迁移文件为编号对 `00N_description.sql` + `00N_description.pg.sql`，当前 schema 版本为 v7（AGENTS.md §7、`server.py:179`）

## 路径布局（infra/utils/paths.py）

- F-101: `PathLayout` 为 `@dataclass(frozen=True)`，单字段 `root: Path`；`from_env()` 类方法从 `OCTOP_HOME` 环境变量或 `~/.octop` 解析（`paths.py:10-20`）
- F-102: `PathLayout.db` 属性返回 `root / "octop.db"`（`paths.py:22-24`）
- F-103: `PathLayout.logs_dir` → `root/logs`，`log` → `logs_dir/octop.log`（`paths.py:26-39`）
- F-104: `PathLayout.config` → `root/config.json`（`paths.py:41-43`）
- F-105: `PathLayout.agents_dir` → `root/agents`，`agent_workspace(agent_id)` → `agents_dir/<agent_id>`，`ensure_agent_workspace` mkdir -p（`paths.py:52-85`）
- F-106: 其他目录：`users_dir`、`expert_market_dir`、`published_experts_dir`、`skill_packages_dir`、`knowledge_dir`、`plugins_dir`、`tool_guard_rules_dir`（`root/security/tool_guard`）、`backups_dir`、`ssl_dir`、`connector_cli_dir`（`paths.py:45-145`）
- F-107: `tool_guard_rules_file` → `root/security/tool_guard/dangerous_shell_commands.yaml`（`paths.py:100-102`）

## API 层（api/app.py）

- F-108: `build_app(server: OctopServer) -> FastAPI` 工厂函数：创建 FastAPI 实例（title="Octop API"），挂载 `server` 到 `app.state.octop_server`，安装异常处理器、CORS、JWT 中间件、setup lockdown 中间件（`app.py:84-113`）
- F-109: 异常处理器：`OctopError` → 本地化 JSONResponse（5xx 记录原始英文日志）；未处理 `Exception` → `INTERNAL_ERROR` 信封（`app.py:60-81`）
- F-110: ACME HTTP-01 challenge 端点 `GET /.well-known/acme-challenge/{token}`（`app.py:115-122`）
- F-111: 挂载 50+ 个 router 模块到 `/api` 前缀，涵盖 setup/auth/agents/chat/channels/cron/connectors/knowledge/providers/admin/backup/tls/security/storage-backends/filesystem/mbti/experts/workspace/agent_files/memory/proactive-care/usage/skill-packages/skills/subagents/terminal/uploads/update/browser/desktop/ollama/onnx/plugins/acp/health/i18n/slash/settings/envs/search/voice/invites/preferences 等（`app.py:124-237`）
- F-112: API 文档使用 Scalar（`scalar_fastapi`），在 `enable_api_docs=True` 时挂载 `/api/docs`（`app.py:239-246`）
- F-113: Dashboard SPA fallback：`GET /{full_path:path}` 返回静态文件，拒绝绝对路径和 `..` 遍历，`assets/` 下内容哈希文件设 `immutable` 缓存，`sw.js`/`manifest.json`/`index.html` 设 `no-cache`（`app.py:33,248-271`）

## CLI 层（cli/）

- F-114: `_LazyCLI(click.Group)` 实现命令延迟加载：`_registry: ClassVar[dict[str, tuple[str, str, str]]] = COMMANDS`；`list_commands` 返回排序后的键；`get_command` 通过 `importlib.import_module` 按需导入模块并获取属性；`format_commands` 直接从 registry 读取帮助文本避免导入（`main.py:57-80`）
- F-115: `cli` 根命令为 `@click.group(cls=_LazyCLI)`，全局选项 `-v/--version`、`--user`（env `OCTOP_USER`）、`--agent`（env `OCTOP_AGENT`）、`--json`（`main.py:83-126`）
- F-116: `COMMANDS` 字典注册 20 个子命令：init、run、service、config、user、agent、chats、channel、cron、provider、models、skills、admin、version、completion、update、clean、backup、acp、plugin（`registry.py:6-31`）
- F-117: `_ensure_utf8_stdio()` 在非 UTF-8 环境（如 Windows GBK）下将 stdout/stderr 重配置为 UTF-8（`errors="replace"`），防止 emoji 导致 UnicodeEncodeError（`main.py:14-38`）
- F-118: `octop run` 命令选项：`--host`、`--port`、`--reload`、`--workers`（默认1）、`--log-level`、`--ssl`、`--ssl-certfile`、`--ssl-keyfile`；host/port 优先级：CLI flags > config.json > 默认值；CLI 传入的 host/port 会持久化到 config.json（`commands/run.py:133-188`）
- F-119: `octop run --ssl` 在无证书时自动生成自签名证书（CN=octop-self-signed，SAN=127.0.0.1，有效期365天），存放于 `~/.octop/ssl/self_signed.crt/key`（`commands/run.py:23-67`）
- F-120: CLI 三层传输：Offline（本地 DB 直读，无需 server）、Embedded/Attach（进程内启动 OctopServer）、External（直接与 OS/daemon 通信）（`docs/cli.md:57-68`、AGENTS.md §5）

## ACP 协议（docs/acp.md）

- F-121: ACP 双向集成：入站（Octop 作为 ACP stdio 服务器，外部 IDE 如 Zed 驱动 Octop agent）、出站（Octop 通过 `acp_runner` 工具委托外部 runner）（`docs/acp.md:3-10`）
- F-122: 四个内置 runner：`opencode`（command=`opencode`, args=`["acp"]`）、`codebuddy`（command=`codebuddy`, args=`["--acp"]`）、`claude_code`（command=`npx`, args=`["-y", "@zed-industries/claude-agent-acp"]`）、`codex`（command=`npx`, args=`["-y", "@zed-industries/codex-acp"]`）（`docs/acp.md:29-34`）
- F-123: Runner 配置为 per-user（存储在 `settings` 表 key `acp_runners:user:{id}`），`acp_runner` 工具启用为 per-agent（`config_json.acp.tool_enabled`）（`docs/acp.md:19-25`）
- F-124: `acp_runner` 工具 action：`list`、`start`（新 session）、`message`（继续 session）、`respond`（响应 permission_required）、`status`、`close`（`docs/acp.md:46-53`）
- F-125: `octop acp [--agent ID] [--debug]` 启动独立 OctopServer 并在 stdin/stdout 上讲 ACP，不需要 `octop run` 运行中（`docs/acp.md:67-80`）
- F-126: HTTP API：`GET/PUT /api/acp`（全局 runners）、`GET/PUT/DELETE /api/acp/{runner_name}`、`GET/PUT /api/agents/{agent_id}/acp`、`PUT /api/agents/{agent_id}/acp/tool`（`docs/acp.md:128-145`）
- F-127: ACP 传输均为 stdio JSON-RPC，Octop 不暴露 HTTP ACP 端点（`docs/acp.md:10`）

## 模块边界禁令（AGENTS.md §5）

- F-128: 依赖流向内：dashboard/ → HTTP → api/ → infra/ → infra/utils/、octop.config；cli/ → launch.py → api/ + infra/（AGENTS.md §5）
- F-129: 硬禁令：`infra/` 不得导入 `api/`/`cli/`/`launch.py`；`api/` 不得导入 `cli/`/`launch.py`；`cli/` 不得导入 `api/`；`infra/db/repos/` 不得导入非 DB `infra` 包；`infra/utils/` 不得导入非 utils `infra` 包（AGENTS.md §5）
- F-130: 只有 `launch.py` 可以在同一模块中同时导入 `infra/server` 和 `api/app`（AGENTS.md §5）
- F-131: `src/octop/dashboard/` 是构建产物，禁止直接编辑，前端源码在 `dashboard/`（AGENTS.md §5/§8）
- F-132: 支持 locale 为 `zh` 和 `en`（`en` 为 fallback），服务端用户可见文本必须来自 i18n bundle（AGENTS.md §7）
- F-133: 数据库 schema 版本当前为 v7（AGENTS.md §7）
