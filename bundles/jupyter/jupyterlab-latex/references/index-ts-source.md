---
type: reference
title: "插件入口源码（src/index.ts）"
description: "JupyterLab LaTeX 扩展的前端插件入口，包含双插件注册（latexPlugin + pdfjsPlugin）、命令系统、工具栏面板、SyncTeX 命令、LaTeX 菜单与表格生成"
tags: [plugin, entry-point, activation, commands, toolbar, synctex, menu, pdfjs]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: index-ts
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/src/index.ts"
    title: "src/index.ts"
---

# 插件入口源码（src/index.ts）

本信源登记 `src/index.ts`（约1448行），这是 JupyterLab LaTeX 扩展的前端主入口文件，负责双插件注册、命令定义、工具栏注入、SyncTeX 双向同步、LaTeX 编辑菜单与新建文件功能。

## 导出项

### 默认导出：plugins 数组

类型 `JupyterFrontEndPlugin<any>[]`，包含两个插件：

| 插件 | ID | provides | requires | optional | autoStart |
|------|-----|----------|----------|----------|-----------|
| `latexPlugin` | `'@jupyterlab/latex:plugin'` | 无 | IDefaultFileBrowser, IDocumentManager, IEditorTracker, ILabShell, ILayoutRestorer, IPDFJSTracker, ISettingRegistry, IStateDB | ILauncher, IMainMenu, ICommandPalette | true |
| `pdfjsPlugin` | `'@jupyterlab/pdfjs-extension:plugin'` | IPDFJSTracker | ILayoutRestorer | 无 | true |

### 命名导出

| 导出 | 类型 | 说明 |
|------|------|------|
| `IPDFJSTracker` | `Token<IPDFJSTracker>` | PDF 追踪器 Token，类型为 `IWidgetTracker<IDocumentWidget<PDFJSViewer>>` |

## CommandIDs 命名空间

| 命令 ID | 标签 | 功能 |
|---------|------|------|
| `latex:open-preview` | `'Show LaTeX Preview'` | 打开 `.tex` 文档的实时预览 |
| `latex:synctex-edit` | `'Scroll Editor to Page'` | PDF→编辑器反向同步 |
| `latex:synctex-view` | `'Scroll PDF to Cursor'` | 编辑器→PDF 正向同步 |
| `latex:create-new-latex-file` | `'LaTeX File'` | 新建 LaTeX 文件 |
| `latex:create-table` | `'Create Table'` | 创建 LaTeX 表格对话框 |

## HTTP 请求函数

### latexBuildRequest(path, synctex, settings)

- URL: `{baseUrl}/latex/build/{path}?synctex={0|1}`
- 方法：GET
- 非200响应抛出 `ServerConnection.ResponseError`
- 返回：`Promise<any>`（response.text()）

### synctexEditRequest(path, pos, settings)

- URL: `{baseUrl}/latex/synctex/{path}?page={page}&x={x}&y={y}`
- 反向同步：PDF 坐标 → 编辑器行列
- 返回：`Promise<ISynctexViewOptions>`（line, column，均为 parseInt 解析的整数）

### synctexViewRequest(path, pos, settings)

- URL: `{baseUrl}/latex/synctex/{path}?line={line}&column={column}`
- 正向同步：编辑器行列 → PDF 坐标
- 返回：`Promise<ISynctexEditOptions>`（page: int, x/y: float，x 坐标在实际使用时被置为0）

## activateLatexPlugin 函数

签名：`function activateLatexPlugin(app, browser, manager, editorTracker, shell, restorer, pdfTracker, settingRegistry, state, launcher, menu, palette): void`

### 核心逻辑

