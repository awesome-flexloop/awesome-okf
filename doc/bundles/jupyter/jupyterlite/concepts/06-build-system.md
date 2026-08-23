---
type: Concept
title: Python 构建系统
description: LiteManager构建管理器、Doit任务框架、Addon插件体系、静态站点构建流程
tags: [build, python, doit, addon, plugin, traitlets, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-source
    resource: /references/build-source.md
    title: 构建系统信源
---

## 构建系统概述

JupyterLite 使用 Python 工具链将前端应用、内核资源、示例内容构建为可部署的静态站点。核心构建管理器是 `LiteManager`，它基于 [doit](https://pydoit.org/) 任务自动化框架，通过 Addon 插件体系实现可扩展的构建流程。

## LiteManager

`LiteManager` 位于 `py/jupyterlite-core/jupyterlite_core/manager.py`，继承自 `LiteBuildConfig`（基于 traitlets 的配置类）。

### 核心职责

1. **加载 Addon 插件**：从 entry points 发现并实例化所有 addon
2. **生成 Doit 任务**：遍历 addon 的 hook 方法，生成 doit 任务生成器
3. **执行构建**：通过 doit 命令行运行任务

### 关键 Traitlets 配置

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `strict` | `Bool` | `True` | 出错即停 |
| `task_prefix` | `Unicode` | `""` | 所有任务名前缀 |
| `disable_addons` | `List` | `[]` | 禁用的 addon 列表 |
| `ignore_sys_prefix` | `Bool/List` | - | 是否忽略系统前缀中的 addon |
| `parsed_extra_args` | `Dict` | `{}` | 未被manager使用的额外CLI参数 |

### 初始化流程

```python
def initialize(self):
    self.log.debug("[lite] [addon] loading ...")
    addons = self._addons  # 触发_default_addons → create_addons()
    self.log.debug(f"[lite] [addon] ... OK {len(addons)} addons")
    self.log.debug("[lite] [tasks] loading ...")
    tasks = self._doit_tasks  # 触发_default_doit_tasks → 生成所有任务
    self.log.debug(f"[lite] [tasks] ... OK {len(tasks)} tasks")
```

`_addons` 和 `_doit_tasks` 都使用 traitlets 的 `@default` 装饰器实现惰性初始化。

## Doit 任务框架

[doit](https://pydoit.org/) 是一个 Python 任务自动化工具，类似于 Make，但使用 Python 定义任务。

### DOIT_CONFIG

LiteManager 的默认 doit 配置：

```python
{
    "dep_file": ".jupyterlite.doit.db",  # 依赖数据库（SQLite）
    "backend": "sqlite3",                 # 后端存储
    "verbosity": 2,                       # 日志详细度
}
```

### Hook 和 Phase 体系

构建任务通过 HOOKS（钩子）和 PHASES（阶段）的组合生成。

**PHASES（阶段）**：
- `pre_`：前置阶段（准备工作）
- （空）：主执行阶段
- `post_`：后置阶段（清理/后处理）

**任务命名规则**：`task_{task_prefix}{phase}{hook}`

例如，如果有 `init`、`build`、`status` 三个hook，生成的任务包括：
- `task_pre_init` → `task_init` → `task_post_init`
- `task_pre_build` → `task_build` → `task_post_build`
- `task_pre_status` → `task_status` → `task_post_status`

### 任务依赖链

`_gather_tasks()` 使用 `doit.create_after()` 建立任务依赖：

```python
if not prev_attr:
    return _gather  # 第一个任务无依赖
@doit.create_after(f"{self.task_prefix}{prev_attr}")
def _delayed_gather():
    yield from _gather()
return _delayed_gather
```

这确保了 hook 之间按顺序执行：`pre_init` → `init` → `post_init` → `pre_build` → `build` → ...

每个阶段内，不同 addon 的任务可以并行执行（doit 支持任务并行）。

### 任务生成

每个 addon 通过其 hook 方法 yield doit 任务字典：

```python
# 示例（addon中的build方法）
def build(self, manager):
    # 每个yield是一个doit任务
    yield {
        "name": "copy:static-files",
        "actions": [(self.copy_files, [manager])],
        "file_dep": [self.source_file],
        "targets": [self.output_file],
        "uptodate": [True],  # 总是重新执行或自定义判断
    }
```

LiteManager 在收集任务时，将任务名重命名为 `{addon_name}:{task_name}`：

```python
patched_task["name"] = f"""{self.task_prefix}{name}:{task["name"]}"""
```

## Addon 插件体系

Addon 是 JupyterLite 构建系统的扩展单元，通过 Python entry points 注册。

### Addon 发现

```python
def create_addons(self):
    addons = {}
    for name, addon_implementation in self._addon_implementations().items():
        if name in self.disable_addons:
            continue  # 被配置禁用
        addon_inst = addon_implementation(manager=self)
        addons[name] = addon_inst
    return addons
```

`_addon_implementations()` 调用 `get_addon_implementations()`，通过 `importlib.metadata.entry_points` 查找 `jupyterlite.addon.v0` entry point 组。

### Addon 约定

每个 addon 实例需要遵循以下约定：

1. **构造函数**：接受 `manager` 关键字参数
2. **`__all__` 列表**：声明该 addon 实现了哪些 hook 方法
3. **Hook 方法**：每个 hook 是一个生成器，yield doit 任务字典

```python
class MyAddon:
    __all__ = ["pre_status", "build", "post_build"]

    def __init__(self, manager):
        self.manager = manager

    def pre_status(self, manager):
        """status前的准备工作"""
        yield {"name": "check-env", "actions": [...]}

    def build(self, manager):
        """构建任务"""
        yield {"name": "my-task", "actions": [...], "file_dep": [...], "targets": [...]}
```

### ignore_sys_prefix

从系统 prefix（如 site-packages）安装的 addon 可能被 `ignore_sys_prefix` 配置忽略，这在开发环境中很有用，可以避免加载已安装版本而使用开发版本。

## 运行构建

### doit_run 方法

```python
def doit_run(self, task, *args, raw=False):
    loader = doit.cmd_base.ModuleTaskLoader(self._doit_tasks)
    config = dict(GLOBAL=self._doit_config)
    runner = doit.doit_cmd.DoitMain(task_loader=loader, extra_config=config)
    return runner.run([task, *args])
```

通过 doit 的 Python API 执行任务，支持子命令（如 `build`、`list`、`clean`）。

### CLI 入口

`py/jupyterlite/` 包提供命令行接口，用户通过 `jupyter lite build` 等命令触发构建。

典型命令：

| 命令 | 说明 |
|------|------|
| `jupyter lite build` | 构建静态站点 |
| `jupyter lite serve` | 启动本地开发服务器 |
| `jupyter lite list` | 列出可用任务和addon |
| `jupyter lite check` | 检查环境 |

## 构建产物

构建完成后输出静态站点目录，典型结构：

```
_output/
├── api/
│   ├── contents/       # 内容索引（__all__.json）
│   ├── kernels/        # 内核规格
│   └── drive           # Service Worker drive API
├── files/              # 静态文件（Notebook、数据）
├── lab/                # JupyterLab应用
├── repl/               # REPL应用
├── retro/              # Notebook应用
├── pyodide/            # Pyodide内核资源（WASM、Python包）
├── xeus-python/        # Xeus Python内核资源（如果包含）
├── service-worker.js   # Service Worker
├── index.html          # 入口页面
└── jupyter-lite.json   # 站点配置
```

## 相关概念

- [整体架构](/concepts/01-architecture-overview.md)
- [浏览器存储](/concepts/05-browser-storage.md)
- [扩展架构](/concepts/07-extension-architecture.md)
- [构建系统信源](/references/build-source.md)
