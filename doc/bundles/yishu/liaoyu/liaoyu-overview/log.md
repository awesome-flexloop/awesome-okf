---
type: log
id: liaoyu-overview-log
title: 艺术疗愈总览知识包编纂日志
description: 艺术疗愈总览（liaoyu-overview）OKF 知识包 R-I-E-V-C 各阶段执行记录——OV-01~11 锚点事实登记、六条四元组洞察、9 文档成稿与六束协同枢纽定位。
tags: [art-therapy, 艺术疗愈, 编纂日志, 六束协同]
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
created: 2026-09-01
status: stable
stale_after: 2027-09-01
---

# 艺术疗愈总览 OKF 知识包编纂日志

> 本束为艺术疗愈知识组六束中的枢纽束：OV 层为全组提供共用锚点（术语、组织、证据、历史骨架），insights.md 汇总六束跨束洞察，本日志记录其成稿过程。

## 2026-09-01 R 阶段（信源调研与事实双源登记）

- 登记锚点事实 11 条（OV-01 ~ OV-11），全表见 [facts.md](facts.md)。其中 9 条具备 ≥2 独立信源；2 条显式标注（单源待核）：OV-07 之 NAPT 成立年份（poetrytherapy.org 本次抓取页面未显示，通称 1981）、OV-11 音乐治疗主动/接受二分（单一直接信源 Gassner & Geretsegger 2022，领域通用分类但按纪律标注）。
- 与其他束重叠的锚点事实（组织成立年、起源脉络）作为总览索引重复登记，以各组织官网为成立年权威信源；先驱生卒年不作总览层重复核对，指向各分支束的双源记录。
- 信源构成：A 级（组织官网、WHO 出版物页与报告 PDF、Cochrane 证据页与综述全文）、B 级（Nordic JACH 发布总结、BJP Moreno 史料、Eur J Public Health Gassner & Geretsegger）、C 级（Moreno Museum、Drama Therapy Resources、术语条目、artsandhealth.ie、EDN、Taikusydän）、D 级（新华网、羊城晚报，仅限中文用法梳理），分级与清单见 [references/sources.md](references/sources.md)。
- G1 质量门：事实均为纯客观陈述、无因果推断词；WHO/Cochrane 数字以报告原文与登记信源为准，转述不编数字。

## 2026-09-01 I 阶段（跨束洞察提炼）

- 六束 facts 合计 77 条（OV-01~11、AT-01~18、MT-01~16、DD-01~11、EA-01~10、CN-01~11）之上提炼 6 条四元组洞察（陈述/证据/反常识/行动），收录于 [insights.md](insights.md)：洞察 1 先驱卒年系统性后移与双源核对纪律（DD-04、EA-01 对照 MT-10、MT-08、AT-03、AT-06）；洞察 2 艺术疗愈三层外延不可混用（AT-13、MT-01、EA-05/06、OV-02/03/05/06、CN-11）；洞察 3 证据规模 ≠ 证据强度（OV-02 对照 MT-13~16、OV-09、CN-10）；洞察 4 中医五音话语与现代 music therapy 两套体系、1988 年传入锚点（CN-01~09、OV-08、MT-05）；洞察 5 组织官方定义为第一锚点且定义版本化（AT-13、DD-03、MT-12、EA-05/09、OV-07/10）；洞察 6 六分支共享五步职业化路径（AT-10/11/14/18、MT-02/04/05、DD-01/03/07/09、EA-08/09/10、OV-07/08/10）。
- 洞察维度互斥覆盖：史料考订、术语分层、证据强度、话语体系、辨析方法、建制结构；供六束横向复用，各分支束不单设 insights。

## 2026-09-01 E 阶段（文档集成稿）

- 13 个文档按束模板成稿（束根 [index.md](index.md)、concepts 6 篇、examples 3 篇、references 2 篇与本日志均为本次新建；facts.md 与 insights.md 为 R/I 阶段既有产物）：束根 [index.md](index.md)（免责声明、三大特点、四节导航、六束地图、两轨快速开始、四类学习路径与扩展占位）＋ concepts（[index](concepts/index.md)、[00 定义辨析与术语分层](concepts/00-overview.md)、[01 历史脉络与分支谱系](concepts/01-history.md)、[02 循证证据概貌](concepts/02-evidence.md)、[03 职业体系与资源地图](concepts/03-professional-orgs.md)、[04 阅读路径与方法论](concepts/04-reading-paths.md)）＋ examples（[index](examples/index.md)、[01 分支选择决策指南](examples/01-branch-chooser.md)、[02 资料可信度评估五步法](examples/02-source-appraisal.md)）＋ references（[index](references/index.md)、[sources](references/sources.md)）＋ 本日志。
- frontmatter 口径：概念/示例/信源文档用 type: OKF 且携带 version: "1.0.0" 与 sources（resource: facts.md）；Index 文档用 type: Index 不带 version/okf_version；仅束根 index.md 携带 okf_version: "0.2"；log.md 用 created: 2026-09-01。
- 版权分层执行：组织定义引用标注官网 URL；WHO/Cochrane 只作转述且数字限于 facts 登记范围；无现代著作整段转录。
- 正文事实引用统一采用 facts 编号（facts OV-xx）；跨束事实引用附加束名（如 facts MT-05，音乐治疗束）；姊妹束链接自束根用 ../<name>/index.md，自子目录按相对层级用 ../../<name>/index.md。
- 枢纽协同定位：本束不重复分支细节，概念 00/01/02/03/04 分别向五个姊妹束引流（术语→组织→证据→路径），六束地图与四类读者路径表为跨束导航入口。

## 2026-09-01 V 阶段（对抗审查——待执行）

- 本束 V 阶段对抗审查尚待执行，本日志先行登记待抽查要点：
  1. 事实编号口径：正文 facts OV-xx 引用与 facts.md 条目逐条对应；跨束事实编号（AT/MT/DD/EA/CN）与 insights.md 引用一致。
  2. 单源披露一致性：OV-07（NAPT 年份）与 OV-11（主动/接受二分）在 facts、sources、概念 03/04 与示例 02 四处表述一致。
  3. 循证表述：概念 02 全部疗效句保留 probably/may/low certainty 层级，无“治愈/有效”式无限定表述。
  4. YAML 安全：双引号标量内无 ASCII 双引号、中文引号全角、日期字段书写规范、description 单行。
  5. 链接完整性：束内相对链接带 .md 后缀；姊妹束链接相对层级正确（束根 ../、子目录 ../../）；toctree 与实际文件一一对应。
  6. 免责声明：束根免责声明含非医疗建议、术语边界、证据规模≠强度三要素。

## 2026-09-01 C 阶段（原子提交记录）

- 本束文档集按原子提交规范待提交：建议单次原子提交（type: docs, scope: okf-bundles，主题：艺术疗愈总览知识包文档集成稿），提交范围限于 liaoyu-overview/ 目录内 11 个文档（含既有 facts.md 与 insights.md 如尚未入库应先行独立提交）。
- 提交边界：不触碰五个姊妹束（art-therapy、music-therapy、dance-drama-therapy、expressive-arts、china-art-therapy）及 liaoyu/yishu 组索引文件；V 阶段对抗审查通过后方可执行提交。
- 六束协同待办：expressive-arts 与 china-art-therapy 两束的集成稿完成后，核对本束六束地图中该两束定位语与其目录结构的一致性。
