---
type: Concept
title: 快速开始
description: 安装 sphinx-togglebutton 并完成最小配置，实现提示框折叠和内容切换
tags: [sphinx, toggle, installation, setup, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:04:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-source
    resource: /references/togglebutton-source.md
    title: sphinx-togglebutton 源码路径映射
---

# 快速开始

## 安装

使用 pip 安装：

```bash
pip install sphinx-togglebutton
```

## 最小配置

在 Sphinx 项目的 `conf.py` 中添加扩展：

```python
extensions = [
    # ... 其他扩展
    'sphinx_togglebutton',
]
```

仅此两步，扩展即可生效，无需其他配置。

## 方式一：折叠提示框（admonition）

给任意 admonition 指令添加 `:class: dropdown` 选项即可使其可折叠（默认隐藏内容）：

```rst
.. note::
    :class: dropdown

    这是一个可折叠的提示框内容。点击标题栏可展开/折叠。
```

默认状态下提示框内容隐藏，点击 "Click to show" 按钮展开。

**默认展开**：同时添加 `toggle-shown` 类使内容默认可见：

```rst
.. warning::
    :class: dropdown, toggle-shown

    这个警告框默认展开，点击可折叠。
```

## 方式二：折叠任意内容（toggle 指令）

使用 `.. toggle::` 指令折叠任意内容块：

```rst
.. toggle::

    这段内容默认隐藏，点击展开查看。

    可以包含任意 RST 内容：

    - 列表项
    - **加粗文本**
    - 代码块等
```

**默认显示**：添加 `:show:` 标志使内容默认展开：

```rst
.. toggle::
    :show:

    这个内容块默认展开显示。
```

## 验证

构建文档后检查：

1. 添加了 `:class: dropdown` 的提示框标题栏出现折叠按钮（chevron 图标）
2. 使用 `.. toggle::` 指令的内容显示为可折叠区域
3. 点击按钮可切换展开/折叠状态
4. 打印预览时所有折叠内容自动展开

## 相关概念

- [简介](00-introduction.md)
- [toggle 指令详解](02-toggle-directive.md)
- [配置项参考](03-configuration.md)
- [基础使用示例](../examples/basic-usage.md)
