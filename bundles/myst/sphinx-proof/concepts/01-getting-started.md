---
type: Concept
title: 快速开始
description: 安装 sphinx-proof，创建第一个定理和证明块，掌握基础用法
tags: [sphinx, proof, installation, getting-started, theorem]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:12:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 快速开始

## 安装

```bash
pip install sphinx-proof
```

## 最小配置

在 `conf.py` 中添加扩展：

```python
extensions = [
    # ... 其他扩展
    'sphinx_proof',
]
```

## 第一个定理

```rst
.. theorem::

   对于任意实数 :math:`x`, :math:`y`，如果 :math:`x > 0` 且 :math:`y > 0`，
   则 :math:`x + y > 0`。
```

输出显示为带编号的定理框："Theorem 1. 对于任意实数..."

## 带标题的定理

```rst
.. theorem:: 勾股定理
   :label: th-pythagoras

   在直角三角形中，设两直角边长为 :math:`a`、:math:`b`，斜边长为 :math:`c`，
   则 :math:`a^2 + b^2 = c^2`。
```

输出："Theorem 2 (勾股定理). 在直角三角形中..."

## 定理与证明配对

```rst
.. theorem:: 算术-几何均值不等式
   :label: th-amgm

   对任意非负实数 :math:`x, y`，有
   :math:`\frac{x + y}{2} \geq \sqrt{xy}`。

.. proof::

   令 :math:`a = \sqrt{x}`，:math:`b = \sqrt{y}`，
   则 :math:`(a - b)^2 \geq 0`，展开得
   :math:`a^2 + b^2 - 2ab \geq 0`，即
   :math:`\frac{x + y}{2} \geq \sqrt{xy}`。
   等号成立当且仅当 :math:`x = y`。
```

## 定义块

```rst
.. definition:: 极限
   :label: def-limit

   设函数 :math:`f(x)` 在点 :math:`x_0` 的某去心邻域内有定义。
   若存在常数 :math:`A`，使得对任意 :math:`\varepsilon > 0`，
   总存在 :math:`\delta > 0`，当 :math:`0 < |x - x_0| < \delta` 时，
   有 :math:`|f(x) - A| < \varepsilon`，
   则称 :math:`A` 为 :math:`f(x)` 当 :math:`x \to x_0` 时的极限。
```

输出："Definition 1 (极限). 设函数..."

## 引用定理

```rst
根据:numref:`th-amgm`，有...

详见:ref:`th-pythagoras`。
```

## 验证安装

构建文档后检查：

1. 定理显示为带编号的彩色框
2. 证明块显示"Proof."前缀
3. `:numref:` 正确显示编号
4. LaTeX 构建正常输出定理环境

## 相关概念

- [简介](/concepts/00-introduction.md)
- [定理类型详解](/concepts/02-theorem-types.md)
- [数学定理排版示例](/examples/math-theorems.md)
