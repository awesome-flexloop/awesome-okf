---
type: Concept
title: 缓存API详解
description: JupyterCacheBase 的核心Python API：添加/查询/删除缓存、Notebook生命周期管理、Artifact处理
tags: [jupyter, cache, api, python, notebook, artifact]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:40:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 缓存API详解

`JupyterCacheBase` 是 jupyter-cache 的核心 API 类，通过 `get_cache(path)` 获取实例。

## 获取缓存实例

```python
from jupyter_cache import get_cache

# 打开或创建缓存目录
cache = get_cache(".jupyter_cache")

# 指定自定义缓存类（高级用法）
cache = get_cache("/path/to/cache", cache_cls=MyCustomCache)
```

`get_cache()` 使用延迟导入，不会立即加载SQLAlchemy等重型依赖。

## 缓存管理API

### 查询缓存信息

```python
# 获取缓存版本
version = cache.get_version()  # "1.0.1"

# 获取缓存路径
path = cache.path  # PosixPath对象

# 获取/设置缓存上限
limit = cache.get_cache_limit()  # 默认1000
cache.change_cache_limit(500)    # 改为500条
```

### 清空缓存

```python
# 完全清空（删除数据库和文件）
cache.clear_cache()

# 触发LRU淘汰
cache.truncate_caches()
```

## Notebook 缓存API

### 添加Notebook到缓存

```python
# 从文件添加
record = cache.cache_notebook_file(
    "executed_notebook.ipynb",
    uri="source_notebook.ipynb",
    description="my cached notebook"
)

# 从nbformat对象添加
import nbformat
nb = nbformat.read("notebook.ipynb", as_version=4)
record = cache.cache_notebook_bundle(
    nb,
    uri="source_notebook.ipynb",
    description="cached from nbformat"
)
```

返回的 `record` 是 `NbCacheRecord` 对象，包含 `pk`、`hashkey`、`created` 等属性。

### 检索缓存的Notebook

```python
# 通过hashkey获取缓存（返回CacheBundleOut）
bundle = cache.get_cache_bundle(hashkey)

# bundle 包含:
# - bundle.nb: 执行后的Notebook节点
# - bundle.record: NbCacheRecord对象
# - bundle.artifacts: 产物文件迭代器

# 获取所有缓存记录
records = cache.list_cached_records()
for r in records:
    print(r.pk, r.hashkey, r.uri)
```

### 删除缓存

```python
# 通过主键删除
cache.remove_cache(pk=1)

# 通过hashkey删除
cache.remove_cache(hashkey="abc123...")
```

## 项目Notebook API

### 添加Notebook到项目

```python
# 添加单个文件
record = cache.add_notebook_file(
    "notebooks/analysis.ipynb",
    assets=["data/input.csv"]  # 关联资源文件
)

# 批量添加
records = cache.add_notebook_files([
    "notebooks/01_intro.ipynb",
    "notebooks/02_analysis.ipynb",
])
```

### 查询项目Notebook

```python
# 获取所有项目Notebook
records = cache.get_project_notebooks()
for r in records:
    print(r.pk, r.uri, r.traceback)

# 通过PK获取
record = cache.get_project_record(pk=1)

# 通过URI获取
record = cache.get_project_record(uri="notebooks/intro.ipynb")
```

### 从项目移除

```python
# 通过PK移除
cache.remove_project_notes(pks=[1, 2])

# 通过URI移除
cache.remove_project_uris(uris=["notebook.ipynb"])
```

### 清除执行错误

```python
# 移除指定Notebook的traceback
cache.remove_tracebacks(pks=[1])
```

## 执行API

```python
# 执行所有未缓存的Notebook
results = cache.execute_all_notebooks()

# 执行时指定执行器
from jupyter_cache.executors.basic import BasicExecutor
results = cache.execute_all_notebooks(
    executor=BasicExecutor(timeout=60)
)
```

## 缓存匹配API

```python
# 匹配缓存到项目，返回 (匹配列表, 不匹配列表)
matched, unmatched = cache.match_cache_to_project()

for nb in matched:
    print(f"{nb.uri} → 缓存命中 (hashkey: {nb.hashkey})")

for nb in unmatched:
    print(f"{nb.uri} → 需要执行")
```

## Artifact（产物）管理

`NbArtifacts` 类管理Notebook执行产生的文件：

```python
from jupyter_cache.cache.main import NbArtifacts

# 创建产物集合
artifacts = NbArtifacts(
    paths=["output/fig.png", "output/data.csv"],
    in_folder="output/"  # 基目录
)

# 获取相对路径
for rel_path in artifacts.relative_paths:
    print(rel_path)  # fig.png, data.csv

# 遍历文件（yield (相对路径, 文件句柄)）
for rel_path, handle in artifacts:
    content = handle.read()
```

## 异常处理

```python
from jupyter_cache.base import CachingError, NbValidityError, RetrievalError

try:
    bundle = cache.get_cache_bundle("nonexistent_hash")
except RetrievalError:
    print("缓存中未找到该hashkey")

try:
    cache.cache_notebook_bundle(invalid_nb)
except NbValidityError:
    print("Notebook格式无效")

try:
    cache.add_notebook_file("exists.ipynb")
except CachingError:
    print("URI已存在")
```

## 序列化支持

`JupyterCacheBase` 支持 pickle 序列化（`__getstate__` 将数据库连接设为None），可安全在多进程间传递：

```python
import pickle
cache_pickled = pickle.dumps(cache)
cache_restored = pickle.loads(cache_pickled)
# 数据库连接在下次访问时自动重建
```

## 相关概念

- [缓存架构设计](/concepts/02-architecture.md)
- [Notebook执行与插件](/concepts/04-notebook-execution.md)
- [配置项参考](/concepts/07-configuration.md)
- [Python API示例](/examples/python-api.md)
