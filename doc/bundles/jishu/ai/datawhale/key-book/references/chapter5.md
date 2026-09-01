---
title: 第5章 稳定性
type: reference
bundle: /datawhale/key-book
chapter: 5
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter5.md
---

# 第5章：稳定性

> 来源：`docs/chapter5.md`，编辑：赵志民、李一飞、王茂霖、詹好

本章从算法性质出发推导泛化保证，是稳定性概念的主体章节，也是 PAC 学习与统计学习理论统一的关键。

## 内容概要

### 5.1 留一交叉验证风险

留一风险（leave-one-out risk）：依次移除一个数据点，用剩余数据训练的模型在被移除点上的风险。保证测试数据不包含在训练集中，类似模型选择时的留一验证。

### 5.2 均匀稳定性与泛化误差上界（定理 5.1）

**β-均匀稳定性**：替换任意样本后损失变化不超过 β。

证明思路：
1. 定义 $\Phi(D)=R(\mathfrak{L}_D)-\hat{R}(\mathfrak{L}_D)$（泛化-经验风险差距）
2. 由 β-稳定性，替换一个样本后 $|\Phi(D)-\Phi(D^{i,z'_i})|\leq 2\beta+M/m$（差有界性）
3. 应用 **McDiarmid 不等式**：
   $$\mathbb{P}(\Phi(D)\geq\mathbb{E}[\Phi(D)]+\epsilon)\leq\exp\left(\frac{-2m\epsilon^2}{(2m\beta+M)^2}\right)$$
4. 简单放缩得泛化风险上界：
   $$\mathbb{P}(R(\mathfrak{L}_D)-\hat{R}(\mathfrak{L}_D)\geq\beta+\epsilon)\leq\exp\left(\frac{-2m\epsilon^2}{(2m\beta+M)^2}\right)$$

关键省略步骤补充：$\frac{M}{m}+\frac{m-1}{m}\beta\leq\frac{M}{m}+\beta$（$m$ 大时 $\beta/m$ 可忽略）。

### 5.3 假设稳定性与泛化误差上界（定理 5.2）

假设稳定性是较弱条件（仅控制期望，非概率），因此只能得到平方平均界，不涉及置信度。证明中利用 i.i.d. 性质任意交换样本下标。

### 5.4 过拟合与欠拟合

- 经验风险与泛化风险差距大 → 过拟合
- 泛化风险与经验风险差距大 → 欠拟合
- 稳定算法通过限制单样本影响防止过拟合

### 5.5 稳定性与可学习性（定理 5.4）

核心结果：**β-均匀稳定性 + ERM ⇒ 不可知 PAC 可学**。

证明结构：
1. 稳定性给出泛化上界（取 $\beta=1/m$）：
   $$R(\mathfrak{L}_D)-\hat{R}(\mathfrak{L}_D)\leq\frac{1}{m}+(2+M)\sqrt{\frac{\ln(1/\delta)}{2m}}$$
2. ERM 性质：$\hat{R}(\mathfrak{L}_D)\leq\hat{R}(h^*)$
3. Hoeffding 控制最优假设：$\hat{R}(h^*)-R(h^*)\leq M\sqrt{\ln(1/\delta)/(2m)}$
4. 合并得 $R(\mathfrak{L}_D)-R(h^*)\leq O(\sqrt{\ln(1/\delta)/m})$
5. 反解样本复杂度 $m=O((1/\epsilon^2)\ln(1/\delta))$

这建立了稳定性与可学性的等价关系，将计算学习理论与统计学习理论统一。

### 5.6 二次分布下 k-近邻稳定性（引理 5.2）

对 $X\sim B(k,1/2)$：

$$\mathbb{P}(|X-k/2|\leq a/2)<\frac{2\sqrt{2}a}{\sqrt{\pi k}}$$

利用 Stirling 公式近似二项式最大项，分奇偶讨论。

### 5.7 稳定性理论的适用范围

三个重要限制：
1. **顺序无关假设**：输出函数与训练集顺序无关。SGD 因顺序影响输出，不适用。
2. **分布一致性**：训练分布需与真实分布一致，数据/概念漂移时不成立。
3. **稳定性 vs 可塑性**：在线学习要求适应新数据（可塑性），与稳定性根本冲突——这引出第 8 章的遗憾界。

## 理论定位

本章开辟了不依赖假设空间计数的泛化分析路径。McDiarmid 不等式是连接算法稳定性与泛化性的数学桥梁，定理 5.4 则揭示了稳定性作为可学性充分必要条件的深刻地位。

## 参见

- 第 4 章：泛化界：VC 维路径的泛化分析
- 第 8 章：遗憾界：在线学习中稳定性与可塑性的张力
