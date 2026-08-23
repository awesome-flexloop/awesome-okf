---
type: Facts
okf_version: "0.2"
title: "jupyter-renderers 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, renderers, mime, typescript, jupyterlab]
sources:
  - ../../../../../external/libs/jupyter/jupyter-renderers/package.json
  - ../../../../../external/libs/jupyter/jupyter-renderers/lerna.json
  - ../../../../../external/libs/jupyter/jupyter-renderers/install.json
  - ../../../../../external/libs/jupyter/jupyter-renderers/README.md
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/fasta-extension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/icons.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/geojson-extension/pyproject.toml
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/autorender.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/katex-extension/schema/plugin.json
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/typesetter.ts
  - ../../../../../external/libs/jupyter/jupyter-renderers/packages/vega3-extension/src/index.ts
---

# jupyter-renderers 源码事实清单

## 一、项目元数据与 Monorepo 结构

- F-001: package.json:2-5 — 根 `package.json` 声明 `private: true`，`workspaces` 指向 `packages/*`。
- F-002: package.json:7 — `build` 脚本执行 `lerna run --parallel build` 并行构建全部子包。
- F-003: package.json:8 — `build-py` 脚本先 `rimraf dist`，再 `lerna exec --concurrency 4 -- python -m build` 并行构建各 Python 包，并把 `dist/jupyterlab*` 统一移动到根 `dist/`。
- F-004: lerna.json:2-4 — lerna 配置 `npmClient: yarn`、`useWorkspaces: true`、`version: independent`（各包独立版本号）。
- F-005: install.json:2-4 — 根 `install.json` 声明 `packageManager: python`、`packageName: jupyterlab-renderers`。
- F-006: README.md:6-8 — README 自述该仓库是一个 monorepo，由若干 JupyterLab _mimerender extensions_ 组成。
- F-007: README.md:12-18 — 包清单表列出 5 个子包及其 MIME types 与 file extensions（fasta、geojson、katex、mathjax2、vega3）。
- F-008: README.md:20-22 — README 标注 `@jupyterlab/plotly-extension` 已废弃，指引改用 Plotly 官方 `jupyterlab-plotly`。

## 二、geojson-extension

- F-009: packages/geojson-extension/package.json:2-3 — npm 包名 `@jupyterlab/geojson-extension`，版本 `3.4.0`。
- F-010: packages/geojson-extension/package.json:95-96 — `jupyterlab.mimeExtension: true`，`outputDir: jupyterlab_geojson/labextension`。
- F-011: packages/geojson-extension/src/index.ts:66 — 导出 `MIME_TYPE = 'application/geo+json'`。
- F-012: packages/geojson-extension/src/index.ts:56 — 常量 `CSS_CLASS = 'jp-RenderedGeoJSON'`。
- F-013: packages/geojson-extension/src/index.ts:282-303 — `RenderedGeoJSON` 类实现 `IRenderMime.IRenderer`，构造时以 `trackResize: false` 创建 `leaflet.map`，并默认添加 `OpenStreetMap.Mapnik` tile layer。
- F-014: packages/geojson-extension/src/index.ts:318-422 — `renderModel()` 创建图层切换按钮，用 `showDialog` 弹出 `TileLayerPalette` 与 API key 输入框切换底图，并用 `leaflet.geoJSON(data, {onEachFeature})` 渲染要素。
- F-015: packages/geojson-extension/src/index.ts:427-441 — `onAfterAttach` 在 `jp-OutputArea-child` 内默认禁用 `scrollWheelZoom`，地图 focus 时启用。
- F-016: packages/geojson-extension/src/index.ts:481-485 — `rendererFactory` 声明 `safe: true`、`mimeTypes: [MIME_TYPE]`，`createRenderer` 返回 `RenderedGeoJSON`。
- F-017: packages/geojson-extension/src/index.ts:487-508 — 导出的 `extensions` 数组首项 `id: '@jupyterlab/geojson-extension:factory'`、`rank: 0`、`dataType: 'json'`。
- F-018: packages/geojson-extension/src/index.ts:493-500 — `fileTypes` 定义 `geojson` 类型，`extensions: ['.geojson', '.geo.json']`，携带 `iconClass`。
- F-019: packages/geojson-extension/src/index.ts:501-506 — `documentWidgetFactoryOptions` 声明 `name: 'GeoJSON'`、`primaryFileType: 'geojson'`、`fileTypes: ['geojson', 'json']`、`defaultFor: ['geojson']`。
- F-020: packages/geojson-extension/src/index.ts:218-264 — `TileLayerPalette` 类继承 `Widget` 实现 `Dialog.IBodyWidget<string>`，提供输入框+下拉列表的瓦片层搜索。
- F-021: packages/geojson-extension/src/index.ts:28-51 — 模块加载时遍历 `providers.json` 递归收集瓦片层名称到 `nameList`，过滤 `OpenStreetMap.BlackAndWhite`、含 `HikeBike` 与 `HERE.` 的条目。
- F-022: packages/geojson-extension/src/icons.ts:5-8 — `layersIcon` 为 `LabIcon`，`name: '@jupyterlab/geojson-extension:layers'`。
- F-023: packages/geojson-extension/src/icons.ts:10-13 — `mapIcon` 为 `LabIcon`，`name: '@jupyterlab/geojson-extension:map'`。
- F-024: packages/geojson-extension/jupyterlab_geojson/__init__.py:4-8 — `_jupyter_labextension_paths()` 返回 `src: labextension`、`dest: '@jupyterlab/geojson-extension'`。

