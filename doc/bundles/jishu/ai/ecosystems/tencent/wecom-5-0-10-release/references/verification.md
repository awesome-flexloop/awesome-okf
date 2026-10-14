---
type: Reference
title: "企业微信 5.0.10 版本新功能核验报告"
description: "P0 权威核验：CLI/MCP 开放与发布时间、模块能力矩阵、安装命令与 npm 包真实性、大圆 AI 报告、智能文档增强、版本时效"
tags: [企业微信, WeCom, CLI, MCP, P0, 核验, npm, 智能表格]
generated: { by: "process:seven-concepts-v", at: "2026-10-14" }
verified: { by: "process:seven-concepts-v", at: "2026-10-14" }
status: stable
stale_after: "2027-01-31"
sources:
  - { id: W, resource: "https://work.weixin.qq.com/nl/act/p/b40dacdc68ee4589?ver=5.0.10&type=new&lang=zh" }
  - { id: O1, resource: "https://work.weixin.qq.com/nl/index/aicli?from=new_intro" }
  - { id: O2, resource: "http://m.toutiao.com/group/7675264433509138998/" }
  - { id: O3, resource: "https://www.npmjs.com/package/@wecom/cli" }
  - { id: O4, resource: "https://work.weixin.qq.com/" }
  - { id: O5, resource: "https://developer.work.weixin.qq.com/document/path/101805" }
  - { id: O6, resource: "http://www.cnstock.com/commonDetail/802000" }
  - { id: O7, resource: "https://juejin.cn/post/7622655641333596196" }
  - { id: O8, resource: "https://open.work.weixin.qq.com/help/wap/detail?docid=21657" }
---

# 核验报告

> **结论：`stable`（无核心声明证伪，3 类口径提示）。** 信源为企业微信**官方自有发布页**，其产品功能声明由官方 AI 开放能力页（O1）、企业微信官网（O4）、开发者中心（O5）与 npm 注册表（O3）交叉确认；发布时间由 IT之家（O2）锚定。未发现源文硬错误，⚠️ 项全部是**时点演进与写法口径**（模块数 7/10/11、命令大小写、灰度状态），已在正文按时点分层呈现。

## 日期与版本

| 对象 | 发布页口径 | 核验结论 | 处理 |
| --- | --- | --- | --- |
| 5.0.10 发布时间 | 页面无日期 | ✅ IT之家 2026-08-18 报道「今日宣布……正式面向所有规模企业开放」（F-019） | 正文补 2026-08-18 锚点，标注为媒体发布日 |
| 版本时效 | 未提后续版本 | ⚠️ 2026-10-14 已发布 5.0.12（WorkBuddy 深度互通）（F-031） | 已知边界声明 5.0.10 已被接替 |
| CLI 包版本 | 未给出版本号 | 补：npm `@wecom/cli` 核验时 v1.3.4、MIT（F-024） | 作为补充事实，标注核验时点 |

## P0 声明核验

| 声明 | 结果 | 权威依据与处理 |
| --- | --- | --- |
| 5.0.10 面向所有规模企业开放 CLI 与 MCP | ✅ | O1 官方页 + O2 发布报道 + O5 开发者中心三方一致；O2 另载「取消企业人数、资质门槛」（F-019/F-020） |
| 七大模块开放接口（消息/邮件/文档/待办/日程/会议/微盘） | ✅（带时点差） | O1 当前页逐项可证且能力描述更细；但模块已扩展为 11 个（F-021/F-027），正文区分「发布页枚举 7 个」与「当前 11 个」 |
| 安装命令 `npx skills add wecomTeam/wecom-unified -y -g` | ✅（大小写有异文） | O1 官方页命令为 `WecomTeam/wecom-unified`；npm 仓库 org canonical = WecomTeam（F-023/F-025）。GitHub org 大小写不敏感，命令可用，但正文标注三处原文 |
| `@wecom/cli` 终端安装路径 | ✅ | npm 注册表一手：官方简介、MIT、仓库 WecomTeam/wecom-cli、v1.3.4（F-024）；O1 给出 `npm install -g @wecom/cli` + `npx skills add WeComTeam/wecom-cli` 双步（F-023） |
| 兼容主流 Agent（WorkBuddy/DeepSeek Harness/MiniMax Code/Kimi Work/Codex） | ✅ | O1 官方页逐字列示，另含「企业自研智能体」（F-022） |
| 智能表格 AI 分析报告·大圆（灰度中） | ✅ | O4 官网 AI 介绍：随时唤起大圆、一键生成专业美观分析报告、可对话调整（F-028）；灰度状态仅发布页标注，按页面时点呈现 |
| 报告随数据更新实时刷新 | ⚠️ 单源 | 仅发布页一句（F-016），O4 摘要未含；正文标注「发布页单源」 |
| 智能文档导出 Word/PDF/Markdown + 打印、描述字号 | ✅ | O4 官网逐字一致（F-029） |
| 安全四机制（权限独立/人工审批/授权有效期/行为留痕） | ⚠️ 媒体转述 | 出自 O2 报道，未取得开发者文档逐字页（F-026）；正文标注转述层级 |
| 典型 Agent 场景（提案 PPT、经营看板、目标拆解） | ✅ | O2 发布日报道中的发布会口径示例（F-032），作为场景非成效呈现 |

