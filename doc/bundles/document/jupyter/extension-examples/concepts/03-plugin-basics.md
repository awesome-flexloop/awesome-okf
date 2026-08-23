---
type: Concept
title: 插件基础与依赖注入
description: 理解JupyterLab的Token依赖注入系统，掌握requires/optional/provides声明和activate函数参数
tags: [jupyterlab, plugin, dependency-injection, token, requires, optional, provides]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: launcher-src
    resource: /references/core-api-tokens.md
    title: launcher/src/index.ts Token注入示例
  - id: widgets-src
    resource: /references/core-api-tokens.md
    title: widgets/src/index.ts requires注入示例
---

## 依赖注入核心思想

JupyterLab 使用 **Token 模式** 实现依赖注入（DI），这是从 Phosphor/Lumino 框架继承的设计模式：

- 每个核心服务（命令面板、Launcher、设置注册表等）都有一个对应的 `Token<T>` 对象
- 插件在 `requires`/`optional` 数组中声明需要哪些 Token
- JupyterLab 在激活插件时，按声明顺序将已初始化的服务实例传入 `activate` 函数
- 插件可以通过 `provides` 导出自己的 Token，供其他插件依赖

这避免了全局单例和硬编码依赖，实现了松耦合和可测试性。

## Token 基础

### 创建 Token

```typescript
import { Token } from '@lumino/coreutils';

// 创建一个唯一的Token，类型参数指定此Token代表的服务类型
export const IMyService = new Token<IMyService>('my-extension:IMyService');
```

- Token 的字符串参数是全局唯一标识符（通常用 `包名:接口名` 格式）
- Token 对象本身不包含实现，只是一个类型安全的标识符
- JupyterLab 核心服务的Token从对应npm包导入（如 `ICommandPalette` from `@jupyterlab/apputils`）

## requires：必需依赖

```typescript
import { ICommandPalette } from '@jupyterlab/apputils';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'command-palette',
  autoStart: true,
  requires: [ICommandPalette],  // 声明必需依赖
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    // palette 是 JupyterLab 注入的 ICommandPalette 实例
    palette.addItem({ command, category: 'Extension Examples' });
  }
};
```

关键规则：
- `requires` 中的Token必须可用，否则插件**不会被激活**
- activate函数参数顺序与requires数组顺序一致
- 第一个参数始终是 `JupyterFrontEnd` app实例
- widgets示例需要 `ICommandPalette` 才能将命令添加到面板

## optional：可选依赖

```typescript
import { ILauncher } from '@jupyterlab/launcher';

const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/launcher:plugin',
  autoStart: true,
  requires: [IFileBrowserFactory],
  optional: [ILauncher, ICommandPalette],  // 声明可选依赖
  activate: (
    app: JupyterFrontEnd,
    browserFactory: IFileBrowserFactory,
    launcher: ILauncher | null,      // 可能为null！
    palette: ICommandPalette | null  // 可能为null！
  ) => {
    // 使用launcher前必须检查null
    if (launcher) {
      launcher.add({ command, category: 'Extension Examples', rank: 1 });
    }
    if (palette) {
      palette.addItem({ command, args: { isPalette: true }, category });
    }
  }
};
```

关键规则：
- `optional` 中的Token如果不可用，传入 `null`
- 类型签名必须包含 `| null`
- 使用前必须进行null检查
- 典型场景：Launcher在某些环境（如JupyterLite精简模式）可能不存在

## provides：导出服务

```typescript
import { Token } from '@lumino/coreutils';
import { IWidgetTracker } from '@jupyterlab/apputils';

// 定义并导出Token供其他插件使用
export const IExampleDocTracker = new Token<IWidgetTracker<ExampleDocWidget>>(
  'exampleDocTracker'
);

const extension: JupyterFrontEndPlugin<IWidgetTracker<ExampleDocWidget>> = {
  id: 'documents',
  autoStart: true,
  requires: [ILayoutRestorer],
  optional: [ICollaborativeDrive],
  provides: IExampleDocTracker,  // 声明提供此Token
  activate: (app, restorer, drive) => {
    const tracker = new WidgetTracker<ExampleDocWidget>({ namespace: 'documents-example' });
    // ... 配置tracker
    return tracker;  // activate函数返回值即为其他插件注入的实例
  }
};
```

关键规则：
- `provides` 声明此插件提供哪个Token的实现
- `activate` 函数的返回值会被注册为该Token的实例
- 其他插件可以在 `requires`/`optional` 中使用此Token来获取tracker
- 泛型参数 `JupyterFrontEndPlugin<T>` 的T必须与provides的Token类型一致

## 依赖注入参数顺序

activate函数的参数严格按照以下顺序：

```
activate(app, ...requires, ...optional)
```

