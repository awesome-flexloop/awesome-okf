---
type: Concept
title: 安装与基础配置
description: 安装 jupyterlite-sphinx 扩展并在 conf.py 中完成最小配置
tags: [installation, setup, conf.py]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
  - id: config
    resource: /references/config-reference.md
    title: 配置参考
---

安装 jupyterlite-sphinx 非常简单，通过 pip 即可完成。安装后需要在 Sphinx 项目的 `conf.py` 中进行最小配置，即可在文档中使用 JupyterLite 嵌入指令。

## 环境要求

jupyterlite-sphinx 0.23.0 对运行环境有以下要求：

- **Python**：>= 3.10
- **Sphinx**：>= 4
- **构建系统**：hatchling（包本身使用 hatchling 构建，用户安装时无需关心）

## 基础安装

使用 pip 安装核心包：

```bash
pip install jupyterlite-sphinx
```

核心安装会自动拉取以下运行时依赖：

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| `sphinx` | >= 4 | 文档构建引擎 |
| `jupyterlite-core` | >= 0.2, < 0.9 | JupyterLite 核心构建工具 |
| `docutils` | — | RST 解析（Sphinx 依赖） |
| `jupyter_server` | — | Jupyter 服务端基础组件 |
| `jupyterlab_server` | — | JupyterLab 服务端组件 |
| `nbformat` | — | Notebook 文件格式处理 |

## 可选依赖安装

### Markdown Notebook 支持（jupytext）

如果需要在文档中嵌入 Markdown 格式的 Notebook 文件（`.md` 而非 `.ipynb`），需要安装 `markdown` 可选依赖组，它会安装 `jupytext` 包用于 Markdown 与 Notebook 格式的转换：

```bash
pip install jupyterlite-sphinx[markdown]
```

安装后，`.. jupyterlite::` 和 `.. notebooklite::` 指令可以接受 `.md` 文件作为参数，扩展会在构建时自动调用 jupytext 将其转换为 `.ipynb` 格式。如果未安装此依赖而尝试引用 `.md` 文件，会导致导入错误。

### Voici 仪表板支持

如果需要使用 `.. voici::` 指令嵌入 Voici 仪表板，需要单独安装 `voici` 包：

```bash
pip install voici
```

注意 voici 不在 jupyterlite-sphinx 的可选依赖组中，需要独立安装。构建时扩展会检测 voici 是否可用：如果安装了 voici，`jupyter lite build` 会自动包含 voici 应用；如果未安装而使用了 `.. voici::` 指令，会抛出 `RuntimeError`。

## conf.py 最小配置

安装完成后，需要在 Sphinx 项目的 `conf.py` 文件中将 `jupyterlite_sphinx` 添加到 `extensions` 列表中。最简配置如下：

```python
# conf.py
extensions = [
    'jupyterlite_sphinx',
    # ... 其他扩展
]
```

这是唯一**必需**的配置项。添加扩展后，以下功能立即可用：

- `.. jupyterlite::` 指令
- `.. notebooklite::` 指令（含别名 `.. retrolite::`）
- `.. replite::` 指令
- `.. try_examples::` 指令
- HTML 构建时自动执行 `jupyter lite build`
- 自动将 `.ipynb` 文件注册为源文件后缀（可通过 `jupyterlite_bind_ipynb_suffix` 配置关闭）
- 自动注册相关 CSS/JS 静态资源

## 常用配置项

虽然最小配置即可工作，但 jupyterlite-sphinx 提供了丰富的配置项用于定制行为。以下是最常用的几个配置项：

### JupyterLite 构建配置

```python
# conf.py

# JupyterLite 构建配置文件路径（jupyter_lite_config.json）
jupyterlite_config = None  # str | None

# 运行时设置覆盖文件路径（overrides.json）
jupyterlite_overrides = None  # str | None

# JupyterLite 构建目录（--lite-dir）
jupyterlite_dir = str(app.srcdir)  # 默认使用 Sphinx 源目录

# 额外内容路径，支持 glob 模式，会复制到 _contents 下
jupyterlite_contents = None  # str | list[str] | None

# 忽略内容的正则表达式模式列表
jupyterlite_ignore_contents = None  # str | list[str] | None

# Sphinx 源目录下的内容暂存目录名
jupyterlite_content_dir = "_contents"  # str
```

