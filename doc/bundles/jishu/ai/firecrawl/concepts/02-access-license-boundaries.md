---
type: Concept
title: "接入生态与采用边界：九 SDK、开源 vs 云、AGPL 与合规"
description: "九种官方 SDK/CLI/MCP/Skills 接入矩阵、官方集成、免费额度、开源版与云端能力分界、AGPL-3.0/MIT 双许可、自托管栈、robots.txt 合规与四类用户"
tags: [firecrawl, sdk, cli, mcp, agpl, self-hosting, robots-txt, licensing, claude-code]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T22:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w
  - id: official-readme
    url: https://raw.githubusercontent.com/firecrawl/firecrawl/main/README.md
  - id: official-cloud-compare
    url: https://docs.firecrawl.dev/contributing/open-source-or-cloud
  - id: official-pricing
    url: https://www.firecrawl.dev/pricing
---

# 接入生态与采用边界：九 SDK、开源 vs 云、AGPL 与合规

> 生态/边界层：本篇给出接入矩阵、免费额度、开源与云端的能力分界、许可证与自托管现实、合规底线，供技术选型直接对照。

## 1. 九种官方 SDK + 独立 CLI + MCP

Firecrawl 官方维护**正好九种语言 SDK**（与官方 docs/llms.txt 索引逐一对应，F-027/F-060），异步任务统一自动轮询：

| 语言 | 安装 | 2026-09-16 核验 |
|------|------|----------------|
| Python | `pip install firecrawl-py` | PyPI **4.43.0**；v2 API，另有 `AsyncFirecrawl`；旧 v1 的 `FirecrawlApp().scrape_url()` 已废弃 |
| Node.js | `npm install firecrawl` | npm **4.40.0** |
| Go | monorepo `apps/go-sdk` | 主仓库内 |
| Java | jitpack `com.github.firecrawl:firecrawl-java-sdk:2.0` | 独立仓库 |
| Elixir | hex `{:firecrawl, "~> 1.0"}` | 基于 Req/NimbleOptions 的生成客户端 |
| Rust | crates.io `firecrawl = "2"` | 独立仓库 |
| Ruby | `gem install firecrawl-sdk` | 独立仓库 |
| .NET | `dotnet add package firecrawl-sdk` | 独立仓库 |
| PHP | `composer require firecrawl/firecrawl-sdk` | 独立仓库 |

博文列出的 5 条包管理器命令与 Python 示例经逐字核对全部准确，且为当前 v2 SDK 形态（F-028/F-060）：

```python
# 转自官方 README（非作者实测；v2 SDK 形态，F-028）
from firecrawl import Firecrawl

app = Firecrawl(api_key="fc-YOUR_API_KEY")

# 抓取单个 URL，输出干净 Markdown
doc = app.scrape("https://firecrawl.dev", formats=["markdown"])

# 用 Agent 自动收集数据，描述需求即可
result = app.agent(prompt="Find the founders of Stripe")
```

**CLI**：博文命令 `npx -y firecrawl-cli@latest init --all --browser` 逐字属实，装完可在 Agent 中使用，并提供 `firecrawl search / scrape / interact` 命令（F-029）。两处仓库归属需要注意（F-060）：

