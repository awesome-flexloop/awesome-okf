---
okf_version: "0.2"
type: Concept
title: "Agent Reach 是什么：项目身份与发布事实"
description: "Agent Reach 的定位、作者、MIT 许可、2026-02 发布时间线、v1.6.0 与 10.2 万 Star（带时点）与增长曲线旁证（事实层）"
tags: [agent-reach, ai-agent, capability-layer, project-profile, cli]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-08T11:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# Agent Reach 是什么：项目身份与发布事实

> 事实层（What / When / Who）。本文只陈述可核验事实；"能力层"设计解读见 [01](01-capability-layer-architecture.md)，作者观点（五条启示）见 [03](03-skill-md-agent-distribution-paradigm.md)。

## 一句话定位

[Agent Reach](https://github.com/Panniantong/Agent-Reach) 是一个用 Python 编写、MIT 许可的 **AI Agent 互联网能力层（capability layer）CLI**：它本身不做抓取，而是替用户**选型、安装、体检、路由** 多个互联网平台渠道的上游工具，让 AI Agent（Claude Code、Cursor、OpenClaw 等）经统一入口读网页、抽字幕、搜社区、查行情（F-005、F-010、F-057）。

渠道数是随版本变动的指标：v1.5.0 tag 为 13 个、main@2026-10-08 为 16 个、**v1.6.0 为 14 个**（5 默认 + 6 可选 + 3 实验，F-106/F-107/F-108）。本文一律采用现行 v1.6.0 口径，历史数字另注。

官方仓库自述为：

> "Give your AI agent eyes to see the entire internet..."（F-057）

博文给出的中文概括是："它不是一个抓取工具，而是一个能力层——替你选型、安装、体检、路由，把'让 AI 读懂全网'这件反复折腾的事，变成一句命令"（F-005）。

## 身份卡片

| 项目 | 值 | 出处 |
|------|-----|------|
| 仓库 | https://github.com/Panniantong/Agent-Reach | F-003/F-055 |
| 作者 | GitHub 个人账号 **Panniantong**（显示名 Pnant），2020-11-04 注册，1,437 followers，38 个公开仓库；owner 类型 User | F-055 |
| 主语言 | Python（617,420 字节为最大语言块），要求 **Python 3.10+** | F-006/F-055/F-059 |
| 许可证 | **MIT** | F-059 |
| 创建时间 | **2026-02-24**（GitHub API `created_at=2026-02-24T02:10:24Z`）——博文"2026 年 2 月首次发布"准确 | F-004/F-055 |
| 最新版本 | **v1.6.0**（2026-10-23 发布）；共 **8 个 release**（v1.1.0→v1.6.0）。v1.5.0「能力层:多后端路由 + 真体检 + OpenCLI」为上一代 | F-103 |
| 维护状态 | 活跃：最近 push 2026-10-25；38 位贡献者 | F-102 |
| 镜像 | GitCode 同步镜像（gitcode.com/Panniantong/Agent-Reach）、README 友情链接 AtomGit | F-070 |
| 安装入口 | 官方 docs/install.md（一句话安装）；v1.6.0 为 `uv tool install <release zip>` + `agent-reach setup`；**官方警告不要从 PyPI 装同名包** | F-081/F-109/F-110 |

## 热度数据（带时点阅读）

- 第一篇博文 2026-10-06 发布时信息卡写 **92,000+ Star、Fork 约 8,000**（F-004）。
- 2026-10-07/08 快照：**Star 93,673、Fork 8,195、36 位贡献者**（F-056）。
- 第二篇博文 2026-10-17 写 **87,759 Star**，但该数字低于 9 天前的 93,673，非发布日快照（F-077，❌）。
- **2026-10-26 快照：Star 102,508、Fork 9,086、open issues 242、38 位贡献者**（F-102）。
- 四个数字分属不同时点，Star 是持续增长的动态数字，引用时不应省略日期；跨文章比较前先看日期先后。
- 增长曲线有第三方旁证：neodrop.ai 收录显示 **2026-06-22 当周项目登 GitHub Trending #2，当时 36,854 stars、单周 +8,233**（F-072）。即项目 2 月底建仓后，热度在 6 月才集中爆发，10 月达 93k——时间线与"发布后约 4 个月破圈"吻合。README 另挂 Trendshift 徽章 #24387（F-057，第三方趋势榜，与 GitHub 官方 Trending 非同一产品）。

> ⚠️ 博文称"这才是它 92k Star 的真正原因：它卖的不是功能，是'不用再操心'"（F-007）。Star 数本身可核验，但"真正原因"是**推介作者的个人归因（V）**，没有投票或用户调研证据，不应读作客观结论。

## 解决的问题（博文视角）

博文把痛点归纳为"**每次都要重新折腾一遍**"（F-008/F-009）：

| 平台 | 门槛（博文列举） |
|------|----------------|
| YouTube | 抽字幕要装 yt-dlp，还要区分自动字幕与手动字幕 |
| Reddit | 匿名接口早被封，官方 API 审批制，只剩登录态 |
| B站 | 通用下载工具被风控拦死（返回 412），要换专门实现 |
| 小红书 | 不登录打不开，登录又涉及凭据 |
| GitHub | 能用，但认证配置一堆坑 |
| 全网搜索 | 好用的要付费，免费的质量不行 |

博文引用 README 的原话说："这些不难实现，但是需要自己折腾配置"（F-009）。Agent Reach 的回应方式不是再写一个抓取器，而是把易变的接入方式收进一层可替换、可体检的路由结构——机制细节见 [01 · 能力层架构](01-capability-layer-architecture.md)。

## 阅读下一篇

- [01 · 能力层架构：有序后端列表与 14 渠道全景](01-capability-layer-architecture.md)——channels/、active_backend、412 故障案例、三级渠道矩阵
- [04 · 团队落地](04-team-rollout-and-compliance.md)——把个人可用变成团队可管：基线、凭据、体检、合规
- [05 · 版本漂移与渠道矩阵](05-version-drift-and-channel-matrix.md)——13/16/14 三代口径与迁移清单
- [02 · doctor 真体检与安全模型](02-doctor-health-and-security-model.md)——missing/broken/timeout、默认只读、凭据 600
- [03 · SKILL.md 与 Agent 分发范式](03-skill-md-agent-distribution-paradigm.md)——给 Agent 的说明书与五条设计启示（观点层）
