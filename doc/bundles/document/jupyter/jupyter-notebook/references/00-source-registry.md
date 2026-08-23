---
title: 信源登记
type: reference
bundle: jupyter-notebook
created: "2026-08-21"
source:
  repo: "https://github.com/jupyter/notebook"
  version: "v7.7.0a1"
  local_path: "d:/spaces/SpecWeave/external/libs/jupyter/notebook"
---

# 信源登记

本文件记录 OKF Wiki 教程所引用的所有源码文件与事实编号，确保每条知识均可溯源。

## 源码文件索引

| 编号 | 文件路径 | 类型 | 说明 |
|------|---------|------|------|
| S-001 | `pyproject.toml` | 配置 | 项目元数据、依赖声明、Hatchling构建配置 |
| S-002 | `package.json` | 配置 | Lerna monorepo管理、前端依赖与脚本 |
| S-003 | `notebook/__init__.py` | Python入口 | 包初始化、server/labextension路径声明 |
| S-004 | `notebook/app.py` | Python核心 | JupyterNotebookApp类、Handler定义、路由注册 |
| S-005 | `notebook/_version.py` | Python版本 | 版本号定义 |
| S-006 | `packages/application/src/app.ts` | TypeScript核心 | NotebookApp前端应用类 |
| S-007 | `packages/application/src/shell.ts` | TypeScript核心 | NotebookShell布局管理器 |
| S-008 | `packages/application/src/tokens.ts` | TypeScript | DI Token定义（INotebookShell等） |
| S-009 | `packages/application-extension/src/index.ts` | TypeScript扩展 | 主应用扩展插件、命令定义 |
| S-010 | `packages/application/src/panelhandler.ts` | TypeScript | 侧边栏/面板Handler实现 |
| S-011 | `packages/application/src/pathopener.ts` | TypeScript | 路径打开器 |
| S-012 | `packages/shell/` | TypeScript | Shell包（v7中已合并入application包） |

## 事实编号索引（F-xxx）

### 项目元数据与构建

| 编号 | 事实 | 信源 |
|------|------|------|
| F-001 | 版本 v7.7.0a1，Python要求 >=3.10 | S-001 |
| F-002 | 构建系统 Hatchling + hatch-jupyter-builder | S-001 |
| F-003 | 核心依赖: jupyter_server>=2.19.0, jupyterlab>=4.7.0a1, notebook_shim>=0.2.4, tornado>=6.2.0 | S-001 |
| F-004 | 前端使用Lerna管理monorepo，包含13个子包 | S-002 |
| F-005 | 发布工具使用 jupyter-releaser | S-001 |

### Python后端

| 编号 | 事实 | 信源 |
|------|------|------|
| F-010 | `JupyterNotebookApp` 继承 `NotebookConfigShimMixin` + `LabServerApp` | S-004:L242 |
| F-011 | `name = "notebook"`, `app_name = "Jupyter Notebook"` | S-004:L245-246 |
| F-012 | `extension_url = "/"`, `default_url = "/tree"` | S-004:L250-251 |
| F-013 | `file_url_prefix = "/tree"`, `load_other_extensions = True` | S-004:L252-253 |
| F-014 | `NotebookConfigShimMixin` 来自外部包 `notebook_shim.shim` | S-004:L32 |
| F-015 | `expose_app_in_browser` traitlet (Bool, 默认False) | S-004:L257-261 |
| F-016 | `custom_css` traitlet (Bool, 默认True) | S-004:L263-269 |
| F-017 | CLI flags: `--expose-app-in-browser`, `--custom-css` | S-004:L271-280 |
| F-018 | 静态目录默认 `notebook/static`，模板目录默认 `notebook/templates` | S-004:L282-288 |
| F-019 | `NotebookBaseHandler` 继承 `ExtensionHandlerJinjaMixin` + `ExtensionHandlerMixin` + `JupyterHandler` | S-004:L49 |
| F-020 | `NotebookBaseHandler.get_page_config()` 构建前端配置对象 | S-004:L56-130 |
| F-021 | 路由注册: `/tree(.*)`→TreeHandler, `/notebooks(.*)`→NotebookHandler, `/edit(.*)`→FileHandler, `/consoles/(.*)`→ConsoleHandler, `/terminals/(.*)`→TerminalHandler, `/custom/custom.css`→CustomCssHandler | S-004:L350-355 |
| F-022 | TreeHandler判断目录→tree页面、.ipynb→/notebooks重定向、其他→/files | S-004:L133-170 |
| F-023 | NotebookHandler遇到目录重定向到/tree | S-004:L203-218 |
| F-024 | CustomCssHandler读取 `jupyter_config_dir/custom/custom.css` | S-004:L221-239 |
| F-025 | page_config包含: appVersion, baseUrl, terminalsAvailable, token, fullStaticUrl, frontendUrl, exposeAppInBrowser, mathjaxConfig, fullMathjaxUrl, jupyterConfigDir, preferredPath | S-004:L62-99 |
| F-026 | JupyterHub集成: 检测hub_prefix，设置hubPrefix/hubHost/hubUser/shareUrl，清空token | S-004:L334-348 |
| F-027 | `_jupyter_server_extension_points()` 返回 `[{"module": "notebook", "app": JupyterNotebookApp}]` | S-003:L12-16 |
| F-028 | `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": "@jupyter-notebook/lab-extension"}]` | S-003:L19-20 |
| F-029 | 入口函数: `main = launch_new_instance = JupyterNotebookApp.launch_instance` | S-004:L363 |

### TypeScript前端

| 编号 | 事实 | 信源 |
|------|------|------|
| F-030 | `NotebookApp extends JupyterFrontEnd<INotebookShell>` | S-006:L27 |
| F-031 | 构造函数默认创建 `NotebookShell`，注册 `Base64ModelFactory`，支持 `mimeExtensions` 创建rendermime插件 | S-006:L28-35 |
| F-032 | `NotebookShell extends Widget implements JupyterFrontEnd.IShell` | S-007:L82 |
| F-033 | Shell区域类型: `'main' | 'top' | 'menu' | 'left' | 'right' | 'down'` | S-007:L47 |
| F-034 | INotebookShell Token: `'@jupyter-notebook/application:INotebookShell'` | S-007:L31-33 |
| F-035 | Down区域默认大小: `DEFAULT_DOWN_AREA_SIZE = 0.25` (25%) | S-007:L26 |
| F-036 | 面板默认rank: `DEFAULT_RANK = 900` | S-007:L77 |
| F-037 | Shell使用PanelHandler管理top/menu区域，SidePanelHandler管理left/right区域 | S-007:L88-91 |
| F-038 | 主应用扩展插件定义命令: duplicate, handleLink, toggleTop, togglePanel, toggleZen, openLab, openTree, rename, resolveTree | S-009:L92-137 |
| F-039 | TREE_PATTERN正则: `/(notebooks\|edit)/(.*)` | S-009:L76 |
| F-040 | 前端包列表: application, application-extension, console-extension, docmanager-extension, documentsearch-extension, help-extension, lab-extension, notebook-extension, terminal-extension, tree, tree-extension, ui-components, _metapackage | S-002 |
