---
okf_version: "0.2"
title: DeepSeek 网页搜索与抓取 API（Search / Fetch）
description: DeepSeek 官方 Search 与 Fetch 双 API 中文 Wiki——实时网页搜索、单页 Markdown 抓取、搜索语法、质量评分、错误重试、按次计费与账号级 QPS 限速、Agent/RAG 集成实践。
---

# DeepSeek 网页搜索与抓取 API（Search / Fetch）

DeepSeek 官方 [网页搜索与抓取指南](https://api-docs.deepseek.com/zh-cn/guides/search/) 中文 Wiki。Search 与 Fetch 是两个原始 JSON API，为 Agent 与 RAG 应用提供实时网页内容：Search 按 query 搜索网页返回结构化结果（由 DeepSeek 自研搜索引擎提供支持），Fetch 抓取单个网页并以 Markdown 文本返回页面内容。两者均使用与 DeepSeek API 相同的 Bearer 鉴权。

* [concepts/（7 篇）](concepts/index.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
log
```
