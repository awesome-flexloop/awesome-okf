---
type: reference
scope: social-media-agent
name: graphs
version: "0.1.0"
source: https://github.com/langchain-ai/social-media-agent
description: Social Media Agent 图结构参考——14 个 LangGraph 图的注册信息、节点组成与流转逻辑
---

# 图结构参考

本文档详细描述 `langgraph.json` 中注册的 14 个 LangGraph 图的结构。所有图的源码位于 `src/agents/` 目录下。

## 图注册表

来源：`langgraph.json` 第5-18行。

| 图名 | 入口文件 | 导出符号 |
|---|---|---|
| `ingest_data` | `src/agents/ingest-data/ingest-data-graph.ts` | `graph` |
| `generate_post` | `src/agents/generate-post/generate-post-graph.ts` | `generatePostGraph` |
| `upload_post` | `src/agents/upload-post/index.ts` | `uploadPostGraph` |
| `reflection` | `src/agents/reflection/index.ts` | `reflectionGraph` |
| `generate_thread` | `src/agents/generate-thread/index.ts` | `generateThreadGraph` |
| `curate_data` | `src/agents/curate-data/index.ts` | `curateDataGraph` |
| `verify_reddit_post` | `src/agents/verify-reddit-post/verify-reddit-post-graph.ts` | `verifyRedditPostGraph` |
| `verify_tweet` | `src/agents/verify-tweet/verify-tweet-graph.ts` | `verifyTweetGraph` |
| `supervisor` | `src/agents/supervisor/supervisor-graph.ts` | `supervisorGraph` |
| `generate_report` | `src/agents/generate-report/index.ts` | `generateReportGraph` |
| `repurposer` | `src/agents/repurposer/index.ts` | `repurposerGraph` |
| `curated_post_interrupt` | `src/agents/curated-post-interrupt/index.ts` | `curatedPostInterruptGraph` |
| `ingest_repurposed_data` | `src/agents/ingest-repurposed-data/index.ts` | `graph` |
| `repurposer_post_interrupt` | `src/agents/repurposer-post-interrupt/index.ts` | `repurposerPostInterruptGraph` |

## generate_post（核心图）

**文件**：`src/agents/generate-post/generate-post-graph.ts`

### 节点列表

| 节点名 | 实现 | 职责 |
|---|---|---|
| `authSocialsPassthrough` | `nodes/auth-socials.ts` | 透传社交媒体认证信息 |
| `verifyLinksSubGraph` | `verify-links/verify-links-graph.ts` | 子图：并行验证各 URL 内容 |
| `generateContentReport` | `nodes/generate-report/index.ts` | 基于页面内容生成营销报告 |
| `generatePost` | `nodes/generate-post/index.ts` | 生成 Twitter/LinkedIn 帖子文本 |
| `condensePost` | `nodes/condense-post.ts` | 压缩超长帖子（>280 字符） |
| `findAndGenerateImagesSubGraph` | `find-and-generate-images/find-and-generate-images-graph.ts` | 子图：查找或生成配图（含失败回退） |
| `humanNode` | `shared/nodes/generate-post/human-node.ts` | HITL 中断点，等待用户审核 |
| `rewritePost` | `shared/nodes/generate-post/rewrite-post.ts` | 根据用户反馈重写帖子 |
| `rewriteWithSplitUrl` | `nodes/rewrite-with-split-url.ts` | 将 URL 从帖子正文中拆分 |
| `updateScheduleDate` | `shared/nodes/update-scheduled-date.ts` | 从自然语言更新调度日期 |
| `schedulePost` | `shared/nodes/generate-post/schedule-post.ts` | 调度帖子到 Twitter/LinkedIn |

### 边与条件路由

- `START → authSocialsPassthrough → verifyLinksSubGraph`
- `verifyLinksSubGraph → generateReportOrEndConditionalEdge`：
  - URL 已使用或 `pageContents` 为空 → `END`
  - 否则 → `generateContentReport`
- `generateContentReport → routeAfterGeneratingReport`：
  - `state.report` 存在 → `generatePost`
  - 否则 → `END`
- `generatePost → condenseOrHumanConditionalEdge`：
  - 清理 URL 后长度 > 280 且 `condenseCount <= 3` → `condensePost`
  - text-only 模式 → `routeToCuratedInterruptOrContinue`
  - 否则 → `findAndGenerateImagesSubGraph`
- `condensePost → condenseOrHumanConditionalEdge`（循环，最多 3 次）
- `findAndGenerateImagesSubGraph → routeToCuratedInterruptOrContinue`：
  - `origin === "curate-data"` → 通过 SDK 创建 `curated_post_interrupt` 线程 → `END`
  - 否则 → `humanNode`
- `humanNode → rewriteOrEndConditionalEdge`：
  - `state.next` 为 `"rewritePost"` → `rewritePost`
  - `state.next` 为 `"schedulePost"` → `schedulePost`
  - `state.next` 为 `"updateScheduleDate"` → `updateScheduleDate`
  - `state.next` 为 `"rewriteWithSplitUrl"` → `rewriteWithSplitUrl`
  - `state.next` 为 `"unknownResponse"` → `humanNode`
  - `state.next` 未定义 → `END`
- `rewritePost → humanNode`
- `updateScheduleDate → humanNode`
- `rewriteWithSplitUrl → humanNode`
- `schedulePost → END`

### 状态字段

