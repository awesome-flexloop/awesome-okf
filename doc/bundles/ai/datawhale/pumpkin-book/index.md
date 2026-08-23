---
okf_version: "0.2"
type: index
title: "南瓜书（pumpkin-book）"
bundle: pumpkin-book
description: "Datawhale 开源的西瓜书公式推导伴读——对周志华《机器学习》中较难理解的公式补充完整推导细节，覆盖模型评估、线性模型、决策树、神经网络、SVM、贝叶斯、集成学习、聚类、降维、特征选择等16章"
concepts:
  - /datawhale/pumpkin-book/concepts/positioning-and-usage
  - /datawhale/pumpkin-book/concepts/model-evaluation-and-selection
  - /datawhale/pumpkin-book/concepts/linear-models-and-decision-trees
  - /datawhale/pumpkin-book/concepts/neural-networks-and-svm
  - /datawhale/pumpkin-book/concepts/bayesian-and-ensemble-learning
  - /datawhale/pumpkin-book/concepts/clustering-and-dimensionality-reduction
references:
  - /datawhale/pumpkin-book/references/ch1-2-foundations
  - /datawhale/pumpkin-book/references/ch3-4-linear-tree
  - /datawhale/pumpkin-book/references/ch5-6-nn-svm
  - /datawhale/pumpkin-book/references/ch7-8-bayes-ensemble
  - /datawhale/pumpkin-book/references/ch9-11-clustering-dim-feature
  - /datawhale/pumpkin-book/references/ch12-16-advanced
  - /datawhale/pumpkin-book/references/errata
examples:
  - /datawhale/pumpkin-book/examples/linear-regression-derivation
  - /datawhale/pumpkin-book/examples/svm-dual-derivation
  - /datawhale/pumpkin-book/examples/bp-backpropagation
sources: https://github.com/datawhalechina/pumpkin-book
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-23T00:00:00Z"
status: stable
stale_after: "2027-08-23"
---

# 南瓜书（pumpkin-book）

