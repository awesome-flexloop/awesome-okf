---
type: concept
title: "模型评估与选择"
bundle: /datawhale/pumpkin-book
description: "经验误差与过拟合、评估方法（留出法/交叉验证/自助法）、性能度量（P/R/F1/ROC/AUC）、比较检验与偏差方差权衡"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter2/chapter2.md
related:
  - /datawhale/pumpkin-book/concepts/linear-models-and-decision-trees
  - /datawhale/pumpkin-book/concepts/positioning-and-usage
  - /datawhale/pumpkin-book/examples/linear-regression-derivation
  - /datawhale/pumpkin-book/references/ch1-2-foundations
tags: [evaluation, overfitting, cross-validation, roc, auc, bias-variance]
status: stable
---

# 模型评估与选择

模型评估与选择是机器学习流程中的下游环节，回答"如何评估模型优劣"和"如何选择最适合业务场景的模型"两个核心问题。南瓜书建议零基础读者先简单泛读本章或直接跳过，学完第3-6章具体算法后再回看。

## 经验误差与过拟合

**基本概念辨析**：

- **错误率**（error rate）：$E = \frac{a}{m}$，其中 $m$ 为样本总数，$a$ 为分类错误样本数。
- **精度**（accuracy）：精度 = 1 - 错误率。
- **误差**（error）：学习器实际预测输出与样本真实输出之间的差异。
- **经验误差**（empirical error）：学习器在训练集上的误差，又称训练误差。
- **泛化误差**（generalization error）：学习器在新样本（未见过的样本）上的误差。

**过拟合与欠拟合**：

- **过拟合**（overfitting）：模型学习能力相对于数据过于强大，把训练样本自身的特点当作了潜在规律，导致泛化性能下降。
- **欠拟合**（underfitting）：模型学习能力低下，连训练样本的一般性质都没学好。

过拟合无法彻底避免，只能"缓解"。机器学习的一个重要挑战就是"缓解过拟合"。

## 评估方法

评估方法的核心是如何将数据集划分为训练集和测试集。

### 留出法（hold-out）

直接将数据集 $D$ 划分为两个互斥集合：训练集 $S$ 和测试集 $T$，即 $D = S \cup T$，$S \cap T = \varnothing$。

- 操作最简单，最常用。
- 训练/测试集划分要尽可能保持数据分布一致性（分层采样）。
- 单次留出法结果不够稳定，通常多次随机划分重复实验取平均值。

### 交叉验证法（cross-validation）

将数据集 $D$ 划分为 $k$ 个大小相似的互斥子集 $D_1, D_2, \ldots, D_k$，每次用 $k-1$ 个子集训练、1个子集测试，共进行 $k$ 次训练和测试，最终取 $k$ 次结果的均值。

- $k$ 最常用的取值是 10，即 10 折交叉验证。
- 常用于对比同一算法的不同参数配置，或对比不同算法之间的效果。
- 本质是多次留出法，每次换不同子集做测试集，让所有样本至少做一次测试样本。

留一法（Leave-One-Out，LOO）是 $k=m$ 的特例，不受随机样本划分影响，但计算开销大。

### 自助法（bootstrapping）

给定包含 $m$ 个样本的数据集 $D$，有放回地采样 $m$ 次得到数据集 $D'$。样本在 $m$ 次采样中始终不被采到的概率为 $(1-\frac{1}{m})^m$，取极限得 $\frac{1}{e} \approx 0.368$，即约 36.8% 的样本不出现训练集中，这些样本用作测试集（包外估计，out-of-bag estimate）。

- 在数据集较小、难以有效划分训练/测试集时很有用。
- 常用于集成学习（如 Bagging）产生基分类器。
- 改变了初始数据集的分布，会引入估计偏差，数据量足够时优先使用留出法和交叉验证法。

### 超参数与模型参数

- **算法参数（超参数）**：算法本身的配置参数，如 $k$ 近邻的近邻数 $k$、SVM 的惩罚参数 $C$。超参数通过验证集表现来选择。
- **模型参数**：算法训练后得到的参数，如线性回归的权重 $\boldsymbol{w}$ 和偏置 $b$、SVM 的支持向量。

### 验证集（validation set）

实际工程中常用做法：先用留出法划分训练集和测试集，再从训练集中划出一部分作为验证集，基于验证集调参选出最优超参数，最后用最优配置在全部训练集上重新训练，用测试集评估最终性能。

## 性能度量

### 错误率与精度

最基本的度量，适用于分类和回归任务。式(2.2)~式(2.7)分别给出了均匀分布和一般分布下的定义式。

### 查准率、查全率与 F1

对于二分类问题，可将样本真实类别与学习器预测类别的组合划分为：

- **TP**（真正例，true positive）：预测为正、实际为正
- **FP**（假正例，false positive）：预测为正、实际为负
- **TN**（真反例，true negative）：预测为负、实际为负
- **FN**（假反例，false negative）：预测为负、实际为正

**查准率**（precision）：
$$P = \frac{TP}{TP + FP}$$
被预测为正例的样例中，真正正例的比例。

**查全率**（recall）：
$$R = \frac{TP}{TP + FN}$$
所有真正正例中，被成功预测出的比例。

查准率和查全率通常是一对矛盾的度量。P-R 曲线以查准率为纵轴、查全率为横轴，曲线下面积或平衡点（BEP）可用于比较模型。

**F1 度量**：
$$F1 = \frac{2 \times P \times R}{P + R} = \frac{2 \times TP}{\text{样本总数} + TP - TN}$$

F1 是查准率和查全率的调和平均。在多分类场景下有 macro-F1（先各分类别P/R再平均）和 micro-F1（先全局累加TP/FP/TN/FN再计算）。

### ROC 与 AUC

**ROC**（Receiver Operating Characteristic，受试者工作特征）曲线以**真正例率**（TPR）为纵轴、**假正例率**（FPR）为横轴：

$$TPR = \frac{TP}{TP + FN}, \quad FPR = \frac{FP}{TN + FP}$$

ROC 曲线通过依次改变分类阈值绘制。对角线对应随机猜测模型，点(0,1)对应理想模型。

**AUC**（Area Under ROC Curve）是 ROC 曲线下的面积，值越大模型性能越好。AUC 可通过对排序损失求补得到：

$$AUC = 1 - \ell_{rank}$$

### 代价敏感错误率

当不同类型错误的代价不同时（如医疗诊断中将患者误诊为健康的代价远高于反向），需要引入代价矩阵，计算代价敏感错误率。

## 比较检验

- **假设检验**：二项检验、t 检验，基于测试错误率推断泛化错误率。
- **交叉验证 t 检验**：对 k 折交叉验证的结果做成对 t 检验。
- **Friedman 检验与 Nemenyi 后续检验**：多个算法在多个数据集上的比较。

## 偏差与方差

偏差-方差分解（bias-variance decomposition）是解释算法泛化性能的重要框架：

$$E(f;D) = \text{bias}^2(\boldsymbol{x}) + \text{var}(\boldsymbol{x}) + \varepsilon^2$$

- **偏差**（bias）：学习算法的期望预测与真实结果的偏离程度，刻画模型本身的拟合能力。
- **方差**（variance）：同样大小的训练集变动导致的学习性能变化，刻画数据扰动造成的影响。
- **噪声**（noise）：当前任务任何模型所能达到的期望泛化误差下界，刻画问题本身的难度。

偏差与方差通常存在冲突：训练不足时偏差主导（欠拟合），训练加深后方差逐渐主导（过拟合）。
