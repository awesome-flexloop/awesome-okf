---
okf_version: "0.2"
type: Example
title: "CLI 搜索、并行扇出与本地缓存实战"
description: "wigolo 一次性命令与 shell 两种 CLI 用法、--max-results/--include-domains/--search-depth 参数（含博文 --limit 口径勘误）、数组并行、缓存语义检索"
tags: [wigolo, cli, search, cache, parallel-search, json]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T21:15:00+08:00" }
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

# 示例 01：CLI 搜索、并行扇出与本地缓存

> 本文对应博文"终端直玩"与"四个实用技巧"（F-019、F-027~F-030）。参数名以官方 cli.md 为准（F-051）。

## 1. 一次性搜索（headless）

博文示例（F-019）：

```bash
npx wigolo search "local-first AI agent" --limit=3
```

> ⚠️ **参数名口径勘误**：cli.md 中**一次性（headless）模式**的官方签名是 `--max-results=N`；`--limit` 是 `wigolo shell` 交互模式内的别名（F-051）。为避免不同版本行为差异，脚本中推荐官方 headless 写法：

```bash
# 官方 headless 签名（F-051）
wigolo search "local-first AI agent" --max-results 3

# 机器可读输出：--json 只在 stdout 输出一个 JSON 文档，日志全走 stderr
wigolo search "local-first AI agent" --max-results 3 --json 2>/dev/null | jq '.results[].url'
```

返回内容（F-019/F-043）：不只是链接，还有每篇文章的逐字摘录、来源引擎、`evidence_score` 评分、`source_span` 字节定位，以及**哪些引擎失败了**的清单。同一问题第二次搜索明显更快——响应已进本地缓存（F-019）。

全部 10 个工具都支持 headless 形式，wire 参数名到 CLI 按 1:1 映射为 `--kebab-case`（F-051）。

## 2. 技巧一：数组并行扇出

博文技巧（F-027）：不要只搜一个词，传查询数组让 wigolo 在多个引擎上**同时扇出（fan out）**。官方对 search 的定义明确支持 query array 并行广度（F-042）。MCP/JSON 调用形态：

```jsonc
// search 工具入参（wire 形态，下划线命名）
{ "query": ["local-first software", "MCP search server", "offline web cache AI agent"] }
```

一次 MCP 调用即完成多查询×多引擎的并行检索——这是串行宿主工具循环做不到的（官方 "Built for agents" 的核心论点之一，F-042）。

## 3. 技巧二：深度搜索

重要技术调研提高召回率（博文 F-028）：

```bash
# headless 参数（F-051）
wigolo search "RAG 评测框架 2026" --search-depth deep --max-results 10
```

- 默认是标准深度；`--search-depth` 对应 wire 参数 `search_depth`，博文写作 `search_depth: deep`（F-028）；
- `deep` 的完整取值集合未在 CLI 参考中枚举，执行前可用 `wigolo search --help` 现场确认（verification.md 已登记此局限）。

## 4. 技巧三：锁定官方文档域名

避免 SEO 垃圾页污染结果（博文 F-029，Next.js 示例）：

```bash
# headless（F-051）
wigolo search "app router caching" --include-domains nextjs.org
wigolo search "MCP server config" --include-domains modelcontextprotocol.io,docs.anthropic.com
```

wire 形态即博文的 `include_domains: ["nextjs.org"]`（F-029）。同组的过滤参数还有 `--time-range`（时间范围）与 `--exact-match`（精确短语）（F-051）。

## 5. 技巧四：把缓存当私有知识库

每次搜索/抓取过的页面都会进入本地缓存，之后离线也能查、速度为毫秒级（博文 F-030；官方 F-043）：

```bash
wigolo cache stats                          # 缓存统计
wigolo cache search "向量检索"               # 关键词 + 混合语义检索（F-041）
wigolo cache search "RAG" --json | jq .     # 管道处理
wigolo cache clear --query "临时查询"        # 按需清理（F-054）
```

`cache` 工具支持关键词与 hybrid semantic 两种检索（F-041），语义索引由本地嵌入模型生成——等于给自己构建了一个可语义检索的私有网页知识库（F-030）。`wigolo backfill` 还可为索引机制建立前缓存的旧页面补算向量（F-054）。

## 6. 交互模式 `wigolo shell`

探索性操作不想反复支付进程启动成本时，用常驻 REPL（F-054）：

```bash
wigolo shell
```

```text
wigolo> search "bun test runner" --limit 5 --domains bun.sh
wigolo> fetch https://bun.sh/docs/cli/test --max-chars 4000
wigolo> cache stats
wigolo> .json on        # 切换 NDJSON 输出
wigolo> exit
```

注意 shell 内的别名正是博文用到的 `--limit` / `--domains`（F-051）——这解释了博文参数名的来源：它把交互 shell 的别名用在了 npx headless 示例里。也可以用管道喂脚本：

```bash
printf 'search "bun test runner"\nfetch https://bun.sh/docs/cli/test\n' \
  | wigolo shell --json 2>/dev/null | jq -r '.results[]?.url // .url'
```

## 小结：参数名速查

| 意图 | headless / MCP（脚本推荐） | shell 内别名 |
|------|---------------------------|-------------|
| 结果条数 | `--max-results N` | `--limit N` |
| 域名限定 | `--include-domains a,b` | `--domains a,b` |
| 深度 | `--search-depth deep` | `--search-depth` |
| 多查询并行 | query 数组（wire） | 多次/数组 |

## 延伸阅读

- [示例 02：REST、Docker 与 LLM](02-rest-docker-and-llm.md)
- [概念 01：证据模型（评分与 junk 标记）](../concepts/01-ten-tools-and-evidence-model.md)
