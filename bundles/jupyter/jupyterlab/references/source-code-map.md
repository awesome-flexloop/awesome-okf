---
type: Reference
title: JupyterLab 源码文件地图
description: JupyterLab 核心源码文件路径与模块对应关系速查表，覆盖前端 TypeScript 包与 Python 后端入口
tags: [jupyterlab, source-code, reference, file-map, monorepo]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T08:08:00Z" }
verified: { by: "process:grep-api-verification", at: "2026-08-22T08:08:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: jupyterlab-repo
    resource: https://github.com/jupyterlab/jupyterlab
    title: JupyterLab GitHub Repository
---

## JupyterLab 源码文件地图

本文档是 JupyterLab monorepo 中核心源码文件的路径索引，供阅读源码和开发扩展时快速定位。

## 仓库根目录

| 文件/目录 | 说明 |
|-----------|------|
| `package.json` | 根 workspace 配置，声明所有 packages/examples/dev_mode 为 yarn workspaces |
| `lerna.json` | Lerna monorepo 配置（独立版本模式） |
| `jupyterlab/` | Python 包目录（服务端入口） |
| `packages/` | 前端 TypeScript 包目录（~40+ 个包） |
| `dev_mode/` | 开发模式构建配置（webpack/Rspack） |
| `examples/` | 扩展示例代码 |
| `galata/` | UI 测试框架（基于 Playwright） |
| `buildutils/` | 构建工具脚本 |
| `design/` | 早期设计文档 |
| `docs/` | Sphinx 文档源码 |

## Python 后端（jupyterlab/ 目录）

| 文件 | 核心类/函数 | 说明 |
|------|------------|------|
| `jupyterlab/__init__.py` | `_jupyter_server_extension_paths()`, `_jupyter_server_extension_points()`, `load_jupyter_server_extension`, `LabApp` | Python 包入口，注册 server extension |
| `jupyterlab/labapp.py` | `LabApp`, `LabBuildApp`, `LabCleanApp`, `LabPathApp`, `LabWorkspaceApp`, `LabLicensesApp` | 主应用类与子命令（build/clean/path/workspace/licenses） |
| `jupyterlab/commands.py` | `AppOptions`, `build()`, `clean()`, `ensure_app()`, `ensure_core()`, `ensure_dev()`, `watch()`, `get_app_dir()`, `ProgressProcess`, `get_user_settings_dir()`, `get_workspaces_dir()`, `HERE`, `DEV_DIR`, `REPO_ROOT` | 构建与应用管理命令 |
| `jupyterlab/coreconfig.py` | `CoreConfig` | 核心配置（页面配置数据的静态部分） |
| `jupyterlab/serverextension.py` | `load_jupyter_server_extension()` | Server extension 加载函数 |
| `jupyterlab/handlers/build_handler.py` | `Builder`, `BuildHandler`, `build_path` | 前端构建 HTTP handler |
| `jupyterlab/handlers/extension_manager_handler.py` | `ExtensionHandler`, `extensions_handler_path` | 扩展管理 HTTP API |
| `jupyterlab/handlers/plugin_manager_handler.py` | `PluginHandler`, `plugins_handler_path` | 插件管理 HTTP API |
| `jupyterlab/handlers/announcements.py` | `CheckForUpdate`, `CheckForUpdateHandler`, `NewsHandler`, `NeverCheckForUpdate` | 更新检查与公告 handler |
| `jupyterlab/handlers/error_handler.py` | `ErrorHandler` | 应用错误页面 handler |
| `jupyterlab/extensions/__init__.py` | `MANAGERS` | 扩展管理器注册表 |
| `jupyterlab/extensions/manager.py` | `ExtensionPackage`, `ActionResult`, `PluginManager`, `ExtensionManager`, `ExtensionManagerOptions`, `ExtensionManagerMetadata`, `ExtensionsCache` | 扩展管理抽象基类与数据类 |
| `jupyterlab/extensions/pypi.py` | `PyPIExtensionManager` | PyPI 扩展管理器实现 |
| `jupyterlab/extensions/readonly.py` | `ReadOnlyExtensionManager` | 只读扩展管理器（无安装能力） |
| `jupyterlab/_version.py` | `__version__` | 版本号 |

## 前端核心包（packages/ 目录）

### 应用框架层

| 包路径 | 核心文件 | 核心导出 |
|--------|---------|---------|
| `packages/application/` | `src/lab.ts`, `src/frontend.ts`, `src/shell.ts`, `src/tokens.ts`, `src/index.ts`, `src/router.ts`, `src/layoutrestorer.ts`, `src/mimerenderers.ts`, `src/status.ts`, `src/dockpanel.ts` | `JupyterLab`, `JupyterFrontEnd`, `LabShell`, `ILabShell`, `IRouter`, `ILabStatus`, `IConnectionLost`, `LayoutRestorer`, `JupyterFrontEndPlugin`, `createRendermimePlugins()` |
| `packages/apputils/` | `src/index.ts`, `src/tokens.ts`, `src/dialog.tsx` | `CommandLinker`, `Toolbar`, `MainAreaWidget`, `Dialog`, `ICommandPalette`, `ISplashScreen` 等工具组件与 Token |
| `packages/coreutils/` | `src/pageconfig.ts`, `src/path.ts`, `src/url.ts`, `src/signal.ts`, `src/time.ts`, `src/text.ts`, `src/lru.ts`, `src/pluginregistry.ts`, `src/index.ts` | `PageConfig`, `PathExt`, `URLExt`, `Signal`, `Poll`, `Debouncer`, `Throttler`, `PluginRegistry` |
| `packages/services/` | `src/manager.ts`, `src/tokens.ts`, `src/index.ts`, `src/kernel/*.ts`, `src/session/*.ts`, `src/contents/*.ts`, `src/serverconnection.ts` | `ServiceManager`, `KernelManager`, `SessionManager`, `ContentsManager`, `ServerConnection`, `IServiceManager` + 15 个子管理 Token |

### 文档层

| 包路径 | 核心文件 | 核心导出 |
|--------|---------|---------|
| `packages/docregistry/` | `src/registry.ts`, `src/context.ts`, `src/default.ts`, `src/index.ts` | `DocumentRegistry`, `Context<T>`, `DocumentWidget`, `IDocumentWidget`, `IModelFactory`, `IWidgetFactory`, `IWidgetExtension`, `IModel`, `IContext` |
| `packages/docmanager/` | `src/index.ts` | `DocumentManager`, `IDocumentManager`（文档打开/关闭管理） |
| `packages/rendermime/` | `src/index.ts`, `src/latex.ts`, `src/registry.ts` | `RenderMimeRegistry`, `IRenderMimeRegistry`（MIME 类型渲染注册） |
| `packages/rendermime-interfaces/` | `src/index.ts` | `IRenderMime` 接口定义（跨包共享的 MIME 渲染接口） |

### Notebook 层

| 包路径 | 核心文件 | 核心导出 |
|--------|---------|---------|
| `packages/notebook/` | `src/panel.ts`, `src/widget.ts`, `src/model.ts`, `src/widgetfactory.ts`, `src/actions.tsx`, `src/celllist.ts`, `src/tokens.ts`, `src/index.ts`, `src/history.ts`, `src/toc.ts`, `src/modelfactory.ts` | `NotebookPanel`, `Notebook`, `StaticNotebook`, `NotebookModel`, `NotebookWidgetFactory`, `INotebookTracker`, `INotebookTools`, `INotebookCellExecutor`, `NotebookActions` |
| `packages/cells/` | `src/widget.ts`, `src/model.ts`, `src/inputarea.ts`, `src/index.ts` | `Cell`, `CodeCell`, `MarkdownCell`, `RawCell`, `CellModel`, `CodeCellModel`, `MarkdownCellModel`, `InputArea` |
| `packages/outputarea/` | `src/index.ts`, `src/model.ts`, `src/widget.ts` | `OutputArea`, `OutputAreaModel`, `IOutputAreaModel` |
| `packages/nbformat/` | `src/index.ts` | Jupyter Notebook JSON 格式类型定义（v4） |

### 编辑器层

| 包路径 | 核心文件 | 核心导出 |
|--------|---------|---------|
| `packages/codeeditor/` | `src/index.ts` | `CodeEditor.IEditor` 抽象接口，编辑器无关的 API |
| `packages/codemirror/` | `src/index.ts`, `src/theme.ts`, `src/token.ts` | CodeMirror 6 编辑器实现 |
| `packages/completer/` | `src/index.ts`, `src/widget.ts`, `src/handler.ts`, `src/model.ts`, `src/tokens.ts` | `Completer`, `CompleterModel`, `ICompletionManager`（代码补全） |

### 功能组件层

| 包路径 | 核心文件 | 说明 |
|--------|---------|------|
| `packages/filebrowser/` | `src/index.ts` | 文件浏览器组件 |
| `packages/fileeditor/` | `src/index.ts` | 文本文件编辑器 |
| `packages/launcher/` | `src/index.ts`, `src/tokens.ts` | Launcher（启动器页面） |
| `packages/mainmenu/` | `src/index.ts`, `src/file.ts`, `src/edit.ts`, `src/help.ts`, `src/view.ts`, `src/run.ts`, `src/kernel.ts`, `src/tabs.ts`, `src/tokens.ts` | 主菜单栏 |
| `packages/terminal/` | `src/index.ts`, `src/widget.ts`, `src/tokens.ts` | 终端组件 |
| `packages/console/` | `src/index.ts`, `src/widget.ts`, `src/panel.ts`, `src/foreign.ts`, `src/history.ts`, `src/tokens.ts` | 代码控制台（Console） |
| `packages/debugger/` | `src/index.ts`, `src/service.ts`, `src/model.ts`, `src/handler.ts`, `src/tokens.ts` | 调试器 UI 与服务 |
| `packages/lsp/` | `src/index.ts`, `src/manager.ts`, `src/connection.ts`, `src/feature.ts`, `src/plugin.ts`, `src/adapter.ts`, `src/tokens.ts` | Language Server Protocol 集成 |
| `packages/toc/` | `src/index.ts`, `src/factory.ts`, `src/registry.ts`, `src/panel.ts`, `src/tocitem.tsx`, `src/tokens.ts` | 目录（Table of Contents） |
| `packages/statusbar/` | `src/index.ts`, `src/tokens.ts` | 状态栏 |
| `packages/statedb/` | `src/statedb.ts`, `src/index.ts`, `src/tokens.ts` | `StateDB`（前端状态持久化，基于 localStorage/IndexedDB） |
| `packages/setting/` | — | 设置系统（StateDB 之上的 JSON Schema 设置） |
| `packages/running/` | `src/index.tsx` | 运行中的内核/终端列表面板 |
| `packages/inspector/` | `src/index.ts`, `src/tokens.ts` | 上下文检查器（如对象检查器） |
| `packages/mermaid/` | `src/index.ts`, `src/manager.ts`, `src/mime.ts`, `src/tokens.ts` | Mermaid 图表渲染 |
| `packages/csvviewer/` | `src/index.ts`, `src/widget.ts`, `src/model.ts`, `src/parse.ts` | CSV 文件查看器 |
| `packages/htmlviewer/` | `src/index.ts` | HTML 文件查看器 |
| `packages/imageviewer/` | — | 图片查看器 |
| `packages/logconsole/` | `src/index.ts` | 日志控制台 |
| `packages/metadata-form/` | — | 元数据表单 |

### 扩展包（*-extension）

每个功能包通常对应一个 `-extension` 包，负责将功能注册为 JupyterLab 插件。核心扩展包包括：

- `packages/application-extension/` — 核心应用插件（菜单、命令、布局恢复等）
- `packages/apputils-extension/` — 工具插件（调色板、主题管理、设置编辑器等）
- `packages/notebook-extension/` — Notebook 集成插件
- `packages/filebrowser-extension/` — 文件浏览器插件
- `packages/fileeditor-extension/` — 文件编辑器插件
- `packages/terminal-extension/` — 终端插件
- `packages/console-extension/` — 控制台插件
- `packages/launcher-extension/` — 启动器插件
- `packages/debugger-extension/` — 调试器插件
- `packages/mainmenu-extension/` — 主菜单插件
- `packages/shortcuts-extension/` — 快捷键插件
- `packages/theme-light-extension/` — 亮色主题
- `packages/theme-dark-extension/` — 暗色主题

### 主题与样式

| 包路径 | 说明 |
|--------|------|
| `packages/theme-light-extension/` | 默认亮色主题（JupyterLab Light） |
| `packages/theme-dark-extension/` | 默认暗色主题（JupyterLab Dark） |
| `packages/ui-components/` | 共享 UI 组件（图标、按钮、React 组件） |
| `packages/nbconvert-css/` | nbconvert 导出 CSS |

## 相关概念

- [00 概述与知识地图](/concepts/00-introduction.md)
- [01 整体架构概览](/concepts/01-architecture-overview.md)
- [03 插件系统与依赖注入](/concepts/03-plugin-system.md)
- [07 扩展生态系统](/concepts/07-extension-ecosystem.md)
