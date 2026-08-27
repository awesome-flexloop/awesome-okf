---
title: 一致性
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/convergence-rate
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/references/chapter6
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter6.md
---

# 一致性（Consistency）

一致性回答学习理论的终极问题：**当数据量趋于无穷时，学习算法是否收敛到 Bayes 最优分类器？** 它是对学习方法合法性的渐近检验。

## Bayes 最优与 Bayes 风险

给定后验概率 $\eta(x) = P(y=1|x)$，Bayes 最优分类器：

$$h^*(x) = \begin{cases} +1, & \eta(x) \geq 1/2 \\ -1, & \eta(x) < 1/2 \end{cases}$$

其风险 $R^* = R(h^*)$ 是所有可测函数能达到的最小风险，称为 **Bayes 风险**。

## 一致性定义

学习算法输出的分类器序列 $\{h_m\}$ 是**一致的**，若：

$$\lim_{m\to\infty} R(h_m) = R^*$$

注意这与"经验风险收敛到泛化风险"不同——后者是估计一致性，前者要求收敛到**最优**。

## 替代损失一致性（定理 6.1）

实践中常优化凸替代损失（如 hinge、logistic、指数损失）而非 0-1 损失。设替代风险为 $R_\phi$，其最优值为 $R_\phi^*$。若存在常数 $c$ 和 $s$，使得：

$$R(h_m) - R^* \leq 2c\sqrt[s]{R_\phi(h_m) - R_\phi^*}$$

则替代风险收敛 $R_\phi(\hat{f}_m) \to R_\phi^*$ 蕴含 Bayes 一致性 $R(\hat{f}_m) \to R^*$。

这为深度学习中用交叉熵等代理损失优化分类问题提供了理论基础。

## 划分机制一致性（定理 6.2）

以决策树/直方图分类为代表的非参数方法，将样本空间划分为区域 $\Omega(x)$，在区域内按多数类投票。一致性的两个充分条件：

1. **区域直径趋于零**（依概率）：
   $$\lim_{m\to\infty} \mathbb{P}(\text{Diam}(\Omega(x)) \geq \epsilon) = 0$$
2. **区域内样本数趋于无穷**（依概率）：
   $$\lim_{m\to\infty} \mathbb{P}(N(x) > N) = 1, \quad \forall N > 0$$

证明核心：用条件概率极大似然估计 $\hat{\eta}(x)$ 逼近真实后验 $\eta(x)$，再通过 $R(h_m) - R^* \leq 2\mathbb{E}[|\hat{\eta}(x) - \eta(x)|]$ 控制。

## 随机森林一致性（定理 6.5）

简化版随机森林（均匀随机划分，不依赖标签）的一致性证明要点：

1. 区域直径期望 $\mathbb{E}[\text{Diam}(\Omega)] \leq \sqrt{d}\,\mathbb{E}[L_j]$
2. 每次划分后属性边长期望乘以 $3/4$，故 $\mathbb{E}[L_j] \leq (1-1/(4d))^{T_m}$
3. 调和级数发散性 $\mathbb{E}[T_m] = \sum_{i=1}^k 1/i \to \infty$，保证划分次数 $T_m \to \infty$
4. 因此直径趋于零，结合样本数条件得一致性

## 依概率成立（Almost Sure）

一致性证明中频繁使用的概率论概念：

$$\lim_{n\to\infty} \mathbb{P}(|X_n - X| \geq \epsilon) = 0$$

这比逐点收敛弱——允许忽略概率趋于零的例外集合。

## 与其他概念的关系

- 收敛率：一致性只回答"是否收敛"，收敛率回答"多快收敛"
- 泛化界：有限样本的泛化保证是渐近一致性的非渐近版本
- 一致性是统计学习理论中 ERM 原则的基石（Vapnik-Chervonenkis 理论）

## 参见

- 第 6 章：一致性
