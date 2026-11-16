---
okf_version: "0.2"
type: bundle
title: "TRAE 2026-11-15 周报：四项更新与五步核验教程"
description: "TRAE 官方周报（一键部署/画中画/好应用大赏赛/社区创作者计划）的可溯源解读，含 51 条事实、15 项 P0 核验、渠道差异登记与可迁移的厂商周报核验教程；厂商官方公告单源，非操作教程"
tags:
  - trae
  - weekly-update
  - one-click-deploy
  - picture-in-picture
  - creator-ecosystem
  - source-verification
  - tutorial
  - product-announcement
generated: 2026-11-16
verified: process:seven-concepts-v
status: draft
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/LxoUITnmaiH3CzI4AAz0iA
    title: "一周更新：一键部署上线、社区创作者计划开启等"
    author: "TRAE（公众号 TRAE.ai）"
    date: 2026-11-15
  - id: official-changelog
    url: https://trae.cn/changelog
    title: "TRAE 官方更新日志（v3.4.12 / v3.4.15）"
  - id: official-forum-creator
    url: https://forum.trae.cn/t/topic/184139
    title: "TRAE 官方中文社区：社区创作者计划正式招募"
  - id: official-weibo-contest
    url: https://www.sina.cn/news/detail/5363724388141142.html
    title: "TRAE 官方微博：好应用大赏赛（新浪转载）"
  - id: official-contest-detail
    url: http://mp.weixin.qq.com/s?__biz=MzkxMTY4NTAyNQ==&mid=2247521729&idx=1&sn=b74dbc2111733e72db94679ed9164d18
    title: "TRAE 官方：万元大奖！好应用大赏赛正式启动"
  - id: official-pip-detail
    url: http://mp.weixin.qq.com/s?__biz=MzkxMTY4NTAyNQ==&mid=2247521962&idx=1&sn=47c64211111fcb2bc4e6d80b3ef6f02a
    title: "TRAE 官方：我们给 TRAE 加了个画中画小窗"
---

# TRAE 2026-11-15 周报：四项更新与五步核验教程

> **内容性质**：厂商官方周报解读（**非操作教程**、**非源码教程**）。基于公众号「TRAE」2026-11-15 周报，交叉核验 TRAE 官方更新日志、官方中文社区、官方微博及两篇官方专文。
>
> **厂商自述数据提示**：本周报正文**无任何提效倍数／工时节省／成本下降数字**（F-032），无营销数据污染。官方画中画专文中的「高帧率下 CPU 占用通常低于 5%」为**厂商自述压测口径、无第三方实测**（F-049），不在本周报正文，本包不将其写为结论。
>
> **核验结果**：P0 15 项 → **9 ✅ / 6 ⚠️ / 0 ❌**（逐项总表机械计数）。⚠️ 的性质是「摘要体省略了详情页硬约束」与「官方渠道间口径差异」，**不是已证伪**。详见 [核验报告](references/verification.md)。
>
> **不含 `examples/` 的原因**：按操作可复现性两问——问一（有无可照做的流程）为弱是（仅活动／功能入口指引）；问二（是否经作者实测、有版本／输入输出／步骤顺序）为**否**（无版本号、无实测、无输出示例，F-032/F-033）。任一为否即不设，空 `examples/` 制造伪结构。`concepts/03` 是可 follow 的**方法论教程**，不是产品操作示例。

## 读者与用途

| 你想做什么 | 读哪里 |
|-----------|--------|
| 查「这周 TRAE 公布了什么、各事项真正首发于何时」 | [00 本周更新全景](concepts/00-weekly-overview.md) |
| 查某项功能的能力边界与官方版本精确化 | [01 产品能力层](concepts/01-product-capabilities.md) + [trae-one-click-deploy](../trae-one-click-deploy/index.md) |
| 查赛事／创作者计划的完整规则与报名口径 | [02 创作者生态层](concepts/02-creator-ecosystem.md) |
| 学「下次如何自己核验一份厂商公告」 | [03 五步核验法教程](concepts/03-verification-tutorial.md) |

## 术语速查

