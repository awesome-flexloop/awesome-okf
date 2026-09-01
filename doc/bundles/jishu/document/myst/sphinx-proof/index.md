---
type: bundle
title: sphinx-proof
description: Executable Books 生态的 Sphinx 数学定理排版扩展，提供15种定理环境和证明块，支持自动编号、交叉引用和跨类型共享编号
tags:
- sphinx
- extension
- proof
- theorem
- math
- academic
- numbering
- latex
- executable-books
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T04:26:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: proof-repo
  resource: "https://github.com/executablebooks/sphinx-proof"
  title: sphinx-proof GitHub Repository
okf_version: '0.2'
---

# sphinx-proof

sphinx-proof 是 Executable Books 生态中的数学/学术排版 Sphinx 扩展，为技术文档和数学教材提供定理（Theorem）、引理（Lemma）、定义（Definition）、证明（Proof）等结构化排版环境。支持15种可编号数学环境、自动编号、交叉引用、跨类型共享编号、双主题 CSS 和 LaTeX/PDF 输出。

## 核心功能

- **15种定理环境**：theorem、lemma、definition、corollary、axiom、algorithm等
- **自动编号**：每种类型独立编号（Theorem 1, 2, 3...）
- **证明块**：`.. proof::` 创建无编号证明环境，自动添加"Proof."前缀
- **跨类型编号**：可配置推论与定理共享连续编号
- **交叉引用**：`:numref:` 和 `:ref:` 引用定理编号
- **双主题**：标准彩色主题和简约边框主题
- **标题格式**：自定义标题显示模板
- **LaTeX支持**：完整LaTeX/PDF输出

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](concepts/index.md) |
| 💡 示例 | [示例代码](examples/index.md) |
| 📚 参考 | [源码参考](references/index.md) |
| 🔬 规格 | [事实清单](spec/facts.md) · [架构洞察](spec/insights.md) |

## 快速开始

```bash
pip install sphinx-proof
```

```python
# conf.py
extensions = ['sphinx_proof']
```

```rst
.. theorem:: 勾股定理
   :label: th-pythagoras

   在直角三角形中，:math:`a^2 + b^2 = c^2`。

.. proof::

   考虑边长为:math:`a+b`的正方形...
```

## 更新日志

见 [log.md](../log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
