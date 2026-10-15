---
type: Reference
title: "智能硬件接入 WorkBuddy 白皮书 · 信源台账与逐章覆盖登记"
description: "W0/P0/P1/O1 四个实际访问信源与 X1 未取得项的采集登记（URL、访问日期、获取方式、体量、知识归属、覆盖状态），并按白皮书 0~13 章与附录 A/B 逐章登记覆盖结论"
tags: [WorkBuddy, 智能硬件, 采集台账, 覆盖登记, SPA, OKF]
generated: { by: "process:seven-concepts-r", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: W0, resource: "https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA" }
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
  - { id: P1, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/WorkBuddy_v4__.html" }
  - { id: O1, resource: "https://open.workbuddy.cn/" }
---

# 信源台账与逐章覆盖登记

## 采集方法

- 2026-10-15 访问分享页 W0：纯 HTTP 抓取仅得 **4.6 KB 壳页**（`<div id="root">` + `publish-bootstrap-loading`），页面由 `window.__PUBLISH_BOOTSTRAP__` 指向静态制品，属**客户端渲染（SPA）**。
- 依壳页暴露的制品基址取得 **P0**（`janus.data.json`，708 KB 正文数据源，`publishVersion: 20`）与 **P1**（`WorkBuddy_v4__.html`，202 KB，备用）。
- 解析 P0 的节点树（`page-node-id` / `type` / `parentId` / `children` / `tag` / `content`），按 HTML 标签语义还原正文：标题层级、列表、表格、代码块与 ASCII 决策图。提取结果 **1330 行 / 21432 字符**，落工作区外临时文件（不随交付）。
- 正文性质：页脚标注**发行日期 2026 年 08 月**，版权 © 2026 WorkBuddy 开放平台；页面 `<meta name="robots" content="noindex, nofollow">`。
- 声明级覆盖见[事实登记](article-source.md)（F-001 ~ F-190）；本台账记录**信源级 + 章级**覆盖。

## 信源台账

| 代号 | URL | 访问日期 | 获取方式 | 取得体量 | 知识归属 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| W0 | <https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA> | 2026-10-15 | 渲染抓取（SPA 壳页，仅外壳） | 4.6 KB | concepts/00（白皮书定位与使用说明） | 已访问（壳页，正文经 P0 取得） |
| P0 | <https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json> | 2026-10-15 | HTTP 抓取 + 节点树解析 | 708 KB（正文 1330 行 / 21432 字符） | 全束 concepts/00 ~ concepts/10 | 已学习（正文覆盖全文） |
| P1 | <https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/WorkBuddy_v4__.html> | 2026-10-15 | HTTP 抓取 | 202 KB | 备用（未直接引用） | 已获取（备用，未归属） |
| O1 | <https://open.workbuddy.cn/> | — | 未访问 | — | concepts/04、concepts/08（提及处均标注未核验） | **未核验**（本束不在开放平台注册账号） |
| X1 | 随册文件 `assistant-openapi.html`（Swagger UI 交互版） | — | 未获得 | — | concepts/10（附录 A 登记） | **未取得**（本分享页未随附该文件） |

> **未核验 / 未取得说明**：O1 与 X1 均**不计作已覆盖**，全束引用处一律带「未核验」「未取得」标注，不据其推断能力细节。

## 逐章覆盖表（AC-1）

| 章 | 章节标题 | 覆盖状态 | 知识归属文档 | 事实编号区间 |
| --- | --- | --- | --- | --- |
| §0 | 摘要（三阶段、关键数据、如何使用） | 已覆盖 | concepts/00-whitepaper-and-workbuddy-overview | F-001 ~ F-010 |
| §1 | WorkBuddy 简介（六大能力、用户画像） | 已覆盖 | concepts/00-whitepaper-and-workbuddy-overview | F-011 ~ F-026 |
| §2 | 硬件接入的价值（三重放大、三痛点与解法） | 已覆盖 | concepts/01-hardware-value-and-six-touchpoints | F-027 ~ F-034 |
| §3 | 六类硬件触点（听/看/戴/记/聊/协 + 硬件形态） | 已覆盖 | concepts/01-hardware-value-and-six-touchpoints | F-035 ~ F-039 |
| §4 | 合作模式及范本（三方协同、决策图、四模式、范本、商业模式与结算、分层与边界） | 已覆盖 | concepts/02-partnership-models-and-commercial-model | F-040 ~ F-081 |
| §5 | 产品能力全景（Agent 五层、云端能力、端云协同、生态扩展、硬件专区） | 已覆盖 | concepts/03-product-capabilities-and-scenario-matrix | F-082 ~ F-094 |
| §6 | 场景能力矩阵（六触点能力组合、六个真实场景、ToB 场景） | 已覆盖 | concepts/03-product-capabilities-and-scenario-matrix | F-095 ~ F-109 |
| §7 | 开放能力概述（四类能力、核心概念、正式上线声明） | 已覆盖 | concepts/04-open-platform-and-core-concepts | F-110 ~ F-118 |
| §8 | 授权登录 OAuth 2.0（前置准备、授权流程、换票、刷新与撤销、用户标识） | 已覆盖 | concepts/05-oauth2-authorization-flow；examples/00、examples/01 | F-119 ~ F-131 |
| §9 | 接口调用（通用规范、助理接口、任务接口、本机能力） | 已覆盖 | concepts/06-assistant-and-task-apis；examples/02、examples/03、examples/04 | F-132 ~ F-147 |
| §10 | 端到端示例（六步完整流程、硬件端接入姿势） | 已覆盖 | concepts/07-end-to-end-walkthrough-and-faq；examples/05 | F-148 ~ F-150 |
| §11 | 常见问题（合作模式、票据有效期、多用户隔离、401、本机边界、系统平台等） | 已覆盖 | concepts/07-end-to-end-walkthrough-and-faq | F-151 ~ F-160 |
| §12 | 合作落地流程（两条路径、样板节奏、合作原则、准入审核、品牌授权、对接窗口） | 已覆盖 | concepts/08-landing-process-and-access-review；examples/06 | F-161 ~ F-176 |
| §13 | 联合运营（售后三级支持与 SLA、数据看板、联合宣发、版本迭代与共创） | 已覆盖 | concepts/09-joint-operations-and-service-levels | F-177 ~ F-188 |
| 附 A | OpenAPI 完整规范（随册文件引用） | **未取得** | concepts/10-glossary-and-appendix | F-189 |
| 附 B | 术语表（12 条术语） | 已覆盖 | concepts/10-glossary-and-appendix | F-190 |

## 集合比对结论（AC-1）

| 项 | 值 |
| --- | --- |
| 白皮书章节集合（0~13 + 附录 A/B） | 16 |
| 已登记归属集合 | 16 |
| 双向差集 | 0（`expected - registered` = 0，`registered - expected` = 0） |
| 覆盖状态 = 已覆盖 | 15 |
| 覆盖状态 = 未取得（附录 A 随册文件） | 1 |
| 信源 = 已学习 | 2（W0 壳页、P0 数据源） |
| 信源 = 未核验 / 未取得 | 2（O1 未核验、X1 未取得） |

> **获取路径区分**：W0（SPA 壳页）与 P0（正文数据源）为同一次采集的两条路径，本台账显著区分——壳页只提供制品指针，**正文以 P0 为准**。

## 已知观测（不扩大修复范围）

- 分享页 `<meta name="robots">` 为 `noindex, nofollow`，即该页不参与搜索引擎收录；本束引用仍以 W0 为可访问入口。
- 附录 A 引用的随册文件 `assistant-openapi.html`（Swagger UI 交互版）未随本分享页提供，接口的完整字段、错误码与示例响应**无法在本束核验**，已在 concepts/10 与核验报告中登记。
- 白皮书 §7 声称开放平台「已于 2026 年 9 月 2 日正式发布」，而页脚发行日期为「2026 年 08 月」，两者时序不自洽，详见[核验报告](verification.md)。
