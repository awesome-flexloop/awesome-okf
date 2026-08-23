---
type: Concept
title: Checkpoint 与恢复
description: Checkpoint 系统——types/blob/load 三层、会话恢复、rewind 事务、fork/branch 分支、内容寻址 blob 存储
tags: [deepseek-reasonix, checkpoint, recovery, rewind, blob, fork, branch]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## Checkpoint 系统概述

`internal/checkpoint` 包实现 Reasonix 的文件突变捕获、检查点持久化和事务化回滚系统。它不止是"保存快照"，而是带冲突检测的两阶段提交恢复机制。

## Schema 版本

```go
const (
    SchemaV1 = 1
    SchemaV2 = 2
    SchemaV3 = 3
)
```

v1 checkpoint 加载时标记为 `legacy_unverified`——无法验证后续手动编辑。v2 引入 per-file preimage + after fingerprint。v3 使用 turn 目录结构。（F-081）

## 覆盖度

```go
type Coverage string

const (
    CoverageComplete Coverage = "complete"
    CoveragePartial  Coverage = "partial"
    CoverageNone     Coverage = "none"
    CoverageLegacy   Coverage = "legacy"
)
```

覆盖度差距原因包括：`bash_side_effect`、`hook_write`、`mcp_external`、`outside_workspace`、`symlink`、`background_writer_cross_turn`、`legacy_unverified` 等。（F-082）

## FileRevision

每个被跟踪文件的修订记录：

```go
type FileRevision struct {
    Path          string
    Existed       bool
    Mode          uint32
    Encoding      *fileenc.Kind
    SHA256        string
    BlobRef       string
    CaptureSource CaptureSource
    AfterSHA256   string
    AfterExisted  *bool
    Content       *string  // 仅内存存储或 v1 迁移
}
```

`CaptureSource` 标识 preimage 获取方式：`previewer`、`before_mutation`、`after_mutation`、`legacy`、`manual`。（F-083）

## BlobStore：内容寻址存储

`BlobStore` 以 SHA-256 hex 命名 blob 文件，原子写入：

```go
type BlobStore struct {
    dir string
    mu  sync.Mutex
}

func (b *BlobStore) Put(data []byte) (string, error) {
    sum := sha256.Sum256(data)
    ref := hex.EncodeToString(sum[:])
    // 已存在且大小+校验匹配则跳过
    // 否则 AtomicWriteFileStrict 写入
    return ref, nil
}

func (b *BlobStore) Get(ref string) ([]byte, error) {
    data, _ := os.ReadFile(b.path(ref))
    if got := Digest(data); got != ref {
        return nil, fmt.Errorf("blob %s failed content-address verification", ref)
    }
    return data, nil
}
```

Blob 目录通常位于 `<session>.ckpt/blobs`。Get 时验证内容校验和，防止损坏。（F-086）

默认保留策略：

| 常量 | 值 | 说明 |
|------|-----|------|
| `DefaultRetainCheckpoints` | 100 | 最大检查点数 |
| `DefaultBlobQuotaBytes` | 1 GiB | blob 存储配额 |
| `DefaultMaxFileBytes` | 32 MiB | 单文件捕获上限 |

（F-087）

## Rewind 回滚

### 回滚范围

```go
type RewindScope int

const (
    RewindCode         RewindScope = iota // 文件 only
    RewindConversation                    // 消息日志 only
    RewindBoth                            // 两者
)
```

（F-084）

### 回滚计划

`RewindPlan` 是预检查结果，返回给 Controller/UI：

```go
type RewindPlan struct {
    PlanID             string
    Turn               int
    Scope              RewindScope
    Coverage           Coverage
    CoverageGaps       []CoverageGap
    CanFiles           bool
    CanConversation    bool
    Conflicts          []RewindConflict
    Files              []string
    FileCount          int
    ActiveWriters      []ActiveWriter
    HasBoundary        bool
    // ...
}
```

冲突类型（11 种）：`manual_edit`、`external_change`、`deleted_and_recreated`、`type_change`、`mode_change`、`missing_payload`、`path_unsafe`、`active_writer`、`stale_plan`、`boundary_invalid`、`legacy_unverified`。（F-085 隐含）

### 事务状态机

