---
title: 第3章 复杂度
type: reference
bundle: /datawhale/key-book
chapter: 3
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter3.md
---

# 第3章：复杂度

> 来源：`docs/chapter3.md`（源文件 H1 标题为"复杂性分析"，catalog 导航标题为"复杂度"），编辑：王茂霖、李一飞、詹好、赵志民

本章量化假设空间的有效复杂度，是[计算复杂度](/ai/datawhale/key-book/concepts/computational-complexity)概念的主体章节，为第 4 章泛化界提供关键工具。

## 内容概要

### 3.1 VC 维

VC 维（Vapnik-Chervonenkis 维度）是二元分类假设空间复杂度的核心度量：

$$VC(\mathcal{H})=\max\{m:\Pi_{\mathcal{H}}(m)=2^m\}$$

其中增长函数 $\Pi_{\mathcal{H}}(m)$ 是假设空间在大小为 $m$ 的样本集上能实现的不同对分（dichotomy）数量。

- **打散（shattering）**：假设空间能实现样本集上所有 $2^m$ 种标签组合
- VC 维 = 能被打散的最大样本集大小 = 模型有效自由度
- **示例**：二维线性分类器 $sign(wx+b)$ 的 VC 维为 3（能打散平面上任意三点，不能打散四点）

### 3.2 Natarajan 维

多分类问题的复杂度度量，是 VC 维的推广：

- 二分类（$K=2$）时：$VC(\mathcal{H}) = Natarajan(\mathcal{H})$
- $K$ 分类增长函数上界：$\Pi_{\mathcal{H}}(m)\leq m^d K^{2d}$
- 随类别数 $K$ 增加，复杂度指数增长

### 3.3 Rademacher 复杂度

与数据分布相关的复杂度度量，比 VC 维更紧：

$$\Re_m(\mathcal{H}) = \mathbb{E}_{S,\sigma}\left[\sup_{h\in\mathcal{H}}\frac{1}{m}\sum_{i=1}^m\sigma_i h(z_i)\right]$$

其中 $\sigma_i$ 为独立 Rademacher 随机变量（以 1/2 概率取 ±1）。

- 衡量假设空间拟合随机噪声的能力
- 与增长函数关系：$\Re_m(\mathcal{H})\leq\sqrt{2\ln\Pi_{\mathcal{H}}(m)/m}$
- 引入数据几何结构与信噪比，获得分布相关的更紧泛化界

### 3.4 Shattering 可视化

通过二维线性分类器图示：
- 三点的所有 8 种对分均可被线性分类器实现
- 四点存在无法线性分离的对分（XOR 型）
- 故 $VC(\text{linear in }\mathbb{R}^2)=3$

## 三种复杂度对比

| 度量 | 数据相关 | 适用范围 | 紧致性 | 核心思想 |
|:---|:---:|:---|:---|:---|
| VC 维 | 否 | 二分类 | 松（分布无关） | 打散最大样本数 |
| Natarajan 维 | 否 | 多分类 | 松 | 多分类打散 |
| Rademacher 复杂度 | 是 | 实值/分类 | 紧 | 拟合随机噪声能力 |

## 理论定位

本章解决了无限假设空间的"可数性"问题：VC 维通过增长函数将无限空间投影到有限样本上的有限对分数，Rademacher 复杂度进一步利用数据分布。这些度量是 Sauer 引理、对称化技巧和泛化界的基础，决定了从"能表示"到"能学会"的样本量门槛。参见 [线性分类器 VC 维案例](/ai/datawhale/key-book/examples/vc-dimension-linear)。

## 参见

- [第 2 章：可学性](/ai/datawhale/key-book/references/chapter2)：复杂度是 PAC 样本复杂度的决定因素
- [第 4 章：泛化界](/ai/datawhale/key-book/references/chapter4)：VC 维/Rademacher 复杂度直接代入泛化界
