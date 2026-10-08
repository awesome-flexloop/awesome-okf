---
type: reference
title: ScholarClaw 源码事实清单
tags: [scholarclaw, academic-search, skill, facts]
sources:
  - id: scholarclaw-vendor
    resource: vendor/netease-youdao/ScholarClaw/
    title: ScholarClaw 源码（vendor 子模块，基线 commit 97bdb5e）
---

# ScholarClaw 源码事实清单（R 阶段）

> 信源：`vendor/netease-youdao/ScholarClaw/`（基线 commit `97bdb5e4a763d4f98d4603f5be876587c0871e0f`，最后提交 2026-04-03）。本清单仅陈述源码与文档中可直接核验的事实，编号前缀 F-sc-。

## A. 服务端配置（server/config.ts）

### F-sc-001 配置接口与默认值
`ScholarClawConfig` 接口含 5 个字段：`serverUrl`、`apiKey`、`timeout`、`maxRetries`、`debug`；`defaultConfig` 取值为 serverUrl=`https://scholarclaw.youdao.com`、apiKey=`''`、timeout=`30000`、maxRetries=`3`、debug=`false`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`ScholarClawConfig`、`defaultConfig`）

### F-sc-002 配置文件路径
`getConfigFilePath()` 返回 `~/.scholarclaw/config.json`（即 `$HOME/.scholarclaw/config.json`）。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`getConfigFilePath`）

### F-sc-003 配置合并优先级
`createConfig(overrides?, openclawConfig?)` 的合并链为：默认值 ← 配置文件（`~/.scholarclaw/config.json`）← OpenClaw 配置 ← 环境变量 ← 显式 overrides，后者覆盖前者。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`createConfig`）

### F-sc-004 配置校验规则
`validateConfig` 执行三条校验：serverUrl 必填；serverUrl 必须是合法 URL；timeout 小于 1000 时输出警告。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`validateConfig`）

### F-sc-005 搜索引擎常量
`SEARCH_ENGINES` 数组共 9 项：`ARXIV`、`PUBMED`、`GOOGLE`、`KUAKE`、`BOCHA`、`CACHE`、`NIPS`、`THECVF`、`MLR_PRESS`；其中不含 `openalex`（与 README 引擎表不一致，见存疑节）。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`SEARCH_ENGINES`）

### F-sc-006 搜索模式与排序常量
`SEARCH_MODES` 为 `simple`、`ai`；`SORT_OPTIONS` 为 `relevance`、`date`、`citation_count`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`SEARCH_MODES`、`SORT_OPTIONS`）

