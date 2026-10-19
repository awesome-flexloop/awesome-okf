---
type: Concept
title: "03 错误处理：状态码表与重试策略"
description: OpenAI 兼容错误格式（param 恒为 null）、11 类 HTTP 状态码、可重试性三档分流——退避重试/用户介入/终止。
tags: [DeepSeek, 错误处理, HTTP状态码, 重试策略]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 03 错误处理：状态码表与重试策略

## 3.1 错误格式

错误响应使用 **OpenAI 兼容的错误格式**，`param` 字段恒为 `null`：

```json
{
  "error": {
    "message": "'count' must be between 1 and 50",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_request_error"
  }
}
```

## 3.2 HTTP 状态码表

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求头或请求体不合法，包括 JSON 格式错误或字段值无效 |
| 401 | API Key 缺失或无效 |
| 402 | 账号余额不足 |
| 403 | Fetch 请求被安全策略拒绝 |
| 404 | Fetch 未能获取可用的网页内容，例如 URL 不可用、被站点策略拦截、目标站点返回错误、内容类型不受支持或页面没有可提取的 Markdown 正文 |
| 408 | 读取请求体超时 |
| 413 | 请求体超过大小限制 |
| 429 | 超过 Search 或 Fetch 的 QPS 限制 |
| 500 | 服务器内部错误 |
| 504 | 下游请求超时 |

## 3.3 重试策略三档分流

官方对只读请求的重试指引：

| 档位 | 状态码 | 处理方式 |
|------|--------|---------|
| 可重试 | 408、429、5xx | 等待后重试 |
| 需用户介入 | 402 | 先充值再重试 |
| 终止 | 其它 4xx（400/401/403/404/413） | 如不修改请求，请勿重试 |

## 3.4 语义澄清

- **Fetch 的 404 ≠ 页面不存在**：它覆盖"页面存在但没有可提取的 Markdown 正文"等多种情形——机械重试同一 URL 大概率仍失败。
- **403 ≠ 鉴权失败**：Fetch 被安全策略拒绝才是 403；API Key 缺失或无效是 401。
- **Search 与 Fetch 都是只读请求**：重试不会产生副作用，但仍受计费规则约束——只有 HTTP 200 且产生结果的请求才计费（见 [04 计费与限速](04-billing-rate-limits.md)）。
