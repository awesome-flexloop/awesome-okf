---
type: Example
title: 教师版/学生版构建配置
description: "使用 hide_solutions 配置实现教师版/学生版双版本构建，以及自定义 CSS 类和 :hidden: 选项的用法"
tags:
- sphinx
- exercise
- hide-solutions
- teacher-student
- build
- example
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T03:58:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: exercise-source
  resource: /references/exercise-source.md
  title: sphinx-exercise 源码路径映射
---

# 教师版/学生版构建配置

## 方案一：命令行参数切换

使用 `-D` 选项覆盖配置：

```bash
# 学生版（无解答）
sphinx-build -b html -D hide_solutions=True docs docs/_build/student

# 教师版（含解答）
sphinx-build -b html -D hide_solutions=False docs docs/_build/teacher
```

## 方案二：双配置文件

创建 `conf_student.py`：

```python
# conf_student.py
from conf import *  # 继承主配置
hide_solutions = True
```

创建 `conf_teacher.py`：

```python
# conf_teacher.py
from conf import *
hide_solutions = False
```

构建命令：

```bash
# 学生版
sphinx-build -b html -c . -C conf_student.py docs docs/_build/student

# 教师版
sphinx-build -b html docs docs/_build/teacher
```

## 方案三：Makefile 快捷方式

在 `Makefile` 中添加：

```makefile
student:
	@$(SPHINXBUILD) -b html -D hide_solutions=True $(ALLSPHINXOPTS) $(BUILDDIR)/student

teacher:
	@$(SPHINXBUILD) -b html -D hide_solutions=False $(ALLSPHINXOPTS) $(BUILDDIR)/teacher
```

使用：

```bash
make student  # 构建学生版
make teacher  # 构建教师版
```

## 单独隐藏特定练习/解答

即使不使用全局 `hide_solutions`，也可以用 `:hidden:` 选项隐藏单个条目：

```rst
.. exercise:: 内部使用的草稿题
   :hidden:

   这道题不会出现在任何版本中。

.. exercise:: 正式题目
   :label: ex-official

   这是正式题目。

.. solution:: ex-official
   :hidden:

   这个解答也被单独隐藏。
```

## exercise_style 配置示例

使用 `"solution_follow_exercise"` 风格时，解答标题更简洁：

```python
# conf.py
exercise_style = "solution_follow_exercise"
```

此模式下解答必须在对应练习之后（同文档内）：

```rst
.. exercise:: 题目一
   :label: ex1

   题目内容...

.. solution:: ex1

   解答内容...  ✅ 正确（在练习之后）
```

## 中文编号格式

```python
# conf.py
language = "zh_CN"
numfig_format = {"exercise": "习题 %s"}
```

输出标题变为"习题 1"、"习题 2"等。

## 自定义 CSS 样式

添加自定义 CSS 类区分不同难度：

```rst
.. exercise:: 基础题
   :class: easy

   简单的概念题。

.. exercise:: 进阶题
   :class: medium

   需要思考的题目。

.. exercise:: 挑战题
   :class: hard

   高难度题目。
```

在自定义 CSS 中：

```css
.exercise.easy { border-left: 4px solid #4CAF50; }
.exercise.medium { border-left: 4px solid #FF9800; }
.exercise.hard { border-left: 4px solid #F44336; }
```

## 相关示例

- [基础练习与解答](/examples/basic-exercise.md)
- [门控练习包裹内容](/examples/gated-exercises.md)

## 相关概念

- [配置项参考](/concepts/05-configuration.md)
- [解答指令详解](/concepts/03-solution-directive.md)
