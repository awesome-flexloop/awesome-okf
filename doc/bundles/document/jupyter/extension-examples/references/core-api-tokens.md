---
type: Reference
title: JupyterLab 核心 API 与扩展点
description: JupyterLab 扩展开发中常用的核心 Token、服务和扩展点 API 速查
tags: [jupyterlab, api, tokens, extension-points, services]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: app-token
    resource: /references/core-api-tokens.md
    title: "@jupyterlab/application JupyterFrontEnd"
  - id: apputils-tokens
    resource: /references/core-api-tokens.md
    title: "@jupyterlab/apputils 核心服务Token"
  - id: services-tokens
    resource: /references/core-api-tokens.md
    title: "@jupyterlab/services 服务层API"
---

## 核心 Token（依赖注入标识）

所有 Token 从对应 npm 包导入，在 `requires`/`optional` 中声明后由 JupyterLab 注入到 `activate` 函数。

### 应用基础（@jupyterlab/application）

| Token | 类型 | 说明 |
|-------|------|------|
| `JupyterFrontEnd` | 类（非Token） | 应用实例，通过 activate 第一个参数获取 |
| `JupyterFrontEndPlugin<T>` | 类型 | 插件定义类型 |
| `ILayoutRestorer` | Token | 布局恢复服务，恢复用户之前打开的 widgets |

### UI 组件（@jupyterlab/apputils）

| Token | 说明 | 典型用途 |
|-------|------|---------|
| `ICommandPalette` | 命令面板 | `palette.addItem({ command, category })` 注册命令到面板 |
| `MainAreaWidget<T>` | 主区域Widget包装器 | 包装自定义内容Widget，提供工具栏支持 |
| `WidgetTracker<T>` | Widget追踪器 | 追踪打开的widget实例，配合ILayoutRestorer |
| `CommandToolbarButton` | 工具栏按钮组件 | 在工具栏添加命令按钮 |
| `Dialog` / `showDialog()` | 对话框 | 显示模态对话框 |
| `InputDialog` | 输入对话框 | 获取用户输入（getItem/getText/getNumber） |
| `Notification` | 通知系统 | `Notification.success/error/promise/info/warning` |
| `IFrame` | IFrame Widget | 嵌入网页内容 |
| `SessionContext` | 会话上下文 | 管理kernel会话连接 |
| `SessionContextDialogs` | 会话对话框 | kernel选择对话框 |

### 启动器（@jupyterlab/launcher）

| Token | 说明 |
|-------|------|
| `ILauncher` | 启动器卡片注册，`launcher.add({ command, category, rank })` |

### 文件浏览器（@jupyterlab/filebrowser）

| Token | 说明 |
|-------|------|
| `IFileBrowserFactory` | 文件浏览器工厂，`factory.tracker.currentWidget` 获取当前文件 |

### 设置（@jupyterlab/settingregistry）

| Token | 说明 |
|-------|------|
| `ISettingRegistry` | 设置注册表，`settings.load(PLUGIN_ID)` 加载设置，`setting.set(key, value)` 写入 |

### 状态（@jupyterlab/statedb）

| Token | 说明 |
|-------|------|
| `IStateDB` | 状态数据库，`state.fetch(id)` 读取，`state.save(id, value)` 持久化 |

### Notebook（@jupyterlab/notebook）

| Token | 说明 |
|-------|------|
| `INotebookTracker` | Notebook追踪器，`tracker.activeCell` 获取当前活动cell |

### 补全（@jupyterlab/completer）

| Token | 说明 |
|-------|------|
| `ICompletionProviderManager` | 补全提供者管理器，`registerProvider()` 注册自定义补全 |

### 日志控制台（@jupyterlab/logconsole）

| Token/类 | 说明 |
|----------|------|
| `ILoggerRegistry` | 日志记录器注册表，`getLogger(path)` 获取logger |
| `LoggerRegistry` | 日志注册表构造器，需传入 `defaultRendermime` 和 `maxLength` |
| `LogConsolePanel` | 日志面板Widget |
| `IHtmlLog` / `ITextLog` / `IOutputLog` | 日志消息类型 |

### CodeMirror（@jupyterlab/codemirror）

| Token | 说明 |
|-------|------|
| `IEditorExtensionRegistry` | 编辑器扩展注册表，`addExtension()` 注册CodeMirror扩展 |
| `EditorExtensionRegistry` | 包含 `createConfigurableExtension()` 工厂方法 |

### 渲染MIME（@jupyterlab/rendermime-interfaces）

| 接口 | 说明 |
|------|------|
| `IRenderMime.IExtension` | MIME渲染器插件定义 |
| `IRenderMime.IRenderer` | 渲染器接口，需实现 `renderModel(model)` |
| `IRenderMime.IRendererFactory` | 渲染器工厂，含 `safe`/`mimeTypes`/`createRenderer` |

