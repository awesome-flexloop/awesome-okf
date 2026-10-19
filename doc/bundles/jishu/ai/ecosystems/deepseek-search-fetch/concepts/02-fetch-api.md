---
type: Concept
title: "02 Fetch 接口：单页抓取与 Markdown 返回"
description: Fetch 接口完整参考——url 字段约束（长度/host/禁凭据）、title 与 Markdown content 响应、站点可用性与访问策略影响、与 Search 的分工协作。
tags: [DeepSeek, Fetch, 网页抓取, Markdown]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 02 Fetch 接口：单页抓取与 Markdown 返回

## 2.1 定位

Fetch 接口抓取单个网页，以 Markdown 文本返回页面内容。与 Search 的分工：Search 解决"找到哪些网页"，Fetch 解决"这一页写了什么"。

## 2.2 请求

```bash
curl https://api.deepseek.com/v1/tools/fetch \
  -H "Authorization: Bearer <DeepSeek API Key>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article"
  }'
```

### 请求字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 要抓取的网页地址，长度不超过 8192，必须为含 host 的 HTTP/HTTPS URL，且不能携带用户名或密码 |

## 2.3 响应

```json
{
  "title": "Example article",
  "content": "# Example article\n\nArticle content."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题，缺失时为空字符串 |
| `content` | string | 抓取后的 Markdown 正文 |

## 2.4 能力边界

- Fetch 的结果受**目标站点的可用性和访问策略**影响。
- 返回 HTTP 404 时表示 Fetch 未能获取可用的网页内容，官方列举的情形包括：URL 不可用、被站点策略拦截、目标站点返回错误、内容类型不受支持、页面没有可提取的 Markdown 正文（详见 [03 错误处理](03-error-handling.md)）。

## 2.5 与 Search 的协作

| 场景 | 建议用法 |
|------|---------|
| 只需要"有哪些相关信息" | 只用 Search，`need_content` 保持默认 `false`，读 `summary` |
| 需要某几页的完整内容 | Search 拿到 `url` 后，对选中的结果逐个调用 Fetch |
| 全文需求高频 | 权衡 Fetch 的 QPS 上限（25）与目标域名级限制（见 [04 计费与限速](04-billing-rate-limits.md)） |

> Fetch 与 Search 分别独立限速（价格同为每千次成功请求 5 元），详见 [04 计费与限速](04-billing-rate-limits.md)。
