---
type: concept
title: "线性模型与决策树"
bundle: /datawhale/pumpkin-book
description: "线性回归最小二乘、对数几率回归、线性判别分析LDA；决策树信息增益/增益率/基尼指数三种划分准则与剪枝处理"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter3/chapter3.md
related:
  - /datawhale/pumpkin-book/concepts/model-evaluation-and-selection
  - /datawhale/pumpkin-book/concepts/neural-networks-and-svm
  - /datawhale/pumpkin-book/examples/linear-regression-derivation
  - /datawhale/pumpkin-book/references/ch3-4-linear-tree
tags: [linear-regression, logistic-regression, lda, decision-tree, information-gain, gini]
status: stable
---

# 线性模型与决策树

线性模型是机器学习中最基础的模型，很多复杂模型均可认为由线性模型衍生而来；决策树则是最符合人类直觉的分类模型，背后没有复杂的数学推导。两者分别代表了机器学习中"参数化优化"和"规则化划分"两种建模范式。

## 线性模型基本形式

给定 $d$ 个属性描述的样本 $\boldsymbol{x} = (x_1; x_2; \ldots; x_d)$，线性模型表示为：

$$f(\boldsymbol{x}) = \boldsymbol{w}^\top \boldsymbol{x} + b$$

其中 $\boldsymbol{w} = (w_1; w_2; \ldots; w_d)$ 为权重向量，$b$ 为偏置。线性模型形式简单、易于建模，且具有良好的可解释性（权重直观反映各属性的重要性）。

## 线性回归

线性回归试图学得一个线性模型以尽可能准确地预测实值输出标记。

### 一元线性回归

对于只有一个属性的数据集，模型为 $f(x_i) = w x_i + b$。通过最小化均方误差（最小二乘法）求解：

$$(w^*, b^*) = \arg\min_{(w,b)} \sum_{i=1}^{m} (y_i - w x_i - b)^2$$

南瓜书对式(3.4)到式(3.8)的推导做了详细补充，包括对 $w$ 和 $b$ 分别求偏导、令偏导为零、求解闭式解的完整过程。$w$ 的估计式中出现了 $x_i$ 和 $y_i$ 的协方差与方差之比。

### 多元线性回归

当样本有 $d$ 个属性时，将 $b$ 吸收进 $\boldsymbol{w}$（增广权重向量 $\hat{\boldsymbol{w}} = (\boldsymbol{w}; b)$），数据集表示为矩阵 $\mathbf{X}$（每行对应一个样本，最后一列全为1），则：

$$\hat{\boldsymbol{w}}^* = \arg\min_{\hat{\boldsymbol{w}}} (\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})^\top (\boldsymbol{y} - \mathbf{X}\hat{\boldsymbol{w}})$$

令导数为零可得：

$$\hat{\boldsymbol{w}}^* = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \boldsymbol{y}$$

当 $\mathbf{X}^\top \mathbf{X}$ 不可逆时（特征数大于样本数），需要正则化或使用梯度下降。

### 对数线性回归

令模型预测值逼近 $y$ 的对数，即 $\ln y = \boldsymbol{w}^\top \boldsymbol{x} + b$，这是"广义线性模型"的特例。更一般地，通过联系函数 $g(\cdot)$：

$$y = g^{-1}(\boldsymbol{w}^\top \boldsymbol{x} + b)$$

## 对数几率回归（逻辑回归）

对于二分类任务，用对数几率函数（sigmoid 函数）将线性回归的连续输出映射到 $(0,1)$ 区间：

$$y = \frac{1}{1 + e^{-(\boldsymbol{w}^\top \boldsymbol{x} + b)}}$$

对数几率回归的优点：
- 直接对分类可能性建模，无需假设数据分布
- 不仅预测类别，还得到近似概率预测
- 对率函数任意阶可导，具有很好的数学性质
- 求解的目标函数是任意阶可导的凸函数，可得到全局最优解

通过极大似然法估计参数，南瓜书补充了式(3.27)到式(3.30)的推导，将似然函数转化为对数似然并进一步化为凸优化问题。

## 线性判别分析（LDA）

LDA 的思想非常朴素：给定训练样例集，设法将样例投影到一条直线上，使同类样例的投影点尽可能接近、异类样例的投影点尽可能远离。

- **类内散度矩阵** $\mathbf{S}_w$：同类样本投影的协方差之和，越小越好。
- **类间散度矩阵** $\mathbf{S}_b$：不同类均值投影的距离，越大越好。
- **目标函数**：最大化广义瑞利商 $J = \frac{\boldsymbol{w}^\top \mathbf{S}_b \boldsymbol{w}}{\boldsymbol{w}^\top \mathbf{S}_w \boldsymbol{w}}$。

