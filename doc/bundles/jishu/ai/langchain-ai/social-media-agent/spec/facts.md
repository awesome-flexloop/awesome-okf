---
type: spec
scope: social-media-agent
name: facts
version: "0.1.0"
source: https://github.com/langchain-ai/social-media-agent
description: Social Media Agent 事实清单——从源码与配置文件中提取的可验证事实
---

# Social Media Agent 事实清单

## 项目元信息

F-001: 文件 `LICENSE` 第1-3行，许可证为 MIT License，版权归属 "Copyright (c) 2024 LangChain"。

F-002: 文件 `package.json` 第2-9行，npm 包名为 `example-graph`，版本 `0.0.1`，描述为 "A starter template for creating a LangGraph workflow."，包管理器为 `yarn@1.22.22`，主入口 `my_app/graph.ts`，私有包，`"type": "module"`。

F-003: 文件 `package.json` 第11-36行，定义了 20+ 个 npm scripts，包括 `dev`、`build`（tsc）、`test`（Jest 单元测试，排除 `.int.test.ts`）、`test:int`（集成测试）、`lint`（eslint src）、`format`（prettier）、`start:auth`（OAuth 服务器）、`generate_post`、`cron:create/delete/list`、`langgraph:in_mem:up`（`npx @langchain/langgraph-cli@latest dev --port 54367`）。

F-004: 文件 `package.json` 第37-72行，核心依赖包括：`@langchain/langgraph@^1.4.8`、`@langchain/core@^1.2.3`、`@langchain/anthropic@^1.5.2`、`@langchain/openai@^1.5.5`、`@langchain/google-vertexai-web@^2.2.0`、`@langchain/community@^1.1.29`、`@langchain/langgraph-sdk@1.9.28`、`@arcadeai/arcadejs@^2.4.1`、`@mendable/firecrawl-js@1.10.1`、`@octokit/rest@^22.0.1`、`@slack/web-api@^8.0.0`、`@supabase/supabase-js@2.109.0`、`playwright@^1.62.0`、`sharp@^0.35.3`、`snoowrap@^1.23.0`、`twitter-api-v2@^1.29.0`、`zod@^4.4.3`、`express@^5.2.1`、`passport@^0.7.0`。

F-005: 文件 `pyproject.toml`（根目录）第1-5行，Python 项目名为 `langgraph-slack`，版本 `0.0.1`，要求 Python >= 3.11，构建后端为 hatchling。依赖包括 `fastapi>=0.141.1`、`langchain>=1.3.15`、`langchain-openai>=1.5.0`、`langgraph-sdk>=0.3.15`、`langmem>=0.0.15`、`slack-bolt>=1.30.0`、`langgraph-prebuilt>=1.0.11`。

F-006: 文件 `langgraph.json` 第1-24行，LangGraph 配置：`node_version: "20"`，`env: ".env"`，`dependencies: ["."]`，Docker 镜像发行版为 `bookworm`，Dockerfile 行包含 `RUN npx -y playwright@1.62.0 install --with-deps`。注册了 14 个 graph。

## 注册的 Graph（langgraph.json）

F-007: 文件 `langgraph.json` 第5-18行，注册的 14 个 graph 及其入口：
1. `ingest_data` → `./src/agents/ingest-data/ingest-data-graph.ts:graph`
2. `generate_post` → `./src/agents/generate-post/generate-post-graph.ts:generatePostGraph`
3. `upload_post` → `./src/agents/upload-post/index.ts:uploadPostGraph`
4. `reflection` → `./src/agents/reflection/index.ts:reflectionGraph`
5. `generate_thread` → `./src/agents/generate-thread/index.ts:generateThreadGraph`
6. `curate_data` → `./src/agents/curate-data/index.ts:curateDataGraph`
7. `verify_reddit_post` → `./src/agents/verify-reddit-post/verify-reddit-post-graph.ts:verifyRedditPostGraph`
8. `verify_tweet` → `./src/agents/verify-tweet/verify-tweet-graph.ts:verifyTweetGraph`
9. `supervisor` → `./src/agents/supervisor/supervisor-graph.ts:supervisorGraph`
10. `generate_report` → `./src/agents/generate-report/index.ts:generateReportGraph`
11. `repurposer` → `./src/agents/repurposer/index.ts:repurposerGraph`
12. `curated_post_interrupt` → `./src/agents/curated-post-interrupt/index.ts:curatedPostInterruptGraph`
13. `ingest_repurposed_data` → `./src/agents/ingest-repurposed-data/index.ts:graph`
14. `repurposer_post_interrupt` → `./src/agents/repurposer-post-interrupt/index.ts:repurposerPostInterruptGraph`

