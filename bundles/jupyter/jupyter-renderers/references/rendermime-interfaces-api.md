---
type: Reference
title: IRenderMime 核心 API 参考
description: JupyterLab MIME 渲染器扩展开发的核心接口参考，包含 IRenderer、IRendererFactory、IExtension、ILatexTypesetter 等
tags: [api, typescript, rendermime, reference]
sources:
  - id: rendermime-interfaces-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/package.json
    title: fasta-extension package.json (依赖 @jupyterlab/rendermime-interfaces)
  - id: fasta-index
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/src/index.ts
    title: fasta-extension/src/index.ts
  - id: geojson-index
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/index.ts
    title: geojson-extension/src/index.ts
  - id: vega3-index
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/src/index.ts
    title: vega3-extension/src/index.ts
  - id: katex-index
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/index.ts
    title: katex-extension/src/index.ts
  - id: mathjax2-index
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/index.ts
    title: mathjax2-extension/src/index.ts
  - id: mathjax2-typesetter
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/typesetter.ts
    title: mathjax2-extension/src/typesetter.ts
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# IRenderMime 核心 API 参考

本文档基于 jupyter-renderers 中5个扩展包的实际用法，整理 JupyterLab MIME 渲染器开发所需的核心接口。

## IRenderMime.IRenderer

所有 MIME 渲染器 Widget 必须实现的接口，继承自 Lumino Widget 的渲染能力。[^fasta-index][^geojson-index][^vega3-index]

```typescript
interface IRenderer {
  /**
   * 渲染 MIME 模型数据到 Widget 节点
   * @param model - 包含 data 和 metadata 的 MIME 模型
   * @returns Promise，渲染完成时 resolve
   */
  renderModel(model: IRenderMime.IMimeModel): Promise<void>;
}
```

**实现要点**：
- 类必须继承 `Widget`（来自 `@lumino/widgets`）并 `implements IRenderMime.IRenderer`
- 构造函数接收 `IRendererOptions`，从中获取 `mimeType`、`sanitizer`、`resolver` 等
- `renderModel()` 是核心渲染方法，从 `model.data[mimeType]` 获取数据
- 可重写 `onAfterShow()`、`onResize()`、`onUpdateRequest()` 处理生命周期事件
- 需要清理资源时重写 `dispose()`

## IRenderMime.IRendererFactory

渲染器工厂，由 JupyterLab 的 rendermime 注册表用于创建渲染器实例。

```typescript
interface IRendererFactory {
  /**
   * 渲染输出是否安全（已通过 sanitizer 净化）
   * - true: 输出被认为是安全的，不需要额外净化
   * - false: 输出可能包含不安全内容
   */
  safe: boolean;

  /**
   * 此工厂支持的 MIME 类型列表
   */
  mimeTypes: string[];

  /**
   * 创建渲染器实例
   */
  createRenderer: (options: IRendererOptions) => IRenderer;
}
```

**各扩展的 safe 值**：

| 扩展 | safe | dataType | 说明 |
|------|------|----------|------|
| fasta-extension | false | string | FASTA 文本渲染，MSA  viewer 生成 DOM |
| geojson-extension | true | json | GeoJSON → Leaflet 地图，popup 内容显式 sanitize |
| vega3-extension | true | json | Vega 嵌入渲染，vega-embed 处理输出 |

## IRenderMime.IExtension

MIME 渲染器扩展的完整描述符，用于向 JupyterLab 注册文件类型、文档工厂和渲染器。

```typescript
interface IExtension {
  /** 唯一 ID，格式: '包名:标识' */
  id: string;

  /** 渲染器工厂实例 */
  rendererFactory: IRendererFactory;

  /** 优先级（数值越小优先级越高），默认 0 */
  rank?: number;

  /** 数据类型：'string'（文本）或 'json'（结构化数据） */
  dataType: 'string' | 'json';

  /** 注册的文件类型定义 */
  fileTypes?: IFileType[];

  /** 文档 Widget 工厂选项（打开为独立文档时） */
  documentWidgetFactoryOptions?: IWidgetFactoryOptions | IWidgetFactoryOptions[];
}
```

**id 命名规范**：
- FASTA: `'jupyterlab-fasta:Fasta'` / `'jupyterlab-fasta:Clustal'`
- GeoJSON: `'@jupyterlab/geojson-extension:factory'`
- Vega3: `'@jupyterlab/vega3-extension:factory'`

