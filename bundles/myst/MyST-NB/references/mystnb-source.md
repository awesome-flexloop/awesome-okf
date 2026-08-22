---
type: Reference
title: MyST-NB 源码路径映射
description: MyST-NB 核心源文件路径、关键类/函数/配置项索引，供概念文档和示例溯源
tags: [myst-nb, source, mapping, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    path: d:/spaces/SpecWeave/external/libs/ai/executablebooks/MyST-NB/
---

# MyST-NB 源码路径映射

## 项目信息

| 项目 | 值 |
|------|-----|
| 版本 | 1.5.0.dev |
| 许可证 | BSD-3-Clause |
| Python 要求 | >= 3.10 |
| 核心依赖 | myst-parser>=1.0.0, nbclient, nbformat>=5.0, jupyter-cache>=0.5, ipython, sphinx>=5, ipykernel |
| 构建后端 | flit_core >=3.11,<4 |

## 核心模块路径

### 包入口

| 文件 | 关键导出 |
|------|---------|
| `myst_nb/__init__.py` | `__version__`, `setup(app)`, `glue(name, variable, display)` |

### 核心管线（core/）

| 文件 | 关键类/函数 | 说明 |
|------|------------|------|
| `core/config.py` | `NbParserConfig`, `Section`, `custom_formats_converter()`, `ipywidgets_js_factory()` | 配置数据类（30+字段） |
| `core/read.py` | `NbReader`, `create_nb_reader()`, `standard_nb_read()`, `read_myst_markdown_notebook()`, `is_myst_markdown_notebook()`, `UnexpectedCellDirective` | Notebook 读取层 |
| `core/execute/__init__.py` | `create_client()`, `NotebookClientBase`, `ExecutionResult`, `ExecutionError` | 执行客户端工厂 |
| `core/execute/base.py` | `NotebookClientBase`, `EvalNameError` | 执行客户端基类 |
| `core/execute/direct.py` | `NotebookClientDirect` | 直接执行（nbclient） |
| `core/execute/cache.py` | `NotebookClientCache` | 缓存执行（jupyter-cache） |
| `core/execute/inline.py` | `NotebookClientInline` | 内联执行（eval 用） |
| `core/render.py` | `NbElementRenderer`, `MditRenderMixin`, `MimeData`, `load_renderer()`, `get_mime_priority()`, `ExampleMimeRenderPlugin`, `WIDGET_STATE_MIMETYPE`, `WIDGET_VIEW_MIMETYPE` | 渲染层 |
| `core/nb_to_tokens.py` | `notebook_to_tokens()`, `nb_node_to_dict()` | Notebook→Token 转换 |
| `core/loggers.py` | `SphinxDocLogger`, `DocutilsDocLogger`, `DEFAULT_LOG_TYPE` | 日志系统 |
| `core/lexers.py` | `AnsiColorLexer`, `IPythonTracebackLexer` | Pygments 自定义 Lexer |
| `core/variables.py` | `VariableOutput`, `RetrievalError`, `render_variable_outputs()` | 变量输出渲染 |
| `core/utils.py` | `coalesce_streams()` | 工具函数 |

### Sphinx 集成

| 文件 | 关键类/函数 | 说明 |
|------|------------|------|
| `sphinx_ext.py` | `sphinx_setup()`, `create_mystnb_config()`, `add_css()`, `OUTPUT_FOLDER = "jupyter_execute"` | Sphinx 扩展注册主入口 |
| `sphinx_.py` | `Parser`, `SphinxRenderer`, `SphinxEnvType`, `NbMetadataCollector`, `SelectMimeType`, `HideInputCells`, `HideCodeCellNode` | Sphinx 解析器与 Post-Transform |

### Docutils 独立模式

| 文件 | 关键类/函数 | 说明 |
|------|------------|------|
| `docutils_.py` | `Parser`, `DocutilsApp`, `DocutilsNbRenderer`, `cli_html/html5/latex/xml/pseudoxml`, `get_nb_roles_directives()` | Docutils 独立模式解析器与 CLI |

### 扩展模块（ext/）

| 文件 | 关键类/函数 | 说明 |
|------|------------|------|
| `ext/glue/__init__.py` | `glue()`, `extract_glue_data()`, `GLUE_PREFIX`, `load_glue_sphinx()`, `load_glue_docutils()` | Glue 核心 |
| `ext/glue/domain.py` | `NbGlueDomain` | Glue Sphinx Domain |
| `ext/glue/directives.py` | `PasteAnyDirective`, `PasteFigureDirective`, `PasteMarkdownDirective`, `PasteMathDirective` | Glue 指令 |
| `ext/glue/roles.py` | `PasteRoleAny`, `PasteTextRole`, `PasteMarkdownRole` | Glue 角色 |
| `ext/glue/crossref.py` | `ReplacePendingGlueReferences` | Glue 交叉引用 Post-Transform |
| `ext/eval/__init__.py` | `EvalRoleAny`, `retrieve_eval_data()`, `load_eval_sphinx()`, `load_eval_docutils()` | Eval 变量求值 |
| `ext/download.py` | `NbDownloadRole` | nb-download 角色 |
| `ext/execution_tables.py` | `setup_exec_table_extension()` | 执行统计表 |
| `ext/utils.py` | `DirectiveBase`, `RoleBase` | 扩展基类 |

### CLI

| 文件 | 关键函数 | 说明 |
|------|---------|------|
| `cli.py` | `quickstart()`, `md_to_nb()`, `generate_conf_py()`, `generate_jupyter_notebook()`, `generate_text_notebook()`, `generate_index()` | CLI 工具 |

### 其他

| 文件 | 说明 |
|------|------|
| `warnings_.py` | `MystNBWarnings` 枚举（6种）、`create_warning()` |
| `_compat.py` | 兼容性工具 |
| `static/mystnb.css` | 默认 CSS 样式 |

## 入口点（Entry Points）

| 组 | 名称 | 目标 |
|----|------|------|
| `myst_nb.renderers` | default | `myst_nb.core.render:NbElementRenderer` |
| `myst_nb.mime_renderers` | example | `myst_nb.core.render:ExampleMimeRenderPlugin` |
| `pygments.lexers` | myst-ansi | `myst_nb.core.lexers:AnsiColorLexer` |
| `pygments.lexers` | ipythontb | `myst_nb.core.lexers:IPythonTracebackLexer` |
| `jcache.readers` | myst_nb_md | `myst_nb.core.read:myst_nb_reader_plugin` |

## CLI 命令

| 命令 | 入口函数 | 说明 |
|------|---------|------|
| `mystnb-quickstart` | `myst_nb.cli:quickstart` | 创建模板项目 |
| `mystnb-to-jupyter` | `myst_nb.cli:md_to_nb` | 文本 notebook → .ipynb |
| `mystnb-docutils-html` | `myst_nb.docutils_:cli_html` | Markdown → HTML |
| `mystnb-docutils-html5` | `myst_nb.docutils_:cli_html5` | Markdown → HTML5 |
| `mystnb-docutils-latex` | `myst_nb.docutils_:cli_latex` | Markdown → LaTeX |
| `mystnb-docutils-xml` | `myst_nb.docutils_:cli_xml` | Markdown → XML |
| `mystnb-docutils-pseudoxml` | `myst_nb.docutils_:cli_pseudoxml` | Markdown → Pseudo-XML |

## NbParserConfig 字段速查

### 文件读取

| 字段（Sphinx中加 `nb_` 前缀） | 类型 | 默认 | 说明 |
|------|------|------|------|
| `custom_formats` | Dict | {} | 自定义文件后缀→读取器 |

### 配置键名

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `metadata_key` | str | "mystnb" | Notebook 级元数据键 |
| `cell_metadata_key` | str | "mystnb" | Cell 级元数据键 |

### 执行配置

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `execution_mode` | "off"\|"auto"\|"force"\|"cache"\|"inline" | "auto" | 执行模式 |
| `execution_cache_path` | str | "" | 缓存路径 |
| `execution_timeout` | int | 30 | 超时秒数 |
| `execution_in_temp` | bool | False | 临时目录执行 |
| `execution_allow_errors` | bool | False | 允许执行错误 |
| `execution_raise_on_error` | bool | False | 失败抛异常 |
| `execution_show_tb` | bool | False | 显示 traceback |
| `execution_excludepatterns` | Sequence[str] | () | 排除模式 |
| `kernel_rgx_aliases` | Dict[str,str] | {} | Kernel 名称映射 |
| `eval_name_regex` | str | "^[a-zA-Z_]..." | eval 名称正则 |

### 渲染配置

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `render_plugin` | str | "default" | 渲染器入口点 |
| `merge_streams` | bool | False | 合并 stdout/stderr |
| `remove_code_source` | bool | False | 移除代码源码 |
| `remove_code_outputs` | bool | False | 移除代码输出 |
| `scroll_outputs` | bool | False | 输出滚动 |
| `number_source_lines` | bool | False | 代码行号 |
| `output_stderr` | str | "show" | stderr 处理方式 |
| `code_prompt_show` | str | "Show code cell {type}" | 展开提示 |
| `code_prompt_hide` | str | "Hide code cell {type}" | 折叠提示 |
| `render_text_lexer` | str | "myst-ansi" | 文本输出 lexer |
| `render_error_lexer` | str | "ipythontb" | 错误输出 lexer |
| `render_image_options` | Dict | {} | 图片选项 |
| `render_figure_options` | Dict | {} | Figure 选项 |
| `render_markdown_format` | "commonmark"\|"gfm"\|"myst" | "commonmark" | Markdown 渲染格式 |
| `mime_priority_overrides` | Sequence | () | MIME 优先级覆盖 |
| `ipywidgets_js` | Dict | factory | ipywidgets JS 配置 |

## MystNBWarnings 枚举

| 枚举值 | 值 | 说明 |
|--------|-----|------|
| `LEXER` | "lexer" | Lexer 解析问题 |
| `FIG_CAPTION` | "fig_caption" | 图标题问题 |
| `MIME_TYPE` | "mime_type" | MIME 类型问题 |
| `OUTPUT_TYPE` | "output_type" | 输出类型问题 |
| `CELL_METADATA_KEY` | "cell_metadata_key" | cell metadata 键问题 |
| `CELL_CONFIG` | "cell_config" | cell 配置问题 |
