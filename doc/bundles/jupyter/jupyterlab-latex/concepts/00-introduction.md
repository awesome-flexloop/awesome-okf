---
type: concept
title: "jupyterlab-latex 简介"
description: "了解 jupyterlab-latex 在 JupyterLab 生态中的定位——LaTeX 实时编辑扩展，支持自动编译预览、双向 SyncTeX、富编辑工具栏与多引擎支持"
tags: [jupyter, jupyterlab, latex, extension, introduction, overview, live-preview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: package-json
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/package.json"
    title: "package.json"
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/README.md"
    title: "README.md"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: build-py
    resource: "/references/build-py-source.md"
    title: "编译处理器源码"
---

# jupyterlab-latex 简介

`jupyterlab-latex` 是 JupyterLab 的官方扩展，为 `.tex` 文件提供**实时编译预览**能力——打开 LaTeX 文档后，每次保存自动编译为 PDF 并在拆分面板中显示预览，编译错误时自动弹出错误面板。

## 它是什么

安装此扩展后，在 JupyterLab 中打开 `.tex` 文件时：

- 编辑器工具栏自动出现 LaTeX 专用按钮（Preview、格式化、列表、表格、绘图等）
- 点击 Preview 按钮或右键选择 "Show LaTeX Preview"，即可在右侧面板实时预览 PDF
- 每次保存 `.tex` 文件自动触发重新编译，PDF 实时更新
- 编译失败时在底部面板显示错误日志，支持过滤/完整/JSON 三种查看模式
- Shift+Ctrl/Cmd+Click 可在编辑器和 PDF 之间双向跳转定位（SyncTeX）
- Launcher 中提供 "LaTeX File" 快捷入口新建 `.tex` 文件
- 菜单栏新增 LaTeX 菜单，提供数学常数和符号快捷插入

## 它不是什么

此扩展专注于 **LaTeX 文档的编辑体验**，不提供以下能力：

- ❌ 不提供 LaTeX 发行版本身（需系统安装 TeX Live/MiKTeX/Tectonic）
- ❌ 不提供 BibTeX 图形化管理界面
- ❌ 不支持协作编辑冲突解决（虽然兼容 jupyter-collaboration 的 drive 前缀剥离）
- ❌ 不是 WYSIWYG 编辑器（仍是源码编辑 + PDF 预览的分离模式）

## 双组件架构

jupyterlab-latex 采用**前后端双插件**架构：

| 组件 | 技术栈 | 职责 |
|------|--------|------|
| **Lab 扩展（前端）** | TypeScript + React + Lumino + pdfjs-dist | PDF 渲染控件、编辑工具栏、SyncTeX 客户端、错误面板、菜单命令 |
| **Server 扩展（后端）** | Python + Tornado + traitlets | LaTeX 编译调度、BibTeX 自动检测、SyncTeX 命令执行、输出过滤、配置管理 |

前端导出两个 JupyterLab 插件：`latexPlugin`（LaTeX 编辑功能）和 `pdfjsPlugin`（PDF 文档查看器工厂）。PDF 查看器通过 `pdfjs-dist` 2.4.456 实现，注册为独立的 `'PDFJS'` 文档工厂，支持以 base64 模型读取 PDF 文件。

## 项目信息

| 属性 | 值 |
|------|-----|
| npm 包名 | `@jupyterlab/latex` |
| Python 包名 | `jupyterlab_latex` |
| npm 版本 | **4.4.0** |
| 许可证 | BSD-3-Clause |
| 作者 | Jupyter Development Team |
| 仓库 | https://github.com/jupyterlab/jupyterlab-latex |
| JupyterLab 要求 | ≥ 4.0 |
| Python 要求 | ≥ 3.8 |
| 构建系统 | Hatchling + hatch-jupyter-builder |
| PDF 渲染 | pdfjs-dist 2.4.456（bundled singleton） |

## 核心模块速览

| 模块 | 核心类/函数 | 职责 |
|------|-----------|------|
| `src/index.ts` | `latexPlugin`, `pdfjsPlugin`, CommandIDs, EditorToolbarPanel | 插件注册、命令定义、工具栏注入、菜单系统 |
| `src/pdf.ts` | `PDFJSViewer`, `PDFJSDocumentWidget`, `PDFJSViewerFactory` | PDF 渲染、缩放翻页、点击定位 |
| `src/pagenumber.tsx` | `PageNumberComponent`, `PageNumberWidget` | 页码导航 React 组件 |
| `src/error.tsx` | `ErrorPanel`, `LatexError` | 编译错误面板、日志级别切换 |
| `src/style/icons.ts` | 6个 LabIcon 实例 | PDF 工具栏图标 |
| `jupyterlab_latex/__init__.py` | `load_jupyter_server_extension` | URL 路由注册、handler 挂载 |
| `jupyterlab_latex/build.py` | `LatexBuildHandler`, `latex_cleanup` | LaTeX 编译、输出过滤、临时文件清理 |
| `jupyterlab_latex/config.py` | `LatexConfig` | traitlets 配置类（8个配置项） |
| `jupyterlab_latex/synctex.py` | `LatexSynctexHandler`, `parse_synctex_response` | SyncTeX 双向同步、响应解析 |
| `jupyterlab_latex/util.py` | `run_command_sync`, `run_command_async` | 跨平台子进程执行 |

## 生态位置

jupyterlab-latex 是 JupyterLab 扩展系统中**文档类型扩展**的典型示例：它不通过 IDrive 挂载远程文件系统（如 jupyterlab-github），而是注册新的文档工厂（PDFJS）和编辑器扩展（EditorToolbarPanel），并通过自定义服务端 API 端点（`/latex/build`、`/latex/synctex`）实现服务端能力。这种模式适用于需要在 JupyterLab 中集成本地命令行工具（编译器、解释器等）的场景。

---

**下一步阅读：**
- [安装与快速上手](01-getting-started.md) — 5分钟安装并预览第一个 LaTeX 文档
- [架构总览](02-architecture-overview.md) — 理解双插件架构、数据流和 HTTP API
