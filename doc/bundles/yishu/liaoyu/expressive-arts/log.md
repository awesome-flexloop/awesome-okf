---
type: log
id: expressive-arts-log
title: 表达性艺术治疗知识包编纂日志
description: 表达性艺术治疗 OKF 知识包 R/I/E/V/C 各阶段执行记录、Knill 卒年讹传修正项、异说并列与单源待核清单及口径说明
tags: [expressive-arts, 表达性艺术治疗, 编纂日志, 双源核对, 讹传修正]
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
created: 2026-09-01
status: stable
stale_after: 2027-09-01
---

# 表达性艺术治疗 OKF 知识包编纂日志

## 2026-09-01 R 阶段（信源调研与事实登记）

- 调研方法：WebSearch/WebFetch 逐站采集，关键事实 ≥2 独立信源登记；任务拟稿中的既有讹传（Knill 生卒 1934-2023）在采集阶段即被 paeb.org 讣告与通讯、Kiddle 词条、EGS 官网等独立信源证伪。
- 登记事实 10 条（EA-01–EA-10），覆盖：Knill 生平与机构创立（EA-01）、Knill 跨模态理论与代表作（EA-02）、McNiff 与 Lesley 项目（EA-03）、Levine 夫妇存在—诗意取向（EA-04）、IEATA 成立与官方定义（EA-05）、整合取向与单分支艺术治疗的定义区别（EA-06）、诗歌治疗与阅读治疗之辨（EA-07）、Greifer 与 Leedy 职业化起点（EA-08）、NAPT 成立沿革与官方定义（EA-09）、诗歌治疗学术建制（EA-10）；全表见 [facts.md](facts.md)。
- **讹传修正项（Knill 卒年）**：任务拟稿作 1934-2023；IGPE（paeb.org）讣告与通讯 × Kiddle 词条双源核实为生于 1932 年（另有 1932-06-11/07-11 生月两说）、卒于 2020-09-13（约 88 岁）；EGS About 页（Founded in 1994）与 EXA HK 师资册（founding rector）旁证其机构史记载体系可靠，讹传不采信。
- 单源待核与不予登记：McNiff《The Arts and Psychotherapy》1981 出版年单源待核（仅 LibraryThing 著录）；McNiff 出生年（通行传记作 1946）未获双源核实，不予登记；NFBP/PT 认证年份记载不一，不予登记（EA-03、EA-09）。
- G1 质量门：事实均为纯客观陈述、无因果推断词；异说项（生月、书年、重组年、人物身份）均 ≥2 说并列登记不裁决。

## 2026-09-01 I 阶段（洞见与萃取）

- 核心洞察 4 条：①intermodal 与 multimodal 的官方分判是理解本领域的第一术语门槛；②整合取向谱系可概括为“McNiff 开地、Knill 立法、Levines 立言”三线合流（Lesley—ISI/EGS—合著枢纽）；③诗歌治疗一支与整合取向是并列而非从属关系，两术语口径在 SAGE 同义说、Mazza 层级说、NAPT 官方宽口径三份文献间各不相同；④人物生卒与书年的网络讹传密度高，须以组织官网与讣告类一手信源为锚。
- 可复用模式 3 个：组织定义原文直引法（定义 + URL + 试译三层）、讹传双源修正法（拟稿说法 × 一手讣告/官网对勘）、异说并列台账法（甲说/乙说/事实编号三栏）。

## 2026-09-01 E 阶段（萃取成稿）

- 产出 11 文件：束根 [index.md](index.md)＋concepts（[index](concepts/index.md)、[00-overview](concepts/00-overview.md)、[01-knill-intermodal](concepts/01-knill-intermodal.md)、[02-mcniff-levine](concepts/02-mcniff-levine.md)、[03-poetry-therapy](concepts/03-poetry-therapy.md)）＋examples（[index](examples/index.md)、[01-reading-plan](examples/01-reading-plan.md)）＋references（[index](references/index.md)、[sources.md](references/sources.md)）＋[log.md](log.md)。
- 概念文档 4 篇均 1500-4000 字，正文中全部论断以（facts EA-xx）格式回指事实编号；IEATA 与 NAPT 定义引原文并标注 URL；现代著作仅 1-2 句结论性介绍 + 完整书目表。
- 三轨阅读计划书单全部取自 facts.md 已登记著作（A-K 十一书目 + 期刊），未引入未经登记的书目。

## 2026-09-01 V 阶段（对抗审查与一致性自查）

- toctree 完整性：根 index 收录 concepts/index、examples/index、references/index、facts、log 五项；concepts/index 收录 00-03 四篇；examples/index 收录 01-reading-plan；references/index 收录 sources——与各目录实际文件一一对应。
- frontmatter 合规：概念/示例/信源文档 type: OKF 且携带 version、sources（resource 指向 facts.md）、generated、status、stale_after；Index 文档 type: Index；束根独携 okf_version: "0.2"；description 均为单行标量，双引号标量内无 ASCII 双引号，中文语境引号一律全角“”。
- 事实编号口径：facts.md EA-01–EA-10 与各文档（facts EA-xx）引用逐条对应；正文未出现 facts.md 之外的生卒、书年、机构事实。
- 链接检查：全部站内链接为相对路径且带 .md 后缀；姊妹束链接指向实际存在的文件（../art-therapy/index.md、../liaoyu-overview/facts.md——liaoyu-overview 目录暂无 index.md，故链至其 facts.md）；外部 URL 仅用于信源标注。
- 版权分层复查：官网定义段落均为短段原文 + 标注 URL + 试译；著作介绍均为结论性 1-2 句 + 书目表，无整段摘引。

## 2026-09-01 C 阶段（闭环收尾）

- 讹传修正闭环：Knill 卒年讹传（1934-2023 → 1932-2020）在 facts.md（EA-01）、references/sources.md 讹传修正记录表与束根 index.md 三处显式留痕，后续维护者可直接引用；生月两说并入异说台账持续跟踪。
- 待核跟踪项移交：McNiff 1981 出版年、McNiff 出生年、NFBP/PT 认证年份三项登记于 references/sources.md 第四节（单源待核）披露，stale_after（2027-09-01）前复核一次即可维持 stable。
- 与姊妹束协同：本束与 art-therapy（单分支美术治疗）、music-therapy、dance-drama-therapy、liaoyu-overview（主题总览）同属 liaoyu 主题群，束根与概念 00/02 已建立互链；后续若 liaoyu-overview 生成 index.md，可将束根链接从 ../liaoyu-overview/facts.md 升级为 ../liaoyu-overview/index.md。

## 口径说明

- 术语译名：intermodal 统一译“跨模态”，multimodal 译“多模态”，poiesis 译“创制／诗意生成”（首次出现均附原文）；low skill / high sensitivity 保留英文原式并附“低技能、高敏感度”。
- 定义引用：IEATA 术语表定义、NAPT 职业定义均为官网原文整段引用（组织公开定义属可直引范围），随附 URL；除此之外的现代著作文字一律不作整段摘引。
- 异说处理：生月、书年、版权年、重组年、人物身份五组异说全部并列登记不裁决；讹传（Knill 卒年 2023）为“已证伪之记载”，与“尚未裁决之异说”分列（异说台账 vs 讹传修正记录两表）。
- 单源与不予登记：单源待核项在正文引用处就地标注，并在信源登记集中披露；不予登记项（McNiff 出生年、NFBP/PT 年份）在 facts.md 与信源登记各声明一次，正文一律不出现相应数据。
