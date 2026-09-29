---
type: concept
title: "神经网络与支持向量机"
bundle: /datawhale/pumpkin-book
description: "M-P神经元模型、感知机学习规则、BP误差逆传播算法、深度学习；SVM间隔最大化、核函数、软间隔与支持向量回归"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter5/chapter5.md
related:
  - /datawhale/pumpkin-book/concepts/linear-models-and-decision-trees
  - /datawhale/pumpkin-book/concepts/bayesian-and-ensemble-learning
  - /datawhale/pumpkin-book/examples/bp-backpropagation
  - /datawhale/pumpkin-book/examples/svm-dual-derivation
  - /datawhale/pumpkin-book/references/ch5-6-nn-svm
tags: [neural-network, perceptron, backpropagation, svm, kernel, soft-margin]
status: stable
---

# 神经网络与支持向量机

神经网络是当今最主流的机器学习算法族，深层网络即深度学习；支持向量机在深度学习流行前曾是机器学习的主流算法，其核方法至今仍有重要影响。两者分别代表了"分布式表示学习"和"核方法+凸优化"两条技术路线。

## 神经元模型

M-P 神经元模型（McCulloch-Pitts，1943）是神经网络的最基本单元：

$$y = f\left(\sum_{i=1}^{n} w_i x_i - \theta\right)$$

其中 $x_i$ 为输入，$w_i$ 为权重，$\theta$ 为阈值，$f(\cdot)$ 为激活函数。理想激活函数为阶跃函数，但不连续、不光滑，实际常用：

- **Sigmoid 函数**：$\sigma(x) = \frac{1}{1+e^{-x}}$，将输入压缩到 $(0,1)$。
- **ReLU**：$\text{ReLU}(x) = \max(0, x)$，深层网络中常用。

## 感知机与多层网络

### 感知机

感知机由两层神经元组成（输入层+输出层），只能处理线性可分问题。感知机的学习规则为：

$$w_i \leftarrow w_i + \Delta w_i, \quad \Delta w_i = \eta (y - \hat{y}) x_i$$

其中 $\eta$ 为学习率，$y$ 为真实标签，$\hat{y}$ 为预测输出。当预测正确时权重不更新，预测错误时按误差方向调整权重。

感知机的解不唯一——所有能将正负样本正确分开的超平面都是解。这与 SVM 追求"最优间隔"形成对比。

### 多层网络

在输入层和输出层之间加入隐层（hidden layer）即可得到多层前馈神经网络。每层神经元与下一层全连接，同层无连接、跨层无连接。只需一个包含足够多神经元的隐层，多层前馈网络就能以任意精度逼近任意复杂度的连续函数（万能近似定理）。

## 误差逆传播算法（BP）

BP（BackPropagation）算法是训练多层神经网络的经典算法，基于**梯度下降**和**链式法则**。

### 单隐层网络推导

设隐层使用 Sigmoid 激活，输出层也使用 Sigmoid，对训练样例 $(\boldsymbol{x}_k, \boldsymbol{y}_k)$，网络输出为 $\hat{\boldsymbol{y}}_k$，则均方误差为：

$$E_k = \frac{1}{2}\sum_{j=1}^{l} (\hat{y}_j^k - y_j^k)^2$$

BP 算法按以下规则更新参数：

- **输出层权重梯度**：$\Delta w_{hj} = \eta g_j b_h$，其中 $g_j = \hat{y}_j(1-\hat{y}_j)(y_j - \hat{y}_j)$ 为输出层梯度项。
- **隐层权重梯度**：$\Delta v_{ih} = \eta e_h x_i$，其中 $e_h = b_h(1-b_h)\sum_{j=1}^{l} w_{hj} g_j$ 为隐层梯度项。
- **阈值更新**：$\Delta \theta_j = -\eta g_j$，$\Delta \gamma_h = -\eta e_h$。

关键推导技巧：利用 Sigmoid 函数的导数性质 $f'(x) = f(x)(1-f(x))$，将输出层误差通过权重反向传播到隐层。

### 累积 BP 与标准 BP

- **标准 BP**：每次处理一个样本即更新参数，更新频繁，需多次迭代。
- **累积 BP**：读取整个训练集后根据累积误差更新参数，更新次数少，但累积到一定程度后下降缓慢。

### 全局最小与局部最小

- **全局最小**：参数空间中使误差最小的点。
- **局部极小**：该点误差比相邻点小但不是全局最小。

常用"跳出"局部极小的策略：多组不同参数初始化、模拟退火、随机梯度下降、遗传算法等。

## 深度学习

深度学习即深层神经网络的学习。随着网络层数增加，模型复杂度提升、特征学习能力增强，但也带来训练难度：

