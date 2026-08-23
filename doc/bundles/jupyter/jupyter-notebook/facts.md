---
type: Facts
okf_version: '0.2'
title: jupyter-notebook 源码事实清单
tags:
- jupyter
- notebook
- classic
- jupyterlab
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/notebook/pyproject.toml
- ../../../../../external/libs/jupyter/notebook/notebook/_version.py
- ../../../../../external/libs/jupyter/notebook/README.md
- ../../../../../external/libs/jupyter/notebook/notebook/app.py
- ../../../../../external/libs/jupyter/notebook/jupyter_config.json
- ../../../../../external/libs/jupyter/notebook/docs/source/migrate_to_notebook7.md
- ../../../../../external/libs/jupyter/notebook/setup.py
- ../../../../../external/libs/jupyter/notebook/packages/application/src/app.ts
- ../../../../../external/libs/jupyter/notebook/packages/application/src/shell.ts
- ../../../../../external/libs/jupyter/notebook/packages/application/src/panelhandler.ts
- ../../../../../external/libs/jupyter/notebook/packages/application/src/pathopener.ts
- ../../../../../external/libs/jupyter/notebook/app/package.json
- ../../../../../external/libs/jupyter/notebook/packages/lab-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/packages/application-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/packages/docmanager-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/packages/console-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/packages/terminal-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/notebook/__init__.py
- ../../../../../external/libs/jupyter/notebook/notebook/__main__.py
- ../../../../../external/libs/jupyter/notebook/app/templates/tree_template.html
- ../../../../../external/libs/jupyter/notebook/app/templates/notebooks_template.html
- ../../../../../external/libs/jupyter/notebook/packages/notebook-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/jupyter-config/jupyter_server_config.d/notebook.json
- ../../../../../external/libs/jupyter/notebook/app/index.template.js
- ../../../../../external/libs/jupyter/notebook/packages/tree-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/packages/help-extension/src/index.tsx
- ../../../../../external/libs/jupyter/notebook/packages/documentsearch-extension/src/index.ts
- ../../../../../external/libs/jupyter/notebook/tests/test_app.py
---

# Jupyter Notebook v7 源码事实清单

## 一、项目元数据

- F-001: pyproject.toml:10 — Python 包名为 `notebook`，通过 hatchling 构建。
- F-002: pyproject.toml:11 — 项目描述为 "Jupyter Notebook - A web-based notebook environment for interactive computing"。
- F-003: pyproject.toml:14 — 要求 Python >= 3.10。
- F-004: pyproject.toml:30-34 — 支持 Python 3.10、3.11、3.12、3.13、3.14。
- F-005: pyproject.toml:39 — 核心依赖 `jupyter_server>=2.19.0,<3`，使用 Jupyter Server v2 作为后端。
- F-006: pyproject.toml:40 — 核心依赖 `jupyterlab>=4.7.0a1,<4.8`，前端复用 JupyterLab v4.7 组件。
- F-007: pyproject.toml:41 — 核心依赖 `jupyterlab_server>=2.28.0,<3`，服务端基于 jupyterlab_server。
- F-008: pyproject.toml:42 — 依赖 `notebook_shim>=0.2,<0.3`，提供 v6→v7 配置兼容层。
- F-009: pyproject.toml:48 — CLI 入口点 `jupyter-notebook = "notebook.app:main"`。
- F-010: notebook/_version.py:9 — 当前版本号为 `7.7.0a1`（7.7.0 alpha 1）。
- F-011: pyproject.toml:2-6 — 构建系统使用 hatchling + hatch-jupyter-builder + jupyter-builder。
- F-012: pyproject.toml:240-245 — Python 端启用 strict mypy 类型检查，类型标注完整。
- F-013: pyproject.toml:92 — wheel 构建时将 `notebook/labextension` 安装到 `share/jupyter/labextensions/@jupyter-notebook/lab-extension`，即作为 JupyterLab federated extension 分发。
- F-014: README.md:14-16 — 官方维护两个大版本：Classic Notebook v6 和 Notebook v7；v5 不再维护。
- F-015: README.md:23-26 — Notebook v7 前端基于 JupyterLab components，后端基于 Jupyter Server，这是对代码库的重大改变。
- F-016: README.md:18-19 — 为 v5/v6 编写的 extensions 与 Notebook v7 不兼容。

## 二、目录结构