```go
type TransactionState string

const (
    TxPrepared   TransactionState = "prepared"
    TxCommitting TransactionState = "committing"
    TxCommitted  TransactionState = "committed"
    TxAborted    TransactionState = "aborted"
    TxUndone     TransactionState = "undone"
)
```

`TransactionManifest` 是持久化的事务描述：

```go
type TransactionManifest struct {
    SchemaVersion   int
    ID              string
    State           TransactionState
    Kind            string  // rewind|undo|file_revert
    Scope           RewindScope
    Targets         []TransactionTarget
    ConversationForward []byte
    CheckpointBackup []byte
    ParentTransaction string
}
```

每个 `TransactionTarget` 包含双份载荷：
- **Restore**：checkpoint 状态（要写入/删除的内容）
- **Forward**：prepare 时的当前磁盘状态（用于 compensate/undo）
- **PublishTmp/BackupPath**：事务唯一的暂存路径

（F-085）

### 两阶段提交流程

1. **Prepare**：将当前文件复制到 backup，checkpoint 文件写到 staging tmp，设置 `Published` 标记
2. **Commit**：rename 发布，`Published` 标记在首次 rename 前持久化
3. **Crash recovery**：重启后检查 `Published` 标记，保守地检查目标

`RewindResult` 返回操作结果，包含 `UndoAvailable`（是否可撤销）、`ConversationForked`（对话是否被 fork）、`Partial`（部分完成）等字段。

## Checkpoint 加载

`Store.load()` 按 turn 编号选择检查点：
- 读取当前目录和 expired 目录中的 `turn-N.json`
- 同 turn 选择时间戳更新的
- 时间戳相同时，非 expired 优先（priority 2 > 1）
- v1 schema 标记为 `legacy_unverified` coverage gap
- expired payload 的 BlobRef 被清空，标记 `ExpiredFilePayload`

（F-088）

## Fork 与 Branch

### ForkBundle

`ForkBundle` 冻结完整 turn 状态用于策略实验：

```go
type ForkBundle struct {
    Version        int                `json:"version"`  // 1
    Policy         string             `json:"policy"`
    Input          string             `json:"input"`
    EligibleRound  int                `json:"eligible_round"`
    DebtAtFork     int                `json:"debt_at_fork"`
    LocalExecSeen  bool               `json:"local_exec_seen"`
    Messages       []provider.Message `json:"messages"`
}
```

用于 EBM（Evidence-Based Modeling）、reasoning governor、delegation admission 等实验的 A/B 对照。control 和 treatment 从完全相同的冻结点开始。（F-053, F-054）

### BranchMeta

`BranchMeta` 将扁平 session 文件转化为可导航的对话树：

```go
type BranchMeta struct {
    ID               string    `json:"id"`
    Name             string    `json:"name,omitempty"`
    ParentID         string    `json:"parent_id,omitempty"`
    ForkTurn         int       `json:"fork_turn,omitempty"`
    ForkMessageIndex int       `json:"fork_message_index,omitempty"`
    CreatedAt        time.Time `json:"created_at"`
    WorkspaceRoot    string    `json:"workspace_root,omitempty"`
    Model            string    `json:"model,omitempty"`
    QualityFloor     string    `json:"quality_floor,omitempty"`
    ToolApprovalMode string    `json:"tool_approval_mode,omitempty"`
    Goal             string    `json:"goal,omitempty"`
    Recovered        bool      `json:"recovered,omitempty"`
    // ...
}
```

会话本身仍在 `.jsonl` 文件中，元数据位于 `<session>.meta` sidecar。（F-055）

## MutationObserver

`MutationObserver` 是主机端统一文件突变观察器：
- 在工具运行前捕获 preimage
- 工具运行后记录 fingerprint（无论结果如何）
- 不影响 provider-visible 的 schema 或 prompt
- 通过 `Agent.SetMutationObserver` 安装
- TaskTool 继承 observer 给 sub-agent

## 相关概念

- [Agent 运行循环](/concepts/02-agent-run-loop.md)——checkpoint 如何集成到 turn 生命周期
- [Fleet 与 Subagent](/concepts/07-fleet-subagents.md)——后台 writer 的 checkpoint 影响
- [项目架构](/concepts/01-project-architecture.md)——checkpoint 在 boot 中的组装