1. **创建图标**：`LabIcon` 实例（name: `'launcher:latex-icon'`，使用 latex.svg）
2. **openPreview(widget)** 函数：
   - 检查已有预览（`Private.previews.has(path)`），有则触发保存
   - 计算 pdfFilePath = `{dir}/{baseName}.pdf`
   - `findOpenOrRevealPDF()`：查找或打开 PDF 面板（split-right 模式），连接 `positionRequested` 信号
   - `reverseSearch()`：反向同步（x 坐标置0，行号-1转为0-based）
   - `errorPanelInit(err)`：404时提示安装服务端扩展；其他错误创建 ErrorPanel（split-bottom）
   - `onFileChanged()`：保存时触发编译（`latexBuildRequest`），pending 防重入；成功后 revert PDF 上下文；失败显示错误面板
   - 使用 `contents.localPath()` 去除协作扩展添加的 drive 前缀
3. **EditorToolbarPanel 类**（实现 `DocumentRegistry.IWidgetExtension`）：
   - 为 `.tex` 文件编辑器注入工具栏按钮
   - 按钮：Preview、下标/上标/分数、左/中/右对齐、粗体/斜体/下划线、列表/编号、表格、绘图
   - `replaceSelection(action)`：选中文本时包裹 `\command{text}`；未选中时弹出输入对话框
   - `insertPlot()`：6种绘图类型（数学函数、数据文件、散点图、柱状图、等高线、参数图），插入 pgfplots/tikzpicture 代码
4. **状态恢复**：从 IStateDB 恢复之前打开的预览路径
5. **设置监听**：加载 synctex 设置，变更时重新注册/注销 SyncTeX 命令
6. **命令注册**：openLatexPreview（右键菜单）、createNew（Launcher/Palette/File菜单）
7. **SyncTeX 命令注册**（addSynctexCommands）：
   - synctexEdit：PDF 右键菜单，快捷键 `Accel Shift X`
   - synctexView：编辑器右键菜单，快捷键 `Accel Shift X`
   - 双向查找对应 widget（通过 baseName 推导 .tex/.pdf 路径）
8. **LaTeX 菜单**（addLatexMenu）：
   - Constants 子菜单：π、γ、φ
   - Symbols 子菜单：26个数学符号（比较、集合、逻辑）
   - Create Table 命令
9. **上下文菜单**：`.jp-FileEditor` 注册 open-preview 和 synctex-view；`.jp-PDFJSContainer` 注册 synctex-edit

## activatePDFJS 函数

签名：`function activatePDFJS(app, restorer): IPDFJSTracker`

1. 创建 `PDFJSViewerFactory`（name: `'PDFJS'`, modelName: `'base64'`, fileTypes: `['PDF']`, readOnly: true）
2. 创建 `WidgetTracker`（namespace: `'pdfjs-widget'`）
3. 注册布局恢复（`restorer.restore`）
4. 监听 `widgetCreated` 信号，添加到 tracker，设置图标
5. 返回 tracker

## 辅助函数

### isLatexFile(editorTracker)

检查当前编辑器 widget 是否打开 `.tex` 文件，返回 widget 或 null。

### generateTable(rowNum, colNum)

生成 LaTeX tabular 表格代码：
- 列格式：`|c|c|c|`（每列居中+竖线）
- 单元格内容：`cell1 & cell2 & ... \\`
- 行间分隔：`\hline`
- 外层包裹 `\begin{center}...\end{center}`
- 使用 `replace(/^ +/gm, '')` 去除前导空格

## Private 命名空间

| 成员 | 类型 | 说明 |
|------|------|------|
| `id` | number | 错误面板唯一 ID 计数器 |
| `previews` | `Set<string>` | 当前活动预览的文件路径集合 |
| `createErrorPanel()` | 函数 | 创建 ErrorPanel 实例（id: `latex-error-{id}`, title: `'LaTeX Error'`） |

## 常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `latexPluginId` | `'@jupyterlab/latex:plugin'` | LaTeX 插件 ID |
| `FILE_TYPES` | `['PDF']` | PDF 文件类型列表 |
| `FACTORY` | `'PDFJS'` | PDF 查看器工厂名 |
| `FACTORY_EDITOR` | `'Editor'` | 编辑器工厂名 |
| `LAUNCHER_CATEGORY` | `'Other'` | Launcher 分类 |
| `PALETTE_CATEGORY` | `'LaTeX Editor'` | 命令面板分类 |
