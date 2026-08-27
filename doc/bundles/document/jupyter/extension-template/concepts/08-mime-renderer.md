---
type: Concept
title: MIME 渲染器开发
description: 理解 IRenderMime 扩展模型、OutputWidget 渲染器实现、文件类型注册和安全模型，掌握自定义数据格式的可视化方法。
tags: [mimerenderer, irendermime, outputwidget, mime-type, rendering, safe-mode]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: frontend-entry
    resource: /references/frontend-entry-source.md
    title: 前端入口模板解析
  - id: index-ts
    location: template/src/index.ts.jinja
    lines: "56-133"
---

## MIME 渲染器开发

MIME 渲染器扩展用于在 JupyterLab 中为特定 MIME 类型的数据提供自定义可视化。当 notebook 单元格输出某种 MIME 类型的数据时（如 `application/vnd.geo+json`），JupyterLab 会查找注册的渲染器并使用它来显示数据。mimerenderer 类型是最简单的扩展类型之一，不需要 Python 后端。

## MIME 渲染器架构

MIME 渲染器的核心是一个 `IRenderMime.IExtension` 对象，它定义了：
1. 要渲染的 MIME 类型
2. 创建渲染器 Widget 的工厂函数
3. 关联的文件类型和文档视图工厂

```
Notebook Output / File
       │
       │ MIME data (e.g., application/x-my-type)
       ▼
┌──────────────────────────────────┐
│     IRenderMime.Registry         │
│  (查找匹配的 rendererFactory)    │
└──────────┬───────────────────────┘
           │ createRenderer()
           ▼
┌──────────────────────────────────┐
│       OutputWidget               │
│  (implements IRenderMime.IRenderer)│
│  - renderModel(data) → 渲染数据  │
└──────────────────────────────────┘
```

## 生成代码结构

mimerenderer 类型的 `src/index.ts` 结构如下：

```typescript
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { Widget } from '@lumino/widgets';
import { JSONObject } from '@lumino/coreutils';  // 当 data_format == 'json' 时

const MIME_TYPE = 'application/x-my-type';
const CLASS_NAME = 'mimerenderer-my_type';

export class OutputWidget extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass(CLASS_NAME);
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    // string 格式：
    const data = model.data[this._mimeType] as string;
    this.node.textContent = data.slice(0, 16384);
    return Promise.resolve();
  }

  private _mimeType: string;
}

export const rendererFactory: IRenderMime.IRendererFactory = {
  safe: true,
  mimeTypes: [MIME_TYPE],
  createRenderer: options => new OutputWidget(options)
};

const extension: IRenderMime.IExtension = {
  id: 'myextension:plugin',
  rendererFactory,
  rank: 100,
  dataType: 'string',
  fileTypes: [{
    name: 'my_type',
    mimeTypes: [MIME_TYPE],
    extensions: ['.my_type']
  }],
  documentWidgetFactoryOptions: {
    name: 'My Viewer',
    primaryFileType: 'my_type',
    fileTypes: ['my_type'],
    defaultFor: ['my_type']
  }
};

export default extension;
```

## 核心 API 解析

### IRenderMime.IRenderer

