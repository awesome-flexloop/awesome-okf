---
type: concept
title: "MySTMarkdownCell 生命周期"
description: "详解 MySTMarkdownCell 从创建、编辑、渲染到执行表达式的完整生命周期，以及 ActivityMonitor 防抖和 metadata 变更处理机制"
tags: [jupyterlab-myst, markdown-cell, lifecycle, activity-monitor, rendering]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/cell-widget-src.md"
    facts: [F-008, F-009, F-010, F-011, F-012, F-013, F-014]
  - path: "/references/parse-pipeline-src.md"
    facts: [F-027]
---

# MySTMarkdownCell 生命周期

MySTMarkdownCell 是 jupyterlab-myst 的核心 UI 组件，继承自 JupyterLab 的 MarkdownCell，通过一系列 HACK 覆写父类方法，实现了 MyST 渲染、inline expression 结果显示和任务列表交互。

## 创建阶段

### 构造函数执行顺序

```
new MySTMarkdownCell(options)
  │
  ├─ super(options) — 创建默认 MarkdownCell
  │   ├─ 创建 _renderer（默认 Markdown 渲染器）
  │   ├─ 创建 _monitor（ActivityMonitor，timeout=默认值）
  │   └─ 设置 _handleRendered（默认渲染回调）
  │
  ├─ 保存 _notebookRendermime（从 options.rendermime）
  ├─ 创建 _attachmentsResolver（AttachmentsResolver）
  ├─ 创建 _mystModel = new MySTModel()
  ├─ 创建 _mystWidget = new MySTWidget({...})
  ├─ 连接 taskItemChanged 信号 → setTaskItem()
  │
  ├─ HACK 1: 替换 _renderer
  │   this._renderer.dispose()
  │   this._renderer = rendermime.createRenderer('text/plain')
  │   （MyST 不使用默认 Markdown renderer，用 text/plain 占位）
  │
  ├─ HACK 2: 覆写 onTrustedChanged
  │   (this.model).onTrustedChanged = () => this.onModelTrustedChanged()
  │
  ├─ HACK 3: 重建 ActivityMonitor
  │   this._monitor.dispose()
  │   this._monitor = this.createActivityMonitor()  // timeout=100ms
  │
  ├─ HACK 4: 覆写 _handleRendered
  │   this._handleRendered = this.onRenderedChanged
  │
  └─ restoreExpressionsFromMetadata()
      └─ 从 cell metadata['user_expressions'] 恢复表达式结果
```

## 编辑模式 vs 渲染模式

MarkdownCell 有两种模式，通过 `rendered` 属性切换：

- **编辑模式**（rendered = false）：显示 CodeMirror 编辑器，用户编辑 Markdown 源码
- **渲染模式**（rendered = true）：显示渲染后的内容（MySTWidget）

### onRenderedChanged()

```ts
private async onRenderedChanged(): Promise<void> {
  if (!this.rendered) {
    this.showEditor();  // 切换到编辑模式
  } else {
    if (this.placeholder) {
      // 拖拽等占位状态：只更新 fragmentMDAST，不渲染
      await this.updateFragmentMDAST();
      return;
    }
    if (this.rendered) {
      await this.render();  // 执行完整渲染流程
    }
  }
}
```

用户在编辑模式下按 Shift+Enter 或双击渲染区域切换模式。

## 渲染流程（render()）

```ts
async render() {
  // 1. 解析本单元格的 Markdown
  await this.updateFragmentMDAST();
  //    ├─ markdownParse(source) → 基础 MDAST
  //    └─ processCellMDAST(resolver, mdast) → 图片 URL 转换
  //    └─ fragmentMDAST.type = 'block'

  if (!this._mystWidget.node || !this.isAttached) return;

  // 2. 全局聚合：处理整个 Notebook 的所有 MyST 单元格
  await renderNotebook(this.parent as StaticNotebook);
  //    ├─ buildNotebookMDAST(mystCells) → 拼接所有 fragment
  //    ├─ processNotebookMDAST(root, resolver) → 全局转换
  //    └─ 分片回传：每个 cell.mystModel.mdast = children[index]

  // 3. 等待 React 渲染完成
  await this._mystWidget.renderPromise;

  // 4. 将 MySTWidget 挂载到单元格输入区域
  this.inputArea.renderInput(this._mystWidget);
}
```

关键设计：**单个单元格的渲染触发全局重新聚合**。这确保了跨单元格引用（如"见图 2"）始终是最新的。renderNotebook 会更新所有已渲染的 MyST 单元格，不仅仅是当前单元格。

