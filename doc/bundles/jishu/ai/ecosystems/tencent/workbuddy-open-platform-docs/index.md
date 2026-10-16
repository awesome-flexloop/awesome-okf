---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 开放平台开发者文档：平台能力开发、资产上架与 Open API 接入"
description: "对 open.workbuddy.cn 开发者文档站 11 个已声明 URL（D0 导航面 + D1～D10 十篇 /docs/ 内容页）经七概念链路 R→I→E→V 转化：平台概述与八步快速开始、入驻与三档身份认证、技能开发与市场、连接器开发与接入方式、专家与专家团、Buddy 应用开发与发布、第三方应用接入、Open API 认证与通用约定、Open API 接口目录、收入变现、边界与版本缺口；含 11 篇概念 + 5 篇操作用例 + 3 篇查证台账，登记 F-001～F-439 共 439 条事实、站点侧栏 17 篇覆盖状态与五类口径分层"
tags: [WorkBuddy, 腾讯, 开放平台, 开发者文档, 技能, 连接器, 专家, Buddy应用, 第三方应用, OpenAPI, 收入变现, 口径分层, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D0, resource: "https://open.workbuddy.cn/dashboard" }
  - { id: D1, resource: "https://open.workbuddy.cn/docs/what-is-open-platform" }
  - { id: D2, resource: "https://open.workbuddy.cn/docs/onboarding" }
  - { id: D3, resource: "https://open.workbuddy.cn/docs/monetization" }
  - { id: D4, resource: "https://open.workbuddy.cn/docs/skill" }
  - { id: D5, resource: "https://open.workbuddy.cn/docs/connector" }
  - { id: D6, resource: "https://open.workbuddy.cn/docs/expert" }
  - { id: D7, resource: "https://open.workbuddy.cn/docs/expert-team" }
  - { id: D8, resource: "https://open.workbuddy.cn/docs/buddy-app" }
  - { id: D9, resource: "https://open.workbuddy.cn/docs/third-party-app" }
  - { id: D10, resource: "https://open.workbuddy.cn/docs/openapi" }
---

# WorkBuddy 开放平台开发者文档：平台能力开发、资产上架与 Open API 接入

> **内容性质：开发者文档的教程化重组（含可照做操作链路），非实测评测。** 本束对象是腾讯 WorkBuddy 开放平台自有开发者文档站（`open.workbuddy.cn/docs/`）的 11 个已声明 URL（D0 导航面 + D1～D10 十篇 `/docs/` 内容页）。文档按业务类型给出了**步骤化的开发、上架与接入链路**——入驻与资质认证、技能/连接器/专家/专家团/Buddy 应用的创建与提交、第三方应用授权与签名、Open API 鉴权与接口调用、付费资产发布与收入管理——**故设 `examples/`**（操作可复现性两问判定为「是」）。但**审核与上架结果由平台判定、本机无法闭环**：本束**未注册开放平台账号、未申请任何认证与资质、未提交任何审核、未生成真实密钥与 token、未调用任何真实接口**，文档给出的审核结论、审核时长（除分享应用 7 个工作日外）、分成比例等均**不在本束可闭环范围**。因此 `examples/` 全部操作用例逐步骤标注「**未在本机实跑，依据官方文档（F-xxx）**」，所有端点、字段与步骤均为**文档所述快照**。
>
> **可信度状态：`stable`（口径已分层、未采集与官方未给项均已登记）。** 本束信源**全部为腾讯 WorkBuddy 开放平台自有的开发者文档**（`open.workbuddy.cn/docs/`），属**厂商单源自述，无任何第三方独立核验**；其中 D1～D10 十篇 `/docs/` 页经实测为**服务端渲染、无登录依赖**（纯 HTTP GET 即可取得正文），**与同组分享公告束须已登录会话方能读取正文的条件不同**，两束采集条件不可互相套用。逐条见[核验报告](references/verification.md)。

## 这束知识包讲什么

开发者文档回答的核心问题是：**入驻门槛在哪、能开发哪些业务类型、各类资产怎么开发与上架、Open API 怎么授权调用与变现。** 本束按七概念知识沉淀链路（R→I→E→V）把十篇 `/docs/` 页重构为**事实—机制—操作—查证**四层：

