---
okf_version: "0.2"
type: bundle
title: "jupyterlab-latex"
description: "JupyterLab LaTeX 编辑扩展——为 .tex 文件提供实时编译预览、双向 SyncTeX 导航、富编辑工具栏和多 LaTeX 引擎支持，每次保存自动编译并在拆分面板中显示 PDF。"
---

# jupyterlab-latex

> JupyterLab 官方 LaTeX 编辑扩展：打开 .tex 文件自动编译为 PDF 实时预览，支持 SyncTeX 双向跳转、多引擎（XeLaTeX/pdfLaTeX/LuaLaTeX/Tectonic）和富编辑工具栏。

`jupyterlab-latex` 是 JupyterLab 的官方扩展，采用前后端双插件架构——前端通过 pdfjs-dist 渲染 PDF 预览并注入 LaTeX 编辑工具栏，后端通过 Tornado handler 调度 LaTeX 编译和 SyncTeX 同步。打开 `.tex` 文件后，每次保存自动触发编译，PDF 在右侧面板实时更新，编译错误时自动显示错误日志面板。

## 快速导航

### 📘 核心概念（8 篇）

**入门**
- [简介](concepts/00-introduction.md) — 扩展定位、双组件架构、核心模块速览、项目信息
- [安装与快速上手](concepts/01-getting-started.md) — pip/conda 安装、验证方法、第一个 LaTeX 文档

**核心**
- [架构总览](concepts/02-architecture-overview.md) — 双插件架构、前后端数据流、HTTP API 端点、文档工厂注册
- [LaTeX 编译流程](concepts/03-latex-compilation.md) — 命令序列构建、BibTeX 多轮编译、输出过滤、临时文件清理
- [PDF 查看器](concepts/04-pdf-viewer.md) — pdfjs-dist 渲染管线、base64→Blob 转换、缩放翻页、工具栏
- [SyncTeX 双向同步](concepts/05-synctex-sync.md) — 正向/反向搜索、坐标系统转换、CLI 命令解析

**进阶**
- [编辑工具栏与快捷操作](concepts/06-editing-tools.md) — 格式化按钮、列表/表格/绘图插入、数学符号菜单、命令面板
- [配置指南](concepts/07-configuration.md) — 后端 traitlets 配置（引擎/BibTeX/shell escape/自定义命令）、前端 SyncTeX 开关
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（4 个）

- [基本使用示例](examples/01-basic-usage.md) — Hello World、数学公式、表格、参考文献的完整操作步骤
- [SyncTeX 双向跳转工作流](examples/02-synctex-workflow.md) — 正向/反向搜索操作、编辑-查看循环、大文档导航
- [配置示例](examples/03-configuration.md) — 中文文档、Tectonic、BibLaTeX+Biber、shell escape、latexmk 等8种场景
- [故障排查](examples/04-troubleshooting.md) — 安装、编译、SyncTeX、PDF 显示、性能问题的诊断与解决
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（8 个文件）

- [插件入口 src/index.ts](references/index-ts-source.md) — 双插件注册、命令系统、工具栏面板、SyncTeX、LaTeX 菜单（1448行）
- [PDF 查看器 src/pdf.ts](references/pdf-ts-source.md) — PDFJSViewer 渲染、缩放翻页、点击定位、工具栏（658行）
- [页码控件 src/pagenumber.tsx](references/pagenumber-tsx-source.md) — React 页码输入/跳转组件（199行）
- [错误面板 src/error.tsx](references/error-tsx-source.md) — 编译错误显示、三级日志过滤（114行）
- [LaTeX 编译 build.py](references/build-py-source.md) — 编译命令构建、BibTeX 检测、输出过滤、清理（317行）
- [配置类 config.py](references/config-py-source.md) — traitlets 配置项（引擎、shell escape、run_times 等）（33行）
- [SyncTeX 同步 synctex.py](references/synctex-py-source.md) — 正向/反向同步、响应解析（233行）
- [命令执行 util.py](references/util-py-source.md) — 跨平台子进程（Windows 同步/Unix 异步）（62行）
- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| npm 版本 | **4.4.0** |
| JupyterLab 要求 | ≥ 4.0 |
| Python 要求 | ≥ 3.8 |
| 构建系统 | Hatchling + hatch-jupyter-builder |
| PDF 渲染 | pdfjs-dist 2.4.456（bundled singleton） |
| 前端依赖 | @jupyterlab/application, @jupyterlab/apputils, @jupyterlab/docregistry, @lumino/widgets, react 等 |
| 后端依赖 | jupyterlab≥4.0, notebook, tornado, traitlets |
| 许可证 | BSD-3-Clause |
| 作者 | Jupyter Development Team |
| 仓库 | https://github.com/jupyterlab/jupyterlab-latex |
| 源码路径 | `external/libs/jupyter/jupyterlab-latex/` |

## 核心特点

| 特点 | 说明 |
|------|------|
| **实时编译预览** | 保存 .tex 文件自动触发编译，PDF 在 split-right 面板实时更新 |
| **双向 SyncTeX** | 编辑器光标移动自动定位 PDF，Shift+Ctrl/Cmd+Click PDF 跳回编辑器对应行 |
| **多引擎支持** | 支持 XeLaTeX（默认）、pdfLaTeX、LuaLaTeX、Tectonic，可自定义命令参数 |
| **BibTeX 自动检测** | 检测 .bib 文件或 \bibliography 命令，自动执行 latex→bibtex→latex→latex 四遍编译 |
| **富编辑工具栏** | 粗体/斜体/下划线、上标/下标/分数、列表/表格、6种 pgfplots 绘图一键插入 |
| **数学符号菜单** | LaTeX 菜单提供常用希腊字母和数学符号快捷插入 |
| **错误面板** | 编译失败自动弹出底部面板，支持过滤/完整/JSON 三种错误查看模式 |
| **跨平台兼容** | Windows 自动回退到同步子进程执行，Unix/Linux/macOS 使用 Tornado 异步子进程 |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [安装与快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [LaTeX 编译流程](concepts/03-latex-compilation.md) → [PDF 查看器](concepts/04-pdf-viewer.md) → [SyncTeX 双向同步](concepts/05-synctex-sync.md)

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
