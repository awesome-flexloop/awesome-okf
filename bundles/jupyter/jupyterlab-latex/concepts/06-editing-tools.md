---
type: concept
title: "编辑工具栏与快捷操作"
description: "EditorToolbarPanel 如何为 .tex 文件编辑器注入 LaTeX 专用工具栏按钮，包括文本格式化、列表表格插入、数学快捷输入、绘图插入和 LaTeX 菜单系统"
tags: [toolbar, editing, formatting, math-shortcuts, lists, tables, plots, menus, commands]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: schema-plugin
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/schema/plugin.json"
    title: "设置 Schema"
---

# 编辑工具栏与快捷操作

打开 `.tex` 文件时，jupyterlab-latex 通过 `EditorToolbarPanel`（一个 `WidgetExtension`）向 CodeMirror 编辑器工具栏注入 LaTeX 专用按钮。此外还提供命令面板命令、右键菜单项和 LaTeX 菜单栏。

## EditorToolbarPanel 注入机制

`EditorToolbarPanel` 继承自 `WidgetExtension`，注册到文档注册表的 `'Editor'` 工厂：

```typescript
app.docRegistry.addWidgetExtension('Editor', new EditorToolbarPanel(app, settings));
```

当编辑器 widget 创建时，`createNew()` 被调用：

```typescript
createNew(widget: FileEditor, context: DocumentRegistry.IContext<DocumentRegistry.IModel>): IDisposable {
    this.editor = widget;
    this.context = context;
    this.cm = widget.content.editor;
    
    // 检查是否为 .tex 文件
    if (this.context.path.split('.').pop() !== 'tex') {
        return new DisposableDelegate(() => {});  // 不注入按钮
    }
    
    // 注入按钮...
    this.createButtons();
    
    // 注入光标位置监听（SyncTeX 正向搜索）
    this.injectCursorListener();
    
    return new DisposableDelegate(() => {
        // 清理：移除按钮和监听器
        this.buttons.forEach(btn => btn.dispose());
    });
}
```

关键设计：
- **条件注入**：只对 `.tex` 文件显示 LaTeX 工具栏，其他文件类型不受影响
- **DisposableDelegate**：JupyterLab 推荐的清理模式，widget 销毁时自动移除按钮
- **共享实例字段**：由于 `createNew` 可能被多次调用（每个编辑器一个），使用实例字段存储当前编辑器引用

## 工具栏按钮详解

工具栏按钮分为四个功能区：预览操作、文本格式化、列表/表格、绘图。

### 1. 预览操作

| 按钮 | Command ID | 功能 |
|------|-----------|------|
| **Preview** | `CommandIDs.latexPreview` | 打开/刷新 PDF 预览（split-right 面板） |

```typescript
const button = new ToolbarButton({
    label: 'Preview',
    caption: 'Open live preview',
    onClick: () => {
        app.commands.execute(CommandIDs.latexPreview);
    },
});
```

### 2. 文本格式化

| 按钮 | 图标 | 插入内容 | 行为 |
|------|------|---------|------|
| **下标** | X<sub>y</sub> (`$` 图标) | `$x_{}$` / 包裹选中 | 选中文字包裹为下标；无选中时插入 `$x_{}$` |
| **上标** | X<sup>n</sup> (`$` 图标) | `$x^{}$` / 包裹选中 | 选中文字包裹为上标；无选中时插入 `$x^{}$` |
| **分数** | X/Y | 弹窗输入分子分母 | 弹出 `InputDialog`，分别输入分子分母，插入 `\frac{num}{den}` |
| **左对齐** | 左对齐图标 | `\leftline{}` / 包裹选中 | 选中文字左对齐；无选中时插入空命令 |
| **居中** | 居中图标 | `\centerline{}` / 包裹选中 | 选中文字居中；无选中时插入空命令 |
| **右对齐** | 右对齐图标 | `\rightline{}` / 包裹选中 | 选中文字右对齐；无选中时插入空命令 |
| **粗体** | **B** | `\textbf{}` / 包裹选中 | 选中文本加粗；无选中时插入空命令 |
| **斜体** | *I* | `\textit{}` / 包裹选中 | 选中文本斜体；无选中时插入空命令 |
| **下划线** | U̲ | `\underline{}` / 包裹选中 | 选中文本加下划线；无选中时插入空命令 |

### 包裹 vs 插入逻辑

格式化按钮的两种行为模式：