| 术语 | 一句话 |
|------|--------|
| bundle / 本包 | OKF 知识包，最小交付单元；`concepts/` 概念、`references/` 信源、`index.md` 导航 |
| F-xxx | 事实登记编号，本包 F-001~F-051；`R7:F-046` 这类带前缀的是**其他 bundle** 的编号 |
| CD-xxx | 渠道差异台账编号；状态「未澄清」＝暂停判定、须复核，**不等于已判定谁正确** |
| P0 | 必核验级声明：数字／日期／官方表态／功能时间线／成效数字 |
| ✅ / ⚠️ | ✅＝官方渠道间口径一致（非独立证实）；⚠️＝单源或摘要体省略详情页约束 |
| 信源距离 | 发布方离事实的远近，决定采信力度；本包全部为厂商一手 |
| `status: draft` | 单源密集／口径待收敛；`flagged` 用于核心声明被证伪 |
| `stale_after` | 复核到期日，到期不自动下架，须人工复核 |
| `toctree` | Sphinx 站点导航配置块，非正文内容 |

## 一句话结论

这一周报是**一次渠道汇总，不是四次首发**：画中画的实际版本落地在 10-30 v3.4.12，创作者计划在 10-14 已由官方社区首发，大赏赛 11-10 已有完整赛事专文，一键部署 11-12 已有单篇公告。把它读成「四项新功能上线」会系统性高估本周增量；本包同时提供一个可迁移的交付物——**五步核验法**，教读者下次如何自己把厂商公告转成不会误导后来人的知识条目。

## 信源说明

> ⚠️ **信源独立性边界**：本包 R1~R6 全部同属 TRAE 一方（官方公众号／更新日志／官微／官方社区／官方专文），R7 是本仓既有 bundle，R8 为第三方转述但不单独作为事实依据。所谓「交叉核验」实为**同一厂商不同发布渠道之间的口径对齐**，**15 项 P0 无一项有独立第三方验证**；上表 ✅ 仅表示官方渠道间口径一致。详见 [核验报告前置判据](references/verification.md)。

| 信源 | 类型 | 层级 | 用途 |
|------|------|------|------|
| 公众号「TRAE」周报（2026-11-15） | 主信源 | 厂商官方（一手） | 四项公告的存在性、官方表述、文章结构 |
| TRAE 官方更新日志 | 权威 | 官方文档 | 画中画精确版本与日期、一键部署站点管理条目 |
| TRAE 官方中文社区帖（10-14） | 权威 | 官方社区 | 创作者计划五类方向、六项权益、报名表单 |
| TRAE 官方微博（11-10） | 权威 | 官方社媒 | 大赏赛规则与报名口径（渠道差异来源） |
| TRAE 官方赛事专文（11-10） | 权威 | 厂商官方（一手） | 完整赛程、五赛道、六条作品要求、奖项 |
| TRAE 官方画中画专文（11 月） | 权威 | 厂商官方（一手） | 只读／接管机制、后台渲染、平台边界 |
| 本仓 `trae-one-click-deploy` 核验报告 | 内部参照 | 既有知识包 | 同主题交叉引用与结论冲突登记 |

完整 8 条信源清单与 F 编号映射见 [信源索引](references/index.md)。

## 知识结构总览

```
trae-weekly-update-20261115/
├── index.md                                    ← 你在这里
├── log.md                                      生成与门禁日志
├── concepts/
│   ├── 00-weekly-overview.md                    四项时间线、信源距离分层、时效边界
│   ├── 01-product-capabilities.md               一键部署链路、画中画只读镜像与接管机制
│   ├── 02-creator-ecosystem.md                  赛事规则、创作者权益、渠道口径差异
│   └── 03-verification-tutorial.md              ★ 五步核验法教程（可独立 follow）
└── references/
    ├── article-source.md                        事实登记 F-001~F-051（双份之一）
    └── verification.md                          15 项 P0 核验 + 勘误四张清单 + 缺口登记
```

## 分层导航

### 概念文档（4 篇）

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [本周更新全景](concepts/00-weekly-overview.md) | 四项公告的官方首发时点、信源距离四层、三条洞察 |
| 01 | [产品能力层](concepts/01-product-capabilities.md) | 发布链路收口、画中画状态机、官方版本精确化、跨 bundle 结论冲突 |
| 02 | [创作者生态层](concepts/02-creator-ecosystem.md) | 六条作品硬要求、四段赛程、六项权益、五处渠道差异总账 |
| 03 | [五步核验法教程](concepts/03-verification-tutorial.md) | 信源距离→F 编号→P0→勘误四清单→时效状态，含 7 条反模式与跨领域迁移 |

