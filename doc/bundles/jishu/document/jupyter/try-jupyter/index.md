---
type: bundle
okf_version: "0.2"
title: "Try Jupyter"
description: "Try Jupyter是基于JupyterLite构建的浏览器端Jupyter体验站点，提供Python/C++/R/SQLite多内核notebook环境，零安装在浏览器中运行。本教程覆盖从本地构建到多内核配置、UI测试、GitHub Pages部署的完整知识体系。"
tags: [jupyter, jupyterlite, try-jupyter, pyodide, xeus, wasm, browser-jupyter, notebook, github-pages, pixi]
bundle_name: "try-jupyter"
version: "0.1"
language: zh-CN
license: CC-BY-4.0
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: official-repo
    title: "try-jupyter GitHub"
    uri: "https://github.com/jupyter/try-jupyter"
  - id: official-site
    title: "Try Jupyter!"
    uri: "https://jupyter.org/try-jupyter"
  - id: jupyterlite-docs
    title: "JupyterLite Documentation"
    uri: "https://jupyterlite.readthedocs.io"
  - id: source-root
    resource: "../../../../../external/libs/jupyter/try-jupyter"
    title: "try-jupyter/ 源码目录"
---

# Try Jupyter

> 基于 JupyterLite 的浏览器端 Jupyter 体验站点——零安装、多语言内核、静态部署。

## 概述

