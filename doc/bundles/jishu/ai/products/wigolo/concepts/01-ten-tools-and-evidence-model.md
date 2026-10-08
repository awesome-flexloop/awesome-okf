---
okf_version: "0.2"
type: Concept
title: "十工具矩阵与证据模型"
description: "wigolo 的 10 个 MCP 工具、18 个搜索引擎适配器、6 免 Key+3 需 LLM 分层、字节级来源定位、可解释评分与诚实输出机制"
tags: [wigolo, mcp-tools, metasearch, evidence, reranking, llm]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T21:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
  - id: official-cli
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/cli.md
---

# 十工具矩阵与证据模型

> 机制原理层（How）：工具划分、免 Key 边界、证据返回结构。全部条目可溯源至 F-040~F-045。

## 1. 十个工具全景

README Tools 表确认的 10 个工具（F-041），与博文所说"一共十个工具"一致（博文正文列举 9 个能力名，是把 `diff` 与 `watch` 合并描述成了"页面变更监控"，F-007）：

| # | 工具 | 职责 | 免 API Key |
|---|------|------|:---:|
| 1 | `search` | 多引擎网络搜索：**18 个直接适配器**、rank fusion、ML 重排序、逐结果可解释评分；query 数组并行扇出、域名/时间范围限定、精确短语、图片结果（F-042） | ✅ |
| 2 | `fetch` | 单页抓取：分层路由从普通 HTTP 自动升级到无头浏览器以应对反爬/SPA；输出干净 Markdown+元数据+链接；支持 PDF、单标题区段、认证会话、页面动作（点击/输入/滚动/截图）（F-041） | ✅ |
| 3 | `crawl` | 多页爬取：BFS / DFS / sitemap / map-only 四种策略；按域名限速、遵守 robots.txt、样板去重（F-041） | ✅ |
| 4 | `extract` | 结构化提取：表格、元数据、JSON-LD、品牌信息、命名 schema（Article/Recipe/Product 等）或任意自定义 JSON Schema（F-041） | ✅ |
| 5 | `cache` | 查询一切已见过的内容：关键词或混合语义检索；另有统计、清理、变更检测（F-041/F-054） | ✅ |
| 6 | `find_similar` | 相似页面：关键词 + 语义 + 实时网络三路融合（F-041） | ✅ |
| 7 | `research` | 深度研究：分解问题 → 并行子查询 → 抓取来源 → 合成带引用报告（或交宿主 LLM 撰写的结构化 brief）（F-041） | ⚠️ 合成需 LLM |
| 8 | `agent` | 自主采集循环：plan → search → fetch → extract → synthesize，带步骤日志、时间预算、可选输出 schema（F-041） | ⚠️ 合成需 LLM |
| 9 | `diff` | 页面对比：自上次访问以来发生了什么变化（F-041） | ✅ |
| 10 | `watch` | 定时复查并把变更投递给 webhook；定时检查仅在 daemon 或 MCP 会话存活期间运行（F-054） | ✅ |

## 2. 免 Key 边界：6 + 3 分层（对博文口径的补正）

博文说"只有 research 和 agent 两个功能才建议配 Key"（F-009）。官方完整口径是（F-040）：

- **完全免 Key 的 6 个**：`search`、`fetch`、`crawl`、`extract`、`cache`、`find_similar`；
- **需要 LLM 合成的 3 处**：`research`、`agent`，以及 `search` 的 `format=answer` 形态；
- 不配置 LLM 时它们不报错，而是返回 **raw brief + evidence（原始证据包）**，交给调用方 Agent 自己组织答案——这正是博文"不配也行，它会返回原始证据让你的 Agent 自己整理"的出处（F-009）。

因此"零费用"的准确口径是：**搜索/抓取/提取/缓存这条核心链路 $0/query（F-045）；长文合成可选地挂接 LLM——挂免费 Gemini Key 或本地 Ollama 仍可做到零支出，挂商用 LLM 则费用发生在 LLM 侧而非 wigolo 侧**（F-050，博文 F-031"字面意义零成本"评价的边界）。

## 3. 证据模型：不只是给链接

wigolo 把每条搜索结果构造成"Agent 可直接使用的证据"。官方 README 给出的响应结构（节录，F-043）：

```jsonc
{
  "results": [{
    "title": "Logical replication - PostgreSQL docs",
    "url": "https://www.postgresql.org/docs/current/logical-replication.html",
    "excerpt": "Logical replication is a method of replicating data objects…",
    "citation_id": "src-1",
    "source_span": { "start": 1042, "end": 1305 },          // 字节级来源定位
    "evidence_score": { "final": 0.86, "semantic": 0.91,
                        "lexical": 0.78, "engine_consensus": 3 }
  }],
  "citations": [{ "id": "src-1", "url": "…" }],
  "freshness_signal": { "published": "2026-05-12", "confidence": "high" }
}
```

三个关键设计：

1. **字节锚定的逐字摘录**：`source_span.start/end` 给出引文在源页面中的字节偏移区间（官方称 byte-exact provenance）。Agent 引用时不是"大概在这一页"，而是"答案在这段文字的第 1042~1305 字节"（F-011/F-043）。
2. **可解释评分**：`evidence_score` 同时给出最终分、语义分、词法分与引擎共识数，Agent 可以自行检视而非只接受一个黑箱排序（F-043）。
3. **弱结果自标 junk**：内置评分器会把弱结果打上 junk 标记（F-043）。

## 4. 诚实输出（Honest Output）

博文把这一条单独拎出（F-013 为作者归纳），官方 README 的对应承诺包括（F-043）：

- 反爬页面读不了时，返回带标签的 **`blocked_by_challenge` 失败**，而不是把挑战页外壳当内容返回（F-012）；
- 陈旧缓存标 stale、失败引擎逐一列出、后端降级与内容截断都在结果中显式上报；
- fetch 分层路由会先尝试普通 HTTP，遇反爬挑战或 SPA 壳自动升级无头浏览器（F-041）。

工程意义：Agent 能据返回状态决定"换源/重试/告知用户"，而不是把乱码或旧数据当作事实继续推理。

## 5. 官方 Benchmark 应如何引用

博文转述的"四工具对比测试"（F-011）确有出处，但它是 **wigolo 官方 README 的自述演示**（F-044，⚠️ 勘误性质）：

- 实验形态：在**单个 Claude Fable 5 会话**内，把同一冷查询同时分发给内置 WebSearch、wigolo、Tavily、Exa，由 Agent 仅凭证据评判；
- 结果：四者收敛到同一答案与同一顶级来源；wigolo 唯一返回字节锚定摘录、评分分解与逐引擎遥测，并把 2 条弱结果自标 junk；
- 官方自注口径："Feature standing as of July 2026"。

**引用纪律**：这是项目方自行设计、在自家 README 发布的演示，不是第三方独立评测，也没有给出样本量与统计方法。可陈述的结论是"官方演示中四者答案一致、wigolo 额外提供了字节级证据"，不可写成"独立测评证明 wigolo 优于 Tavily/Exa"。官方对比表（2026-07 口径）中 wigolo 独占的四项能力是：字节锚定逐字摘录、可解释评分分解、持久本地记忆（离线即时复查）、查询数据留在本机（F-045）。

## 延伸阅读

- 上手命令见 [examples/01 · CLI 搜索与缓存](../examples/01-cli-search-and-cache.md)
- 本地数据如何落地、为什么能离线复查，见 [02 · 本地优先架构](02-local-first-architecture.md)
