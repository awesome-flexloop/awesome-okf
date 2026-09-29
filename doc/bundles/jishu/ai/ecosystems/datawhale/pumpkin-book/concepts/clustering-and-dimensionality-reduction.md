---
type: concept
title: "聚类与降维"
bundle: /datawhale/pumpkin-book
description: "聚类性能度量与k-Means/DBSCAN/层次聚类；PCA主成分分析、KPCA核化降维、流形学习(Isomap/LLE)；特征选择三方法与稀疏学习"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter9/chapter9.md
related:
  - /datawhale/pumpkin-book/concepts/bayesian-and-ensemble-learning
  - /datawhale/pumpkin-book/concepts/model-evaluation-and-selection
  - /datawhale/pumpkin-book/references/ch9-11-clustering-dim-feature
tags: [clustering, kmeans, dbscan, pca, dimensionality-reduction, manifold, feature-selection]
status: stable
---

# 聚类与降维

聚类和降维是无监督学习的两大核心任务。聚类试图将数据样本划分为若干不相交的子集（簇），降维则通过数学变换将高维数据映射到低维子空间。第11章的特征选择与降维有相似动机但方法不同——特征选择保留原始特征，降维产生新特征。

## 聚类任务

聚类（clustering）将数据集划分为若干簇（cluster），每个簇对应潜在的概念或类别。与分类不同，聚类的类别标记未知，算法自动发现数据中的结构。

聚类的核心问题：（1）如何度量相似性（距离）；（2）如何确定簇的数量和形状；（3）如何评估聚类质量。

## 性能度量

聚类性能度量也称"有效性指标"，分外部指标和内部指标。

### 外部指标

将聚类结果与某个"参考模型"（如领域专家给出的划分）比较。定义：
- $a$：在 $C$ 和 $C^*$ 中都是同簇的样本对数量
- $b$：在 $C$ 中同簇、在 $C^*$ 中不同簇的样本对数量
- $c$：在 $C$ 中不同簇、在 $C^*$ 中同簇的样本对数量
- $d$：在两者中都不同簇的样本对数量

常用外部指标：
- **Jaccard 系数**：$\text{JC} = \frac{a}{a+b+c}$
- **FM 指数**：$\text{FMI} = \sqrt{\frac{a}{a+b}\cdot\frac{a}{a+c}}$
- **Rand 指数**：$\text{RI} = \frac{2(a+d)}{m(m-1)}$

### 内部指标

不利用参考模型，直接考察聚类本身。建立在簇内样本间距离（intra-cluster）和簇间样本间距离（inter-cluster）之上：
- **DB 指数**（Davies-Bouldin Index）：簇内距离均值之和除以簇间距，越小越好。
- **Dunn 指数**：最小簇间距与最大簇内距离之比，越大越好。

## 距离计算

对函数 $\text{dist}(\cdot,\cdot)$，若满足非负性、同一性、对称性、直递性（三角不等式），则称为度量。

- **闵可夫斯基距离**：$\text{dist}_{mk}(\boldsymbol{x}_i,\boldsymbol{x}_j) = \left(\sum_u |x_{iu}-x_{ju}|^p\right)^{1/p}$
  - $p=2$ 为欧氏距离
  - $p=1$ 为曼哈顿距离
- **VDM（Value Difference Metric）**：用于无序属性，基于属性值在各簇中出现频率的差异度量。
- 混合属性距离可将闵氏距离和 VDM 组合。

不同距离度量可能影响聚类结果。当属性重要性不同时，可使用加权距离。

## 原型聚类

原型聚类假设聚类结构能通过一组原型刻画。

### k-Means 算法

k-Means 是最经典的聚类算法：

1. 随机选择 $k$ 个样本作为初始均值向量（质心）。
2. 将每个样本划入距其最近的质心所属的簇。
3. 根据新划分重新计算各簇质心（取簇内样本均值）。
4. 重复步骤 2-3 直到质心不再变化或变化小于阈值。

目标函数（最小化平方误差）：
$$E = \sum_{i=1}^{k}\sum_{\boldsymbol{x} \in C_i}\|\boldsymbol{x} - \boldsymbol{\mu}_i\|_2^2$$

$k$ 值需预先指定，可通过肘部法或轮廓系数选择。初始质心选择影响结果，k-Means++ 优化了初始化策略。

### 学习向量量化（LVQ）

LVQ 假设数据样本带有类标记（监督信息），基于原型向量进行分类学习，而非纯聚类。通过对样本的"胜者为王"（WTA）策略更新原型向量。

### 高斯混合聚类（GMM）

假设数据由多个高斯分布混合生成，用 EM 算法估计各高斯分量的参数（均值、协方差、混合系数），最终根据后验概率确定簇归属。GMM 可产生"软聚类"结果（样本以概率属于各簇）。

## 密度聚类

密度聚类假设聚类结构能通过样本分布的紧密程度确定，能发现任意形状的簇。

### DBSCAN

