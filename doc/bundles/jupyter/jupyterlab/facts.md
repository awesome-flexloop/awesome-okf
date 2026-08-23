---
type: Facts
okf_version: '0.2'
title: jupyterlab 源码事实清单
tags:
- jupyter
- jupyterlab
- frontend
- notebook
- ide
- extension
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/jupyterlab/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/_version.py
- ../../../../../external/libs/jupyter/jupyterlab/package.json
- ../../../../../external/libs/jupyter/jupyterlab/lerna.json
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/staging/package.json
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/__init__.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/__main__.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/labapp.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/serverextension.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/commands.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/coreconfig.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/labextensions.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/labhubapp.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/federated_labextensions.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/utils.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/debuglog.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/browser_check.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/pytest_plugin.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/upgrade_extension.py
- ../../../../../external/libs/jupyter/jupyterlab/buildapi.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/handlers/announcements.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/handlers/build_handler.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/handlers/error_handler.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/handlers/extension_manager_handler.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/handlers/plugin_manager_handler.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/extensions/__init__.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/extensions/manager.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/extensions/readonly.py
- ../../../../../external/libs/jupyter/jupyterlab/jupyterlab/extensions/pypi.py
- ../../../../../external/libs/jupyter/jupyterlab/packages/statedb/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/application/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/coreutils/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/metapackage/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/services/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/settingregistry/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/notebook/package.json
- ../../../../../external/libs/jupyter/jupyterlab/packages/workspaces/package.json
- ../../../../../external/libs/jupyter/jupyterlab/jupyter-config/jupyter_server_config.d/jupyterlab.json
- ../../../../../external/libs/jupyter/jupyterlab/jupyter-config/jupyter_notebook_config.d/jupyterlab.json
---

# JupyterLab 源码事实清单

## 一、项目元数据

- F-001: pyproject.toml:9 — Python 包名为 `jupyterlab`。
- F-002: pyproject.toml:10 — 项目描述为 "JupyterLab computational environment"。
- F-003: pyproject.toml:13 — 要求 Python >= 3.10。
- F-004: pyproject.toml:14-16 — 作者为 Jupyter Development Team，邮箱 jupyter@googlegroups.com。
- F-005: pyproject.toml:17-20 — 关键词为 "ipython"、"jupyter"。
- F-006: pyproject.toml:22 — 开发状态为 Production/Stable（5 - Production/Stable）。
- F-007: pyproject.toml:23-25 — Framework 分类器标记为 Framework :: Jupyter :: JupyterLab :: 4。
- F-008: pyproject.toml:31-35 — 支持 Python 版本 3.10、3.11、3.12、3.13、3.14。
- F-009: pyproject.toml:5 — 构建系统后端为 hatchling>=1.21.1，依赖 jupyter-builder>=1.1.1。
- F-010: pyproject.toml:54-56 — 版本号为动态字段，从 jupyterlab/_version.py 读取。
- F-011: jupyterlab/_version.py:9 — 当前版本为 4.7.0-alpha.1，由 VersionInfo(4, 7, 0, "alpha", 1) 定义。
- F-012: jupyterlab/_version.py:6 — 版本信息使用 namedtuple VersionInfo，包含 major、minor、micro、releaselevel、serial 五个字段。
- F-013: pyproject.toml:58-61 — CLI 入口点：`jupyter-lab` 指向 jupyterlab.labapp:main，`jupyter-labextension` 指向 jupyterlab.labextensions:main，`jupyter-labhub` 指向 jupyterlab.labhubapp:main。
- F-014: pyproject.toml:63-65 — 注册了两个 extension_manager_v1 entry point：readonly 和 pypi。
- F-015: package.json:2-3 — 根 npm 包名为 @jupyterlab/repo-top，版本 0.0.1，标记为 private。
- F-016: package.json:144 — 使用 Yarn 3.5.0 作为包管理器（packageManager 字段）。
- F-017: lerna.json:3-4 — Lerna 配置为 independent 版本模式，npmClient 为 yarn。
- F-018: jupyterlab/staging/package.json:232-233 — 要求 Node.js >= 20.0.0。

## 二、目录结构

### Python 包结构

