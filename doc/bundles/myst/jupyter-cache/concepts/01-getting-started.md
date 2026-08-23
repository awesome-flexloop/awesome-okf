---
type: Concept
title: 快速开始
description: 安装 jupyter-cache，初始化缓存，添加Notebook，执行和查看结果的基本CLI流程
tags: [jupyter, cache, installation, cli, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:36:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 快速开始

## 安装

```bash
pip install jupyter-cache
```

## CLI 基本工作流程

### 1. 初始化缓存

在项目目录中，缓存默认存储在 `./.jupyter_cache/`：

```bash
jcache project info
```

首次运行时自动创建缓存目录和数据库。

### 2. 添加 Notebook 到项目

```bash
jcache notebook add my_notebook.ipynb
jcache notebook add notebooks/*.ipynb
```

这将 Notebook 注册到项目（记录到 `nbproject` 表），但不执行。

### 3. 查看项目 Notebook

```bash
jcache notebook list
```

输出显示所有已添加的 Notebook 及其缓存状态（✅已缓存/❌失败/-未执行）。

### 4. 执行 Notebook

```bash
# 执行所有未缓存的 Notebook
jcache notebook execute-all

# 执行特定 Notebook（按ID）
jcache notebook execute 1
```

执行成功的 Notebook 将被缓存（存储到 `nbcache` 表和文件系统）。

### 5. 查看缓存

```bash
jcache cache list
```

显示所有已缓存的执行结果，包括 hashkey、源URI、创建时间和访问时间。

### 6. 匹配缓存到项目

```bash
jcache notebook match
```

显示哪些项目 Notebook 命中缓存，哪些需要重新执行。

### 7. 重新执行

修改 Notebook 代码后，重新运行 `execute-all`：
- 代码未变的 Notebook：直接从缓存读取（秒级完成）
- 代码已变的 Notebook：重新执行并更新缓存

## Python API 快速开始

```python
from jupyter_cache import get_cache

# 初始化/打开缓存
cache = get_cache(".jupyter_cache")

# 添加 Notebook
record = cache.add_notebook_file("my_notebook.ipynb")

# 执行所有未缓存的 Notebook
cache.execute_all_notebooks()

# 获取缓存的 Notebook
bundles = cache.get_cache_bundle(record.hashkey)
```

## 典型工作流

```bash
# 首次构建（执行所有 Notebook）
jcache notebook add *.ipynb
jcache notebook execute-all

# 日常开发（仅执行修改的 Notebook）
jcache notebook execute-all  # 未修改的自动从缓存读取

# 清理
jcache cache clear  # 清空缓存重新执行
```

## 验证安装

```bash
jcache --version
# jcache, version 1.0.1

jcache project info
# 显示缓存路径、版本等信息
```

## 相关概念

- [简介](/concepts/00-introduction.md)
- [缓存架构设计](/concepts/02-architecture.md)
- [CLI 命令参考](/concepts/05-cli-reference.md)
- [基本使用示例](/examples/basic-usage.md)
