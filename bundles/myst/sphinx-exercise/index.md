---
type: bundle
title: sphinx-exercise
description: Executable Books 生态的 Sphinx 练习与解答扩展，支持自动编号、交叉引用、教师版/学生版构建和门控指令
tags:
- sphinx
- extension
- exercise
- solution
- education
- numbering
- cross-reference
- executable-books
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T04:02:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: exercise-repo
  resource: "https://github.com/executablebooks/sphinx-exercise"
  title: sphinx-exercise GitHub Repository
okf_version: '0.2'
---

# sphinx-exercise

sphinx-exercise 是 Executable Books 生态中的教育类 Sphinx 扩展，为技术文档、教材、教程添加结构化的练习（Exercise）与解答（Solution）块。支持自动编号、交叉引用、教师版/学生版双版本构建、门控指令包裹任意内容、多语言国际化和 LaTeX/PDF 输出。

## 核心功能

- **自动编号**：练习块自动编号为"Exercise N"，使用 Sphinx numfig 机制
- **解答关联**：通过 label 将解答绑定到练习，标题自动显示"Solution to Exercise N"
- **交叉引用**：`:ref:` 和 `:numref:` 引用练习编号
- **全局隐藏**：`hide_solutions=True` 构建时物理移除解答（非CSS隐藏）
- **门控指令**：start/end 指令对包裹任意 RST 内容，无需缩进
- **多语言**：内置 i18n 框架，"Exercise"/"Solution"可翻译
- **LaTeX 支持**：完整的 LaTeX/PDF 输出

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](/concepts/index.md) |
| 💡 示例 | [示例代码](/examples/index.md) |
| 📚 参考 | [源码参考](/references/index.md) |
| 🔬 规格 | [事实清单](/spec/facts.md) · [架构洞察](/spec/insights.md) |

## 快速开始

```bash
pip install sphinx-exercise
```

```python
# conf.py
extensions = ['sphinx_exercise']
```

```rst
.. exercise:: 计算阶乘
   :label: ex-factorial

   编写函数计算 n!。

.. solution:: ex-factorial

   .. code-block:: python

      def factorial(n):
          return 1 if n <= 1 else n * factorial(n-1)
```

## 更新日志

见 [log.md](/log.md)。
