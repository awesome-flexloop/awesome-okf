---
type: concept
title: "SyncTeX 双向同步"
description: "SyncTeX 机制如何实现 .tex 编辑器与 PDF 预览之间的双向定位：正向搜索（编辑器→PDF）和反向搜索（PDF→编辑器），包括坐标系统、命令构建、响应解析"
tags: [synctex, forward-search, inverse-search, pdf-coordinate, editor-navigation, click-sync]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: synctex-py
    resource: "/references/synctex-py-source.md"
    title: "SyncTeX处理器源码"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: pdf-ts
    resource: "/references/pdf-ts-source.md"
    title: "PDF查看器源码"
---

# SyncTeX 双向同步

SyncTeX 是 Gauthier Van Damme 开发的 TeX 输出同步工具，通过编译时生成的 `.synctex.gz` 压缩索引文件，在 LaTeX 源码（.tex）和 PDF 输出之间建立双向映射。jupyterlab-latex 完整实现了**正向搜索**（编辑器→PDF，光标跳到对应页面位置）和**反向搜索**（PDF→编辑器，点击跳回源码对应行）。

## SyncTeX 前置条件

1. **编译时启用 SyncTeX**：编译命令需要 `-synctex=1` 参数（由前端 `synctex` 设置控制，默认开启）
2. **`.synctex.gz` 文件存在**：编译成功后在 `.tex` 同目录生成，包含源码行号→PDF 页码/坐标的映射
3. **LaTeX 引擎支持**：XeLaTeX、pdfLaTeX、LuaLaTeX、Tectonic 均支持 SyncTeX

## 设置开关

SyncTeX 功能可在 JupyterLab 设置中关闭：

```typescript
// ISettingRegistry schema/plugin.json
// jupyterlab-latex:synctex → boolean (default: true)
```

当 `synctex` 设置为 `false` 时：
- 编译请求的 `synctex=0` 参数传入后端
- 编译命令不追加 `-synctex=1` 参数
- 编辑器光标移动不触发正向同步
- PDF 点击不触发反向同步

## 正向搜索（Forward Search：编辑器 → PDF）

正向搜索将编辑器中的光标位置映射到 PDF 中的对应页面和坐标，使 PDF 自动翻到对应页并高亮。

### 触发时机

`EditorToolbarPanel.createNew()` 中为编辑器注入光标位置监听：

```typescript
editor.model.selections.changed.connect(() => {
    const block = editor.getPositionAt(editor.getSelection().start);
    cm = { line: block.line, ch: block.column };
    if (pdfContext && this._syncTex) {
        synctex(cm, pdfContext.path, widget, app);
    }
});
```

当用户在编辑器中**点击移动光标**或**选择文本**时触发正向搜索。

注意：正向搜索仅在已存在 PDF 预览面板（`pdfContext` 非空）时才执行。

### 请求流程

```typescript
async function synctex(cm, path, widget, app) {
    // 1. 确保文件已保存（SyncTeX 需要最新文件）
    await widget.context.save();
    
    // 2. 构造 URL
    const synctex_url = new URL(url_path_join(
        serverSettings.baseUrl, 'latex', 'synctex',
        url_path_join(...path.split('/'))
    ));
    synctex_url.searchParams.append('line', cm.line + 1);     // 0-based → 1-based
    synctex_url.searchParams.append('column', cm.ch + 1);     // 0-based → 1-based
    
    // 3. 发送请求
    const resp = await ServerConnection.makeRequest(
        synctex_url.toString(), {}, serverSettings
    );
    const respJson = await resp.json();
    
    // 4. 触发 PDF 端定位
    if (widget.pdf.content.viewer) {
        widget.pdf.content.goToPosition(respJson);
    }
}
```

**坐标转换注意**：CodeMirror 编辑器的 `line` 和 `ch`（column）是 0-based 的，但 SyncTeX CLI 使用 1-based，所以请求时需要 `+1`。

### 后端处理

`LatexSynctexHandler.get(path)` 检测到有 `line` 参数时执行正向同步：

```python
if not self.line:
    raise web.HTTPError(500, "Failed to run SyncTeX: line parameter is required!")

pos = dict(
    i=Line(self.line),
    j=Column(self.column),
    h=1,  # before
)
code, output = await run_synctex(
    'view',
    os.path.relpath(self.filepath_local, self.tex_dir),
    self.pdfpath,
    pos,
    self.tex_dir,
)
```

**SyncTeX view 命令**：
```
synctex view -i <line>:<column>:<sourcefile> -o <pdffile>
```

响应解析通过 `parse_synctex_response()` 完成，提取 `Page`、`h`、`v` 等字段后返回 JSON。

### PDF 端定位

`PDFJSViewer.goToPosition()` 接收后端返回的坐标：

