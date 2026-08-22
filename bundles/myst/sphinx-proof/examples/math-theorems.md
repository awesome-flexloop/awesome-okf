---
type: Example
title: 数学定理排版
description: 使用 sphinx-proof 排版数学定理、引理、定义、证明的完整示例，包含交叉引用
tags: [sphinx, proof, example, math, theorem, proof-environment]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:22:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 数学定理排版

## 完整数学论述示例

以下示例展示一个典型的数学论述结构：公理→定义→引理→定理→证明→推论。

```rst
.. axiom:: 实数完备性
   :label: ax-completeness

   实数集:math:`\mathbb{R}`中任何有上界的非空子集必有上确界。

.. definition:: 数列极限
   :label: def-seq-limit

   设:math:`\{a_n\}` 为实数数列，:math:`A \in \mathbb{R}`。
   若对任意:math:`\varepsilon > 0`，存在正整数:math:`N`，
   当:math:`n > N` 时有:math:`|a_n - A| < \varepsilon`，
   则称:math:`A` 为数列:math:`\{a_n\}` 的极限。

.. lemma:: 有界性
   :label: lem-bounded

   收敛数列必有界。

.. proof::

   设:math:`\lim_{n\to\infty} a_n = A`。
   取:math:`\varepsilon = 1`，存在:math:`N`，当:math:`n > N` 时
   :math:`|a_n - A| < 1`，即:math:`|a_n| < |A| + 1`。
   令:math:`M = \max\{|a_1|, \ldots, |a_N|, |A| + 1\}`，
   则对所有:math:`n`，:math:`|a_n| \leq M`。

.. theorem:: 单调有界定理
   :label: th-monotone

   单调有界数列必收敛。具体地：

   - 单调递增且有上界的数列收敛于其上确界；
   - 单调递减且有下界的数列收敛于其下确界。

.. proof::

   设:math:`\{a_n\}` 单调递增且有上界。
   由:numref:`ax-completeness`，上确界:math:`A = \sup\{a_n\}` 存在。
   对任意:math:`\varepsilon > 0`，:math:`A - \varepsilon` 不是上界，
   故存在:math:`N` 使得:math:`a_N > A - \varepsilon`。
   由单调性，当:math:`n > N` 时:math:`a_n \geq a_N > A - \varepsilon`。
   又:math:`a_n \leq A < A + \varepsilon`，故:math:`|a_n - A| < \varepsilon`。
   由:numref:`def-seq-limit`，:math:`\lim a_n = A`。

.. corollary::
   :label: cor-bolzano

   任何有界数列必有收敛子列（Bolzano-Weierstrass定理）。
```

## 算法描述

```rst
.. algorithm:: 二分查找
   :label: algo-binary

   **输入**：有序数组:math:`a[0..n-1]`，目标值:math:`x`

   **输出**：目标值位置或 -1

   1. 设:math:`low = 0`，:math:`high = n - 1`
   2. 当:math:`low \leq high` 时：

      a. 令:math:`mid = \lfloor(low + high) / 2\rfloor`
      b. 若:math:`a[mid] = x`，返回:math:`mid`
      c. 若:math:`a[mid] < x`，令:math:`low = mid + 1`
      d. 若:math:`a[mid] > x`，令:math:`high = mid - 1`

   3. 返回 -1
```

## 备注与示例

```rst
.. remark::

   注意定理:numref:`th-monotone`的逆命题不成立：收敛数列不一定单调。
   例如:math:`a_n = (-1)^n / n` 收敛于0但不单调。

.. example::

   数列:math:`a_n = 1 - 1/n` 单调递增且有上界1，
   由定理:numref:`th-monotone`，其极限为1。
```

## 无编号定理

```rst
.. theorem::
   :nonumber:

   这是一个不需要编号的常识性定理。
```

## 相关示例

- [自定义编号与配置](/examples/custom-numbering.md)

## 相关概念

- [定理类型详解](/concepts/02-theorem-types.md)
- [证明指令](/concepts/03-proof-directive.md)
- [交叉引用与编号映射](/concepts/04-cross-references.md)