## generate_post 图结构

F-008: 文件 `src/agents/generate-post/generate-post-graph.ts` 第185-271行，`generatePostGraph` 由 `StateGraph(GeneratePostAnnotation, GeneratePostConfigurableAnnotation)` 构建，包含 11 个节点：`authSocialsPassthrough`、`verifyLinksSubGraph`、`generatePost`、`condensePost`、`humanNode`、`schedulePost`、`rewritePost`、`generateContentReport`、`findAndGenerateImagesSubGraph`、`updateScheduleDate`、`rewriteWithSplitUrl`。

F-009: 文件 `src/agents/generate-post/generate-post-graph.ts` 第90-106行，`condenseOrHumanConditionalEdge` 函数：先移除 post 中的 URL，若清理后长度 > 280 且 `condenseCount <= 3` 则路由到 `condensePost`；否则若为 text-only 模式则调用 `routeToCuratedInterruptOrContinue`，否则路由到 `findAndGenerateImagesSubGraph`。

F-010: 文件 `src/agents/generate-post/generate-post-graph.ts` 第115-126行，`checkIfUrlsArePreviouslyUsed` 函数：若 `skipUsedUrlsCheck` 配置为 true 则返回 false；否则从 LangGraph store 获取已保存 URL，检查输入 URL 是否存在重复。

F-011: 文件 `src/agents/generate-post/generate-post-graph.ts` 第128-151行，`generateReportOrEndConditionalEdge` 函数：检查 `relevantLinks` 和 `links` 是否已使用，或 `pageContents` 是否为空；若任一条件成立则路由到 `END`，否则路由到 `generateContentReport`。

F-012: 文件 `src/agents/generate-post/generate-post-graph.ts` 第34-60行，`findAndGenerateImagesWithFallback` 函数：调用 `findAndGenerateImagesGraph.invoke`，失败时捕获异常并回退到纯文本模式（返回空对象）。

F-013: 文件 `src/agents/generate-post/generate-post-graph.ts` 第158-183行，`routeToCuratedInterruptOrContinue` 函数：若 `config.configurable.origin === "curate-data"`，则通过 LangGraph SDK Client 创建新 thread 并调用 `curated_post_interrupt` graph，然后返回 `END`；否则返回 `humanNode`。

## generate_post 状态定义

F-014: 文件 `src/agents/generate-post/generate-post-state.ts` 第26-108行，`GeneratePostAnnotation` 状态字段包括：`links`（string[]，默认 []）、`report`（复用 IngestDataAnnotation）、扩展自 `VerifyLinksResultAnnotation.spec`、`post`（string，默认 ""）、`complexPost`（ComplexPost | undefined）、`scheduleDate`（DateType）、`userResponse`（string | undefined）、`next`（联合类型：`"schedulePost" | "rewritePost" | "updateScheduleDate" | "unknownResponse" | "rewriteWithSplitUrl" | typeof END | undefined`）、`image`（`{imageUrl, mimeType} | undefined`）、`condenseCount`（number，默认 0）。

