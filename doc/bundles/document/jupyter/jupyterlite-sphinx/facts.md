---
type: Facts
okf_version: "0.2"
title: "jupyterlite-sphinx 源码事实清单"
generated: "2026-08-22"
tags: [jupyter,jupyterlite,sphinx,documentation]
sources:
  - ../../../../../external/libs/jupyter/jupyterlite-sphinx/pyproject.toml
  - ../../../../../external/libs/jupyter/jupyterlite-sphinx/jupyterlite_sphinx/__init__.py
  - ../../../../../external/libs/jupyter/jupyterlite-sphinx/jupyterlite_sphinx/jupyterlite_sphinx.py
  - ../../../../../external/libs/jupyter/jupyterlite-sphinx/jupyterlite_sphinx/_try_examples.py
---

# jupyterlite-sphinx 源码事实清单

## 项目元数据

- F-001: pyproject.toml:6 — 项目名为 `jupyterlite-sphinx`，版本通过 `tool.hatch.version` 动态从 `__init__.py` 读取
- F-002: pyproject.toml:8 — 描述为 "Sphinx extension for deploying JupyterLite"
- F-003: pyproject.toml:11 — requires-python 为 `>=3.10`
- F-004: pyproject.toml:15-22 — 核心依赖：docutils、jupyter_server、jupyterlab_server、jupyterlite-core >=0.2,<0.9、nbformat、sphinx>=4
- F-005: pyproject.toml:25 — markdown 可选依赖包含 jupytext（用于 Markdown 格式 notebook 支持）
- F-006: pyproject.toml:2 — 构建系统使用 hatchling
- F-007: __init__.py:3 — __version__ = "0.23.0"
- F-008: __init__.py:1 — 模块仅导出 setup 函数（Sphinx 扩展入口）

## 核心常量

- F-009: jupyterlite_sphinx.py:40 — CONTENT_DIR = "_contents"（文档构建时的 notebook 暂存目录）
- F-010: jupyterlite_sphinx.py:41 — JUPYTERLITE_DIR = "lite"（JupyterLite 构建输出目录名）

## Sphinx 指令（Directives）

- F-011: jupyterlite_sphinx.py:428-571 — RepliteDirective：`.. replite::` 指令，在文档中嵌入 REPL 控制台，has_content=True，支持 width、height、kernel、execute、clear_cells_on_execute、clear_code_content_on_execute、hide_code_input、prompt_cell_position、show_banner、toolbar、theme、prompt、prompt_color、search_params、new_tab、new_tab_button_text、showbanner 等选项
- F-012: jupyterlite_sphinx.py:769-776 — JupyterLiteDirective：`.. jupyterlite::` 指令，嵌入 JupyterLab 界面（iframe_cls=JupyterLiteIframe, newtab_cls=JupyterLiteTab），接受一个 notebook 路径参数
- F-013: jupyterlite_sphinx.py:779-786 — NotebookLiteDirective：`.. notebooklite::` 指令，嵌入 NotebookLite 界面（iframe_cls=NotebookLiteIframe, newtab_cls=NotebookLiteTab），接受 notebook 路径参数
- F-014: jupyterlite_sphinx.py:789-804 — VoiciDirective：`.. voici::` 指令，嵌入 Voici 仪表板界面，run() 中检查 voici 是否已安装，未安装则抛出 RuntimeError
- F-015: jupyterlite_sphinx.py:824-984 — TryExamplesDirective：`.. try_examples::` 指令，将 doctest 示例转换为可交互 notebook，支持 height、theme、button_text、example_class、warning_text 选项
- F-016: jupyterlite_sphinx.py:1277 — `retrolite` 指令作为 `notebooklite` 的别名注册（向后兼容）
- F-017: jupyterlite_sphinx.py:574-746 — _LiteDirective 基类实现通用逻辑：notebook 路径解析、_contents 目录管理、Markdown notebook 通过 jupytext 转换为 ipynb、strip_tagged_cells 功能（移除含 `jupyterlite_sphinx_strip` tag 的单元格）、new_tab 模式支持
- F-018: jupyterlite_sphinx.py:597-620 — _strip_notebook_cells 方法过滤掉 metadata.tags 中包含 `jupyterlite_sphinx_strip` 的单元格
- F-019: jupyterlite_sphinx.py:667-684 — Markdown notebook 处理：使用 jupytext.read() 读取 .md 文件，转换为 .ipynb 写入 _contents 目录，通过 mtime 比较判断是否需要重新转换
- F-020: jupyterlite_sphinx.py:467-527 — RepliteDirective 的 REPL 选项映射：将 snake_case 选项转换为 camelCase URL 参数（如 clear_cells_on_execute → clearCellsOnExecute），布尔值转换为 "0"/"1"
- F-021: jupyterlite_sphinx.py:521-526 — prompt_cell_position 验证：必须是 top/bottom/left/right 之一
- F-022: jupyterlite_sphinx.py:533-536 — prefix 路径计算：使用 os.path.relpath 计算当前文档到 lite 目录的相对路径，确保多目录文档中 URL 正确

