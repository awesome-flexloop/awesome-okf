---
type: Concept
title: GeoJSON 地理数据渲染器
description: @jupyterlab/geojson-extension 扩展实现，使用 Leaflet 地图库渲染 GeoJSON 地理数据，支持多种底图切换、API Key 管理、属性弹窗和 Notebook 滚动适配
tags: [geojson, leaflet, map, gis, mime-renderer]
sources:
  - id: geojson-index
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/index.ts
    title: geojson-extension/src/index.ts
  - id: geojson-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/package.json
    title: geojson-extension/package.json
  - id: geojson-icons
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/icons.ts
    title: geojson-extension/src/icons.ts
  - id: geojson-init
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/jupyterlab_geojson/__init__.py
    title: jupyterlab_geojson/__init__.py
  - id: geojson-providers
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/providers.json
    title: providers.json (底图配置)
  - id: geojson-access
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/access_data.json
    title: access_data.json (API Key 配置)
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# GeoJSON 地理数据渲染器

GeoJSON 扩展（@jupyterlab/geojson-extension）为 JupyterLab 提供交互式地图渲染能力，使用 [Leaflet](https://leafletjs.com/) 地图库将 GeoJSON 数据叠加到底图上，支持底图切换、属性弹窗和模糊搜索。

## 基本信息

| 属性 | 值 |
|------|-----|
| npm 包名 | @jupyterlab/geojson-extension |
| 版本 | 3.4.0 |
| Python 包名 | jupyterlab_geojson |
| MIME 类型 | `application/geo+json` |
| 文件扩展名 | `.geojson`、`.geo.json` |
| dataType | `'json'` |
| safe | `true`（popup 内容经 sanitizer 净化） |
| CSS 类名 | `jp-RenderedGeoJSON` |
| 图标类名 | `jp-MaterialIcon jp-GeoJSONIcon` |

## GeoJSON 数据格式

GeoJSON 是一种基于 JSON 的地理数据格式，支持点（Point）、线（LineString）、面（Polygon）及其组合类型（MultiPoint、MultiLineString、MultiPolygon、GeometryCollection）和要素集合（FeatureCollection）：

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [116.4, 39.9]},
      "properties": {"name": "北京"}
    }
  ]
}
```

## 核心实现

### RenderedGeoJSON Widget

GeoJSON 渲染器是5个扩展中最复杂的，包含地图初始化、底图切换、属性弹窗、模糊搜索、滚动适配等功能。

#### 构造函数与地图初始化

```typescript
export class RenderedGeoJSON extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this.addClass(CSS_CLASS);                     // 'jp-RenderedGeoJSON'
    this._mimeType = options.mimeType;
    this._sanitizer = options.sanitizer;           // 获取 HTML 净化器

    // 创建 Leaflet 地图实例（禁用 trackResize，使用 Lumino resize 事件）
    this._map = leaflet.map(this.node, {
      trackResize: false
    });

    // 默认添加 OpenStreetMap 底图
    this._lastAddedLayer = leaflet.tileLayer(
      tilelayers_data['OpenStreetMap']['Mapnik'].url,
      tilelayers_data['OpenStreetMap']['Mapnik']
    );
    this._lastAddedLayer.addTo(this._map);
  }
