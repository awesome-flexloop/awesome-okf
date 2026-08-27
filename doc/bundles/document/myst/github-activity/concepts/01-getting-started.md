---
type: Concept
title: 快速开始
description: 安装github-activity、配置GitHub Token、生成第一个变更日志
tags: [github, activity, installation, getting-started, token]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:04:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# 快速开始

## 安装

```bash
pip install github-activity
```

## 配置GitHub Token（推荐）

虽然不配置Token也可以使用（匿名访问），但GitHub API速率限制很低（每小时60次请求）。配置Personal Access Token后速率限制提高到每小时5000次。

### 方式一：环境变量

```bash
export GITHUB_TOKEN=your_github_token
```

### 方式二：CLI参数

```bash
github-activity executablebooks/github-activity --auth your_github_token
```

### 获取Token

在 GitHub → Settings → Developer settings → Personal access tokens 中生成，只需 `public_repo` 权限即可。

## 生成第一个变更日志

### 获取最近活动

```bash
github-activity executablebooks/github-activity
```

输出当前仓库最近的合并PR和关闭的Issue。

### 指定时间范围

```bash
# 自某个日期以来
github-activity executablebooks/github-activity --since 2024-01-01

# 日期范围
github-activity executablebooks/github-activity --since 2024-01-01 --until 2024-06-30
```

### 基于Git标签

在git仓库目录中运行，自动使用标签作为时间范围：

```bash
cd your-repo
github-activity  # 自动检测上一个tag到HEAD
```

### 输出到文件

```bash
github-activity executablebooks/github-activity --output changelog.md
```

## 基本使用示例

### 查看特定版本的变更

```bash
# v0.1.0到v0.2.0之间的变更
github-activity executablebooks/jupyter-cache --since v0.1.0 --until v0.2.0
```

### 仅查看PR（不包括Issue）

```bash
github-activity executablebooks/sphinx-tabs --kind pr
```

### 仅查看Issue

```bash
github-activity executablebooks/sphinx-tabs --kind issue
```

## 输出示例

生成的Markdown大致格式：

```markdown
# v0.2.0 (2024-06-15)

## New features added

- Add new directive for XYZ [#123](https://github.com/...) (@contributor)

## Bugs fixed

- Fix issue with ABC [#124](https://github.com/...) (@contributor2)
```

## 验证安装

```bash
github-activity --version
```

## 相关概念

- [简介](00-introduction.md)
- [CLI命令详解](02-cli-usage.md)
- [变更日志生成示例](../examples/changelog-generation.md)
