---
type: Concept
title: "01 Search 接口：请求、搜索语法与响应"
description: Search 接口完整参考——五个请求字段、八类搜索语法操作符、results 十字段结构、rerank_score 与 authority 质量阈值。
tags: [DeepSeek, Search, 搜索语法, rerank_score, authority]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 01 Search 接口：请求、搜索语法与响应

## 1.1 请求

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

### 请求字段

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 是 | - | 搜索词，1～128 个 Unicode 字符，不能全为空白，支持搜索语法 |
| `count` | integer | 否 | 10 | 返回条数，1～50 |
| `ori_question` | string | 否 | - | 触发搜索的用户原始问题，1～128 个字符，有助于更好地理解搜索意图，传 `null` 视为未提供 |
| `localization` | string | 否 | `""` | 用于优先返回本地化搜索结果的 IP 地址 |
| `need_content` | boolean | 否 | `false` | 是否在 `content` 中返回网页正文，为 `false` 时 `content` 恒为空字符串 |

> 请求体中的未知字段会被忽略。

## 1.2 搜索语法

`query` 中的搜索语法会原样传递给搜索服务。可以在一个 query 中组合多个操作符。

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `site:` | `DeepSeek site:github.com` | 将结果限制在指定站点；指定多个时用空格分隔并通过 OR 连接，如 `DeepSeek site:github.com OR site:huggingface.co` |
| `-site:` | `DeepSeek -site:example.com` | 排除指定站点，指定多个时用空格分隔 |
| `-关键词` | `DeepSeek -广告` | 排除包含指定关键词的网页，指定多个时用空格分隔 |
| `-"短语"` | `DeepSeek -"release notes"` | 排除包含指定短语的网页，短语内可以包含空格，指定多个时用空格分隔 |
| `"..."` | `DeepSeek "精确短语"` | 精确匹配指定短语，指定多个时用空格分隔 |
| `lang:` | `DeepSeek lang:zh,en` | 将结果限制在指定语言，多种语言用逗号分隔 |
| `after:` | `DeepSeek after:2025` 或 `DeepSeek after:2025-01-01` | 将结果限制在指定日期之后发布的网页 |
| `before:` | `DeepSeek before:2026` 或 `DeepSeek before:2026-06-01` | 将结果限制在指定日期之前发布的网页 |

### 组合示例

```json
{
  "query": "DeepSeek 模型 site:github.com OR site:huggingface.co lang:zh after:2025",
  "count": 10
}
```

## 1.3 响应

请求成功时返回 HTTP 200 与 `results` 数组。搜索正常结束但没有匹配结果时，返回空数组。

```json
{
  "results": [
    {
      "rerank_score": 2.4,
      "title": "DeepSeek V4 模型发布",
      "url": "https://example.com/deepseek-v4",
      "snippet": "DeepSeek V4 已上线，支持工具调用与长上下文。",
      "summary": "DeepSeek 发布了 V4 模型。此次发布改进了工具调用与长上下文能力，适合 Agent 工作流。",
      "content": "DeepSeek V4 现已正式上线……",
      "site_name": "Example News",
      "site_icon": "https://example.com/favicon.ico",
      "date": "2026-06-01T00:00:00+00:00",
      "authority": 3
    }
  ]
}
```

### results 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `rerank_score` | number | 排序分数，0～3 分，综合考虑相关性、权威性、时效性等维度，大于等于 1.5 分为优质结果 |
| `title` | string | 标题 |
| `url` | string | 结果链接 |
| `snippet` | string | 短摘要，与 query 相关，通常为 100～200 字符，适用于前端展现 |
| `summary` | string | 长摘要，与 query 相关，通常为 600～800 字符，适用于给模型阅读 |
| `content` | string | 网页正文，`need_content` 为 `false` 或正文缺失时为空字符串 |
| `site_name` | string 或 null | 站点名称，缺失时为 `null` |
| `site_icon` | string 或 null | 站点图标 URL，缺失时为 `null` |
| `date` | string 或 null | 发布时间，统一为 UTC 的 RFC 3339 格式，未知时为 `null` |
| `authority` | integer | 网页权威性，0～4（-1 表示未知），大于等于 3 为极权威结果 |

## 1.4 两个质量阈值

| 阈值 | 含义 | 用法 |
|------|------|------|
| `rerank_score` ≥ 1.5 | 优质结果（相关性、权威性、时效性综合） | 下游只消费高分结果 |
| `authority` ≥ 3 | 极权威网页 | 权威性敏感场景过滤 |

> `date` 为 null 时表示发布时间未知；`site_name`/`site_icon` 缺失时为 null，前端展示需做空值兜底。