### F-sc-007 任务状态常量
`BLOG_STATUSES` 与 `BENCHMARK_STATUSES` 均为 `pending`、`running`、`completed`、`failed`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/config.ts`（`BLOG_STATUSES`、`BENCHMARK_STATUSES`）

## B. 服务入口与 HTTP 路由（server/index.ts）

### F-sc-008 客户端类与默认实例
`server/index.ts` 导出 `ScholarClawClient` 类与默认实例 `scholarClawClient`；类内方法均通过统一请求方法发出 HTTP 调用（`submitBlog` 除外，见 F-sc-015）。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`ScholarClawClient`、`scholarClawClient`）

### F-sc-009 健康检查（简易）
`health()` 发送 `GET /health`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`health`）

### F-sc-010 健康检查（详细）
`healthDetailed()` 发送 `GET /search/health`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`healthDetailed`）

### F-sc-011 搜索路由与默认参数
`search()` 发送 `GET /search`，默认参数：engine=`bocha`、limit=`100`、page=`1`、page_size=`10`、mode=`simple`、sort_by=`relevance`、with_citations=`true`、return_all=`false`；`freshness` 参数标记 `@deprecated` 并保留向后兼容映射（day→week）。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`search`）

### F-sc-012 学术搜索与查询分析
`scholarSearch()` 发送 `POST /scholar/search`；`analyzeQuery()` 发送 `POST /scholar/analyze`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`scholarSearch`、`analyzeQuery`）

### F-sc-013 引用统计与引用列表
`getCitationStats()` 发送 `GET /citations/stats`；`getCitations()` 发送 `GET /citations`，默认 page_size=`20`、sort_by=`citation_count`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`getCitationStats`、`getCitations`）

### F-sc-014 OpenAlex 相关路由
`getOpenAlexCitedBy()` 发送 `GET /openalex/cited_by`；`findAndCitedBy()` 发送 `GET /openalex/find_and_cited_by`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`getOpenAlexCitedBy`、`findAndCitedBy`）

### F-sc-015 博客提交
`submitBlog()` 发送 `POST /api/blog/submit`，请求体使用 `URLSearchParams` 表单编码；该方法是唯一不走统一 `request()` 请求通道的方法，不设置 JSON Content-Type。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`submitBlog`）

### F-sc-016 博客任务查询路由
`getBlogTask()` 发送 `GET /api/blog/task/{id}`；`getBlogResult()` 发送 `GET /api/blog/result/{id}`；`listBlogTasks()` 发送 `GET /api/blog/tasks`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`getBlogTask`、`getBlogResult`、`listBlogTasks`）

### F-sc-017 基准测试提交
`submitBenchmark()` 发送 `POST /api/benchmark/submit`，默认参数：model_name=`deepseek-v3.1-chat-250922`、use_llm=`true`、enrich=`true`、max_citations=`200`、max_papers=`100`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`submitBenchmark`）

### F-sc-018 基准测试查询路由
`getBenchmarkResult()` 发送 `GET /api/benchmark/result/{arxivId}`，超时时间 60000ms；`getBenchmarkTask()` 发送 `GET /api/benchmark/task/{taskId}`；`listBenchmarkTasks()` 发送 `GET /api/benchmark/completed`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`getBenchmarkResult`、`getBenchmarkTask`、`listBenchmarkTasks`）

### F-sc-019 推荐路由
`getRecommendedPapers()` 发送 `GET /api/recommend/papers`，默认 limit=`12`；`getRecommendedBlogs()` 发送 `GET /api/recommend/blogs`，默认返回 10 条；`getPaperRepos()` 发送 `GET /api/recommend/paper/{id}/detail`，默认 min_stars=`5`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`getRecommendedPapers`、`getRecommendedBlogs`、`getPaperRepos`）

### F-sc-020 错误类型与认证错误判定
`ScholarClawError` 为自定义错误类；`isAuthError` 以 HTTP 状态码 401/403/429 或中英文关键词正则判定认证类错误。
- 证据：`vendor/netease-youdao/ScholarClaw/server/index.ts`（`ScholarClawError`、`isAuthError`）

## C. 类型定义（server/types.ts）

### F-sc-021 分页类型
`PaginationParams` 定义分页入参；`PaginatedResponse<T>` 泛型含 `results`、`total`、`page`、`page_size`、`total_pages`、`has_next`、`has_prev` 字段。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`PaginationParams`、`PaginatedResponse`）

### F-sc-022 搜索请求与结果类型
`SearchRequest` 中 `q` 必填、`freshness` 标记 `@deprecated`；`SearchResult` 含 18 个字段；`ScholarClawResponse` 为 AI 模式响应（mode=`'ai'` 时含 `report` 字段）。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`SearchRequest`、`SearchResult`、`ScholarClawResponse`）

### F-sc-023 学术搜索类型族
`ScholarSearchRequest`（含 query/messages/caller_id/max_results/search_engine/enable_citation_expansion/enable_rerank）、`QueryAnalysis`（含 core_question/keyword_queries/semantic_queries/required_criteria/nice_to_have_criteria/time_range/search_engine）、`ScholarSearchResponse`（含 query/results/summary/analysis/usage/total_results）三接口齐备。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`ScholarSearchRequest`、`QueryAnalysis`、`ScholarSearchResponse`）

### F-sc-024 引用类型
`CitationStats` 与 `CitationItem` 定义引用统计与引用条目结构。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`CitationStats`、`CitationItem`）

### F-sc-025 OpenAlex 类型族
`OpenAlexCitedByRequest`、`OpenAlexFindAndCitedByRequest`、`OpenAlexWork`、`OpenAlexFindAndCitedByResponse` 定义 OpenAlex 请求与响应结构。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`OpenAlex*`）

### F-sc-026 博客类型族
`BlogSubmitRequest` 定义博客提交入参；`BlogTask` 同时含数字主键 `id:number` 与字符串 `task_id` 等字段；`BlogResult` 在 `BlogTask` 基础上增加 `markdown_content`、`blog_content`。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`BlogSubmitRequest`、`BlogTask`、`BlogResult`）

### F-sc-027 基准测试类型族
`BenchmarkSubmitRequest`、`BenchmarkTask`、`BenchmarkResult`（含 statistics/all_results/benchmark_intro 字段）定义基准测试三类结构。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`BenchmarkSubmitRequest`、`BenchmarkTask`、`BenchmarkResult`）

### F-sc-028 推荐与健康类型
`RecommendedPaper`、`GitHubRepo`、`RecommendedBlog` 定义推荐三类结构；`HealthCheckResponse`、`DetailedHealthCheckResponse` 定义两级健康检查响应。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`（`RecommendedPaper`、`GitHubRepo`、`RecommendedBlog`、`HealthCheckResponse`、`DetailedHealthCheckResponse`）

