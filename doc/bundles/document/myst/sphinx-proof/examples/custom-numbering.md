---
type: Example
title: 自定义编号与配置
description: 跨类型编号映射、中文编号格式、简约主题、自定义标题格式等配置示例
tags: [sphinx, proof, configuration, numbering, theme, example]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:24:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 自定义编号与配置

## 中文编号格式

```python
# conf.py
extensions = ['sphinx_proof']
language = "zh_CN"

numfig_format = {
    "theorem": "定理 %s",
    "lemma": "引理 %s",
    "definition": "定义 %s",
    "corollary": "推论 %s",
    "proposition": "命题 %s",
    "axiom": "公理 %s",
    "algorithm": "算法 %s",
    "remark": "备注 %s",
    "conjecture": "猜想 %s",
    "example": "示例 %s",
    "property": "性质 %s",
    "observation": "观察 %s",
    "criterion": "准则 %s",
    "assumption": "假设 %s",
    "notation": "记号 %s",
}
```

## 跨类型共享编号

将推论和引理映射到定理的计数器，实现连续编号：

```python
# conf.py
prf_realtyp_to_countertyp = {
    "corollary": "theorem",
    "lemma": "theorem",
}
```

效果：
```
Theorem 1（定理）
Theorem 2（引理，共享编号）
Theorem 3（定理）
Theorem 4（推论，共享编号）
```

## 简约主题

```python
# conf.py
proof_minimal_theme = True
```

简约主题使用更轻量的 CSS，仅带左侧边框，无背景色填充。

## 自定义标题格式

```python
# 默认格式：Theorem 1 (标题)
proof_title_format = " (%t)"

# 方括号：Theorem 1 [标题]
proof_title_format = " [%t]"

# 冒号分隔：Theorem 1: 标题
proof_title_format = ": %t"

# 破折号：Theorem 1 — 标题
proof_title_format = " — %t"
```

```rst
.. theorem:: 费马大定理

   当n>2时，x^n+y^n=z^n无正整数解。
```

使用 `proof_title_format = ": %t"` 时输出："Theorem 1: 费马大定理"

## 自定义字体粗细

```python
# 编号加粗
proof_number_weight = "bold"

# 标题正常粗细
proof_title_weight = "normal"

# 使用数值
proof_number_weight = "700"
proof_title_weight = "400"
```

## 自定义 CSS 类

```rst
.. theorem:: 重要定理
   :class: important highlight

   这个定理有自定义CSS类。

.. proof::
   :class: sketch

   证明概要...
```

在自定义 CSS 中：

```css
div.proof.important {
    border-left: 5px solid #d32f2f;
    background-color: #fff3e0;
}

div.proof.highlight {
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
```

## 组合配置示例

适用于中文数学教材的完整配置：

```python
# conf.py
extensions = ['sphinx_proof']
language = "zh_CN"

numfig_format = {
    "theorem": "定理 %s",
    "lemma": "引理 %s",
    "definition": "定义 %s",
    "corollary": "推论 %s",
    "proposition": "命题 %s",
    "axiom": "公理 %s",
    "algorithm": "算法 %s",
}

# 推论和引理跟随定理编号
prf_realtyp_to_countertyp = {
    "corollary": "theorem",
    "lemma": "theorem",
}

proof_title_format = " — %t"
proof_minimal_theme = True
```

## 相关示例

- [数学定理排版](/examples/math-theorems.md)

## 相关概念

- [配置项参考](/concepts/05-configuration.md)
- [交叉引用与编号映射](/concepts/04-cross-references.md)
