---
okf_version: "0.2"
type: Reference
title: 博文事实清单——《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》
description: 极客之家 2026-09-03 推文的 F 编号事实登记（双份登记之 bundle 份，与 spec facts.md 编号集合一致）
tags: [loopx, 事实登记, 微信博文, 长程-agent]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
  - id: github-loopx
    url: https://github.com/huangruiteng/loopx
  - id: pypi-loopx
    url: https://pypi.org/project/loopx/
  - id: openviking
    url: https://github.com/volcengine/OpenViking
  - id: ts-migration-rfc
    url: https://github.com/huangruiteng/loopx/blob/main/docs/architecture/rfcs/typescript-control-plane-migration-v0.md
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的 **bundle 侧登记**，与 spec `.trae/specs/okf-wiki-ecosystem/loopx-long-horizon-agent-okf-wiki/facts.md` 构成双份登记，编号集合须一致（F-001 ~ F-049，连续无跳号）。
> 【博】= 博文事实；【官】= 核验阶段补充事实（官方源）。观点条目标注「作者观点」。

## A. 信源元信息

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-001 | 标题《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》；公众号「极客之家」；作者「丛林」；发布于 2026-09-03 14:05；标注原创，文末定位山西 | 【博】 | ✅ browser 提取页面元信息 |
| F-002 | 文章 URL：https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ ；正文 2777 字符 | 【博】 | ✅ |
| F-036 | 「极客之家」公众号自述定位：长期分享实用开源项目，可后台留言互动 | 【博】 | P2 单源（自述） |

## B. 问题陈述与作者动机

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-003 | 作者描述长周期使用痛点：AI 编程工具连续工作数天时，第二天上下文中已无第一天目标，改过哪些文件、为何改对不上，无法复盘 | 【博】作者观点（体验陈述） | P2 |
| F-004 | 作者称执行节奏会乱：该停下确认时不停一路跑；无进展时一轮轮空烧 token | 【博】作者观点 | P2 |
| F-005 | 作者判断：靠聊天记忆加定时器管不住长周期任务 | 【博】作者观点 | P2 |

## C. LoopX 定位与热度

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-006 | LoopX 是开源、本地优先（local-first）的长程 Agent 控制面（control plane），作者称之为"状态内核"，运行在现有 AI 编程工具之上而非取代它们 | 【博】 | ✅ 官方 README 同口径 |
| F-007 | 分工：Codex、Claude Code、Cursor 等宿主负责逐轮执行；LoopX 管理跨轮次、跨天事项——目标、当前卡点、下一轮动作、每轮证据、剩余预算 | 【博】 | ✅ 官方 README 状态层描述一致 |
| F-008 | 博文称项目 GitHub 已有 5000 多 Star，"开源不久"，纯 Python 编写 | 【博】 | ⚠️ Star ✅（2026-09-13 API 实测 5818）；"纯 Python"见 F-041 |
| F-009 | 官方一句话定位："把会干活的 Agent，接成可管理、可复盘、可持续改进的数字员工" | 【博】 | ✅ PyPI/GitHub 项目描述逐字一致 |
| F-035 | 开源地址：https://github.com/huangruiteng/loopx | 【博】 | ✅ 仓库存在 |
| F-037 | GitHub API 实测（2026-09-13）：star 5818、fork 530、watch 28、开放 issue 83；Apache-2.0；仓库创建于 2026-05-31；主语言统计 Python；topics 含 agent-control-plane、agent-harness、agent-ops、long-horizon-agents、loop-engineering | 【官】GitHub API | ✅ |

