---
type: Concept
title: sphinx-exercise 简介
description: sphinx-exercise 是什么——为 Sphinx 文档添加练习与解答块，支持自动编号、交叉引用、全局隐藏解答、门控指令和多语言
tags: [sphinx, exercise, solution, education, introduction, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:44:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# sphinx-exercise 简介

sphinx-exercise 是 Executable Books 生态中的教育类 Sphinx 扩展，为技术文档、教材、教程添加结构化的练习（Exercise）和解答（Solution）块，支持自动编号、交叉引用、教师版/学生版构建和 LaTeX 输出。

## 核心功能

- **自动编号**：练习块默认自动编号为"Exercise 1"、"Exercise 2"等，可通过 `:nonumber:` 关闭
- **解答关联**：`.. solution::` 通过 label 关联对应练习，标题自动显示"Solution to Exercise N"
- **交叉引用**：使用 `{ref}` 或 `{numref}` 角色引用练习编号
- **全局隐藏**：`hide_solutions = True` 在构建时物理移除所有解答内容（非CSS隐藏）
- **门控指令**：`exercise-start`/`exercise-end` 对可包裹任意 RST 内容
- **多语言支持**：内置翻译框架，"Exercise"/"Solution"等标题文本支持国际化
- **LaTeX/PDF 支持**：完整的 LaTeX 输出支持
- **并行构建安全**：正确实现 purge/merge 支持并行读写

## 适用场景

- 编程教程的课后习题
- 数学教材的例题与解答
- 在线课程的互动练习
- 技术文档的"动手试试"区块
- 教师版（含答案）和学生版（不含答案）双版本构建

## 指令概览

| 指令 | 用途 |
|------|------|
| `.. exercise:: [副标题]` | 创建练习块（自包含内容） |
| `.. exercise-start:: [副标题]` / `.. exercise-end::` | 门控练习对（包裹任意内容） |
| `.. solution:: <exercise-label>` | 创建解答块 |
| `.. solution-start:: <label>` / `.. solution-end::` | 门控解答对 |

## 相关概念

- [快速开始](01-getting-started.md)
- [练习指令详解](02-exercise-directive.md)
- [解答指令详解](03-solution-directive.md)
