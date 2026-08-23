---
type: Reference
title: sphinx-copybutton 源码路径映射
description: sphinx-copybutton 核心源文件路径、职责与关键代码位置索引
tags: [sphinx, sphinx-extension, copybutton, source, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-repo
    resource: https://github.com/executablebooks/sphinx-copybutton
    title: sphinx-copybutton GitHub Repository
---

# sphinx-copybutton 源码路径映射

本文档为 sphinx-copybutton 源码的文件级索引，标注每个核心文件的路径、职责和关键代码行号。源路径相对于 `external/libs/ai/executablebooks/sphinx-copybutton/`。

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `sphinx_copybutton/__init__.py` | 99 行 | 扩展注册入口、配置项定义、事件钩子、静态资源管理 | `setup()` L68-99、`add_to_context()` L16-66、`scb_static_path()` L10-13 |
| `sphinx_copybutton/_static/copybutton.js_t` | 175 行 | Jinja2 模板化主脚本，DOM 操作、ClipboardJS 初始化、本地化、图标管理 | `addCopyButtonToCodeCells()` L126-173、`runWhenDOMLoaded()` L82-92、`copyTargetText()` L150-158 |
| `sphinx_copybutton/_static/copybutton_funcs.js` | 73 行 | 文本过滤与格式化纯函数（ES Module） | `filterText()` L12-19、`formatCopyText()` L23-73、`escapeRegExp()` L1-3 |
| `sphinx_copybutton/_static/copybutton.css` | 94 行 | 复制按钮样式、tooltip 样式、打印隐藏 | `.copybtn` L2-32、`.o-tooltip--left` L59-87、`@media print` L90-94 |

## 静态资源

| 路径 | 说明 |
|------|------|
| `sphinx_copybutton/_static/clipboard.min.js` | ClipboardJS 第三方库（通过 git submodule 引入，处理剪贴板 API 兼容性） |
| `sphinx_copybutton/_static/copy-button.svg` | 默认复制图标 |
| `sphinx_copybutton/_static/check-solid.svg` | 成功状态对勾图标 |

## 配置与构建文件

| 文件 | 说明 |
|------|------|
| `setup.py` | 包元数据、依赖声明、package_data 静态文件清单 |
| `setup.cfg` | 仅包含 license_file 配置 |
| `MANIFEST.in` | 打包文件清单 |
| `tox.ini` | 测试环境配置 |
| `.pre-commit-config.yaml` | 代码风格检查配置 |

## 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目简介、安装、使用说明 |
| `docs/conf.py` | 文档构建配置 |
| `docs/index.md` | 文档入口 |
| `docs/use.md` | 使用指南 |
| `docs/changelog.md` | 版本变更记录 |
| `docs/reference/example.md` | 配置示例 |
| `docs/reference/literal.py` | 自定义 literal 指令示例 |

## setup() 函数源码参考

```python
def setup(app):
    logger.verbose("Adding copy buttons to code blocks...")
    app.connect("builder-inited", scb_static_path)

    # 配置项注册
    app.add_config_value("copybutton_prompt_text", "", "html")
    app.add_config_value("copybutton_prompt_is_regexp", False, "html")
    app.add_config_value("copybutton_only_copy_prompt_lines", True, "html")
    app.add_config_value("copybutton_remove_prompts", True, "html")
    app.add_config_value("copybutton_copy_empty_lines", True, "html")
    app.add_config_value("copybutton_line_continuation_character", "", "html")
    app.add_config_value("copybutton_here_doc_delimiter", "", "html")
    app.add_config_value("copybutton_image_svg", "", "html")
    app.add_config_value("copybutton_selector", "div.highlight pre", "html")
    app.add_config_value("copybutton_exclude", ".linenos", "html")
    app.add_config_value("copybutton_image_path", "", "html")  # deprecated

    app.connect("config-inited", add_to_context)

    app.add_css_file("copybutton.css")
    app.add_js_file("clipboard.min.js")
    app.add_js_file("copybutton.js")
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

## 配置项速查表

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `copybutton_prompt_text` | str | `""` | 要剥离的提示符文本 |
| `copybutton_prompt_is_regexp` | bool | `False` | prompt_text 是否为正则表达式 |
| `copybutton_only_copy_prompt_lines` | bool | `True` | 是否只复制含提示符的行 |
| `copybutton_remove_prompts` | bool | `True` | 复制时是否移除提示符 |
| `copybutton_copy_empty_lines` | bool | `True` | 是否保留空行 |
| `copybutton_line_continuation_character` | str | `""` | 行续接字符（如 `\`） |
| `copybutton_here_doc_delimiter` | str | `""` | HERE 文档分隔符 |
| `copybutton_image_svg` | str | `""` | 自定义复制按钮 SVG |
| `copybutton_selector` | str | `"div.highlight pre"` | 目标代码块 CSS 选择器 |
| `copybutton_exclude` | str | `".linenos"` | 复制时排除的子元素选择器 |

## 相关概念

- [扩展架构与注册机制](/concepts/02-extension-architecture.md)
- [文本处理与提示符剥离](/concepts/03-text-processing.md)
- [自定义样式与图标](/concepts/04-customization.md)
