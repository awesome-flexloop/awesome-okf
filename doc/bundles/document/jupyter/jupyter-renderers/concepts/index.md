---
type: Index
title: Concepts 索引
description: jupyter-renderers 概念文档索引
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# Concepts 概念文档

| 编号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [简介](00-introduction.md) | 项目概述、5个扩展包列表、安装方式、核心依赖 |
| 01 | [Monorepo 架构](01-monorepo-architecture.md) | Lerna + Yarn Workspaces、目录结构、tsc references、构建流水线 |
| 02 | [MIME 渲染器模式](02-mime-renderer-pattern.md) | 四要素模式：MIME类型常量、Widget类、渲染工厂、扩展描述符 |
| 03 | [扩展类型](03-extension-types.md) | MIME文件渲染器 vs 应用扩展、ILatexTypesetter、disabledExtensions互斥 |
| 04 | [FASTA 渲染器](04-fasta-renderer.md) | 生物序列可视化、MSA Viewer、TYPES映射表、尺寸自适应 |
| 05 | [GeoJSON 渲染器](05-geojson-renderer.md) | Leaflet地图、底图切换、API Key、sanitize弹窗、滚轮适配、dispose清理 |
| 06 | [数学公式渲染器](06-math-renderers.md) | KaTeX vs MathJax2、ILatexTypesetter接口、autorender算法、异步加载、宏配置 |
| 07 | [Vega/Vega-Lite 渲染器](07-vega-renderer.md) | vega-embed、异步渲染、IResolver URL解析、PNG回退、双文档工厂 |
| 08 | [Python 打包](08-python-packaging.md) | hatchling + hatch-jupyter-builder、_jupyter_labextension_paths、wheel构建 |

## 学习路径建议

1. **入门路径**：00 → 01 → 02 → 03 → 08（理解架构和模式后再看具体实现）
2. **MIME 渲染器路径**：02 → 04 → 05 → 07（对比三个渲染器的共性与差异）
3. **应用扩展路径**：03 → 06（理解 ILatexTypesetter 服务模式）
4. **打包发布路径**：01 → 08（从 monorepo 构建到 wheel 发布）

```{toctree}
:maxdepth: 7

00-introduction
01-monorepo-architecture
02-mime-renderer-pattern
03-extension-types
04-fasta-renderer
05-geojson-renderer
06-math-renderers
07-vega-renderer
08-python-packaging
```
