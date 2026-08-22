---
type: concept
title: "架构总览"
description: "jupyterlab-latex 的双插件架构、前后端数据流、HTTP API 端点、文档工厂注册与扩展生命周期"
tags: [architecture, dual-plugin, data-flow, http-api, document-factory, lifecycle]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-py
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/__init__.py"
    title: "__init__.py"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: pdf-ts
    resource: "/references/pdf-ts-source.md"
    title: "PDF查看器源码"
  - id: api-yaml
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/api/api.yaml"
    title: "OpenAPI 规范"
---

# 架构总览

jupyterlab-latex 采用**前后端分离的双插件架构**：前端是两个 JupyterLab 插件（LaTeX 编辑插件 + PDF 查看器插件），后端是一个 Jupyter Server 扩展（提供编译和 SyncTeX HTTP API）。

## 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    JupyterLab 前端                       │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │ latexPlugin  │    │ pdfjsPlugin  │                   │
│  │ (LaTeX编辑)   │◄──►│ (PDF查看器)   │                   │
│  │              │    │              │                   │
│  │ ┌──────────┐ │    │ ┌──────────┐ │                   │
│  │ │EditorTool│ │    │ │PDFJSViewer│ │                   │
│  │ │barPanel  │ │    │ │(pdfjs-dist)│ │                   │
│  │ └──────────┘ │    │ └──────────┘ │                   │
│  │ ┌──────────┐ │    │ ┌──────────┐ │                   │
│  │ │ErrorPanel│ │    │ │PageNumber│ │                   │
│  │ └──────────┘ │    │ └──────────┘ │                   │
│  │ ┌──────────┐ │    │ ┌──────────┐ │                   │
│  │ │Commmands │ │    │ │Toolbar   │ │                   │
│  │ │+Menus    │ │    │ └──────────┘ │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │ positionRequested │                           │
│         │ (SyncTeX反向)    │                           │
│         └────────┬─────────┘                           │
│                  │                                      │
│         ServerConnection.makeRequest                    │
└──────────────────┼──────────────────────────────────────┘
                   │ HTTP GET
                   ▼
