---
okf_version: "0.2"
type: Concept
title: "wigolo 是什么：项目身份与发布事实"
description: "wigolo 的定位、作者、许可证、开源时间线、社区热度与 Public Beta 状态（事实层，所有数字带核验时点）"
tags: [wigolo, mcp, local-first, ai-agent, project-profile]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T20:55:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: github-api
    url: https://api.github.com/repos/KnockOutEZ/wigolo
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
---

# wigolo 是什么：项目身份与发布事实

> 事实层（What / When / Who）。本文只陈述可核验事实，观点与评价见作者原文（F-013/F-014/F-031）。

## 一句话定位

wigolo（[github.com/KnockOutEZ/wigolo](https://github.com/KnockOutEZ/wigolo)）是一个**本地优先（local-first）的 AI Agent Web 情报层**：以 MCP Server、REST 服务或嵌入式 SDK 的形态，为 AI Agent 提供搜索、抓取、爬取、结构化提取、缓存、相似查找、深度研究与自主采集共 10 个工具，核心工具不需要任何 API Key（F-004、F-036、F-040、F-041）。

官方仓库自述为：

> "The go-to web for your AI coding agent — local-first search, fetch, crawl & research over MCP. No API keys, no cloud, $0/query. Public beta."（F-036）

它要替代的不是浏览器，而是 Tavily、Exa 这类**按调用计费的云端搜索 API**——Agent 查资料不再为每次搜索付费，重复查询命中本地缓存（F-014 为博文对这一痛点的描述）。

## 身份卡片

| 项目 | 值 | 出处 |
|------|-----|------|
| 仓库 | https://github.com/KnockOutEZ/wigolo | F-003/F-034 |
| 作者 | GitHub 个人账号 **KnockOutEZ**（owner 类型 User）；本人 X：[@yourtowhid](https://x.com/yourtowhid) | F-034/F-053 |
| 主语言 | TypeScript | F-034 |
| 许可证 | **AGPL-3.0**（README 许可证徽章；GitHub API 未自动识别 SPDX，以仓库 LICENSE 为准） | F-006/F-037 |
| 创建时间 | **2026-04-12**（GitHub API `created_at`）——博文"四月份开源"准确 | F-005/F-034 |
| 成熟度 | **Public Beta**，更新频繁（核验前一天 2026-09-15 仍有 push） | F-032/F-035/F-037 |
| npm 包 | [`wigolo`](https://www.npmjs.com/package/wigolo)（CLI/MCP Server）；另有 `wigolo-sdk`（TS）与 `pip install wigolo`（Python） | F-036/F-052 |
| 项目主页 | https://knockoutez.github.io/wigolo/ | F-036 |
| 社区 | Discord 服务器、GitHub Issues/Discussions；赞助渠道（Buy Me a Coffee、赞助商 TestMu AI） | F-053/F-055 |

## 热度数据（带时点阅读）

- 博文 2026-09-15 发布时称「三千多颗 Star」（F-005）。
- 2026-09-16 GitHub API 时点快照：**Star 5,268、Fork 419、Open Issues 59、Watch/订阅 21**（F-035）。
- Star 是持续增长的动态数字，两个数字分别代表各自时点，均不应在引用时省略日期。
- 博文称项目「在 GitHub Trending 上挂了好几天」（F-005）：官方 README 挂载的是第三方趋势榜 **Trendshift** 徽章（仓库编号 [#79424](https://trendshift.io/repositories/79424)）。Trendshift 与 GitHub 官方 Trending 是两个不同产品，"登上 GitHub Trending"无官方材料可证实（F-053，⚠️ 口径勘误见 [verification.md](../references/verification.md)）。

## 解决的问题（博文视角）

博文作者将痛点归纳为两点（F-014，属作者观点层，此处仅转述）：

1. **付费焦虑**：Claude Code、Cursor 等编码 Agent 联网查资料要配 Tavily/Exa 等付费搜索 API，按月累积；
2. **一次性消耗**：多数工具把搜索结果当消耗品，同一网页今天查过明天再问要重新搜索、抓取、读取，重复花钱花时间。

wigolo 用"公共搜索引擎直连适配器 + 本地重排序/嵌入 + 本地持久缓存"回应这两点，机制细节见 [01-十工具与证据模型](01-ten-tools-and-evidence-model.md) 与 [02-本地优先架构](02-local-first-architecture.md)。

## 阅读下一篇

- [01 · 十工具与证据模型](01-ten-tools-and-evidence-model.md)——10 个工具分别做什么、18 引擎适配器、字节级证据与可解释评分
- [02 · 本地优先架构](02-local-first-architecture.md)——隐私边界与 MCP/REST/Docker/SDK 四种部署形态