```typescript
function wrapOrInsert(editor, command, placeholder='') {
    const selection = editor.getSelection();
    if (selection) {
        // 有选中文本：包裹
        editor.replaceSelection(`\\${command}{${selection}}`);
    } else {
        // 无选中：插入命令+占位，光标定位到花括号内
        const cursor = editor.getCursorPosition();
        const insertText = `\\${command}{${placeholder}}`;
        editor.replaceSelection(insertText);
        // 将光标移动到 {} 内部
        editor.setCursorPosition({
            line: cursor.line,
            column: cursor.column + command.length + 2,
        });
    }
}
```

### 3. 列表与表格

| 按钮 | 图标 | 插入内容 | 行为 |
|------|------|---------|------|
| **无序列表** | 列表图标 | `itemize` 环境 | 插入 `\begin{itemize}\n  \item \n\end{itemize}` |
| **有序列表** | 编号图标 | `enumerate` 环境 | 插入 `\begin{enumerate}\n  \item \n\end{enumerate}` |
| **表格** | 表格图标 | `tabular` 环境 | 弹出对话框输入行列数，生成对应的表格代码 |

**表格插入对话框**：

点击表格按钮后，依次弹出两个 `InputDialog`：
1. 输入列数（默认 3）
2. 输入行数（默认 3）

生成的代码格式：
```latex
\begin{tabular}{|c|c|c|}
    \hline
     &  & \\
    \hline
     &  & \\
    \hline
     &  & \\
    \hline
\end{tabular}
```
- 列格式：每列居中（`c`），列之间有竖线（`|`）
- 行格式：每行前后有 `\hline` 横线
- 空单元格用空格占位

### 4. 绘图插入

| 按钮 | 图标 | 插入内容 |
|------|------|---------|
| **插入绘图** | 图表图标 | 6种 pgfplots 类型之一 |

点击绘图按钮后弹出选择对话框，提供以下选项：

| 选项 | 插入的绘图类型 | LaTeX 环境 |
|------|--------------|-----------|
| Polar | 极坐标图 | `\begin{polaraxis}` |
| Rectangular | 直角坐标图 | `\begin{axis}` |
| SemilogX | X 轴对数坐标 | `\begin{semilogxaxis}` |
| SemilogY | Y 轴对数坐标 | `\begin{semilogyaxis}` |
| LogLog | 双对数坐标 | `\begin{loglogaxis}` |
| SmithChart | 史密斯圆图 | `\begin{smithchart}` |

所有绘图插入均使用 pgfplots 包，需要文档中包含 `\usepackage{pgfplots}`。

## CommandIDs 命令系统

所有 LaTeX 操作都通过 JupyterLab 命令系统注册，可以在命令面板（Ctrl+Shift+C）中搜索执行。

| Command ID | 标签 | 功能 |
|-----------|------|------|
| `jupyterlab-latex:open-latex-preview` | LaTeX: Open LaTeX Preview | 打开 PDF 预览 |
| `jupyterlab-latex:run-latex` | LaTeX: Run LaTeX | 运行 LaTeX 编译 |
| `jupyterlab-latex:latex-superscript` | LaTeX: Insert superscript | 插入上标 |
| `jupyterlab-latex:latex-subscript` | LaTeX: Insert subscript | 插入下标 |
| `jupyterlab-latex:latex-fraction` | LaTeX: Insert fraction | 插入分数（弹窗） |
| `jupyterlab-latex:latex-bold` | LaTeX: Insert boldface | 插入粗体 |
| `jupyterlab-latex:latex-italic` | LaTeX: Insert italic | 插入斜体 |
| `jupyterlab-latex:latex-underline` | LaTeX: Insert underline | 插入下划线 |
| `jupyterlab-latex:latex-equation` | LaTeX: Insert equation | 插入 equation 环境 |
| `jupyterlab-latex:latex-item-list` | LaTeX: Insert itemize | 插入无序列表 |
| `jupyterlab-latex:latex-enum-list` | LaTeX: Insert enumerate | 插入有序列表 |
| `jupyterlab-latex:latex-table` | LaTeX: Insert table | 插入表格（弹窗） |
| `jupyterlab-latex:latex-plot` | LaTeX: Insert plot | 插入绘图（选择类型） |
| `jupyterlab-latex:latex-left` | LaTeX: Insert leftline | 左对齐 |
| `jupyterlab-latex:latex-center` | LaTeX: Insert centerline | 居中 |
| `jupyterlab-latex:latex-right` | LaTeX: Insert rightline | 右对齐 |
| `jupyterlab-latex:create-new-latex-file` | LaTeX: New LaTeX file | 新建 .tex 文件 |
| `jupyterlab-latex:synctex-from-pdf` | LaTeX: SyncTeX from PDF | PDF→编辑器同步 |
| `jupyterlab-latex:synctex-from-editor` | LaTeX: SyncTeX from editor | 编辑器→PDF同步 |

