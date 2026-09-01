---
type: OKF
title: 编纂日志
description: 音乐治疗知识包 2026-09-01 R/I/E/V/C 五阶段编纂执行记录与网络讹传修正清单。
tags: [music-therapy, 音乐治疗, 编纂日志, OKF]
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
status: stable
stale_after: 2027-09-01
---

# 编纂日志

倒序日期分组；本束仅一个编纂日。

## 2026-09-01

**R（研究/事实登记）**
- 沿用既有 facts.md（MT-01 ~ MT-16）：每条事实 ≥2 独立信源，个别标注（单源待核）；信源覆盖 musictherapy.org 三页、bamt.org 档案与 BJMT、Cochrane/PMC/PubMed、期刊纪念文（Approaches、MTP、Music and Medicine）、图书馆目录与书目页。
- 任务清单与 facts 核对时发现作者归属冲突：精神分裂症 Cochrane 综述原写 Bradt 等，经核实 2017 年更新版第一作者为 Geretsegger（facts MT-13 备注），Bradt 对应术前焦虑综述（MT-16）。

**I（架构设计）**
- 定型三层结构：concepts（00 总览 / 01 美国职业化 / 02 英国传统 / 03 三大模型 / 04 循证证据）+ examples（01 三轨阅读计划 / 02 GIM 文献导读）+ references（sources 信源登记）。
- 决策：GIM 单独成篇（examples/02），因网络误读最重，需独立安全边界声明；循证篇按四篇 Cochrane 逐篇登记而非汇总叙述，以保住结局特定的证据质量表述。

**E（撰写）**
- 产出 13 个文件：束根 index.md（含免责声明、定位对比、三轨路径）；concepts 5 篇；examples 2 篇；references 2 篇；log.md。
- 版权分层执行：AMTA 定义英文原文引用并标注 musictherapy.org URL（MT-01）；现代著作（Gaston 1968、Priestley 1975/1994、Bonny & Savary 1973、Nordoff & Robbins 1971/1977、Bruscia 1989/1998/2014）仅作 1—2 句结论性转述 + 完整书目。

**V（核对）**
- 双源核对确认并修正的网络讹传项：
  - Geretsegger/Bradt 作者归属（facts MT-13 备注）；
  - Mary Priestley 卒年 2017-06-11，双纪念文一致（facts MT-08）；
  - Paul Nordoff 卒年 1977-01-18（Prabook + BJMT 2012），生日两说仅记月（facts MT-10）；
  - 《Creative Music Therapy》1977 年（John Day）而非 UK 官网清单所标 1971（facts MT-11 备注）；
  - 《Therapy in Music for Handicapped Children》1971 Gollancz 版成立，另录 1965 年初版书名沿革（单源待核）（facts MT-11）。
- 异说并列不裁决：Guildhall 培训课程 1967（BSMT 档案 + Prabook）vs 1968（Sing Up Foundation）（facts MT-07 备注）。
- （单源待核）逐项复核留档于[信源登记](references/sources.md)：MT-02（RMT 1956）、MT-03（1975 更名）、MT-05（1946—1948 建课年份）、MT-06（Menninger 实习点）、MT-08（AMT 1970s 时点）、MT-09（ICM 1973）、MT-11（1965 初版沿革）。
- 循证篇逐篇复核限定词：精神分裂症“中至低质量、作为补充、效应不一致”（MT-13）；抑郁“极低至低置信度（荷兰 2024 指南表述）”（MT-14）；痴呆“≥5 次、部分结局中等、未见获益结局与无长期效应、新闻稿旧数据 22 试验/890 人已披露”（MT-15）；术前焦虑“STAI-S -5.72（95% CI -7.27 至 -4.17）、多数试验高偏倚风险”（MT-16）。

**C（收尾）**
- 相对链接全部带 .md 后缀；姊妹束链接（../art-therapy/index.md、../china-art-therapy/index.md）自束根与子目录分别按层级书写。
- frontmatter 统一：Index 文档 type: Index；其余文档 type: OKF + version 1.0.0 + sources 指向 facts.md + generated（agent:general_purpose_task, 2026-09-01T20:00:00+08:00）+ status: stable + stale_after: 2027-09-01；束根携带 okf_version: "0.2"。
- YAML 安全自查：全部 description 均未在双引号标量内使用 ASCII 双引号。
- 遗留事项：7 项（单源待核）条目与 Guildhall 异说维持标注，待后续补源；facts.md 未做任何改动。
