---
type: Reference
title: "开源对标信源：OmniRoute 本地 AI Gateway（inurl 路由/压缩机制参照系）"
description: "G5（2026-09-28）四源交叉核验 OmniRoute 实体与其 19 路由策略/Combo/RTK 压缩机制，作为 inurl /app「路由与压缩」面板自述「OmniRoute 同款思路」的外部参照系；只做事实对标与口径差异记录，不作抄袭/侵权判定。"
tags: [P0核验, 开源对标, AI网关, 路由策略, 信源]
status: verified
reverified: 2026-09-28
stale_after: 2026-12-31
sources:
  - id: omniroute-site
    resource: https://www.omniroute.online/
    title: "OmniRoute 官方站（#1 Open Source AI Router；352 providers / 19 routing strategies / :20128）"
    last_verified: 2026-09-28
  - id: omniroute-npm
    resource: https://www.npmjs.com/package/omniroute
    title: "npm 包 omniroute（访问时 v3.8.49；19 策略表、Combos、RTK 压缩、免费层口径）"
    last_verified: 2026-09-28
  - id: omniroute-github
    resource: https://github.com/diegosouzapw/OmniRoute
    title: "GitHub diegosouzapw/OmniRoute（MIT 许可、本地优先、自托管网关源码）"
    last_verified: 2026-09-28
  - id: media-tencent
    resource: https://developer.cloud.tencent.cn/article/2745276
    title: "腾讯云开发者社区（2026-09-17）：OmniRoute 19 策略/Combo/RTK+Caveman 第三方复述"
    last_verified: 2026-09-28
related_facts: [F-095, F-104]
---

# 开源对标信源：OmniRoute

> 本页为 G5 三次复核（2026-09-28）新增信源。inurl `/app` 设置页在路由策略、提示词压缩与 Combo 三处**主动写出**「OmniRoute 同款思路，规则式实现」「与 OmniRoute 的 Combo 路由链一致」（事实登记见 [article-source.md](article-source.md) F-095/F-104）。本页核实 OmniRoute 是什么、两者机制口径何处相同何处不同。

## 1. 实体卡（四源交叉，2026-09-28 访问）

| 项 | 口径 | 来源 |
|---|---|---|
| 定位 | 开源、**本地优先（local-first）自托管 AI Gateway / AI Router**，一个 OpenAI 兼容端点统一多家模型供应商，自动故障转移 | 官方站、npm、媒体 |
| 许可 | **MIT License**（第三方指南与媒体均述「free, MIT-licensed」；以 GitHub 仓库 LICENSE 为准） | GitHub、omniroute.site |
| 分发 | `npm install -g omniroute`（访问时 npm 显示 **v3.8.49**，19 天前发布，累计 288 个版本）；另支持 Docker/Electron/PWA/Termux/ARM | npm、媒体 |
| 本地端点 | 安装后网关在 **http://localhost:20128**，API 前缀 `/v1`（OpenAI 兼容），控制台 :20128；零配置时 `model:"auto"` 无需密钥即可用免费路由 | 官方站、npm、非官方指南 |
| 维护者 | diegosouzapw（联系邮箱 diegosouza.pw@outlook.com，巴西；Kimi/Moonshot AI 为其 founding Open Source Friend）；项目已加入 **Cheaper Inference** 商业生态 | npm、官方站 |
| 能力面 | 19 路由策略 + Combo 分层组合 + 上下文压缩（RTK+Caveman）+ 熔断/加密凭据/MCP/A2A/memory/guardrails/evals；兼容 Claude Code、Codex、Cursor 等 30+ 客户端 | 官方站、媒体 |

> ⚠️ **时点自述数字（不固化、不交叉仲裁）**：providers 数量在不同来源/时点差异明显——官方站 2026-09-28 自称 **352 providers**；npm README 同期口径为「43 个免费层 provider pools / 516 个模型、约 1.53B 免费 tokens/月」；2026-09-17 中文媒体引述 README 为「290+ providers、500+ models、90+ 免费层、约 2.9 万 Star」，官方站同期显示 69.9k stars。**这些数字随 catalog 双周审计与统计口径变化，本束只记录区间与出处，不作为任何结论的定量依据。**

## 2. 机制对照（与 inurl /app 面板逐项）

