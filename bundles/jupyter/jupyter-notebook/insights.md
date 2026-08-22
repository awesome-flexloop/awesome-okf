---
type: Insights
okf_version: '0.2'
title: jupyter-notebook 架构洞察
tags:
- jupyter
- notebook
- classic
- jupyterlab
- architecture
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/notebook/pyproject.toml
- ../../../../../external/libs/jupyter/notebook/package.json
- ../../../../../external/libs/jupyter/notebook/README.md
- ../../../../../external/libs/jupyter/notebook/setup.py
- ../../../../../external/libs/jupyter/notebook/notebook/__init__.py
- ../../../../../external/libs/jupyter/notebook/notebook/__main__.py
- ../../../../../external/libs/jupyter/notebook/notebook/_version.py
- ../../../../../external/libs/jupyter/notebook/notebook/app.py
---

# Jupyter Notebook v7 架构洞察

## 架构层次图

```mermaid
graph TB
    subgraph Browser["浏览器层"]
        UI["Notebook UI<br/>(单文档、经典布局)"]
        Shell["NotebookShell<br/>(6区域布局: top/menu/main/left/right/down)"]
        NBPkg["@jupyter-notebook/*<br/>(12个自定义包)"]
    end

    subgraph LabFE["JupyterLab 前端层"]
        JLabFE["@jupyterlab/* 核心包<br/>(application, notebook, docmanager,<br/>filebrowser, console, terminal,<br/>codemirror, debugger, toc, lsp...)"]
        Lumino["@lumino/*<br/>(widgets, commands, signaling...)"]
        JLabUI["@jupyterlab/ui-components"]
    end

    subgraph AppFE["Notebook 前端应用"]
        AppEntry["index.template.js<br/>(PluginRegistry + 路由分发)"]
        Pages["多页面路由<br/>(/tree, /notebooks, /edit,<br/>/consoles, /terminals)"]
        FedExt["Federated Extensions<br/>(webpack module federation)"]
    end

    subgraph PyBE["Python 后端层"]
        NbApp["JupyterNotebookApp<br/>(ExtensionApp)"]
        Shim["notebook_shim<br/>(v6→v7 配置映射)"]
        Handlers["6个页面 Handlers<br/>(Tree, Notebook, Edit,<br/>Console, Terminal, CustomCss)"]
    end

    subgraph JServer["Jupyter Server 层"]
        LabSrv["LabServerApp<br/>(from jupyterlab_server)"]
        JServer["jupyter_server<br/>(kernel, contents, sessions, auth)"]
        Tornado["Tornado Web Server"]
    end

    UI --> Shell
    Shell --> NBPkg
    NBPkg --> JLabFE
    Pages --> AppEntry
    AppEntry --> NBPkg
    AppEntry --> FedExt
    JLabFE --> Lumino
    JLabFE --> JLabUI

    NbApp --> Shim
    NbApp --> Handlers
    NbApp -->|"继承"| LabSrv
    Handlers -->|"渲染模板+page_config"| AppEntry
    LabSrv --> JServer
    JServer --> Tornado

    style UI fill:#e1f5fe
    style Shell fill:#e1f5fe
    style NBPkg fill:#e1f5fe
    style JLabFE fill:#fff3e0
    style Lumino fill:#fff3e0
    style JLabUI fill:#fff3e0
    style AppEntry fill:#e8f5e9
    style Pages fill:#e8f5e9
    style FedExt fill:#e8f5e9
    style NbApp fill:#f3e5f5
    style Shim fill:#fce4ec
    style Handlers fill:#f3e5f5
    style LabSrv fill:#fff8e1
    style JServer fill:#fff8e1
    style Tornado fill:#fff8e1
```

---

## 洞察一：薄壳设计——复用而非重写的架构抉择

### 核心观察

Notebook v7 的 Python 包仅包含 **1 个核心源文件** (`app.py`，约 366 行) 和 **12 个前端包**，而它所依赖的 JupyterLab 包含 **100+ 前端包** 和完整的后端服务层。从代码量对比来看，Notebook v7 的自有代码与 JupyterLab 的比例约为 **1:10** 甚至更小。

### 设计模式：配置即差异

Notebook v7 并不重新实现 Notebook 的核心功能（notebook 编辑、cell 执行、kernel 管理、文件浏览等），而是通过以下三层"过滤"来将 JupyterLab 重塑为经典 Notebook 体验：

1. **后端继承与覆盖**：`JupyterNotebookApp` 继承 `LabServerApp`，仅覆盖 `default_url`（`/tree` 而非 `/lab`）、`static_dir`/`templates_dir` 等目录配置，以及注册 6 个经典路由 Handlers。所有 kernel/contents/sessions API 完全复用 jupyter_server 和 jupyterlab_server。

