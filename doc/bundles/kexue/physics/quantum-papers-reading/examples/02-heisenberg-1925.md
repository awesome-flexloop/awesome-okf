---
type: Example
title: 海森堡 1925 矩阵力学论文精读
description: '"Über quantentheoretische Umdeutung kinematischer und mechanischer Beziehungen" 德文原文精读——只用量子理论可解释量的纲领'
tags: [example, 海森堡, 矩阵力学, 德文]
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

# 海森堡 1925 矩阵力学论文精读

## 一、文本定位

- 底本：*Zeitschrift für Physik* 33, 879-893（1925 年 7 月 29 日收到，见姊妹束 facts F-045），PD。
- 权威英译：van der Waerden 编 *Sources of Quantum Mechanics*（1967，在版权）Paper 12——本束不引用其译文，德文原文为 PD 可直接引用。
- 语言：德文 Fraktur；注意论文中**没有"矩阵"（Matrix）一词**——"矩阵力学"之名来自 Born-Jordan 论文（*Z. Phys.* 34, 858）。

## 二、承前：纲领句

开篇第一段（德文，PD）：

> "In dieser Arbeit wird versucht, zu einer Begründung der quantentheoretischen Mechanik zu gelangen, die ausschließlich auf Beziehungen zwischen prinzipiell beobachtbaren Größen basiert."

中译示范：**"本工作尝试为量子理论力学寻求一种基础，它完全建立在原则上可观察量之间的关系之上。"**

**读这里要停一下**：这是物理学史上最著名的纲领句之一。"原则上可观察"（prinzipiell beobachtbar）排除了电子轨道（e. g. 轨道位置、周期），留下的只有辐射频率与强度——因此力学量必须用双下标 x(n,m) 重写。

## 三、精读：三步核心论证

### 第一步：频率重写（§1）

经典电动力学中电子运动分解为傅里叶级数，辐射频率为谐波倍数 ν = n·ω。玻尔理论中谱线频率却是 ν(n,m) = (E_n − E_m)/h——**不构成谐波序列**。海森堡宣布：把经典傅里叶级数的每一项换成以 ν(n,m) 为索引的"虚拟振子"集合。

### 第二步：数组乘法（§1 末-§2）

经典量相乘时傅里叶系数卷积：

$$c_k = \sum_{j} a_j b_{k-j}$$

换成 ν(n,m) 索引后自然变成双下标求和：

$$x y(n,m) = \sum_k x(n,k)\, y(k,m)$$

**这就是矩阵乘法**——海森堡注意到这种乘法"一般不可交换"（原文 "nicht kommutativ"），并把它作为量子化的代价接受。

### 第三步：量子条件与均匀性（§2 后半 + Born-Jordan 补全）

海森堡用经典轨道的"相位平均"替代式导出叠加关系（Thomas-Kuhn 求和规则雏形），但完整量子条件 pq − qp = ħ/i 由 Born 与 Jordan 在一个月后的论文给出（见 [facts.md](../facts.md) F-002）。

## 四、符号还原表

| 原文记号 | 现代对应 | 注 |
|---------|---------|-----|
| x(n,m) | 矩阵元 ⟨n|x̂|m⟩ | 双下标数组 |
| ν(n,m) | 跃迁频率 | 里茨组合原则 |
| R(n,m) | 辐射强度系数 | 振幅模方 |
| J | 经典作用量积分 | ∮p dq |
| W | 能量 | E |

## 五、历史定位

- 论文结尾承认"重大的困难"：与能量守恒、多自由度系统的普遍性尚待解决——这三项恰是 Born-Jordan 与三人论文（Dreimännerarbeit，*Z. Phys.* 35, 557）补全的内容。
- 可观察性纲领后来被批评为自我矛盾（海森堡自己很快在 1927 不确定性论文中引入不可直接观察的波函数振幅），但作为**构造策略**它是成功的。
- 现代教科书直接写矩阵力学，删去了"虚拟振子"的历史中介——精读的核心收获是看到双下标数组不是"突然发明矩阵"，而是从经典卷积强制演化出来的。

## 六、检查清单

1. 频率组合原理如何把经典傅里叶级数改写为 ν(n,m) 索引？
2. 数组乘法的不可交换性在哪里显现？
3. Born-Jordan 补全了什么？海森堡原文遗漏在哪？

## 相关文档

- [矩阵与波动力学形式对照](../concepts/01-formalisms.md)
- [薛定谔 1926 精读](03-schrodinger-1926.md)
