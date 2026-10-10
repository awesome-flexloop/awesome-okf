---
okf_version: "0.2"
type: reference
title: 来源清单
description: Skills Manager bundle 信源登记——文章、官方仓库/README/API/Release 及观察时间
tags: [skills-manager, sources, manifest]
generated:
  by: process:seven-concepts
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: flagged
stale_after: "2026-12-31"
sources:
  - id: wechat-article
    url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg"
  - id: github-repo
    url: "https://github.com/xingkongliang/skills-manager"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
  - id: github-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager"
---

# 来源清单

| 来源 id | 说明 | 访问入口 | 观察时间 | 用途 |
|---|---|---|---|---|
| `wechat-article` | 微信公开文章《又一个 skill 神级工具，帮我省了太多时间。》（开源日记） | https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg | 2026-10-04 发布页元信息 | F-001~F-020、F-033~F-044 |
| `github-repo` | 官方 GitHub 仓库 `xingkongliang/skills-manager`（MIT） | https://github.com/xingkongliang/skills-manager | — | F-021、F-017 |
| `github-api` | 仓库 API（描述、`updated_at`、许可） | https://api.github.com/repos/xingkongliang/skills-manager | 2026-10-10T04:40:27Z | F-021、F-031 |
| `github-main-commit` | 主分支 README 快照（固定提交） | commit `9e03d833829bc5e004263f61dec75f3bc8e39062`（2026-10-09T21:34:41Z） | 2026-10-10 | F-023、F-024、F-028、F-029、F-031、F-034、F-040、F-041 |
| `github-readme` | 官方英文 README | raw 固定 commit SHA | 2026-10-10 | F-022、F-023、F-024、F-028、F-029 |
| `github-release-api` | `releases/latest` API | https://api.github.com/repos/xingkongliang/skills-manager/releases/latest | 2026-10-10 | F-030 |
| `github-release-list-api` | Release 列表 API | https://api.github.com/repos/xingkongliang/skills-manager/releases | 2026-10-10 | F-030 |
| `github-release-page` | 网页 `/releases/latest` | https://github.com/xingkongliang/skills-manager/releases/latest | 2026-10-10 | F-030 |
| `backup-source` | 实现源码 `git_backup.rs`（100 MiB 阈值） | 仓库源码 | 源码阅读快照 | F-025 |
| `oauth-source` | 实现源码 `connect_with_token`/`sanitize_url_to_keychain` | 仓库源码 | 源码阅读快照 | F-026、F-032 |
| `sync-source` | 实现源码 `sync_engine.rs`（链接策略） | 仓库源码 | 源码阅读快照 | F-027 |

## 历史与审计

- 仓库描述与版本为**动态值**：README commit SHA 已固定为 `9e03d833…`，以保留稳定快照；`releases/latest`、Release 列表与网页三视图在 2026-10-10 均指向 `v1.40.3`。
- 历史版本记录 `v1.22.1`/`v1.28.3`/`v1.17.0` 无原始响应、不可复现，作为审计历史保留，不作为当前结论（F-030）。
- 源码结论来自实现分支阅读，不代表实机测试或安全审计。