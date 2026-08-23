---
type: Concept
title: MIME 渲染器开发模式
description: JupyterLab MIME 渲染器的标准开发模式——Widget 子类、renderModel 方法、渲染工厂、扩展描述符、文件类型注册，基于 fasta/geojson/vega3 的共同模式提炼
tags: [mime-renderer, pattern, widget, rendermime, development]
sources:
  - id: fasta-index
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/src/index.ts
    title: fasta-extension/src/index.ts
  - id: geojson-index
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/index.ts
    title: geojson-extension/src/index.ts
  - id: vega3-index
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/src/index.ts
    title: vega3-extension/src/index.ts
  - id: rendermime-api
    resource: .agents/skills/source-code-to-okf-wiki/SKILL.md
    title: IRenderMime API
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# MIME 渲染器开发模式

jupyter-renderers 中的3个 MIME 渲染器（fasta、geojson、vega3）遵循高度一致的代码模式。掌握这个通用模板，可以快速理解每个具体渲染器的实现，并据此开发自定义 MIME 渲染器。

## 四要素模式

每个 MIME 渲染器由四个核心要素构成：

```
┌──────────────────────────────────────────────┐
│  1. MIME 类型常量（TYPES / MIME_TYPE）        │
│     定义支持的 MIME 类型、文件扩展名、解析器   │
├──────────────────────────────────────────────┤
│  2. 渲染器 Widget 类（extends Widget）        │
│     实现 IRenderMime.IRenderer 接口           │
│     - 构造函数：初始化 DOM 和渲染引擎         │
│     - renderModel()：核心渲染逻辑             │
│     - 生命周期方法：onResize/onUpdateRequest  │
├──────────────────────────────────────────────┤
│  3. 渲染器工厂（rendererFactory）             │
│     实现 IRenderMime.IRendererFactory 接口    │
│     - safe/mimeTypes/createRenderer           │
├──────────────────────────────────────────────┤
│  4. 扩展描述符（extensions 数组/对象）         │
│     实现 IRenderMime.IExtension 接口          │
│     - id/rendererFactory/rank/dataType        │
│     - fileTypes/documentWidgetFactoryOptions │
└──────────────────────────────────────────────┘
```

## 要素1：MIME 类型定义

渲染器首先声明支持的 MIME 类型和文件扩展名。

**简单模式（单 MIME 类型）**——GeoJSON 和 Vega3 使用常量：[^geojson-index][^vega3-index]

```typescript
// GeoJSON: 单一 MIME 类型
export const MIME_TYPE = 'application/geo+json';

// Vega3: 两个 MIME 类型用常量
export const VEGA_MIME_TYPE = 'application/vnd.vega.v3+json';
export const VEGALITE_MIME_TYPE = 'application/vnd.vegalite.v2+json';
```

**映射模式（多 MIME 类型）**——FASTA 使用 TYPES 对象映射：[^fasta-index]

```typescript
const TYPES: {
  [key: string]: { name: string; extensions: string[]; reader: any };
} = {
  'application/vnd.fasta.fasta': {
    name: 'Fasta',
    extensions: ['.fasta', '.fa'],
    reader: msa.io.fasta
  },
  'application/vnd.clustal.clustal': {
    name: 'Clustal',
    extensions: ['.clustal', '.aln'],
    reader: msa.io.clustal
  }
};
```

映射模式适合支持多个 MIME 类型且每个类型有不同解析器的场景。

## 要素2：渲染器 Widget 类

渲染器 Widget 是核心，继承 `Widget` 并实现 `IRenderMime.IRenderer` 接口。

### 构造函数模式

```typescript
export class RenderedData extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    // 1. 保存 MIME 类型
    this._mimeType = options.mimeType;

    // 2. 添加 CSS 类名
    this.addClass('jp-RenderedMSA');  // 或 'jp-RenderedGeoJSON', 'jp-RenderedVegaCommon3'

    // 3. 初始化渲染引擎（创建 DOM 元素和第三方库实例）
    const div = document.createElement('div');
    this.msa = new msa.msa({ el: div, vis: { /* 配置 */ } });
    this.node.appendChild(div);
  }
}
```

**构造函数中获取的 options**：

| 属性 | 类型 | 用途 | 使用的渲染器 |
|------|------|------|-------------|
| `mimeType` | string | 当前渲染的 MIME 类型 | 所有 |
| `sanitizer` | ISanitizer | HTML 净化 | geojson |
| `resolver` | IResolver | URL 解析（加载外部数据） | vega3 |

### renderModel 方法

