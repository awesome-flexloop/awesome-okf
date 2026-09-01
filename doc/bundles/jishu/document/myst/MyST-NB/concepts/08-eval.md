---
type: Concept
title: Eval 内联求值
description: "{eval} 角色/指令在 Markdown 正文中内联求值 kernel 变量，inline 执行模式，eval_name_regex 安全限制"
tags:
- myst-nb
- eval
- inline
- variable
- kernel
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T02:30:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: mystnb-source
  resource: /references/mystnb-source.md
  title: MyST-NB 源码路径映射
---

## Eval 内联求值

Eval 是 MyST-NB 的内联变量求值系统，允许在 Markdown 正文句子中通过 `{eval}` 角色实时求值 kernel 变量的值，实现「文中有码，码中有文」的计算叙事。

## 基本用法

### 前提条件

Eval 需要 `nb_execution_mode = "inline"`（inline 模式维护持久 kernel 连接）。

### 行内求值

```markdown
数据集中共有 {eval}`len(df)` 条记录。
模型准确率为 {eval}`accuracy`，F1 分数为 {eval}`f1_score:.3f`。
```

### 块级求值

````markdown
模型性能统计：

```{eval}
df.describe()
```
````

块级 eval 会将表达式的输出按 MIME 优先级渲染（类似 code cell 输出）。

## 工作原理

1. **Kernel 连接**：inline 模式下，`NotebookClientInline` 启动并维护一个持久的 Jupyter kernel
2. **变量求值**：{eval} 角色调用 `nb_client.eval_variable(key)` 在 kernel 中执行表达式
3. **输出获取**：求值结果以 mimebundle 形式返回
4. **渲染**：按 MIME 优先级选择渲染方式，生成 docutils 节点

## 安全限制

为防止任意代码执行，eval 表达式受 `nb_eval_name_regex` 限制：

```python
nb_eval_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
```

这意味着默认情况下，eval 只允许简单的变量名（如 `x`、`my_var`），不允许函数调用（如 `df.mean()`）或复杂表达式。

如果需要更灵活的表达式，可以放宽正则：

```python
import re
nb_eval_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_.\[\]():,'\" ]*$"
```

> ⚠️ 注意：放宽 eval 正则会增加安全风险，特别是在构建不受信任的 notebook 时。

## 与 Glue 的区别

| 特性 | Glue | Eval |
|------|------|------|
| 方向 | 代码→文档（先计算后引用） | 文档→代码（正文中求值） |
| 时机 | Notebook 执行阶段提取 | 文档解析阶段实时求值 |
| Kernel | 普通执行模式即可 | 需要 inline 模式（持久 kernel） |
| 表达式 | 变量名（glue() 的参数） | 任意 Python 表达式（受正则限制） |
| 跨页面 | 支持（NbGlueDomain） | 不支持（仅限当前文档的 kernel） |
| 输出控制 | 多种渲染模式（text/md/figure/math） | 自动选择 MIME 类型 |

## 典型场景

- **报告中的数值**：`共 {eval}`n_samples` 个样本，平均值 {eval}`mean_val:.2f``
- **动态统计**：在正文中插入实时计算的统计量
- **条件内容**（配合 glue 更灵活）：根据计算结果在文档中展示不同内容

## 错误处理

- 表达式不匹配正则 → `EvalNameError`，发出警告
- 变量不存在 → `RetrievalError`，发出警告
- 表达式执行出错 → 显示 ename/evalue 错误信息
- Kernel 不可用 → 提示 "This document does not have a running kernel"

## 相关概念

- [Glue 变量粘贴](07-glue.md)
- [执行模式与缓存](05-execution-modes.md)
- [配置系统](04-config-system.md)
- [Glue & Eval 实战示例](../examples/03-glue-and-eval.md)
