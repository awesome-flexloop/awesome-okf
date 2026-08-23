---
type: reference
title: "第7-8章：贝叶斯分类器与集成学习"
bundle: /datawhale/pumpkin-book
description: "第7章贝叶斯分类器（贝叶斯决策论/朴素贝叶斯/贝叶斯网/EM）与第8章集成学习（Boosting/Bagging/随机森林/结合策略）"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter7/chapter7.md
path: docs/chapter7/chapter7.md, docs/chapter8/chapter8.md
tags: [bayesian, naive-bayes, bayesian-network, em, ensemble, boosting, adaboost, bagging, random-forest]
status: stable
---

# 第7-8章：贝叶斯分类器与集成学习

## 信源信息

- **第7章文件路径**：`docs/chapter7/chapter7.md`
- **第7章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter7/chapter7.md
- **第8章文件路径**：`docs/chapter8/chapter8.md`
- **第8章 GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter8/chapter8.md

## 第7章内容概要

本章从概率框架的贝叶斯视角建模，理论性较强：

- **7.1 贝叶斯决策论**：
  - 式(7.1)~式(7.5)后验概率与贝叶斯最优分类器推导
  - 最小错误率决策与最小风险决策
  - 贝叶斯定理：$P(c|\boldsymbol{x}) = P(\boldsymbol{x}|c)P(c)/P(\boldsymbol{x})$
- **7.2 极大似然估计**：
  - 式(7.9)~式(7.12)对数似然函数与参数估计
  - 高斯假设下均值和方差的MLE推导
  - 频率主义vs贝叶斯主义的参数观
- **7.3 朴素贝叶斯分类器**：
  - 属性条件独立性假设
  - 式(7.14)~式(7.17)后验概率计算与拉普拉斯修正
  - 文本分类应用（垃圾邮件检测）
- **7.4 半朴素贝叶斯分类器**：
  - 适当放松独立性假设，ODE/SPODE/AODE/TAN
- **7.5 贝叶斯网**：
  - 有向无环图（DAG）与条件概率表（CPT）
  - 结构学习（MDL评分搜索）、参数学习
  - 推断（变量消去/吉布斯采样近似推断）
- **7.6 EM算法**：
  - 隐变量模型的参数估计
  - E步（计算Q函数/后验概率期望）与M步（最大化Q函数更新参数）
  - 收敛到局部极大值，GMM和HMM的Baum-Welch是典型应用

组队学习时间：3天。贝叶斯网和EM可与第14章概率图模型合并学习。

## 第8章内容概要

集成学习组合多个学习器获得更优性能：

- **8.1 个体与集成**：
  - 同质/异质集成、基学习器
  - "好而不同"的个体学习器要求
  - 误差-分歧分解（式8.10，集成泛化误差=平均误差-平均分歧）
- **8.2 Boosting**：
  - 串行集成，每轮关注错分样本
  - 式(8.1)~式(8.11)AdaBoost完整推导：
    - 样本权重初始化与更新
    - 基学习器权重 $\alpha_t = \frac{1}{2}\ln\frac{1-\epsilon_t}{\epsilon_t}$
    - 指数损失函数视角
    - 前向分步加性模型解释
  - Boosting主要降低偏差
- **8.3 Bagging与随机森林**：
  - Bagging：自助采样+并行集成+投票/平均，包外估计
  - 随机森林：Bagging+随机属性选择（每节点随机选k个属性），双重随机性
  - Bagging主要降低方差
- **8.4 结合策略**：
  - 平均法（简单平均/加权平均）
  - 投票法（绝对多数/相对多数/加权投票）
  - 学习法（Stacking堆叠泛化）
- **8.5 多样性**：
  - 多样性度量（不合度量/相关系数/Q统计量/κ统计量）
  - 多样性增强（数据样本扰动/输入属性扰动/输出表示扰动/算法参数扰动）

组队学习时间：3天（含两个视频教程p=12和p=13）。

## 对应概念

- [贝叶斯与集成学习](../concepts/bayesian-and-ensemble-learning.md)
