---
type: OKF
title: JupyterLite Demo 教程
description: JupyterLite 官方演示仓库的系统化教程，涵盖站点结构、三大内核、%pip包管理、数据可视化、交互式控件、GitHub Pages部署与自定义定制
tags: [jupyterlite, jupyter, demo, pyodide, wasm, github-pages, notebook, deployment, visualization, p5js]
okf_version: "0.2"
version: "0.8.0"
source: https://github.com/jupyterlite/demo
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite Demo 教程

JupyterLite Demo 是 [JupyterLite](https://jupyterlite.readthedocs.io/) 的官方演示站点部署模板，展示了如何将 Jupyter 环境完全部署在浏览器中——无需服务器、无需安装，打开网页即可使用完整的 JupyterLab。

本教程基于对官方 Demo 仓库（jupyterlite/demo）的系统化分析，讲解 JupyterLite 站点的部署配置、三大内核（Pyodide/JavaScript/p5.js）、浏览器端包管理、数据可视化、交互式控件、以及站点定制方法。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-JupyterLite Demo 简介](concepts/00-introduction.md) — 是什么、核心特性、与传统Jupyter的区别
- [01-Demo仓库结构与三件套模式](concepts/01-demo-overview.md) — 依赖+内容+CI三件套、三层笔记本结构
- [02-站点配置详解](concepts/02-site-configuration.md) — jupyter-lite.json、扩展管理、配置项
- [03-三大内核生态对比](concepts/03-kernel-ecosystem.md) — Pyodide/JS/p5 内核特性与选择策略
- [04-内容目录与数据文件组织](concepts/04-content-and-data.md) — content/布局、数据共享、MIME渲染
- [05-Pyodide生态库与%pip安装](concepts/05-pyodide-libraries.md) — 浏览器端pip、预装vs按需、可视化库模式
- [06-GitHub Pages部署流水线](concepts/06-deployment-github-pages.md) — CI/CD、构建参数、本地预览
- [07-自定义Demo站点指南](concepts/07-customization-guide.md) — 主题、扩展、语言包、品牌定制

### [实践示例](examples/index.md)
- [01-从零部署到GitHub Pages](examples/01-first-deployment.md) — 10分钟完成第一个站点
- [02-Python内核基础使用](examples/02-python-basics.md) — 基础语法、display、magics、网络请求
- [03-数据可视化实战](examples/03-data-visualization.md) — Matplotlib/Altair/Plotly三大库
- [04-交互式控件与图表](examples/04-interactive-widgets.md) — ipywidgets+bqplot交互
- [05-交互式地图可视化](examples/05-interactive-maps.md) — folium+ipyleaflet地图
- [06-创意编程与物理模拟](examples/06-creative-coding.md) — p5.js+ipycanvas+pyb2d
- [07-构建自定义Demo站点](examples/07-custom-demo-site.md) — 完整定制流程

### [信源参考](references/index.md)
- [仓库元信源](references/repo-readme.md) — 版本、目录结构、核心文件
- [依赖配置信源](references/requirements-source.md) — 所有包版本与用途
- [站点配置信源](references/config-source.md) — jupyter-lite.json字段
- [部署流水线信源](references/deploy-workflow-source.md) — GitHub Actions配置
- [笔记本目录信源](references/notebook-catalog.md) — 所有示例笔记本索引

## 🚀 快速体验

在线演示：[jupyterlite.github.io/demo](https://jupyterlite.github.io/demo)

本地构建：
```bash
pip install jupyterlite-core jupyterlite-pyodide-kernel jupyterlab
mkdir content && echo 'print("Hello JupyterLite!")' > content/hello.ipynb
jupyter lite build --contents content --output-dir dist
jupyter lite serve --output-dir dist
# 访问 http://localhost:8000
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 零后端 | 所有计算在浏览器 WebAssembly 中运行 |
| 📦 静态部署 | 部署到 GitHub Pages、Vercel、任意 CDN |
| 🐍 三大内核 | Pyodide(Python)、JavaScript、p5.js 开箱即用 |
| 📊 科学计算 | numpy/pandas/matplotlib/altair/plotly 等 |
| 🎛️ 富交互 | ipywidgets、bqplot、ipyleaflet、ipycanvas |
| 🎨 可定制 | 主题、语言包、扩展、配置灵活可配 |
| 💾 本地持久化 | IndexedDB 存储文件，支持离线使用 |

## 🏗️ 三件套架构

JupyterLite Demo 采用极简的「三件套」部署模式：

```
┌─────────────────────────────────────────┐
│  ① requirements.txt（依赖声明）          │
│  jupyterlite-core + 内核 + 扩展 + 主题   │
├─────────────────────────────────────────┤
│  ② content/（内容目录）                  │
│  笔记本(.ipynb) + 数据文件(.csv/.json)   │
├─────────────────────────────────────────┤
│  ③ .github/workflows/deploy.yml（CI/CD） │
│  安装依赖 → 构建 → 部署 GitHub Pages     │
└─────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门体验**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-仓库结构](concepts/01-demo-overview.md)，理解三件套模式
2. **动手部署**：跟着 [01-从零部署](examples/01-first-deployment.md) 创建第一个站点
3. **Python 基础**：学习 [02-Python基础](examples/02-python-basics.md) 掌握内核基础操作
4. **数据可视化**：跟着 [03-数据可视化](examples/03-data-visualization.md) 实践三大图表库
5. **交互控件**：学习 [04-交互式控件](examples/04-interactive-widgets.md) 和 [05-地图可视化](examples/05-interactive-maps.md)
6. **创意编程**：探索 [06-创意编程](examples/06-creative-coding.md) 的 p5.js 和物理模拟
7. **定制站点**：阅读 [06-部署流水线](concepts/06-deployment-github-pages.md) 和 [07-自定义指南](concepts/07-customization-guide.md)，跟着 [07-构建自定义站点](examples/07-custom-demo-site.md) 打造自己的站点

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
