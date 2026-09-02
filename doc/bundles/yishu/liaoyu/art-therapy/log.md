---
type: log
id: art-therapy-log
title: 美术治疗知识包编纂日志
description: 美术治疗（art therapy）OKF 知识包 R-I-E-V-C 各阶段执行记录——18 条事实双源登记、洞察并入总览束、13 文档成稿、对抗审查待执行与原子提交安排。
tags: [art-therapy, 美术治疗, 编纂日志, 双源核对]
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
created: 2026-09-01
status: stable
stale_after: 2027-09-01
---

# 美术治疗 OKF 知识包编纂日志

## 2026-09-01 R 阶段（信源调研与事实双源登记）

- 调研方法：WebSearch/WebFetch 逐站采集，按“档案 × 期刊 × 官网”跨系统双源原则登记；对教学演示文稿（Prezi 系列）作同源甄别（多版本互承 Gantt 1992 者整体计单源）。
- 登记事实 18 条（AT-01–AT-18），全表见 [facts.md](facts.md)。其中 17 条具备 ≥2 独立信源；AT-09（Elinor Ulman 生卒年与教育背景）仅获教学演示同源互证，显式标注（单源待核），并保留 Taylor & Francis Gantt 1992 Tribute 的间接佐证线索。
- 异说并列登记 7 处不裁决：Hill 术语首用 1942/1945（AT-02）、Walden School 1914/1915（AT-03）、《Schizophrenic Art》1950/1953（AT-05）、Kramer 卒日 2014-02-21/22（AT-06）、Ulman 编辑任期两种表述（AT-11）、《Bulletin》更名 1970/1979（AT-12）、Buck HTP 首发 1948/1949 及页码著录分歧（AT-17）。
- 信源构成：A 级（组织官网与学术档案：arttherapy.org、NYU MC.215、Penn Ms. Coll. 294、JWA、KU 展览、Philemon、LOC、普林斯顿/威斯康星/Bibliotheca Alexandrina 目录、Wiley/T&F/SAGE/PEP-Web）、B 级（期刊综述与讣告：Mental Illness 2014、ATOL 讣告、Betts & Groth-Marnat 2014、KJAT 2017 等）、C 级（百科镜像、科普站、教学演示、拍卖著录、讲义转载），全表见 [references/sources.md](references/sources.md)。
- G1 质量门：事实均为陈述句、无因果推断词；争议项一律 ≥2 说并列；AATA 定义引用标注官网 URL 并注明新旧版本差异。

## 2026-09-01 I 阶段（洞见萃取并入总览束）

- 本束不单设 insights.md；核心洞见（术语三层分判、双源异说并列法、评估传统与治疗传统的分野、循证表述克制纪律）已并入疗愈总览束（liaoyu-overview）的 insights 文档，供六束（art-therapy、music-therapy、expressive-arts、dance-drama-therapy、china-art-therapy、liaoyu-overview）横向复用。
- 可复用模式沉淀：人物生卒双源核对法、定义溯源法、术语分层法——三法在 [examples/02-source-appraisal.md](examples/02-source-appraisal.md) 中以本束真实案例完成示范。

## 2026-09-01 E 阶段（文档集成稿）

- 13 个文档按束模板成稿：束根 [index.md](index.md)（含免责声明、三节导航、两轨快速开始、定位对比表、三轨学习路径）＋ concepts（[index](concepts/index.md)、[00 总览](concepts/00-overview.md)、[01 创始人谱系](concepts/01-founders.md)、[02 荣格与美术治疗](concepts/02-jung-influence.md)、[03 绘画投射技术脉络](concepts/03-projective-techniques.md)、[04 取向对读与当代视角](concepts/04-theory-dialogue.md)）＋ examples（[index](examples/index.md)、[01 三轨阅读计划](examples/01-reading-plan.md)、[02 信源判读](examples/02-source-appraisal.md)）＋ references（[index](references/index.md)、[sources](references/sources.md)）＋ 本日志。
- frontmatter 口径：概念/示例/信源文档用 type: OKF 且携带 version: "1.0.0" 与 sources（resource: facts.md）；Index 文档用 type: Index 不带 version/okf_version；仅束根 index.md 携带 okf_version: "0.2"；log.md 用 created: 2026-09-01。
- 版权分层执行：现代著作（Hill/Naumburg/Kramer 等）仅 1-2 句结论性引用＋完整书目，不整段转录；AATA 定义引用标注 arttherapy.org URL；荣格《红书》出版信息以档案与基金会官网为准。
- 正文事实引用统一采用 facts 编号（facts AT-xx）逐点标注；跨束链接采用相对形态并指向姊妹束现存文件（facts.md）。