```

**Leaflet marker 图标修复**：由于 webpack 打包问题，Leaflet 默认的 marker 图标 URL 硬编码在源码中，需要手动修复：

```typescript
delete (leaflet.Icon.Default.prototype as any)['_getIconUrl'];
leaflet.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetinaUrl,    // import 的 2x 图标
  iconUrl: iconUrl,                // import 的 1x 图标
  shadowUrl: shadowUrl             // import 的阴影图标
});
```

这是一个 webpack 打包的经典 workaround，通过 import 图标文件并手动覆盖 Leaflet 默认配置来解决。

#### renderModel 方法

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  const data = model.data[this._mimeType] as GeoJSON.GeoJsonObject;
  return new Promise<void>((resolve, reject) => {
    // 1. 创建底图切换按钮
    const button = document.createElement('button');
    button.className = 'jp-RenderedGeoJSONLayerIcon';
    button.onclick = () => showDialog({
      title: '',
      body: new TileLayerPalette(nameList),    // 底图选择面板
      buttons: [Dialog.cancelButton(), Dialog.okButton()]
    }).then(result => {
      // 切换底图逻辑（处理 API Key 需求）
      this._switchTileLayer(result.value);
    });

    // 2. 创建 GeoJSON 图层并添加到地图
    this._geoJSONLayer = leaflet
      .geoJSON(data, {
        onEachFeature: (feature, layer) => {
          if (feature.properties) {
            // 将属性渲染为表格弹窗，经 sanitizer 净化
            let popupContent = '<table>';
            for (const p in feature.properties) {
              popupContent += `<tr><td>${p}:</td><td><b>${feature.properties[p]}</b></td></tr>`;
            }
            popupContent += '</table>';
            layer.bindPopup(this._sanitizer.sanitize(popupContent));
          }
        }
      })
      .addTo(this._map);
    this.update();
    resolve();
  });
}
```

#### 属性弹窗安全处理

GeoJSON 要素的属性通过 `onEachFeature` 回调渲染为 HTML 表格弹窗，使用 `this._sanitizer.sanitize()` 净化，防止 XSS 攻击。这也是 GeoJSON 设置 `safe: true` 的原因——输出已通过 ISanitizer 净化。

#### 尺寸自适应与视图适配

```typescript
protected onUpdateRequest(msg: Message): void {
  if (this.isVisible) {
    this._map.invalidateSize();                  // 通知 Leaflet 容器尺寸变化
  }
  if (this._geoJSONLayer) {
    this._map.fitBounds(this._geoJSONLayer.getBounds());  // 自动缩放到数据范围
  }
}
```

`invalidateSize()` 告诉 Leaflet 更新地图容器尺寸，`fitBounds()` 自动将视图缩放到 GeoJSON 数据的边界范围。

#### Notebook 滚轮缩放适配

GeoJSON 在 Notebook 输出区域中默认禁用滚轮缩放，避免与 Notebook 页面滚动冲突：

```typescript
protected onAfterAttach(msg: Message): void {
  if (this.parent?.hasClass('jp-OutputArea-child')) {
    this._map.scrollWheelZoom.disable();         // 默认禁用滚轮缩放
    this._map.on('blur', () => this._map.scrollWheelZoom.disable());
    this._map.on('focus', () => this._map.scrollWheelZoom.enable());
  }
  this.update();
}
```

当地图获得焦点时启用滚轮缩放，失去焦点时禁用。这解决了在 Notebook 中滚动页面时误触发放大/缩小地图的问题。

#### 资源清理

GeoJSON 是唯一重写 `dispose()` 方法的渲染器，因为 Leaflet map 需要手动销毁以防止内存泄漏：

```typescript
dispose(): void {
  this._map.remove();    // 销毁 Leaflet 地图实例
  this._map = null!;
  super.dispose();
}
```

## 底图系统

### 底图数据源

底图配置存储在 `providers.json` 中，包含多个底图提供商的配置：

- **OpenStreetMap**：Mapnik（默认底图，无需 API Key）
- **其他提供商**：可能需要 API Key（如 Mapbox、Esri 等）

`access_data.json` 记录哪些底图提供商需要 API Key 以及对应的参数名。

### TileLayerPalette（底图选择面板）

底图切换按钮点击后弹出对话框，包含模糊搜索框和底图列表：

```typescript
export class TileLayerPalette extends Widget implements Dialog.IBodyWidget<string> {
  constructor(list: Array<string> = []) {
    super();
    this._query = document.createElement('input');
    this._query.placeholder = 'Search for a tile layer';
    this._query.addEventListener('keyup', () => this.query_changed());
    // ...创建 select 列表
  }

  query_changed() {
    // 模糊搜索过滤底图列表
    const results = search(nameList, this._query.value);
    // 更新 select 选项
  }

  getValue(): string {
    return this._selectList.value;    // 返回选中的底图名称
  }
}
```