## 三、vega3-extension

- F-025: packages/vega3-extension/package.json:2-3 — npm 包名 `@jupyterlab/vega3-extension`，版本 `3.3.0`。
- F-026: packages/vega3-extension/package.json:85-86 — `jupyterlab.mimeExtension: true`，`outputDir: jupyterlab_vega3/labextension`。
- F-027: packages/vega3-extension/package.json:60 — 运行时依赖 `vega-embed: 3.9.2`。
- F-028: packages/vega3-extension/src/index.ts:35 — 导出 `VEGA_MIME_TYPE = 'application/vnd.vega.v3+json'`。
- F-029: packages/vega3-extension/src/index.ts:43 — 导出 `VEGALITE_MIME_TYPE = 'application/vnd.vegalite.v2+json'`。
- F-030: packages/vega3-extension/src/index.ts:17-27 — 定义 `VEGA_COMMON_CLASS`、`VEGA_CLASS`、`VEGALITE_CLASS` 三个 CSS class 常量。
- F-031: packages/vega3-extension/src/index.ts:48-60 — `RenderedVega3` 类实现 `IRenderMime.IRenderer`，构造时根据 mimeType 追加 Vega 或 Vega-Lite 的 CSS class。
- F-032: packages/vega3-extension/src/index.ts:65-102 — `renderModel()` 读取 `model.metadata[this._mimeType].embed_options`，经 `resolver.resolveUrl('')`/`getDownloadUrl` 构造 vega loader 的 `baseURL`，再调用 `vegaEmbed(el, data, options)`。
- F-033: packages/vega3-extension/src/index.ts:89-97 — 若 `model.data` 缺 `image/png`，调用 `result.view.toImageURL('png')` 并把 base64 数据写回 `model.setData({ data })`。
- F-034: packages/vega3-extension/src/index.ts:111-115 — `rendererFactory` 声明 `safe: true`、`mimeTypes: [VEGA_MIME_TYPE, VEGALITE_MIME_TYPE]`。
- F-035: packages/vega3-extension/src/index.ts:117-121 — 导出扩展 `id: '@jupyterlab/vega3-extension:factory'`、`rank: 59`、`dataType: 'json'`。
- F-036: packages/vega3-extension/src/index.ts:122-135 — `documentWidgetFactoryOptions` 定义 `Vega 3`（primaryFileType `vega3`）与 `Vega-Lite 2`（primaryFileType `vega-lite2`）两个文档工厂。
- F-037: packages/vega3-extension/src/index.ts:136-149 — `fileTypes` 定义 `vega3`（`.vg`, `.vg.json`, `.vega`）与 `vega-lite2`（`.vl`, `.vl.json`, `.vegalite`），共用 `jp-MaterialIcon jp-VegaIcon`。

