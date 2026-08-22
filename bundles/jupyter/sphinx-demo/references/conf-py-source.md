---
type: Reference
title: conf.py 配置项完整速查
description: sphinx-demo 中 conf.py 所有 jupyterlite-sphinx 相关配置项的完整登记，包含类型、默认值、取值说明和源码位置
tags: [conf.py, sphinx, configuration, jupyterlite-sphinx]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyodide-conf
    resource: /references/conf-py-source.md
    title: Pyodide 示例 conf.py
  - id: xeus-conf
    resource: /references/conf-py-source.md
    title: Xeus 示例 conf.py
---

## conf.py 配置项完整速查

本信源文档登记 sphinx-demo 项目中 `conf.py` 内所有与 `jupyterlite-sphinx` 集成相关的配置项。

## 项目基本信息

| 配置项 | 取值 | 说明 |
|--------|------|------|
| `project` | `"jupyterlite-sphinx-demo"` | Sphinx 项目名称 |
| `copyright` | `"2025, JupyterLite Contributors"` | 版权声明 |
| `author` | `"JupyterLite Contributors"` | 作者 |
| `release` | `"1.0.0"` | 版本号 |

## Sphinx 扩展列表

```python
extensions = [
    "sphinx.ext.autodoc",        # 自动文档生成
    "sphinx.ext.mathjax",        # LaTeX 数学公式渲染
    "sphinx.ext.autosummary",    # 自动摘要
    "sphinx.ext.doctest",        # doctest 测试
    "jupyterlite_sphinx",        # JupyterLite 集成核心扩展
    "sphinx_design",             # UI 组件（dropdown、卡片等）
    "myst_nb",                   # MyST Markdown notebook 支持
    "numpydoc",                  # NumPy 风格 docstring 解析
]
```

## jupyterlite-sphinx 核心配置

| 配置项 | 类型 | 默认值 | demo 取值 | 说明 |
|--------|------|--------|-----------|------|
| `jupyterlite_contents` | `list[str]` | `None` | `["custom_contents/*"]` | glob 模式列表，匹配的文件/目录作为 JupyterLite 站点内容 |
| `jupyterlite_silence` | `bool` | `True` | `True` | 是否静默 JupyterLite 构建输出（CI 中通过 `-D jupyterlite_silence=0` 覆盖） |
| `strip_tagged_cells` | `bool` | `False` | `True` | 是否从 Notebook 中剥离带有 `jupyterlite_sphinx_strip` 标签的单元格 |
| `jupyterlite_dir` | `str` | `str(app.srcdir)` | 未设置（使用默认） | JupyterLite 构建输出目录 |
| `jupyterlite_config` | `str` | `None` | 未设置 | jupyter_lite_config.json 路径 |
| `jupyterlite_overrides` | `str` | `None` | 未设置 | overrides.json 路径 |
| `jupyterlite_bind_ipynb_suffix` | `bool` | `True` | 未设置（使用默认） | 是否绑定 .ipynb 后缀到 NotebookLiteParser |

## TryExamples 配置

| 配置项 | 类型 | 默认值 | demo 取值 | 说明 |
|--------|------|--------|-----------|------|
| `global_enable_try_examples` | `bool` | `False` | `True` | 是否全局自动为 docstring Examples 节插入 TryExamples 按钮 |
| `try_examples_global_button_text` | `str` | `None` | `"Try it online"` | 所有 TryExamples 按钮的全局文本 |
| `try_examples_global_warning_text` | `str` | `None` | Markdown 格式警告消息 | 交互式示例顶部的实验性警告 |
| `try_examples_global_theme` | `str` | `None` | 未设置 | TryExamples iframe 的 JupyterLab 主题 |
| `try_examples_preamble` | `str` | `None` | 未设置 | 每个示例 notebook 顶部插入的预导入代码 |
| `jupyterlite_content_dir` | `str` | `"_contents"` | 未设置（使用默认） | Notebook 内容在构建目录中的子目录名 |

## 新标签页按钮文本配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `jupyterlite_new_tab_button_text` | `"Open as a notebook"` | jupyterlite 指令新标签页按钮文本 |
| `notebooklite_new_tab_button_text` | `"Open as a notebook"` | notebooklite 指令新标签页按钮文本 |
| `voici_new_tab_button_text` | `"Open with Voici"` | voici 指令新标签页按钮文本 |
| `replite_new_tab_button_text` | `"Open in a REPL"` | replite 指令新标签页按钮文本 |

## REPL 配置（demo 中未显式设置）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `replite_auto_execute` | `True` | REPL 是否自动执行代码 |
| `replite_show_banner` | `True` | 是否显示 REPL banner |
| `replite_prompt_cell_position` | `"bottom"` | 提示单元格位置（bottom/top/left/right） |

## MyST-NB 配置

| 配置项 | 取值 | 说明 |
|--------|------|------|
| `nb_execution_mode` | `"auto"` | Notebook 执行模式（auto/force/off/cache） |

## HTML 主题配置

| 配置项 | 取值 | 说明 |
|--------|------|------|
| `html_theme` | `"pydata_sphinx_theme"` | 使用 PyData Sphinx Theme |
| `html_logo` | `"_static/icon.svg"` | 站点 Logo |
| `html_static_path` | `["_static"]` | 静态文件目录 |
| `html_css_files` | `["button_styling.css"]` | 额外 CSS 文件 |
| `html_js_files` | `["pypi.js"]` | 额外 JS 文件 |

## sys.path 配置

```python
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("disabled_examples"))
```

这两行确保 Sphinx 可以导入当前目录的 `example.py` 和 `disabled_examples/` 目录下的 `disabled_example.py`，供 `automodule` 指令使用。

## PyData 主题选项（html_theme_options）

| 配置键 | demo 取值 | 说明 |
|--------|-----------|------|
| `icon_links` | GitHub + PyPI 两个图标链接 | 导航栏图标链接 |
| `switcher.json_url` | 根目录 switcher.json | 版本切换器 JSON 路径 |
| `switcher.version_match` | `"pyodide"` / `"xeus"` | 当前站点匹配的版本标识 |
| `navbar_end` | `["theme-switcher", "version-switcher", "navbar-icon-links"]` | 导航栏右侧组件 |
| `navbar_persistent` | `["search-button"]` | 常驻导航栏组件 |
| `use_edit_page_button` | `True` | 启用"编辑此页"按钮 |
| `secondary_sidebar_items` | 全局显示 page-toc/sourcelink/edit-this-page，首页仅 page-toc | 右侧边栏组件 |

## html_context（GitHub 编辑链接）

| 配置键 | 取值 | 说明 |
|--------|------|------|
| `github_url` | `"https://github.com"` | GitHub 基础 URL |
| `github_user` | `"jupyterlite"` | GitHub 用户名 |
| `github_repo` | `"sphinx-demo"` | 仓库名 |
| `github_version` | `"main"` | 分支名 |
| `doc_path` | `"pyodide-kernel-example/docs/source/"` / `"xeus-kernel-example/docs/source/"` | 文档源路径 |

## 相关概念

- [00-introduction](/concepts/00-introduction.md)
- [03-sphinx-conf](/concepts/03-sphinx-conf.md)
- [02-quick-start](/concepts/02-quick-start.md)
- [/references/json-config-source.md](/references/json-config-source.md)