### UI组件（@jupyterlab/ui-components）

| Token/类 | 说明 |
|----------|------|
| `LabIcon` | 自定义图标，`new LabIcon({ name, svgstr })` |
| `IFormRendererRegistry` | 表单渲染器注册表 |
| 内置图标 | `reactIcon`, `runIcon`, `markdownIcon`, `buildIcon`, `addIcon`, `clearIcon`, `listIcon` |

### 翻译（@jupyterlab/translation）

| Token | 说明 |
|-------|------|
| `ITranslator` | 翻译服务，`translator.load('jupyterlab')` 获取翻译bundle |
| `nullTranslator` | 空翻译器（默认fallback） |

### 服务层（@jupyterlab/services）

| 类/接口 | 说明 |
|---------|------|
| `ServiceManager` | 服务管理器，包含sessions/kernelspecs等 |
| `ServerConnection` | 服务器连接，`makeSettings()` / `makeRequest()` 调用后端API |
| `KernelMessage` | Kernel消息类型定义 |
| `Kernel.IFuture` | Kernel执行future对象 |

### 核心工具（@jupyterlab/coreutils）

| 类/函数 | 说明 |
|---------|------|
| `PageConfig.getBaseUrl()` | 获取Jupyter服务器base URL |
| `URLExt.join()` | URL路径拼接 |

### Lumino 基础库

| 包 | 核心类 | 说明 |
|----|--------|------|
| `@lumino/widgets` | `Widget` | 基础Widget，生命周期方法onAfterAttach/onBeforeDetach |
| `@lumino/widgets` | `StackedPanel` | 堆叠面板 |
| `@lumino/messaging` | `Message` | 消息系统 |
| `@lumino/signaling` | `Signal<T, U>` | 信号系统，`.connect()` / `.emit()` |
| `@lumino/coreutils` | `Token<T>` | DI Token创建 `new Token<T>('unique-id')` |
| `@lumino/coreutils` | `PromiseDelegate<T>` | Promise委托模式 |
| `@lumino/datagrid` | `DataGrid` / `DataModel` | 高性能数据表格 |

### 文档系统（@jupyterlab/docregistry）

| 类/接口 | 说明 |
|---------|------|
| `DocumentRegistry` | 文档注册表，`addFileType/addModelFactory/addWidgetFactory` |
| `ABCWidgetFactory<T, U>` | Widget工厂基类，实现 `createNewWidget(context)` |
| `DocumentWidget<T, U>` | 文档Widget基类 |
| `DocumentRegistry.IContext<T>` | 文档上下文，包含 `model`/`path`/`ready`/`pathChanged` |
| `DocumentRegistry.IModel` | 文档模型接口（dirty/readOnly/toString/fromString） |

## JupyterFrontEnd 实例属性

通过 `activate(app: JupyterFrontEnd)` 获得的 `app` 对象：

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `app.commands` | `CommandRegistry` | 命令注册表 |
| `app.shell` | `ILabShell` / `JupyterFrontEnd.IShell` | 布局shell |
| `app.serviceManager` | `ServiceManager.IManager` | 服务管理器 |
| `app.docRegistry` | `DocumentRegistry` | 文档注册表 |
| `app.restored` | `Promise<void>` | 应用恢复完成Promise |
| `app.commands.addCommand()` | 方法 | 注册命令 |
| `app.commands.execute()` | 方法 | 执行命令 |
| `app.shell.add(widget, area)` | 方法 | 添加widget到指定区域 |

## Shell 布局区域

| 区域名 | 常量/字符串 | 说明 |
|--------|------------|------|
| 主工作区 | `'main'` | 主要内容区域（notebook/editor打开于此） |
| 顶部栏 | `'top'` | 顶部区域（toparea-text-widget示例） |
| 左侧栏 | `'left'` | 左侧边栏 |
| 右侧栏 | `'right'` | 右侧边栏 |
| 底部栏 | `'bottom'` | 底部区域 |
| 头部 | `'header'` | 页眉 |

## commands.addCommand 选项

```typescript
commands.addCommand(commandId, {
  label: string | (args) => string,    // 显示名称
  caption: string,                      // 提示文本
  icon?: LabIcon | (args) => LabIcon,  // 图标
  execute: (args) => any,              // 执行函数
  isVisible?: () => boolean,           // 可见性（动态）
  isEnabled?: () => boolean,           // 启用状态（动态）
  isToggled?: () => boolean,           // 切换状态
});
```

## 相关概念

- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [命令系统](/concepts/04-commands.md)
- [Widget与Shell布局](/concepts/05-widgets-shell.md)