┌─────────────────────────────────────────────────────────┐
│                  Jupyter Server 后端                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              URL Routing                         │    │
│  │  /latex/build/*  → LatexBuildHandler            │    │
│  │  /latex/synctex/* → LatexSynctexHandler         │    │
│  └──────────┬──────────────────────┬───────────────┘    │
│             ▼                      ▼                    │
│  ┌──────────────────┐   ┌──────────────────────┐       │
│  │LatexBuildHandler │   │LatexSynctexHandler   │       │
│  │                  │   │                      │       │
│  │build_tex_cmd_seq │   │build_synctex_cmd     │       │
│  │run_latex         │   │run_synctex           │       │
│  │filter_output     │   │parse_synctex_response│       │
│  │bib_condition     │   │                      │       │
│  └────────┬─────────┘   └──────────┬───────────┘       │
│           │                        │                    │
│           ▼                        ▼                    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  run_command (util.py)                          │    │
│  │  Unix: tornado.process.Subprocess (async)       │    │
│  │  Windows: subprocess.run (sync fallback)        │    │
│  └────────────────────┬────────────────────────────┘    │
│                       │                                  │
│                       ▼ 子进程调用                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  系统 LaTeX 工具链                               │    │
│  │  xelatex/pdflatex/lualatex/tectonic + bibtex    │    │
│  │  synctex                                         │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 前端双插件

### latexPlugin（`@jupyterlab/latex:plugin`）

核心 LaTeX 编辑功能插件，依赖 8 个必需服务和 3 个可选服务：

**必需依赖**：
- `IDefaultFileBrowser`：文件浏览器（用于新建文件的默认路径）
- `IDocumentManager`：文档管理器（查找/打开/关联 widget 与 context）
- `IEditorTracker`：编辑器追踪器（获取当前活动编辑器）
- `ILabShell`：Lab 外壳（添加面板到主区域）
- `ILayoutRestorer`：布局恢复（恢复 PDF 面板和状态）
- `IPDFJSTracker`：PDF 追踪器（查找 PDF widget 用于 SyncTeX）
- `ISettingRegistry`：设置注册表（读取 synctex 开关）
- `IStateDB`：状态数据库（保存/恢复活动预览路径）

**可选依赖**：
- `ILauncher`：启动器（注册新建 LaTeX 文件入口）
- `IMainMenu`：主菜单（添加 LaTeX 菜单）
- `ICommandPalette`：命令面板（注册命令）

### pdfjsPlugin（`@jupyterlab/pdfjs-extension:plugin`）

独立的 PDF 查看器插件，注册 `'PDFJS'` 文档工厂：

- **provides**：`IPDFJSTracker`（供 latexPlugin 注入使用）
- **工厂配置**：name=`'PDFJS'`，modelName=`'base64'`，fileTypes=`['PDF']`，readOnly=`true`
- 负责创建 `PDFJSDocumentWidget`，内含 PDFJSViewer（pdfjs-dist 渲染）和工具栏

## HTTP API 端点

后端注册两个 GET 端点（均需认证 `@web.authenticated`）：

### GET /latex/build/{filePath}

触发 LaTeX 编译。

**Query 参数**：
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `synctex` | int | 1 | 是否生成 SyncTeX 数据（1=是，0=否） |

**响应**：
| 状态码 | 说明 | 内容 |
|--------|------|------|
| 200 | 编译成功 | `"LaTeX compiled"` |
| 400 | 非 .tex 文件 | 错误消息字符串 |
| 403 | 文件不存在 | 错误消息字符串 |
| 500 | 编译错误 | JSON: `{fullMessage, errorOnlyMessage}` |

### GET /latex/synctex/{filePath}

SyncTeX 双向同步。

**Query 参数**（正向同步 .tex → PDF）：
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `line` | int | 1 | 编辑器行号（1-based） |
| `column` | int | 1 | 编辑器列号（1-based） |

**Query 参数**（反向同步 .pdf → .tex）：
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `page` | int | 1 | PDF 页码 |
| `x` | float | 0 | x 坐标（pt，72dpi） |
| `y` | float | 0 | y 坐标（pt，72dpi） |

**响应**：
| 状态码 | 说明 | 内容 |
|--------|------|------|
| 200 | 同步成功 | JSON: `{line, column, page, x, y}` |
| 400 | 文件类型错误 | 错误消息字符串 |
| 403 | 文件/.synctex.gz 不存在 | 错误消息字符串 |
| 500 | SyncTeX 执行错误 | 错误消息字符串 |

## 编译预览数据流

```
用户保存 .tex 文件
    │
    ▼
onFileChanged() 回调 (src/index.ts)
    │
    ├─ pending 防重入检查
    ├─ contents.localPath() 剥离 drive 前缀
    │
    ▼
latexBuildRequest(localPath, synctex, settings)
    │  HTTP GET /latex/build/{path}?synctex={0|1}
    │
    ▼
LatexBuildHandler.get(path)
    │
    ├─ 路径验证（存在 + .tex 扩展名）
    ├─ latex_cleanup 上下文（切换目录 + 白名单保留）
    ├─ build_tex_cmd_sequence() 构建命令序列
    │    ├─ manual_cmd_args? → 用户自定义命令
    │    ├─ tectonic? → Tectonic 内置序列
    │    └─ 默认 → xelatex + shell-escape flag
    │    └─ 检测 .bib → 插入 bibtex + 两次额外编译
    │
    ▼
run_latex(sequence)
    │  遍历命令序列，逐个 yield run_command(cmd)
    │
    ├─ 成功 → "LaTeX compiled"
    └─ 失败 → 500 + JSON {fullMessage, errorOnlyMessage}
    │
    ▼ (HTTP 响应返回前端)
    │
    ├─ 成功: pdfContext.revert() 或 findOpenOrRevealPDF()
    │    └─ PDFJSViewer._render() 重新加载 PDF
    │         ├─ base64→Blob→ObjectURL
    │         ├─ pdfjsLib.getDocument()
    │         └─ 保留缩放/滚动位置
    │
    └─ 失败: errorPanelInit(err)
         └─ 创建 ErrorPanel (split-bottom)
              └─ LatexError React 组件 (Filtered/Unfiltered/JSON)
```

## 文档工厂注册

pdfjsPlugin 通过 `app.docRegistry.addWidgetFactory(factory)` 注册 `PDFJSViewerFactory`，使得：

1. JupyterLab 识别 `.pdf` 文件类型
2. 双击 `.pdf` 文件时使用 PDFJSViewer 打开
3. LaTeX 编译产出 PDF 后，通过 `manager.openOrReveal(pdfFilePath, 'PDFJS')` 以 split-right 模式打开
4. PDF 模型使用 `'base64'` 编码读取，因为 PDF 是二进制文件

## 编辑器扩展注册

latexPlugin 通过 `app.docRegistry.addWidgetExtension('Editor', new EditorToolbarPanel())` 向所有编辑器注入工具栏扩展：

- `EditorToolbarPanel.createNew()` 在每个编辑器 widget 创建时被调用
- 检查 `context.path.endsWith('.tex')` 决定是否注入 LaTeX 按钮
- 返回 `DisposableDelegate` 在 widget 销毁时清理按钮

## 状态持久化

- **活动预览路径**：保存在 `IStateDB`（key: `'jupyterlab-latex'`），格式 `{paths: string[]}`
- **SyncTeX 设置**：通过 `ISettingRegistry` 管理（schema/plugin.json 定义 synctex 布尔值）
- **布局恢复**：PDF 面板位置通过 `ILayoutRestorer` 恢复

---

**下一步阅读：**
- [LaTeX 编译流程](03-latex-compilation.md) — 深入命令序列构建、引擎切换、输出过滤
- [PDF 查看器](04-pdf-viewer.md) — pdfjs-dist 集成、渲染管线、工具栏
- [SyncTeX 双向同步](05-synctex-sync.md) — 编辑器与 PDF 之间的精确跳转
