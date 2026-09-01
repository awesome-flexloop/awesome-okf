---
title: 插件系统
type: concept
bundle: jupyter-notebook
chapter: "06"
difficulty: advanced
tags: ["frontend", "extension", "plugin", "token-di", "lumino"]
prerequisites: ["01-architecture-overview", "03-frontend-shell"]
sources: ["F-031", "F-034", "F-038", "F-039", "F-040"]
next: ["01-frontend-extension", "03-customize-shell"]
---

# 06 | 插件系统

Jupyter Notebook v7 的前端完全基于JupyterLab的插件系统构建。理解插件系统是开发Notebook扩展的核心前提。

## 什么是JupyterFrontEndPlugin

JupyterLab插件系统使用 `JupyterFrontEndPlugin` 类型定义插件。每个插件是一个声明式对象，包含ID、依赖、激活函数和可选配置。

```typescript
interface JupyterFrontEndPlugin<T> {
    id: string;                    // 插件唯一标识符
    autoStart?: boolean;           // 是否自动启动
    requires?: Token<any>[];       // 必需依赖（Token列表）
    optional?: Token<any>[];       // 可选依赖
    provides?: Token<T>;           // 本插件提供的服务Token
    activate: (app: JupyterFrontEnd, ...args: any[]) => T | Promise<T>;
    description?: string;          // 插件描述
}
```

Notebook v7 完全复用此插件模型。所有Notebook专属功能都是以插件形式注册到 `NotebookApp` 的。

## Token依赖注入

插件系统使用Lumino的 `Token` 模式实现依赖注入，这是理解插件开发的关键概念。

### Token的作用

Token是一个**全局唯一的标识符**，用于在插件之间传递服务实例。它类似于：
- Angular的 `InjectionToken`
- InversifyJS的 `Symbol` 标识符
- Java的 `Class<T>` 类型引用

### 定义一个Token

```typescript
import { Token } from '@lumino/coreutils';

export const INotebookShell = new Token<INotebookShell>(
    '@jupyter-notebook/application:INotebookShell'
);
```

