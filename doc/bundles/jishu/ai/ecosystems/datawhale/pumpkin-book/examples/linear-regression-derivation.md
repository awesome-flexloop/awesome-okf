---
type: example
title: "线性回归最小二乘推导"
bundle: /datawhale/pumpkin-book
description: "一元线性回归参数w和b的最小二乘估计完整推导，多元线性回归矩阵形式闭式解"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter3/chapter3.md
related:
  - /datawhale/pumpkin-book/concepts/linear-models-and-decision-trees
  - /datawhale/pumpkin-book/references/ch3-4-linear-tree
tags: [linear-regression, least-squares, derivation, closed-form]
status: stable
---

# 线性回归最小二乘推导

本示例展示南瓜书对西瓜书第3章线性回归公式的推导补充，从最小二乘目标函数出发，推导出参数 $w$ 和 $b$ 的闭式解。

## 问题设定

给定数据集 $D = \{(x_1,y_1),(x_2,y_2),\ldots,(x_m,y_m)\}$，一元线性回归试图学得：

$$f(x_i) = w x_i + b$$

使得 $f(x_i) \approx y_i$。采用均方误差作为性能度量，通过最小化均方误差求解参数：

$$(w^*, b^*) = \arg\min_{(w,b)} \sum_{i=1}^{m}(y_i - w x_i - b)^2$$

均方误差对应欧氏距离，基于均方误差最小化的模型求解方法称为"最小二乘法"。

## 对 b 求偏导

将目标函数记为 $E_{(w,b)} = \sum_{i=1}^{m}(y_i - w x_i - b)^2$，对 $b$ 求偏导：

$$\frac{\partial E_{(w,b)}}{\partial b} = \sum_{i=1}^{m} 2(y_i - w x_i - b)(-1) = -2\sum_{i=1}^{m}(y_i - w x_i - b)$$

令偏导为零：

$$\sum_{i=1}^{m}(y_i - w x_i - b) = 0$$

展开：

$$\sum_{i=1}^{m} y_i - w\sum_{i=1}^{m} x_i - mb = 0$$

解得：

$$b^* = \frac{1}{m}\sum_{i=1}^{m}y_i - w\frac{1}{m}\sum_{i=1}^{m}x_i = \bar{y} - w\bar{x}$$

其中 $\bar{x} = \frac{1}{m}\sum x_i$，$\bar{y} = \frac{1}{m}\sum y_i$。

## 对 w 求偏导

对 $w$ 求偏导：

$$\frac{\partial E_{(w,b)}}{\partial w} = \sum_{i=1}^{m} 2(y_i - w x_i - b)(-x_i) = -2\sum_{i=1}^{m}x_i(y_i - w x_i - b)$$

令偏导为零，将 $b^* = \bar{y} - w\bar{x}$ 代入：

$$\sum_{i=1}^{m}x_i(y_i - w x_i - \bar{y} + w\bar{x}) = 0$$

展开并整理含 $w$ 的项：

$$\sum_{i=1}^{m}x_i(y_i - \bar{y}) - w\sum_{i=1}^{m}x_i(x_i - \bar{x}) = 0$$

解得：

$$w^* = \frac{\sum_{i=1}^{m}x_i(y_i - \bar{y})}{\sum_{i=1}^{m}x_i(x_i - \bar{x})}$$

将分子分母展开可进一步化为更直观的形式：

$$w^* = \frac{\sum_{i=1}^{m}(x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^{m}(x_i - \bar{x})^2}$$

这就是 $w$ 的最小二乘估计。分子为 $x$ 与 $y$ 的协方差（未归一化），分母为 $x$ 的方差（未归一化）。

## 多元线性回归矩阵形式

当样本有 $d$ 个属性时，将 $b$ 吸收进权重向量 $\hat{\boldsymbol{w}} = (\boldsymbol{w};b)$，数据集表示为 $m \times (d+1)$ 矩阵：

$$\mathbf{X} = \begin{pmatrix} x_{11} & \cdots & x_{1d} & 1 \\ \vdots & \ddots & \vdots & \vdots \\ x_{m1} & \cdots & x_{md} & 1 \end{pmatrix}$$

目标函数为：

$$\hat{\boldsymbol{w}}^* = \arg\min_{\hat{\boldsymbol{w}}} (\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})^\top(\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})$$

令 $E_{\hat{\boldsymbol{w}}} = (\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})^\top(\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})$，对 $\hat{\boldsymbol{w}}$ 求导：

$$\frac{\partial E_{\hat{\boldsymbol{w}}}}{\partial \hat{\boldsymbol{w}}} = 2\mathbf{X}^\top(\mathbf{X}\hat{\boldsymbol{w}} - \boldsymbol{y})$$

令导数为零：

$$\mathbf{X}^\top\mathbf{X}\hat{\boldsymbol{w}}^* = \mathbf{X}^\top\boldsymbol{y}$$

当 $\mathbf{X}^\top\mathbf{X}$ 可逆时：

$$\hat{\boldsymbol{w}}^* = (\mathbf{X}^\top\mathbf{X})^{-1}\mathbf{X}^\top\boldsymbol{y}$$

最终学得的多元线性回归模型为：

$$f(\hat{\boldsymbol{x}}_i) = \hat{\boldsymbol{x}}_i^\top(\mathbf{X}^\top\mathbf{X})^{-1}\mathbf{X}^\top\boldsymbol{y}$$

## 关键知识点

1. **arg min 与 min 的区别**：`min` 输出目标函数的最小值，`arg min` 输出使目标函数达到最小值时的参数取值。
2. **矩阵求导**：对向量 $\hat{\boldsymbol{w}}$ 求导时利用了 $\frac{\partial}{\partial \boldsymbol{x}}(\boldsymbol{a}^\top\boldsymbol{x}) = \boldsymbol{a}$ 和 $\frac{\partial}{\partial \boldsymbol{x}}(\boldsymbol{x}^\top\mathbf{A}\boldsymbol{x}) = (\mathbf{A}+\mathbf{A}^\top)\boldsymbol{x}$ 等规则。
3. **不可逆情况**：当 $\mathbf{X}^\top\mathbf{X}$ 不可逆（特征数大于样本数或存在共线性）时，需要正则化（如岭回归）或使用梯度下降迭代求解。
4. **几何意义**：最小二乘法等价于将 $\boldsymbol{y}$ 正交投影到 $\mathbf{X}$ 的列空间，$(\mathbf{X}^\top\mathbf{X})^{-1}\mathbf{X}^\top$ 即投影矩阵。
