---
okf_version: "0.2"
type: bundle
title: "Firecrawl：把整个互联网变成 AI 数据库的网页上下文 API"
description: "开源项目 Firecrawl 技术综述（非一手实测教程）——Search/Scrape/Interact 等七端点、Agent 与 /extract、spark-1 弃用→spark-2、九 SDK/CLI/MCP 接入、开源 vs 云能力分界与 AGPL 边界（两轮 26 簇核验 20✅/5⚠️/2❌）"
tags: [firecrawl, web-scraping, web-crawler, ai-agent, mcp, llm-data, structured-output, agpl, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-09-16T22:35:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T22:35:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w
  - id: github-repo
    url: https://github.com/firecrawl/firecrawl
  - id: github-api
    url: https://api.github.com/repos/firecrawl/firecrawl
  - id: official-readme
    url: https://raw.githubusercontent.com/firecrawl/firecrawl/main/README.md
  - id: official-home
    url: https://www.firecrawl.dev/
  - id: official-alternatives
    url: https://www.firecrawl.dev/alternatives
  - id: official-docs-agent
    url: https://docs.firecrawl.dev/features/agent
  - id: spark-launch-blog
    url: https://www.firecrawl.dev/blog/introducing-spark-1
  - id: official-about
    url: https://www.firecrawl.dev/about
---

# Firecrawl：把整个互联网变成 AI 数据库的网页上下文 API

> **类型**：技术综述/开源项目盘点（**非一手实测操作教程，无 examples/**）——博文代码片段逐字来自官方 README，作者未提供实测过程、版本锁定与运行输出。
> **信源**：微信公众号「开源软件社」推介文（2026-09-01）→ 2026-09-16 两轮官方源交叉核验（GitHub REST/commits API、main 分支 README、npm/PyPI、firecrawl.dev 官网/文档/pricing、SEC Form D）。
> **核验结论**：两轮 26 个 P0/P1 声明簇 **20 ✅ / 5 ⚠️ / 2 ❌**，两处 ❌ 均为非核心细节（失实的"最近提交日期"、查无出处的"数百万页面"样本限定），核心声明全部成立（`status: stable`）。

> ⚠️ **厂商自述数据提示**：本包引用的 **96% 成功率、P95 3,387ms、"便宜 60%"** 均为 Firecrawl 官方自述/自建基准数字，无第三方独立复测；引用时必须连同口径（数据集、测量日期、发布时点）一并使用，详见 [concepts/00 §4](concepts/00-project-and-endpoints.md) 与 [references/verification.md](references/verification.md)。

## 本文概要

[Firecrawl](https://github.com/firecrawl/firecrawl) 是一个 TypeScript 编写、AGPL-3.0 许可、2024-04 创建于 GitHub 的开源**网页上下文 API**：以七个端点（Search、Scrape、Interact、Crawl、Map、Batch Scrape、Agent）覆盖「找到网页 → 拿到内容 → 操作页面」全链路，把重度 JS 页面也转为干净 Markdown 与结构化 JSON 供 AI Agent 直接消费；配套九语言 SDK、独立 CLI、MCP 服务端与 Skills 生态，并提供 firecrawl.dev 托管版与自托管路径。GitHub Star 从博文口径的 171,711（对应约 8/28–8/31）增长至核验时 **181,040**（2026-09-16）。

## 阅读路径（concepts/）

| 文档 | 主题 |
|------|------|
| [00-project-and-endpoints.md](concepts/00-project-and-endpoints.md) | **事实层**：定位、仓库事实卡（含两处博文勘误）、七端点能力地图与链路图、96%/3.4s 基准口径、团队与公司 |
| [01-agent-data-workflow.md](concepts/01-agent-data-workflow.md) | **机制层**：Agent 与 /extract 的真实关系（软弃用）、trace/snapshots 溯源、Pydantic 结构化、spark-1 全系弃用→spark-2/effort、Actions、媒体解析 |
| [02-access-license-boundaries.md](concepts/02-access-license-boundaries.md) | **生态/边界层**：九 SDK/CLI/MCP 仓库归属、官方集成与免费额度、开源 vs 云能力分界、AGPL-3.0/MIT、自托管栈、robots.txt 合规、四类用户 |

## ⚠️ 阅读前必知的勘误与口径

1. **「最近提交 2026-08-24」失实（❌）**：commits API 实证 08-20~31 共 94 个提交、博文发布当天（09-01）至少 5 个，仓库高频活跃（09-16 最新 #4645）（F-008/F-049）。
2. **P95「跨数百万页面」查无出处（❌）**：3.4s 数字属实（官方 3,387ms），但样本是自建 **1,000-URL 基准**（scrape-content-dataset-v1，2026-01-13 运行），非"数百万页面"；**96% 也是该基准上的成功率**（同基准 Puppeteer 79%、cURL 75%），不是全网覆盖率（F-006/F-007/F-050/F-051）。
3. **spark-1 已整体过时**：spark-1-mini/pro **均已 deprecated，请求统一路由 spark-2**（官方 Agent 文档）；博文"默认 mini"与官方 2026-01 发布文一致，但 README legacy 表写"pro default"——官方页面自相矛盾，两说都已过时；现在用 effort(low/medium/high) 调推理档位（F-021/F-038/F-052）。
4. **Agent 来源机制要精确**：Agent 标准响应不带 sources 字段，来源经 trace 的 snapshots/tool_call/live view 获取；响应体内显式 sources 目前只有 /extract 的 `showSources=true`；/extract 是"建议迁移"而非已下线（F-018/F-053）。
5. **Star 动态数字带时点**：171,711 ≈ 2026-08-28~31；核验现值 181,040（2026-09-16）。"17 万开发者用脚投票"为博文修辞，Star 是点赞数非开发者数（F-005/F-049）。
6. **仓库归属细节**：MCP 包名 `firecrawl-mcp` 但仓库是 firecrawl/firecrawl-mcp-server（firecrawl-mcp 路径 404）；CLI 在独立仓库 firecrawl/cli；增强代理/轮换/Actions/Agent 为云端专属（F-055/F-060）。
7. 三创始人经 README 示例与官网 About 双重证实：Caleb Peffer（CEO）、Eric Ciarla（CGO）、Nicolas Silberstein Camara（CTO）；公司法定主体是 **SideGuide Technologies, Inc. d/b/a Firecrawl**（F-054/F-061）。

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 主体 | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)；SideGuide Technologies, Inc. d/b/a Firecrawl（YC S22，旧金山；Mendable 为前序产品名） |
| 创建 / 主语言 / 许可 | 2024-04-15 / TypeScript / 主仓 AGPL-3.0（SDK 与部分 UI 为 MIT，根许可证文件名 LICENSE） |
| Star / Fork | **181,040 / 9,753**（2026-09-16 GitHub API 快照；博文口径 171,711 ≈ 8 月底） |
| 七端点 | Search · Scrape · Interact · Crawl · Map · Batch Scrape · Agent |
| API | `https://api.firecrawl.dev/v2/`，`fc-` 前缀 key；异步任务 SDK 自动轮询；另有 keyless 兜底 |
| 模型现状 | **默认 spark-2**；spark-1-mini/pro 已弃用（兼容路由 spark-2）；effort low/medium/high 调推理预算（与 model 互斥） |
| 接入 | 9 语言 SDK（firecrawl-py 4.43.0 等）· firecrawl-cli（独立仓库 firecrawl/cli）· firecrawl-mcp（仓库 firecrawl-mcp-server）· Skills Catalog |
| 免费档 | 1,000 credits/月（约 500 search 或 1,000 页）；Agent 5 次免费/天；Playground 免代码试用 |
| 合规 | 默认遵守 robots.txt；绕过开关 ignoreRobotsTxt 为 Enterprise 专属；合规责任在使用者 |

## 已知边界

- **非一手实测教程**：本文为项目综述，代码为官方 README 示例（v2 SDK 形态），不含版本锁定实测、运行输出与踩坑记录；无 examples/。
- **数字时效**：Star/版本/免费额度/功能集均为 2026-09-16 快照，`stale_after: 2026-12-31`，到期前复核 Star 量级、spark 模型换代、credits 口径与开源/云端差异表变动。
- **厂商口径**：覆盖率/延迟/成本类数字均来自官方自述材料（96% 与 3,387ms 基于厂商自建千 URL 基准），未独立复测；本包不做无信源的同业排名（官方自举对照为 Apify、ScrapingBee）。
- **开源自托管现实**：Agent/Actions/Browser sandbox/增强代理/仪表盘为云端专属；自托管需自备 OpenAI 兼容 API 或 Ollama、另部署 Fire-engine，并运维 PostgreSQL/Redis/RabbitMQ/Playwright 栈。
- **许可使用**：AGPL-3.0 网络开源义务可能影响闭源 SaaS 改造，商用前对照 LICENSE（详见 [concepts/02 §5](concepts/02-access-license-boundaries.md)）。

## 信源与可信度

- 博文事实清单（F-001~F-063，双份登记）：[references/article-source.md](references/article-source.md)
- P0 核验报告与勘误四张清单（含第一轮误判修订记录）：[references/verification.md](references/verification.md)
- 信源距离：第三方编译推介 → 已升级为 GitHub API/commits API + 官方 README + 官网一手页面 + SEC EDGAR 多源交叉核验；两处 ❌ 已在正文落实正确值。

## 主题关联

- [wigolo](../wigolo/index.md)：本地优先、核心工具零 API Key 的 Web 情报层（与 Firecrawl 云端/托管路线互补）
- [browseract](../browseract/index.md)：浏览器自动化 Agent（操作型 vs Firecrawl 的取数型）
- [agent-platform-notes](../agent-platform-notes/index.md)：Agent 平台与工具散篇聚合入口
- [mattpocock-skills](../mattpocock-skills/index.md)：同由微信博文转化的 Agent Skills 生态综述

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
