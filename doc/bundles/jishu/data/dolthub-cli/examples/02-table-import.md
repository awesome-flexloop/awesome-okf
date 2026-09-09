---
type: Example
title: "表导入示例"
description: "dh table import 的 CSV/JSON 导入命令，覆盖主键、更新模式、提交信息与 --no-wait"
tags: [dh, dolthub, cli, import, csv, example]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# 表导入示例

> 本示例覆盖 `dh table import` 的 CSV 与 JSON 导入。命令与源码 README 及 `import.go` 定义一致。

## 基本导入（创建表）

```sh
dh table import people people.csv --db OWNER/DATABASE --branch main \
  --primary-key id --message "Import people"
```

命令默认**创建表**（F-056）。主键可用逗号分隔或重复 flag：

```sh
dh table import people people.csv --db OWNER/DATABASE --branch main \
  --primary-key tenant_id --primary-key id
```

## 更新已有表

用 `--overwrite`、`--update`、`--replace` 之一导入已有表（三者互斥，F-056）：

```sh
dh table import people changes.csv --db OWNER/DATABASE --branch main --update
```

JSON 格式必须配合 `--update` 或 `--replace`（F-056）：

```sh
dh table import people changes.json --db OWNER/DATABASE --branch main --update
```

## 格式与约束

- 支持 CSV / PSV / XLSX / JSON（F-056）
- 格式从扩展名推断，或用 `--file-type` 显式指定
- `--branch` 必填（API v2 不暴露默认分支）
- 文件必须为普通、非空、≤1 GiB；不支持 stdin（F-047）
- 上传期间保持文件不变

## 跳过等待

`--no-wait` 在上传 + 提交后立即返回 OperationRef：

```sh
dh table import people people.csv --db OWNER/DATABASE --branch main \
  --primary-key id --no-wait
```

结构化输出用 `--json id,status,result` 或 `--no-wait --json id,href`。

## 相关概念

* [SQL 查询与表导入](/concepts/03-sql-and-import.md)
* [SQL 查询示例](/examples/01-sql-queries.md)
