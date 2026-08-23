---
type: reference
title: "第1-2章：绪论与模型评估与选择"
bundle: /datawhale/pumpkin-book
description: "第1章绪论（基本术语/假设空间/归纳偏好/NFL定理）与第2章模型评估与选择（误差/评估方法/性能度量）"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter1/chapter1.md
path: docs/chapter1/chapter1.md, docs/chapter2/chapter2.md
tags: [introduction, terminology, evaluation, cross-validation, metrics]
status: stable
---

# 第1-2章：绪论与模型评估与选择

## 信源信息

- **第1章文件路径**：`docs/chapter1/chapter1.md`
- **第1章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter1/chapter1.md
- **第2章文件路径**：`docs/chapter2/chapter2.md`
- **第2章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter2/chapter2.md
- **第1章法语版**：`docs/chapter1/chapter1_FR.md`
- **第2章法语版**：`docs/chapter2/chapter2_FR.md`
- **第2章资源**：`docs/chapter2/resources/images/roc.png`（ROC曲线图）

## 第1章内容概要

绪论作为西瓜书和南瓜书的开篇，主要讲解：

- **1.1 引言**：算法与模型的区分、算法产出模型、模型是具体函数
- **1.2 基本术语**：样本/示例、样本空间/属性空间、数据集、训练集/测试集、模型/学习器、标记/标记空间、分类（二分类/多分类）、回归、监督学习/无监督学习、泛化、分布（独立同分布假设）
- **1.3 假设空间**：假设空间与版本空间的概念，以房价预测为例说明一元线性回归和多项式回归对应不同假设空间，所有能拟合训练集的模型构成版本空间
- **1.4 归纳偏好**：不同算法有不同偏好，奥卡姆剃刀原则，NFL（没有免费的午餐）定理——式(1.1)和式(1.2)的推导说明所有算法期望性能相同

组队学习时间：1.5天。配套视频：BV1Mh411e7VU?p=2。

## 第2章内容概要

模型评估与选择讲述如何评估模型优劣：

- **2.1 经验误差与过拟合**：错误率/精度、误差/经验误差/泛化误差、过拟合与欠拟合的辨析
- **2.2 评估方法**：留出法、交叉验证法（k折/留一法）、自助法（bootstrapping，包外估计）；超参数与模型参数的区别；验证集的概念与调参流程
- **2.3 性能度量**：
  - 式(2.2)~式(2.7)：错误率/精度的均匀分布与一般分布表达式
  - 式(2.8)~式(2.9)：查准率P与查全率R
  - P-R曲线与平衡点（BEP）、F1度量（式2.10）、macro-F1/micro-F1
  - ROC曲线与AUC（式2.20~2.22），ROC曲线绘制方法
  - 代价敏感错误率与代价曲线
- **2.4 比较检验**：假设检验（二项检验/t检验）、交叉验证t检验、Friedman检验与Nemenyi后续检验
- **2.5 偏差与方差**：偏差-方差分解，偏差主导（欠拟合）与方差主导（过拟合）

组队学习时间：1.5天。本章建议零基础读者简单泛读，学完第3-6章后再回看。

## 对应概念

- [南瓜书定位与使用方法](../concepts/positioning-and-usage.md)
- [模型评估与选择](../concepts/model-evaluation-and-selection.md)
