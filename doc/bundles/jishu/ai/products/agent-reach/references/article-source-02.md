---
okf_version: "0.2"
type: Reference
title: "Agent Reach 第二篇博文事实清单（架构文摘 2026-10-17）"
description: "微信公众号「架构文摘」《87.7k Stars！给 Agent 装上全网之眼》的 F 编号事实登记（F-073~F-120，48 条），含 2026-10-26 对 v1.6.0 的复核口径"
tags: [agent-reach, article-source, fact-registry, blog-article, second-source]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-26T10:40:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: official-skill
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/agent_reach/skill/SKILL.md
  - id: official-sessions
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/agent_reach/skill/references/sessions.md
  - id: readme-v150
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/v1.5.0/README.md
  - id: install-v150
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/v1.5.0/docs/install.md
---

# 第二篇博文事实清单（article-source-02）

> 本文件是 F 编号事实的**第二批登记**（F-073~F-120，48 条），与 [article-source.md](article-source.md) 的 F-001~F-072（第一批）连续衔接、无跳号。
> 类型：**O**=客观事实，**V**=作者观点/评价，**S**=项目方（厂商）自述。核验：✅ 官方一致 ｜ ⚠️ 口径/时效差异 ｜ ❌ 与官方材料矛盾（详见 [verification-02.md](verification-02.md)）。
> 博文：公众号「架构文摘」《87.7k Stars！给 Agent 装上全网之眼，零 API 费，读遍16个国内外主流自媒体平台》，2026-10-17 09:08 发布，正文约 3,594 字符，无编号小节，含 1 张平台表。
> 第二批同时收录 2026-10-26 对 main 分支（v1.6.0）的复核结果，用于修正首版（v1.5.0 口径）的时效偏差。

## A. 文章元信息（F-073 ~ F-075）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-073 | O | 标题《87.7k Stars！给 Agent 装上全网之眼，零 API 费，读遍16个国内外主流自媒体平台》；公众号「架构文摘」；发布 2026-10-17 09:08；正文约 3,594 字符；无编号小节，结构为"一句话简介 → 三大亮点 → 三个关键设计决策 → 安装与配置 → 团队落地 → 适用场景 → 优缺点与避坑 → 最后说两句" | ✅ |
| F-074 | O | 文末自陈"本人在写稿时未逐条真机复现，具体以官方文档为准"——作者主动声明未实测，信源等级应低于一手实测 | ✅ |
| F-075 | O | 推介项目 Agent Reach，仓库 https://github.com/Panniantong/Agent-Reach（文内出现两次） | ✅ |

## B. 热度与成本口径（F-076 ~ F-079）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-076 | O | "上线半年多"：仓库 `created_at=2026-02-24`，至发文 2026-10-17 约 7 个半月 | ✅ F-105 |
| F-077 | O | "Stars 冲到 87,759"：该数字**低于** 2026-10-08 的实测 93,673，也低于 2026-10-26 的 102,508，非发布日快照 | ❌ F-102/F-107 |
| F-078 | O | "日提交、日维护不断，还登上了 Trendshift 日榜榜首"：README 顶部挂 Trendshift 徽章（repository 24387，"GitHub Trending #1 Repository of the Day"）；最近 push 2026-10-25 | ✅ F-117 |
| F-079 | S | "零 API 费：所有工具开源、API 免费；唯一可能花钱的是服务器代理（约 $1/月），本地电脑不需要" | ⚠️ F-091/F-114/F-115 |

## C. 定位与机制（F-080 ~ F-085）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-080 | S | 一句话简介：Agent Reach 是"给 coding agent 用的能力层"——比具体实现高一层，负责选型、安装、体检、路由，不负责底层读取本身 | ✅ |
| F-081 | O | 安装话术与链接：`帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md` | ✅ |
| F-082 | O | 安装器步骤：装 CLI 工具 → 检查系统基建（Node.js、gh CLI、mcporter）→ 按授权装依赖 → 检测本机还是服务器 → 问要不要装更多渠道 | ⚠️ 属 v1.5.0 口径；v1.6.0 改为 uv 安装 + `agent-reach setup`（F-109） |
| F-083 | O | 装完跑 `agent-reach doctor`，一条命令给出每渠道通不通、当前走哪个后端、坏了怎么修；更新同样一句话，不用重装 | ✅ 命令存在；v1.6.0 起输出改为单个 JSON，人读用 `doctor --text`（F-111） |
| F-084 | S | 每个平台 = 首选 → 备选 → 备选的有序后端列表，逐个真实探测，首个完整可用者当选，坏掉的给出修复处方 | ✅ |
| F-085 | O | 2026 年 6 月 yt-dlp 被 B站风控 412 封死，路由切到 bili-cli，用户零操作 | ✅ F-115 |

