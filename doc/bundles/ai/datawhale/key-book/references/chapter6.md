---
title: 第6章 一致性
type: reference
bundle: /datawhale/key-book
chapter: 6
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter6.md
---

# 第6章：一致性

> 来源：`docs/chapter6.md`，编辑：赵志民、王茂霖、詹好

本章研究训练数据趋于无穷时分类器是否收敛到 Bayes 最优，是[一致性](/ai/datawhale/key-book/concepts/consistency)概念的主体章节。

## 内容概要

### 6.1 泛化风险的无偏估计

- **泛化风险**：$R(f)=\mathbb{E}_{(x,y)\sim\mathcal{D}}[\mathbb{I}(yf(x)\leq 0)]$
- **经验风险**：$\hat{R}(f)=\frac{1}{m}\sum_{i=1}^m\mathbb{I}(y_if(x_i)\leq 0)$
- **无偏性证明**：i.i.d. 采样下每个样本期望相同，$\mathbb{E}[\hat{R}(f)]=R(f)$

### 6.2 替代函数一致性（定理 6.1）

实践优化凸替代损失 $\phi$（如 hinge、logistic），而非 0-1 损失。充分条件：

$$R(\hat{f}_m)-R^*\leq 2c\sqrt[s]{R_\phi(\hat{f}_m)-R_\phi^*}$$

当替代风险收敛到最优 $R_\phi(\hat{f}_m)\to R_\phi^*$ 时，0-1 风险也收敛到 Bayes 风险 $R(\hat{f}_m)\to R^*$。

这为"用交叉熵等代理损失训练分类器"提供了理论合法性。

### 6.3 划分机制方法

将样本空间划分为互不相容区域，区域内按多数类投票。典型例子是**决策树**——每个节点对应一次空间划分，剪枝即减少不必要划分。

与参数方法的区别：在泛函空间直接搜索，而非在参数空间搜索超平面。

### 6.4 依概率成立（Almost Sure）

概率论概念：

$$\lim_{n\to\infty}\mathbb{P}((Diam(\Omega)-0)\geq\epsilon)=0$$

比逐点收敛弱，允许忽略概率趋于 0 的例外集合。是一致性证明的核心收敛模式。

### 6.5 划分机制一致性（定理 6.2）

两个充分条件：
1. 区域直径依概率趋于 0：$\lim_{m\to\infty}\mathbb{P}(Diam(\Omega(x))\geq\epsilon)=0$
2. 区域内样本数依概率趋于无穷：$\lim_{m\to\infty}\mathbb{P}(N(x)>N)=1$

证明结构：
1. 定义条件概率极大似然估计 $\hat{\eta}(x)=\frac{1}{N(x)}\sum_{x_i\in\Omega(x)}\mathbb{I}(y_i=+1)$
2. 用 $\eta(x)$ 的连续性，直径趋于 0 时邻域内 $\bar{\eta}(x)\to\eta(x)$
3. 拆分 $N(x)=0$ 和 $N(x)>0$，利用引理 6.3 控制条件方差
4. 分情况 $N(x)\leq k$ 和 $N(x)>k$ 放缩
5. 由 $N(x)\to\infty$ 依概率，各项趋于 0
6. 最终 $R(h_m)-R^*\leq 2\mathbb{E}[|\hat{\eta}(x)-\eta(x)|]\to 0$

### 6.6 随机森林划分一致性（定理 6.5）

简化版随机森林（均匀随机划分，不依赖标签）的一致性证明：

1. 直径与边长关系：$Diam(\Omega)=\sqrt{\sum_j L_j^2}$
2. Jensen 不等式：$\mathbb{E}[\sqrt{\sum L_j^2}]\leq\sqrt{d\,\mathbb{E}[L_1^2]}$
3. 每次划分后边长期望乘以 $3/4$（$\max(U_i,1-U_i)$ 的期望）
4. 属性被划分次数 $K_j\sim B(T_m,1/d)$
5. $\mathbb{E}[L_j]\leq(1-1/(4d))^{T_m}$
6. 划分次数 $T_m=\sum\xi_i$，其中 $\xi_i\sim Bernoulli(1/i)$
7. 调和级数发散 $\mathbb{E}[T_m]=\sum 1/i\to\infty$，故 $T_m\to\infty$ 依概率
8. 因此直径趋于 0，结合样本数条件得一致性

## 理论定位

本章从有限样本泛化跨越到渐近分析。替代损失一致性是连接理论与工程实践的关键定理；划分机制一致性为决策树、随机森林等非参数方法提供了理论基础；随机森林证明展示了概率论工具（Jensen、Stirling、调和级数）在学习理论中的综合运用。

## 参见

- [第 7 章：收敛率](/ai/datawhale/key-book/references/chapter7)：一致性只回答"是否收敛"，收敛率回答"多快"
- [附录](/ai/datawhale/key-book/references/appendix)：凸函数、Jensen 不等式等数学基础
