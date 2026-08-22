---
type: Reference
title: CLI 命令参考
description: jcache CLI 全部命令、子命令和选项的完整参考
tags: [jupyter, cache, cli, command-line, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:32:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-repo
    resource: https://github.com/executablebooks/jupyter-cache
    title: jupyter-cache GitHub Repository
---

# CLI 命令参考

jupyter-cache 提供 `jcache` 命令行工具，分为四个子命令组。

## 全局选项

| 选项 | 说明 |
|------|------|
| `-V, --version` | 显示版本号 |
| `-v, --verbose` | 详细输出 |
| `-p, --cache-path PATH` | 指定缓存路径（默认 `./.jupyter_cache`） |
| `--help` | 显示帮助信息 |

## jcache cache（缓存管理）

管理已执行的notebook缓存记录。

| 命令 | 说明 |
|------|------|
| `jcache cache list` | 列出所有缓存的notebook |
| `jcache cache show <pk>` | 显示指定缓存记录详情 |
| `jcache cache add <path>` | 添加已执行的notebook到缓存 |
| `jcache cache remove <pk>` | 删除指定缓存记录 |
| `jcache cache clear` | 清空所有缓存 |
| `jcache cache limit` | 显示缓存大小限制 |
| `jcache cache limit <size>` | 设置缓存大小限制 |

## jcache notebook（Notebook管理）

管理项目中的notebook。

| 命令 | 说明 |
|------|------|
| `jcache notebook list` | 列出项目中的notebook |
| `jcache notebook add <path>` | 添加notebook到项目 |
| `jcache notebook remove <pk/uri>` | 从项目移除notebook |
| `jcache notebook execute <pk>` | 执行指定notebook |
| `jcache notebook execute-all` | 执行所有待执行notebook |
| `jcache notebook match` | 匹配缓存到项目notebook（显示缓存命中情况） |

## jcache project（项目管理）

管理项目级别的操作。

| 命令 | 说明 |
|------|------|
| `jcache project info` | 显示项目信息（缓存路径、版本、记录数） |
| `jcache project clear` | 清空项目记录（保留缓存） |

## 命令输出状态符号

| 符号 | 含义 |
|------|------|
| ✅ [ID] | 已缓存，括号内为缓存记录ID |
| ❌ | 执行失败（有traceback） |
| ❗️ | 不可读（读取失败） |
| - | 未缓存/待执行 |

## 相关概念

- [CLI 快速入门](/concepts/05-cli-reference.md)
- [基本使用示例](/examples/basic-usage.md)