### 构建行为配置

```python
# conf.py

# 是否静默 jupyter lite build 输出（失败时仍会打印错误信息）
jupyterlite_silence = True  # bool

# 是否剥离带有 jupyterlite_sphinx_strip 标签的 notebook 单元格
strip_tagged_cells = False  # bool

# 是否将 .ipynb 后缀绑定到 NotebookLiteParser
jupyterlite_bind_ipynb_suffix = True  # bool

# 传递给 jupyter lite build 的额外 CLI 参数（字典形式）
jupyterlite_build_command_options = None  # dict | None
```

注意：`jupyterlite_build_command_options` 中禁止覆盖 `contents`、`output-dir`、`lite-dir` 三个参数，违反时会抛出 `RuntimeError`。

### 新标签页按钮文本

当使用 `:new_tab: True` 选项时，各指令对应的按钮默认文本可以通过以下配置项自定义：

```python
# conf.py
jupyterlite_new_tab_button_text = "Open as a notebook"
notebooklite_new_tab_button_text = "Open as a notebook"
voici_new_tab_button_text = "Open with Voici"
replite_new_tab_button_text = "Open in a REPL"
```

这些配置也可以在指令级别通过 `:new_tab_button_text:` 选项覆盖。

### REPL 行为配置

针对 `.. replite::` 指令，有一组专门控制 REPL 行为的配置项：

```python
# conf.py
replite_auto_execute = True               # REPL 加载时是否自动执行代码
replite_clear_cells_on_execute = False    # 执行新单元格时是否清除之前单元格
replite_clear_code_content_on_execute = False  # 执行后是否清空提示单元格代码
replite_hide_code_input = False           # 是否隐藏输入单元格（仅显示输出）
replite_prompt_cell_position = "bottom"   # 提示单元格位置：bottom/top/left/right
replite_show_banner = True                # 是否显示内核 banner
```

这些全局配置可以在指令级别通过对应的蛇形命名选项覆盖（如 `:auto_execute: False`）。

### TryExamples 全局配置

```python
# conf.py

# 是否全局自动为 autodoc docstring 的 Examples 段注入 try_examples 指令
global_enable_try_examples = False  # bool

# 全局默认的 example_class CSS 类
try_examples_global_theme = None  # str | None

# 全局默认警告文本
try_examples_global_warning_text = None  # str | None

# 全局默认按钮文本（None 时使用 "Try it with JupyterLite!"）
try_examples_global_button_text = None  # str | None

# 全局预导入代码，作为 code cell 插入每个生成 notebook 的第2个单元格
try_examples_preamble = None  # str | None
```

## 配置生效时机

配置项的 `rebuild` 属性决定了修改配置后是否需要完全重建文档：

- `rebuild: True` 的配置项：修改后需要完全重新构建（如 `jupyterlite_silence`、`strip_tagged_cells`、`global_enable_try_examples` 等影响全局行为的配置）
- `rebuild: html` 的配置项：修改后只需重新构建 HTML 即可生效（如路径配置、按钮文本、REPL 行为等）

大多数情况下，执行 `make html`（或等效的 `sphinx-build -b html` 命令）即可使所有配置生效。

## 验证安装

安装和配置完成后，可以通过构建文档验证是否正常工作：

```bash
sphinx-build -b html docs/ docs/_build/
```

如果构建成功且输出目录中包含 `lite/` 子目录，说明 jupyterlite-sphinx 已正确安装并集成。构建输出中不应出现与 jupyterlite 相关的错误信息（`jupyterlite_silence=True` 时构建输出会被静默，只有失败时才会打印错误）。

## 相关概念

- [jupyterlite-sphinx 是什么](00-introduction.md)
- [快速开始](02-quick-start.md)
- [指令系统总览](03-directive-overview.md)
