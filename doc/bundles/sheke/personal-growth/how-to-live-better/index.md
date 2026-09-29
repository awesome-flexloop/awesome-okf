---
okf_version: "0.2"
type: bundle
title: 高性价比人生指南（HowToLiveBetter）循证生活决策精读教程
description: "开源书 HowToLiveBetter（615 条/33 章，Unlicense）的多信源精读教程——证据分级与四资源性价比两套评价系统、33 章导览、21 条标杆条目逐条核验精读（CPR/低钠盐/卒中/反诈/N+1 等）、检索页与 AI skill 用法、边界与决策迁移；含 19 项 P0 独立核验（498→608→615 版本演进对照）"
tags: [循证决策, 生活指南, 高性价比人生指南, HowToLiveBetter, 证据分级, 成本收益, 急救, 法律红线, 职场维权, 个人成长, 开源项目导读, 统计素养]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-28T21:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-28T21:30:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: blog
    resource: https://blog.mushroom.cv/blog/howtolive-better-evidence-based-chinese-life-guide-498-tips/
    title: mushroom.cv《高性价比人生指南：498 条循证建议……》（Mycelium Protocol，2026-09-17，CC BY 4.0）
  - id: live
    resource: https://eternity4719.github.io/HowToLiveBetter/
    title: 官方在线检索页
  - id: mirror-dlgrv
    resource: https://dlgrv.github.io/HowToLiveBetter/zh/?sec=1
    title: dlgrv 非官方翻译快照（608 条，滞后）
  - id: mirror-cdy
    resource: https://cdyforever.github.io/how-to-live-better/
    title: cdyforever 33 节渲染镜像
  - id: repo
    resource: https://github.com/eternity4719/HowToLiveBetter
    title: 原仓（README/book 33 章/docs/skills，Unlicense）
  - id: api
    resource: https://api.github.com/repos/eternity4719/HowToLiveBetter
    title: GitHub API 元数据（2026-09-28）
  - id: pubmed-ssass
    resource: https://pubmed.ncbi.nlm.nih.gov/34459569/
    title: 核验源：SSaSS 低钠盐 NEJM 2021
  - id: cochrane-helmet
    resource: https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004333.pub3/full
    title: 核验源：Cochrane 头盔评价
  - id: pubmed-ohca
    resource: https://pubmed.ncbi.nlm.nih.gov/37722403/
    title: 核验源：BASIC-OHCA Lancet Public Health 2023
  - id: nhtsa-2022
    resource: https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813573
    title: 核验源：NHTSA 乘员保护 2022 数据
  - id: who-gsrrs2023
    resource: https://cdn.who.int/media/docs/default-source/country-profiles/road-safety/road-safety-2023-chn.pdf
    title: 核验源：WHO 全球道路安全现状报告 2023（中国）
  - id: npc-antifraud
    resource: http://www.npc.gov.cn/npc/c2/c30834/202209/t20220902_319186.html
    title: 核验源：反电信网络诈骗法
  - id: npc-contract
    resource: http://www.npc.gov.cn/npc/c1773/c2518/c12898/201905/t20190523_46320.html
    title: 核验源：劳动合同法
  - id: mca-2024
    resource: https://www.mca.gov.cn/gdnps/n2445/n2451/n2458/n2681/c1662004999980006189/attr/400985.pdf
    title: 核验源：民政部 2024 年统计公报
---

# 高性价比人生指南（HowToLiveBetter）循证生活决策精读教程

> **⚠️ 性质声明**：本 bundle 是对开源项目 **HowToLiveBetter《高性价比人生指南》**（Unlicense，github.com/eternity4719/HowToLiveBetter）的**第三方导读与核验转化**，非原书、非官方出版物，**不构成医疗、法律或投资建议**——重大决策请咨询执业医师/律师/持牌机构并核对当期有效法规。原书持续高频更新（2026-09-07 上线；498 条是 2026-09-17 二手博文快照，2026-09-28 原仓已为 615 条），全量 615 条与最新数字**一律以原仓为准**；本包仅精读 21 条标杆条目。

> **📌 版本时点提示（2026-09-28）**：你在二手文章里看到的"498 条/31 章/A323·B126·C49/极高 88"是 **2026-09-17 博文快照**；原仓现行口径为 **615 条/33 章/A415·B151·C49/争议 57/TODO 35/极高 104·高 279·一般 232**，dlgrv 镜像的 608 条是滞后翻译快照。三套数字是版本演进而非矛盾（[核验报告](references/verification.md)版本对照表）。

