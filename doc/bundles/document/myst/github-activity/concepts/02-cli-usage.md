---
type: Concept
title: CLI命令详解
description: github-activity CLI的完整用法：仓库指定、时间范围、输出格式、认证、缓存等选项
tags: [github, activity, cli, command, options, changelog]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:06:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# CLI命令详解

## 基本语法

```bash
github-activity [OPTIONS] [TARGET]
```

`TARGET` 是 GitHub 仓库标识符，格式为 `owner/repo`（如 `executablebooks/jupyter-cache`）。如果在 git 仓库目录中运行，可以省略 TARGET，自动检测当前仓库的远程地址。

## 仓库目标

```bash
# 指定仓库
github-activity executablebooks/github-activity

# 在仓库目录中自动检测
cd /path/to/my/repo
github-activity  # 自动使用 origin remote 的仓库
```

## 时间范围选项

### --since / --until

指定活动时间范围：

```bash
# 自某日期以来
github-activity owner/repo --since 2024-01-01

# 日期范围
github-activity owner/repo --since 2024-01-01 --until 2024-06-30

# 基于Git标签
github-activity owner/repo --since v1.0.0 --until v2.0.0

# 相对时间（如果支持）
github-activity owner/repo --since 2024-01-01
```

日期格式支持 ISO 8601（`2024-01-01`、`2024-01-01T00:00:00Z`）和 Git 标签名。

### 无参数默认行为

如果不指定 `--since`/`--until`：
- 在git仓库中：使用最近的tag到HEAD
- 非git仓库：使用最近的活动

## 活动类型选项

### --kind

指定获取的活动类型：

```bash
# 仅PR（默认）
github-activity owner/repo --kind pr

# 仅Issue
github-activity owner/repo --kind issue

# 两者都包含
github-activity owner/repo --kind both
```

## 认证选项

### --auth

传入 GitHub Personal Access Token：

```bash
github-activity owner/repo --auth ghp_xxxxxxxxxxxx
```

或使用环境变量 `GITHUB_TOKEN`：

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
github-activity owner/repo
```

## 输出选项

### --output

将输出写入文件而非stdout：

```bash
github-activity owner/repo --output CHANGELOG.md
```

### --heading

自定义输出标题级别：

```bash
github-activity owner/repo --heading 2  # 使用##作为顶级标题
```

## 缓存选项

### --cache/--no-cache

控制API响应缓存：

```bash
# 启用缓存（默认）
github-activity owner/repo --cache

# 禁用缓存，强制从API获取最新数据
github-activity owner/repo --no-cache
```

缓存存储在临时目录中，减少重复API调用。

## 标签分类配置

### --tags

使用自定义标签分类配置文件：

```bash
github-activity owner/repo --tags my_tags.json
```

配置文件为JSON格式，覆盖默认分类规则。详见[标签分类配置](04-configuration.md)。

## 分支选项

### --branch

指定分支：

```bash
github-activity owner/repo --branch develop
```

默认为仓库的默认分支（通常是 `main`）。

## 实际使用示例

### 生成Release Notes

```bash
# 在发布新版本时生成v1.0.0到v1.1.0的变更日志
github-activity myorg/myrepo \
  --since v1.0.0 \
  --until v1.1.0 \
  --output docs/changelog/v1.1.0.md \
  --auth $GITHUB_TOKEN
```

### 生成周报

```bash
# 过去7天的活动
github-activity myorg/myrepo \
  --since $(date -d "7 days ago" +%Y-%m-%d) \
  --auth $GITHUB_TOKEN
```

### 包含Issues和PRs

```bash
github-activity myorg/myrepo --kind both
```

## 退出码

- `0`：成功
- `1`：一般错误（API错误、认证失败等）

## 相关概念

- [快速开始](01-getting-started.md)
- [标签分类配置](04-configuration.md)
- [数据获取与处理](03-activity-data.md)
- [变更日志生成示例](../examples/changelog-generation.md)
