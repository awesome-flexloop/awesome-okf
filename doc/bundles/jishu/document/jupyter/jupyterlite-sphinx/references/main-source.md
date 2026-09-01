---
type: Reference
title: 核心模块 jupyterlite_sphinx.py 源码索引
description: jupyterlite-sphinx 主模块的源码文件索引，包含所有公共类、函数和配置项的源码位置
tags: [source, core, sphinx-extension]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source-py
    resource: /references/main-source.md
    title: jupyterlite_sphinx.py source
---

## 源码文件位置

- **主模块**：`jupyterlite_sphinx/jupyterlite_sphinx.py`
- **版本**：0.23.0
- **构建系统**：hatchling
- **Python 要求**：>=3.10

## 模块级常量

| 常量 | 值 | 行号 |
|------|----|------|
| `HERE` | `Path(__file__).parent` | 38 |
| `CONTENT_DIR` | `"_contents"` | 40 |
| `JUPYTERLITE_DIR` | `"lite"` | 41 |

## 工具函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `skip(self, node)` | 45-46 | 非HTML格式节点跳过访问器 |
| `visit_element_html(self, node)` | 50-52 | HTML格式节点访问器 |
| `_build_options(lite_options)` | 55-68 | 将选项字典转为URL查询参数 |
| `search_params_parser(search_params)` | 1356-1368 | 解析search_params指令选项 |

## 自定义节点类

| 类名 | 继承自 | 行号 | lite_app | notebooks_path |
|------|--------|------|----------|----------------|
| `_PromptedIframe` | `Element` | 71-131 | — | — |
| `_InTab` | `Element` | 134-168 | — | — |
| `_LiteIframe` | `_PromptedIframe` | 171-205 | 子类定义 | 子类定义 |
| `RepliteIframe` | `_LiteIframe` | 208-215 | `"repl/"` | `""` |
| `JupyterLiteIframe` | `_LiteIframe` | 218-225 | `"lab/"` | `""` |
| `BaseNotebookTab` | `_InTab` | 228-234 | `None` | `None` |
| `JupyterLiteTab` | `BaseNotebookTab` | 237-244 | `"lab/"` | `""` |
| `NotebookLiteTab` | `BaseNotebookTab` | 247-254 | `"tree/"` | `"../notebooks/"` |
| `RepliteTab` | `Element` | 260-335 | `"repl/"` | `""` |
| `NotebookLiteIframe` | `_LiteIframe` | 338-345 | `"tree/"` | `"../notebooks/"` |
| `VoiciBase` | `object` | 348-360 | `"voici/"` | — |
| `VoiciIframe` | `_PromptedIframe` | 363-385 | VoiciBase路径 | — |
| `VoiciTab` | `Element` | 390-425 | VoiciBase路径 | — |

## Sphinx 指令类

| 类名 | 继承自 | 行号 | 对应指令名 |
|------|--------|------|-----------|
| `RepliteDirective` | `SphinxDirective` | 428-571 | `replite` |
| `_LiteDirective` | `SphinxDirective` | 574-746 | 基类 |
| `BaseJupyterViewDirective` | `_LiteDirective` | 749-766 | 基类 |
| `JupyterLiteDirective` | `BaseJupyterViewDirective` | 769-776 | `jupyterlite` |
| `NotebookLiteDirective` | `BaseJupyterViewDirective` | 779-786 | `notebooklite`/`retrolite` |
| `VoiciDirective` | `BaseJupyterViewDirective` | 789-804 | `voici` |
| `NotebookLiteParser` | `RSTParser` | 807-821 | `.ipynb` 源解析 |
| `TryExamplesDirective` | `SphinxDirective` | 824-984 | `try_examples` |

## 事件处理函数

| 函数 | 行号 | 连接的事件 |
|------|------|-----------|
| `_process_docstring_examples(app, docname, source)` | 987-990 | `source-read` |
| `_process_autodoc_docstrings(app, what, name, obj, options, lines)` | 993-1004 | `autodoc-process-docstring` |
| `conditional_process_examples(app, config)` | 1007-1010 | `config-inited` |
| `inited(app, config)` | 1013-1027 | `config-inited` |
| `jupyterlite_build(app, error)` | 1046-1210 | `build-finished` |

## setup() 注册项

`setup(app)` 函数位于第 1213-1353 行，注册内容：

**配置值（add_config_value）：**

| 配置名 | 默认值 | 行号 |
|--------|--------|------|
| `jupyterlite_config` | `None` | 1222 |
| `jupyterlite_overrides` | `None` | 1223 |
| `jupyterlite_dir` | `str(app.srcdir)` | 1224 |
| `jupyterlite_contents` | `None` | 1225 |
| `jupyterlite_ignore_contents` | `None` | 1226 |
| `jupyterlite_bind_ipynb_suffix` | `True` | 1227 |
| `jupyterlite_silence` | `True` | 1228 |
| `strip_tagged_cells` | `False` | 1229 |
| `jupyterlite_build_command_options` | `None` | 1232 |
| `global_enable_try_examples` | `False` | 1234 |
| `try_examples_global_theme` | `None` | 1235 |
| `try_examples_global_warning_text` | `None` | 1236 |
| `try_examples_global_button_text` | `None` | 1237-1241 |
| `try_examples_preamble` | `None` | 1242 |
| `jupyterlite_content_dir` | `CONTENT_DIR` | 1243 |
| `jupyterlite_new_tab_button_text` | `"Open as a notebook"` | 1247-1249 |
| `notebooklite_new_tab_button_text` | `"Open as a notebook"` | 1250-1252 |
| `voici_new_tab_button_text` | `"Open with Voici"` | 1253 |
| `replite_new_tab_button_text` | `"Open in a REPL"` | 1254-1256 |
| `replite_auto_execute` | `True` | 1259 |
| `replite_clear_cells_on_execute` | `False` | 1260 |
| `replite_clear_code_content_on_execute` | `False` | 1261 |
| `replite_hide_code_input` | `False` | 1262 |
| `replite_prompt_cell_position` | `"bottom"` | 1263 |
| `replite_show_banner` | `True` | 1264 |

**注册的指令（add_directive）：** `notebooklite`, `retrolite`(别名), `jupyterlite`, `replite`, `voici`, `try_examples`

**注册的节点（add_node）：** NotebookLiteIframe, JupyterLiteIframe, NotebookLiteTab, JupyterLiteTab, RepliteIframe, RepliteTab, VoiciIframe, VoiciTab

**资源文件：** jupyterlite_sphinx.css, jupyterlite_sphinx.js, Google Fonts Vibur, try_examples.json（可选）

## 可选依赖

| 依赖 | 导入位置 | 用途 | 安装方式 |
|------|---------|------|---------|
| `jupytext` | 28-31 | Markdown notebook (.md) 转换 | `pip install jupyterlite-sphinx[markdown]` |
| `voici` | 33-36 | Voici dashboard 渲染 | `pip install voici` |

## 相关概念

- [节点类层次](../concepts/11-node-hierarchy.md)
- [构建流程详解](../concepts/10-build-process.md)
- [配置参考](../concepts/09-configuration.md)
- [_try_examples 模块源码](try-examples-source.md)
- [前端 JS 源码](js-source.md)