来源：`src/agents/generate-post/generate-post-state.ts`

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `links` | `string[]` | `[]` | 输入 URL 列表 |
| `report` | 复用 IngestDataAnnotation | — | 内容营销报告 |
| `post` | `string` | `""` | 生成的帖子文本 |
| `complexPost` | `ComplexPost \| undefined` | `undefined` | URL 拆分后的复杂帖子 |
| `scheduleDate` | `DateType` | — | 调度日期 |
| `userResponse` | `string \| undefined` | `undefined` | 用户审核反馈 |
| `next` | 联合类型 | `undefined` | 下一节点路由指令 |
| `image` | `{imageUrl, mimeType} \| undefined` | `undefined` | 配图 |
| `condenseCount` | `number` | `0` | 已压缩次数 |

此外通过 `...VerifyLinksResultAnnotation.spec` 扩展了 `pageContents`、`relevantLinks` 等验证结果字段。

### 可配置字段

| 配置键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `postToLinkedInOrganization` | `boolean` | `undefined` | 是否发布到 LinkedIn 组织页 |
| `textOnlyMode` | `boolean` | `false` | 纯文本模式（禁用图片） |
| `origin` | `string` | `undefined` | 调用来源（如 `"curate-data"`） |
| `skipContentRelevancyCheck` | `boolean` | `undefined` | 跳过内容相关性检查 |
| `skipUsedUrlsCheck` | `boolean` | `undefined` | 跳过 URL 去重检查 |

## verify-links（子图）

**文件**：`src/agents/verify-links/verify-links-graph.ts`

### 节点

| 节点名 | 适用 URL 类型 | 实现 |
|---|---|---|
| `verifyYouTubeContent` | YouTube | `shared/nodes/verify-youtube.ts` |
| `verifyGitHubContent` | GitHub | `shared/nodes/verify-github.ts` |
| `verifyTweetSubGraph` | Twitter | `verify-tweet/verify-tweet-graph.ts` |
| `verifyRedditContent` | Reddit | `verify-reddit-post/verify-reddit-post-graph.ts` |
| `verifyLumaEvent` | Luma | `shared/nodes/verify-luma.ts` |
| `verifyGeneralContent` | 其他 | `shared/nodes/verify-general.ts` |

### 路由逻辑

`routeLinkTypes` 函数遍历 `state.links`，对每个链接调用 `getUrlType(link)` 判断类型，通过 `Send` API 创建并行任务。所有验证节点完成后直接路由到 `END`。这是典型的 **scatter-gather（扇出-扇入）** 模式。

## supervisor（编排图）

**文件**：`src/agents/supervisor/supervisor-graph.ts`

### 节点

| 节点名 | 实现 | 职责 |
|---|---|---|
| `ingestData` | 调用 `curateDataGraph` | 从多源拉取并策展内容 |
| `generateReport` | 调用 `generateReportGraph` | 为每项内容生成报告（并行） |
| `groupReports` | `nodes/group-reports.ts` | 聚合所有报告 |
| `determinePostType` | `nodes/determine-post-type.ts` | 决定帖子类型 |
| `generatePosts` | `nodes/generate-posts.ts` | 批量生成帖子 |

### 并行 fan-out

`startGenerateReportRuns` 函数从 `curatedData` 中提取四类数据，为每项创建 `Send("generateReport", ...)`：

- `tweetsGroupedByContent` → 每项传 `{tweetGroup}`
- `githubTrendingData` → 每项传 `{pageContent, relevantLinks}`
- `generalContents` → 每项传 `{pageContent, relevantLinks}`
- `redditPosts` → 每项传 `{pageContent, relevantLinks}`

流程：`START → ingestData → (并行 generateReport) → groupReports → determinePostType → generatePosts → END`。

## memory-v2 reflection（Python 图）

**文件**：`memory-v2/memory_v2/graph.py`

单节点图，使用 `ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)` 和 `langmem` 的 `create_prompt_optimizer(model, kind="metaprompt")`。

### 节点逻辑

`reflection(state, store)` 节点：
1. 从 store 的 `("reflection_rules",)` 命名空间读取当前规则提示词。
2. 接收 `state.user_response`（用户反馈）和 `state.original_post`（原始帖子）。
3. 通过 metaprompt 优化器分析反馈，生成更新后的规则。
4. 将新规则写回 store。

规则更新原则：仅添加用户明确要求的规则，不推断隐式反馈，新规则与旧规则冲突时以新规则为准。

## LangGraph 运行时配置

**文件**：`langgraph.json`

```json
{
  "node_version": "20",
  "env": ".env",
  "dependencies": ["."],
  "image_distro": "bookworm",
  "dockerfile_lines": [
    "RUN npx -y playwright@1.62.0 install --with-deps"
  ]
}
```

- Node.js 20 运行时
- Docker 镜像基于 Debian Bookworm
- 容器内预装 Playwright 浏览器（用于 GitHub 等页面截图）
- 环境变量从 `.env` 文件加载

## 平台客户端

**目录**：`src/clients/`

| 平台 | 文件 | 关键依赖 | 认证方式 |
|---|---|---|---|
| Twitter | `twitter/client.ts` | `twitter-api-v2`、`@arcadeai/arcadejs` | Arcade 或 OAuth 1.0a |
| LinkedIn | `linkedin.ts` | 直接 API 调用 | Arcade 或 OAuth 2.0 |
| Slack | `slack/client.ts` | `@slack/web-api` | Bot Token |
| Reddit | `reddit/client.ts`、`snoowrap.ts` | `snoowrap` | User-less token |
| OAuth 服务器 | `auth-server.ts` | `express`、`passport`、`passport-twitter` | 本地 OAuth 回调 |

## 相关文档

- [总览](/ai/langchain-ai/social-media-agent/concepts/overview)
- [事实清单](/ai/langchain-ai/social-media-agent/spec/facts)
- [深度洞察](/ai/langchain-ai/social-media-agent/spec/insights)
