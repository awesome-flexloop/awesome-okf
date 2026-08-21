---
title: 架构总览
type: concept
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "01"
difficulty: intermediate
tags: ["architecture", "frontend", "backend"]
prerequisites: ["00-introduction"]
sources: ["F-010", "F-021", "F-030", "F-032", "F-033"]
next: ["02-backend-app", "03-frontend-shell"]
---

# 01 | 架构总览

## 整体架构

Jupyter Notebook v7 采用经典的**前后端分离**架构，后端提供REST API和静态页面服务，前端在浏览器中运行单页应用（SPA）。

```
┌──────────────────────────────────────────────────────────────┐
│                        浏览器 (Client)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              NotebookApp (JupyterFrontEnd)             │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │            NotebookShell (Lumino Widget)         │  │  │
│  │  │  ┌──────┐  ┌──────────────────────────────────┐  │  │  │
│  │  │  │ Menu │  │            Top Bar               │  │  │  │
│  │  │  └──────┘  └──────────────────────────────────┘  │  │  │
│  │  │  ┌────┐  ┌──────────────────────────┐  ┌─────┐  │  │  │
│  │  │  │Left│  │                          │  │Right│  │  │  │
│  │  │  │    │  │       Main Area          │  │     │  │  │  │
│  │  │  │    │  │   (Notebook/File/Edit)   │  │     │  │  │  │
│  │  │  │    │  │                          │  │     │  │  │  │
│  │  │  └────┘  └──────────────────────────┘  └─────┘  │  │  │
│  │  │              ┌─────────────────────┐             │  │  │
│  │  │              │     Down Area       │             │  │  │
│  │  │              │  (Console/Status)   │             │  │  │
│  │  │              └─────────────────────┘             │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │           Plugin System (Token DI)               │  │  │
│  │  │  @jupyter-notebook/application-extension         │  │  │
│  │  │  @jupyter-notebook/notebook-extension            │  │  │
│  │  │  @jupyter-notebook/tree-extension ...            │  │  │
│  │  │  + 所有 JupyterLab 插件                          │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                         │ HTTP/WebSocket                     │
└─────────────────────────┼────────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────────┐
│                   Tornado Server                            │
│  ┌───────────────────────▼────────────────────────────────┐  │
│  │           JupyterNotebookApp (LabServerApp)            │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │              Notebook Handlers                   │  │  │
│  │  │  /tree(.*)        → TreeHandler                  │  │  │
│  │  │  /notebooks(.*)   → NotebookHandler              │  │  │
│  │  │  /edit(.*)        → FileHandler                  │  │  │
│  │  │  /consoles/(.*)   → ConsoleHandler               │  │  │
│  │  │  /terminals/(.*)  → TerminalHandler              │  │  │
│  │  │  /custom/custom.css → CustomCssHandler           │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │        Jupyter Server Core Handlers              │  │  │
│  │  │  /api/contents, /api/kernels, /api/sessions...   │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │     JupyterLab Handlers (LabServerApp)           │  │  │
│  │  │  /lab, /lab/api, /lab/tree ...                   │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 后端架构

### 核心类继承关系

```
ExtensionApp (jupyter_server)
    └── LabServerApp (jupyterlab_server)
            └── NotebookConfigShimMixin (notebook_shim)
                    └── JupyterNotebookApp (notebook/app.py)
```

> **信源**: `class JupyterNotebookApp(NotebookConfigShimMixin, LabServerApp)`（F-010）

`JupyterNotebookApp` 是整个后端的入口类，它：
1. 继承 `LabServerApp` 获得JupyterLab的全部后端能力
2. 通过 `NotebookConfigShimMixin` 获得v6配置兼容性
3. 注册6个页面渲染Handler
4. 配置静态文件、模板、Jinja2环境

### Handler体系

Notebook自己定义的Handler非常精简，只负责**页面渲染**：

| Handler | 路由 | 职责 |
|---------|------|------|
| `NotebookBaseHandler` | - | 基类，提供 `get_page_config()` |
| `TreeHandler` | `/tree(.*)` | 文件浏览器页面/目录列表 |
| `NotebookHandler` | `/notebooks(.*)` | Notebook编辑页面 |
| `FileHandler` | `/edit(.*)` | 文本文件编辑页面 |
| `ConsoleHandler` | `/consoles/(.*)` | 控制台页面 |
| `TerminalHandler` | `/terminals/(.*)` | 终端页面 |
| `CustomCssHandler` | `/custom/custom.css` | 自定义CSS样式 |

> **信源**: 路由注册代码 `app.py:L350-355`（F-021）

所有业务API（文件操作、Kernel管理、Session管理等）均由Jupyter Server和JupyterLab提供。

## 前端架构

### 核心类关系

```
JupyterFrontEnd (@jupyterlab/application)
    └── NotebookApp (@jupyter-notebook/application)
            ├── shell: NotebookShell (implements JupyterFrontEnd.IShell)
            ├── commands: CommandRegistry
            └── docRegistry: DocumentRegistry
