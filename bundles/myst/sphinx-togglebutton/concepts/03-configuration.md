---
type: Concept
title: 配置项参考
description: sphinx-togglebutton 的全部配置项详解：选择器、提示文本、打印行为及其在 conf.py 中的设置方法
tags: [sphinx, toggle, configuration, selector, i18n]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:08:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-source
    resource: /references/togglebutton-source.md
    title: sphinx-togglebutton 源码路径映射
---

# 配置项参考

sphinx-togglebutton 在 `conf.py` 中提供以下配置项，均在 `setup()` 中通过 `app.add_config_value()` 注册，重建类型为 `"html"`。

## togglebutton_selector

**类型**：`str`  
**默认值**：`".toggle, .admonition.dropdown"`

CSS 选择器，用于指定哪些页面元素将被添加折叠按钮。JS 端通过 `document.querySelectorAll(togglebuttonSelector)` 查找匹配元素。

```python
# conf.py
togglebutton_selector = ".toggle, .admonition.dropdown, .my-special-class"
```

可以自定义选择器为任意 CSS 选择器，实现对特定元素的自动折叠。例如，给所有 `.. warning::` 添加折叠：

```python
togglebutton_selector = ".toggle, .admonition.dropdown, .warning"
```

> **注意**：选择器由 JS 端执行，使用标准的 `querySelectorAll` 语法。

## togglebutton_hint

**类型**：`str`  
**默认值**：`"Click to show"`（根据 Sphinx 语言设置自动国际化）

折叠状态下按钮的提示文本（即点击可展开内容时的提示）。

```python
togglebutton_hint = "点击展开"
```

默认值通过 `sphinx.locale.get_translation()` 国际化，支持 30+ 种语言，会自动跟随 Sphinx 的 `language` 配置。

## togglebutton_hint_hide

**类型**：`str`  
**默认值**：`"Click to hide"`（自动国际化）

展开状态下按钮的提示文本（即点击可折叠内容时的提示）。

```python
togglebutton_hint_hide = "点击折叠"
```

## togglebutton_open_on_print

**类型**：`bool`  
**默认值**：`True`

控制打印（或导出 PDF）时是否自动展开所有折叠内容。

- `True`（默认）：`beforeprint` 事件触发时展开所有折叠内容，`afterprint` 时恢复原始状态
- `False`：打印时保持折叠状态不变

```python
togglebutton_open_on_print = False  # 打印时不自动展开
```

## 配置传递机制

配置值从 Python 到 JavaScript 的传递采用**构建时内联注入**模式：

1. `config-inited` 事件触发 `initialize_js_assets()`
2. 该函数通过 `app.add_js_file(None, body="let toggleHintShow = '...';")` 注入内联 `<script>` 标签
3. 内联脚本在 `togglebutton.js` 之前执行，定义全局变量
4. `togglebutton.js` 读取这些全局变量作为配置

这种模式的优势：
- JS 文件本身完全静态，可被 CDN 缓存
- 配置值在 HTML 中直接内联，零运行时请求开销
- 支持国际化翻译在构建时注入

## 相关概念

- [toggle 指令详解](/concepts/02-toggle-directive.md)
- [打印与国际化示例](/examples/print-and-i18n.md)