F-015: 文件 `src/agents/generate-post/generate-post-state.ts` 第113-143行，`GeneratePostConfigurableAnnotation` 可配置字段：`POST_TO_LINKEDIN_ORGANIZATION`（boolean）、`TEXT_ONLY_MODE`（boolean，默认 false）、`origin`（string | undefined）、`SKIP_CONTENT_RELEVANCY_CHECK`（boolean）、`SKIP_USED_URLS_CHECK`（boolean）。

## 常量与配置键

F-016: 文件 `src/agents/generate-post/constants.ts` 第3-69行，定义 `ALLOWED_DAYS`（周一至周日）和 `ALLOWED_TIMES`（从 8:00 AM 到 5:00 PM，每 10 分钟一个时间槽，共 55 个）。

F-017: 文件 `src/agents/generate-post/constants.ts` 第71-84行，GitHub 截图配置：`GITHUB_SCREENSHOT_OPTIONS` 裁剪区域为 width 1200、height 1500、x 525、y 350；`GITHUB_BROWSER_CONTEXT_OPTIONS` 视口为 1920×1500。

F-018: 文件 `src/agents/generate-post/constants.ts` 第86-109行，配置键常量：LinkedIn 相关（`LINKEDIN_PERSON_URN`、`LINKEDIN_ORGANIZATION_ID`、`LINKEDIN_ACCESS_TOKEN`、`POST_TO_LINKEDIN_ORGANIZATION`、`LINKEDIN_USER_ID`、`LINKEDIN_MAIN_ACCESS_TOKEN`、`LINKEDIN_MAIN_ORGANIZATION_ID`）、Twitter 相关（`TWITTER_USER_ID`、`TWITTER_TOKEN`、`TWITTER_TOKEN_SECRET`、`INGEST_TWITTER_USERNAME`、`TWITTER_MAIN_USER_TOKEN`、`TWITTER_MAIN_USER_TOKEN_SECRET`）、`TEXT_ONLY_MODE`、`SKIP_CONTENT_RELEVANCY_CHECK`、`SKIP_USED_URLS_CHECK`。

## verify-links 子图

F-019: 文件 `src/agents/verify-links/verify-links-graph.ts` 第16-48行，`routeLinkTypes` 函数根据 `getUrlType(link)` 返回的 URL 类型，通过 `Send` API 并行分发到不同验证节点：`twitter` → `verifyTweetSubGraph`，`youtube` → `verifyYouTubeContent`，`github` → `verifyGitHubContent`，`reddit` → `verifyRedditContent`，`luma` → `verifyLumaEvent`，其他 → `verifyGeneralContent`。

F-020: 文件 `src/agents/verify-links/verify-links-graph.ts` 第50-88行，`verifyLinksGraph` 注册 6 个验证节点，全部通过条件边从 `START` 分发，所有验证节点完成后直接路由到 `END`（fan-out/fan-in 模式）。

## supervisor 图

F-021: 文件 `src/agents/supervisor/supervisor-graph.ts` 第24-60行，`startGenerateReportRuns` 函数从 `curatedData` 中提取四类数据（tweetsGroupedByContent、githubTrendingData、generalContents、redditPosts），为每一项创建一个 `Send("generateReport", ...)`，实现并行的 map-reduce 风格 fan-out。

F-022: 文件 `src/agents/supervisor/supervisor-graph.ts` 第82-108行，`supervisorGraph` 包含 5 个节点：`ingestData`（调用 curateDataGraph）、`generateReport`（调用 generateReportGraph）、`groupReports`、`determinePostType`、`generatePosts`。流程为 START → ingestData → (并行 generateReport) → groupReports → determinePostType → generatePosts → END。

## 平台客户端

F-023: 目录 `src/clients/` 包含以下平台客户端：`twitter/`（client.ts、types.ts、utils.ts、SETUP.md）、`slack/`（client.ts、types.ts、utils.ts）、`reddit/`（client.ts、snoowrap.ts、get-user-less-token.ts、types.ts）、`linkedin.ts`、`auth-server.ts`（Express + Passport OAuth 服务器）、`types.ts`。

