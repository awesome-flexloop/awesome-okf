---
type: Reference
title: "JupyterLab 源码文件地图"
description: JupyterLab 核心源码文件路径与模块对应关系速查表，覆盖 Python 后端入口、前端 103 个 packages 分类及关键 TypeScript 文件深度索引
tags: [jupyterlab, source-code, reference, file-map, monorepo, python-backend, frontend-packages]
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
---

## JupyterLab 源码文件地图

本文档是 JupyterLab monorepo 中核心源码文件的路径索引，覆盖 Python 后端入口文件、前端 103 个 packages 的分类速查，以及关键 TypeScript 源文件的深度索引。所有路径均相对于仓库根目录 `external/libs/jupyter/jupyterlab/`。

## 一、Python 后端核心文件

Python 包位于 `jupyterlab/` 目录，基于 Tornado 和 Jupyter Server 2.x 构建。

### 1.1 应用入口与主应用

| 文件路径 | 关键类/函数 | 说明 |
|----------|------------|------|
| `jupyterlab/__init__.py` | `load_jupyter_server_extension`、`_jupyter_server_extension_paths()`、`_jupyter_server_extension_points()` | 包入口，导出 `__version__`，同时支持经典 Notebook Server 和 Jupyter Server 2.x 双协议注册（F-020, F-155, F-156） |
| `jupyterlab/__main__.py` | `main()` | `python -m jupyterlab` 入口，委托给 `labapp.main()`（F-022） |
| `jupyterlab/_version.py` | `VersionInfo` namedtuple | 版本定义，当前版本 4.7.0-alpha.1，包含 major/minor/micro/releaselevel/serial 五字段（F-011, F-012） |
| `jupyterlab/labapp.py` | `LabApp`、`LabBuildApp`、`LabCleanApp`、`LabPathApp`、`LabWorkspaceApp`、`LabLicensesApp` | 主应用类，继承 `NotebookConfigShimMixin` 和 `LabServerApp`；含三种运行模式、page_config 设置、Handler 注册、子命令注册（F-023, F-076-F-097） |
| `jupyterlab/serverextension.py` | `load_jupyter_server_extension()` | 旧版 Notebook Server 兼容 shim，创建 LabApp 实例并设置 favicon/logo 重定向（F-024） |
| `jupyterlab/labhubapp.py` | `SingleUserLabApp` | JupyterHub 单用户集成，继承 `make_singleuser_app(ServerApp)`，默认 URL `/lab`（F-028, F-157） |

### 1.2 构建系统与命令

| 文件路径 | 关键类/函数 | 说明 |
|----------|------------|------|
| `jupyterlab/commands.py` | `AppOptions`、`_AppHandler`、`ProgressProcess`、`build()`、`clean()`、`enable_extension()`、`disable_extension()` | 构建系统核心，管理 Rspack 构建、Yarn 依赖、扩展启用/禁用、目录解析（F-025, F-124-F-136） |
| `jupyterlab/coreconfig.py` | `CoreConfig` | 核心包配置管理，从 staging/package.json 读取，支持 add/remove/clear_packages（F-026） |
| `jupyterlab/labextensions.py` | `main()` | `jupyter-labextension` CLI 入口，提供 install/uninstall/enable/disable/list/update 子命令（F-027） |
| `jupyterlab/federated_labextensions.py` | 委托函数 | 联合扩展的已弃用包装，委托给 `jupyter_builder.federated_extensions`（F-029） |
| `jupyterlab/upgrade_extension.py` | 升级工具 | 基于 copier 模板引擎的扩展升级工具（F-034） |
| `buildapi.py` | `builder()` | Hatch 构建钩子，调用 npm_builder，删除 .js.map，验证版本一致性（F-042, F-140） |

### 1.3 扩展管理（Python 侧）

