---
type: Concept
title: "术语表与附录：12 条术语对照与附录 A 未取得说明"
description: "白皮书附录 B 的 12 条术语（含三级用户标识）逐条对照与本束篇章导航，以及附录 A 随册接口规范文件未取得的登记说明。"
tags: [WorkBuddy, 智能硬件, 术语表, 附录, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
  - { id: P1, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/WorkBuddy_v4__.html" }
---

# 术语表与附录：12 条术语对照与附录 A 未取得说明

本篇回答：读懂本束其余篇章绕不开的那些专有名词各指什么，以及附录 A 的接口规范为什么在本束缺席。事实取材附录 A/B 与版权信息（F-189、F-190）。

## 附录 A · OpenAPI 完整规范（未取得）

白皮书附录 A 说明：完整字段、错误码与示例响应见**随册文件** `assistant-openapi.html`（Swagger UI 交互版），且白皮书所述接口与其保持一致（F-189）。但本分享页**未随附该文件**，故本束将其登记为「未取得」（信源代号 X1，`未取得`）。由此，本束遵守一条纪律：**不据章节标题或术语名称推断字段细节**——凡只在 `assistant-openapi.html` 里才有的字段、错误码与示例响应，一律不复现、不猜测（F-189，`未取得`）。需要完整规范时请查阅白皮书随册文件或官网开发者文档（`以官网为准`，F-113）。需说明的是，「未取得」不等于「不存在」：该文件在官方侧应存在——白皮书正文明确引用了它，只是本分享页未随附；本束如实登记为采集缺口，而非宣称其缺失（F-189）。

## 附录 B · 术语表（12 条）

白皮书附录 B 术语表口径为 **12 条**（F-190）；其中末条 `openid / unionid / uid` 为三级用户标识，本表按三条独立标识分行呈现（其逐级粒度定义另见 F-131），与 12 条口径一致：

| 术语 | 含义 | 事实 | 本束相关篇章 |
| --- | --- | --- | --- |
| WorkBuddy | 7×24 云端 AI 智能助理平台 | F-190 | [白皮书面貌](00-whitepaper-and-workbuddy-overview.md) |
| Assistant（助理） | 用户拥有的 AI 角色，包含名称、指令、能力标签，支持 local 或 cloud 部署 | F-190 | [助理与任务接口](06-assistant-and-task-apis.md) |
| Task（任务） | 用户对某个助理发起的一次执行，包含输入、工具链、产出物与状态 | F-190 | [助理与任务接口](06-assistant-and-task-apis.md) |
| Runtime / Sandbox（云端执行环境） | 云端安全存储与执行环境，cloud 助理激活后由平台分配 | F-190 | [助理与任务接口](06-assistant-and-task-apis.md) |
| scope（权限范围） | 授权时勾选的能力边界，如 `assistant.read`、`task.write`，用户可随时撤销 | F-190 | [授权登录流程](05-oauth2-authorization-flow.md) |
| execution_target（任务执行位置） | `cloud` 表示任务在云端执行，`local` 表示在用户本机客户端执行 | F-190 | [助理与任务接口](06-assistant-and-task-apis.md) |
| Skill | WorkBuddy 生态中的能力扩展模块，覆盖行业知识、工具与工作流 | F-190 | [产品能力与场景矩阵](03-product-capabilities-and-scenario-matrix.md) |
| Connector | 硬件或第三方系统接入 WorkBuddy 生态的能力桥接组件 | F-190 | [产品能力与场景矩阵](03-product-capabilities-and-scenario-matrix.md) |
| 个人票据（access_token） | 由 OAuth 2.0 授权码流程颁发，代表终端用户身份，用于调用开放接口 | F-190 | [授权登录流程](05-oauth2-authorization-flow.md) |
| openid | 用户在合作方 App 下的唯一标识（粒度＝每个应用，对开发者可见） | F-131、F-190 | [授权登录流程](05-oauth2-authorization-flow.md) |
| unionid | 同一开发者跨 App 的用户统一标识（粒度＝每个开发者，对开发者可见） | F-131、F-190 | [授权登录流程](05-oauth2-authorization-flow.md) |
| uid | WorkBuddy 平台用户唯一标识（粒度＝全局，对开发者不可见） | F-131、F-190 | [授权登录流程](05-oauth2-authorization-flow.md) |

对照使用时可把握三点：其一，`scope` 与 `execution_target` 是本束出现频率最高的两个概念——前者决定「能做什么」，后者决定「在哪里做」（F-190）；其二，`access_token` 代表的是**终端用户**而非合作方应用，理解这一点才理解得了「只返回该用户资产」的接口边界（F-190、F-132）；其三，三级标识中只有 `openid` 与 `unionid` 对开发者可见，`uid` 为平台全局标识、对开发者不可见，因此合作方侧做多用户隔离应以 `openid` 为主键（F-131）。

## 本束导航一览

| 想回答的问题 | 去哪篇 |
| --- | --- |
| 白皮书是什么、WorkBuddy 与六大能力 | [00 白皮书与 WorkBuddy 概览](00-whitepaper-and-workbuddy-overview.md) |
| 硬件为何接入、六类触点 | [01 硬件价值与六类触点](01-hardware-value-and-six-touchpoints.md) |
| 合作模式、商务路径与分层 | [02 合作模式与商业模型](02-partnership-models-and-commercial-model.md) |
| 产品能力与场景矩阵 | [03 产品能力与场景矩阵](03-product-capabilities-and-scenario-matrix.md) |
| 开放能力与核心概念 | [04 开放平台与核心概念](04-open-platform-and-core-concepts.md) |
| OAuth 2.0 授权与换票 | [05 授权登录流程](05-oauth2-authorization-flow.md) |
| 助理与任务接口 | [06 助理与任务接口](06-assistant-and-task-apis.md) |
| 端到端与常见问题 | [07 端到端演练与常见问题](07-end-to-end-walkthrough-and-faq.md) |
| 落地路径与准入审核 | [08 落地流程与准入审核](08-landing-process-and-access-review.md) |
| 联合运营与服务水平 | [09 联合运营与服务水平](09-joint-operations-and-service-levels.md) |

术语与接口的逐条出处见 [事实登记](../references/article-source.md) 与 [核验报告](../references/verification.md)；完整信源台账见 [信源清单](../references/source-manifest.md)。