- npm 包 `firecrawl-cli`（1.23.3，bin 名 firecrawl）归属**独立仓库 [firecrawl/cli](https://github.com/firecrawl/cli)**（约 631 stars），**不在主仓库内**；
- MCP：npm **包名**是 `firecrawl-mcp`（3.24.0），但 GitHub **仓库**是 [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)（约 7.5k stars；`firecrawl/firecrawl-mcp` 这个路径 404；`mendableai/firecrawl-mcp-server` 是改名重定向）（F-030/F-042）。

此外官方还有面向 AI agent 的自助 onboarding 技能（`curl -s https://firecrawl.dev/agent-onboarding/SKILL.md`，F-043）、Skills Catalog（[firecrawl/skills](https://github.com/firecrawl/skills)，`npx skills add firecrawl/skills`，按 CLI/主仓/workflows 三个仓库分流贡献，F-044），以及 Lovable、Zapier、n8n 等平台集成（F-045）。

## 2. Agent 客户端集成：Claude Code、Antigravity、OpenCode 全部官方在册

博文点名的三个客户端均有官方 quickstart 且页面实测可达（F-025/F-057）：

- **Claude Code**：不仅有 quickstart，Firecrawl 还是**官方 Claude 插件**——`claude plugin install firecrawl@claude-plugins-official`；托管 MCP 端点 `https://mcp.firecrawl.dev/v2/mcp-oauth`；
- **Antigravity**（Google）：官方 quickstart「MCP Web Search & Scrape in Antigravity」；
- **OpenCode**：官方 quickstart 存在，CLI 安装注释也列出 "Claude Code, Codex, OpenCode"。

## 3. 免费额度与试用

- 托管版 Free Plan：**1,000 credits/月、$0、无需银行卡**（约合 500 次 search 或 1,000 页 scrape，2 并发、低速率限制）（F-058）；
- Agent 另享 **5 次免费运行/天**（选型指南口径，F-058）；
- SDK/MCP 还支持 **keyless（无密钥）**访问 Search/Scrape/Parse 作为兜底；
- 官方 Playground（firecrawl.dev/playground）免代码直接试用各端点（F-031/F-058）。

## 4. 开源版 vs 云端：能力分界（选型关键）

博文「云端有额外功能、自部署要自己搞定代理基础设施」的提示准确。官方对比表的完整分界（F-055/F-032）：

| 能力 | 开源自托管 | 云端 firecrawl.dev |
|------|:---:|:---:|
| Scrape / Crawl / Map / Search / Batch scrape | ✔ | ✔ |
| Extract（/v2/extract，含 showSources） | ✔ | ✔ |
| JSON mode / LLM-ready formats / Change tracking / SDKs | ✔ | ✔ |
| **Agent（/agent）** | ❌ | ✔（云端专属，含 5 次免费/天） |
| **Browser sandbox / Interact·Actions（页面操作）** | ❌ | ✔ |
| **Enhanced proxies / Proxy rotations（增强代理与轮换）** | ❌ | ✔ |
| **Dashboard / Enterprise features（含 ignoreRobotsTxt）** | ❌ | ✔ |

自托管的另外两个现实成本（F-055/F-063）：

1. **LLM 抽取需自带模型**：自备 OpenAI 兼容 API 或本地 Ollama，否则结构化抽取无引擎；
2. **Fire-engine（高级反爬栈）需另行部署且不含在开源版**，截图与页面动作默认栈不支持；
3. 运维依赖栈为 PostgreSQL（默认队列）、Redis、RabbitMQ、Playwright（可选 FoundationDB）——这些组件自身许可需部署者自行留意。

## 5. 许可证：AGPL-3.0 主仓 + MIT SDK/UI

- 主仓库根目录许可证文件就是普通 **`LICENSE`**（AGPL-3.0 全文，约 35KB；没有 LICENSE.md 之类命名）（F-062）；
- README 原文："This project is primarily licensed under … AGPL-3.0. **The SDKs and some UI components are licensed under the MIT License.**" 实测 MIT 许可证位于 `apps/python-sdk/LICENSE`、`apps/js-sdk/LICENSE`、`apps/elixir-sdk/LICENSE`、`apps/ruby-sdk/LICENSE`、`apps/ui/ingestion-ui/LICENSE`（F-062）；
- 未发现官方在 AGPL 之外另加自托管商用限制——其商业边界实际通过上节的**云端专属能力**实现（F-062）；
- **采用提示**：通过 MIT 许可的 SDK 调用云端 API 无 AGPL 传染性问题；但**修改 AGPL 主仓库源码并以网络服务形式对外提供**（SaaS）会触发 AGPL 的网络开源义务。闭源商用前应对照 LICENSE 与官方对比表评估，必要时走云端/企业版（F-032）。

## 6. 合规底线：robots.txt 与使用者责任

- README 原文："**By default, Firecrawl respects robots.txt directives.** … It is the sole responsibility of end users to respect websites' policies when scraping."（F-033，逐字核实）；
- Crawl 文档参数表：robots.txt 默认遵守，唯一绕过开关 `ignoreRobotsTxt` 默认为 false 且为 **Enterprise 专属**；抓取时同时读取 `FirecrawlAgent` user-agent 与 `*` 规则（F-056）；
- 博文「工具无罪，合规在人心」（F-034 作者观点）与官方责任划分方向一致：抓取前应核对目标站 robots.txt、隐私政策与使用条款。

## 7. 四类适用人群（博文框架，F-026）

| 人群 | 用法要点 | 核验补注 |
|------|---------|---------|
| AI 应用 / Agent 开发者 | Agent/Search/Scrape 作实时网页上下文，MCP + CLI 直连 | Claude Code/Antigravity/OpenCode 官方在册（F-057） |
| 数据 / 研究团队 | Batch Scrape + Map 批量采集、结构化抽取 | 大规模代理轮换/队列在云端最完整（F-055） |
| 产品 / 内容团队 | 竞品监控、价格跟踪、内容聚合，免维护爬虫基础设施 | 直接用托管版，Free Plan 1,000 credits/月（F-058） |
| 个人开发者 / 自托管爱好者 | 自托管 + 贡献代码 | 需接受 Postgres/Redis/RabbitMQ/Playwright 栈与自带 LLM（F-063/F-055） |

官方文档自举的同业对照是 **Apify 与 ScrapingBee**（README 以三者企业特性对比作为 high effort Agent 示例，F-048）；同主题的本地优先替代可参读知识包 [wigolo](../../wigolo/index.md)（免 API Key 的本地 MCP 搜索/抓取层，与 Firecrawl 云端路线互补）。
