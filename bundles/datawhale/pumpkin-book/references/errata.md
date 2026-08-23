---
type: reference
title: "勘误表"
bundle: /datawhale/pumpkin-book
description: "南瓜书纸质版各印次公式与文字勘误汇总（第2版第6次印刷至第1版第4次印刷）"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/errata.md
path: docs/errata.md
tags: [errata, corrections, print-editions]
status: stable
---

# 勘误表

## 信源信息

- **文件路径**：`docs/errata.md`
- **GitHub**：https://github.com/datawhalechina/pumpkin-book/blob/master/docs/errata.md
- **在线查看**：https://datawhalechina.github.io/pumpkin-book/#/errata

## 使用方法

首先找到你的书的印次，接下来对着下表索引印次，该印次及其之后印次的勘误都是你书中所要注意的勘误，该印次前的所有勘误在当前印次均已修正。

## 勘误汇总（按印次从新到旧）

### 第2版第6次印刷（2024.01）

| 页码 | 位置 | 原文 | 修正 | 贡献者 |
|------|------|------|------|--------|
| 127页 | 式(8.7)的推导最后一句 | "两边同除$\frac{1}{2}$" | "两边同乘$\frac{1}{2}$" | @Acumen7 |
| 181页 | 式(10.14)推导第⑥步 | $-\boldsymbol{x}_i^{\top}\mathbf{W}^{\top} \mathbf{x}_i$ | $-\boldsymbol{x}_i^{\top} \mathbf{W}\mathbf{W}^{\top} \mathbf{x}_i$ | @huishengye |
| 195页 | 式(10.31)目标函数 | $\operatorname{tr}(\mathbf{Z}\mathbf{M}\mathbf{Z}\mathbf{Z}^{\top})$ | $\operatorname{tr}(\mathbf{Z}\mathbf{M}\mathbf{Z}^{\top})$ | @CoderKingXY |
| 86页 | 样本内积 | $\boldsymbol{x}_i^{\mathrm{T}}\boldsymbol{x}_j$（上标格式错误） | $\boldsymbol{x}_i^{\mathrm{T}}\boldsymbol{x}_j$ | 交流群13 @. |
| 97/98页 | LDA推导 | $\boldsymbol{w}^{\mathrm{T}} \mathbf{S}_{b}^{\phi} \boldsymbol{w}$ | $\boldsymbol{w}^{\mathrm{T}} \mathbf{S}_{w}^{\phi} \boldsymbol{w}$ | 交流群6 @Sodas |

### 第2版第5次印刷（2023.11）

| 页码 | 位置 | 原文 | 修正 | 贡献者 |
|------|------|------|------|--------|
| 98页 | 6.6.5核对率回归第2个公式 | $\boldsymbol{x}_i$ | $\boldsymbol{z}_i$ | 交流群11 @[太阳]🌈 |
| 13页 | 式(2.17)解释最后一段 | macro-F1代入macro-P/macro-R | micro-F1代入micro-P/micro-R | - |
| 46页 | 式(3.32)推导第一段 | "左下角" | "右下角" | - |
| 52页 | 3.6类别不平衡开头 | "对于类别平衡问题" | "对于类别不平衡问题" | - |

### 第2版第4次印刷（2023.10）

| 页码 | 位置 | 原文 | 修正 | 贡献者 |
|------|------|------|------|--------|
| 172页 | Frobenius范数定义 | $\|\mathbf{A}\|_F=\sum\sum\|a_{ij}\|^2$ | $\|\mathbf{A}\|_F^2=\sum\sum\|a_{ij}\|^2$ | @吴津宇 |

### 第1版第12次印刷（2022.06）

| 位置 | 原文 | 修正 | 贡献者 |
|------|------|------|--------|
| 式(3.9) | $\hat{\boldsymbol{x}}_i=(x_1;...;x_d;1)$ | $\hat{\boldsymbol{x}}_i=(x_{i1};...;x_{id};1)$ | @Link2Truth |

### 第1版第10次印刷（2021.12）

| 位置 | 原文 | 修正 |
|------|------|------|
| 式(10.2)解释最后一行 | $1 + P^2(c^*|\boldsymbol{x}) \leqslant 2$ | $1 + P(c^*|\boldsymbol{x}) \leqslant 2$ |

### 第1版第7次印刷（2021.10）

| 页码 | 位置 | 原文 | 修正 |
|------|------|------|------|
| 92页 | 式(10.28) | "n行1列的单位向量" | "n行1列的元素值全为1的向量" |
| 95页 | 式(11.6) | "$w$的分量过太" | "$w$的分量过大" |
| - | 式(11.18) | $\boldsymbol{b}$列向量有笔误 | 最新表述见在线版本 |

### 第1版第6次印刷（2021.07）

| 页码 | 位置 | 说明 |
|------|------|------|
| 17页 | 式(3.37) | $\lambda$取值解析不严谨，最新表述见在线版本 chapter3?id=_337 |

### 第1版第4次印刷（2021.05）

| 页码 | 位置 | 原文 | 修正 |
|------|------|------|------|
| 17页 | 式(3.37) | $\mathbf{S}_{b} \boldsymbol{w}=\lambda \mathbf{S}_{b} \boldsymbol{w}$ | $\mathbf{S}_{b} \boldsymbol{w}=\lambda \mathbf{S}_{w} \boldsymbol{w}$ |
| 80页 | 式(9.34) | $\mu$未加粗 | 改为粗体$\boldsymbol{\mu}$表示向量 |
| 117页 | 式(12.42) | "$\Phi(Z)$表示经验误差和泛化误差的上确界" | "$\Phi(Z)$表示泛化误差和经验误差的差的上确界" |
| 145页 | 式(14.36) | $\Sigma_{z\ne j}$ | $\Sigma_{k\ne j}$ |

## 勘误反馈

若发现南瓜书中的错误，可通过以下方式反馈：
- GitHub Issues：https://github.com/datawhalechina/pumpkin-book/issues
- 微信联系：at-Sm1les（提交后通常24小时内回复）
