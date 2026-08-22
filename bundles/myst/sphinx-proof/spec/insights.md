---
type: spec
title: sphinx-proof 架构洞察
description: sphinx-proof 源码洞察记录
tags:
- sphinx-proof
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-proof-source
  resource: /references/proof-source.md
  title: sphinx-proof proof-source
---

# sphinx-proof 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。

## 洞察 I-001：类声明式指令注册——15种定理类型一行一个类

- **陈述**：sphinx-proof 为 15 种数学定理类型（theorem/lemma/definition/...）各定义一个仅含 `name` 属性的空类，全部继承共享 `ElementDirective` 基类。基类在 `run()` 中通过 `self.name.split(":")[1]` 动态获取类型名，根据类型名查找对应节点类、CSS 类、计数器类型，实现"声明一个类=注册一个指令"的极简扩展模式。
- **证据**：F-005~F-008（15种类型仅设name属性）、F-012（动态获取realtyp）、F-103（动态查找NODE_TYPES[countertyp]）
- **反常识**：大多数 Sphinx 扩展为每种指令写一个独立的 run() 方法，导致大量重复代码。sphinx-proof 用"空类+共享基类+动态分发"模式，新增定理类型只需在 proof_type.py 中添加一个 3 行空类，不需要修改任何其他代码——基类的 `realtyp` 反射机制自动处理所有差异。
- **行动**：设计多类型同构指令族时（如告警级别、数学环境、提示框类型），使用空类继承+基类动态分发模式，将类型差异通过数据（字典/配置）而非代码（if/elif）驱动。

## 洞察 I-002：跨类型编号映射——prf_realtyp_to_countertyp 的计数器共享

- **陈述**：通过 `prf_realtyp_to_countertyp` 配置字典，可将不同定理类型映射到同一计数器。例如将 corollary（推论）映射到 theorem（定理），使推论和定理共享连续编号（Theorem 1, Theorem 2, Corollary 3），符合数学文档惯例（推论继承定理编号序列）。
- **证据**：F-013（countertyp映射查找）、F-031（prf_realtyp_to_countertyp配置）、F-120（node存储countertype属性）、DEFAULT_REALTYP_TO_COUNTERTYP默认每种类型独立计数
- **反常识**：Sphinx 内置的 `add_enumerable_node()` 要求每种 figtype 独立编号。sphinx-proof 通过在指令层面（而非 Sphinx 层面）做 countertype 映射，将 corollary 的节点创建为 theorem 类型的 enumerable node，巧妙绕过了 Sphinx 的限制——node_type = NODE_TYPES[countertyp] 而非 NODE_TYPES[realtyp]。
- **行动**：需要跨类型共享编号时，在指令层选择目标类型的节点类而非新建独立计数器；通过配置映射表而非硬编码类型关系，保持灵活性。

## 洞察 I-003：CSS 运行时修改——构建后注入字体配置

- **陈述**：`copy_asset_files()` 在 build-finished 阶段复制 CSS 后，若用户配置了 `proof_number_weight` 或 `proof_title_weight`，会读取输出目录中的 CSS 文件，通过字符串替换（`str.replace()`）将默认 font-weight 值替换为用户配置值，再写回文件。
- **证据**：F-082~F-099（CSS字符串替换逻辑）、F-033~F-034（字体粗细配置项）
- **反常识**：常规做法是在 CSS 中使用 CSS 变量（`--proof-number-weight`），通过内联 style 或额外 CSS 文件覆盖。sphinx-proof 选择直接修改输出 CSS 文件的"粗暴"方式，原因是避免了 CSS 变量的兼容性问题（老浏览器）和额外 CSS 文件的加载——但代价是依赖 CSS 文件中精确的字符串匹配，如果 CSS 格式变化就会替换失败。
- **行动**：简单的 CSS 主题定制可以在构建后通过字符串替换注入配置，但更推荐使用 CSS 变量方案以获得更好的可维护性。

## 洞察 I-004：Proof 指令的 Admonition 复用——零编号证明块

- **陈述**：`.. proof::` 指令不创建自定义节点，而是直接使用 docutils 的 `nodes.admonition()` 标准节点。它通过在内容第一行自动添加 "Proof. " 前缀来模拟证明标题，而非使用独立的标题节点。
- **证据**：F-023（nodes.admonition()创建节点）、F-024（self.content[0] = "Proof. " + 原文）、F-021（proof指令无label/nonumber选项）
- **反常识**：与 15 种定理类型使用自定义 enumerable node 不同，proof 指令刻意不做编号和标签，直接复用 admonition 视觉风格。这是因为在数学文档中，证明（Proof）总是紧邻它所证明的定理，不需要独立编号或交叉引用——它是定理的附属，而非独立实体。这种不对称设计（定理编号/证明不编号）是对数学写作惯例的忠实反映。
- **行动**：区分"需要编号和引用的独立实体"和"依附于其他实体的附属块"，前者使用自定义 enumerable node + Domain 注册，后者可复用 docutils 标准节点（admonition）简化实现。

## 知识地图

```
sphinx-proof/
├── 入门层
│   ├── 00-introduction.md     → I-001 功能概览与15种定理类型
│   └── 01-getting-started.md  → 安装与基本用法
├── 核心层
│   ├── 02-theorem-types.md    → I-001 15种定理类型详解
│   ├── 03-proof-directive.md  → I-004 proof指令与证明块
│   ├── 04-cross-references.md → I-002 交叉引用与编号映射
│   └── 05-configuration.md    → I-003 主题与样式配置
└── 实践层
    └── examples/
        ├── math-theorems.md   → 数学定理排版示例
        └── custom-numbering.md → 跨类型编号与自定义配置
```
