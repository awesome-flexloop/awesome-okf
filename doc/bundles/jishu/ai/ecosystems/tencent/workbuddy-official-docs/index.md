---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 官方站点与四区文档：腾讯全场景 AI 办公工作台的产品与操作知识包"
description: "腾讯 WorkBuddy 官方站点与文档站四区（workbuddy / enterprise / workbuddyapp / workbuddymini）经七概念链路转化：产品定位与任务模型、Agent 执行与权限、25+ 功能面、专家/技能/插件、连接器与 MCP、知识库集成、云助理与定时任务、小程序与网站应用发布、三端差异、积分与套餐、企业版管控与安全；含 520 条登记事实与 190 条页级覆盖台账"
tags: [WorkBuddy, 腾讯, AI办公, Agent, MCP, 技能, 连接器, 知识库, 小程序, 企业版, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: stable
stale_after: "2027-04-15"
sources:
  - { id: W0, resource: "https://www.workbuddy.cn/" }
  - { id: W1, resource: "https://www.workbuddy.cn/docs/workbuddy/" }
  - { id: W2, resource: "https://www.workbuddy.cn/docs/enterprise/" }
  - { id: W3, resource: "https://www.workbuddy.cn/docs/workbuddyapp/" }
  - { id: W4, resource: "https://www.workbuddy.cn/docs/workbuddymini/" }
  - { id: W5, resource: "https://www.workbuddy.cn/docs/" }
  - { id: S1, resource: "https://www.workbuddy.cn/docs/sitemap.xml" }
  - { id: S2, resource: "https://www.workbuddy.cn/sitemap-pages.xml" }
  - { id: P1, resource: "https://www.workbuddy.cn/privacy" }
  - { id: P2, resource: "https://www.workbuddy.cn/pricing/" }
---

# WorkBuddy 官方站点与四区文档：腾讯全场景 AI 办公工作台

> **内容性质：产品官方文档的教程化重组（含可照做操作链路），非实测评测。** 官方文档提供了安装、任务创建、连接器/MCP 接入、技能与专家、知识库、定时任务、小程序与网站应用发布、企业后台配置等可照做的操作链路，故**设 `examples/`**；但本束**未在本机安装或实跑过 WorkBuddy**，所有操作用例逐段标注「未在本机实跑，依据官方文档（F-xxx）」，判据取自官方文档描述。
>
> **可信度状态：`stable`（操作类事实可靠度高于宣传类；厂商自述、四类口径已分层、40 页未取得已登记）。** 本束信源**全部为腾讯官方站点**，无第三方独立核验；官网首页的三项认证与加密声明在文档站未获印证；企业版文档区多数子页在核验时未呈现独立正文。逐条见[核验报告](references/verification.md)。

## 这束知识包讲什么

WorkBuddy 是腾讯出品的全场景 AI 办公工作台：用自然语言描述需求，由它自主规划、调用工具、生成文件，把过程与结果留给用户审核（F-002）。本束按七概念知识沉淀链路（R→I→E→V）把官方站点与文档站四区重构为**事实—机制—操作—查证**四层：

| 顺序 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| 1 | [产品定位与总览](concepts/00-overview-and-positioning.md) | WorkBuddy 是什么、谁出品、与传统 AI 对话差在哪、界面怎么分区、这几个月怎么演进？ |
| 2 | [任务模型与工作流](concepts/01-task-model-and-workflow.md) | 任务怎么创建、管理、续用？对话区和结果区怎么用？ |
| 3 | [Agent 执行与权限边界](concepts/02-agent-execution-and-permissions.md) | 自主规划与工具调用怎样跑？文件与命令的权限边界在哪？ |
| 4 | [功能面与界面](concepts/03-feature-map-and-ui.md) | 侧边栏、右侧边栏、设置、文件浏览器、设计创意、灵感各是什么？ |
| 5 | [专家、技能与插件](concepts/04-experts-skills-and-plugins.md) | 专家/专家团/技能/插件分别解决什么问题？ |
| 6 | [连接器与 MCP](concepts/05-connectors-and-mcp.md) | 外部服务与数据怎么接进来？权限与积分边界是什么？ |
| 7 | [知识库与资料库](concepts/06-knowledge-base-and-library.md) | 资料库与腾讯文档/乐享/ima/人机双写如何组织与联动？ |
| 8 | [云助理、定时任务与企业智能体](concepts/07-cloud-agent-and-automation.md) | 远程控制与自动化怎么运作？ |
| 9 | [应用发布](concepts/08-app-publishing.md) | 小程序与网站应用怎么生成、发布、更新、下线？云服务额度怎么算？ |
| 10 | [多端与腾讯生态](concepts/09-multidevice-and-tencent-ecosystem.md) | 桌面/App/小程序三端差异是什么？生态与 IM 机器人怎么接入？ |
| 11 | [积分与套餐](concepts/10-credits-and-pricing.md) | 积分怎么消耗？套餐、升级折算、退款规则是什么？ |
| 12 | [企业版管控与安全](concepts/11-enterprise-admin-and-security.md) | 企业版管控面有哪些？隐私与安全合规到什么程度？ |
| 实操 | [操作用例（00 ~ 08）](examples/index.md) | 安装与首个任务 → 任务管理 → 对话与结果 → 连接器/MCP → 技能与专家 → 知识库 → 自动化 → 发布 → 企业后台 |
| 查证 | [事实登记](references/article-source.md)（F-001 ~ F-520）、[采集台账](references/source-manifest.md)（190 URL）、[核验报告](references/verification.md) | 每条说法的出处、页级覆盖与核验结论 |

## 已知边界

- **厂商自述，无第三方核验**：全部信源为腾讯官网与官方文档站，无独立评测与成效数据；涉及采购与合规决策须以官方最新页面为准（见核验报告「信源距离评估」）。
- **官网宣传口径 vs 文档可配置项**（`官网宣传口径`）：官网首页宣称全链路 TLS/AES-256 加密与密钥独立托管（F-515）、RBAC 多级权限与操作审计日志（F-516）、已通过 ISO 27001 / SOC 2 / 等保三级（F-517）；**前三项认证在文档站四区零印证、官网无证书查询入口**，不得当作已核实事实引用。
- **四端差异**（`三端差异`）：桌面端 / App / 小程序端同名功能页存在措辞与能力集合不一致，例：执行环境在 App 叫「云端工作 / 连接电脑」、在小程序叫「云上模式 / 本机模式」（F-315）；模型选择页小程序端给倍率表、App 端不给（F-345、F-399）；小程序端特产「微信文件」「ima 知识库」入口与微信订阅通知、产物分享链接有效期 30 天（F-376、F-394、F-405）。引用时必须带端别。
- **企业版边界**（`企业版专属`）：席位与起购量（旗舰版 1 个坐席起购 F-505、专享版缩容下限 100 个 F-508）、每成员默认 2000 积分限额（F-507）、腾讯统一身份（旗舰版已接入、专享版未接入，F-490）、Skill 下发策略（F-495）、模型管控（F-197）、私有化部署（F-484）属企业版管控面，不得写成个人版可用。注意「旗舰版」在个人套餐（999 元/月，F-068）与企业 SaaS 版（F-485）中同名不同义。
- **企业版文档区大面积「未取得」**：`/docs/enterprise/` 为客户端渲染站点，27 个 sitemap 路径中多数未呈现独立正文（别名至「产品概述」或占位），核验时仅 6 处取得真实正文（产品概述、产品优势、登录及更新、企业管理员、Skill 管理、购买方式）；**其余模块（模型管理、日志管理、IP 白名单、研发度量、Playbook、Connector 管理、席位管理、飞书/企业微信集成、计费页等）不得据页面标题推断能力细节**（F-512 ~ F-514）。
- **官网 sitemap 与实际站点不一致**：`sitemap-pages.xml` 收录的 7 个着陆页（`/about`、`/changelog`、`/download`、`/skills`、`/templates`、`/terms`、`/use-cases`）核验时全部 404（F-435）；官网首页与定价页为 SPA，纯 HTTP 未渲染（F-423、F-424）。
- **版本时效**（`核验时点 2026-10-15`）：更新日志最新为 **5.7.7（2026-10-08）**（F-081、F-082），而历史版本下载页同版本标 **2026-10-09**（F-042）；企业版页面页脚时间戳跨 2026-07-06 ~ 2026-09-19（F-488、F-503、F-511），与其 sitemap 时间戳 2026-10-14 不同步。引用版本号与日期必须带核验时点。
- **未取得页不计作已学习**：190 个 sitemap URL 中已学习 150、未取得 40（客户端渲染占位 / 语义路径别名 / HTTP 404 三类），逐条列于[采集台账](references/source-manifest.md)。
- **未在本机实跑**：全部 `examples/` 的操作步骤与结果判据取自官方文档，未实际执行；不要据本束判断「某功能在某版本一定能跑通」。
- **同组既有束的口径互证**：本束独立复核确认更新日志止于 5.7.7，与[企业微信 5.0.12 版本快照](../wecom-5-0-12-release/index.md)记录的「通稿先行于产品文档」一致。

## 主题关联

- [企业微信 5.0.12 版本新功能](../wecom-5-0-12-release/index.md)——企微 × WorkBuddy 深度互通版本快照（机器人领用入口、大圆协作、5.8.0 通稿口径）；与本束构成「Agent 进入协作流（企微侧）」与「Agent 本体能力（产品侧）」的互补读法。
- [WorkBuddy 一句话做 MVP](../workbuddy-one-sentence-mvp/index.md)——同产品早期（5.6.1 时期）实测软文核验束；本束记录其后 5.7.x 的能力演进与官方口径。
- [WorkBuddy 沙箱公网端点](../workbuddy-sandbox-public-endpoint/index.md)——WorkBuddy/CloudStudio 运行环境边界核验，可与本束[企业智能体 Runtime](concepts/07-cloud-agent-and-automation.md) 与[应用发布云服务](concepts/08-app-publishing.md)对照。
- [腾讯 Buddy 系列产品观察](../tencent-buddy-family/index.md)——Buddy 品牌矩阵；本束的企业版三产品结构（CodeBuddy / WorkBuddy / WorkBuddy Managed Agents，F-478）是矩阵在云侧的组织方式。
- [CodeBuddy 产品矩阵](../codebuddy/index.md)——同一账号体系与积分共享（F-071），企业版 Skill 管理同时覆盖 CodeBuddy 与 WorkBuddy 能力扩展（F-493）。
- [Octop 自托管多用户多 Agent](../octop/index.md)——同为腾讯系 Agent 平台，可对照「云端托管（CloudAgent）vs 自托管（Octop）」两种形态。
- [WorkBuddy 开放平台分享能力接入与推广管理](../workbuddy-open-platform-sharing-and-promotion/index.md)——同产品开放平台侧两篇平台公告（分享能力接入、推广管理）；本束记录产品与四端文档，该束记录面向开发者/资产作者的开放平台能力，构成「产品本体能力」与「平台分发能力」的互补读法；本束核验到的版本线止于 5.7.7 与该束公告要求的 5.8.0 门槛形成口径落差互证。

## 一句话结论

WorkBuddy 的官方文档已经把「一句话下任务 → 自主执行 → 交付可验收产物」这条主线铺到了相当细的颗粒度（任务模型、权限两档、专家/技能/插件三层扩展、连接器与 MCP 可视化接入、资料库 MD/CSV/HTML 三载体联动、定时任务与云端沙箱、小程序与网站应用托管发布），并且用同一套账号体系贯通了桌面、App、小程序三端与企业管控面；但核验日的证据结构也说明它的阶段位置——能力细节几乎全部来自厂商单源，企业版后台文档大面积尚未就位，官网宣传的安全认证在文档侧找不到对应说明，适合当作「**能力已成型、口径待复核**」的产品知识底座使用。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
