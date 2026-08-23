---
type: example
title: "BP 反向传播算法推导"
bundle: /datawhale/pumpkin-book
description: "单隐层前馈网络误差逆传播的链式法则推导，输出层与隐层梯度项公式"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter5/chapter5.md
related:
  - /datawhale/pumpkin-book/concepts/neural-networks-and-svm
  - /datawhale/pumpkin-book/references/ch5-6-nn-svm
tags: [neural-network, backpropagation, chain-rule, sigmoid, gradient]
status: stable
---

# BP 反向传播算法推导

本示例展示南瓜书对西瓜书第5章 BP（误差逆传播）算法的推导补充，以单隐层前馈网络为例，利用链式法则和 Sigmoid 导数性质推导出各层权重和阈值的更新公式。

## 网络结构

给定训练集 $D = \{(\boldsymbol{x}_1,\boldsymbol{y}_1),\ldots,(\boldsymbol{x}_m,\boldsymbol{y}_m)\}$，考虑一个单隐层前馈网络：

- **输入层**：$d$ 个神经元，输入 $\boldsymbol{x} = (x_1,\ldots,x_d)$
- **隐层**：$q$ 个神经元，输出 $\boldsymbol{b} = (b_1,\ldots,b_q)$
- **输出层**：$l$ 个神经元，输出 $\hat{\boldsymbol{y}} = (\hat{y}_1,\ldots,\hat{y}_l)$

权重与阈值：
- 输入层到隐层：权重 $v_{ih}$（第 $i$ 个输入到第 $h$ 个隐层神经元），隐层阈值 $\gamma_h$
- 隐层到输出层：权重 $w_{hj}$（第 $h$ 个隐层到第 $j$ 个输出神经元），输出层阈值 $\theta_j$

隐层和输出层均使用 Sigmoid 函数：
$$\sigma(x) = \frac{1}{1+e^{-x}}, \quad \sigma'(x) = \sigma(x)(1-\sigma(x))$$

## 前向传播

对单个训练样例 $(\boldsymbol{x}_k, \boldsymbol{y}_k)$：

隐层第 $h$ 个神经元的输入：
$$\alpha_h = \sum_{i=1}^{d} v_{ih} x_i$$

隐层第 $h$ 个神经元的输出：
$$b_h = \sigma(\alpha_h - \gamma_h)$$

输出层第 $j$ 个神经元的输入：
$$\beta_j = \sum_{h=1}^{q} w_{hj} b_h$$

输出层第 $j$ 个神经元的输出：
$$\hat{y}_j = \sigma(\beta_j - \theta_j)$$

## 误差函数

网络在样例 $(\boldsymbol{x}_k, \boldsymbol{y}_k)$ 上的均方误差：

$$E_k = \frac{1}{2}\sum_{j=1}^{l}(\hat{y}_j^k - y_j^k)^2$$

BP 算法基于梯度下降，沿负梯度方向更新参数。任意参数 $v$ 的更新规则为：

$$v \leftarrow v + \Delta v, \quad \Delta v = -\eta \frac{\partial E_k}{\partial v}$$

其中 $\eta$ 为学习率。

## 输出层梯度推导

### 输出层权重 w_hj

$$\Delta w_{hj} = -\eta \frac{\partial E_k}{\partial w_{hj}}$$

链式法则分解：
$$\frac{\partial E_k}{\partial w_{hj}} = \frac{\partial E_k}{\partial \hat{y}_j} \cdot \frac{\partial \hat{y}_j}{\partial \beta_j} \cdot \frac{\partial \beta_j}{\partial w_{hj}}$$

逐项计算：

1. $\frac{\partial E_k}{\partial \hat{y}_j} = \hat{y}_j - y_j$
2. $\frac{\partial \hat{y}_j}{\partial \beta_j} = \hat{y}_j(1-\hat{y}_j)$（Sigmoid 导数性质）
3. $\frac{\partial \beta_j}{\partial w_{hj}} = b_h$

因此：

$$\frac{\partial E_k}{\partial w_{hj}} = (\hat{y}_j - y_j)\hat{y}_j(1-\hat{y}_j)b_h$$

