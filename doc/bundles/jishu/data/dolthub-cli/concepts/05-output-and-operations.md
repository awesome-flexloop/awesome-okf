---
type: Concept
title: "结构化输出与异步操作"
description: "dh 的 JSON/jq/template 结构化输出、表格渲染、异步操作轮询与游标分页，对应 F-043~F-046、F-050~F-051"
tags: [dh, dolthub, cli, json, jq, operation, pagination]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# 结构化输出与异步操作

> 本文档介绍 `dh` 的统一输出机制（表格 / JSON / jq / template）与异步操作抽象（Operation + 轮询 + 分页）。对应 [F-043~F-046、F-050~F-051](/references/source.md)。

`dh` 用一套统一机制处理"给人看"与"给机器看"两种输出，并把所有异步写操作收敛为单一抽象。

## 双形态表格输出

`tableprinter.Table` 根据 TTY 状态切换输出形态（F-050）：

- **终端（TTY）**：用 `text/tabwriter` 对齐，表头大写
- **非终端（管道/重定向）**：tab 分隔的纯文本行，便于脚本解析

这保证同一条命令既可交互观看，也可 `| awk` / `| cut` 处理。

## 结构化输出：JSON / jq / template

`AddJSONFlags` 给命令统一加三个 flag（F-051）：

| flag | 作用 |
|------|------|
| `--json <fields>` | 输出 JSON，仅投影指定字段 |
| `--jq <expr>` | 用 jq 表达式过滤 JSON（需配合 `--json`） |
| `--template <tpl>` | 用 Go template 格式化（需配合 `--json`） |

`--json`/`--jq`/`--template` 能力复用 GitHub CLI 的 `go-gh/v2` 库（F-051）。字段投影由 `selectFields` 用反射按字段名裁剪 JSON，避免把整份响应（含无关字段）倒给用户。

每个命令声明自己的合法 JSON 字段集，`AddJSONFlags` 在 `PreRunE` 校验——未知字段直接报用法错误。

## 异步操作统一抽象

DoltHub 的重写操作（SQL write、fork、merge、table import、Dolt CI）都是异步的。`dh` 把它们统一为 `Operation` 模型（F-043、F-046）：

- `OperationType`：import / merge / sql_write / fork / dolt_ci
- `OperationStatus`：queued / running / succeeded / failed

写操作提交后返回 `OperationRef{id, href}`，由 `operationwaiter.Waiter` 轮询至终态（F-044）。

### 轮询策略

`Waiter` 采用**指数退避 + 随机抖动**（F-044）：

- 初始 interval 1s，倍增，封顶 10s
- 每次实际延迟 = interval × (0.8 + 0.4 × rand)，即 0.8~1.2 倍抖动
- `Observe` 回调把每次状态变化喂给进度显示（`operation/progress`）
- `--no-wait` 可跳过等待，直接打印 `OperationRef`

失败时返回 `FailedError`，聚合 operation 的 `Error.Title/Detail/Code`。

## 游标分页

`pagination.Collect` 是泛型游标分页器（F-045）：把 `next_page_token` 当作不透明值逐页拉取，检测重复 token 防死循环，支持 `limit` 截断。

## 相关概念

* [SQL 查询与表导入](/concepts/03-sql-and-import.md)
* [仓库协作操作](/concepts/04-repository-operations.md)
