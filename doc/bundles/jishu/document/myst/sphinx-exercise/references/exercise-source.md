---
type: Reference
title: sphinx-exercise 源码路径映射
description: sphinx-exercise 核心源文件路径、指令、节点与关键代码位置索引
tags: [sphinx, exercise, solution, directive, source, executable-books]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:42:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-repo
    resource: https://github.com/executablebooks/sphinx-exercise
    title: sphinx-exercise GitHub Repository
---

# sphinx-exercise 源码路径映射

源路径相对于 `external/libs/ai/executablebooks/sphinx-exercise/`。

## 核心文件清单

| 文件 | 职责 |
|------|------|
| `sphinx_exercise/__init__.py` | setup()、事件处理、注册表管理、资源复制 |
| `sphinx_exercise/directive.py` | 6个指令类（Exercise/Solution + Start/End门控对） |
| `sphinx_exercise/nodes.py` | 自定义节点类型与 HTML/LaTeX visit/depart 方法 |
| `sphinx_exercise/transforms.py` | CheckGatedDirectives、MergeGatedExercises、MergeGatedSolutions |
| `sphinx_exercise/post_transforms.py` | 标题解析、引用更新、链接文本解析 |
| `sphinx_exercise/latex.py` | LaTeX 输出支持 |
| `sphinx_exercise/utils.py` | 工具函数 |
| `sphinx_exercise/_compat.py` | docutils findall 兼容性封装 |
| `sphinx_exercise/assets/html/exercise.css` | HTML 样式 |
| `sphinx_exercise/translations/locales/` | i18n 翻译文件 |

## 六个指令

| 指令 | 类名 | 继承 | 说明 |
|------|------|------|------|
| `.. exercise::` | ExerciseDirective | SphinxExerciseBaseDirective | 带编号/无编号练习块 |
| `.. exercise-start::` | ExerciseStartDirective | ExerciseDirective | 门控练习开始 |
| `.. exercise-end::` | ExerciseEndDirective | SphinxDirective | 门控练习结束 |
| `.. solution:: <label>` | SolutionDirective | SphinxExerciseBaseDirective | 关联练习的解答块 |
| `.. solution-start:: <label>` | SolutionStartDirective | SolutionDirective | 门控解答开始 |
| `.. solution-end::` | SolutionEndDirective | SphinxDirective | 门控解答结束 |

## setup() 关键事件连接顺序

| 事件 | 回调 | 顺序 |
|------|------|------|
| config-inited | init_numfig | 1 |
| env-purge-doc | purge_exercises | 5 |
| doctree-read | doctree_read | 8 |
| env-merge-info | merge_exercises | 9 |
| env-updated | validate_exercise_solution_order | 10 |
| build-finished | copy_asset_files | 16 |

## 相关概念

- [简介](../concepts/00-introduction.md)
- [练习指令详解](../concepts/02-exercise-directive.md)
- [解答指令详解](../concepts/03-solution-directive.md)
