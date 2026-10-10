---
okf_version: "0.2"
type: Reference
title: P0 权威核验报告——InkOS 博文（2026-10-10 核验）
description: 4 项 P0 声明核验（0✅/4⚠️/0❌）、三处勘误（Agent 数量五vs十、审计维度37vs33、星标10Kvs5.6K）、厂商站台无出处，核验方法与未覆盖边界
tags: [inkos, P0核验, 勘误, 信源核验, 时效管理, AI小说]
generated:
  by: reference_agent/trae-solo
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: draft
stale_after: "2026-12-10"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/wJr32O2L82eq5k_7wJHiJQ
    title: "Github已获10K星标，开源AI小说神器来了！（枫音AI，2026-10-08）"
  - id: github
    resource: https://github.com/Narcooo/inkos
    title: "Narcooo/inkos README"
  - id: github-api
    resource: https://api.github.com/repos/Narcooo/inkos
    title: "Narcooo/inkos GitHub API 元数据"
---

# P0 权威核验报告

## 一、核验概览

| 项目 | 值 |
|---|---|
| 核验日期 | **2026-10-10** |
| 核验对象 | 微信公众号「枫音AI」2026-10-08 08:03 推文《Github已获10K星标，开源AI小说神器来了！》 |
| 信源距离 | **第三方媒体产品推广文（营销软文）+ 作者主观体验评价**（非官方口径，非代码级/真机级实测）；涉产品自宣数据（星标、Agent 数量、审计维度、厂商站台）一律按 P0 处理 |
| P0 声明数 | **4 条**（F-001、F-002、F-009、F-022） |
| P0 结论分布 | **✅ 0 / ⚠️ 4 / ❌ 0** |
| P0 ⚠️ 项 | F-001（星标 10K→实测 5.6K）、F-002（厂商站台无出处）、F-0093（Agent 五个→实际十角色）、F-022（审计 37 维→实测 33 维） |
| 核验补充事实 | F-029~F-048 共 **20 条**，来自 GitHub 官方 API + README |
| 勘误 | **E-1 ~ E-3 共 3 条**（Agent 数量误述 / 审计维度误述 / 星标量级出入）；E-4 厂商站台无出处 |
| 总体结论 | 产品与仓库**真实存在、开源（AGPL-3.0）、核心能力（五 Agent 流水线、三层记忆、去 AI 味、文风仿写、守护进程）全部证实**；但文章在**具体数字上含三处误述**（Agent 数量、审计维度、星标），均为**营销软文的夸大/简化口径** → bundle `status: draft`，正文须以官方口径为准并标注勘误 |

## 二、P0 核验记录

核验分两路并行进行：批 A（GitHub 仓库/API 事实）、批 B（功能口径 vs 官方 README）。

### 批 A｜GitHub 仓库事实

| 项 | 结论 | 官方原文关键措辞或实测值 | 来源 URL |
|---|---|---|---|
| F-029 仓库存在性 | ✅ | 仓库 `Narcooo/inkos` 存在，公开，默认分支 master | https://api.github.com/repos/Narcooo/inkos |
| F-030 官方描述 | ✅ | "Autonomous novel writing AI Agent — agents write, audit, and revise novels with human review gates" | 同上 |
| F-031 元数据 | ✅ | 主语言 TypeScript；created_at 2026-03-12；forks 1,043；open_issues 123 | 同上 |
| F-032 许可证 | ✅ | **AGPL-3.0**（GNU Affero GPL v3.0）；commit 记录 2026-04-10 切换 | 同上 + README LICENSE |
| F-046 星标（P0） | ⚠️ | `stargazers_count` = **5,595**、watchers = 5,595（核验日 2026-10-10）——文章"10K"为发布时点自宣/夸大 | https://api.github.com/repos/Narcooo/inkos |
| F-047 厂商站台（P0） | ⚠️ | README 无 Kimi/火山等厂商官方"站台"声明，仅 README"欢迎加群"社区链接 | https://github.com/Narcooo/inkos |

### 批 B｜功能口径 vs 官方 README