- F-017: notebook/ — Python 包目录仅包含 6 个条目：`__init__.py`、`__main__.py`、`_version.py`、`app.py`、`py.typed`、`custom/custom.css`，极其精简。
- F-018: notebook/ — 没有独立的 `handlers/`、`extensions/`、`shim.py` 子目录或模块；handlers 全部内联在 app.py 中，shim 通过外部依赖 notebook_shim 提供。
- F-019: app/ — 前端应用构建入口目录，包含 rspack 构建配置、HTML 模板和入口 JS。
- F-020: app/templates/ — 6 个 Jinja2 HTML 模板：tree_template.html、notebooks_template.html、edit_template.html、consoles_template.html、terminals_template.html、error_template.html。
- F-021: packages/ — 前端 TypeScript 包目录，共 12 个子包（_metapackage + 11 个功能包）。
- F-022: packages/_metapackage/ — 元包，用于聚合和构建所有子包。
- F-023: packages/application/ — 核心应用包，定义 NotebookApp、NotebookShell、PanelHandler 等。
- F-024: packages/application-extension/ — 应用基础插件（shell、菜单、路由、splash、zen mode 等）。
- F-025: packages/lab-extension/ — JupyterLab 互操作插件（interface switcher、launch tree）。
- F-026: packages/notebook-extension/ — Notebook 专属功能插件（checkpoints、kernel logo/status、full-width、scroll output 等）。
- F-027: packages/tree/ — Tree（文件浏览器）页面核心 widget（NotebookTreeWidget）。
- F-028: packages/tree-extension/ — Tree 页面插件（file actions、new dropdown、running sessions）。
- F-029: packages/console-extension/ — Console 页面插件（路由、新标签页打开、scratchpad console）。
- F-030: packages/terminal-extension/ — Terminal 页面插件（路由、新标签页打开）。
- F-031: packages/docmanager-extension/ — 文档管理插件（文档在新标签页打开的 IDocumentWidgetOpener 实现）。
- F-032: packages/help-extension/ — 帮助菜单插件（About 对话框、外部资源链接）。
- F-033: packages/documentsearch-extension/ — 文档搜索插件（为当前 widget 添加 searchable CSS class）。
- F-034: packages/ui-components/ — 自定义 UI 组件（jupyterIcon 等图标）。
- F-035: jupyter-config/ — Jupyter 配置目录，包含 `jupyter_server_config.d/notebook.json` 自动启用 notebook 扩展。
- F-036: buildutils/ — 构建工具脚本（develop、release-bump、upgrade-lab-dependencies 等），用 TypeScript 编写。
- F-037: ui-tests/ — Playwright 端到端测试，覆盖 general、layout、menus、notebook、settings、tree、mobile、console、editor、filebrowser、links、smoke 等场景。
- F-038: tests/ — Python 后端测试，仅 conftest.py 和 test_app.py 两个文件。

## 三、NotebookApp 主应用（Python 端）

- F-039: notebook/app.py:242 — `JupyterNotebookApp` 继承自 `NotebookConfigShimMixin` 和 `LabServerApp`，MRO 中 shim 在前。
- F-040: notebook/app.py:25 — `LabServerApp` 从 `jupyterlab_server` 导入，NotebookApp 本质上是一个定制化的 LabServerApp。
- F-041: notebook/app.py:32 — `NotebookConfigShimMixin` 从外部包 `notebook_shim.shim` 导入，不在 notebook 仓库内实现。
- F-042: notebook/app.py:245 — 应用名 `name = "notebook"`。
- F-043: notebook/app.py:246 — 应用显示名 `app_name = "Jupyter Notebook"`。
- F-044: notebook/app.py:250 — `extension_url = "/"`，作为 Jupyter Server 扩展挂载在根路径。
- F-045: notebook/app.py:251 — `default_url = Unicode("/tree", config=True)`，默认重定向到 `/tree`（文件浏览器页面），而非 JupyterLab 的 `/lab`。
- F-046: notebook/app.py:252 — `file_url_prefix = "/tree"`。
- F-047: notebook/app.py:253 — `load_other_extensions = True`，加载其他已安装的 server extensions。
- F-048: notebook/app.py:254 — `app_dir` 指向 JupyterLab 的 app 目录（通过 `jupyterlab.commands.get_app_dir()` 获取），复用 Lab 的设置/主题/工作区目录。
- F-049: notebook/app.py:257-261 — `expose_app_in_browser` 配置项控制是否将全局 app 实例暴露到 `window.jupyterapp`。
- F-050: notebook/app.py:263-269 — `custom_css` 配置项（默认 True）控制是否加载自定义 CSS，保留经典 Notebook 的 `custom/custom.css` 功能。
- F-051: notebook/app.py:271-280 — Notebook 新增两个命令行 flag：`--expose-app-in-browser` 和 `--custom-css`。
- F-052: notebook/app.py:282-308 — 静态文件、模板、app_settings、schemas、themes、user_settings、workspaces 目录均通过 `@default` 装饰器设置，static/templates 指向 notebook 包内目录，其余指向 JupyterLab 的用户目录。
- F-053: notebook/app.py:326-356 — `initialize_handlers()` 注册 6 个 Tornado 路由：`/tree(.*)`、`/notebooks(.*)`、`/edit(.*)`、`/consoles/(.*)`、`/terminals/(.*)`、`/custom/custom.css`，然后调用 `super().initialize_handlers()` 继承 LabServerApp 的 handlers。
- F-054: notebook/app.py:330-331 — 检测 `nbclassic` 扩展是否启用，将结果存入 `page_config["nbclassic_enabled"]`，供前端 interface switcher 使用。
- F-055: notebook/app.py:334-348 — 集成 JupyterHub 支持：从 tornado_settings 读取 hub_prefix、hub_host、user 等信息写入 page_config，并清空 token 避免泄露 API token。
- F-056: notebook/app.py:363 — `main = launch_new_instance = JupyterNotebookApp.launch_instance`，提供两个别名作为 CLI 入口。

