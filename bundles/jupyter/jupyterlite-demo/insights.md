---
type: Insights
title: jupyterlite-demo 架构洞察
description: 从源码事实中提炼的4个核心洞察，以及知识地图和文档分组设计
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T18:00:00+08:00'
status: stable
sources:
- ../../../../../external/libs/jupyter/demo/README.md
okf_version: '0.2'
tags:
- insights
- architecture
---

# I 阶段：架构洞察与知识结构设计

## 核心洞察（四元组）

### 洞察 I-1：Demo 仓库的本质是「依赖清单+内容目录+CI配置」三件套

- **陈述**：JupyterLite Demo 仓库不是一个代码库，而是一个「最小可行部署模板」——它只包含三个必要元素：①requirements.txt 声明站点预装的包和内核；②content/ 目录存放随站点分发的笔记本和数据文件；③.github/workflows/deploy.yml 定义构建和部署流水线。没有 Python/JS 源码、没有自定义扩展代码。
- **证据**：F-001~F-010（项目元信息）、F-011~F-021（依赖清单）、F-028~F-030（目录结构）
- **反常识**：传统 Jupyter 部署教程通常强调「安装 Jupyter→配置服务器→启动内核」的复杂流程，但 JupyterLite Demo 仓库完全不需要服务器端代码——构建产物是纯静态文件，可以部署到任意静态托管服务（GitHub Pages、Vercel、CDN）。这意味着"部署 Jupyter"的门槛被降低到了"写一个 requirements.txt + 放几个 ipynb 文件"。
- **行动**：教程应该围绕这三件套组织，重点讲解 dependencies 声明策略、content 目录布局、CI/CD 配置方法，而非源码分析。

### 洞察 I-2：`%pip install` 是浏览器端包管理的核心机制

- **陈述**：Demo 中几乎所有 Pyodide 示例笔记本都在第一个代码单元使用 `%pip install -q <package>` 在浏览器端动态安装第三方包，而非依赖构建时预装。预装在 requirements.txt 中的包（jupyterlite-core、pyodide-kernel 等）是站点级内核和扩展；用户代码依赖的数据分析/可视化库（altair、plotly、folium、bqplot 等）则在 Notebook 内通过 %pip 按需安装。
- **证据**：F-056、F-058、F-060、F-061、F-064、F-067、F-071、F-082（所有 pyodide 笔记本均使用 %pip install）
- **反常识**：传统 Python 环境中 pip install 是系统级操作，需要网络和磁盘权限，且一次安装全局可用。JupyterLite 的 `%pip install` 在浏览器中运行，包被下载到浏览器内存/IndexedDB，仅当前会话有效，刷新页面可能需要重新安装。这改变了"依赖管理"的心智模型——从"环境预装"变为"Notebook 自声明依赖"。
- **行动**：教程需要专门章节讲解浏览器端 %pip 的工作原理、限制（纯 Python wheel 才能安装）、预装 vs 按需安装的策略选择。

### 洞察 I-3：内容目录遵循「分层展示」模式——从基础语法到领域应用

- **陈述**：Demo 的笔记本组织呈现清晰的三层递进结构：①根级 3 个笔记本（python/javascript/p5）展示三种内核的基础语法和核心能力；②pyodide/ 下 8 个笔记本按可视化/交互/渲染分类展示 Python 生态库的使用；③pyodide/pyb2d/ 下 8 个物理引擎和游戏示例展示高级/趣味应用。数据文件（data/）作为共享资源被各笔记本引用。
- **证据**：F-028~F-030（目录结构）、F-031~F-055（根级笔记本和数据）、F-056~F-081（pyodide 示例分类）
- **反常识**：很多人以为 JupyterLite 只是一个"能在浏览器跑 Python 的玩具"，但 Demo 展示了完整的科学计算栈——从基础的 numpy/matplotlib 到交互式图表（plotly/bqplot）、地图（folium/ipyleaflet）、物理模拟（pyb2d）、创意编程（p5.js/ipycanvas）。这说明 JupyterLite 的 Pyodide 内核已经能承载相当复杂的计算任务。
- **行动**：教程应该按「内核基础→数据可视化→交互式控件→高级应用」的学习路径组织概念文档，每个示例文档对应一类笔记本的使用模式。

### 洞察 I-4：站点配置极简但关键——disabledExtensions 控制用户体验

- **陈述**：整个站点的配置仅通过 repl/jupyter-lite.json 一个文件完成，唯一配置项是 disabledExtensions 数组，禁用了 drawio、kernel-spy 和 tour 三个扩展。配置文件遵循 jupyter-lite-schema-version 0。其余配置全部走 Jupyter 约定的默认值。
- **证据**：F-007、F-024~F-026（jupyter-lite.json 配置）
- **反常识**：很多框架的 demo 项目包含大量配置文件来"展示功能"，但 JupyterLite Demo 的配置策略是"最小化配置"——只禁用已知有问题的扩展（jupyterlab-tour 有 bug，见 F-026），其余全部走默认值。这说明 JupyterLite 的"约定优于配置"设计哲学：默认配置即可获得良好体验。
- **行动**：教程需要讲解 jupyter-lite.json 的配置项（disabledExtensions、settings overrides 等），同时强调"默认即可用"的设计理念，避免过度配置。

## 知识地图

### 文档分组与学习路径

```
入门层（概念 00-01）
├── 00-introduction.md          → I-1：JupyterLite Demo 是什么、能做什么
└── 01-demo-overview.md         → I-1+I-3：仓库结构、三件套模式、笔记本分层

核心层（概念 02-05）
├── 02-site-configuration.md    → I-4：jupyter-lite.json 配置、扩展管理
├── 03-kernel-ecosystem.md      → I-1+I-2：三种内核对比、内核选择策略
├── 04-content-and-data.md      → I-3：content/ 目录布局、数据文件组织
└── 05-pyodide-libraries.md     → I-2+I-3：%pip install 机制、预装 vs 按需

进阶层（概念 06-07）
├── 06-deployment-github-pages.md → I-1：CI/CD 流水线、GitHub Pages 部署
└── 07-customization-guide.md     → 综合：主题/语言包/扩展定制
```

### 事实覆盖映射

| 概念文档 | 覆盖事实 |
|----------|----------|
| 00-introduction | F-001~F-006, F-088~F-089 |
| 01-demo-overview | F-007~F-010, F-028~F-030, F-048~F-055 |
| 02-site-configuration | F-024~F-026, F-007 |
| 03-kernel-ecosystem | F-011~F-017, F-031~F-047 |
| 04-content-and-data | F-023, F-048~F-052, F-076~F-078 |
| 05-pyodide-libraries | F-020~F-021, F-056~F-082, F-090 |
| 06-deployment-github-pages | F-005, F-009~F-010, F-022~F-023, F-083~F-086 |
| 07-customization-guide | F-018~F-019, F-027, F-087 |

### 示例文档规划

| 示例文档 | 对应笔记本 | 核心技能 |
|----------|------------|----------|
| 01-first-deployment | 部署流程 | 从零到部署的完整步骤 |
| 02-python-basics | python.ipynb | Pyodide 基础、display、magics |
| 03-data-visualization | altair+matplotlib+plotly | 数据可视化三剑客 |
| 04-interactive-widgets | interactive-widgets.ipynb | ipywidgets+bqplot 交互 |
| 05-interactive-maps | folium+ipyleaflet | 地图可视化 |
| 06-creative-coding | p5+ipycanvas+pyb2d | 创意编程与物理模拟 |
| 07-custom-demo-site | 综合定制 | 自定义主题/扩展/配置 |
