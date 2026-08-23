---
title: 第2章 可学性
type: reference
bundle: /datawhale/key-book
chapter: 2
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter2.md
---

# 第2章：可学性

> 来源：`docs/chapter2.md`，编辑：赵志民、王茂霖、李一飞、詹好

本章围绕"事件是否能够通过机器学习来解决"展开，引入 PAC 学习框架，是[可学性](/datawhale/key-book/concepts/learnability)概念的主体章节。

## 内容概要

### 2.1 概念与假设空间

- **输入空间** $\mathcal{X}$：所有可能实例的集合
- **输出空间** $\mathcal{Y}=\{0,1\}$：二元分类标签（可扩展为多分类）
- **概念** $c:\mathcal{X}\to\mathcal{Y}$：目标映射
- **概念类** $\mathcal{C}$：待学习概念的集合
- **假设空间** $\mathcal{H}=\{h:\mathcal{X}\to\mathcal{Y}\}$：学习算法可输出的所有映射
- **欠拟合 vs 过拟合**：假设空间过小导致欠拟合，过大导致过拟合
- **双下降现象**：过参数化深度学习模型中测试误差呈非单调曲线（欠拟合→插值阈值峰值→过参数化再次下降），挑战传统偏差-方差权衡

### 2.2 经验误差与泛化误差

- **泛化误差** $R(h)=\mathbb{P}_{x\sim\mathcal{D}}[h(x)\neq c(x)]$
- **经验误差** $\hat{R}_S(h)=\frac{1}{m}\sum_{i=1}^m\mathbb{I}[h(x_i)\neq c(x_i)]$
- **无偏性证明**：$\mathbb{E}[\hat{R}(h;D)]=R(h;\mathcal{D})$（独立同分布样本期望相同）

### 2.3 假设空间可分性与学习复杂度

- **可分性**：存在假设完全区分所有样本——仅是能力上限，非充分条件
- **时间复杂度**：抽象图灵机上的操作数
- **样本复杂度**：达到给定精度所需样本数
- 有限假设空间穷举搜索 $O(|\mathcal{H}|m_H(\epsilon,\delta))$；$|\mathcal{H}_n|=2^n$ 时计算复杂度指数增长

### 2.4 PAC-Bayes 理论

结合 PAC 学习与贝叶斯方法，通过假设空间上的后验分布 $Q$（先验 $P$）给出泛化界：

$$\mathbb{E}_Q[L(h)]\leq\mathbb{E}_Q[\hat{L}(h)]+\sqrt{\frac{KL(Q\|P)+\ln(1/\delta)+\ln m+\ln 2}{2m-1}}$$

KL 散度作为后验偏离先验的复杂度惩罚。

### 2.5 3-DNF 不可高效 PAC 学习性

完整证明 3 项析取范式在 $RP\neq NP$ 假设下不可高效 PAC 学：

1. 归约自图 3-着色问题（NP 完全）
2. 构造样本集 $S_G$：正例 $v(i)$（第 $i$ 位为 0）、反例 $e(i,j)$（第 $i,j$ 位为 0）
3. 图 3-可着色 ⟺ 存在 3 项 DNF 与 $S_G$ 一致
4. 颜色划分 → 合取子句构造
5. 若 3-DNF 可高效学习，则可在多项式时间内解决 3-着色，故 $RP=NP$

## 核心概念

- **PAC 辨识**：以 $1-\delta$ 概率输出 $R(h)\leq\epsilon$ 的假设
- **PAC 可学**：样本复杂度为 $1/\epsilon,1/\delta,\text{size}(x),\text{size}(c)$ 的多项式
- **不可知 PAC 可学**：不要求目标概念在 $\mathcal{H}$ 中，只需 $R(h)-\min_{h'}R(h')\leq\epsilon$
- **恰当 vs 不恰当**：输出假设是否属于 $\mathcal{H}$

## 理论定位

本章建立了理论机器学习的问题形式化：从"什么是学习"到"何时可学"。PAC 框架将哲学问题转化为可分析的数学问题，并通过 3-DNF 的不可学性结果首次展示计算复杂性对学习的根本约束。参见 [3-DNF 不可学案例](/datawhale/key-book/examples/pac-3dnf)。

## 参见

- [第 3 章：复杂性分析](/datawhale/key-book/references/chapter3)：VC 维等复杂度度量量化 PAC 学习的样本代价
- [第 5 章：稳定性](/datawhale/key-book/references/chapter5)：定理 5.4 建立稳定性与不可知 PAC 可学性的等价
