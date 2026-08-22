---
type: Example
title: 嵌入现有 Notebook 文件
description: 将 .ipynb 或 MyST Markdown Notebook 文件嵌入文档并自动打开
tags: [example, notebook, ipynb, myst]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

本示例演示如何将已有的 Jupyter Notebook 文件（`.ipynb`）或 MyST Markdown Notebook 文件（`.md`，需要 jupytext 支持）嵌入到 Sphinx 文档中。与空白 JupyterLab 环境不同，嵌入 Notebook 文件后，JupyterLite 会自动打开指定的 Notebook 文件，读者可以直接查看和运行其中的代码单元格，无需手动创建文件。

## 项目结构

```
my-docs/
├── conf.py
├── index.rst
├── notebooks/
│   └── my_notebook.ipynb      # 要嵌入的 Notebook 文件
├── markdown_notebooks/
│   └── my_markdown_notebook.md  # MyST Markdown Notebook（可选）
└── _build/
```

## conf.py 配置

```python
# conf.py

project = 'Notebook Embed Demo'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

extensions = [
    'jupyterlite_sphinx',
]

html_theme = 'alabaster'

# 可选：启用 strip_tagged_cells，自动去除带有
# "jupyterlite_sphinx_strip" 标签的单元格
strip_tagged_cells = True
```

## RST 中嵌入 .ipynb 文件

在 `.. jupyterlite::` 指令后传入 Notebook 文件的路径作为参数，JupyterLite 会自动在 iframe 中打开该 Notebook：

```rst
嵌入 Notebook 示例
=================

下面嵌入了一个演示 Notebook：

.. jupyterlite:: notebooks/my_notebook.ipynb
   :width: 100%
   :height: 600px
   :prompt: 打开演示 Notebook
```

指令参数（即 Notebook 路径）遵循 Sphinx 的文件路径解析规则，与 `literalinclude` 等指令一致：

- **相对路径**（如上例 `notebooks/my_notebook.ipynb`）：相对于当前 RST 源文件所在目录
- **绝对路径**（以 `/` 开头，如 `/notebooks/my_notebook.ipynb`）：相对于 Sphinx 文档根目录（`conf.py` 所在目录）

构建时，jupyterlite-sphinx 会自动将引用的 Notebook 文件复制到内容暂存目录 `_contents/` 下，供 JupyterLite 构建系统打包到最终的静态站点中。

## 在新标签页中打开

使用 `:new_tab:` 选项可以将 Notebook 在新浏览器标签页中打开，而非嵌入到当前页面的 iframe 中：

```rst
.. jupyterlite:: notebooks/my_notebook.ipynb
   :new_tab: True
   :new_tab_button_text: 在新标签页中打开 Notebook
```

`:new_tab: True` 渲染为一个按钮，点击后调用 `window.open()` 在新标签页中打开 JupyterLite 并加载指定 Notebook。`:new_tab_button_text:` 可自定义按钮文本；若不指定，默认使用全局配置 `jupyterlite_new_tab_button_text` 的值（默认为 "Open as a notebook"）。

## 嵌入 MyST Markdown Notebook（.md 文件）

jupyterlite-sphinx 支持嵌入 MyST Markdown 格式的 Notebook 文件（通常由 jupytext 维护），但需要安装 jupytext 依赖：

```bash
pip install "jupyterlite-sphinx[markdown]"
```

在 RST 中引用 `.md` 文件的方式与 `.ipynb` 完全一致：

```rst
.. jupyterlite:: markdown_notebooks/my_markdown_notebook.md
   :width: 100%
   :height: 600px
   :prompt: 打开 Markdown Notebook
```

构建过程中，jupyterlite-sphinx 会自动调用 jupytext 将 `.md` 文件转换为 `.ipynb` 格式，并存储在 `_contents/` 目录下。转换会检查文件修改时间（mtime），仅在源文件比目标文件新时才重新转换，避免不必要的重复构建。

若未安装 jupytext 却尝试引用 `.md` 文件，构建时会抛出 `ImportError` 并提示安装 `jupyterlite-sphinx[markdown]`。

## 使用 notebooklite 指令

除了 `jupyterlite` 指令（对应 JupyterLab 界面），还可以使用 `notebooklite` 指令，它使用 JupyterLite 的 tree（文件树）视图打开 Notebook：

```rst
.. notebooklite:: notebooks/my_notebook.ipynb
   :width: 100%
   :height: 600px
   :prompt: 在经典 Notebook 界面中打开
```

`notebooklite` 指令（别名为 `retrolite`，向后兼容）对应的 JupyterLite 应用路径为 `tree/`，Notebook 路径前缀为 `../notebooks/`，提供类似经典 Jupyter Notebook 的界面体验。`jupyterlite` 指令则使用 `lab/` 路径，提供 JupyterLab 界面。

## strip_tagged_cells：去除标记单元格

在 conf.py 中设置 `strip_tagged_cells = True` 后，构建时会自动从 Notebook 中移除带有 `jupyterlite_sphinx_strip` 标签（tag）的单元格。这在以下场景中非常有用：

- Notebook 中包含仅用于文档说明但不需要在交互式环境中执行的单元格
- 需要隐藏某些教学提示或答案单元格
- 需要区分"阅读版本"和"交互版本"的内容

为 Notebook 单元格添加标签的方法：在 JupyterLab 中选中单元格，打开右侧属性面板（Property Inspector），在 "Tags" 部分添加 `jupyterlite_sphinx_strip` 标签，然后保存 Notebook。

```python
# conf.py
strip_tagged_cells = True
```

启用此选项后，被标记的单元格在复制到 `_contents/` 目录时会被移除，JupyterLite 中打开的 Notebook 不包含这些单元格。对于 Markdown Notebook 文件（`.md`），此选项同样生效——转换后的 `.ipynb` 中被标记的单元格也会被剥离。

## 路径解析规则详解

理解 Notebook 文件路径解析对于正确组织项目结构至关重要：

1. **相对路径**：如 `notebooks/demo.ipynb`，Sphinx 的 `relfn2path()` 方法将其解析为相对于当前 RST 源文件所在目录的绝对路径
2. **绝对路径**：如 `/examples/demo.ipynb`（以 `/` 开头），相对于 Sphinx 源目录（`conf.py` 所在目录，即 `app.srcdir`）
3. **依赖追踪**：通过 `env.note_dependency(rel_filename)` 注册文件依赖，当 Notebook 文件修改时，Sphinx 会自动标记引用该文件的文档为需要重新构建
4. **文件名冲突**：多个指令引用不同路径但同名的 Notebook 文件时，由于相对路径的保留，不会发生冲突——它们在 `_contents/` 中保持各自的相对目录结构

## 完整示例：index.rst

```rst
Notebook 嵌入演示
================

.. jupyterlite:: notebooks/intro.ipynb
   :width: 100%
   :height: 500px
   :prompt: 交互式入门教程

或者在新标签页中打开：

.. jupyterlite:: notebooks/advanced.ipynb
   :new_tab: True
   :new_tab_button_text: 打开高级教程（新标签页）
```

## 相关概念

- [jupyterlite 指令详解](/concepts/04-jupyterlite-directive.md)
- [notebooklite 指令详解](/concepts/05-notebooklite-directive.md)
- [构建流程](/concepts/10-build-process.md)
- [配置参考](/references/config-reference.md)
- [核心模块源码](/references/main-source.md)
