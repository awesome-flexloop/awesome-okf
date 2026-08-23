---
type: concept
title: "PDF 查看器"
description: "基于 pdfjs-dist 的 PDF 渲染控件 PDFJSViewer 的设计，包括渲染管线、缩放翻页、工具栏、PDFJSViewerFactory 文档工厂注册，以及 PDF 数据流转"
tags: [pdf, pdfjs, viewer, rendering, zoom, toolbar, document-factory, base64-model]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pdf-ts
    resource: "/references/pdf-ts-source.md"
    title: "PDF查看器源码"
  - id: pagenumber-tsx
    resource: "/references/pagenumber-tsx-source.md"
    title: "页码控件源码"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
---

# PDF 查看器

jupyterlab-latex 的 PDF 预览功能基于 Mozilla 的 **pdfjs-dist** 库（v2.4.456，作为 JupyterLab 单例依赖共享），通过自定义的 `PDFJSViewer` 控件封装渲染逻辑，使用 `PDFJSViewerFactory` 注册为 JupyterLab 文档工厂，使 `.pdf` 文件能以内置查看器打开。

## PDFJSViewer 类层次

```
Widget (Lumino)
  └─ MainAreaWidget
       └─ PDFJSViewer          ← PDF 渲染核心控件
            ├─ _viewer: HTMLDivElement  (pdfjs iframe容器)
            ├─ _toolbar: Toolbar        (缩放/翻页/页码)
            ├─ _renderTask: RenderTask  (当前渲染任务)
            ├─ _pdfDocument: PDFDocumentProxy (PDF文档对象)
            ├─ _page: PDFPageProxy      (当前页面对象)
            ├─ _scrollTop/_scrollLeft   (滚动位置)
            └─ eventBus: EventBus       (pdfjs事件总线)

PDFJSDocumentWidget extends MainAreaWidget<PDFJSViewer>
  └─ 包装 PDFJSViewer 为文档 widget，关联 context/model

Widget (Lumino)
  └─ ReactWidget
       └─ PageNumberWidget  ← 页码输入 React 组件
            └─ PageNumberComponent (React.Component)

ABCWidgetFactory<PDFJSDocumentWidget, DocumentRegistry.IModel>
  └─ PDFJSViewerFactory     ← 文档工厂，创建 PDFJSDocumentWidget
```

## 数据流转：从 base64 到可见 PDF

PDF 数据从磁盘到屏幕的完整路径：

```
Jupyter Contents Manager
    │  model='base64', 读取 .pdf 文件为 base64 字符串
    ▼
DocumentModel (base64 编码的 PDF 数据)
    │  model.contentChanged 信号触发
    ▼
PDFJSViewer._render()
    │
    ├─ 从 context 取出 base64 字符串
    ├─ base64ToBlob() → Blob (application/pdf)
    │    └─ 将 base64 每 512 字符分块解码（防止栈溢出）
    ├─ URL.createObjectURL(blob) → blob: URL
    ├─ viewer.src = blob URL  (设置 iframe src)
    │
    ▼
iframe 加载 pdfjs viewer.html
    │  使用 CDN 加载的 pdfjs-dist
    │  通过 postMessage 与主页面通信
    ▼
PDF 页面渲染到 canvas
```

### base64 解码为 Blob

`PDFJSViewer.base64ToBlob()` 方法处理 PDF 的二进制数据：

```typescript
static base64ToBlob(b64Data, contentType='', sliceSize=512) {
    b64Data = b64Data.replace(/\s/g, '');  // 去除空白
    const byteCharacters = atob(b64Data);  // base64 → 二进制字符串
    // 每 sliceSize 字节分块，避免 atob 结果过长导致栈溢出
    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        byteArrays.push(new Uint8Array(byteNumbers));
    }
    return new Blob(byteArrays, { type: contentType });
}
```

分块解码是因为大 PDF 文件（>1MB）的 base64 字符串可能在 `atob` 后产生超长字符串，直接转换可能导致 JavaScript 调用栈溢出。

## 渲染管线 _render()

`_render()` 是 PDFJSViewer 的核心方法，在以下时机被调用：