LDA 的核心思路与第10章主成分分析（PCA）相同——都是通过特征值分解寻找最优投影方向，可结合学习加深理解。

## 多分类学习

利用二分类学习器解决多分类问题的经典策略：

- **OvO（一对一）**：$N$ 个类两两配对训练 $N(N-1)/2$ 个分类器，投票产生结果。
- **OvR（一对其余）**：每次将一个类作为正例、其余作为反例，训练 $N$ 个分类器。
- **MvM（多对多）**：每次将若干类作为正例、若干类作为反例，常用 ECOC（纠错输出码）技术。

## 类别不平衡问题

当不同类别的训练样本数差别很大时：
- **缩放法（再缩放）**：对反类样例的"权重"进行调整，使正负例在学习器中影响平衡。
- **欠采样**：去除部分反例使正反例数目接近（如 EasyEnsemble）。
- **过采样**：增加正例使数目接近（如 SMOTE 通过插值合成正例）。
- **阈值移动**：基于后验概率的决策阈值进行调整。

## 决策树基本流程

决策树基于树结构进行决策，每个内部节点表示一个属性测试，每个分支表示测试输出，每个叶节点表示决策结果。决策过程就是"if...elif...else..."的递归判断。

递归返回的三种情形：
1. 当前节点所有样本同属一类，无需再划分。
2. 属性集为空或所有样本在属性集上取值相同，无法再划分，取多数类。
3. 某属性值分支无样本，将该分支标记为叶节点，类别设为全体样本最多的类（先验分布）。

## 划分选择

决策树的关键是如何选择最优划分属性。三种经典准则对应三种经典算法：

### 信息增益（ID3 算法）

**信息熵**度量样本集合纯度：
$$\text{Ent}(D) = -\sum_{k=1}^{|\mathcal{Y}|} p_k \log_2 p_k$$

**信息增益**表示用属性 $a$ 划分后纯度提升：
$$\text{Gain}(D, a) = \text{Ent}(D) - \sum_{v=1}^{V} \frac{|D^v|}{|D|} \text{Ent}(D^v)$$

信息增益越大，划分后纯度提升越大。ID3 算法选择信息增益最大的属性。信息增益对可取值数目多的属性有偏好。

### 增益率（C4.5 算法）

为克服信息增益偏好取值多属性的问题，C4.5 使用增益率：

$$\text{Gain\_ratio}(D, a) = \frac{\text{Gain}(D, a)}{\text{IV}(a)}$$

其中 $\text{IV}(a) = -\sum_{v=1}^{V} \frac{|D^v|}{|D|} \log_2 \frac{|D^v|}{|D|}$ 为属性 $a$ 的固有值。增益率对可取值数目少的属性有偏好，因此 C4.5 先从信息增益高于平均水平的属性中再选增益率最高的。

### 基尼指数（CART 算法）

CART（Classification and Regression Tree）使用基尼指数：

$$\text{Gini}(D) = 1 - \sum_{k=1}^{|\mathcal{Y}|} p_k^2$$

基尼指数反映从数据集中随机抽取两个样本类别不一致的概率，越小越好。属性 $a$ 的基尼指数为：

$$\text{Gini\_index}(D, a) = \sum_{v=1}^{V} \frac{|D^v|}{|D|} \text{Gini}(D^v)$$

CART 选择使划分后基尼指数最小的属性。

## 剪枝处理

剪枝是决策树对付过拟合的主要手段。

- **预剪枝**（prepruning）：在划分前先估计能否提升泛化性能，不能则停止划分并标记为叶节点。基于验证集判断，降低过拟合风险、显著减少训练时间，但可能带来欠拟合风险。
- **后剪枝**（postpruning）：先训练完整决策树，自底向上考察非叶节点，若替换为叶节点能提升泛化性能则剪枝。欠拟合风险小、泛化性能往往更好，但训练时间开销大。

## 连续与缺失值

- **连续值处理**：采用二分法（bi-partition），将连续属性排序后取相邻值中点作为候选划分点，选择使信息增益最大的划分点。与离散属性不同，连续属性在后续划分中可重复使用。
- **缺失值处理**：需解决两个问题——如何在属性值缺失时进行划分选择（用无缺失样本计算信息增益并按比例折扣），以及如何对缺失样本进行划分（将样本以不同概率划入不同子节点）。

## 多变量决策树

单变量决策树的分类边界轴平行，多变量决策树（斜决策树）在线性分类器组合下能实现更复杂的分类边界，如 OC1 系统中每个内部节点是形如 $\sum_i w_i a_i \leqslant t$ 的线性组合测试。
