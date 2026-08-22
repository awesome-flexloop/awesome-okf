---
type: Reference
title: sphinx-proof 源码路径映射
description: sphinx-proof 核心源文件、15种定理类型指令与配置项索引
tags: [sphinx, proof, theorem, directive, source, math]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:08:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-repo
    resource: https://github.com/executablebooks/sphinx-proof
    title: sphinx-proof GitHub Repository
---

# sphinx-proof 源码路径映射

源路径相对于 `external/libs/ai/executablebooks/sphinx-proof/`。

## 核心文件清单

| 文件 | 职责 |
|------|------|
| `sphinx_proof/__init__.py` | setup()、配置验证、CSS复制、numfig初始化 |
| `sphinx_proof/directive.py` | ElementDirective（15种类型共享基类）、ProofDirective |
| `sphinx_proof/proof_type.py` | 15种定理类型的空类声明、PROOF_TYPES字典 |
| `sphinx_proof/nodes.py` | 自定义节点与visit/depart方法 |
| `sphinx_proof/domain.py` | ProofDomain（交叉引用域） |
| `sphinx_proof/_static/proof.css` | 标准主题CSS |
| `sphinx_proof/_static/minimal/proof.css` | 简约主题CSS |

## 15种定理类型

| 类型 | 指令名 | 中文 | 编号 |
|------|--------|------|------|
| axiom | `.. axiom::` | 公理 | ✅ |
| theorem | `.. theorem::` | 定理 | ✅ |
| lemma | `.. lemma::` | 引理 | ✅ |
| algorithm | `.. algorithm::` | 算法 | ✅ |
| definition | `.. definition::` | 定义 | ✅ |
| remark | `.. remark::` | 备注 | ✅ |
| conjecture | `.. conjecture::` | 猜想 | ✅ |
| corollary | `.. corollary::` | 推论 | ✅ |
| criterion | `.. criterion::` | 准则 | ✅ |
| example | `.. example::` | 示例 | ✅ |
| property | `.. property::` | 性质 | ✅ |
| observation | `.. observation::` | 观察 | ✅ |
| proposition | `.. proposition::` | 命题 | ✅ |
| assumption | `.. assumption::` | 假设 | ✅ |
| notation | `.. notation::` | 记号 | ✅ |
| proof | `.. proof::` | 证明 | ❌（admonition，无编号） |

## 配置项一览

| 配置 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `proof_minimal_theme` | bool | False | 使用简约主题CSS |
| `prf_realtyp_to_countertyp` | dict | {} | 跨类型编号映射 |
| `proof_title_format` | str | `" (%t)"` | 标题格式模板 |
| `proof_number_weight` | str | "" | 编号字体粗细 |
| `proof_title_weight` | str | "" | 标题字体粗细 |

## 相关概念

- [简介](/concepts/00-introduction.md)
- [定理类型详解](/concepts/02-theorem-types.md)
- [配置项参考](/concepts/05-configuration.md)
