---
title: 第1章 预备知识
type: reference
bundle: /datawhale/key-book
chapter: 1
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter1.md
---

# 第1章：预备知识

> 来源：`docs/chapter1.md`（源文件 H1 标题为"预备定理"，catalog 导航标题为"预备知识"），编辑：赵志民、李一飞

本章是全书的数学工具库，系统回顾概率不等式、集中不等式与分析基础，为后续七大理论主题提供证明手段。

## 内容概要

### 基础不等式（1.1–1.10）

- **Jensen 不等式**（1.1）：凸函数的期望不等式，证明利用 Taylor 展开
- **Hölder 不等式**（1.2）：$L^p$ 空间的基本不等式，Young 不等式推导
- **Cauchy-Schwarz 不等式**（1.3）：$p=q=2$ 的 Hölder 特例
- **Lyapunov 不等式**（1.4）：矩的单调性
- **Minkowski 不等式**（1.5）：$L^p$ 范数的三角不等式
- **Bhatia-Davis 不等式**（1.6）：有界随机变量的方差上界
- **Union Bound**（1.7）：概率的次可加性
- **Markov 不等式**（1.8）：非负随机变量的尾界基础
- **Chebyshev 不等式**（1.9）：方差驱动的双侧尾界
- **Cantelli 不等式**（1.10）：单边 Chebyshev 加强版

### 集中不等式（1.11–1.18）

- **Chernoff 界**（1.11）：矩母函数方法，引入次高斯性与次指数性定义
- **Chernoff 乘积形式**（1.12）：独立 Bernoulli 和的尾界
- **最优 Chernoff 界**（1.13）：凸共轭（Cramér 变换）给出最优指数衰减
- **Hoeffding 不等式**（1.14）：有界独立随机变量的核心集中不等式，不要求同分布
- **McDiarmid 不等式**（1.15）：差有界函数的集中，引入差有界性、离散鞅、Azuma-Hoeffding 引理
- **Bennett 不等式**（1.16）：利用方差信息的加强版
- **Bernstein 不等式**（1.17）：矩条件 ⇒ 亚指数条件 ⇒ Chernoff 界，小偏差区域方差主导
- **Azuma–Hoeffding 不等式**（1.18）：鞅差序列的集中，构造指数超鞅证明

### 分析与几何工具（1.19–1.28）

- **Slud 不等式**（1.19）：二项分布的正态近似下界
- **上确界加性公式**（1.20）：$\sup(f+g)\leq\sup f+\sup g$
- **正态分布不等式**（1.21）：标准正态尾界
- **AM-GM 不等式**（1.22）：算术-几何平均不等式
- **Young 不等式**（1.23）：$ab\leq a^p/p+b^q/q$
- **Bayes 定理**（1.24）：后验概率更新
- **广义二项式定理**（1.25）：实数指数的二项展开
- **Stirling 公式**（1.26）：阶乘渐近近似
- **散度定理**（1.27）：体积分与面积分转换
- **分离超平面定理**（1.28）：不相交凸集的严格分离

## 关键定义

- **次高斯性**：$\mathbb{E}[e^{\lambda X}]\leq\exp(\sigma^2\lambda^2/2)$，尾端高斯衰减
- **次指数性**：矩母函数在 $\lambda\in(0,a)$ 有界，尾端指数衰减
- **差有界性**：替换单个自变量函数变化不超过 $c_i$
- **离散鞅**：$\mathbb{E}[Z_{m+1}|\mathcal{F}_m]=Z_m$
- **鞅差序列**：$D_i=Z_i-Z_{i-1}$，$\mathbb{E}[D_i|\mathcal{F}_{i-1}]=0$

## 理论定位

本章工具按强度递进：Markov → Chebyshev → Chernoff → Hoeffding → McDiarmid/Bernstein → Azuma，对应从独立同分布到鞅差序列、从无界到有界、从方差信息到矩条件的逐步精细化。这些不等式是[泛化界](/datawhale/key-book/concepts/generalization-bound)、[稳定性](/datawhale/key-book/concepts/stability)、[收敛率](/datawhale/key-book/concepts/convergence-rate)证明的通用武器。

## 参见

- [附录](/datawhale/key-book/references/appendix)：凸分析、优化、概率论的基础概念备查
- [第 4 章：泛化界](/datawhale/key-book/references/chapter4)：集中不等式的直接应用
