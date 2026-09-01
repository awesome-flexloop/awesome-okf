---
type: Example
title: 玻尔兹曼 1872 H 定理论文精读
description: '"Weitere Studien über das Wärmegleichgewicht unter Gasmolekülen" 德文原文精读——H 函数的构造与分子混沌假设的位置'
tags: [example, 玻尔兹曼, H定理, 德文, 统计力学]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T23:00:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-31T23:00:00+08:00" }
status: stable
stale_after: 2027-08-31
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
  - id: lang
    resource: /concepts/01-probability-language.md
    title: 概率论与统计语言
---

# 玻尔兹曼 1872 H 定理论文精读

## 一、文本定位

- 底本：Ludwig Boltzmann，"Weitere Studien über das Wärmegleichgewicht unter Gasmolekülen"，*Sitzungsberichte der Kaiserlichen Akademie der Wissenschaften (Wien)* IIa 66, 275-370（1872），PD。
- 后续：Maxwell 速度分布的一般化推导与 H 函数（原文记号 E，后由 Burbury 引入 H 记法传播）。
- 相关德文原版：玻尔兹曼《气体理论讲义》（1896-1898）PD，Brush 英译（1964）在版权（见姊妹束 facts F-028/F-029）。

## 二、承前：论文要解决什么

1860 年 Maxwell 给出平衡态速度分布，但**趋向平衡的过程**没有理论。玻尔兹曼 1872 的目标：证明任意初始分布经二元碰撞演化必然趋向 Maxwell 分布，并给出单调量。

## 三、精读：H 函数的构造

定义（原文思路，现代记号）：

$$H = \int f(v)\,\ln f(v)\,d^3v$$

（f 为速度分布函数；原文用 E 或直接写积分表达式，未用单一字母 H——H 记号是后起的。）

推导骨架：

1. 二元碰撞改变 f(v₁)f(v₂) → f(v₁')f(v₂')。
2. 碰撞的细致平衡由速度变换的雅可比与能量/动量守恒保证。
3. dH/dt ≤ 0，等号当且仅当 f 为 Maxwell 分布。

**读这里要停一下**：第 2 步"碰撞对在碰撞前无关联"（**Stosszahlansatz**，分子混沌）是 dH/dt ≤ 0 的真正源头——它把**时间箭头**从假设层面注入了时间对称的微观动力学。原文未把它标为独立假设，这正是 Loschmidt 1876 可逆性佯谬的攻击点。

## 四、与熵的连接

论文未直接说"H 就是负熵"。连接在 1877 年论文（配容计数）与《气体理论讲义》中逐步完成：

| 概念 | 1872 | 1877 | 现代 |
|------|------|------|------|
| 对象 | 连续分布 f | 离散配容 | 相空间分布 |
| 单调量 | H 递减 | 配容数 W 递增 | S = k ln W |

## 五、历史定位

- **可逆性佯谬**（Loschmidt 1876）：把所有分子速度反演，H 应当沿原路递增——微观可逆 vs 宏观不可逆。玻尔兹曼回应：H 单调是**概率性**陈述，不是力学定理。
- **复现佯谬**（Zermelo 1896）：庞加莱复现定理说有限系统近似回到初态。回应：复现时间远超宇宙年龄——"不可逆"是实践层面的必然。
- 《气体理论讲义》第二部分是这两场论战的系统总结（防御段，见 [方法论](../concepts/00-method.md)）。
- S = k log W 刻于维也纳墓碑，但该式为普朗克整理（见姊妹束 facts F-030）。

## 六、检查清单

1. dH/dt ≤ 0 的证明在哪一步用了分子混沌？
2. 1872 的 f 与 1877 的 W 是什么关系？
3. Loschmidt 佯谬为什么攻击不到 Maxwell 分布本身？
4. 为什么说"H 是概率性定理"？

## 相关文档

- [概率论与统计语言](../concepts/01-probability-language.md)
- [吉布斯 1902 精读](03-gibbs-1902.md)