| 文件路径 | 关键类/函数 | 说明 |
|----------|------------|------|
| `jupyterlab/extensions/__init__.py` | `MANAGERS`、`get_readonly_manager()`、`get_pypi_manager()` | 从 entry point `jupyterlab.extension_manager_v1` 动态加载扩展管理器工厂（F-113, F-114） |
| `jupyterlab/extensions/manager.py` | `ExtensionPackage`、`ActionResult`、`PluginManagerOptions`、`ExtensionManagerOptions`、`PluginManager`、`ExtensionManager` | 扩展管理核心：`ExtensionPackage` frozen dataclass 定义扩展元数据；`PluginManager` 管理插件锁定（sys_prefix/user/system 三级）；`ExtensionManager` 抽象基类要求实现 metadata/get_latest_version/list_packages/install/uninstall（F-115-F-119） |
| `jupyterlab/extensions/readonly.py` | `ReadOnlyExtensionManager` | 只读扩展管理器，不支持安装/卸载，install/uninstall 返回 error 状态（F-120） |
| `jupyterlab/extensions/pypi.py` | `PyPIExtensionManager` | PyPI 扩展管理器，使用 pip + httpx，支持代理配置，使用 async_lru 缓存（F-121-F-123） |

### 1.4 HTTP Handlers（/lab/api/*）

| 文件路径 | 关键类/函数 | 路由 | 说明 |
|----------|------------|------|------|
| `jupyterlab/handlers/announcements.py` | `NewsHandler`、`CheckForUpdateHandler`、`NeverCheckForUpdate`、`CheckForUpdate`、`Notification` | `/lab/api/news`、`/lab/api/update` | 公告 Atom feed 解析、PyPI 版本检查；`Notification` frozen dataclass 含 createdAt/message/type/link 等字段（F-098-F-103） |
| `jupyterlab/handlers/build_handler.py` | `Builder`、`BuildHandler` | `/lab/api/build` | 构建状态管理，ThreadPoolExecutor(max_workers=5) 异步执行，支持 GET/POST/DELETE；构建失败自动 clean+rebuild（F-104-F-106） |
| `jupyterlab/handlers/error_handler.py` | `ErrorHandler` | — | 返回简单 HTML 错误页面，构建失败时显示而非退出进程（F-107） |
| `jupyterlab/handlers/extension_manager_handler.py` | `ExtensionHandler` | `/lab/api/extensions` | 扩展管理 API，GET 支持分页（refresh/query/page/per_page）和 RFC 5988 Link 头；POST 支持 install/uninstall/enable/disable（F-108-F-110） |
| `jupyterlab/handlers/plugin_manager_handler.py` | `PluginHandler` | `/lab/api/plugins` | 插件管理 API，GET 返回锁定信息（lockRules/allLocked），POST 支持 enable/disable（F-111, F-112） |

### 1.5 工具与配置

| 文件路径 | 关键类/函数 | 说明 |
|----------|------------|------|
| `jupyterlab/utils.py` | `deprecated` 装饰器、`jupyterlab_deprecation` | 弃用警告工具（F-030） |
| `jupyterlab/debuglog.py` | `DebugLogFileMixin` | 上下文管理器形式的调试日志文件输出（F-031） |
| `jupyterlab/browser_check.py` | 浏览器检查工具 | 浏览器自动化检查（F-032） |
| `jupyterlab/pytest_plugin.py` | pytest 插件 | pytest 集成（F-033） |
| `jupyterlab/staging/` | Rspack 配置、HTML 模板 | 生产构建 staging 目录，含 `package.json`（@jupyterlab/application-top）、Rspack 配置、Jinja2 模板（F-035, F-036） |
| `jupyter-config/jupyter_server_config.d/jupyterlab.json` | ServerApp 配置 | 自动启用 jupyterlab server extension（F-040） |
| `jupyter-config/jupyter_notebook_config.d/jupyterlab.json` | NotebookApp 配置 | 旧版 Notebook App 自动启用配置（F-041） |

## 二、前端 Packages 分类速查

前端包位于 `packages/` 目录，共 **103 个**子目录，使用 Lerna + Yarn Workspaces 管理（F-016, F-017）。按职责分为五类。

### 2.1 核心包（18 个）

提供应用框架、基础服务、接口定义和工具函数，标记为 `coreDependency`。

