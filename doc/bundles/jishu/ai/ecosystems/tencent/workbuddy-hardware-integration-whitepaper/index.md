---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 智能硬件接入白皮书：腾讯 AI 底座 × 智能硬件的接入方案知识包"
description: "腾讯 WorkBuddy 开放平台《智能硬件接入 WorkBuddy 白皮书》（发行日期 2026 年 08 月）经七概念链路转化：战略与商务（三方协同、四种合作模式、三条商业路径、L1/L2 分层）、产品与能力（Agent 五层引擎、云端能力包、端云协同、生态三层、硬件专区、六触点场景矩阵）、技术接入（开放平台四类能力、OAuth 2.0 + PKCE、Assistants/Tasks 接口、本机能力、端到端链路）、落地与运营（两条接入路径、准入审核、品牌授权、三级支持与 SLA、联合宣发）；含 190 条登记事实与 7 篇可照做接入示例"
tags: [WorkBuddy, 腾讯, 智能硬件, AI硬件, OAuth2, OpenAPI, 开放平台, 合作模式, 硬件接入, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: W0, resource: "https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA" }
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json" }
  - { id: P1, resource: "https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/WorkBuddy_v4__.html" }
  - { id: O1, resource: "https://open.workbuddy.cn/" }
---

# WorkBuddy 智能硬件接入白皮书：腾讯 AI 底座 × 智能硬件的接入方案

> **内容性质：厂商白皮书 + 可照做接入指南的教程化重组，非实测评测。** 白皮书由 WorkBuddy 开放平台于 2026 年 08 月发行，分「战略与商务 / 产品与能力 / 技术接入 / 落地与运营」四部分；其中第三部分与 §12 给出了 OAuth 2.0 授权、接口调用、端到端流程与自助接入的可照做链路，故**设 `examples/`**；但本束**未在开放平台注册应用、未申请真实凭证、未调用任何接口**，所有接入步骤逐段标注「未在本机实跑，依据白皮书（F-xxx）」。
>
> **可信度状态：`stable`（口径已分层、未核验与未取得项已登记）。** 本束信源为**单一厂商自述材料**（白皮书分享页及其正文数据源 `publishVersion: 20`），无第三方独立核验；白皮书转引的三项市场指标（腾讯财报、易观分析）原始报告本束未获取；开放平台官网 **未核验**、附录 A 随册 OpenAPI 文件 **未取得**。逐条见[核验报告](references/verification.md)。

## 这束知识包讲什么

白皮书回答的核心问题是：**硬件厂商如何把 WorkBuddy 的云端 AI 能力接进自己的产品，并决定商业模式。** 本束按七概念知识沉淀链路（R→I→E→V）把四个部分重构为**事实—机制—操作—查证**四层：

| 顺序 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| 1 | [白皮书与 WorkBuddy 总览](concepts/00-whitepaper-and-workbuddy-overview.md) | 白皮书是什么、谁写的、给谁看？WorkBuddy 是什么、六大能力是什么、市场数据从哪来？ |
| 2 | [硬件价值与六类触点](concepts/01-hardware-value-and-six-touchpoints.md) | 硬件为什么值得接入？价值三重放大、三痛点解法、六类触点怎么划分？ |
| 3 | [合作模式与商业模式](concepts/02-partnership-models-and-commercial-model.md) | 三方怎么分工？四种模式怎么选？商业路径与结算口径是什么？L1/L2 分层边界在哪？ |
| 4 | [产品能力与场景矩阵](concepts/03-product-capabilities-and-scenario-matrix.md) | Agent 五层引擎、云端能力包、端云协同、生态三层、硬件专区是什么？六个真实场景长什么样？ |
| 5 | [开放平台与核心概念](concepts/04-open-platform-and-core-concepts.md) | 开放平台暴露哪四类能力？核心概念有哪些？它的时效边界在哪？ |
| 6 | [OAuth 2.0 授权流程](concepts/05-oauth2-authorization-flow.md) | 授权码 + PKCE 怎么走？票据怎么换、怎么刷、怎么撤？三级用户标识是什么？ |
| 7 | [助理与任务接口](concepts/06-assistant-and-task-apis.md) | 通用规范是什么？助理与任务接口各有哪些？本机能力怎么用、scope 怎么配？ |
| 8 | [端到端链路与常见问题](concepts/07-end-to-end-walkthrough-and-faq.md) | 从绑定到完成一次任务要几步？硬件端该怎么接？十个常见问题怎么答？ |
| 9 | [落地流程与准入审核](concepts/08-landing-process-and-access-review.md) | 两条接入路径怎么走？准入条件、审核流程、上架退出、品牌授权怎么规定？ |
| 10 | [联合运营与服务体系](concepts/09-joint-operations-and-service-levels.md) | 上线后有哪些支持与 SLA？数据看板、联合宣发、版本迭代机制是什么？ |
| 11 | [术语表与附录](concepts/10-glossary-and-appendix.md) | 12 条术语分别什么意思？附录 A 的接口规范拿到了吗？ |
| 实操 | [接入示例（00 ~ 06）](examples/index.md) | 注册应用与配置 scope → OAuth 授权换票 → 创建并激活云端助理 → 发起任务与读结果 → 刷新撤销票据 → 硬件后端反向代理 → 自助接入与审核 |
| 查证 | [事实登记](references/article-source.md)（F-001 ~ F-190）、[采集台账](references/source-manifest.md)、[核验报告](references/verification.md) | 每条说法的出处、章节覆盖与核验结论 |

