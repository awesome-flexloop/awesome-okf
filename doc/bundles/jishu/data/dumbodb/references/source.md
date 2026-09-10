---
type: Reference
title: dumbodb 源码事实登记
description: "DumboDB（dolthub/dumbodb）源码信源登记——仓库元信息、Backend 三层接口、rootish 编码、BSON 编解码、VersioningBackend 接口，F-001~F-024 编号事实零推测登记"
tags: [dumbodb, dolt, source-code, golang, facts, dolthub, mongodb]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: dumbodb-repo
    resource: https://github.com/dolthub/dumbodb
    title: dolthub/dumbodb（官方仓库）
  - id: dumbodb-local
    resource: "本地克隆（tag v0.6.3，commit 7b226dac4ef1fe10ca90818a446a7cec6b458cd3）"
    title: dumbodb 源码逐文件精读
---

# dumbodb 源码事实登记

> 本文件是知识包全部正文的事实底账，编号 **F-001 ~ F-024**。所有正文中的数字、类型名、方法名、参数均可在下表找到逐字出处。

## 一、仓库元信息与整体架构

| 编号 | 事实 | 出处 |
|---|---|---|
| F-001 | 模块路径 `github.com/dolthub/dumbodb`，Go 1.26.7，slogan "MongoDB and Git had a baby"，协议目标 MongoDB 8.0.28 | go.mod + main.go |
| F-002 | 基于 FerretDB v1.24.2 适配，兼容 MongoDB 8.0 wire 协议，Apache 2.0 license | README.md + go.mod |
| F-003 | 核心包 `internal/backends` 定义三个接口：`Backend`、`Database`、`Collection` | backends.go |
| F-004 | `Backend` 是有状态长生命周期接口（thread-safe）；`Database` 和 `Collection` 是无状态临时接口 | backends.go 包文档 |
| F-005 | Contract wrappers：`BackendContract`、`DatabaseContract`、`CollectionContract` 负责 validation + tracing + resource tracking | backend.go + database.go |

## 二、设计原则与 Dolt 后端

| 编号 | 事实 | 出处 |
|---|---|---|
| F-006 | 设计原则 6 条：接口设计/状态性/不频繁查 information_schema/context per-op/error codes/参数不修改/testing | backends.go 包文档 |
| F-007 | Dolt 后端位于 `internal/backends/dolt/`，包含 ~100+ Go 文件 | ls internal/backends/dolt/ |
| F-008 | 存储层级：NBS（Normalized Block Store）→ STRT（Storage Read Trace）→ RTVL（Reference Tree Value Layer）→ ADRM → prolly.Map per collection | dolt/database.go + storage 层 |
| F-009 | `dbState` struct 字段：backend、name、dbDir、cs（*nbs.GenerationalNBS）、ns（tree.NodeStore）、vs（*dolttypes.ValueStore）、doltDB（*doltdb.DoltDB）、datasDB（datas.Database） | dolt/database.go |
| F-010 | `dbState` 并发保护：`branchWSMu sync.RWMutex` 保护 `branchWS map[string]*branchWS`；`mergeState *mergeInProgress` 跟踪进行中的合并 | dolt/database.go |

## 三、Rootish 编码与数据库解析

| 编号 | 事实 | 出处 |
|---|---|---|
| F-011 | 编码格式 `dbname@rootish`，`@` 为 `DBRootishSep` 常量分隔符 | dolt/database.go parseDatabaseName |
| F-012 | rootish 支持：branch name、commit hash、tag、祖先表达式（如 `main~2`） | dolt/database.go resolveAM |
| F-013 | percent-decoding：`feature%2Ffoo` → `feature/foo`，支持含 `/` 的分支名 | dolt/database.go |
| F-014 | `resolveAM()` 根据 rootish 类型选择 AccessMethod：`main`→working-set AM；tag→`GetDataset("refs/tags/<tag>")`；其他分支→`txnVisibleWS` | dolt/database.go |
| F-015 | `txnVisibleWS` 保证 read-your-own-writes：session dirty 时使用 session WS，否则使用当前 txn 可见 WS | dolt/database.go |
| F-016 | 所有-digit 后缀不被视为 rootish（防误判）；MaxDatabaseName=128 bytes（MongoDB 限制 63 bytes）；MaxRootish=512 bytes | dolt/database.go |

## 四、Collection 访问与 BSON 编解码

| 编号 | 事实 | 出处 |
|---|---|---|
| F-017 | `collection` struct：`db *database`、`name string`；`getMap()` 解析 DB→AM tree→Get(collection)→openCollection | dolt/collection.go |
| F-018 | `Query()` 优先检查 `naturalHint`，然后尝试 index lookup（filter 非 natural 且无 collation），否则全表扫描 | dolt/collection.go |
| F-019 | `bsonFormatVersion byte = 0x01`，prepend 到每个存储的 BSON 文档前 | dolt/bson.go |
| F-020 | `docToBSON()`：sortDocumentKeys（`_id` 保持原序）→ wire BSON encode → prepend version byte | dolt/bson.go |
| F-021 | `bsonToDoc()`：strip version byte → decode to `*types.Document`；MinMaxKey 通过 `FromDocumentRaw` 特殊处理 | dolt/bson.go |

## 五、VersioningBackend 接口

| 编号 | 事实 | 出处 |
|---|---|---|
| F-022 | `VersioningBackend` 是 40+ 方法的可选接口；非实现后端返回 "dolt versioning not supported" | backend.go VersioningBackend |
| F-023 | 方法分四类：提交管理（Commit/CherryPick/Rebase/Revert/Tag）、分支管理（Branch/Push/Fetch/Clone/Pull）、差异分析（Status/Diff/Log/Conflicts/ResolveConflict）、存储维护（GC/Undrop/PurgeDropped） | backend.go |
| F-024 | 冲突两类型：`documentEdit`（共享 _id）和 `uniqueKeyCollision`（不同 _id 争同一索引键）；Resolution 支持 "ours"/"theirs"/"custom" | backend.go ConflictInfo |
