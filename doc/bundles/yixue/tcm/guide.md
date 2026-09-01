---
type: Guide
title: "🌿 tcm 域知识包使用指南"
description: "中医经典与理论域阅读地图——5 个知识包内容导航、按目标选择阅读路径、文献学体例约定（双源核对/异文标注/托名分层）、信源体系、常见问题与后续扩展"
tags: [tcm, guide, reading-map, 中医经典, 使用指南]
generated: { by: reference_agent/trae-glm, at: 2026-08-31T10:00:00+08:00 }
verified:
  - { by: process:seven-concepts-v-review, at: 2026-08-30T18:00:00+08:00 }
status: stable
stale_after: 2027-08-31
sources:
  - id: tcm-domain
    resource: /doc/bundles/tcm/
    title: "tcm 域 5 个知识包（tcm-overview / nanjing / shanghan-zabinglun / shennong-bencaojing / waijing-weiyan）"
  - id: neijing-cross-ref
    resource: /doc/bundles/think/huangdi-neijing/neijing-reading/
    title: "《黄帝内经》阅读教程（think 域，交叉引用）"
---

# 🌿 tcm 域知识包使用指南

本指南帮助读者（及 AI 智能体）快速理解「中医经典与理论」域的内容布局、阅读路径与文献学体例约定。本域全部内容为**古籍文献学习资料，非医疗建议**；任何健康问题请咨询执业医师，文中方药剂量仅为文献记录。

- 📍 域入口：[tcm 域索引](index.md) ｜ 📚 分组：[中医经典（Classics）](classics/index.md)
- 📝 版本变更：见 [tcm 域版本更新日志](changelog.md)
- 🧭 全库导航：[知识包总索引](../index.md)

---

## 1. 本域是什么

tcm 域存放中医（Traditional Chinese Medicine）典籍体系的系统化阅读教程，以"**典籍谱系总览 + 经典逐部精读**"为骨架，提供：

- **原文精读**：核心篇目/难/条文/药条/序录均经**双信源逐字核对**，异文显式标注；
- **文献学诚实呈现**：托名性质、成书年代诸说并列不武断，辑复本性质显式标注，版本系统并列不作"真本"裁决；
- **注家谱系**：历代注家立场登记与注本分级（入门/进阶/研究级），不转录受版权保护的现代注文；
- **阅读方法论**：沉淀可复用的古籍阅读模式（双源核读、托名分层判读、谱系分级阅读）。

本域当前含 **1 个分组、5 个知识包**，共 **60 篇内容文档**（概念 34 · 示例 13 · 信源参考 13）。

## 2. 知识包地图

| 知识包 | 解决什么问题 | 内容构成 | 入口 |
|---|---|---|---|
| **中医典籍总览**<br>`tcm-overview` | 中医典籍体系长什么样？四大经典怎么来的？古籍该怎么读？ | 谱系三层分层（经典/各家学说/临床）、四大经典导读（6 种组合并列）、版本学常识（异文五分法）、托名五问法、书目分级、3 个阅读模式 | [束入口](classics/tcm-overview/index.md) |
| **难经**<br>`nanjing` | 《难经》81 难说什么？脉诊"独取寸口"何义？与内经什么关系？ | 81 难题名全录、第一难逐句精读、成书五说并列、吕广/杨玄操/滑寿/徐大椿注家谱系、三源异文登记 | [束入口](classics/nanjing/index.md) |
| **伤寒杂病论**<br>`shanghan-zabinglun` | 六经辨证是什么？398 条怎么读？宋本/桂林古本有何区别？ | 成书流变（王叔和整理→宋代校订）、四版本系统考、六经辨证框架、398 条编号索引+金匮 25 篇存目、太阳篇 23 条逐条精读 | [束入口](classics/shanghan-zabinglun/index.md) |
| **神农本草经**<br>`shennong-bencaojing` | 《本经》为什么是"辑复本"？三品分类怎么分？365 药怎么对不上？ | 辑本系统（卢复/孙星衍/顾观光/森立之）与六类差异、三品理论、序录 13 句逐句精读、11 味代表药双源照录、363 条药目存目 | [束入口](classics/shennong-bencaojing/index.md) |
| **黄帝外经**<br>`waijing-weiyan` | 《黄帝外经》不是佚失了吗？今本《外经微言》是什么？ | 九卷八十一篇双源核对、13 篇精读原文、命门水火与颠倒顺逆思想、文献学三层分离（著录/托名/文本）、真伪两派并列考辨 | [束入口](classics/waijing-weiyan/index.md) |

