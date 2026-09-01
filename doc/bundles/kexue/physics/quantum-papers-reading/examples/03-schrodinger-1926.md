---
type: Example
title: 薛定谔 1926 波动力学论文精读
description: '"Quantisierung als Eigenwertproblem"（第一篇）德文原文精读——从哈密顿变分问题到本征值问题的替换'
tags: [example, 薛定谔, 波动力学, 德文]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T22:30:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-31T22:30:00+08:00" }
status: stable
stale_after: 2027-08-31
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
  - id: formalisms
    resource: /concepts/01-formalisms.md
    title: 形式对照
---

# 薛定谔 1926 波动力学论文精读（第一篇）

## 一、文本定位

- 底本：*Annalen der Physik* 第 4 辑 vol. 79, 361-376 页（1926-01-27 收到），PD。
- 德文合集 *Abhandlungen zur Wellenmechanik*（1928）与英译 *Collected Papers on Wave Mechanics*（Shearer & Deans 译，1928，美国 PD）均可用（见姊妹束 facts F-052/F-053）。
- 本篇精读四部曲之第一篇：氢原子的本征值问题。

## 二、承前：纲领句

> "Die zunächst hier vorgetragene Gedankenkette ist gewissermassen eine Umbildung und Kritik der Herrn de Broglie vorgeschlagenen These von den 'Phasenwellen'..."

中译示范：**"本文首先提出的思路链，可以说是对德布罗意先生'相位波'论题的一种改造与批判……"**

紧随其后的替换宣言（大意）：

**"我们不把量子化规则本身当作首要的，而是把它替换为另一种要求——某个空间函数的（自然的）单值性要求。"**

**读这里要停一下**：薛定谔的策略是"形式替换"：抛弃量子条件的特设性（quantum condition as postulate），让分立谱作为**边值问题的自然产物**出现。这与海森堡"可观察性"纲领完全不同的正当性路线（见 [形式对照](../concepts/01-formalisms.md)）。

## 三、精读：哈密顿类比的核心推导

第一篇论文的骨架：

1. **变分问题**：把经典的雅可比-哈密顿方程的"作用量函数" S 改写为 Ψ = K·log S，要求变分积分
$$\int\!\!\int \left[q\,\Psi^2 + \sum \frac{\partial \Psi}{\partial x_i}^2 \right] dx\,dy\,dz$$
取极值（q 为势能相关系数）。
2. **欧拉方程**：得到与德布罗意相位波一致的偏微分方程。
3. **氢原子求解**：分离变量（球坐标），径向方程的解在原点与无穷远的**单值、有限、平方可积**条件迫使参数取分立值——里德伯公式再现。
4. **E = hn 诠释**：本征值差给出光谱频率。

现代对照：从 −(ℏ²/2m)∇²Ψ + VΨ = EΨ 出发一步求解氢原子；薛定谔的变分进路在现代表述中被算符代数取代，但"分立谱=边值条件"的洞察原样保留。

## 四、符号还原表

| 原文记号 | 现代对应 | 注 |
|---------|---------|-----|
| Ψ | 波函数 | 论文首篇尚未赋予概率诠释 |
| K | 归一常数 | Ψ = K log S 的标度 |
| E | 本征值 | 定态能量 |
| S | 哈密顿作用量函数 | 与 Ψ 经对数关系连接 |
| a₀ | 氢原子半径参数 | 玻尔第一轨道半径 |

## 五、历史定位

- 论文开篇就引用德布罗意并称"改造与批判"——薛定谔 1924 年即读过德布罗意博士论文（HAL 全文，见 [原文精读束信源](../../physics-original-text-reading/references/01-sources.md)）。
- 概率诠释的缺位：第一篇论文把 Ψ 当"过程的真实描述"（与 later Born 诠释对立）；玻恩 1926 年才给出统计诠释。
- 现代教材的氢原子解跳过变分出发点——精读收获是看到"量子化条件 → 单值性要求"这一**正当性转移**。

## 六、检查清单

1. 薛定谔用什么替换量子化规则？为什么说这是"正当性转移"？
2. 分立谱在推导的哪一步出现？
3. 第一篇论文中 Ψ 的诠释与现代的差别？
4. 哈密顿类比（几何光学/波动光学）在论文哪里出现？

## 相关文档

- [玻尔 1913 精读](01-bohr-1913.md)（被替换的量子条件）
- [海森堡 1925 精读](02-heisenberg-1925.md)（竞争形式）
