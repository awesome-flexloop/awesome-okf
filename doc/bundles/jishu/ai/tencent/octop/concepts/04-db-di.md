---
type: Concept
title: "数据库层与 DI：DatabasePool、RepoBundle、SharedServices"
description: "DatabasePool Protocol 抽象、SqlitePool（WAL+RLock）与 PostgresPool（psycopg_pool）实现、RepoBundle 22 个 Repository、SharedServices DI 容器、数据库迁移与 Greenfield 延迟绑定。"
tags: [octop, database, sqlite, postgresql, dependency-injection, repository, migration]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/db-layer.md
    title: 数据库层源码信源
---

# 数据库层与依赖注入

Octop 的数据库层通过 Protocol 抽象支持 SQLite（默认）和 PostgreSQL 两种后端，使用 Repository 模式和手动 DI 容器组织数据访问。

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

Protocol 定义了三个核心操作（F-089）：
- `connect()`：获取数据库连接的 context manager
- `transaction()`：获取事务连接的 context manager（BEGIN/COMMIT/ROLLBACK）
- `close()`：关闭连接池
- `dialect`：字符串标识方言（`"sqlite"` 或 `"postgresql"`）

`@runtime_checkable` 允许使用 `isinstance` 检查。

## SqlitePool

```python
class SqlitePool:
    dialect = "sqlite"

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

关键设计（F-090）：

| 特性 | 实现 | 原因 |
|------|------|------|
| 单连接 | 所有线程共享一个 `sqlite3.Connection` | SQLite 单文件数据库，多连接易死锁 |
| RLock | `threading.RLock` 串行化所有访问 | 保护单连接的线程安全 |
| WAL 模式 | `PRAGMA journal_mode = WAL` | 读写不互斥，提升并发 |
| 外键约束 | `PRAGMA foreign_keys = ON` | 强制引用完整性 |
| Autocommit | `isolation_level=None` | 事务由 `transaction()` 显式管理 |
| 文件权限 | POSIX 下 `chmod 0o600` | 仅所有者可读写数据库文件 |

`connect()` 获取锁并 yield 连接；`transaction()` 在锁内执行 `BEGIN`/`COMMIT`/`ROLLBACK`。

## PostgresPool

```python
class PostgresPool:
    dialect = "postgresql"

    def __init__(self, conninfo: str, *, min_size=1, max_size=8):
        self._pool = ConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": _compat_row_factory},
            open=True,
        )
```

关键设计（F-091）：

- 使用 `psycopg_pool.ConnectionPool`，min_size=1, max_size=8
- `_compat_row_factory` 产生 `_CompatRow`，同时支持 `row["col"]` 和 `row[0]` 访问（兼容 sqlite3.Row 接口）
- `_PgConnectionProxy` 包装连接，自动将 `?` 占位符改写为 `%s`（`qmark_to_pyformat`）
- `transaction()` 使用 psycopg 原生 `conn.transaction()` context manager
- 支持 `langgraph-checkpoint-postgres` 作为 LangGraph checkpointer 后端

### 占位符兼容

```python
def qmark_to_pyformat(sql: str) -> str:
    return sql.replace("?", "%s")
```

简单字符串替换使 SQLite 风格的 `?` 占位符 SQL 可在 PostgreSQL 上运行。Repository 层统一使用 `?` 占位符，由 proxy 层转换（F-092）。

## RepoBundle：22 个 Repository

`RepoBundle` 是 frozen dataclass，聚合全部 22 个 Repository（F-093）：

```python
@dataclass(frozen=True)
class RepoBundle:
    db: DatabasePool
    user_repo: UserRepo
    invite_repo: InviteRepo
    agent_repo: AgentRepo
    provider_repo: ProviderRepo
    channel_repo: ChannelRepo
    cron_repo: CronJobRepo
    session_repo: SessionRepo
    thread_repo: ThreadRepo
    secret_repo: SecretRepo
    audit_repo: AuditRepo
    usage_repo: UsageRepo
    settings_repo: SettingsRepo
    storage_backend_repo: BackendRepo
    connector_repo: ConnectorRepo
    skill_package_repo: SkillPackageRepo
    published_expert_repo: PublishedExpertRepo
    knowledge_repo: KnowledgeRepo
    voice_provider_repo: VoiceProviderRepo
    care_push_repo: CarePushRepo
    proactive_care_config_repo: ProactiveCareConfigRepo
    sso_repo: SsoRepo