## 四、katex-extension

- F-038: packages/katex-extension/package.json:2-3 — npm 包名 `@jupyterlab/katex-extension`，版本 `3.4.0`。
- F-039: packages/katex-extension/package.json:92-99 — `jupyterlab.extension: true`、`outputDir: jupyterlab_katex/labextension`、`schemaDir: schema`，`disabledExtensions` 列出 `@jupyterlab/mathjax-extension:plugin` 与 `@jupyterlab/mathjax2-extension:plugin`。
- F-040: packages/katex-extension/src/index.ts:17 — 常量 `katexPluginId = '@jupyterlab/katex-extension:plugin'`。
- F-041: packages/katex-extension/src/index.ts:28-35 — `KatexTypesetter` 类实现 `IRenderMime.ILatexTypesetter`，`typeset(node)` 调用 `renderMathInElement(node, options)`。
- F-042: packages/katex-extension/src/index.ts:40-68 — `katexPlugin` 为 `JupyterFrontEndPlugin<ILatexTypesetter>`，`requires: [ISettingRegistry]`、`provides: ILatexTypesetter`、`autoStart: true`。
- F-043: packages/katex-extension/src/index.ts:51-54 — `updateSettings` 读取 `settings.get('macros').composite` 写入 `options.macros`。
- F-044: packages/katex-extension/src/autorender.ts:199-211 — `defaultAutoRenderOptions` 声明 5 组 `delimiters`（`$$`/`\\[`/`\\(`/`$`/`\begin{equation}`）与 `ignoredTags: ['script','noscript','style','textarea','pre','code']`。
- F-045: packages/katex-extension/src/autorender.ts:12-36 — `findEndOfMath` 遍历文本计数 `{}` 层级以定位右定界符。
- F-046: packages/katex-extension/src/autorender.ts:38-113 — `splitAtDelimiters` 把文本切分为 `text`/`math` 片段（`IParseData`）。
- F-047: packages/katex-extension/src/autorender.ts:132-158 — `renderMathInText` 对 math 片段调用 `katex.render(math, span, optionsCopy)`，失败时回退插入原始 `rawData`。
- F-048: packages/katex-extension/src/autorender.ts:213-222 — 导出 `renderMathInElement(elem, options)`，合并默认项后递归 `renderElem` 处理文本节点与元素节点。
- F-049: packages/katex-extension/schema/plugin.json:5-10 — 设置 schema 定义 `macros` 属性（`type: object`，`default: {}`）。

## 五、mathjax2-extension

