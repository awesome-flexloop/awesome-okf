---
type: example
title: "SVM 对偶问题推导"
bundle: /datawhale/pumpkin-book
description: "间隔最大化原问题到拉格朗日对偶问题的完整推导链路，KKT条件与支持向量识别"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter6/chapter6.md
related:
  - /datawhale/pumpkin-book/concepts/neural-networks-and-svm
  - /datawhale/pumpkin-book/references/ch5-6-nn-svm
tags: [svm, dual-problem, lagrangian, kkt, support-vectors]
status: stable
---

# SVM 对偶问题推导

本示例展示南瓜书对西瓜书第6章支持向量机核心公式的推导补充，从间隔最大化原问题出发，通过拉格朗日对偶性推导出 SVM 的对偶问题。

## 原问题

对于二分类问题，假设训练数据集线性可分，SVM 寻找最大间隔划分超平面：

$$\boldsymbol{w}^\top \boldsymbol{x} + b = 0$$

两个异类支持向量到超平面的距离之和为间隔 $\gamma = \frac{2}{\|\boldsymbol{w}\|}$。最大化间隔等价于最小化 $\|\boldsymbol{w}\|^2$：

$$\min_{\boldsymbol{w},b} \frac{1}{2}\|\boldsymbol{w}\|^2 \tag{6.1}$$
$$\text{s.t.} \quad y_i(\boldsymbol{w}^\top\boldsymbol{x}_i + b) \geq 1, \quad i = 1,2,\ldots,m \tag{6.2}$$

其中 $\frac{1}{2}$ 是为了求导方便。

## 构造拉格朗日函数

对每个不等式约束引入拉格朗日乘子 $\alpha_i \geq 0$，拉格朗日函数为：

$$L(\boldsymbol{w}, b, \boldsymbol{\alpha}) = \frac{1}{2}\|\boldsymbol{w}\|^2 + \sum_{i=1}^{m}\alpha_i\left(1 - y_i(\boldsymbol{w}^\top\boldsymbol{x}_i + b)\right)$$

其中 $\boldsymbol{\alpha} = (\alpha_1;\alpha_2;\ldots;\alpha_m)$。

原问题等价于：
$$\min_{\boldsymbol{w},b}\max_{\boldsymbol{\alpha}:\alpha_i\geq 0} L(\boldsymbol{w}, b, \boldsymbol{\alpha})$$

## 转化为对偶问题

利用强对偶性，将原问题转化为对偶问题：

$$\max_{\boldsymbol{\alpha}:\alpha_i\geq 0}\min_{\boldsymbol{w},b} L(\boldsymbol{w}, b, \boldsymbol{\alpha})$$

先对 $\boldsymbol{w}$ 和 $b$ 求偏导并令其为零。

### 对 w 求偏导

$$\frac{\partial L}{\partial \boldsymbol{w}} = \boldsymbol{w} - \sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i = 0$$

得：

$$\boldsymbol{w} = \sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i \tag{6.6}$$

### 对 b 求偏导

$$\frac{\partial L}{\partial b} = -\sum_{i=1}^{m}\alpha_i y_i = 0$$

得：

$$\sum_{i=1}^{m}\alpha_i y_i = 0 \tag{6.7}$$

### 代入拉格朗日函数

将式(6.6)代入 $L(\boldsymbol{w}, b, \boldsymbol{\alpha})$：

$$\begin{aligned}
L &= \frac{1}{2}\|\boldsymbol{w}\|^2 + \sum_{i=1}^{m}\alpha_i - \sum_{i=1}^{m}\alpha_i y_i\boldsymbol{w}^\top\boldsymbol{x}_i - b\sum_{i=1}^{m}\alpha_i y_i \\
&= \frac{1}{2}\boldsymbol{w}^\top\boldsymbol{w} + \sum_{i=1}^{m}\alpha_i - \boldsymbol{w}^\top\sum_{i=1}^{m}\alpha_i y_i\boldsymbol{x}_i - 0
\end{aligned}$$