这是渲染的核心方法，接收 MIME 数据模型并渲染到 Widget 节点：

```typescript
renderModel(model: IRenderMime.IRenderMimeModel): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    // 1. 从模型获取数据
    const data = model.data[this._mimeType];

    // 2. 使用第三方库渲染数据
    // ...（具体渲染逻辑因渲染器而异）

    // 3. 更新尺寸
    this.update();

    // 4. 完成
    resolve();
  });
}
```

**三种渲染模式对比**：

| 渲染器 | 数据获取方式 | 渲染方式 | 返回值 |
|--------|------------|---------|--------|
| FASTA | `model.data[mimeType]` as string | `_parser.parse(data)` → msa 渲染 | 同步 Promise.resolve() |
| GeoJSON | `model.data[mimeType]` as GeoJSON | Leaflet `geoJSON(data).addTo(map)` | 同步 Promise.resolve() |
| Vega3 | `model.data[mimeType]` as JSONObject | `vegaEmbed(el, data, options)` | 异步（vegaEmbed 返回 Promise） |

### 生命周期方法

渲染器可以重写 Lumino Widget 的生命周期方法：

```typescript
// 组件显示后更新
protected onAfterShow(msg: Message): void {
  this.update();
}

// 容器尺寸变化时更新
protected onResize(msg: Widget.ResizeMessage): void {
  this.update();
}

// 更新请求处理
protected onUpdateRequest(msg: Message): void {
  if (this.isVisible) {
    // 调整渲染内容尺寸
    // GeoJSON: this._map.invalidateSize() + fitBounds
    // FASTA: 调整 MSA 对齐宽度
    // Vega3: 无需（vega-embed 自适应）
  }
}

// 清理资源（GeoJSON 需要 dispose Leaflet map）
dispose(): void {
  this._map.remove();
  this._map = null!;
  super.dispose();
}
```

**注意**：只有 GeoJSON 重写了 `dispose()`，因为 Leaflet map 需要手动清理以防止内存泄漏。纯 DOM 渲染的 FASTA 和 Vega3 不需要额外清理。

### afterAttach 处理（GeoJSON 特有）

GeoJSON 重写了 `onAfterAttach` 来处理 Notebook 输出区域的滚动冲突：

```typescript
protected onAfterAttach(msg: Message): void {
  if (this.parent?.hasClass('jp-OutputArea-child')) {
    // 在 Notebook 输出中：默认禁用滚轮缩放，避免与页面滚动冲突
    this._map.scrollWheelZoom.disable();
    this._map.on('blur', () => this._map.scrollWheelZoom.disable());
    this._map.on('focus', () => this._map.scrollWheelZoom.enable());
  }
  this.update();
}
```

## 要素3：渲染器工厂

```typescript
export const rendererFactory: IRenderMime.IRendererFactory = {
  safe: true,          // 或 false
  mimeTypes: [MIME_TYPE],  // 或 Object.keys(TYPES)
  createRenderer: options => new RenderedGeoJSON(options)
};
```

**safe 字段的含义**：

- `safe: true`（GeoJSON、Vega3）：渲染输出被认为是安全的，JupyterLab 不需要额外净化。GeoJSON 中 popup 内容显式调用了 `sanitizer.sanitize()`。
- `safe: false`（FASTA）：输出可能包含不安全内容，JupyterLab 会在不信任的 Notebook 中对其进行额外处理。

## 要素4：扩展描述符

扩展描述符将渲染器注册到 JupyterLab，声明文件类型和文档工厂。

**单 MIME 类型（GeoJSON）**：[^geojson-index]

```typescript
const extensions: IRenderMime.IExtension = {
  id: '@jupyterlab/geojson-extension:factory',
  rendererFactory,
  rank: 0,
  dataType: 'json',
  fileTypes: [
    {
      name: 'geojson',
      mimeTypes: [MIME_TYPE],
      extensions: ['.geojson', '.geo.json'],
      iconClass: 'jp-MaterialIcon jp-GeoJSONIcon'
    }
  ],
  documentWidgetFactoryOptions: {
    name: 'GeoJSON',
    primaryFileType: 'geojson',
    fileTypes: ['geojson', 'json'],
    defaultFor: ['geojson']
  }
};
export default extensions;
```

**多 MIME 类型（FASTA）**：[^fasta-index]

