---
type: Concept
title: 解答指令详解
description: solution 指令的语法、与练习的关联方式、标题文本规则、hide_solutions 全局隐藏机制
tags: [sphinx, exercise, solution, directive, hide, teacher-student]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:50:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 解答指令详解

## 基本语法

```rst
.. solution:: <练习label>
   :label: 解答的唯一标识符
   :class: 自定义CSS类
   :hidden:

   解答内容...
```

与 `exercise` 指令不同，`solution` **必须**提供一个参数：关联练习的 label。

## 参数

### 必填参数：练习引用

solution 的第一个参数必须是对应练习的 label 值：

```rst
.. exercise:: 计算阶乘
   :label: ex-factorial

   编写计算 n! 的函数。

.. solution:: ex-factorial

   .. code-block:: python

      def factorial(n):
          return 1 if n <= 1 else n * factorial(n-1)
```

解答标题显示为"Solution to Exercise 1"（自动关联练习编号）。

## 选项

### `:label:`

为解答本身指定唯一标识符，可被交叉引用：

```rst
.. solution:: ex-factorial
   :label: sol-factorial

   解答内容...

查看 :ref:`sol-factorial` 获取参考答案。
```

### `:class:`

添加自定义 CSS 类：

```rst
.. solution:: ex-factorial
   :class: detailed-solution
```

### `:hidden:`

单独隐藏某个解答（构建时移除）：

```rst
.. solution:: ex-factorial
   :hidden:

   这个解答不会出现。
```

## 标题文本规则

解答标题根据 `exercise_style` 配置有两种格式：

| 配置值 | 标题格式 | 示例 |
|--------|---------|------|
| 默认（`""`） | "Solution to Exercise N" | Solution to Exercise 1 |
| `"solution_follow_exercise"` | "Solution" | Solution（标题后跟随练习编号） |

```python
# conf.py
exercise_style = "solution_follow_exercise"
```

当使用 `"solution_follow_exercise"` 时，`validate_exercise_solution_order()` 会在 env-updated 阶段验证：
- 解答必须与引用的练习在同一文档中
- 解答必须出现在练习之后

违反时输出黄色警告。

## hide_solutions：全局隐藏机制

在 `conf.py` 中设置：

```python
hide_solutions = True
```

### 工作原理

- 当 `hide_solutions = True` 时，`SolutionDirective.run()` 在最开始检查此配置
- 若为 True，直接返回空列表 `[]`，解答内容完全不进入 doctree
- 这是**构建时物理移除**，非 CSS `display: none` 隐藏
- 输出的 HTML/LaTeX/PDF 中不包含任何解答文本

### 双版本构建策略

使用 Sphinx 的 `-c` 选项或多个 conf 文件实现教师版/学生版：

```bash
# 学生版（无解答）
sphinx-build -b html -D hide_solutions=True source build/student

# 教师版（含解答）
sphinx-build -b html source build/teacher
```

或者使用两个 conf 文件：

```python
# conf_student.py
from conf import *
hide_solutions = True
```

```bash
sphinx-build -c . -b html -C source build/student  # 使用 conf_student.py
```

## 解答标题的延迟解析

解答标题在 Post-Transform 阶段（而非指令 run() 阶段）才最终确定，因为：
1. 练习的自动编号在 enumerable node 解析后才分配
2. 跨文档引用需要等待所有 doctree 读取完毕
3. `ResolveTitlesInSolutions` Post-Transform 查找 `target_label` 对应的练习节点，获取编号后生成完整标题

## 相关概念

- [练习指令详解](/concepts/02-exercise-directive.md)
- [门控指令](/concepts/04-gated-directives.md)
- [配置项参考](/concepts/05-configuration.md)
- [教师版/学生版示例](/examples/hide-solutions.md)