```

`RepoBundle.from_pool(db)` 工厂方法用同一个 DatabasePool 构造全部 Repository（F-094）。

### Repository 边界

每个 Repository 对应一个或多个数据库表，只允许导入（F-129）：
- `infra/db/_base`
- `infra/utils/`

Repository **不得**导入 `agents/`、`gateway/`、`api/` 或其他编排层代码。这保证了数据访问层的纯净性。

## SharedServices：DI 容器

```python
@dataclass(frozen=True)
class SharedServices:
    paths: PathLayout
    config: OctopConfig
    repos: RepoBundle

    @property
    def db(self) -> DatabasePool:
        return self.repos.db

    # 22 个 repo 委托属性...
    @property
    def agent_repo(self) -> AgentRepo:
        return self.repos.agent_repo
```

`SharedServices` 是系统的 DI 容器（F-095），将三个横切关注点捆绑：
- `paths`：文件系统布局
- `config`：进程配置
- `repos`：全部 Repository

它提供 22 个 repo 的委托 property，使消费者可以写 `services.agent_repo` 而非 `services.repos.agent_repo`。

### 工厂函数

```python
def build_shared_services(*, db, paths, config) -> SharedServices:
    return SharedServices(
        paths=paths,
        config=config,
        repos=RepoBundle.from_pool(db),
    )
```

来源：F-096。

### 使用方式

- **OctopServer**：`self.services` 持有 SharedServices，传递给 `_boot_runtime`
- **AgentManager**：通过 `repos` 参数接收 RepoBundle
- **Gateway**：通过 `repos` 参数接收 RepoBundle
- **API Routers**：通过 `Depends(get_server)` 获取 OctopServer，再访问 `server.services`
- **CronManager/UserManager**：同样通过构造函数注入

这是纯手动 DI，无 IoC 框架——所有装配在 `_boot_runtime` 中显式完成。

## open_database 工厂

```python
def open_database(config: OctopConfig, paths: PathLayout) -> DatabasePool:
    if config.database.is_postgresql:
        return PostgresPool(config.database.postgresql_conninfo())
    return SqlitePool(resolve_sqlite_db_path(config, paths))
```

来源：F-097。

### SQLite 路径解析

```python
def resolve_sqlite_db_path(config, paths) -> Path:
    if config.database_in_file or database_env_configured():
        return config.database.resolve_sqlite_path(paths.root)
    return paths.db  # ~/.octop/octop.db
```

- config.json 中有 `database` 段或设置了 `OCTOP_DATABASE_*` 环境变量 → 使用配置路径
- 否则使用默认 `~/.octop/octop.db`（legacy 布局）

来源：F-098。

## Greenfield 延迟绑定

```python
def should_defer_control_plane_db(config, paths) -> bool:
    if config.database.is_postgresql:
        return False
    if database_env_configured():
        return False
    return not resolve_sqlite_db_path(config, paths).exists()
```

全新安装时（SQLite + 无 DB 文件 + 无环境变量配置）返回 True（F-099）。此时 OctopServer 不打开数据库，HTTP 层先启动，等 setup wizard 完成数据库选型后调用 `bind_control_plane()` 热绑定。

这是 I-01 洞察的核心机制。

## 数据库迁移

- SQLite 和 PostgreSQL **共享同一 schema**（F-100）
- 迁移文件为编号对：
  - `00N_description.sql`（SQLite 语法）
  - `00N_description.pg.sql`（PostgreSQL 语法）
- 通过 `run_migrations(db)` 执行
- 当前 schema 版本：**v7**
- SQLite 无法用 ALTER 表达的表重建在 `migrate.py` helper 中，必须保持幂等
- `_schema_version` 是已应用迁移的水印，不是每次编辑的变更日志

### 资源表约定

API 可见的实体表（agents、channels、threads 等）使用：
- `id`：整数代理主键（AUTOINCREMENT / GENERATED BY DEFAULT AS IDENTITY）
- `{entity}_id`：公开字符串 UNIQUE（ULID/short id），API 和外键引用使用它
- 子表存储字符串 id 并 `REFERENCES parent({entity}_id)`，不 FK 整数 id

不适用于此约定的表：users（整数 user_id FKs）、name-keyed config（providers）、append-only logs（usage_log/audit_log）、KV（settings/secrets）等。

## 数据目录

默认数据目录为 `~/.octop/`，包含：
- `octop.db`：SQLite 数据库文件（WAL 模式下还有 `-wal` 和 `-shm` 文件）
- `config.json`：进程配置
- `logs/`：日志目录
- `agents/<agent_id>/`：Agent 工作区
- `backups/`、`ssl/`、`plugins/`、`knowledge/` 等

可通过 `OCTOP_HOME` 环境变量覆盖（F-101）。

## 相关概念

- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)
- [/concepts/02-agent-runtime.md](02-agent-runtime.md)
