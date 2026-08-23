---
type: concept
scope: social-media-agent
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/social-media-agent
description: Social Media Agent 总览——基于 LangGraph 的多图协作社交媒体内容生成 Agent
---

# Social Media Agent 总览

## 什么是 Social Media Agent

Social Media Agent 是 LangChain 团队开源的社交媒体内容生成 Agent。它接收一个 URL，自动抓取并分析网页内容，生成适合 Twitter 和 LinkedIn 发布的帖子，通过 human-in-the-loop（HITL）流程让用户审核、修改后调度发布。

- **仓库**：https://github.com/langchain-ai/social-media-agent
- **许可证**：MIT（Copyright (c) 2024 LangChain）
- **主语言**：TypeScript（Node.js 20），含 Python 记忆子项目
- **核心框架**：LangGraph（`@langchain/langgraph@^1.4.8`）
- **LLM 提供商**：Anthropic Claude（主要）、Google Vertex AI（YouTube）、OpenAI（可选）

## 解决的问题

手动为博客文章、GitHub 仓库、YouTube 视频等内容创建社交媒体帖子耗时且重复。该 Agent 自动化了从内容摄取到发布调度的完整流程：

1. **多源内容解析**：自动识别 URL 类型（网页、GitHub、Twitter、YouTube、Reddit、Luma），采用对应的抓取和验证策略。
2. **内容相关性过滤**：通过 LLM 生成营销报告，判断内容是否与业务上下文相关。
3. **帖子生成与压缩**：生成帖子文本，超过 280 字符时自动压缩（最多 3 次）。
4. **图片选配**：可选地从内容中查找或 AI 生成配图。
5. **人工审核**：在 humanNode 中断，用户可接受、重写、改日期或拆分 URL。
6. **多平台调度**：通过 Arcade 或自建 OAuth 调度到 Twitter 和 LinkedIn。

## 核心架构：14 个协作图

项目在 `langgraph.json` 中注册了 14 个独立 LangGraph 图，每个图聚焦单一职责：

| 类别 | 图名 | 职责 |
|---|---|---|
| 内容生成 | `generate_post` | 核心图：URL → 验证 → 报告 → 帖子 → 审核 → 调度 |
| 内容生成 | `generate_thread` | 生成 Twitter thread（多帖串联） |
| 内容生成 | `generate_report` | 从页面内容生成营销报告 |
| 内容验证 | `verify_tweet` | 验证 Twitter 内容及外链 |
| 内容验证 | `verify_reddit_post` | 验证 Reddit 帖子及外链 |
| 数据摄取 | `ingest_data` | 从 Slack/Twitter 摄取原始数据 |
| 数据策展 | `curate_data` | 从多源拉取、分组、去重内容 |
| 编排 | `supervisor` | 批处理编排：策展 → 并行报告 → 分组 → 批量生成 |
| 发布 | `upload_post` | 上传/发布帖子到社交媒体 |
| 反思 | `reflection` | 从用户反馈中学习，更新提示词规则 |
| 内容改编 | `repurposer` | 将已有内容改编为新帖子 |
| 数据摄取 | `ingest_repurposed_data` | 摄取待改编的内容 |
| 中断处理 | `curated_post_interrupt` | 策展帖子的独立中断处理 |
| 中断处理 | `repurposer_post_interrupt` | 改编帖子的独立中断处理 |

详见 [图结构参考](/langchain-ai/social-media-agent/references/graphs)。

## generate_post 流程图

```
START
  │
  ▼
authSocialsPassthrough ── 社交媒体认证透传
  │
  ▼
verifyLinksSubGraph ────── 并行验证各 URL 类型（fan-out/fan-in）
  │
  ├─ URL已使用或无内容 ──→ END
  │
  ▼
generateContentReport ─── 生成营销报告
  │
  ├─ report为空 ─────────→ END
  │
  ▼
generatePost ──────────── 生成帖子
  │
  ▼
condensePost? ◄────────── 若 >280 字符且压缩次数 ≤3（循环）
  │
  ▼
findAndGenerateImages ─── 查找/生成配图（失败则回退纯文本）
  │
  ▼
humanNode ═══════════════ HITL 中断（等待用户审核）
  │
  ├─ rewritePost ─────────┐
  ├─ updateScheduleDate ──┤ 处理后回到 humanNode
  ├─ rewriteWithSplitUrl ─┘
  ├─ unknownResponse ─────→ humanNode（重新提示）
  │
  ▼
schedulePost ──────────── 调度到 Twitter/LinkedIn
  │
  ▼
END
```

