---
type: Concept
title: "06 Notebook 与 Cell 架构"
description: "JupyterLab Notebook 的三层 Widget 结构、Cell 类型体系、NotebookModel 数据模型、代码执行流程与窗口化渲染机制"
tags: [jupyterlab, notebook, cell, widget, lumino, yjs, kernel, windowing]
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
---

Notebook 是 JupyterLab 的核心交互单元。一个 `.ipynb` 文件在前端被渲染为三层嵌套的 Widget 结构，每层承担不同职责：外层 `NotebookPanel` 负责文档外壳与会话管理，中层 `Notebook` 负责单元格列表的选择与键盘导航，底层 `Cell` 负责单个单元格的编辑与渲染。本文拆解这三层结构及其协作机制。

## 三层 Widget 结构

JupyterLab 的 Notebook UI 遵循 Lumino Widget 嵌套模式，从外到内分为三层：

```
NotebookPanel (DocumentWidget)
├── Toolbar (工具栏：保存/插入/运行/中断/重启)
└── Notebook (StaticNotebook → WindowedList)
    ├── Cell 0 (CodeCell / MarkdownCell / RawCell)
    ├── Cell 1
    └── Cell N
```

### NotebookPanel：外层面板

`NotebookPanel` 定义在 `packages/notebook/src/panel.ts:33`，继承自 `DocumentWidget<Notebook, INotebookModel>`。它是文档注册表（DocumentRegistry）创建的顶层 Widget，包含两个子区域：

- **工具栏**（`this.toolbar`）：CSS 类 `jp-NotebookPanel-toolbar`，承载保存、插入单元格、运行、中断内核、重启内核等按钮。
- **内容区**（`this.content`）：即 `Notebook` 实例，CSS 类 `jp-NotebookPanel-notebook`。

`NotebookPanel` 在构造时将 `context.model` 赋给 `this.content.model`（panel.ts:46），建立模型与视图的绑定。它还监听 `sessionContext.kernelChanged` 和 `statusChanged` 信号：当内核切换时，自动将 `language_info` 和 `kernelspec` 写入文档 metadata（panel.ts:191-243）；当内核自动重启时弹出提示对话框。`NotebookPanel` 还实现了打印符号 `[Printing.symbol]`，通过 nbconvert 将 Notebook 转为 HTML 后调用浏览器打印（panel.ts:151-166）。

### Notebook：单元格列表 Widget

`StaticNotebook` 定义在 `packages/notebook/src/widget.ts:206`，继承自 `WindowedList<NotebookViewModel>`。`Notebook` 类（widget.ts:1766）继承 `StaticNotebook`，增加了交互能力：

- **activeCellIndex**（widget.ts:1976）：当前活动单元格的索引，通过 setter 触发 `activeCellChanged` 和 `stateChanged` 信号。当列表为空时返回 -1。
- **activeCell**（widget.ts:2034）：当前活动单元格的 `Cell` Widget 实例。
- **mode**：`NotebookMode` 类型，取值 `'command'` 或 `'edit'`（widget.ts:175）。命令模式下键盘事件由 Notebook 处理（导航、快捷键），编辑模式下事件传递给 CodeMirror 编辑器。
- **selectionChanged** 信号：多选状态变化时触发。

`StaticNotebook` 持有 `rendermime`（MIME 渲染注册表）、`contentFactory`（Cell 工厂）、`editorConfig` 和 `notebookConfig` 配置对象。它通过 `modelChanged` 信号在模型切换时重建 Cell Widget 列表。

### Cell：单个单元格

`Cell<T extends ICellModel>` 定义在 `packages/cells/src/widget.ts:196`，继承 Lumino `Widget`。Cell 的 DOM 结构包含：

- `jp-Cell-header`：单元格头部（CellHeader）
- `jp-Cell-inputWrapper`：输入区包装，包含 `InputCollapser`、`InputArea`（CodeMirror 编辑器 + Prompt）
- `jp-Cell-outputWrapper`：输出区包装（仅 CodeCell），包含 `OutputCollapser` 和 `OutputArea`
- `jp-Cell-footer`：单元格尾部（CellFooter）

