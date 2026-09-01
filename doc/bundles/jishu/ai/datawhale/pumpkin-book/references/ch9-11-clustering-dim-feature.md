---
type: reference
title: "第9-11章：聚类、降维与特征选择"
bundle: /datawhale/pumpkin-book
description: "第9章聚类（k-Means/DBSCAN/层次聚类）、第10章降维与度量学习（PCA/KPCA/流形学习）、第11章特征选择与稀疏学习"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter9/chapter9.md
path: docs/chapter9/chapter9.md, docs/chapter10/chapter10.md, docs/chapter11/chapter11.md
tags: [clustering, kmeans, dbscan, hierarchical, pca, mds, manifold, feature-selection, sparse-learning]
status: stable
---

# 第9-11章：聚类、降维与特征选择

## 信源信息

- **第9章文件路径**：`docs/chapter9/chapter9.md`
- **第9章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter9/chapter9.md
- **第10章文件路径**：`docs/chapter10/chapter10.md`
- **第10章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter10/chapter10.md
- **第11章文件路径**：`docs/chapter11/chapter11.md`
- **第11章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter11/chapter11.md

## 第9章内容概要

聚类是无监督学习的代表任务：

- **9.1 聚类任务**：簇的概念，聚类vs分类（有无标记）
- **9.2 性能度量**：
  - 外部指标：Jaccard系数(JC)、FM指数、Rand指数(RI)
  - 内部指标：DB指数(DBI)、Dunn指数(DI)
  - 式(9.1)~式(9.13)各指标推导
- **9.3 距离计算**：
  - 闵可夫斯基距离（欧氏距离p=2/曼哈顿距离p=1）
  - VDM（无序属性距离度量）
  - 混合属性距离加权组合
- **9.4 原型聚类**：
  - k-Means算法（式9.18~9.21目标函数与更新规则）
  - 学习向量量化(LVQ，利用监督信息)
  - 高斯混合聚类(GMM，EM算法求解，软聚类)
- **9.5 密度聚类**：
  - DBSCAN算法（$\epsilon$-邻域/MinPts/核心对象/密度直达/可达/相连）
  - 能发现任意形状簇，标记噪声点
- **9.6 层次聚类**：
  - AGNES自底向上聚合
  - 单链接/全链接/均链接三种簇间距离

组队学习时间：3天。

## 第10章内容概要

降维缓解维数灾难，本章需要较多线性代数基础：

- **10.1 预备知识**：
  - 符号约定（分号=列向量，逗号=行向量）
  - 线性代数与矩阵分析基础（特征值分解/SVD/矩阵求导/迹运算）
- **10.2 k近邻学习**：
  - 懒惰学习、$k$值选择、投票机制
  - 错误率上界（不超过贝叶斯最优分类器错误率两倍）
- **10.3 低维嵌入**：
  - 多维缩放(MDS)：保持降维前后样本间距离不变
  - 式(10.5)~式(10.12)内积矩阵特征值分解推导
- **10.4 主成分分析（PCA）**：
  - 最近重构性与最大可分性两种等价推导
  - 式(10.14)~式(10.17)协方差矩阵特征值分解
  - 中心化→协方差矩阵→特征值分解→取前d'个特征向量
- **10.5 核化线性降维**：
  - KPCA：核技巧在PCA中的应用
  - 式(10.25)~式(10.28)核矩阵特征值分解
- **10.6 流形学习**：
  - 等度量映射(Isomap)：测地线距离+MDS
  - 局部线性嵌入(LLE)：保持邻域线性重构权重
  - 式(10.28)~式(10.35)LLE推导
- **10.7 度量学习**：
  - 马氏距离与度量矩阵M学习
  - NCA、ITML等方法

组队学习时间：3天（含两个视频教程p=15和p=16）。

## 第11章内容概要

特征选择从原始特征中选取相关特征子集：

- **11.1 子集搜索与评价**：
  - 前向/后向/双向搜索
  - 信息增益作为子集评价准则（式11.1，与决策树相同）
  - 特征选择vs降维：保留原特征vs产生新特征
- **11.2 过滤式选择（filter）**：
  - Relief：基于"猜中近邻"和"猜错近邻"的相关统计量
  - Relief-F多分类扩展
- **11.3 包裹式选择（wrapper）**：
  - LVW(Las Vegas Wrapper)：以学习器性能为评价准则
  - 随机搜索+交叉验证，效果好但计算开销大
- **11.4 嵌入式选择与L1正则化**：
  - 特征选择与训练过程融合
  - L1正则化(Lasso)产生稀疏解，自动特征选择
  - L2正则化(Ridge) vs L1正则化，L1稀疏性几何解释
- **11.5 稀疏表示与字典学习**：
  - 稀疏表示：用最少字典原子表达样本
  - 字典学习（KSVD算法）
- **11.6 压缩感知**：
  - 信号稀疏可压缩前提
  - 欠采样条件下通过$\ell_1$范数恢复原始信号
  - 等距约束性(RIP)
- **11.7 阅读材料**：决策树与特征选择的关系、L1正则化优化方法

组队学习时间：3天。

## 对应概念

- [聚类与降维](../concepts/clustering-and-dimensionality-reduction.md)