DBSCAN（Density-Based Spatial Clustering of Applications with Noise）基于一组"邻域"参数（$\epsilon$, MinPts）刻画样本分布的紧密程度：

- **$\epsilon$-邻域**：给定样本 $\boldsymbol{x}_j$，其 $\epsilon$-邻域包含距它不超过 $\epsilon$ 的所有样本。
- **核心对象**：$\epsilon$-邻域内至少包含 MinPts 个样本的对象。
- **密度直达/可达/相连**：通过核心对象和邻域关系建立样本间的连接。

DBSCAN 从核心对象出发，将所有密度可达的样本连成一个簇。不在任何簇中的样本标记为噪声。DBSCAN 不需预先指定簇数，但对 $\epsilon$ 和 MinPts 敏感。

## 层次聚类

层次聚类在不同层次对数据集进行划分，形成树形聚类结构。

### AGNES

AGNES（Agglomerative Nesting）是自底向上的聚合策略：

1. 初始时每个样本为一个簇。
2. 找到距离最近的两个簇进行合并。
3. 重复直到达到预设簇数。

簇间距离计算方式：
- **单链接**（single-linkage）：取两簇最近样本间距离。
- **全链接**（complete-linkage）：取两簇最远样本间距离。
- **均链接**（average-linkage）：取两簇所有样本对的平均距离。

## 降维

维数灾难（curse of dimensionality）：高维空间中样本稀疏、距离计算困难，且易导致过拟合。降维是缓解维数灾难的有效途径。

### 低维嵌入

多维缩放（MDS）要求降维后样本间距离保持不变：
$$\min_{\mathbf{Z}} \sum_{i=1}^{m}\sum_{j=1}^{m}(\|\boldsymbol{z}_i - \boldsymbol{z}_j\| - \text{dist}_{ij})^2$$

通过对内积矩阵 $\mathbf{B} = \mathbf{Z}\mathbf{Z}^\top$ 做特征值分解求解。

### 主成分分析（PCA）

PCA 是最常用的降维方法，目标是找一个超平面对样本进行恰当表达：

1. 对所有样本进行中心化：$\boldsymbol{x}_i \leftarrow \boldsymbol{x}_i - \frac{1}{m}\sum_j \boldsymbol{x}_j$。
2. 计算样本协方差矩阵 $\mathbf{X}\mathbf{X}^\top$。
3. 对协方差矩阵做特征值分解。
4. 取最大的 $d'$ 个特征值对应的特征向量构成投影矩阵 $\mathbf{W}$。
5. 投影：$\boldsymbol{z}_i = \mathbf{W}^\top \boldsymbol{x}_i$。

PCA 使投影后样本各维度方差最大（信息保留最多），且各维度线性无关。等价于对协方差矩阵做特征值分解，或对中心化数据矩阵做 SVD。

### 核化线性降维（KPCA）

当样本在高维特征空间中线性可分时，将核方法引入 PCA：在核化的特征空间中执行 PCA，通过核函数计算内积而不显式映射到高维。

### 流形学习

流形学习借鉴"流形假设"（高维数据在一个低维流形上），从高维采样数据中恢复低维流形结构。

- **等度量映射（Isomap）**：用测地线距离（流形上的最短路径）替代欧氏距离，建立近邻图后用最短路径算法近似测地线距离，再用 MDS 降维。
- **局部线性嵌入（LLE）**：保持邻域内样本间的线性重构关系，先为每个样本找近邻并计算重构权重，再在低维空间保持重构权重不变。

### 度量学习

度量学习尝试学习出一个合适的距离度量，马氏距离对应的度量矩阵 $\mathbf{M}$ 可通过学习得到。NCA（邻域成分分析）和 ITML（信息理论度量学习）是代表性方法。

## 特征选择与稀疏学习

### 特征选择的动机

- 减轻维数灾难、降低学习任务难度
- 去除不相关特征，降低学习难度
- 提高模型可解释性

特征选择与降维的区别：特征选择从原始特征中选出子集（保留原特征语义），降维对特征做映射变换（产生新特征）。

### 三类方法

- **过滤式（filter）**：先进行特征选择再训练学习器，特征选择过程与学习器无关。代表：Relief（Relief-F），基于"相关统计量"度量特征重要性。
- **包裹式（wrapper）**：直接把学习器性能作为特征子集的评价准则。代表：LVW（Las Vegas Wrapper），在特征子集空间中随机搜索。效果好但计算开销大。
- **嵌入式（embedding）**：特征选择过程与学习器训练过程融为一体，在优化目标中加入 L1 正则化（Lasso）自动进行特征选择。$\ell_1$ 正则化产生稀疏解，使部分特征权重恰好为零。

### 稀疏表示与字典学习

- **稀疏表示**：用尽可能少的字典原子线性表达样本，获得稀疏解。
- **字典学习**：学习一组基向量（字典），使样本能被稀疏表示。KSVD 是经典算法。
- **压缩感知**：在信号稀疏可压缩前提下，可通过远低于奈奎斯特采样率的观测恢复原始信号。
