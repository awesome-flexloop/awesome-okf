---
type: reference
title: "第5-6章：神经网络与支持向量机"
bundle: /datawhale/pumpkin-book
description: "第5章神经网络（M-P神经元/感知机/BP算法/深度学习）与第6章支持向量机（间隔/对偶/核函数/软间隔/SVR）"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter5/chapter5.md
path: docs/chapter5/chapter5.md, docs/chapter6/chapter6.md
tags: [neural-network, perceptron, bp, svm, kernel-method, soft-margin, svr]
status: stable
---

# 第5-6章：神经网络与支持向量机

## 信源信息

- **第5章文件路径**：`docs/chapter5/chapter5.md`
- **第5章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter5/chapter5.md
- **第6章文件路径**：`docs/chapter6/chapter6.md`
- **第6章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter6/chapter6.md

## 第5章内容概要

神经网络是当今最主流的机器学习算法族：

- **5.1 神经元模型**：M-P神经元模型（McCulloch-Pitts，1943），激活函数（阶跃函数/Sigmoid/ReLU），"阈(yù)"而非"阀(fá)"的读音提示
- **5.2 感知机与多层网络**：
  - 式(5.1)~式(5.2)感知机参数更新公式推导（感知机模型、学习策略、学习算法）
  - 感知机只能处理线性可分问题，解不唯一
  - 多层前馈网络（输入层/隐层/输出层），万能近似定理
- **5.3 误差逆传播算法（BP）**：
  - 单隐层网络结构与前向传播
  - 式(5.4)~式(5.12)输出层和隐层梯度项推导（链式法则+Sigmoid导数性质）
  - 标准BP（逐样本更新）vs 累积BP（全数据集更新）
  - 全局最小与局部最小，跳出局部极小的策略
- **5.4 全局最小与局部最小**：多组初始化、模拟退火、随机梯度下降
- **5.5 深度学习**：深层神经网络、梯度消失问题、无监督逐层预训练、CNN/RNN/Transformer

组队学习时间：3天。

## 第6章内容概要

SVM在深度学习流行前是机器学习主流算法：

- **6.1 间隔与支持向量**：
  - 图6.1解释：感知机解不唯一 vs SVM找中间超平面
  - 式(6.1)超平面方程与法向量性质
  - 式(6.2)几何间隔与函数间隔
  - 式(6.5)~式(6.6)间隔最大化原问题
- **6.2 对偶问题**：
  - 式(6.8)~式(6.11)拉格朗日函数构造与对偶推导
  - 式(6.17)KKT条件与互补松弛性
  - 支持向量的识别（$\alpha_i > 0$）
  - SMO算法（式6.21~6.25，两个变量二次规划解析解）
- **6.3 核函数**：
  - 特征空间映射与核技巧
  - 式(6.23)~式(6.26)核函数定义与Mercer定理
  - 常用核函数（线性核/多项式核/高斯RBF核/Sigmoid核）
  - 核函数选择（RBF最通用）
- **6.4 软间隔与正则化**：
  - 式(6.29)~式(6.35)松弛变量与软间隔目标
  - hinge损失 $\ell(z) = \max(0,1-z)$
  - 惩罚参数C的作用（C大→硬间隔，C小→软间隔）
  - 正则化问题与支持向量回归的统一视角
- **6.5 支持向量回归（SVR）**：
  - $\epsilon$-不敏感损失与间隔带
  - 式(6.43)~式(6.52)SVR对偶问题推导
  - SVR解的稀疏性
- **6.6 核方法**：表示定理、核线性判别分析（KLDA）、核方法的通用性

组队学习时间：3天（支持向量机+软间隔与SVR各含视频教程）。

## 对应概念与示例

- [神经网络与支持向量机](../concepts/neural-networks-and-svm.md)
- [SVM对偶问题推导](../examples/svm-dual-derivation.md)
- [BP反向传播算法推导](../examples/bp-backpropagation.md)
