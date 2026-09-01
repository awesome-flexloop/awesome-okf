---
type: Reference
title: "服务器启动与组合根（OctopServer / launch.py）"
description: "OctopServer 进程编排器与 launch.py 组合根的源码信源登记，涵盖启动/停止流程、AppRuntime、Greenfield 延迟绑定、日志与 JWT 密钥。"
tags: [octop, server, launch, composition-root, uvicorn]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-024~F-043
---

# 服务器启动与组合根

本信源登记 `src/octop/infra/server.py` 与 `src/octop/launch.py` 的全部可验证事实。

## 组合根 launch.py

`launch.py` 是 Octop 唯一同时导入 `infra/server` 和 `api/app` 的模块（F-029），承担进程级装配职责：

```python
async def run_foreground(
    *, host, port, reload, workers, log_level,
    ssl_certfile, ssl_keyfile,
) -> None:
    srv = OctopServer()
    await srv.start()
    cfg = srv.services.config if srv.services is not None else srv.config
    # ... TLS listen plan ...
    app = build_app(srv)
    # ... uvicorn serve ...
    finally:
        await srv.stop()
```

- `run_foreground` 为 async 函数（F-024），构造 `OctopServer()` → `start()` → `build_app(srv)` → uvicorn 服务 → `stop()`。
- `run_foreground_blocking(**kwargs)` 通过 `asyncio.run()` 包装，供 Click 命令和测试使用（F-025）。
- 支持 TLS 双端口模式：HTTPS + HTTP companion（ACME challenge + redirect），此时强制 `workers=1` 且禁用 reload（F-026）。
- 单端口模式支持 `reload` 和多 `workers`（F-027）。

## OctopServer 类

`OctopServer`（`infra/server.py:104`）是进程级编排器：

| 成员 | 类型 | 说明 |
|------|------|------|
| `paths` | `PathLayout` | 文件系统布局 |
| `config` | `OctopConfig \| None` | 进程配置 |
| `services` | `SharedServices \| None` | DI 容器（DB 绑定后非 None） |
| `app_runtime` | `AppRuntime \| None` | 运行时单例集合 |
| `expert_catalog` | `ExpertCatalog \| None` | 专家库目录 |
| `subagent_catalog` | `SubagentCatalog \| None` | 子代理目录 |
| `plugin_manager` | `PluginManager \| None` | 插件管理器 |
| `wizard_tokens` | `WizardTokenStore` | 向导令牌（TTL 300s） |

来源：F-030、F-031、F-043。

## AppRuntime 数据类

`AppRuntime`（`server.py:78-101`）持有五个运行时单例：

```python
@dataclass
class AppRuntime:
    agent_registry: AgentManager
    gateway: Gateway
    cron_manager: CronManager
    user_manager: UserManager
    proactive_scheduler: ProactiveCareScheduler

    def replace_services(self, services: SharedServices, config: OctopConfig) -> None: ...
```

`replace_services` 用于 setup wizard 热交换控制面 DB，将所有单例重定向到新的 repos/config（F-032、F-033）。

## start() 启动流程

`start()` 方法（F-035）按序执行：

1. `paths.ensure_root()` 创建 `~/.octop/`
2. 加载 `.env` 文件
3. `_setup_logging()` 配置日志
4. `load_config(paths.config)` 读取 config.json
5. 构造并刷新 `ExpertCatalog`、`SubagentCatalog`
6. 构造 `PluginManager` 并 `load_installed(install_deps=True)`
7. 若 `should_defer_control_plane_db()` 为 True → 生成 wizard 密码后返回（services 为 None）
8. 否则：`open_database()` → `run_migrations()` → `build_shared_services()` → `_ensure_jwt_secret()` → `_boot_runtime()`

## _boot_runtime() 装配顺序

`_boot_runtime(config)`（F-037）严格按序构造：

1. `AgentManager(repos, paths, config, expert_catalog, plugin_manager)`
2. `Gateway(agent_manager, repos)` → `await gateway.boot()`
3. 设置 slash meta（version + started_at）
4. `CronManager(gateway, repos, timezone)` → `await cron_mgr.boot()`
5. 安装 TLS 自动续期 job、自动备份 job
6. `registry.set_cron_manager()` / `set_team_processor()`
7. `ProactiveCareService` + `ProactiveCareScheduler`
8. `await registry.boot()`
9. `await gateway.refresh_media_backends()`
10. `UserManager(services)` → `await user_mgr.boot()`
11. `await proactive_scheduler.start_all()`
12. 组装 `AppRuntime`
13. `resume_pending_index_jobs(services)`

## bind_control_plane() 热绑定

首次运行向导在用户选择数据库后端后调用（F-036）：
- 幂等：已绑定时 no-op
- 重新 `load_config` → `open_database` → `run_migrations` → `build_shared_services` → `_ensure_jwt_secret` → `_boot_runtime`

## stop() 关闭顺序

`stop()`（F-038）按依赖逆序关闭：
`proactive_scheduler` → `cron_manager` → `gateway` → `agent_registry` → `user_manager` → `services.db.close()`。

## 辅助机制

- **JWT 密钥**：`_ensure_jwt_secret()` 通过 `secret_repo.get_or_create("jwt", lambda: os.urandom(32))` 生成 32 字节随机密钥（F-039）。
- **日志**：`TimedRotatingFileHandler` 每日轮转，默认保留 14 天（`OCTOP_LOG_RETENTION_DAYS`），文件 `~/.octop/logs/octop.log`；启动时清理过期日志文件；同时捕获 uvicorn 日志（F-040）。
- **SSO 服务**：`sso_service` 属性懒加载并缓存进程级 `SsoService`，使 JWKS 缓存跨请求存活（F-041）。
- **Wizard 密码**：`require_setup_password=True` 时生成一次性密码写入 `~/octop-login.txt` 并打印黄色 banner（F-042）。

## 相关概念

- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/04-db-di.md](../concepts/04-db-di.md)
