---
type: "index"
title: "JupyterLab Demo 演示环境教程"
description: "JupyterLab Demo 仓库源码学习教程——从Binder一键演示环境到配置化素材组装、扩展生态的系统化知识体系"
tags: [jupyterlab, demo, binder, reproducible, teaching, extension, notebook]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: "references/repo-readme.md", title: "README信源登记" }
  - { id: build-py, resource: "references/build-py-source.md", title: "build.py源码信源" }
  - { id: binder-config, resource: "references/binder-config-source.md", title: "Binder配置信源" }
  - { id: talks-yml, resource: "references/talks-yml-source.md", title: "talks.yml信源" }
  - { id: narrative, resource: "references/narrative-source.md", title: "Narrative演示脚本信源" }
  - { id: ci-workflow, resource: "references/ci-workflow-source.md", title: "CI工作流信源" }
  - { id: repo-url, resource: "https://github.com/jupyterlab/jupyterlab-demo", title: "GitHub仓库" }
  - { id: binder-url, resource: "https://mybinder.org/v2/gh/jupyterlab/jupyterlab-demo/master?urlpath=lab", title: "Binder在线体验" }
---

# JupyterLab Demo 演示环境教程

> 基于 jupyterlab-demo 仓库（BSD-3-Clause）的系统化学习教程——演示环境即代码（Demo as Code）的最佳实践

JupyterLab Demo 是 Jupyter 官方团队维护的演示仓库，它通过 Binder 实现了"点击链接即可获得完整演示环境"的零安装体验。这个仓库不仅是一个 JupyterLab 功能展示集，更是一个精心设计的**演示环境工程化模板**——通过 Binder 配置、构建脚本、YAML 声明式配置和工作区预设，将"演示"本身代码化、版本化、可复现。

本教程从仓库源码出发，系统讲解"演示环境即代码"的完整技术栈：Binder 环境配置、build.py 配置化素材组装、多内核多格式演示能力、工作区布局预设、以及 JupyterLab 扩展生态，帮助你理解如何构建自己的可复现演示环境。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [项目定位与设计理念](concepts/00-introduction.md) | "演示环境即代码"哲学、核心特性、Binder交付模式 |
| [仓库目录结构详解](concepts/01-repo-structure.md) | 配置层/构建层/素材层/输出层的四层分层架构 |

### 核心架构

| 文档 | 说明 |
|------|------|
| [Binder 环境配置三要素](concepts/02-binder-config.md) | environment.yml（依赖声明）+ postBuild（构建脚本）+ workspace.json（布局预设） |
| [build.py 与 talks.yml 配置化组装系统](concepts/03-build-system.md) | 声明式素材管理——files/folders/rename三种操作、四套预设场景、外部仓库自动克隆 |

### 演示内容

| 文档 | 说明 |
|------|------|
| [演示能力维度与多内核支持](concepts/04-demo-capabilities.md) | 多格式查看器（CSV/GeoJSON/FASTA/Vega-Lite）、多语言内核（Python/R/C++/Julia）、交互控件与实时协作 |
| [Notebook 示例解析](concepts/05-notebook-examples.md) | Data/Fasta/R/Lorenz 各 Notebook 详解，以及外部引入的pandas/bqplot/C++示例 |
| [数据文件与多格式查看器](concepts/06-data-files.md) | iris.csv、GeoJSON、FASTA、Vega-Lite、图片音视频的许可证来源与查看器特性 |

### 进阶主题

| 文档 | 说明 |
|------|------|
| [工作区布局与交互体验设计](concepts/07-workspace-layout.md) | Lumino Dock Panel布局模型、workspace.json配置、演示布局设计考量 |
| [插件架构与扩展生态](concepts/08-extension-demo.md) | "Everything is a Plugin"设计哲学、扩展类型与开发模式、fasta/draw.io案例 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [在 Binder 启动 JupyterLab 演示环境](examples/01-launch-binder.md) | 一键启动、预设布局体验、8步功能探索 |
| [创建自定义演讲配置](examples/02-custom-demo-talk.md) | 为特定受众定制演示——添加talks.yml配置、文件选择与友好命名 |
| [本地搭建演示环境](examples/03-local-setup.md) | Conda环境创建、构建脚本运行、离线演示准备 |
| [为演示添加自定义内容](examples/04-add-demo-content.md) | 添加Notebook/数据/脚本、依赖管理、文件命名最佳实践 |
| [开发 JupyterLab 扩展入门](examples/05-extension-dev.md) | cookiecutter模板、Hello World命令、核心API速查 |

### 信源登记簿

* [参考资料索引](references/index.md) — README、build.py、Binder配置、talks.yml、narrative脚本、CI工作流信源登记

## 学习路径建议

**体验者路径（5分钟快速上手）**：
```
00（设计理念）→ examples/01（Binder启动）→ 04（能力概览）
```

**使用者路径（本地搭建+自定义演示）**：
```
00 → 01（目录结构）→ examples/03（本地搭建）→ examples/02（自定义配置）→ examples/04（添加内容）
```

**架构理解路径（理解演示工程化）**：
```
00 → 01 → 02（Binder配置）→ 03（build系统）→ 07（工作区布局）→ 08（扩展生态）
```

**扩展开发者路径（开发JupyterLab扩展）**：
```
04（能力维度）→ 08（插件架构）→ examples/05（扩展开发入门）
```

## 源码版本

本教程基于 jupyterlab-demo 仓库（master分支，JupyterCon 2017/SciPy 2017 时期版本），源码路径：`external/libs/jupyter/jupyterlab-demo/`。

- 许可证：BSD-3-Clause（代码），数据文件各自遵循其许可证（CC0/CC-BY/NASA Public Domain/BSD-3等）
- Binder 环境：基于 Conda（conda-forge channels），Python 3.6 + JupyterLab 0.27
- 核心依赖：jupyterlab、ipykernel、r-irkernel、xeus-cling、bqplot、ipyleaflet、pandas、scikit-learn、matplotlib、scipy、jupyter-collaboration、jupyter-offlinenotebook、jupyterlab-fasta、jupyterlab-geojson
- 外部素材仓库（7个）：PythonDataScienceHandbook、Urban-Data-Challenge、Altair、TCGA Notebooks、QuantStack C++ Notebooks、Julia Notebooks
- 内置演示场景（4个）：test_talk、scipy2017-tutorial、jupytercon2017、demo（默认）
- 在线体验：https://mybinder.org/v2/gh/jupyterlab/jupyterlab-demo/master?urlpath=lab
- CI 测试：GitHub Actions 验证 Data.ipynb、Fasta.ipynb、R.ipynb 三个 Notebook

> ⚠️ **版本注意**：本仓库基于 JupyterLab 0.27（2017年版本），现代 JupyterLab 4.x 的扩展API已发生较大变化（特别是预构建扩展系统）。concepts/08 和 examples/05 中关于扩展开发的内容以现代 JupyterLab 4.x API 为准，而仓库本身的 fasta/geojson 扩展使用的是旧版API。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
