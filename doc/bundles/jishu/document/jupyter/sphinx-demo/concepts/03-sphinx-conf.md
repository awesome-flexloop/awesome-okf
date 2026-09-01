---
type: Concept
title: Sphinx conf.py 配置详解
description: conf.py 中所有 jupyterlite-sphinx 相关配置项的详细说明，包括扩展列表、核心配置、TryExamples、主题选项
tags: [conf.py, sphinx, configuration, extensions, theme]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: conf-py
    resource: /references/conf-py-source.md
    title: Pyodide/Xeus conf.py 源码
---

## 扩展配置

### 核心扩展列表

```python
extensions = [
    "sphinx.ext.autodoc",       # 从 docstring 自动生成 API 文档
    "sphinx.ext.mathjax",       # 渲染 LaTeX 数学公式（如 $E=mc^2$）
    "sphinx.ext.autosummary",   # 自动生成 API 摘要表
    "sphinx.ext.doctest",       # 运行文档中的 doctest 示例
    "jupyterlite_sphinx",       # ← JupyterLite 集成的核心扩展
    "sphinx_design",            # 提供 dropdown、卡片等 UI 组件
    "myst_nb",                  # MyST Markdown + Jupyter Notebook 支持
    "numpydoc",                 # 解析 NumPy 风格的 docstring
]
```

理解每个扩展的作用有助于排查问题：

- **`jupyterlite_sphinx`**：提供 `jupyterlite`/`notebooklite`/`replite`/`voici`/`try_examples` 指令，是本项目的核心
- **`numpydoc`**：解析 NumPy 风格 docstring 中的 Parameters/Returns/Examples 等节，是 TryExamples 功能的前提——autodoc 需要它来正确提取 Examples 节
- **`myst_nb`**：支持在 Markdown 中嵌入 Notebook 单元格（`{code-cell}`），并处理 `.ipynb` 文件
- **`sphinx_design`**：demo 首页使用 `{dropdown}` 和 `{grid}` 指令创建交互式卡片布局

### sys.path 配置

```python
import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("disabled_examples"))
```

这两行将文档源目录添加到 Python 路径，使得 `automodule` 指令可以导入 `example.py` 和 `disabled_examples/disabled_example.py`。如果你的文档代码在其他位置，需要相应调整路径。

## JupyterLite 核心配置项

### jupyterlite_contents

```python
jupyterlite_contents = ["custom_contents/*"]
```

此配置指定哪些文件/目录应被包含到 JupyterLite 环境中。取值为 glob 模式列表：

- 匹配的文件会被复制到 JupyterLite 的文件系统中
- 用户打开 JupyterLite 时可以直接访问这些文件
- glob 路径相对于 `conf.py` 所在目录

常见用法：
```python
jupyterlite_contents = ["notebooks/*.ipynb", "data/*"]
```

### jupyterlite_silence

```python
jupyterlite_silence = True
```

控制 JupyterLite CLI 构建过程的输出详细程度：
- `True`：静默模式（默认），只显示错误
- `False`：显示详细构建日志

demo 在 CI 中通过 `-D jupyterlite_silence=0` 覆盖此设置，以便排查构建问题。

### strip_tagged_cells

```python
strip_tagged_cells = True
```

启用后，带有 `jupyterlite_sphinx_strip` 标签的 Notebook 单元格会在 JupyterLite Notebook 中被移除，但在 Sphinx 渲染的文档页面中保留。

典型用途：在 Notebook 开头添加解释性 Markdown 单元格，这些说明在文档中可见，但在用户点击按钮打开的可执行 Notebook 中不会出现，避免干扰代码执行。

详细说明见 [07-notebook-embedding](07-notebook-embedding.md)。

## TryExamples 配置项

### global_enable_try_examples

```python
global_enable_try_examples = True
```

这是 TryExamples 功能的总开关。启用后：
- Sphinx 构建时会自动检测 `automodule` 页面中 docstring 的 Examples 节
- 在每个代码示例块旁自动插入"Try it online"按钮
- 无需手动添加 `.. try_examples::` 指令

关闭后，只有显式使用 `.. try_examples::` 指令的位置才会显示按钮。

### try_examples_global_button_text

```python
try_examples_global_button_text = "Try it online"
```

所有自动生成的 TryExamples 按钮上显示的文本。每个指令也可以通过 `:button_text:` 选项单独覆盖。

### try_examples_global_warning_text

demo 中设置的警告文本：

```python
try_examples_global_warning_text = (
    "Interactive examples are experimental, and may not work as expected "
    "when compared to the native Jupyter experience. Please report issues "
    "and help us improve."
)
```

这段文本以 admonition（提示框）形式显示在交互式 iframe 上方，告知用户这是实验性功能。支持 Markdown 格式。

## MyST-NB 配置

```python
nb_execution_mode = "auto"
```

控制 Notebook 的执行模式：
- `"auto"`：如果 Notebook 有输出则不执行，没有输出则执行
- `"force"`：始终执行 Notebook（CI 推荐，确保代码可运行）
- `"off"`：不执行 Notebook
- `"cache"`：仅当源文件变化时重新执行

对于包含 JupyterLite 交互内容的文档，通常使用 `"auto"` 或 `"off"`，因为实际代码执行发生在用户的浏览器中，而非构建时。

## 主题与静态资源

### html_theme 和 html_static_path

```python
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["button_styling.css"]
```

demo 使用 PyData Sphinx Theme，并加载自定义 CSS 文件 `button_styling.css` 来美化 TryExamples 按钮。自定义 CSS/JS 文件放在 `_static/` 目录下，通过 `html_css_files`/`html_js_files` 引用。

### html_context（GitHub 编辑链接）

```python
html_context = {
    "github_url": "https://github.com",
    "github_user": "jupyterlite",
    "github_repo": "sphinx-demo",
    "github_version": "main",
    "doc_path": "pyodide-kernel-example/docs/source/",
}
```

配合 PyData 主题的 `use_edit_page_button: True`，在页面底部显示"编辑此页"链接，跳转到 GitHub 上对应文件的编辑页面。`doc_path` 是从仓库根到文档源目录的相对路径，Pyodide 和 Xeus 两个示例的 `doc_path` 不同。

## 完整配置速查

所有配置项的完整列表和默认值见 [/references/conf-py-source.md](../references/conf-py-source.md)。

## 相关内容

- [02-quick-start](02-quick-start.md)
- [04-kernel-comparison](04-kernel-comparison.md)
- [05-config-files](05-config-files.md)
- [06-try-examples](06-try-examples.md)
- [/references/conf-py-source.md](../references/conf-py-source.md)
