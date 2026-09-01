---
type: Concept
title: 符号的现代还原
description: 历史物理符号与现代记号的对照还原表——momenta、vis viva、calorique、Resonator、phase wave 等术语的精确翻译
tags: [concept, 符号还原, 物理术语]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T22:00:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-31T22:00:00+08:00" }
status: stable
stale_after: 2027-08-31
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
  - id: style
    resource: ../physics-classics-reading/concepts/05-geometric-reading.md
    title: 几何风格与代数风格（姊妹束）
---

# 符号的现代还原

原文中的每个术语都可能与现代教科书用法有偏差。下表收录本束精读示范涉及的高频术语，还原原则：**先看作者的定义，再看现代对应**。

## 术语还原表

| 原文术语 | 出处 | 作者定义（简述） | 现代对应 | 易错点 |
|---------|------|----------------|---------|--------|
| momentum (celeritatis) | 伽利略 TNS；惠更斯 | 速度的瞬时增量/瞬间值 | dv 或瞬时速度 v | 不是现代"动量" p=mv |
| vis viva（活力） | 莱布尼茨学派 | mv² | 2×动能 | 差常数因子 2 |
| vis centrifuga | 惠更斯《摆钟论》Part V | 离心力定理中的"离心努力" | mv²/r（向心加速度的反作用表述） | 惠更斯给出的是张力差而非矢量 |
| chute de calorique | 卡诺 1824 | 热质从高温到低温的"下落" | 温差驱动做功（但热非守恒量） | 卡诺热质说下"热量不变"，与现代 Q₁−Q₂=W 冲突 |
| puissance motrice | 卡诺 1824 | 动力（机械功） | 功 W | 不是"功率" |
| Resonator | 普朗克 1901 | 与辐射场平衡的单频振子 | 黑体腔壁振子（能量取平均值） | U 是平均能量，能级离散是假设步骤 |
| Elementargebiet / element | 普朗克 1901 | 能量复分的小份 ε | 能量子 hν 的前身 | ε 复分数按组合计数，ν 依赖后来才显式化 |
| phase wave / onde de phase | 德布罗意 1924 | 与运动粒子相谐的波 | 物质波 ψ（的非相对论极限） | 德布罗意推导用的是相对论框架 |
| induction（electrical） | 法拉第 ERE I | 邻近带电体引起的电状态 | 电磁感应/静电感应（依上下文） | Series I 的 induction 是电流感应 |
| magnetic curves / lines of force | 法拉第 | 力线的物理实在 | 磁场线 B | 法拉第把场线当实体，不是几何辅助 |
| ensemble | 吉布斯 1902 | 大量相同宏观约束系统的虚构集合 | 系综（同义保留） | 吉布斯定义即现代定义，术语直接沿用 |
| index of probability | 吉布斯 1902 | 概率的对数 | ln ρ（相空间密度对数） | 吉布斯的"index"是指数/对数义，不是指标 |

## 还原操作三步

1. **找定义**：原作者在首次使用术语处几乎都给定义（惠更斯在《摆钟论》Part IV 定义"摆动中心"；吉布斯在 Chap. IV 定义 ensemble）。先抄定义，不猜。
2. **量纲核对**：把作者公式两边按现代单位量纲核对，可以迅速暴露"差常数因子"类偏差（vis viva 差 2、普朗克 ε 与 hν 的关系）。
3. **回推一道**：用作者符号重推其结论，再翻译成现代符号重推一遍。两次结果不一致时，差异处就是概念演变点——在精读笔记中显式标注。

## 一个完整例子：普朗克的复分

普朗克 1901 论文 §2 把 N 个共振器的总能量 U_N 复分为 P 个等份 ε，组合计数给出熵：

$$S_N = k \ln \frac{(N+P-1)!}{N! (P-1)!}$$

现代视角的还原链条：等份 ε → ε = hν（同一论文后文引入）→ 大数极限 → 维恩位移约束 → 黑体谱公式。跳过"等份复分"直接写 E = nhν，就跳过了"组合计数"这一让普朗克本人都觉得"孤注一掷"（Akt der Verzweiflung）的论证核心。

## 相关文档

- 版本与段落定位：[原文校勘入门](01-textual-criticism.md)。
- 历史语境：[文本的历史定位](03-historical-positioning.md)。