| 顺序 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| 00 | [开放平台概览与八步快速开始](concepts/00-overview-and-quickstart.md) | 开放平台是什么？能开发哪些业务类型？从入驻到上线的八步是什么？平台优势如何表述？ |
| 01 | [入驻开放平台与三档身份认证](concepts/01-onboarding-and-qualification.md) | 个人认证 / 管理员实名认证 / 企业认证三档分别怎么做？企业信息上传到完成企业验证怎么走？认证结果与规则、失败场景如何处理？ |
| 02 | [技能：开发与市场](concepts/02-skill-development-and-marketplace.md) | 技能在市场上如何展示与安装？技能怎么创建、打包、提交与上架？ |
| 03 | [连接器：开发与接入方式](concepts/03-connector-development-and-access-modes.md) | 连接器有哪些接入方式（MCP / CLI + Skill）？元信息、认证与凭证、图标与提交前检查怎么配？ |
| 04 | [专家与专家团](concepts/04-expert-and-expert-team.md) | 专家与专家团分别是什么？怎么创建、配置与发布？两者如何区分？ |
| 05 | [Buddy 应用：开发与发布](concepts/05-buddy-app-develop-and-publish.md) | Buddy 应用怎么创建、开发与发布？它与技能、连接器的关系是什么？ |
| 06 | [第三方应用接入](concepts/06-third-party-app-access.md) | 第三方应用分哪几类？端与版本边界在哪？授权认证与签名怎么走？ |
| 07 | [Open API：认证与通用约定](concepts/07-openapi-auth-and-conventions.md) | Open API 怎么鉴权（OAuth、access_token、签名）？请求响应与错误约定是什么？ |
| 08 | [Open API：接口目录](concepts/08-openapi-endpoint-catalog.md) | Open API 提供了哪些接口？按功能如何分类，各自用途与关键参数是什么？ |
| 09 | [收入变现：开通门槛、付费资产与收入管理](concepts/09-monetization-and-revenue.md) | 变现怎么开通？怎么发布付费资产、管理收入？分成比例与结算周期是什么？ |
| 10 | [边界、版本与已知缺口](concepts/10-boundaries-versions-and-known-gaps.md) | 本束信源边界在哪？哪些页未采集、哪些项官方未给？有哪些跨页口径并列与勘误？ |
| 实操 | [操作用例（00 ~ 04）](examples/index.md) | 照做：入驻与资质认证 → 构建并提交技能 → 构建并提交连接器 → OAuth 授权并调用 Open API → 发布并管理付费资产 |
| 查证 | [F 编号事实登记](references/article-source.md)（F-001 ~ F-439）、[页级采集与覆盖台账](references/source-manifest.md)、[核验报告](references/verification.md) | 每条说法的出处、页级与侧栏覆盖状态、核验结论（五类口径分层、勘误 E1～E3、官方未给清单、V 四视角对抗审查） |

## 已知边界

以下边界**集中声明、逐条可查**；须明确区分「**官方未给**」「**本束未采集**」与「**未在本机实跑**」三类，均**不可**替官方宣布，也**不可**断言平台的现状或功能可用性。

