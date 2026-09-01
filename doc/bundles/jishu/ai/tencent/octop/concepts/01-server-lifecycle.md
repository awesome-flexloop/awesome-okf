---
type: Concept
title: "服务器生命周期：OctopServer 启动/停止与 AppRuntime"
description: "OctopServer 的 start/stop 流程、_boot_runtime 装配顺序、Greenfield 延迟绑定、AppRuntime 运行时单例、热替换机制。"
tags: [octop, server, lifecycle, startup, shutdown, app-runtime]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/server-launch.md
    title: 服务器启动与组合根
---

# 服务器生命周期：OctopServer

`OctopServer` 是 Octop 的进程级编排器，负责按正确顺序装配和拆除所有运行时单例。

## 三种状态

OctopServer 实例在生命周期中经历三种状态：

```
构造（__init__）
    │
    ▼
start() ──► [延迟模式] services=None, app_runtime=None
    │              │
    │              ▼
    │        bind_control_plane()  ← Setup wizard 完成数据库选型
    │              │
    ▼              ▼
[完整模式] services≠None, app_runtime≠None
    │
    ▼
stop() → 资源释放
```

`database_bound` 属性返回 `self.services is not None and self.app_runtime is not None`，用于判断当前处于哪种模式（F-034）。

## start() 完整流程

```python
async def start(self) -> None:
    if self._started:
        return
    self.paths.ensure_root()                    # 1. 创建 ~/.octop/
    apply_env_file(...)                         # 2. 加载 .env
    self._setup_logging()                       # 3. 配置日志
    config = load_config(self.paths.config)     # 4. 加载 config.json
    self.config = config

    # 5. 加载专家库/子代理目录/插件
    self.expert_catalog = ExpertCatalog(...)
    self.expert_catalog.refresh()
    self.subagent_catalog = SubagentCatalog(...)
    self.subagent_catalog.refresh()
    self.plugin_manager = PluginManager(...)
    self.plugin_manager.load_installed(install_deps=True)

    # 6. Greenfield 判断
    if should_defer_control_plane_db(config, self.paths):
        self._started = True
        self._emit_wizard_password(user_count=0)
        return  # ← 延迟模式：不打开数据库

    # 7. 完整启动
    db = open_database(config, self.paths)
    run_migrations(db)
    self.services = build_shared_services(db=db, paths=self.paths, config=config)
    self._ensure_jwt_secret()
    await self._boot_runtime(config)
    self._started = True
    self._emit_wizard_password(user_count=self.user_manager.count())
```

来源：F-035。

### Greenfield 延迟绑定

当满足以下全部条件时，OctopServer 以"无数据库"模式启动（I-01、F-099）：

1. 使用 SQLite 驱动（非 PostgreSQL）
2. 未设置任何 `OCTOP_DATABASE_*` 环境变量
3. SQLite 文件不存在（全新安装）

此时 HTTP 服务先启动，setup lockdown 中间件封锁非 setup 路由，用户通过浏览器向导选择数据库后端。向导完成后调用 `bind_control_plane()` 热绑定。

### bind_control_plane()

```python
async def bind_control_plane(self) -> None:
    if self.database_bound:
        return  # 幂等
    config = load_config(self.paths.config)
    db = open_database(config, self.paths)
    run_migrations(db)
    self.services = build_shared_services(...)
    self._ensure_jwt_secret()
    await self._boot_runtime(config)
```

此方法在 setup wizard 持久化 `database` 配置到 config.json 后调用，无需重启进程（F-036）。

## _boot_runtime() 装配顺序

这是系统的核心装配方法，严格按依赖顺序构造五个运行时单例（F-037）：

