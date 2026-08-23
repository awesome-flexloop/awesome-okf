---
type: Reference
title: JupyterLite Python构建系统源码信源
description: LiteManager构建管理器、Addon插件体系、Doit任务框架的源码API登记
tags: [build, doit, addon, python, manager, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:06:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-manager
    resource: /references/build-source.md
    title: py/jupyterlite-core/jupyterlite_core/manager.py
---

## 源码位置

- `py/jupyterlite-core/jupyterlite_core/manager.py` — LiteManager构建管理器（~143行）
- `py/jupyterlite-core/jupyterlite_core/config.py` — LiteBuildConfig配置基类
- `py/jupyterlite-core/jupyterlite_core/addons.py` — Addon插件加载（entry_points）
- `py/jupyterlite-core/jupyterlite_core/constants.py` — HOOKS/PHASES/HOOK_PARENTS常量
- `py/jupyterlite-core/jupyterlite_core/` — Addon实现目录

## 导出 API

### LiteManager（manager.py，继承LiteBuildConfig）

| API | 签名 | 行号 |
|-----|------|------|
| `LiteManager` | `class LiteManager(LiteBuildConfig)` | L13 |
| `strict` | `Bool(True)` traitlet，出错即停 | L20 |
| `task_prefix` | `Unicode("")` traitlet，任务名前缀 | L24 |
| `parsed_extra_args` | `Dict()`，额外CLI参数 | L29 |
| `initialize()` | `() => None`，初始化addons和tasks | L36 |
| `doit_run(task, *args, raw=False)` | 运行doit子命令 | L45 |
| `create_addons()` | `() => dict[str, Addon]`，从entry_points加载addons | L57 |
| `_default_doit_config()` | `() => dict`，默认DOIT_CONFIG | L91 |
| `_default_doit_tasks()` | `() => dict`，生成doit任务生成器 | L100 |
| `_gather_tasks(attr, prev_attr)` | 内部：收集特定hook阶段的任务 | L116 |

### 默认 DOIT_CONFIG

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `dep_file` | `.jupyterlite.doit.db` | doit依赖数据库文件 |
| `backend` | `sqlite3` | 后端存储 |
| `verbosity` | `2` | 日志详细度 |

### 构建Hook体系（constants.py）

HOOKS（钩子）和 PHASES（阶段）组合形成任务生成器：

| PHASE | 说明 |
|-------|------|
| `pre_` | 前置阶段 |
| (空) | 主阶段 |
| `post_` | 后置阶段 |

任务命名格式：`task_{prefix}{phase}{hook}`，例如：
- `task_pre_init`
- `task_init`
- `task_post_init`
- `task_pre_build`
- `task_build`
- `task_post_build`

### Addon插件机制

1. **发现**：通过 `importlib.metadata.entry_points` 发现 `jupyterlite.addon.v0` 入口点
2. **加载**：`create_addons()` 实例化每个addon，传入 `manager=self`
3. **禁用**：通过 `disable_addons` 配置跳过指定addon
4. **任务声明**：每个addon通过 `__all__` 列表声明自己实现了哪些hook方法
5. **任务收集**：`_gather_tasks()` 遍历所有addons，收集对应阶段的任务生成器

### Addon基类约定

Addon实例需要：
- 接受 `manager` 关键字参数
- 定义 `__all__` 列表，列出实现的hook名称（如 `["pre_status", "build", "post_build"]`）
- 每个hook方法是一个生成器，yield doit任务字典（包含 `name`、`actions`、`file_dep`、`targets`、`uptodate` 等字段）

## 核心Addon（从源码包结构推断）

| Addon | 路径 | 功能 |
|-------|------|------|
| `contents` | addons/contents.py | 处理内容文件索引 |
| `serve` | addons/serve.py | 本地开发服务器 |
| `build` | addons/build.py | 构建前端应用 |
| `check` | addons/check.py | 环境检查 |
| `list_addons` | addons/list.py | 列出可用addons |
