---
type: Reference
title: 库内交叉引用
description: 算经阅读教程与 OKF 知识库内其他知识包的关联登记，含数学排版、符号计算、数学可视化与中国古典阅读教程等关联 bundle
tags: [reference, cross-ref, 交叉引用, 导航]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-30T10:15:00+08:00" }
status: stable
stale_after: 2027-08-30
---

# 库内交叉引用

本文件登记“算经阅读教程”与 OKF 知识库（doc/bundles/）内其他知识包的关联。阅读算经时遇到的数学公式渲染、符号验证、可视化问题，可顺藤摸瓜进入下列 bundle。

## 一、数学工具链关联

| 关联 bundle | 路径 | 关联点 |
|-----------|------|--------|
| KaTeX 数学排版 | [document/katex](../../../../jishu/document/katex/index.md) | 本知识包 examples/ 中的现代数学解读使用 LaTeX 公式（由 Sphinx + KaTeX 渲染）；想理解页面公式的渲染机制与语法，进入该 bundle |
| SymPy 符号计算 | [data/pydata/sympy](../../../../jishu/data/pydata/sympy/index.md) | 可用 SymPy 复现古算：解线性方程组（方程术）、大衍求一术（CRT）、开方术（数值求根）、割圆术迭代（π 逼近）；examples/ 各篇的“现代数学解读”均可作为 SymPy 练习素材 |
| Manim 数学动画 | [viz/3b1b/manim](../../../../jishu/viz/3b1b/manim/index.md) | 割圆术、重差测量、盈不足双假设、天元术消元等算法具有强几何/过程性，适合用 Manim 制作教学动画 |

## 二、思想域内关联

| 关联 bundle | 路径 | 关联点 |
|-----------|------|--------|
| 帛书《老子》阅读教程 | [think/laozi/boshu-reading](../../../laozi/boshu-reading/index.md) | 同属 think 域的中国古典阅读教程，与本 bundle 是“方法姊妹篇”：二者都采用“原文选读 + 白话解读 + 系统阅读计划”的教程结构；读算经前可参考其“怎么读古籍”的通用策略 |
| Ψhē 数学形式化 | [think/psi/psi-math](../../../../zhexue/psi/psi-math/index.md) | 同属 think 域数学主题的邻居，关注现代数学基础的形式化体系；与本 bundle 的古代算法传统构成“数学思想”的两端，可对照阅读 |

## 三、规范关联

| 关联 bundle | 路径 | 关联点 |
|-----------|------|--------|
| OKF 规范 | [meta/okf-spec](../../../../meta/okf-spec/index.md) | 本知识包遵循 OKF v0.2 格式（type frontmatter、concepts/examples/references 三层结构、toctree 导航）；格式疑问查该 bundle |

## 四、外部资源导航

外部在线信源见 [online-sources.md](online-sources.md)，点校本见 [core-editions.md](core-editions.md)，研究文献见 [modern-studies.md](modern-studies.md)。