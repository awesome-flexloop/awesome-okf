---
okf_version: "0.2"
type: Concept
title: InkOS 是什么——让多个 AI Agent 接力写完一部长篇的创作智能体系统
description: InkOS 开源定位、三种交互入口、10 个 Agent 流水线总览与"五个 Agent"勘误边界、AGPL-3.0 开源协议与项目背景（GitHub 星标 5.6K）
tags: [inkos, ai小说, 多智能体, 创作系统, 开源, AGPL, agent流水线, 核验勘误]
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
    title: "Narcooo/inkos GitHub API"
---

# InkOS 是什么——让多个 AI Agent 接力写完一部长篇的创作智能体系统

## 一句话定位

InkOS 是 **`Narcooo/inkos` 开源的 AI 小说创作智能体系统**（官方英文描述："Autonomous novel writing AI Agent — agents write, audit, and revise novels with human review gates"，F-030）。它不是"又一个 AI 写作对话框"，而是一套**由多个 AI Agent 接力完成一部长篇小说**的系统：写、审、改全程接管，用流水线把"搭框架 → 写正文 → 审计 → 修订"拆给不同角色，并靠一套持久化记忆（真相文件 + SQLite）保证写到百万字也不丢设定（F-005、F-017）。

## 项目背景与开源口径

| 项 | 值 | 出处 |
|---|---|---|
| 仓库 | `github.com/Narcooo/inkos`，公开，默认分支 master | F-029（GitHub API） |
| 主语言 / 建仓 | TypeScript / 2026-03-12 | F-031 |
| 开源协议 | **AGPL-3.0**（GNU Affero GPL v3.0，2026-04-10 切换） | F-032（官方 API + LICENSE） |
| 星标 | 核验日（2026-10-10）**5,595**；forks 1,043；open_issues 123 | F-046/F-031 |
| 发布形态 | npm 包 `@actalk/inkos` 全局安装；已发布为 **OpenClaw Skill**（clawhub.ai/narcooo/inkos） | F-034/F-039 |

> ⚠️ **博文星标勘误（E-3）**：文章标题称"已获 10K 星标"，核验日 [GitHub API](https://api.github.com/repos/Narcooo/inkos) 实测仅 **5,595**（≈5.6K）。"10K"为发布时点自宣或夸大的营销口径，**不应作为独立事实引用**。
>
> ⚠️ **开源协议补充**：文章只写了"开源"，未提许可证。InkOS 正式采用 **AGPL-3.0**——这一点对想二次开发/商用部署的读者很重要（AGPL 的传染性不同于 MIT/Apache），需在选型时评估。

## 三种交互入口（"Simple 表面，Complex 内核"）

InkOS 提供三套交互方式，**共享同一套交互内核**（阅读体验上是"一个对话框"，运行机制上是"一套控制脑"）：TUI（`inkos tui` 全屏仪表盘）、Studio（本地 Web 工作台）、以及 OpenClaw/任一兼容 Agent 直接调用（`inkos interact --json`）[F-040]。

博文作者对它的评价（F-019，**作者观点，P2 单源**）是"表面足够简单、内核足够复杂"，把小说创作所需的复杂流程压缩进一个对话框——用户只需说一句创意，系统就自动完成世界观、角色卡、大纲、细纲的搭建与确认（F-005、F-011、F-012）。这一"先建框架、人确认后再推进"的设计的确贴近官方"对话式建书 + 人工审核门控"的定位（F-036）。

## 架构总览：不是"五个"，而是 10 个 Agent 角色

> 🔴 **架构勘误（E-1，影响最大）**：博文反复强调"它把写长篇网文拆成**五个** AI Agent"（F-009、F-013、F-020）。核验官方 README"工作原理"表后，实际是 **10 个 Agent 角色**协同完成一章（F-033）。

| 角色 | 职责 | 博文是否提及 |
|---|---|---|
| 雷达 Radar | 扫描平台趋势与读者偏好，指导故事方向（**可插拔、可跳过**） | ✅（F-021） |
| 规划师 Planner | 读作者意图+当前焦点+记忆检索结果，产出本章意图（must-keep/must-avoid） | ❌ 漏述 |
| 编排师 Composer | 从全量真相文件按相关性选上下文，编译规则栈与运行时产物 | ❌ 漏述 |
| 建筑师 Architect | 规划章节结构：大纲、场景节拍、节奏控制 | ❌（博文在隐含层，未点名） |
| 写手 Writer | 基于编排后的精简上下文生成正文（字数治理+对话引导） | ✅（F-020） |
| 观察者 Observer | 从正文中过度提取 9 类事实（角色/位置/资源/关系/情感/信息/伏笔/时间/物理状态） | ❌ 漏述 |
| 反射器 Reflector | 输出 JSON delta（非全量 markdown），代码层做 Zod schema 校验后 immutable 写入 | ❌ 漏述 |
| 归一化器 Normalizer | 单 pass 压缩/扩展，将章节字数拉入允许区间 | ❌ 漏述 |
| 连续性审计员 Auditor | 对照 7 真相文件验证草稿，**33 维度**检查 | ✅（但数字误述，见 E-2） |
| 修订者 Reviser | 修复审计发现的问题——关键自动修，其他给人工审核 | ✅（F-023） |

**为什么"五个 vs 十个"很重要？** 博文的"五个"只覆盖了**下游最直观的节点**（雷达/建筑师/写手/审计/修订），而省略了系统**真正区别于普通 AI 写作工具**的上游编排机制——**规划师**（决定本章该写什么意图）、**编排师**（决定把哪些上下文喂给写手）、**观察者/反射器**（从正文回写状态、由代码层校验写入而不是让 LLM 自由发挥）。这三点恰恰是 InkOS"写得长、记得住"的关键（F-033、F-038）。详见 [记忆与 Agent 流水线](01-memory-and-agent-pipeline.md)。

## 博文两者关系与阅读建议

- **本 bundle 信息分层**：博文（枫音AI 推广文）作为**宣传来源**——其架构描述与数字不可直接引用，但功能清单与 UI 描述可用于定位；**官方 GitHub README 为权威事实源**，所有技术细节以 README 为准（F-029~F-048）。
- **一句话结论**：InkOS 真实存在、开源可用、核心能力（多 Agent 流水线 + 长期记忆 + 去 AI 味 + 文风仿写 + 守护进程）全部由官方 README 证实；但推广文的**星标数字被夸大、Agent 与审计维度数字有误述、厂商站台无出处**——读者应把它当"带营销夸大的产品介绍"来读，当 "可评估的创作工具" 来用。