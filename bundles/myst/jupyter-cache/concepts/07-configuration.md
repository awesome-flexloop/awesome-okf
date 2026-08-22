---
type: Concept
title: 配置项参考
description: jupyter-cache的缓存限制、执行配置、数据库路径等配置项说明
tags: [jupyter, cache, configuration, settings, cache-limit, database]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:48:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 配置项参考

## 缓存路径配置

### 默认路径

默认缓存目录为当前工作目录下的 `.jupyter_cache/`。

### 指定缓存路径

**CLI方式**：
```bash
jcache -p /custom/cache/path cache list
```

**Python API方式**：
```python
from jupyter_cache import get_cache
cache = get_cache("/custom/cache/path")
```

### 缓存目录结构

```
{cache_path}/
├── global.db              # SQLite数据库
├── __version__.txt        # 版本标识
└── executed/
    └── {hashkey}/
        ├── base.ipynb
        └── artifacts/
```

## 缓存大小限制

### 默认值

默认缓存上限为 **1000** 条记录（`DEFAULT_CACHE_LIMIT = 1000`）。

### 查看当前限制

```bash
jcache cache limit
```

```python
cache.get_cache_limit()  # 1000
```

### 修改缓存限制

```bash
jcache cache limit 500
```

```python
cache.change_cache_limit(500)
```

缓存限制存储在 `settings` 表中，键为 `cache_limit`。

### LRU淘汰机制

当缓存记录数超过限制时，`truncate_caches()` 按以下规则淘汰：
1. 按 `accessed` 字段升序排列（最久未访问的在前）
2. 删除超出限制的记录
3. 同时删除文件系统上对应的 `executed/{hashkey}/` 目录

注意：淘汰在添加新缓存时触发（写入时检查），不会定期自动清理。

## 执行配置

### 超时设置

通过 `exec_data` 传递给执行器：

```python
cache.execute_all_notebooks(
    exec_data={"timeout": 120}  # 每个cell超时120秒
)
```

### 错误处理

```python
cache.execute_all_notebooks(
    exec_data={"allow_errors": True}  # 遇到错误继续执行
)
```

- `allow_errors=False`（默认）：遇到第一个错误即停止执行，记录traceback
- `allow_errors=True`：继续执行后续单元格，错误信息记录在输出中

### Kernel配置

```python
cache.execute_all_notebooks(
    exec_data={"kernel_name": "python3"}
)
```

## Notebook读取配置

通过 `read_data` 字典配置读取行为：

```python
# 默认文件系统读取
read_data = {"name": "filesystem"}

# 自定义读取器
read_data = {"name": "s3", "bucket": "my-bucket"}
```

`read_data` 必须包含 `name` 字段（读取器名称），其他字段为该读取器的配置。

## Artifact（产物）配置

添加Notebook时可指定关联资源文件：

```python
cache.add_notebook_file(
    "notebook.ipynb",
    assets=["data/input.csv", "images/logo.png"]
)
```

`assets` 必须是Notebook所在目录或其子目录中的文件路径（验证在`validate_assets()`中进行）。

## 数据库配置

### 数据库类型

使用SQLite数据库，文件名为 `global.db`，存储在缓存目录中。

### 连接管理

数据库连接通过懒加载创建（首次访问 `cache.db` 属性时）：

```python
@property
def db(self):
    if self._db is None:
        self._db = create_db(self.path)
    return self._db
```

Session 使用 `session_context()` 上下文管理器：

```python
with session_context(db) as session:
    result = session.query(Setting).filter_by(key=key).one_or_none()
    session.commit()
```

- 自动 commit（无异常时）
- 异常时 rollback
- 总是关闭 session
- OperationalError 转换为友好提示

### 版本管理

创建缓存时写入 `__version__.txt` 文件记录版本号，用于后续版本迁移检测。

```python
cache.get_version()  # "1.0.1"
```

## CLI详细输出

使用 `-v/--verbose` 启用详细输出：

```bash
jcache -v notebook execute-all
```

## 环境变量

当前版本不使用环境变量配置，所有配置通过CLI参数、Python API或数据库settings表完成。

## 相关概念

- [缓存架构设计](/concepts/02-architecture.md)
- [缓存API详解](/concepts/03-cache-api.md)
- [CLI命令详解](/concepts/05-cli-reference.md)
- [CI集成示例](/examples/ci-integration.md)
