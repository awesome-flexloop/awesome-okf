---
okf_version: "0.2"
type: Reference
title: 博文事实清单——《Github已获10K星标，开源AI小说神器来了！》
description: 枫音AI 2026-10-08 推文的 F 编号事实登记（bundle 侧登记，区分 page_fact 与 author_claim），并含 GitHub 仓库/API 核验补充事实，编号连续
tags: [inkos, 事实登记, 微信博文, AI小说, 多智能体, 创作系统]
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
    author: "枫音"
  - id: github
    resource: https://github.com/Narcooo/inkos
    title: "Narcooo/inkos GitHub 仓库（README 主人）"
  - id: github-api
    resource: https://api.github.com/repos/Narcooo/inkos
    title: "Narcooo/inkos GitHub API 元数据"
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的 **bundle 侧登记**，记录微信公众号推广文原文口径与关键声明，并在同一编号体系内加入 GitHub 官方仓库/API 核验补充事实。
> **编号分段**：F-001~F-028 = 博文原文事实（区分 page_fact 页面事实 / author_claim 作者观点与自宣）；F-029~F-048 = 核验补充事实（GitHub 官方一手来源）。
> **信源距离层级取值**：`页面事实` / `作者观点` / `作者一手实测` / `官方文档` / `官方API` / `厂商自宣` / `第三方综述`。
> **P 级**：P0 = 产品/作者自宣类必核验数字（星标、Agent 数量、审计维度、厂商站台）；P1 = 一般技术事实；P2 = 观点/自述类单源。

## A. 博文元信息

| 项目 | 内容 |
|---|---|
| 标题 | 《Github已获10K星标，开源AI小说神器来了！》 |
| 公众号 / 作者 | 枫音AI / 枫音 |
| 发布时间 | 2026-10-08 08:03 |
| 文章 URL | https://mp.weixin.qq.com/s/wJr32O2L82eq5k_7wJHiJQ |
| 体裁 | 第三方媒体开源项目产品推广文（营销软文，含作者主观体验评价） |
| 采集/核验日 | 2026-10-10 |
| 主线实体 | InkOS（开源的 AI 故事创作智能体系统，GitHub: `Narcooo/inkos`） |

## B. 博文原文事实（F-001~F-028）