## 四、Handler 层

- F-057: notebook/app.py:49-54 — `NotebookBaseHandler` 继承 `ExtensionHandlerJinjaMixin`、`ExtensionHandlerMixin`、`JupyterHandler`，提供 `custom_css` 属性和 `get_page_config()` 方法，是所有页面 Handler 的基类。
- F-058: notebook/app.py:56-130 — `NotebookBaseHandler.get_page_config()` 构建前端配置对象，包含 appVersion、baseUrl、token、mathjax 配置、labextensions 路径等，并调用 `jupyterlab_server.config.get_page_config()` 获取 Lab 页面配置。
- F-059: notebook/app.py:133-170 — `TreeHandler` 处理 `/tree(.*)` 路由：目录显示 tree 页面，notebook 文件重定向到 `/notebooks/`，其他文件重定向到 `/files/`（原始文件下载）。
- F-060: notebook/app.py:173-180 — `ConsoleHandler` 处理 `/consoles/(.*)` 路由，渲染 consoles.html 模板。
- F-061: notebook/app.py:183-190 — `TerminalHandler` 处理 `/terminals/(.*)` 路由，渲染 terminals.html 模板。
- F-062: notebook/app.py:193-200 — `FileHandler` 处理 `/edit(.*)` 路由，渲染 edit.html 模板（文件编辑器页面）。
- F-063: notebook/app.py:203-218 — `NotebookHandler` 处理 `/notebooks(.*)` 路由：如果路径是目录则重定向到 `/tree/`，否则渲染 notebooks.html 模板。
- F-064: notebook/app.py:221-239 — `CustomCssHandler` 处理 `/custom/custom.css` 路由：从 Jupyter 配置目录或 static 目录读取 custom.css 返回给浏览器，保留经典 Notebook 的自定义 CSS 功能。

## 五、Shim 兼容层

- F-065: pyproject.toml:42 — shim 层通过外部包 `notebook_shim>=0.2,<0.3` 提供，不在本仓库内实现。
- F-066: notebook/app.py:242 — `NotebookConfigShimMixin` 作为 JupyterNotebookApp 的第一个父类（MRO 优先），将 v6 的配置项映射到 v7/JupyterServer 配置。
- F-067: jupyter-config/jupyter_server_config.d/notebook.json:1-7 — 自动配置文件在 `ServerApp.jpserver_extensions` 中启用 `notebook` 扩展，用户安装后无需手动配置。
- F-068: jupyter_config.json:1-4 — 项目根目录的 jupyter_config.json 设置 `LabApp.expose_app_in_browser = true` 和 `JupyterNotebookApp.expose_app_in_browser = true`，用于开发模式。
- F-069: docs/source/migrate_to_notebook7.md:31-34 — 需要 Classic Notebook 兼容的用户可切换到 `nbclassic` 包，它提供旧界面兼容和过渡期支持。
- F-070: setup.py:1-3 — setup.py 仅为 shim，内容为 `__import__("setuptools").setup()`，用于兼容需要 setup.py 的旧版 JupyterLab extension 工具链。

## 六、前端包架构

