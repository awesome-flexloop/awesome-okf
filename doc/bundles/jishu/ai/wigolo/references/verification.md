---
okf_version: "0.2"
type: Reference
title: "wigolo 博文 P0 权威核验报告"
description: "对博文 18 项 P0/P1 声明的官方交叉核验：14✅/4⚠️/0❌，含勘误四张清单（日期版本/成效溯源/口径对照/引文逐字）"
tags: [wigolo, verification, p0-check, fact-check, errata]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-09-16T20:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: github-api
    url: https://api.github.com/repos/KnockOutEZ/wigolo
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
  - id: official-installation
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/installation.md
  - id: official-cli
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/cli.md
---

# P0 权威核验报告

> 核验时间：2026-09-16。信源：GitHub REST API（仓库元数据时点快照）、main 分支 README.md、docs/installation.md、docs/cli.md（均为项目一手官方文档）。
> 博文信源距离：第三方开源推介号（GHub开源甄选）转述，其中 Benchmark 段属**厂商自述材料**。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（数字/日期/命令/许可/成效） | 15 | ✅ 11 / ⚠️ 4 / ❌ 0 |
| P1（能力声明/兼容列表） | 3 | ✅ 3 |
| 合计 | 18 | **✅ 14 / ⚠️ 4 / ❌ 0** |

**总体评估**：博文事实准确度高——全部安装命令、端口、镜像名、环境变量、引擎数（18）、工具总数（10）、开源月份、许可证均与官方材料逐字一致。4 项 ⚠️ 全部是**动态时点数、产品口径或参数细节**，无一项构成核心声明造假：项目真实存在、「核心功能零 API Key、$0/query」属实。故 bundle 状态为 **stable**，但下列勘误须在正文落实。

## 勘误四张清单

### ① 日期/版本表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 「四月份开源」（F-005） | GitHub API `created_at=2026-04-12T15:04:11Z`（F-034） | ✅ 一致 |
| Node.js 20+，LTS 已到 22（F-015） | README 徽章与 Quickstart 均要求 Node ≥20（F-037/F-038） | ✅ 一致 |
| Public Beta（F-032） | README status 徽章 `public beta`、官方描述含 "Public beta."（F-036/F-037） | ✅ 一致 |
| AGPL-3.0（F-006） | README license 徽章 AGPL-3.0；GitHub API license.spdx_id=NOASSERTION（平台未自动识别）（F-037） | ✅ 以作者 LICENSE/徽章为准 |

### ② 成效数字溯源表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| Star「三千多颗」（F-005） | 2026-09-16 API 实测 **5268**（F-035）。博文 2026-09-15 发布，"三千多"为发文前后时点口径，Star 为持续增长动态数字 | ⚠️ **时效差异非造假**；正文呈现官方现值 5268（2026-09-16 时点）并标注博文口径 |
| 四工具对比"唯一"返回逐字摘录+字节定位+可解释评分（F-011） | 确出自官方 README Benchmark 段，但实验条件为**单个 Claude Fable 5 会话内的演示**，由项目方自行设计与表述，对比表自注 "Feature standing as of July 2026"（F-044） | ⚠️ **厂商自述，非第三方独立评测**；正文必须标注"官方自述演示"，不得写成独立测评结论 |
| 「零成本/$0」（F-031） | 官方对比表 wigolo=$0/query 且无 API key（F-045）；但 research/agent/answer 三类 LLM 合成功能在不用本地 Ollama 时仍可能产生 LLM 侧费用（F-040） | ✅ 核心工具零费用成立；正文限定口径"核心 6 工具 $0/query，LLM 合成可选" |

### ③ 口径对照表

