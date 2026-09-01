---
type: Concept
title: Vega/Vega-Lite 可视化渲染器
description: "@jupyterlab/vega3-extension 使用 vega-embed 渲染 Vega 3 和 Vega-Lite 2 声明式可视化图表，支持数据加载、PNG导出和多文档工厂"
tags: [vega, vega-lite, visualization, chart, vega-embed, mime-renderer]
sources:
  - id: vega3-index
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/src/index.ts
    title: vega3-extension/src/index.ts
  - id: vega3-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/package.json
    title: vega3-extension/package.json
  - id: vega3-init
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/jupyterlab_vega3/__init__.py
    title: jupyterlab_vega3/__init__.py
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# Vega/Vega-Lite 可视化渲染器

Vega3 扩展（@jupyterlab/vega3-extension）为 JupyterLab 提供 [Vega](https://vega.github.io/vega/) 和 [Vega-Lite](https://vega.github.io/vega-lite/) 声明式可视化图表的渲染能力，使用 [vega-embed](https://github.com/vega/vega-embed) 库将 JSON 可视化规约渲染为交互式 SVG/Canvas 图表。

## 基本信息

| 属性 | Vega 3 | Vega-Lite 2 |
|------|--------|-------------|
| MIME 类型 | `application/vnd.vega.v3+json` | `application/vnd.vegalite.v2+json` |
| 文件扩展名 | `.vg`, `.vg.json`, `.vega` | `.vl`, `.vl.json`, `.vegalite` |
| 内部名称 | `vega3` | `vega-lite2` |
| CSS 类名 | `jp-RenderedVega3` | `jp-RenderedVegaLite2` |
| mode 参数 | `'vega'` | `'vega-lite'` |

通用属性：

| 属性 | 值 |
|------|-----|
| npm 包名 | @jupyterlab/vega3-extension |
| 版本 | 3.3.0 |
| Python 包名 | jupyterlab_vega3 |
| dataType | `'json'` |
| safe | `true` |
| rank | 59（优先级高于 vega2 扩展） |
| vega-embed 版本 | 3.9.2（固定版本） |

## Vega 与 Vega-Lite 简介

**Vega** 是一种声明式可视化语法，用 JSON 描述数据可视化的完整细节（坐标轴、图例、标记、数据转换等）。Vega-Lite 是 Vega 的高级封装，提供更简洁的语法自动生成 Vega 规约。

Vega MIME 类型版本号与 Vega 主版本号对应（v3 对应 Vega 3.x），不同版本的 Vega 规约可能不兼容。

## 核心实现

### MIME 类型常量

```typescript
export const VEGA_MIME_TYPE = 'application/vnd.vega.v3+json';
export const VEGALITE_MIME_TYPE = 'application/vnd.vegalite.v2+json';
```

MIME 类型中的版本号（v3、v2）是 JupyterLab 支持多版本 Vega 并行渲染的关键——不同版本的 Vega 扩展注册不同 MIME 类型，互不干扰。

### RenderedVega3 Widget

```typescript
export class RenderedVega3 extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this._resolver = options.resolver!;       // 获取 URL 解析器（必需）
    this.addClass(VEGA_COMMON_CLASS);          // 'jp-RenderedVegaCommon3'
    this.addClass(
      this._mimeType === VEGA_MIME_TYPE ? VEGA_CLASS : VEGALITE_CLASS
    );
  }
```

构造函数根据 MIME 类型添加不同的 CSS 类名，支持差异化样式。Vega3 是唯一**必须**使用 `options.resolver` 的渲染器，用于解析数据文件的相对路径。

### renderModel 方法

Vega3 的 `renderModel` 是所有渲染器中最复杂的，因为它涉及异步数据加载和 PNG 导出：[^vega3-index]

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  const data = model.data[this._mimeType] as JSONObject;
  const metadata = model.metadata[this._mimeType] as {
    embed_options?: EmbedOptions;
  };
  const embedOptions = metadata?.embed_options ?? {};
  const mode: Mode = this._mimeType === VEGA_MIME_TYPE ? 'vega' : 'vega-lite';

  return this._resolver.resolveUrl('').then((path: string) => {
    return this._resolver.getDownloadUrl(path).then(baseURL => {
      // 配置 Vega 数据加载器（baseURL 用于解析相对路径数据引用）
      const loader = vega.loader({ baseURL });
      const options: EmbedOptions = {
        actions: true,        // 显示 Vega 操作菜单（导出 PNG/SVG/查看源码）
        ...embedOptions,      // 用户可通过 metadata 覆盖配置
        mode,                 // 'vega' 或 'vega-lite'
        loader                // 自定义数据加载器
      };

      // 创建容器并渲染
      const el = document.createElement('div');
      this.node.innerHTML = '';  // 清空之前的内容
      this.node.appendChild(el);

      return vegaEmbed(el, data, options).then(result => {
        // 渲染完成后，生成 PNG 并添加到输出数据
        if (!model.data['image/png']) {
          return result.view.toImageURL('png').then(imageData => {
            const data = {
              ...model.data,
              'image/png': imageData.split(',')[1]  // 提取 base64 数据
            };
            model.setData({ data });
          });
        }
      });
    });
  });
}
```

### 异步渲染流程

Vega3 的渲染完全异步：

```
1. 获取 JSON 数据和 metadata 配置
2. 通过 resolver 解析 baseURL（处理相对路径数据）
3. 创建 Vega loader（支持从 JupyterLab 服务器加载数据文件）
4. 清空 Widget 节点，创建新容器
5. 调用 vegaEmbed(el, data, options) 渲染图表
6. （可选）生成 PNG 缩略图并添加到模型数据
7. 返回 Promise（渲染完成时 resolve）
```

### URL 解析器（IResolver）

Vega3 使用 `IResolver` 解析数据文件的相对路径：

```typescript
this._resolver.resolveUrl('').then(path => {
  return this._resolver.getDownloadUrl(path).then(baseURL => {
    const loader = vega.loader({ baseURL });
    // ...
  });
});
```

当 Vega 规约中引用外部数据文件（如 `"url": "data.csv"`）时，Vega loader 使用 `baseURL` 解析为 JupyterLab 服务器上的绝对路径，通过 Jupyter Server 的 Contents API 下载数据。这使得 Vega 图表可以引用 Notebook 同目录下的数据文件。

### metadata 配置覆盖

用户可以通过 output metadata 自定义 vega-embed 配置：

```python
from IPython.display import display
display(
    {"application/vnd.vega.v3+json": vega_spec},
    metadata={
        "application/vnd.vega.v3+json": {
            "embed_options": {
                "theme": "dark",
                "actions": {"export": True, "source": False, "editor": False}
            }
        }
    },
    raw=True
)
```

`embed_options` 与默认配置（`actions: true, mode, loader`）合并，用户配置优先级更高。

### PNG 导出功能

Vega3 渲染完成后自动生成 PNG 缩略图：

```typescript
if (!model.data['image/png']) {
  return result.view.toImageURL('png').then(imageData => {
    model.setData({
      data: {
        ...model.data,
        'image/png': imageData.split(',')[1]
      }
    });
  });
}
```

这会将 Vega 图表的 PNG 表示添加到 MIME 模型的 `image/png` 数据中。当 Notebook 被不支持 Vega 的查看器（如 GitHub 渲染器）打开时，可以显示 PNG 静态图片作为回退。

**条件检查**：`if (!model.data['image/png'])` 确保不会覆盖已有的 PNG 数据。

### CSS 类名设计

Vega3 使用三个 CSS 类名实现差异化样式：

| CSS 类名 | 应用于 | 用途 |
|---------|--------|------|
| `jp-RenderedVegaCommon3` | 所有 Vega3/Vega-Lite2 渲染器 | 公共样式 |
| `jp-RenderedVega3` | Vega 3 图表 | Vega 特有样式 |
| `jp-RenderedVegaLite2` | Vega-Lite 2 图表 | Vega-Lite 特有样式 |

### rank 优先级

```typescript
rank: 59,  // prefer over vega 2 extension
```

rank 值为 59，高于旧版 vega2 扩展（通常 rank=0 优先级最高，数值越大优先级越低？需注意：JupyterLab rendermime 中 rank 数值小的优先级更高。此处 rank=59 意味着比默认 rank=0 的渲染器优先级低，但注释说"prefer over vega2"，这可能是因为 vega2 的 rank 更高）。

实际上，JupyterLab 的 MIME 渲染器优先级中，rank 值越小优先级越高。Vega3 设置 rank=59 可能是为了在 Vega3 和 Vega2 同时存在时，通过其他机制（如 MIME 类型特异性）确保 Vega3 优先。

### 双文档工厂注册

Vega3 注册了两个文件类型和两个文档工厂：[^vega3-index]

```typescript
documentWidgetFactoryOptions: [
  {
    name: 'Vega 3',
    primaryFileType: 'vega3',
    fileTypes: ['vega3', 'json'],
    defaultFor: ['vega3']
  },
  {
    name: 'Vega-Lite 2',
    primaryFileType: 'vega-lite2',
    fileTypes: ['vega-lite2', 'json'],
    defaultFor: ['vega-lite2']
  }
],
fileTypes: [
  {
    mimeTypes: [VEGA_MIME_TYPE],
    name: 'vega3',
    extensions: ['.vg', '.vg.json', '.vega'],
    iconClass: 'jp-MaterialIcon jp-VegaIcon'
  },
  {
    mimeTypes: [VEGALITE_MIME_TYPE],
    name: 'vega-lite2',
    extensions: ['.vl', '.vl.json', '.vegalite'],
    iconClass: 'jp-MaterialIcon jp-VegaIcon'
  }
]
```

这意味着：
- `.vg`/`.vg.json`/`.vega` 文件用 "Vega 3" 工厂打开
- `.vl`/`.vl.json`/`.vegalite` 文件用 "Vega-Lite 2" 工厂打开
- 两种工厂都接受 `.json` 文件（但不是默认打开方式）

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| vega-embed | 3.9.2（固定版本） | Vega/Vega-Lite 渲染核心 |
| @lumino/coreutils | ^1.0.0 \|\| ^2.1.0 | JSONObject 类型 |
| @lumino/widgets | ^1.0.0 \|\| ^2.1.0 | Widget 基类 |
| @jupyterlab/rendermime-interfaces | ^3.0.0 \|\| ^3.8.0 | MIME 渲染器接口 |

**注意**：vega-embed 使用固定版本 `3.9.2`（非 `^3.9.2`），这是因为 Vega/Vega-Lite 的规约格式在不同小版本间可能有不兼容变化，固定版本确保渲染行为一致。

## 与其他渲染器的区别

| 特性 | Vega3 | FASTA | GeoJSON |
|------|-------|-------|---------|
| renderModel 返回 | Promise（异步） | Promise.resolve() | Promise.resolve() |
| 使用 resolver | ✅ 必须 | ❌ | ❌ |
| 修改 model.data | ✅ 添加 PNG 输出 | ❌ | ❌ |
| metadata 支持 | ✅ embed_options | ❌ | ❌ |
| 清空节点 | ✅ innerHTML='' | ❌ | ❌ |
| dispose 重写 | ❌ | ❌ | ✅（Leaflet 清理） |

## 相关概念

- [MIME 渲染器开发模式](02-mime-renderer-pattern.md)
- [FASTA 生物序列渲染器](04-fasta-renderer.md)
- [GeoJSON 地理数据渲染器](05-geojson-renderer.md)
- [IRenderMime 核心 API 参考](../references/rendermime-interfaces-api.md)

[^vega3-index]: vega3-extension/src/index.ts
