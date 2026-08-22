---
type: Facts
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- latex
- pdf
- synctex
- pdfjs
- extension
sources:
- ../../../../../external/libs/jupyter/jupyterlab-latex/package.json
- ../../../../../external/libs/jupyter/jupyterlab-latex/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlab-latex/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlab-latex/src/pdf.ts
- ../../../../../external/libs/jupyter/jupyterlab-latex/src/style/icons.ts
- ../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/build.py
- ../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/config.py
- ../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/synctex.py
- ../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/util.py
- ../../../../../external/libs/jupyter/jupyterlab-latex/schema/plugin.json
title: jupyterlab-latex 源码事实清单
---

# jupyterlab-latex Facts

## 项目元数据

- F-001: package.json:2 — npm 包名为 `@jupyterlab/latex`。
- F-002: package.json:3 — 版本号为 `4.4.0`。
- F-003: package.json:4 — 描述为 "JupyterLab extension for running LaTeX"。
- F-004: package.json:15 — 许可证为 BSD-3-Clause。
- F-005: package.json:16-18 — 作者为 Jupyter Development Team。
- F-006: pyproject.toml — Python 后端包名为 `jupyterlab-latex`，提供 Tornado API handlers。

## 项目结构

- F-007: src/index.ts — 插件主入口，包含两个插件：LaTeX 编辑器扩展和 PDF.js 查看器。
- F-008: src/pdf.ts — `PDFJSViewer` 和 `PDFJSDocumentWidget`，基于 PDF.js 的 PDF 渲染器。
- F-009: src/pagenumber.tsx — 页码导航 React 组件。
- F-010: src/error.tsx — LaTeX 编译错误面板。
- F-011: src/style/icons.ts — PDF 工具栏图标定义。
- F-012: jupyterlab_latex/build.py — Python 后端，`LatexBuildHandler` 处理 LaTeX 编译请求。
- F-013: jupyterlab_latex/config.py — `LatexConfig` 使用 traitlets 定义可配置选项。
- F-014: jupyterlab_latex/synctex.py — SyncTeX 同步处理逻辑。
- F-015: jupyterlab_latex/util.py — 命令执行工具函数。
- F-016: schema/plugin.json — JupyterLab 设置 schema（synctex 开关）。
- F-017: style/icons/ — 16 个 SVG 图标（粗体/斜体/下划线/对齐/列表/表格/缩放等）。

## 核心依赖

- F-018: package.json:66-80 — 依赖 JupyterLab 4 核心包：application、apputils、codeeditor、coreutils、docmanager、docregistry、filebrowser、fileeditor、launcher、mainmenu、notebook、services、settingregistry、statedb、ui-components。
- F-019: package.json:81-86 — 依赖 Lumino 包：coreutils、disposable、domutils、messaging、signaling(2.1.1)、widgets。
- F-020: package.json:87 — 使用 `pdfjs-dist: 2.4.456` 作为 PDF 渲染引擎，配置为 bundled singleton。
- F-021: package.json:88-89 — 使用 React 18.2.0。
- F-022: package.json:90 — 依赖 `yjs: ^13.6.1`（协作编辑兼容）。

## 插件结构

- F-023: src/index.ts:128-143 — `latexPlugin` 插件 ID 为 `@jupyterlab/latex:plugin`，autoStart: true。
- F-024: src/index.ts:130-138 — latexPlugin 需要：IDefaultFileBrowser、IDocumentManager、IEditorTracker、ILabShell、ILayoutRestorer、IPDFJSTracker、ISettingRegistry、IStateDB。
- F-025: src/index.ts:1368-1374 — `pdfjsPlugin` 插件 ID 为 `@jupyterlab/pdfjs-extension:plugin`，提供 IPDFJSTracker，注册 PDF 文件查看器工厂。
- F-026: src/index.ts:82-84 — `IPDFJSTracker` Token 标识 PDF 查看器追踪器。
- F-027: src/index.ts:1421 — 默认导出两个插件的数组 `[latexPlugin, pdfjsPlugin]`。

## 命令系统

- F-028: src/index.ts:89-111 — CommandIDs 命名空间定义 5 个命令：openLatexPreview、synctexEdit、synctexView、createNew、createTable。
- F-029: src/index.ts:974-987 — `latex:open-preview` 命令：对当前 .tex 文件打开实时预览，仅在 .tex 文件编辑器中可见。
- F-030: src/index.ts:98 — `latex:synctex-edit`：从 PDF 位置跳转到编辑器对应行。
- F-031: src/index.ts:103 — `latex:synctex-view`：从编辑器光标位置跳转到 PDF 对应页。
- F-032: src/index.ts:108 — `latex:create-new-latex-file`：创建新的 .tex 文件。
- F-033: src/index.ts:110 — `latex:create-table`：通过对话框输入行列数创建 LaTeX 表格。
- F-034: src/index.ts:1170-1182 — SyncTeX 双向导航绑定快捷键 `Accel Shift X`（Ctrl+Shift+X / Cmd+Shift+X），分别在编辑器和 PDF 查看器中生效。
- F-035: src/index.ts:1187-1326 — LaTeX 菜单系统包含 Constants（π、γ、φ）和 Symbols（数学符号：≤、≥、⊂、⊃、∈、∪、∩、¬、∧、∨ 等）两个子菜单。
- F-036: src/index.ts:1328-1350 — `generateTable()` 函数生成 LaTeX tabular 环境代码，支持自定义行列数，自动添加 \hline 和单元格占位符。