## D. Shell 脚本（scripts/ 与根目录）

### F-sc-029 脚本文件计数
`scripts/` 目录下实际存在 16 个 `.sh` 文件（1 个公共库 `common.sh` + 15 个功能脚本）；仓库根目录另有 `package.sh`、`install.sh` 两个脚本。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/`（Glob 计数）、`vendor/netease-youdao/ScholarClaw/package.sh`、`install.sh`

### F-sc-030 公共库 common.sh
`common.sh` 提供 `init_config` 初始化、`get_api_key`/`get_server_url`（取值优先级：环境变量 > 配置文件 > 默认值）、curl 统一调用模式（`-s -w "\n%{http_code}"`）、`handle_http_error` 错误处理；检测到 `jq` 时用 `jq .` 美化输出。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/common.sh`

### F-sc-031 search.sh
通用搜索脚本：自实现 URL 编码函数，调用 `/search` 接口，参数含 query、engine、limit、page、mode、sort 等；输出 HTTP 状态码与 JSON 响应。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/search.sh`

### F-sc-032 scholar.sh
学术搜索脚本：默认走 `POST /scholar/search`；`--analyze-only` 参数切换为 `POST /scholar/analyze`；curl 设置 `--max-time 60`。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/scholar.sh`

### F-sc-033 citations.sh 与 citations_stats.sh
`citations.sh` 查询 `/citations` 引用列表（支持分页与排序参数）；`citations_stats.sh` 查询 `/citations/stats` 引用统计。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/citations.sh`、`citations_stats.sh`

### F-sc-034 openalex_cited.sh 与 openalex_find.sh
两脚本分别调用 `/openalex/cited_by` 与 `/openalex/find_and_cited_by`；均使用 `jq -sRr @uri` 进行 URL 编码。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/openalex_cited.sh`、`openalex_find.sh`

### F-sc-035 blog_submit.sh
博客提交脚本：以 multipart 表单（curl `-F` 参数）向 `/api/blog/submit` 提交，输出任务 ID 等响应字段。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/blog_submit.sh`

### F-sc-036 blog_status.sh 与 blog_result.sh
`blog_status.sh` 查询 `/api/blog/task/{id}` 任务状态；`blog_result.sh` 查询 `/api/blog/result/{id}` 获取结果内容。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/blog_status.sh`、`blog_result.sh`

