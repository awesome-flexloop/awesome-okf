---
type: Concept
title: github-activity 简介
description: github-activity是什么——通过GitHub GraphQL API生成仓库变更日志的CLI工具，支持PR分类、Markdown输出和标签自定义
tags: [github, activity, changelog, graphql, cli, release-notes]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:02:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# github-activity 简介

github-activity 是 Executable Books 生态中的命令行工具，通过 GitHub GraphQL API 获取仓库的 Issues 和 Pull Requests 活动数据，自动分类并生成格式化的 Markdown 变更日志（Changelog）。常用于发布新版本时自动生成 release notes。

## 核心功能

- **GraphQL数据获取**：使用GitHub v4 GraphQL API高效获取PR/Issue数据
- **智能PR分类**：基于标签和标题前缀自动分类PR（新功能、修复、文档等8类）
- **Markdown输出**：生成结构化的Markdown变更日志
- **时间范围过滤**：按标签、日期、分支过滤活动
- **Token认证**：支持GitHub Personal Access Token，提高API速率限制
- **本地缓存**：缓存API响应避免重复请求
- **Git集成**：自动检测仓库标签作为时间范围

## PR分类体系

| 分类 | 匹配标签 | 匹配标题前缀 | 说明 |
|------|---------|-------------|------|
| API变更 | breaking, api-change | BREAK, BREAKING | 破坏性变更 |
| 新功能 | feature, new | NEW, FEAT | 新增功能 |
| 功能废弃 | deprecation | DEPRECATE, DEP | 废弃功能 |
| 增强 | enhancement | ENH, IMPROVE | 功能增强 |
| Bug修复 | bug, bugfix | FIX, BUG | Bug修复 |
| 维护 | maintenance | MAINT, MNT | 维护更新 |
| 文档 | documentation/docs | DOC, DOCS | 文档更新 |
| CI | ci | CI | CI/CD更新 |

## 典型使用场景

- **发布Release Notes**：在两次版本标签之间生成变更日志
- **周报/月报**：生成一段时间内的仓库活动摘要
- **贡献者报告**：统计贡献者活动
- **自动化CI**：在Release流水线中自动生成changelog

## 安装

```bash
pip install github-activity
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [CLI命令详解](/concepts/02-cli-usage.md)
- [变更日志生成示例](/examples/changelog-generation.md)