2. **前端 Shell 替换**：Notebook 定义了自己的 `NotebookShell`（6 区域布局：top/menu/main/left/right/down），替代 JupyterLab 的 `LabShell`（更复杂的多文档 Dock Panel 布局）。NotebookShell 强制 **单文档模式**（main 区域同一时间只允许一个 widget），这与经典 Notebook 的一次只打开一个 notebook 的交互模式一致。

3. **插件白名单筛选**：这是最关键的差异层。在 `app/package.json` 的 `jupyterlab.plugins` 配置中，Notebook 对每个 JupyterLab 扩展做了精细的插件筛选：
   - 根路由 `/` 只启用 application-extension 的 4 个核心插件（context-menu、faviconbusy、router、top-bar）
   - `/tree` 路由加载 filebrowser、running sessions、setting editor 等"仪表盘"插件
   - `/notebooks` 路由才加载 notebook-extension、debugger、toc、tooltip 等编辑功能
   - 所有页面都 **不启用** JupyterLab 的 launcher、extension manager（仅在 /tree 启用）等 Lab 特色功能

### 为什么不重写？

这一决策基于务实的工程考量：

- **维护成本**：JupyterLab 已有 5+ 年的成熟开发，cell 编辑、kernel 通信、CRDT 协作、debugger、LSP、主题系统等核心功能高度复杂，重写将导致功能碎片化。
- **扩展生态**：JupyterLab 的 extension 生态已经成熟（federated extensions），Notebook v7 通过作为 JupyterLab 的一个"发行版"自动获得大部分 Lab 扩展兼容性。
- **演进路径**：JupyterLab 持续迭代新功能（如 RTC 协作、debugger），Notebook v7 通过版本对齐（`jupyterlab>=4.7.0a1,<4.8`）自动获得这些更新。

### 核心模式提炼

> **Thin Shell Pattern（薄壳模式）**：当需要为一个功能丰富的平台提供一个简化/聚焦的界面变体时，不重新实现核心功能，而是通过（1）继承并覆盖应用基类、（2）替换布局 Shell、（3）插件白名单筛选 三个层次来"修剪"出目标体验。核心代码作为配置和布局差异存在，而非功能实现。

---

## 洞察二：Shim 层与多页面路由——向后兼容的渐进式迁移

### 核心观察

Notebook v7 在架构上做了一个根本性的转变：从经典 Notebook v6 的**单块 Tornado 应用**变为 jupyter_server 的 **ExtensionApp**。这一转变意味着配置文件路径、API 端点、扩展机制全部变化。Notebook 通过两个互补的策略实现平滑迁移。

### 策略一：notebook_shim 配置映射层

`notebook_shim` 是一个独立的外部包（`notebook_shim>=0.2,<0.3`），作为 `NotebookConfigShimMixin` 被混入 `JupyterNotebookApp` 的 MRO 首位。它的核心职责是：

- 将经典的 `jupyter_notebook_config.py` 配置项映射到 jupyter_server 的 `jupyter_server_config.py` 配置项
- 将旧版 trait 名称（如 `NotebookApp.ip`、`NotebookApp.port`）转发到 `ServerApp.ip`、`ServerApp.port`
- 处理已废弃配置的 deprecation warning，引导用户迁移

通过 MRO 优先级（Mixin 在 `LabServerApp` 之前），shim 层可以拦截和转换配置访问，使得用户旧的配置文件无需立即修改即可工作。

### 策略二：多页面路由 + 新标签页导航

经典 Notebook v6 是**多页面应用**（MPA）：文件浏览器、notebook 编辑器、terminal 各自是独立的 HTML 页面，通过浏览器标签页切换。JupyterLab 是**单页面应用**（SPA）：所有内容在一个页面中通过 Dock Panel 管理。

Notebook v7 采取了一个折中方案——**多页面单应用**（Multi-Page Single-App）：

1. 后端定义 5 个经典路由（`/tree`、`/notebooks/`、`/edit/`、`/consoles/`、`/terminals/`），每个路由返回独立的 HTML 页面（但 body 为空，仅注入 page_config）
2. 前端根据 page_config 中的 `notebookPage` 值动态加载不同的插件集
3. 文档打开默认通过 `window.open()` 在**新浏览器标签页**中打开，而非在当前页面的 Dock Panel 中添加 tab
4. `IDocumentWidgetOpener` 的自定义实现（`docmanager-extension:opener`）根据文件扩展名决定路由（.ipynb → `/notebooks/`，其他 → `/edit/`），然后在新标签页打开并 dispose 当前 widget

