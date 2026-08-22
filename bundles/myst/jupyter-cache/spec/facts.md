---
type: spec
title: jupyter-cache 源码事实清单
description: jupyter-cache 源码事实清单
tags:
- jupyter-cache
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: jupyter-cache-source
  resource: /references/cache-source.md
  title: jupyter-cache cache-source
- id: jupyter-cache-source-1
  resource: /references/cli-commands.md
  title: jupyter-cache cli-commands
---

# jupyter-cache 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 版本号 `__version__ = "1.0.1"`
- F-002: 包名为 `jupyter-cache`，为 Jupyter Notebook 执行结果提供通用缓存层
- F-003: `__init__.py` 仅含 `__version__` 和 `get_cache()` 函数（懒加载主类以保持 CLI 启动速度）
- F-004: 核心模块分布：`cache/`（数据库+API）、`executors/`（执行引擎）、`cli/`（命令行）、`base.py`（抽象基类）、`readers.py`（notebook读取器）
- F-005: 数据库使用 SQLite，通过 SQLAlchemy ORM，数据库文件名为 `global.db`

## 数据库 Schema（cache/db.py）

- F-006: 三张表：`settings`（键值配置）、`nbproject`（项目notebook记录）、`nbcache`（已执行notebook缓存）
- F-007: `Setting` 表：pk(Integer PK)、key(String 36, unique)、value(JSON)
- F-008: `NbProjectRecord` 表：pk(Integer PK)、uri(String 255 unique)、read_data(JSON)、assets(JSON, 默认list)、exec_data(JSON, nullable)、created(DateTime UTC)、traceback(Text)
- F-009: `NbCacheRecord` 表：pk(Integer PK)、hashkey(String 255 unique)、uri(String 255)、description(String 255)、data(JSON)、created(DateTime UTC)、accessed(DateTime UTC, onupdate自动更新)
- F-010: `create_db()` 使用 `sqlite:///{path}/global.db` 创建引擎，首次创建时自动建表并写入 `__version__.txt`
- F-011: `session_context()` 提供上下文管理器，自动 commit/rollback/close
- F-012: `datetime_utcnow()` 返回 UTC 时间的 lambda 工厂函数
- F-013: `NbCacheRecord.records_to_delete()` 根据 cache_limit 返回最旧记录 PK 列表用于LRU淘汰

## 核心 API（cache/main.py - JupyterCacheBase）

- F-014: `JupyterCacheBase(path)` 初始化缓存目录，懒加载数据库连接
- F-015: 缓存目录结构：`executed/{hashkey}/base.ipynb`（执行后的notebook）+ `executed/{hashkey}/artifacts/`（关联资源）
- F-016: `cache_limit` 默认 1000，通过 `Setting` 表存储，`truncate_caches()` 超限时删除最旧记录
- F-017: `cache_notebook_bundle()` / `cache_notebook_file()` 将notebook添加到缓存（计算hashkey→存储文件→创建NbCacheRecord）
- F-018: `get_cache_bundle()` / `get_cached_notebook()` 通过hashkey检索缓存的notebook
- F-019: `add_notebook_file()` / `add_notebook_files()` 将notebook添加到项目（创建NbProjectRecord）
- F-020: `get_project_notebooks()` 返回项目中所有notebook记录
- F-021: `match_cache_to_notebooks()` 或 `match_cache_to_project()` 通过hashkey匹配缓存与项目notebook
- F-022: `execute_notebook()` / `execute_all_notebooks()` 执行notebook并缓存结果
- F-023: `remove_cache()` / `clear_cache()` 删除缓存记录及文件
- F-024: `get_version()` 读取 `__version__.txt` 返回缓存版本
- F-025: NbArtifacts 类管理执行产物（artifact files），提供 `relative_paths` 和 `__iter__`（yield (相对路径, 文件句柄)）
- F-026: hashkey 通过对notebook内容（代码单元格源码）计算 hash 生成，相同代码→相同hashkey→缓存命中

## 抽象基类（base.py - JupyterCacheAbstract）

- F-027: 定义了缓存API的抽象接口
- F-028: 异常类：`CachingError`、`NbValidityError`、`RetrievalError`
- F-029: 数据类：`ProjectNb`、`CacheBundleIn`、`CacheBundleOut`
- F-030: `NB_VERSION = 4`（Notebook格式版本号）

## Notebook 读取器（readers.py）

- F-031: `get_reader()` 根据 read_data 中的 name 字段返回对应读取器
- F-032: `DEFAULT_READ_DATA = {"name": "filesystem"}`，默认从文件系统读取
- F-033: `NbReadError` 读取失败异常
- F-034: 读取器可通过 entry points 扩展（`entry_points.py` 加载插件）

## 执行器（executors/）

- F-035: `executors/base.py` 定义 `Executor` 抽象基类
- F-036: `executors/basic.py` 实现 `BasicExecutor`，使用 jupyter_client 直接执行notebook
- F-037: `executors/utils.py` 提供执行相关工具函数
- F-038: 执行器支持 entry point 插件扩展
- F-039: 基本执行流程：读取notebook→创建kernel→逐cell执行→收集输出→返回执行后的notebook

## CLI（cli/）

- F-040: CLI 基于 Click 框架，入口命令为 `jcache`
- F-041: 四个子命令组：`cmd_main`（主命令）、`cmd_cache`（缓存管理）、`cmd_notebook`（notebook管理）、`cmd_project`（项目管理）
- F-042: `cli/arguments.py` 定义通用CLI参数，`cli/options.py` 定义通用选项
- F-043: `cli/utils.py` 提供CLI辅助函数（如表格显示）

## Entry Points（entry_points.py）

- F-044: 通过 setuptools entry points 系统注册插件
- F-045: 可扩展点：executors（执行器）、readers（读取器）、converters（转换器）

## 工具函数（utils.py）

- F-046: `to_relative_paths()` 将绝对路径转为相对于基目录的相对路径
- F-047: `shorten_path()` 缩短路径显示
- F-048: 序列化和反序列化相关工具

## 并行与安全

- F-049: SQLAlchemy session 使用上下文管理器确保事务正确关闭
- F-050: `__getstate__` 将 `_db` 设为 None 以支持 pickle 序列化（跨进程传递）
- F-051: 目录创建使用 `parents=True` 递归创建
