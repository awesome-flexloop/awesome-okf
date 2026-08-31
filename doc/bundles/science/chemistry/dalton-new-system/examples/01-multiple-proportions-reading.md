---
type: Example
title: 倍比定律段落逐句精读
description: 以碳的两种氧化物为案例，对道尔顿 1808 年原子量表数据与化合规则原文做逐句精读：原文→今译→注释→用现代原子量复算，演示倍比定律的发现逻辑
tags: [example, 倍比定律, 逐句精读, 原子量, 复算, 道尔顿]
generated: { by: "agent:seven-concepts-r-e", at: "2026-08-30T00:00:00+08:00" }
status: draft
stale_after: 2027-08-30
sources:
  - id: original-sources
    resource: /references/original-sources.md
    title: 原著与公版原文信源
  - id: modern-scholarship
    resource: /references/modern-scholarship.md
    title: 现代学术研究信源
---

## 倍比定律段落逐句精读

本篇用"解剖麻雀"的方式读一个完整案例：道尔顿如何从碳的两种氧化物数据中读出倍比定律。读法分四步：**原文 → 今译 → 注释 → 现代复算**。建议拿纸笔跟着算一遍。

## 第一步：原文（1808 年原子量表与规则句）

1808 年《化学哲学新体系》第三章原子量表中，与本案相关的条目为[^1]：

| 原书条目 | 道尔顿给出的相对重量 |
|---------|--------------------|
| Carbone（碳） | 5 |
| Oxygen（氧） | 7 |
| Carbonic oxide（一氧化碳） | 12 |
| Carbonic acid（碳酸气＝二氧化碳） | 19 |

同章化合规则原文：

> "When only one combination of two bodies can be obtained, it must be presumed to be a binary one."（两种物体若只能得到一种化合物，必须假定它是二元的。）

以及化合等级句：

> "1 atom of A + 1 atom of B = 1 atom of C, binary. 1 atom of A + 2 atoms of B = 1 atom of D, ternary."

## 第二步：今译与逐行解读

**表格部分**：碳的原子重量定为 5，氧定为 7（均以氢＝1 为基准）。碳的"低度氧化物"carbonic oxide 重 12，"高度氧化物"carbonic acid 重 19。

**规则句解读**：碳与氧已知有两种化合物，不适用"唯一即二元"的推定；道尔顿把较少见的 carbonic oxide 定为二元（1 碳 + 1 氧），把 carbonic acid 定为三元（1 碳 + 2 氧）。

**验算道尔顿自己的数字**：

- carbonic oxide = 碳 5 + 氧 7 = 12 ✓ 与表中值一致；
- carbonic acid = 碳 5 + 氧 7×2 = 19 ✓ 与表中值一致。

## 第三步：注释

| 原书用词 | 现代对应 | 说明 |
|---------|---------|------|
| carbonic oxide | 一氧化碳 CO | 碳在氧气不足时燃烧的产物，有毒 |
| carbonic acid | 二氧化碳 CO₂ | 当时称"碳酸气"，溶于水显酸性 |
| binary / ternary | 二元 / 三元 | 1A+1B / 1A+2B 或 2A+1B |
| presumed | 被假定 | 道尔顿明言这是假设，不是实测 |

关键背景：当时的实验只能测定化合物中元素的**重量百分比**（例如测得碳酸气中碳占约 27%、氧占约 73%），无法直接数出原子个数。道尔顿用化合规则补上"个数"这一环，才把重量比换算成原子量比。

## 第四步：现代复算

用现代相对原子质量（C ≈ 12，O ≈ 16）重新检验：

**1. 道尔顿的组成判断对不对？**

- 一氧化碳 CO：1 碳 + 1 氧 —— 二元，道尔顿判断正确；
- 二氧化碳 CO₂：1 碳 + 2 氧 —— 三元，道尔顿判断正确。

在这个案例里，道尔顿的组成假设恰好成立，这也是倍比定律最早被确认的案例之一。

**2. 倍比定律的定量验证**

取等量的碳（比如 12 份重）：

- 在 CO 中，与 12 份碳结合的氧为 16 份；
- 在 CO₂ 中，与 12 份碳结合的氧为 32 份；
- 氧的重量比 = 16 : 32 = **1 : 2**，简单整数比。

用道尔顿自己的数字同样成立：等量碳（5 份）对应的氧分别为 7 与 14，比为 7 : 14 = **1 : 2**。

**3. 道尔顿的原子量错在哪里？**

道尔顿定氧＝7（现代约 16）、碳＝5（现代约 12），偏差来自水的组成：他把水定为 HO（实为 H₂O），氧原子量少算了一半多；碳值又经含氧化合物间接传递误差。但值得注意的是：**原子量数值错了，倍比定律的整数比关系依然成立**——因为倍比只依赖原子个数比，不依赖原子量绝对值。这正是"定量预言可以独立于具体数值误差而生效"的漂亮例子。

## 延伸练习

用同样方法检验道尔顿表中的两种烃（答案见[原子量与最大简单性规则](../concepts/03-atomic-weights.md)）：

- olefiant gas（油气＝乙烯）：道尔顿作 1 碳 + 1 氢，重 6；
- carburetted hydrogen（碳化氢＝甲烷）：道尔顿作 1 碳 + 2 氢，重 7。

思考题：用现代化学式 C₂H₄ 与 CH₄ 计算，与等量碳结合的氢重量比是多少？道尔顿的数字给出的比值又是多少？两个比值为何方向相反但同样是简单整数比？

## 相关文档

- [原子量与最大简单性规则](../concepts/03-atomic-weights.md) — 规则与表格的系统讲解
- [核心段落选读](../concepts/04-key-passages.md) — 规则句原文出处
- [原典阅读路线](02-reading-route.md) — 到原书表格页的导航
- [影响、证实与遗产](../concepts/05-legacy.md) — 倍比定律在原子论接受史中的角色

[^1]: 道尔顿《化学哲学新体系》1808 年版第三章原子量表，公版摘录见 [Giunta, Classic Chemistry: Dalton](../references/original-sources.md)；定律叙述另见 [John Dalton — Encyclopaedia Britannica](https://www.britannica.com/biography/John-Dalton)，访问日期 2026-08-30。