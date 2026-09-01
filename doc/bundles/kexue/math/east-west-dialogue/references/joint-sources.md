---
type: Reference
title: 中西原文与译本联合信源
description: 中西数学原典在线入口总表——复用既有两束已验证信源并新增比较研究专用入口，全部经实际访问验证
tags: [reference, sources, 原典, 联合信源, ctext, Gutenberg, 在线信源]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-01T12:00:00+08:00" }
status: draft
stale_after: 2027-09-01
sources:
  - id: s-guoxuedashi-jhyb
    resource: https://www.guoxuedashi.com/SiKuQuanShu/bk101682c/
    title: 国学大师·四库百科《几何原本》条目
    author: org:国学大师
---

# 中西原文与译本联合信源

本篇是中西对读的原典入口总表。对读要求同时触及两传统的原文或权威译文，故按"西方侧 / 中国侧 / 联合侧"三栏组织。**既有两束已验证信源以链接指向登记页，本篇不重复登记**；新增信源于 2026-09-01 实测可达。

## 西方侧（link → classics-reading 束）

| 信源 | 入口 | 本包用途 |
|------|------|---------|
| 公共领域原文平台总表 | [classics-reading/原文信源](../../classics-reading/references/original-sources.md) | Gutenberg、Internet Archive、Gallica、Perseus、Clay 等十大平台 |
| 《几何原本》希英对照 | Fitzpatrick PDF（见上述登记页） | 勾股 I.47 原文对照（[示例 01](../examples/01-pythagorean-comparison.md)） |
| 阿基米德 Heath 译本扫描 | Internet Archive（见上述登记页） | 《圆的度量》原文对照（[示例 03](../examples/03-pi-comparison.md)） |
| 译本注本谱系 | [classics-reading/译本信源](../../classics-reading/references/translations-commentaries.md) | Heath、Clavius 底本脉络 |

## 中国侧（link → suanjing-reading 束）

| 信源 ID | 入口 | 本包用途 |
|---------|------|---------|
| s-ctext-jiuzhang | [九章算术全文（ctext）](https://ctext.org/nine-chapters)（登记页：[suanjing-reading/在线信源](../../../../guoxue/suanxue/suanjing-reading/references/online-sources.md)） | 方程章、正负术原文（[示例 02](../examples/02-linear-systems-comparison.md)） |
| s-ctext-zhoubi | [周髀算经全文（ctext）](https://ctext.org/zhou-bi-suan-jing)（同上登记页） | 商高勾股、陈子表述原文（[示例 01](../examples/01-pythagorean-comparison.md)） |
| s-zdic | 汉典古籍《周髀算经》赵爽注本（见登记页） | 弦图注原文 |
| 中国点校本谱系 | [suanjing-reading/核心版本](../../../../guoxue/suanxue/suanjing-reading/references/core-editions.md) | 钱宝琮 1963、郭书春/刘钝 1998 |

## 联合侧（本包新增）

| 信源 ID | 信源 | URL | 验证结论（2026-09-01） |
|---------|------|-----|----------------------|
| s-guoxuedashi-jhyb | 国学大师·四库百科《几何原本》条目 | https://www.guoxuedashi.com/SiKuQuanShu/bk101682c/ | ✅ 可达。1606 起译、1607 刻印、克拉维乌斯底本、1857 韩应陛刊本、1865 金陵书局十五卷本、明清中算家几何著述清单 |
| s-ctext-math | ctext 算书类目（导航入口） | https://ctext.org/mathematics/zhs | ✅ 可达（2026-08-30 既有束已验证，复用）。中西算书对照浏览的统一起点 |
| s-mactutor | MacTutor 数学史档案 | https://mathshistory.st-andrews.ac.uk/ | ✅ 可达。传记与主题文章总库，比较视角的西文导航站（详见 [comparative-studies](comparative-studies.md)） |

## 原文引录规范

1. 双源引录处分别标注信源 ID 与底本（西方选段标注译本与页码，中国选段标注 ctext/点校本）。
2. 中国原文保留繁体字形与古籍用字（"句股"不作"勾股"），白话译文另起。
3. 引录为精选片段；受版权保护的现代译本（Clarke 1966、Cohen-Whitman 1999 等）不复制文本，仅作对照指引。

相关概念：[几何与度量对读](../concepts/03-geometry-measurement.md) · [接触与互鉴对读](../concepts/08-contact-mutual-learning.md)
