---
type: Reference
title: "数据库层：Pool Protocol、RepoBundle 与 SharedServices DI"
description: "DatabasePool Protocol、SqlitePool/PostgresPool 实现、RepoBundle 22 个 Repo、SharedServices DI 容器、open_database 工厂与 Greenfield 延迟绑定机制。"
tags: [octop, database, sqlite, postgresql, di, repository, migration]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-089~F-100
---

# 数据库层：Pool Protocol、RepoBundle 与 SharedServices DI

本信源登记 `src/octop/infra/db/` 下 `pool.py`、`services.py`、`factory.py` 的全部可验证事实。

## DatabasePool Protocol

```python
@runtime_checkable
class DatabasePool(Protocol):
    dialect: str

    @contextmanager
    def connect(self) -> Iterator[Any]: ...

    @contextmanager
    def transaction(self) -> Iterator[Any]: ...

    def close(self) -> None: ...
```

来源：F-089。Protocol 使用 `@runtime_checkable` 装饰，支持 `isinstance` 检查。

## SqlitePool

```python
class SqlitePool:
    dialect: str = "sqlite"

    def __init__(self, path: Path):
        self._conn = sqlite3.connect(
            str(path),
            check_same_thread=False,
            isolation_level=None,  # autocommit
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._lock = threading.RLock()
```

关键特性（F-090）：
- **单共享连接**：所有线程复用同一连接，通过 `threading.RLock` 串行化
- **WAL 模式**：`PRAGMA journal_mode = WAL` 支持并发读写
- **外键约束**：`PRAGMA foreign_keys = ON`
- **autocommit**：`isolation_level=None`，事务通过 `transaction()` context manager 显式 `BEGIN/COMMIT/ROLLBACK`
- **POSIX 权限**：首次创建时 `chmod 0o600`（仅所有者可读写）
- `connect()` 获取 RLock 并 yield 连接；`transaction()` 在锁内执行 BEGIN/COMMIT/ROLLBACK

## PostgresPool

```python
class PostgresPool:
    dialect: str = "postgresql"

    def __init__(self, conninfo: str, *, min_size: int = 1, max_size: int = 8):
        from psycopg_pool import ConnectionPool
        self._pool = ConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": _compat_row_factory},
            open=True,
        )
```

关键特性（F-091）：
- 基于 `psycopg_pool.ConnectionPool`，min_size=1, max_size=8
- `_compat_row_factory` 产生 `_CompatRow` 对象，同时支持 `row["col"]` 和 `row[0]` 访问（兼容 sqlite3.Row 接口）
- `_PgConnectionProxy` 包装 psycopg 连接，将 `?` 占位符改写为 `%s`（`qmark_to_pyformat`）
- `transaction()` 使用 psycopg 原生 `conn.transaction()` context manager

### 占位符转换

```python
def qmark_to_pyformat(sql: str) -> str:
    return sql.replace("?", "%s")
```

简单字符串替换（无语义字符串感知），使 SQLite 风格的 `?` 占位符 SQL 可在 PostgreSQL 上运行（F-092）。

## RepoBundle

`RepoBundle` 是 frozen dataclass，聚合 22 个 Repository（F-093）：

| 字段 | Repository | 职责 |
|------|-----------|------|
| `user_repo` | `UserRepo` | 用户 |
| `invite_repo` | `InviteRepo` | 邀请码 |
| `agent_repo` | `AgentRepo` | Agent |
| `provider_repo` | `ProviderRepo` | LLM Provider |
| `channel_repo` | `ChannelRepo` | IM 通道 |
| `cron_repo` | `CronJobRepo` | 定时任务 |
| `session_repo` | `SessionRepo` | 会话 |
| `thread_repo` | `ThreadRepo` | 线程 |
| `secret_repo` | `SecretRepo` | 密钥（JWT 等） |
| `audit_repo` | `AuditRepo` | 审计日志 |
| `usage_repo` | `UsageRepo` | 使用量 |
| `settings_repo` | `SettingsRepo` | KV 设置 |
| `storage_backend_repo` | `BackendRepo` | 存储后端 |
| `connector_repo` | `ConnectorRepo` | 连接器/MCP |
| `skill_package_repo` | `SkillPackageRepo` | 技能包 |
| `published_expert_repo` | `PublishedExpertRepo` | 已发布专家 |
| `knowledge_repo` | `KnowledgeRepo` | 知识库 |
| `voice_provider_repo` | `VoiceProviderRepo` | 语音 Provider |
| `care_push_repo` | `CarePushRepo` | 主动关怀推送 |
| `proactive_care_config_repo` | `ProactiveCareConfigRepo` | 主动关怀配置 |
| `sso_repo` | `SsoRepo` | SSO 状态 |

