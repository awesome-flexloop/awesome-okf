---
type: Concept
title: 概率论与统计语言
description: 从玻尔兹曼的 Stellungswahrscheinlichkeit 到吉布斯的 ensemble 的语言迁移——德文概率术语还原表
tags: [concept, 概率论, 统计语言, 术语还原]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T23:00:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-31T23:00:00+08:00" }
status: stable
stale_after: 2027-08-31
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
---

# 概率论与统计语言

## 一、德文概率术语还原表

| 德文术语 | 出处 | 直译 | 现代对应 |
|---------|------|------|---------|
| Stellungswahrscheinlichkeit | 玻尔兹曼 1877/1872 | 位置（配容）概率 | 微观态数 W |
| wahrscheinlichster Zustand | 玻尔兹曼 | 最概然态 | 平衡态（most probable） |
| Complexionen | 玻尔兹曼 1877 | 配容（组合） | 微观态 |
| Stosszahlansatz | 玻尔兹曼 H 定理传统 | 碰撞数假设 | 分子混沌（molecular chaos） |
| Monode / Ergode | 玻尔兹曼 1884 | 单系/遍历系 | 微正则系综的早期名 |
| index of probability | 吉布斯 1902 | 概率指数 | ln ρ |
| modulus | 吉布斯 1902 | 模量 | kT（正则分布参数） |

## 二、从计数到系综：两次抽象

1. **玻尔兹曼 1872→1877**：从连续分布的 H 函数转向**离散配容计数**（Combinationslehne 组合学），S ∝ log W 的雏形出现——把"分布"理解为"可数的配容集合"。
2. **吉布斯 1902**：不数真实分子，数**虚构副本**（ensemble）——把统计对象从"系统内粒子"升维到"系统副本"。系综分布函数 ρ 在相空间演化，熵是 ln ρ 的相空间积分。

**读这里要停一下**：吉布斯的"population"（总体）与玻尔兹曼的"unendliche Schar"（无限群）是不同的虚构——前者是相空间中的分布，后者是同一时刻的粒子集合。混用两者会把系综理论读成分子运动论。

## 三、 Ergodicity 的词源与误区

- "Ergode"（玻尔兹曼 1884）由 ergon（功）+ eidos（类）构成，本义"能量固定的类"。
- "Ergodic hypothesis"（遍历假设）的现代严格化（准遍历性）与 19 世纪表述强度不同；精读 1902 前的文本时不把现代遍历理论读入。

## 四、普朗克的整理者角色

S = k log W 作为"玻尔兹曼熵公式"的标准形式由普朗克在 1900-1901 论文与讲义中固定（k 也因此得名玻尔兹曼-普朗克常数）；玻尔兹曼本人从未写下此式（见姊妹束 facts F-030）。精读玻尔兹曼原文时应按 H 函数与配容计数读，不按"公式"读。

## 相关文档

- [热统经典精读方法论](00-method.md)
- 姊妹束 [符号的现代还原](../../physics-original-text-reading/concepts/02-symbol-restoration.md)
