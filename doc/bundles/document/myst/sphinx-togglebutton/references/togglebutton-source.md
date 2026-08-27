---
type: Reference
title: sphinx-togglebutton 源码路径映射
description: sphinx-togglebutton 核心源文件路径、职责与关键代码位置索引
tags: [sphinx, toggle, extension, source, executable-books]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-repo
    resource: https://github.com/executablebooks/sphinx-togglebutton
    title: sphinx-togglebutton GitHub Repository
---

# sphinx-togglebutton 源码路径映射

本文档为 sphinx-togglebutton 源码的文件级索引。源路径相对于 `external/libs/ai/executablebooks/sphinx-togglebutton/`。

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `sphinx_togglebutton/__init__.py` | 107 行 | 扩展入口、指令定义、配置注册、静态资源管理 | `setup()` L69-107、`Toggle` 类 L47-63、`initialize_js_assets()` L22-33 |
| `sphinx_togglebutton/_static/togglebutton.js` | 257 行 | 前端折叠交互逻辑 | `initToggleItems()` L11-112、`toggleHidden()` L115-129、打印处理 L225-257 |
| `sphinx_togglebutton/_static/togglebutton.css` | - | 折叠按钮样式 | `.toggle-button`、`.toggle-hidden`、`.toggle-details` 样式规则 |
| `setup.cfg` | 40 行 | 包元数据、依赖声明 | `[options]` L15-21、`[options.package_data]` L32-40 |

## 翻译资源

| 路径 | 说明 |
|------|------|
| `sphinx_togglebutton/translations/locales/` | 30+ 种语言的 gettext 翻译文件（.po/.mo） |
| `sphinx_togglebutton/translations/jsons/` | JSON 格式的翻译源文件（Hide.json、Show.json） |

## 关键配置参考

### setup() 函数

```python
def setup(app):
    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, "translations", "locales")
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)
    app.connect("builder-inited", st_static_path)
    app.add_css_file("togglebutton.css")
    app.add_config_value("togglebutton_selector", ".toggle, .admonition.dropdown", "html")
    app.add_config_value("togglebutton_hint", f"{translate('Click to show')}", "html")
    app.add_config_value("togglebutton_hint_hide", f"{translate('Click to hide')}", "html")
    app.add_config_value("togglebutton_open_on_print", True, "html")
    app.connect("builder-inited", insert_custom_selection_config)
    app.connect("config-inited", initialize_js_assets)
    app.add_directive("toggle", Toggle)
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}
```

### Toggle 指令

```python
class Toggle(Directive):
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {"id": directives.unchanged, "show": directives.flag}

    def run(self):
        self.assert_has_content()
        classes = ["toggle"]
        if "show" in self.options:
            classes.append("toggle-shown")
        parent = nodes.container(classes=classes)
        self.state.nested_parse(self.content, self.content_offset, parent)
        return [parent]
```

## 相关概念

- [简介](../concepts/00-introduction.md)
- [快速开始](../concepts/01-getting-started.md)
- [toggle 指令详解](../concepts/02-toggle-directive.md)
- [配置项参考](../concepts/03-configuration.md)
