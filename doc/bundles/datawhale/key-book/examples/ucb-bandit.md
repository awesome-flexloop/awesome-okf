---
title: UCB 多臂赌博机与遗憾界
type: example
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/regret-bound
  - /datawhale/key-book/concepts/convergence-rate
  - /datawhale/key-book/references/chapter8
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter8.md
---

# 案例：UCB 多臂赌博机与遗憾界

本案例展示 UCB（Upper Confidence Bound）算法如何在探索-利用权衡中实现对数遗憾，是理解[遗憾界](/datawhale/key-book/concepts/regret-bound)的经典示例。

## 问题设定

**随机多臂赌博机**（Stochastic Multi-Armed Bandit）：
- $K$ 个摇臂（行动），每个摇臂 $i$ 的回报服从未知分布，均值为 $\mu_i$
- 每轮选择一个摇臂 $i_t$，观察回报 $r_t$
- 最优臂 $i^* = \arg\max_i \mu_i$，均值差 $\Delta_i = \mu^* - \mu_i$
- 目标：最小化 $T$ 轮累积遗憾

$$\text{Regret}(T) = \sum_{t=1}^T (\mu^* - \mu_{i_t}) = T\mu^* - \sum_{t=1}^T \mu_{i_t}$$

## UCB 算法

**面对不确定性保持乐观**（Optimism in the Face of Uncertainty）：

$$i_t = \arg\max_i \left( \hat{\mu}_i(t-1) + \sqrt{\frac{2\ln t}{n_i(t-1)}} \right)$$

其中：
- $\hat{\mu}_i$：摇臂 $i$ 的经验平均回报（利用项）
- $n_i$：摇臂 $i$ 已被选择的次数
- $\sqrt{2\ln t/n_i}$：置信宽度（探索项），随选择次数增加而减小

**直觉**：
- 摇臂被选得少（$n_i$ 小）→ 置信区间宽 → 上界高 → 倾向于探索
- 摇臂被选得多（$n_i$ 大）→ 置信区间窄 → 上界接近真实均值 → 利用高均值臂

## 遗憾界（定理 8.3）

$$\mathbb{E}[\text{Regret}(T)] \leq \sum_{i=1}^K \frac{2\ln T}{\Delta_i} + O(1) = O(K\log T)$$

关键：遗憾随时间**对数增长**，而非线性增长——算法以越来越高的频率选择最优臂。

## 证明思路

### 1. 次优臂被选次数

设 $n_i^T$ 为前 $T$ 轮中次优臂 $i$ 被选择的次数：

$$\mathbb{E}[\text{Regret}(T)] = \sum_{i\neq i^*} \Delta_i \mathbb{E}[n_i^T]$$

### 2. UCB 选择条件

若次优臂 $i$ 在第 $t$ 轮被选，则其 UCB 必不低于最优臂的 UCB：

$$\hat{\mu}_i + \sqrt{\frac{2\ln t}{n_i}} \geq \hat{\mu}_* + \sqrt{\frac{2\ln t}{n_*}}$$

这至少蕴含以下三种情况之一：
1. 最优臂被低估：$\hat{\mu}_* \leq \mu_* - \sqrt{2\ln t/n_*}$
2. 次优臂被高估：$\hat{\mu}_i \geq \mu_i + \sqrt{2\ln t/n_i}$
3. 次优臂选择不足：$n_i < \lceil 2\ln T/\Delta_i^2 \rceil$

### 3. 控制低估/高估概率

由 Hoeffding 不等式，情况 1 和 2 的概率各为 $t^{-4}$：

$$\mathbb{P}(\hat{\mu}_* \leq \mu_* - \epsilon) \leq e^{-2n_*\epsilon^2} = t^{-4}$$

### 4. 有界选择次数

$$\mathbb{E}[n_i^T] \leq \left\lceil\frac{2\ln T}{\Delta_i^2}\right\rceil + 2\sum_{t=1}^{T-1}\sum_{p=1}^{t-1}\sum_{q=l}^{t-1} t^{-4}$$

利用 $p$-级数 $\sum t^{-2}$ 收敛（Basel 问题 $\sum t^{-2}=\pi^2/6\leq 2$），第二项为常数。

### 5. 合并遗憾

$$\mathbb{E}[\text{Regret}] \leq \sum_{i\neq i^*} \left(\frac{2\ln T}{\Delta_i} + O(\Delta_i)\right) = \sum_i \frac{2\ln T}{\Delta_i} + O(1)$$

## 对钩函数现象

遗憾界中每项 $\Delta_i$ 的贡献形如对钩函数 $f(x)=Ax+B/x$：

$$\Delta_i \cdot \mathbb{E}[n_i^T] \approx (1+\pi^2/3)\Delta_i + \frac{2\ln T}{\Delta_i}$$

- $\Delta_i$ 大（臂明显差）→ 探索少，但每次选择代价大 → 遗憾主要来自第一项
- $\Delta_i$ 小（臂接近最优）→ 探索多，但每次选择代价小 → 遗憾主要来自第二项
- **最难学的是"中等差距"的臂**

## 扩展：线性赌博机

当臂具有线性结构 $r_i = w^T x_i + \text{noise}$：
- 用岭回归估计 $w^* = (X^TX+\lambda I)^{-1}X^TY$
- Sherman-Morrison-Woodbury 公式实现 $O(d^2)$ 增量更新
- 遗憾界改进为 $O(d\sqrt{T})$，与维度 $d$ 而非臂数 $K$ 相关

## 扩展：凸赌博机

仅观察函数值（非梯度）时：
- 单样本梯度估计：$\mathbb{E}_{u\in\mathbb{S}}[f(x+\delta u)u]=\frac{\delta}{d}\nabla\mathbb{E}_{v\in\mathbb{B}}[f(x+\delta v)]$
- 用单位球面随机探测梯度方向
- 遗憾退化为 $O(T^{3/4})$，反映信息减少的代价

## 关键洞察

1. **探索-利用权衡**可被数学精确量化：UCB 的置信项自动平衡二者。
2. **对数遗憾**意味着算法渐近只选最优臂，次优臂选择次数有界。
3. **信息结构决定性能阶**：全信息 $O(\sqrt{T})$ → 拔河信息 $O(T^{3/4})$，反馈越弱遗憾越大。
4. **遗憾与收敛率的对偶**：在线 $O(\sqrt{T})$ 遗憾等价于离线 $O(1/\sqrt{T})$ 收敛率，是同一数学结构的两面。

## 参见

- [遗憾界](/datawhale/key-book/concepts/regret-bound)
- [收敛率](/datawhale/key-book/concepts/convergence-rate)
- [第 8 章：遗憾界](/datawhale/key-book/references/chapter8)
