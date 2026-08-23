---
title: 3-DNF 的不可高效 PAC 学习性
type: example
bundle: /datawhale/key-book
related:
  - /datawhale/key-book/concepts/learnability
  - /datawhale/key-book/concepts/computational-complexity
  - /datawhale/key-book/references/chapter2
sources:
  - https://github.com/datawhalechina/key-book/blob/master/docs/chapter2.md
---

# 案例：3-DNF 的不可高效 PAC 学习性

本案例展示计算复杂性理论如何证明一个概念类**信息论上可学但计算上不可学**，是理解[可学性](/datawhale/key-book/concepts/learnability)中"高效"限定词的关键。

## 问题定义

**3 项析取范式（3-term Disjunctive Normal Form, 3-DNF）**：由三个子句组成的布尔公式，每个子句是布尔变量的合取（AND），整个公式是三个子句的析取（OR）。

对 $n$ 个布尔变量，公式大小最多为 $6n$（每个子句最多 $2n$ 个文字）。

## 核心结论

> 3-DNF 概念类不是高效 PAC 可学的，除非 $RP=NP$。

由于普遍认为 $RP\neq NP$，这意味着不存在多项式时间的 PAC 学习算法。

## 证明策略：归约自图 3-着色

### 1. 选择 NP 完全问题

**图 3-着色问题**：给定无向图 $G=(V,E)$，判断能否用三种颜色为顶点着色，使任意边的两个端点颜色不同。这是经典 NP 完全问题。

### 2. 构造样本集 $S_G$

对图的每个顶点和每条边构造样本：

- **正例** $v(i)$（对应顶点 $i$）：
  - 第 $i$ 位为 0，其余位为 1
  - 标签为 +1
- **反例** $e(i,j)$（对应边 $(i,j)$）：
  - 第 $i$ 位和第 $j$ 位为 0，其余位为 1
  - 标签为 -1

### 3. 等价性

$$G\text{ 是 3-可着色的} \iff \exists\text{ 3-DNF 公式与 }S_G\text{ 一致}$$

### 4. 正向构造（3-可着色 ⇒ 3-DNF 一致）

假设图可 3-着色，将顶点分为三组 $T_R, T_B, T_Y$（红、蓝、黄）。

对每种颜色构造一个合取子句：
- $T_R$ 子句由所有**不着红色**的顶点变量的**否定**组成
- 例如顶点 $j,k$ 不着红色，则 $T_R = \neg x_j \wedge \neg x_k$

**验证正例**：顶点 $i$ 着红色，$v(i)$ 第 $i$ 位为 0、其余为 1。$T_R$ 中所有文字对应非红色顶点，这些位置在 $v(i)$ 中均为 1，故 $\neg x_j$ 为真，$v(i)$ 满足 $T_R$，整个 DNF 为真。

**验证反例**：边 $(i,j)$ 两端颜色不同（设 $i$ 红、$j$ 蓝）。$e(i,j)$ 第 $i,j$ 位为 0。
- $T_R$ 需要第 $i$ 位为 1 才满足（但为 0），不满足
- $T_B$ 需要第 $j$ 位为 1 才满足（但为 0），不满足
- $T_Y$ 同理不满足
- 整个 DNF 为假 ✓

### 5. 反向推导

如果存在 3-DNF 与 $S_G$ 一致，则三个子句对应三种颜色划分，可构造合法 3-着色。

### 6. 复杂性结论

若 3-DNF 可在多项式时间 PAC 学，则可用它在多项式时间内解决图 3-着色问题（构造样本→学习→判断一致性），从而 $RP=NP$。

## 关键洞察

1. **信息论可学 ≠ 高效可学**：3-DNF 的 VC 维有限（$O(n)$），信息论上需要多项式样本，但找到一致假设是 NP 难的。
2. **样本复杂度与时间复杂度的分离**：PAC 框架同时要求二者为多项式，缺一不可。
3. **归约是计算学习理论的核心证明技术**：将已知困难问题归约为学习问题，证明不可学性。

## 延伸

- 这一结果属于**计算学习理论**（COLT）的传统，与 Valiant（1984）的 PAC 框架一脉相承
- 类似的不可学结果包括：布尔公式、有限自动机等概念类在密码学假设下不可学
- 深度学习中的"可学习性"问题更微妙：神经网络的 VC 维虽大，但 SGD 仍能找到泛化良好的解——这是经典理论尚未完全解释的

## 参见

- [可学性](/datawhale/key-book/concepts/learnability)
- [计算复杂度](/datawhale/key-book/concepts/computational-complexity)
- [第 2 章：可学性](/datawhale/key-book/references/chapter2)
