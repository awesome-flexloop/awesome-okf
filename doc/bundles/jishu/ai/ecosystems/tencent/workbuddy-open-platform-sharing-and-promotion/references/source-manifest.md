---
type: Reference
title: "WorkBuddy 开放平台两篇平台公告 · 逐页采集与覆盖台账"
description: "A1/A2 两篇平台公告与 N1/N2 平台导航面的逐页覆盖登记——URL、访问日期、标题、正文解析状态、知识归属文档与覆盖状态，并含公告页侧边栏 13 项模块地图登记与「已声明集合 = 已处理集合」双向差集结论"
tags: [WorkBuddy, 开放平台, 采集台账, 覆盖登记, OKF]
generated: { by: "process:seven-concepts-r", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: A1, resource: "https://open.workbuddy.cn/dashboard/contents/ann_1791894782641_zyedev?source=announcement" }
  - { id: A2, resource: "https://open.workbuddy.cn/dashboard/contents/ann_1790063369912_8degpw?source=announcement" }
  - { id: N1, resource: "https://open.workbuddy.cn/" }
  - { id: N2, resource: "https://open.workbuddy.cn/dashboard" }
---

# 逐页采集与覆盖台账

## 采集方法与边界

- **采集时点**：2026-10-15（本束核验快照基准）。
- **采集方式**：`open.workbuddy.cn` 为 SPA，需登录会话方能读取渲染后正文；本次经受控浏览器在**已登录会话**中读取 `document.body.innerText`，两篇公告（A1/A2）均取得**完整正文**（非摘要、非截断）。
- **采集边界**：仅采集 A1/A2 两篇公告正文与公告页侧边栏可见的平台导航面；公告正文中提及但未展开的指向物（《PC 端开发手册》、WorkBuddy 品牌设计规范、WorkBuddy 客户端 5.8.0）仅登记为指引入口，不展开学习；不采集开放平台后台的「注册应用」「新建推广」等操作型页面（需真实账号且会产生真实数据）；不做站外递归抓取。
- **登记纪律**：模块地图仅证明「这些入口在公告页侧边栏存在」，**不据模块名称推断其功能细节**；凡未采集的模块，一律标注「本次未采集，仅登记入口」。
- F 编号事实见[事实登记](article-source.md)（F-001 ~ F-064）；本台账记录**页级**覆盖，事实登记记录**声明级**覆盖；核验结论见[核验报告](verification.md)。

## 集合比对结论（AC-1）

| 项 | 值 |
| --- | --- |
| 本束声明处理的页面集合（内容页 + 导航面） | 4（A1 / A2 / N1 / N2） |
| 已处理（取得采集结果）集合 | 4 |
| 双向差集 | 0（`已声明 - 已处理` = 0，`已处理 - 已声明` = 0） |
| 正文解析状态 = 已取得完整正文 | 2（A1 / A2） |
| 正文解析状态 = 可达（导航面，仅核可达性） | 2（N1 / N2） |
| 平台模块地图登记行 | 13（全部标注「本次未采集，仅登记入口」） |

> **结论**：`已声明页面集合 = 已处理集合`，双向差集为空。模块地图 13 行**只登记入口不求证能力**，在[核验报告](verification.md)「五类口径」中作为「公告口径 vs 平台现状」的边界说明。

## 内容页与导航面明细（六要素）

六要素：URL、访问日期、标题、正文解析状态、知识归属文档、覆盖状态。

| 编号 | URL | 访问日期 | 标题 | 正文解析状态 | 知识归属文档 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | <https://open.workbuddy.cn/dashboard/contents/ann_1791894782641_zyedev?source=announcement> | 2026-10-15 | WorkBuddy开放平台上线「分享能力接入」，支持第三方应用将内容分享至WorkBuddy | 已取得完整正文（渲染后正文，非摘要非截断） | concepts/01-share-capability-integration.md；examples/00-integrate-share-capability.md | 已学习（归纳覆盖，未逐字镜像） |
| A2 | <https://open.workbuddy.cn/dashboard/contents/ann_1790063369912_8degpw?source=announcement> | 2026-10-15 | WorkBuddy 开放平台上线「推广管理」，支持生成分享链接与微信小程序码 | 已取得完整正文（渲染后正文，非摘要非截断） | concepts/02-promotion-management.md；examples/01-create-and-track-promotion.md | 已学习（归纳覆盖，未逐字镜像） |
| N1 | <https://open.workbuddy.cn/> | 2026-10-15 | WorkBuddy 开放平台（入口） | 可达（导航面，仅核可达性） | concepts/00-open-platform-overview.md | 已学习（入口可达性核实） |
| N2 | <https://open.workbuddy.cn/dashboard> | 2026-10-15 | WorkBuddy 开放平台（首页） | 可达（导航面，仅核可达性） | concepts/00-open-platform-overview.md | 已学习（入口可达性核实） |

> A1/A2 的公告日期（2026-10-14）、栏目（平台公告）与版本要求（客户端 5.8.0）在[事实登记](article-source.md)中逐条可核（F-017 / F-018 / F-028 / F-034 / F-035 / F-046 / F-058）。

## 公告页侧边栏 · 平台模块地图登记（13 行）

> **登记价值**：证明这些入口在公告页侧边栏存在，并作为 concepts/00 模块地图表的数据来源。**逐行标注「本次未采集，仅登记入口」**——不据模块名称推断功能细节。

| # | 模块 | 路径 | 知识归属文档 | 覆盖状态 |
| --- | --- | --- | --- | --- |
| 1 | Buddy 应用 | `/buddy-app/all` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 2 | 专家 | `/expert/all` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 3 | 技能 | `/skill/all` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 4 | 连接器 | `/connector/all` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 5 | 硬件接入 | `/application/all/device` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 6 | 分享功能接入 | `/app-feature/all` | concepts/01-share-capability-integration.md | 本次未采集，仅登记入口（A1 的功能入口） |
| 7 | 积分兑换 | `/application/all/credit` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 8 | 推广管理 | `/growth` | concepts/02-promotion-management.md | 本次未采集，仅登记入口（A2 的功能入口） |
| 9 | 数据概览 | `/operations` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 10 | 推广效果 | `/growth/effect` | concepts/02-promotion-management.md | 本次未采集，仅登记入口（A2 的数据入口） |
| 11 | 收入变现 | `/monetization` | concepts/00-open-platform-overview.md | 本次未采集，仅登记入口 |
| 12 | 认证信息 | `/settings/cert-info` | concepts/03-boundaries-versions-and-policy.md | 本次未采集，仅登记入口（与「企业认证」开放门槛相关） |
| 13 | 开发者信息 | `/settings/developer` | concepts/03-boundaries-versions-and-policy.md | 本次未采集，仅登记入口（与开发者身份相关） |

> **补救方式**：如后续需各模块能力细节，应另立新束逐页采集对应模块独立页；本束不据路径或名称推断任何能力项。
