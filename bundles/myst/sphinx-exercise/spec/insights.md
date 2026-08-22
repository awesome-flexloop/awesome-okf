---
type: spec
title: sphinx-exercise 架构洞察
description: sphinx-exercise 源码洞察记录
tags:
- sphinx-exercise
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-exercise-source
  resource: /references/exercise-source.md
  title: sphinx-exercise exercise-source
---

# sphinx-exercise 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。

## 洞察 I-001：Gated 指令对——跨越内容块的非嵌套标记机制

- **陈述**：sphinx-exercise 设计了三对指令：`exercise`/`solution`（自包含块）和 `exercise-start`/`exercise-end`、`solution-start`/`solution-end`（门控对）。门控对通过独立的 start/end 指令标记区域边界，而非使用嵌套内容结构，使得练习/解答可以包裹任意文档内容（包括跨越多段 RST 标记的内容），不受指令嵌套解析限制。
- **证据**：F-028~F-033（门控指令对设计）、F-034~F-036（Transform 阶段合并门控内容）
- **反常识**：docutils 指令的 `has_content = True` 要求内容必须在指令体内部缩进，无法"包裹"同级的其他指令（如代码块、表格、另一个指令）。门控对模式通过两个独立指令标记区域开始和结束，绕过了 docutils 的嵌套限制——但代价是需要 Transform 阶段才能正确合并内容，在 doctree 解析时 start/end 之间的内容还不属于练习节点。
- **行动**：当需要标记任意 RST 内容区域（可能包含其他指令、表格等）时，使用 start/end 门控指令对 + Transform 合并模式，而非强行嵌套内容解析。

## 洞察 I-002：全局注册表驱动的交叉引用系统

- **陈述**：sphinx-exercise 通过 `env.sphinx_exercise_registry` 字典维护全局练习/解答注册表（label → {type, docname, node}），在 `doctree-read` 事件中将节点注册到 Sphinx StandardDomain 的 labels/anonlabels 中，使 `{ref}` 和 `{numref}` 角色可以交叉引用练习编号。
- **证据**：F-021、F-087（注册表存储）、F-050（doctree_read 注册到 std domain）、F-048~F-049（并行构建的 purge/merge）
- **反常识**：练习编号使用 Sphinx 的 `add_enumerable_node()` + `numfig` 机制而非手动编号。这意味着编号由 Sphinx 在 `doctree-resolved` 阶段统一分配，`init_numfig()` 强制开启 `numfig = True` 并注册 `"exercise": "Exercise %s"` 格式——这是与 Sphinx 内置图/表编号同一套机制，不是自定义计数器。
- **行动**：需要自动编号和交叉引用的 Sphinx 扩展应使用 `add_enumerable_node()` + StandardDomain labels，而非自建计数器；务必实现 env-purge-doc 和 env-merge-info 事件处理器以支持并行构建。

## 洞察 I-003：hide_solutions——构建时全局内容移除

- **陈述**：`hide_solutions` 配置设为 `True` 时，所有 `.. solution::` 指令在 `run()` 阶段直接返回空列表 `[]`，内容完全不进入 doctree，而不是通过 CSS 隐藏。这确保解答在教师版/学生版构建中物理移除，无法通过查看源码获取。
- **证据**：F-041（hide_solutions 配置）、F-025（run() 中检查 hide_solutions 返回空）
- **反常识**：很多"隐藏内容"方案使用 CSS `display: none` 或 JS 折叠，这在教育场景中是安全隐患（学生可以查看页面源码看到答案）。sphinx-exercise 在指令解析阶段就丢弃解答内容，输出的 HTML/LaTeX/PDF 中完全不包含解答文本，是真正的"构建时移除"而非"渲染时隐藏"。
- **行动**：教育类文档扩展中，需要"教师版/学生版"内容差异时，在指令 run() 阶段根据配置决定是否返回节点（物理移除），而非依赖 CSS/JS 隐藏。

## 洞察 I-004：Post-Transform 标题解析——标题延迟绑定

- **陈述**：练习和解答的标题节点（exercise_title/exercise_subtitle/solution_title）在指令 run() 阶段只是空节点容器，标题文本在 Post-Transform 阶段（`ResolveTitlesInExercises`、`ResolveTitlesInSolutions`）才被解析为最终的 docutils/Sphinx 节点。解答标题需要在此阶段查找关联练习的编号才能生成"Solution to Exercise 1"这样的完整标题。
- **证据**：F-011（内部标题节点类型）、F-038~F-040（Post-Transform 标题解析）、F-024（标题文本根据 exercise_style 配置）
- **反常识**：为什么不在指令 run() 阶段就生成完整标题？因为（1）exercise 的自动编号在 enumerable node 解析后才确定，（2）solution 需要查找 target_label 对应的练习编号，而跨文档引用在 doctree-read 阶段还未解析，（3）Post-Transform 阶段在所有 doctree 读取完成后执行，此时所有引用目标已可解析。
- **行动**：当节点渲染依赖其他文档或编号等延迟确定的信息时，使用"空壳节点 + Post-Transform 解析"模式，避免在指令 run() 阶段过早绑定信息。

## 知识地图

```
sphinx-exercise/
├── 入门层
│   ├── 00-introduction.md     → I-001, I-003 功能概览
│   └── 01-getting-started.md  → 安装与基础用法
├── 核心层
│   ├── 02-exercise-directive.md  → I-002 练习指令详解
│   ├── 03-solution-directive.md  → I-003, I-004 解答指令与隐藏
│   ├── 04-gated-directives.md    → I-001 门控指令对
│   └── 05-configuration.md       → 配置项与教师/学生版
└── 实践层
    └── examples/
        ├── basic-exercise.md  → 基础练习示例
        ├── hide-solutions.md  → 教师版/学生版配置
        └── gated-exercises.md → 门控指令包裹内容
```
