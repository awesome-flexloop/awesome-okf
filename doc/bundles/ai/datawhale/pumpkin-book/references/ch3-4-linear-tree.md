---
type: reference
title: "第3-4章：线性模型与决策树"
bundle: /datawhale/pumpkin-book
description: "第3章线性模型（线性回归/对数几率回归/LDA）与第4章决策树（信息增益/增益率/基尼指数/剪枝）"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter3/chapter3.md
path: docs/chapter3/chapter3.md, docs/chapter4/chapter4.md
tags: [linear-models, regression, logistic, lda, decision-tree, information-gain, pruning]
status: stable
---

# 第3-4章：线性模型与决策树

## 信源信息

- **第3章文件路径**：`docs/chapter3/chapter3.md`
- **第3章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter3/chapter3.md
- **第4章文件路径**：`docs/chapter4/chapter4.md`
- **第4章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter4/chapter4.md
- **第4章资源**：`docs/chapter4/resources/4_11.pptx`及4个PDF（4_11_a~d.pdf）

## 第3章内容概要

线性模型是机器学习最基础的模型，很多复杂模型由其衍生：

- **3.1 基本形式**：$f(\boldsymbol{x}) = \boldsymbol{w}^\top\boldsymbol{x} + b$，列向量用分号、行向量用逗号的书写约定
- **3.2 线性回归**：
  - 属性数值化（离散属性连续化/one-hot编码）
  - 式(3.4)一元线性回归最小二乘推导（arg min符号解释、w和b的闭式解）
  - 式(3.10)~式(3.11)多元线性回归的矩阵形式推导
  - 对数线性回归与广义线性模型
- **3.3 对数几率回归**：
  - Sigmoid函数与对数几率
  - 式(3.27)~式(3.30)极大似然估计推导（凸优化问题）
  - 牛顿法求解
- **3.4 线性判别分析（LDA）**：
  - 类内散度矩阵$\mathbf{S}_w$与类间散度矩阵$\mathbf{S}_b$
  - 式(3.32)~式(3.37)广义瑞利商最大化推导
  - LDA与PCA的联系（均为特征值分解找投影方向）
- **3.5 多分类学习**：OvO、OvR、MvM（ECOC纠错输出码）
- **3.6 类别不平衡问题**：再缩放、欠采样、过采样（SMOTE）、阈值移动

组队学习时间：9天（线性回归3天+对数几率回归3天+LDA 3天）。

## 第4章内容概要

决策树符合人类日常思维，数学推导较少：

- **4.1 基本流程**：递归构建决策树，三种递归返回情形（同类样本/属性耗尽/空分支）
- **4.2 划分选择**：
  - 信息增益（ID3）：信息熵Ent(D)、信息增益Gain(D,a)推导
  - 增益率（C4.5）：固有值IV(a)、先筛后选策略
  - 基尼指数（CART）：Gini(D)与Gini_index(D,a)
- **4.3 剪枝处理**：
  - 预剪枝（基于验证集精度判断是否划分，可能欠拟合）
  - 后剪枝（自底向上考察，欠拟合风险小但开销大）
- **4.4 连续与缺失值**：
  - 连续值二分法（候选划分点取相邻值中点）
  - 缺失值处理（划分选择时用无缺失子集+比例折扣；样本划分时按概率划入不同子节点）
- **4.5 多变量决策树**：斜决策树，内部节点为属性线性组合测试

组队学习时间：3天。

## 对应概念与示例

- [线性模型与决策树](../concepts/linear-models-and-decision-trees.md)
- [线性回归最小二乘推导](../examples/linear-regression-derivation.md)
