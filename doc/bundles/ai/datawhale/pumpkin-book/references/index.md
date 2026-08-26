---
okf_version: "0.2"
type: index
title: "南瓜书信源登记"
bundle: /datawhale/pumpkin-book
description: "南瓜书全部16章文档与勘误表的信源登记"
sources: https://github.com/datawhalechina/pumpkin-book
---

# 信源登记簿

本目录登记南瓜书全部 16 章文档和勘误表的信源信息。所有概念文档和示例文档的 `sources` 字段均指向 GitHub 源码仓库中的对应章节。

## 基础篇（第1-2章）

* [第1-2章：绪论与模型评估与选择](ch1-2-foundations.md) — 基本术语、假设空间、归纳偏好；经验误差、评估方法、性能度量（P/R/F1/ROC/AUC）。

## 经典模型篇（第3-8章）

* [第3-4章：线性模型与决策树](ch3-4-linear-tree.md) — 线性回归、对数几率回归、LDA；信息增益/增益率/基尼指数、剪枝、连续缺失值。
* [第5-6章：神经网络与支持向量机](ch5-6-nn-svm.md) — 感知机、BP反向传播；间隔最大化、对偶问题、核函数、软间隔、SVR。
* [第7-8章：贝叶斯分类器与集成学习](ch7-8-bayes-ensemble.md) — 贝叶斯决策论、朴素贝叶斯、贝叶斯网、EM；AdaBoost、Bagging、随机森林、结合策略。

## 无监督与进阶篇（第9-16章）

* [第9-11章：聚类、降维与特征选择](ch9-11-clustering-dim-feature.md) — k-Means/DBSCAN/层次聚类、PCA/KPCA/流形学习、过滤式/包裹式/嵌入式特征选择。
* [第12-16章：进阶主题](ch12-16-advanced.md) — 计算学习理论、半监督学习、概率图模型、规则学习、强化学习。

## 勘误

* [勘误表](errata.md) — 纸质版各印次（第2版第6次印刷至第1版第4次印刷）的公式与文字勘误汇总。

```{toctree}
:maxdepth: 7

ch1-2-foundations
ch12-16-advanced
ch3-4-linear-tree
ch5-6-nn-svm
ch7-8-bayes-ensemble
ch9-11-clustering-dim-feature
errata
```