Cell 支持 `inputHidden`/`outputHidden` 折叠状态，并将折叠状态持久化到模型 metadata 的 `jupyter.source_hidden`/`jupyter.outputs_hidden` 字段（widget.ts:473-493）。Cell 还实现了 `inViewport` 信号，配合窗口化系统在单元格进入/离开视口时触发渲染或回收。

## Cell 类型体系

JupyterLab 支持三种 Cell 类型，均在 `packages/cells/src/widget.ts` 中定义：

### CodeCell（代码单元格）

`CodeCell` 继承 `Cell<ICodeCellModel>`（widget.ts:1091），是唯一可执行的 Cell 类型。它在构造时创建 `OutputArea` 实例（widget.ts:1117），用于渲染内核返回的输出结果。CodeCell 额外维护：

- **prompt**：执行计数提示符，如 `[1]`、`[*]`（运行中）、`[ ]`（未执行）。
- **outputArea**：`OutputArea` Widget，管理 `OutputAreaModel` 中的输出列表。
- **executionState** / **executionCount**：来自模型的执行状态和计数，驱动 Prompt 显示。

### MarkdownCell（Markdown 单元格）

`MarkdownCell` 继承 `AttachmentsCell<IMarkdownCellModel>`（widget.ts:2162），支持编辑/预览双模式。在编辑模式下显示 CodeMirror 编辑器，在渲染模式下通过 `rendermime` 将 Markdown 渲染为 HTML。它还支持标题折叠（`headingCollapsed`），点击标题旁的折叠按钮可隐藏该标题下的所有子单元格。MarkdownCell 管理附件（attachments），保存时自动清理未引用的附件（panel.ts:86-98）。

### RawCell（原始单元格）

`RawCell` 继承 `Cell<IRawCellModel>`（widget.ts:2688），不经过任何渲染器，直接显示原始文本。RawCell 通常用于 nbconvert 导出时需要原样保留的内容（如 LaTeX 原文）。

## NotebookModel 与 sharedModel

`NotebookModel` 定义在 `packages/notebook/src/model.ts:99`，实现 `INotebookModel` 接口。其核心数据结构包括：

- **cells: CellList**（model.ts:157）：可观察的单元格模型列表，基于 `IObservableList`，在增删改时发出 `changed` 信号。
- **sharedModel: ISharedNotebook**（model.ts:68）：底层 Yjs CRDT 文档，默认由 `YNotebook.create()` 创建（model.ts:109）。它存储单元格内容、metadata、nbformat 版本号，是实时协作的数据基础。
- **metadata**（model.ts:199）：Notebook 级元数据的副本，提供 `getMetadata`/`setMetadata`/`deleteMetadata` 方法。
- **nbformat / nbformatMinor**：Notebook 格式版本号，来自 sharedModel。
- **deletedCells: string[]**：自上次运行以来删除的单元格 ID 列表。
- **dirty / readOnly**：文档脏标记和只读状态，dirty 委托给 sharedModel。

`NotebookModel` 构造时连接 `_cells.changed`、`sharedModel.changed` 和 `sharedModel.metadataChanged` 三个信号，将底层 Yjs 文档变化转发为 Lumino 信号，供 Widget 层响应。模型支持 `standaloneModel` 标志——当外部传入 sharedModel 时为 false（协作场景），否则为 true（独立文档）。

## 代码执行流程

CodeCell 的执行是 Notebook 最核心的交互链路，涉及前端、Kernel 服务和输出渲染三层：

1. **触发**：用户点击运行按钮或按 `Shift+Enter`，调用 `NotebookActions.runAndAdvance`（actions.tsx:814）或 `NotebookActions.run`（actions.tsx:737）。
2. **委托执行器**：`runCell` 内部函数（actions.tsx:3050）将执行请求封装为 `INotebookCellExecutor.IRunCellOptions`，调用可插拔的 `executor.runCell()`；未设置 executor 时回退到 `defaultRunCell`。
3. **Kernel 请求**：默认执行器通过 `sessionContext.session.kernel.requestExecute()` 向 Kernel 发送 `execute_request` 消息，携带代码内容和 `store_history` 标志。
4. **IOPub 消息流**：Kernel 通过 IOPub 通道回发状态消息：`status: busy` → `execute_input` → 多个 `stream`/`display_data`/`execute_result`/`error` 消息 → `status: idle`。
5. **输出追加**：`@jupyterlab/services` 的 Future 对象将每条 IOPub 消息转为 `IObservableList` 变更，CodeCell 的 `OutputAreaModel` 追加输出项。
6. **渲染更新**：`OutputArea` Widget 监听 model 变化，通过 `rendermime` 注册表为每种 MIME 类型选择渲染器，将输出渲染为 DOM 节点。
7. **执行计数**：收到 `execute_input` 消息时更新 `executionCount`，Prompt 从 `[*]` 变为 `[N]`。

