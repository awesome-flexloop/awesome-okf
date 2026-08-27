---
type: concept
title: "jupyterlab-myst 架构与插件系统"
description: "详解 jupyterlab-myst 的三插件架构、MySTContentFactory 单元格工厂、JupyterLab 扩展点机制以及与 JupyterLab 生命周期的集成"
tags: [jupyterlab-myst, jupyterlab, plugin, architecture, content-factory]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/plugin-entry-src.md"
    facts: [F-003, F-004, F-005, F-006, F-007]
---

# jupyterlab-myst 架构与插件系统

jupyterlab-myst 作为 JupyterLab 扩展，通过三个独立的 JupyterFrontEndPlugin 实现对 Markdown 单元格和 Markdown 文件的 MyST 增强。每个插件利用 JupyterLab 的不同扩展点，协同工作但互不耦合。

## 三个插件的职责

```
JupyterLab 启动
  │
  ├─ 1. content-factory 插件（ID: jupyterlab-myst:content-factory）
  │     提供 NotebookPanel.IContentFactory
  │     → 替换默认 MarkdownCell 为 MySTMarkdownCell
  │
  ├─ 2. executor 插件（ID: jupyterlab-myst:executor）
  │     监听 NotebookActions.executed 信号
  │     → 代码单元格执行后自动求值 inline expression
  │
  └─ 3. mime-renderer 插件（ID: jupyterlab-myst:mime-renderer）
        注册 text/markdown MIME 渲染工厂
        → Markdown Viewer 使用 MyST 渲染独立 .md 文件
```

## Plugin 1: Content Factory

### 扩展点

`NotebookPanel.IContentFactory` 是 JupyterLab 创建 Notebook 单元格时使用的工厂接口。通过提供自定义实现，扩展可以替换任何单元格类型的创建逻辑。

```ts
const plugin: JupyterFrontEndPlugin<NotebookPanel.IContentFactory> = {
  id: 'jupyterlab-myst:content-factory',
  provides: NotebookPanel.IContentFactory,
  requires: [IEditorServices],
  autoStart: true,
  activate: (app: JupyterFrontEnd, editorServices: IEditorServices) => {
    const editorFactory = editorServices.factoryService.newInlineEditor;
    return new MySTContentFactory({ editorFactory });
  }
};
```

### MySTContentFactory

MySTContentFactory 继承 JupyterLab 内置的 `NotebookPanel.ContentFactory`，只覆盖一个方法：`createMarkdownCell()`。当 Notebook 需要创建新的 Markdown 单元格时，此方法返回 MySTMarkdownCell 实例而非默认 MarkdownCell。

其他单元格类型（Code、Raw）仍然使用默认实现，不受影响。

这种替换策略的优点：
- 不需要 monkey-patching 任何 JupyterLab 内部类
- 遵循 JupyterLab 的标准扩展机制
- 不影响非 Markdown 单元格
- 与其他替换 ContentFactory 的扩展可能冲突（但这是 JupyterLab 架构限制，非 jupyterlab-myst 特有）

## Plugin 2: Executor

### 扩展点

`NotebookActions.executed` 是 JupyterLab 的全局信号（ISignal），在任何代码单元格执行完成后触发。jupyterlab-myst 连接此信号来触发 inline expression 的求值。

```ts
const executorPlugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-myst:executor',
  requires: [INotebookTracker],
  autoStart: true,
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    NotebookActions.executed.connect(async (sender, { notebook, cell }) => {
      await notebookCellExecuted(notebook, cell, tracker);
    });
  }
};
```

### 为什么需要 INotebookTracker？

信号回调只提供 notebook 和 cell 对象，但执行 inline expression 需要 SessionContext（获取内核连接）。SessionContext 属于 NotebookPanel（Notebook 的外壳 Widget），而非 Notebook 本身。INotebookTracker 用于从 notebook 反向查找对应的 NotebookPanel：

```ts
const panel = tracker.find((w: NotebookPanel) => w.content === notebook);
const ctx = panel?.sessionContext;
```

## Plugin 3: MIME Renderer

### 扩展点

`IRenderMimeRegistry` 是 JupyterLab 的 MIME 类型渲染注册表。通过 `addFactory()` 注册自定义渲染工厂，可以接管特定 MIME 类型的渲染。

```ts
const mimeRendererPlugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-myst:mime-renderer',
  requires: [IRenderMimeRegistry],
  autoStart: true,
  optional: [IMarkdownViewerTracker, ISettingRegistry],
  activate: (app, registry, tracker?, settingRegistry?) => {
    // 禁用 frontmatter 隐藏
    settingRegistry?.load('@jupyterlab/markdownviewer-extension:plugin')
      .then(settings => settings.set('hideFrontMatter', false));
    // 注册 MyST 渲染器
    registry.addFactory(mystMarkdownRendererFactory);
  }
};
```

### 工厂配置

```ts
const mystMarkdownRendererFactory = {
  safe: true,         // 标记为安全（不执行任意脚本）
  mimeTypes: ['text/markdown'],
  defaultRank: 50,    // 优先级，数值越高越优先
  createRenderer: options => new RenderedMySTMarkdown(options)
};
```

JupyterLab 内置 Markdown 渲染器的 rank 通常较低，设置 defaultRank=50 确保 MyST 渲染器优先使用。

### Optional 依赖解释

- **IMarkdownViewerTracker**：不直接使用，但作为 optional 依赖确保 JupyterLab 的 Markdown Viewer 插件先完成注册（否则 addFactory 的时机可能有问题）。
- **ISettingRegistry**：用于修改 Markdown Viewer 的设置（hideFrontMatter=false），让 YAML frontmatter 块可见。

## 插件间协作关系

三个插件虽然独立注册，但在运行时通过 JupyterLab 的服务系统协作：

```
content-factory 创建 MySTMarkdownCell
    ↓
MySTMarkdownCell 创建 MySTWidget（React 渲染器）
    ↓
MySTWidget 需要 IRenderMimeRegistry（用于 inline expression 输出渲染）
    ↓
mime-renderer 注册 RenderedMySTMarkdown（独立 .md 文件场景）
    ↓
executor 监听代码执行，调用 notebookCellExecuted
    ↓
notebookCellExecuted 更新 MySTMarkdownCell 的 expressions metadata
    ↓
metadata 变化触发 MySTWidget 重渲染，显示最新表达式结果
```

## autoStart: true 的含义

三个插件都设置 `autoStart: true`，意味着 JupyterLab 启动时自动激活，不需要用户手动启用。这确保了 MyST 渲染在所有 Notebook 和 Markdown 文件中默认可用。

## 与 JupyterLab 服务的依赖关系

| 服务 Token | 用途 | 插件 |
|---|---|---|
| IEditorServices | 获取 inline editor 工厂 | content-factory |
| INotebookTracker | 查找 NotebookPanel 获取 SessionContext | executor |
| IRenderMimeRegistry | 注册 MIME 渲染工厂，创建输出渲染器 | mime-renderer |
| IMarkdownViewerTracker | 确保 Markdown Viewer 先注册 | mime-renderer（optional） |
| ISettingRegistry | 修改 Markdown Viewer 设置 | mime-renderer（optional） |

## 相关概念

- [01-myst-rendering-pipeline.md](01-myst-rendering-pipeline.md)：MyST 解析和渲染管道
- [02-myst-markdown-cell.md](02-myst-markdown-cell.md)：MySTMarkdownCell 生命周期
- [03-inline-expressions.md](03-inline-expressions.md)：内联表达式执行机制
- [01-using-jupyterlab-myst.md](../examples/01-using-jupyterlab-myst.md)：安装和使用示例