| 包名 | npm 包名 | 说明 |
|------|---------|------|
| `application` | `@jupyterlab/application` | 应用核心：JupyterLab 类、JupyterFrontEnd 抽象基类、LabShell、Router、Token 定义（F-043, F-145） |
| `coreutils` | `@jupyterlab/coreutils` | 核心工具函数：URL/路径/信号/文本/时间/LRU 缓存，浏览器端用 path-browserify 替换 Node path（F-045, F-151） |
| `services` | `@jupyterlab/services` | Jupyter REST API 客户端：Kernel/Session/Content/Terminal/Setting/Workspace 等管理器，浏览器端 shim ws 模块（F-046, F-164） |
| `statedb` | `@jupyterlab/statedb` | 状态数据库：LocalStorage 后端 + DataConnector 抽象模式，作为设置和工作区的客户端状态基础（F-067, F-144） |
| `settingregistry` | `@jupyterlab/settingregistry` | 设置注册表：JSON Schema 验证（ajv）+ 插件设置持久化 + RJSF 表单渲染（F-049, F-165） |
| `workspaces` | `@jupyterlab/workspaces` | 工作区管理：保存/恢复前端布局状态，依赖 services 和 @lumino/signaling（F-050） |
| `docregistry` | `@jupyterlab/docregistry` | 文档注册表：Context/DocumentModel/WidgetFactory/WidgetExtension 扩展点（F-053） |
| `rendermime` | `@jupyterlab/rendermime` | MIME 渲染注册表：latex/livetext/widgets 渲染器管理（F-054） |
| `rendermime-interfaces` | `@jupyterlab/rendermime-interfaces` | IRenderMime 接口定义，v3.15.0-alpha.1（F-054） |
| `codeeditor` | `@jupyterlab/codeeditor` | 编辑器抽象接口：IEditor/IModel/IEditorFactory（F-052） |
| `nbformat` | `@jupyterlab/nbformat` | Jupyter Notebook 格式（.ipynb）TypeScript 类型定义（F-066） |
| `observables` | `@jupyterlab/observables` | 可观察数据结构：ModelDB 等，v5.7.0-alpha.1（F-065） |
| `translation` | `@jupyterlab/translation` | 国际化/gettext 翻译功能（F-069） |
| `ui-components` | `@jupyterlab/ui-components` | 共享 React UI 组件库：LabIcon/TabBarSvg/ContextMenuSvg/SidePanel 等（F-068） |
| `apputils` | `@jupyterlab/apputils` | 应用工具组件：对话框/工具栏/命令栏/打印/剪贴板/许可证/CommandLinker（F-051） |
| `mainmenu` | `@jupyterlab/mainmenu` | 主菜单栏：File/Edit/View/Run/Kernel/Tabs/Settings/Help 菜单定义（F-056） |
| `metapackage` | `@jupyterlab/metapackage` | 元包，聚合全部 88 个核心 @jupyterlab/* 包，版本统一跟随 4.7.0-alpha.1（F-071, F-152） |
| `core-meta` | — | 核心元数据包（F-075） |

### 2.2 功能包（32 个）

提供具体的 Widget/Model 实现，被对应的 `-extension` 包注册到应用中。

| 包名 | npm 包名 | 说明 |
|------|---------|------|
| `notebook` | `@jupyterlab/notebook` | Notebook 面板/Widget：NotebookPanel/Notebook/NotebookModel/NotebookActions/CellList/windowing/toc（F-047, F-153） |
| `cells` | `@jupyterlab/cells` | 单元格组件：CodeCell/MarkdownCell/RawCell，含 inputarea/collapser/headerfooter/placeholder（F-048） |
| `outputarea` | `@jupyterlab/outputarea` | 输出区域组件：OutputAreaModel/OutputAreaWidget，渲染执行结果（F-064） |
| `codemirror` | `@jupyterlab/codemirror` | CodeMirror 6 实现：editor/commands/language/theme/token/mimetype（F-052） |
| `completer` | `@jupyterlab/completer` | 代码补全组件：widget/model/handler/inline/ghost/icons（F-057） |
| `console` | `@jupyterlab/console` | 控制台面板：panel/widget/foreign/history（F-058） |
| `debugger` | `@jupyterlab/debugger` | 调试器 UI 和协议：service/session/sources/sidebar/handler/config/factory（F-059） |
| `lsp` | `@jupyterlab/lsp` | Language Server Protocol 客户端：connection/manager/feature/adapters/plugin/positioning（F-060） |
| `filebrowser` | `@jupyterlab/filebrowser` | 文件浏览器：browser/crumbs/listing/model/upload（F-055） |
| `fileeditor` | `@jupyterlab/fileeditor` | 文本编辑器 Widget（F-072） |
| `docmanager` | `@jupyterlab/docmanager` | 文档管理器：打开/保存/关闭/最近文件、对话框（F-053） |
| `launcher` | `@jupyterlab/launcher` | 启动器面板：widget/tokens（F-063） |
| `terminal` | `@jupyterlab/terminal` | 终端组件（xterm.js 封装）（F-062） |
| `statusbar` | `@jupyterlab/statusbar` | 状态栏组件框架（F-061） |
| `toc` | `@jupyterlab/toc` | 目录生成器：factory/model/panel/registry/tracker/tocitem/tocctree，v6.7.0-alpha.1（F-070） |
| `csvviewer` | `@jupyterlab/csvviewer` | CSV 查看器：model/parse/widget/toolbar（F-072） |
| `htmlviewer` | `@jupyterlab/htmlviewer` | HTML IFrame 查看器（F-072） |
| `imageviewer` | `@jupyterlab/imageviewer` | 图片查看器（F-072） |
| `markdownviewer` | `@jupyterlab/markdownviewer` | Markdown 预览（F-072） |
| `mermaid` | `@jupyterlab/mermaid` | Mermaid 图表渲染：manager/markdown/mime（F-072） |
| `attachments` | `@jupyterlab/attachments` | 附件模型（F-072） |
| `cell-toolbar` | `@jupyterlab/cell-toolbar` | 单元格工具栏（F-072） |
| `documentsearch` | `@jupyterlab/documentsearch` | 文档搜索（F-072） |
| `extensionmanager` | `@jupyterlab/extensionmanager` | 扩展管理器 UI（F-072） |
| `inspector` | `@jupyterlab/inspector` | 对象检查器：handler/inspector（F-072） |
| `logconsole` | `@jupyterlab/logconsole` | 日志控制台：logger/registry/widget（F-072） |
| `metadataform` | `@jupyterlab/metadataform` | 元数据表单（React）（F-072） |
| `pluginmanager` | `@jupyterlab/pluginmanager` | 插件管理器 UI：model（F-072） |
| `property-inspector` | `@jupyterlab/property-inspector` | 属性检查器（F-072） |
| `running` | `@jupyterlab/running` | 运行中面板（F-072） |
| `settingeditor` | `@jupyterlab/settingeditor` | 设置编辑器（F-072） |
| `tooltip` | `@jupyterlab/tooltip` | 工具提示（F-072） |

### 2.3 MIME 扩展包（6 个）

注册为 `mimeExtensions`，提供特定 MIME 类型的渲染能力，无需应用启动即可工作。

| 包名 | npm 包名 | 说明 |
|------|---------|------|
| `javascript-extension` | `@jupyterlab/javascript-extension` | JavaScript MIME 渲染扩展（F-073） |
| `json-extension` | `@jupyterlab/json-extension` | JSON MIME 渲染扩展（F-073） |
| `pdf-extension` | `@jupyterlab/pdf-extension` | PDF MIME 渲染扩展（F-073） |
| `vega5-extension` | `@jupyterlab/vega5-extension` | Vega/Vega-Lite 图表渲染扩展（F-073） |
| `audio-extension` | `@jupyterlab/audio-extension` | 音频 MIME 渲染扩展（F-073） |
| `video-extension` | `@jupyterlab/video-extension` | 视频 MIME 渲染扩展（F-073） |

### 2.4 功能扩展包（44 个）

注册为 `extensions`，每个包导出一个或多个 `JupyterFrontEndPlugin`，在应用启动时被激活并注册命令、Widget、菜单等。

| 包名 | npm 包名 | 说明 |
|------|---------|------|
| `application-extension` | `@jupyterlab/application-extension` | 核心应用扩展：注册默认命令、布局、路由（F-044） |
| `apputils-extension` | `@jupyterlab/apputils-extension` | 注册核心命令和主题加载（F-051） |
| `codemirror-extension` | `@jupyterlab/codemirror-extension` | 注册 CodeMirror 为默认编辑器（F-052） |
| `completer-extension` | `@jupyterlab/completer-extension` | 绑定补全到编辑器和控制台（F-057） |
| `console-extension` | `@jupyterlab/console-extension` | 注册控制台功能（F-058） |
| `debugger-extension` | `@jupyterlab/debugger-extension` | 注册调试器功能（F-059） |
| `lsp-extension` | `@jupyterlab/lsp-extension` | 注册 LSP 功能（F-060） |
| `docmanager-extension` | `@jupyterlab/docmanager-extension` | 注册文档管理命令（F-053） |
| `filebrowser-extension` | `@jupyterlab/filebrowser-extension` | 注册文件浏览器到左侧面板（F-055） |
| `mainmenu-extension` | `@jupyterlab/mainmenu-extension` | 注册菜单栏（F-056） |
| `terminal-extension` | `@jupyterlab/terminal-extension` | 注册终端功能（F-062） |
| `launcher-extension` | `@jupyterlab/launcher-extension` | 注册 Launcher（F-063） |
| `statusbar-extension` | `@jupyterlab/statusbar-extension` | 注册默认状态栏项（F-061） |
| `toc-extension` | `@jupyterlab/toc-extension` | 注册 TOC 面板（F-070） |
| `translation-extension` | `@jupyterlab/translation-extension` | 注册翻译（F-069） |
| `ui-components-extension` | `@jupyterlab/ui-components-extension` | 注册 UI 组件（F-068） |
| `rendermime-extension` | `@jupyterlab/rendermime-extension` | 注册默认渲染器（F-054） |
| `notebook-extension` | `@jupyterlab/notebook-extension` | 注册 Notebook 功能（F-074） |
| `cell-toolbar-extension` | `@jupyterlab/cell-toolbar-extension` | 注册单元格工具栏（F-074） |
| `celltags-extension` | `@jupyterlab/celltags-extension` | 注册单元格标签功能（F-074） |
| `csvviewer-extension` | `@jupyterlab/csvviewer-extension` | 注册 CSV 查看器（F-074） |
| `documentsearch-extension` | `@jupyterlab/documentsearch-extension` | 注册文档搜索（F-074） |
| `extensionmanager-extension` | `@jupyterlab/extensionmanager-extension` | 注册扩展管理器 UI（F-074） |
| `fileeditor-extension` | `@jupyterlab/fileeditor-extension` | 注册文本编辑器（F-074） |
| `help-extension` | `@jupyterlab/help-extension` | 注册帮助菜单（F-074） |
| `htmlviewer-extension` | `@jupyterlab/htmlviewer-extension` | 注册 HTML 查看器（F-074） |
| `hub-extension` | `@jupyterlab/hub-extension` | JupyterHub 集成（F-074） |
| `imageviewer-extension` | `@jupyterlab/imageviewer-extension` | 注册图片查看器（F-074） |
| `inspector-extension` | `@jupyterlab/inspector-extension` | 注册对象检查器（F-074） |
| `logconsole-extension` | `@jupyterlab/logconsole-extension` | 注册日志控制台（F-074） |
| `markdownviewer-extension` | `@jupyterlab/markdownviewer-extension` | 注册 Markdown 预览（F-074） |
| `markedparser-extension` | `@jupyterlab/markedparser-extension` | Marked Markdown 解析器（F-074） |
| `mathjax-extension` | `@jupyterlab/mathjax-extension` | 数学公式渲染（F-074） |
| `mermaid-extension` | `@jupyterlab/mermaid-extension` | 注册 Mermaid 图表（F-074） |
| `metadataform-extension` | `@jupyterlab/metadataform-extension` | 注册元数据表单（F-074） |
| `pluginmanager-extension` | `@jupyterlab/pluginmanager-extension` | 注册插件管理器 UI（F-074） |
| `running-extension` | `@jupyterlab/running-extension` | 注册运行中面板（F-074） |
| `services-extension` | `@jupyterlab/services-extension` | 注册服务层扩展（F-074） |
| `settingeditor-extension` | `@jupyterlab/settingeditor-extension` | 注册设置编辑器（F-074） |
| `shortcuts-extension` | `@jupyterlab/shortcuts-extension` | 键盘快捷键，v5.5.0-alpha.1（F-074） |
| `theme-light-extension` | `@jupyterlab/theme-light-extension` | 亮色主题（F-074） |
| `theme-dark-extension` | `@jupyterlab/theme-dark-extension` | 暗色主题（F-074） |
| `theme-dark-high-contrast-extension` | `@jupyterlab/theme-dark-high-contrast-extension` | 高对比度暗色主题（F-074） |
| `tooltip-extension` | `@jupyterlab/tooltip-extension` | 注册工具提示（F-074） |
| `workspaces-extension` | `@jupyterlab/workspaces-extension` | 注册工作区功能（F-074） |

### 2.5 构建/测试/元数据包（3 个）

| 包名 | 说明 |
|------|------|
| `nbconvert-css` | nbconvert 导出 CSS 样式（F-075） |
| `testing` | 测试工具集（F-075） |
| `core-meta` | 核心元数据（已列入核心包，此处为构建视角重复记录）（F-075） |

> **包数量统计**：核心包 18 + 功能包 32 + MIME 扩展包 6 + 功能扩展包 44 + 构建测试包 3 = **103 个**（F-043-F-075）。

## 三、关键源码文件深度索引

### 3.1 `packages/application/src/` — 应用核心

| 文件 | 关键导出 | 行号 | 说明 |
|------|---------|------|------|
| `lab.ts` | `class JupyterLab extends JupyterFrontEnd<ILabShell>` | L21 | JupyterLab 主应用类，单例。构造函数创建 LabShell 和 ServiceManager，初始化 restored Promise，注册 MIME 渲染插件，添加 Base64ModelFactory（F-043, F-154） |
| | `constructor(options)` | L25 | 构造函数：调用 super()，创建 `_info`（JupyterLab.Info），设置 restored 链（shell.restored → activateDeferredPlugins → _allPluginsActivated.resolve），初始化 paths，devMode 时添加 CSS 类 |
| | `allPluginsActivated: Promise<void>` | L163 | Promise，在所有插件（含 deferred）激活完成后 resolve |
| | `registerPluginModule(mod)` | L173 | 从插件模块注册插件（已弃用） |
| | `_allPluginsActivated` | L303 | PromiseDelegate 实例 |
| `frontend.ts` | `abstract class JupyterFrontEnd<T, U> extends Application<T>` | L42 | 前端应用抽象基类，继承 Lumino Application。定义四大核心属性：commands（继承）、shell（继承）、docRegistry、serviceManager |
| | `constructor(options)` | L49 | 构造函数：创建 ContextMenuSvg、CommandLinker、DocumentRegistry、ServiceManager，设置 restored Promise |
| | `abstract readonly name/namespace/version` | L82-92 | 子类必须实现的抽象属性 |
| | `readonly commandLinker` | L97 | CommandLinker 实例，用于命令链接 |
| | `readonly contextMenu` | L102 | ContextMenuSvg 实例 |
| | `readonly docRegistry` | L107 | DocumentRegistry 实例 |
| | `readonly restored: Promise<void>` | L112 | 状态首次恢复完成的 Promise |
| | `readonly serviceManager` | L117 | ServiceManager.IManager 实例 |
| | `format: U` | L122 | 应用形态因子（desktop/mobile） |
| | `type JupyterFrontEndPlugin<T, U, V>` | L25 | 插件类型别名，等价于 `IPlugin<JupyterFrontEnd<U, V>, T>` |
| `shell.ts` | `const ILabShell = new Token<ILabShell>()` | L75 | LabShell 的依赖注入 Token，标识 `@jupyterlab/application:ILabShell` |
| | `interface ILabShell extends LabShell` | L83 | ILabShell 接口，直接继承 LabShell 类 |
| | `type Area` | L92-100 | Shell 区域类型联合：`'main' \| 'header' \| 'top' \| 'menu' \| 'left' \| 'right' \| 'bottom' \| 'down'`（8 个区域） |
| | `class LabShell extends Widget implements JupyterFrontEnd.IShell` | L368 | LabShell 实现类，继承 Lumino Widget。构造函数创建完整布局树：headerPanel → menuHandler/topHandler → hboxPanel(leftSideBar + vsplitPanel + rightSideBar) → bottomPanel；vsplitPanel 含 hsplitPanel(leftArea + dockPanel + rightArea) 和 downPanel |
| | `add(widget, area, options)` | L1014 | 将 Widget 添加到指定区域，支持 rank 排序和用户布局位置恢复；根据 area 分发到 _addToMainArea/_addToLeftArea 等私有方法 |
| | `collapseLeft()/collapseRight()/collapseDown()` | L1132-1153 | 折叠左/右/下侧区域 |
| | `expandLeft()/expandRight()/expandDown()` | L1173-1199 | 展开左/右/下侧区域，展开最后使用的标签页 |
| | `currentChanged: ISignal` | L609 | 当前 Widget 变化信号，由内部 FocusTracker 驱动 |
| | `activeChanged: ISignal` | L578 | 活跃 Widget 变化信号 |
| | `currentWidget: Widget \| null` | L633 | 当前 Widget（FocusTracker.currentWidget） |
| | `activeWidget: Widget \| null` | L585 | 活跃 Widget（FocusTracker.activeWidget） |
| | `_tracker: FocusTracker<Widget>` | — | 内部 FocusTracker，追踪 main area 和 down area 的 Widget 焦点 |
| `tokens.ts` | `IConnectionLost` | L16 | 连接丢失处理器 Token |
| | `ILabStatus` | L40 | 应用状态 Token（busy/dirty） |
| | `IRouter` | L89 | URL 路由器 Token |
| | `interface IRouter` | L97 | 路由器接口：base/commands/current/routed/stop/navigate/register/reload/route |
| `router.ts` | `class Router implements IRouter` | L18 | 路由器实现，解析 window.location，支持路由规则注册（pattern + command）和导航 |
| | `get current()` | L40 | 解析当前 URL，返回 {hash, path, request, search} |
| | `register(options)` | — | 注册路由规则，返回 IDisposable |
| `status.ts` | `class LabStatus` | — | 应用 busy/dirty 状态管理，实现 ILabStatus 接口 |
| `index.ts` | 桶导出 | — | 重新导出 application 包的所有公共 API |

### 3.2 `packages/services/src/` — 服务层

| 文件 | 关键导出 | 行号 | 说明 |
|------|---------|------|------|
| `manager.ts` | `class ServiceManager implements ServiceManager.IManager` | L48 | 服务管理器，聚合 12 个子管理器。构造函数创建所有子管理器实例，代理连接失败信号，ready Promise 在 sessions/kernelspecs/terminals 就绪后 resolve |
| | `contents: ContentsManager` | L60 | 内容/文件管理器 |
| | `events: EventManager` | L61 | 事件管理器 |
| | `kernels: KernelManager` | L62 | 内核管理器 |
| | `sessions: SessionManager` | L63 | 会话管理器（依赖 kernels） |
| | `settings: SettingManager` | L69 | 设置管理器 |
| | `terminals: TerminalManager` | L70 | 终端管理器 |
| | `builder: BuildManager` | L71 | 构建管理器 |
| | `workspaces: WorkspaceManager` | L72 | 工作区管理器 |
| | `nbconvert: NbConvertManager` | L73 | nbconvert 管理器 |
| | `kernelspecs: KernelSpecManager` | L74 | 内核规格管理器 |
| | `user: UserManager` | L75 | 用户管理器 |
| | `serverSettings: ServerConnection.ISettings` | L59 | 服务器连接设置 |
| | `ready: Promise<void>` | L87 | 服务就绪 Promise |
| | `connectionFailure: ISignal` | L95 | 连接失败信号 |

### 3.3 `packages/notebook/src/` — Notebook 核心

| 文件 | 关键导出 | 说明 |
|------|---------|------|
| `widget.ts` | `Notebook` | Notebook Widget，继承 StaticNotebook，管理 CellList 和窗口化渲染（F-153） |
| `model.ts` | `NotebookModel` | Notebook 数据模型，管理 cells 列表和元数据（F-153） |
| `panel.ts` | `NotebookPanel` | Notebook 面板，组合 Notebook Widget 和工具栏/内容栏（F-153） |
| `actions.tsx` | `NotebookActions` | Notebook 操作：运行/插入/删除/移动/分割单元格（F-153） |
| `celllist.ts` | `CellList` | 单元格列表，支持虚拟化（F-153） |
| `windowing.ts` | 窗口化渲染 | 视口内单元格渲染优化（F-153） |
| `history.ts` | 编辑历史 | 单元格编辑历史管理（F-153） |
| `toc.ts` | Notebook 目录项 | TOC 工厂实现（F-153） |
| `tracker.ts` | NotebookTracker | Notebook Widget 追踪器 |
| `tokens.ts` | Notebook 相关 Token | INotebookTracker 等依赖注入令牌 |
| `default.json` | 默认工具栏配置 | 默认工具栏按钮定义（F-153） |

### 3.4 `packages/cells/src/` — 单元格组件

| 文件 | 关键导出 | 说明 |
|------|---------|------|
| `widget.ts` | `CodeCell`、`MarkdownCell`、`RawCell` | 三种单元格 Widget（F-048） |
| `model.ts` | `CodeCellModel`、`MarkdownCellModel`、`RawCellModel` | 单元格数据模型（F-048） |
| `inputarea.ts` | `InputArea`、`InputPrompt` | 单元格输入区域组件（F-048） |
| `collapser.tsx` | `InputCollapser`、`OutputCollapser` | 单元格折叠器（F-048） |
| `headerfooter.ts` | `CellHeader`、`CellFooter` | 单元格头尾组件（F-048） |
| `placeholder.ts` | `Placeholder` | 单元格占位符（F-048） |

### 3.5 其他关键文件

| 文件路径 | 关键导出 | 说明 |
|----------|---------|------|
| `packages/coreutils/src/pageconfig.ts` | `PageConfig` | 页面配置工具类，从 HTML 中嵌入的 `jupyter-config-data` script 标签读取配置值（F-167） |
| `packages/coreutils/src/url.ts` | `URLExt` | URL 工具函数：parse/join/encode 等（F-045） |
| `packages/coreutils/src/path.ts` | `PathExt` | 路径工具函数，浏览器端使用 path-browserify（F-151） |
| `packages/coreutils/src/signal.ts` | 信号工具 | 信号相关工具函数 |
| `packages/docregistry/src/context.ts` | `Context<T>` | 文档上下文，管理文档的保存/加载/恢复 |
| `packages/docregistry/src/default.ts` | `TextModelFactory`、`Base64ModelFactory` | 默认文档模型工厂 |
| `packages/rendermime/src/registry.ts` | `RenderMimeRegistry` | MIME 渲染器注册表 |
| `packages/apputils/src/dialog.tsx` | `Dialog`、`showDialog` | 对话框组件和工具函数 |
| `packages/apputils/src/clipboard.ts` | `Clipboard` | 系统剪贴板封装 |
| `jupyterlab/staging/package.json` | `jupyterlab` 字段 | 构建配置：46 个核心 extensions、5 个 mimeExtensions、约 70 个 singletonPackages（F-138, F-139） |

## 四、仓库根目录关键文件

| 文件/目录 | 说明 |
|-----------|------|
| `package.json` | 根 npm 包 `@jupyterlab/repo-top`，private，Yarn 3.5.0，resolutions 固定 React/Yjs/Rspack 等版本（F-015, F-016, F-166） |
| `lerna.json` | Lerna 配置：independent 版本模式，npmClient=yarn（F-017） |
| `pyproject.toml` | Python 包配置：hatchling 构建、核心依赖、CLI 入口点、entry points、Hatch 构建钩子（F-001-F-014, F-158-F-163） |
| `jupyterlab/staging/` | 生产构建目录，含 Rspack 配置和 HTML 模板（F-035） |
| `jupyterlab/galata/` | Galata UI 测试框架 Python 端（F-037） |
| `jupyterlab/tests/` | Python 后端测试目录（F-038） |
| `examples/` | 扩展示例代码 |
| `dev_mode/` | 开发模式构建输出目录（F-124） |

## 相关概念

- [00 概述与知识地图](../concepts/00-introduction.md)
- [01 整体架构概览](../concepts/01-architecture-overview.md)
- [02 应用框架与 Shell 布局](../concepts/02-application-shell.md)
- [03 插件系统与依赖注入](../concepts/03-plugin-system.md)
- [04 服务层与后端通信](../concepts/04-service-layer.md)
- [08 构建系统与运行模式](../concepts/08-build-and-modes.md)