| 时机 | 触发源 |
|------|--------|
| Widget 首次挂载 | `onAfterAttach()` → `_ready.fulfill()` → `context.ready.then(_render)` |
| 文件内容变化 | `context.model.contentChanged` 信号（编译完成后 PDF 更新） |
| 手动刷新 | 外部调用 `_render()`（编译成功后） |

渲染步骤：

```typescript
private _render(): void {
    if (this._renderTask) {
        this._renderTask.cancel();  // 取消正在进行的渲染
    }
    // 1. 获取 base64 PDF 数据
    if ((this.context.model as DocumentRegistry.IModel).toString().length == 0) {
        return;  // 空内容，跳过
    }
    const pdfData = (this.context.model as DocumentRegistry.IModel).toString();
    
    // 2. 创建 blob URL（注意：旧 URL 需要回收避免内存泄漏）
    const blob = Private.b64toBlob(pdfData, 'application/pdf');
    const oldUrl = Private.blobUrls.get(this._discoverCurrentPath());
    if (oldUrl) URL.revokeObjectURL(oldUrl);
    const blobUrl = URL.createObjectURL(blob);
    Private.blobUrls.set(path, blobUrl);
    
    // 3. 设置 iframe src
    this._viewer.src = blobUrl;
    
    // 4. 渲染完成后恢复位置
    this._eventBus.on('pagesloaded', () => {
        if (this._scrollTop != 0) this._viewer.contentWindow.scrollTo(0, this._scrollTop);
        // zoom 恢复逻辑...
    });
}
```

### 位置保持

每次重新渲染（编译后 PDF 更新）时，扩展会保留用户的浏览位置：

- **滚动位置**：`_viewerPageChanged()` 监听 `pagechanging` 事件记录 scrollTop
- **缩放比例**：`_setScale()` 记录 `currentScaleValue`，渲染后通过 eventBus 的 `scalechanging` 事件恢复
- **页码**：通过 `_currentPageNumber` 记录，渲染完成后跳转

## 工具栏

PDF 查看器顶部有一个精简工具栏（比 pdfjs web viewer 默认工具栏少很多按钮），按钮在 `Private.createToolbar()` 中定义：

| 按钮 | 图标 | Command | 功能 |
|------|------|---------|------|
| Previous Page | `previousIcon` | `previous-page` | 翻到上一页 |
| Next Page | `nextIcon` | `next-page` | 翻到下一页 |
| Page Number | — | — | 页码输入框（React 组件） |
| Zoom Out | `zoomOutIcon` | `zoom-out` | 缩小 |
| Zoom In | `zoomInIcon` | `zoom-in` | 放大 |
| Zoom to Fit | `zoomFitIcon` | `zoom-initial`（page-fit） | 适应窗口 |

### 缩放预设

`ZOOM_VALUES` 定义了可用的缩放级别：
```typescript
Private.ZOOM_VALUES = [
    'auto', 'page-actual', 'page-fit', 'page-width',
    '0.5', '0.75', '1', '1.25', '1.5', '2', '3', '4'
];
```
- 预设值：`auto`, `page-actual`（实际大小）, `page-fit`（适应窗口）, `page-width`（适应宽度）
- 数值缩放：50%, 75%, 100%, 125%, 150%, 200%, 300%, 400%

### 页码导航

页码控件由独立的 React 组件 `PageNumberWidget` 提供，位于工具栏 Previous/Next 和 Zoom 之间：
- 显示格式：`"当前页 / 总页数"` 或 `"标签 (N of M)"`
- 支持直接输入页码后按 Enter 跳转
- 支持罗马数字等自定义页码标签（通过 `pagelabels` 事件获取）

## PDFJSViewerFactory 文档工厂

`PDFJSViewerFactory` 继承自 `ABCWidgetFactory`，注册到 JupyterLab 文档注册表：

```typescript
const factory = new PDFJSViewerFactory({
    name: 'PDFJS',
    modelName: 'base64',       // 使用 base64 模型读取二进制 PDF
    fileTypes: ['PDF'],         // 关联 .pdf 文件类型
    defaultFor: ['PDF'],        // 作为 PDF 默认打开方式
    readOnly: true,             // PDF 不可编辑
    toolbarFactory: () => Private.createToolbar(commands),
    ...
});
```

