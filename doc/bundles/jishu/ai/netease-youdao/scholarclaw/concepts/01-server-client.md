---
type: concept
title: TypeScript 客户端与 HTTP 路由
description: "`ScholarClawClient` 的 20 个方法、9 组 HTTP 路由、统一 request 通道与 submitBlog 例外、类型体系与错误判定。"
tags: [scholarclaw, typescript, http-api, client, routing]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# TypeScript 客户端与 HTTP 路由

`server/index.ts` 导出 `ScholarClawClient` 类与默认实例 `scholarClawClient`（F-sc-008）。它是全部后端 API 的**路由与参数契约的权威参照**——即使你不直接运行它（TS 侧不被构建，见 [/concepts/00-overview.md](/concepts/00-overview.md)），对接后端或核对 shell 脚本行为时都应以它为准。

## 统一 request 通道与唯一例外

类内方法均通过统一请求方法发出 HTTP 调用，JSON 编码；唯一的例外是 `submitBlog()`：它使用 `URLSearchParams` 表单编码，不设置 JSON Content-Type，也不走统一 `request()` 通道（F-sc-008、F-sc-015）。与之对照，shell 侧 `blog_submit.sh` 用的是 curl `-F` multipart 表单（F-sc-035）——同一接口、两套编码，集成时需注意（详见 [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)）。

## 9 组路由与 20 个方法

| 组 | 方法 | 路由与默认参数 |
|----|------|----------------|
| 健康检查 | `health()` | `GET /health`（F-sc-009） |
| 健康检查 | `healthDetailed()` | `GET /search/health`（F-sc-010） |
| 通用搜索 | `search()` | `GET /search`；默认 engine=`bocha`、limit=`100`、page=`1`、page_size=`10`、mode=`simple`、sort_by=`relevance`、with_citations=`true`、return_all=`false`；`freshness` 已标记 `@deprecated` 并保留向后兼容映射（day→week）（F-sc-011） |
| 学术搜索 | `scholarSearch()` | `POST /scholar/search`（F-sc-012） |
| 学术搜索 | `analyzeQuery()` | `POST /scholar/analyze`（F-sc-012） |
| 引用 | `getCitationStats()` | `GET /citations/stats`（F-sc-013） |
| 引用 | `getCitations()` | `GET /citations`；默认 page_size=`20`、sort_by=`citation_count`（F-sc-013） |
| OpenAlex | `getOpenAlexCitedBy()` | `GET /openalex/cited_by`（F-sc-014） |
| OpenAlex | `findAndCitedBy()` | `GET /openalex/find_and_cited_by`（F-sc-014） |
| 博客 | `submitBlog()` | `POST /api/blog/submit`，表单编码（F-sc-015） |
| 博客 | `getBlogTask()` | `GET /api/blog/task/{id}`（F-sc-016） |
| 博客 | `getBlogResult()` | `GET /api/blog/result/{id}`（F-sc-016） |
| 博客 | `listBlogTasks()` | `GET /api/blog/tasks`（F-sc-016） |
| 基准测试 | `submitBenchmark()` | `POST /api/benchmark/submit`；默认 model_name=`deepseek-v3.1-chat-250922`、use_llm=`true`、enrich=`true`、max_citations=`200`、max_papers=`100`（F-sc-017） |
| 基准测试 | `getBenchmarkResult()` | `GET /api/benchmark/result/{arxivId}`，超时 60000ms（F-sc-018） |
| 基准测试 | `getBenchmarkTask()` | `GET /api/benchmark/task/{taskId}`（F-sc-018） |
| 基准测试 | `listBenchmarkTasks()` | `GET /api/benchmark/completed`（F-sc-018） |
| 推荐 | `getRecommendedPapers()` | `GET /api/recommend/papers`，默认 limit=`12`（F-sc-019） |
| 推荐 | `getRecommendedBlogs()` | `GET /api/recommend/blogs`，默认返回 10 条（F-sc-019） |
| 推荐 | `getPaperRepos()` | `GET /api/recommend/paper/{id}/detail`，默认 min_stars=`5`（F-sc-019） |

## 类型体系（server/types.ts）

类型定义按功能族组织，与路由一一对应（F-sc-021~F-sc-028）：

- **分页**：`PaginationParams` 入参；`PaginatedResponse<T>` 泛型含 `results`、`total`、`page`、`page_size`、`total_pages`、`has_next`、`has_prev`（F-sc-021）。
- **通用搜索**：`SearchRequest` 中 `q` 必填、`freshness` 标记 `@deprecated`；`SearchResult` 含 18 个字段；`ScholarClawResponse` 为 AI 模式响应（mode=`'ai'` 时含 `report` 字段）（F-sc-022）。
- **学术搜索**：`ScholarSearchRequest`（含 query/messages/caller_id/max_results/search_engine/enable_citation_expansion/enable_rerank）、`QueryAnalysis`（含 core_question/keyword_queries/semantic_queries/required_criteria/nice_to_have_criteria/time_range/search_engine）、`ScholarSearchResponse`（含 query/results/summary/analysis/usage/total_results）（F-sc-023）。
- **引用 / OpenAlex / 博客 / 基准 / 推荐 / 健康**：`CitationStats` 与 `CitationItem`（F-sc-024）；`OpenAlexCitedByRequest`、`OpenAlexFindAndCitedByRequest`、`OpenAlexWork`、`OpenAlexFindAndCitedByResponse`（F-sc-025）；`BlogSubmitRequest`、`BlogTask`（同时含数字主键 `id:number` 与字符串 `task_id`）、`BlogResult`（增加 `markdown_content`、`blog_content`）（F-sc-026）；`BenchmarkSubmitRequest`、`BenchmarkTask`、`BenchmarkResult`（含 statistics/all_results/benchmark_intro）（F-sc-027）；`RecommendedPaper`、`GitHubRepo`、`RecommendedBlog`、`HealthCheckResponse`、`DetailedHealthCheckResponse`（F-sc-028）。

## 错误处理与认证判定

`ScholarClawError` 为自定义错误类；`isAuthError` 以 HTTP 状态码 401/403/429 或中英文关键词正则判定认证类错误（F-sc-020）。故障排查的实用顺序是：先用健康检查区分网络/服务端问题，再查 apiKey 配置——401/403/429 即指向认证类错误。

## 使用提示

- 直接对接后端 API 时，以本客户端为路由与参数契约的权威参照，以 shell 脚本验证实际可用的最小参数集。
- 该层未经构建验证（`main` 指向 `.ts` 源文件、无构建脚本），引用其类型时把它当"活文档"而非"已发布 SDK"（F-sc-057、F-sc-060）。
- 博客任务状态字段同时存在数字 `id` 与字符串 `task_id`，轮询与取结果时注意 task_id 的取值（F-sc-026）；状态取值集合存在源码间不一致，见 [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)。

## 相关概念

- [/concepts/00-overview.md](/concepts/00-overview.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)
