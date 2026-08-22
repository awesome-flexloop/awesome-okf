---
type: reference
title: "PDF 查看器源码（src/pdf.ts）"
description: "基于 pdfjs-dist 的 PDF 渲染组件，包含 PDFJSViewer 控件、PDFJSDocumentWidget、PDFJSViewerFactory、工具栏与页码控件"
tags: [pdf, pdfjs, viewer, widget, toolbar, zoom, navigation, b64toBlob]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pdf-ts
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/src/pdf.ts"
    title: "src/pdf.ts"
---

# PDF 查看器源码（src/pdf.ts）

本信源登记 `src/pdf.ts`（约658行），这是基于 pdfjs-dist 2.4.456 实现的 PDF 渲染查看器组件，提供 PDF 显示、缩放、翻页、下载、SyncTeX 点击定位等功能。

## 导出项

### PDFJSViewer 类

继承自 `Widget`，核心 PDF 渲染控件。

#### 构造函数

`constructor(context: DocumentRegistry.Context)`：
- 调用 `Private.createNode()` 创建 DOM 节点
- `Private.ensurePDFJS()` 异步加载 pdfjs-dist 库，初始化 `EventBus` 和 `PDFViewer`
- 监听 `context.pathChanged` 更新标题
- `context.ready` 后调用 `_render()`，监听 `contentChanged` 和 `fileChanged` 自动更新

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `context` | `DocumentRegistry.Context` | 文档上下文（只读） |
| `viewer` | `any \| undefined` | pdfjs-dist PDFViewer 实例 |
| `ready` | `Promise<void>` | 查看器就绪 Promise（通过 PromiseDelegate） |
| `position` | `IPosition`（getter） | 当前滚动位置（page, x=0, y=0） |
| `position` | setter | 设置滚动位置（page/x/y），含页码 clamp 和 y 坐标翻转 |
| `positionRequested` | `ISignal<this, IPosition>` | Shift+Ctrl/Cmd+Click 时发射位置信号 |

#### position setter 实现细节

- 页码 clamp 到 `[1, pagesCount+1]`
- y 坐标翻转：`yPos = yMax - (pos.y - MARGIN)`，MARGIN=72（1英寸边距）
- 调用 `viewer.scrollPageIntoView({pageNumber, destArray: [pageNumber, {name:'XYZ'}, x, yPos, scale]})`

#### 方法

| 方法 | 说明 |
|------|------|
| `dispose()` | 释放 ObjectURL，调用 super.dispose() |
| `fit()` | 设置 `currentScaleValue = 'page-width'` 适配宽度 |
| `handleEvent(event)` | 处理 click 事件 |
| `_render()` | 核心渲染：base64→Blob→ObjectURL→getDocument→setDocument，保留缩放和滚动位置 |
| `_handleClick(evt)` | Shift+Accel 点击时计算 PDF 坐标并发射 positionRequested 信号 |
| `_clientToPDFPosition(x,y)` | 屏幕坐标→PDF 坐标转换（遍历页面 textLayer，使用 viewport.convertToPdfPoint） |
| `_onTitleChanged()` | 标题设为文件名 |
| `onAfterAttach(msg)` | 添加 click 事件监听 |
| `onBeforeDetach(msg)` | 移除 click 事件监听 |
| `onUpdateRequest(msg)` | 调用 `_render()` 更新 |

#### 渲染流程（_render）

1. 等待 `_pdfjsLoaded`
2. 从 `context.model.toString()` 获取 base64 数据
3. `Private.b64toBlob()` 转为 Blob
4. 创建 ObjectURL，调用 `getDocument(url).promise`
5. `viewer.setDocument(pdfDocument)` 加载文档
6. 处理 pageLabels（非标准页码标签，如罗马数字）
7. `firstPagePromise` 后设置缩放、标记 `_hasRendered = true`
8. `pagesPromise` 后恢复滚动位置，清理旧文档和旧 URL

### PDFJSDocumentWidget 类

继承自 `DocumentWidget<PDFJSViewer>`：
- 构造函数中创建 `PDFJSViewer` 作为 content
- 通过 `Private.createToolbar(content)` 创建工具栏
- reveal 设为 `content.ready`

### PDFJSViewerFactory 类

继承自 `ABCWidgetFactory<IDocumentWidget<PDFJSViewer>, DocumentRegistry.IModel>`：
- `createNewWidget(context)` 返回 `new PDFJSDocumentWidget(context)`

### PDFJSViewer.IPosition 接口

| 字段 | 类型 | 说明 |
|------|------|------|
| `page` | `number` | PDF 页码（1-based） |
| `x` | `number` | x 坐标（pt，72dpi） |
| `y` | `number` | y 坐标（pt，72dpi） |

## 常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `MIME_TYPE` | `'application/pdf'` | PDF MIME 类型 |
| `PDF_CLASS` | `'pdfViewer'` | pdfjs-dist 内置 CSS 类 |
| `PDF_CONTAINER_CLASS` | `'jp-PDFJSContainer'` | JupyterLab PDF 容器 CSS 类 |
| `IS_MAC` | `!!navigator.platform.match(/Mac/i)` | 是否 Mac 平台 |
| `SCALE_DELTA` | `1.1` | 缩放步进因子 |
| `MAX_SCALE` | `10.0` | 最大缩放比例 |
| `MIN_SCALE` | `0.25` | 最小缩放比例 |
| `MARGIN` | `72` | 滚动边距（1英寸=72pt） |

## Private 命名空间

### createNode()

创建 DOM 结构：外层 `div.jp-PDFJSContainer` > 内层 `div.pdfViewer`，tabIndex=-1。

### createToolbar(content)

创建 PDF 工具栏，包含按钮：

| 按钮 | 图标 | 行为 |
|------|------|------|
| previous | previousIcon | currentPageNumber = max(current-1, 1) |
| next | nextIcon | currentPageNumber = min(current+1, pagesCount) |
| PageNumber | PageNumberWidget | 页码输入/显示控件 |
| spacer | - | 弹性空白 |
| zoomOut | zoomOutIcon | newScale = floor((current/1.1)*10)/10，不低于 MIN_SCALE |
| zoomIn | zoomInIcon | newScale = ceil((current*1.1)*10)/10，不高于 MAX_SCALE |
| fit | fitIcon | currentScaleValue = 'page-width' |
| download | downloadIcon | context.download() |

### b64toBlob(b64Data, contentType='', sliceSize=512)

base64 字符串转 Blob 对象：atob 解码→分块（512字节）→Uint8Array→Blob。

### ensurePDFJS()

异步加载 pdfjs-dist 资源：
- `import('pdfjs-dist/build/pdf.min.js')` → 提取 getDocument
- `import('pdfjs-dist/build/pdf.worker.entry')` → Worker 入口
- `import('pdfjs-dist/web/pdf_viewer')` → 提取 PDFViewer, EventBus
- `import('pdfjs-dist/web/pdf_viewer.css')` → 样式
- 返回 `{ getDocument, PDFViewer, EventBus }`

## 点击同步机制

- 触发条件：Shift+Accel 点击（Mac: Shift+Cmd, 其他: Shift+Ctrl）
- 坐标转换：屏幕坐标 → 遍历可见页面 textLayer → `ElementExt.hitTest` 命中检测 → `viewport.convertToPdfPoint()` 转换
- 信号发射：`positionRequested.emit({page, x, y})`
- 在 index.ts 中 `openPreview()` 的 `reverseSearch` 响应此信号