`RepoBundle.from_pool(db)` classmethod 用同一个 db pool 构造全部 22 个 Repo（F-094）。

## SharedServices

```python
@dataclass(frozen=True)
class SharedServices:
    paths: PathLayout
    config: OctopConfig
    repos: RepoBundle

    @property
    def db(self) -> DatabasePool: return self.repos.db
    # 22 个 repo 委托属性...
```

`SharedServices` 是 DI 容器（F-095），将 `PathLayout`、`OctopConfig`、`RepoBundle` 捆绑传递给所有领域服务。它提供 `db` 属性和 22 个 repo 的委托 property，使消费者可以写 `services.agent_repo` 而非 `services.repos.agent_repo`。

工厂函数（F-096）：

```python
def build_shared_services(*, db, paths, config) -> SharedServices:
    return SharedServices(paths=paths, config=config, repos=RepoBundle.from_pool(db))
```

## open_database 工厂

```python
def open_database(config: OctopConfig, paths: PathLayout) -> DatabasePool:
    db_cfg = config.database
    if db_cfg.is_postgresql:
        return PostgresPool(db_cfg.postgresql_conninfo())
    return SqlitePool(resolve_sqlite_db_path(config, paths))
```

来源：F-097。

### SQLite 路径解析

```python
def resolve_sqlite_db_path(config, paths) -> Path:
    if config.database_in_file or database_env_configured():
        return db_cfg.resolve_sqlite_path(paths.root)
    return paths.db  # ~/.octop/octop.db
```

- config.json 中显式配置了 `database` 或设置了 `OCTOP_DATABASE_*` 环境变量 → 使用配置路径
- 否则使用默认 `~/.octop/octop.db`（legacy 布局）

来源：F-098。

### Greenfield 延迟绑定

```python
def should_defer_control_plane_db(config, paths) -> bool:
    if config.database.is_postgresql:
        return False
    if database_env_configured():
        return False
    return not resolve_sqlite_db_path(config, paths).exists()
```

仅在以下全部条件满足时返回 True（F-099）：
1. 使用 SQLite（非 PostgreSQL）
2. 未设置任何 `OCTOP_DATABASE_*` 环境变量
3. SQLite 文件不存在（全新安装）

此时 OctopServer.start() 不打开数据库，等待 setup wizard 通过 `bind_control_plane()` 热绑定。

## 数据库迁移

- SQLite 和 PostgreSQL 共享同一 schema（F-100）
- 迁移文件为编号对：`00N_description.sql`（SQLite）+ `00N_description.pg.sql`（PostgreSQL）
- 当前 schema 版本为 v7
- 通过 `run_migrations(db)` 执行
- SQLite 无法用 ALTER 表达的重建逻辑在 `migrate.py` helper 中，必须幂等

## 模块边界

`infra/db/repos/` 中的每个 Repo 只允许导入 `infra/db/_base`、`infra/utils/`，不得导入 `agents/`、`gateway/`、`api/` 或其他编排层代码（F-129）。

## 相关概念

- [/concepts/04-db-di.md](/concepts/04-db-di.md)
- [/concepts/01-server-lifecycle.md](/concepts/01-server-lifecycle.md)
- [/concepts/00-architecture.md](/concepts/00-architecture.md)
