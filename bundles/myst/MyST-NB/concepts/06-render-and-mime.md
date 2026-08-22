---
type: Concept
title: 渲染与 MIME 类型
description: MIME 类型优先级系统、多输出格式渲染、图片处理、ipywidgets、stderr 处理、自定义渲染插件
tags: [myst-nb, render, mime, output, ipywidgets, image]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 渲染与 MIME 类型

Jupyter Notebook 的代码 cell 输出是一个 **mimebundle**——同一份数据有多种 MIME 格式表示（如 pandas DataFrame 同时有 text/plain、text/html、text/markdown 表示）。MyST-NB 通过 MIME 类型优先级系统，根据目标输出格式（HTML/LaTeX/文本）选择最合适的渲染方式。

## MIME 优先级系统

每个 builder（html/latex/text/man 等）有自己的 MIME 优先级列表，决定在多种格式中优先选择哪种：

- **HTML builder**：优先 `text/html` → `image/svg+xml` → `image/png` → `text/markdown` → `text/plain`
- **LaTeX builder**：优先 `text/latex` → `application/pdf` → `image/png` → `text/plain`
- **Text builder**：优先 `text/plain`

### MIME 优先级覆盖

通过 `nb_mime_priority_overrides` 自定义优先级：

```python
# 格式：(builder_name, mime_type, priority)
# priority 为 None 表示禁用该 MIME 类型
nb_mime_priority_overrides = [
    ("html", "text/plain", 0),       # text/plain 优先（调试用）
    ("latex", "text/latex", 1),      # LaTeX 输出优先
    ("html", "application/vnd.plotly.v1+json", None),  # 禁用 Plotly
]
```

### SelectMimeType Post-Transform

MIME 类型的最终选择发生在 Sphinx Post-Transform 阶段（`SelectMimeType`），此时 builder 已知，可以准确选择优先级最高的可用 MIME 类型。

## 输出类型渲染

### 文本输出（text/plain）

stdout/stderr 和 text/plain 输出使用 Pygments 高亮渲染：
- 普通文本输出 → `myst-ansi` lexer（支持 ANSI 颜色代码解析）
- 错误/traceback → `ipythontb` lexer（IPython traceback 语法高亮）

配置：
```python
nb_render_text_lexer = "myst-ansi"     # 文本 lexer
nb_render_error_lexer = "ipythontb"   # 错误 lexer
```

Cell 级别覆盖：
````markdown
```{code-cell}
---
mystnb:
  text_lexer: "ipythontb"
  error_lexer: "py3tb"
---
```
````

### 图片输出

支持的图片 MIME 类型：
- `image/png`、`image/jpeg`、`image/gif`、`image/webp`（二进制，base64 解码后保存为文件）
- `image/svg+xml`（文本，保存为 .svg 文件）
- `application/pdf`（LaTeX builder 使用）

图片保存路径：`jupyter_execute/` 文件夹（Sphinx 模式自动设置），生成唯一文件名。

渲染选项：
```python
nb_render_image_options = {
    "width": "600px",
    "align": "center",
    "class": "my-image",
}
```

Cell 级别设置：
````markdown
```{code-cell}
---
mystnb:
  image:
    width: 400px
    alt: "示例图片"
---
import matplotlib.pyplot as plt
plt.plot([1,2,3])
```
````

### Figure 输出

图片可以渲染为 figure（带标题、编号）：
````markdown
```{code-cell}
---
mystnb:
  figure:
    caption: "数据趋势图"
    name: fig-trend
---
plt.plot(x, y)
```
````

通过 `{ref}` 引用：`见 {ref}`fig-trend``。

### HTML 输出（text/html）

`text/html` MIME 类型输出作为 raw HTML 节点直接嵌入文档。DataFrame、Plotly、Bokeh 等库的 HTML 输出以此方式渲染。

### Markdown 输出（text/markdown）

`text/markdown` MIME 类型输出会被递归解析为 MyST Markdown，渲染为完整的 docutils 节点。

渲染格式配置：
```python
nb_render_markdown_format = "commonmark"  # 或 "gfm"、"myst"
```

### 数学输出（text/latex）

`text/latex` 输出渲染为数学节点，在 HTML 中由 MathJax 渲染，在 LaTeX 中为原生数学。

### ipywidgets 输出

`application/vnd.jupyter.widget-state+json` 和 `application/vnd.jupyter.widget-view+json` MIME 类型支持交互式 ipywidgets。MyST-NB 自动加载：
- RequireJS（依赖管理）
- `@jupyter-widgets/html-manager`（Widget 渲染器）

默认 CDN 配置：
```python
nb_ipywidgets_js = {
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js": {
        "integrity": "sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=",
        "crossorigin": "anonymous",
    },
    "https://cdn.jsdelivr.net/npm/@jupyter-widgets/html-manager@1.0.6/dist/embed-amd.js": {
        "data-jupyter-widgets-cdn": "https://cdn.jsdelivr.net/npm/",
        "crossorigin": "anonymous",
    },
}
```

可自定义为本地路径或其他 CDN。

### stderr 处理

`nb_output_stderr` 控制 stderr 输出的处理方式：

| 值 | 行为 |
|----|------|
| `"show"` | 正常显示（默认） |
| `"remove"` | 移除 stderr，不警告 |
| `"remove-warn"` | 移除 stderr，发警告 |
| `"warn"` | 显示 stderr，发警告 |
| `"error"` | stderr 作为错误报告 |
| `"severe"` | stderr 作为严重错误（中断构建） |

Cell 级别：
````markdown
```{code-cell}
---
mystnb:
  output_stderr: "remove"
---
```
````

### 流合并

`nb_merge_streams = True` 将同一 cell 中所有 stdout 输出合并为一个块，stderr 同理。适用于输出分段的场景。

## 自定义渲染插件

通过 entry points 注册自定义渲染器和 MIME 渲染插件：

### 自定义渲染器

注册 `myst_nb.renderers` entry point，继承 `NbElementRenderer`。

### 自定义 MIME 渲染插件

注册 `myst_nb.mime_renderers` entry point，实现 MIME 类型到 docutils 节点的转换。

## 渲染插件加载

渲染器通过 `load_renderer()` 函数从 entry points 加载：

```python
# pyproject.toml
[project.entry-points."myst_nb.renderers"]
my_renderer = "my_package:MyRenderer"
```

配置中选择：
```python
nb_render_plugin = "my_renderer"
```

## 相关概念

- [四阶段处理管线](03-processing-pipeline.md)
- [代码隐藏与输出控制](09-hiding-code.md)
- [配置系统](04-config-system.md)
- [Glue 变量粘贴](07-glue.md)
