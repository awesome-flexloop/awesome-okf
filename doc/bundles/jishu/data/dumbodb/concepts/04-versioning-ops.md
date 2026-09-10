---
type: Concept
title: 版本化操作与冲突模型
description: "dumbodb VersioningBackend 40+ 可选接口、Commit/Branch/Merge/Diff/Log 操作、documentEdit/uniqueKeyCollision 冲突模型、Resolution 策略。F-022~F-024。"
tags: [dumbodb, versioning, dolt, conflict]
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

# 版本化操作与冲突模型

> **对应 F 编号**：F-022 ~ F-024

## VersioningBackend 可选接口（F-022）

`VersioningBackend` 是 dumbodb 将 Dolt 版本控制能力插件化的核心设计：

```go
type VersioningBackend interface {
    // 提交管理
    DumboDBCommit(ctx, params) (CommitResult, error)
    DumboDBCherryPick(ctx, params) error
    DumboDBRebase(ctx, params) error
    DumboDBRevert(ctx, params) error
    DumboDBTag(ctx, params) error

    // 分支管理
    DumboDBBranch(ctx, params) ([]BranchInfo, error)
    DumboDBPush(ctx, params) error
    DumboDBFetch(ctx, params) error
    DumboDBClone(ctx, params) error
    DumboDBPull(ctx, params) error

    // 差异分析
    DumboDBStatus(ctx, params) (StatusInfo, error)
    DumboDBDiff(ctx, params) ([]CollectionDiff, error)
    DumboDBLog(ctx, params) ([]CommitInfo, error)
    DumboDBConflicts(ctx, params) ([]ConflictInfo, error)
    DumboDBResolveConflict(ctx, params) error

    // 存储维护
    DumboDBGC(ctx, params) (GCResult, error)
    UndropDatabase(ctx, params) error
    ListDroppedDatabases(ctx) ([]DroppedDB, error)
    PurgeDroppedDatabases(ctx, params) error
}
```

**非实现后端**：如果 Backend 未实现 `VersioningBackend`，所有上述方法返回 `"dolt versioning not supported"` 错误。

## 方法分类

| 类别 | 方法 | 说明 |
|------|------|------|
| **提交管理** | Commit、CherryPick、Rebase、Revert、Tag | 创建版本快照、拣选/变基/还原提交、打标签 |
| **分支管理** | Branch、Push、Fetch、Clone、Pull | 创建/删除/列出分支、远程同步 |
| **差异分析** | Status、Diff、Log、Conflicts、ResolveConflict | 查看工作集状态、比较版本差异、解决冲突 |
| **存储维护** | GC、UndropDatabase、ListDroppedDatabases、PurgeDroppedDatabases | 垃圾回收、恢复/清除已删除数据库 |

## Commit 参数与结果（F-012）

```go
type CommitParams struct {
    DBName       string
    Branch       string
    Message      string
    Author       string  // 必填
    Committer    string  // 可选，默认同 Author
    Timestamp    int64   // 可选，Unix ms
    AllowEmpty   bool    // 允许空提交
}

type CommitResult struct {
    CommitID           string
    Branch             string
    Message            string
    Author             string
    Timestamp          int64   // Unix ms
    Committer          string
    CommitterTimestamp int64
}
```

特殊错误：`ErrEmptyCommit = "nothing to commit, working tree clean"`

## Branch 操作（F-013）

```go
type BranchParams struct {
    DBName string
    Action string  // "add" / "update" / "remove" / "list"
    From   string  // 连接 rootish
    Name   string
    Force  bool    // remove 时强制删除
}

type BranchConfigUpdate struct {
    PullRemote   string
    PullBranch   string
    PullRebase   bool
    PullFF       string  // "fast-forward" / "no-fast-forward" / "never"
    PushRemote   string
    PushBranch   string
}

type BranchInfo struct {
    Name           string
    CommitID       string
    Pull           *BranchConfigUpdate
    Push           *BranchConfigUpdate
    RemoteTracking string
    Remote         string
    Ref            string
}
```