- F-071: packages/application/src/app.ts:27 — 前端 `NotebookApp` 类继承自 `JupyterFrontEnd<INotebookShell>`（不是 JupyterLab 的 JupyterLab 类），但使用 `JupyterLab.defaultInfo` 作为应用信息默认值。
- F-072: packages/application/src/app.ts:63 — 前端应用名 `name = 'Jupyter Notebook'`。
- F-073: packages/application/src/app.ts:84 — 版本从 PageConfig 获取 `appVersion`。
- F-074: packages/application/src/shell.ts:82 — `NotebookShell` 继承自 `Widget` 并实现 `JupyterFrontEnd.IShell` 接口，是 Notebook 专属的 Shell 布局（不同于 JupyterLab 的 ILabShell）。
- F-075: packages/application/src/shell.ts:47 — Shell 定义 6 个布局区域：`main`、`top`、`menu`、`left`、`right`、`down`。
- F-076: packages/application/src/shell.ts:124-126 — 侧边栏（left/right）默认隐藏，启动后不显示。
- F-077: packages/application/src/shell.ts:184 — down 面板（底部面板）初始隐藏，用于显示 log console 等。
- F-078: packages/application/src/shell.ts:175 — 左右中布局的相对尺寸为 [1, 2.5, 1]，中间主区域最宽。
- F-079: packages/application/src/shell.ts:370-385 — main 区域同一时间只允许一个 widget（单文档模式），与 JupyterLab 的多标签/多文档模式不同。
- F-080: packages/application/src/panelhandler.ts:16-63 — `PanelHandler` 使用 rank 排序管理面板中的 widget，按 rank 插入到正确位置。
- F-081: packages/application/src/panelhandler.ts:68-298 — `SidePanelHandler` 管理侧边栏（StackedPanel），同一时间只显示一个 widget，支持展开/折叠、关闭按钮。
- F-082: packages/application/src/pathopener.ts:11-26 — `DefaultNotebookPathOpener` 实现 `INotebookPathOpener`，通过 `window.open()` 在新浏览器标签页打开路径，这是 Notebook 多页面导航的核心机制。
- F-083: app/index.template.js:220-231 — 前端启动时创建 `NotebookApp` 实例（从 `@jupyter-notebook/application` 导入），传入 PluginRegistry、ServiceManager、mimeExtensions 和 availablePlugins。
- F-084: app/index.template.js:53-82 — 根据 `notebookPage` PageConfig 值（tree/notebooks/edit/consoles/terminals）动态加载不同页面的插件集，实现多页面单应用架构。
- F-085: app/index.template.js:125-167 — 支持 federated extensions（动态加载），通过 webpack module federation 从 `fullLabextensionsUrl` 加载第三方扩展。
- F-086: app/package.json:6-9 — 构建工具使用 rspack（不是 webpack），配置了 build、build:prod、build:prod:minimize、build:prod:release 等多个构建脚本。

## 七、与 JupyterLab 的关系

