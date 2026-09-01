---
type: Reference
title: 交叉引用
description: 中西数学对读知识包与库内知识包的交叉引用——两束逐主题对应索引与可视化/形式化/符号计算知识包
tags: [reference, 交叉引用, 库内导航, 对应索引]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-01T12:00:00+08:00" }
status: draft
stale_after: 2027-09-01
sources:
  - id: x-bundles-index
    resource: ../../index.md
    title: 知识包总索引
    author: org:awesome-okf-xs
---

# 交叉引用

本包是"比较整合层"，大量内容依赖既有两束。本篇给出**逐主题对应索引**：读本包任一概念前，可先定位两束中的源文档。

## 一、六大对读主题 × 两束对应文档

| 本包概念 | 西方侧（classics-reading） | 中国侧（suanjing-reading） |
|---------|---------------------------|---------------------------|
| [几何与度量](../concepts/03-geometry-measurement.md) | [古希腊几何：欧几里得、阿基米德](../../classics-reading/concepts/05-greek-geometry.md) | [周髀算经](../../../../guoxue/suanxue/suanjing-reading/concepts/06-zhoubi-suanjing.md)、[九章结构](../../../../guoxue/suanxue/suanjing-reading/concepts/03-jiuzhang-structure.md) |
| [数论与代数](../concepts/04-number-theory-algebra.md) | [希腊化数论：丢番图、帕普斯](../../classics-reading/concepts/06-hellenistic-number-theory.md)、[高斯《算术研究》](../../classics-reading/concepts/10-gauss-turn.md) | [九章核心术文](../../../../guoxue/suanxue/suanjing-reading/concepts/04-jiuzhang-key-methods.md)、[大衍求一/天元/四元](../../../../guoxue/suanxue/suanjing-reading/concepts/10-dayan-tianyuan-siyuan.md)、[物不知数与 CRT](../../../../guoxue/suanxue/suanjing-reading/examples/05-wuwuzhishu-crt.md) |
| [极限与无穷小](../concepts/05-limits-infinity.md) | [古希腊几何：阿基米德部分](../../classics-reading/concepts/05-greek-geometry.md) | [刘徽注](../../../../guoxue/suanxue/suanjing-reading/concepts/05-liuhui-commentary.md)、[割圆术与圆周率](../../../../guoxue/suanxue/suanjing-reading/examples/07-geyuan-pi.md)、[祖冲之父子](../../../../guoxue/suanxue/suanjing-reading/concepts/08-zu-chongzhi.md) |
| [符号化与抽象](../concepts/06-symbolization-abstraction.md) | [阿拉伯代数：花剌子米、海亚姆](../../classics-reading/concepts/07-islamic-algebra.md)、[17 世纪革命：笛卡尔](../../classics-reading/concepts/08-early-modern-17c.md) | [天元术/四元术](../../../../guoxue/suanxue/suanjing-reading/concepts/10-dayan-tianyuan-siyuan.md)、[筹算与记数](../../../../guoxue/suanxue/suanjing-reading/concepts/02-chousuan-numeration.md) |
| [公理化与算法化](../concepts/07-axiomatic-algorithmic.md) | [古希腊几何：原本体系](../../classics-reading/concepts/05-greek-geometry.md)、[严格化与基础](../../classics-reading/concepts/12-rigor-and-foundations.md) | [九章结构](../../../../guoxue/suanxue/suanjing-reading/concepts/03-jiuzhang-structure.md)、[中国数学特征](../../../../guoxue/suanxue/suanjing-reading/concepts/12-chinese-math-characteristics.md) |
| [接触与互鉴](../concepts/08-contact-mutual-learning.md) | [17 世纪革命](../../classics-reading/concepts/08-early-modern-17c.md) | [明清转型](../../../../guoxue/suanxue/suanjing-reading/concepts/11-ming-qing-transition.md) |

## 二、对读示范 × 两束对应示例

| 本包示例 | 既有束支撑文档 |
|---------|---------------|
| [勾股对读](../examples/01-pythagorean-comparison.md) | [classics-reading 欧几里得精读示范](../../classics-reading/examples/01-euclid-close-reading.md)（I.47 三层读法）、[suanjing-reading 勾股测量](../../../../guoxue/suanxue/suanjing-reading/examples/04-gougu-pythagoras.md) |
| [线性方程组对读](../examples/02-linear-systems-comparison.md) | [suanjing-reading 方程术与正负术](../../../../guoxue/suanxue/suanjing-reading/examples/03-fangcheng-negative.md) |
| [圆周率对读](../examples/03-pi-comparison.md) | [suanjing-reading 割圆术与圆周率](../../../../guoxue/suanxue/suanjing-reading/examples/07-geyuan-pi.md) |

## 三、技术知识包（现代工具复现古代计算）

| 库内知识包 | 路径 | 对读用途 |
|-----------|------|---------|
| SymPy 符号计算 | [jishu/data/pydata/sympy](../../../../jishu/data/pydata/sympy/index.md) | 用 `solve_linear_system` 复现方程术与高斯消元的等价性 |
| 3Blue1Brown / Manim | [jishu/viz/3b1b](../../../../jishu/viz/3b1b/index.md) | 勾股面积拼接与弦图出入相补的可视化动画素材 |
| Ψhē 数学形式化 | [zhexue/psi/psi-math](../../../../zhexue/psi/psi-math/index.md) | 公理化体系的形式化视角（欧氏公理组的现代重构） |
| KaTeX 数学排版 | [jishu/document/katex](../../../../jishu/document/katex/index.md) | 本包 LaTeX 公式的渲染支撑 |
| NumPy | [jishu/data/pydata/numpy](../../../../jishu/data/pydata/numpy/index.md) | 算筹布列的矩阵表示实验 |

## 四、域内相邻知识包

| 知识包 | 路径 | 对读关联 |
|-------|------|---------|
| 中西化学双线索 | [kexue/chemistry](../../../chemistry/index.md) | "中西双线索"组织范式的同域先例 |
| 中西物理学双线索 | [kexue/physics](../../../physics/index.md) | 元典对读的另一学科平行案例 |
| 国学·算学分组 | [guoxue/suanxue](../../../../guoxue/suanxue/index.md) | 中国算经束所在分组 |

外部资源（MacTutor 主题页、EMS Magazine 开放获取文章等）见 [comparative-studies.md](comparative-studies.md)。