## 已知边界

- **单一厂商自述，无第三方核验**：全部事实来自 WorkBuddy 开放平台白皮书；无独立评测或成效数据；涉及采购、合规与上线决策须以开放平台官网最新公示与双方商务协议为准。
- **市场数据为转引，原始报告未核验**（`第三方数据`）：§0.1 的「日活第一」标注来源为腾讯 2026 Q1 财报（F-006）、「2097 万/月」标注来源为易观分析（F-007），**两份原始报告本束均未获取**，不得当作本束独立结论引用。
- **同文档 Skills 数量不一致**（`厂商自宣口径`）：§0.1 为「2.2 万+」（F-008），§1.1 与 §5.4 为「7 万余」（F-019、F-092）；本束并列登记、不裁决真伪，引用时须带章节位置。
- **发行日期与发布日时序不自洽**：页脚发行日期为 **2026 年 08 月**（F-002），而 §7 声称平台「已于 2026 年 9 月 2 日正式发布」（F-112），前者早于后者，属白皮书内部不一致（勘误 E-1）。
- **接口清单为发行日快照，以官网为准**（`以官网为准`）：白皮书 §7 明示第 7–10 章接口清单、鉴权、示例与联调流程「均以官网开发者文档的最新版本为准」（F-113）；本束 concepts/05–06 与 examples 的端点与参数为**快照**，实际接入须对照 <https://open.workbuddy.cn/>。
- **开放平台官网未核验**（`未核验`）：O1 <https://open.workbuddy.cn/> 本束未访问、未注册账号，官网当前的接口清单与实际开放状态**未与本束对照**（F-114、F-176）。
- **附录 A 随册文件未取得**（`未取得`）：白皮书引用的 `assistant-openapi.html`（Swagger UI 交互版）未随分享页提供，接口的完整字段、错误码与示例响应**无法在本束核验**（F-189）；未取得 ≠ 不存在。
- **六个真实场景为匿名化处理**（`匿名化场景`）：§6.1 明示品牌与产品名已匿名（F-102 ~ F-108），一律**不得反推、关联或用于商业尽调**；仅作品类与能力组合的方法论参考。
- **商务数字为框架性参考**（`商务框架性参考`）：三条商业路径的定价/分成/授权费白皮书**未给出具体数额**（F-069 ~ F-077），一律「以协议为准 / 通过商务窗口一事一议」；不得写成确定承诺。
- **未在本机实跑**：全部 `examples/` 的步骤与判据取自白皮书，未实际执行；不要据本束判断「某接口在某时点一定能调通」。
- **获取路径说明**：分享页 W0 为 SPA 壳页（4.6 KB），正文实际取自其制品数据源 P0（`publishVersion: 20`）；该制品为版本化 URL，后续更新可能改变位置（详见[采集台账](references/source-manifest.md)）。

## 主题关联

- [WorkBuddy 官方站点与四区文档](../workbuddy-official-docs/index.md)——同产品的官方文档教程化束（12 概念 + 9 示例 + 520 条事实）；本束是其在**智能硬件接入**方向的分支，二者共享 `open.workbuddy.cn` 开放平台口径。
- [WorkBuddy 开放平台分享与推广](../workbuddy-open-platform-sharing-and-promotion/index.md)——同属开放平台侧的公告教程化束（分享能力接入、推广管理）；与本束构成「开放平台能力接入（硬件侧）」与「开放平台能力接入（应用分享侧）」的互补读法。
- [WorkBuddy 一句话做 MVP](../workbuddy-one-sentence-mvp/index.md)——同产品早期实测软文核验束；可与本束 §5/§6 的能力分层对照。
- [WorkBuddy/CloudStudio 沙箱公网端点](../workbuddy-sandbox-public-endpoint/index.md)——运行环境边界核验；可与本束 concepts/03 端云协同、concepts/07 硬件端接入姿势对照。
- [腾讯 Buddy 系列产品观察](../tencent-buddy-family/index.md)——Buddy 品牌矩阵；本束的 WorkBuddy 定位（F-011、F-012）是其矩阵中的一环。
- [企业微信 5.0.12 版本更新](../wecom-5-0-12-release/index.md)——企微 × WorkBuddy 深度互通的版本快照；可作为「WorkBuddy 进入企业协作流」的另一条路径对照。
- [CodeBuddy 产品矩阵](../codebuddy/index.md)——同一账号与积分体系下的 AI 编程产品线（F-008 提及的多模型能力语境）。
- [Octop 自托管多用户多 Agent](../octop/index.md)——同为腾讯系 Agent 平台，可对照「云端托管（本束）vs 自托管」两种形态。

## 一句话结论

这份白皮书把「硬件厂商接入 WorkBuddy」的**完整决策链**铺得相当细——从六类触点的场景矩阵、四种合作模式的三问决策、三条商业路径与 L1/L2 分层，到 OAuth 2.0 + PKCE 的授权码流程、Assistants/Tasks 接口与 scope 清单、硬件端「票据不下发端侧、后端反向代理」的接入姿势，再到准入审核、品牌授权与三级支持 SLA；但证据结构也说明了它的阶段位置——**全部为厂商单源自述**，市场数据是转引且原始报告未核验，Skills 数量与发行/发布日期两处内部不自洽，接口清单只到发行日快照，开放平台官网与随册 OpenAPI 文件均未触达。适合当作「**接入方案与商务框架已成型、具体口径待官网与协议复核**」的决策底座使用。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