> **信源**: [shell.ts:L31-33](../references/00-source-registry.md#S-007)（F-034）

Token字符串约定：`@namespace/package-name:ServiceName`，确保全局唯一。

### 使用Token声明依赖

```typescript
const myPlugin: JupyterFrontEndPlugin<void> = {
    id: '@jupyter-notebook/my-extension:plugin',
    autoStart: true,
    requires: [INotebookShell, ICommandPalette],  // 声明需要的服务
    activate: (
        app: JupyterFrontEnd,
        shell: INotebookShell,      // 第一个requires对应第一个参数
        palette: ICommandPalette    // 第二个requires对应第二个参数
    ) => {
        // 使用 shell 和 palette...
    }
};
```

运行时，应用在激活插件时，会根据Token查找已注册的服务实例并注入。

### 提供服务

如果一个插件创建了一个可被其他插件使用的服务，通过 `provides` 声明：

```typescript
const myServicePlugin: JupyterFrontEndPlugin<IMyService> = {
    id: '@jupyter-notebook/my-extension:service',
    provides: IMyService,          // 声明本插件提供IMyService
    requires: [INotebookShell],
    activate: (app: JupyterFrontEnd, shell: INotebookShell): IMyService => {
        const service = new MyService(shell);
        return service;            // 返回服务实例
    }
};
```

其他插件就可以在 `requires` 或 `optional` 中声明 `IMyService` 来获取该实例。

## 插件激活流程

应用启动时，插件按以下顺序激活：

1. **注册阶段**：所有插件被添加到应用注册表，但不激活
2. **拓扑排序**：根据 `requires`/`provides` 关系构建依赖图，计算激活顺序
3. **核心服务激活**：先激活提供核心服务的插件（CommandRegistry, Shell等）
4. **自动启动插件**：按依赖顺序激活所有 `autoStart: true` 的插件
5. **按需激活**：其他插件在首次被请求时激活

```
应用启动
  │
  ├─ 注册所有插件到PluginRegistry
  │
  ├─ 激活核心插件（无依赖的基础服务）
  │   ├─ @jupyterlab/application-extension:commands → CommandRegistry
  │   ├─ @jupyterlab/application-extension:shell → NotebookShell
  │   └─ @jupyterlab/apputils-extension:palette → ICommandPalette
  │
  ├─ 激活Notebook核心插件
  │   ├─ @jupyter-notebook/application-extension:router → IRouter
  │   ├─ @jupyter-notebook/application-extension:dirty → 脏检查
  │   ├─ @jupyter-notebook/tree-extension:widget → 文件浏览器
  │   └─ @jupyter-notebook/notebook-extension:plugin → Notebook widget工厂
  │
  └─ 激活第三方插件
      └─ 用户安装的所有labextension
```

## Notebook内置插件

Notebook v7 通过 `@jupyter-notebook/*` 命名空间注册了以下内置插件包（F-040）：

| 包名 | npm包名 | 职责 |
|------|---------|------|
| application | `@jupyter-notebook/application` | 核心：NotebookApp, NotebookShell, Token定义 |
| application-extension | `@jupyter-notebook/application-extension` | 主扩展：命令、路由、脏检查、Zen模式 |
| notebook-extension | `@jupyter-notebook/notebook-extension` | Notebook专属功能：Kernel Logo、信任状态、菜单覆盖 |
| tree-extension | `@jupyter-notebook/tree-extension` | 文件浏览器：文件操作、widget工厂 |
| tree | `@jupyter-notebook/tree` | Tree页面widget：NotebookTree组件 |
| terminal-extension | `@jupyter-notebook/terminal-extension` | 终端功能 |
| console-extension | `@jupyter-notebook/console-extension` | 控制台功能（草稿板） |
| docmanager-extension | `@jupyter-notebook/docmanager-extension` | 文档管理扩展 |
| documentsearch-extension | `@jupyter-notebook/documentsearch-extension` | 文档搜索 |
| help-extension | `@jupyter-notebook/help-extension` | 帮助菜单 |
| lab-extension | `@jupyter-notebook/lab-extension` | 接口切换器、启动树 |
| ui-components | `@jupyter-notebook/ui-components` | UI组件、图标 |
| _metapackage | `@jupyter-notebook/metapackage` | 元包：依赖聚合 |

## 核心命令系统

插件通过 `app.commands`（CommandRegistry）注册命令，命令是插件间交互的主要方式。

### 命令定义

```typescript
// application-extension中定义的命令（F-038）
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

### 注册命令

```typescript
app.commands.addCommand(CommandIDs.toggleZen, {
    label: 'Zen Mode',
    caption: 'Toggle Zen Mode',
    isToggled: () => shell.isZenMode,
    execute: () => {
        shell.toggleZen();
    }
});
```

### 添加到菜单/工具栏/命令面板

```typescript
// 添加到命令面板
palette.addItem({
    command: CommandIDs.toggleZen,
    category: 'Main Area'
});

// 添加到菜单
if (mainMenu) {
    mainMenu.viewMenu.addGroup([{ command: CommandIDs.toggleZen }]);
}
```

## 路由系统

Notebook前端使用 `IRouter` 服务处理URL路由。

### Tree路径正则

```typescript
const TREE_PATTERN = new RegExp('/(notebooks|edit)/(.*)');
```

> **信源**: [application-extension/src/index.ts:L76](../references/00-source-registry.md#S-009)（F-039）

这个正则匹配 `/notebooks/...` 和 `/edit/...` 路径，插件注册路由处理器来响应URL导航：

```typescript
router.register({
    pattern: TREE_PATTERN,
    rank: 100,
    command: CommandIDs.resolveTree
});
```

当用户导航到 `/notebooks/example.ipynb` 时，路由系统：
1. 匹配 `TREE_PATTERN`
2. 执行 `resolveTree` 命令
3. 命令解析路径，打开对应文件

## 添加Widget到Shell

插件最常见的操作是向Shell添加widget：

```typescript
import { INotebookShell } from '@jupyter-notebook/application';

const plugin: JupyterFrontEndPlugin<void> = {
    id: 'my-extension:plugin',
    autoStart: true,
    requires: [INotebookShell],
    activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
        // 创建widget
        const widget = new Widget();
        widget.id = 'my-widget';
        widget.title.label = 'My Panel';
        widget.title.icon = myIcon;
        widget.title.closable = true;

        // 添加到Shell
        shell.add(widget, 'left', { rank: 500 });
    }
};
```

## 与JupyterLab插件的兼容性

由于Notebook v7基于JupyterLab，**绝大多数JupyterLab插件可以直接在Notebook中使用**，无需修改。插件兼容性取决于：

### 完全兼容的插件

- 提供文档widget工厂（如新的文件类型渲染器）
- 添加命令菜单项
- 添加渲染MIME类型
- 提供通用服务（如翻译、设置）

### 可能需要适配的插件

- 直接操作JupyterLab Shell（`ILabShell`）而非NotebookShell
- 依赖JupyterLab特有的dock布局功能
- 硬编码了 `@jupyterlab/application:ILabShell` Token

对于需要适配的插件，可以通过检测Shell类型来提供不同行为：

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
    id: 'my-extension:plugin',
    optional: [ILabShell, INotebookShell],
    activate: (app, labShell, notebookShell) => {
        if (notebookShell) {
            // Notebook v7环境
            notebookShell.add(widget, 'left');
        } else if (labShell) {
            // JupyterLab环境
            labShell.add(widget, 'left');
        }
    }
};
```

## 插件发现与加载

### LabExtension路径

前端插件通过 `_jupyter_labextension_paths()` 发现：

```python
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "@jupyter-notebook/lab-extension"}]
```

> **信源**: [__init__.py:L19-20](../references/00-source-registry.md#S-003)（F-028）

安装后，pip将前端构建产物（JS bundle）放到Python包的 `labextension/` 目录，JupyterLab/Notebook在启动时扫描此目录加载插件。

### 第三方插件安装

```bash
# 安装JupyterLab/Notebook兼容的插件
pip install jupyterlab-git
jupyter labextension install @jupyter-widgets/jupyterlab-manager
# 或者直接用pip安装（prebuilt extensions）
pip install jupyterlab-code-formatter
```

Prebuilt extensions（JupyterLab 3.0+）不需要 `jupyter labextension install`，pip安装后自动可用。

## 插件开发最佳实践

1. **Token命名规范**: 使用 `@your-npm-package:IServiceName` 格式
2. **插件ID规范**: 使用 `@your-npm-package:function-name` 格式
3. **可选依赖**: 将非核心依赖放在 `optional` 中，增强兼容性
4. **不直接操作DOM**: 通过Lumino Widget系统管理UI
5. **异步激活**: 如果activate函数需要异步操作，返回Promise
6. **资源清理**: 在widget的 `dispose` 方法中清理事件监听和资源
7. **配置支持**: 通过 `ISettingRegistry` 提供用户可配置项

## 下一步

- → [实战：开发前端扩展](../examples/01-frontend-extension.md) 创建一个完整的侧边栏插件
- → [实战：自定义Shell布局](../examples/03-customize-shell.md) 通过插件修改Shell配置
