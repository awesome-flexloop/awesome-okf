---
type: Concept
title: "00 Search / Fetch 双 API 全景"
description: DeepSeek 网页搜索与抓取能力总览——Search 自研搜索引擎结构化结果、Fetch 单页 Markdown 抓取、统一 Bearer 鉴权、端点速查与最小可运行示例。
tags: [DeepSeek, Search, Fetch, 搜索API, Agent, RAG, 网页抓取]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 00 Search / Fetch 双 API 全景

## 0.1 三个核心结论

1. **双 API 分工明确**：Search 按 query 搜索网页、返回结构化结果，由 DeepSeek 自研搜索引擎提供支持；Fetch 抓取单个网页、以 Markdown 文本返回页面内容。
2. **面向 Agent 与 RAG 场景**：两者都是原始 JSON API，为 Agent 与 RAG 应用提供实时网页内容。
3. **复用主 API 鉴权**：使用与 DeepSeek API 相同的 Bearer 鉴权，Base URL 为 `https://api.deepseek.com`。

## 0.2 端点速查

| API | 端点 | 一句话说明 |
|-----|------|-----------|
| Search | `POST https://api.deepseek.com/v1/tools/search` | 按 query 搜索网页，返回结构化结果 |
| Fetch | `POST https://api.deepseek.com/v1/tools/fetch` | 抓取单个网页，返回 Markdown 正文 |

## 0.3 鉴权

在请求头中携带 API Key 和 JSON 内容类型，两项均为必填：

| 请求头 | 必填 | 值 |
|--------|------|-----|
| `Authorization` | 是 | `Bearer <DeepSeek API Key>` |
| `Content-Type` | 是 | `application/json` |

> API Key 在 DeepSeek 开放平台（platform.deepseek.com）创建获取。

## 0.4 最小可运行示例

### curl（Search）

```bash
curl https://api.deepseek.com/v1/tools/search \
  -H "Authorization: Bearer <DeepSeek API Key>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "DeepSeek V4 模型 发布",
    "count": 5,
    "need_content": true
  }'
```

### Python（Search）

```python
import requests

response = requests.post(
    "https://api.deepseek.com/v1/tools/search",
    headers={
        "Authorization": "Bearer <DeepSeek API Key>",
    },
    json={
        "query": "DeepSeek V4 模型 发布",
        "count": 5,
        "need_content": True,
    },
)
response.raise_for_status()
for result in response.json()["results"]:
    print(result["title"], result["url"])
    print(result["summary"])
```

### curl（Fetch）

```bash
curl https://api.deepseek.com/v1/tools/fetch \
  -H "Authorization: Bearer <DeepSeek API Key>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article"
  }'
```

### Python（Fetch）

```python
import requests

response = requests.post(
    "https://api.deepseek.com/v1/tools/fetch",
    headers={
        "Authorization": "Bearer <DeepSeek API Key>",
    },
    json={"url": "https://example.com/article"},
)
response.raise_for_status()
page = response.json()
print(page["title"])
print(page["content"])
```

> 官方 Python 示例统一使用 `response.raise_for_status()` 处理错误。

## 0.5 文档导航

| 章节 | 内容 | 适合读者 |
|------|------|---------|
| [01 Search 接口](01-search-api.md) | 请求字段、搜索语法、响应字段与质量评分 | 开发者 |
| [02 Fetch 接口](02-fetch-api.md) | 请求约束、响应结构、与 Search 的协作 | 开发者 |
| [03 错误处理](03-error-handling.md) | 状态码表、重试策略三档分流 | 开发者 |
| [04 计费与限速](04-billing-rate-limits.md) | 按次计费规则、QPS 水位 | 技术决策者 |
| [05 Agent 集成实践](05-agent-integration.md) | 双摘要分层、质量过滤、限流设计 | Agent/RAG 工程师 |
| [06 术语表](06-glossary.md) | 专业术语解释 | 初学者 |

## 0.6 补充说明

- 完整的请求与响应 Schema 见官方 Search API Reference 与 Fetch API Reference。
- 请求体中的未知字段会被忽略。
- Search 和 Fetch 都是只读请求。
