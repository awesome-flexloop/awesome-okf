---
type: reference
title: "jupyterlab-myst 插件入口与架构源�?
description: "src/index.ts 三个插件定义、MySTContentFactory 工厂类、类型定义文�?
source_path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/index.ts"
key_exports:
  - plugin (jupyterlab-myst:content-factory)
  - executorPlugin (jupyterlab-myst:executor)
  - mimeRendererPlugin (jupyterlab-myst:mime-renderer)
  - MySTContentFactory
facts: [F-003, F-004, F-005, F-006, F-007]
tags: [jupyterlab-myst, reference]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/"
    facts: []
---

# jupyterlab-myst 插件入口与架�?
## 源码路径

- `src/index.ts`：三�?JupyterFrontEndPlugin 定义
- `src/MySTContentFactory.ts`：自定义 ContentFactory
- `src/types.ts`：IMySTMarkdownCell 等类型接�?
## 三个插件

### 1. content-factory 插件

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

提供 NotebookPanel.IContentFactory，JupyterLab 创建 Notebook 时使用此工厂创建 Markdown 单元格。MySTContentFactory 覆盖 `createMarkdownCell` 方法，返�?MySTMarkdownCell 实例�?
### 2. executor 插件

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

监听全局 NotebookActions.executed 信号，当任何代码单元格执行完成后触发 notebookCellExecuted 处理 Markdown 单元格中�?inline expression�?
### 3. mime-renderer 插件

```ts
const mimeRendererPlugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-myst:mime-renderer',
  requires: [IRenderMimeRegistry],
  autoStart: true,
  optional: [IMarkdownViewerTracker, ISettingRegistry],
  activate: (app, registry, tracker?, settingRegistry?) => {
    // 自动禁用 frontmatter 隐藏
    settingRegistry?.load('@jupyterlab/markdownviewer-extension:plugin')
      .then(settings => settings.set('hideFrontMatter', false));
    registry.addFactory(mystMarkdownRendererFactory);
  }
};
```

�?IRenderMimeRegistry 注册 text/markdown 渲染工厂。IMarkdownViewerTracker 作为 optional 依赖，确保内�?Markdown 渲染器先完成注册�?
## MySTContentFactory

MySTContentFactory 继承 NotebookPanel.ContentFactory，覆�?createMarkdownCell 方法返回 MySTMarkdownCell 实例而非默认 MarkdownCell。这�?JupyterLab 替换单元格类型的标准扩展点�?