> **《黄帝内经》在哪里？** 《素问》《灵枢》的阅读教程位于 think 域：[think/huangdi-neijing/neijing-reading](../think/huangdi-neijing/neijing-reading/index.md)（8 篇名篇逐字精读 + 12 周通读计划 + 异文双录）。tcm 域通过交叉引用与其贯通，内经的文献学事实（成书、底本、王冰注、运气七篇等）沉淀在总览束中。这样安排避免重复建设——四大经典在 tcm/think 两域协作覆盖。

## 3. 按读者身份选择阅读路径

五条路径按读者身份设计，可对号入座；路径之间允许交叉（如临床从业者兼做文献核对）。

### 🟢 路径一：零基础爱好者 / 传统文化读者

- **你是谁**：没有中医专业背景，想系统了解中医典籍到底在讲什么，或对养生、传统文化有兴趣。
- **预期收获**：建立中医典籍谱系的全景坐标，能读懂核心名篇的原文大意，不再被"黄帝/神农"的托名叙述误导。
- **建议投入**：每周 2–3 小时，约 8–12 周；时间有限者可用总览束的 [四大经典通读计划](classics/tcm-overview/examples/four-classics-reading-plan.md) 压缩为 4 周速览。

**阅读步骤**：

1. [tcm-overview](classics/tcm-overview/index.md) concepts/00–01：典籍谱系分层 + 四大经典导读（约 2–3 小时，建立坐标系）
2. 转入 [《黄帝内经》教程（think 域）](../think/huangdi-neijing/neijing-reading/index.md)：先读 8 篇名篇精读，有余力再跟 12 周通读计划
3. 回到 tcm 域，凭兴趣任选一束深入（喜欢脉诊选难经，喜欢方药选伤寒/本草）

> ⛔ **避坑**：不要一上来直接啃《伤寒论》398 条或本草 363 药目——没有谱系坐标会陷入条文迷宫。先读总览束。

### 🩺 路径二：临床从业者 / 中医院校学生

- **你是谁**：学过中医基础理论、方剂学，需要回到经典原文核对教材与课堂表述，或做经方/本草的源头梳理。
- **预期收获**：掌握六经辨证框架与方证体系、本草序录与三品分类；建立"教材表述 ≠ 经典原文"的版本意识，能以底本原文核对二手转述。
- **建议投入**：精读为主，约 4–8 周；可作为长期案头工具书反复查阅。

**阅读步骤**：

1. 先打"版本疫苗"：[版本学常识](classics/tcm-overview/concepts/02-philology-basics.md) + [双源核对实操演示](classics/tcm-overview/examples/dual-source-verification-demo.md)（约 1 小时，理解条文异文与信源缩写体例）
2. [shanghan-zabinglun](classics/shanghan-zabinglun/index.md)：[六经辨证框架](classics/shanghan-zabinglun/concepts/03-six-channels-framework.md) → [太阳病篇 23 条逐条精读](classics/shanghan-zabinglun/examples/taiyang-passages.md) → [六经辨证阅读路线图](classics/shanghan-zabinglun/examples/six-channels-reading-map.md)；日常查条文用 [398 条编号索引](classics/shanghan-zabinglun/references/catalog-398.md)
3. [shennong-bencaojing](classics/shennong-bencaojing/index.md)：[序录逐句精读](classics/shennong-bencaojing/examples/preface-close-reading.md) → [三品对照阅读法](classics/shennong-bencaojing/examples/three-grades-comparison.md)；**先读 concepts/01 理解辑复本性质**——今本《本经》是明清辑本而非汉世原书
4. 方证与本草互参：伤寒方剂中的药物，回到本草经药条看早期功效记载

> ⚠️ 本路径全部内容为文献研读，**不构成临床处方与用药依据**；汉代度量衡、药物基原与今不同，实际诊疗遵执业规范与现行药典。

### 🔍 路径三：文献学 / 版本学研究者

- **你是谁**：关注成书年代、版本源流、辑佚辨伪，或从事古籍整理、知识史研究。
- **预期收获**：掌握中医典籍"托名层/文本层/辑复层"三层分离判读方法；获得三个可迁移到其他古籍领域的阅读模式（双源核读、托名分层、谱系分级）。
- **建议投入**：专题研究节奏，按课题需要深入；方法论部分约 1 周可掌握。

**阅读步骤**：

