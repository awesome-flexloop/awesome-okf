---
type: Concept
title: "SQL 查询与表导入"
description: "dh sql 的读/写查询、table import 的分片上传与异步导入流程，对应 F-047~F-057"
tags: [dh, dolthub, cli, sql, import, upload]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# SQL 查询与表导入

> 本文档拆解 `dh sql`（读/写查询）与 `dh table import`（分片上传 + 异步导入）两条核心数据链路。对应 [F-047~F-057](/references/source.md)。

`dh` 的两条"数据主链路"体现了 DoltHub 云 API 的设计哲学：**读同步、写异步、重操作分片上传**。

## SQL 查询

`dh sql` 分读/写两种模式（F-053）：

| 模式 | 关键 flag | 行为 |
|------|----------|------|
| 读查询 | `--ref`（必须） | 同步返回结果集 |
| 写查询 | `--write` + `--branch`（必须） | 异步提交，返回 OperationRef |

SQL 来源有三种：命令行参数、`--file`（`-` 表示 stdin）、管道 stdin（F-053，源码 `readQuery`）。

**读查询**走 `RunSQLRead`（POST `/databases/{owner}/{db}/sql`，body 编码），同步返回 `QueryResult`（F-054）：

```sh
dh sql --db OWNER/DATABASE --ref main "select * from table_name limit 10"
```

**写查询**走 `RunSQLWrite`（POST `/databases/{owner}/{db}/sql-writes`），异步返回 `OperationRef`，默认等待完成，`--no-wait` 跳过（F-055）：

```sh
dh sql --write --db OWNER/DATABASE --branch main \
  "update table_name set value = 1 where id = 42"
```

## 表导入：分片上传

`dh table import` 支持 CSV / PSV / XLSX / JSON（JSON 需 `--update`/`--replace`），`--overwrite`/`--update`/`--replace` 互斥（F-056）。

导入流程四步（F-057）：

1. `CreateImportUpload`——向 API 申请分片上传会话，返回 token、contents_key、各 part 的预签名 URL
2. `upload.File`——本地并发上传分片
3. `CreateImport`——提交完整导入（含各 part 的 ETag 与整体 MD5）
4. `operationwaiter.Waiter`——轮询导入操作至终态

### 上传细节

- 分片大小 5 MiB，最大文件 1 GiB（F-047）
- 4 worker 并发，最多 20 MiB part 缓冲（F-047）
- 上传客户端**刻意无 OAuth、无 cookie、无重定向**（预签名 URL 已含凭据，避免二次携带泄露）
- 每个 part 上传后计算 md5；最终 `FilePartsMD5 = md5(拼接各 part 的 base64 digest)`，与 DoltHub Web 上传器口径一致（F-048）
- 预签名 URL 10 分钟过期，失败需重启（不刷新、不续传）；400/403 提示 URL 可能过期（F-049）
- 上传前后 `Stat` 对比，文件被改动则报错重跑（F-057）

### 与 git commit 的呼应

表导入本质是"在指定 branch 上产生一次数据 commit"。`--message` 提供导入 commit message，`--primary-key` 指定主键列（逗号分隔或重复 flag）。

## 相关概念

* [结构化输出与异步操作](/concepts/05-output-and-operations.md)
* [仓库协作操作](/concepts/04-repository-operations.md)
