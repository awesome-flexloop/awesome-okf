---
okf_version: "0.2"
type: bundles-index
title: "中医经典（Classics）"
description: "中医典籍谱系总览与经典精读——难经·伤寒杂病论·神农本草经逐部精读教程、《黄帝外经》研读、《黄帝内经》交叉引用；原文双源核对、版本源流、注家谱系、阅读方法论"
---

# 中医经典（Classics）知识包

本分组收录中医典籍体系的核心知识包：以"典籍谱系总览 + 经典逐部精读"为骨架，提供原文精读（核心难/条文/序录双信源逐字核对）、底本与版本源流、成书与托名之争的学说并列、历代注家谱系与注本分级，以及跨经典的典籍谱系分层与阅读方法论。《黄帝内经》的阅读教程位于 think 域（见下方交叉引用），本分组通过交叉引用贯通四大经典全景；扩展书目（温病学派、本草纲目、针灸甲乙经等）在总览束书目分级中占位，供后续扩展。

| 统计项 | 数量 |
|---|---|
| 知识包 | 5 |
| 概念文档 | 34 |
| 示例文档 | 13 |
| 信源参考 | 13 |

> ⚠️ **医学免责声明**：本分组全部内容为古籍文献学习资料，非医疗建议；任何健康问题请咨询执业医师。文中方药剂量仅为文献记录。

## 知识包列表

| 知识包 | 链接 | 描述 | 文档数 |
|---|---|---|---|
| 中医典籍总览 | [tcm-overview](tcm-overview/index.md) | 中医典籍谱系分层（经典/各家学说/临床）、四大经典导读、版本学常识、书目分级与阅读方法论、264 条事实与洞察沉淀 | 6概念 · 2示例 · 3信源 |
| 难经 | [nanjing](nanjing/index.md) | 81 难结构与题名全录、脉学核心难逐字精读、与内经的设难关系、注家谱系（吕广/杨玄操/滑寿/徐大椿） | 6概念 · 2示例 · 2信源 |
| 伤寒杂病论 | [shanghan-zabinglun](shanghan-zabinglun/index.md) | 六经辨证框架与 398 条编号索引、核心条文精读、金匮要略选读、版本系统考（宋本/成注本/桂林古本/康平本） | 7概念 · 2示例 · 3信源 |
| 神农本草经 | [shennong-bencaojing](shennong-bencaojing/index.md) | 辑复性质与辑本系统（孙星衍/顾观光/森立之）、三品分类与 365 药归属、序录与代表药精读 | 6概念 · 2示例 · 2信源 |
| 黄帝外经 | [waijing-weiyan](waijing-weiyan/index.md) | 《黄帝外经》（今本《外经微言》，清·陈士铎述）研读——九卷八十一篇双源核对原文、命门水火与颠倒顺逆思想、文献学三层分离与真伪考辨 | 9概念 · 5示例 · 3信源 |

## 交叉引用：《黄帝内经》

《黄帝内经》阅读教程位于 think 域：[think/huangdi-neijing/neijing-reading](../../huangdi-neijing/neijing-reading/index.md)——面向普通读者的权威原文阅读指南，含版本底本链、8 篇名篇逐字精读、历代注本导航与 12 周通读计划。本分组总览束的四大经典导读中提供《黄帝内经》的谱系定位与成书考证视角，与该教程互为补充。

## 推荐阅读路径（按读者身份）

完整路径（含预期收获、时间投入与避坑提示）见域指南：[tcm/guide.md](../guide.md) 第 3 节。

- **零基础爱好者**：[tcm-overview](tcm-overview/index.md) concepts/00–01 → [《黄帝内经》教程（think 域）](../../huangdi-neijing/neijing-reading/index.md) → 凭兴趣选束深入
- **临床从业者 / 中医院校学生**：先读[版本学常识](tcm-overview/concepts/02-philology-basics.md)打底 → [shanghan-zabinglun](shanghan-zabinglun/index.md)（六经框架→太阳篇精读→398 条索引备查）→ [shennong-bencaojing](shennong-bencaojing/index.md)（序录精读→三品对照）
- **文献学 / 版本学研究者**：[tcm-overview](tcm-overview/index.md) concepts/02–03、05（阅读方法论）→ [双源核对演示](tcm-overview/examples/dual-source-verification-demo.md) → 伤寒版本考 / 本草辑本考 / [外经真伪考辨](waijing-weiyan/concepts/03-authenticity-debate.md) 三专题对读
- **专题兴趣**：脉学读 [nanjing](nanjing/index.md)；命门水火与养生读 [waijing-weiyan](waijing-weiyan/index.md)；本草药物读 [shennong-bencaojing](shennong-bencaojing/index.md)
- **AI 智能体 / 知识库构建**：直接读 [域指南第 9 节](../guide.md) 与各束束根 toctree

## 数据源

经典原文均经双信源逐字核对，信源登记于各束 `references/`，包括：中国哲学书电子化计划（ctext.org）、维基文库、国学导航等公开古籍库，以及通行底本刊刻信息（伤寒论赵开美宋本、本草经孙星衍/顾观光辑本、难经通行本）。方法论工作记录（264 条事实登记、5 条洞察、3 个阅读模式）沉淀于 [tcm-overview](tcm-overview/index.md)。

```{toctree}
:hidden:
:maxdepth: 7

tcm-overview/index
nanjing/index
shanghan-zabinglun/index
shennong-bencaojing/index
waijing-weiyan/index
```