- F-019: jupyterlab/ — Python 包根目录，包含所有后端代码。
- F-020: jupyterlab/__init__.py — 包入口，导出 __version__、load_jupyter_server_extension 及公告检查类。
- F-021: jupyterlab/_version.py — 版本定义文件，使用 namedtuple 管理版本。
- F-022: jupyterlab/__main__.py — python -m jupyterlab 入口，调用 labapp.main()。
- F-023: jupyterlab/labapp.py — LabApp 主应用类及子命令类（LabBuildApp、LabCleanApp、LabPathApp、LabWorkspaceApp、LabLicensesApp）。
- F-024: jupyterlab/serverextension.py — 旧版 Notebook Server 兼容的扩展加载 shim，创建 LabApp 实例并设置 favicon/logo 重定向。
- F-025: jupyterlab/commands.py — 构建系统核心，包含 AppOptions、_AppHandler、ProgressProcess 及各类构建/扩展管理函数。
- F-026: jupyterlab/coreconfig.py — CoreConfig 类，管理核心包配置（从 staging/package.json 读取），支持 add/remove/clear_packages。
- F-027: jupyterlab/labextensions.py — jupyter-labextension CLI 入口点，提供 install/uninstall/enable/disable/list/update 等子命令。
- F-028: jupyterlab/labhubapp.py — JupyterHub SingleUserLabApp 集成，默认 URL 为 /lab。
- F-029: jupyterlab/federated_labextensions.py — 联合扩展的已弃用包装函数，委托给 jupyter_builder.federated_extensions。
- F-030: jupyterlab/utils.py — deprecated 装饰器和 jupyterlab_deprecation 自定义警告类。
- F-031: jupyterlab/debuglog.py — DebugLogFileMixin，提供上下文管理器形式的调试日志文件输出。
- F-032: jupyterlab/browser_check.py — 浏览器自动化检查工具。
- F-033: jupyterlab/pytest_plugin.py — pytest 插件。
- F-034: jupyterlab/upgrade_extension.py — 扩展升级工具，基于 copier 模板引擎。
- F-035: jupyterlab/staging/ — 生产构建 staging 目录，包含 Rspack 配置和 HTML 模板。
- F-036: jupyterlab/staging/package.json — @jupyterlab/application-top 私有包（构建入口），定义核心 extensions/mimeExtensions/singletonPackages 列表。
- F-037: jupyterlab/galata/ — Galata UI 测试框架的 Python 端。
- F-038: jupyterlab/tests/ — Python 后端测试目录，含 test_app.py、test_extensions.py、test_build_api.py 等。
- F-039: jupyter-config/ — Jupyter 配置自动发现目录。
- F-040: jupyter-config/jupyter_server_config.d/jupyterlab.json — 自动启用 jupyterlab server extension（ServerApp.jpserver_extensions）。
- F-041: jupyter-config/jupyter_notebook_config.d/jupyterlab.json — 旧版 Notebook App 的自动启用配置。
- F-042: buildapi.py — Hatch 构建钩子，调用 npm_builder，删除 .js.map 文件，验证 NPM/Python 版本一致性。

### 前端包清单（packages/ 共103个子目录）

