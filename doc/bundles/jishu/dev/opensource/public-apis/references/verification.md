---
type: Reference
title: "public-apis 核验报告"
description: "对文章规模数字、目录字段、许可证与配套 API 的独立核验及勘误"
tags: [public-apis, P0, 核验, 勘误]
generated: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/rCCa5Y_UpWB_HKL4VCORvA" }
  - { id: repo, resource: "https://github.com/public-apis/public-apis" }
  - { id: repo-api, resource: "https://api.github.com/repos/public-apis/public-apis" }
  - { id: api, resource: "https://github.com/davemachado/public-api" }
---

# public-apis 核验报告

> **状态：flagged。** 文章的 Star 数与当前可获得的 GitHub API 快照、第三方快照不一致；条目数量也会随 README 更新变化。本文只把 51 分类和目录字段视为可复核事实，不把文章的热度数字当作稳定指标。

## P0 勘误表

| 对象 | 文章口径 | 核验结果 | 处理 |
|---|---|---|---|
| 分类数 | 51 | 2026-09-20 读取 raw README 的 Index 仍为 51 项 | 正文保留并标注读取时点 |
| API 条目数 | 1700 多个 | 同日按 Markdown 表格行统计约 1850 条 | 正文改为“约 1850 条快照”，不写成固定规模 |
| Star | 4.7 万/471k+ 标题 | GitHub API 返回 267955，但其 `updated_at`/`pushed_at` 字段明显陈旧；其他公开快照也互相冲突 | 保留文章口径作为原文事实，bundle 标 `flagged`，不作当前数值结论 |
| 许可证 | MIT | GitHub API 的 `license.key=mit`，LICENSE 内容为 MIT 授权条款 | 通过 |
| 配套 API | `/entries`、`/random`、`/categories`、`/health`，无需鉴权、HTTPS、CORS | 配套项目 README 明确列出 | 通过，但不推导 SLA |

## 事实边界

- `public-apis` 是目录，不是统一代理或统一计费网关。条目里的免费状态、限额、认证和商用许可属于各自服务。
- `Auth=No` 只说明目录字段中的认证要求，不等于接口没有速率限制、没有滥用防护或可直接用于生产。
- `HTTPS=Yes` 与 `CORS=Yes` 是筛选信号，不是对数据质量、可用性或隐私合规的保证。
- 配套 API 的 README 是项目自述；本次未建立持续监控，也未验证每个端点的当前响应时间或 SLA。

## 对抗审查记录

1. **事实视角**：F-005/F-006 的规模数字存在时点冲突，已在正文和状态中显式标记。
2. **结构视角**：本 bundle 不创建 `examples/`，避免把文章的经验性筛选写成可复制的官方操作教程。
3. **读者视角**：所有建议都要求回到单个 API 的官方文档，避免“清单即许可”的误读。
4. **时效视角**：`stale_after` 设置为 2026-10-20，届时应复核 README、Star、条目数量和配套 API 状态。

## 核验限制

本报告使用公开 README、GitHub REST API 与配套 API README；没有调用第三方 API、注册服务、验证商业条款或执行生产压测。
