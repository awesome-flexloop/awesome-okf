---
title: 可学性
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/computational-complexity
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/concepts/stability
  - /datawhale/key-book/references/chapter2
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter2.md
---

# 可学性（Learnability）

可学性回答机器学习理论的第一性问题：**一个任务是否能从有限数据中被学习？** 它将"学会"从模糊直觉转化为严格的数学定义。

## PAC 学习框架

Valiant（1984）提出的**概率近似正确**（Probably Approximately Correct, PAC）框架是可学性的形式化基础：

- **近似正确**：泛化误差 $R(h) = P_{(x,y)\sim\mathcal{D}}[h(x)\neq y] \leq \epsilon$
- **概率**：上述条件以至少 $1-\delta$ 的概率成立
- **有限样本**：样本量 $m \geq \text{poly}(1/\epsilon, 1/\delta, \text{size}(x), \text{size}(c))$

一个概念类 $\mathcal{C}$ 是**PAC 可学**的，当存在学习算法 $\mathfrak{L}$，对任意目标概念 $c\in\mathcal{C}$、任意分布 $\mathcal{D}$、任意 $0<\epsilon,\delta<1$，在观察到 $m$ 个独立同分布样本后，以至少 $1-\delta$ 概率输出 $R(h)\leq\epsilon$ 的假设。

## 关键区分

- **可分性 ≠ 可学性**：高斯核 SVM 能打散任意样本（可分），但从无限假设空间中找到正确映射可能计算不可行。
- **信息论可学 ≠ 高效可学**：3 项析取范式（3-DNF）信息论上可学，但在 $RP\neq NP$ 假设下不存在多项式时间 PAC 学习算法。
- **可表示 ≠ 可学会**：通用逼近定理保证神经网络能表示任意连续函数，但不保证有限数据下能通过优化找到该函数。

## 两种 PAC 模型

1. **恰当 PAC 可学**（proper PAC）：输出假设必须属于假设空间 $\mathcal{H}$
2. **不可知 PAC 可学**（agnostic PAC）：不要求目标概念在 $\mathcal{H}$ 中，只需 $R(h) - \min_{h'\in\mathcal{H}}R(h') \leq \epsilon$

## PAC-Bayes 扩展

PAC-Bayes 理论通过假设空间上的后验分布 $Q$（先验 $P$）给出泛化界：

$$\mathbb{E}_Q[L(h)] \leq \mathbb{E}_Q[\hat{L}(h)] + \sqrt{\frac{KL(Q\|P) + \ln\frac{1}{\delta} + \ln m + \ln 2}{2m-1}}$$

KL 散度惩罚后验偏离先验的程度，将贝叶斯方法与 PAC 框架统一。

## 与其他概念的关系

- [计算复杂度](/ai/datawhale/key-book/concepts/computational-complexity)决定 PAC 学习的样本与时间代价
- [泛化界](/ai/datawhale/key-book/concepts/generalization-bound)是 PAC 可学性的直接技术手段
- [稳定性](/ai/datawhale/key-book/concepts/stability)提供了不依赖假设空间计数的可学性判据（定理 5.4 证明稳定性与不可知 PAC 可学等价）

## 参见

- [第 2 章：可学性](/ai/datawhale/key-book/references/chapter2)
- [3-DNF 不可学案例](/ai/datawhale/key-book/examples/pac-3dnf)
