---
type: Concept
title: 配置参考
description: jupyterlite-sphinx 所有 conf.py 配置项详解，包括 JupyterLite 构建配置、TryExamples 配置、REPL 行为配置和运行时配置
tags: [configuration, conf.py, options, settings]
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

jupyterlite-sphinx 扩展通过 Sphinx 的 `conf.py` 文件提供丰富的配置项，用于控制 JupyterLite 构建行为、指令默认参数、TryExamples 全局设置和 REPL 交互行为。所有配置项均通过 `app.add_config_value()` 在扩展的 `setup()` 函数中注册（源码第 1222-1264 行），在 `conf.py` 中直接赋值即可生效。

本文按功能分组详细讲解所有配置项。

## JupyterLite 核心配置

这组配置项控制 JupyterLite 站点的构建过程，影响所有指令嵌入的 JupyterLite 环境。

### jupyterlite_config

- **类型**：`str | None`
- **默认值**：`None`
- **是否触发重建**：是（html 页面重建）

指定 JupyterLite 构建配置文件（`jupyter_lite_config.json`）的路径。该文件用于自定义 JupyterLite 站点的构建行为，例如指定启用的应用、安装额外的包、配置内核等。

```python
# conf.py
jupyterlite_config = "jupyter_lite_config.json"
```

### jupyterlite_overrides

- **类型**：`str | None`
- **默认值**：`None`
- **是否触发重建**：是

指定 JupyterLite 运行时设置覆盖文件（`overrides.json`）的路径。该文件用于覆盖 JupyterLab/Notebook 的设置（如主题、字体、快捷键等），在 JupyterLite 启动时应用。文件必须存在，否则会抛出 `FileNotFoundError`。

```python
jupyterlite_overrides = "overrides.json"
```

### jupyterlite_dir

- **类型**：`str`
- **默认值**：`str(app.srcdir)`（即 Sphinx 源目录）
- **是否触发重建**：是

指定 JupyterLite 的构建工作目录（对应 `jupyter lite build` 的 `--lite-dir` 参数）。JupyterLite 的中间构建产物和最终输出都存放在此目录下。默认使用 Sphinx 的源目录，通常不需要修改。

### jupyterlite_contents

- **类型**：`str | list[str] | None`
- **默认值**：`None`
- **是否触发重建**：是

指定额外的内容路径，这些路径下的文件会被纳入 JupyterLite 的文件系统。支持 glob 模式匹配，方便批量包含 Notebook 和数据文件。

- **路径是目录时**：整个目录会被复制到 `_contents/` 下，保留目录名
- **路径是文件时**：文件直接传递给 JupyterLite 构建

```python
# 单个目录
jupyterlite_contents = "notebooks"

# 多个路径，支持 glob
jupyterlite_contents = ["notebooks/*.ipynb", "data/", "examples/tutorial*.ipynb"]
```

各指令中引用的 Notebook 文件也会自动复制到 `_contents/`，不需要在此配置。

### jupyterlite_ignore_contents

- **类型**：`str | list[str] | None`
- **默认值**：`None`
- **是否触发重建**：是

指定忽略内容的正则表达式模式列表，匹配的文件不会被包含到 JupyterLite 构建中。对应 `jupyter lite build` 的 `--ignore-contents` 参数。

```python
jupyterlite_ignore_contents = [r"_draft/.*", r".*\.tmp\.ipynb"]
```

### jupyterlite_bind_ipynb_suffix

- **类型**：`bool`
- **默认值**：`True`
- **是否触发重建**：是

控制是否将 `.ipynb` 文件后缀绑定到 `NotebookLiteParser` 解析器。启用后，直接放置在 Sphinx 源目录中的 `.ipynb` 文件会被自动解析为包含 `notebooklite` 指令的文档页面，无需手动编写 RST 文件。

```python
jupyterlite_bind_ipynb_suffix = True  # 默认启用
```

### jupyterlite_silence

- **类型**：`bool`
- **默认值**：`True`
- **是否触发重建**：是（配置值变更触发）

控制是否静默 `jupyter lite build` 命令的输出。设为 `True` 时，构建过程中的 stdout 输出会被抑制（构建失败时 stderr 仍会打印），保持 Sphinx 构建日志的整洁。

```python
jupyterlite_silence = True  # 默认静默
```

### jupyterlite_content_dir

- **类型**：`str`
- **默认值**：`"_contents"`
- **是否触发重建**：是

Sphinx 源目录下用于暂存 Notebook 内容的目录名。各指令引用的 Notebook 文件以及 try_examples 生成的 Notebook 文件都会先复制到这个目录，再由 JupyterLite 构建流程处理。通常不需要修改。

### jupyterlite_build_command_options

