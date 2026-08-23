---
okf_version: "0.2"
type: index
title: "南瓜书核心概念"
bundle: /datawhale/pumpkin-book
description: "南瓜书核心概念文档导航"
sources: https://github.com/datawhalechina/pumpkin-book
---

# 核心概念

本目录包含南瓜书（西瓜书公式推导伴读）的 6 个核心概念文档，按学习路径排列：从定位与使用方法入手，再按西瓜书章节顺序覆盖模型评估、经典监督模型、概率模型与无监督学习。

## 使用入门

* [南瓜书定位与使用方法](positioning-and-usage.md) — 南瓜书与西瓜书的互补关系、推荐使用方法（以西瓜书为主线、按需查阅）、数学基础要求、配套视频与代码资源。

## 基础与评估

* [模型评估与选择](model-evaluation-and-selection.md) — 经验误差与过拟合、留出法/交叉验证法/自助法、超参数与模型参数、查准率查全率F1、ROC与AUC、偏差与方差。

## 经典监督模型

* [线性模型与决策树](linear-models-and-decision-trees.md) — 线性回归最小二乘、对数几率回归、线性判别分析LDA；信息增益/增益率/基尼指数三种划分选择、剪枝处理、连续与缺失值。
* [神经网络与SVM](neural-networks-and-svm.md) — M-P神经元模型、感知机学习规则、BP误差逆传播算法、间隔与支持向量、核函数、软间隔与支持向量回归。

## 概率模型与集成

* [贝叶斯与集成学习](bayesian-and-ensemble-learning.md) — 贝叶斯决策论与极大似然、朴素贝叶斯、贝叶斯网、EM算法；Boosting(AdaBoost)、Bagging与随机森林、结合策略。

## 无监督学习

* [聚类与降维](clustering-and-dimensionality-reduction.md) — 聚类性能度量、k-Means/DBSCAN/层次聚类；PCA主成分分析、KPCA核化降维、流形学习(Isomap/LLE)；特征选择三方法。