- **梯度消失/爆炸**：反向传播中梯度经多层链式相乘，可能指数级衰减或增长。ReLU、批归一化、残差连接等技术缓解了这一问题。
- **无监督逐层预训练**：早期深度网络训练策略，先对每层做无监督预训练再整体微调。
- **现代架构**：CNN（卷积神经网络）处理图像、RNN/LSTM 处理序列、Transformer 基于注意力机制，均通过 BP 算法端到端训练。

## 支持向量机（SVM）

### 间隔与支持向量

分类超平面为 $\boldsymbol{w}^\top \boldsymbol{x} + b = 0$，样本到超平面的距离为：

$$r = \frac{|\boldsymbol{w}^\top \boldsymbol{x} + b|}{\|\boldsymbol{w}\|}$$

SVM 要找的是离正负样本都尽可能远、位于"正中间"的超平面——即间隔最大化的超平面。两个异类支持向量到超平面的距离之和为间隔 $\gamma = \frac{2}{\|\boldsymbol{w}\|}$。

支持向量是指距离超平面最近、满足 $\boldsymbol{w}^\top \boldsymbol{x}_i + b = \pm 1$ 的训练样本，它们决定了超平面的位置。

### 对偶问题

原始优化问题：
$$\min_{\boldsymbol{w},b} \frac{1}{2}\|\boldsymbol{w}\|^2 \quad \text{s.t.} \quad y_i(\boldsymbol{w}^\top \boldsymbol{x}_i + b) \geq 1$$

通过拉格朗日乘数法转化为对偶问题：
$$\max_{\boldsymbol{\alpha}} \sum_{i=1}^{m}\alpha_i - \frac{1}{2}\sum_{i=1}^{m}\sum_{j=1}^{m}\alpha_i\alpha_j y_i y_j \boldsymbol{x}_i^\top\boldsymbol{x}_j$$
$$\text{s.t.} \quad \sum_{i=1}^{m}\alpha_i y_i = 0, \quad \alpha_i \geq 0$$

满足 KKT 条件时，$\alpha_i > 0$ 对应的样本即为支持向量。最终模型为：

$$f(\boldsymbol{x}) = \sum_{i=1}^{m}\alpha_i y_i \boldsymbol{x}_i^\top \boldsymbol{x} + b$$

### 核函数

当样本在原始空间线性不可分时，将样本映射到更高维的特征空间，使其在高维线性可分。由于对偶问题中只涉及内积 $\boldsymbol{x}_i^\top \boldsymbol{x}_j$，可以用核函数直接计算：

$$\kappa(\boldsymbol{x}_i, \boldsymbol{x}_j) = \phi(\boldsymbol{x}_i)^\top \phi(\boldsymbol{x}_j)$$

常用核函数：
- **线性核**：$\kappa(\boldsymbol{x}_i,\boldsymbol{x}_j) = \boldsymbol{x}_i^\top \boldsymbol{x}_j$
- **多项式核**：$\kappa(\boldsymbol{x}_i,\boldsymbol{x}_j) = (\boldsymbol{x}_i^\top \boldsymbol{x}_j)^d$
- **高斯核（RBF）**：$\kappa(\boldsymbol{x}_i,\boldsymbol{x}_j) = \exp(-\gamma\|\boldsymbol{x}_i - \boldsymbol{x}_j\|^2)$
- **Sigmoid 核**：$\kappa(\boldsymbol{x}_i,\boldsymbol{x}_j) = \tanh(\beta\boldsymbol{x}_i^\top \boldsymbol{x}_j + \theta)$

核函数选择是 SVM 的最大变数，高斯核最通用。

### 软间隔

现实中很难确定合适的核函数使训练样本线性可分，即使线性可分也可能是噪声导致。软间隔允许某些样本不满足约束 $y_i(\boldsymbol{w}^\top \boldsymbol{x}_i + b) \geq 1$，引入松弛变量 $\xi_i \geq 0$：

$$\min_{\boldsymbol{w},b,\xi_i} \frac{1}{2}\|\boldsymbol{w}\|^2 + C\sum_{i=1}^{m}\xi_i$$

其中 $C > 0$ 为惩罚参数，$C$ 越大对误分类惩罚越重（趋向硬间隔），$C$ 越小越宽容。常用 hinge 损失 $\ell(z) = \max(0, 1-z)$。

### 支持向量回归（SVR）

SVR 允许预测值与真实值之间存在 $\epsilon$ 的偏差而不计损失，相当于以 $f(\boldsymbol{x})$ 为中心构建宽度为 $2\epsilon$ 的间隔带，落入间隔带的样本不计算损失。SVR 的解仍具有稀疏性，只有支持向量（间隔带之外的样本）对模型有贡献。

### 核方法

基于核函数的学习方法统称核方法，表示定理表明：任何对称正半定核函数都可隐式定义一个再生核希尔伯特空间（RKHS），最优解可表示为核函数的线性组合。核方法不限于 SVM，还可用于核 PCA、核 Fisher 判别等。
