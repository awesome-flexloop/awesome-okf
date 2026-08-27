---
type: reference
title: "第12-16章：进阶主题"
bundle: /datawhale/pumpkin-book
description: "第12章计算学习理论、第13章半监督学习、第14章概率图模型、第15章规则学习、第16章强化学习"
source: https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter12/chapter12.md
path: docs/chapter12/chapter12.md, docs/chapter13/chapter13.md, docs/chapter14/chapter14.md, docs/chapter15/chapter15.md, docs/chapter16/chapter16.md
tags: [computational-learning-theory, pac, vc-dimension, semi-supervised, probabilistic-graphical-model, rule-learning, reinforcement-learning]
status: stable
---

# 第12-16章：进阶主题

## 信源信息

- **第12章**：`docs/chapter12/chapter12.md` → https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter12/chapter12.md
- **第13章**：`docs/chapter13/chapter13.md` → https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter13/chapter13.md
- **第14章**：`docs/chapter14/chapter14.md` → https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter14/chapter14.md
- **第15章**：`docs/chapter15/chapter15.md` → https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter15/chapter15.md
- **第16章**：`docs/chapter16/chapter16.md` → https://github.com/datawhalechina/pumpkin-book/blob/master/docs/chapter16/chapter16.md

## 第12章 计算学习理论

计算学习理论是机器学习的理论基础，分析学习算法的泛化能力和困难程度：

- **12.1 基础知识**：泛化误差与经验误差、PAC辨识与PAC可学
- **12.2 PAC学习**：
  - PAC（Probably Approximately Correct，概率近似正确）框架
  - 有限假设空间的可学性分析
  - 式(12.4)~式(12.9)样本复杂度推导
- **12.3 有限空间的泛化界**：
  - 可分情形与不可分情形
  - 式(12.14)~式(12.22)泛化误差界
- **12.4 VC维**：
  - 打散（shatter）与VC维定义
  - 式(12.24)~式(12.31)基于VC维的泛化界
  - 常见假设空间的VC维（超平面/决策树等）
- **12.5 Rademacher复杂度**：
  - 比VC维更紧的泛化界
  - 式(12.37)~式(12.50)Rademacher复杂度相关推导
- **12.6 稳定性**：
  - 算法的均匀稳定性与泛化性能
  - 式(12.51)~式(12.59)稳定性与泛化误差界

## 第13章 半监督学习

半监督学习利用大量未标记数据辅助少量有标记数据：

- **13.1 生成式方法**：假设数据由同一生成模型产生，EM算法求解
- **13.2 半监督SVM（S3VM）**：
  - 低密度分割思想
  - TSVM（Transductive SVM）：尝试未标记样本的各种标记指派
  - 式(13.1)~式(13.5)目标函数
- **13.3 图半监督学习**：
  - 构建图（样本为节点、相似度为边权）
  - 标签传播算法
  - 式(13.8)~式(13.15)高斯场与调和函数
- **13.4 基于分歧的方法**：
  - 协同训练（co-training）：多视图数据上训练两个学习器互相教导
  - 式(13.16)~式(13.21)协同训练理论分析
- **13.5 半监督聚类**：约束k均值、约束种子k均值

## 第14章 概率图模型

概率图模型用图结构表达概率分布的条件独立性：

- **14.1 隐马尔可夫模型（HMM）**：
  - 观测序列/状态序列、转移概率/观测概率/初始状态概率
  - 评估问题（前向/后向算法）
  - 解码问题（Viterbi算法）
  - 学习问题（Baum-Welch，即EM）
- **14.2 马尔可夫随机场（MRF）**：
  - 无向图模型、团与势函数
  - 条件独立性、全局/局部/成对马尔可夫性
- **14.3 条件随机场（CRF）**：
  - 判别式无向图模型
  - 线性链CRF与序列标注
- **14.4 学习与推断**：
  - 变量消去法（精确推断）
  - 信念传播（BP，sum-product算法）
- **14.5 近似推断**：
  - MCMC采样（Metropolis-Hastings、吉布斯采样）
  - 变分推断
- **14.6 话题模型**：
  - 隐狄利克雷分配（LDA）
  - 式(14.36)~式(14.40)LDA的概率图与推断
- **14.7 词向量模型**：从LSA到word2vec的演进

## 第15章 规则学习

规则学习从数据中产生形如"IF...THEN..."的逻辑规则：

- **15.1 基本概念**：规则、规则头/规则体、覆盖、正例/反例
- **15.2 序贯覆盖**：
  - 自顶向下（生成-测试）与自底向上
  - 式(15.1)~式(15.3)规则评估指标（覆盖率/准确率/似然率）
- **15.3 剪枝优化**：
  - 预剪枝/后剪枝
  - REP（Reduced Error Pruning）
- **15.4 一阶规则学习**：
  - 关系型数据与逻辑变量
  - FOIL算法（First-Order Inductive Learner）
  - 式(15.4)FOIL增益
- **15.5 归纳逻辑程序设计（ILP）**：
  - 最小一般泛化（LGG）
  - 逆归结（inverse resolution）
  - 式(15.5)~式(15.12)逆归结的四种操作

## 第16章 强化学习

强化学习通过与环境交互获得奖励来学习最优策略：

- **16.1 任务与奖赏**：
  - 马尔可夫决策过程（MDP）：状态/动作/转移概率/奖赏
  - 总回报与折扣因子
  - 式(16.1)累计奖赏定义
- **16.2 策略迭代与值迭代**：
  - 状态值函数$V^\pi(s)$与动作值函数$Q^\pi(s,a)$
  - 贝尔曼方程（式16.6~16.10）
  - 策略评估与策略改进
  - 值迭代（式16.13~16.14）
- **16.3 时序差分学习**：
  - Q-Learning（式16.21，off-policy）
  - Sarsa（式16.19，on-policy）
  - $\epsilon$-贪心探索
- **16.4 值函数近似**：
  - 大规模/连续状态空间下用函数逼近值函数
  - DQN（深度Q网络）的思想
- **16.5 模仿学习**：
  - 直接模仿学习
  - 逆强化学习（从专家行为反推奖赏函数）

## 对应概念

第12-16章为进阶主题，在本知识包中作为 [references](index.md) 信源登记，未单独展开为概念文档。核心概念文档聚焦第1-11章的经典机器学习算法。
