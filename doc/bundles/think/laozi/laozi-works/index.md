---
type: OKF
title: 老子著作（出土文献原文与权威解读）知识包
description: 聚焦老子本人著作的原文与解读本体，以出土文献（郭店楚简、马王堆帛书、北大汉简）为主基准提供《道德经》原文，三线并收出土文献校注、历代注本、现代学者注本的权威解读，兼顾相关道家著作概览。
tags: [laozi, 老子, 道德经, 出土文献, 帛书, 郭店楚简, 北大汉简, 注本, 中国哲学, 道家]
version: "1.0.0"
source: 出土文献整理本（郭店楚简/马王堆帛书/北大汉简）+ 历代注本 + 现代学术注本
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:00:00+08:00" }
status: draft
stale_after: 2027-08-30
okf_version: "0.2"
---

# 老子著作（出土文献原文与权威解读）

本知识包（bundle）聚焦**老子本人著作的原文与解读本体**，以出土文献为主基准提供《道德经》原文，三线并收权威解读。与既有 bundle 互补：`boshu-reading`（怎么读帛书）、`laozi-lineage`（版本源流谱系）侧重方法与源流，本 bundle 侧重「原文 + 解读」的横向整合。

## 快速导航

### [概念文档](concepts/index.md) — 4 篇核心概念
- [《道德经》名实与全书概览](concepts/daodejing-overview.md) — 书名沿革、篇章结构、德经/道经篇序
- [出土文献三大系统](concepts/unerthed-systems.md) — 郭店楚简、马王堆帛书、北大汉简成书与价值
- [核心哲学概念](concepts/core-concepts.md) — 道、德、无为、自然的出土文献视角
- [相关道家著作概览](concepts/related-works.md) — 《文子》《关尹子》《阴符经》成书、真伪与老子思想关系

### [出土文献原文](text/index.md) — 出土文献原文与异文
- [帛书甲本原文](text/boshu-jia.md) — 标注残毁处，与乙本互补
- [帛书乙本原文](text/boshu-yi.md) — 较完整底本，标注与甲本差异
- [郭店楚简本现存部分](text/guodian.md) — 显式说明残简范围
- [北大汉简本原文](text/beida-hanjian.md) — 保存最完整的汉代抄本
- [关键异文对照](text/key-variants.md) — 核心异文逐条对照，链接至解读

### [权威解读](commentaries/index.md) — 三线并收
- [出土文献校注解读](commentaries/unerthed-collation.md) — 高明、裘锡圭、北大简整理组
- [历代注本解读](commentaries/historical-commentaries.md) — 王弼、河上公、严遵、苏辙
- [现代学者注本解读](commentaries/modern-commentaries.md) — 陈鼓应、楼宇烈、李零
- [争议与不确定性](commentaries/controversies.md) — 断代/释文/诠释分歧显式化

### [信源登记簿](references/index.md) — 可核查信源
- [出土文献整理本](references/core-manuscripts.md)
- [历代注本信源](references/historical-commentaries.md)
- [现代注本信源](references/modern-studies.md)

### 工作文档
- [事实清单](facts.md) — 42 条零推测事实（R 阶段）
- [架构洞察](insights.md) — 4 条核心洞察（I 阶段）
- [可复用模式](patterns.md) — 3 个方法模式（E 阶段）

## Bundle 定位

| 维度 | boshu-reading（已存在） | laozi-lineage（已存在） | laozi-works（本 bundle） |
|------|----------------------|----------------------|------------------------|
| 核心问题 | 怎么读帛书？ | 版本怎么流传？ | 原文与解读本体是什么？ |
| 视角 | 读者/学习者 | 文献学者/校勘者 | 内容整合者 |
| 侧重 | 阅读路径、注本选用 | 传本详述、异文考证 | 出土原文 + 三线解读 |
| 适合阶段 | 入门→进阶 | 研究级 | 全阶段查阅 |

## 原文与解读策略

- **原文基准**：出土文献为主（郭店楚简 1993、马王堆帛书 1973、北大汉简 2009 入藏）。
- **释文溯源**：所有释文溯源自正式出版整理本，残毁处标注，不编造。
- **解读三线**：出土校注（文本层）→ 历代注本（义理层）→ 现代注本（综合层），分歧显式化。

```{toctree}
:hidden:
:maxdepth: 7

usage
concepts/index
text/index
commentaries/index
references/index
facts
insights
patterns
log
```