- **类型**：`dict | None`
- **默认值**：`None`
- **是否触发重建**：是

传递给 `jupyter lite build` 命令的额外 CLI 参数，以字典形式指定，字典的 key 不需要加 `--` 前缀。

```python
jupyterlite_build_command_options = {
    "debug": True,
    "output-archive": "jupyterlite-build.zip",
}
```

**禁止覆盖的选项**：以下三个选项由扩展内部管理，在 `jupyterlite_build_command_options` 中设置会被忽略：

- `contents`：由 `jupyterlite_contents` 和各指令的文件引用自动管理
- `output-dir`：固定为 Sphinx 输出目录下的 `lite/` 子目录
- `lite-dir`：由 `jupyterlite_dir` 配置控制

### strip_tagged_cells

- **类型**：`bool`
- **默认值**：`False`
- **是否触发重建**：是（配置值变更触发）

控制是否剥离 Notebook 中带有 `jupyterlite_sphinx_strip` 标签的单元格。这对于在 Notebook 中包含不希望在 JupyterLite 嵌入中显示的单元格（如解答代码、测试代码等）非常有用。

```python
strip_tagged_cells = True
```

在 Notebook 的单元格 metadata 中添加 `"tags": ["jupyterlite_sphinx_strip"]` 即可标记该单元格在嵌入时被移除。

## TryExamples 全局配置

这组配置项控制 [try_examples 指令](/concepts/08-try-examples-directive.md) 的全局默认行为。

### global_enable_try_examples

- **类型**：`bool`
- **默认值**：`False`
- **是否触发重建**：是（配置值变更触发）

是否全局启用 autodoc 自动注入。启用后，Sphinx autodoc 扩展在处理 Python docstring 中的 `Examples` 段时，会自动将其包裹在 `try_examples` 指令中，无需手动编写 RST 标记。

```python
global_enable_try_examples = True
```

启用后，可以通过在 docstring 中添加 `.. disable_try_examples` 注释来排除特定 Examples 段。

### try_examples_global_theme

- **类型**：`str | None`
- **默认值**：`None`
- **是否触发重建**：是

全局默认的 `example_class` CSS 类名，应用于所有 try_examples 实例的容器。指令级别的 `:theme:` 选项会覆盖此全局值。

```python
try_examples_global_theme = "my-custom-example"
```

### try_examples_global_warning_text

- **类型**：`str | None`
- **默认值**：`None`
- **是否触发重建**：是

全局默认的警告文本，会在每个生成的 Notebook 顶部显示。指令级别的 `:warning_text:` 选项会覆盖此全局值。

```python
try_examples_global_warning_text = "注意：示例代码在浏览器中运行，修改后请重新执行单元格。"
```

### try_examples_global_button_text

- **类型**：`str | None`
- **默认值**：`None`（使用内置默认值 `"Try it with JupyterLite!"`）
- **是否触发重建**：是

全局默认的 "Try it" 按钮文本。指令级别的 `:button_text:` 选项会覆盖此全局值。

```python
try_examples_global_button_text = "在线运行示例"
```

### try_examples_preamble

- **类型**：`str | None`
- **默认值**：`None`
- **是否触发重建**：是

全局预导入代码，作为独立的代码单元格插入到每个生成的 Notebook 中（位于 warning 单元格之后、示例代码单元格之前）。用于统一导入常用库。

```python
try_examples_preamble = """
import numpy as np
import matplotlib.pyplot as plt
"""
```

## 新标签页按钮文本配置

这组配置项自定义各指令在新标签页模式下按钮的默认显示文本：

| 配置名 | 默认值 | 对应指令 |
|--------|--------|---------|
| `jupyterlite_new_tab_button_text` | `"Open as a notebook"` | [jupyterlite](/concepts/04-jupyterlite-directive.md) |
| `notebooklite_new_tab_button_text` | `"Open as a notebook"` | [notebooklite](/concepts/05-notebooklite-directive.md) |
| `voici_new_tab_button_text` | `"Open with Voici"` | [voici](/concepts/07-voici-directive.md) |
| `replite_new_tab_button_text` | `"Open in a REPL"` | [replite](/concepts/06-replite-directive.md) |

```python
# 统一设置为中文
jupyterlite_new_tab_button_text = "在 JupyterLab 中打开"
notebooklite_new_tab_button_text = "在 Notebook 中打开"
voici_new_tab_button_text = "打开仪表板"
replite_new_tab_button_text = "打开 REPL 控制台"
```

指令级别的 `:new_tab_button_text:` 选项会覆盖对应的全局配置值。

## REPL 行为配置

这组配置项控制 [replite 指令](/concepts/06-replite-directive.md) 中 REPL 控制台的默认行为：

