---
type: Concept
title: sphinx-proof 简介
description: sphinx-proof 是什么——为 Sphinx 文档提供数学定理/引理/定义/证明等学术排版环境，支持自动编号和交叉引用
tags: [sphinx, proof, theorem, math, introduction, academic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:10:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# sphinx-proof 简介

sphinx-proof 是 Executable Books 生态中的数学/学术排版 Sphinx 扩展，为技术文档、数学教材、学术论文提供定理（Theorem）、引理（Lemma）、定义（Definition）、证明（Proof）等结构化排版环境，支持自动编号、交叉引用和 LaTeX 输出。

## 核心功能

- **15种数学环境**：定理、引理、定义、推论、猜想、公理、算法等共15种可编号类型
- **自动编号**：每种类型独立自动编号（Theorem 1, Theorem 2...）
- **交叉引用**：使用 `:label:` 和 `:ref:`/`:numref:` 引用定理编号
- **证明块**：`.. proof::` 指令创建无编号证明环境
- **跨类型编号**：可配置推论与定理共享编号序列
- **双主题CSS**：标准主题和简约主题可选
- **标题格式定制**：自定义标题显示模板
- **LaTeX支持**：完整LaTeX/PDF输出

## 15种定理类型

| 指令 | 中文 | 典型用途 |
|------|------|---------|
| `.. theorem::` | 定理 | 主要结论 |
| `.. lemma::` | 引理 | 辅助定理 |
| `.. corollary::` | 推论 | 定理的直接结论 |
| `.. proposition::` | 命题 | 待证明陈述 |
| `.. definition::` | 定义 | 概念定义 |
| `.. axiom::` | 公理 | 基本假设 |
| `.. conjecture::` | 猜想 | 未证明猜测 |
| `.. proof::` | 证明 | 证明过程（无编号） |
| `.. algorithm::` | 算法 | 算法描述 |
| `.. example::` | 示例 | 举例说明 |
| `.. remark::` | 备注 | 补充说明 |
| `.. property::` | 性质 | 属性描述 |
| `.. observation::` | 观察 | 观察结论 |
| `.. criterion::` | 准则 | 判断标准 |
| `.. assumption::` | 假设 | 前提假设 |
| `.. notation::` | 记号 | 符号约定 |

## 与 sphinx-exercise 的关系

sphinx-proof 与 sphinx-exercise 均由 QuantEcon 团队开发，设计模式相似：
- 都使用 `add_enumerable_node()` + numfig 自动编号
- 都支持 `:label:`/`:nonumber:` 选项
- 都有全局注册表和 Domain 用于交叉引用
- 区别：sphinx-proof 面向数学排版，sphinx-exercise 面向教育练习

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [定理类型详解](/concepts/02-theorem-types.md)
- [证明指令](/concepts/03-proof-directive.md)
