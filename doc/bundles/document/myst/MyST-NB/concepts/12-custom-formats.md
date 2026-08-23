---
type: Concept
title: 自定义格式与扩展
description: nb_custom_formats 注册自定义 Notebook 格式读取器、自定义渲染器插件、自定义 MIME 渲染器
tags: [myst-nb, custom-format, extension, plugin, entry-point]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 自定义格式与扩展

MyST-NB 支持三种扩展机制：自定义文件格式读取器、自定义渲染器插件、自定义 MIME 渲染器。

## 自定义文件格式（nb_custom_formats）

通过 `nb_custom_formats` 配置注册额外的文件后缀和对应的读取函数，使 MyST-NB 能够处理非标准格式的 notebook 文件（如 R Markdown、.Rmd 等）。

### 配置格式

```python
nb_custom_formats = {
    ".Rmd": ["myst_nb.converters.rmd_to_nb", {"some_option": True}, False],
    ".py": ["my_package.py_to_nb", {}, True],  # commonmark_only=True
}
```

每个后缀映射一个长度为 2 或 3 的元组：
- `[0]`：读取函数的 Python 对象路径（字符串），通过 `sphinx.util.import_object` 动态加载
- `[1]`：传递给读取函数的关键字参数（dict）
- `[2]`（可选）：bool，表示是否以 CommonMark -only 模式解析 Markdown cell

如果只提供字符串（而非元组），等价于 `(string, {}, False)`。

### 读取函数签名

```python
def my_reader(text: str, **kwargs) -> nbformat.NotebookNode:
    """读取自定义格式文本，返回 NotebookNode。
    
    Parameters
    ----------
    text : str
        文件内容（UTF-8 字符串）
    **kwargs
        配置中指定的额外参数
    
    Returns
    -------
    nbformat.NotebookNode
        nbformat v4 格式的 notebook 对象
    """
    # 解析 text 并构建 notebook
    import nbformat as nbf
    nb = nbf.v4.new_notebook()
    # ... 解析逻辑 ...
    return nb
```

### 后缀匹配

后缀按长度降序匹配，最长匹配优先：
- `file.tar.gz.md` → 优先匹配 `.tar.gz.md`，再匹配 `.gz.md`，最后 `.md`
- 标准后缀 `.ipynb` 总是可用（standard_nb_read）
- `.md` 文件特殊处理：只有 frontmatter 含 `file_format: mystnb` 才作为 notebook

### 内置格式

- `.ipynb`：标准 Jupyter Notebook 格式（默认）
- `.md`（带 mystnb frontmatter）：MyST 文本格式 Notebook
- jupytext 支持：通过 jupytext 包可以读取 .Rmd、.py:percent 等格式

## 自定义渲染器插件

通过 `myst_nb.renderers` entry point 注册自定义 Notebook 元素渲染器，替换默认的 `NbElementRenderer`。

### 注册方式

```toml
# pyproject.toml
[project.entry-points."myst_nb.renderers"]
my_renderer = "my_package:MyRenderer"
```

配置中选择：
```python
nb_render_plugin = "my_renderer"
```

### 渲染器基类

自定义渲染器应继承或实现与 `NbElementRenderer` 相同的接口。渲染器负责：
- 渲染 code cell 源码（语法高亮）
- 渲染 code cell 输出（根据 MIME 类型选择渲染方式）
- 处理 glue 数据
- 处理 stderr

## 自定义 MIME 渲染器

通过 `myst_nb.mime_renderers` entry point 注册自定义 MIME 类型渲染插件，处理默认渲染器不支持的 MIME 类型。

### 注册方式

```toml
[project.entry-points."myst_nb.mime_renderers"]
plotly = "my_package:PlotlyMimeRenderer"
```

### MIME 渲染器用途

默认渲染器支持以下 MIME 类型：
- text/plain（ANSI 高亮）
- text/html
- text/markdown
- text/latex
- image/png, image/jpeg, image/gif, image/webp, image/svg+xml, application/pdf
- application/vnd.jupyter.widget-state+json
- application/vnd.jupyter.widget-view+json
- error/traceback
- application/papermill.record+*（glue 内部数据）

自定义 MIME 渲染器可扩展支持：
- Plotly（application/vnd.plotly.v1+json）
- Bokeh（application/vnd.bokehjs_load.v0+json）
- Altair（application/vnd.vegalite.v4+json）
- 自定义数据可视化库

## 自定义 Pygments Lexer

MyST-NB 注册了两个自定义 Pygments Lexer（通过 entry points）：

```toml
[project.entry-points."pygments.lexers"]
myst-ansi = "myst_nb.core.lexers:AnsiColorLexer"
ipythontb = "myst_nb.core.lexers:IPythonTracebackLexer"
```

- **AnsiColorLexer**（myst-ansi）：解析终端 ANSI 颜色代码，渲染彩色终端输出
- **IPythonTracebackLexer**（ipythontb）：高亮 IPython traceback 输出

可以在 `nb_render_text_lexer` 和 `nb_render_error_lexer` 中使用这些 lexer 或自定义的 Pygments Lexer。

## 自定义 jupyter-cache Reader

通过 `jcache.readers` entry point 注册自定义 jupyter-cache 读取插件：

```toml
[project.entry-points."jcache.readers"]
myst_nb_md = "myst_nb.core.read:myst_nb_reader_plugin"
```

这使得 jupyter-cache 能够识别和缓存 MyST 文本格式的 notebook。

## 扩展开发建议

1. **自定义格式**适合：需要支持特殊 notebook 文件格式（如 R Markdown、Python 脚本格式）
2. **自定义渲染器**适合：需要完全改变 notebook 元素渲染方式（如特殊输出格式）
3. **自定义 MIME 渲染器**适合：添加新的 MIME 输出类型支持（最常用的扩展方式）
4. 所有扩展通过 entry points 注册，无需修改 MyST-NB 源码

## 相关概念

- [渲染与 MIME 类型](06-render-and-mime.md)
- [MyST Notebook 文件格式](02-notebook-format.md)
- [配置系统](04-config-system.md)
- [四阶段处理管线](03-processing-pipeline.md)
