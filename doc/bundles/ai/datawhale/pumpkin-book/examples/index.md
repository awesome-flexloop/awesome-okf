---
okf_version: "0.2"
type: index
title: "南瓜书推导示例"
bundle: /datawhale/pumpkin-book
description: "以具体公式推导为例，展示南瓜书的推导讲解风格"
sources: https://github.com/datawhalechina/pumpkin-book
---

# 推导示例

本目录包含 3 个公式推导示例，展示南瓜书"从本科数学基础出发，补全西瓜书省略推导步骤"的讲解风格。每个示例对应西瓜书的核心算法，是理解南瓜书推导方法的最佳入口。

* [线性回归最小二乘推导](linear-regression-derivation.md) — 一元线性回归参数 w 和 b 的最小二乘估计完整推导，多元线性回归矩阵形式闭式解。对应南瓜书第3章。
* [SVM 对偶问题推导](svm-dual-derivation.md) — 间隔最大化原问题→拉格朗日函数→对偶问题→KKT条件→支持向量识别的完整链路。对应南瓜书第6章。
* [BP 反向传播算法推导](bp-backpropagation.md) — 单隐层网络输出层与隐层梯度项推导，Sigmoid 导数性质与链式法则应用。对应南瓜书第5章。

```{toctree}
:hidden:

bp-backpropagation
linear-regression-derivation
svm-dual-derivation
```