```

> **信源**: `export class NotebookApp extends JupyterFrontEnd<INotebookShell>`（F-030）

### NotebookShell 六区域模型

NotebookShell将UI划分为6个命名区域（F-033）：

```
     ┌─────────────────────────────────┐
     │            menu                 │ ← 菜单栏
     ├─────────────────────────────────┤
     │            top                  │ ← 顶部工具栏
     ├────┬──────────────────────┬─────┤
     │    │                      │     │
     │left│        main          │right│ ← 主内容区 + 左右侧边栏
     │    │                      │     │
     ├────┴──────────────────────┴─────┤
     │            down                 │ ← 底部面板（控制台等）
     └─────────────────────────────────┘
```

| 区域 | 用途 | Handler类型 |
|------|------|------------|
| `menu` | 菜单栏 | PanelHandler |
| `top` | 顶部工具栏 | PanelHandler |
| `left` | 左侧边栏（文件浏览器等） | SidePanelHandler |
| `main` | 主内容区（Notebook/文件编辑器） | Panel |
| `right` | 右侧边栏（属性检查器等） | SidePanelHandler |
| `down` | 底部面板（控制台/日志） | 默认占25%高度 |

> **信源**: shell.ts 区域定义 `'main' | 'top' | 'menu' | 'left' | 'right' | 'down'`（F-033）

## 请求生命周期

### 打开一个Notebook文件的完整流程

1. **用户访问** `http://localhost:8888/notebooks/example.ipynb`
2. **Tornado路由匹配**: `/notebooks(.*)` → `NotebookHandler`
3. **NotebookHandler.get()** 检查路径：
   - 如果是目录 → 重定向到 `/tree/`
   - 如果是文件 → 渲染 `notebooks.html` 模板
4. **get_page_config()** 构建前端配置JSON：
   - 包含appVersion、baseUrl、token、mathjaxConfig等
   - 递归合并labextension配置
5. **浏览器加载** HTML + JS bundle，启动 `NotebookApp`
6. **插件激活**：所有 `autoStart: true` 的JupyterLab插件按依赖顺序激活
7. **Notebook插件** 解析URL路径，打开对应文件
8. **WebSocket连接** 建立到Kernel的通信通道
9. **渲染Notebook**：在main区域显示Notebook widget

> **信源**: NotebookHandler.get() 逻辑 `app.py:L206-218`（F-023），get_page_config() `app.py:L56-130`（F-020, F-025）

## 关键设计决策

### 1. 为什么Notebook自己只定义页面Handler？

因为v7的核心理念是**复用JupyterLab**。Notebook不需要重新实现文件API、Kernel API、Session管理——这些都由Jupyter Server和JupyterLab提供。Notebook只负责提供"经典Notebook体验"的页面入口和Shell布局。

### 2. 为什么需要notebook_shim？

Notebook 6.x有大量traitlets配置项（如 `NotebookApp.port`、`NotebookApp.notebook_dir`）。v7中这些配置项属于 `ServerApp` 或 `LabServerApp`。`notebook_shim` 提供了一个Mixin类，将旧配置名映射到新配置名，实现平滑迁移。

### 3. 前端为什么用Token DI？

JupyterLab插件系统使用Lumino的Token模式实现依赖注入（类似Angular的InjectionToken）。每个服务定义一个唯一的Token，插件在activate函数中声明需要的Token，运行时由应用注入对应实例。这实现了插件间的**松耦合**。

## 目录结构导览

```
notebook/                          # Python后端包
├── __init__.py                    # 入口：extension paths声明
├── _version.py                    # 版本号
├── app.py                         # 核心：JupyterNotebookApp + Handlers
└── custom/custom.css              # 默认自定义CSS

packages/                          # TypeScript前端包
├── application/                   # 核心应用与Shell
│   └── src/
│       ├── app.ts                 # NotebookApp类
│       ├── shell.ts               # NotebookShell布局
│       ├── panelhandler.ts        # 面板Handler
│       ├── pathopener.ts          # 路径打开器
│       └── tokens.ts              # DI Token定义
├── application-extension/         # 主应用扩展插件
├── notebook-extension/            # Notebook专属功能插件
├── tree-extension/                # 文件浏览器插件
├── terminal-extension/            # 终端插件
├── console-extension/             # 控制台插件
├── docmanager-extension/          # 文档管理插件
├── documentsearch-extension/      # 文档搜索插件
├── help-extension/                # 帮助菜单插件
├── lab-extension/                 # Lab切换/启动树插件
├── ui-components/                 # UI组件与图标
├── tree/                          # Tree页面widget
└── _metapackage/                  # 元包（依赖聚合）
```

> **信源**: 前端包列表（F-040）

## 下一步

- → [后端应用类](./02-backend-app.md) 深入理解JupyterNotebookApp的启动流程与配置系统
- → [前端Shell布局](./03-frontend-shell.md) 深入理解NotebookShell的区域管理与widget添加机制