## D. 平台矩阵（F-086 ~ F-091）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-086 | S | "支持 16 个平台"（标题与正文均用该数字） | ⚠️ 可由 main@2026-10-08 的 16 个渠道实现复现（F-107），但对应版本的 README 表格只列 13 行；v1.6.0 已收缩为 14（F-108） |
| F-087 | O | 文章平台表实为 **13 行**：网页、YouTube、RSS、GitHub、Twitter/X、B站、Reddit、小红书、LinkedIn、BOSS直聘、V2EX、雪球、小宇宙——与"16 个平台"的表述相差 3 行（缺 Exa 全网搜索、Facebook、Instagram） | ⚠️ 内部口径不一致 |
| F-088 | O | 平台表逐行能力：网页=Jina Reader 读任意网页；YouTube=字幕提取+搜索（yt-dlp）；RSS=feedparser；GitHub=gh CLI 读公开仓库+搜索；Twitter=读单条推文（配置后解锁搜索/时间线/长文）；B站=搜索+详情（bili-cli，字幕需 OpenCLI）；Reddit=匿名接口已封，需 OpenCLI；小红书=需 OpenCLI 会话；LinkedIn=Jina Reader 读公开页；BOSS直聘=CDP 链路体检；V2EX=热门/节点/回复；雪球=行情/搜索/热帖；小宇宙=音频转文字（Whisper） | ✅ 与 v1.5.0 README 表逐行一致（BOSS 行来自渠道实现与 1.6 README） |
| F-089 | S | 装好即用为零配置，需要登录态的"告诉 agent 帮我配 XXX 即可解锁" | ✅ v1.5.0 口径 |
| F-090 | S | Cookie 只存本地 `~/.agent-reach/config.yaml`，文件权限 600，不上传不外传 | ✅ v1.5.0 README 明文（F-115）；v1.6.0 文档未重述 600 |
| F-091 | S | "零 API 费：所有工具开源、API 免费" | ⚠️ v1.6.0 README 明确 YouTube/小宇宙转文字需 Groq 或 OpenAI Key（F-114） |

## E. 安全与边界（F-092 ~ F-096）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-092 | O | "`agent-reach install` 默认只检查环境、不改系统、不写配置（`--dry-run` 可预览全部操作），只有显式 `--system` 才装依赖写 SKILL.md" | ❌ 官方无 `--system` 参数；v1.5.0 为 `install --env=auto [--safe\|--dry-run]`（F-110） |
| F-093 | O | "README 明说：Twitter 只接受用户通过 Cookie-Editor 手工导出的内容" | ⚠️ v1.5.0 README 原文是"**优先使用** Cookie-Editor 导出"，同时提供 OpenCLI 登录态路径；"只接受"是加码表述（F-115） |
| F-094 | O | "Agent Reach 不替用户执行小红书登录，也不读取小红书浏览器 Cookie" | ❌ 前半句成立；后半句与官方相反——OpenCLI 路径"复用浏览器登录态"，v1.6.0 更明确首次会把该站 Cookie 复制一次到专用浏览器（F-113） |
| F-095 | O | "装环境：`pip install agent-reach`（README 特别提醒：不要从 PyPI 装同名包，它不是本项目）" | ❌ 自相矛盾：`pip install agent-reach` 正是从 PyPI 装同名包；官方只允许 GitHub release/archive（F-109/F-110） |
| F-096 | O | 使用方式：直接说"帮我看看这个链接""B站搜一下 AI 教程""全网搜一下 LLM 框架对比"，agent 读了 SKILL.md 后自己知道调什么命令 | ✅ |

## F. 团队落地与评价（F-097 ~ F-101，全部为作者观点）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-097 | V | 团队落地四段：① 统一能力基线（新成员一句安装口令对齐环境）② 登录态集中管控（专用小号 + Cookie-Editor 手工导出、Cookie 本地 600）③ 自动化体检（把 doctor 塞进环境自检脚本/CI 前置）④ 合规红线（先评估数据用途与平台 ToS） | ⚠️ 观点/建议，无官方出处；②的实现方式已被 v1.6.0 自动复制会话取代（见 [概念 04](../concepts/04-team-rollout-and-compliance.md)） |
| F-098 | V | 适用人群三类：用 Claude Code/OpenClaw/Cursor/Windsurf 的开发者；维护"会联网的 agent 环境"的团队；做信息抓取/舆情监测流水线的人 | ⚠️ 观点 |
| F-099 | V | 优点三条：能力层定位聪明；首选+备选多后端解决可持续性；16 平台覆盖广 + 零 API 费 + Cookie 本地 + MIT | ⚠️ 观点；平台数与"零 API 费"见 F-086/F-091 |
| F-100 | V | 不足三条：本质是路由层，上游停更会传导；登录态仍需手动配且有封号风险；README 被赞助商广告占据 | ✅ 赞助商事实成立（F-116），判断属观点 |
| F-101 | V | "合规灰色地带：涉及推特/小红书读取，大陆语境下需自行评估" | ⚠️ 观点，但与项目"只读"边界并列阅读更稳妥（F-118） |

