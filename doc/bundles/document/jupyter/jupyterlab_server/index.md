---
okf_version: "0.2"
type: bundle
title: "jupyterlab_server"
description: "JupyterLab 前端与 Jupyter Server 之间的服务端胶合层：JSON Schema 设置管理、工作区持久化、主题服务、国际化、扩展黑白名单与许可证报告。本知识包从源码出发，系统讲解 jupyterlab_server v2.28.0 的架构、API 和实战用法。"
---

# jupyterlab_server

> JupyterLab 前端与 Jupyter Server 之间的服务端胶合层——提供设置管理、工作区持久化、主题服务、国际化、扩展黑白名单与许可证报告。

`jupyterlab_server` 是 JupyterLab 生态的服务端核心组件。它不是独立的服务器，而是作为 Jupyter Server 的 ExtensionApp 插件运行，为 JupyterLab 类前端应用提供 REST API 和页面渲染服务。作为前端与 `jupyter_server` 之间的中间层，它承载了设置管理、工作区布局持久化、主题CSS处理、多语言国际化、扩展黑白名单和第三方许可证报告等关键能力。

## 快速导航

### 📘 核心概念（10 篇）

**入门**
- [简介](concepts/00-introduction.md) — 项目定位、六大子系统、模块速览、公共API
- [5分钟快速上手](concepts/01-getting-started.md) — 安装、启动、核心配置、REST API体验、CLI工具

**核心架构**
- [架构总览](concepts/02-architecture-overview.md) — 四层架构（App→Config→Handler→Manager）、模块依赖、请求流程、设计模式
- [应用与配置系统](concepts/03-app-and-config.md) — LabServerApp 继承体系、LabConfig Mixin、traitlets配置、page_config多级合并、联邦扩展发现
- [Handler与路由系统](concepts/04-handlers-and-routing.md) — add_handlers() 五阶段注册、URL模式匹配、LabHandler页面渲染、NotFoundHandler前端路由fallback

**子系统**
- [设置系统](concepts/05-settings-system.md) — JSON Schema驱动、三层覆盖（默认→overrides→用户）、Schema验证、SettingsHandler REST API
- [工作区管理](concepts/06-workspaces.md) — slugify文件名安全化、WorkspacesManager CRUD、工作区文件格式、工作区CLI（list/export/import）
- [主题、扩展列表与许可证](concepts/07-themes-listings-licenses.md) — CSS URL重写、扩展黑白名单远程获取与定时刷新、许可证多格式报告（JSON/CSV/Markdown）
- [国际化系统](concepts/08-internationalization.md) — TranslationBundle gettext封装、translator全局管理器、语言包发现、JSON Schema自动翻译、REST API
- [进程管理与CLI工具](concepts/09-process-and-cli.md) — Process跨平台子进程管理、WatchHelper守护进程、ProcessApp基类、测试fixtures
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（3 个）

- [基础使用示例](examples/00-basic-usage.md) — 命令行启动、自定义LabApp应用、Python配置文件、编程方式启动
- [设置系统API](examples/01-settings-api.md) — REST API CRUD、Python get_settings/save_settings、overrides强制配置、Schema验证
- [工作区与国际化](examples/02-workspaces-i18n.md) — 工作区CRUD与slugify、CLI导入导出、TranslationBundle翻译、Schema自动翻译
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（7 个模块组）

- [主应用源码](references/app-source.md) — LabServerApp类、配置traitlets、初始化流程、弃用别名
- [配置系统源码](references/config-source.md) — LabConfig类、页面配置构建、get_federated_extensions()、ConfigManager多级配置
- [路由与页面渲染源码](references/handlers-source.md) — LabHandler页面渲染、add_handlers()路由注册、URL规范化、NotFoundHandler
- [设置系统源码](references/settings-source.md) — SettingsHandler、SchemaHandler基类、JSON Schema验证、三层覆盖、设置持久化
- [工作区管理源码](references/workspaces-source.md) — WorkspacesManager CRUD、slugify、REST端点、工作区CLI子命令
- [国际化系统源码](references/i18n-source.md) — TranslationBundle、translator管理器、语言包发现、Schema翻译
- [辅助模块源码](references/misc-source.md) — ThemesHandler CSS重写、ListingsHandler、LicensesManager、Process跨平台子进程、OpenAPI规范
- [源码信源索引](references/index.md) — 信源文档总目录（含全部20+模块的文件级索引）

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v2.28.0** |
| Python 版本要求 | ≥ 3.8 |
| 构建系统 | Hatchling ≥ 1.7 |
| 核心依赖 | jupyter_server ≥1.21,<3、jsonschema ≥4.18.0、json5 ≥0.9.0、jinja2 ≥3.0.3、babel ≥2.10、requests ≥2.31、packaging ≥21.3 |
| 可选依赖 | openapi_core~=0.18.0、ruamel.yaml |
| 许可证 | BSD-3-Clause |
| 源码仓库 | https://github.com/jupyterlab/jupyterlab_server |
| CLI 命令 | `python -m jupyterlab_server`、`python -m jupyterlab_server.workspaces`、`python -m jupyterlab_server.licenses` |
| 源码路径 | `external/libs/jupyter/jupyterlab_server/` |

## 核心子系统一览

| 子系统 | 核心模块 | REST端点 | 关键类/函数 |
|--------|---------|---------|------------|
| 设置管理 | settings_handler.py + settings_utils.py | `/lab/api/settings/...` | SchemaHandler, get_settings(), save_settings() |
| 工作区管理 | workspaces_handler.py + workspaces_app.py | `/lab/api/workspaces/...` | WorkspacesManager, slugify, WorkspaceXxxApp |
| 主题服务 | themes_handler.py | `/lab/api/themes/...` | ThemesHandler（CSS URL重写） |
| 国际化 | translation_utils.py + translations_handler.py | `/lab/api/translations/...` | TranslationBundle, translator, TranslationsHandler |
| 扩展列表 | listings_handler.py | `/lab/api/listings/...` | ListingsHandler, fetch_listings() |
| 许可证报告 | licenses_handler.py + licenses_app.py | `/lab/api/licenses/...` | LicensesManager, LicensesApp |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [应用与配置](concepts/03-app-and-config.md) → [Handler与路由](concepts/04-handlers-and-routing.md) → [设置系统](concepts/05-settings-system.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
