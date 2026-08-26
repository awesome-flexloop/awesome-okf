---
type: bundle
okf_version: "0.2"
scope: social-media-agent
name: social-media-agent
version: "0.1.0"
source: https://github.com/langchain-ai/social-media-agent
description: Social Media Agent——LangChain 开源的基于 LangGraph 多图协作的社交媒体内容生成 Agent，接收 URL 自动生成 Twitter/LinkedIn 帖子，支持 HITL 审核、多源内容验证、图片选配与定时发布
---

# Social Media Agent

**Social Media Agent** 是 LangChain 团队开源的社交媒体内容生成 Agent。它接收 URL，自动抓取并分析网页内容，生成适合 Twitter 和 LinkedIn 的帖子，通过 human-in-the-loop 流程让用户审核、修改后调度发布。项目采用 TypeScript 实现核心工作流，包含 14 个独立协作的 LangGraph 图，并附带 Python 记忆/反思子系统。

- **版本**：0.0.1（package.json）
- **许可证**：MIT（Copyright (c) 2024 LangChain）
- **主语言**：TypeScript（Node.js 20）
- **核心框架**：LangGraph `@langchain/langgraph@^1.4.8`
- **LLM**：Anthropic Claude（主要）、Google Vertex AI（YouTube）

## 核心特性

- **多图协作架构**：14 个职责单一的 LangGraph 图，通过子图嵌套和 SDK 远程调用协作
- **多源 URL 验证**：自动识别 Twitter/YouTube/GitHub/Reddit/Luma/通用网页，并行抓取验证
- **HITL 审核流程**：humanNode 中断点支持接受、重写、改期、URL 拆分等操作，循环直到确认
- **自动压缩循环**：帖子超过 280 字符时自动压缩，最多 3 次防止无限循环
- **图片选配**：从内容中查找或 AI 生成配图，失败时优雅降级为纯文本
- **双认证路径**：Arcade 统一认证或自建 Express+Passport OAuth 服务器
- **跨 run 记忆**：LangGraph Store 实现 URL 去重和用户反馈反思规则
- **批处理编排**：supervisor 图通过 Send API 并行处理多源内容

## 图列表

| 图名 | 职责 |
|---|---|
| `generate_post` | 核心图：URL → 验证 → 报告 → 帖子 → 审核 → 调度 |
| `generate_thread` | 生成 Twitter thread |
| `generate_report` | 生成营销内容报告 |
| `verify_links` | 并行验证多类型 URL |
| `verify_tweet` | 验证 Twitter 内容及外链 |
| `verify_reddit_post` | 验证 Reddit 帖子 |
| `supervisor` | 批处理编排：策展 → 并行报告 → 批量生成 |
| `curate_data` | 多源数据拉取与分组 |
| `ingest_data` | 从 Slack/Twitter 摄取数据 |
| `upload_post` | 上传发布帖子 |
| `reflection` | 从用户反馈学习更新规则 |
| `repurposer` | 内容改编 |
| `curated_post_interrupt` | 策展帖子中断处理 |
| `ingest_repurposed_data` | 摄取待改编内容 |

详见 [图结构参考](/ai/langchain-ai/social-media-agent/references/graphs)。

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/social-media-agent/concepts/overview) — 项目定位、14 图架构、generate_post 流程、技术栈

### 参考

- [图结构参考](/ai/langchain-ai/social-media-agent/references/graphs) — 各图节点、状态字段、条件路由、运行时配置

### 规格

- [事实清单](/ai/langchain-ai/social-media-agent/spec/facts) — 从源码中提取的 34 条可验证事实
- [深度洞察](/ai/langchain-ai/social-media-agent/spec/insights) — 多图架构、HITL 状态机、Send API 并行模式等 10 条设计洞察

## 目录结构

```
social-media-agent/
├── spec/
│   ├── facts.md
│   └── insights.md
├── concepts/
│   ├── index.md
│   └── overview.md
├── references/
│   ├── index.md
│   └── graphs.md
├── log.md
└── index.md
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
spec/facts
spec/insights
log
```
