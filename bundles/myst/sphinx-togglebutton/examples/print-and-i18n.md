---
type: Example
title: 打印与国际化配置
description: 配置 sphinx-togglebutton 的打印行为、自定义提示文本和多语言支持
tags: [sphinx, toggle, print, i18n, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:12:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-source
    resource: /references/togglebutton-source.md
    title: sphinx-togglebutton 源码路径映射
---

# 打印与国际化配置

## 打印行为控制

默认情况下，打印文档（Ctrl+P）或导出 PDF 时，所有折叠内容会自动展开，确保打印输出包含完整信息。打印结束后恢复用户的折叠状态。

### 关闭自动展开

```python
# conf.py
togglebutton_open_on_print = False
```

设置为 `False` 后，打印时折叠内容保持折叠状态，不会自动展开。

### 打印行为的实现机制

扩展通过监听两个浏览器事件实现打印状态管理：

1. **`beforeprint`**：遍历所有折叠元素，记录当前状态到 `dataset`，然后展开所有内容
2. **`afterprint`**：根据记录的状态恢复折叠

对 `<details>` 元素设置 `el.open = true/false`，对 admonition 元素程序化点击按钮。

## 自定义提示文本

### 中文提示文本

```python
# conf.py
togglebutton_hint = "点击显示内容"
togglebutton_hint_hide = "点击隐藏内容"
```

### 英文自定义文本

```python
# conf.py
togglebutton_hint = "Expand"
togglebutton_hint_hide = "Collapse"
```

## 国际化（i18n）

扩展内置 30+ 种语言的翻译，默认跟随 Sphinx 的 `language` 配置：

```python
# conf.py — 使用中文
language = 'zh_CN'
```

无需额外配置，按钮提示文本会自动使用对应语言的翻译。支持的语言包括：英语、简体中文、繁体中文、日语、韩语、德语、法语、西班牙语、俄语、葡萄牙语、阿拉伯语、印地语、孟加拉语等。

## 自定义选择器场景

### 为特定类添加折叠

```python
# conf.py
togglebutton_selector = ".toggle, .admonition.dropdown, .my-collapsible"
```

然后在 RST 中为任意容器添加该类：

```rst
.. container:: my-collapsible

    这段内容也会被自动折叠。
```

### 折叠所有 warning 提示框

```python
# conf.py
togglebutton_selector = ".toggle, .admonition.dropdown, .warning"
```

所有 `.. warning::` 提示框自动变为可折叠状态（默认隐藏）。

## 外部扩展集成

`togglebutton.js` 暴露了全局函数 `syncAllToggleHints()`，供其他扩展在动态修改折叠状态后同步按钮提示文本：

```javascript
// 其他扩展代码中
if (typeof syncAllToggleHints === 'function') {
    syncAllToggleHints();
}
```

此外，扩展使用 `MutationObserver` 监听所有 `.toggle` 元素的 class 属性变化，当其他代码添加/移除 `toggle-hidden` 类时，按钮提示文本会自动同步。

## 相关概念

- [配置项参考](/concepts/03-configuration.md)
- [基础使用示例](basic-usage.md)
