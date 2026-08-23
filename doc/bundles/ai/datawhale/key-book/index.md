---
title: 钥匙书 Key-book 知识束
type: index
bundle: key-book
description: 周志华等《机器学习理论导引》伴读笔记《钥匙书》的知识束，系统梳理理论机器学习七大支柱——可学性、计算复杂度、泛化界、稳定性、一致性、收敛率、遗憾界，涵盖 PAC 学习、VC 维、Rademacher 复杂度、算法稳定性、Bayes 一致性、优化收敛率、在线学习遗憾界等核心理论。
concepts:
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/concepts/computational-complexity
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/concepts/stability
  - /datawhale/key-book/concepts/consistency
  - /datawhale/key-book/concepts/convergence-rate
  - /datawhale/key-book/concepts/regret-bound
references:
  - /datawhale/key-book/references/chapter1
  - /datawhale/key-book/references/chapter2
  - /datawhale/key-book/references/chapter3
  - /datawhale/key-book/references/chapter4
  - /datawhale/key-book/references/chapter5
  - /datawhale/key-book/references/chapter6
  - /datawhale/key-book/references/chapter7
  - /datawhale/key-book/references/chapter8
  - /datawhale/key-book/references/appendix
examples:
  - /datawhale/key-book/examples/pac-3dnf
  - /datawhale/key-book/examples/vc-dimension-linear
  - /datawhale/key-book/examples/ucb-bandit
sources:
  - https://github.com/datawhalechina/key-book
---

# 钥匙书 Key-book 知识束

本知识束基于 Datawhale 开源项目 [《钥匙书 Key-book》](https://github.com/datawhalechina/key-book)，该项目是周志华、王魏、高尉、张利军所著《机器学习理论导引》（机械工业出版社，2020）的伴读笔记，提供概念解释、证明补充与案例分享。

## 七大理论支柱

理论机器学习围绕七个核心概念展开，构成"能否学 → 需多少 → 差多少 → 稳不稳 → 对不对 → 快不快 → 变不变"的完整判据链：

| 支柱 | 概念 | 核心问题 | 对应章节 |
|:---:|:---|:---|:---|
| 1 | [可学性](/ai/datawhale/key-book/concepts/learnability) | 问题能否从数据中被学习 | 第 2 章 |
| 2 | [计算复杂度](/ai/datawhale/key-book/concepts/computational-complexity) | 学习需要多少样本与时间 | 第 2、3 章 |
| 3 | [泛化界](/ai/datawhale/key-book/concepts/generalization-bound) | 经验误差与真实误差差距多大 | 第 4 章 |
| 4 | [稳定性](/ai/datawhale/key-book/concepts/stability) | 算法对样本扰动是否敏感 | 第 5 章 |
| 5 | [一致性](/ai/datawhale/key-book/concepts/consistency) | 数据无穷时是否收敛到 Bayes 最优 | 第 6 章 |
| 6 | [收敛率](/ai/datawhale/key-book/concepts/convergence-rate) | 优化算法以多快速度逼近最优 | 第 7 章 |
| 7 | [遗憾界](/ai/datawhale/key-book/concepts/regret-bound) | 在线序列决策的累积损失能否受控 | 第 8 章 |

## 三层分析框架

全书隐含"有限 → 无限"的递进线索：

1. **有限假设空间 + 有限样本**：Union Bound + Hoeffding 直接控制
2. **无限假设空间 + 有限样本**：VC 维 / Rademacher 复杂度 / 稳定性引入有效自由度
3. **无限样本渐近 + 非渐近速率**：一致性、收敛率、遗憾界回答极限与速度

## 章节导航

- [第 1 章：预备知识](/ai/datawhale/key-book/references/chapter1) — 集中不等式与分析工具库
- [第 2 章：可学性](/ai/datawhale/key-book/references/chapter2) — PAC 学习框架
- [第 3 章：复杂度](/ai/datawhale/key-book/references/chapter3) — VC 维、Natarajan 维、Rademacher 复杂度
- [第 4 章：泛化界](/ai/datawhale/key-book/references/chapter4) — 有限/无限假设空间泛化保证
- [第 5 章：稳定性](/ai/datawhale/key-book/references/chapter5) — 算法稳定性与泛化性
- [第 6 章：一致性](/ai/datawhale/key-book/references/chapter6) — 收敛到 Bayes 最优的条件
- [第 7 章：收敛率](/ai/datawhale/key-book/references/chapter7) — 确定性与随机优化
- [第 8 章：遗憾界](/ai/datawhale/key-book/references/chapter8) — 在线学习与赌博机
- [附录](/ai/datawhale/key-book/references/appendix) — 范数、凸分析、优化、概率论基础

## 核心洞察

详见 [spec/insights.md](spec/insights.md)：

1. 七大支柱构成完整判据链
2. 从有限到无限的三层分析框架递进
3. PAC 学习与统计学习理论在稳定性处统一
4. 离线 i.i.d. 到在线非平稳的范式转换
