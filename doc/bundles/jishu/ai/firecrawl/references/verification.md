---
okf_version: "0.2"
type: Reference
title: "Firecrawl 博文 P0 权威核验报告"
description: "两轮 26 项 P0/P1 声明簇核验：20✅/5⚠️/2❌，含勘误四张清单（日期版本/成效溯源/口径对照/引文逐字）与第一轮误判修订记录"
tags: [firecrawl, verification, p0-check, fact-check, errata]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-09-16T22:15:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w
  - id: github-api
    url: https://api.github.com/repos/firecrawl/firecrawl
  - id: github-commits
    url: https://api.github.com/repos/firecrawl/firecrawl/commits
  - id: official-readme
    url: https://raw.githubusercontent.com/firecrawl/firecrawl/main/README.md
  - id: official-home
    url: https://www.firecrawl.dev/
  - id: official-alternatives
    url: https://www.firecrawl.dev/alternatives
  - id: official-docs-agent
    url: https://docs.firecrawl.dev/features/agent
  - id: official-v25-blog
    url: https://www.firecrawl.dev/blog/introducing-firecrawl-v2-5
  - id: spark-launch-blog
    url: https://www.firecrawl.dev/blog/introducing-spark-1
  - id: official-about
    url: https://www.firecrawl.dev/about
  - id: official-pricing
    url: https://www.firecrawl.dev/pricing
  - id: sec-form-d
    url: https://www.sec.gov/Archives/edgar/data/2072161/000207216126000001/primary_doc.xml
---

# P0 权威核验报告

> 核验时间：2026-09-16（两轮独立核验：第一轮 GitHub API + README 19 项；第二轮两路独立子代理深核 26 簇，GitHub 仓库线 + 官网/公司线）。
> 博文信源距离：第三方开源推介号（开源软件社）的**编译性项目介绍**——非厂商账号、非一手实测，事实几乎全部转译自官方 GitHub README 与仓库元数据；其中 96%/3.4s/60% 等数字源头为**厂商自述材料**。

## 核验总览

| 轮次 | 方法 | 结果 |
|------|------|------|
| 第一轮 | GitHub REST API + main 分支 README + v2.5 发布文 | 19 项：17✅ / 1❌ / 其余⚠️ |
| 第二轮 | commits API + npm/PyPI registry + 官网首页/docs/pricing/alternatives + SEC EDGAR | 修订第一轮 1 项误判，新增实证勘误 1 项 |
| **合计（26 个声明簇）** | — | **✅ 20 / ⚠️ 5 / ❌ 2** |

**总体评估**：博文事实框架准确——七端点、九 SDK、安装命令、许可证、定位引语、创始人姓名、客户端集成均与官方材料一致。两处 ❌ 都是**非核心细节**（一个失实日期、一个查无出处的样本限定语），文章核心声明（Firecrawl 是 17 万 Star 的开源 web context API、能干什么、怎么接入）全部成立。故 bundle 为 **stable**，下列勘误已在 concepts 正文逐条落实。

## 勘误四张清单

### ① 日期/版本表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 「最近一次提交就在 2026 年 8 月 24 日」（F-008，正文出现两次） | commits API 实证：08-20~08-31 共 **94 个提交**、08-31 当天有提交、**2026-09-01 当天至少 5 个**（如 #4490 "Spark 2 threads" 23:37Z）；核验当日最新为 2026-09-16 #4645（F-049） | ❌ **失实**：发文（09-01）时仓库保持高频提交，"最近提交停在 08-24"不成立。正文改呈现可验证的提交频率 |
| Star 171,711「时间拨回 2026 年 8 月」（F-005） | star-history 曲线：08-01≈158.3k、08-24≈169.9k、09-01≈173.9k；171,711 对应约 **8/28–8/31**；2026-09-16 API 实测 **181,040**（F-049） | ⚠️ 数字真实但"8 月"口径偏宽（8 月初约 15.8 万）；正文标注对应时点与现值 |
| 「默认的 spark-1-mini……spark-1-pro」（F-021） | 三方口径：① 官方 2026-01-14 发布文确写 "**Spark 1 Mini (Default)**"、"Mini is 60% cheaper"——与博文一致；② README 现行「Model Selection (Legacy)」表写 pro (default)——官方页面自相矛盾；③ docs/features/agent 现行口径：**spark-1 全系 deprecated，名字仅作兼容别名、请求路由 spark-2**，spark-2 现为默认（F-038/F-052） | ⚠️ **第一轮曾判博文 ❌，第二轮修订为 ⚠️**：博文符合其转述时点的官方发布文，但"mini/pro 二选一"框架整体已过时；正文以 spark-2 现状为准并记录口径冲突 |
| 主仓库 TypeScript、AGPL-3.0（F-008） | API：language=TypeScript、license.spdx_id=AGPL-3.0（F-035） | ✅ |
| 仓库 2024 年创建（背景） | created_at=2024-04-15（F-035）；2022 年以 YC S22 项目启动（F-054） | ✅ |
| 包名/安装命令 5 条 + CLI 命令（F-028/F-029） | PyPI firecrawl-py 4.43.0、npm firecrawl 4.40.0、gem/dotnet/composer 名逐字一致；`npx -y firecrawl-cli@latest init --all --browser` 逐字一致（F-060） | ✅ 命令本身无误（仓库归属勘误见清单③） |
| Python SDK 示例形态（F-028） | 与当前 v2 SDK 一致（4.43.0）；旧 v1 `FirecrawlApp().scrape_url()` 已废弃（F-060） | ✅（引用时标注 v2，避免旧教程混用） |

