---
okf_version: "0.2"
type: concept
title: "jupyter_core 简介"
description: "了解 jupyter_core 在 Jupyter 生态中的定位、核心能力、项目信息与模块速览。"
tags: [jupyter, core, introduction, overview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: version-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/version.py"
    title: "jupyter_core/version.py"
  - id: init-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/__init__.py"
    title: "jupyter_core/__init__.py"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyter_core/pyproject.toml"
    title: "pyproject.toml"
---

# jupyter_core 简介

`jupyter_core` 是 Jupyter 生态系统的核心基础库，为所有 Jupyter 项目（Notebook、JupyterLab、IPython Kernel 等）提供共享的底层基础设施。它本身不包含任何 Notebook 或前端界面逻辑，而是专注于提供一套稳定、跨平台的公共能力。

## 四大支柱

jupyter_core 的核心能力可以归纳为四大支柱：

| 支柱 | 模块 | 职责 |
|------|------|------|
| **跨平台路径管理** | `paths.py` | 统一管理 config/data/runtime 三类目录的定位、搜索路径、安全写入 |
| **命令行调度** | `command.py` | 实现 `jupyter` 根命令，自动发现并调度 `jupyter-*` 子命令 |
| **应用基类** | `application.py` | 提供 `JupyterApp` 基类，封装配置加载、日志、子命令分发等通用逻辑 |
| **工具函数** | `utils/` | 目录创建、弃用警告、异步桥接（`run_sync`、`ensure_event_loop` 等） |

## 项目信息

| 属性 | 值 |
|------|-----|
| 版本 | 5.9.1 |
| Python 版本要求 | ≥ 3.10 |
| 构建系统 | Hatchling (≥ 1.4) |
| 必需依赖 | `platformdirs` ≥ 2.5, `traitlets` ≥ 5.3 |
| 可选依赖 | `argcomplete`（Tab 补全）, `pywin32`（Windows 安全权限） |
| 许可证 | BSD-3-Clause |
| 源码仓库 | https://github.com/jupyter/jupyter_core |

## 生态位置

```
┌─────────────────────────────────────────────────────┐
│                  Jupyter Frontends                   │
│   Notebook   JupyterLab   QtConsole   nbconvert    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              jupyter_client / ipykernel              │
│           （内核管理、消息协议、通信）               │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    jupyter_core                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  paths   │ │ command  │ │application│ │ utils  │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  + migrate.py（配置迁移）                            │
│  + troubleshoot.py（环境诊断）                       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Python 标准库 + traitlets               │
│      platformdirs（跨平台路径） / asyncio / os       │
└─────────────────────────────────────────────────────┘
```

## 核心模块速览

| 模块 | 主要公开 API | 说明 |
|------|-------------|------|
| `jupyter_core.paths` | `jupyter_config_dir()`, `jupyter_data_dir()`, `jupyter_runtime_dir()`, `jupyter_path()`, `jupyter_config_path()`, `secure_write()`, `is_hidden()` | 路径定位与安全文件写入 |
| `jupyter_core.command` | `main()`, `JupyterParser`, `list_subcommands()`, `_execvp()` | `jupyter` CLI 入口与子命令调度 |
| `jupyter_core.application` | `JupyterApp`, `JupyterAsyncApp`, `NoStart`, `base_aliases`, `base_flags`, `launch_instance` | Jupyter 应用基类 |
| `jupyter_core.utils` | `ensure_dir_exists()`, `run_sync()`, `ensure_event_loop()`, `ensure_async()`, `deprecation()` | 通用工具函数与异步桥接 |
| `jupyter_core.migrate` | `migrate()`, `get_ipython_dir()`, `JupyterMigrate` | IPython 3.x → Jupyter 4.x 配置迁移 |
| `jupyter_core.troubleshoot` | `main()`, `get_data()`, `subs()` | 环境诊断信息收集 |

## CLI 命令

安装 jupyter_core 后，会注册三个命令行入口：

| 命令 | 入口点 | 功能 |
|------|--------|------|
| `jupyter` | `jupyter_core.command:main` | 根命令，调度子命令或查询路径/版本信息 |
| `jupyter-migrate` | `jupyter_core.migrate:main` | 将旧版 IPython（< 4.0）配置迁移到 Jupyter 目录 |
| `jupyter-troubleshoot` | `jupyter_core.troubleshoot:main` | 输出环境诊断信息，用于排查安装问题 |

此外，当安装其他 Jupyter 子项目（如 `notebook`、`jupyterlab`）时，它们会自动注册自己的 `jupyter-*` 子命令，通过 `jupyter` 根命令统一调度，例如 `jupyter notebook`、`jupyter lab`。

---

**下一步阅读：**
- [快速上手](01-getting-started.md) — 安装并在 5 分钟内体验核心 API
- [架构总览](02-architecture-overview.md) — 理解四层架构与设计哲学
- [路径系统详解](03-path-system.md) — 深入跨平台路径管理机制
