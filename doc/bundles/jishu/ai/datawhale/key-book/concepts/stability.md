---
title: 稳定性
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/concepts/regret-bound
  - /datawhale/key-book/references/chapter5
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter5.md
---

# 稳定性（Stability）

稳定性从**算法性质**而非假设空间性质出发推导泛化保证：如果替换训练集中的一个样本不会剧烈改变算法输出，则该算法具有良好的泛化能力。这是不依赖 VC 维计数的替代泛化分析路径。

## 核心定义

### 替换样本 β-均匀稳定性

对任意数据集 $D$、任意位置 $i$、任意替换样本 $z'_i$，算法输出满足：

$$\sup_{z\in\mathcal{Z}} |\ell(\mathfrak{L}_D, z) - \ell(\mathfrak{L}_{D^{i,z'_i}}, z)| \leq \beta$$

### 移除样本 γ-均匀稳定性

$$\sup_{z\in\mathcal{Z}} |\ell(\mathfrak{L}_D, z) - \ell(\mathfrak{L}_{D^{\setminus i}}, z)| \leq \gamma$$

### 假设稳定性

较弱的条件，仅保证风险期望被上界控制：

$$\mathbb{E}_{D,z}\left[|\ell(\mathfrak{L}_D,z) - \ell(\mathfrak{L}_{D^{\setminus i}},z)|\right] \leq \gamma$$

## 稳定性 ⇒ 泛化（定理 5.1）

关键证明思路：定义 $\Phi(D) = R(\mathfrak{L}_D) - \hat{R}(\mathfrak{L}_D)$（泛化风险与经验风险差距）。

1. 由 β-均匀稳定性，替换一个样本后 $|\Phi(D) - \Phi(D^{i,z'_i})| \leq 2\beta + M/m$（差有界性）
2. 应用 **McDiarmid 不等式**：
   $$\mathbb{P}(\Phi(D) \geq \mathbb{E}[\Phi(D)] + \epsilon) \leq \exp\left(\frac{-2m\epsilon^2}{(2m\beta+M)^2}\right)$$
3. 当 $\beta = O(1/m)$ 时，$m\beta$ 有界，泛化差距为 $O(\sqrt{\ln(1/\delta)/m})$

## 稳定性 ⇔ 可学性（定理 5.4）

均匀稳定性 + ERM 原则 ⇒ 不可知 PAC 可学：

- 稳定性给出泛化上界 $R(\mathfrak{L}_D) - \hat{R}(\mathfrak{L}_D) \leq O(\sqrt{\ln(1/\delta)/m})$
- ERM 给出经验风险最优性 $\hat{R}(\mathfrak{L}_D) \leq \hat{R}(h^*)$
- Hoeffding 控制 $\hat{R}(h^*) - R(h^*) \leq O(\sqrt{\ln(1/\delta)/m})$
- 三者合并得到样本复杂度 $m = O((1/\epsilon^2)\ln(1/\delta))$

这揭示了 **PAC 学习理论与统计学习理论在稳定性概念上的统一**。

## 过拟合与欠拟合

- 经验风险与泛化风险差距大 → 过拟合
- 泛化风险与经验风险差距大 → 欠拟合
- 稳定的算法通过限制单样本影响来防止过拟合

## 适用边界

稳定性分析有两个重要前提，并非所有算法都满足：

1. **顺序无关性**：假设输出与训练集顺序无关。SGD 等在线算法因顺序影响输出，不适用经典稳定性框架。
2. **分布一致性**：假设训练分布与真实分布一致。数据/概念漂移场景下稳定性要求可能不成立。
3. **稳定性 vs 可塑性**：在线学习需要算法适应新数据（可塑性），与稳定性目标存在根本张力，需用遗憾界分析。

## 与其他概念的关系

- 泛化界：稳定性提供算法依赖的泛化保证，是 VC 维方法的替代
- 可学性：定理 5.4 建立稳定性与不可知 PAC 可学性的等价
- 遗憾界：在线学习中稳定性与可塑性的张力由遗憾分析平衡

## 参见

- 第 5 章：稳定性