| 博文声明（F） | 官方口径 | 结论 |
|--------------|---------|------|
| 「GitHub Trending 挂了好几天」（F-005） | README 挂载的是 **Trendshift** 徽章（trendshift.io/repositories/79424，第三方趋势榜），非 GitHub 官方 Trending（F-053） | ⚠️ 两产品名称相近但不同；无法证实"登上 GitHub Trending"，正文仅陈述可验证的 Trendshift 上榜事实 |
| 需要配 Key 的功能是「research 和 agent 两个」（F-009） | 官方明确 6 工具免 key；需 LLM 的是 research、agent **以及 `search format=answer`** 共三处（F-040） | ⚠️→✅ 博文不完整（漏 answer 形态），非错误，正文按官方补正 |
| 支持 7 个 Agent 客户端（F-017） | 官方 `--agents` 目标为 9 个（另有 OpenCode、Antigravity）（F-039） | ✅ 博文为不穷尽列举，正文补全 |
| 「十个工具」（F-007） | 官方 Tools 表确为 10 个；博文正文罗列 9 个能力名（diff 与 watch 被合并描述为"页面变更监控"）（F-041） | ✅ 总数正确 |
| `:full` 标签预装好浏览器引擎（F-023） | 官方文档中 full 是仓库 Dockerfile 的**构建目标**（`docker build --target full`），文档未确认 ghcr 已发布 `:full` 预构建标签（F-047） | ⚠️ 正文呈现官方口径：发布镜像仅确认 slim；full 需自行 build |

### ④ 引文逐字/命令逐字核对表

| 博文引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| `npx wigolo init --agents=claude-code`（F-016） | README 示例 `npx wigolo init --agents=claude-code,cursor` 同构（F-038） | ✅ |
| 约 1.5GB 空间（F-016） | README "~1.5 GB of free disk"（F-038） | ✅ |
| `npx wigolo doctor`（F-018） | README Quickstart 与 cli.md 均有（F-054） | ✅ |
| `npx wigolo search "..." --limit=3`（F-019） | cli.md 中 **headless** 一次性 search 签名为 `--max-results=N`；`--limit` 是 `wigolo shell` 交互模式内的别名（F-051） | ⚠️ 博文跨模式借用参数名；正文两个模式都给出，以官方签名为准 |
| `wigolo serve` / 127.0.0.1:3333（F-020） | cli.md/README 逐字一致（F-049） | ✅ |
| curl `POST /v1/search` + JSON body（F-021） | README curl 示例逐字一致；官方另说明 `POST /v1/{tool}` 覆盖全部 10 工具（F-049） | ✅ |
| OpenAPI 3.1（F-021） | `GET /openapi.json` 为 OpenAPI 3.1 契约（F-049） | ✅ |
| Docker 两条命令（F-022） | installation.md stdio 命令逐字一致；HTTP 形式与 `serve --host`/`WIGOLO_API_TOKEN` 机制兼容，官方另提供 compose 文件（F-046/F-048） | ✅ |
| `WIGOLO_LLM_PROVIDER=gemini` / `GEMINI_API_KEY` / aistudio.google.com/apikey（F-024） | README 逐字一致（F-050） | ✅ |
| Anthropic/OpenAI/Groq/Ollama（F-025） | README 列 anthropic·openai·groq 与 ollama/OpenAI 兼容端点（F-050） | ✅ |
| `blocked_by_challenge`（F-012） | README "you get a labeled `blocked_by_challenge` failure"（F-043） | ✅ |
| `include_domains` / `search_depth: deep`（F-028/F-029） | cli.md 有 `--include-domains`、`--search-depth`（wire 名为下划线）；deep 具体取值集合未在 CLI 参考枚举，以 `wigolo search --help` 为准（F-051/F-042） | ✅ 参数存在；取值现场确认 |

## 博文笔误登记（非事实错误，正文不沿用）

- F-033：结尾段「eighteen个搜索引擎」中英混杂（数字本身 18 正确，与官方一致）
- F-033：仓库链接提示词写作「guthub地址」（正确链接 URL 本身拼写正确）

## 核验方法与局限

1. **方法**：GitHub REST API 获取仓库不可伪造元数据（创建时间/Star/语言/owner 类型）；WebFetch 拉取 main 分支 raw 文档逐字比对命令、参数名与功能表述。
2. **局限**：① 未实际安装运行 wigolo，CLI 行为层（如 `--limit` 是否在 headless 模式作为别名被接受）以官方文档签名为准；② 18 个适配器的具体引擎名单、`search-depth` 枚举值未展开核验（不影响博文结论）；③ 厂商 Benchmark 未复现。
3. **复核安排**：stale_after=2026-12-31 前复核 Star 量级、Beta→GA 状态、`:full` 标签发布情况与 CLI 参数稳定性。