| 编号 | 事实陈述 | 类型 | 信源层级 | P 级 | 核验结论 |
|---|---|---|---|---|---|
| F-001 | 文章称 InkOS 是"体验感最好的 AI 小说创作工具之一、GitHub 上已获 10K 星标" | author_claim | 作者观点 | **P0** | ⚠️ 核验日 GitHub API 实测 5,595（≈5.6K），见 F-046 |
| F-002 | 文章称 Kimi、火山等多个 AI 大模型厂商站台支持该项目，并在文中打广告 | author_claim | 作者观点 | **P0** | ⚠️ 无可核验出处（注：GitHub README 有"欢迎加群"社区链接，但无厂商官方"站台"证据），见 F-047 |
| F-003 | 文章介绍大模型有上下文限制、记忆系统压缩影响写作质量 | author_claim | 作者观点 | P2 | 观点，常识性背景，不核验 |
| F-004 | 文章称 InkOS 是作者体验过的同类型里门槛最低的一款，像 AI 聊天一样 | author_claim | 作者观点 | P2 | 观点，不核验 |
| F-005 | InkOS 输入想法后，自动创建世界观、角色卡、大纲、细纲 | page_fact | 页面事实 | P1 | ✅ 与 README 建筑师/规划/ Brief 流程一致（F-036） |
| F-006 | 项目地址 github.com/Narcooo/inkos | page_fact | 页面事实 | P1 | ✅ 仓库存在（F-029） |
| F-007 | InkOS 是一个开源的 AI 故事创作智能体系统 | page_fact | 页面事实 | P1 | ✅ 开源（AGPL-3.0，F-032）；"故事创作智能体系统"与官方描述"Autonomous novel writing AI Agent"一致 |
| F-008 | 支持长篇小说、独立短篇、剧本、同人番外、互动影视、开放世界 | page_fact | 页面事实 | P1 | ✅ README 覆盖长篇/续写/番外/同人/仿写；剧本/互动影视/开放世界见 F-038 |
| F-009 | 文章称它把写长篇网文拆成五个 AI Agent，每个管一部分，流水线完成 | page_fact | 页面事实（转述） | **P0** | ⚠️ README 实际列 **10 个角色**（含 6 关键节点 Agent），见 F-033/E-1 |
| F-010 | 文章称 InkOS 之前是 Skill 包，最近推出 Web UI | page_fact | 页面事实 | P1 | ✅ 已发布为 OpenClaw Skill（F-034）；"Studio 2.0"为本地 Web 工作台 |
| F-011 | 左侧选项目、输入想法，先完善故事框架由用户确认，确认后才继续 | page_fact | 页面事实 | P1 | ✅ 与"对话式建书/人工审核门控"一致（F-036/F-040） |
| F-012 | 点击继续进入预设工作流，Agent 逐步搭建世界观、角色、大纲、细纲 | page_fact | 页面事实 | P1 | ✅ 与建筑师/规划师/编排师分工一致 |
| F-013 | 五个 Agent 之一是审计员，盯创作过程，发现易被平台审核卡住的设定就督促回炉 | page_fact | 作者转述 | **P0** | ⚠️ 审计维度实为 33（含连续性与合规类），文章未给 37 维度出处见 E-2；"平台审核卡住设定"对应主题规则/合规 |
| F-014 | 等待时间看"设计员"脸色，被多打回几次可能半小时 | author_claim | 作者观点 | P2 | 观点，不核验 |
| F-015 | "我的创作"界面：左对话窗口、右书本设定；含角色信息、情感弧线、伏笔、故事基石、规划 | page_fact | 页面事实 | P1 | ✅ 对应真相文件 7 类（角色矩阵/情感弧线/伏笔/当前状态/章节摘要等，F-035） |
| F-016 | 生成正文时可指定第几章，自动读取整本书设定，新变化随故事推进更新 | page_fact | 页面事实 | P1 | ✅ 与 7 真相文件 + 记忆检索一致 |
| F-017 | 写了几百章仍能记得初始设定与中途转变 | page_fact | 页面事实 | P1 | ✅ 与长期记忆（真相文件 + SQLite 全文检索）一致 |
| F-018 | 内置"去 AI 味"Skill，左下角加号引用 Skill 改写章节 | page_fact | 页面事实 | P1 | ✅ README "去 AI 味"内置于写手 prompt + `revise --mode anti-detect`（F-041） |
| F-019 | 表面简单、内核复杂：把小说创作复杂流程压缩进一个对话框 | author_claim | 作者观点 | P2 | 观点，不核验 |
| F-020 | 背后五个 Agent：雷达（市场调研）、建筑师（框架/角色/长期控制文件）、写手（写作）、审计员（检查）、修订者（修改） | page_fact | 作者转述 | **P0** | ⚠️ 雷达/建筑师/写手/审计/修订证实；但 README 另含规划师/编排师/观察者/反射器/归一化器，共 10 角色（F-033/E-1） |
| F-021 | 雷达扫描市场和平台读者喜好，可不用 | page_fact | 页面事实 | P1 | ✅ 雷达可插拔、可跳过（F-033） |
| F-022 | 审计员从 37 个维度检查（角色记忆、物资连续性、伏笔回收、大纲偏离、叙事节奏、情感弧线） | page_fact | 作者转述 | **P0** | ⚠️ README 为 **33 维**（连续性审计员），见 F-037/E-2 |
| F-023 | 修订者负责修改；修一次查一次，修不好人工介入 | page_fact | 页面事实 | P1 | ✅ "关键问题自动修复，其他标记给人工审核" |
| F-024 | 记忆管理三层：①结构化状态文件（JSON，含当前状态/伏笔/章节摘要，每次校验）②Markdown 投影（给人看、可改）③SQLite 时序记忆库（本地全文检索，一百多章时从中找事实和伏笔喂给写手） | page_fact | 页面事实 | P1 | ✅ 与 README 完全对应（F-035/F-038） |
| F-025 | 项目设置里可看到内置 Skill 和 Prompt，是系统核心框架 | page_fact | 页面事实 | P1 | ✅ README 创作规则体系 + skills/ 目录 |
| F-026 | 通知渠道：加通讯软件挂机写，写完叫醒；守护进程模式保护流程不打断 | page_fact | 页面事实 | P1 | ✅ 通知推送（Telegram/飞书/企业微信/Webhook）+ `inkos up` 守护（F-042） |
| F-027 | 文风分析：输入喜欢的小说风格段落，自动读取风格特点套用到小说 | page_fact | 页面事实 | P1 | ✅ `inkos style analyze` / `style import`（F-043） |
| F-028 | 安装：把提示词发给 Agent 自动启动安装；需在"模型配置"加 AI 大模型；建议官方平台（第三方中转站需能自动读模型列表） | page_fact | 页面事实 + 作者建议 | P1 | ✅ npm 全局安装 `npm i -g @actalk/inkos` + 模型配置必须（F-031/F-044）；"官方平台更稳"为作者建议 |

## C. 核验补充事实（F-029~F-048，GitHub 官方一手来源）