## Log & Diff（F-014）

```go
type LogParams struct {
    DBName  string
    Branch  string
    ConnBranch string  // 连接所在分支
    Limit   int
    From    string  // seed frontier（起始 commit）
    Stat    bool    // 显示统计
    Patch   bool    // 显示 patch
    All     bool    // 所有分支
}

type DiffParams struct {
    DBName    string
    ConnRootish string  // 连接 rootish
    From      string  // 起始版本（empty = HEAD）
    To        string  // 目标版本（empty = working set）
}
```

## 冲突模型（F-023）

dumbodb 定义两种冲突类型：

### 类型一：documentEdit（共享 _id 冲突）

```
Base:      { _id: 1, name: "Alice" }
Our edit:  { _id: 1, name: "Alice (us)" }
Their edit:{ _id: 1, name: "Alice (them)" }
```

两个分支对**同一文档**（相同 `_id`）做了不同修改，合并时产生冲突。

### 类型二：uniqueKeyCollision（不同 _id 争同一索引键）

```
Our doc:   { _id: 1, email: "a@example.com" }  ← unique index on email
Their doc: { _id: 2, email: "a@example.com" }  ← unique index on email
```

两个不同文档（不同 `_id`）争用同一个**唯一索引键**，违反唯一性约束。

### ConflictInfo 结构（F-023）

```go
type ConflictInfo struct {
    ConflictID    string         // 冲突唯一标识
    Type          ConflictType   // "documentEdit" 或 "uniqueKeyCollision"
    Base          *types.Document
    Ours          *types.Document
    Theirs        *types.Document
    OurDiffType   DiffType
    TheirDiffType DiffType
    Reason        string
}
```

## 冲突解决（F-024）

```go
type Resolution string
const (
    ResolutionOurs   Resolution = "ours"    // 保留我们的版本
    ResolutionTheirs Resolution = "theirs"  // 保留他们的版本
    ResolutionCustom Resolution = "custom"  // 自定义合并
)

// 解决单个冲突
err := backend.DumboDBResolveConflict(ctx, ResolveConflictParams{
    DBName:    "mydb",
    ConflictID: "conflict-123",
    Resolution: ResolutionOurs,
})
```

支持三种解决策略：
- `"ours"`：保留当前分支的版本
- `"theirs"`：接受被合并分支的版本
- `"custom"`：提供自定义文档作为合并结果

**不支持三方自动合并**——当两种策略都无法解决时，需人工介入。

## 自定义命令体系（F-024）

dumbodb 提供一组 MongoDB custom commands 封装版本控制操作：

| 命令 | 对应 Go 方法 | 说明 |
|------|-------------|------|
| `dumboCommit` | DumboDBCommit | 提交当前工作集 |
| `dumboBranch` | DumboDBBranch | 分支 CRUD |
| `dumboMerge` | DumboDBMerge | 合并分支 |
| `dumboLog` | DumboDBLog | 查看提交历史 |
| `dumboStatus` | DumboDBStatus | 查看工作集状态 |
| `dumboDiff` | DumboDBDiff | 比较版本差异 |
| `dumboConflicts` | DumboDBConflicts | 列出冲突 |
| `dumboResolveConflict` | DumboDBResolveConflict | 解决冲突 |
| `dumboGC` | DumboDBGC | 垃圾回收 |
| `dolt*` | 同上（别名） | `doltCommit` 等前缀别名也支持 |

使用示例：

```javascript
// mongosh 中执行
db.adminCommand({ dumboCommit: 1, branch: "main", message: "save work" })
db.adminCommand({ dumboBranch: 1, action: "list" })
db.adminCommand({ dumboLog: 1, limit: 10 })
```

## 学习路径

回到上一节：
* [BSON 存储](03-bson-storage.md) — 理解文档如何存储到底层
* 回到 overview — 理解整体架构定位
