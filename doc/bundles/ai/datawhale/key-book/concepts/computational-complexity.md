---
title: 计算复杂度
type: concept
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/references/chapter2
  - /datawhale/key-book/references/chapter3
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter2.md
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter3.md
---

# 计算复杂度（Computational Complexity）

计算复杂度量化学习任务的资源代价，包含两个互补维度：**样本复杂度**（需要多少数据）与**时间复杂度**（需要多少计算）。假设空间的复杂性分析是连接二者的桥梁。

## 样本复杂度

有限假设空间 $|\mathcal{H}|$ 的样本复杂度：

$$m \geq \frac{1}{\epsilon}\left(\ln|\mathcal{H}| + \ln\frac{1}{\delta}\right)$$

这表明所需样本量随假设空间大小对数增长。当 $|\mathcal{H}|=\infty$ 时，需用有效复杂度替代 $\ln|\mathcal{H}|$。

## 时间复杂度

在抽象图灵机上定义为"需要执行的操作数量"。对有限假设类的穷举搜索需 $O(|\mathcal{H}| \cdot m)$ 时间：

- $|\mathcal{H}_n|=n$：多项式，高效
- $|\mathcal{H}_n|=2^n$：样本复杂度仍为多项式，但计算复杂度指数增长，低效

这解释了为什么 3-DNF 不可高效 PAC 学——它归约于 NP 完全问题。

## 假设空间复杂度度量

### VC 维（Vapnik-Chervonenkis Dimension）

$$VC(\mathcal{H}) = \max\{m : \Pi_{\mathcal{H}}(m) = 2^m\}$$

即假设空间能**打散**（shatter）的最大样本集大小——能实现样本上所有 $2^m$ 种对分。二维线性分类器 $sign(wx+b)$ 的 VC 维为 3。

VC 维是二元分类中模型有效自由度的度量，与参数量无必然联系。

### Natarajan 维

多分类问题的 VC 维推广。当类别数 $K=2$ 时退化为 VC 维。增长函数上界：

$$\Pi_{\mathcal{H}}(m) \leq m^d K^{2d}$$

### Rademacher 复杂度

与数据分布相关的复杂度度量：

$$\Re_m(\mathcal{H}) = \mathbb{E}_{S,\sigma}\left[\sup_{h\in\mathcal{H}}\frac{1}{m}\sum_{i=1}^m \sigma_i h(z_i)\right]$$

其中 $\sigma_i$ 为 Rademacher 随机变量（±1 各半）。它衡量假设空间与随机噪声的相关程度，上界为：

$$\Re_m(\mathcal{H}) \leq \sqrt{\frac{2\ln\Pi_{\mathcal{H}}(m)}{m}}$$

Rademacher 复杂度因引入数据分布，比 VC 维给出更紧的泛化界。

## 三者关系

| 度量 | 是否依赖数据 | 适用问题 | 紧致性 |
|:---|:---:|:---|:---|
| VC 维 | 否 | 二元分类 | 松（分布无关） |
| Natarajan 维 | 否 | 多分类 | 松 |
| Rademacher 复杂度 | 是 | 实值/分类 | 紧（分布相关） |

## 与其他概念的关系

- [可学性](/ai/datawhale/key-book/concepts/learnability)要求样本和时间复杂度均为多项式
- [泛化界](/ai/datawhale/key-book/concepts/generalization-bound)的阶由复杂度度量决定（$O(\sqrt{d/m})$）
- 深度学习的双下降现象挑战了"复杂度越高越易过拟合"的传统认知

## 参见

- [第 2 章：可学性](/ai/datawhale/key-book/references/chapter2)
- [第 3 章：复杂性分析](/ai/datawhale/key-book/references/chapter3)
- [线性分类器 VC 维案例](/ai/datawhale/key-book/examples/vc-dimension-linear)
