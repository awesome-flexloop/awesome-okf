---
type: Concept
title: 门控指令
description: exercise-start/exercise-end 和 solution-start/solution-end 门控指令对的用法、工作原理和适用场景
tags: [sphinx, exercise, gated, directive, wrap-content]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:52:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 门控指令

## 为什么需要门控指令？

标准的 `.. exercise::` 和 `.. solution::` 指令使用缩进内容块，要求所有内容必须嵌套在指令内部：

```rst
.. exercise::

   这里的内容必须全部缩进
   包括代码块、表格等
```

这在某些场景下不够灵活——当练习内容包含复杂的多指令组合，或者你希望练习区域跨越文档中已有的结构时，缩进嵌套会变得很笨拙。门控指令对（Gated Directives）通过独立的开始/结束标记解决这个问题。

## exercise-start / exercise-end

```rst
.. exercise-start:: 练习标题
   :label: ex-gated

这里可以放任意 RST 内容，不需要缩进。

.. code-block:: python

   print("不需要缩进")

.. note::

   甚至可以包含其他指令。

.. exercise-end::
```

`exercise-start` 和 `exercise-end` 之间的所有内容都会被包含在练习框内。

### 支持的选项

`exercise-start` 继承自 `ExerciseDirective`，支持相同选项：`:label:`、`:class:`、`:nonumber:`、`:hidden:`。

## solution-start / solution-end

同样的模式用于解答：

```rst
.. solution-start:: ex-gated
   :label: sol-gated

解答内容，不需要缩进。

.. code-block:: python

   print("答案")

.. solution-end::
```

`solution-start` 必须指定关联练习的 label（同 `.. solution::`）。

## 工作原理

门控指令对通过以下流程工作：

1. **指令解析阶段**：`exercise-start` 创建开始节点并注册到 `sphinx_exercise_gated_registry[docname]`，记录行号和序列标记 "S"（Start）；`exercise-end` 创建结束节点，记录行号和序列标记 "E"（End）
2. **Transform 阶段**：
   - `CheckGatedDirectives`：验证 start/end 是否正确配对（S 和 E 必须交替出现）
   - `MergeGatedExercises`：找到 start 和 end 节点，将它们之间的所有节点移入练习节点内部
   - `MergeGatedSolutions`：对解答执行同样的合并操作
3. **Post-Transform 阶段**：标题解析和引用更新（同非门控指令）

### 门控注册表结构

```python
env.sphinx_exercise_gated_registry[docname] = {
    "start": [10],           # start 指令所在行号列表
    "end": [25],             # end 指令所在行号列表
    "sequence": ["S", "E"],  # S/E 出现顺序
    "msg": ["exercise-start at line: 10", "exercise-end at line: 25"],
    "type": "exercise"       # "exercise" 或 "solution"
}
```

## 自包含 vs 门控：如何选择

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 简单练习，内容较短 | `.. exercise::` | 语法简洁，一个指令完成 |
| 练习内容包含多个代码块/表格/指令 | `exercise-start/end` | 不需要额外缩进 |
| 练习需要包裹文档中已有的段落结构 | `exercise-start/end` | 不打断文档流 |
| 解答紧邻对应练习 | `.. solution::` | 简单直接 |
| 解答内容较长或跨多个区块 | `solution-start/end` | 灵活包裹 |

## 注意事项

- 门控指令对必须正确配对：每个 start 必须有对应的 end
- 不能交叉嵌套（如 exercise-start → solution-start → exercise-end → solution-end）
- `CheckGatedDirectives` Transform 会检查配对问题并发出警告
- exercise-end 和 solution-end 不接受任何参数或选项

## 相关概念

- [练习指令详解](/concepts/02-exercise-directive.md)
- [解答指令详解](/concepts/03-solution-directive.md)
- [门控练习示例](/examples/gated-exercises.md)