```
1. AgentManager(repos, paths, config, expert_catalog, plugin_manager)
      ↓ 传入 repos
2. Gateway(agent_manager, repos)
      await gateway.boot()
      → 构造 GlobalProcessor
      → 构造 ChannelManager
      → 注册 WebSocketChannel + CliChannel
      → 加载 IM channels from DB
      ↓
3. gateway.set_slash_meta(version, started_at)
      ↓
4. CronManager(gateway, repos, timezone)
      await cron_mgr.boot()
      → install_auto_renewal_job(cron_mgr, paths)    # TLS 续期
      → install_auto_backup_job(cron_mgr, server)    # 自动备份
      ↓
5. registry.set_cron_manager(cron_mgr)
   registry.set_team_processor(gateway.processor)
      ↓
6. ProactiveCareService(gateway, care_push_repo, agent_manager, timezone)
   ProactiveCareScheduler(care_service, config_repo, session_repo)
      ↓
7. await registry.boot()
      → HarnessAgentManager 构造
      → 加载所有 enabled agents
      ↓
8. await gateway.refresh_media_backends()
      ↓ （Gateway 先于 agents boot，此时 media backends 才可解析）
9. UserManager(services)
      await user_mgr.boot()
      ↓
10. await proactive_scheduler.start_all()
      ↓
11. self.app_runtime = AppRuntime(
        agent_registry=registry,
        gateway=gateway,
        cron_manager=cron_mgr,
        user_manager=user_mgr,
        proactive_scheduler=proactive_scheduler,
    )
      ↓
12. resume_pending_index_jobs(services)  # 恢复未完成的知识库索引
```

关键顺序约束：
- Gateway 必须在 AgentManager 之后构造（Gateway 持有 agent_manager 引用）
- Gateway.boot() 必须在 registry.boot() 之前（GlobalProcessor 需要先就绪）
- `refresh_media_backends()` 必须在 agents 启动后调用（解决启动顺序间隙）

## AppRuntime

```python
@dataclass
class AppRuntime:
    agent_registry: AgentManager
    gateway: Gateway
    cron_manager: CronManager
    user_manager: UserManager
    proactive_scheduler: ProactiveCareScheduler
```

AppRuntime 是五个运行时单例的不可变容器（F-032）。它的 `replace_services(services, config)` 方法支持在控制面 DB 热交换后将所有单例重定向到新的 repos（F-033）：

```python
def replace_services(self, services, config):
    self.user_manager.replace_services(services)
    self.agent_registry.replace_persistence(services.repos, config)
    self.gateway.replace_repos(services.repos)
    self.cron_manager.replace_repos(services.repos)
    self.proactive_scheduler.replace_persistence(...)
```

## stop() 关闭顺序

关闭顺序与启动顺序相反（F-038）：

```
1. proactive_scheduler.shutdown()
2. cron_manager.shutdown()
3. gateway.shutdown()
4. agent_registry.shutdown()
5. user_manager.shutdown_all()
6. services.db.close()
7. 清空 services / app_runtime / _started
```

所有关闭操作在 `try/finally` 中执行，确保即使某个组件关闭失败也会关闭数据库连接。

## 辅助机制

### JWT 密钥

`_ensure_jwt_secret()` 在数据库绑定后确保 JWT 签名密钥存在（F-039）：

```python
self.services.secret_repo.get_or_create("jwt", lambda: os.urandom(32))
```

密钥为 32 字节随机值，持久化在 `secrets` 表中。

### 日志系统

- `TimedRotatingFileHandler` 每日午夜轮转
- 默认保留 14 天（`OCTOP_LOG_RETENTION_DAYS` 环境变量可覆盖）
- 日志文件：`~/.octop/logs/octop.log`
- 启动时额外清理过期轮转文件（安全网）
- uvicorn 的 access/error 日志也写入同一文件

来源：F-040。

### Wizard 密码

首次启动时若 `require_setup_password=True`，生成一次性随机密码写入 `~/octop-login.txt`，并在终端打印黄色 banner。用户在 Dashboard setup wizard 中粘贴此密码完成初始化（F-042）。

### SSO 服务懒加载

`sso_service` 属性首次访问时构造 `SsoService` 并缓存，使 OIDC discovery 文档和 JWKS 缓存跨请求存活（F-041）。

## 相关概念

- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/02-agent-runtime.md](02-agent-runtime.md)
- [/concepts/03-gateway-channels.md](03-gateway-channels.md)