[南瓜书](https://github.com/datawhalechina/pumpkin-book) 是 Datawhale 开源的机器学习公式推导伴读书，对周志华教授《机器学习》（西瓜书）中较难理解的公式加以解析，并补充具体的推导细节。全书 16 章与西瓜书严格一一对应，以本科数学基础（高等数学、线性代数、概率论与数理统计）为起点，帮助读者消除阅读西瓜书时的"数学恐惧"。

## 知识地图

```
📖 基础篇（第1-2章）
  ├── 绪论 → 基本术语、假设空间、归纳偏好、NFL定理
  └── 模型评估与选择 → 误差/过拟合、留出法/交叉验证、性能度量（P/R/F1/ROC/AUC）
        ↓
📐 经典模型篇（第3-8章）
  ├── 线性模型 → 线性回归、对数几率回归、线性判别分析（LDA）
  ├── 决策树 → 信息增益/增益率/基尼指数、剪枝、连续缺失值
  ├── 神经网络 → M-P神经元、感知机、BP反向传播、深度学习
  ├── 支持向量机 → 间隔最大化、核函数、软间隔、SVR
  ├── 贝叶斯分类器 → 贝叶斯决策论、朴素贝叶斯、贝叶斯网、EM算法
  └── 集成学习 → Boosting(AdaBoost)、Bagging、随机森林、结合策略
        ↓
🔍 无监督与进阶篇（第9-16章）
  ├── 聚类 → k-Means、DBSCAN、层次聚类、性能度量
  ├── 降维与度量学习 → PCA、KPCA、Isomap、LLE、度量学习
  ├── 特征选择与稀疏学习 → 过滤式/包裹式/嵌入式、L1正则、压缩感知
  ├── 计算学习理论 → PAC学习、VC维、Rademacher复杂度
  ├── 半监督学习 → 生成式方法、半监督SVM、图半监督
  ├── 概率图模型 → HMM、MRF、CRF、话题模型、词向量
  ├── 规则学习 → 序贯覆盖、剪枝、一阶规则、归纳逻辑程序
  └── 强化学习 → MDP、策略迭代、Q-Learning、模仿学习
```

## 核心概念（concepts/）

| 概念 | 内容 |
|------|------|
| [南瓜书定位与使用方法](concepts/positioning-and-usage.md) | 南瓜书与西瓜书的互补关系、推荐使用方法、数学基础要求、配套资源 |
| [模型评估与选择](concepts/model-evaluation-and-selection.md) | 经验误差与过拟合、留出法/交叉验证法/自助法、查准率查全率F1、ROC与AUC、偏差方差权衡 |
| [线性模型与决策树](concepts/linear-models-and-decision-trees.md) | 线性回归最小二乘、对数几率回归、LDA、信息增益/增益率/基尼指数、剪枝 |
| [神经网络与SVM](concepts/neural-networks-and-svm.md) | M-P神经元、感知机、BP反向传播算法、间隔最大化、核函数、软间隔与SVR |
| [贝叶斯与集成学习](concepts/bayesian-and-ensemble-learning.md) | 贝叶斯决策论、朴素贝叶斯、EM算法、AdaBoost、Bagging、随机森林、结合策略 |
| [聚类与降维](concepts/clustering-and-dimensionality-reduction.md) | k-Means/DBSCAN/层次聚类、性能度量、PCA主成分分析、流形学习、特征选择 |

## 推导示例（examples/）

| 示例 | 内容 |
|------|------|
| [线性回归最小二乘推导](examples/linear-regression-derivation.md) | 一元线性回归参数 w 和 b 的最小二乘估计完整推导，多元线性回归的矩阵形式 |
| [SVM对偶问题推导](examples/svm-dual-derivation.md) | 间隔最大化原问题→拉格朗日对偶→KKT条件→支持向量的完整推导链路 |
| [BP反向传播算法推导](examples/bp-backpropagation.md) | 单隐层网络误差逆传播的链式法则推导，输出层与隐层梯度公式 |

## 信源登记（references/）

| 信源 | 内容 |
|------|------|
| [第1-2章：绪论与模型评估](references/ch1-2-foundations.md) | 基本术语、假设空间、评估方法、性能度量 |
| [第3-4章：线性模型与决策树](references/ch3-4-linear-tree.md) | 线性回归、对数几率回归、LDA、决策树划分选择与剪枝 |
| [第5-6章：神经网络与SVM](references/ch5-6-nn-svm.md) | 感知机、BP算法、间隔与支持向量、核函数、软间隔 |
| [第7-8章：贝叶斯与集成学习](references/ch7-8-bayes-ensemble.md) | 贝叶斯决策论、朴素贝叶斯、EM、Boosting、Bagging |
| [第9-11章：聚类、降维与特征选择](references/ch9-11-clustering-dim-feature.md) | 聚类算法、PCA/流形学习、特征选择三方法 |
| [第12-16章：进阶主题](references/ch12-16-advanced.md) | 计算学习理论、半监督学习、概率图模型、规则学习、强化学习 |
| [勘误表](references/errata.md) | 纸质版各印次公式与文字勘误汇总 |

## 学习路径推荐

### 路径1：公式查阅（以西瓜书为主线）

```
西瓜书阅读 → 遇到推导困难的公式 → 查阅南瓜书对应章节 → 配合B站视频理解
```

### 路径2：系统学习（组队学习节奏）

```
第1章(1.5天) → 第2章(1.5天，可延后) → 第3章(9天) → 第4章(3天)
→ 第5章(3天) → 第6章(3天) → 第7章(3天) → 第8章(3天)
→ 第9章(3天) → 第10章(3天) → 第11章(3天) → ...
```

> 提示：零基础读者建议第1、2章公式简单过一遍即可，学完第3-6章后再回看第2章会轻松很多。

## 核心洞察

1. **公式推导驱动的理解方法**：南瓜书以公式编号为锚点，补上西瓜书省略的代数变形与求导过程，让读者从"记住结论"走向"复现推导"，建立算法的数学心智模型。
2. **西瓜书-南瓜书互补共生**：西瓜书提供知识骨架（动机/直觉/伪代码），南瓜书填充数学血肉（推导/证明/符号），二者章节严格一一对应，不可独立使用。
3. **本科数学基础的最小完备集**：高等数学（优化求解）、线性代数（矩阵运算）、概率论（概率模型）三门课贯穿16章，超纲内容以附录形式补充。

## 版本信息

- **配套西瓜书版次**：2016年1月第1版
- **许可证**：CC BY-NC-SA 4.0
- **官方仓库**：https://github.com/datawhalechina/pumpkin-book
- **在线阅读**：https://datawhalechina.github.io/pumpkin-book/
- **配套视频**：https://www.bilibili.com/video/BV1Mh411e7VU
