---
type: Concept
title: 快速开始
description: 从零开始安装和配置 sphinx-copybutton 的最小化步骤，5分钟内启用代码块复制功能
tags: [sphinx, sphinx-extension, copybutton, getting-started, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# 快速开始

本文档介绍如何在 5 分钟内为你的 Sphinx 文档启用代码块复制按钮功能。

## 安装

使用 pip 安装：

```bash
pip install sphinx-copybutton
```

或使用 conda（通过 conda-forge）：

```bash
conda install -c conda-forge sphinx-copybutton
```

## 启用扩展

在 Sphinx 项目的 `conf.py` 中，将 `sphinx_copybutton` 添加到 `extensions` 列表：

```python
# conf.py
extensions = [
    # ... 其他扩展
    'sphinx_copybutton',
]
```

这就是最小配置！构建文档后，所有代码块右上角都会出现一个复制按钮，鼠标悬停时显示。

## 验证安装

构建文档并检查效果：

```bash
sphinx-build -b html docs docs/_build/html
```

打开生成的 HTML 页面，将鼠标悬停在任意代码块上，右上角应出现一个小的复制图标。点击按钮后：

1. 图标短暂变为绿色对勾
2. 按钮 tooltip 显示"复制成功!"（或对应语言的翻译）
3. 代码内容已复制到剪贴板
4. 2 秒后按钮恢复原状

## 构建第一个文档

如果你还没有 Sphinx 项目，可以快速创建一个：

```bash
# 安装 Sphinx（如未安装）
pip install sphinx

# 创建项目目录
mkdir my-docs && cd my-docs

# 快速启动 Sphinx 项目
sphinx-quickstart --sep -p "My Docs" -a "Your Name" -v "0.1" -l zh_CN

# 编辑 source/conf.py 添加扩展
# extensions = ['sphinx_copybutton']

# 构建
sphinx-build -b html source build
```

在 `source/index.rst` 中添加一个代码块示例：

```rst
Welcome to My Docs
==================

这是一个代码块示例：

.. code-block:: python

   print("Hello, sphinx-copybutton!")

.. code-block:: bash

   $ echo "复制我试试"
   $ pip install sphinx-copybutton
```

## 下一步

最小配置已可使用，但 sphinx-copybutton 的真正价值在于**智能提示符剥离**——当你的代码块包含 shell 提示符（`$`）或 Python REPL 提示符（`>>>`）时，需要额外配置才能让复制的内容可以直接粘贴运行。详见：

- [文本处理与提示符剥离](/concepts/03-text-processing.md)——配置提示符剥离、行续接等高级文本处理
- [Shell 提示符配置示例](/examples/shell-prompts.md)——Bash、Python、IPython 等场景的完整配置

## 常见问题

**Q: 按钮不显示？**

A: 检查以下事项：
1. 确认 `sphinx_copybutton` 已添加到 `extensions` 列表
2. 确认构建时没有报错（运行 `sphinx-build` 时观察输出）
3. 检查浏览器控制台是否有 JavaScript 错误
4. 确认代码块被渲染在 `div.highlight pre` 选择器下（这是 Sphinx 默认结构）

**Q: 按钮位置不对或样式异常？**

A: 可能是主题与 copybutton 的 CSS 冲突。参考[自定义样式与图标](/concepts/04-customization.md)调整样式。

**Q: 复制的内容包含行号？**

A: 确保代码块没有启用行号（`linenos` 选项），或通过 `copybutton_exclude` 配置排除行号元素。详见[文本处理](/concepts/03-text-processing.md)。

## 相关概念

- [sphinx-copybutton 简介](/concepts/00-introduction.md)
- [扩展架构与注册机制](/concepts/02-extension-architecture.md)
- [文本处理与提示符剥离](/concepts/03-text-processing.md)
- [基础配置示例](/examples/basic-setup.md)