## 内容变更监听（ActivityMonitor）

### 为什么重建 ActivityMonitor？

默认 MarkdownCell 的 ActivityMonitor 有两个问题：
1. timeout 较长，导致双渲染（JupyterLab 默认渲染先触发，MyST 渲染后触发）
2. metadata 变化也会触发 contentChanged 信号，导致不必要的重渲染

### createActivityMonitor()

```ts
private createActivityMonitor() {
  const activityMonitor = new ActivityMonitor({
    signal: this.model.contentChanged,
    timeout: 100  // HACK: 更短的超时，让 Jupyter 先更新
  });

  this.ready.then(() => {
    activityMonitor.activityStopped.connect(() => {
      if (this.rendered && !this._metadataJustChanged) {
        this.update();  // 重新渲染
      }
      this._metadataJustChanged = false;
    }, this);
  });

  return activityMonitor;
}
```

### metadata 变更拦截

`_metadataJustChanged` 标志位的工作机制：

1. metadata 变化 → `onMetadataChanged()` 设置 `_metadataJustChanged = true`
2. contentChanged 信号触发 → ActivityMonitor 等待 100ms
3. activityStopped 触发 → 检查 `_metadataJustChanged`
4. 如果是 metadata-only 变更 → 跳过 update()
5. 如果是内容变更 → 执行 update()
6. 重置 `_metadataJustChanged = false`

这防止了 inline expression 结果写入 metadata 时触发无限渲染循环（写入 metadata → contentChanged → 重渲染 → 写入 metadata → ...）。

## Trust 变化处理

```ts
private onModelTrustedChanged() {
  this._mystWidget.trusted = this.model.trusted;
  this.restoreExpressionsFromMetadata();
}
```

当单元格被标记为受信任时：
1. 更新 MySTWidget 的 trusted 属性（UserExpressionsProvider 使用）
2. 从 metadata 恢复 expressions（In trusted 模式才渲染表达式结果）

不受信任的单元格不显示 inline expression 的执行结果（安全考虑：防止通过 MIME bundle 注入恶意 HTML/JS）。

## Metadata 变化处理

```ts
protected onMetadataChanged(model, args: IMapChange): void {
  this._metadataJustChanged = true;
  switch (args.key) {
    case 'user_expressions':
      this.restoreExpressionsFromMetadata();
      break;
    default:
      super.onMetadataChanged(model, args);
  }
}
```

- `user_expressions` key 变化 → 恢复表达式到 MySTModel（触发 React 重渲染）
- 其他 key → 委托父类处理

## 任务列表交互

```ts
private setTaskItem(_, change: ITaskItemChange): void {
  const text = this.model.sharedModel.getSource();
  const lines = text.split('\n');
  lines[change.line] = lines[change.line].replace(
    /^(\s*(?:-|\*)\s*)(\[[\s|x]\])/,
    change.checked ? '$1[x]' : '$1[ ]'
  );
  this.model.sharedModel.setSource(lines.join('\n'));
}
```

用户点击任务列表复选框时：
1. MySTWidget 通过 taskItemChanged 信号发送 {line, checked}
2. setTaskItem 使用正则替换对应行的 `[ ]` / `[x]`
3. 更新 sharedModel（Yjs 协作模型），触发内容变更
4. ActivityMonitor 防抖后触发重新渲染

使用 `sharedModel.setSource()` 而非直接修改 model.source，确保 Yjs 协作编辑下的多端同步。

## Fragment 模式（Placeholder）

当单元格处于 placeholder 状态（如拖拽过程中），onRenderedChanged 只调用 `updateFragmentMDAST()` 而不执行完整 render()。这确保即使单元格未完全渲染，其他单元格也能获得最新的 fragmentMDAST 用于跨单元格引用。

## 清理与销毁

MySTMarkdownCell 没有显式的 dispose 覆写。父类 MarkdownCell 的 dispose 会清理 _monitor 和 _renderer。MySTWidget 作为 Lumino Widget 在 inputArea 清理时自动 dispose。MySTModel 在 mystModel setter 中 dispose 旧模型。

## 相关概念

- [00-architecture-plugins.md](00-architecture-plugins.md)：插件架构
- [01-myst-rendering-pipeline.md](01-myst-rendering-pipeline.md)：解析渲染管道
- [03-inline-expressions.md](03-inline-expressions.md)：内联表达式执行
