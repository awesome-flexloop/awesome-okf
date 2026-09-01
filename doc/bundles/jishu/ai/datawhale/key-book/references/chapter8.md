---
title: 第8章 遗憾界
type: reference
bundle: /datawhale/key-book
chapter: 8
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter8.md
---

# 第8章：遗憾界

> 来源：`docs/chapter8.md`，编辑：赵志民、詹好

本章分析在线学习中算法的累积损失与事后最优策略的差距，是遗憾界概念的主体章节，标志着从批量 i.i.d. 范式到在线非平稳范式的转换。

## 内容概要

### 8.1 超额风险与遗憾的区别

| 维度 | 超额风险 | 遗憾 |
|:---|:---|:---|
| 定义 | $\mathbb{E}[l(w_{T+1})]-\min_w\mathbb{E}[l(w)]$ | $\sum f_t(w_t)-\min_w\sum f_t(w)$ |
| 期望 | 有 | 无 |
| 结构 | 一次性计算最终模型 | 多轮损失求和 |
| 数据假设 | i.i.d. | 无分布假设 |

关键：$w_t$ 只依赖历史 $(x_1,y_1),\ldots,(x_{t-1},y_{t-1})$，与当前轮无关。

### 8.2 Maler 算法

多专家自适应在线学习算法（Multiple Sub-algorithms & Learning Rates）：

| 函数类型 | 遗憾界 |
|:---|:---|
| 一般凸函数 | $O(\sqrt{T})$ |
| 指数凹函数 | $O(d\log T)$ |
| 强凸函数 | $O(\log T)$ |

**元算法**：加权混合凸专家、指数凹专家、强凸专家的预测，用指数权重更新。
**凸专家**：在线梯度下降 $x_{t+1}=\Pi_D(x_t-\frac{D}{\eta^c G\sqrt{t}}\nabla c_t(x_t^c))$
**指数凹专家**：Newton 步 + 协方差矩阵更新 $\Sigma_{t+1}=\Sigma_t+gg^T$
**强凸专家**：加权梯度下降，步长 $1/(2\eta^2G^2t)$

### 8.3 随机多臂赌博机遗憾界（定理 8.3，UCB）

$K$ 个摇臂，UCB（Upper Confidence Bound）策略选择 $\hat{\mu}_i+\sqrt{2\ln t/n_i}$ 最大的臂：

$$\mathbb{E}[\text{regret}]\leq\sum_{i=1}^K\frac{2\ln T}{\Delta_i}+O(1)=O(K\log T)$$

证明补充：
- 最优臂选择条件分解为三种情况（调整后互斥更清晰）
- 次优臂选择次数 $\mathbb{E}[n_i^T]\leq\lceil 2\ln T/\Delta_i^2\rceil+2\sum t^{-4}$
- $p$-级数 $\sum t^{-2}$ 收敛（Basel 问题 $\pi^2/6$），积分放缩 $\leq 2$
- 遗憾界与 $\Delta_i$ 呈对钩函数 $f(x)=Ax+B/x$：过大过小均增大遗憾

### 8.4 线性赌博机

假设臂回报为 $w^Tx$，转化为岭回归：

$$w^*=(X^TX+\lambda I)^{-1}X^TY$$

利用 **Sherman-Morrison-Woodbury 公式**进行 $O(d^2)$ 增量更新，避免每轮重新求逆。

### 8.5 Sherman-Morrison-Woodbury 公式

$$(A+UCV)^{-1}=A^{-1}-A^{-1}U(C^{-1}+VA^{-1}U)^{-1}VA^{-1}$$

验证 $A+UCV$ 与右侧乘积为单位矩阵即证。这是矩阵求逆的核心低秩修正工具。

### 8.6 单样本近似梯度（引理 8.2）

凸赌博机中仅观察函数值时的梯度估计：

$$\mathbb{E}_{u\in\mathbb{S}}[f(x+\delta u)u]=\frac{\delta}{d}\nabla\mathbb{E}_{v\in\mathbb{B}}[f(x+\delta v)]$$

证明三步：
1. 左边：单位球面积分表达
2. 右边：单位球体积分 + 梯度 + **散度定理**转化为球面积分
3. 利用 $d$ 维球体积 $Vol_d(\delta\mathbb{B})=\frac{\delta}{d}Vol_{d-1}(\delta\mathbb{S})$ 关联两边

### 8.7 凸赌博机在线梯度下降（引理 8.3）

凸可微函数序列，随机梯度满足 $\mathbb{E}[g_t|\omega_t]=\nabla f_t(\omega_t)$，$\|g_t\|\leq l$，步长 $\eta=\Lambda/(l\sqrt{T})$：

$$\sum_{t=1}^T\mathbb{E}[f_t(\omega_t)]-\min_\omega\sum_{t=1}^T f_t(\omega)\leq l\Lambda\sqrt{T}$$

证明：潜在函数 $\|\omega_t-\omega^*\|^2$ + 投影非扩张性 + 望远镜求和。

### 8.8 缩减投影误差（引理 8.4）

$$\min_{\omega\in(1-\alpha)W}\sum f_t(\omega)-\min_{\omega\in W}\sum f_t(\omega)\leq 2\alpha cT$$

利用凸性 $f_t((1-\alpha)\omega)\leq\alpha f_t(0)+(1-\alpha)f_t(\omega)$ 和有界性 $|f_t|\leq c$。

### 8.9 凸赌博机遗憾界（定理 8.5）

结合引理 8.2（梯度估计）、8.3（在线梯度下降）、8.4（缩减投影），达到 $O(T^{3/4})$ 遗憾。

参数选择分析：
- 步长 $\eta=\Lambda_2/(dc/\delta\sqrt{T})$
- 缩减系数 $\alpha$ 与扰动系数 $\delta$ 形成对钩函数 $f(\delta)=A\delta+B/\delta+C$
- 最优 $\delta^*=T^{-1/4}\sqrt{dc\Lambda_2/(3l)}$，得 $O(T^{3/4})$
- 取 $\alpha=\delta/\Lambda_1$ 可进一步紧致

## 理论定位

本章完成了全书最根本的范式转换：从 i.i.d. 批量统计学习到无分布假设的在线博弈学习。遗憾界不仅是在线学习的性能度量，更在大模型时代的分布偏移、持续学习、对抗环境中具有现实意义。$O(\sqrt{T})$ 全信息与 $O(T^{3/4})$ 拔河信息的差距，精确量化了反馈信息结构对学习性能的决定作用。参见 UCB 多臂赌博机案例。

## 参见

- 第 5 章：稳定性：在线学习的可塑性与离线稳定性的张力
- 第 7 章：收敛率：离线 $O(1/\sqrt{T})$ 与在线 $O(\sqrt{T})$ 的数学同源性