渲染器 Widget 必须实现 `IRenderMime.IRenderer` 接口，核心方法是 `renderModel`：

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void>
```

- `model.data`：包含 MIME 类型到数据的映射，通过 `model.data[this._mimeType]` 获取当前 MIME 类型的数据
- `model.metadata`：输出元数据
- `model.setData(options)`：更新数据（用于交互式渲染器）
- 返回 Promise，渲染完成后 resolve

### IRenderMime.IRendererFactory

```typescript
interface IRendererFactory {
  safe: boolean;                          // 是否安全（详见安全模型）
  mimeTypes: string[];                    // 支持的 MIME 类型列表
  createRenderer: (options: IRendererOptions) => IRenderer;
}
```

一个工厂可以为多个 MIME 类型创建渲染器。

### IRenderMime.IExtension

```typescript
interface IExtension {
  id: string;
  rendererFactory: IRendererFactory;
  rank?: number;                          // 渲染优先级（数字越小优先级越高）
  dataType: 'string' | 'json';            // 数据格式
  fileTypes?: IFileType[];                // 关联文件类型
  documentWidgetFactoryOptions?: IDocumentWidgetFactoryOptions | IDocumentWidgetFactoryOptions[];
}
```

## 数据格式（data_format）

Copier 参数 `data_format` 决定数据如何传递给渲染器：

### string 格式

```typescript
// Copier 选择 data_format: string
const data = model.data[this._mimeType] as string;
this.node.textContent = data.slice(0, 16384);  // 截断到 16KB
```

适用于文本类数据：CSV、SVG、纯文本格式、自定义标记语言等。

### json 格式

```typescript
// Copier 选择 data_format: json
import { JSONObject } from '@lumino/coreutils';
const data = model.data[this._mimeType] as JSONObject;
this.node.textContent = JSON.stringify(data);
```

适用于结构化数据：GeoJSON、Plotly JSON、Vega-Lite 规范、自定义 JSON 格式等。

## 文件类型注册

`fileTypes` 数组将 MIME 类型关联到文件扩展名：

```typescript
fileTypes: [{
  name: 'my_type',           // 文件类型内部名称（唯一标识符）
  mimeTypes: [MIME_TYPE],    // 关联的 MIME 类型
  extensions: ['.my_type'],  // 文件扩展名
  iconLabel: '?',            // 可选：图标
  contentType: 'file',       // 可选：内容类型
  fileFormat: 'text'         // 可选：文件格式
}]
```

文件类型注册后：
1. 在文件浏览器中，`.my_type` 文件会显示正确的图标
2. 双击 `.my_type` 文件会用注册的 viewer 打开
3. 文件内容自动以 MIME 类型数据形式传递给渲染器

## 文档视图工厂

`documentWidgetFactoryOptions` 配置了作为独立文档查看器的行为：

```typescript
documentWidgetFactoryOptions: {
  name: 'My Viewer',              // 查看器显示名称（在"Open With"菜单中）
  primaryFileType: 'my_type',     // 主要文件类型
  fileTypes: ['my_type'],         // 支持的文件类型列表
  defaultFor: ['my_type'],        // 默认打开这些类型
  canStartKernel: false,          // 是否可以启动内核
  preferKernel: false,            // 是否优先使用内核
  toolbar: [...]                  // 可选：自定义工具栏
}
```

这意味着：
1. 在文件浏览器中打开 `.my_type` 文件会自动使用这个查看器
2. 在文件的"Open With"右键菜单中会出现"My Viewer"选项
3. 用户也可以选择其他已注册的查看器（如文本编辑器）

## 渲染器优先级（rank）

`rank` 控制当多个渲染器支持同一 MIME 类型时的优先级：
- 数字越小优先级越高
- 内置渲染器 rank 通常在 0-100 范围
- 默认值 100 适合自定义渲染器
- 如果要覆盖内置渲染器，使用更小的 rank（如 50）

## 安全模型（safe 属性）

`rendererFactory.safe` 是最重要的安全属性：

| safe 值 | 含义 | 信任行为 | 典型用例 |
|---------|------|---------|---------|
| `true` | 渲染器处理的是安全数据 | 总是渲染（包括不受信任的 notebook） | 文本、图片、非交互式图表 |
| `false` | 渲染器可能执行代码或执行危险操作 | 受信任 notebook 正常渲染；不受信任 notebook 显示"Run cell to view output" | HTML/JavaScript、可执行脚本、任意网络请求 |

**判断原则**：如果渲染器会将数据作为 HTML/JS 执行、发出网络请求、访问用户文件系统，则 `safe: false`；如果只是展示数据可视化（文本、Canvas、SVG 静态渲染），则 `safe: true`。

JupyterLab 的安全模型：
- 受信任的 notebook（用户自己创建或显式信任的）：所有渲染器正常工作
- 不受信任的 notebook（从外部打开的）：safe: false 的渲染器显示警告占位符，需要用户执行单元格才能渲染
- 这是防止 XSS 和恶意代码的重要安全机制

## 自定义渲染器实现

模板生成的 `OutputWidget` 只是将数据显示为文本。实际开发中，你需要替换 `renderModel` 的实现来进行真正的可视化。以下是常见模式：

### Canvas 渲染

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  const data = model.data[this._mimeType] as JSONObject;
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 300;
  const ctx = canvas.getContext('2d')!;
  // 用 Canvas API 绘制
  this.node.appendChild(canvas);
  return Promise.resolve();
}
```

### SVG 渲染

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  const svgData = model.data[this._mimeType] as string;
  this.node.innerHTML = svgData;  // 注意：只在确认数据安全时使用 innerHTML
  return Promise.resolve();
}
```

### 使用第三方库（如 D3、React）

```typescript
import * as d3 from 'd3';

renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  const data = model.data[this._mimeType] as any;
  // 使用 d3 在 this.node 中创建可视化
  const svg = d3.select(this.node).append('svg')
    .attr('width', 400).attr('height', 300);
  // ... d3 绘图逻辑
  return Promise.resolve();
}
```

记住在 `package.json` 中添加依赖：`jlpm add d3 @types/d3`。

## 相关概念

- [四种扩展类型对比](03-four-extension-types.md)
- [前端扩展开发](06-frontend-extension.md)
- [双包构建系统](05-build-system.md)
