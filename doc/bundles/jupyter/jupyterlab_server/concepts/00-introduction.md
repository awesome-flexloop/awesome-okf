---
okf_version: "0.2"
type: concept
title: "jupyterlab_server 简介"
description: "了解 jupyterlab_server 在 Jupyter 生态中的定位——JupyterLab 前端与 Jupyter Server 之间的服务端胶合层，核心能力、项目信息与模块速览。"
tags: [jupyterlab, server, introduction, overview, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/__init__.py"
    title: "jupyterlab_server/__init__.py"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/pyproject.toml"
    title: "pyproject.toml"
  - id: version-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/_version.py"
    title: "jupyterlab_server/_version.py"
---

# jupyterlab_server 简介

`jupyterlab_server` 是 JupyterLab 生态中的服务端核心组件，承担 JupyterLab 前端与 Jupyter Server 之间的**REST API 层与页面渲染层**角色。它本身不是一个独立的服务器，而是作为 Jupyter Server 的 ExtensionApp 插件运行，为 JupyterLab 类前端应用提供设置管理、工作区持久化、主题服务、国际化、扩展黑白名单和许可证报告等后端能力。

## 核心定位

```
┌─────────────────────────────────────────────────────┐
│                  JupyterLab 前端                     │
│     (设置面板 / 工作区 / 主题 / 语言切换)              │
└──────────────────────┬──────────────────────────────┘
                       │  HTTP REST API
┌──────────────────────▼──────────────────────────────┐
│               jupyterlab_server                      │
│  ┌──────────┐┌──────────┐┌──────────┐┌────────────┐ │
│  │ Settings ││Workspaces││  Themes  ││Translations│ │
│  └──────────┘└──────────┘└──────────┘└────────────┘ │
│  ┌──────────┐┌──────────┐┌──────────┐               │
│  │ Listings ││Licenses  ││ Lab HTML │               │
│  └──────────┘└──────────┘└──────────┘               │
└──────────────────────┬──────────────────────────────┘
                       │  ExtensionApp 插件机制
┌──────────────────────▼──────────────────────────────┐
│                   jupyter_server                     │
│        (Tornado / 内核管理 / 文件服务 / 认证)         │
└─────────────────────────────────────────────────────┘
```

jupyterlab_server 处于前端与 jupyter_server 之间：
- **向上**：为 JupyterLab 前端提供 REST API 和 HTML 页面渲染
- **向下**：作为 ExtensionApp 插件挂载到 jupyter_server，复用其 Tornado 基础设施、认证、内核管理等能力

## 六大核心子系统

| 子系统 | 模块 | 职责 |
|--------|------|------|
| **设置管理** | `settings_handler.py` + `settings_utils.py` | JSON Schema驱动的前端设置存储、验证和覆盖 |
| **工作区管理** | `workspaces_handler.py` + `workspaces_app.py` | 多工作区布局的CRUD持久化与CLI工具 |
| **主题服务** | `themes_handler.py` | 主题CSS文件服务与URL重写 |
| **国际化** | `translation_utils.py` + `translations_handler.py` | gettext翻译、语言包发现、Schema自动翻译 |
| **扩展列表** | `listings_handler.py` | 扩展黑白名单远程获取与定时刷新 |
| **许可证报告** | `licenses_handler.py` + `licenses_app.py` | 第三方许可证收集与多格式报告（JSON/CSV/Markdown） |

## 项目信息

| 属性 | 值 |
|------|-----|
| 版本 | **2.28.0** |
| Python 版本要求 | ≥ 3.8 |
| 构建系统 | Hatchling ≥ 1.7 |
| 核心依赖 | `jupyter_server` ≥1.21,<3、`jsonschema` ≥4.18.0、`json5` ≥0.9.0、`jinja2` ≥3.0.3、`babel` ≥2.10、`requests` ≥2.31、`packaging` ≥21.3 |
| 可选依赖(openapi) | `openapi_core~=0.18.0`、`ruamel.yaml` |
| 许可证 | BSD-3-Clause |
| 源码仓库 | https://github.com/jupyterlab/jupyterlab_server |
| 文档 | https://jupyterlab-server.readthedocs.io |
| CLI入口 | `python -m jupyterlab_server` |

## 公共 API（__init__.py 导出）

| 导出项 | 类型 | 说明 |
|--------|------|------|
| `LabServerApp` | 类 | 主应用类（ExtensionApp） |
| `LabConfig` | 类 | 配置Mixin类 |
| `LabHandler` | 类 | JupyterLab页面渲染处理器 |
| `add_handlers` | 函数 | 路由注册函数 |
| `LicensesApp` | 类 | 许可证报告CLI |
| `WorkspaceListApp` | 类 | 工作区列表CLI |
| `WorkspaceExportApp` | 类 | 工作区导出CLI |
| `WorkspaceImportApp` | 类 | 工作区导入CLI |
| `translator` | 类(静态) | 全局翻译管理器 |
| `slugify` | 函数 | 工作区名→安全文件名转换 |
| `WORKSPACE_EXTENSION` | 常量 | `.jupyterlab-workspace` |
| `__version__` | 字符串 | 版本号 |

## 模块速览

| 模块 | 主要公开API | 说明 |
|------|-------------|------|
| `app.py` | `LabServerApp`, `main` | 主应用，ExtensionApp入口 |
| `config.py` | `LabConfig`, `get_page_config`, `get_federated_extensions`, `get_static_page_config` | 配置traitlets、页面配置构建、联邦扩展发现 |
| `handlers.py` | `LabHandler`, `add_handlers`, `NotFoundHandler` | 页面渲染、路由注册、URL规范化 |
| `settings_handler.py` | `SettingsHandler` | 设置REST API |
| `settings_utils.py` | `SchemaHandler`, `get_settings`, `save_settings` | 设置核心逻辑、Schema验证、overrides |
| `workspaces_handler.py` | `WorkspacesHandler`, `WorkspacesManager`, `slugify` | 工作区CRUD与文件名安全化 |
| `workspaces_app.py` | `WorkspaceListApp`, `WorkspaceExportApp`, `WorkspaceImportApp` | 工作区CLI命令 |
| `themes_handler.py` | `ThemesHandler` | 主题CSS服务与URL重写 |
| `listings_handler.py` | `ListingsHandler`, `fetch_listings` | 扩展黑白名单 |
| `licenses_handler.py` | `LicensesHandler`, `LicensesManager` | 许可证报告API |
| `licenses_app.py` | `LicensesApp` | 许可证CLI |
| `translation_utils.py` | `TranslationBundle`, `translator` | 国际化核心、语言包管理 |
| `translations_handler.py` | `TranslationsHandler` | 翻译REST API |
| `process.py` | `Process`, `WatchHelper`, `which` | 子进程管理 |
| `process_app.py` | `ProcessApp` | 运行子进程的ExtensionApp基类 |
| `spec.py` | `get_openapi_spec`, `get_openapi_spec_dict` | OpenAPI规范加载 |
| `server.py` | — | ⚠️ 已弃用，从jupyter_server转发 |

---

**下一步阅读：**
- [快速上手](01-getting-started.md) — 安装与基础使用
- [架构总览](02-architecture-overview.md) — 理解模块分层与请求流程
- [应用与配置](03-app-and-config.md) — LabServerApp 与 LabConfig 深入
