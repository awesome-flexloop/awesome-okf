---
type: Reference
title: github-activity 源码路径映射
description: github-activity 核心源文件、API函数、CLI命令和PR分类配置索引
tags: [github, activity, changelog, graphql, cli, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-repo
    resource: https://github.com/executablebooks/github-activity
    title: github-activity GitHub Repository
---

# github-activity 源码路径映射

源路径相对于 `external/libs/ai/executablebooks/github-activity/github_activity/`。

## 核心文件清单

| 文件 | 职责 |
|------|------|
| `__init__.py` | 包入口、版本号 |
| `github_activity.py` | 核心逻辑：PR分类、数据获取、Markdown生成 |
| `graphql.py` | GitHub GraphQL API客户端、分页处理 |
| `auth.py` | GitHub Token认证 |
| `cache.py` | API响应缓存装饰器 |
| `cli.py` | Click CLI入口和命令定义 |
| `git.py` | Git命令行集成、标签/分支检测 |

## 核心函数

| 函数 | 功能 |
|------|------|
| `get_activity()` | 获取仓库/组织活动数据，返回DataFrame |
| `generate_activity_markdown()` | 将活动数据转换为Markdown |
| `generate_all_activity_md()` | 生成完整变更日志 |

## PR分类类型

| 类型key | 标签匹配 | 前缀匹配 | 说明 |
|---------|---------|---------|------|
| api_change | api-change/breaking | BREAK/BREAKING/BRK/UPGRADE | API破坏性变更 |
| new | feature/new | NEW/FEAT/FEATURE | 新功能 |
| deprecate | deprecation/deprecate | DEPRECATE/DEP | 功能废弃 |
| enhancement | enhancement | ENH/IMPROVE/IMP | 功能增强 |
| bug | bug/bugfix | FIX/BUG | Bug修复 |
| maintenance | maintenance/maint | MAINT/MNT | 维护更新 |
| documentation | documentation/docs/doc | DOC/DOCS | 文档更新 |
| ci | ci/continuous-integration | CI | CI/CD更新 |

## CLI命令

| 命令 | 说明 |
|------|------|
| `github-activity <repo>` | 生成指定仓库的活动报告 |
| 主要选项：`--since`, `--until`, `--kind`, `--auth`, `--output`, `--cache`, `--tags` |

## 相关概念

- [简介](../concepts/00-introduction.md)
- [CLI命令详解](../concepts/02-cli-usage.md)
- [标签分类配置](../concepts/04-configuration.md)