### ② 成效数字溯源表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 「覆盖 96% 的网页，包括 JS 重度页面」（F-006，3 次） | 官网首页逐字："96% coverage on our **1,000-URL firecrawl/scrape-content-dataset-v1** benchmark, run **Jan 13, 2026**"；同基准 Puppeteer 79%、cURL 75%（F-050）。v2.5 发布文（2025-10-30）为出处链上游（F-037） | ⚠️ **厂商自述基准**：是自建千 URL 数据集上的成功率，不是"96% 的网页"；正文保留数字但呈现完整口径，index 顶部提示块标注 |
| 「P95 延迟 3.4 秒，跨数百万页面实测」（F-007） | 官网首页逐字："**P95 latency of 3,387 ms** on the same 1,000-URL benchmark"（F-051）。3.4s≈3,387ms 约数成立；**"数百万页面"查无任何官方出处**——"5B+ requests served" 是服务总量非测试样本 | ❌ 数字✅但样本依据失实：正文采用官方"1,000-URL 基准、3,387ms、2026-01-13"完整表述，删除"数百万页面" |
| spark-1-mini「便宜 60%」（F-021） | 出自官方 2026-01-14 发布文逐字 "60% cheaper"（F-038）；但全系已 deprecated（F-052） | ⚠️ 厂商自述历史报价，数字有出处；正文标注发布时点与弃用现状 |
| 「17 万开发者用脚投票」（F-034 引申） | Star 是仓库点赞数而非开发者数；181,040 star / 9,753 fork（F-035/F-049） | ➖ 作者修辞，正文不沿用"开发者数"等同 |
| 「批处理数千个 URL」（F-016） | README 原文 "Scrape thousands of URLs asynchronously"（F-036） | ✅ 厂商能力承诺，有 README 出处 |

### ③ 口径对照表

| 博文口径（F） | 官方口径 | 结论 |
|--------------|---------|------|
| 「MCP 配置加 firecrawl-mcp 服务端」（F-030） | npm **包名**确为 firecrawl-mcp（3.24.0）；但**仓库**是 [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)（firecrawl/firecrawl-mcp 路径 404；mendableai 旧名为重定向）（F-060） | ⚠️ 包名✅、仓库名需按官方全称 |
| 「CLI 一条命令」（F-029） | 命令逐字属实；npm 包 firecrawl-cli（1.23.3，bin 名 firecrawl）归属**独立仓库 firecrawl/cli**（约 631 stars），不在主仓库（F-060） | ⚠️ 正文补充归属，避免误在主仓库找 CLI 源码 |
| Search「返回的不是十条链接」（F-011） | README 有 "full page content from results"，但**没有"不是十条链接"的对比原话**（F-036） | ⚠️ 引述方演绎，正文转述为能力描述、不加引号 |
| Agent「返回结果附来源链接」（F-018） | Agent 标准响应体**无** sources/citations 字段；来源经 trace artifacts（snapshots）、tool_call 结果、live view 获取；显式 sources 仅 /extract 的 `showSources=true`（F-053） | ⚠️ 可溯源✅但"随结果附链接"措辞不精确，正文按机制分层表述 |
| 「脏活累活零配置内置：轮换代理……」（F-024） | README 承诺逐字在（"no proxy headaches, just clean data"）；但官方开源 vs 云对比表中 **Enhanced proxies、Proxy rotations 为云端专属**，自托管需自行解决代理基础设施（F-055） | ⚠️ 开源读者需注意：该承诺的完整版对应托管服务 |
| 「云端含额外功能，自己部署搞定代理」（F-032） | 官方对比表：**Agent、Browser sandbox、Actions、Enhanced proxies、Proxy rotations、Dashboard、Enterprise 仅云端有**；开源版含 Scrape/Crawl/Map/Search/Batch/Extract；自托管 LLM 抽取需自备 OpenAI 兼容 API/Ollama，Fire-engine 另部署（F-055） | ✅ 博文提示准确，正文补全官方完整清单 |
| 「PDF、DOCX 内嵌直接解析」（F-022） | 官方带 **web-hosted（网页托管）**限定；完整支持 PDF/DOCX/DOC/ODT/RTF/XLSX/XLS/HTML → layout-aware Markdown；PDF 1 credit/页（F-059） | ✅ 能力属实，正文补限定词/格式/计费 |
| 三位创始人（F-020） | README 示例 ✅；About 页独立证实并给职务：Caleb Peffer CEO、Eric Ciarla CGO、Nicolas Silberstein Camara CTO（F-061） | ✅ 双重信源 |
| 公司背景（正文未详述） | 法定主体 **SideGuide Technologies, Inc. d/b/a Firecrawl**（特拉华，SF；Mendable 为前序产品名）；YC S22；2025-08 A 轮 $14.5M（Nexus 领投）；About 页 $16.2M；SEC 2026-09-14 Form D 已售优先股 $82.06M（F-054） | ✅ 核验补充（博文未提公司主体，无冲突） |

