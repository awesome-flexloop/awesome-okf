---
type: Concept
title: 定理类型详解
description: sphinx-proof 15种可编号定理类型的语法、选项、标题格式和编号机制
tags: [sphinx, proof, theorem, directive, types, numbering]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:14:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 定理类型详解

## 通用语法

所有15种可编号定理类型共享相同的语法（均继承自 `ElementDirective`）：

```rst
.. 类型名:: [可选标题]
   :label: 唯一标识符
   :class: 自定义CSS类
   :nonumber:

   内容...
```

## 参数与选项

### 可选参数：标题

第一个（也是唯一的）位置参数是定理的自定义标题：

```rst
.. theorem:: 费马大定理

   当整数 :math:`n > 2` 时，方程 :math:`x^n + y^n = z^n` 没有正整数解。
```

标题显示格式由 `proof_title_format` 配置控制，默认为 ` (%t)`，即显示为"Theorem 1 (费马大定理)"。

### `:label:` 选项

指定唯一标识符用于交叉引用：

```rst
.. lemma:: 辅助不等式
   :label: lem-aux

   对任意实数 :math:`x`，有 :math:`x^2 \geq 0`。

由:numref:`lem-aux` 可知...
```

若不指定 label，自动生成为 `{类型名}-{序号}`（如 `theorem-0`）。

### `:class:` 选项

添加自定义 CSS 类：

```rst
.. theorem:: 重要定理
   :class: important

   这个定理需要特别注意。
```

### `:nonumber:` 选项

禁用自动编号：

```rst
.. theorem:: 常识性结论
   :nonumber:

   所有正数大于零。
```

无编号时使用 `unenumerable_node`，显示为不带编号的定理框。

## 15种类型详解

### 核心逻辑类型

| 类型 | 用途 | 编号格式 |
|------|------|---------|
| `theorem` | 主要定理、核心结论 | Theorem 1, 2, 3... |
| `lemma` | 引理、辅助定理 | Lemma 1, 2, 3... |
| `proposition` | 命题、待证陈述 | Proposition 1, 2... |
| `corollary` | 推论（由定理直接得出） | Corollary 1, 2... |

### 定义与基础类型

| 类型 | 用途 | 编号格式 |
|------|------|---------|
| `definition` | 概念定义 | Definition 1, 2... |
| `axiom` | 公理、基本假设（无需证明） | Axiom 1, 2... |
| `assumption` | 假设、前提条件 | Assumption 1, 2... |
| `notation` | 符号约定 | Notation 1, 2... |

### 说明类型

| 类型 | 用途 | 编号格式 |
|------|------|---------|
| `remark` | 备注、补充说明 | Remark 1, 2... |
| `conjecture` | 猜想（尚未证明） | Conjecture 1, 2... |
| `example` | 示例、例证 | Example 1, 2... |
| `observation` | 观察结果 | Observation 1, 2... |
| `property` | 性质、属性 | Property 1, 2... |
| `criterion` | 判定准则 | Criterion 1, 2... |

### 算法类型

| 类型 | 用途 | 编号格式 |
|------|------|---------|
| `algorithm` | 算法描述 | Algorithm 1, 2... |

## 独立编号机制

默认情况下，每种类型拥有独立的编号计数器：

- Theorem 1 → Theorem 2 → Theorem 3（独立序列）
- Lemma 1 → Lemma 2（独立序列）
- Definition 1 → Definition 2（独立序列）

这通过 `DEFAULT_REALTYP_TO_COUNTERTYP` 字典实现，每种类型映射到自身作为计数器类型。

## CSS 类名规则

每个定理块的 CSS 类为 `["proof", 类型名]`：

- 定理：`class="proof theorem"`
- 引理：`class="proof lemma"`
- 定义：`class="proof definition"`

可通过 CSS 区分不同类型的外观（颜色、图标等）。

## HTML 输出结构

```html
<div class="proof theorem" id="th-pythagoras">
  <p class="admonition-title">
    <span class="caption-number">Theorem 1</span>
    <span class="caption-text"> (勾股定理)</span>
  </p>
  <div class="theorem-content">
    在直角三角形中...
  </div>
</div>
```

## 重复标签检测

若两个定理使用相同的 `:label:`，会输出红色警告：

```
duplicate theorem label 'th-main', other instance in other_doc
```

## 相关概念

- [证明指令](/concepts/03-proof-directive.md)
- [交叉引用与编号映射](/concepts/04-cross-references.md)
- [配置项参考](/concepts/05-configuration.md)
- [数学定理排版示例](/examples/math-theorems.md)
