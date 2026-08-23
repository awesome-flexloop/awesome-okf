---
type: Concept
title: 快速开始
description: 安装 sphinx-tabs 并创建第一个标签页组件，掌握 tabs/tab 指令的基本用法
tags: [sphinx, tabs, installation, setup, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:24:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 快速开始

## 安装

```bash
pip install sphinx-tabs
```

## 最小配置

在 `conf.py` 中添加扩展：

```python
extensions = [
    # ... 其他扩展
    'sphinx_tabs.tabs',
]
```

## 第一个标签页

使用 `.. tabs::` 作为容器，内部用 `.. tab::` 定义每个标签页：

```rst
.. tabs::

   .. tab:: 标签一

      这是第一个标签页的内容。

   .. tab:: 标签二

      这是第二个标签页的内容。

      支持任意 RST 内容：列表、代码块、图片等。
```

构建文档后会看到两个可切换的标签按钮，点击切换面板内容。

## 多语言代码示例（code-tab）

`.. code-tab::` 专为代码示例设计，第一个参数指定语言（lexer）：

```rst
.. tabs::

   .. code-tab:: python

      print("Hello, World!")

   .. code-tab:: javascript

      console.log("Hello, World!");

   .. code-tab:: r

      cat("Hello, World!\n")
```

每个 code-tab 自动获得语法高亮，标签名显示为语言全称（如 "Python" 而非 "python"）。

## 验证安装

构建文档后检查：

1. 标签按钮显示在内容上方
2. 点击标签切换面板内容
3. 键盘左右箭头可在标签间导航
4. 不使用标签页的页面不加载 tabs.css/tabs.js
5. code-tab 的代码有正确的语法高亮

## 相关概念

- [简介](/concepts/00-introduction.md)
- [四个指令详解](/concepts/02-directives.md)
- [基础标签页示例](/examples/basic-tabs.md)