## 窗口化渲染

对于包含数百甚至数千个 Cell 的大型 Notebook，JupyterLab 采用窗口化（windowing）技术避免一次性渲染所有 Cell。核心实现在 `packages/notebook/src/windowing.ts`：

- **NotebookViewModel**（windowing.ts:136）：继承 `WindowedListModel`，估算每个 Cell 的高度（基于编辑器行数和输出行数），为虚拟滚动条提供位置计算。
- **NotebookWindowedLayout**：自定义布局，只将视口内（含 overscan 区域）的 Cell 挂载到 DOM，视口外的 Cell 被 `Widget.detach` 移除但保留实例。
- **IntersectionObserver**（windowing.ts:49-51）：子类化 IntersectionObserver，在 Notebook 滚动时暂停回调以避免性能抖动，精确检测 Cell 进入/离开视口。
- **content-visibility CSS**：另一种窗口化模式（`contentVisibility`），利用浏览器原生 CSS `content-visibility: auto` 跳过离屏 Cell 的渲染，比 `full` 模式更轻量。
- **ScrollbarItem**（widget.ts:1565）：虚拟滚动条上的迷你条目，显示 Cell 类型、执行计数和脏标记，帮助用户在长 Notebook 中定位。

窗口化模式由 `notebookConfig.windowingMode` 控制，可选 `'full'`、`'defer'`、`'contentVisibility'`。NotebookPanel 在 `onBeforeHide`/`onBeforeShow` 中设置 `content.isParentHidden`（panel.ts:171-186），通知窗口化列表在 Notebook 隐藏时暂停观察。

## Cell 工具栏扩展点

`@jupyterlab/cell-toolbar` 包提供了 Cell 级别的工具栏扩展点。`CellToolbarTracker`（celltoolbartracker.ts:53）为每个 Notebook 创建追踪器，在活动 Cell 旁显示浮动工具栏。扩展开发者可通过注册 Widget 扩展向工具栏添加按钮——`CellToolbarTracker` 本身作为一个 Widget Extension，在 Notebook 创建时自动实例化（celltoolbartracker.ts:523）。这使得第三方扩展可以为特定类型的 Cell（如代码单元格）添加上下文操作按钮，而无需修改核心代码。

## NotebookActions：常用操作的静态封装

`NotebookActions` 是一个命名空间（actions.tsx:146），以静态函数形式封装了 Notebook 的所有常用操作，命令系统和 UI 按钮都委托给它：

| 分类 | 方法 |
|------|------|
| 执行 | `run`、`runCells`、`runAndAdvance`、`runAndInsert`、`runAll`、`runAllAbove`、`runAllBelow`、`runSelected` |
| 编辑 | `deleteCells`、`insertAbove`、`insertBelow`、`splitCell`、`mergeCells`、`changeCellType` |
| 移动 | `moveUp`、`moveDown`、`moveCells` |
| 剪贴板 | `copy`、`paste`、`copyOrCut`、`copyToSystemClipboard`、`pasteFromSystemClipboard` |
| 选择/历史 | `selectAll`、`undo`、`redo` |

这些函数均接收 `Notebook` 实例作为第一个参数，操作其 model 和 activeCellIndex。例如 `deleteCells`（actions.tsx:501）从 model 中移除选中的 Cell 并调整 activeCellIndex；`changeCellType`（actions.tsx:708）将 Cell 在 code/markdown/raw 之间转换，保留源文本内容。

## 相关概念

- [05 文档注册与 Widget 工厂](05-document-widget-system.md)
- [07 扩展生态系统](07-extension-ecosystem.md)
- [04 服务层与后端通信](04-service-layer.md)
- [08 构建系统与运行模式](08-build-and-modes.md)
