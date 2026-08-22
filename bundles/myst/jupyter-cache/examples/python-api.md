---
type: Example
title: Python API编程
description: 使用Python API操作jupyter-cache：编程方式管理缓存、执行Notebook、自定义配置和检索结果
tags: [jupyter, cache, python, api, example, programmatic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:52:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# Python API编程

## 基本操作

### 初始化缓存

```python
from jupyter_cache import get_cache

# 打开或创建缓存
cache = get_cache(".jupyter_cache")

# 查看缓存版本
print(cache.get_version())  # "1.0.1"
```

### 添加Notebook

```python
# 添加单个Notebook
record = cache.add_notebook_file("notebooks/intro.ipynb")
print(f"Added: PK={record.pk}, URI={record.uri}")

# 批量添加
records = cache.add_notebook_files([
    "notebooks/01_intro.ipynb",
    "notebooks/02_analysis.ipynb",
])

# 带关联资源
record = cache.add_notebook_file(
    "notebooks/analysis.ipynb",
    assets=["notebooks/data/input.csv"]
)
```

### 执行Notebook

```python
# 执行所有未缓存的Notebook
results = cache.execute_all_notebooks()

# 指定执行器和超时
from jupyter_cache.executors.basic import BasicExecutor
executor = BasicExecutor(timeout=120)
results = cache.execute_all_notebooks(executor=executor)
```

### 查询结果

```python
# 列出项目Notebook
for record in cache.get_project_notebooks():
    print(f"PK={record.pk}, URI={record.uri}, "
          f"traceback={record.traceback or 'None'}")

# 列出缓存记录
for record in cache.list_cached_records():
    print(f"PK={record.pk}, hashkey={record.hashkey[:16]}..., "
          f"uri={record.uri}")
```

### 匹配缓存

```python
# 查看哪些Notebook命中了缓存
matched, unmatched = cache.match_cache_to_project()

for nb in matched:
    print(f"✓ {nb.uri} → cache hit")

for nb in unmatched:
    print(f"✗ {nb.uri} → needs execution")
```

## 缓存管理

### 检索缓存的Notebook

```python
# 通过hashkey获取
bundle = cache.get_cache_bundle(hashkey="abc123...")

# bundle.nb 是执行后的Notebook对象
for cell in bundle.nb.cells:
    if cell.cell_type == "code":
        for output in cell.outputs:
            print(output.get("text", ""))
```

### 添加已执行的Notebook

```python
import nbformat

# 读取已执行的Notebook
nb = nbformat.read("executed_notebook.ipynb", as_version=4)

# 缓存它
record = cache.cache_notebook_bundle(
    nb,
    uri="source_notebook.ipynb",
    description="Manually executed",
    data={"execution_time": 45.2}
)
print(f"Cached: hashkey={record.hashkey}")
```

### 删除缓存

```python
# 通过PK删除
cache.remove_cache(pk=1)

# 清空所有缓存
cache.clear_cache()
```

### 缓存大小限制

```python
# 获取当前限制
print(cache.get_cache_limit())  # 1000

# 修改限制
cache.change_cache_limit(100)

# 触发LRU淘汰（删除超出限制的最旧缓存）
cache.truncate_caches()
```

## 集成到文档构建流程

以下是在 Sphinx/MyST-NB 构建前缓存Notebook执行结果的示例：

```python
"""build_notebooks.py - 预执行Notebook并缓存结果"""

from jupyter_cache import get_cache
from pathlib import Path

def cache_notebooks(notebook_dir: str, cache_path: str = ".jupyter_cache"):
    """执行目录中所有Notebook，使用缓存避免重复执行。"""
    cache = get_cache(cache_path)

    # 添加所有Notebook
    notebook_files = list(Path(notebook_dir).glob("*.ipynb"))
    for nb_path in notebook_files:
        try:
            cache.add_notebook_file(str(nb_path))
        except Exception:
            pass  # 已存在则跳过

    # 执行未缓存的Notebook
    print(f"Executing notebooks from {notebook_dir}...")
    cache.execute_all_notebooks()

    # 报告状态
    matched, unmatched = cache.match_cache_to_project()
    print(f"Cached: {len(matched)}, Needs execution: {len(unmatched)}")

    return cache

if __name__ == "__main__":
    cache_notebooks("notebooks")
```

## 遍历Artifacts

```python
from jupyter_cache.cache.main import NbArtifacts

# 创建产物集合
artifacts = NbArtifacts(
    paths=["output/figure.png", "output/data.csv"],
    in_folder="output/",
    check_existence=True
)

# 获取相对路径
print(list(artifacts.relative_paths))
# [PosixPath('figure.png'), PosixPath('data.csv')]

# 遍历文件内容
for rel_path, handle in artifacts:
    content = handle.read()
    print(f"{rel_path}: {len(content)} bytes")
```

## 异常处理

```python
from jupyter_cache import get_cache
from jupyter_cache.base import (
    CachingError, NbValidityError, RetrievalError
)

cache = get_cache(".jupyter_cache")

try:
    bundle = cache.get_cache_bundle("nonexistent")
except RetrievalError as e:
    print(f"Not in cache: {e}")

try:
    cache.add_notebook_file("not_found.ipynb")
except (CachingError, NbValidityError) as e:
    print(f"Failed to add: {e}")
```

## 相关示例

- [基本CLI使用](/examples/basic-usage.md)
- [CI集成与缓存策略](/examples/ci-integration.md)

## 相关概念

- [缓存API详解](/concepts/03-cache-api.md)
- [读取器与执行器扩展](/concepts/06-readers-and-executors.md)
- [配置项参考](/concepts/07-configuration.md)