例如：
```typescript
requires: [A, B],
optional: [C, D],

activate: (app, a: A, b: B, c: C | null, d: D | null) => { ... }
```

launcher示例的参数对应关系：
```typescript
requires: [IFileBrowserFactory],        // → browserFactory
optional: [ILauncher, ICommandPalette], // → launcher, palette

activate: (app, browserFactory, launcher, palette)
```

## 双兼容模式：多插件导出

某些扩展需要同时支持JupyterLab和Jupyter Notebook v7+，通过导出多个插件实现：

```typescript
// JupyterLab专属插件（依赖ILabShell）
const pluginJupyterLab: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/clap-button:pluginLab',
  autoStart: true,
  requires: [ILabShell],  // 只在JupyterLab中存在
  activate: (app, labShell) => {
    const widget = new ClapWidget();
    app.shell.add(widget, 'top');  // 添加到顶部栏
  }
};

// Jupyter Notebook专属插件（依赖INotebookShell）
const pluginJupyterNotebook: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/clap-button:pluginNotebook',
  autoStart: true,
  requires: [INotebookShell],  // 只在Notebook v7中存在
  activate: (app, notebookShell) => {
    const widget = new ClapWidget();
    app.shell.add(widget, 'right');  // 添加到右侧栏
  }
};

// 导出插件数组
const plugins = [pluginJupyterLab, pluginJupyterNotebook];
export default plugins;
```

在JupyterLab中，`pluginJupyterNotebook` 因为 `requires: [INotebookShell]` 不满足而不激活；
在Notebook v7中，`pluginJupyterLab` 同理不激活。这样同一npm包自动适配两个前端。

另一种双兼容策略（shout-button-message示例）：只使用 `optional` 检测环境，不导出多插件：
```typescript
optional: [IStatusBar],  // 状态栏只在JupyterLab中存在
activate: (app, statusBar: IStatusBar | null) => {
  // 始终添加shout按钮
  // 如果statusBar存在（Lab环境），额外添加状态栏widget
  if (statusBar) { ... }
}
```

## 等待应用就绪

某些操作需要等JupyterLab完全恢复后才能执行：

```typescript
app.restored.then(() => {
  // 应用恢复完成，可以安全访问状态
  state.fetch(PLUGIN_ID).then(value => { ... });
});
```

settings示例展示了等待设置加载：
```typescript
Promise.all([app.restored, settings.load(PLUGIN_ID)])
  .then(([, setting]) => {
    // 设置加载完成，可以安全使用
  });
```

## 避免activate中的异步阻塞

server-extension示例有重要提示：

```typescript
activate: (app, palette, launcher) => {
  // 不要在activate中使用await！会延迟应用启动
  // 错误：await requestAPI<any>('hello')

  // 正确：使用.then()链式调用，不阻塞activate
  requestAPI<any>('hello')
    .then(data => console.log(data))
    .catch(reason => console.error(reason));
}
```

在activate函数中避免 `await` 长时间运行的操作（如网络请求），因为这会延迟JupyterLab的启动。使用 `.then()` 进行非阻塞调用。

## 核心Token速查

常用Token及所在包：

| Token | 包 | 用途 |
|-------|-----|------|
| `ICommandPalette` | @jupyterlab/apputils | 命令面板 |
| `ILauncher` | @jupyterlab/launcher | 启动器 |
| `IFileBrowserFactory` | @jupyterlab/filebrowser | 文件浏览器 |
| `ISettingRegistry` | @jupyterlab/settingregistry | 设置注册表 |
| `IStateDB` | @jupyterlab/statedb | 状态数据库 |
| `INotebookTracker` | @jupyterlab/notebook | Notebook追踪器 |
| `ILayoutRestorer` | @jupyterlab/application | 布局恢复 |
| `IRenderMimeRegistry` | @jupyterlab/rendermime | MIME渲染注册表 |
| `ITranslator` | @jupyterlab/translation | 国际化 |
| `ICompletionProviderManager` | @jupyterlab/completer | 补全管理器 |
| `ILoggerRegistry` | @jupyterlab/logconsole | 日志注册表 |
| `IEditorExtensionRegistry` | @jupyterlab/codemirror | CodeMirror扩展 |
| `IStatusBar` | @jupyterlab/statusbar（可选） | 状态栏 |
| `ILabShell` | @jupyterlab/application | Lab特有Shell |
| `INotebookShell` | @jupyter-notebook/application | Notebook特有Shell |
| `ICollaborativeDrive` | @jupyter/collaborative-drive | 协作驱动（可选） |

## 相关概念

- [Hello World：最小插件](/concepts/01-hello-world.md)
- [命令系统](/concepts/04-commands.md)
- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [核心API与Token参考](/references/core-api-tokens.md)