## 口径并存表（非错误，禁止抹平）

| 维度 | 发布页 W（5.0.10 快照） | IT之家 O2（2026-08-18） | 官方 AI 页 O1（2026-10-14） |
| --- | --- | --- | --- |
| 模块数量 | 枚举 **7** 个（消息/邮件/文档/待办/日程/会议/微盘） | 概括「**十大**核心办公模块」（列举含通讯录） | **11** 个（文档系拆分为文档/表格/智能表格/智能文档，另增通讯录） |
| 文档能力 | 「文档」含创建文档**和表格** | 统称文档、表格 | 文档、表格、智能表格、智能文档四个独立卡片 |
| 安装命令 org 大小写 | `wecomTeam/wecom-unified` | `WecomTeam / wecom-unified`（排版带空格） | 对话路径 `WecomTeam/wecom-unified`；终端路径 `WeComTeam/wecom-cli` |
| Skill 包 | 仅 `wecom-unified`（一体包） | 仅引一体包 | 区分 `wecom-unified`（Agent 对话安装）与 `wecom-cli`（终端安装） |

**裁决**：三条时间线各自成立——发布页是 5.0.10 时点快照，O1 是核验时点（5.0.12 周期）的现状，差异源于能力持续上线；bundle 正文以发布页为事实主体，以 O1 为「现状演进」旁证，不以新口径改写快照。

## 信源距离与厂商叙事评估

- W 为**当事厂商官方发布**，对「产品提供什么能力」类声明是最高信源；O1/O4/O5 同为官方，互证充分。
- 全页**零成效数字**（无提效倍数、工时节省、成本下降），勘误四张清单第②张不适用，不存在营销数据污染面。
- O2（IT之家）承担两类官方页未载信息：发布**日期**（F-019）、门槛取消背景（F-020）、安全四机制（F-026）；其中安全机制未获开发者文档逐字复核，降级标注为媒体转述。
- O6（上海证券报，2026-10-14）等权威媒体提供版本时效旁证（F-031），同时解释 O1 兼容 Agent 列表首位为何是 WorkBuddy。

## V 四视角对抗审查

| 视角 | 攻击点 | 修正/结论 |
| --- | --- | --- |
| 魔鬼代言人 | 「开放 CLI/MCP」可能只是营销说法，包/仓库可能不存在；7 模块可能夸大 | npm 注册表一手证实 `@wecom/cli`（MIT、WecomTeam/wecom-cli、v1.3.4）（F-024）；模块逐项在 O1 可证；仍把 7/10/11 三个口径并列，防止把演进现状倒灌成发布日事实 |
| 新人 | 读者会把 `wecom-unified` 与 `wecom-cli` 当同一个包；照抄小写命令担心不规范；以为 5.0.10 是最新版 | 机制篇单设「两条安装路径与命令口径」小节，分包解释、给 canonical 写法并说明 GitHub 大小写重定向；总览篇明示 5.0.12 已于 2026-10-14 接替 |
| 业务方 | 灰度中功能可能用不了；企业数据被 Agent 调用有合规风险；版本能力会变 | 保留「功能灰度中」原标注；安全四机制（权限独立/审批/有效期/留痕）入正文并标注媒体转述；`stale_after: 2027-01-31` + 已知边界 |
| 未来视角 | 模块数、包版本、兼容 Agent 列表都会继续变；F-016 单源声明可能被证伪 | 所有时变信息带核验时点（2026-10-14，@wecom/cli v1.3.4）；F-016 标单源；到期复核官方页模块数与后续版本 |

## 双份事实编号

spec `facts.md` 与本目录 `article-source.md` 均登记 F-001～F-033，编号集合连续一致（18 条发布页事实 + 15 条核验补充）。

## 状态裁决

发布页**核心声明全部通过**官方或权威交叉核验，无 ❌ 证伪项；3 处 ⚠️（模块口径时间差、命令大小写、单源/转述条目）均不构成对核心声明的否定，且已在正文分层落实，bundle 定为 `status: stable`。版本时效内容（灰度范围、模块与包版本、兼容 Agent 列表、5.0.12 后续演进）在 `stale_after: 2027-01-31` 前安排复核。