## D. 核心功能（博文六块）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-010 | 状态内核：目标建立后，范围、进展、每轮证据等持久状态全部存于本地文件，不走任何云服务 | 【博】 | ✅ Local first 徽章 + 本地状态目录（F-046） |
| F-011 | 宿主会话关闭、电脑重启、隔一周再打开，工作可从上次停下的轮次续跑，无需翻聊天记录推断 | 【博】 | ✅ "durable across days, restarts, and harnesses" |
| F-012 | quota 机制：每次调度触发前先执行 `quota should-run` 检查——该 Agent 现在该行动吗、还有预算吗、有无实际状态变化 | 【博】 | ✅ 官方核心 tick 五命令之首 |
| F-013 | 无状态变化则跳过，该轮不计费；空转、预检失败、试运行（dry-run）均不计费 | 【博】 | ✅ 官方逐字（F-044） |
| F-014 | 人类门禁：需要人拍板的节点循环暂停并携带具体问题（如改动是否合入、路线是否继续），答复后才继续，非模糊"等待确认" | 【博】 | ✅ "Concrete user gates instead of a vague 'waiting for owner.'" |
| F-015 | 危险权限、对外发布、生产环境写操作决定权始终在人；不做全自动生产控制 | 【博】 | ✅ "not an autonomous production controller... final ownership stay with the human" |
| F-016 | `loopx dashboard` 在浏览器拉起本地工作台：进行中目标、等待回复门禁、定时挂起与已停任务均可见 | 【博】 | ✅ 官方受支持浏览器/PWA 路径 |
| F-017 | 工作台可同时挂多个 Agent 会话（Codex 干一段、Claude Code 接一段），目标状态与证据不丢 | 【博】 | ✅ |
| F-018 | 多宿主：Codex App、Codex CLI、Claude Code、Cursor 均有现成接入；国产 DeepSeek Harness 支持；可接自定义 runner；支持多 Agent 协作 | 【博】 | ✅ 官方宿主表范围更大（F-045） |

## E. 200 小时实证

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-019 | 作者作为 OpenViking 贡献者的公开 PR 序列：首个 PR 到最近一次 review 跨度超 200 小时；issue 修复与可复用修复知识同步沉淀 | 【博】 | ✅ 官方 README 专节 + 169 PR 实测（F-042） |
| F-020 | 博文转述边界：200 小时为自然时间跨度（wall-clock），模型未连续跑 200 小时，不代表无人值守 | 【博】 | ✅ 官方边界逐字对应（F-043） |
| F-042 | OpenViking：volcengine/OpenViking，"Self-evolving Context Database for AI Agents"，37,622 star（09-13），创建于 2026-01-05；huangruiteng 公开 PR 169 个，最早 #3335 于 2026-07-17 | 【官】GitHub API | ✅ |
| F-043 | 官方边界原文："This measures wall-clock project time, not continuous model execution or unattended production autonomy."；另有脱敏 Auto ML 200h+ 案例（标注非独立可复现/非生产成果/非雇主背书） | 【官】README | ✅ |
| F-048 | 官方"Used In Real Projects"三例独立用户报告：>13h C++ 精度运行；4 天无人值守；7 个已合并 PR（zilliztech/mfs，1B+ token 为用户自述）；官方标注"当前最强三例" | 【官】README | ✅ |

## F. 快速开始（作者实测路径）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-021 | 环境要求：Python 3.11+；macOS/Linux 直接用；Windows 需 PowerShell 7 | 【博】 | ✅ requires-python >=3.11 |
| F-022 | 安装三步：`python3 -m pip install --upgrade loopx` → `loopx workflow-skills --install` → `loopx doctor` | 【博】作者实测 | ✅ 逐字一致（1.0 仍同组命令） |
| F-023 | 安装后重启 AI 编程工具以重新加载工作流技能 | 【博】作者实测 | ✅ 官方同要求 |
| F-024 | `cd /path/to/your-project` → `loopx connect` → `loopx status` | 【博】作者实测 | ✅ |
| F-025 | 未初始化时 connect 提示状态缺失：`loopx start-goal --guided --project . --goal-text "你的长期目标"` | 【博】作者实测 | ✅ |
| F-026 | status 可见当前目标/待拍板门禁/下一待办；dashboard 开工作台；博文称"没什么要配置，没有三方依赖，也没有遥测" | 【博】作者实测 | ⚠️ 0.4/0.5 时点成立；1.0 起需 Node 22.18+（F-040/F-041） |
| F-046 | 本地状态文件：保持 `.loopx/`、`.codex/goals/`、`.local/` 被 gitignore；连接成功标志：doctor 通过 + `.loopx/registry.json` + status 显示目标/门禁/待办 | 【官】README | ✅ |
| F-047 | 无遥测佐证：官方反馈 issue 模板"It is optional, contains no telemetry"，禁含日志/路径/凭证/项目名；`loopx first-run-report` 仅本地打印预填链接 | 【官】README | ✅ |

