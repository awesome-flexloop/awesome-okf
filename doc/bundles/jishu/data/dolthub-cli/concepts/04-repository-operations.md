---
type: Concept
title: "仓库协作操作"
description: "dh 的数据库/分支/标签/Release/Pull Request 操作与仓库解析规则，对应 F-039~F-042、F-052、F-058"
tags: [dh, dolthub, cli, branch, pr, release, resolver]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# 仓库协作操作

> 本文档介绍 `dh` 的数据库/分支/标签/Release/Pull Request 操作，以及仓库定位（`--db`）的解析规则。对应 [F-039~F-042、F-052、F-058](/references/source.md)。

`dh` 复刻了 GitHub 的协作模型到数据领域：数据库仓库、分支、标签、Release、Pull Request 一一对应。

## 仓库解析

所有命令通过 `--db`（或隐藏别名 `--repo`，F-052）定位目标数据库。`repository.Parse` 支持三种写法（F-039）：

| 写法 | 示例 |
|------|------|
| `OWNER/REPO` | `dolthub/us-housing-prices` |
| `HOST/OWNER/REPO` | `www.dolthub.com/dolthub/us-housing-prices` |
| DoltHub URL | `https://www.dolthub.com/repositories/dolthub/us-housing-prices` |

未显式传 `--db` 时，`Resolver` 按优先级解析（F-040）：

```
--db 显式 → DH_REPO → 已配置默认仓库 → dolt remote -v 候选 → 交互选择
```

`ReadDoltRemotes` 会执行 `dolt remote -v` 读取本地 Dolt 仓库的 remote，并把 `doltremoteapi.dolthub.com` 归一化为 `www.dolthub.com`（F-041）。无候选时报错提示可用 `--db`、`DH_REPO` 或 `dh config set repo`（F-042）。

## 资源与操作

各资源的客户端方法按文件拆分（`databases.go`/`branches.go`/`tags.go`/`releases.go`/`pulls.go`），命令层对应 `db`/`branch`/`tag`/`release`/`pr` 命令组。

| 资源 | 典型操作 | 异步？ |
|------|---------|--------|
| 数据库（db） | create / fork / view | fork 异步（返回 OperationRef） |
| 分支（branch） | create（from branch/commit） | 否 |
| 标签（tag） | create | 否 |
| Release | create / list | 否 |
| Pull Request（pr） | create / merge / close / reopen / comment / edit / list / view | merge 异步 |

### 分支与标签的版本源

创建分支/标签时，`RevisionSource` 是一个"判别联合"——`--from-branch` 与 `--from-commit` 二选一（`cmdutil.RevisionSource` 校验恰好其一）。

### Pull Request

PR 模型区分 `PullSummary`（列表用，无 from/to 分支）与 `Pull`（详情用，含 `from_branch`/`to_branch`）（F-043 附近模型见 `models.go`）。`CreatePull` 提交后返回完整 PR，`MergePull` 走异步 merge 操作返回 `OperationRef`。

### browse：打开浏览器

`dh browse` 不调 API，只构造 Web URL 并打开浏览器（F-058）：`repositories/{owner}/{name}`，可加 `data/{branch}` 或 `pulls/{number}`。跨平台打开方式见 `browser.System.Browse`（F-059）。

## 相关概念

* [SQL 查询与表导入](/concepts/03-sql-and-import.md)
* [结构化输出与异步操作](/concepts/05-output-and-operations.md)