## 实时预览机制

- F-037: src/index.ts:283-423 — `openPreview()` 函数：保存 .tex 文件时触发 LaTeX 编译，编译成功后以 split-right 模式打开/刷新 PDF 查看器。
- F-038: src/index.ts:364-392 — 文件保存时的编译流程：使用 `pending` 标志防止并发编译；调用 `/latex/build/{path}` 端点；成功则 revert PDF context（重新加载），失败则显示错误面板。
- F-039: src/index.ts:305-320 — PDF 以 `split-right` 模式打开，即编辑器和 PDF 左右分栏显示。
- F-040: src/index.ts:322-334 — PDF 反向搜索（PDF→编辑器）：通过 `positionRequested` 信号触发，由于 SyncTeX x 坐标不可靠，强制设置 x:0 仅同步行位置。
- F-041: src/index.ts:336-361 — 编译错误处理：404 错误提示服务器扩展未安装；其他错误创建 ErrorPanel 以 split-bottom 模式显示。
- F-042: src/index.ts:1436 — 使用 `Set<string>` 缓存当前活跃的预览路径，防止重复打开。
- F-043: src/index.ts:413 — 预览状态通过 IStateDB 持久化，重启 JupyterLab 后可恢复活跃预览。
- F-044: src/index.ts:935-944 — 初始化时从 StateDB 恢复之前活跃的预览。

## SyncTeX 双向同步

- F-045: src/index.ts:154-170 — `latexBuildRequest()` 调用 `/latex/build/{path}?synctex={0|1}` 端点触发编译。
- F-046: src/index.ts:181-202 — `synctexEditRequest()`：PDF→编辑器，传递 page/x/y 参数，返回 line/column。
- F-047: src/index.ts:213-235 — `synctexViewRequest()`：编辑器→PDF，传递 line/column 参数（转为1-based），返回 page/x/y。
- F-048: src/index.ts:1141 — PDF 正向搜索时 x 坐标强制设为 0，因 SyncTeX x 坐标映射不可靠。
- F-049: src/index.ts:273 — SyncTeX 功能可通过设置（`synctex` 配置项）开关，默认启用。

## 编辑器工具栏扩展

- F-050: src/index.ts:425-929 — `EditorToolbarPanel` 实现 `DocumentRegistry.IWidgetExtension`，为 .tex 文件编辑器工具栏插入 LaTeX 编辑按钮。
- F-051: src/index.ts:892-908 — 工具栏按钮仅在文件扩展名为 .tex 时插入，包括：预览、上下标、分数、对齐（左/中/右）、粗体/斜体/下划线、列表（有序/无序）、表格、图表。
- F-052: src/index.ts:452-472 — `replaceSelection(action)` 通用函数：对选中文本包装 `\command{text}`，无选中则弹出输入对话框。
- F-053: src/index.ts:596-743 — 插入图表功能支持 6 种类型：数学表达式、数据文件、散点图、柱状图、等高线图、参数图，使用 pgfplots/tikzpicture 模板代码。
- F-054: src/index.ts:931 — 工具栏扩展注册到 'Editor' widget factory。

## PDF 查看器

- F-055: src/pdf.ts:41 — PDF MIME 类型为 `application/pdf`。
- F-056: src/pdf.ts:61 — 缩放步进因子为 1.1。
- F-057: src/pdf.ts:66-71 — 缩放范围为 0.25x 到 10.0x。
- F-058: src/pdf.ts:76 — 滚动边距为 72px（1 英寸 @ 72dpi）。
- F-059: src/index.ts:1381-1386 — PDF 查看器工厂名称为 `'PDFJS'`，modelName 为 `'base64'`，readOnly: true。
- F-060: src/pdf.ts — PDFJSViewer 包含 Toolbar：下载、适应页面、上一页/下一页、放大/缩小、页码输入。

## 后端编译配置

- F-061: jupyterlab_latex/config.py:11 — 默认 LaTeX 引擎为 `xelatex`（可配置）。
- F-062: jupyterlab_latex/config.py:20 — shell_escape 默认为 `'restricted'`，支持 allow/disallow/restricted 三档。
- F-063: jupyterlab_latex/config.py:27 — 默认编译次数为 1（run_times）。
- F-064: jupyterlab_latex/config.py:13 — BibTeX 默认不禁用（disable_bibtex=False），自动检测 .bib 文件决定是否运行 bibtex。
- F-065: jupyterlab_latex/config.py:15 — 默认 BibTeX 命令为 `bibtex`。
- F-066: jupyterlab_latex/build.py:112-119 — 支持 Tectonic 引擎（现代 Rust 实现的 LaTeX 引擎），使用 `--outfmt=pdf` 和 `--synctex` 参数。
- F-067: jupyterlab_latex/build.py:121-130 — TeX Live 模式编译命令：`{engine} -interaction=nonstopmode -halt-on-error -file-line-error -synctex={0|1} {filename}`。
- F-068: jupyterlab_latex/build.py:138-151 — BibTeX 编译序列：latex → bibtex → latex → latex（需要两次 latex 以解决交叉引用）。
- F-069: jupyterlab_latex/build.py:14-61 — `latex_cleanup()` 上下文管理器：可选择清理编译过程中产生的临时文件，支持白名单和灰名单机制。