| 项 | 结论 | 官方原文关键措辞或实测值 | 来源 URL |
|---|---|---|---|
| F-033 Agent 数量（P0） | ⚠️ | 官方"每一章由多个 Agent 接力完成"列 **10 个角色**：雷达/规划师/编排师/建筑师/写手/观察者/反射器/归一化器/连续性审计员/修订者；雷达可插拔可跳过 — 文章"五个"是缺省简化（E-1） | https://github.com/Narcooo/inkos (工作原理表) |
| F-035 真相文件 | ✅ | 7 个真相文件（current_state/particle_ledger/pending_hooks/chapter_summaries/subplot_board/emotional_arcs/character_matrix），0.6.0+ 权威源迁 JSON（Zod schema 校验），markdown 保留为人类可读投影 | 同上（长期记忆节） |
| F-037 审计维度（P0） | ⚠️ | "连续性审计员从 **33 个维度**检查每一章草稿"——文章"37 维"无出处（E-2） | 同上（核心特性节） |
| F-038 SQLite 记忆库 | ✅ | Node 22+ 自动启用 SQLite 时序记忆数据库（story/memory.db），按相关性检索历史事实/伏笔/章节摘要，避免全文注入上下文膨胀 — 与文章 F-024 三层记忆完全对应 | 同上（工作原理·长期记忆节） |
| F-039 安装与配置 | ✅ | `npm i -g @actalk/inkos`；`inkos config set-global --provider --base-url --api-key --model`，存 `~/.inkos/.env` | 同上（快速开始节） |
| F-040 交互内核 | ✅ | TUI（inkos tui）/ Studio / `inkos interact --json` / OpenClaw 共享同一交互内核；支持 `--lang en` 英文 | 同上（更新+使用模式节） |
| F-041 去 AI 味 | ✅ | 写手 prompt 内建词汇疲劳词表/禁用句式/文风指纹；`revise --mode anti-detect` | 同上（核心特性节） |
| F-042 守护+通知 | ✅ | `inkos up` 后台循环写章；通知支持 Telegram/飞书/企业微信/Webhook（HMAC-SHA256 + 事件过滤） | 同上（核心特性节） |
| F-043 文风仿写 | ✅ | `inkos style analyze` 提取指纹 + `style import` 注入 | 同上（核心特性节） |
| F-044 续写/同人 | ✅ | `inkos import chapters` 逆向 7 真相文件；`inkos fanfic init --from --mode canon/au/ooc/cp` | 同上（核心特性节） |
| F-045 多模型路由 | ✅ | `inkos config set-model <agent>` 按 Agent 分配模型 | 同上（快速开始节） |

## 三、勘误表

| # | 博文口径 | 正确口径 | 证据（F 编号） | 影响面 |
|---|---|---|---|---|
| **E-1** | 写长篇网文拆成"五个 AI Agent" | 官方共 **10 个 Agent 角色**（雷达/规划师/编排师/建筑师/写手/观察者/反射器/归一化器/审计员/修订者）；文章"五个"只覆盖了其中下游核心节点（雷达+建筑师+写手+审计+修订），漏了规划师/编排师/观察者/反射器/归一化器 | F-009、F-013、F-020、F-033 | 架构误述：低估了系统编排层级（编排师/观察者/反射器负责上下文选材与状态写入），易让读者误以为只有前端 5 步骤 |
| **E-2** | 审计员从"37 个维度"检查 | 官方为 **33 个维度**（连续性审计员，含角色记忆/物资连续性/伏笔回收/大纲偏离/叙事节奏/情感弧线等）；"37"无出处 | F-013、F-022、F-037 | 数字误述，量级接近但不可直接用 |
| **E-3** | 标题"已获 10K 星标" | 核验日（2026-10-10）GitHub API 实测 **5,595**（≈5.6K）；"10K"为发布时点自宣或夸大，量级不符 | F-001、F-046 | 标题钩子夸大：吸引点击的营销数字 |
| **E-4** | "Kimi、火山等多个 AI 大模型厂商都站台支持这个项目" | GitHub README 及 API **无任何厂商官方"站台"声明**；仅有社区加群入口；文中"打广告"截图不具权威性 | F-002、F-047 | 营销宣称无独立出处——既非厂商官方背书，也无可引用第三方 |

> **E-1 特别标注**：这是本次核验中**影响最大的误述**——把 10 角色的多智能体编排系统简化为"五个 Agent"，会掩盖 InKOS 真正区别于普通 AI 写作工具的核心机制（编排师按相关性选上下文、观察者过度提取 9 类事实、反射器输出 JSON delta 由代码层 Zod 校验写入）。bundle 正文一律采用官方的 10 角色模型，并在 concepts 中明确标注博文"五个"仅是下游简化描述。
> **E-3/E-4 特别标注**：两处属**营销软文普遍手法**（星标量级夸大 + 厂商站台渲染），不影响产品本身真实存在与功能可信，但读者**不应将推广文的数字与背书当作独立事实**。

## 四、核验方法与未覆盖边界

- **方法**：GitHub API（`api.github.com/repos/Narcooo/inkos`）+ 仓库 raw README（中文 README 主人全文逐节核实）+ WeChat 博文全文 WebFetch
- **未覆盖**：
  1. 博文发布日（2026-10-08）的星标时点快照无法还原，仅能取核验日实测值（5,595）
  2. 文章中引用的 UI 界面截图未在真机运行验证（Studio/TUI 实际渲染）
  3. "Kimi、火山厂商站台"无法逐厂商回溯（无官方新闻稿/官方账号声明）
  4. 文章称"写一章可能半小时"等耗时数字为作者经验，无基准测试
  5. 30+ 篇待跑与真实写作质量未做代码级/真机级实测
- **未真机实测**：examples 中的命令经官方文档逐字比对，但**本包制作中未执行任何安装/写作**——全部命令正确性以官方 README 逐字为准（非实测输出）。