### 工厂选项

| 属性 | 值 | 含义 |
|------|-----|------|
| `name` | `'PDFJS'` | 工厂名称，用于 `commands.docRegistry:open-widget` 调用 |
| `modelName` | `'base64'` | 使用 base64 编码模型读取文件内容 |
| `fileTypes` | `['PDF']` | 关联 PDF 文件类型 |
| `defaultFor` | `['PDF']` | 双击 .pdf 文件时默认使用此工厂 |
| `readOnly` | `true` | PDF 查看器为只读 |
| `preferKernel` | `false` | 不关联内核 |
| `canStartKernel` | `false` | 不启动内核 |
| `shutdownOnClose` | `false` | 关闭不关闭内核（无内核） |
| `toolbarFactory` | `createToolbar` | 自定义工具栏工厂 |

### 创建新 Widget

`createNewWidget(context)` 创建 PDFJSDocumentWidget 时：
- 创建 `PDFJSViewer` 实例，传入 context
- 设置 `content.title.label = basename(context.path)`
- 设置 `content.title.icon = pdfIcon`（LaTeX 文件类型图标）
- 返回 `new PDFJSDocumentWidget({ content, context })`

## 点击定位（反向 SyncTeX）

PDFJSViewer 监听 iframe 的 `mousedown` 事件：

```typescript
this._viewer.onload = () => {
    this._viewer.contentWindow.addEventListener('mousedown', (event: MouseEvent) => {
        if (event.shiftKey && event.ctrlKey || event.shiftKey && event.metaKey) {
            event.preventDefault();
            this._handleClick(event);
        }
    });
};
```

点击位置转换为 PDF 坐标后，通过 `positionRequested` 信号发送：

```typescript
this._positionRequested.emit({
    x: pageX,    // 72dpi 单位
    y: pageY,
    page: page,
    path: path
});
```

坐标转换细节：
- 获取点击元素的 `data-page-number` 属性确定页码
- 从 `data-loaded` div 获取缩放后的页面宽高（`clientWidth`/`clientHeight`）
- 点击位置相对于页面 div 的 offsetX/offsetY 除以缩放比例，乘以 CSS_UNITS（96/72）转换为 PDF 72dpi 坐标
- y 轴翻转：`(divHeight / zoom) * CSS_UNITS - pageY`（因为 PDF 坐标系 y 轴从底部向上）

## Blob URL 内存管理

由于每次渲染都创建新的 `blob:` URL，需要及时回收旧 URL 防止内存泄漏：

```typescript
// 存储路径→blobUrl 映射
const oldUrl = Private.blobUrls.get(path);
if (oldUrl) URL.revokeObjectURL(oldUrl);
const blobUrl = URL.createObjectURL(blob);
Private.blobUrls.set(path, blobUrl);
```

Widget 销毁时也应该清理对应 blob URL（在 `dispose` 方法中通过 `content.disposed` 信号处理）。

## 与 pdfjs web viewer 的差异

jupyterlab-latex 的 PDF 查看器相比 Mozilla 官方 PDF.js Web Viewer 做了裁剪：

| 功能 | pdfjs web viewer | jupyterlab-latex |
|------|-----------------|------------------|
| 侧边栏（书签/缩略图/附件） | ✅ | ❌ |
| 搜索 | ✅ | ❌ |
| 旋转 | ✅ | ❌ |
| 打印/下载 | ✅ | ❌（通过 JupyterLab 文件菜单） |
| 演示模式 | ✅ | ❌ |
| 工具栏 | 完整 | 精简（翻页+缩放+页码） |
| SyncTeX 反向点击 | ❌ | ✅ |

这种精简设计是有意为之——PDF 预览是 LaTeX 编辑的辅助功能，而非完整 PDF 阅读器。

---

**下一步阅读：**
- [SyncTeX 双向同步](05-synctex-sync.md) — 编辑器与 PDF 之间的精确跳转
- [编辑工具栏与快捷操作](06-editing-tools.md) — LaTeX 编辑器中的工具栏按钮与插入功能
