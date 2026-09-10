---
type: Concept
title: 架构分层
description: "dumbodb Backend→Database→Collection 三层接口、BackendContract wrapper 机制、dbState 核心状态结构。F-003~F-008。"
tags: [dumbodb, dolt, architecture]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: dumbodb-repo
    resource: https://github.com/dolthub/dumbodb
    title: dolthub/dumbodb
  - id: dumbodb-local
    resource: "本地克隆（tag v0.6.3，commit 7b226dac4ef1fe10ca90818a446a7cec6b458cd3）"
---

# 架构分层

> **对应 F 编号**：F-003 ~ F-008

## 三层接口模型

dumbodb 的存储抽象分为三层，每层职责清晰：

```
Backend（有状态，进程级单例）
    │  持有 database map（name → *database）
    │  线程安全，长生命周期
    ├── Database（无状态，每次操作创建）
    │       │  持有 collection cache
    │       │  不负责持久化
    │       └── Collection（无状态，每次操作创建）
    │               │  Query / InsertAll / UpdateAll / DeleteAll
    │               │  Stats / ListIndexes / CreateIndexes / DropIndexes
    │               └── prolly.Map per collection（Dolt 存储层）
```

## Backend 接口（F-003）

`Backend` 是顶层有状态接口，核心方法：

```go
type Backend interface {
    // 数据库操作
    CreateDatabase(ctx, name) error
    DropDatabase(ctx, name) error
    Database(ctx, name) (Database, error)
    ListDatabases(ctx) ([]string, error)

    // 生命周期
    Start(ctx) error
    Close() error

    // 可选：VersioningBackend 能力
    // （通过类型断言判断是否支持）
}
```

Backend 实现必须：
- 自行维护数据库/集合列表（不频繁查询 information_schema）
- 线程安全（多 goroutine 并发访问）
- 每个操作接受独立 context（不在 backend 层缓存 context）

## Database 接口（F-004）

`Database` 是无状态临时接口，每次操作由 Backend 创建：

```go
type Database interface {
    Collection(name string) (Collection, error)
    ListCollections(ctx) ([]CollectionInfo, error)
    // ... system collections
}
```

`CollectionInfo` 包含：
- `Name string`
- `Validator`、`ValidationLevel`、`ValidationAction`
- `Collation`、`Indexes`

## Collection 接口（F-018）

`Collection` 是最低层无状态接口：

```go
type Collection interface {
    Query(ctx, filter) (RowIter, error)
    Count(ctx, filter) (int64, error)
    Explain(ctx, filter) (map[string]interface{}, error)
    InsertAll(ctx, docs []types.Document) error
    UpdateAll(ctx, filter, update) (int64, error)
    DeleteAll(ctx, filter) (int64, error)
    Stats(ctx) (map[string]interface{}, error)
    Compact(ctx) error
    ListIndexes(ctx) ([]IndexInfo, error)
    CreateIndexes(ctx, specs []IndexSpec) error
    DropIndexes(ctx, names []string) error
}
```

关键约束：
- `InsertAll`：原子操作，自动创建 DB/collection，分配 timestamp record ID
- `UpdateAll`：支持 `FieldMutation` 实现 structural sharing（部分更新）
- `DeleteAll`：接受重复 ID，部分失败时原子回滚

## BackendContract Wrapper（F-005）

`BackendContract` 是统一校验和追踪层，对所有 Backend 方法做：
1. **Resource tracking**：跟踪打开的 Database/Collection，防止资源泄漏
2. **SessionAwareBackend 转发**：如果 Backend 实现了 `SessionAwareBackend`，转发 session 生命周期事件
3. **AutoCommitBackend 转发**：如果 Backend 实现了 `AutoCommitBackend`，在 command 边界自动提交

```
Client Call
    ↓
BackendContract.Validate()      ← 校验输入参数
    ↓
BackendContract.Track()         ← 注册资源
    ↓
Backend.Method()                ← 实际执行
    ↓
BackendContract.Untrack()       ← 清理资源
```

## dbState 核心状态（F-009~F-010）

`dbState` 是每个数据库的内部状态结构：

```go
type dbState struct {
    backend  *Backend
    name     string
    dbDir    string

    // Dolt 存储层
    cs  *nbs.GenerationalNBS   // Normalized Block Store
    ns  tree.NodeStore          // Node Store
    vs  *dolttypes.ValueStore   // Value Store
    doltDB *doltdb.DoltDB     // 版本化数据库实例
    datasDB datas.Database      // 数据访问层

    // 并发保护
    branchWSMu sync.RWMutex
    branchWS   map[string]*branchWS  // 各分支的 working set

    // 合并状态
    mergeState *mergeInProgress
}
```

常量：
- `defaultSessionTimeout = 30 * time.Minute`
- `defaultDroppedDatabaseTTL = 30 * 24 * time.Hour`（30 天）

## 存储层级（F-008）

从底层到上层：

```
NBS (Normalized Block Store)     ← 物理块存储，压缩去重
    ↑
STRT (Storage Read Trace)         ← 读路径追踪，调试用
    ↑
RTVL (Reference Tree Value Layer) ← 引用树值层，处理版本跳转
    ↑
ADRM (Access Method Resolution)   ← AccessMethod 解析
    ↑
prolly.Map per collection         ← 每集合一个 prolly tree，存储 BSON 文档
```

## 学习路径

继续阅读：
* [Rootish 编码系统](02-rootish-system.md) — 如何从 `dbname@rootish` 解析到具体 Database
* [BSON 存储](03-bson-storage.md) — Collection 层如何将 BSON 映射到 prolly.Map
