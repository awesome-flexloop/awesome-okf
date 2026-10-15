---
type: Concept
title: "WorkBuddy 开放平台是什么：模块地图与两篇公告的位置"
description: "open.workbuddy.cn 的模块地图（13 项入口，逐项标注覆盖状态）与两篇平台公告（分享能力接入 / 推广管理）在平台中的位置及本篇阅读路径。"
tags: [WorkBuddy, 开放平台, 模块地图, 平台公告, 腾讯]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: A1, resource: "https://open.workbuddy.cn/dashboard/contents/ann_1791894782641_zyedev?source=announcement" }
  - { id: A2, resource: "https://open.workbuddy.cn/dashboard/contents/ann_1790063369912_8degpw?source=announcement" }
  - { id: N1, resource: "https://open.workbuddy.cn/" }
  - { id: N2, resource: "https://open.workbuddy.cn/dashboard" }
---

# WorkBuddy 开放平台是什么：模块地图与两篇公告的位置

WorkBuddy 开放平台是腾讯 WorkBuddy 面向开发者 / 合作方的开放入口，平台入口 `https://open.workbuddy.cn/` 与首页 `https://open.workbuddy.cn/dashboard` 在核验时点 **2026-10-15** 均可达（F-001、F-002，`平台现状`，`核验时点 2026-10-15`）。本束采集对象只有该平台「平台公告」栏目下的两篇上线公告；各模块的独立页面**本次未采集**，下文模块地图仅证明「这些入口在公告页侧边栏存在」，**不得**据模块名称推断其功能细节（F-003，`未采集`）。

## 平台模块地图（13 项，全部仅登记入口）

公告页侧边栏呈现 **13 项**模块入口（F-003），逐项路径与覆盖状态如下（F-004 ~ F-016，`未采集`）：

| 模块 | 路径 | 覆盖状态 | 与本束的关系（事实） |
| --- | --- | --- | --- |
| Buddy 应用 | `/buddy-app/all` | 本次未采集，仅登记入口 | 资产类型之一，公告称其分享功能「正在规划中」（F-004、F-053） |
| 专家 | `/expert/all` | 本次未采集，仅登记入口 | 资产类型之一，支持「分享链接 + 微信小程序码」（F-005、F-051） |
| 技能 | `/skill/all` | 本次未采集，仅登记入口 | 资产类型之一，支持「分享链接 + 微信小程序码」（F-006、F-051） |
| 连接器 | `/connector/all` | 本次未采集，仅登记入口 | 资产类型之一，暂时仅支持「分享链接」（F-007、F-052） |
| 硬件接入 | `/application/all/device` | 本次未采集，仅登记入口 | 平台模块，本束不覆盖其内容（F-008） |
| 分享功能接入 | `/app-feature/all` | 本次未采集，仅登记入口 | **A1 的功能入口，本束覆盖其能力口径**（F-009） |
| 积分兑换 | `/application/all/credit` | 本次未采集，仅登记入口 | 平台模块，本束不覆盖其内容（F-010） |
| 推广管理 | `/growth` | 本次未采集，仅登记入口 | **A2 的功能入口，本束覆盖其能力口径**（F-011） |
| 数据概览 | `/operations` | 本次未采集，仅登记入口 | 平台模块，本束不覆盖其内容（F-012） |
| 推广效果 | `/growth/effect` | 本次未采集，仅登记入口 | **A2 的数据入口，本束覆盖其效果口径**（F-013） |
| 收入变现 | `/monetization` | 本次未采集，仅登记入口 | 平台模块，本束不覆盖其内容（F-014） |
| 认证信息 | `/settings/cert-info` | 本次未采集，仅登记入口 | 与「企业认证」开放门槛相关（F-015、F-029） |
| 开发者信息 | `/settings/developer` | 本次未采集，仅登记入口 | 与开发者身份相关（F-016） |

> **登记纪律**：上表 13 行全部标注「本次未采集，仅登记入口」；模块地图只证「入口存在」，不证其功能（F-003、F-064）。凡未采集的模块，一律不得据名称补全能力细节。

## 两篇公告在平台中的位置

两篇公告均为**公告口径**（面向开发者的上线通知，非接口文档），其位置与归属如下（F-017、F-018、F-034、F-035）：

| 公告 | 标题 | 发布日期 / 栏目 | 对应模块入口 | 事实 |
| --- | --- | --- | --- | --- |
| A1 | WorkBuddy开放平台上线「分享能力接入」，支持第三方应用将内容分享至WorkBuddy | 2026-10-14 / 平台公告 | 分享功能接入 `/app-feature/all` | F-017、F-018、F-009 |
| A2 | WorkBuddy 开放平台上线「推广管理」，支持生成分享链接与微信小程序码 | 2026-10-14 / 平台公告 | 推广管理 `/growth` | F-034、F-035、F-011 |

两篇公告**同日同栏目**发布（均 2026-10-14，栏目均为「平台公告」），且**均要求客户端 5.8.0 及以上版本**（F-058，`版本时效`）。

## 阅读路径（本篇回答「平台是什么」，能力细节分三篇）

| 想回答的问题 | 去哪篇 |
| --- | --- |
| 分享能力接入是什么、第三方应用怎么接入、审核与密钥怎么走 | [01-share-capability-integration](01-share-capability-integration.md) |
| 推广管理是什么、怎么创建与追踪效果、资产类型差异在哪 | [02-promotion-management](02-promotion-management.md) |
| 能不能接入、支持哪些端与资产、版本门槛与口径落差 | [03-boundaries-versions-and-policy](03-boundaries-versions-and-policy.md) |

- 事实出处与核验：[事实登记](../references/article-source.md)、[核验报告](../references/verification.md)。
- 同组对照束（版本线口径落差对照方）：[WorkBuddy 官方站点与四区文档](../../workbuddy-official-docs/index.md)；「通稿先行于产品文档」的同组先例见 [企业微信 5.0.12 版本快照](../../wecom-5-0-12-release/index.md)（F-059、F-060）。
