---
type: Concept
title: jupyter-renderers 简介
description: jupyter-renderers 是 JupyterLab 官方 MIME 渲染器扩展集合，以 Lerna monorepo 组织，提供 FASTA/GeoJSON/KaTeX/MathJax2/Vega3 五种常见格式的渲染能力
tags: [introduction, overview, mime-renderer]
sources:
  - id: readme
    resource: external/libs/jupyter/jupyter-renderers/README.md
    title: README.md
  - id: root-pkg
    resource: external/libs/jupyter/jupyter-renderers/package.json
    title: root package.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# jupyter-renderers 简介

jupyter-renderers 是 JupyterLab 官方维护的 [MIME 渲染器扩展](https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html#mime-renderer-extensions)集合，以 [Lerna](https://lerna.js.org/) monorepo 形式组织，为常见文件格式和 MIME 类型提供开箱即用的渲染能力。[^readme]

## 什么是 MIME 渲染器

MIME 渲染器（MIME Renderer Extension）是 JupyterLab 扩展的一种类型，负责将特定 MIME 类型的数据渲染为可视化 Widget。当 Notebook 输出或文件浏览器打开一个 JupyterLab 不原生支持的格式时，对应的 MIME 渲染器接管渲染工作。

例如，当用户打开一个 `.geojson` 文件时，JupyterLab 的 rendermime 注册表查找 `application/geo+json` MIME 类型对应的渲染器，调用 GeoJSON 扩展创建 Leaflet 地图 Widget 来展示地理数据。

## 包含的扩展包

| 包名 | npm 包名 | MIME 类型 | 文件扩展名 | 渲染内容 |
|------|---------|-----------|-----------|---------|
| fasta-extension | @jupyterlab/fasta-extension (v3.3.0) | `application/vnd.fasta.fasta` | `.fasta`, `.fa` | 生物序列多序列比对（MSA） |
| geojson-extension | @jupyterlab/geojson-extension (v3.4.0) | `application/geo+json` | `.geojson`, `.geo.json` | 地理数据交互式地图 |
| katex-extension | @jupyterlab/katex-extension (v3.4.0) | N/A（ILatexTypesetter） | N/A | KaTeX 数学公式排版 |
| mathjax2-extension | @jupyterlab/mathjax2-extension (v4.0.0) | N/A（ILatexTypesetter） | N/A | MathJax 2 数学公式排版 |
| vega3-extension | @jupyterlab/vega3-extension (v3.3.0) | `application/vnd.vega.v3+json`, `application/vnd.vegalite.v2+json` | `.vg`, `.vg.json`, `.vega`, `.vl`, `.vl.json`, `.vegalite` | Vega/Vega-Lite 可视化图表 |

## 两类扩展

jupyter-renderers 包含两种不同类型的 JupyterLab 扩展：

1. **MIME 渲染器扩展**（mimeExtension）：fasta、geojson、vega3——注册特定 MIME 类型的渲染工厂，在 Notebook 输出或文件查看器中渲染富媒体内容。
2. **应用服务扩展**（extension）：katex、mathjax2——提供 `ILatexTypesetter` 服务，替换 JupyterLab 默认的数学公式排版引擎。它们不渲染文件，而是作为全局服务被其他组件调用。

详见[扩展类型详解](/concepts/03-extension-types.md)。

## 安装

JupyterLab 3.0+ 支持预构建扩展，可直接通过 pip 安装：

```bash
pip install jupyterlab-fasta
pip install jupyterlab-geojson
pip install jupyterlab-katex
pip install jupyterlab-mathjax2
pip install jupyterlab-vega3
```

安装后重启 JupyterLab 即可使用，无需 Node.js 编译。

## 核心依赖

所有扩展共享以下核心依赖：[^root-pkg]

- **@jupyterlab/rendermime-interfaces**：MIME 渲染器接口定义（`IRenderer`、`IRendererFactory`、`IExtension` 等）
- **@lumino/widgets**：Widget 基类，提供 DOM 容器和生命周期管理
- **@lumino/messaging**：消息系统，用于处理 resize/show/update 等事件
- **TypeScript ~5.0.2**：开发语言
- **@jupyterlab/builder ^4.0.0**：扩展构建工具

## 相关概念

- [Monorepo 架构与构建系统](/concepts/01-monorepo-architecture.md)
- [MIME 渲染器开发模式](/concepts/02-mime-renderer-pattern.md)
- [扩展类型：MIME 渲染器 vs 应用扩展](/concepts/03-extension-types.md)
- [IRenderMime 核心 API 参考](/references/rendermime-interfaces-api.md)

[^readme]: 项目说明
[^root-pkg]: root package.json