## G. 适用场景与作者评价（作者观点层）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-027 | 适用①：跨数天工程任务（大型重构、持续 issue 清理） | 【博】作者观点 | 与官方用例一致 |
| F-028 | 适用②：定时巡检（盯 PR、每日报），配额闸门防空烧 | 【博】作者观点 | 官方 heartbeat/monitor 对应 |
| F-029 | 适用③：ML 实验与研究，假设/证据/淘汰路线留痕 | 【博】作者观点 | Auto ML showcase、Explore 对应 |
| F-030 | 适用④：有审批要求的项目（发布/敏感数据），卡人工门禁 | 【博】作者观点 | 官方 gates 对应 |
| F-031 | 适用⑤：多 Agent 协作（一干一 review），所有权与交接清晰 | 【博】作者观点 | peer-agent teams 对应 |
| F-032 | 总评：行业进步多在单次任务；真实工作跨周；LoopX 不碰模型、只管状态与治理，思路方向很好，"大概率后面要火起来" | 【博】作者观点（含预测） | P2 单源；预测不固化为事实 |
| F-033 | 现状不成熟：v0.4.x 阶段；高级路径可选默认关闭/实验性；文档量大上手难；适合重度用户，不适合甩手掌柜 | 【博】作者观点 | ⚠️ 版本滞后（F-039）；默认关闭一项与官方 Explore 一致 |
| F-034 | 两个使用前提：高强度使用、常跑长任务；轻度玩家没必要 | 【博】作者观点 | P2 |

## H. 核验补充事实（版本时间线与架构演进）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-038 | PyPI 时间线：0.4.8（08-16）、0.4.9/0.5.0（08-19）、0.5.1（08-20）、0.5.2（08-22）、0.5.3（09-01）、0.5.4（09-02 UTC）、1.0.0（09-06）、1.0.1（09-07）、1.0.2（09-09）、1.0.3（09-11）、1.0.4/1.0.5（09-15）；requires-python >=3.11；无强制运行时依赖（deepseek-harness-sdk 为 optional extra） | 【官】PyPI JSON API | ✅ |
| F-039 | **勘误①（日期/版本表）**：博文 09-03 发布称"v0.4.x 阶段"，当日最新已是 0.5.4（0.5 线 08-19 开始）；核验时最新 1.0.5 | 【官】 | ⚠️ |
| F-040 | main 分支 README 要求：Python 3.11+ **且 Node.js 22.18.0+**（推荐 24 LTS）；Node 运行托管的空闲即退 TypeScript Effect 内核，LoopX 自动启动；Windows 原生 PowerShell 7 | 【官】README main | ✅ |
| F-041 | **勘误②（口径/时效）**：TS 迁移 RFC 日期 2026-08-15、Accepted（transaction-payoff 进行中，09-13 修订），Python→TypeScript 增量替换、不维护两套语义实现；博文"纯 Python"为 0.4/0.5 发货形态，1.0（09-06 起）为 Python 分发货 + 托管 TS 内核 | 【官】RFC + PyPI | ⚠️ |
| F-044 | 计费规则原文："Quiet skips, preflight failures, and dry-run previews do not spend."；自动轮次先查 quota、验证 writeback 后才 spend；安全兜底车道不得绕过用户门禁 | 【官】README | ✅ |
| F-045 | 官方宿主表：Codex App（含 SSH）、Codex CLI、Claude Code（opt-in 适配器，/loopx、/loop）、Cursor/shell/自定义 runner、DeepSeek Harness（dsh 原生插件/goal-mode）、KunlunCode、OpenCode、Pi、ZCode、Antigravity、Kiro；最小自定义 runner 示例 `examples/custom-runtime-minimal-cli-turn-smoke.py` | 【官】README | ✅ |
| F-049 | LoopX 1.0 Personal Agent Workspace：目标/注意力/会话/任务/文件/调度/恢复本地持久化；dashboard 为浏览器/PWA 受支持路径；1.0 另有桌面预览（mac 签名更新但未公证、Windows 手动更新+独立 CLI）；新增 Lark 异步收件箱与 Manager 群契约 | 【官】README + releases | ✅ |