1. [tcm-overview](classics/tcm-overview/index.md) concepts/02–03：[版本学常识（异文五分法）](classics/tcm-overview/concepts/02-philology-basics.md) + [托名五问法](classics/tcm-overview/concepts/03-pseudepigrapha-dating.md)
2. [concepts/05 阅读方法论](classics/tcm-overview/concepts/05-reading-methodology.md)：三个可复用模式（双源逐字核读法 L2 / 托名辑复分层法 L2 / 谱系分级阅读法 L1）
3. [双源核对实操演示](classics/tcm-overview/examples/dual-source-verification-demo.md)：以《难经》异文"耗/好"为例的完整七步流程
4. 三个版本专题对读：[伤寒四版本系统考](classics/shanghan-zabinglun/concepts/02-version-systems.md)（宋本/成注本/桂林古本/康平本）、[本草经四辑本系统](classics/shennong-bencaojing/concepts/01-reconstruction-systems.md)（卢复/孙星衍/顾观光/森立之）、[外经真伪考辨](classics/waijing-weiyan/concepts/03-authenticity-debate.md)（著录/托名/文本三层分离）
5. 各束 `references/sources-*` 是信源登记簿（底本、校勘记、访问日期），可直接作为研究索引

### 🤖 路径四：AI 智能体 / 知识库构建者

- **你是谁**：需要程序化消费本域内容构建问答、RAG 或智能体检索。
- **预期收获**：理解文档元数据路由、引用规范与内容边界，输出时不违反文献学体例与医疗合规。
- **建议投入**：30 分钟通读入口文档即可上手。

**阅读步骤**：

