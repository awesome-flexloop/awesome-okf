---
type: Example
title: "SQL 查询示例"
description: "dh sql 读查询与写查询的实操命令，覆盖 --ref/--file/stdin/--json 与异步写查询的 --no-wait"
tags: [dh, dolthub, cli, sql, example]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# SQL 查询示例

> 本示例覆盖 `dh sql` 的读查询与写查询。命令与源码 README 及 `sql.go` 定义一致。

## 读查询

对某分支/标签/提交执行只读查询（F-053）：

```sh
dh sql --db OWNER/DATABASE --ref main "select * from table_name limit 10"
```

SQL 也可来自文件或管道（`--file -` 表示 stdin）：

```sh
dh sql --db OWNER/DATABASE --ref main --file query.sql
echo "select 1" | dh sql --db OWNER/DATABASE --ref main
```

结构化结果用 `--json` 投影字段（F-054，读模式合法字段：columns/message/rows/status/warnings）：

```sh
dh sql --db OWNER/DATABASE --ref main \
  --json columns,rows,status "select * from t limit 5"
```

## 写查询

写查询是异步的：`--branch` 为目标分支，可选 `--from-branch` 指定创建 feature 分支时的 base（F-053、F-055）：

```sh
dh sql --write --db OWNER/DATABASE --branch main \
  "update table_name set value = 1 where id = 42"

dh sql --write --db OWNER/DATABASE --branch feature/update \
  --from-branch main --file update.sql
```

写命令默认等待完成并显示操作状态；`--no-wait` 立即打印已接受的 OperationRef（F-055）：

```sh
dh sql --write --db OWNER/DATABASE --branch main --no-wait \
  "delete from t where id = 0"
```

## 相关概念

* [SQL 查询与表导入](/concepts/03-sql-and-import.md)
* [表导入示例](/examples/02-table-import.md)