- **① 厂商自述、无第三方核验**：本束全部 F 编号事实（F-001～F-439）**仅来自腾讯 WorkBuddy 开放平台自有开发者文档**，属厂商自述；无第三方独立印证、亦无官方变更日志可用（文档站未见统一版本号与 changelog）。操作类事实（流程、字段表、示例、枚举、错误码）可靠度高于宣传类表述。见[核验报告](references/verification.md) 第六节。
- **② 未在本机实跑**：本束**未注册账号、未申请认证与资质、未提交审核、未生成密钥与 token、未调用任何真实接口**；任何「功能可用 / 已通过审核 / 已上线」类表述均**不可断言**。`examples/` 全部步骤为**文档转述**，逐步骤标注「未在本机实跑，依据官方文档（F-xxx）」，凭证一律占位符。
- **③ 未采集 ≠ 不存在**：站点侧栏共 **17 篇 `/docs/`** 页，其中已声明并处理 **10**（D1～D10）、**本次未采集仅登记入口 7**——`api-token`、`contact`、`developer-profile`、`legal-basis-and-examples`、`operations-data`、`service-categories-individual`、`service-categories-enterprise`（这 7 篇只证明「该 slug 存在于站点侧栏」，**不得据名称推断**功能细节、字段、权限或门槛）；另有非页面布局资源 `layout-216c2d1532f8d94c`（`layout-` + 16 位十六进制，属前端布局分片，在 D1～D10 十页命中集合中恒等重现）**已显式排除**，不计入任何页面集合与覆盖率分母。`已声明 − 已处理` 与 `已处理 − 已声明` **双向差集为空**。见[采集台账](references/source-manifest.md) 第三/四节。
- **④ 官方未给**：文档**提及但未给出细节**的项全束统一标「**官方未给**」，**不得据页面名称、同组其他束或常识补全**，**不得**写成「默认无限制」——包括：**分成比例**（F-048、F-049、F-056 仅给出结算关系/结算方式/签约的存在与入口）、**结算周期**（仅提「账单明细」可对账，F-067）、**审核时长**（除分享应用给出「**7 个工作日内**」F-294 外，其余各类审核时长均未给出）、**全局限流与配额**（仅单接口级有分页上限，F-386、F-395）、**移动端开放时间点**（仅表述为「后续开放 / 将陆续开放」，F-291、F-292），以及企业认证完整材料清单、token 撤销机制、模型池完整清单、席位上限具体数值等。完整清单见[核验报告](references/verification.md) 第五节。
- **⑤ 跨页口径不一致并列**：两处均为**两处官方口径并列**，非任一方错误，一律**并列表述、不择一、不替官方判定**——① 签名填充算法：`PSS`（**F-308**，D9「生成密钥」）对 `PKCS#1 v1.5`（**F-346**，D9「签名生成：详细步骤」）；② 凭证有效期：`24h`（**F-285**，D9「Token 类型一览」）对 `expires_in: 3600`（**F-366**，D10「换取接口调用凭证」，单位秒）。数字存在但两页口径冲突，属「有值但冲突」而非「未给」。见[核验报告](references/verification.md) 第四节。
- **⑥ 版本时效三方并列**：三方**并列登记、不择一、不互相倒写**——本束文档站**未见统一版本号**（核验时点 **2026-10-16**）；同组 [WorkBuddy 官方站点与四区文档](../workbuddy-official-docs/index.md) 束的产品更新日志止于 **5.7.7（2026-10-08）**；同组 [分享能力接入与推广管理](../workbuddy-open-platform-sharing-and-promotion/index.md) 束的平台公告要求客户端 **≥ 5.8.0（公告 2026-10-14）**。**后两个数字来自同组束，不属本束 F 编号集合**，引用时须注明各自来源与所属束。
- **⑦ 勘误 E1～E3（文档自身缺陷）**：**E1** = D5「连接器」页 `mcp.json` 远程 MCP 示例 URL 原文含乱入文本 `https://mcptokenSchema 字段.example.com/mcp`（F-105），属站点编辑错误，**不得**作为可用端点照抄、不擅自更正；**E2** = D2「入驻开放平台」页个人认证必填信息「开发者真实姓名 / 真实姓名」并列（F-040），照抄并列、不合并、不推断哪项是笔误；**E3** = D5/D6/D7 正文存在悬空章节引用（「见 6.3 / 6.4 / 第六节 / 第九节」），正文中找不到对应编号章节，登记为文档内部引用缺陷，**不得据编号推断被引用内容**。见[核验报告](references/verification.md) 第二节。
- **⑧ 端与形态边界须带端别**：本束所有端相关声明均标注端归属，**不可混写**——**本地助理相关能力**（查询在线状态 / 发送消息 / 查询历史）属 **PC 端本机**（F-271、F-377、F-378、F-380、F-385）；**云端任务 / ACP 通道 / 会话产物**（云端任务与鉴权 token、SSE + JSON-RPC 2.0 实时通信、产物拉取与媒体下载）属**云侧**（F-389、F-390、F-392、F-401、F-410、F-417）；**分享能力接入**当前 **PC 端已支持**（Windows / macOS 应用）、**移动端「后续开放」**（规划态），客户端须 **≥ 5.8.0**（F-291、F-292、F-321、F-353）；内嵌 `data` 支持矩阵为**移动端支持、PC 端不支持**（F-341、F-351）；第三方应用类型（**硬件接入 / Buddy 应用 / 积分应用**）为**并列类型**，非同一种能力（F-272～F-275）。见[边界、版本与已知缺口](concepts/10-boundaries-versions-and-known-gaps.md)。

## 主题关联

- [WorkBuddy 官方站点与四区文档](../workbuddy-official-docs/index.md) —— 同产品的官方文档教程化束（产品定位与四端文档），其**产品版本线口径（5.7.7）**与本束版本时效三方并列互照。
- [WorkBuddy 开放平台分享与推广](../workbuddy-open-platform-sharing-and-promotion/index.md) —— 同属开放平台侧的平台公告教程化束，其公告口径（**端边界当前仅 PC 端**、客户端 **≥ 5.8.0** 门槛）与本束 D9 文档口径**互证**，两束采集条件不同（该束公告需已登录会话）。
- [WorkBuddy 智能硬件接入白皮书](../workbuddy-hardware-integration-whitepaper/index.md) —— 硬件接入方向的商务与 **OAuth 2.0 + PKCE** 链路束，可与本束第三方应用授权认证与 Open API 鉴权链路对照。
- [CodeBuddy 产品矩阵](../codebuddy/index.md) —— 同账号与积分体系下的产品线，可对照本束 Open API 涉及的账号体系与产品矩阵语境。

## 一句话结论

本束能支持**入驻门槛**（个人 / 管理员实名 / 企业三档认证路径与规则）、**可开发哪些业务类型**（技能、专家、专家团、连接器、外部应用接入共 5 类）、**接口分类与端边界**（Open API 按认证授权、本地助理、云端任务、会话产物等分类，且逐项标注 PC 端本机 / 云侧 / 移动端规划态）、**变现门槛**（两步开通：先入驻建立结算关系再发布付费资产；一次性付费与按月付费两种模式）这几类判断；但它同时标定了**信源距离的上限**——**厂商单源自述、无第三方核验、未在本机实跑**，分成比例、结算周期、全局限流配额等商务与边界数字**官方未给**，跨页两处口径并列不择一，7 篇侧栏页未采集。适合当作「**开发与接入链路已成形、具体商务与边界口径待官方补全与实跑复核**」的开发者底座使用。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