这种设计保留了经典 Notebook 用户"每个 notebook 一个标签页"的心智模型，同时底层完全复用 JupyterLab 的 SPA 插件体系。

### 策略三：nbclassic 过渡方案

对于无法立即迁移的用户，Notebook v7 提供了与 `nbclassic` 包的共存能力——`initialize_handlers()` 检测 `nbclassic` 扩展是否启用，前端 interface switcher 在工具栏提供 "Open in NbClassic" 按钮，用户可按需切换到完全兼容 v6 的界面。

### 核心模式提炼

> **Compatibility Shim Pattern（兼容填充层模式）**：当进行底层架构迁移时，通过（1）外部 Mixin 包做配置/API 映射、（2）保留旧的 URL 路由和页面导航范式、（3）提供旧版本并行运行选项，实现用户无感的渐进式迁移。Shim 层作为外部依赖存在，可在未来版本中独立移除。

---

## 洞察三：经典 UI 的"行为复刻"而非"代码复用"

### 核心观察

Notebook v7 的 HTML 模板为空 body（仅含 `<script id="jupyter-config-data">` 和移除 token 的脚本），所有 UI 都由 JavaScript 渲染——这意味着它**没有复用**经典 Notebook v6 的任何 HTML/CSS/JS 代码。但在用户体验层面，v7 通过 JupyterLab 插件体系精心复刻了经典行为。

### 复刻策略：Lab 插件 + Notebook 专属插件

Notebook v7 的 12 个自定义前端包中，有相当部分是为了复刻经典 Notebook 的交互细节：

| 经典行为 | v7 实现方式 | 所在包 |
|---------|-----------|--------|
| 顶部显示 "Last Checkpoint" 时间 | `checkpoints` 插件，Poll 轮询 + TopBar widget | notebook-extension |
| 输出超过阈值自动滚动 | `scrollOutput` 插件，监听 outputArea.model.changed | notebook-extension |
| Trusted/Not Trusted 指示器 | `trusted` 插件，React 组件 + menu 区域 | notebook-extension |
| Kernel 状态文字显示 | `kernelStatus` 插件，menu 区域 widget | notebook-extension |
| Kernel logo 图标 | `kernelLogo` 插件，TopBar widget | notebook-extension |
| 全宽 Notebook 布局 | `fullWidthNotebook` 插件，CSS class toggle | notebook-extension |
| 浏览器标签页 favicon 随 kernel 状态变化 | `tabIcon` 插件，监听 kernel status | notebook-extension |
| 自定义 CSS 加载 | `CustomCssHandler`（后端）+ custom.css 静态文件 | app.py + custom/ |
| Scratchpad console | `scratchpadConsole` 插件，右侧面板 | console-extension |
| Zen Mode（全屏隐藏 header/menu） | `zen` 插件，requestFullscreen + collapse | application-extension |
| "Close and Shut Down" 关闭标签页 | `closeTab` 插件，window.close() | notebook-extension |
| Jupyter logo 点击跳转文件浏览器 | `logo` 插件，TopBar widget | application-extension |
| New 下拉菜单（Notebook/Terminal/Console） | `createNew` 插件，toolbar factory | tree-extension |

### 关键设计：选择性禁用 Lab 功能

复刻经典体验不仅是"添加"功能，更重要的是"移除"Lab 的特性：

- **Tabs 菜单被 dispose**：经典 Notebook 无多文档标签概念，`menus` 插件总是 dispose 掉 `menu.tabsMenu`
- **Kernel/Run 菜单按页面显示**：在 tree/consoles/terminals 页面 dispose 掉 kernelMenu 和 runMenu
- **Side Panel 默认隐藏**：经典 Notebook 默认无左右侧边栏，NotebookShell 的 left/right handler 默认 hide
- **单文档模式**：main 区域已存在 widget 时，新 widget 不会被添加（而是在新标签页打开）
- **自定义 SettingConnector**：覆盖 JupyterLab 某些插件的默认设置，例如帮助 pager 默认在底部面板（down area）打开，复刻经典 Notebook 的 pager 行为

### 核心模式提炼

> **Behavioral Recreation Pattern（行为复刻模式）**：当底层 UI 框架完全替换后，经典交互体验通过新框架的插件/组件机制重新实现，而非移植旧代码。关键在于（1）识别经典用户的核心交互习惯、（2）用新框架的原语重建这些行为、（3）主动移除/禁用新框架中与经典体验冲突的功能。这使得代码完全现代化，同时保留用户熟悉的操作范式。
