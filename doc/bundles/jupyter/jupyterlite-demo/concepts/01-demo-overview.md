---
type: Concept
title: Demo 仓库结构与三件套模式
description: JupyterLite Demo 仓库的目录结构、核心文件职责，以及「依赖+内容+CI」三件套部署模式
tags: [structure, repository, layout, content-directory, three-piece-pattern]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta
    resource: /references/repo-readme.md
    title: JupyterLite Demo 仓库元信源
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 仓库目录总览

JupyterLite Demo 仓库采用极简结构，总共不到 20 个核心文件：

```
demo/
├── .github/
│   └── workflows/
│       └── deploy.yml          # ③ CI/CD 部署流水线
├── content/                    # ② 内容目录
│   ├── data/                   #    数据文件
│   ├── pyodide/                #    Pyodide 内核示例
│   │   └── pyb2d/              #    物理引擎示例
│   ├── javascript.ipynb
│   ├── p5.ipynb
│   └── python.ipynb
├── repl/
│   └── jupyter-lite.json       # 站点配置
├── .nojekyll                   # GitHub Pages 标记
├── LICENSE
├── README.md
└── requirements.txt            # ① 依赖声明
```

## 三件套模式

JupyterLite Demo 的核心设计模式是**三件套**：依赖声明 + 内容目录 + 部署配置。理解这三者的职责和关系，就能掌握 JupyterLite 站点的构建原理。

### ① 依赖声明（requirements.txt）

requirements.txt 告诉 `jupyter lite build` 命令需要将哪些 Python 包打入站点：

- **核心组件**：jupyterlite-core、jupyterlab、notebook——构成站点的基础框架
- **内核包**：pyodide-kernel、javascript-kernel、p5-kernel——提供不同语言的执行引擎
- **扩展包**：fasta/geojson 渲染器、语言包、主题——增强 JupyterLab 功能
- **控件/绘图库**：ipywidgets、ipympl、ipycanvas、plotly、bqplot——预装到内核环境

构建时，这些包被安装到构建环境中，JupyterLite 会自动发现其中的 JupyterLab 扩展和内核规格，将对应的前端资源（JS/CSS/WASM）打包到静态站点中。

### ② 内容目录（content/）

content/ 目录存放随站点分发的文件，构建时被复制到站点的虚拟文件系统中：

- **根级笔记本**：python.ipynb、javascript.ipynb、p5.ipynb——三种内核的入门示例
- **data/ 子目录**：CSV、GeoJSON、FASTA、PNG 等数据文件，笔记本可直接读取
- **pyodide/ 子目录**：更丰富的 Pyodide 内核示例，按主题分类（可视化、地图、交互等）
- **pyodide/pyb2d/**：Box2D 物理引擎的高级示例和游戏

构建时 README.md 也被复制到 content/ 目录（由 CI 中的 `cp README.md content` 完成）。

### ③ 部署配置（deploy.yml + jupyter-lite.json）

- **deploy.yml**：GitHub Actions 工作流，自动化执行「安装依赖→构建站点→上传产物→部署 Pages」
- **jupyter-lite.json**：站点运行时配置（如禁用不需要的扩展），控制 JupyterLab 的行为

## 三层笔记本结构

content/ 目录下的笔记本呈现清晰的**三层递进**结构：

### 第一层：内核基础（根目录，3 个笔记本）

面向初次接触 JupyterLite 的用户，每个笔记本对应一种内核：

- `python.ipynb`：Pyodide 内核完整功能演示（变量、函数、错误处理、display、magics、网络请求）
- `javascript.ipynb`：JavaScript 内核基础（console 输出、异步操作、数学公式）
- `p5.ipynb`：p5.js 创意编程（setup/draw 函数、%show 渲染）

### 第二层：Python 生态库（pyodide/，8 个笔记本）

面向想用 Python 做数据分析/可视化的用户：

- 数据可视化：altair（声明式统计图表）、matplotlib（基础绘图）、plotly（交互式图表）
- 交互式控件：interactive-widgets（ipywidgets + bqplot）
- 地图可视化：folium（简单地图）、ipyleaflet（地图+图表联动）
- 画布绘图：ipycanvas（康威生命游戏）
- 自定义渲染：renderers（FASTA/GeoJSON MIME 类型）

### 第三层：高级应用（pyodide/pyb2d/，8 个笔记本）

面向想探索 JupyterLite 高级能力的用户：

- 物理模拟：0_tutorial、color_mixing、gauss_machine、newtons_cradle（牛顿摆）
- 游戏示例：angry_shapes（愤怒的小鸟）、billiard（台球）、goo（粘粘世界）、rocket（火箭）

### 共享资源：data/

data/ 目录作为所有笔记本共享的数据资源层，包含 CSV、GeoJSON、FASTA、JSON 等格式的示例数据。

## 构建产物结构

执行 `jupyter lite build --contents content --output-dir dist` 后，dist/ 目录包含：

```
dist/
├── lab/                # JupyterLab 应用
├── repl/               # REPL 应用
├── tree/               # 文件浏览器
├── Pyodide/            # Pyodide WASM 文件和包
├── @jupyterlite/       # JupyterLite 内核和服务
├── files/              # content/ 目录的文件（用户可见）
├── index.html          # 入口页面（重定向到 lab/ 或 repl/）
├── jupyter-lite.json   # 构建生成的运行时配置
└── service-worker.js   # Service Worker（离线缓存）
```

## 相关概念

- [JupyterLite Demo 简介](/concepts/00-introduction.md)
- [站点配置详解](/concepts/02-site-configuration.md)
- [三大内核生态对比](/concepts/03-kernel-ecosystem.md)
- [内容目录与数据文件组织](/concepts/04-content-and-data.md)
