---
type: concept
title: "南瓜书定位与使用方法"
bundle: /datawhale/pumpkin-book
description: "南瓜书与西瓜书的互补共生关系、推荐使用方法、数学基础要求与配套资源"
sources: https://github.com/datawhalechina/pumpkin-book/blob/master/README.md
related:
  - /datawhale/pumpkin-book/concepts/model-evaluation-and-selection
  - /datawhale/pumpkin-book/concepts/linear-models-and-decision-trees
  - /datawhale/pumpkin-book/references/ch1-2-foundations
tags: [positioning, usage, watermelon-book, prerequisites]
status: stable
---

# 南瓜书定位与使用方法

## 南瓜书是什么

南瓜书（pumpkin-book）是 Datawhale 开源团队对周志华教授《机器学习》（俗称"西瓜书"）的公式推导伴读。西瓜书为了使尽可能多的读者通过它了解机器学习，对部分公式的推导细节没有详述；南瓜书则针对这些较难理解的公式加以解析，并补充具体的推导细节。

南瓜书的定位不是一本独立的机器学习教材，而是西瓜书的**推导笔记与补充材料**。周志华教授本人认为"理工科数学基础扎实点的大二下学生应该对西瓜书中的推导细节无困难"，南瓜书则自嘲为"数学渣渣在自学时记下来的笔记"，帮助更多读者达到这一基础水平。

## 西瓜书-南瓜书互补关系

两本书构成"骨架-血肉"式的互补架构：

| 维度 | 西瓜书 | 南瓜书 |
|------|--------|--------|
| 角色 | 主线教材 | 推导伴读 |
| 内容 | 算法动机、核心思想、图表直觉、伪代码、实验对比 | 公式编号定位、代数变形、求导过程、矩阵运算 |
| 回答的问题 | 算法是什么、为什么需要、效果如何 | 公式怎么来的、每步变换的依据是什么 |
| 阅读方式 | 从头到尾线性阅读 | 按需查阅、遇到卡壳时翻找 |
| 章节对应 | 16章 | 16章严格一一对应 |

南瓜书所有内容都以西瓜书的内容为前置知识进行表述，脱离西瓜书单独阅读南瓜书会缺失上下文。

## 推荐使用方法

1. **以西瓜书为主线**：正常阅读西瓜书，遇到自己推导不出来或者看不懂的公式时，再查阅南瓜书对应章节的推导。
2. **初学不深究前两章**：第1章（绪论）和第2章（模型评估与选择）的公式对小白强烈不建议深究，简单过一下即可，等学完第3-6章具体算法后再回来啃。
3. **配合视频和代码**：每章开头标注了配套 B 站视频教程链接（BV1Mh411e7VU）和配套代码仓库（machine-learning-toy-code），形成"阅读→推导→视频→代码"的学习闭环。
4. **利用勘误表**：纸质版和开源版均有已知勘误，查阅时对照 [errata](../references/errata.md) 确认是否已有修正。

## 数学基础要求

南瓜书明确要求读者具备以下三门大学数学必修课基础：

- **高等数学**：极限、导数、偏导数、梯度、积分、拉格朗日乘数法
- **线性代数**：向量与矩阵运算、矩阵求逆、特征值与特征向量、矩阵求导
- **概率论与数理统计**：概率分布、条件概率、贝叶斯定理、极大似然估计、期望与方差

超纲的数学知识（如矩阵分析中的核范数、流形几何）南瓜书会以附录和参考文献的形式给出，不强行塞入正文。

## 配套资源

| 资源 | 地址 |
|------|------|
| GitHub 仓库 | https://github.com/datawhalechina/pumpkin-book |
| 在线阅读 | https://datawhalechina.github.io/pumpkin-book/ |
| 视频教程 | https://www.bilibili.com/video/BV1Mh411e7VU |
| PDF 下载 | https://github.com/datawhalechina/pumpkin-book/releases |
| 配套代码 | https://github.com/datawhalechina/machine-learning-toy-code |
| 组队学习 | https://www.datawhale.cn/learn/summary/2 |
| 纸质版 | 人民邮电出版社（京东/当当/天猫有售） |

## 编委会

- **主编**：谢文睿（@Sm1les）、秦州（@archwalker）、贾彬彬（@jbb0523）
- **编委**：juxiao、Majingmin、MrBigFan、shanry、Ye980226

## 许可证

本作品采用 [CC BY-NC-SA 4.0](http://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议。
