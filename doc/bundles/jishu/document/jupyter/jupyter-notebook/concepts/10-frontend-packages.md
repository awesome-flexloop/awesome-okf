---
title: 前端包结构
type: concept
bundle: jupyter-notebook
chapter: "10"
difficulty: intermediate
tags: ["frontend", "packages", "monorepo", "lerna"]
prerequisites: ["01-architecture-overview", "03-frontend-shell", "06-extension-system"]
sources: ["F-040"]
next: ["11-migration-guide"]
---

# 10 | 前端包结构

Notebook v7 前端由13个npm包组成Lerna monorepo，每个包负责特定功能域。理解包结构是阅读前端源码和开发扩展的基础。

## 包总览

| 包名 | npm包名 | 代码量 | 核心职责 |
|------|---------|--------|---------|
| application | `@jupyter-notebook/application` | ⭐⭐⭐ | NotebookApp、NotebookShell、Token定义 |
| application-extension | `@jupyter-notebook/application-extension` | ⭐⭐⭐ | 主插件、命令、路由、Zen模式 |
| notebook-extension | `@jupyter-notebook/notebook-extension` | ⭐⭐ | Notebook专属功能（Kernel Logo、信任状态） |
| tree | `@jupyter-notebook/tree` | ⭐⭐ | NotebookTree widget |
| tree-extension | `@jupyter-notebook/tree-extension` | ⭐⭐ | 文件浏览器命令与widget工厂 |
| terminal-extension | `@jupyter-notebook/terminal-extension` | ⭐ | 终端集成 |
| console-extension | `@jupyter-notebook/console-extension` | ⭐ | 控制台/草稿板 |
| docmanager-extension | `@jupyter-notebook/docmanager-extension` | ⭐ | 文档管理扩展 |
| documentsearch-extension | `@jupyter-notebook/documentsearch-extension` | ⭐ | 文档搜索 |
| help-extension | `@jupyter-notebook/help-extension` | ⭐ | 帮助菜单 |
| lab-extension | `@jupyter-notebook/lab-extension` | ⭐ | JupyterLab切换、启动树 |
| ui-components | `@jupyter-notebook/ui-components` | ⭐ | 图标、UI组件 |
| _metapackage | `@jupyter-notebook/metapackage` | - | 依赖聚合（不包含代码） |

> **信源**: packages/目录列表（F-040）

## 核心包详解

### 1. application（核心应用包）

**路径**: `packages/application/`

这是Notebook前端最核心的包，定义了：

| 文件 | 内容 |
|------|------|
| `src/app.ts` | `NotebookApp` 类（继承JupyterFrontEnd） |
| `src/shell.ts` | `NotebookShell` 类（六区域布局） |
| `src/tokens.ts` | DI Token定义（INotebookShell等） |
| `src/panelhandler.ts` | PanelHandler / SidePanelHandler |
| `src/pathopener.ts` | NotebookPathOpener |
| `src/index.ts` | 公共API导出 |

**关键导出**:
```typescript
// packages/application/src/index.ts
export { NotebookApp } from './app';
export { NotebookShell, INotebookShell } from './shell';
export { SidePanel, SidePanelHandler, SidePanelPalette } from './panelhandler';
export { INotebookPathOpener, defaultNotebookPathOpener } from './pathopener';
```

**依赖**:
- `@jupyterlab/application` (JupyterFrontEnd基类)
- `@jupyterlab/docregistry` (文档模型)
- `@lumino/widgets` (Widget基类)
- `@lumino/coreutils` (Token, PromiseDelegate)

### 2. application-extension（主应用扩展包）

**路径**: `packages/application-extension/`

这是Notebook前端功能最丰富的包，包含多个插件：

| 插件 | ID前缀 | 功能 |
|------|--------|------|
| dirty | `:dirty` | 关闭标签页脏检查 |
| commands | `:commands` | 核心命令注册 |
| router | `:router` | URL路由处理 |
| zenmode | `:zenmode` | Zen模式切换 |
| topbar | `:topbar` | 顶部栏 |
| menu | `:menu` | 菜单注册 |
| palette | `:palette` | 命令面板 |
| settings | `:settings` | 设置连接器 |

