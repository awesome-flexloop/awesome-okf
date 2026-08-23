---
type: Concept
title: "Try Jupyter 项目概述"
description: "Try Jupyter 是基于JupyterLite构建的浏览器端Jupyter体验站点，提供Python/C++/R/SQLite多内核notebook环境，无需安装即可在浏览器中运行。"
tags: [try-jupyter, jupyterlite, overview, browser-jupyter, introduction]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/try-jupyter/README.md"
    title: "try-jupyter/README.md"
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml 项目配置"
---

# Try Jupyter 项目概述

Try Jupyter 是 [Project Jupyter](https://jupyter.org) 官方提供的**浏览器端Jupyter体验站点**，部署在 [jupyter.org/try-jupyter](https://jupyter.org/try-jupyter)。它基于 [JupyterLite](https://jupyterlite.readthedocs.io) 技术，将完整的JupyterLab环境打包为静态网站，用户无需安装任何软件即可在浏览器中运行notebook。

## 核心特性

- **零安装**：打开浏览器即可使用，不需要本地安装Python或Jupyter
- **多语言内核**：同时支持 Python（Pyodide + Xeus-Python）、C++23、R、SQLite 共4种语言内核
- **丰富的科学计算库**：内置 NumPy、Matplotlib、SciPy、Pillow、ipywidgets、ipyleaflet、bqplot、plotly 等
- **交互式可视化**：支持 ipycanvas（Canvas绑定）、ipympl（Matplotlib交互）、ipyleaflet（地图）
- **终端支持**：浏览器内终端，预安装 Git、Vim、Nano、tree 等工具
- **多语言界面**：内置英语、法语、中文语言包
- **文件查看器**：支持 GeoJSON、FASTA 等特殊数据格式查看
- **暗色主题**：内置 JupyterLab Night 暗色主题

## 项目定位

Try Jupyter 不是一个Python库或可安装包，而是一个**JupyterLite演示站点的配置仓库**。它的核心价值在于：

1. **展示JupyterLite能力**：作为Jupyter官方的"try it"入口，展示浏览器端Jupyter的完整能力
2. **教学与入门**：提供Intro等入门notebook，帮助新用户快速了解Jupyter生态
3. **多语言演示**：展示Xeus内核框架支持的多语言notebook能力
4. **配置参考**：为其他想要自建JupyterLite站点的开发者提供配置范本

## 技术栈概览

| 层面 | 技术 |
|------|------|
| 核心框架 | JupyterLite 0.8.x |
| 前端界面 | JupyterLab 4.6+, Notebook 7.6+ |
| Python内核 | Pyodide（CPython WASM）+ Xeus-Python |
| 多语言内核 | Xeus框架（C++/R/SQLite） |
| 包管理/任务编排 | Pixi（conda-forge） |
| 构建工具 | JupyterLite CLI (`jupyter lite build`) |
| 浏览器自动化 | Playwright |
| 测试框架 | pytest + pytest-playwright |
| 部署 | GitHub Pages |
| 预览环境 | ReadTheDocs |

## 站点访问

| 环境 | URL | 触发方式 |
|------|-----|---------|
| 正式站点 | https://jupyter.org/try-jupyter | main分支自动部署 |
| PR预览 | `https://try-jupyter--{PR号}.org.readthedocs.build/en/{PR号}` | PR打开时自动评论 |

## 仓库结构

```
try-jupyter/
├── content/              # 用户可见内容
│   ├── notebooks/        # 7个演示notebook
│   └── data/             # 示例数据文件
├── repl/                 # REPL模式配置
├── scripts/              # 构建后处理脚本
│   ├── add_plausible.py  # 注入分析代码
│   └── filter_xeus_kernels.py  # 过滤内核
├── ui-tests/             # Playwright E2E测试
├── environment-*.yml      # Xeus内核环境定义
├── jupyter-lite.json      # 站点主配置
├── jupyter_lite_config.json  # 构建配置
├── cockle-config-in.json  # 终端配置模板
└── pyproject.toml         # Pixi项目配置
```

→ 快速开始本地构建请阅读 [快速开始](01-getting-started.md)
→ 了解整体架构请阅读 [架构总览](02-architecture-overview.md)

## 相关概念

- [快速开始](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
- [配置系统](03-configuration-system.md)