## 2026-09-01 V 阶段（对抗审查——待执行）

- 本束 V 阶段对抗审查尚待执行，本日志先行登记待抽查要点：
  1. 事实编号口径：正文 facts AT-xx 引用与 facts.md 条目逐条对应（重点抽查 AT-02、AT-09、AT-17）。
  2. 异说登记完整性：正文呈现的异说是否与 facts 条目内的并列说明一致、无单边择取。
  3. 单源待核披露：AT-09 在 facts、sources、01-founders 三处的表述是否一致。
  4. 循证表述：疗效相关段落是否仅转述综述结论并注明证据性质（重点抽查 04-theory-dialogue 第五节）。
  5. frontmatter 与 YAML 安全：双引号标量内无 ASCII 双引号、中文引号全角、日期字段书写规范。
  6. 链接完整性：束内相对链接带 .md 后缀；跨束链接指向现存文件；toctree 与实际文件一一对应。

## 2026-09-01 C 阶段（原子提交记录）

- 本束文档集按原子提交规范待提交：建议单次原子提交（type: docs, scope: okf-bundles，主题：美术治疗知识包文档集成稿），提交范围限于 art-therapy/ 目录内 13 个新建文档；facts.md（R 阶段产物）如尚未入库，应作为独立原子提交先行（type: docs, scope: okf-bundles，主题：美术治疗事实登记）。
- 提交边界：不触碰其他任何束（music-therapy、expressive-arts、dance-drama-therapy、china-art-therapy、liaoyu-overview）及组索引文件；V 阶段对抗审查通过后方可执行提交。

## 2026-09-02 视觉增补（R/E/V 阶段）

- 增补束封面配图 1 张：seedream 生成暖灰纸感编辑插画 `art-therapy-easel-mandala.jpg`（画架、半成品抽象画布、颜料画笔与曼陀罗纹样，意象化呈现以主动艺术创作为核心的工作方式），落 `doc/_static/bundles/yishu/liaoyu/art-therapy/images/`，以引导句＋图片行插入束根 [index.md](index.md)「⚠️ 免责声明」块之后、「📚 快速导航」之前。
- 增补 Mermaid 图 2 张：M4 美术治疗先驱谱系（[concepts/01-founders.md](concepts/01-founders.md) 开篇导语段后、「一、Adrian Hill」前，四人谱系链至 AATA）；M5 绘画投射技术与美术治疗并行脉络（[concepts/03-projective-techniques.md](concepts/03-projective-techniques.md)「一、定位：评估传统与治疗传统的分野」小节末、「二、Goodenough」前，双 subgraph 并行脉络）。
- 方法：seven-concepts 链路 R（视觉点盘点）→ I（高价值可视化点洞察）→ E（配图与图产出、插入）→ V（对抗验证）；图中全部人名、生卒年、书名、组织名均可溯源至本束正文与 facts（AT-01–AT-18；AATA 1969 引 OV-07），无新造事实、无因果演绎；M4 顺序为「术语—理论—平台—建制」谱系角色链而非严格生卒先后，引导句已显式声明；Mermaid 源码遵循主仓库门禁（单行标签、含中文标签双引号包裹、无 `<br/>`、块内无空行），逐字采用视觉方案单行版本，未作改写。
- 增量边界：本次仅新增引导句、图片引用行与 Mermaid 围栏块，未改动 frontmatter、事实正文、免责声明、toctree、facts.md 与 references/。