- F-050: packages/mathjax2-extension/package.json:2-3 — npm 包名 `@jupyterlab/mathjax2-extension`，版本 `4.0.0`。
- F-051: packages/mathjax2-extension/package.json:95-97 — `jupyterlab.extension: true`，`outputDir: jupyterlab_mathjax2/labextension`。
- F-052: packages/mathjax2-extension/src/index.ts:23-27 — 插件对象 `id: '@jupyterlab/mathjax2-extension:plugin'`、`autoStart: true`、`provides: ILatexTypesetter`、`optional: [ITranslator]`。
- F-053: packages/mathjax2-extension/src/index.ts:34-48 — `activate` 从 `PageConfig.getOption` 读取 `fullMathjaxUrl` 与 `mathjaxConfig`，`url` 缺失时抛 `Error`。
- F-054: packages/mathjax2-extension/src/typesetter.ts:15-22 — `MathJaxTypesetter` 类实现 `IRenderMime.ILatexTypesetter`，构造时保存 `url` 与 `config`。
- F-055: packages/mathjax2-extension/src/typesetter.ts:32-49 — `typeset(node)` 首次调用触发 `_init()`，随后 `MathJax.Hub.Queue(['Typeset', MathJax.Hub, node])` 并 `Require` AMSmath 后 `resetEquationNumbers()`。
- F-056: packages/mathjax2-extension/src/typesetter.ts:54-65 — `_init()` 向 `head` 注入 `<script src="${url}?config=${config}&delayStartupUntil=configured">`。
- F-057: packages/mathjax2-extension/src/typesetter.ts:70-100 — `_onLoad()` 调用 `MathJax.Hub.Config` 设置 `tex2jax.inlineMath`/`displayMath`、`displayAlign: 'center'`、`CommonHTML`/`HTML-CSS` 行断行与字体、`skipStartupTypeset: true`。
- F-058: packages/mathjax2-extension/src/typesetter.ts:102-113 — 注册 `StartupHook('End Config')` 删除 `MathJax_Hover_Arrow:hover span` 与 `MathJax_MenuClose:hover span` 样式，规避 Chromium 性能问题。

## 六、fasta-extension

- F-059: packages/fasta-extension/package.json:2-3 — npm 包名 `@jupyterlab/fasta-extension`，版本 `3.3.0`。
- F-060: packages/fasta-extension/package.json:88-90 — `jupyterlab.mimeExtension: true`，`outputDir: jupyterlab_fasta/labextension`。
- F-061: packages/fasta-extension/src/index.ts:14-27 — `TYPES` 映射两个 MIME：`application/vnd.fasta.fasta`（Fasta，`.fasta`/`.fa`）与 `application/vnd.clustal.clustal`（Clustal，`.clustal`/`.aln`），reader 取自 `msa.io`。
- F-062: packages/fasta-extension/src/index.ts:32-54 — `RenderedData` 类实现 `IRenderMime.IRenderer`，构造时以 `new msa.msa({ el, vis })` 初始化 MSA 视图。
- F-063: packages/fasta-extension/src/index.ts:72-81 — `renderModel()` 用 `TYPES[this._mimeType].reader.parse(data)` 解析序列并 `this.msa.seqs.reset(seqs)`、`this.msa.render()`。
- F-064: packages/fasta-extension/src/index.ts:119-123 — `rendererFactory` 声明 `safe: false`、`mimeTypes: Object.keys(TYPES)`。
- F-065: packages/fasta-extension/src/index.ts:125-147 — `extensions` 由 `Object.keys(TYPES).map()` 生成，`id: jupyterlab-fasta:${name}`、`rank: 0`、`dataType: 'string'`，并声明 `fileTypes` 与 `documentWidgetFactoryOptions`。

## 七、Python 扩展包装与构建

- F-066: packages/geojson-extension/pyproject.toml:1-3 — 构建系统为 `hatchling.build`，requires 含 `hatchling>=1.5.0`、`jupyterlab>=4.0.0,<5`、`hatch-nodejs-version`。
- F-067: packages/geojson-extension/pyproject.toml:6-9 — Python 包名 `jupyterlab_geojson`，`requires-python = ">=3.8"`。
- F-068: packages/geojson-extension/pyproject.toml:28-29 — `[tool.hatch.version] source = "nodejs"`，版本号取自 Node 包。
- F-069: packages/geojson-extension/pyproject.toml:38-40 — wheel `shared-data` 把 `jupyterlab_geojson/labextension` 映射到 `share/jupyter/labextensions/@jupyterlab/geojson-extension`，并同步 `install.json`。
- F-070: packages/geojson-extension/pyproject.toml:45-52 — `hatch-jupyter-builder` hook 以 `npm_builder` 构建，`ensured-targets` 检查 `static/style.js` 与 `package.json`。