| 配置名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `replite_auto_execute` | `bool` | `True` | REPL 加载时是否自动执行预填代码 |
| `replite_clear_cells_on_execute` | `bool` | `False` | 执行新单元格时是否清除之前的单元格输出 |
| `replite_clear_code_content_on_execute` | `bool` | `False` | 执行后是否清空提示单元格的代码内容 |
| `replite_hide_code_input` | `bool` | `False` | 是否隐藏代码输入区域（仅显示输出） |
| `replite_prompt_cell_position` | `str` | `"bottom"` | 输入提示单元格位置：`"bottom"`/`"top"`/`"left"`/`"right"` |
| `replite_show_banner` | `bool` | `True` | 是否显示内核启动 banner 信息 |

```python
# REPL 示例配置
replite_auto_execute = False          # 不自动执行，让读者手动点击运行
replite_prompt_cell_position = "top" # 输入框在顶部
replite_show_banner = False          # 隐藏 banner 节省空间
```

指令级别的对应选项（如 `:execute:`、`:hide_code_input:` 等）会覆盖全局配置值。

## 运行时配置（try_examples.json）

除了 `conf.py` 中的构建时配置外，try_examples 还支持通过 `try_examples.json` 文件进行**运行时配置**——该文件放置在 Sphinx 源目录根下，部署后可直接编辑修改，无需重新构建 HTML 文档。前端 JavaScript 在页面加载时通过 fetch 请求读取该文件。

| 字段 | 类型 | 说明 |
|------|------|------|
| `global_min_height` | 字符串（如 `"400px"`） | 所有 try_examples iframe 的全局最小高度 |
| `ignore_patterns` | 字符串数组（JS 正则表达式） | 匹配 URL pathname 的正则列表，匹配页面的 try_examples 按钮将被隐藏 |

示例配置文件：

```json
{
  "global_min_height": "500px",
  "ignore_patterns": ["/api/", "/changelog/", ".*-dev/"]
}
```

`ignore_patterns` 使用 JavaScript 正则表达式语法，对当前页面的 `window.location.pathname` 进行匹配测试。匹配成功时，该页面上所有 try_examples 按钮会被自动隐藏。这可用于在 API 参考页、变更日志等不适合交互式示例的页面自动禁用功能。

如果 `try_examples.json` 文件不存在（404），前端会静默忽略，不会报错。

## 配置项与 rebuild 类型

每个配置项的 rebuild 类型决定了配置值变更后 Sphinx 需要重新构建的范围：

- **html**：HTML 输出需要重新生成（环境文档不需要重新解析）
- **True**（空值表示完全重建）：需要完全重新构建（环境数据失效）

大多数 JupyterLite 相关配置变更后都需要重新运行 `jupyter lite build`，因此 rebuild 类型为 `html`。影响 docstring 解析和指令生成的配置（如 `global_enable_try_examples`、`strip_tagged_cells`）需要完全重建。

## 完整配置示例

以下是一个较为完整的 `conf.py` 配置示例，展示常用配置项的组合使用：

```python
# conf.py

# -- JupyterLite 核心配置 --
jupyterlite_dir = "docs"
jupyterlite_contents = ["notebooks", "data"]
jupyterlite_config = "jupyter_lite_config.json"
jupyterlite_silence = True
strip_tagged_cells = True
jupyterlite_build_command_options = {
    "debug": False,
}

# -- TryExamples 配置 --
global_enable_try_examples = True
try_examples_global_button_text = "在线运行"
try_examples_global_warning_text = "示例代码在浏览器端执行，可能需要几秒加载。"
try_examples_preamble = """
import numpy as np
import matplotlib.pyplot as plt
"""

# -- REPL 配置 --
replite_auto_execute = True
replite_show_banner = False
replite_prompt_cell_position = "bottom"

# -- 按钮文本 --
jupyterlite_new_tab_button_text = "在 JupyterLab 中打开"
notebooklite_new_tab_button_text = "在 Notebook 中打开"
replite_new_tab_button_text = "打开 REPL"
voici_new_tab_button_text = "打开仪表板"
```

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [jupyterlite 指令——嵌入 JupyterLab](/concepts/04-jupyterlite-directive.md)
- [notebooklite 指令——嵌入经典 Notebook](/concepts/05-notebooklite-directive.md)
- [replite 指令——嵌入交互式 REPL](/concepts/06-replite-directive.md)
- [voici 指令——嵌入 Voici 仪表板](/concepts/07-voici-directive.md)
- [try_examples 指令——交互式文档示例](/concepts/08-try-examples-directive.md)
- [核心模块源码](/references/main-source.md)
- [配置项完整速查表](/references/config-reference.md)