```typescript
goToPosition(pos: SyncTexPosition): void {
    // 构造 pdfjs viewer 可识别的位置对象
    const dest = {
        pageNumber: pos.page,
        left: pos.x,
        top: pos.y,
        scaleSelection: 'page-fit',
    };
    // 通过 eventBus 触发跳转
    this._eventBus.dispatch('scrolltopage', {
        pageNumber: pos.page,
    });
    // 跳转到具体位置并高亮...
}
```

### PDF 坐标系统

SyncTeX 返回的坐标是 **72 dpi 的 PostScript 点**（pt），以页面左下角为原点，y 轴向上。pdfjs-dist 的 CSS 像素坐标是 96 dpi（CSS_UNITS = 96/72），以页面左上角为原点，y 轴向下。两者需要转换：

```
PDF 点 → CSS 像素：
  x_css = (x_pt * 72 / 96) * zoom
  y_css = ((page_height_pt - y_pt) * 72 / 96) * zoom
```

## 反向搜索（Inverse Search：PDF → 编辑器）

反向搜索让用户在 PDF 中 Shift+Ctrl/Cmd+Click 点击时，编辑器跳转到对应的源码位置。

### 触发方式

在 PDF 查看器 iframe 中按住 **Shift+Ctrl（Windows/Linux）** 或 **Shift+Cmd（macOS）** 并点击鼠标。这个组合键由 `PDFJSViewer._viewer.onload` 中的事件监听器捕获：

```javascript
if (event.shiftKey && event.ctrlKey || event.shiftKey && event.metaKey) {
    event.preventDefault();
    that._handleClick(event);
}
```

点击的键盘修饰符要求与 TeX 编辑器（如 TeXStudio）的惯例一致。

### 点击坐标获取

`_handleClick(event)` 将 DOM 点击位置转换为 PDF 坐标：

```typescript
private _handleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    // 向上查找 data-page-number 属性确定页码
    let pageElement = target.closest('[data-page-number]') as HTMLElement;
    const page = parseInt(pageElement.getAttribute('data-page-number'), 10);
    
    // 获取包含画布的 div（id 以 "pageContainer" 开头）
    const pageContainer = pageElement.parentElement;
    const divHeight = pageContainer.clientHeight;
    
    // 计算点击位置相对于容器的偏移
    const boundingRect = pageContainer.getBoundingClientRect();
    const x = event.clientX - boundingRect.left;
    const y = event.clientY - boundingRect.top;
    
    // 获取当前缩放级别
    const zoom = parseFloat(
        pageContainer.style.getPropertyValue('--scale-factor')
    );
    
    // DOM 像素 → PDF 点（72dpi）
    const CSS_UNITS = 96.0 / 72.0;
    const pageX = x / zoom * CSS_UNITS;
    const pageY = (divHeight / zoom) * CSS_UNITS - y / zoom * CSS_UNITS;
    //         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^
    //         页面总高度(PDF点)               y轴翻转(DOM→PDF坐标系)
    
    // 发送 positionRequested 信号
    this._positionRequested.emit({
        x: pageX, y: pageY, page: page,
        pageHeight: divHeight / zoom * CSS_UNITS,
        path: this._path || this.context.path,
        edit: true  // 标识这是编辑/同步操作
    });
}
```

### 请求流程

`positionRequested` 信号的处理函数在 `latexPlugin.activate()` 中连接：

```typescript
widget._positionRequested.connect(async (viewer, pos) => {
    // 1. 构造 URL（反向同步使用 page/x/y 参数）
    const synctex_url = new URL(...);
    synctex_url.searchParams.append('page', pos.page);
    synctex_url.searchParams.append('x', pos.x);
    synctex_url.searchParams.append('y', pos.y);
    
    // 2. 发送请求
    const resp = await ServerConnection.makeRequest(synctex_url, {}, settings);
    const respJson = await resp.json();
    
    // 3. 解析结果，找到对应的编辑器 widget
    // ...（在 widget 中查找对应 .tex 文件的编辑器）
    
    // 4. 跳转到编辑器对应行
    editor.setSelection({
        start: { line: respJson.line - 1, column: respJson.column - 1 },
        end: { line: respJson.line - 1, column: respJson.column - 1 },
    });
    shell.activateById(widget.id);  // 激活编辑器面板
});
```

### 后端处理

`LatexSynctexHandler.get(path)` 检测到有 `page` 参数时执行反向同步：

```python
if not self.page:
    raise web.HTTPError(500, "Failed to run SyncTeX: page parameter is required!")

pos = dict(
    i=Page(self.page),
    h=X(self.x),
    v=Y(self.y),
)
code, output = await run_synctex(
    'edit',
    os.path.relpath(self.filepath_local, self.tex_dir),
    self.pdfpath,
    pos,
    self.tex_dir,
)
```

**SyncTeX edit 命令**：
```
synctex edit -o <page>:<x>:<y>:<pdffile> -d <directory>
```

响应解析后返回包含 `line` 和 `column` 的 JSON。

### 编辑器跳转