## HTML 节点（Iframe/Tab 元素）

- F-023: jupyterlite_sphinx.py:71-132 — _PromptedIframe：支持 prompt 模式的 iframe 节点，prompt=True 时渲染为带"Try It Live!"按钮的 div（默认背景色 #f7dc1e），点击后通过 window.jupyterliteShowIframe() JS 函数加载 iframe
- F-024: jupyterlite_sphinx.py:134-168 — _InTab：新标签页按钮节点，渲染为 `<button onclick="window.open(...)">` 按钮
- F-025: jupyterlite_sphinx.py:171-205 — _LiteIframe：继承 _PromptedIframe，根据 content（行内代码）或 notebook 参数构建 iframe_src URL，content 通过 `code=` URL 参数传递
- F-026: jupyterlite_sphinx.py:208-215 — RepliteIframe：lite_app = "repl/"，notebooks_path = ""（REPL 模式）
- F-027: jupyterlite_sphinx.py:218-225 — JupyterLiteIframe：lite_app = "lab/"，notebooks_path = ""（JupyterLab 模式）
- F-028: jupyterlite_sphinx.py:338-345 — NotebookLiteIframe：lite_app = "tree/"，notebooks_path = "../notebooks/"（文件树模式）
- F-029: jupyterlite_sphinx.py:260-335 — RepliteTab：不继承 _InTab，独立实现 URL 构建，处理 execute、clearCellsOnExecute、clearCodeContentOnExecute、hideCodeInput、showBanner、promptCellPosition 等 REPL 特有参数
- F-030: jupyterlite_sphinx.py:348-386 — VoiciIframe/VoiciBase：Voici 使用不同 URL 结构，notebook 路径为 `voici/render/{name}.html`，默认 tree 视图为 `voici/tree`
- F-031: jupyterlite_sphinx.py:55-68 — _build_options 函数将选项 dict 转换为 URL 查询参数，包含 "showbanner" → "showBanner" 的大小写修正映射

## NotebookLite 解析器

- F-032: jupyterlite_sphinx.py:807-821 — NotebookLiteParser：自定义 RSTParser，supported = ("jupyterlite_notebook",)，parse 方法将 .ipynb 文件自动转换为 `.. notebooklite::` 指令渲染
- F-033: jupyterlite_sphinx.py:1022-1027 — 当 jupyterlite_bind_ipynb_suffix 为 True（默认）且 .ipynb 不在 source_suffix 中时，自动注册 .ipynb 后缀使用 NotebookLiteParser

## JupyterLite 构建集成

- F-034: jupyterlite_sphinx.py:1046-1210 — jupyterlite_build 函数连接到 Sphinx 的 build-finished 事件，在 HTML 构建完成后执行 `jupyter lite build` 命令
- F-035: jupyterlite_sphinx.py:1128-1131 — 默认构建 apps：notebooks、edit、lab、repl、tree、consoles；如果 voici 已安装则额外构建 voici app
- F-036: jupyterlite_sphinx.py:1089-1121 — contents 处理：展开 glob 模式，目录复制到 _contents 暂存区保留目录名，单个文件通过 --contents 参数传递
- F-037: jupyterlite_sphinx.py:1133-1151 — 构建命令固定包含 --debug、--contents（_contents 目录）、--output-dir（<outdir>/lite）、--lite-dir 参数
- F-038: jupyterlite_sphinx.py:1153-1167 — jupyterlite_build_command_options 允许追加额外构建选项，但禁止覆盖 contents/output-dir/lite-dir 三个关键选项
- F-039: jupyterlite_sphinx.py:1174-1176 — jupyterlite_silence 配置（默认 True）将构建输出重定向到 PIPE，失败时再打印 stdout/stderr
- F-040: jupyterlite_sphinx.py:1013-1020 — inited 函数连接到 config-inited 事件，清空并重建 _contents 目录
- F-041: jupyterlite_sphinx.py:1207-1210 — 构建完成后清理 .jupyterlite.doit.db 文件