```typescript
// FASTA 为每个 MIME 类型生成一个扩展描述符
const extensions = Object.keys(TYPES).map(k => {
  const { name } = TYPES[k];
  return {
    id: `jupyterlab-fasta:${name}`,
    rendererFactory,
    rank: 0,
    dataType: 'string',
    fileTypes: [{
      name,
      extensions: TYPES[k].extensions,
      mimeTypes: [k],
      iconClass: 'jp-MaterialIcon jp-MSAIcon'
    }],
    documentWidgetFactoryOptions: {
      name,
      primaryFileType: name,
      fileTypes: [name],
      defaultFor: [name]
    }
  } as IRenderMime.IExtension;
});
export default extensions;
```

**多文档工厂（Vega3）**：[^vega3-index]

```typescript
// Vega3 注册两个文件类型和两个文档工厂
const extension: IRenderMime.IExtension = {
  id: '@jupyterlab/vega3-extension:factory',
  rendererFactory,
  rank: 59,  // 高于旧版 vega2（rank 数值小=优先级高？注意：rank=0 优先级最高）
  dataType: 'json',
  documentWidgetFactoryOptions: [
    { name: 'Vega 3', primaryFileType: 'vega3', fileTypes: ['vega3', 'json'], defaultFor: ['vega3'] },
    { name: 'Vega-Lite 2', primaryFileType: 'vega-lite2', fileTypes: ['vega-lite2', 'json'], defaultFor: ['vega-lite2'] }
  ],
  fileTypes: [
    { mimeTypes: [VEGA_MIME_TYPE], name: 'vega3', extensions: ['.vg', '.vg.json', '.vega'], iconClass: 'jp-MaterialIcon jp-VegaIcon' },
    { mimeTypes: [VEGALITE_MIME_TYPE], name: 'vega-lite2', extensions: ['.vl', '.vl.json', '.vegalite'], iconClass: 'jp-MaterialIcon jp-VegaIcon' }
  ]
};
```

### dataType 字段

| 值 | 含义 | 使用的渲染器 |
|----|------|-------------|
| `'string'` | 数据以字符串形式传递（文本格式） | FASTA |
| `'json'` | 数据以 JSON 对象形式传递（结构化数据） | GeoJSON、Vega3 |

### fileTypes 与 documentWidgetFactoryOptions 的关系

- `fileTypes`：注册文件类型到 JupyterLab 的文档注册表，关联 MIME 类型、扩展名和图标
- `documentWidgetFactoryOptions`：创建文档 Widget 工厂，使用户可以双击文件在新标签页中打开
- 两者通过 `name`/`primaryFileType` 关联

## 标准模板总结

```typescript
// 1. 导入
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';

// 2. MIME 类型常量
const MIME_TYPE = 'application/x-my-format';
const CSS_CLASS = 'jp-RenderedMyFormat';

// 3. 渲染器 Widget
export class RenderedMyFormat extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass(CSS_CLASS);
    // 初始化 DOM 和渲染引擎
  }

  renderModel(model: IRenderMime.IRenderMimeModel): Promise<void> {
    const data = model.data[this._mimeType];
    // 渲染数据到 this.node
    this.update();
    return Promise.resolve();
  }

  protected onResize(msg: Widget.ResizeMessage): void {
    this.update();
  }

  private _mimeType: string;
}

// 4. 渲染器工厂
export const rendererFactory: IRenderMime.IRendererFactory = {
  safe: true,
  mimeTypes: [MIME_TYPE],
  createRenderer: options => new RenderedMyFormat(options)
};

// 5. 扩展描述符
const extension: IRenderMime.IExtension = {
  id: 'my-extension:factory',
  rendererFactory,
  rank: 0,
  dataType: 'json',  // 或 'string'
  fileTypes: [{
    name: 'my-format',
    mimeTypes: [MIME_TYPE],
    extensions: ['.myfmt'],
    iconClass: 'jp-MaterialIcon jp-MyFormatIcon'
  }],
  documentWidgetFactoryOptions: {
    name: 'My Format',
    primaryFileType: 'my-format',
    fileTypes: ['my-format'],
    defaultFor: ['my-format']
  }
};

export default extension;
```

## 相关概念

- [扩展类型：MIME 渲染器 vs 应用扩展](/concepts/03-extension-types.md)
- [FASTA 生物序列渲染器](/concepts/04-fasta-renderer.md)
- [GeoJSON 地理数据渲染器](/concepts/05-geojson-renderer.md)
- [Vega/Vega-Lite 可视化渲染器](/concepts/07-vega-renderer.md)
- [IRenderMime 核心 API 参考](/references/rendermime-interfaces-api.md)
- [创建自定义 MIME 渲染器](/examples/01-custom-mime-renderer.md)
