---
type: OKF
title: 鬼谷子知识包
description: 《鬼谷子》先秦纵横家经典原文与解读教程
tags: [guiguzi, 鬼谷子, 纵横家, 捭阖, 中国哲学]
version: "1.0.0"
source: 公共领域古籍《鬼谷子》及历代注疏
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-30T00:00:00+08:00" }
status: stable
stale_after: 2027-08-30
okf_version: "0.2"
---

# 鬼谷子知识包

本知识包（bundle）是先秦纵横家经典《鬼谷子》的系统阅读教程，收录逐字双源核对的原文（据 ctext.org《四部丛刊》本与《正统道藏》本）、核心概念与历代注家立场，并自觉区分「托名层（作者归属）/ 文本层（思想内容与成书时代）/ 接受层（历代注疏与评价）」三层文本，不在作者真伪上武断裁决。与同域《老子》《庄子》知识包互补，本 bundle 侧重「如何读懂纵横术经典」。

## 📚 快速导航

### [概念文档](concepts/index.md) — 7 篇核心概念
- [什么是鬼谷子](concepts/00-what-is-guiguzi.md) — 「鬼谷子」其人、「鬼谷」地望与书名含义
- [版本源流](concepts/01-text-transmission.md) — 书志著录（隋志/新旧唐书）与道藏本卷次、传世本流变
- [作者与成书之争](concepts/02-authorship-debate.md) — 托名层/文本层区分
- [原文全录与篇目结构](concepts/03-full-text.md) — 现存篇目分段 + 亡佚篇目存目
- [核心概念解读](concepts/04-core-concepts.md) — 捭阖/反应/内揵/抵巇/飞箝/忤合/揣摩权谋决/符言
- [历代注家与立场](concepts/05-commentaries.md) — 皇甫谧→陶弘景→尹知章/乐壹→现代
- [历史影响](concepts/06-influence.md) — 与纵横家/兵家/道家关系及《战国纵横家书》互证

### [实践示例](examples/index.md) — 2 篇实操指南
- [《捭阖》逐句精读](examples/01-baihe-reading.md) — 多注家立场对照精读
- [通读计划](examples/02-reading-plan.md) — 注本选用与篇目顺序建议

### [信源参考](references/index.md) — 3 类信源登记
- [权威底本清单](references/core-texts.md) — 道藏本/ctext/维基文库/四库本 + 信源 URL
- [注本分级表](references/commentaries.md) — 入门/进阶/研究级注本选用
- [交叉引用](references/cross-ref.md) — 关联 laozi 系 bundle、阴符经六家注与外部资源

### 工作文档
- [事实清单](facts.md) — 42 条零推测事实（G1）
- [架构洞察](insights.md) — 4 条核心洞察 + 2 个可复用阅读模式（G2/G3）

## 🚀 快速开始

如果你从未系统读过《鬼谷子》：

1. 先读[什么是鬼谷子](concepts/00-what-is-guiguzi.md)建立人物与文本的基本定位
2. 读[作者与成书之争](concepts/02-authorship-debate.md)，理解「托名层/文本层」区分
3. 打开[通读计划](examples/02-reading-plan.md)，按篇目顺序开始读[原文全录](concepts/03-full-text.md)

如果你读过《鬼谷子》但想读得更「真」：

1. 从[版本源流](concepts/01-text-transmission.md)理解「今本为何是十二篇 + 外篇」
2. 对照[原文全录](concepts/03-full-text.md)的异文标注逐字核读
3. 跟着[《捭阖》逐句精读](examples/01-baihe-reading.md)体会多注家对照法

## 🎯 Bundle 定位

| 维度 | 本 bundle（guiguzi） |
|------|----------------------|
| 视角 | 读者 / 学习者 |
| 核心问题 | 《鬼谷子》讲了什么？原文如何忠实读？如何区分托名与文本、注家引申？ |
| 文本边界 | 十二篇 + 本经阴符七术 + 中经 + 持枢残篇，逐字双源核对 |
| 适合阶段 | 入门 → 进阶 |

## 📖 推荐学习路径

```
零基础读者（第一次读）：
  概念00 → 02 → 示例02 → 概念03（原文）→ 概念04

有古文基础：
  概念01 → 02 → 概念03（核对异文）→ 示例01 → 概念05

研究型读者：
  全部概念 → references 三篇信源 → 交叉引用 laozi 系 bundle
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