> **📌 核验提示**：2026-09-28 对 19 项关键声明完成独立权威核验，并用**原仓完整本地克隆**（commit bad9e99）对全书 33 章逐章机器核对——33 章条目数求和精确 = 615、21 条精读的 29 个关键数字 29/29 命中、10 项医学研究全部真实且效应值逐字吻合。确认原书 3 处口径问题已在正文按核验值呈现（溶栓为 9 项 RCT 非 16 项、BASIC-OHCA 的 20.3%/1.2% 为全队列口径、燃气指定产品禁令为条例第 18 条第 6 项）；2 处出处/措辞精化；另有 1 处系本包早期摘要的自我更正（肇事逃逸条——原书本就正确并列引用实施条例第 92 条）。均为非核心细节，`status: stable`。

《高性价比人生指南》解决大多数生活建议的两个通病——**没来源**，或有来源但不告诉你**值不值**：615 条建议每条写明花掉什么（钱/时间/毅力）、换回什么（寿命/时间精力/金钱/人身自由）、证据多硬（A/B/C，只引期刊论文与官方文件）、来源在哪，并按性价比而非类别排序。本知识包按 R→I→E→V 转化流程生成：**89 条事实登记**（F-001~F-089，含 19 项 P0 核验补充与本地全量克隆结构审计）、7 篇概念文档、2 篇信源文档。

---

## 信源说明

| 信源 | 类型 | 覆盖 |
|---|---|---|
| 原仓 README/book/docs/skills + GitHub API | 一手（项目本体与平台数据） | 现行 615 条/33 章口径、机制规则、精选条目原文、元数据与时点 |
| NEJM/Cochrane/JAMA/Lancet/China CDC Weekly/AHA/WHO/NHTSA/全国人大/政府部委/民政部 | 核验信源（一手期刊与官方页） | 19 项 P0 结论（F-070~F-086） |
| mushroom.cv 博文（CC BY 4.0，2026-09-17） | 第三方善意盘点 | 498 条时代快照、项目早期增长数据 |
| dlgrv / cdyforever 两个 Fork | 二手镜像 | 608 条版本证据、33 章结构交叉印证 |

完整事实与核验见 [references/article-source.md](references/article-source.md) 与 [references/verification.md](references/verification.md)。

---

## 📚 知识结构总览

```
how-to-live-better/
├── concepts/                         # 7 篇概念教程
│   ├── 00-project-landscape.md       # 事实层：项目全貌与 498→608→615 版本演进
│   ├── 01-evidence-grading.md        # 机制层：A/B/C、争议/TODO 与统计数字素养
│   ├── 02-cost-benefit-model.md      # 机制层：四资源/三成本/量级阈值/性价比档/受益人四档
│   ├── 03-chapter-map.md             # 导航层：33 章四大板块导览 + 5 篇长文（Mermaid）
│   ├── 04-high-value-entries.md      # 应用层：21 条标杆条目精读
│   ├── 05-how-to-use.md              # 使用层：检索页/离线三件套/AI skill/自托管/选站
│   └── 06-boundaries-and-method.md   # 迁移层：六条边界 + 评估任意建议的七步工作表
├── references/
│   ├── article-source.md             # F-001~F-089 多信源事实双份登记
│   └── verification.md               # 19 项 P0 核验 + 版本演进对照 + 勘误四清单
├── index.md                          # 本文件
└── log.md                            # 生成日志
```