**Schema文件**:
- `shell.json` — Shell布局配置
- `menus.json` — 菜单定义
- `shortcuts.json` — 快捷键
- `top.json` — 顶部栏配置
- `zen.json` — Zen模式配置
- `title.json` — 标题配置
- `pages.json` — 页面配置

**关键命令**（F-038）:
```typescript
namespace CommandIDs {
    export const duplicate = 'application:duplicate';
    export const handleLink = 'application:handle-local-link';
    export const toggleTop = 'application:toggle-top';
    export const togglePanel = 'application:toggle-panel';
    export const toggleZen = 'application:toggle-zen';
    export const openLab = 'application:open-lab';
    export const openTree = 'application:open-tree';
    export const rename = 'application:rename';
    export const resolveTree = 'application:resolve-tree';
}
```

> **信源**: [application-extension/src/index.ts:L92-137](../references/00-source-registry.md#S-009)（F-038）

### 3. notebook-extension（Notebook专属功能包）

**路径**: `packages/notebook-extension/`

提供Notebook经典功能：
- Kernel Logo显示
- Notebook信任状态（trusted.tsx）
- 检查点管理
- 关闭标签确认
- Notebook元数据编辑
- 全宽Notebook模式
- 滚动输出
- 菜单覆盖（修改JupyterLab默认菜单）

**Schema文件**:
- `checkpoints.json` — 检查点配置
- `close-tab.json` — 关闭标签配置
- `edit-notebook-metadata.json` — 元数据编辑配置
- `full-width-notebook.json` — 全宽配置
- `kernel-logo.json` — Kernel Logo配置
- `menu-override.json` — 菜单覆盖配置
- `scroll-output.json` — 滚动输出配置

### 4. tree（Tree页面包）

**路径**: `packages/tree/`

定义 `NotebookTree` widget，是文件浏览器页面的主容器：

| 文件 | 内容 |
|------|------|
| `src/notebook-tree.ts` | NotebookTree类 |
| `src/token.ts` | INotebookTree Token |
| `src/index.ts` | 公共API导出 |

### 5. tree-extension（Tree功能扩展包）

**路径**: `packages/tree-extension/`

提供文件浏览器的命令和widget工厂：
- 文件操作命令（新建/重命名/删除/上传）
- 文件浏览器widget工厂
- 启动器（Launcher）条目

**Schema文件**:
- `file-actions.json` — 文件操作配置
- `widget.json` — Widget配置

### 6. ui-components（UI组件包）

**路径**: `packages/ui-components/`

提供Notebook专属的UI组件和图标：

| 文件 | 内容 |
|------|------|
| `src/icon/index.ts` | 图标导出 |
| `src/icon/iconimports.ts` | 图标导入（jupyter.svg等） |
| `src/index.ts` | 公共API |
| `style/icons/jupyter.svg` | Jupyter图标SVG |

### 7. 其他扩展包

#### terminal-extension

终端功能插件，将JupyterLab的终端能力集成到NotebookShell中。终端widget添加到down区域或单独的终端页面。

#### console-extension

控制台/草稿板功能。Schema `scratchpad-console.json` 配置草稿板行为。

#### docmanager-extension

文档管理扩展，处理文档打开/关闭/保存的生命周期事件。

#### documentsearch-extension

文档搜索功能，在Notebook和文件编辑器中提供搜索/替换。

#### help-extension

帮助菜单，提供Jupyter Notebook帮助链接。Schema `open.json` 配置打开行为。

#### lab-extension

提供JupyterLab切换功能和启动树：
- "Open in JupyterLab" 命令
- 启动树页面（Launch Tree）
- 接口切换器

Schema文件：
- `interface-switcher.json` — 接口切换配置
- `launch-tree.json` — 启动树配置

### 8. _metapackage（元包）

**路径**: `packages/_metapackage/`

元包不包含实际代码，只声明对所有 `@jupyter-notebook/*` 包的依赖。这是前端构建的入口，确保所有包都被包含在最终bundle中。

```json
{
  "name": "@jupyter-notebook/metapackage",
  "private": true,
  "dependencies": {
    "@jupyter-notebook/application": "^7.7.0-alpha.1",
    "@jupyter-notebook/application-extension": "^7.7.0-alpha.1",
    "@jupyter-notebook/notebook-extension": "^7.7.0-alpha.1",
    "...": "..."
  }
}
```

## 包依赖关系图

```
                         ┌──────────────┐
                         │ _metapackage │
                         └──────┬───────┘
                                │ depends on all
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
│  application   │   │  ui-components     │   │  notebook-extension│
│ (核心App/Shell) │   │  (图标/组件)       │   │  (Notebook功能)     │
└───────┬────────┘   └─────────┬─────────┘   └─────────┬─────────┘
        │                      │                       │
        ├──────────────────────┴───────────────────────┤
        │            被所有扩展包依赖                    │
        ▼                                              ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│application-      │  │ tree-extension   │  │ lab-extension     │
│extension         │  │                  │  │                   │
│(主插件/命令/路由) │  │ (文件浏览器)      │  │ (Lab切换/启动树)  │
└──────────────────┘  └────────┬─────────┘  └───────────────────┘
                               │
                      ┌────────▼─────────┐
                      │ tree             │
                      │ (NotebookTree)   │
                      └──────────────────┘

独立扩展包（依赖application，不互相依赖）:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│terminal-extension│  │console-extension │  │docmanager-       │
│                  │  │                  │  │extension         │
└──────────────────┘  └──────────────────┘  └──────────────────┘
┌──────────────────┐  ┌──────────────────┐
│documentsearch-   │  │ help-extension   │
│extension         │  │                  │
└──────────────────┘  └──────────────────┘
```

## 每个包的标准结构

每个npm包遵循统一结构：

```
packages/<package-name>/
├── package.json          # 包配置
├── tsconfig.json         # TypeScript配置
├── babel.config.js       # Babel配置（如果有测试）
├── jest.config.js        # Jest配置（如果有测试）
├── src/
│   ├── index.ts          # 公共API导出
│   └── ...               # 源码文件
├── style/
│   ├── base.css          # 基础样式
│   ├── index.css         # 样式入口
│   ├── index.js          # 样式导入（webpack入口）
│   └── ...               # 其他CSS文件
├── schema/               # JSON Schema文件（如果有设置）
│   └── *.json
└── test/                 # 测试文件（如果有）
    └── *.spec.ts
```

## 如何阅读前端源码

推荐阅读顺序：

1. **packages/application/src/tokens.ts** — 了解所有Token定义
2. **packages/application/src/shell.ts** — 理解Shell布局
3. **packages/application/src/app.ts** — 理解应用启动
4. **packages/application-extension/src/index.ts** — 理解插件注册和命令
5. **packages/notebook-extension/src/index.ts** — 理解Notebook专属功能
6. **packages/tree-extension/src/index.ts** — 理解文件浏览器
7. 其他扩展包按需阅读

## 开发新前端包

如果你需要为Notebook开发新的前端功能：

1. 在 `packages/` 下创建新目录
2. 参考现有包的 `package.json` 和 `tsconfig.json`
3. 在 `packages/_metapackage/package.json` 中添加依赖
4. 在根 `package.json` 中确认workspace包含
5. 运行 `npm install` 链接新包
6. 开发并build

但大多数情况下，**不需要创建新包**——作为第三方扩展发布即可（类似JupyterLab第三方扩展）。Notebook内置包只是官方核心功能。

## 下一步

- → [v6到v7迁移指南](11-migration-guide.md) 从Notebook 6迁移到7的完整指南