## Try Examples 功能

- F-042: _try_examples.py:7-124 — examples_to_notebook 函数解析 doctest 风格的 Examples 块，将 `>>>` 代码行和输出转换为 notebook 单元格，支持多行代码（`...` 前缀）、输出行捕获、markdown 文本、LaTeX 转换
- F-043: _try_examples.py:63 — 忽略 `.. plot::` 和 `.. only::` 指令下的内容
- F-044: _try_examples.py:186-225 — _process_latex 将 `:math:\`...\`` 转换为 `$...$`，`.. math::` 块转换为 `$$ ... $$`
- F-045: _try_examples.py:228-269 — _process_literal_blocks 将 RST `::` 字面量块转换为 Markdown 代码围栏（```）
- F-046: _try_examples.py:155-171 — _convert_links 将 Sphinx 风格链接（`text <url>`_）转换为 Markdown 链接（text）
- F-047: _try_examples.py:174-183 — _strip_ref_identifiers 移除 Sphinx 交叉引用标识符（[R4c2dbc17006a-1]_ → [1]_）
- F-048: _try_examples.py:334-416 — insert_try_examples_directive 在 autodoc 处理后的 docstring 中自动插入 `.. try_examples::` 指令，支持 `.. disable_try_examples` 注释禁用，识别 numpydoc 和 sphinx.ext.napoleon 两种格式的 Examples 节
- F-049: jupyterlite_sphinx.py:987-1010 — 当 global_enable_try_examples 为 True 时，自动连接 source-read（.py 文件）和 autodoc-process-docstring 事件处理
- F-050: jupyterlite_sphinx.py:974-981 — Try Examples 运行时支持 try_examples.json 配置文件，通过 DOMContentLoaded 事件加载

## 配置选项

- F-051: jupyterlite_sphinx.py:1222-1264 — setup() 注册了大量 Sphinx 配置值：jupyterlite_config、jupyterlite_overrides、jupyterlite_dir、jupyterlite_contents、jupyterlite_ignore_contents、jupyterlite_bind_ipynb_suffix（默认 True）、jupyterlite_silence（默认 True）、strip_tagged_cells（默认 False）、jupyterlite_build_command_options、jupyterlite_content_dir（默认 "_contents"）
- F-052: jupyterlite_sphinx.py:1234-1242 — Try Examples 配置：global_enable_try_examples（默认 False）、try_examples_global_theme、try_examples_global_warning_text、try_examples_global_button_text、try_examples_preamble
- F-053: jupyterlite_sphinx.py:1247-1256 — new_tab 按钮文本配置：jupyterlite_new_tab_button_text（默认 "Open as a notebook"）、notebooklite_new_tab_button_text、voici_new_tab_button_text（默认 "Open with Voici"）、replite_new_tab_button_text（默认 "Open in a REPL"）
- F-054: jupyterlite_sphinx.py:1259-1264 — REPL 全局配置：replite_auto_execute（默认 True）、replite_clear_cells_on_execute（默认 False）、replite_clear_code_content_on_execute（默认 False）、replite_hide_code_input（默认 False）、replite_prompt_cell_position（默认 "bottom"）、replite_show_banner（默认 True）

## 静态资源

- F-055: jupyterlite_sphinx.py:1340-1346 — setup() 复制 jupyterlite_sphinx.css 和 jupyterlite_sphinx.js 到 _static 目录，并添加 CSS/JS 文件引用
- F-056: jupyterlite_sphinx.py:1343 — 加载 Google Fonts 的 Vibur 字体
- F-057: jupyterlite_sphinx.py:1349-1351 — 如果存在 try_examples.json 则复制到输出目录
- F-058: jupyterlite_sphinx.py:1353 — 返回 parallel_read_safe: True，支持 Sphinx 并行读取

## 搜索参数处理

- F-059: jupyterlite_sphinx.py:1356-1368 — search_params_parser 验证 search_params 选项：接受 True/False 或 `["param1", "param2"]` 数组格式，参数名不能包含特殊字符
