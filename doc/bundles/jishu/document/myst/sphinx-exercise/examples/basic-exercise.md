---
type: Example
title: 基础练习与解答
description: 创建练习块、关联解答、交叉引用、无编号练习等基础用法示例
tags: [sphinx, exercise, example, basic, cross-reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 基础练习与解答

## 简单练习

```rst
.. exercise::

   Python 中如何定义一个函数？请写出基本语法。
```

## 带副标题的练习

```rst
.. exercise:: 列表推导式

   使用列表推导式生成 1 到 10 的平方数列表。
```

## 练习与解答配对

```rst
.. exercise:: 斐波那契数列
   :label: ex-fib

   编写函数计算第 n 个斐波那契数。

.. solution:: ex-fib

   .. code-block:: python

      def fibonacci(n):
          if n <= 1:
              return n
          a, b = 0, 1
          for _ in range(2, n + 1):
              a, b = b, a + b
          return b
```

## 无编号练习

```rst
.. exercise:: 思考题
   :nonumber:

   为什么 Python 中列表是可变的而元组是不可变的？
   这种设计有什么优势？
```

## 交叉引用

```rst
.. exercise:: 阶乘函数
   :label: ex-factorial

   编写递归函数计算 n!。

如 :numref:`ex-factorial` 所示，递归是一种简洁的实现方式。
参考答案见 :ref:`解答 <sol-factorial>`。

.. solution:: ex-factorial
   :label: sol-factorial

   .. code-block:: python

      def factorial(n):
          return 1 if n <= 1 else n * factorial(n - 1)
```

## 多个练习连续排列

```rst
.. exercise:: 变量交换
   :label: ex-swap

   不使用临时变量交换两个变量的值。

.. solution:: ex-swap

   .. code-block:: python

      a, b = b, a

.. exercise:: 字符串反转
   :label: ex-reverse

   如何反转一个字符串？

.. solution:: ex-reverse

   .. code-block:: python

      s = s[::-1]
```

编号自动递增：Exercise 1、Exercise 2、Exercise 3...

## 相关示例

- [教师版/学生版配置](hide-solutions.md)
- [门控练习包裹内容](gated-exercises.md)

## 相关概念

- [练习指令详解](../concepts/02-exercise-directive.md)
- [解答指令详解](../concepts/03-solution-directive.md)