## 多源 URL 验证

`verifyLinksSubGraph` 使用 LangGraph 的 `Send` API，根据 URL 类型并行分发到专用验证节点：

- **Twitter**：抓取推文内容，验证外链
- **YouTube**：通过 Google Vertex AI 获取视频摘要
- **GitHub**：通过 Octokit 获取仓库信息，Playwright 截图
- **Reddit**：通过 snoowrap 获取帖子内容
- **Luma**：验证活动页面
- **General**：FireCrawl 抓取通用网页内容

详见 [图结构参考](/langchain-ai/social-media-agent/references/graphs)。

## 技术栈

### 后端（TypeScript）

- **LangGraph JS**：工作流编排、状态管理、HITL 中断
- **LangChain JS**：LLM 抽象、prompt 模板
- **Anthropic Claude**：主要 LLM（帖子生成、报告、反思）
- **FireCrawl**：网页内容抓取
- **Arcade**：社交媒体统一认证与调度
- **Supabase**：图片存储
- **Playwright + Sharp**：网页截图和图片处理
- **Express + Passport**：自建 OAuth 认证服务器

### 记忆子系统（Python）

- **langmem**：提示词优化与反思记忆
- **langchain-anthropic**：Claude 客户端
- **LangGraph Store**：持久化反思规则

## 配置与定制

### 运行模式

- **快速入门模式**：仅需 Anthropic + FireCrawl + Arcade，不支持 GitHub/YouTube/Slack/图片
- **完整模式**：启用全部集成，需要所有 API 凭证

### 关键配置项

| 配置键 | 环境变量 | 作用 |
|---|---|---|
| `textOnlyMode` | `TEXT_ONLY_MODE` | 禁用图片处理 |
| `skipContentRelevancyCheck` | `SKIP_CONTENT_RELEVANCY_CHECK` | 跳过业务相关性验证 |
| `skipUsedUrlsCheck` | `SKIP_USED_URLS_CHECK` | 跳过 URL 去重 |
| `postToLinkedInOrganization` | `POST_TO_LINKEDIN_ORGANIZATION` | 发布到 LinkedIn 组织页 |

### 提示词定制

四个核心提示词区段可独立定制：`BUSINESS_CONTEXT`、`TWEET_EXAMPLES`、`POST_STRUCTURE_INSTRUCTIONS`、`POST_CONTENT_RULES`。详见 [深度洞察](/langchain-ai/social-media-agent/spec/insights) 第 9 节。

## 目录结构

```
social-media-agent/
├── src/
│   ├── agents/               # 14 个 LangGraph 图
│   │   ├── generate-post/    # 核心帖子生成图
│   │   ├── verify-links/     # URL 验证子图
│   │   ├── supervisor/       # 批处理编排图
│   │   ├── curate-data/      # 数据策展图
│   │   ├── reflection/       # 反思图
│   │   └── ...
│   ├── clients/              # 社交媒体平台客户端
│   │   ├── twitter/
│   │   ├── slack/
│   │   ├── reddit/
│   │   ├── linkedin.ts
│   │   └── auth-server.ts
│   ├── utils/                # 工具函数
│   ├── tests/                # 单元与集成测试
│   └── evals/                # 评估脚本
├── memory-v2/                # Python 记忆/反思子项目
│   └── memory_v2/
│       ├── graph.py
│       └── state.py
├── scripts/                  # Cron 与运维脚本
├── langgraph.json            # LangGraph 配置（14 图注册）
├── package.json
└── pyproject.toml            # Python Slack 集成
```

## 进一步阅读

- [图结构参考](/langchain-ai/social-media-agent/references/graphs) — 14 个 LangGraph 图的详细结构与节点说明
- [事实清单](/langchain-ai/social-media-agent/spec/facts) — 从源码中提取的可验证事实
- [深度洞察](/langchain-ai/social-media-agent/spec/insights) — 架构决策与设计模式分析