- F-087: app/package.json:31-112 — resolutions 中锁定了 50+ 个 `@jupyterlab/*` 包版本为 `~4.7.0-alpha.1`，几乎复用所有 JupyterLab 核心前端包。
- F-088: app/package.json:131-197 — dependencies 中 Notebook 自有包仅 11 个（@jupyter-notebook/*），而 @jupyterlab/* 依赖包超过 40 个，Notebook 自有代码占比很小。
- F-089: app/package.json:221-385 — `jupyterlab.plugins` 配置定义了 5 个 URL 路由（/、/tree、/notebooks、/consoles、/edit）各自加载哪些插件，对 JupyterLab 插件做了精细化白名单筛选。
- F-090: app/package.json:230-235 — 根路由 `/` 只启用 `@jupyterlab/application-extension` 的 4 个插件（context-menu、faviconbusy、router、top-bar），而不是全部启用。
- F-091: app/package.json:236-248 — `@jupyterlab/apputils-extension` 仅启用 11 个核心插件（palette、notification、sanitizer、settings、state、themes 等），不启用 Lab 全部功能。
- F-092: app/package.json:296-304 — `/notebooks` 路由额外加载 `@jupyterlab/notebook-extension` 的 8 个插件（cell-executor、export、factory、tracker 等），这些是 notebook 编辑页面专属的。
- F-093: app/package.json:316-336 — `/tree` 路由加载 filebrowser（browser 模式，非 factory）、running sessions、extension manager、setting editor 等"仪表盘"类插件。
- F-094: app/package.json:386-445 — singletonPackages 列表包含 60+ 个包（@jupyterlab/*、@lumino/*、react、yjs、codemirror 等），这些包在 module federation 中作为单例共享。
- F-095: packages/lab-extension/src/index.ts:68-243 — `interfaceSwitcher` 插件检测当前环境（Notebook/Lab/NbClassic），在工具栏添加"Open in…"切换按钮，实现多界面互操作。
- F-096: packages/lab-extension/src/index.ts:99-100 — 通过 `PageConfig.getOption('nbclassic_enabled')` 检测 NbClassic 是否可用。
- F-097: packages/application-extension/src/index.ts:307-328 — `menus` 插件总是 dispose 掉 Tabs 菜单（JupyterLab 的多文档标签菜单在 Notebook 单文档模式下不需要），并根据页面类型 dispose 掉 Edit/Kernel/Run 菜单。
- F-098: packages/docmanager-extension/src/index.ts:42-85 — 自定义 `IDocumentWidgetOpener` 实现：默认通过 `window.open()` 在新标签页打开文档（.ipynb → /notebooks/，其他 → /edit/），而非在当前页面添加 widget。
- F-099: packages/console-extension/src/index.ts:99-141 — console 的 redirect 插件：如果 console 与当前 notebook 共享 kernel，则在右侧面板打开（scratchpad 模式）；否则在新标签页打开并 dispose 掉当前 widget。
- F-100: packages/terminal-extension/src/index.ts:76-109 — terminal 的 redirect 插件：terminal 总是在新标签页打开，当前页面的 widget 被 dispose。

## 八、入口点与注册机制

- F-101: notebook/__init__.py:8-9 — `_jupyter_server_extension_paths()` 返回 `[{"module": "notebook"}]`，这是经典的 server extension 发现函数。
- F-102: notebook/__init__.py:12-16 — `_jupyter_server_extension_points()` 返回 `[{"module": "notebook", "app": JupyterNotebookApp}]`，这是现代 jupyter_server v2 的 ExtensionApp 注册方式。
- F-103: notebook/__init__.py:19-20 — `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": "@jupyter-notebook/lab-extension"}]`，将预构建的前端资产注册为 JupyterLab federated labextension。
- F-104: notebook/__main__.py:5-7 — `python -m notebook` 执行 `from notebook.app import main; sys.exit(main())`。
- F-105: app/templates/tree_template.html:28 — tree 页面设置 `notebookPage='tree'` sentinel 值，前端据此决定加载哪些插件。
- F-106: app/templates/notebooks_template.html:28 — notebook 编辑页面设置 `notebookPage='notebooks'`。
- F-107: app/templates/tree_template.html:30-32 — 所有页面通过 `<script id="jupyter-config-data" type="application/json">` 注入 page_config JSON 数据。
- F-108: app/templates/notebooks_template.html:22 — notebook 页面 body 有 `data-notebook="notebooks"` 属性，用于 CSS 选择器和 JS 判断。
- F-109: app/templates/*.html — 所有 HTML 模板为空 body（仅含 script 标签），页面内容完全由 JavaScript 渲染，与经典 Notebook v6 的服务端渲染不同。
- F-110: app/templates/*.html:22 — body 使用 `class="jp-ThemedContainer"`，主题系统完全由 JupyterLab 提供。

## 九、经典 UI 保留策略

- F-111: packages/application-extension/src/index.ts:1240-1298 — `zen` 插件实现 Zen Mode（全屏+隐藏 top/menu），致敬经典 Notebook 的简洁界面。
- F-112: packages/notebook-extension/src/index.ts:588-670 — `scrollOutput` 插件复刻经典 Notebook 的输出自动滚动逻辑（输出超过 100 行时自动滚动）。
- F-113: packages/notebook-extension/src/index.ts:358-436 — `fullWidthNotebook` 插件支持全屏宽度 notebook（经典 Notebook 默认全宽，JupyterLab 默认居中）。
- F-114: packages/notebook-extension/src/index.ts:754-781 — `trusted` 插件在菜单区域显示 Trusted 指示器，对应经典 Notebook 的可信/不可信标识。
- F-115: notebook/app.py:221-239 — `CustomCssHandler` 保留经典 Notebook 的 `~/.jupyter/custom/custom.css` 自定义 CSS 加载功能。
- F-116: packages/notebook-extension/src/index.ts:104-235 — `checkpoints` 插件在顶部栏显示 "Last Checkpoint: ..." 信息，复刻经典 Notebook 的检查点时间显示。
- F-117: packages/console-extension/src/index.ts:147-253 — `scratchpadConsole` 插件实现 scratchpad console（附着在 notebook 右侧的临时 console），是经典 Notebook 用户常需的功能。
- F-118: packages/application-extension/src/index.ts:783-866 — `topVisibility` 插件支持自动隐藏 top header（移动端自动隐藏，桌面端可配置），提供更专注的编辑体验。
- F-119: packages/application-extension/src/index.ts:188-212 — `logo` 插件在 top 区域添加 Jupyter logo，点击跳转到 `/tree` 页面。
- F-120: packages/application-extension/src/index.ts:649-778 — `title` 插件在 top 区域显示文档标题，点击可重命名文件。