1. 先读本指南 [第 9 节「给 AI 智能体的使用提示」](#9-给-ai-智能体的使用提示)：frontmatter 路由、信源缩写引用、禁止构拟、医疗边界
2. [tcm-overview 的方法论登记](classics/tcm-overview/references/methodology-records.md)：了解 264 条编号事实的登记体例（OV/NGJ/NJ/SH/BC 前缀）
3. 各束束根 `index.md` 的 toctree 即完整内容清单，可直接解析为检索目录

### 📜 路径五：专题兴趣读者

只关心一个具体主题，按主题直达：

| 兴趣点 | 阅读顺序 |
|---|---|
| **脉诊脉学** | [nanjing](classics/nanjing/index.md) concepts/01–03（81 难结构、与内经关系、独取寸口/命门概念）→ [第一难逐句精读](classics/nanjing/examples/first-nan-cunkou.md) → [难经与内经对照读法](classics/nanjing/examples/nanjing-neijing-parallel.md) |
| **命门/水火理论** | [waijing-weiyan](classics/waijing-weiyan/index.md) concepts/05–06（颠倒顺逆、命门水火）→ [命门三章精读](classics/waijing-weiyan/examples/mingmen-three-chapters.md) |
| **养生/顺逆寿夭** | [外经卷一养生篇精读（上）](classics/waijing-weiyan/examples/juan1-yangsheng-a.md)、[（下）](classics/waijing-weiyan/examples/juan1-yangsheng-b.md) → [《伤阳》篇](classics/waijing-weiyan/examples/shanyang.md) |
| **《外经微言》真伪之疑** | concepts/00–03（什么是外经 → 发现流传 → 作者成书 → [真伪考辨](classics/waijing-weiyan/concepts/03-authenticity-debate.md)） |
| **本草/药物** | [shennong-bencaojing](classics/shennong-bencaojing/index.md) concepts/02–04（三品分类 → 序录 → [代表药选读](classics/shennong-bencaojing/concepts/04-representative-herbs.md)） |

> ⚠️ 外经束《紅鉛損益篇》涉及明代道教方术内容，束内附有文献性质批判性说明，现代医学与伦理不取，阅读时请注意其史料性质。

## 4. 束内文档结构怎么读

每个知识包（束）遵循 OKF v0.2 三层结构，对应传统治学的"经—注—簿录"：

| 目录 | 层次 | 内容 | 怎么读 |
|---|---|---|---|
| `concepts/` | **经**（经典原文事实层） | 典籍本身的事实：成书、结构、核心概念、版本、注家、影响 | 系统学习时按编号 00→05 顺序读 |
| `examples/` | **注**（实操精读层） | 原文逐句/逐条精读、阅读路线图、对照阅读法 | 配合原文读，是"带着你读"的部分 |
| `references/` | **簿录**（文献著录层） | 权威底本与信源登记、注本分级表、条文/药目存目索引 | 查阅用：找底本、查信源、检索存目 |
| `index.md` | 束根 | 束导航 + toctree + 免责声明 | 每束的入口 |
| `log.md` | 变更记录 | 该束的创建与修订日志 | 想了解束的来龙去脉时读 |

**精读原文与存目的区别**：本域只对选定核心篇目做逐字精读（如难经精读 20 难、伤寒 71 条、本草经序录+11 味药、外经 13 篇）；未精读的篇/条/药以**存目清单**全录（难经 81 难题名、伤寒 398 条索引、金匮 25 篇、本草经 363 条药目、外经 81 篇目录），每条附一句导读，**不构拟补全**——这是诚实的文献边界。

## 5. 文献学体例约定（阅读前必读）

本域有若干贯穿全束的体例约定，理解它们才能正确阅读：

1. **双信源核对与信源缩写**：精读原文均经两个独立信源逐字核对，条文末标注信源缩写（如 C=ctext、W=维基文库、J=中医宝典 等，各束 references/ 有缩写表）。网络电子文本是"带版本立场的转录层"，不是中立的原文。

2. **异文标注体例**：底本文字不同之处，一律显式标注"**某本作某**"（如"维基文库本作'耗'，国学导航本作'好'"）；义理级异文（影响理解的差异）**两读并列、不作裁决**，由读者结合注家谱系自行判断。异文同时登记于各束 references/ 与精读文档校记。

3. **托名/成书/辑复三层分离**：
   - 《神农本草经》《黄帝内经》《难经》均为**托名之作**——成书于战国至秦汉的长时段累积，非神农/黄帝/秦越人亲著。因此全域禁用"神农曰/黄帝说/秦越人说"式表述，一律作"《难经》第 N 难作某""某辑本某药条作某"；
   - 成书年代诸说**并列登记**（如难经成书五说、本草经秦汉说/战国说），标注依据文献，不武断取一；
   - 《神农本草经》原书早佚，今本为明清以来**辑复本**（卢复/孙星衍/顾观光/森立之等），引用一律标注"某辑本"，辑本间六类差异（三品归属/药序/条目数/治主用字/句读/配伍数字）成体系覆盖。

4. **版本系统不裁决**：《伤寒论》宋本（赵开美刻本）、成无己注本、桂林古本、康平本四个版本系统并列呈现，桂林古本真伪两说并列；不宣称某一"真本"。另需注意：**伤寒论 398 条编号为现代校注者所加**，非古本旧式。

5. **现代注本的版权边界**：1949 年后现代校注本（如刘渡舟《伤寒论校注》等）仅作**书目登记与结论性引用**（底本选择等事实），不转录其受版权保护的题解、译文、注解；白话讲解均为依据公版原文自撰。注家对照采用"谱系立场登记"（如难经束登记吕广/杨玄操/滑寿的立场分歧），不虚构注文引文。

6. **医学免责**：每束首屏均有"文献学习资料、非医疗建议"声明；古籍所载药物功效、毒性与剂量为历史文献记录，现代用药请遵执业医师与药典指导。

## 6. 信源体系

精读原文的双源核对所依据的公开信源（各束 references/ 有完整登记与访问日期）：

- **中国哲学书电子化计划**（ctext.org）：伤寒论主信源之一
- **维基文库**（zh.wikisource.org）：难经/本草经/外经/伤寒底本或对校本
- **国学导航**、**中医宝典**、**古书网**、**古诗文网**、**中华文库**：对校与参证
- **底本刊刻信息**：伤寒论赵开美宋本、本草经孙星衍/顾观光/森立之辑本、外经 1984 年中医古籍出版社影印本等书目著录
- **书志著录**：《汉书·艺文志》等（著录层事实，如"《外经》三十七卷已佚"）

信源分级与可信度讨论见总览束 [权威信源总登记](classics/tcm-overview/references/authoritative-sources.md)。

## 7. 跨域互参

| 主题 | 位置 |
|---|---|
| 《黄帝内经》精读教程 | [think/huangdi-neijing/neijing-reading](../think/huangdi-neijing/neijing-reading/index.md) |
| 道家道教医学传统（医道同源、道藏医书、出土方技） | [think/daoyi](../think/daoyi/index.md) |
| 《老子》《庄子》等道家经典（与中医理论互参） | [think/laozi](../think/laozi/index.md) |
| OKF 知识包格式规范 | [meta/okf-spec](../meta/okf-spec/index.md) |

## 8. 常见问题（FAQ）

**Q1：为什么 tcm 域没有《黄帝内经》束？**
A：内经教程已由 think 域 [huangdi-neijing/neijing-reading](../think/huangdi-neijing/neijing-reading/index.md) 承担（8 篇名篇精读、12 周通读计划、异文双录、三层解读）。为避免重复建设，tcm 域采用交叉引用贯通，内经的文献学事实（162 篇存目、顾从德本/史崧本、王冰注与运气七篇等）沉淀在 tcm-overview 总览束中。

**Q2：《神农本草经》不是 365 味药吗，为什么存目是 363 条？**
A：序录自称"365 种"应周天之数，但今传辑复本的药目数目因辑本而异。本域存目据孙星衍辑本电子版誊录并经逐段复核：电子版目录标题 353 条，另有 10 味药以"嵌入"形式出现在正文中而无目录标题（如石胆、五色石脂、菟丝子、枸杞、茯苓、蠡鱼、翘根、山茱萸、赤小豆、雷丸），补入后实计 363 条（上经 146/中经 114/下经 103），与 365 之数仍差 2。这一差异在束内如实登记，不臆改凑数——古籍目录学问题本应如此呈现。

**Q3：《黄帝外经》不是早已失传了吗？这个束读的是什么？**
A：《汉书·艺文志》著录的《黄帝外经》三十七卷确实已佚（著录层事实）。今本《外经微言》九卷八十一篇为清代陈士铎述（1697 年左右流传，1980 年天津发现抄本、1984 年中医古籍出版社影印），题"岐伯天师传"。它与古《外经》是否为一书，学界真伪两派各有依据，束内**并列不裁决**，并以"著录层/托名层/文本层"三层分离帮助读者独立判断。无论真伪，其命门水火、颠倒顺逆思想在医学思想史上有独立价值。

**Q4：异文处我该信哪个版本？**
A：本域的立场是"**呈现异文、标注来源、不替读者裁决**"。义理级异文（如难经"肾有一也/二也"、伤寒 182 条"不恶热/不恶寒反恶热"）建议：①先看两个本子各自的注家怎么解释；②查该束 references/ 的底本源流（更早的底本通常更接近文本原貌，但不绝对）；③理解两读各自的义理脉络。异文本身就是古籍流传史的一部分。

**Q5：我能照这些内容用药、开方、针灸吗？**
A：**不能。** 本域是文献学习资料，不是诊疗指导。古籍方药剂量为历史记录（汉代度量衡与今不同、药物基原有变迁、部分药物有毒性管控），任何实际医疗行为请咨询执业医师并以现行药典为准。

**Q6：内容里的事实如何核实？**
A：本域建设时登记了 264 条编号事实（OV/NGJ/NJ/SH/BC 前缀，每条附信源 URL）与外经束 90 条（WJ 前缀），经过双源核对与对抗审查（13 处原文逐字复核、10 条事实 URL 核验）。事实工作记录在总览束 [methodology-records](classics/tcm-overview/references/methodology-records.md) 有描述性登记。

**Q7：后续还会增加哪些中医知识包？**
A：总览束书目分级中已占位的扩展方向包括：温病学派（《温病条辨》等）、《本草纲目》、《针灸甲乙经》、《脉经》等。新增束将同步更新 [域版本日志](changelog.md) 与各束 log.md。

## 9. 给 AI 智能体的使用提示

- **元数据自包含**：每个文档顶部 YAML frontmatter 携带 `type`/`title`/`description`/`sources`/`generated`/`verified`/`status`，可直接解析路由；束根 `index.md` 含 `okf_version: "0.2"`。
- **引用原文时**：连同信源缩写与异文校记一并引用，**不得**省略异文只取一读；**禁止**将托名文本表述为历史人物亲述（用"《难经》第 N 难作某"而非"秦越人说"）。
- **回答医疗问题时**：必须携带"非医疗建议"边界，引导就医。
- **存目即边界**：存目清单中无精读内容的篇目，不得凭常识或外部记忆补写原文——本域对未核对文本不构拟。
- **变更追踪**：域级变更看 [changelog.md](changelog.md)，束级细节看各束 `log.md`。

---

> 📖 建议第一次阅读从 [classics/index.md](classics/index.md) 的"推荐阅读路径"开始；文献学体例的详细方法论见 [tcm-overview/concepts/05-reading-methodology](classics/tcm-overview/concepts/05-reading-methodology.md)。
