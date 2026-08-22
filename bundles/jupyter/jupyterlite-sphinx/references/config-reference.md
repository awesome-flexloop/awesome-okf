---
type: Reference
title: 配置项完整速查表
description: jupyterlite-sphinx 所有 conf.py 配置项的速查参考，包含默认值、类型和说明
tags: [reference, config, conf.py, options]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: config-ref
    resource: /references/config-reference.md
    title: Configuration reference
---

## 源码位置

所有配置项通过 `app.add_config_value()` 在 `setup()` 函数中注册，位于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1222-1264`。

## JupyterLite 核心配置

| 配置名 | 类型 | 默认值 | rebuild | 说明 |
|--------|------|--------|---------|------|
| `jupyterlite_config` | `str`\|`None` | `None` | html | JupyterLite 构建时配置文件路径（jupyter_lite_config.json） |
| `jupyterlite_overrides` | `str`\|`None` | `None` | html | 运行时设置覆盖文件路径（overrides.json），文件必须存在否则抛出 FileNotFoundError |
| `jupyterlite_dir` | `str` | `str(app.srcdir)` | html | JupyterLite 构建目录（--lite-dir） |
| `jupyterlite_contents` | `str`\|`list[str]`\|`None` | `None` | html | 额外内容路径，支持 glob 模式；目录会复制到 _contents 下保留目录名，文件直接传递 |
| `jupyterlite_ignore_contents` | `str`\|`list[str]`\|`None` | `None` | html | 忽略内容的正则表达式模式列表，传递给 --ignore-contents |
| `jupyterlite_bind_ipynb_suffix` | `bool` | `True` | html | 是否将 .ipynb 后缀绑定到 NotebookLiteParser |
| `jupyterlite_silence` | `bool` | `True` | True | 是否静默 jupyter lite build 输出（失败时仍会打印） |
| `jupyterlite_content_dir` | `str` | `"_contents"` | html | Sphinx 源目录下的内容暂存目录名 |
| `jupyterlite_build_command_options` | `dict`\|`None` | `None` | html | 传递给 `jupyter lite build` 的额外 CLI 参数（字典 key 不加 -- 前缀）；禁止覆盖 contents/output-dir/lite-dir |
| `strip_tagged_cells` | `bool` | `False` | True | 是否剥离带有 `jupyterlite_sphinx_strip` 标签的 notebook 单元格 |

## TryExamples 全局配置

| 配置名 | 类型 | 默认值 | rebuild | 说明 |
|--------|------|--------|---------|------|
| `global_enable_try_examples` | `bool` | `False` | True | 是否全局自动为 autodoc docstring 的 Examples 段注入 try_examples 指令 |
| `try_examples_global_theme` | `str`\|`None` | `None` | True | 全局默认的 example_class CSS 类 |
| `try_examples_global_warning_text` | `str`\|`None` | `None` | True | 全局默认警告文本 |
| `try_examples_global_button_text` | `str`\|`None` | `None` | html | 全局默认按钮文本（None 时使用 "Try it with JupyterLite!"） |
| `try_examples_preamble` | `str`\|`None` | `None` | html | 全局预导入代码，作为 code cell 插入每个生成 notebook 的第2个单元格（在warning之后） |

## 新标签页按钮文本配置

| 配置名 | 类型 | 默认值 | rebuild | 对应指令 |
|--------|------|--------|---------|---------|
| `jupyterlite_new_tab_button_text` | `str` | `"Open as a notebook"` | html | `jupyterlite` |
| `notebooklite_new_tab_button_text` | `str` | `"Open as a notebook"` | html | `notebooklite` |
| `voici_new_tab_button_text` | `str` | `"Open with Voici"` | html | `voici` |
| `replite_new_tab_button_text` | `str` | `"Open in a REPL"` | html | `replite` |

## Replite/REPL 行为配置

| 配置名 | 类型 | 默认值 | rebuild | 说明 |
|--------|------|--------|---------|------|
| `replite_auto_execute` | `bool` | `True` | html | REPL 加载时是否自动执行代码 |
| `replite_clear_cells_on_execute` | `bool` | `False` | html | 执行新单元格时是否清除之前的单元格 |
| `replite_clear_code_content_on_execute` | `bool` | `False` | html | 执行后是否清空提示单元格的代码内容 |
| `replite_hide_code_input` | `bool` | `False` | html | 是否隐藏输入单元格（仅显示输出） |
| `replite_prompt_cell_position` | `str` | `"bottom"` | html | 提示单元格位置：`"bottom"`/`"top"`/`"left"`/`"right"` |
| `replite_show_banner` | `bool` | `True` | html | 是否显示内核 banner |

## 运行时配置（try_examples.json）

此文件放置在 Sphinx 源目录根，部署后可在不重建文档的情况下修改：

| 字段 | 类型 | 说明 |
|------|------|------|
| `global_min_height` | `str`（如 `"400px"`） | iframe 全局最小高度 |
| `ignore_patterns` | `list[str]`（JS 正则） | 匹配 URL pathname 的正则列表，匹配页面的按钮将被隐藏 |

## jupyter lite build 默认启用的 apps

构建命令中默认启用以下 JupyterLite 应用（`--apps` 参数）：

- `notebooks`
- `edit`
- `lab`
- `repl`
- `tree`
- `consoles`
- `voici`（仅当 voici 包已安装时）

## 相关概念

- [配置详解](/concepts/09-configuration.md)
- [构建流程详解](/concepts/10-build-process.md)
- [各指令文档](/concepts/03-directive-overview.md)
