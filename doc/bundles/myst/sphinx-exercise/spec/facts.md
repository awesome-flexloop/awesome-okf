---
type: spec
title: sphinx-exercise 源码事实清单
description: sphinx-exercise 源码事实清单
tags:
- sphinx-exercise
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-exercise-source
  resource: /references/exercise-source.md
  title: sphinx-exercise exercise-source
---

# sphinx-exercise 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 版本号 `__version__ = "1.2.1"`
- F-002: 包名为 `sphinx-exercise`，为 Sphinx 文档添加练习（Exercise）与解答（Solution）支持
- F-003: 核心 Python 文件 9 个：`__init__.py`（setup逻辑354行）、`directive.py`（438行）、`nodes.py`、`transforms.py`、`post_transforms.py`、`latex.py`、`utils.py`、`_compat.py`、`translations/_convert.py`
- F-004: 静态资源：`assets/html/exercise.css`
- F-005: 国际化消息目录名 `"exercise"`，使用 `sphinx.locale.get_translation()` 加载翻译
- F-006: 翻译文件位于 `translations/locales/` 目录，通过 `app.add_message_catalog()` 注册

## 自定义节点类型

- F-007: `exercise_node`：无编号练习节点，非 enumerable
- F-008: `exercise_enumerable_node`：带自动编号练习节点，通过 `app.add_enumerable_node(..., "exercise", None)` 注册
- F-009: `solution_node`：解答节点
- F-010: `exercise_end_node`、`solution_start_node`、`solution_end_node`：门控指令的内部节点，无 visit/depart 方法
- F-011: `exercise_title`、`exercise_subtitle`、`solution_title`、`solution_subtitle`：内部标题节点，post_transform 阶段解析为 docutils 节点
- F-012: `exercise_latex_number_reference`：LaTeX 编号引用节点

## ExerciseDirective（练习指令）

- F-013: `name = "exercise"`，`has_content = True`，`required_arguments = 0`，`optional_arguments = 1`
- F-014: option_spec：`label`（unchanged_required）、`class`（class_option）、`nonumber`（flag）、`hidden`（flag）
- F-015: 若指定 `:nonumber:` 则使用 `exercise_node`，否则使用 `exercise_enumerable_node`（自动编号）
- F-016: 可选参数作为副标题（subtitle），通过 `self.state.inline_text()` 解析行内标记
- F-017: label 未指定时自动生成：`{docname}-exercise-{serial_number}`
- F-018: `:hidden:` 标志使指令返回空列表（不输出到最终文档）
- F-019: `duplicate_labels()` 检查重复标签，重复时返回空列表并输出红色警告
- F-020: 节点属性包括：`classes`、`ids`、`label`、`docname`、`title`、`type`、`hidden`、`serial_number`
- F-021: 注册表 `env.sphinx_exercise_registry[label]` 存储 type、docname 和节点深拷贝

## SolutionDirective（解答指令）

- F-022: `name = "solution"`，`has_content = True`，`required_arguments = 1`（关联练习的 label）
- F-023: option_spec：`label`、`class`、`hidden`（无 `:nonumber:`）
- F-024: 标题文本根据 `exercise_style` 配置切换：默认 `"Solution to"`，`"solution_follow_exercise"` 时为 `"Solution"`
- F-025: 若全局配置 `hide_solutions = True`，solution 指令直接返回空列表
- F-026: 节点存储 `target_label` 属性指向关联练习的 label
- F-027: 解答与练习类似，支持 `:hidden:`、自动 label 生成、重复检测、注册表存储

## 门控指令（Gated Directives）

- F-028: `ExerciseStartDirective` 继承 `ExerciseDirective`，`name = "exercise-start"`
- F-029: `ExerciseEndDirective` 继承 `SphinxDirective`，`name = "exercise-end"`，无参数
- F-030: `SolutionStartDirective` 继承 `SolutionDirective`，`name = "solution-start"`，`solution_node = solution_start_node`
- F-031: `SolutionEndDirective` 继承 `SphinxDirective`，`name = "solution-end"`
- F-032: 门控指令通过 `env.sphinx_exercise_gated_registry` 跟踪 start/end 位置和序列（S/E）
- F-033: 每个文档的门控注册表包含：`start`（行号列表）、`end`（行号列表）、`sequence`（S/E序列）、`msg`（消息列表）、`type`（exercise/solution）

## Transforms（转换阶段）

- F-034: `CheckGatedDirectives`：app.add_transform() 注册，检查门控指令配对（start/end 匹配）
- F-035: `MergeGatedExercises`：app.add_transform() 注册，合并 exercise-start 和 exercise-end 之间的内容
- F-036: `MergeGatedSolutions`：app.add_transform() 注册，合并 solution-start 和 solution-end 之间的内容

## Post-Transforms（后转换阶段）

- F-037: `UpdateReferencesToEnumerated`：将引用更新为指向 enumerable 节点
- F-038: `ResolveTitlesInExercises`：解析练习标题（将 exercise_title/exercise_subtitle 转为标准节点）
- F-039: `ResolveTitlesInSolutions`：解析解答标题，关联目标练习编号
- F-040: `ResolveLinkTextToSolutions`：解析指向解答的链接文本

## setup() 配置项

- F-041: `hide_solutions` 配置，默认 `False`，设为 `True` 全局隐藏所有解答
- F-042: `exercise_style` 配置，默认 `""`，设为 `"solution_follow_exercise"` 时解答标题为"Solution"而非"Solution to"
- F-043: `init_numfig()` 在 `config-inited` 事件中强制 `numfig = True`，设置 `numfig_format = {"exercise": "Exercise %s"}`
- F-044: 事件连接顺序：config-inited(1) → env-purge-doc(5) → doctree-read(8) → env-merge-info(9) → env-updated(10) → build-finished(16)
- F-045: 每个节点注册了 HTML、singlehtml、LaTeX 三种 builder 的 visit/depart 方法
- F-046: `app.add_css_file("exercise.css")` 添加样式
- F-047: `copy_asset_files()` 在 build-finished 时复制 CSS 到输出目录
- F-048: `purge_exercises()` 在 env-purge-doc 时清理注册表中当前文档的条目
- F-049: `merge_exercises()` 在 env-merge-info 时合并并行构建的注册表
- F-050: `doctree_read()` 在 doctree-read 时遍历节点注册到 std domain 的 labels/anonlabels，并跟踪节点顺序
- F-051: `validate_exercise_solution_order()` 在 env-updated 时验证 solution_follow_exercise 模式下解答是否在对应练习之后
- F-052: 返回 `parallel_read_safe: True, parallel_write_safe: True`
