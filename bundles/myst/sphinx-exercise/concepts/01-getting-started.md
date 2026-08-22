---
type: Concept
title: 快速开始
description: 安装 sphinx-exercise，配置 conf.py，创建第一个练习和解答块
tags: [sphinx, exercise, installation, getting-started, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:46:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 快速开始

## 安装

```bash
pip install sphinx-exercise
```

## 最小配置

在 `conf.py` 中添加扩展：

```python
extensions = [
    # ... 其他扩展
    'sphinx_exercise',
]
```

## 第一个练习

```rst
.. exercise:: 第一个练习

   请回答以下问题：1 + 1 = ?
```

构建后输出一个带编号的练习框，显示"Exercise 1：第一个练习"。

## 练习与解答配对

```rst
.. exercise:: 计算阶乘
   :label: factorial

   编写一个函数计算 n!（n的阶乘）。

.. solution:: factorial

   .. code-block:: python

      def factorial(n):
          if n <= 1:
              return 1
          return n * factorial(n - 1)
```

解答通过 label 参数（`factorial`）关联到练习，显示为"Solution to Exercise 1"。

## 引用练习编号

```rst
如 :numref:`factorial` 所示...
```

输出为"如 Exercise 1 所示..."。

## 教师版/学生版切换

**学生版（隐藏解答）**：

```python
# conf.py
hide_solutions = True
```

**教师版（含解答）**：

```python
# conf.py
hide_solutions = False  # 默认值
```

`hide_solutions = True` 时解答内容在构建阶段就被物理移除，学生无法通过查看 HTML 源码获取答案。

## 验证安装

构建文档后检查：

1. 练习显示为带"Exercise N"编号的框
2. 解答显示为"Solution to Exercise N"框
3. `:numref:` 交叉引用正确显示编号
4. `hide_solutions = True` 时解答完全不出现
5. LaTeX/PDF 构建正常输出

## 相关概念

- [简介](/concepts/00-introduction.md)
- [练习指令详解](/concepts/02-exercise-directive.md)
- [基础练习示例](/examples/basic-exercise.md)