### F-sc-037 blog.sh 同步封装
`blog.sh` 串行封装「提交→轮询状态→取结果」流程：轮询间隔 `POLL_INTERVAL=5` 秒、默认总超时 `DEFAULT_TIMEOUT=600` 秒；状态匹配分支含 `completed|success`、`failed|error`、`pending|running|processing|queued`。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/blog.sh`（`POLL_INTERVAL`、`DEFAULT_TIMEOUT`、状态 case 分支）

### F-sc-038 benchmark_chat.sh
基准对话脚本：默认超时 `DEFAULT_TIMEOUT=120`；`-s` 参数切换为 SSE 模式（curl `-N` 加 `Accept: text/event-stream` 头）；history 参数默认 `[]`。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/benchmark_chat.sh`（`DEFAULT_TIMEOUT`、SSE 分支、history 默认值）

### F-sc-039 recommend_papers.sh、recommend_blogs.sh、paper_repos.sh
三脚本分别调用 `/api/recommend/papers`、`/api/recommend/blogs`、`/api/recommend/paper/{id}/detail` 推荐接口。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/recommend_papers.sh`、`recommend_blogs.sh`、`paper_repos.sh`

### F-sc-040 health.sh
健康检查脚本：curl 设置 `--max-time 10`，默认请求 `/health`；`-v` 参数追加请求 `/search/health` 详细健康检查。
- 证据：`vendor/netease-youdao/ScholarClaw/scripts/health.sh`

### F-sc-041 package.sh 打包脚本
`package.sh` 构建 `dist/` 目录内容并生成 tar.gz、zip 归档及对应 sha256 校验文件。
- 证据：`vendor/netease-youdao/ScholarClaw/package.sh`

### F-sc-042 install.sh 安装脚本
`install.sh` 将 skill 安装至 `~/.scholarclaw` 目录，生成 `scholarclaw.env`、写入 `aliases.sh` 的 `sc-*` 命令别名，并分发 `scholarclaw` 快速启动脚本。
- 证据：`vendor/netease-youdao/ScholarClaw/install.sh`

## E. SKILL.md 能力定义与调用契约

### F-sc-043 SKILL.md 元数据
SKILL.md frontmatter：`name: scholarclaw`、`version: 1.4.1`、`official: false`。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（frontmatter）

### F-sc-044 触发条件
SKILL.md 声明：学术场景（论文检索、文献调研、学术问答等）下应使用本 skill 替代 web-search。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（触发条件节）

### F-sc-045 响应时间期望
SKILL.md 给出分场景的响应时间期望表（区分简易搜索、AI 模式、博客生成等场景的耗时预期）。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（响应时间节）

### F-sc-046 SSE 事件处理契约
SSE 流中仅提取 `final_response` 与 `response_chunk` 事件；`session_start`、`tool_call_*` 事件被忽略。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（SSE 节）

### F-sc-047 博客异步三步法
博客生成按「提交→轮询任务状态→获取结果」三步执行；SKILL.md 约定轮询间隔 10–15 秒、最多轮询 40 次。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（博客流程节）

### F-sc-048 重试策略
HTTP 503/504 按 2s、4s、8s 退避重试，最多 3 次；HTTP 400/404 不重试。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（重试策略节）

### F-sc-049 能力清单
SKILL.md 能力表列出 7 项能力。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（能力表）

### F-sc-050 配置优先级声明
SKILL.md 声明配置取值优先级：环境变量 > OpenClaw 配置 > 配置文件 > 默认值。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（配置节）

### F-sc-051 依赖声明
Dependencies 节声明：`curl` 必需、`jq` 可选。
- 证据：`vendor/netease-youdao/ScholarClaw/SKILL.md`（Dependencies 节）

## F. 示例、依赖与构建

### F-sc-052 示例文件清单
`examples/` 目录含 4 个示例文档：`basic-search.md`、`scholar-search.md`、`sota-chat.md`、`blog-generation.md`。
- 证据：`vendor/netease-youdao/ScholarClaw/examples/`（Glob 计数）

### F-sc-053 basic-search.md 示例
演示通用搜索命令调用方式与响应 JSON 形状。
- 证据：`vendor/netease-youdao/ScholarClaw/examples/basic-search.md`

### F-sc-054 scholar-search.md 示例
演示学术搜索（scholar.sh）命令用法，含查询分析模式的调用示例与响应结构。
- 证据：`vendor/netease-youdao/ScholarClaw/examples/scholar-search.md`

### F-sc-055 sota-chat.md 示例
演示 SOTA 对话（SSE 流式）场景的命令与事件序列。
- 证据：`vendor/netease-youdao/ScholarClaw/examples/sota-chat.md`

### F-sc-056 blog-generation.md 示例
演示博客生成的异步提交流程、轮询与结果获取的命令序列。
- 证据：`vendor/netease-youdao/ScholarClaw/examples/blog-generation.md`

### F-sc-057 package.json 基础事实
`package.json`：version=`1.4.1`；main=`server/index.ts`；engines 要求 node>=`16.0.0`；dependencies 为空；devDependencies 含 `@types/node ^20`、`typescript ^5`。
- 证据：`vendor/netease-youdao/ScholarClaw/package.json`

### F-sc-058 npm scripts 别名
`package.json` 定义 14 个 npm scripts 别名，对应各 shell 脚本功能。
- 证据：`vendor/netease-youdao/ScholarClaw/package.json`（scripts 字段）

### F-sc-059 lobsterai 元数据块
`package.json` 含 `lobsterai` 块：skillType=`api`、requiresAuth=`false`、14 个 supportedCommands、defaultServerUrl 及环境变量声明。
- 证据：`vendor/netease-youdao/ScholarClaw/package.json`（lobsterai 字段）

### F-sc-060 tsconfig 编译配置
`tsconfig.json`：target=`ES2020`、module=`ESNext`、strict=`true`、rootDir=`./server`、outDir=`./dist`。
- 证据：`vendor/netease-youdao/ScholarClaw/tsconfig.json`

### F-sc-061 README 文档结构
README.md 含功能介绍、引擎表（9 引擎）、API 参考表、环境变量表、Script Reference 表等章节。
- 证据：`vendor/netease-youdao/ScholarClaw/README.md`

## G. 存疑与差异（源码间不一致，仅登记不裁决）

### F-sc-062 引擎清单差异
README.md 引擎表列出 9 个引擎且含 `openalex`、不含 `cache`；而 `config.ts` 的 `SEARCH_ENGINES` 含 `CACHE`、不含 `openalex`（OpenAlex 功能实际由 `/openalex/*` 路由承载，见 F-sc-014）。两处清单不一致。
- 证据：`vendor/netease-youdao/ScholarClaw/README.md`（引擎表）、`server/config.ts`（`SEARCH_ENGINES`）

### F-sc-063 博客状态取值差异
`types.ts`/`config.ts` 的状态枚举为 `pending/running/completed/failed`；而 `blog.sh` 的状态匹配分支与 SKILL.md 状态示例中出现 `processing`、`queued`、`success` 取值。状态取值集合在不同文件中不一致。
- 证据：`vendor/netease-youdao/ScholarClaw/server/types.ts`、`server/config.ts`（`BLOG_STATUSES`）、`scripts/blog.sh`、`SKILL.md`

### F-sc-064 supportedCommands 与脚本集差异
`package.json` 的 14 个 supportedCommands 不含 `blog.sh` 同步封装脚本；而 `install.sh` 生成的 `sc-blog` 别名指向 `blog.sh`。
- 证据：`vendor/netease-youdao/ScholarClaw/package.json`（supportedCommands）、`install.sh`（sc-blog 别名）
