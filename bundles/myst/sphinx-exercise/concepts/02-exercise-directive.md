---
type: Concept
title: 练习指令详解
description: exercise 指令的语法、选项（label/class/nonumber/hidden）、自动编号机制与交叉引用
tags: [sphinx, exercise, directive, numbering, cross-reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:48:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 练习指令详解

## 基本语法

```rst
.. exercise:: [副标题文本]
   :label: 唯一标识符
   :class: 自定义CSS类
   :nonumber:
   :hidden:

   练习内容...
```

## 参数与选项

### 参数：副标题（可选）

第一个（也是唯一的）位置参数是练习的副标题，显示在编号之后：

```rst
.. exercise:: 计算斐波那契数列

   编写函数计算第 n 个斐波那契数。
```

输出标题为"Exercise 1：计算斐波那契数列"。

副标题支持行内 RST 标记（通过 `state.inline_text()` 解析）。

### 选项：`:label:`

为练习指定唯一标识符，用于交叉引用和解答关联：

```rst
.. exercise:: 阶乘计算
   :label: ex-factorial

   计算 5! 的值。

解答见 :numref:`ex-factorial` 的解答。
```

若不指定 label，自动生成格式为 `{docname}-exercise-{serial_number}` 的内部 label。

### 选项：`:nonumber:`

禁用自动编号：

```rst
.. exercise:: 思考题
   :nonumber:

   这是一个不编号的思考问题。
```

- 无 `:nonumber:`：使用 `exercise_enumerable_node`，通过 Sphinx numfig 机制自动编号
- 有 `:nonumber:`：使用 `exercise_node`，无编号，仅显示"Exercise"标题

### 选项：`:class:`

添加自定义 CSS 类用于样式定制：

```rst
.. exercise:: 挑战题
   :class: challenge

   这是一道挑战级别的题目。
```

### 选项：`:hidden:`

从输出中移除此练习（构建时移除，非 CSS 隐藏）：

```rst
.. exercise:: 草稿题目
   :hidden:

   这道题不会出现在最终文档中。
```

## 自动编号机制

sphinx-exercise 使用 Sphinx 内置的 `numfig`（编号图表）机制：

1. `init_numfig()` 在配置初始化时强制设置 `numfig = True`
2. 通过 `app.add_enumerable_node(exercise_enumerable_node, "exercise", None)` 注册可编号节点
3. 编号格式为 `numfig_format = {"exercise": "Exercise %s"}`，`%s` 替换为编号
4. 编号由 Sphinx 在解析阶段自动递增，按文档中出现顺序编号

### 自定义编号格式

在 `conf.py` 中覆盖 `numfig_format`：

```python
numfig_format = {"exercise": "习题 %s"}
```

## 交叉引用

使用标准 Sphinx 引用角色引用练习：

| 角色 | 效果 |
|------|------|
| `:ref:`ex-label`` | 跳转到练习，显示标题文本 |
| `:numref:`ex-label`` | 显示"Exercise N"格式的编号链接 |

```rst
.. exercise:: 我的练习
   :label: my-ex

   练习内容...

如 :numref:`my-ex` 所述，详见 :ref:`my-ex`。
```

## HTML 输出结构

```html
<div class="exercise" id="ex-factorial">
  <div class="exercise-header">
    <span class="exercise-number">Exercise 1</span>
    <span class="exercise-title">计算阶乘</span>
  </div>
  <div class="exercise-content">
    编写一个函数计算 n! ...
  </div>
</div>
```

## 相关概念

- [解答指令详解](/concepts/03-solution-directive.md)
- [门控指令](/concepts/04-gated-directives.md)
- [配置项参考](/concepts/05-configuration.md)
- [基础练习示例](/examples/basic-exercise.md)