### 命令执行上下文

所有编辑命令都依赖以下上下文对象：
- **editor**：当前活动的 CodeMirror 编辑器实例
- **context**：当前文档上下文（用于获取路径、保存文件）
- **app**：JupyterLab 应用实例（用于命令调度、面板管理）
- **widget**：当前编辑器 widget

命令执行前通过 `app.shell.currentWidget` 和 `findWidgetByContext()` 定位当前编辑器。

## LaTeX 菜单栏

当 `IMainMenu` 可用时，扩展在 JupyterLab 菜单栏新增 "LaTeX" 菜单：

```typescript
latexMenu.menu.addItem({ command: CommandIDs.latexSuperscript });
latexMenu.menu.addItem({ command: CommandIDs.latexSubscript });
latexMenu.menu.addItem({ command: CommandIDs.latexPreview });
// ... 数学符号子菜单
```

### 数学常数子菜单

提供常用数学常数的快捷插入：

| 菜单项 | 插入的 LaTeX 命令 |
|--------|------------------|
| α (alpha) | `\alpha` |
| β (beta) | `\beta` |
| γ (gamma) | `\gamma` |
| δ (delta) | `\delta` |
| ε (epsilon) | `\epsilon` |
| π (pi) | `\pi` |
| ∞ (infinity) | `\infty` |
| ° (degree) | `\circ` |

### 数学符号子菜单

提供常用数学符号的快捷插入：

| 菜单项 | 插入的 LaTeX 命令 |
|--------|------------------|
| ± (plus-minus) | `\pm` |
| × (times) | `\times` |
| ÷ (div) | `\div` |
| ≤ (leq) | `\leq` |
| ≥ (geq) | `\geq` |
| ≠ (neq) | `\neq` |
| ∑ (sum) | `\sum` |
| ∫ (int) | `\int` |
| √ (sqrt) | `\sqrt{}` |
| … (dots) | `\dots` |

## Launcher 入口

当 `ILauncher` 可用时，在 Launcher 的 Other 分类下添加 "LaTeX File" 卡片：

```typescript
launcher.add({
    command: CommandIDs.newLatexFile,
    category: 'Other',
    rank: 10,
});
```

点击后执行 `CommandIDs.newLatexFile`：
1. 获取文件浏览器默认路径
2. 生成新文件名（`untitled.tex`，重名时追加数字）
3. 在文件浏览器中新建 `.tex` 文件
4. 在主区域打开新文件

## 右键上下文菜单

编辑器的右键菜单中添加：

| 菜单项 | 命令 | 条件 |
|--------|------|------|
| Show LaTeX Preview | `CommandIDs.latexPreview` | 仅 .tex 文件 |
| Create New LaTeX File | `CommandIDs.newLatexFile` | 始终可用 |

菜单项通过 `app.contextMenu.addItemOp` 注册，绑定到 `.jp-FileEditor` 选择器。

## 键盘快捷键

jupyterlab-latex 当前版本**未注册自定义键盘快捷键**。所有功能通过工具栏按钮、命令面板或菜单触发。用户可通过 JupyterLab Settings → Keyboard Shortcuts 自定义绑定。

建议用户自行绑定的常用快捷键：

```json
{
    "shortcuts": [
        {
            "command": "jupyterlab-latex:open-latex-preview",
            "keys": ["Ctrl+Shift+P"],
            "selector": "[data-file-ext='tex']"
        },
        {
            "command": "jupyterlab-latex:latex-bold",
            "keys": ["Ctrl+B"],
            "selector": ".jp-FileEditor"
        },
        {
            "command": "jupyterlab-latex:latex-italic",
            "keys": ["Ctrl+I"],
            "selector": ".jp-FileEditor"
        }
    ]
}
```

---

**下一步阅读：**
- [配置指南](07-configuration.md) — 编译引擎、SyncTeX 开关等配置详解
- [基本使用示例](../examples/01-basic-usage.md) — 操作步骤示例
