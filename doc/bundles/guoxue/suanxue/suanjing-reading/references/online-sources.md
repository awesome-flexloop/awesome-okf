---
type: Reference
title: 在线原典信源
description: 中国数学典籍原文的在线全文与影印底本信源登记，含中国哲学书电子化计划（ctext.org）、汉典古籍、中华文库、国学大师、维基文库等公开稳定入口
tags: [reference, sources, 算经, 古籍全文, ctext, 在线信源]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-30T10:00:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: s-ctext-math
    resource: https://ctext.org/mathematics/zhs
    title: 中国哲学书电子化计划·算书类目
    author: org:Chinese Text Project
  - id: s-ctext-zhoubi
    resource: https://ctext.org/zhou-bi-suan-jing
    title: 周髀算经（ctext 全文）
    author: org:Chinese Text Project
  - id: s-ctext-jiuzhang
    resource: https://ctext.org/nine-chapters
    title: 九章算术（ctext 全文）
    author: org:Chinese Text Project
  - id: s-ctext-haidao
    resource: https://ctext.org/hai-dao-suan-jing
    title: 海岛算经（ctext 全文）
    author: org:Chinese Text Project
  - id: s-ctext-sunzi
    resource: https://ctext.org/sunzi-suan-jing
    title: 孙子算经（ctext 全文）
    author: org:Chinese Text Project
  - id: s-zdic
    resource: https://gj.zdic.net/zibu/326/
    title: 汉典古籍·周髀算经（赵爽、甄鸾注本）
    author: org:汉典
  - id: s-zhonghuashu
    resource: https://www.zhonghuashu.com/
    title: 中华文库·海岛算经等古籍
    author: org:中华典藏
  - id: s-guoxuedashi
    resource: https://www.guoxuedashi.com/
    title: 国学大师·九章算经等算法类古籍
    author: org:国学大师
  - id: s-wikisource
    resource: https://zh.wikisource.org/
    title: 维基文库（中文）·算经条目
    author: org:Wikimedia
  - id: s-wikipedia
    resource: https://zh.wikipedia.org/
    title: 维基百科·中国数学史相关条目
    author: org:Wikimedia
---

# 在线原典信源

本文件登记中国数学典籍（先秦至明清）原文的在线公开信源。这些是本知识包"原文引录"的一级信源——所有 examples/ 中的原文片段均取自下列站点，并在引录处标注信源 ID 与底本。

## 信源分级说明

| 级别 | 类型 | 说明 | 本包用途 |
|------|------|------|---------|
| 一级 | 原典全文与影印底本 | 站点提供繁体原文全文，并链接扫描影印本（如《四部丛刊》《四库全书》） | 原文引录、底本核对 |
| 二级 | 现代整理电子文本 | 基于点校本录入的电子文本，附现代标点 | 白话译文对照 |
| 三级 | 百科条目 | 综合性介绍与书目信息 | 背景与导航，不作原文依据 |

## 一级信源：ctext.org（中国哲学书电子化计划）

ctext.org 是本知识包最主要的原文信源，提供繁体原文全文、英文机器辅助翻译，并链接多个影印底本扫描页。下列 URL 均于 2026-08-30 实测可达。

| 信源 ID | 典籍 | URL | 年代标注（站点） | 影印底本 |
|---------|------|-----|----------------|---------|
| s-ctext-math | 算书类目（导航入口） | https://ctext.org/mathematics/zhs | — | 类目页，聚合下列各书 |
| s-ctext-zhoubi | 《周髀算经》 | https://ctext.org/zhou-bi-suan-jing | [汉] 约公元前 50 年–公元 100 年 | 《四部丛刊初编》本（res=77422）；《槐庐丛书》本《周髀算经·数术记遗》（res=79068） |
| s-ctext-jiuzhang | 《九章算术》（又名《九章算经》） | https://ctext.org/nine-chapters | [西汉–新] 约公元前 120 年–公元 20 年 | 《四部丛刊初编》本（res=77423）；《钦定四库全书》本（res=5782） |
| s-ctext-haidao | 《海岛算经》 | https://ctext.org/hai-dao-suan-jing | [三国] 公元 263 年 | 刘徽《重差》单行本，唐李淳风等注 |
| s-ctext-sunzi | 《孙子算经》 | https://ctext.org/sunzi-suan-jing | [南北朝] 420–581 年 | 《知不足斋丛书》本《孙子算经+五曹算经》（res=80226） |

使用要点：

- ctext 原文页路径形如 `https://ctext.org/<book>/<chapter>/zhs`（简体界面）或 `/<book>/<chapter>`（繁体界面），可按篇章直接定位，例如孙子算经序为 `/sunzi-suan-jing/xu/zhs`。
- 影印底本通过页面"电子图书馆"链接访问，形如 `https://ctext.org/library.pl?if=gb&res=<编号>`，`res` 编号即底本在 ctext 书库中的稳定标识。
- 站点提供英文翻译（AI 辅助 + 用户修订），仅作参考，不作学术依据。

## 一级信源：其他古籍全文站点

| 信源 ID | 站点 | 入口 | 收录与特点 | 实测情况 |
|---------|------|------|-----------|---------|
| s-zdic | 汉典古籍 | https://gj.zdic.net/zibu/326/9157.html （周髀算经） | 《周髀算经》赵爽（汉）、甄鸾（北周）注本全文；子部·科技类下另有多种算书 | 2026-08-30 实测可达，含勾三股四弦五、陈子测日等段落 |
| s-zhonghuashu | 中华文库（中华典藏） | https://www.zhonghuashu.com/wiki/海島算經 | 《海岛算经》等算书全文，附《四库全书总目》提要 | 2026-08-30 实测可达，含海岛九题原文 |
| s-guoxuedashi | 国学大师 | https://www.guoxuedashi.com/ （子部·算法类） | 《九章算经》等算法类古籍，收录现代点校排印本电子文本（含钱宝琮校点本提要） | 2026-08-30 实测可达 |

## 二级/三级信源：维基体系

| 信源 ID | 站点 | 入口 | 用途 | 备注 |
|---------|------|------|------|------|
| s-wikisource | 维基文库（中文） | https://zh.wikisource.org/wiki/周髀算經 等 | 算经原文的另一电子文本来源，可与 ctext 互校 | 维基文库为开放编辑，引文须回查 ctext 或点校本 |
| s-wikipedia | 维基百科 | https://zh.wikipedia.org/wiki/九章算術 、https://en.wikipedia.org/wiki/The_Nine_Chapters_on_the_Mathematical_Art | 典籍概况、年代、人物、算法的导航性介绍 | 百科条目仅作背景导航；关键事实以 [core-editions.md](core-editions.md) 与 [modern-studies.md](modern-studies.md) 为准 |

> 可达性说明：ctext.org、汉典、中华文库、国学大师于 2026-08-30 经抓取实测可达；维基系站点对自动化抓取有限制，浏览器访问正常，URL 为长期稳定入口。

## 原文引录规范

本知识包 examples/ 与 concepts/ 中的原文引录遵循以下规范：

1. 每段原文在引录处注明信源 ID（如 `据 s-ctext-haidao`）与底本（如"《四部丛刊初编》本"）。
2. 原文保留繁体字形与古籍用字（如"句股"不作"勾股"、"實/法"保留），白话译文另起段落。
3. 引录为"精选片段"而非全文转贴：每部典籍只选与现代数学概念对照最直接的术文与算题。
4. 凡涉及现代研究的解释，引用 [modern-studies.md](modern-studies.md) 中的三级信源，不直接改写百科文本。
