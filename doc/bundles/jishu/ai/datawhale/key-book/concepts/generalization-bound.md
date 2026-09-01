---
title: 泛化界
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/concepts/computational-complexity
  - /datawhale/key-book/concepts/stability
  - /datawhale/key-book/references/chapter4
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter4.md
---

# 泛化界（Generalization Bound）

泛化界量化**经验误差**（训练集上观测到的）与**泛化误差**（真实分布上的期望）之间的差距，是回答"训练好是否等于真的好"的理论工具。

## 基本定义

- **泛化误差**：$R(h) = \mathbb{P}_{(x,y)\sim\mathcal{D}}[h(x)\neq y]$（未知，因 $\mathcal{D}$ 未知）
- **经验误差**：$\hat{R}_S(h) = \frac{1}{m}\sum_{i=1}^m \mathbb{I}[h(x_i)\neq y_i]$（可观测）
- **关键性质**：$\mathbb{E}_S[\hat{R}_S(h)] = R(h)$（经验误差是泛化误差的无偏估计）

## 有限假设空间泛化界

基于 Union Bound + Hoeffding 不等式：

$$\mathbb{P}\left(\exists h\in\mathcal{H}: |\hat{R}_S(h) - R(h)| > \epsilon\right) \leq 2|\mathcal{H}|\exp(-2m\epsilon^2)$$

反解得到以 $1-\delta$ 概率成立的泛化界：

$$R(h) \leq \hat{R}_S(h) + \sqrt{\frac{\ln|\mathcal{H}| + \ln(2/\delta)}{2m}}$$

## 无限假设空间：对称化与增长函数

当 $|\mathcal{H}|=\infty$，Union Bound 失效。核心技巧是**对称化**（symmetrization）：引入 Ghost 样本集 $S'$，将 $|\hat{R}_S(h)-R(h)|$ 转化为 $|\hat{R}_S(h)-\hat{R}_{S'}(h)|$，再用增长函数 $\Pi_{\mathcal{H}}(2m)$ 控制不同对分数量：

$$\mathbb{P}(|R(h)-\hat{R}_S(h)|>\epsilon) \leq 4\Pi_{\mathcal{H}}(2m)\exp\left(-\frac{m\epsilon^2}{8}\right)$$

## VC 维泛化界

代入 Sauer 引理 $\Pi_{\mathcal{H}}(m) \leq (em/d)^d$，得到：

$$R(h) \leq \hat{R}_S(h) + \sqrt{\frac{8d\ln\frac{2em}{d} + 8\ln\frac{4}{\delta}}{m}}$$

收敛率为 $O(\sqrt{d\ln(m/d)/m})$：当 $m/d$ 越大（样本多、VC 维低），泛化差距越小。

## Rademacher 复杂度泛化界

基于数据分布的更紧界：

$$R(h) \leq \hat{R}_S(h) + \Re_m(\mathcal{H}) + \sqrt{\frac{\ln(1/\delta)}{2m}}$$

其中 $\Re_m(\mathcal{H})$ 为经验 Rademacher 复杂度，利用数据几何结构获得紧致性。

## 泛化下界（No Free Lunch 型）

定理 4.6 表明，对任意学习算法，总存在"坏"分布使得：

$$\mathbb{P}\left(R(h_D) > \frac{d-1}{32m}\right) \geq \frac{1}{100}$$

不可分情形下泛化误差下界为 $\Omega(\sqrt{d/m})$。这证明不存在万能学习算法。

## 间隔泛化界

SVM 的 $\rho$-间隔损失函数是 $1/\rho$-Lipschitz 的，结合 Rademacher 复杂度得到与间隔相关的泛化界，解释了大间隔分类器的泛化优势。

## 与其他概念的关系

- 可学性：PAC 可学性本质是泛化界的直接推论
- 计算复杂度：泛化界的阶由 VC 维/Rademacher 复杂度决定
- 稳定性：提供不依赖假设空间复杂度的替代泛化保证

## 参见

- 第 4 章：泛化界