## memory-v2 Python 子项目

F-024: 文件 `memory-v2/pyproject.toml` 第1-8行，Poetry 项目名为 `memory-v2`，版本 `0.0.1`，描述 "Memory graph for the Social Media Agent."，作者 Brace Sproul，MIT 许可证，要求 Python >=3.11,<4.0.0。

F-025: 文件 `memory-v2/pyproject.toml` 第10-28行，依赖包括 `langmem>=0.0.5rc5`、`langgraph>=1.0.0`、`langchain-anthropic>=0.3.3`、`langgraph-sdk>=0.3.13`，并包含多个 CVE 修复版本约束（starlette、urllib3、cryptography、langchain-core、h11、aiohttp、langchain-text-splitters）。

F-026: 文件 `memory-v2/memory_v2/graph.py` 第1-91行，定义了一个单节点 reflection graph：使用 `ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)`，通过 `langmem.prompts.looping.create_prompt_optimizer(model, kind="metaprompt")` 创建提示词优化器，从 LangGraph store 的 `("reflection_rules",)` 命名空间读取/写入反思规则。`reflection` 节点接收 `state.user_response`（用户反馈）和 `state.original_post`（原始帖子），生成更新后的规则提示词并存入 store。

## FEATURES.md 记录的特性

F-027: 文件 `FEATURES.md` 第18-31行，"Used URLs" 特性：当 run 到达 `humanNode` 时，`relevantLinks` 和 `links` 状态字段中的所有 URL 会存入 LangGraph store。`verifyLinksSubGraph` 执行后检查这些 URL 是否已在之前的帖子中使用，若任一已存在则路由到 `END` 不生成帖子。可通过 `SKIP_USED_URLS_CHECK` 环境变量或 `skipUsedUrlsCheck` 配置字段跳过。

F-028: 文件 `FEATURES.md` 第54-78行，"Skip Content Verification" 特性：`generate_post` graph 默认验证链接内容是否与 business context 相关，可通过 `SKIP_CONTENT_RELEVANCY_CHECK` 环境变量或 `skipContentRelevancyCheck` 配置字段跳过。

F-029: 文件 `FEATURES.md` 第86-94行，"Exclude URLs" 特性：每个 verify links 子图中都有 `shouldExclude<type>Content` 检查（实现在 `src/agents/should-exclude.ts`），仅当 `USE_LANGCHAIN_PROMPTS` 环境变量为 `true` 时启用 LangChain 专用的 URL 排除逻辑。

## README 记录的架构信息

F-030: 文件 `README.md` 第3行，项目核心功能：接收一个 URL，基于 URL 内容生成 Twitter 和 LinkedIn 帖子，使用 human-in-the-loop (HITL) 流程处理社交媒体平台认证及用户修改/接受/拒绝。

F-031: 文件 `README.md` 第37-43行，基础模式（basic setup）缺少的功能：解析 GitHub/Twitter/YouTube URL 内容、从 Slack 摄取数据或发送更新到 Slack、图片选择与上传。

F-032: 文件 `README.md` 第45-51行，快速入门所需 API：Anthropic API（LLM）、LangSmith（tracing）、FireCrawl API（网页抓取）、Arcade（社交媒体认证与调度）。

F-033: 文件 `README.md` 第154-165行，完整设置所需服务：Anthropic API、Google Vertex AI（YouTube 视频内容）、LangSmith、FireCrawl、Arcade、Twitter Developer Account（上传媒体）、LinkedIn Developer Account、GitHub API、Supabase（图片存储）、Slack Developer Account（可选）。

F-034: 文件 `README.md` 第407-413行，自定义提示词的四个关键部分：`BUSINESS_CONTEXT`（业务上下文）、`TWEET_EXAMPLES`（few-shot 示例）、`POST_STRUCTURE_INSTRUCTIONS`（帖子结构指令）、`POST_CONTENT_RULES`（内容风格规则）。
