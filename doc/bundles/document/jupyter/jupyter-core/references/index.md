---
okf_version: "0.2"
type: references
title: "Jupyter Core 源码信源索引"
description: "jupyter_core核心源码的事实采集文档索引，所有API引用均可溯源至这些文件"
tags: [references, source, index, paths, command, application, utils, migrate, troubleshoot]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paths-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py"
    title: "jupyter_core/paths.py"
  - id: command-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/command.py"
    title: "jupyter_core/command.py"
  - id: application-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/application.py"
    title: "jupyter_core/application.py"
  - id: utils-init-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/utils/__init__.py"
    title: "jupyter_core/utils/__init__.py"
  - id: migrate-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py"
    title: "jupyter_core/migrate.py"
  - id: troubleshoot-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py"
    title: "jupyter_core/troubleshoot.py"
  - id: version-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/version.py"
    title: "jupyter_core/version.py"
---

# 源码信源索引

本文档索引 jupyter_core 核心源码的事实采集文档。所有概念文档和示例文档中引用的API均溯源至这些信源文件。

## 信源文档清单

| 文档 | 覆盖源码 | 核心内容 |
|------|---------|---------|
| [paths-source.md](paths-source.md) | `paths.py` (~1114行) | 跨平台路径发现（config/data/runtime）、四级路径搜索层级、安全写入(secure_write)、隐藏文件检测、Win32 DACL权限设置、platformdirs集成、环境变量优先级 |
| [command-source.md](command-source.md) | `command.py` (~408行) | jupyter CLI入口、JupyterParser(自定义argparse)、子命令PATH发现、list_subcommands嵌套过滤、跨平台_execvp（Windows Popen替代）、argcomplete补全、核心包版本显示 |
| [application-source.md](application-source.md) | `application.py` (~322行) | JupyterApp(traitlets Application)基类、JupyterAsyncApp异步基类、base_aliases/base_flags、config_file_paths搜索、migrate_config/load_config_file/write_default_config、subcommand os.execv分发、NoStart异常、_TaskRunner后台线程事件循环 |
| [utils-source.md](utils-source.md) | `utils/__init__.py` (~221行) | ensure_dir_exists目录创建、deprecation弃用警告(含_external_stacklevel栈帧计算)、run_sync装饰器(sync/async桥接)、_TaskRunner后台线程事件循环、ensure_event_loop事件循环管理、ensure_async同步/异步统一await |
| [migrate-source.md](migrate-source.md) | `migrate.py` (~282行) | IPython 3.x→Jupyter 4.x迁移工具、JupyterMigrate应用类、目录/文件/配置迁移(migrate_dir/migrate_file/migrate_config)、custom.js/css迁移、配置文件重命名(ipython_→jupyter_)与类名替换、migrated标记防重复幂等 |
| [troubleshoot-source.md](troubleshoot-source.md) | `troubleshoot.py` (~111行) | 环境诊断工具(仅3个函数)、subs外部命令执行与stdout捕获、get_data环境信息字典收集(PATH/sys.path/platform/pip/conda)、main诊断输出入口、argcomplete早退优化 |

## 源码文件清单

| 源码文件 | 行数估算 | 核心类/函数 |
|---------|---------|------------|
| `jupyter_core/paths.py` | ~1114行 | jupyter_config_dir, jupyter_data_dir, jupyter_runtime_dir, jupyter_path, jupyter_config_path, secure_write, is_hidden, prefer_environment_over_user, win32_restrict_file_to_user |
| `jupyter_core/command.py` | ~408行 | JupyterParser, main, list_subcommands, _execvp, _jupyter_abspath, _path_with_self, jupyter_parser, _evaluate_argcomplete |
| `jupyter_core/application.py` | ~322行 | JupyterApp, JupyterAsyncApp, NoStart, base_aliases, base_flags, launch_instance |
| `jupyter_core/utils/__init__.py` | ~221行 | ensure_dir_exists, deprecation, _external_stacklevel, _get_frame, run_sync, ensure_event_loop, ensure_async, _TaskRunner |
| `jupyter_core/migrate.py` | ~282行 | get_ipython_dir, migrate_dir, migrate_file, migrate_one, migrate_static_custom, migrate_config, migrate, JupyterMigrate |
| `jupyter_core/troubleshoot.py` | ~111行 | subs, get_data, main |
| `jupyter_core/version.py` | ~19行 | __version__ = "5.9.1", version_info |
| `jupyter_core/__init__.py` | ~3行 | 导入 __version__, version_info |

## pyproject.toml 关键元数据

- 包名：`jupyter_core`
- 版本：5.9.1
- 构建系统：hatchling (`hatchling.build`)
- 核心依赖：`platformdirs>=2.5`, `traitlets>=5.3`
- Python要求：>=3.10
- 入口脚本：`jupyter = "jupyter_core.command:main"`, `jupyter-migrate = "jupyter_core.migrate:main"`, `jupyter-troubleshoot = "jupyter_core.troubleshoot:main"`
- 模块导出：`jupyter_core.paths`, `jupyter_core.command`, `jupyter_core.application`, `jupyter_core.utils`, `jupyter_core.migrate`, `jupyter_core.troubleshoot`

## 验证阶段方法

所有信源事实均通过以下方法采集：
1. 直接读取源码文件（`Read`工具）
2. 记录关键函数签名、常量值、行为逻辑
3. 在概念文档中通过sources字段溯源

验证阶段（V阶段）将通过`Grep`工具对所有文档中提及的类名、方法名、参数名进行源码级验证。

## 导航

- [概念文档索引](../concepts/index.md)
- [示例文档索引](../examples/index.md)
- [教程首页](../index.md)

```{toctree}
:maxdepth: 7

application-source
command-source
migrate-source
paths-source
troubleshoot-source
utils-source
```
