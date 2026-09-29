---
title: 第7章 收敛率
type: reference
bundle: /datawhale/key-book
chapter: 7
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter7.md
---

# 第7章：收敛率

> 来源：`docs/chapter7.md`，编辑：赵志民

本章分析优化算法逼近最优解的速度，是收敛率概念的主体章节，涵盖确定性与随机优化。

## 内容概要

### 7.1 算法收敛率分类

$$\lim_{t\to\infty}\frac{\|x_{t+1}-x^*\|}{\|x_t-x^*\|^p}=C$$

- **超线性收敛**：$p\geq 1, C=0$（牛顿法为平方收敛 $p=2$）
- **线性收敛**：$p=1, 0<C<1$（误差几何级数下降）
- **次线性收敛**：$p=1, C=1$（误差减速减小）

### 7.2 凸函数确定性优化（定理 7.1）

对 $\gamma$-光滑凸函数，梯度下降返回 $T$ 轮迭代**均值**（非最后一次），步长 $\eta=\Gamma/(l\sqrt{T})$：

$$f(\bar{\omega})-f(\omega^*)\leq O\left(\frac{1}{\sqrt{T}}\right)$$

**为什么返回均值？** 凸函数梯度下降步长是启发式的，单次迭代不保证局部最优，但均值具有稳定的次线性收敛率。步长优化利用 AM-GM 不等式（$n=2$ 情形 $\sqrt{xy}\leq(x+y)/2$）。

### 7.3 强凸函数确定性优化（定理 7.3）

对 $\lambda$-强凸且 $\gamma$-光滑函数，返回**最后一次迭代** $\omega_T$：

$$f(\omega_T)-f(\omega^*)\leq O\left(\left(1-\frac{\lambda}{\gamma}\right)^T\right)$$

**为什么可返回最后一次？** 强凸条件下梯度更新有闭式解 $\omega_{t+1}=\omega_t-\frac{1}{\gamma}\nabla f(\omega_t)$，每次迭代是该邻域全局最优，无需平均。

**关键关系**：$\gamma\geq\lambda$（光滑系数决定上界，强凸系数决定下界）。

证明中对 $f(\alpha)=\frac{\gamma-\lambda}{\lambda}\alpha^2-\alpha$ 分三种情况讨论（$\gamma=\lambda$、$\lambda/(2(\gamma-\lambda))\geq 1$、$<1$）。

### 7.4 鞅差序列的 Bernstein 不等式（定理 7.6）

随机优化的核心尾界工具。设 $X_i$ 为有界鞅差序列（$|X_i|\leq K$），$S_i=\sum_{j=1}^i X_j$，条件方差 $V_k^2=\sum_{i=1}^k\mathbb{E}[X_i^2|\mathcal{F}_{i-1}]$：

$$\mathbb{P}\left(\max_{i\leq k}S_i>t,\ V_k^2\leq v\right)\leq\exp\left(-\frac{t^2}{2(v+Kt/3)}\right)$$

证明要点：
1. 构造指数超鞅 $Q_k=\exp(\theta S_k/K - g(\theta)V_k^2/K^2)$
2. 利用 $e^{\theta x}\leq 1+\theta x+g(\theta)x^2$（$|x|\leq 1$）验证超鞅性质
3. 优化 $\theta=\log(1+Kt/v)$ 得最紧界
4. 利用 $h(u)=(1+u)\log(1+u)-u\geq u^2/(2(1+u/3))$ 化简

### 7.5 Epoch-GD 收敛率（引理 7.2、7.3，定理 7.7）

分阶段 epoch 的随机梯度下降：
- **引理 7.2**：外层循环收敛率泛化上界，利用 Cauchy-Schwarz 控制范数和，鞅差 Bernstein 控制波动
- **引理 7.3**：数学归纳法建立特定步长和迭代次数下的递推
- **定理 7.7**：Epoch-GD 最终收敛率

关键技巧：
- 按 $A_T$（累积梯度范数平方）分层，每层应用定理 7.6
- 开口向下二次函数最大值优化步长
- $f(x)=(1-1/x)^x$ 单调递增证明（用于分析 $(1-1/k^\dagger)^{k^\dagger}$）

### 7.6 SVM 实例

将收敛率理论应用于支持向量机的优化分析。

## 理论定位

本章从"是否收敛"（一致性）进入"多快收敛"。凸性/强凸性决定收敛率阶（次线性 vs 线性），光滑性决定步长上界。鞅差 Bernstein 不等式是随机优化的关键工具，将第 1 章的集中不等式从独立随机变量推广到条件依赖序列。

## 参见

- 第 6 章：一致性：渐近收敛的定性分析
- 第 8 章：遗憾界：在线 $O(\sqrt{T})$ 遗憾与离线 $O(1/\sqrt{T})$ 收敛率数学同源
- 附录：强凸函数、光滑性、凸优化定义
