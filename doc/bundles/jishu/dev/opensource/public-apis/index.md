---
okf_version: "0.2"
type: bundle
title: "public-apis 公共 API 清单"
description: "从微信公众号文章学习 GitHub public-apis 目录的结构、筛选方法、配套查询 API 与生产使用边界；资源综述，非操作教程"
tags: [public-apis, 公共 API, GitHub, API 选型, 开源资源]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
verification_scope: "文章事实、官方 README、GitHub API 元数据与配套 API 文档的静态核验"
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/rCCa5Y_UpWB_HKL4VCORvA" }
  - { id: repo, resource: "https://github.com/public-apis/public-apis" }
  - { id: repo-api, resource: "https://api.github.com/repos/public-apis/public-apis" }
  - { id: api, resource: "https://github.com/davemachado/public-api" }
---

# public-apis 公共 API 清单

> **证据警示：flagged。** 文章的 Star 数是时点快照，无法与当前可获得的 GitHub API 快照稳定对齐；条目数量也会随 README 更新。本包适合学习目录结构与候选筛选，不把目录或“免费”标签视为单个 API 的商用许可、SLA 或安全认证。

这是一个**资源目录综述，非操作教程**。文章没有提供完整版本、输入输出、实测日志和可复现安装步骤，因此本包不创建 `examples/`。

## 阅读路径

| 顺序 | 入口 | 核心问题 |
|---|---|---|
| 1 | [public-apis 是什么](concepts/00-public-apis-catalog.md) | 目录收录什么，五列元数据如何理解？ |
| 2 | [发现与筛选公共 API](concepts/01-discovery-and-selection.md) | 如何从分类和 Auth/HTTPS/CORS 缩小候选？ |
| 3 | [配套 API 与治理边界](concepts/02-companion-api-and-governance.md) | 如何查询目录，以及为什么仍需逐服务审查？ |
| 查证 | [文章事实清单](references/article-source.md)与[核验报告](references/verification.md) | 哪些数字已核验，哪些仍有时点边界？ |

## 已知边界

- 2026-09-20 读取 raw README 得到 51 个分类、约 1850 条 Markdown 表格行；这是快照，不是固定承诺。[F-004～F-005](references/article-source.md)
- 文章中的 4.7 万 Star/471k+ 标题数字与公开 API 快照冲突，因此保留在事实表而不作为当前指标。[F-006](references/article-source.md)
- 主仓库 MIT 许可不覆盖每个被收录 API 的数据、服务条款和商用授权。[F-007、F-020](references/article-source.md)
- 配套 API 文档声明无需鉴权、HTTPS、CORS，但本次未验证生产 SLA、限流或每个端点的当前可用性。[F-015～F-017](references/article-source.md)

## 主题关联

[程序员常用网站](../concepts/04-programmer-websites.md)提供更早期的开发者资源盘点；本包聚焦一个持续变化的公共 API 目录及其工程筛选边界。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