| 机制 | OmniRoute（开源原型口径） | inurl（/app 界面自述口径，F-095） |
|---|---|---|
| 路由策略数量 | **19 种**（priority、fill-first、weighted、round-robin、cost-optimized、headroom、context-optimized、cache-optimized、lkgp、auto 等，可按 combo 步骤混用） | **19 种**（轮询、延迟优先、优先级、成本优先、健康优先、成功率优先、随机、最少使用、余量优先、加权、粘性、多样性、可靠性、成本+延迟兼顾、新鲜度、自动、极速优先、极廉价优先、均衡 Top3 轮询） |
| 多策略组合 | **Combos**（旗舰特性）：多目标分层，当前层不可用/额度耗尽自动流转下一层；`auto` 按健康/额度/成本/延迟等多因子实时打分构建虚拟 combo | **路由链 Combo**：以 `>` 分隔多个策略，按层级依次尝试，上一层全部失败自动流转下一层；页面原文「与 OmniRoute 的 Combo 路由链一致」「共 19 种可任意组合」 |
| 提示词压缩 | **12 引擎流水线**，自述可压缩适用上下文 **15–95%**；文档化的工具链重负载示例约 **89%**（RTK + Caveman，重写 git diff/grep/日志等冗长工具输出） | **5 档预设**：Lite≈15% / Standard≈30% / Aggressive≈50% / Ultra≈75% / RTK 工具链去重 60–90%；页面原文「压缩率为估算值（OmniRoute 同款思路，规则式实现）；代码块/链接/JSON 均原样保留，绝不损坏」 |
| 偏好生效方式 | 本地配置文件/控制台，请求经本地网关 | 设置保存到账户后**下发本机代理**，「下次请求自动生效，无需重启」；厂商调用仍从用户电脑发出（界面口径） |
| 部署与信任模型 | 完全本地自托管，官方自称 **zero telemetry**、请求路径无 OmniRoute 云；MIT 源码可审计 | **闭源云控制台 + 闭源本机代理**（运行时下载、启动器内嵌令牌与主密钥，供应链层不在 E2EE 覆盖内，见 [verification.md](verification.md) F-053）；云端存密文与 escrow |
| 供应商规模 | 官方站自称 352 providers（时点自述，见上注） | catalog 机器审计 46 providers / 133 模型（F-090） |

## 3. 关键差异（避免对标过度）

1. **相似层在"本机代理的路由/压缩策略"，不在整体架构**：OmniRoute 是无云的纯本地开源网关；inurl 是"云控制台（密钥库/套餐/后台）+ 本机代理"双层闭源产品。策略命名与 Combo 概念同源，不等于产品形态相同。
2. **压缩率数字两套口径，均为各自自述**：OmniRoute 称 15–95%（12 引擎、工具链示例 ~89%）；inurl 五档上限 75%、RTK 档 60–90%，且页面自标"估算值"。本束未对任何一方做独立基准测试，**两个数字都不作为事实承诺引用**。
3. **可审计性不同**：OmniRoute 策略/压缩实现有 MIT 源码可核；inurl 代理为运行时下载的闭源程序，"规则式实现"无法从源码验证，只能记为界面自述。

## 4. 边界声明

- inurl 页面已**主动自认**机制思路来自 OmniRoute（"同款思路""Combo 一致"），本页仅记录这一自认与双方公开口径。
- **本页不作抄袭、剽窃或侵权判定**：MIT 许可允许自由借鉴与再实现；"思路/命名相似"与"源码或许可违约"是不同层面的结论，后者需要代码级比对与法律判断，超出公开资料复核的范围。
- 本页同样不评价两个方案的优劣或推荐取舍；选型讨论限于 [../concepts/03-cost-strategy-boundaries.md](../concepts/03-cost-strategy-boundaries.md) 的 flagged 边界内。

## 5. 来源与访问记录

- [omniroute.online](https://www.omniroute.online/)（官方站，2026-09-28 访问）
- [npmjs.com/package/omniroute](https://www.npmjs.com/package/omniroute)（v3.8.49，2026-09-28 访问）
- [github.com/diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute)（2026-09-28 访问，LICENSE 以仓库为准）
- [腾讯云开发者社区·OmniRoute 介绍](https://developer.cloud.tencent.cn/article/2745276)（2026-09-17 发布，2026-09-28 访问；第三方媒体，数字为其发稿时点口径）
- 旁证（非主要信源）：[omniroute.site](https://omniroute.site/) 非官方指南（MIT/端口/压缩率/auto 子模式口径一致）
