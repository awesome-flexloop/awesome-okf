---
type: Example
title: 牛顿《原理》第三卷精读示范
description: 以第三卷"哲学中的推理规则"与现象→命题结构为例，演示体系专著的读法——规则、现象、命题的论证链条与坐标
tags: [example, 牛顿, 自然哲学的数学原理, 精读示范, 综合几何]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:30:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-30T10:30:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
  - id: primary
    resource: /references/01-primary-sources.md
    title: 核心元典原文信源总表
  - id: concept-style
    resource: /concepts/05-geometric-reading.md
    title: 几何风格与代数风格
---

# 牛顿《原理》第三卷精读示范

本文以《自然哲学的数学原理》（*Philosophiæ Naturalis Principia Mathematica*，1687）第三卷的方法论开篇与命题结构为例，演示体系专著的读法。

## 一、文本定位

- 拉丁原版 1687；二版 1713（加入"总释"）；三版 1726。公有领域。
- Motte 1729 英译本（PD；Gutenberg #76404 为 1846 编本）；Cohen-Whitman 1999 新译（在版权，见 [信源总表](../references/01-primary-sources.md)）。
- 建议入门顺序：第三卷"推理规则"→ 现象 → 命题，而非从第一卷开头读起。

## 二、读法第一步：先读"哲学中的推理规则"

第三卷开篇的四条 *Regulae Philosophandi* 是全书方法论：规则 I、II 在 1687 年初版中已有（初版置于“假说”条目之下），规则 III 为 1713 年二版新增，规则 IV 为 1726 年三版新增，四条最终定型于三版。Motte 1846 英译（公有领域）：

> "We are to admit no more causes of natural things than such as are both true and sufficient to explain their appearances."（规则 I，经济原则）

中译示范：**"除那些真实且足以解释自然事物现象的原因之外，不应承认更多的原因。"**

> "Therefore to the same natural effects we must, as far as possible, assign the same causes."（规则 II，齐一性）

中译示范：**"因此，对于同样的自然结果，必须尽可能赋予同样的原因。"**

这四条规则是第三卷"天地统一"论证的逻辑授权：如果下落苹果与绕行月球受同样平方反比力支配（规则 II），那么第一卷证明的轨道力学可以直接用于天体。

## 三、读法第二步：看清"现象 → 命题"的论证链

第三卷的结构不同于第一卷（纯数学），每一步都对着观测数据：

| 环节 | 内容 | 读者任务 |
|------|------|---------|
| 现象（Phaenomena）I-VI | 开普勒定律在行星与卫星系统中的观测陈述（周期 ∝ 半径^3/2 等） | 把每条现象标为"观测事实输入" |
| 命题 I-III | 由现象 + 第一卷命题反推：木星/土星卫星受指向母行星的向心力、行星受指向太阳的向心力，均按平方反比衰减 | 对照第一卷命题 1-3、11-13 |
| 命题 IV | 月球检验：月球向心加速度与地面 g 的反平方外推一致 | 建议手算：g/3600 ≈ 月球向心加速度 |
| 命题 VII-VIII | 万有引力：一切物体相互吸引，引力与质量乘积成正比 | 注意"质量"概念在这里被精确化 |

月球检验（命题 IV）是全书最动人的段落之一：把 g 按反平方律外推到月球轨道距离（约 60 个地球半径，故缩小 3600 倍），得到的加速度与月球轨道运动所需向心加速度吻合——地面力学与天体力学在此定量对接。

## 四、读法第三步：几何证明卡住时的现代对照

第一卷命题 11（"由椭圆运动推出平方反比力"）的几何证明是最著名的硬骨头。读法：

1. 先记住命题的输入（椭圆焦点轨道）与输出（力 ∝ 1/r²）。
2. 几何证明读不下去时，用现代方法重解：椭圆轨道 r = p/(1+e cosθ)，比耐公式给出中心力 F ∝ 1/r²。
3. Chandrasekhar《Newton's Principia for the Common Reader》对该命题有逐行现代重解（在版权，图书馆借阅）。
4. 回到原文确认牛顿用了哪些引理（尤其引理 12，椭圆切线/直径性质）。

目标不是独立完成几何证明，而是看清**论证链条不依赖现代符号也成立**。

## 五、版本提醒

- "总释"（General Scholium，含 "Hypotheses non fingo"——"我不杜撰假说"）是 1713 年二版才加入的，读 1687 结构时不要误置。
- Motte 译本与 Cohen-Whitman 译本在术语上有差别（如 "quantity of matter" = 质量），引用时标注译本与版次，方法见 [版本与译本甄别](../concepts/03-versions-translations.md)。

## 六、检查清单

1. 四条推理规则中，哪一条直接授权"苹果与月球同因"？
2. 第三卷的"现象"是理论推导还是观测陈述？
3. 月球检验中 3600 这个数字从哪来？
4. 命题 11 的输入和输出分别是什么？

## 相关文档

- [几何风格与代数风格](../concepts/05-geometric-reading.md)
- [论文阅读法](../concepts/06-paper-reading.md)
- [权威解读资源](../references/02-interpretations.md)