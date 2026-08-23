---
title: 附录
type: reference
bundle: /datawhale/key-book
chapter: appendix
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/appendix.md
---

# 附录

> 来源：`docs/appendix.md`，编辑：赵志民、李一飞

附录系统梳理全书所需的数学基础，涵盖范数、凸分析、优化理论、概率论，是理解七大理论主题的必备备查。

## 内容概要

### 范数

- **半范数三条件**：半正定性、齐次性、次可加性（三角不等式）
- **范数**：额外要求 $\|v\|=0\Rightarrow v=0$
- 常用范数：$\ell_0$（非零元素数）、$\ell_1$（绝对值和）、$\ell_2$（欧几里得）、$\ell_p$、$\ell_\infty$（最大值）、加权范数 $\|x\|_A=\sqrt{x^TAx}$

### 凸集合

- 定义：任意两点连线完全在集合内
- **投影非扩张性**：$\|\Pi(x)-\Pi(x')\|_2\leq\|x-x'\|_2$（通过分离超平面 + Cauchy-Schwarz 证明）
- 投影算子 $\Pi(x)=\arg\min_{y\in K}\|x-y\|_2$ 在凸优化中保证全局最优

### Hessian 矩阵

函数二阶偏导数组成的方阵，用于判断凸性（半正定）和强凸性（正定）。

### 凸函数

四种等价定义：
1. **凸性条件**：$f(\alpha x+(1-\alpha)y)\leq\alpha f(x)+(1-\alpha)f(y)$
2. **一阶条件**：$f(y)\geq f(x)+\nabla f(x)^T(y-x)$
3. **二阶条件**：Hessian 半正定
4. **Jensen 不等式**：$f(\sum w_ix_i)\leq\sum w_if(x_i)$
5. **上图集**：epi$(f)$ 为凸集

凸函数局部最优 = 全局最优（反证法证明）。

### 凹函数

定义相反，$-f$ 为凸函数。

### 强凸函数

$\lambda$-强凸：

$$f(\alpha x+(1-\alpha)y)\leq\alpha f(x)+(1-\alpha)f(y)-\frac{\lambda}{2}\alpha(1-\alpha)\|x-y\|^2$$

等价条件：Hessian 正定、梯度强单调。直观上任意点可构造二次函数下界。附录给出定理 7.2 的完整证明：$f(w)-f(w^*)\geq\frac{\lambda}{2}\|w-w^*\|^2$。

### 指数凹函数

$\exp(-\alpha f(x))$ 为凹函数。性质弱于强凸但强于凸，在在线优化中带来 $O(d\log T)$ 遗憾。

### 凸优化

一般形式：

$$\min f_0(x)\quad\text{s.t.}\ f_i(x)\leq 0,\ g_j(x)=0$$

三大优势：全局最优性、多项式时间高效算法、广泛应用。

### 仿射

- **仿射变换**：$y=Ax+b$（线性变换 + 平移）
- 保持共线性、平行性、凸性、长度比例、质心
- **仿射集**：任意两点连线全在集合内；包含原点的仿射集是子空间
- **仿射包**：aff$(S)$ = 包含 S 的最小仿射集

### Slater 条件/定理

- **Slater 条件**：存在严格可行点 $x\in\text{relint}(D)$，$f_i(x)<0$
- **Slater 定理**：凸优化 + Slater 条件 ⇒ 强对偶性成立，对偶最优解非空有界
- 附录通过支撑超平面定理给出完整证明，分 $\lambda_0=0$（矛盾）和 $\lambda_0>0$ 两种情况

### KKT 条件

最优性的一阶必要条件（凸问题中为充要）：
- 主问题稳定性、主问题约束、对偶约束、互补松弛
- KKT 与 Slater 的区别：KKT 是最优性条件，Slater 是强对偶性条件；Slater 成立时 KKT 为充要

### 偏序集

自反性、反对称性、传递性。与全序的区别：允许元素不可比较。

### 上下界

上确界（supremum）= 最小上界；下确界（infimum）= 最大下界。

### 尾界与置信界

- **尾界**：随机变量偏离期望的概率上限（Chebyshev、Hoeffding、Bernstein）
- **置信界**：参数估计的区间，具有置信水平

### 连续性与 Lipschitz 连续性

- **连续**：输入微小变化导致输出微小变化
- **$L$-Lipschitz**：$\|f(x)-f(y)\|\leq L\|x-y\|$，变化率有界
- 可微 + 导数有界 ⟺ Lipschitz 连续（微分中值定理证明）
- Lipschitz 连续 ⇒ 连续，反之不成立

### 光滑性

$L$-光滑：梯度 $L$-Lipschitz，三种等价定义：
1. $\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|$
2. $\|\nabla^2 f(x)\|\leq L$
3. $f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2$

光滑性关注梯度变化速度（曲率），Lipschitz 关注函数值变化速度（陡峭程度）。

### 次梯度

凸函数不可导点的"导数区间"：$f(x)-f(x_0)\geq c(x-x_0)$。次微分 $\partial f(x_0)=[a,b]$ 为左右导数之间的区间。广泛应用于 SVM 和非光滑优化。

### 对偶空间

线性泛函 $f:V\to k$ 的集合 $V^*=\text{Hom}_k(V,k)$。

### Legendre 变换与共轭函数

- **Legendre 变换**：$p=f'(x)$，$g(p)=xp-f(x)$
- **凸共轭（Legendre-Fenchel 变换）**：$f^*(y)=\sup_x(y^Tx-f(x))$
- 性质：凸性（证明）、逆序性（$f\leq g\Rightarrow f^*\geq g^*$）、极值变换（可微时 $f^*(y)\leq f^*(\nabla f(x))$）

### σ-代数与过滤

- **σ-代数**：包含全集、对补集封闭、对可数并封闭的集合族
- **过滤** $\{\mathcal{F}_t\}$：随时间递增的 σ-代数序列，表示可观测信息的累积

### 鞅

- **鞅**：$\mathbb{E}[X_s|\mathcal{F}_t]=X_t$（$s\geq t$），"公平游戏"
- **超鞅（上鞅）**：$\mathbb{E}[X_s|\mathcal{F}_t]\leq X_t$（期望递减）
- **亚鞅（下鞅）**：$\mathbb{E}[X_s|\mathcal{F}_t]\geq X_t$
- **鞅差序列**：$D_t=X_t-X_{t-1}$，$\mathbb{E}[D_t|\mathcal{F}_{t-1}]=0$
- 鞅差不要求独立，但条件期望为零；是 Azuma-Hoeffding、Freedman 不等式的基础

### KL 散度

$$D_{KL}(P\|Q)=\sum_x P(x)\ln\frac{P(x)}{Q(x)}$$

非负性由 Jensen 不等式证明（$\ln$ 为凹函数）。非对称，用于 PAC-Bayes、VAE、GAN。

### 先验与后验

- **先验** $P(\theta)$：观察数据前的初始信念
- **后验** $P(\theta|D)=\frac{P(D|\theta)P(\theta)}{P(D)}$：Bayes 定理更新

### 其他

- **拓扑向量空间**：向量空间 + 使加法和数乘连续的拓扑
- **超平面**：$n\cdot x=c$，划分两个半空间
- **紧空间**：有限开覆盖性质，"表现得像有限的"
- **Taylor 展开**：多项式逼近函数，Maclaurin 为 $a=0$ 特例

## 理论定位

附录是全书的"数学底座"。第 1 章（预备定理）提供集中不等式工具，附录提供凸分析、优化、概率论的概念基础。二者配合，构成七大理论主题证明的完整数学语言体系。
