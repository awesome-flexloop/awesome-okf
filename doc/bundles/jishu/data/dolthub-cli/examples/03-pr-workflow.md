---
type: Example
title: "Pull Request 协作工作流示例"
description: "dh branch/pr/release/tag/browse 的协作命令，覆盖从建分支到 PR 创建、评论、合并的完整数据协作流"
tags: [dh, dolthub, cli, pr, branch, example]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# Pull Request 协作工作流示例

> 本示例覆盖 `dh` 的数据库协作流：建分支 → 写数据 → 创建 PR → 评论 → 合并。命令形态与命令组定义一致。

## 1. 创建分支

```sh
dh branch create feature/update --db OWNER/DATABASE --from-branch main
```

分支创建需指定 `--from-branch` 或 `--from-commit` 之一（二选一）。

## 2. 在分支上写数据

```sh
dh sql --write --db OWNER/DATABASE --branch feature/update \
  "update t set v = 1 where id = 42"
```

## 3. 创建 Pull Request

```sh
dh pr create --db OWNER/DATABASE \
  --from-branch feature/update --to-branch main \
  --title "Update v" --description "描述改动"
```

## 4. 评论与列表

```sh
dh pr comment --db OWNER/DATABASE 42 --body "reviewed"
dh pr list --db OWNER/DATABASE
dh pr view --db OWNER/DATABASE 42
```

## 5. 合并

合并走异步操作，返回 OperationRef（F-043）：

```sh
dh pr merge --db OWNER/DATABASE 42
```

合并失败后可 `dh pr reopen`，或 `dh pr close` 关闭。

## 6. 打标签与发 Release

```sh
dh tag create v1.0 --db OWNER/DATABASE --from-branch main
dh release create v1.0 --db OWNER/DATABASE --title "v1.0"
```

## 7. 在浏览器查看

```sh
dh browse --db OWNER/DATABASE            # 打开仓库首页
dh browse --db OWNER/DATABASE --pull 42  # 打开 PR #42
dh browse --db OWNER/DATABASE --branch main  # 打开 main 分支
```

## 相关概念

* [仓库协作操作](/concepts/04-repository-operations.md)
* [结构化输出与异步操作](/concepts/05-output-and-operations.md)