## G. 复核：身份与热度（2026-10-26，F-102 ~ F-105）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-102 | O | GitHub API 2026-10-26：Star **102,508**、Fork **9,086**、open issues 242、贡献者 38、最近 push 2026-10-25、默认分支 main、未归档 | ✅ |
| F-103 | O | 最新 release **v1.6.0**（2026-10-23）；共 **8** 个 release（v1.1.0→v1.6.0），首版 2026-02-25 | ✅ |
| F-104 | O | 仓库描述 "Give your AI agent eyes to see the entire internet…one CLI, zero API fees."；语言 Python；许可 MIT；topics 含 mcp/claude-code/cursor | ✅ |
| F-105 | O | `created_at=2026-02-24T02:10:24Z` | ✅ |

## H. 复核：v1.5.0 → v1.6.0 口径变化（F-106 ~ F-120）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-106 | O | v1.5.0 tag 的 `agent_reach/channels/` 有 15 个 py 文件 = 2 个框架文件 + **13 个渠道模块**（bilibili/exa_search/github/linkedin/reddit/rss/twitter/v2ex/web/xiaohongshu/xiaoyuzhou/xueqiu/youtube） | ✅ |
| F-107 | O | main@2026-10-08（首版核验时点）：20 个 py 文件 = 3 个框架文件 + 17 个实现，其中 mcporter 为 Exa 承载，**16 个对外渠道** | ✅ 首版记录，解释"16"的来源 |
| F-108 | O | main@2026-10-26（v1.6.0）：17 个 py 文件 = 3 个框架文件（`__init__`/`base`/`_opencli_site`）+ **14 个渠道实现**；README 分级为 **默认 5**（bilibili/v2ex/github/youtube/web）、**可选 6**（xiaohongshu/xueqiu/boss/xiaoyuzhou/linkedin/reddit）、**实验 3**（twitter/facebook/instagram）；**RSS 与 Exa 全网搜索已不在列** | ✅ |
| F-109 | O | v1.6.0 安装：`uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip` + `agent-reach setup`；从 1.5 及更早升级有专章；文档明写"PyPI 上叫 agent-reach 的包不是本项目，绝不要从 PyPI 安装" | ✅ |
| F-110 | O | v1.5.0 安装：`pipx install https://github.com/Panniantong/agent-reach/archive/main.zip`（或 `pip install` 同一 GitHub archive URL）；授权参数只有 `--safe`（只检查）与 `--dry-run`（预览）；**全文无 `--system`** | ✅ |
| F-111 | O | v1.6.0 起每条 `agent-reach` 命令输出单个 JSON 对象，读 `ok`/`result`/`error.hint`；人读报告用 `agent-reach doctor --text`，实测单渠道用 `agent-reach check <渠道> --text` | ✅ |
| F-112 | O | v1.6.0 专用浏览器：所有浏览器渠道共用一个配置，优先 CloakBrowser、失败回退本机 Chrome；默认无头不弹窗；闲置 10 分钟自动关闭；同平台并发 2、全局 4，同平台两次搜索间隔 ≥10 秒 | ✅ |
| F-113 | O | v1.6.0 会话复用：首次使用某站时，若 Chrome 已连 OpenCLI 扩展，把**该站 Cookie 复制一次**到专用浏览器；不复制整个浏览器目录、其他站点或密码库，不改动来源浏览器；之后一直复用，`login --import-existing` 可手动重取 | ✅ 直接反驳"不读取浏览器 Cookie"（F-094） |
| F-114 | O | v1.6.0 需密钥的能力：YouTube 转文字、小宇宙播客转文字需 Groq 或 OpenAI Key；Key 由用户本人在终端 `agent-reach configure groq-key` 填写，不发聊天 | ✅ |
| F-115 | O | v1.5.0 README 明载：`~/.agent-reach/config.yaml` 权限 600；代理仅服务器需要（~$1/月）；"yt-dlp 被 B站风控 412 封死（2026-06 实测）"；推荐 Cookie-Editor 导出 | ✅ |
| F-116 | O | main README 赞助商区块列 **6 家**：Bright Data、RapidProxy、BrowserAct、腾讯云 Lighthouse（OpenClaw）、CoreClaw、优刻得星图 AstraFlow（文章只点名 4 家） | ✅ |
| F-117 | O | README 顶部 Trendshift 徽章指向 `trendshift.io/repositories/24387`，alt 文本为 "Trendshift GitHub Trending #1 Repository of the Day" | ✅ |
| F-118 | O | v1.6.0 README 安全声明：只读（不发帖/评论/点赞/私信）；从不替用户登录、不要密码；复用登录建议换小号；专用浏览器只对本机开放；Key 不要发在聊天里 | ✅ |
| F-119 | O | v1.6.0 SKILL 红线：只读；不代登录、不索要或输出密码与 Cookie；普通查询不改依赖、不自动更新；结果含 `meta.update` 时每轮只提醒一次 | ✅ |
| F-120 | O | 文末为公众号引流（关注「架构文摘」、点赞转发推荐），并声明"本号持续更新实用有趣的开源项目" | ✅ |
