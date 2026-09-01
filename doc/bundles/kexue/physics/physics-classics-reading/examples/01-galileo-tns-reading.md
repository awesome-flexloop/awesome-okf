---
type: Example
title: 伽利略《两门新科学》第三日精读示范
description: 以第三日"自然加速运动"第1-2命题为例，演示对话体与比例论几何的读法——匀加速定义、落体定律推导与中文对照
tags: [example, 伽利略, 两门新科学, 精读示范, 对话体]
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

# 伽利略《两门新科学》第三日精读示范

本文以《两门新科学》（*Discorsi e Dimostrazioni Matematiche Intorno a Due Nuove Scienze*，1638）第三日"论自然加速运动"（De Motu Naturaliter Accelerato）的开篇命题为例，演示对话体与比例论几何的读法。

## 一、文本定位

- 原文：意大利文，1638 年 Leiden 出版；公有领域。
- 英译本：Crew & de Salvio，Macmillan 1914（PD），archive.org 全文（见 [信源总表](../references/01-primary-sources.md)）。
- 中译：武际可译，北京大学出版社 2006（在版权，不转述译文，本文引文为基于英译的中译示范）。

## 二、读法第一步：抓住定义的选择

第三日的结构是伽利略先给出匀加速运动的**定义**，再证明该定义与自由落体相容。关键文本（Crew-de Salvio 英译，PD）：

> "A motion is said to be equally or uniformly accelerated when, starting from rest, its momentum (celeritatis momenta) receives equal increments in equal times."

中译示范：**"任何运动，若从静止出发，在相等的时间内获得相等的速度增量，即称为匀加速运动。"**

读这里要停一下。伽利略借萨尔维亚蒂之口讨论过另一个候选定义：速度正比于已走过的距离（v ∝ s）。他选择了速度正比于时间（v ∝ t），理由之一是后者与"自由落体从很小高度落下时冲击力较小"的经验相容。这是一个**定义选择**，不是自明真理——教材通常直接把 v = at 写出来，跳过了这个论证。

## 三、读法第二步：跟随命题链（比例论几何）

定义之后是核心命题（Crew-de Salvio 英译，PD）：

> "The spaces described by a body falling from rest with a uniformly accelerated motion are to each other as the squares of the time-intervals employed in traversing these distances."

中译示范：**"由静止出发做匀加速运动的物体所通过的距离之比，等于通过各段距离所用时间间隔的平方之比。"**

这就是落体定律 s ∝ t²。伽利略的证明不用公式，用几何：线段 AB 表示时间，线上各点引出的平行线长度表示速度增长，由这些平行线围成的三角形面积等于"速度增量之和"；再用比例论把面积之比转化为距离之比。

**练习（翻译法）**：把这个几何证明用现代符号重写——速度 v = gt，距离 s = ½gt²，于是 s₁/s₂ = t₁²/t₂²。重写后回到图上，确认三角形面积对应 ½gt²。完成这一步，就掌握了比例论几何与现代公式的互换。

## 四、读法第三步：注意实验的位置

第三日还包含著名的斜面实验与"水钟"计时描述（用于验证时间平方律），但伽利略把实验放在论证之后，作为"自然确实采用这种加速"的确认，而非定义的来源。这与教材"由实验归纳定律"的叙述顺序相反——原文的顺序是：定义（可设想）→ 几何推论 → 实验确认。

## 五、对话体的读法提示

| 角色 | 作用 | 读者策略 |
|------|------|---------|
| 萨尔维亚蒂（Salviati） | 提出证明 | 主线论证跟随他 |
| 萨格雷多（Sagredo） | 聪明的提问者 | 他的疑问通常等于读者的疑问，重点读 |
| 辛普利西奥（Simplicio） | 亚里士多德立场的质疑者 | 他的反驳用来暴露旧观点的困难 |

对话中出现"等等，辛普利西奥，请你看……"这类段落，往往是全书论证最关键的转折。

## 六、检查清单

读完第三日开篇（定义 + 前两个命题 + 斜面实验段），应能用自己的话回答：

1. 伽利略为什么不把"速度正比于距离"作为匀加速定义？
2. s ∝ t² 是定义、推论还是实验结果？
3. 几何图中的三角形面积对应哪个物理量？
4. 水钟实验在论证链条中起什么作用？

回答不出第 2 题时，回读定义与命题之间的段落——这是第三日最容易被教材简化掉的结构。

## 相关文档

- [几何风格与代数风格](../concepts/05-geometric-reading.md)
- [为什么读物理学经典原文](../concepts/00-why-read-originals.md)
- [核心元典原文信源总表](../references/01-primary-sources.md)