由式(6.6)知 $\boldsymbol{w} = \sum_j \alpha_j y_j \boldsymbol{x}_j$，代入：

$$\begin{aligned}
L &= \frac{1}{2}\left(\sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i\right)^\top\left(\sum_{j=1}^{m}\alpha_j y_j \boldsymbol{x}_j\right) + \sum_{i=1}^{m}\alpha_i - \left(\sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i\right)^\top\left(\sum_{j=1}^{m}\alpha_j y_j \boldsymbol{x}_j\right) \\
&= \sum_{i=1}^{m}\alpha_i - \frac{1}{2}\sum_{i=1}^{m}\sum_{j=1}^{m}\alpha_i\alpha_j y_i y_j \boldsymbol{x}_i^\top\boldsymbol{x}_j
\end{aligned}$$

## 对偶问题

最终对偶问题为：

$$\max_{\boldsymbol{\alpha}} \sum_{i=1}^{m}\alpha_i - \frac{1}{2}\sum_{i=1}^{m}\sum_{j=1}^{m}\alpha_i\alpha_j y_i y_j \boldsymbol{x}_i^\top\boldsymbol{x}_j \tag{6.8}$$
$$\text{s.t.} \quad \sum_{i=1}^{m}\alpha_i y_i = 0, \quad \alpha_i \geq 0 \tag{6.9}$$

解出 $\boldsymbol{\alpha}$ 后，由式(6.6)计算 $\boldsymbol{w}$，再求 $b$。

## KKT 条件

对偶问题和原问题满足强对偶性的充要条件是 KKT（Karush-Kuhn-Tucker）条件：

$$\begin{cases}
\alpha_i \geq 0 \\
y_i f(\boldsymbol{x}_i) - 1 \geq 0 \\
\alpha_i (y_i f(\boldsymbol{x}_i) - 1) = 0
\end{cases}$$

其中 $f(\boldsymbol{x}_i) = \boldsymbol{w}^\top\boldsymbol{x}_i + b$。

第三个条件（互补松弛性）是理解支持向量的关键：

- 若 $\alpha_i > 0$，则必有 $y_i f(\boldsymbol{x}_i) = 1$，即该样本恰好在最大间隔边界上——这就是**支持向量**。
- 若 $\alpha_i = 0$，则该样本对模型没有贡献（可能在间隔内被正确分类，也可能在间隔外）。

最终模型为：

$$f(\boldsymbol{x}) = \sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i^\top\boldsymbol{x} + b$$

由于只有支持向量（$\alpha_i > 0$）参与求和，SVM 的解具有稀疏性。

## 核函数引入

当样本线性不可分时，将 $\boldsymbol{x}$ 映射到高维特征空间 $\phi(\boldsymbol{x})$，对偶问题中的内积 $\boldsymbol{x}_i^\top\boldsymbol{x}_j$ 替换为核函数：

$$\kappa(\boldsymbol{x}_i, \boldsymbol{x}_j) = \phi(\boldsymbol{x}_i)^\top\phi(\boldsymbol{x}_j)$$

对偶问题变为：

$$\max_{\boldsymbol{\alpha}} \sum_{i=1}^{m}\alpha_i - \frac{1}{2}\sum_{i=1}^{m}\sum_{j=1}^{m}\alpha_i\alpha_j y_i y_j \kappa(\boldsymbol{x}_i, \boldsymbol{x}_j)$$

这样不需要显式计算高维映射，直接通过核函数计算内积，即"核技巧"。

## 关键知识点

1. **为什么用对偶问题**：对偶问题自然引入核函数，且求解复杂度与特征维度无关（与样本数有关），适合高维稀疏数据。
2. **强对偶性**：SVM 原问题是凸二次规划，满足 Slater 条件，因此强对偶成立，对偶问题的最优值等于原问题最优值。
3. **SMO 算法**：实际求解对偶问题时使用 SMO（Sequential Minimal Optimization），每次固定其他变量只优化两个变量，高效求解大规模问题。
4. **稀疏性**：非支持向量的 $\alpha_i = 0$，不影响最终决策函数，这是 SVM 解的重要性质。
