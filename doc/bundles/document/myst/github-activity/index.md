---
type: bundle
title: github-activity
description: Executable Books 生态的 GitHub 活动变更日志生成工具，基于GraphQL API自动分类PR并生成Markdown Release Notes
tags:
- github
- changelog
- graphql
- cli
- release-notes
- pr
- activity
- executable-books
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T05:14:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: ga-repo
  resource: "https://github.com/executablebooks/github-activity"
  title: github-activity GitHub Repository
okf_version: '0.2'
---

# github-activity

github-activity 是 Executable Books 生态中的命令行工具，通过 GitHub GraphQL API 获取仓库的 Pull Requests 和 Issues 活动数据，基于标签和标题前缀自动分类，生成格式化的 Markdown 变更日志（Changelog/Release Notes）。

## 核心功能

- **GraphQL高效获取**：使用GitHub v4 GraphQL API，比REST减少10倍请求量
- **智能PR分类**：8种内置分类（破坏性变更/新功能/修复/文档/CI等）
- **双模式匹配**：标签匹配+标题前缀匹配，容错率高
- **Markdown输出**：结构化变更日志，适合Release Notes
- **时间范围**：支持日期、Git标签过滤
- **Token认证**：提高API速率限制
- **本地缓存**：避免重复API请求
- **Git集成**：自动检测仓库标签
- **Python API**：DataFrame为中心的数据流，可编程处理

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](/concepts/index.md) |
| 💡 示例 | [示例代码](/examples/index.md) |
| 📚 参考 | [源码参考](/references/index.md) |
| 🔬 规格 | [事实清单](/spec/facts.md) · [架构洞察](/spec/insights.md) |

## 快速开始

```bash
pip install github-activity
export GITHUB_TOKEN=your_token
```

```bash
# 生成v0.1.0到v0.2.0之间的变更日志
github-activity owner/repo --since v0.1.0 --until v0.2.0 --output CHANGELOG.md
```

## 更新日志

见 [log.md](/log.md)。
