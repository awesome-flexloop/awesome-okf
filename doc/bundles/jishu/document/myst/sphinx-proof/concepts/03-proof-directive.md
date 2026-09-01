---
type: Concept
title: 证明指令
description: proof 指令的用法、与定理的配合方式、admonition 节点实现、无编号设计
tags: [sphinx, proof, directive, admonition, proof-environment]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:16:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 证明指令

## 基本语法

```rst
.. proof::

   证明内容...
```

`.. proof::` 创建一个证明块，无编号、无 label、不参与交叉引用。

## 核心特点

### 无编号

与 15 种定理类型不同，`proof` 指令不使用 `add_enumerable_node()`，不分配编号。在数学写作惯例中，证明总是依附于它所证明的定理，不需要独立编号。

### 自动 "Proof." 前缀

proof 指令会自动在内容第一行添加"Proof. "前缀：

```rst
.. proof::

   由定义直接可得。
```

输出为："Proof. 由定义直接可得。"

实现方式：
```python
self.content[0] = "{}. ".format(realtyp.title()) + self.content[0]
```

即首行内容被修改为 `"Proof. " + 原始内容`。

### 使用标准 Admonition 节点

proof 指令使用 docutils 内置的 `nodes.admonition()` 创建节点，而非自定义节点类型。这意味着证明块会被渲染为标准的提示框样式，与 `.. note::`、`.. warning::` 等 admonition 指令外观一致。

### 选项

proof 指令仅支持 `:class:` 选项：

```rst
.. proof::
   :class: sketch

   这里给出证明概要...
```

无 `:label:`、`:nonumber:` 选项。

## 定理与证明的典型配合

### 紧邻模式（最常见）

证明直接跟在定理之后：

```rst
.. theorem:: AM-GM不等式
   :label: th-amgm

   对非负实数:math:`x,y`，有:math:`\frac{x+y}{2} \geq \sqrt{xy}`。

.. proof::

   令:math:`a = \sqrt{x}`，:math:`b = \sqrt{y}`。
   由:math:`(a-b)^2 \geq 0`，展开即可得证。
```

### 无编号证明（用于证明概要）

```rst
.. proof::
   :class: proof-sketch

   （证明概要）使用数学归纳法...
```

### 多个证明

一个定理可以有多个证明（不同方法）：

```rst
.. theorem::
   :label: th-main

   主要定理内容...

.. proof::

   证明方法一：构造法...

.. proof::

   证明方法二：反证法...
```

## 与 theorem 的设计差异

| 特性 | theorem 等15种类型 | proof |
|------|-------------------|-------|
| 编号 | ✅ 自动编号 | ❌ 无编号 |
| `:label:` | ✅ 支持 | ❌ 不支持 |
| `:nonumber:` | ✅ 支持 | ❌ 不需要 |
| 交叉引用 | ✅ 支持 | ❌ 不可引用 |
| 节点类型 | enumerable/unenumerable 自定义节点 | admonition 标准节点 |
| 标题 | 类型名+编号+可选标题 | "Proof." 前缀 |
| 计数器 | 各自独立 | 无 |

## 相关概念

- [定理类型详解](02-theorem-types.md)
- [交叉引用与编号映射](04-cross-references.md)
- [数学定理排版示例](../examples/math-theorems.md)