定义输出层梯度项 $g_j$：

$$g_j = -\frac{\partial E_k}{\partial (\beta_j - \theta_j)} = -(\hat{y}_j - y_j)\hat{y}_j(1-\hat{y}_j) = \hat{y}_j(1-\hat{y}_j)(y_j - \hat{y}_j)$$

则权重更新为：

$$\Delta w_{hj} = \eta g_j b_h$$

### 输出层阈值 theta_j

$$\Delta \theta_j = -\eta\frac{\partial E_k}{\partial \theta_j} = -\eta\frac{\partial E_k}{\partial \hat{y}_j}\cdot\frac{\partial \hat{y}_j}{\partial \theta_j} = -\eta(\hat{y}_j-y_j)\cdot(-\hat{y}_j(1-\hat{y}_j)) = -\eta g_j$$

## 隐层梯度推导

### 隐层权重 v_ih

$$\frac{\partial E_k}{\partial v_{ih}} = \frac{\partial E_k}{\partial b_h}\cdot\frac{\partial b_h}{\partial \alpha_h}\cdot\frac{\partial \alpha_h}{\partial v_{ih}}$$

关键在于 $\frac{\partial E_k}{\partial b_h}$——隐层输出 $b_h$ 影响所有输出层神经元，需要链式求和：

$$\frac{\partial E_k}{\partial b_h} = \sum_{j=1}^{l}\frac{\partial E_k}{\partial \beta_j}\cdot\frac{\partial \beta_j}{\partial b_h} = \sum_{j=1}^{l}(-g_j)w_{hj}$$

其余两项：
- $\frac{\partial b_h}{\partial \alpha_h} = b_h(1-b_h)$（Sigmoid 导数）
- $\frac{\partial \alpha_h}{\partial v_{ih}} = x_i$

定义隐层梯度项 $e_h$：

$$e_h = -\frac{\partial E_k}{\partial (\alpha_h - \gamma_h)} = b_h(1-b_h)\sum_{j=1}^{l}w_{hj}g_j$$

则权重更新为：

$$\Delta v_{ih} = \eta e_h x_i$$

### 隐层阈值 gamma_h

$$\Delta \gamma_h = -\eta e_h$$

## BP 算法完整流程

1. 网络中所有权重和阈值初始化为 (0,1) 间的随机数。
2. 输入训练样例，前向传播计算各层输出 $b_h$ 和 $\hat{y}_j$。
3. 计算输出层梯度项 $g_j = \hat{y}_j(1-\hat{y}_j)(y_j - \hat{y}_j)$。
4. 计算隐层梯度项 $e_h = b_h(1-b_h)\sum_j w_{hj}g_j$。
5. 更新输出层权重和阈值：$w_{hj} \leftarrow w_{hj} + \eta g_j b_h$，$\theta_j \leftarrow \theta_j - \eta g_j$。
6. 更新隐层权重和阈值：$v_{ih} \leftarrow v_{ih} + \eta e_h x_i$，$\gamma_h \leftarrow \gamma_h - \eta e_h$。
7. 重复步骤 2-6 直到达到停止条件（训练轮数或误差阈值）。

## 关键知识点

1. **Sigmoid 导数性质**：$\sigma'(x) = \sigma(x)(1-\sigma(x))$ 使梯度计算极其简洁，只需用已计算的输出值相乘，无需重新求指数。
2. **误差反向传播**：输出层误差 $g_j$ 通过权重 $w_{hj}$ 传回隐层，加权求和后乘以隐层激活导数得到 $e_h$，这就是"逆传播"名称的由来。
3. **梯度消失**：Sigmoid 在输入绝对值较大时趋近饱和（导数趋近0），多层叠加后梯度指数级衰减，这是深层网络训练困难的核心原因，ReLU 有效缓解了此问题。
4. **标准 BP 与累积 BP**：标准 BP 每样本更新一次（随机梯度下降），累积 BP 遍历全部训练集后更新一次（批量梯度下降）。实际中常用小批量梯度下降折中。