### 模糊搜索实现

GeoJSON 实现了一个基于 `@lumino/algorithm` 的 `StringExt.matchSumOfDeltas` 的模糊搜索：

```typescript
function fuzzySearch(item: string, query: string): IScore | null {
  const value = item.toLocaleLowerCase();
  const rgx = /\b\w/g;                             // 词边界正则
  const rgxMatch = rgx.exec(value);
  const match = StringExt.matchSumOfDeltas(value, query, rgxMatch?.index);
  if (match && match.score <= score) {
    score = match.score;
    indices = match.indices;
  }
  // ...
}
```

搜索按词边界匹配，支持首字母缩写式搜索（如输入 "OSM" 匹配 "OpenStreetMap"）。

### TextInput（API Key 输入）

当选择需要 API Key 的底图时（如 Mapbox），弹出第二个对话框请求 API Key：

```typescript
export class TextInput extends Widget implements Dialog.IBodyWidget<string> {
  constructor(placeHolder = '') {
    super();
    this._urlInput = document.createElement('input');
    this._urlInput.type = 'password';             // 密码模式输入
    this._urlInput.placeholder = placeHolder;
  }
  getValue(): string {
    return this._urlInput.value;
  }
}
```

API Key 输入使用 `type='password'` 隐藏输入内容，输入后动态设置到 `tilelayers_data` 对应底图的配置中。

### 底图切换逻辑

```typescript
if (input_name?.includes('.')) {
  // 两级名称（如 "OpenStreetMap.Mapnik"）
  const [APIname, subname] = input_name.split('.');
  if (access_data[APIname] !== undefined) {
    // 需要 API Key → 弹出输入框
    showDialog({ body: new TextInput('Enter the API key please'), ... })
      .then(result => {
        tilelayers_data[APIname][subname][APIkey] = result.value;
        this._switchLayer(APIname, subname);
      });
  } else {
    this._switchLayer(APIname, subname);  // 无需 API Key，直接切换
  }
}
```

## 图标系统

使用 JupyterLab 的 `LabIcon` 系统注册自定义图标：[^geojson-icons]

```typescript
import { LabIcon } from '@jupyterlab/ui-components';
import layersSvgstr from '../style/icons/layers-32px.svg';
import mapSvgstr from '../style/icons/geojson.svg';

export const layersIcon = new LabIcon({
  name: '@jupyterlab/geojson-extension:layers',
  svgstr: layersSvgstr
});

export const mapIcon = new LabIcon({
  name: '@jupyterlab/geojson-extension:map',
  svgstr: mapSvgstr
});
```

图标通过 import SVG 字符串（由 webpack 处理）创建 LabIcon 实例，可在按钮、文件浏览器等地方使用。

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| leaflet | ^1.5.0 | Leaflet 地图库（核心渲染引擎） |
| @jupyterlab/apputils | ^3.0.0 \|\| ^4.0.0 | Dialog、showDialog 对话框 |
| @jupyterlab/ui-components | ^3.0.0 \|\| ^4.0.0 | LabIcon 图标系统 |
| @lumino/algorithm | ^1.0.0 \|\| ^2.1.0 | StringExt 模糊搜索 |
| @jupyterlab/rendermime-interfaces | ^3.0.0 \|\| ^3.8.0 | MIME 渲染器接口 |
| @lumino/widgets | ^1.0.0 \|\| ^2.1.0 | Widget 基类 |

## 相关概念

- [MIME 渲染器开发模式](/concepts/02-mime-renderer-pattern.md)
- [FASTA 生物序列渲染器](/concepts/04-fasta-renderer.md)
- [Vega/Vega-Lite 可视化渲染器](/concepts/07-vega-renderer.md)
- [IRenderMime 核心 API 参考](/references/rendermime-interfaces-api.md)
