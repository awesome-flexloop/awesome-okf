---
type: Reference
title: jupyter-cache 源码路径映射
description: jupyter-cache 核心源文件、数据库表、API方法、CLI命令和扩展点索引
tags: [jupyter, cache, notebook, sqlalchemy, sqlite, cli, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-repo
    resource: https://github.com/executablebooks/jupyter-cache
    title: jupyter-cache GitHub Repository
---

# jupyter-cache 源码路径映射

源路径相对于 `external/libs/ai/executablebooks/jupyter-cache/jupyter_cache/`。

## 核心文件清单

| 文件 | 职责 |
|------|------|
| `__init__.py` | 版本号、get_cache() 延迟入口（保持CLI冷启动速度） |
| `base.py` | 抽象基类 JupyterCacheAbstract、异常类、数据类 |
| `cache/main.py` | JupyterCacheBase 主API实现（300+行） |
| `cache/db.py` | SQLAlchemy ORM模型、数据库创建、session管理 |
| `executors/base.py` | Executor 抽象基类 |
| `executors/basic.py` | BasicExecutor（jupyter_client本地执行） |
| `executors/utils.py` | 执行工具函数 |
| `readers.py` | Notebook读取器（默认filesystem） |
| `entry_points.py` | setuptools entry points 插件加载 |
| `utils.py` | 工具函数（路径处理、缩短路径等） |

## CLI 文件

| 文件 | 职责 |
|------|------|
| `cli/__init__.py` | Click CLI入口（jcache命令） |
| `cli/arguments.py` | 通用CLI参数定义 |
| `cli/options.py` | 通用CLI选项定义 |
| `cli/utils.py` | CLI辅助函数（表格显示等） |
| `cli/commands/cmd_main.py` | 主命令 |
| `cli/commands/cmd_cache.py` | 缓存管理子命令 |
| `cli/commands/cmd_notebook.py` | Notebook管理子命令 |
| `cli/commands/cmd_project.py` | 项目管理子命令 |

## 数据库表

| 表名 | ORM类 | 用途 |
|------|-------|------|
| `settings` | Setting | 键值配置（cache_limit等） |
| `nbproject` | NbProjectRecord | 项目中待执行的notebook列表 |
| `nbcache` | NbCacheRecord | 已执行notebook缓存记录 |

## JupyterCacheBase 核心方法

| 方法 | 功能 |
|------|------|
| `cache_notebook_bundle()` | 将notebook添加到缓存 |
| `get_cache_bundle(hashkey)` | 通过hashkey获取缓存notebook |
| `add_notebook_file(uri)` | 添加notebook到项目 |
| `get_project_notebooks()` | 列出项目notebook |
| `execute_all_notebooks()` | 执行所有待执行notebook |
| `match_cache_to_project()` | 匹配缓存到项目notebook |
| `remove_cache(pk)` | 删除缓存记录 |
| `clear_cache()` | 清空整个缓存 |
| `truncate_caches()` | LRU淘汰超量缓存 |
| `change_cache_limit(size)` | 修改缓存上限 |

## Entry Points 扩展点

| 扩展点 | 用途 | 默认实现 |
|--------|------|---------|
| `jupyter_cache.executors` | Notebook执行引擎 | basic（jupyter_client） |
| `jupyter_cache.readers` | Notebook读取来源 | filesystem |
| `jupyter_cache.converters` | Notebook格式转换 | - |

## 相关概念

- [简介](/concepts/00-introduction.md)
- [缓存架构设计](/concepts/02-architecture.md)
- [缓存API详解](/concepts/03-cache-api.md)