| 编号 | 事实陈述 | 类型 | 信源层级 | P 级 | 核验结论 |
|---|---|---|---|---|---|
| F-029 | 仓库 `Narcooo/inkos` 存在，公开，默认分支 master | page_fact | 官方API | P1 | ✅ |
| F-030 | 官方描述："Autonomous novel writing AI Agent — agents write, audit, and revise novels with human review gates" | page_fact | 官方API | P1 | ✅ |
| F-031 | 主语言 TypeScript；建仓 2026-03-12；forks 1,043；open_issues 123 | page_fact | 官方API | P1 | ✅ 核验日 2026-10-10 |
| F-032 | 许可证为 **AGPL-3.0**（GNU Affero GPL v3.0，2026-04-10 切换） | page_fact | 官方API | P1 | ✅ 文章称"开源"未提 License，须补充 AGPL 属性 |
| F-033 | 作用域含 10 个 Agent 角色：雷达/规划师/编排师/建筑师/写手/观察者/反射器/归一化器/连续性审计员/修订者；雷达可插拔 | page_fact | 官方文档 | P1 | ✅ 见 E-1（文章"五个"是缺省/简化口径） |
| F-034 | 已发布为 OpenClaw Skill（clawhub.ai/narcooo/inkos），`clawhub install inkos` 安装；npm 包名 `@actalk/inkos` | page_fact | 官方文档 | P1 | ✅ |
| F-035 | 每本书维护 7 个"真相文件"：current_state（世界状态）、particle_ledger（资源账本）、pending_hooks（未闭合伏笔）、chapter_summaries（章节摘要）、subplot_board（支线进度板）、emotional_arcs（情感弧线）、character_matrix（角色交互矩阵） | page_fact | 官方文档 | P1 | ✅ 与文章 F-024 三层记忆一致 |
| F-036 | 对话式建书：通过自然语言对话逐步构思设定，草稿就绪后一键创建；`inkos book create --brief my-ideas.md` 传入脑洞/世界观/人设 | page_fact | 官方文档 | P1 | ✅ 与 F-011/F-015 对应 |
| F-037 | 连续性审计员从 **33 维度**检查每一章草稿（角色记忆、物资连续性、伏笔回收、大纲偏离、叙事节奏、情感弧线） | page_fact | 官方文档 | P1 | ✅ 见 E-2（文章"37 维"无出处） |
| F-038 | SQLite 时序记忆数据库（story/memory.db）在 Node 22+ 自动启用，按相关性检索历史事实/伏笔/章节摘要，避免上下文膨胀 | page_fact | 官方文档 | P1 | ✅ 对应文章 F-024 |
| F-039 | 安装命令：`npm i -g @actalk/inkos`；配置 `inkos config set-global --provider <openai|anthropic|custom> --base-url <url> --api-key <key> --model <model>`，配置存 `~/.inkos/.env` | page_fact | 官方文档 | P1 | ✅ |
| F-040 | 支持 `--lang en` 英文写作；TUI（`inkos tui`）、Studio、OpenClaw 共享同一交互内核（`inkos interact --json`） | page_fact | 官方文档 | P1 | ✅ |
| F-041 | 去 AI 味：写手 agent 内置词汇疲劳词表/禁用句式/文风指纹注入；`revise --mode anti-detect` 对已有章节反检测改写 | page_fact | 官方文档 | P1 | ✅ 对应 F-018 |
| F-042 | 守护进程 `inkos up` 启动后台循环自动写章；通知推送支持 Telegram/飞书/企业微信/Webhook（HMAC-SHA256 签名 + 事件过滤） | page_fact | 官方文档 | P1 | ✅ 对应 F-026 |
| F-043 | 文风仿写：`inkos style analyze`（句长分布/词频/节奏指纹）+ `inkos style import` 注入指定书 | page_fact | 官方文档 | P1 | ✅ 对应 F-027 |
| F-044 | 支持续写已有作品（`inkos import chapters`，逆向工程 7 真相文件）与同人创作（`inkos fanfic init --from --mode canon/au/ooc/cp`） | page_fact | 官方文档 | P1 | ✅ 对应 F-008 |
| F-045 | 多模型路由：`inkos config set-model <agent> <model> --provider <p>` 按 Agent 分配不同模型，未配自动回退全局 | page_fact | 官方文档 | P1 | ✅ |
| F-046 | 星标核验：核验日（2026-10-10）GitHub API `stargazers_count` = **5,595**、watchers = 5,595 | page_fact | 官方API | **P0** | ⚠️ 文章"10K"为发布时点自宣或口径，核验日量级不符（5.6K < 10K）见 E-1 |
| F-047 | 厂商站台核验：GitHub README 无 Kimi/火山等厂商官方"站台"声明；仅有社区加群入口；文章"厂商站台广告"无可核验出处 | page_fact | 官方文档 | **P0** | ⚠️ 见 E-3 |
| F-048 | 文章称"审计员督促回炉重新设定"，对应 README "审计不通过自动进入修订→再审计循环，直到关键问题清零" | page_fact | 官方文档 | P1 | ✅ |