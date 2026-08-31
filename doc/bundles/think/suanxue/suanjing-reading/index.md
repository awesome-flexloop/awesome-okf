---
type: OKF
title: 中国算经阅读教程
description: 面向现代读者的中国数学典籍系统阅读教程——以《九章算术》《周髀算经》《算经十书》与宋元四大算家为脉络，七道名题实战（分数、盈不足、方程正负、勾股、物不知数、百鸡、割圆）配合古今数学对照与原文选读。
tags: [suanxue, 算经, 九章算术, 周髀算经, 刘徽, 祖冲之, 中国数学史, 算法传统, 阅读教程]
version: "1.0.0"
source: 公开原典（ctext.org 等）与现代学术文献整理，信源见 references/
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-30T13:00:00+08:00" }
status: stable
stale_after: 2027-08-30
okf_version: "0.2"
---

# 中国算经阅读教程

本知识包（bundle）是中国数学典籍的系统阅读教程，覆盖先秦至明清的主要数学著作：《周髀算经》《九章算术》、刘徽注与《海岛算经》、《算经十书》、祖冲之父子、宋元四大家（秦九韶、李冶、杨辉、朱世杰），直到明清珠算普及与中西会通。教程以"原文引录—白话译文—现代数学解读—延伸"四段式算题实战为主干，配合概念框架、96 条登记事实与分级信源，所有原文均注明底本出处。

## 📚 快速导航

### [概念文档](concepts/index.md) — 14 篇知识框架
- [为什么读中国算经](concepts/00-why-read-suanjing.md) — 三个理由与常见误解
- [中国数学史历史总览](concepts/01-history-overview.md) — 先秦至清代时间线
- [算筹与十进位值制记数法](concepts/02-chousuan-numeration.md) — 纵橫两式、位置符号
- [《九章算术》的结构与体例](concepts/03-jiuzhang-structure.md) — 九章名目、问—答—术
- [《九章算术》核心算法](concepts/04-jiuzhang-key-methods.md) — 分数/今有术/盈不足/方程/开方/勾股
- [刘徽与《九章算术注》](concepts/05-liuhui-commentary.md) — 割圆术、阳马极限、牟合方盖
- [《周髀算经》与测望之学](concepts/06-zhoubi-suanjing.md) — 商高、陈子、赵爽弦图
- [算经十书各书导读](concepts/07-suanjing-shishu.md) — 海岛、孙子、张丘建、缉古等
- [祖冲之父子：圆周率与祖暅原理](concepts/08-zu-chongzhi.md) — 密率 355/113、幂势原理
- [宋元数学高峰](concepts/09-song-yuan-peak.md) — 贾宪、秦九韶、李冶、杨辉、朱世杰
- [大衍求一术、天元术与四元术](concepts/10-dayan-tianyuan-siyuan.md) — 筹算代数的三大程序
- [明清转型：珠算、西学东渐与算经辑佚](concepts/11-ming-qing-transition.md) — 算法统宗、几何原本、数理精蕴
- [中国数学的特征与中西比较](concepts/12-chinese-math-characteristics.md) — 五大特征与两种误读
- [阅读路径与书单](concepts/13-reading-path.md) — 三级书单与四周路线

### [实践示例](examples/index.md) — 7 篇算题实战 + 1 篇计划
- [方田·合分术](examples/01-fangtian-fractions.md) — 世界最早的分数加法程序
- [盈不足术](examples/02-yingbuzu-double-false.md) — 双假设试位法
- [方程术与正负术](examples/03-fangcheng-negative.md) — 筹算矩阵上的高斯消元
- [句股术与弦图](examples/04-gougu-pythagoras.md) — 勾股定理的出入相补证明
- [物不知数](examples/05-wuwuzhishu-crt.md) — 中国剩余定理的算经原型
- [百鸡问题](examples/06-baiji-weng.md) — 世界最早的不定方程组整数解
- [割圆术](examples/07-geyuan-pi.md) — 极限迭代确定圆周率
- [八周通读计划](examples/08-reading-plan.md) — 每周任务与自测清单

### [信源参考](references/index.md) — 4 篇信源登记
- [在线原典信源](references/online-sources.md) — ctext/汉典/中华文库等全文入口与底本编号
- [核心点校本与出土文献](references/core-editions.md) — 钱宝琮、郭书春、白尚恕、李继闵整理本
- [现代学术研究文献](references/modern-studies.md) — 钱宝琮、Needham、Martzloff、Chemla 等
- [库内交叉引用](references/cross-ref.md) — katex、SymPy、Manim、Ψhē 数学形式化等关联包

### 工作文档
- [事实清单](facts.md) — 96 条零推测事实（F-001~F-096）与锚点核验表
- [架构洞察](insights.md) — 5 条四元组洞察与知识地图

## 🚀 快速开始

如果你只带好奇心而来：

1. 先读[为什么读中国算经](concepts/00-why-read-suanjing.md)；
2. 打开[八周通读计划](examples/08-reading-plan.md)，从第 1 周的《孙子算经》与[物不知数](examples/05-wuwuzhishu-crt.md)开始做题；
3. 每做一道题，回概念文档读对应章节建立框架。

如果你有数学或工程背景：

1. 直接做题：[盈不足](examples/02-yingbuzu-double-false.md)、[方程正负](examples/03-fangcheng-negative.md)、[割圆](examples/07-geyuan-pi.md)——三道题即可体会中算的算法本质；
2. 再读[中国数学的特征与中西比较](concepts/12-chinese-math-characteristics.md)与[架构洞察](insights.md)；
3. 按[阅读路径与书单](concepts/13-reading-path.md)进入点校本。

## 🎯 Bundle 定位

| 维度 | 内容 |
|------|------|
| 视角 | 现代读者/学习者（不是文献校勘） |
| 核心问题 | 中国数学典籍写了什么？怎么用今天的数学读懂它？ |
| 方法 | 原文引录（注明底本）→ 白话译文 → 现代数学复算 → 历史延伸 |
| 覆盖 | 先秦至明清，以《九章》体系与宋元高峰为重点 |
| 信源 | 全部原文登记于 references/，事实编号可回溯（F-xxx） |

## 📖 推荐学习路径

```
入门路径（先做题）：
  概念00 → 示例05（物不知数）→ 示例01（分数）→ 示例04（勾股）
  → 概念01（历史总览）→ 示例02/03/06/07 → 概念03-12

体系路径（先框架）：
  概念00→01→02 → 概念03→04 → 概念05→06→07→08
  → 概念09→10 → 概念11→12 → 示例01-07 做题 → 示例08 通读原典

研究路径：
  全部概念 → references/core-editions 点校本 → references/modern-studies 专著
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```