- F-043: packages/application — @jupyterlab/application，应用核心（JupyterLab 类、ILabShell、JupyterFrontEnd、Router），标记 coreDependency。
- F-044: packages/application-extension — @jupyterlab/application-extension，核心应用扩展插件（注册默认命令、布局、路由）。
- F-045: packages/coreutils — @jupyterlab/coreutils v6.7.0-alpha.1，核心工具函数（URL/路径/信号/文本/时间/LRU缓存），依赖 @lumino/coreutils、minimist、path-browserify、url-parse，标记 coreDependency。
- F-046: packages/services — @jupyterlab/services v7.7.0-alpha.1，Jupyter REST API 客户端（Kernel/Session/Content/Terminal），依赖 ws、@jupyter/ydoc，浏览器端 shim ws 模块。
- F-047: packages/notebook — @jupyterlab/notebook v4.7.0-alpha.1，Notebook 面板/Widget，依赖 cells/codemirror/docregistry/outputarea/rendermime/services/@jupyter/ydoc，含 widget/model/panel/actions/windowing/toc。
- F-048: packages/cells — @jupyterlab/cells，单元格组件（CodeCell/MarkdownCell/RawCell），含 widget/model/inputarea/collapser/headerfooter/placeholder。
- F-049: packages/settingregistry — @jupyterlab/settingregistry v4.7.0-alpha.1，设置注册表（JSON Schema 验证/插件设置持久化），依赖 ajv/json5/@rjsf/utils。
- F-050: packages/workspaces — @jupyterlab/workspaces v4.7.0-alpha.1，工作区管理（保存/恢复布局状态），依赖 services/@lumino/signaling。
- F-051: packages/apputils、apputils-extension — @jupyterlab/apputils，应用工具组件（对话框/工具栏/命令栏/打印/剪贴板/许可证），apputils-extension 注册核心命令和主题加载。
- F-052: packages/codeeditor、codemirror、codemirror-extension — codeeditor 为编辑器抽象接口；codemirror 为 CodeMirror 6 实现（editor/commands/language/theme/token/mimetype）；codemirror-extension 注册 CodeMirror 为默认编辑器。
- F-053: packages/docregistry、docmanager、docmanager-extension — docregistry 为文档注册表（Context/DocumentModel/WidgetFactory）；docmanager 为文档管理器（打开/保存/关闭/最近文件）；docmanager-extension 注册文档管理命令。
- F-054: packages/rendermime、rendermime-interfaces、rendermime-extension — rendermime-interfaces v3.15.0-alpha.1 定义 IRenderMime 接口；rendermime 为 MIME 渲染注册表（latex/livetext/widgets）；rendermime-extension 注册默认渲染器。
- F-055: packages/filebrowser、filebrowser-extension — filebrowser 为文件浏览器组件（browser/crumbs/listing/model/upload）；filebrowser-extension 注册文件浏览器到左侧面板。
- F-056: packages/mainmenu、mainmenu-extension — mainmenu 为主菜单栏（File/Edit/View/Run/Kernel/Tabs/Settings/Help 菜单定义）；mainmenu-extension 注册菜单栏。
- F-057: packages/completer、completer-extension — completer 为代码补全组件（widget/model/handler/inline/ghost/icons）；completer-extension 绑定补全到编辑器和控制台。
- F-058: packages/console、console-extension — console 为控制台面板（panel/widget/foreign/history）；console-extension 注册控制台功能。
- F-059: packages/debugger、debugger-extension — debugger 为调试器 UI 和协议（service/session/sources/sidebar/handler/config/factory）；debugger-extension 注册调试器功能。
- F-060: packages/lsp、lsp-extension — lsp 为 Language Server Protocol 客户端（connection/manager/feature/adapters/plugin/positioning）；lsp-extension 注册 LSP 功能。
- F-061: packages/statusbar、statusbar-extension — statusbar 为状态栏组件框架；statusbar-extension 注册默认状态栏项。
- F-062: packages/terminal、terminal-extension — terminal 为终端组件（xterm.js 封装）；terminal-extension 注册终端功能。
- F-063: packages/launcher、launcher-extension — launcher 为启动器面板（widget/tokens）；launcher-extension 注册 Launcher。
- F-064: packages/outputarea — @jupyterlab/outputarea，输出区域组件（model/widget，渲染执行结果）。
- F-065: packages/observables — @jupyterlab/observables v5.7.0-alpha.1，可观察数据结构（modeldb）。
- F-066: packages/nbformat — @jupyterlab/nbformat，Jupyter Notebook 格式（.ipynb）TypeScript 类型定义。
- F-067: packages/statedb — @jupyterlab/statedb，状态数据库（LocalStorage 后端/数据连接器模式）。
- F-068: packages/ui-components、ui-components-extension — ui-components 为共享 React UI 组件库；ui-components-extension 注册组件。
- F-069: packages/translation、translation-extension — translation 为国际化/gettext 翻译功能；translation-extension 注册翻译。
- F-070: packages/toc、toc-extension v6.7.0-alpha.1 — toc 为目录生成器（factory/model/panel/registry/tracker/tocitem/tocctree）；toc-extension 注册 TOC 面板。
- F-071: packages/metapackage — @jupyterlab/metapackage，聚合所有 88 个核心 @jupyterlab/* 包的元包。
- F-072: packages 中功能类包（提供 Widget/Model）：attachments（附件模型）、cell-toolbar（单元格工具栏）、csvviewer（CSV 查看器）、documentsearch（文档搜索）、extensionmanager（扩展管理器 UI）、fileeditor（文本编辑器）、htmlviewer（HTML IFrame 查看器）、imageviewer（图片查看器）、inspector（对象检查器）、logconsole（日志控制台）、markdownviewer（Markdown 预览）、mermaid（Mermaid 图表）、metadataform（元数据表单）、pluginmanager（插件管理器 UI）、property-inspector（属性检查器）、running（运行中面板）、settingeditor（设置编辑器）、tooltip（工具提示）。
- F-073: packages 中 MIME 渲染扩展包（注册为 mimeExtensions）：javascript-extension、json-extension、pdf-extension、vega5-extension（Vega/Vega-Lite）、audio-extension（音频）、video-extension（视频）。
- F-074: packages 中核心功能扩展包（注册为 extensions）：cell-toolbar-extension、celltags-extension（单元格标签）、csvviewer-extension、debugger-extension、documentsearch-extension、extensionmanager-extension、filebrowser-extension、fileeditor-extension、help-extension（帮助菜单）、htmlviewer-extension、hub-extension（JupyterHub 集成）、imageviewer-extension、inspector-extension、launcher-extension、logconsole-extension、lsp-extension、markdownviewer-extension、markedparser-extension（Marked Markdown 解析）、mathjax-extension（数学公式）、mermaid-extension、metadataform-extension、notebook-extension、pluginmanager-extension、rendermime-extension、running-extension、services-extension、settingeditor-extension、shortcuts-extension v5.5.0-alpha.1（键盘快捷键）、statusbar-extension、terminal-extension、tooltip-extension、ui-components-extension、workspaces-extension、theme-light-extension（亮色主题）、theme-dark-extension（暗色主题）、theme-dark-high-contrast-extension（高对比度暗色主题）。
- F-075: packages 中构建/测试/元数据包：core-meta（核心元数据）、nbconvert-css（nbconvert 导出 CSS）、testing（测试工具集）。

## 三、LabApp 主应用

- F-076: jupyterlab/labapp.py:417 — LabApp 继承自 NotebookConfigShimMixin 和 LabServerApp（来自 jupyterlab_server）。
- F-077: jupyterlab/labapp.py:420-421 — LabApp.name = "lab"，LabApp.app_name = "JupyterLab"。
- F-078: jupyterlab/labapp.py:424 — load_other_extensions = True，启动时加载其他 server extensions。
- F-079: jupyterlab/labapp.py:513 — default_url = "/lab"，默认重定向到 /lab。
- F-080: jupyterlab/labapp.py:432-445 — 三种运行模式：Core mode（--core-mode，包内置资源，无扩展）、Dev mode（--dev-mode，dev_mode/ 本地构建）、App mode（--app-dir，用户自定义扩展集）。
- F-081: jupyterlab/labapp.py:532-541 — core_mode 为布尔配置项，True 时禁用第三方扩展，使用 pip 包内预构建 JS 资源。
- F-082: jupyterlab/labapp.py:543-551 — dev_mode 为布尔配置项，使用 dev_mode/ 目录下未发布的本地 JS 包，页面顶部显示红色条带。
- F-083: jupyterlab/labapp.py:563-569 — extension_manager 配置项默认为 "pypi"，可选 "readonly"，通过 entry point 可扩展。
- F-084: jupyterlab/labapp.py:613-617 — lock_all_plugins 配置项，锁定所有插件不可在 UI 中启用/禁用。
- F-085: jupyterlab/labapp.py:619-624 — check_for_updates_class 可配置，默认为 CheckForUpdate，接受 CheckForUpdateABC 子类，支持自定义更新检查。
- F-086: jupyterlab/labapp.py:606-611 — news_url 默认值为 "https://jupyterlab.github.io/assets/feed.xml"，设为 None 关闭公告。
- F-087: jupyterlab/labapp.py:595-604 — collaborative 配置项已弃用，要求独立安装 jupyter_collaboration 扩展。
- F-088: jupyterlab/labapp.py:679-724 — initialize_templates() 根据运行模式设置 static_paths、template_paths、labextensions_path；core_mode 下 labextensions_path 为空。
- F-089: jupyterlab/labapp.py:738-933 — initialize_handlers() 设置 page_config、注册 BuildHandler/ExtensionHandler/PluginHandler/公告 Handler、处理 JupyterHub 元数据。
- F-090: jupyterlab/labapp.py:745-746 — buildAvailable 和 buildCheck 在 core_mode 和 dev_mode 下为 False，前端不显示构建 UI。
- F-091: jupyterlab/labapp.py:747 — page_config 中设置 devMode 标志，前端据此显示开发模式红色条带。
- F-092: jupyterlab/labapp.py:814-858 — 扩展管理器通过 entry point 动态加载，实例化失败时回退到 ReadOnlyExtensionManager。
- F-093: jupyterlab/labapp.py:912-926 — JupyterHub 环境下自动检测 hub_prefix/hubHost/hubUser/shareUrl 元数据，清空 token 避免泄露。
- F-094: jupyterlab/labapp.py:960 — main = launch_new_instance = LabApp.launch_instance，模块级入口点。
- F-095: jupyterlab/labapp.py:503-511 — 子命令注册：build（LabBuildApp）、clean（LabCleanApp）、path/paths（LabPathApp）、workspace/workspaces（LabWorkspaceApp）、licenses（LabLicensesApp）。
- F-096: jupyterlab/labapp.py:145-210 — LabBuildApp 支持 dev_build/minimize/pre_clean/splice_source 选项，构建失败时显示详细排错信息。
- F-097: jupyterlab/labapp.py:245-284 — LabCleanApp 支持按 extensions/settings/static/all 选择性清理。

## 四、后端 Handler

- F-098: jupyterlab/handlers/announcements.py:293-294 — API 路由：NewsHandler 为 /lab/api/news，CheckForUpdateHandler 为 /lab/api/update。
- F-099: jupyterlab/handlers/announcements.py:78-116 — CheckForUpdate 请求 PyPI JSON API（https://pypi.org/pypi/jupyterlab/json）比较版本，返回更新通知。
- F-100: jupyterlab/handlers/announcements.py:119-141 — NeverCheckForUpdate 始终返回 None，供管理员禁用外部网络请求。
- F-101: jupyterlab/handlers/announcements.py:190-290 — NewsHandler 从 Atom feed 获取公告，解析 XML entry，返回 Notification 列表。
- F-102: jupyterlab/handlers/announcements.py:30-48 — Notification frozen dataclass：createdAt/message/modifiedAt/type/link/options，type 取值 default/error/info/success/warning。
- F-103: jupyterlab/handlers/announcements.py:161 — 所有 Handler 方法使用 @web.authenticated 装饰器要求认证。
- F-104: jupyterlab/handlers/build_handler.py:198 — BuildHandler 路由路径为 /lab/api/build。
- F-105: jupyterlab/handlers/build_handler.py:21-149 — Builder 类管理构建状态（building/canceled），使用 ThreadPoolExecutor(max_workers=5) 异步执行，构建失败时自动 clean+rebuild。
- F-106: jupyterlab/handlers/build_handler.py:151-194 — BuildHandler 支持 GET（查询状态）、POST（触发构建）、DELETE（取消构建）。
- F-107: jupyterlab/handlers/error_handler.py:24-39 — ErrorHandler 返回简单 HTML 错误页面，显示错误消息列表。
- F-108: jupyterlab/handlers/extension_manager_handler.py:146 — ExtensionHandler 路由路径为 /lab/api/extensions。
- F-109: jupyterlab/handlers/extension_manager_handler.py:22-96 — ExtensionHandler GET 支持 refresh/query/page/per_page 参数，返回分页扩展列表和 RFC 5988 Link 头（first/prev/next/last）。
- F-110: jupyterlab/handlers/extension_manager_handler.py:98-142 — ExtensionHandler POST 支持 install/uninstall/enable/disable 四种命令。
- F-111: jupyterlab/handlers/plugin_manager_handler.py:64 — PluginHandler 路由路径为 /lab/api/plugins。
- F-112: jupyterlab/handlers/plugin_manager_handler.py:20-60 — PluginHandler GET 返回插件锁定信息（lockRules/allLocked），POST 支持 enable/disable 插件。

## 五、扩展系统（Python 侧）

- F-113: jupyterlab/extensions/__init__.py:15-18 — MANAGERS 字典从 importlib.metadata.entry_points(group="jupyterlab.extension_manager_v1") 动态加载。
- F-114: jupyterlab/extensions/__init__.py:24-39 — 内置两个工厂函数：get_readonly_manager() 返回 ReadOnlyExtensionManager，get_pypi_manager() 返回 PyPIExtensionManager。
- F-115: jupyterlab/extensions/manager.py:55-101 — ExtensionPackage frozen dataclass，字段含 name/description/homepage_url/pkg_type/installed_version/latest_version/status/enabled/core/companion/approved/install 等。
- F-116: jupyterlab/extensions/manager.py:104-118 — ActionResult frozen dataclass：status（ok/warning/error）、message、needs_restart（frontend/kernel/server）。
- F-117: jupyterlab/extensions/manager.py:121-150 — PluginManagerOptions/ExtensionManagerOptions dataclass：lock_rules/lock_all/allowed_extensions_uris/blocked_extensions_uris/listings_refresh_seconds/listings_tornado_options。
- F-118: jupyterlab/extensions/manager.py:181-298 — PluginManager 类管理插件启用/禁用/锁定，支持 sys_prefix/user/system 三个级别，锁定规则支持插件名或扩展名（冒号格式 extension:plugin）。
- F-119: jupyterlab/extensions/manager.py:301-391 — ExtensionManager 抽象基类继承 PluginManager，要求实现 metadata/get_latest_version/list_packages/install/uninstall 五个抽象方法，支持 PeriodicCallback 定时刷新黑白名单。
- F-120: jupyterlab/extensions/readonly.py:13-84 — ReadOnlyExtensionManager 不支持安装/卸载，install/uninstall 返回 error 状态，is_install_allowed 返回 False，metadata 标记 can_install=False。
- F-121: jupyterlab/extensions/pypi.py:4 — PyPIExtensionManager 使用 pip 作为包管理器、PyPI.org 作为包源。
- F-122: jupyterlab/extensions/pypi.py:27,29 — PyPIExtensionManager 依赖 httpx 异步 HTTP 客户端，使用 async_lru.alru_cache 缓存扩展列表。
- F-123: jupyterlab/extensions/pypi.py:67-73 — 支持 ALL_PROXY/http_proxy/HTTP_PROXY/https_proxy/HTTPS_PROXY 环境变量代理配置，兼容 httpx 0.28+ 的 mounts API。

## 六、构建系统

- F-124: jupyterlab/commands.py:51-63 — 路径常量：HERE 为 jupyterlab 包目录，REPO_ROOT 为仓库根目录，DEV_DIR 为 REPO_ROOT/dev_mode。
- F-125: jupyterlab/commands.py:56 — RSPACK_EXPECT 正则匹配构建完成输出，包含 "theme-light-extension/style/theme.css" 和 "Rspack compiled"。
- F-126: jupyterlab/commands.py:74-143 — ProgressProcess 类封装子进程执行，带 spinner 动画（-/\\|/）和 kill_event 中止支持。
- F-127: jupyterlab/commands.py:151-162 — 目录解析函数：get_user_settings_dir()/get_workspaces_dir() 分别读取 JUPYTERLAB_SETTINGS_DIR/JUPYTERLAB_WORKSPACES_DIR 环境变量，默认在 <jupyter_config_dir>/lab/ 下。
- F-128: jupyterlab/commands.py:165-208 — get_app_dir() 按优先级查找：JUPYTERLAB_DIR → sys.prefix/share/jupyter/lab → 用户级 site → /usr/local/share → 相对路径推导。
- F-129: jupyterlab/commands.py:354-422 — AppOptions 类（HasTraits）配置项：app_dir/logger/core_config/kill_event/labextensions_path/registry/splice_source/skip_full_build_check/verbose。
- F-130: jupyterlab/commands.py:686 — _AppHandler 内部类是构建和扩展管理的实际实现者，初始化时深拷贝 core_data 避免污染。
- F-131: jupyterlab/commands.py:211-238 — dedupe_yarn() 使用 yarn-berry-deduplicate 的 fewerHighest 策略减少重复依赖。
- F-132: jupyterlab/commands.py:241-258 — ensure_node_modules() 运行 yarn --immutable --immutable-cache，失败则重新安装。
- F-133: jupyterlab/commands.py:261-282 — ensure_dev()/ensure_core() 分别确保开发模式和核心模式的静态资源存在。
- F-134: jupyterlab/commands.py:542-563 — build() 委托 _AppHandler.build()，支持 production/minimize/clean_staging 参数；production=None 时根据是否有 linked/local 包自动判断。
- F-135: jupyterlab/commands.py:508-537 — clean() 清理 extensions/settings/staging/static 子目录或整个 app_dir，禁止清理 dev/core 目录。
- F-136: jupyterlab/commands.py:573-651 — 扩展管理函数：enable_extension/disable_extension/lock_extension/unlock_extension/check_extension/list_extensions/link_package/unlink_package，均委托给 _AppHandler。
- F-137: jupyterlab/staging/package.json:7-19 — 构建脚本使用 Rspack（非 Webpack），支持 build:dev/build:prod/build:prod:minimize/build:prod:release/watch 等配置。
- F-138: jupyterlab/staging/package.json:235-368 — jupyterlab 字段定义 name="JupyterLab"、version="4.7.0a1"、46个核心 extensions、5个 mimeExtensions、约70个 singletonPackages、buildDir="./build"、outputDir=".."、staticDir="../static"。
- F-139: jupyterlab/staging/package.json:296-365 — singletonPackages 列表确保 React/Lumino/CodeMirror/Yjs 等框架包只有一个实例，防止多实例冲突。
- F-140: pyproject.toml:211-232 — Hatch 构建钩子：build-function="buildapi.builder"，editable 模式从 packages/ 构建到 dev_mode/static，生产构建从 staging/ 构建到 jupyterlab/static。
- F-141: pyproject.toml:152-158 — wheel 共享数据映射：static/→share/jupyter/lab/static、schemas/→share/jupyter/lab/schemas、themes/→share/jupyter/lab/themes、jupyter-config/→etc/jupyter。

## 七、工作区/设置/国际化

- F-142: jupyterlab/labapp.py:308-361 — LabWorkspaceExportApp/ImportApp/ListApp 继承 jupyterlab_server 对应类，重写 workspaces_dir 默认值；LabWorkspaceApp 聚合为子命令。
- F-143: jupyterlab/handlers/announcements.py:15 — 后端翻译使用 jupyterlab_server.translation_utils 的 gettext 翻译器，前端由 @jupyterlab/translation 包提供。
- F-144: packages/statedb/package.json:37-42 — statedb 提供基于 LocalStorage 的状态持久化和数据连接器（DataConnector）模式，被 settingregistry 和 services 直接依赖，经 services 被 workspaces 间接使用，作为设置和工作区的客户端状态存储基础。

## 八、前端包架构

- F-145: packages/application/package.json:44-63 — @jupyterlab/application 依赖全套 @lumino/*（algorithm/application/commands/coreutils/disposable/messaging/polling/properties/signaling/widgets），以及 @jupyterlab/apputils/coreutils/docregistry/rendermime/services/statedb/translation/ui-components。
- F-146: packages/application/package.json:76-82 — @jupyterlab/application 标记 coreDependency:true，extraStyles 引入 @fortawesome/fontawesome-free 的 CSS。
- F-147: jupyterlab/staging/package.json:149-151 — 前端框架：React 18（react ^18.2.0/react-dom ^18.2.0）、Yjs ^13.5.40（CRDT 协作）。
- F-148: jupyterlab/staging/package.json:132-146 — Lumino 依赖共15个包：algorithm/application/commands/coreutils/datagrid/disposable/domutils/dragdrop/keyboard/messaging/polling/properties/signaling/virtualdom/widgets。
- F-149: jupyterlab/staging/package.json:147-148,130-131 — UI 层使用 @microsoft/fast-element/fast-foundation Web Components；编辑器解析器使用 @lezer/common/highlight（CodeMirror 6 生态）。
- F-150: jupyterlab/staging/package.json:213,22-24 — 构建工具为 @rspack/cli+@rspack/core ^2.0.2（Rust 编写的高性能打包器），CodeMirror 6 相关包（@codemirror/language/state/view）锁定为 ^6.0.0。
- F-151: packages/coreutils/package.json:17-18 — coreutils 浏览器端将 Node.js path 模块替换为 path-browserify。
- F-152: packages/metapackage/package.json:40-142 — @jupyterlab/metapackage 聚合全部 88 个核心 @jupyterlab/* 包，版本号统一跟随 4.7.0-alpha.1 系列。
- F-153: packages/notebook/src/ — Notebook 包源码结构：widget.ts（Notebook Widget）、model.ts（NotebookModel）、panel.ts（NotebookPanel）、actions.tsx（NotebookActions）、celllist.ts（CellList 虚拟化列表）、history.ts（编辑历史）、windowing.ts（窗口化渲染）、toc.ts（Notebook 目录项）、default.json（默认工具栏配置）。
- F-154: packages/application/src/ — Application 包源码结构：lab.ts（JupyterLab 主类）、shell.ts（LabShell 布局/DockPanel）、router.ts（前端路由）、tokens.ts（IToken 依赖注入令牌）、status.ts。

## 九、入口点与集成

- F-155: jupyterlab/__init__.py:15-16 — _jupyter_server_extension_paths() 返回 [{"module": "jupyterlab"}]（经典 Notebook Server 路径）。
- F-156: jupyterlab/__init__.py:19-21 — _jupyter_server_extension_points() 返回 [{"module": "jupyterlab", "app": LabApp}]（jupyter_server 2.x ExtensionApp 路径）。
- F-157: jupyterlab/labhubapp.py:15-17,48-59 — SingleUserLabApp 设置 JUPYTERHUB_SINGLEUSER_APP 环境变量避免导入旧 notebook 包，继承 make_singleuser_app(ServerApp)，默认 URL /lab，find_server_extensions() 中无条件启用 jupyterlab。
- F-158: pyproject.toml:46 — 核心依赖 jupyterlab_server>=2.28.0,<3（提供 LabServerApp/WorkspaceApp/LicensesApp/page_config/get_page_config 等基类和工具）。
- F-159: pyproject.toml:44 — 核心依赖 jupyter_server>=2.19.0,<3（Tornado-based Jupyter Server 2.x）。
- F-160: pyproject.toml:47 — 依赖 notebook_shim>=0.2（经典 Notebook 配置兼容层，NotebookConfigShimMixin）。
- F-161: pyproject.toml:45 — 依赖 jupyter-lsp>=2.0.0（Language Server Protocol 服务端集成）。
- F-162: pyproject.toml:37-53 — 其他 Python 依赖：jupyter-builder>=1.1.1、async_lru>=1.0.0、httpx>=0.25.0、ipykernel>=6.5.0、jinja2>=3.0.3、jupyter_core、packaging>=23.2、tornado>=6.2.0、traitlets。
- F-163: pyproject.toml:39,50-51 — 关键技术栈选择：httpx（异步 HTTP 客户端）、tornado>=6.2.0（Web 框架）、traitlets（配置系统）。
- F-164: packages/services/package.json:58 — 前端 WebSocket 使用 ws ^8.11.0（Node 端），浏览器端通过 shim 使用原生 WebSocket。
- F-165: packages/settingregistry/package.json:48 — JSON Schema 验证使用 ajv ^8.12.0，表单渲染使用 @rjsf/utils ^5.13.4。
- F-166: package.json:107-117 — 根 resolutions 固定关键包版本：@rspack/* 2.0.2、react ^18.2.0、yjs ^13.5.40、lodash ^4.17.23、marked ^17.0.6、prettier ^3.8.1。
- F-167: jupyterlab/labapp.py:742-757 — page_config_data 在 initialize_handlers 中设置，传递 devMode/token/exposeAppInBrowser/quitButton/allow_hidden_files/delete_to_trash/notebookVersion/buildAvailable/buildCheck/extensionManager/news/hub* 等配置给前端。
