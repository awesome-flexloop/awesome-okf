---
okf_version: "0.2"
type: bundle
title: InkOS——让多个 AI Agent 接力写完一部长篇的开源创作智能体系统
description: 开源 AI 小说创作智能体系统教程（枫音AI 推文核验转化）——10 个 Agent 流水线、7 真相文件与三层记忆、去 AI 味与文风仿写、守护进程挂机写书、续写与同人，含从零建书实操与四项勘误
tags: [inkos, ai小说, 多智能体, 创作系统, 记忆系统, 真相文件, 去ai味, 文风仿写, 守护进程, 开源, AGPL, 核验转化]
generated:
  by: reference_agent/trae-solo
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: draft
stale_after: "2026-12-10"
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: blog
    resource: https://mp.weixin.qq.com/s/wJr32O2L82eq5k_7wJHiJQ
    title: "Github已获10K星标，开源AI小说神器来了！（枫音AI，2026-10-08）"
  - id: github
    resource: https://github.com/Narcooo/inkos
    title: "Narcooo/inkos GitHub 仓库（README 主人）"
  - id: github-api
    resource: https://api.github.com/repos/Narcooo/inkos
    title: "Narcooo/inkos GitHub API 元数据"
---

# InkOS——让多个 AI Agent 接力写完一部长篇的开源创作智能体系统

> **类型**：开源创作工具教程（第三方媒体产品推广文 + 官方 GitHub README/API 核验转化）
> **信源**：微信公众号「枫音AI」2026-10-08 推文《Github已获10K星标，开源AI小说神器来了！》+ GitHub 仓库 `Narcooo/inkos` 与 API（核验日 2026-10-10）。博文为**带营销夸大的产品推广文**，其架构数字与厂商站台宣称需经官方核验后方可引用；**官方 README 为技术事实的权威源**。
> **P0 核验**：4 条 P0 声明（星标数、Agent 数量、审计维度、厂商站台）→ **0❌ / 4⚠️**，全部为口径偏差而非事实不成立；核心能力（多 Agent 流水线、长期记忆、去 AI 味、文风仿写、守护进程、续写与同人）**全部由官方 README 证实**。勘误四项 E-1~E-4 见 [verification.md](references/verification.md)。

## 本文概要

InkOS 是 **`Narcooo/inkos` 开源的 AI 小说创作智能体系统**（官方描述："Autonomous novel writing AI Agent — agents write, audit, and revise novels with human review gates"，F-030）。它**不是又一个 AI 写作对话框**，而是一套**由多个 AI Agent 接力完成一部长篇小说**的系统：写、审、改全程接管，用流水线把"搭框架 → 写正文 → 审计 → 修订"拆给不同角色，并靠一套持久化记忆（7 真相文件 + 三层记忆）保证写到百万字也不丢设定。交互上有 TUI、Studio、OpenClaw 三种入口；内容侧支持去 AI 味、文风仿写、守护进程挂机写书、续写与同人。

> ⚠️ **三条先读提示**：
> 1. **"十个还是五个 Agent"是最重要勘误（E-1）**：博文反复称拆成 **五个** Agent（F-009/F-013/F-020），官方 README 实际是 **10 个角色**（雷达/规划师/编排师/建筑师/写手/观察者/反射器/归一化器/审计员/修订者，F-033）。博文的"五个"只覆盖下游最直观的节点，漏掉了规划师、编排师、观察者/反射器——恰恰是"写得长、记得住"的关键。
> 2. **星标被夸大（E-3）**：标题称"10K 星标"，核验日 GitHub API 实测 **5,595**（≈5.6K）——"10K"为发布时点自宣或夸大口径，不作为独立事实。
> 3. **开源协议补充**：博文只写"开源"未提 License，InkOS 正式采用 **AGPL-3.0**（F-032）——想二次开发/商用部署需先评估 AGPL 传染性。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-inkos-overview.md](concepts/00-inkos-overview.md) | InkOS 是什么——一句话定位、三种交互入口（TUI/Studio/OpenClaw）、项目背景与 AGPL-3.0、10 个 Agent 流水线总览与"五个 vs 十个"勘误边界 |
| [01-memory-and-agent-pipeline.md](concepts/01-memory-and-agent-pipeline.md) | 怎么做到"写到百万字还记得住"——10 角色接力管线、7 真相文件唯一事实源、三层记忆（JSON 权威态+Markdown 投影+SQLite 时序检索）、编排师选材与反射器 JSON delta 写入、审计与修订闭环 |
| [02-content-capabilities-and-fit.md](concepts/02-content-capabilities-and-fit.md) | 内容能力全景与适用边界——去 AI 味（疲劳词/禁用句式/文风指纹）、文风仿写（style analyze/import）、守护进程挂机写书、续写与同人、多模型路由；适合做什么/不适合做什么决策表 |

