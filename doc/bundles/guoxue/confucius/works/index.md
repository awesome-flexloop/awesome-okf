---
type: OKF
title: 孔子相关著作阅读教程
description: 孔子本人相关著作（《春秋》《诗》《书》《礼》《乐》《易》《论语》）阅读教程：逐部标注归属层级（亲作/整理/辑录/存疑）的归属矩阵、双源核对原文（ctext.org 与 zh.wikisource.org）、经注三层与今古文分歧、春秋笔法与论语代表章句精读、注本分级选用决策树
tags: [confucius, six-classics, 春秋, 诗经, 尚书, 周易, 论语, 三礼, 述而不作, 阅读教程]
version: "1.0.0"
source: 权威电子文本调研（ctext.org、zh.wikisource.org、中国孔子网 chinakongzi.org）＋ 注疏与译注文献（《十三经注疏》、杨伯峻《论语译注》《春秋左传注》、程树德《论语集释》、高亨《周易古经今注》、程俊英《诗经注析》）＋ 出土文献（定州汉简《论语》、郭店简、上博简、清华简）
generated: { by: "agent:create-kongzi-works-okf-wiki", at: "2026-08-31T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-31T00:00:00+08:00" }
status: stable
stale_after: 2027-08-31
okf_version: "0.2"
---

# 孔子相关著作阅读教程

本知识包（bundle）梳理**孔子本人相关的著作**——即传统所谓「六经」及《论语》，目标是为每部著作提供权威、可靠的原文与解读，并**诚实地标注每部著作与孔子的真实关系**。

- **归属分级**：亲作 / 整理传授 / 弟子辑录 / 存疑四层，杜绝「孔子著六经」的俗说，凡传统说法与辨伪证据并列呈现
- **原文双源核对**：选录原文以 ctext.org 与 zh.wikisource.org 双源逐字核对，异文并列登记不仲裁
- **注家立场分开**：今古文、汉宋、出土文献三层不混淆，关键句呈现 ≥2 种注家立场

## 📚 快速导航

### [概念文档](concepts/index.md) — 9 篇
- [00 述而不作](concepts/00-shu-er-bu-zuo.md) — 孔子与六经关系的总纲
- [01 春秋](concepts/01-chunqiu.md) — 亲作/修订、笔削义例、三传注疏
- [02 诗经](concepts/02-shijing.md) — 删诗说、风雅颂、四家诗与注本
- [03 尚书](concepts/03-shangshu.md) — 今古文、伪古文、清华简、要义
- [04 礼与乐](concepts/04-li-yue.md) — 三礼、正乐、乐经亡佚
- [05 周易与易传](concepts/05-zhouyi-yizhuan.md) — 韦编三绝、十翼归属存疑
- [06 论语](concepts/06-lunyu.md) — 成书、张侯论、郑玄注、定州汉简
- [07 版本源流](concepts/07-banben-yuanliu.md) — 六经次序、今古文经、出土文献
- [08 归属矩阵与辨伪史](concepts/08-guishu-bianwei.md) — 宋以来辨伪史

### [精读示例](examples/index.md) — 3 篇
- [01 春秋笔法精读](examples/01-chunqiu-bifa.md) — 「郑伯克段于鄢」三传对照
- [02 论语选读](examples/02-lunyu-xuandu.md) — 学而/为政/述而代表章句逐句解读
- [03 诗书选读](examples/03-shishu-xuandu.md) — 诗经代表篇目 + 尚书代表篇章

### [信源参考](references/index.md) — 3 份信源登记
- [权威底本](references/01-authoritative-editions.md) — 十三经注疏、中华书局点校本、ctext.org
- [注本分级](references/02-commentaries-graded.md) — 一阶注疏/二阶现代注译/三阶普及读本
- [信源登记与交叉引用](references/03-sources-cross-ref.md) — laozi/huangdi/confucian 互链

### 工作文档
- [事实清单](facts.md) — 63 条信源事实（F-001~F-063）
- [架构洞察](insights.md) — 4 条四元组洞察 + 3 个可复用阅读模式
- [工作日志](log.md) — R→I→E→V→C 全程记录

## 🔍 归属矩阵速览

| 著作 | 归属层级 | 传统说 | 现代辨伪 / 考古依据 |
|------|---------|--------|---------------------|
| 《春秋》 | 亲作 / 修订（存议） | 孔子据鲁史修订，笔削寓褒贬（《孟子》《史记》） | 「作」与「修」之争；三传解经属后代经学建构 |
| 《诗》 | 整理 / 传授 | 「孔子删诗三千篇」（《史记》）存疑 | 孔子自称「诗三百」；季札观乐时已近定型 |
| 《书》 | 整理 / 传授 | 孔子「序书传」、编次百篇 | 今古文之争；清华简证伪古文尚书 |
| 《礼》 | 整理 / 传授 | 孔子订礼、《仪礼》出孔子 | 《周礼》《仪礼》约成书于战国 |
| 《乐》 | 整理（已亡佚） | 孔子「正乐」 | 《乐》经只存目，西汉立五经不列《乐》 |
| 《易》（十翼） | 存疑 | 「人更三圣」：孔子作《易传》十翼 | 欧阳修《易童子问》疑《系辞》《文言》非孔子作 |
| 《论语》 | 弟子辑录 | 门人「辑而论纂」 | 定州汉简为最早实物，异文分章有出入 |

## 🚀 快速开始

1. 先读 [00 述而不作](concepts/00-shu-er-bu-zuo.md) 与 [08 归属矩阵与辨伪史](concepts/08-guishu-bianwei.md)，建立「每部书与孔子是何种关系」的坐标
2. 若关注「孔子思想」，从 [06 论语](concepts/06-lunyu.md) 及其[选读](examples/02-lunyu-xuandu.md) 入手——《论语》是距孔子最近的言行实录
3. 若关注「孔子编书」，从 [01 春秋](concepts/01-chunqiu.md)、[02 诗经](concepts/02-shijing.md)、[03 尚书](concepts/03-shangshu.md) 分头进入
4. 涉及文本可靠性问题，回查 [07 版本源流](concepts/07-banben-yuanliu.md) 与 [信源登记](references/03-sources-cross-ref.md)

## 🔗 相关知识包

- 儒家系统对读：[think/confucian/four-books](../../confucian/four-books/index.md)（《大学》《中庸》《论语》《孟子》四书教程）
- 先秦思想对读：[think/laozi/boshu-reading](../../laozi/boshu-reading/index.md)（《老子》帛书教程）、[think/huangdi-neijing/neijing-reading](../../../yixue/huangdi-neijing/neijing-reading/index.md)（《黄帝内经》教程）
- 详细交叉引用见[信源登记与交叉引用](references/03-sources-cross-ref.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```