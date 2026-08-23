---
type: Concept
title: FASTA 生物序列渲染器
description: @jupyterlab/fasta-extension 扩展实现，使用 MSA（Multiple Sequence Alignment）查看器渲染 FASTA/Clustal 格式的生物序列数据
tags: [fasta, bioinformatics, msa, sequence-alignment, mime-renderer]
sources:
  - id: fasta-index
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/src/index.ts
    title: fasta-extension/src/index.ts
  - id: fasta-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/package.json
    title: fasta-extension/package.json
  - id: fasta-init
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/jupyterlab_fasta/__init__.py
    title: jupyterlab_fasta/__init__.py
  - id: fasta-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/pyproject.toml
    title: fasta-extension/pyproject.toml
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# FASTA 生物序列渲染器

FASTA 扩展（@jupyterlab/fasta-extension）为 JupyterLab 提供生物序列数据的可视化渲染能力，支持 FASTA 和 Clustal 两种格式，使用 [MSA（Multiple Sequence Alignment）Viewer](https://github.com/wilzbach/msa) 库展示多序列比对结果。

## 基本信息

| 属性 | 值 |
|------|-----|
| npm 包名 | @jupyterlab/fasta-extension |
| 版本 | 3.3.0 |
| Python 包名 | jupyterlab_fasta |
| MIME 类型 | `application/vnd.fasta.fasta`、`application/vnd.clustal.clustal` |
| 文件扩展名 | `.fasta`、`.fa`、`.clustal`、`.aln` |
| dataType | `'string'` |
| safe | `false` |
| CSS 类名 | `jp-RenderedMSA` |

## 支持的格式

### FASTA 格式

FASTA 是生物信息学中最常用的序列格式，以 `>` 开头的行描述序列名称，后续行为序列数据：

```
>seq1 sequence description
ACGTACGTACGTACGTACGT
>seq2 another sequence
ACGTACGTACGTACGTACGT
```

### Clustal 格式

Clustal 是多序列比对输出格式，包含序列比对结果和保守性标记：

```
CLUSTAL W (1.83) multiple sequence alignment

seq1      ACGTACGTACGT
seq2      ACGT-CGTACGT
          * ****  ****
```

## 核心实现

### TYPES 映射表

FASTA 扩展使用 TYPES 对象映射表管理两种格式：[^fasta-index]

```typescript
const TYPES: {
  [key: string]: { name: string; extensions: string[]; reader: any };
} = {
  'application/vnd.fasta.fasta': {
    name: 'Fasta',
    extensions: ['.fasta', '.fa'],
    reader: msa.io.fasta        // FASTA 解析器
  },
  'application/vnd.clustal.clustal': {
    name: 'Clustal',
    extensions: ['.clustal', '.aln'],
    reader: msa.io.clustal      // Clustal 解析器
  }
};
```

通过 `Object.keys(TYPES)` 动态获取支持的 MIME 类型列表，每个类型对应不同的解析器（`msa.io.fasta` 或 `msa.io.clustal`）。

### RenderedData Widget

渲染器 Widget 在构造函数中初始化 MSA 查看器：[^fasta-index]

```typescript
export class RenderedData extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this._parser = TYPES[this._mimeType].reader;  // 根据 MIME 类型选择解析器
    this.addClass('jp-RenderedMSA');

    // 创建 MSA 查看器
    const msaDiv = document.createElement('div');
    this.msa = new msa.msa({
      el: msaDiv,
      vis: {
        sequences: true,        // 显示序列
        markers: true,          // 显示标记
        metacell: false,        // 不显示元单元格
        conserv: false,         // 不显示保守性
        overviewbox: true,      // 显示概览框
        seqlogo: false,         // 不显示序列 logo
        gapHeader: false,       // 不显示间隙头
        leftHeader: true        // 显示左侧头（序列名）
      }
    });

    this.node.appendChild(msaDiv);
  }
```

### MSA 可视化配置

`vis` 配置项控制 MSA 查看器的显示元素：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `sequences` | true | 显示序列行 |
| `markers` | true | 显示位置标记 |
| `metacell` | false | 隐藏元数据单元格 |
| `conserv` | false | 隐藏保守性轨道 |
| `overviewbox` | true | 显示鸟瞰概览框（导航用） |
| `seqlogo` | false | 隐藏序列 logo |
| `gapHeader` | false | 隐藏间隙列头 |
| `leftHeader` | true | 显示序列名称列头 |

### renderModel 方法

```typescript
renderModel(model: IRenderMime.IMimeModel): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    const data = model.data[this._mimeType];     // 获取字符串数据
    const seqs = this._parser.parse(data);       // 使用对应解析器解析
    this.msa.seqs.reset(seqs);                   // 加载序列到 MSA
    this.msa.render();                           // 渲染
    this.update();                               // 触发尺寸更新
    resolve();
  });
}
```

渲染流程：获取字符串数据 → 使用对应的解析器（FASTA/Clustal）解析为序列对象 → 加载到 MSA 查看器 → 渲染 → 更新尺寸。

### 尺寸自适应

FASTA 渲染器重写了 `onUpdateRequest` 方法来处理 MSA 对齐区域的宽度自适应：

```typescript
protected onUpdateRequest(msg: Message): void {
  if (this.isVisible) {
    const newWidth =
      this.node.getBoundingClientRect().width -
      this.msa.g.zoomer.getLeftBlockWidth();     // 减去左侧序列名宽度
    this.msa.g.zoomer.set('alignmentWidth', newWidth);
  }
}
```

当 Widget 尺寸变化时，计算可用宽度（容器宽度减去左侧序列名区域宽度），动态设置 MSA 对齐区域的宽度。

### 菜单禁用注释

代码中有一段被注释掉的菜单创建代码：

```typescript
// The menu doesn't work correctly in the absolutely positioned panel, so
// disabling it for now. This appears to be fixed in msa master, but the npm
// package hasn't been updated in a year. See
// https://github.com/wilzbach/msa/issues/226.
/*
this.menu = new msa.menu.defaultmenu({msa: this.msa});
this.msa.addView('menu', this.menu);
this.node.appendChild(this.menu.el);
*/
```

MSA 内置菜单在 JupyterLab 的绝对定位面板中无法正常工作，npm 包未更新修复此问题，因此菜单功能被禁用。

### 扩展描述符

FASTA 为每个 MIME 类型生成一个独立的扩展描述符：[^fasta-index]

```typescript
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
```

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| @jlab-contrib/msa | ^1.1.2 | MSA 多序列比对查看器（核心渲染引擎） |
| @jupyterlab/rendermime-interfaces | ^3.0.0 \|\| ^3.8.0 | MIME 渲染器接口 |
| @lumino/widgets | ^1.0.0 \|\| ^2.1.0 | Widget 基类 |
| @lumino/messaging | ^1.0.0 \|\| ^2.0.0 | 消息系统 |

## 安装与使用

```bash
pip install jupyterlab-fasta
```

安装后，在 JupyterLab 中：
1. 双击 `.fasta` 或 `.fa` 文件，MSA 查看器自动打开
2. 在 Notebook 中输出 FASTA 格式数据（设置 MIME 类型为 `application/vnd.fasta.fasta`），自动渲染为多序列比对视图

## 相关概念

- [MIME 渲染器开发模式](/concepts/02-mime-renderer-pattern.md)
- [GeoJSON 地理数据渲染器](/concepts/05-geojson-renderer.md)
- [Vega/Vega-Lite 可视化渲染器](/concepts/07-vega-renderer.md)
- [IRenderMime 核心 API 参考](/references/rendermime-interfaces-api.md)
