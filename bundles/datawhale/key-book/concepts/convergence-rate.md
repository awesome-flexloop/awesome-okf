---
title: 收敛率
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/consistency
  - /datawhale/key-book/concepts/regret-bound
  - /datawhale/key-book/references/chapter7
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter7.md
---

# 收敛率（Convergence Rate）

收敛率量化优化算法逼近最优解的**速度**。如果说[一致性](/datawhale/key-book/concepts/consistency)回答"最终能否到达"，收敛率回答的是"多快能到"——在资源约束下，速度往往比极限更关键。

## 收敛率分类

设迭代序列 $\{x_t\}$ 逼近最优解 $x^*$，定义：

$$\lim_{t\to\infty} \frac{\|x_{t+1} - x^*\|}{\|x_t - x^*\|^p} = C$$

| 类型 | 阶数 $p$ | 因子 $C$ | 误差行为 | 典型算法 |
|:---|:---:|:---:|:---|:---|
| 超线性收敛 | $p\geq 1$ | $C=0$ | 误差加速减小 | 牛顿法 |
| 线性收敛 | $p=1$ | $0<C<1$ | 几何级数下降 | 强凸函数梯度下降 |
| 次线性收敛 | $p=1$ | $C=1$ | 误差减速减小 | 凸函数梯度下降 |

$p>1$ 时称 $p$ 阶收敛（$p=2$ 为平方收敛，$p=3$ 为立方收敛）。

## 确定性优化

### 凸函数梯度下降（定理 7.1）

对 $\gamma$-光滑凸函数，步长 $\eta = \Gamma/(l\sqrt{T})$，返回 $T$ 轮迭代均值：

$$f(\bar{\omega}) - f(\omega^*) \leq O\left(\frac{1}{\sqrt{T}}\right)$$

**为什么返回均值而非最后一次迭代？** 因为凸函数梯度下降的步长是启发式的，无法保证单次迭代的局部最优性，但均值具有稳定的次线性收敛率。

### 强凸函数梯度下降（定理 7.3）

对 $\lambda$-强凸且 $\gamma$-光滑函数，步长 $1/\gamma$，返回最后一次迭代：

$$f(\omega_T) - f(\omega^*) \leq O\left(\left(1-\frac{\lambda}{\gamma}\right)^T\right)$$

**为什么可以返回最后一次迭代？** 强凸条件下梯度更新有闭式解，每次迭代都是该邻域的全局最优，因此无需平均。注意 $\gamma \geq \lambda$（光滑系数决定上界，强凸系数决定下界）。

## 随机优化

### 鞅差序列的 Bernstein 不等式（定理 7.6）

随机梯度下降中的梯度噪声构成鞅差序列（条件期望为零）。Freedman 型不等式同时控制累积和与条件方差：

$$\mathbb{P}\left(\max_{i\leq k} S_i > t,\ V_k^2 \leq v\right) \leq \exp\left(-\frac{t^2}{2(v + Kt/3)}\right)$$

其中 $V_k^2 = \sum_{i=1}^k \mathbb{E}[X_i^2|\mathcal{F}_{i-1}]$ 为条件方差，$|X_i|\leq K$。

### Epoch-GD（定理 7.7）

分阶段 epoch 的梯度下降，每个 epoch 内逐步减小步长。通过鞅差 Bernstein 不等式控制每个 epoch 的波动，最终达到 $O(1/T)$ 的随机优化收敛率（优于简单 SGD 的 $O(1/\sqrt{T})$）。

证明中使用的关键技巧：
- Cauchy-Schwarz 不等式控制范数和
- 二次函数最大值点优化步长
- 数学归纳法建立 epoch 递推

## 优化中的关键函数性质

| 性质 | 定义 | 对收敛的影响 |
|:---|:---|:---|
| 凸性 | $f(\alpha x+(1-\alpha)y)\leq\alpha f(x)+(1-\alpha)f(y)$ | 局部最优=全局最优 |
| $\lambda$-强凸 | 凸性 + $\frac{\lambda}{2}\|x-y\|^2$ 下界 | 线性收敛 |
| $\gamma$-光滑 | 梯度 $L$-Lipschitz | 二次上界，步长上界 $1/\gamma$ |
| 指数凹 | $\exp(-\alpha f)$ 为凹 | 介于凸与强凸之间 |

## 与其他概念的关系

- [一致性](/datawhale/key-book/concepts/consistency)：收敛率是一致性的定量化，从"是否"到"多快"
- [遗憾界](/datawhale/key-book/concepts/regret-bound)：在线学习的遗憾 $O(\sqrt{T})$ 与离线凸优化的次线性收敛率 $O(1/\sqrt{T})$ 数学同源
- 光滑性与强凸性是决定收敛率的两个关键函数性质（附录详述）

## 参见

- [第 7 章：收敛率](/datawhale/key-book/references/chapter7)
