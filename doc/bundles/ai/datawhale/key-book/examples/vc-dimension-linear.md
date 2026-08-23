---
title: 线性分类器的 VC 维
type: example
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/computational-complexity
  - /datawhale/key-book/concepts/generalization-bound
  - /datawhale/key-book/references/chapter3
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter3.md
---

# 案例：线性分类器的 VC 维

本案例通过二维线性分类器直观展示 VC 维的含义，是理解[计算复杂度](/ai/datawhale/key-book/concepts/computational-complexity)中"有效自由度"的经典示例。

## 问题设定

考虑二维空间 $\mathbb{R}^2$ 中的线性分类器：

$$h_{w,b}(x) = \text{sign}(w^T x + b), \quad w\in\mathbb{R}^2,\ b\in\mathbb{R}$$

假设空间 $\mathcal{H}$ 包含所有线性决策边界（直线）。

## 结论

$$VC(\text{linear classifiers in }\mathbb{R}^2) = 3$$

线性分类器能打散平面上**最多 3 个点**，但无法打散 4 个点。

## 三点可打散

给定平面上不共线的三个点，存在 $2^3=8$ 种标签组合。对每种组合，都能找到一条直线正确分类：

1. **全正/全负**：直线放在所有点一侧
2. **一个正两个负**：直线将该点与其余两点分开
3. **两个正一个负**：同理
4. **交替标签**：只要三点不共线，线性可分

直观上，三角形任意一边都可作为决策边界，将一个顶点与另外两个分开。

## 四点不可打散

考虑四点的两种情况：

### 情况一：三点共线

若三点共线，存在无法线性分离的标签排列（交替标签 +-+- 无法用一条直线分开）。

### 情况二：凸四边形

将四点放在凸四边形顶点上。考虑**对角标签**（两个对角为正、另两个对角为负），即 XOR 型模式：

```
  + ●───────● -
    │       │
    │       │
  - ●───────● +
```

任何直线都无法将两个对角点与另外两个对角点分开——这需要非线性边界。

因此四点存在无法实现的对分，不能被打散。

## 一般结论

对 $d$ 维空间中的线性分类器（含偏置项）：

$$VC(\mathcal{H}) = d + 1$$

| 维度 | VC 维 |
|:---:|:---:|
| 1 维（阈值） | 2 |
| 2 维（直线） | 3 |
| 3 维（平面） | 4 |
| $d$ 维（超平面） | $d+1$ |

参数数量为 $d+1$（$d$ 个权重 + 1 个偏置），VC 维恰好等于参数数量——这是线性模型的特殊性质，**不适用于非线性模型**。

## 泛化界推论

由 VC 维泛化界（定理 4.3）：

$$R(h) \leq \hat{R}_S(h) + \sqrt{\frac{8d\ln\frac{2em}{d}+8\ln\frac{4}{\delta}}{m}}$$

对二维线性分类器（$d=3$）：
- 样本量 $m=100$：泛化差距约 $\sqrt{24\ln(66.7)/100}\approx 0.37$
- 样本量 $m=1000$：泛化差距约 $\sqrt{24\ln(667)/1000}\approx 0.14$
- 样本量 $m=10000$：泛化差距约 $\sqrt{24\ln(6667)/10000}\approx 0.05$

泛化差距以 $O(\sqrt{\ln m/m})$ 速度减小。

## 关键洞察

1. **VC 维 ≠ 参数量**：线性模型恰好相等，但神经网络等非线性模型中 VC 维可远大于参数量（或反之）。
2. **VC 维衡量"有效自由度"**：不是模型有多少参数，而是它能在多少种不同的点集上实现所有标签组合。
3. **打散是存在性概念**：只需存在一个大小为 VC 维的点集可被打散，不要求所有点集。
4. **双下降现象**：过参数化深度学习模型的测试误差非单调，挑战了"VC 维越高泛化越差"的传统推论。

## 参见

- [计算复杂度](/ai/datawhale/key-book/concepts/computational-complexity)
- [泛化界](/ai/datawhale/key-book/concepts/generalization-bound)
- [第 3 章：复杂性分析](/ai/datawhale/key-book/references/chapter3)