> 本 bundle **不设 examples/**：按"操作可复现性两问"判定——作品主体是生活建议而非经实测的技术操作流程；检索页筛选、离线版下载、AI skill 安装等使用动作已在 [concepts/05](concepts/05-how-to-use.md) 以图文步骤承载（判定记录见转化 spec）。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|---|---|
| [项目全貌与版本演进](concepts/00-project-landscape.md) | 项目档案（Unlicense、2026-09-07 上线、19,238 星/1,355 fork@2026-09-28）、数据即网页的架构、498→608→615 时间线、docs 长文与 AI skill 生态、"备选单非任务清单"姿态 |
| [证据分级与统计数字素养](concepts/01-evidence-grading.md) | A/B/C 判定界线、争议（57）与 TODO（35）机制、只引一手纪律、九组统计术语（RCT/荟萃/队列/HR·RR·OR/CI/混杂/反向因果）、独立核验发现的两处口径修正、三步质疑法 |
| [四资源与性价比决策模型](concepts/02-cost-benefit-model.md) | 四资源不跨口径、三成本、收益量级事前阈值表、极高/高/一般合档规则（档位作者自承 C 级、与证据正交）、受益者四档不合并、七步决策算法 |
| [33 章导览与长文地图](concepts/03-chapter-map.md) | 四大板块 Mermaid 全景；33 章逐章"代表问题+口径"表；docs 五篇长文（结婚账本/应急装备/生物钟夜班/陌生人救助/平台资质）导引 |
| [标杆条目精读 21 条](concepts/04-high-value-entries.md) | 健康安全 14（安全带/头盔/报警器/燃气/蘑菇/血压/安全座椅/救生衣/CPR/老人摔倒/卒中/眼中风/心梗/低钠盐）+法律 3（逃逸/反诈/AI 换脸）+职场 2（加班费/N·N+1·2N）+人生大事 2（择偶可预测性/离结比），逐条六要素与核验注 |
| [如何使用：检索页、离线版与 AI skill](concepts/05-how-to-use.md) | 五维组合筛选、三个推荐筛选组合、HTML/PDF/EPUB 固定下载链接、life-decision-guide 在 Claude Code/Codex 的安装与"查不到不编"边界、自托管三坑、四站选择表 |
| [适用边界与方法迁移](concepts/06-boundaries-and-method.md) | 六条边界（法域/时点/角色/外推/证据类型/署名）、对抗视角软肋自查、评估任意外部建议的七步工作表与盘问示范 |

### 信源层（references/）

| 文档 | 核心内容 |
|---|---|
| [多信源事实清单](references/article-source.md) | F-001~F-089 双份登记：元信息 15、版本计数 9、机制规则 18、精选条目 27、核验补充 17、R1 补登 2、本地全书审计 1；事实/作者观点/快照三层标记 |
| [P0 核验报告与版本演进对照](references/verification.md) | 医学 10 项+法规社科 9 项三态总表；498/31→608→615/33 对照；勘误四张清单（日期版本/数字溯源/口径对照/引文条号）；信源距离五分类；**本地完整克隆逐章审计（33 章求和=615、29/29 命中）**；方法边界 |

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2026-09-28 原仓 main 分支（615 条口径）与同日前完成的 19 项一手信源核验生成
- **事实规模**：89 条 F 编号（F-001~F-089），双份登记集合一致
- **核验情况**：P0 共 19 项——✅ 通过 16 项（含 1 项本包摘要自我更正）、⚠️ 原书口径问题 3 项（均已在正文按核验值呈现）、口径/出处精化 2 项、❌ 核心声明失败 0 项；另经本地完整克隆逐章审计全书结构（F-089）；无硬编 URL、无"研究不存在"
- **status**：stable——所有差异均为非核心细节，原书循证框架与核心数字经独立核验成立
- **stale_after**：2027-03-31——方法论骨架跨周期有效；条目计数、stars、法规条款与金额属强时效内容，到期前应对照原仓复核
- **方法论链路**：R（多信源采集 + 19 项 P0 核验）→ I（三层知识拆分：事实/机制/导航应用）→ E（信源先行成文）→ V（四视角审查 + 八项机械门禁），详见 [log.md](log.md)

### 已知边界

1. **非专业建议**：健康条目不替代诊疗（急症 120、用药遵医嘱），法律条目不替代律师意见，金额与处罚档次以主管机关当期规定为准。
2. **数字时点**：615/415/151/49、104/279/232、19,238 stars 等均为 2026-09-28 时点值；博文 498 口径仅作历史快照。
3. **C 级与 TODO**：C 级 49 条为作者经验/共识；35 处 TODO 是原书自承未核到官方原文的缺口；引用时不得把这两类当硬证据。
4. **镜像滞后**：dlgrv 608 条为自声明滞后的翻译快照，cdyforever 不保证同步；事实判断只以原仓为准。
5. **抽样核验**：本包只独立核验 19 项 P0 与 21 条精读条目的直接引文，不对 615 条全部引文负责；原书 `docs/引用对照.md`（约 110KB）与 `docs/核实记录/` 是其持续核验工件。
6. **许可与署名**：原书 Unlicense、介绍博文 CC BY 4.0（© Mycelium Protocol）；本包为蒸馏导读非全量搬运，转发原书或博文内容时分别遵守其许可与署名要求。

---

**本知识包共收录 9 个内容文档（7 个概念 + 2 个信源），外加 2 个子目录索引、根索引与生成日志，合计 13 个文件。**

同组相关：[female-charm-eq](../female-charm-eq/index.md) 与 [male-charm-eq](../male-charm-eq/index.md)（魅力与情商专项能力教程，附 30 天实操路线）——本包提供"用证据评估一切生活决策"的通用框架与条目库，两束提供亲密关系场景的专项能力模型，三者同属"用证据优化个人生活"主题簇。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
