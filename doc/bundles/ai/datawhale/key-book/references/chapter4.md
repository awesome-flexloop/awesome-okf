---
title: 第4章 泛化界
type: reference
bundle: /datawhale/key-book
chapter: 4
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter4.md
---

# 第4章：泛化界

> 来源：`docs/chapter4.md`，编辑：赵志民、李一飞、王茂霖、詹好

本章系统推导有限和无限假设空间的泛化误差界，是[泛化界](/ai/datawhale/key-book/concepts/generalization-bound)概念的主体章节。

## 内容概要

### 4.1 可分情形中的"等效"假设

- 机器学习是**不适定问题**（ill-posed）：解不唯一（训练数据无法覆盖所有情况）
- 正则化通过引入额外约束解决不适定性

### 4.2 定理 4.1 与 PAC 定理的关系

- **定理 2.1**：PAC 辨识定义
- **定理 2.2**：PAC 可学的样本复杂度条件
- **定理 4.1**：逆向使用定理 2.1/2.2，从样本量下界推导泛化保证
- 三者形成"定义→条件→结论"的闭环

### 4.3 有限假设空间泛化界（定理 4.2）

补充式 (4.6)→(4.7) 的省略推导：
1. 存在性概率展开为各假设概率的并集
2. Union Bound 放缩为概率之和
3. Hoeffding 不等式（引理 2.1）控制单假设偏差
4. 令 $2\exp(-2m\epsilon^2)=\delta/|\mathcal{H}|$ 反解 $\epsilon$

### 4.4 无限假设空间：对称化（引理 4.1）

当 $m\geq 2/\epsilon^2$ 时：

$$\mathbb{P}(|R(h)-\hat{R}_S(h)|>\epsilon)\leq 4\Pi_{\mathcal{H}}(2m)\exp\left(-\frac{m\epsilon^2}{8}\right)$$

证明两步走：
1. 用 Ghost 样本集 $S'$ 将泛化-经验差距转化为两个经验差距
2. 用增长函数控制对分数量，置换论证 + Hoeffding 得指数界

### 4.5 VC 维泛化界（定理 4.3）

代入 Sauer 引理 $\Pi_{\mathcal{H}}(2m)\leq(2em/d)^d$：

$$\mathbb{P}\left(|R(h)-\hat{R}(h)|>\sqrt{\frac{8d\ln\frac{2em}{d}+8\ln\frac{4}{\delta}}{m}}\right)\leq\delta$$

收敛率 $O(\sqrt{d\ln(m/d)/m})$：$m/d$ 越大泛化越好。

### 4.6 Rademacher 复杂度回顾

- VC 维与数据分布无关 → 界"松"
- Rademacher 复杂度基于数据分布 → 界"紧"
- 经验 Rademacher 复杂度与 Rademacher 复杂度的关系如同观测序列与随机变量

### 4.7 泛化下界（定理 4.6、4.7）

- **定理 4.6**：可分情形下存在分布使泛化误差以常数概率 $\geq (d-1)/(32m)$
- **定理 4.7**：不可分情形下任意算法存在"坏"分布使泛化误差为 $O(\sqrt{d/m})$
- 证明通过两枚不均匀硬币的决策问题，利用 Slud 不等式和正态分布不等式
- **No Free Lunch**：不存在万能学习算法，泛化保证依赖假设空间结构

### 4.8–4.11 间隔泛化界

- **引理 4.2**：二硬币决策问题的最小误差下界
- **引理 4.6/4.7**：泛化下界的详细推导，含四次启发式限制
- **$\rho$-间隔损失的 Lipschitz 性**：$|\Phi_\rho(x_1)-\Phi_\rho(x_2)|\leq(1/\rho)|x_1-x_2|$
- **定理 4.8**：SVM 间隔泛化界，结合 Rademacher 复杂度 + Lipschitz 性质

## 理论定位

本章展示了从有限到无限假设空间的泛化分析方法论跃迁：Union Bound → 对称化 + 增长函数 → VC 维 → Rademacher 复杂度。泛化上界与下界共同界定了学习的可能性边界，是 PAC 可学性的技术核心。

## 参见

- [第 3 章：复杂性分析](/ai/datawhale/key-book/references/chapter3)：VC 维与 Rademacher 复杂度的定义
- [第 5 章：稳定性](/ai/datawhale/key-book/references/chapter5)：算法依赖的替代泛化保证