收到后端响应后，前端：
1. **1-based → 0-based** 转换：`line - 1`, `column - 1`
2. **设置光标位置**：`editor.setSelection({start: {line, column}, end: {line, column}})`
3. **滚动到光标行**：CodeMirror 自动滚动使选中行可见
4. **激活编辑器面板**：`shell.activateById(widget.id)` 将焦点切到编辑器

## SyncTeX CLI 命令详解

### synctex view（正向搜索）

```bash
synctex view -i <line>:<column>:<source.tex> -o <output.pdf>
```

**参数**：
- `-i`：输入位置——行号:列号:源文件路径
- `-o`：输出 PDF 文件路径

**输出格式**（SynctexParser 解析）：
```
Output:
Page:1
x:185.000000
y:352.250000
h:16.250000
W:345.000000
H:6.666672
before:
1:0:0:0:0
```

### synctex edit（反向搜索）

```bash
synctex edit -o <page>:<x>:<y>:<output.pdf> -d <directory>
```

**参数**：
- `-o`：输出位置——页码:x坐标:y坐标:PDF文件路径
- `-d`：工作目录

**输出格式**（SynctexParser 解析）：
```
Input: /path/to/source.tex
Line:42
Column:5
Offset:0
...
```

## SynctexParser 解析器

`synctex.py` 中的 `SynctexParser` 类解析 SyncTeX CLI 的文本输出：

```python
class SynctexParser:
    def __init__(self, output, fwd_search=True):
        self.current_block = {}
        self.current_key = None
        self.handler = fwd_parse_node if fwd_search else bwd_parse_node
        self.fwd = fwd_search
        for line in output.split('\n'):
            self.parseline(line)
```

解析状态机：
1. 遇到 `Output:`/`Input:`/`Before:`/`After:` 等节标记时重置当前块
2. 遇到 `Page:`/`x:`/`y:`/`h:`/`Line:`/`Column:` 等键值对时提取数值
3. 遇到空行或节结束时将当前块添加到结果列表

**正向搜索解析结果**：包含 `Page`、`x`、`y`、`h`（高度）、`W`（宽度）、`H`（高度）等字段。

**反向搜索解析结果**：包含 `Input`（源文件路径）、`Line`（行号）、`Column`（列号）、`Offset` 等字段。

## 多文件项目的 SyncTeX

SyncTeX 天然支持多文件项目：
- 当用户在子文件（通过 `\input`/`\include` 引入）中点击时，反向搜索返回子文件的路径
- 前端根据返回的 `input` 字段查找对应的编辑器 widget 并跳转
- 当用户在主文件中移动光标时，正向搜索通过 `.synctex.gz` 中的映射定位到正确的 PDF 位置

## SyncTeX 工作流程总图

```
┌─────────────── 正向搜索 ───────────────┐
│                                         │
│ 编辑器光标移动                           │
│    │ selections.changed                 │
│    ▼                                    │
│ synctex(line,col,path)                  │
│    │ GET /latex/synctex/{path}         │
│    │   ?line=N&column=M                 │
│    ▼                                    │
│ synctex view -i N:M:file.tex -o pdf    │
│    │ 解析输出 → {page, x, y}           │
│    ▼                                    │
│ PDFJSViewer.goToPosition({page,x,y})   │
│    │ eventBus.dispatch scrolltopage     │
│    ▼                                    │
│ PDF 翻到对应页并定位 ◄──────────────────┘
│
┌─────────────── 反向搜索 ───────────────┐
│                                         │
│ Shift+Ctrl+Click PDF                   │
│    │ mousedown 事件                     │
│    ▼                                    │
│ _handleClick(event)                    │
│    │ DOM坐标 → PDF点坐标                │
│    ▼                                    │
│ positionRequested.emit({page,x,y,path})│
│    │ GET /latex/synctex/{path}         │
│    │   ?page=P&x=X&y=Y                 │
│    ▼                                    │
│ synctex edit -o P:X:Y:file.pdf -d dir  │
│    │ 解析输出 → {input, line, column}  │
│    ▼                                    │
│ editor.setSelection(line-1,col-1)      │
│    │ 激活编辑器面板                     │
│    ▼                                    │
│ 编辑器跳转到对应行 ◄────────────────────┘
```

## SyncTeX 精度限制

SyncTeX 的精度受以下因素影响：

| 因素 | 影响 |
|------|------|
| 宏展开 | `\newcommand` 定义的宏内部位置可能映射到宏定义处而非调用处 |
| 数学公式 | 复杂公式中的符号位置可能不够精确 |
| 分页 | 自动分页的内容在页边界处位置可能有偏差 |
| 缩放 | 低缩放级别下点击位置精度降低（像素→点转换误差放大） |

一般情况下，SyncTeX 能精确到行级定位（精确到具体命令/单词），足以满足日常导航需求。

---

**下一步阅读：**
- [编辑工具栏与快捷操作](06-editing-tools.md) — LaTeX 编辑器工具栏按钮详解
- [配置指南](../examples/03-configuration.md) — SyncTeX 开关与其他配置项