Try Jupyter 是 [Project Jupyter](https://jupyter.org) 官方的"try it"入口站点，部署在 [jupyter.org/try-jupyter](https://jupyter.org/try-jupyter)。它使用 [JupyterLite](https://jupyterlite.readthedocs.io) 技术将完整的 JupyterLab 环境编译为纯静态文件（HTML + JavaScript + WebAssembly），用户打开浏览器即可使用 Python、C++、R、SQLite 等多语言 Notebook，无需安装任何软件。

- ✅ **零安装**：浏览器即开即用，不需要本地Python/Jupyter
- ✅ **多语言内核**：Python（Pyodide + Xeus-Python）、C++23、R、SQLite 共5个内核
- ✅ **科学计算**：NumPy、Matplotlib、SciPy、ipywidgets、plotly 等预装
- ✅ **交互式可视化**：bqplot、ipycanvas、ipyleaflet、ipympl
- ✅ **浏览器终端**：WASM终端，预安装Git、Vim、Nano
- ✅ **多语言界面**：英语/法语/中文
- ✅ **Playwright E2E测试**：每个notebook自动执行验证
- ✅ **GitHub Pages部署**：静态站点，CI/CD自动化

## 快速开始

```bash
# 安装pixi后
git clone https://github.com/jupyter/try-jupyter.git
cd try-jupyter
pixi install
pixi run build && pixi run filter-kernels
pixi run python -m http.server 8000 --directory dist
# 浏览器打开 http://localhost:8000/lab/index.html
```

→ 更多详情见 [快速开始](concepts/01-getting-started.md)

## 核心架构

```
┌─────────────────────────────────────────────┐
│                用户浏览器                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │JupyterLab│  │Notebook7 │  │ Terminal  │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       └─────────────┼─────────────┘         │
│            ┌────────┴────────┐              │
│            │  JupyterLite    │              │
│            │     Core        │              │
│            └──┬───┬───┬───┬──┘              │
│         ┌─────┘   │   │   └──────┐         │
│         ↓         ↓   ↓          ↓         │
│     ┌──────┐┌──────┐┌────┐┌──────────┐    │
│     │Pyodide││Xeus- ││R  ││ SQLite   │    │
│     │Python││Python││   ││          │    │
│     └──────┘│ Cpp  │└────┘└──────────┘    │
│             └──────┘                        │
│                   WebAssembly               │
└─────────────────────────────────────────────┘
                ↑ 静态文件
        GitHub Pages / ReadTheDocs
```

## 文档导航

### 📚 概念文档（按学习路径）

| 章节 | 内容 |
|------|------|
| [00 项目概述](concepts/00-introduction.md) | 是什么、核心特性、技术栈、仓库结构 |
| [01 快速开始](concepts/01-getting-started.md) | 安装pixi、构建站点、本地预览、可用任务一览 |
| [02 架构总览](concepts/02-architecture-overview.md) | 双内核体系（Pyodide+Xeus）、静态站点生成、配置驱动、禁用扩展策略 |
| [03 配置系统](concepts/03-configuration-system.md) | jupyter-lite.json、jupyter_lite_config.json、cockle终端配置、REPL覆盖 |
| [04 内核生态](concepts/04-kernel-ecosystem.md) | Pyodide vs Xeus、4个environment-*.yml、内核白名单过滤 |
| [05 构建管线](concepts/05-build-pipeline.md) | Pixi任务编排、6个构建任务、BeautifulSoup后处理脚本 |
| [06 Notebook与数据](concepts/06-notebooks-and-content.md) | 7个notebook详解、8个数据文件、文件查看器扩展 |
| [07 UI测试框架](concepts/07-ui-testing.md) | Playwright E2E、fixtures设计、cell执行监控、stderr检测、失败重试 |
| [08 部署](concepts/08-deployment.md) | GitHub Actions三阶段流水线、GitHub Pages、ReadTheDocs PR预览 |
| [09 终端支持](concepts/09-terminal-support.md) | Cockle WASM终端、预安装包、别名、Git环境变量 |

→ [完整概念索引](concepts/index.md)

### 🧪 可运行示例

| 示例 | 内容 |
|------|------|
| [01 本地构建与预览](examples/01-local-build.md) | 从零开始安装pixi、构建、预览的完整步骤 |
| [02 自定义内核环境](examples/02-custom-kernel.md) | 添加Julia内核、修改包依赖、移除不需要的内核 |
| [03 添加新Notebook](examples/03-add-notebook.md) | 在线编辑notebook、注册已知警告、通过E2E测试 |

→ [完整示例索引](examples/index.md)

### 📖 源码信源

所有API和配置描述均可溯源至源码信源文档：

| 信源 | 覆盖范围 |
|------|---------|
| [pyproject.toml](references/pyproject-source.md) | 项目元数据、30+依赖包、6个pixi任务、pytest配置 |
| [配置文件](references/config-source.md) | 4个JSON配置文件完整字段解析 |
| [构建脚本](references/scripts-source.md) | add_plausible.py + filter_xeus_kernels.py 逻辑解析 |
| [UI测试框架](references/test-source.md) | conftest.py + test_notebooks.py + utils.py 完整API |
| [CI/CD工作流](references/ci-source.md) | deploy.yml + rtd-preview.yml + .readthedocs.yml 流水线 |

→ [信源索引](references/index.md)

## 项目信息

| 属性 | 值 |
|------|---|
| 项目名 | `try-jupyter` |
| 作者 | Project Jupyter (`jupyter@googlegroups.com`) |
| 核心框架 | JupyterLite 0.8.x |
| JupyterLab | ≥4.6.0,<5 |
| Notebook | ≥7.6.0,<8 |
| Python | ≥3.12（构建环境） |
| Node.js | ≥22 |
| 包管理 | Pixi（conda-forge） |
| 测试 | Playwright + pytest |
| 部署 | GitHub Pages |
| 预览 | ReadTheDocs |
| 许可证 | BSD-3-Clause（源码）/ CC-BY-4.0（本文档） |
| 源码路径 | `external/libs/jupyter/try-jupyter/` |

## 预装Notebook一览

| Notebook | 内核 | 内容 |
|----------|------|------|
| Intro.ipynb | Python | JupyterLite入门介绍 |
| Lorenz.ipynb | Python | 洛伦兹吸引子（混沌理论+3D可视化） |
| cpp.ipynb | C++23 | C++基础语法 |
| cpp-third-party-libs.ipynb | C++23 | xtensor/xsimd/symengine等第三方库 |
| cpp-tiny-ray-tracer.ipynb | C++23 | 光线追踪渲染器 |
| r.ipynb | R | R语言+ggplot2可视化 |
| sqlite.ipynb | SQLite | SQL查询演示 |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
