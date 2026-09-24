---
type: Concept
title: "public-apis 是什么"
description: "把 public-apis 理解为可浏览的公共 API 目录，而不是统一调用平台"
tags: [public-apis, API 目录, GitHub, 开源资源]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: verification, resource: "/references/verification.md" }
  - { id: repo, resource: "https://github.com/public-apis/public-apis" }
---

# public-apis 是什么

## 一句话定位

`public-apis/public-apis` 是一个把公共 API 按主题整理成 Markdown 目录的 GitHub 开源项目。它的 README 自述为 “A collective list of free APIs”。[F-002～F-003](../references/article-source.md)

它解决的是“先找到候选数据源”的发现问题，不是把天气、汇率、新闻等服务统一代理到一个接口里。真正调用时仍要打开条目链接，阅读服务商自己的认证、限额、数据许可与隐私条款。[F-013、F-020](../references/article-source.md)

## 目录的最小信息模型

每个条目用一个表格行提供四类筛选信号：

| 字段 | 读者要问的问题 | 不能推出的结论 |
|---|---|---|
| `Description` | 它大致提供什么数据或能力？ | 不能替代官方 API 文档 |
| `Auth` | 是否需要 API Key、OAuth 或其他认证？ | `No` 不等于没有限流 |
| `HTTPS` | 是否支持加密传输？ | `Yes` 不等于数据可信 |
| `CORS` | 浏览器跨域调用是否可能？ | `Yes` 不等于一定稳定 |

字段结构来自文章与当前 README 的目录观察。[F-008～F-009](../references/article-source.md)

## 规模数字的时点性

文章写的是 51 个分类、1700 多个条目和约 4.7 万 Star；2026-09-20 读取 raw README 时，Index 仍有 51 个分类，按 Markdown 表格行统计约 1850 条。[F-004～F-006](../references/article-source.md)

Star 数不能作为本教程的稳定事实：GitHub API 快照与其他公开页面不一致，且 API 元数据本身存在陈旧字段。应把 Star 和条目数理解为带读取日期的观测值，而不是项目质量或可用性的证明。[核验报告](../references/verification.md)

## 阅读边界

本项目的 MIT 许可证只覆盖该仓库自身的内容；目录中每个第三方 API 仍有独立条款。所谓“免费”可能只是免费入口或免费额度，不能直接翻译成“永久免费、无限量或可商用”。[F-007、F-020](../references/article-source.md)