### 信源参考（2 篇）

| 文档 | 内容 |
|------|------|
| [事实登记](references/article-source.md) | F-001~F-051，按发布元信息／四板块／信源结构／核验补充分组；与 spec `facts.md` 双份登记 |
| [P0 核验报告](references/verification.md) | 15 项逐项结论、勘误四张清单、6 项缺口登记、与既有 bundle 的结论冲突登记 |

## 信任与生命周期

- **P0 核验**：15 项中 9 项通过、6 项部分通过、0 项失败（机械计数见核验报告总表）。
- **事实分级**：原文事实 33 条、核验补充 18 条；**作者观点 0 条**（公告体，官方定位均按「官方表述」标注）。
- **status: draft 的理由**：① 四板块均为厂商单一渠道公告、能力细节无独立实测；② 3 处官方渠道间口径差异待收敛；③ 活动类信息在 2026-12-06 后失效。与同分组 [`trae-one-click-deploy`](../trae-one-click-deploy/index.md)（同样厂商单源，draft）先例一致。**不置 `flagged`**（核心声明未被证伪）。
- **分板块失效时点**（单个到期日无法覆盖）：报名 11-23 截止 → 02 篇报名口径失效；评审 11-24 起、获奖公布 12-04~12-06 → 赛程与奖项失效；创作者计划首批招募完成 → 权益与入口失效；限免结束 → 01 篇计费边界失效。
- **到期处置**（`stale_action` 语义）：`stale_after: 2026-12-31`；到期未复核应转 `flagged` 或归档，不得继续以 `draft` 正常呈现。
- **复核责任人**（`review_owner` 语义）：**待指派**（本包生成时未指定 owner），须在首次复核前落名。二者以正文声明而不新增 frontmatter 自定义字段，以保持与全库既有 bundle frontmatter 的字段一致性（V 阶段审查决策，见 `log.md`）。
- **stale_after 到期须复核**：① 赛事获奖结果与日程是否调整 ② 限免是否结束 ③ 创作者计划首批 100 位是否招募完成 ④ 画中画 Windows 版是否全量 ⑤ 三处渠道差异是否获官方澄清。

## 已知边界

1. **无客户端版本号**：周报只说「升级至最新版本」，官方日志 11-03 与 11-08 均标 v3.4.15，第三方称 11-09 为 v3.4.17（F-036），无法定位具体构建。
2. **限免规则未知**：起止时间、结束后计费口径未给出。
3. **报名起始日差异**：11.9（官方微博）／11.10（周报＋赛事专文），未见官方澄清（见 [CD-001 台账](references/verification.md)）。
4. **招募状态未知**：首批 100 位是否仍开放、截止时间未给出。
5. **平台可用性**：画中画 macOS 已上线，Windows「陆续开放体验」（F-049），周报未提。
6. **奖项金额歧义**：赛事专文图片 OCR 中冠亚军金额顺序存在歧义（F-045）。
7. **无实测证据**：四项能力／活动均无实际站点链接、构建日志、耗时或第三方实测，本包不提供可复现步骤。
8. **跨 bundle 结论未改写**：`trae-one-click-deploy` 核验表第 3 项记「官方日志无独立条目」，本次发现 11-08 站点管理条目（灰度中），已登记「须复核」但不改写原束。

## 主题关联

| 关联束 | 关系 |
|--------|------|
| [TRAE Community 生态（分组首页）](../index.md) | 上级分组；本束归入「📰 战略资讯」板块（厂商周报解读） |
| [trae-one-click-deploy](../trae-one-click-deploy/index.md) | **同主题**：11-12 单篇公告的深度解读（六步链路、可见性模型、支持范围与硬边界）；本束只做周报中的摘要 + 版本侧进展，二者分工互补 |
| [threeui](../threeui/index.md) | 同为资讯盘点类博文转化束，同样因操作可复现性两问而不设 `examples/` |
| [tushare-ai-office](../tushare-ai-office/index.md) | 同为厂商动态类，其 P0 出现 ❌ 故 `status: flagged`；本束 0 ❌ 但单源密集，取 draft |
| [bytedance-ai-consolidation](../bytedance-ai-consolidation/index.md) | 字节 AI 业务组织与竞争格局背景（TRAE 所属体系） |

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