### ④ 引文逐字/命令逐字核对表

| 博文引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| "The context API to search, scrape, and interact with the web at scale"（F-004） | 逐字命中 GitHub repo **description** 字段（带 🔥）；README H1 为 "The **API**…"，"context API" 在第二句（F-036） | ✅ 引语准确，出处是 repo About 而非 README 标题 |
| "no proxy headaches, just clean data"（F-024） | README Why Firecrawl 节逐字（F-036） | ✅ |
| "更快、更可靠，不需要提前知道 URL"（F-018） | README 逐字 "faster, more reliable, and doesn't require you to know the URLs upfront"（F-036） | ✅ |
| 九种 SDK 语言清单（F-027） | docs/llms.txt 索引正好 9 个：Python/Node/Go/Java/Ruby/Rust/.NET/PHP/Elixir（F-060） | ✅ |
| 「默认尊重 robots.txt」（F-033） | README 逐字 "By default, Firecrawl respects robots.txt directives."；绕过开关 ignoreRobotsTxt 为 Enterprise 专属（F-056） | ✅ |
| Claude Code / Antigravity / OpenCode 配合（F-025） | 三处官方 quickstart 均 HTTP 200；Claude Code 为官方插件（`claude plugin install firecrawl@claude-plugins-official`，托管 MCP mcp.firecrawl.dev/v2/mcp-oauth）（F-057） | ✅ |
| README 创始人示例三人（F-020） | README 示例 JSON 逐字：Eric Ciarla / Nicolas Camara / Caleb Peffer，role 均 Co-founder（F-040） | ✅ |
| 代码示例 `app.scrape(..., formats=["markdown"])`、`app.agent(prompt=...)`、key 前缀 `fc-`（F-028） | 主 README 与 apps/python-sdk README 逐字一致（F-036/F-060） | ✅ |

## 第一轮误判修订记录（V 阶段自我纠偏）

| 项 | 第一轮结论 | 第二轮证据 | 终判 |
|----|-----------|-----------|------|
| F-021/F-038 默认模型 | ❌ 博文"默认 mini"与官方相反（据 README legacy 表 pro default） | 官方 2026-01-14 发布文逐字 "Spark 1 Mini (Default)"，博文与发布文一致；矛盾存在于**官方两页之间**；且 spark-1 全系已弃用→spark-2 | ⚠️ 口径冲突 + 时效过期（非博文硬错），正文呈现三方口径 |
| F-008 提交日期 | ⚠️ "无法逐日回溯" | commits API 给出逐日证据：09-01 当天 5+ 提交，"08-24 为最近提交"被证伪 | ❌ 升级为实证勘误 |

## 核验方法与局限

1. **方法**：① GitHub REST API 取不可伪造仓库元数据（创建时间/Star/语言/许可/pushed_at）；② commits API 逐日核对提交活跃度；③ raw README（main，940 行）逐字比对端点/引文/命令；④ npm/PyPI registry 核对包名版本；⑤ firecrawl.dev 首页/pricing/alternatives/docs 核对成效数字口径与产品现状；⑥ SEC EDGAR Form D 核对公司主体与融资。
2. **局限**：① 未实际注册账号调用云端 API（命令/端点以官方文档与 README 为准）；② 1,000-URL 厂商基准未独立复测（已按厂商自述标注，不引为独立结论）；③ Star 为实时动态值，所有引用均带 2026-09-16 时点；④ 官网文档存在新旧页不一致（/features/models 旧表残留），已采信 Agent 页现行弃用声明并在正文提示。
3. **复核安排**：`stale_after: 2026-12-31` 前复核：Star 量级、spark-2 之后是否再换代、免费额度与 credits 口径、SEC Form D 后续是否披露轮次/估值、开源/云端功能差异表变动。
