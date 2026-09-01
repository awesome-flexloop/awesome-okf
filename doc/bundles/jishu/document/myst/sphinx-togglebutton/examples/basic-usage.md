---
type: Example
title: 基础使用示例
description: sphinx-togglebutton 的常见使用场景：提示框折叠、答案隐藏、内容区域折叠的完整 RST 示例
tags: [sphinx, toggle, example, admonition, dropdown]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:10:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-source
    resource: /references/togglebutton-source.md
    title: sphinx-togglebutton 源码路径映射
---

# 基础使用示例

本文档提供 sphinx-togglebutton 在文档中的常见使用示例。

## 示例一：折叠提示框（默认隐藏）

```rst
.. note::
    :class: dropdown

    这是一条补充说明内容，默认折叠隐藏，读者点击标题栏即可展开查看。
    适合放置非核心但有用的额外信息。

.. tip::
    :class: dropdown

    💡 进阶技巧：使用快捷键 Ctrl+P 可以快速打开打印预览。

.. warning::
    :class: dropdown

    ⚠️ 注意：此操作不可逆，请确保已备份重要数据后再执行。
```

效果：三个提示框默认折叠，仅显示标题栏，点击展开内容。

## 示例二：折叠提示框（默认展开）

```rst
.. important::
    :class: dropdown, toggle-shown

    这个重要提示默认展开显示，读者可以手动折叠。
    适合放置首次阅读需要注意、但后续可以收起的信息。
```

## 示例三：习题答案折叠

```rst
**练习 1**：Python 中 `list` 和 `tuple` 的主要区别是什么？

.. toggle::

    **参考答案**：

    - **list**（列表）：可变序列，使用方括号 `[]` 创建，支持增删改操作
    - **tuple**（元组）：不可变序列，使用圆括号 `()` 创建，创建后不能修改

    元组因为不可变，可以作为字典的键使用，而列表不行。
```

## 示例四：折叠代码实现

```rst
使用 Python 实现快速排序算法：

.. toggle::

    .. code-block:: python

        def quicksort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x < pivot]
            middle = [x for x in arr if x == pivot]
            right = [x for x in arr if x > pivot]
            return quicksort(left) + middle + quicksort(right)

    时间复杂度：平均 O(n log n)，最坏 O(n²)
```

## 示例五：折叠多内容组合

```rst
.. toggle::
    :show:

    点击可折叠此区域（默认展开）。其中包含多种内容类型：

    1. **加粗文本** 和 *斜体文本*
    2. 行内代码：``print("hello")``
    3. 列表项

    .. code-block:: python

        # 嵌套代码块
        for i in range(10):
            print(i)

    .. note::

        折叠区域内也可以嵌套其他 admonition。
```

## 完整 conf.py 配置

```python
# conf.py
extensions = [
    'sphinx_togglebutton',
]

# 可选：自定义配置
togglebutton_hint = "点击展开内容"
togglebutton_hint_hide = "点击折叠内容"
togglebutton_open_on_print = True
```

## 相关概念

- [快速开始](../concepts/01-getting-started.md)
- [toggle 指令详解](../concepts/02-toggle-directive.md)
- [配置项参考](../concepts/03-configuration.md)
