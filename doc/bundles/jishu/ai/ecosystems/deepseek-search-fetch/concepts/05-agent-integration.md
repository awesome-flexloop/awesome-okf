---
type: Concept
title: "05 Agent / RAG 集成实践"
description: 基于官方文档事实的集成实践指南——双摘要分层消费、质量阈值过滤、need_content 成本策略、并发限流水位与错误三档分流。本章为实践建议层，与官方事实文档区分。
tags: [DeepSeek, Agent, RAG, 集成实践, 限流设计]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 05 Agent / RAG 集成实践

> **本章定位**：以下为基于官方文档事实（01–04 章）整理的**实践建议**，非官方强制规范；集成时请以官方文档为准。

## 5.1 双摘要分层消费

Search 结果的摘要是按消费者分层的：

| 字段 | 量级 | 设计意图 | 建议用法 |
|------|------|---------|---------|
| `snippet` | 100～200 字符 | 前端展现 | 渲染到 UI 的搜索结果列表 |
| `summary` | 600～800 字符 | 给模型阅读 | 直接拼入 LLM 上下文 / RAG 检索片段 |
| `content` | 完整正文 | 需要全文时 | `need_content: true` 开启，或对选中 URL 二次 Fetch |

默认 `need_content: false` 时 `content` 恒为空字符串——先用摘要完成任务、确需全文再取，是成本与上下文长度双友好的路径。

## 5.2 质量过滤阈值

- `rerank_score` ≥ 1.5：优质结果（综合相关性、权威性、时效性）；
- `authority` ≥ 3：极权威结果（0～4 分制，-1 未知）。

实践上可按场景组合：RAG 粗召回用 `rerank_score` 阈值；权威性敏感场景（如事实核查）叠加 `authority` 阈值，并对 `authority = -1`（未知）设计兜底而非直接丢弃。

## 5.3 搜索语法的 Agent 工具化

若将 Search 暴露为 Agent 的工具（function calling），可在工具参数中保留组合能力：

- `site:` 限定官方域（如 `site:github.com`）可显著抑制低质来源；
- `after:`/`before:` 支持年（`after:2025`）与日期（`after:2025-01-01`）两种粒度，适合"只要近期信息"类请求；
- `-"短语"` 排除已知噪声短语；
- `lang:zh,en` 约束返回语言。

同时把 `ori_question`（触发搜索的用户原始问题）传给 API，官方说明它有助于更好地理解搜索意图。

## 5.4 并发与限流水位

| 水位 | 数值 | 设计要点 |
|------|------|---------|
| Search 账号级 | 100 QPS | 按账号粒度计——同账号多把 API Key 不能横向扩吞吐（多账号可各自独立计） |
| Fetch 账号级 | 25 QPS | 批量抓取按此上限做并发池 |
| Fetch 域名级 | 未公布 | 同域名抓取需额外分桶 + 退避，429 可能先于此处出现 |
| 与模型并发 | 相互独立 | 模型侧限流不会与工具侧限流互相挤占 |

对 408 / 429 / 5xx 做指数退避重试；其它 4xx 不修改请求不重试（见 [03 错误处理](03-error-handling.md)）。

## 5.5 错误三档分流模板

```text
收到响应状态码：
├─ 408 / 429 / 5xx → 退避后重试（可重试档）
├─ 402            → 提示用户充值，暂停任务（用户介入档）
├─ 401            → 检查 API Key 配置（用户介入档）
└─ 400 / 403 / 404 / 413 → 记录失败，不再重试同一请求（终止档）
   └─ Fetch 404 → 标记"该页无可提取正文"，避免机械重试
```

## 5.6 成本估算线性模型

单次成功请求 0.005 元（Search 与 Fetch 同价）：

```text
日成本 ≈ (Search 成功次数 + Fetch 成功次数) × 0.005 元
```

失败请求、空结果、超时均不计费；`count` 的大小不影响价格。注意：若产品经由 DeepSeek Harness / Claude Code / Codex 的 Server 端工具调用走 Search/Fetch，2026-11-01 起这部分也将按次计费（见 [04 计费与限速](04-billing-rate-limits.md)）。
