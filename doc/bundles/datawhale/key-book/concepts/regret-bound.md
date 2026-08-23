---
title: 遗憾界
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/convergence-rate
  - /datawhale/key-book/concepts/stability
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/references/chapter8
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter8.md
---

# 遗憾界（Regret Bound）

遗憾界是**在线学习**（Online Learning）的核心性能度量。当数据以序列形式到达、不满足独立同分布假设、甚至允许对抗选择时，遗憾衡量算法的累积损失与事后最优固定决策之间的差距。

## 遗憾 vs 超额风险

| 维度 | 超额风险（批量学习） | 遗憾（在线学习） |
|:---|:---|:---|
| 定义 | $\mathbb{E}[l(w_{T+1})] - \min_w \mathbb{E}[l(w)]$ | $\sum_{t=1}^T f_t(w_t) - \min_w\sum_{t=1}^T f_t(w)$ |
| 期望 | 有（对分布求期望） | 无（不假设分布） |
| 时间结构 | 学习后输出单一模型 | 每轮决策，累积求和 |
| 数据假设 | i.i.d. | 无分布假设，可对抗 |

遗憾定义的关键：$w_t$ 只依赖于历史 $(x_1,y_1),\ldots,(x_{t-1},y_{t-1})$，与当前轮 $(x_t,y_t)$ 无关。

## 在线凸优化

### 在线梯度下降（引理 8.3）

对凸可微函数序列，$f_t$ 梯度有界 $\|\nabla f_t\|\leq l$，决策集直径 $\Lambda$，步长 $\eta = \Lambda/(l\sqrt{T})$：

$$\sum_{t=1}^T \mathbb{E}[f_t(\omega_t)] - \min_\omega \sum_{t=1}^T f_t(\omega) \leq l\Lambda\sqrt{T}$$

证明核心是**潜在函数论证**：用 $\|\omega_t - \omega^*\|^2$ 作为 Lyapunov 函数，望远镜求和得到 $O(\sqrt{T})$ 遗憾。这与凸函数批量梯度下降的 $O(1/\sqrt{T})$ 收敛率数学等价。

### 自适应算法 Maler

Maler（Multiple Sub-algorithms & Learning Rates）通过多专家加权混合，自适应函数类型：

| 函数类型 | 遗憾界 |
|:---|:---|
| 一般凸函数 | $O(\sqrt{T})$ |
| 指数凹函数 | $O(d\log T)$ |
| 强凸函数 | $O(\log T)$ |

元算法用指数权重更新各专家的混合概率，无需预先知道函数属于哪一类。

## 多臂赌博机（Multi-Armed Bandit）

### 随机多臂赌博机（定理 8.3，UCB）

$K$ 个摇臂，最优臂与第 $i$ 臂的均值差为 $\Delta_i$，UCB（Upper Confidence Bound）策略的遗憾：

$$\mathbb{E}[\text{regret}] \leq \sum_{i=1}^K \frac{2\ln T}{\Delta_i} + O(1) = O(K\log T)$$

UCB 的核心思想是**面对不确定性保持乐观**：选择 $\hat{\mu}_i + \sqrt{2\ln t/n_i}$ 最大的臂，上置信界同时利用已有信息（探索）和高均值（利用）。

### 线性赌博机

假设臂的期望回报为 $w^T x$（线性结构），通过岭回归估计参数：

$$w^* = (X^TX + \lambda I)^{-1}X^TY$$

利用 **Sherman-Morrison-Woodbury 公式**进行 $O(d^2)$ 增量更新，避免每轮重新求逆。

### 凸赌博机（定理 8.5）

仅观察函数值（非梯度）的凸在线优化，通过**单样本梯度估计**（引理 8.2）：

$$\mathbb{E}_{u\in\mathbb{S}}[f(x+\delta u)u] = \frac{\delta}{d}\nabla \mathbb{E}_{v\in\mathbb{B}}[f(x+\delta v)]$$

用单位球面上的随机函数值探测梯度方向（散度定理），结合缩减投影（引理 8.4），达到 $O(T^{3/4})$ 遗憾——比全信息 $O(\sqrt{T})$ 差，反映了反馈信息减少的代价。

## 探索-利用权衡

赌博机设置的根本张力：
- **利用**（exploitation）：选择当前已知最优臂
- **探索**（exploration）：尝试不确定的臂以获取信息

UCB 用置信上界自然平衡二者；Thompson Sampling 通过后验采样实现随机平衡。这一权衡是强化学习与在线决策的核心问题。

## 与其他概念的关系

- [收敛率](/datawhale/key-book/concepts/convergence-rate)：离线 $O(1/\sqrt{T})$ 收敛率与在线 $O(\sqrt{T})$ 遗憾是同一数学结构的两面
- [稳定性](/datawhale/key-book/concepts/stability)：在线学习要求可塑性（适应新数据），与稳定性（对扰动不敏感）存在张力
- [可学性](/datawhale/key-book/concepts/learnability)：遗憾界放弃 i.i.d. 假设，是 PAC 框架在非平稳环境的推广

## 参见

- [第 8 章：遗憾界](/datawhale/key-book/references/chapter8)
- [UCB 多臂赌博机案例](/datawhale/key-book/examples/ucb-bandit)