**rank 优先级**：
- vega3-extension 使用 `rank: 59`，高于旧版 vega2 扩展（rank 更高 = 优先级更低？需注意：rank 数值小的优先）

### IFileType

```typescript
interface IFileType {
  name: string;           // 文件类型内部名称（如 'geojson', 'vega3'）
  extensions: string[];   // 文件扩展名列表（如 ['.geojson', '.geo.json']）
  mimeTypes: string[];    // 关联的 MIME 类型
  iconClass?: string;     // CSS 图标类名（如 'jp-MaterialIcon jp-GeoJSONIcon'）
}
```

### IWidgetFactoryOptions

```typescript
interface IWidgetFactoryOptions {
  name: string;                     // 工厂显示名称
  primaryFileType: string;          // 主文件类型名
  fileTypes: string[];              // 支持的文件类型
  defaultFor?: string[];            // 默认打开的文件类型
}
```

## IRenderMime.IMimeModel

传递给渲染器的数据模型：

```typescript
interface IMimeModel {
  /** MIME 类型 → 数据的映射 */
  readonly data: ReadonlyJSONObject;

  /** MIME 类型 → 元数据的映射 */
  readonly metadata: ReadonlyJSONObject;

  /**
   * 更新模型数据（如渲染器添加额外 MIME 输出）
   */
  setData(options: { data?: PartialJSONObject; metadata?: PartialJSONObject }): void;
}
```

**使用示例**（Vega3 导出 PNG）：[^vega3-index]

```typescript
// 渲染完成后生成 PNG 并添加到模型
if (!model.data['image/png']) {
  const imageData = await result.view.toImageURL('png');
  model.setData({
    data: {
      ...model.data,
      'image/png': imageData.split(',')[1]
    }
  });
}
```

## IRenderMime.IRendererOptions

渲染器构造选项：

```typescript
interface IRendererOptions {
  mimeType: string;          // 当前渲染的 MIME 类型
  sanitizer?: ISanitizer;    // HTML 净化工具
  resolver?: IResolver;      // URL 解析器（用于解析相对路径数据）
  linkHandler?: ILinkHandler;// 链接处理
  latexTypesetter?: ILatexTypesetter; // LaTeX 排版器
  translator?: ITranslator;  // 翻译器
}
```

## IRenderMime.ILatexTypesetter

数学公式排版接口，由 KaTeX 和 MathJax2 扩展提供。[^katex-index][^mathjax2-typesetter]

```typescript
interface ILatexTypesetter {
  /**
   * 对 DOM 节点中的数学公式进行排版
   * @param node - 包含数学公式的 HTML 元素
   */
  typeset(node: HTMLElement): void;
}
```

**实现对比**：

| 特性 | KaTeX (KatexTypesetter) | MathJax2 (MathJaxTypesetter) |
|------|------------------------|------------------------------|
| 加载方式 | 打包到扩展中（katex npm 包） | 动态注入 `<script>` 从 CDN 加载 |
| 配置来源 | ISettingRegistry（用户设置） | PageConfig（fullMathjaxUrl, mathjaxConfig） |
| 异步处理 | 同步渲染 | PromiseDelegate 等待加载完成 |
| 宏支持 | 通过 settings 配置 macros | 通过 MathJax Hub.Config 配置 |
| 扩展类型 | extension（应用扩展） | extension（应用扩展） |
| 互斥 | disabledExtensions 禁用 MathJax | 无（被 KaTeX 禁用时不加载） |

## ISanitizer

HTML 净化接口（GeoJSON 用于 popup 内容安全）：

```typescript
interface ISanitizer {
  /**
   * 净化 HTML 字符串，移除不安全内容
   */
  sanitize(dirty: string, allowed?: any): string;
}
```

**用法**（GeoJSON popup 安全处理）：[^geojson-index]

```typescript
layer.bindPopup(this._sanitizer.sanitize(popupContent));
```

## IResolver

URL 解析器接口（Vega3 用于解析数据文件相对路径）：

```typescript
interface IResolver {
  /** 解析相对 URL 为绝对 URL */
  resolveUrl(url: string): Promise<string>;

  /** 获取可用于下载的 URL */
  getDownloadUrl(url: string): Promise<string>;
}
```

**用法**（Vega3 数据加载）：[^vega3-index]

```typescript
this._resolver.resolveUrl('').then((path: string) => {
  return this._resolver.getDownloadUrl(path).then(baseURL => {
    const loader = vega.loader({ baseURL });
    // 使用 loader 加载 Vega 数据
  });
});
```
