# 数据库与自动迁移

Jupyter Scheduler 使用 SQLAlchemy ORM 进行数据持久化，默认使用 SQLite 数据库，并内置轻量级自动迁移机制。

## 数据库配置

### 默认数据库

默认数据库路径为 `{jupyter_data_dir()}/scheduler.sqlite`，即 Jupyter 数据目录下的 SQLite 文件。

可通过配置覆盖：
```python
c.SchedulerApp.db_url = "sqlite:///path/to/custom.db"
# 或
c.SchedulerApp.db_url = "postgresql://user:pass@host/db"
```

### 每后端独立数据库

通过 backend_config 可为特定后端配置独立数据库：
```python
c.SchedulerApp.backend_config = {
    "my_backend": {"db_url": "postgresql://..."}
}
```

未配置时所有后端共享全局 db_url。

## ORM 模型

参见 [数据模型](08-data-models.md) 中的 ORM 部分。核心表为 `jobs` 和 `job_definitions`，使用 CommonColumns mixin 共享字段。

## 自动迁移机制

`update_db_schema()` 实现轻量级自动迁移，在 `create_tables()` 中被调用：

```python
def update_db_schema(engine, Base):
    inspector = inspect(engine)
    for table in Base.metadata.sorted_tables:
        table_name = table.key
        if not inspector.has_table(table_name):
            continue  # 新表由create_all创建
        
        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
        
        with engine.begin() as conn:
            for column in table.columns:
                if column.name not in existing_columns:
                    # 生成 ALTER TABLE ADD COLUMN 语句
                    column_type = column.type.compile(dialect=engine.dialect)
                    default = column.default.arg if column.default and callable(column.default.arg) is False else None
                    null = "NULL" if column.nullable else "NOT NULL"
                    sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {column_type} {null}'
                    conn.execute(text(sql))
```

### 迁移策略

- **只增不删**：仅添加缺失的列（ADD COLUMN），不删除或修改现有列
- **Nullable 约束**：新添加的列必须允许 NULL（SQLite ALTER TABLE ADD COLUMN 的限制）
- **默认值**：新列的 default 在迁移时被忽略（代码层面的默认值在ORM层面生效）
- **自动创建**：首次启动时 create_all 创建所有表
- **drop_tables**：开发时可设置 `drop_tables=True` 重建表（生产环境禁用）

### 迁移流程

```
服务器启动
  │
  ▼
create_engine(db_url)
  │
  ▼
update_db_schema(engine, Base)
  │  ├── 检查现有表结构
  │  └── ALTER TABLE ADD COLUMN（添加新字段）
  │
  ▼
Base.metadata.create_all(engine)
  │  └── 创建不存在的表
  │
  ▼
数据库就绪
```

## TaskRunner 的独立缓存

TaskRunner 使用内存 SQLite（`"sqlite://"`）作为调度缓存，与主数据库分离：

```python
# task_runner.py
def __init__(self, ...):
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    self._session = sessionmaker(bind=engine)()
```

缓存表 `job_definitions_cache` 存储调度状态（next_run_time、active、timezone、schedule），与主数据库的 JobDefinition 表分离，原因：
1. 避免跨进程并发问题（TaskRunner 在事件循环中高频读写）
2. 减少对主数据库的轮询压力
3. 缓存数据可从主数据库重建（populate_cache 时全量加载）

## 时间戳

所有时间字段使用**毫秒级 Unix 时间戳**（整数类型），而非 datetime 对象：

```python
def get_utc_timestamp():
    return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)
```

- create_time：记录创建时自动设置
- update_time：每次更新时自动刷新（onupdate）
- start_time/end_time：作业执行开始/结束时间

使用整数时间戳避免数据库间 datetime 类型兼容性问题。

## Session 管理

`create_session(db_url)` 返回 sessionmaker 工厂（非 session 实例），每次使用时创建新 session：

```python
# Scheduler中
self._session = create_session(self.db_url)

# 使用时
session = self._session()
try:
    # 数据库操作
    session.commit()
finally:
    session.close()
```

子进程（ExecutionManager）独立创建 sessionmaker 和 session，不共享父进程的数据库连接。