### examples/ — 实操示例

> 本目录是**基于官方 README 逐字核验重组的实操指引，不是博文作者的实测记录**：博文仅以营销软文口径描述界面与流程，未给任何命令、无版本号、无输出；本包制作中也未在任何环境真机执行。执行前请以官方最新文档为准。

| 文档 | 主题 |
|------|------|
| [00-install-and-first-book.md](examples/00-install-and-first-book.md) | 从零跑通 InkOS——npm 全局安装、模型配置、`inkos book create --brief` 建书并走完"世界观→角色→大纲→细纲→确认→开写"、守护进程 `inkos up` 挂机写章与通知；含配置检查表与常见坑 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | F-001~F-048 事实清单（博文事实 28 条 + 核验补充 20 条），逐条标注信源层级、author_claim 与 P 级 |
| [verification.md](references/verification.md) | P0 权威核验报告：4 项 P0（0✅/4⚠️/0❌）、批 A/B 两路核验记录、勘误四项（E-1 Agent 五vs十 / E-2 审计 37vs33 / E-3 星标 10Kvs5.6K / E-4 厂商站台无出处）、核验方法与未覆盖边界 |

## 主题关联

- [Orca ADE 多 Agent 桌面工作台](../orca-ade/index.md)：同为"多 Agent 编排"工具，但 Orca 面向**编程 Agent 舰队的并行编排**，InkOS 面向**创作 Agent 流水线的长程协作**——一个是工作台编排层，一个是创作控制面。
- [EchoBird 百灵鸟 AI Agent 桌面管理工具](../echobird/index.md)：同为"模型枢纽 + 本地 LLM"，可对照"管接哪个模型"与 InkOS "管怎么写长书"的差异。
- [LoopX 长程 Agent 控制面](../loopx/index.md)：同公众号同体裁转化；LoopX 治理"跨天跑、不空烧"，InkOS 治理"跨章节写、不崩设定"，都是长程状态外化到文件系统的路线。

## 已知边界

- **未真机实测**：examples 中命令均经官方 README 逐字核验，但**本包制作中未在任何环境执行**；文中引号内容为官方 README 措辞而非实测输出。
- **星标时点口径**：博文"10K"为发文时点（2026-10-08）表述；核验日（10-10）GitHub API 实测 **5,595**（F-046、E-3），引用务必带时点。
- **Agent 具名数**：官方 README 明确 10 个角色（F-033）；博文"五个"为缺省/简化口径（E-1），无歧义但须以官方为准。
- **审计维度**：官方为 **33 维**（F-037）；博文"37 维"无出处（E-2）。
- **厂商站台无出处**：博文称 Kimi/火山站台（F-002），GitHub README 无任何厂商官方站台声明（F-047、E-4），应剥离营销话术后评估。
- **AGPL 未在博文书面**：博文只写"开源"，实际为 AGPL-3.0（F-032），二次开发/商用需评估。
- **未覆盖项**：博文发布时点（10-08）星标快照无法还原；"去 AI 味"实际效果依赖模型、无法本文档量化验证；多模型路由的边际收益取决于用户模型池。
- **观点分层**：F-002/F-003/F-004/F-014/F-019/F-028 等为博文作者观点（P2 单源），正文已显式标注，不作为事实引用。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```