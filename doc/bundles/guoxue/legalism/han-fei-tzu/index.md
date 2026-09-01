---
type: bundle
id: han-fei-tzu
title: 韩非子
subtitle: 法家集大成的法·术·势体系阅读教程
description: 《韩非子》OKF 知识包。以九篇核心篇章为骨架，覆盖法术势三纲、性本利论、参验方法论、刑名之学、法不阿贵、孤愤与说难、显学批判、集大成谱系八大概念域；附《五蠹》《孤愤》《说难》三篇双源逐字精读（异文显式登记）与校本系统、数字信源、解读文献三份信源谱系。全部引文经 ctext.org 与 moocky.net 双源核验，不虚构任何引文。
okf_version: "0.2"
language: zh
category: think/legalism
status: stable
created: 2026-08-30
facts: .trae/specs/create-legalism-okf-wiki/facts-han-fei-tzu.md
sources:
  - https://ctext.org/hanfeizi/zhs
  - https://moocky.net/b/hanfeizi
  - https://m.gushiwen.cn/guwen/bookv_66bf9111c262.aspx
---

# 韩非子（Han Feizi）

《韩非子》是先秦法家思想的集大成文献。据《史记·老子韩非列传》：韩非为"韩之诸公子"，"喜刑名法术之学，而其归本于黄老"；"为人口吃，不能道说，而善著书"，与李斯俱事荀卿，李斯自以为不如（F-HF-031）。秦王政读《孤愤》《五蠹》之书，叹"嗟乎，寡人得见此人与之游，死不恨矣"，秦因急攻韩（F-HF-032）；韩非虽知说之难、"为说难书甚具"，终死于秦，不能自脱（F-HF-034）。

本知识包（bundle）以《韩非子》九篇核心篇章（《五蠹》《孤愤》《说难》《有度》《二柄》《定法》《难势》《显学》《六反》节选）为骨架，组织八大概念域与三篇双源精读，服务于"读懂原文、辨明异文、核对信源"的研读目标。

## 全书结构总览

- 通行本《韩非子》共五十五篇，篇数与《汉书·艺文志》著录一致（F-HF-001）。
- 《韩非子》本称《韩子》，唐代为与韩愈区分改称《韩非子》；今通行本经汉代刘向编定（F-HF-002）。

### 作者归属分层

| 层次 | 内容 | 依据 |
|---|---|---|
| 史源亲著层 | 《孤愤》《五蠹》《内外储》《说林》《说难》十余万言，司马迁明录为韩非所著 | F-HF-033 |
| 编定层 | 今本五十五篇经汉代刘向编定成书 | F-HF-002 |
| 精读骨架层 | 本包九篇核心篇章，原文经 ctext.org + moocky.net 数字双源核对 | F-HF-003、F-HF-005 |

本包不作五十五篇逐篇归属裁决；争议篇目的归属学说留作增量扩展。

## 知识包结构

| 分区 | 内容 | 入口 |
|---|---|---|
| 概念 | 八大核心概念文档 | [法·术·势三纲](concepts/fa-shu-shi.md) |
| 精读 | 《五蠹》《孤愤》《说难》三篇双源逐字精读（含异文标注） | [《五蠹》精读](examples/wu-du.md) |
| 信源 | 校本系统、数字信源、解读文献三份谱系 | [校本系统](references/collation-traditions.md) |
| 日志 | 编纂与核验过程记录 | [log.md](log.md) |

## 核心概念一览

1. **法·术·势三纲**（[concepts/fa-shu-shi.md](concepts/fa-shu-shi.md)）——"皆帝王之具也"的治理工具论及其现代学术争论
2. **性本利论**（[concepts/human-nature-profit.md](concepts/human-nature-profit.md)）——"民固骄于爱、听于威"的人性前提
3. **参验方法论**（[concepts/can-yan-verification.md](concepts/can-yan-verification.md)）——"无参验而必之者，愚也"的认识论标准
4. **刑名之学**（[concepts/xing-ming-doctrine.md](concepts/xing-ming-doctrine.md)）——"循名而责实"的考核之术
5. **法不阿贵**（[concepts/fa-bu-a-gui.md](concepts/fa-bu-a-gui.md)）——"法不阿贵，绳不挠曲"的普遍适用原则
6. **孤愤与说难**（[concepts/gu-fen-shuo-nan.md](concepts/gu-fen-shuo-nan.md)）——法术之士的处境论与游说方法论
7. **显学批判**（[concepts/xian-xue-critique.md](concepts/xian-xue-critique.md)）——对儒墨两显学的批判与历史进化论
8. **集大成谱系**（[concepts/ji-da-cheng-lineage.md](concepts/ji-da-cheng-lineage.md)）——"集大成"叙事的学术史检讨

## 学习路径

- **首次研读**：[法·术·势三纲](concepts/fa-shu-shi.md) → [性本利论](concepts/human-nature-profit.md) → [法不阿贵](concepts/fa-bu-a-gui.md)，建立概念骨架，再入[《五蠹》精读](examples/wu-du.md)。
- **文本精读**：直接进入[《五蠹》精读](examples/wu-du.md)、[《孤愤》精读](examples/ku-fen.md)、[《说难》精读](examples/shuo-nan.md)，逐段对照双源原文与异文标注。
- **学术研究**：从[集大成谱系](concepts/ji-da-cheng-lineage.md)进入现代学术争论，再核对[解读文献](references/interpretations.md)与[校本系统](references/collation-traditions.md)。

## 使用方式

本包事实编号前缀为 F-HF（信源事实登记见主仓 `.trae/specs/create-legalism-okf-wiki/facts-han-fei-tzu.md`，共 50 条）。引用本包任何原文时，请通过对应事实编号回溯 ctext.org / moocky.net 信源 URL 复核；凡两源文字有出入处，均以异文事实（F-HF-042 至 F-HF-050）显式标注"某本作某"，不作隐性裁断。

```{toctree}
:hidden:
:maxdepth: 7

concepts/fa-shu-shi
concepts/human-nature-profit
concepts/can-yan-verification
concepts/xing-ming-doctrine
concepts/fa-bu-a-gui
concepts/gu-fen-shuo-nan
concepts/xian-xue-critique
concepts/ji-da-cheng-lineage
examples/wu-du
examples/ku-fen
examples/shuo-nan
references/collation-traditions
references/digital-sources
references/interpretations
log
```
