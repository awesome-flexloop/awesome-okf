---
type: Index
title: jupyter-renderers 教程索引
description: JupyterLab 官方 MIME 渲染器扩展集合源码学习教程索引
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# jupyter-renderers 教程

> 学习源码：[external/libs/jupyter/jupyter-renderers](../../../../external/libs/jupyter/jupyter-renderers/)

jupyter-renderers 是 JupyterLab 官方维护的 MIME 渲染器扩展集合，包含 FASTA 生物序列、GeoJSON 地理数据、KaTeX/MathJax2 数学公式、Vega/Vega-Lite 可视化五个扩展包。本教程从源码出发，系统性地讲解 MIME 渲染器和应用扩展的开发模式。

## 📚 概念文档（Concepts）

| 编号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [简介](concepts/00-introduction.md) | 项目概述、扩展包列表、安装方式、核心依赖 |
| 01 | [Monorepo 架构](concepts/01-monorepo-architecture.md) | Lerna + Yarn Workspaces、目录结构、构建流水线、Python wheel 打包 |
| 02 | [MIME 渲染器模式](concepts/02-mime-renderer-pattern.md) | 四要素模式：MIME类型、Widget类、渲染工厂、扩展描述符 |
| 03 | [扩展类型](concepts/03-extension-types.md) | MIME 渲染器 vs 应用扩展、ILatexTypesetter、互斥机制 |
| 04 | [FASTA 渲染器](concepts/04-fasta-renderer.md) | 生物序列可视化、MSA Viewer、多格式解析、尺寸自适应 |
| 05 | [GeoJSON 渲染器](concepts/05-geojson-renderer.md) | Leaflet 地图、底图切换、API Key 管理、属性弹窗、滚轮适配、模糊搜索 |
| 06 | [数学公式渲染器](concepts/06-math-renderers.md) | KaTeX vs MathJax2 对比、ILatexTypesetter、自动渲染算法、异步加载、宏配置 |
| 07 | [Vega/Vega-Lite 渲染器](concepts/07-vega-renderer.md) | 声明式可视化、vega-embed、异步渲染、URL解析器、PNG回退 |
| 08 | [Python 打包](concepts/08-python-packaging.md) | 预构建扩展、hatch-jupyter-builder、_jupyter_labextension_paths、wheel构建 |

## 🛠️ 示例教程（Examples）

| 编号 | 文档 | 内容 |
|------|------|------|
| 01 | [开发自定义 MIME 渲染器](examples/01-custom-mime-renderer.md) | 从零开发 CSV 表格渲染器，完整演示四要素模式 |
| 02 | [自定义 LaTeX 排版器](examples/02-custom-latex-typesetter.md) | 开发 ILatexTypesetter 应用扩展，异步加载模式、互斥机制 |

## 📖 参考文档（References）

| 文档 | 内容 |
|------|------|
| [IRenderMime API 参考](references/rendermime-interfaces-api.md) | IRendererFactory、IRenderer、IExtension、IOptions、IMimeModel 核心接口 |
| [扩展配置参考](references/extension-config-reference.md) | mimeExtension vs extension、rank、safe、dataType、fileTypes、documentWidgetFactoryOptions |
| [Python 入口点参考](references/python-entrypoint-reference.md) | _jupyter_labextension_paths、labextension 目录结构、pyproject.toml 配置 |

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
