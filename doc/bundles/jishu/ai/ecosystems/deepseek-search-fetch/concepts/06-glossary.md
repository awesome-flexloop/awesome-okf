---
type: Concept
title: "06 术语表"
description: Search / Fetch API 相关术语速查——Bearer 鉴权、QPS、rerank_score、authority、snippet/summary、RFC 3339、Server 端工具调用、Agent/RAG。
tags: [DeepSeek, 术语表, 术语]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 06 术语表

| 术语 | 解释 |
|------|------|
| Search | DeepSeek 的网页搜索接口，按 query 搜索网页返回结构化结果，由 DeepSeek 自研搜索引擎提供支持；端点 `POST /v1/tools/search` |
| Fetch | DeepSeek 的网页抓取接口，抓取单个网页并以 Markdown 文本返回页面内容；端点 `POST /v1/tools/fetch` |
| Bearer 鉴权 | 在 `Authorization` 请求头中携带 `Bearer <API Key>` 的认证方式，Search/Fetch 与 DeepSeek 主 API 共用 |
| Base URL | API 的基础地址，本双 API 为 `https://api.deepseek.com` |
| rerank_score | Search 结果的排序分数，0～3 分，综合相关性、权威性、时效性；≥1.5 为优质结果 |
| authority | 网页权威性评分，0～4 分（-1 表示未知）；≥3 为极权威结果 |
| snippet | 与 query 相关的短摘要（通常 100～200 字符），适用于前端展现 |
| summary | 与 query 相关的长摘要（通常 600～800 字符），适用于给模型阅读 |
| need_content | Search 请求的开关字段，控制是否返回网页正文；为 `false` 时 `content` 恒为空字符串 |
| ori_question | 触发搜索的用户原始问题，帮助 API 更好地理解搜索意图 |
| localization | 用于优先返回本地化搜索结果的 IP 地址 |
| RFC 3339 | 日期时间格式标准；Search 结果的 `date` 字段统一为 UTC 的 RFC 3339 格式 |
| QPS | 每秒请求数（Queries Per Second）；本双 API 按账号粒度限速，Search 100 / Fetch 25，Fetch 另有目标域名级限制 |
| OpenAI 兼容错误格式 | 错误响应的 JSON 结构 `{ message, type, param, code }`；本双 API 的 `param` 恒为 `null` |
| Server 端工具调用 | 在 DeepSeek Harness / Claude Code / Codex 中由服务端代为执行的 Search/Fetch 调用；北京时间 2026-11-01 00:00 起按次计费 |
| Agent | 以 LLM 为核心、可自主调用工具完成任务的程序；Search/Fetch 的官方目标场景之一 |
| RAG | 检索增强生成（Retrieval-Augmented Generation）；先检索外部内容再交由模型生成，Search/Fetch 可作为其实时检索层 |
| 按次计费 | 本双 API 的计费模式：每 1,000 次成功请求 5 元，不按 token 或返回条数计费；仅 HTTP 200 且产生结果才计费 |
