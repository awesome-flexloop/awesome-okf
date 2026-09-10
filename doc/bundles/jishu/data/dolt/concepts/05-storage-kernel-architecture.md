---
okf_version: "0.2"
type: concept
title: 存储内核架构
description: "dolthub/dolt 主仓存储层源码解读——Noms Block Store（NBS）、Prolly Tree、Flatbuffer 序列化与 DoltDB 高层句柄，F-157~F-182"
tags: [dolt, storage, nbs, prolly-tree, flatbuffer, source-code]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-main-repo
    resource: https://github.com/dolthub/dolt
    title: "dolthub/dolt 官方主仓"
  - id: dolt-main-local
    resource: "external/dao/action/DoltHub/dolt（HEAD 65bd3306b0，tag v2.3.2）"
    title: "Dolt 主仓源码逐文件精读"
---

# 存储内核架构

> 本文档覆盖 Dolt 的存储内核层，包括 Noms Block Store（NBS）、Prolly Tree、Flatbuffer 序列化与 DoltDB 高层句柄。对应 F-157~F-182。
> **信源距离**：① 官方源码（本地克隆 `external/dao/action/DoltHub/dolt`）。

---

## 一、存储架构全景

Dolt 的存储层由两大部分组成：

```
┌─────────────────────────────────────────────────────┐
│                   DoltDB（高层句柄）                  │
│  ResolveHash / ResolveCommitRef / ResolveWorkingSet  │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐      ┌───────────────┐
│  Prolly Tree  │      │  Noms Block   │
│  (NodeStore)  │      │     Store     │
│               │      │     (NBS)     │
│ - 行级 diff   │      │               │
│ - 值寻址      │      │ - 内容寻址    │
│ - O(1)历史   │      │ - DAG 存储    │
└───────┬───────┘      └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    ▼
          Flatbuffer 序列化
          （21 个 .fbs 文件）
```

> **F-157**

---

## 二、Noms Block Store（NBS）

### 2.1 核心概念

NBS（Noms Block Store）是 Dolt 的底层块存储引擎，继承自 Noms 项目：

- **内容寻址**：每个 chunk 由其内容的 SHA3-256 哈希唯一标识
- **DAG 结构**：chunk 之间通过引用形成有向无环图
- **不可变追加**：无 update/delete，只有 insert + update root + GC
- **多后端支持**：S3、GCS、OCI、Git、Azure Blob、OSS、本地文件、本地 journal

> **F-112 ~ F-113**

### 2.2 ChunkStore 接口

[Dolt 的 chunk_store.go](https://github.com/dolthub/dolt/blob/main/go/store/chunks/chunk_store.go) 定义了 13 个方法：

```go
type ChunkStore interface {
    Get(hash.Hash) ([]byte, error)
    GetMany(hashes HashSet) -> Channel
    Has(hash.Hash) (bool, error)
    HasMany(hashes HashSet) -> Channel
    Put(hash.Hash, []byte) error
    Version() string
    AccessMode() AccessMode
    Rebase() error
    Root() (hash.Hash, error)
    Commit(expected, actual hash.Hash) error
    Stats() Stats
    PersistGhostHashes([]hash.Hash) error
    Close() error
    Teardown()
}
```

> **F-109 ~ F-111**

### 2.3 Commit 原子性保证

`Put()` 只保证内存可见性，真正的持久化由 `Commit()` 通过 CAS（Compare-And-Swap）乐观锁保证：

```
Put(chunk) → 写入内存 buffer
Commit(expectedRoot, newRoot) → CAS 推进 manifest root
GC() → 清理孤儿 chunk
```

若两个并发 writer 同时 commit，CAS 失败的一方回退重试。

> **F-116**

### 2.4 Manifest 结构

[manifest.go](https://github.com/dolthub/dolt/blob/main/go/store/nbs/manifest.go) 中 `manifestContents`：

```go
type manifestContents struct {
    manifestVers uint64   // manifest 版本号
    nbfVers      string   // Noms 格式版本
    appendix     []byte   // 扩展数据
    specs        []Spec   // 后端规格
    lock         []byte   // 分布式锁
    root         hash.Hash // 当前 root
    gcGen        uint64   // GC 代数
}
```

> **F-114**

### 2.5 Chunk Journal

[journal.go](https://github.com/dolthub/dolt/blob/main/go/store/nbs/journal.go) 实现两种布局：

| 布局 | 特点 |
|------|------|
| 单文件布局 | 所有 chunk 写入单一 journal 文件，适合小数据集 |
| Table file 布局 | 按大小分片，支持并发写入，适合生产环境 |

两者互斥——同一 store 不能同时使用两种布局。

> **F-115**

---

## 三、Prolly Tree 存储引擎

### 3.1 核心思想

Prolly Tree（PERSISTENT R-OoseVELT tree）是 Dolt 的行级版本控制核心：

- **值寻址**：键按值哈希排序，而非按插入位置
- **行级 diff**：两个版本的 Prolly Tree 差异可在 O(n) 时间内计算
- **历史视图**：每个 commit 保留一份完整的 Prolly Tree 快照（通过 copy-on-write）

> **F-125**

### 3.2 NodeStore 接口

[Prolly Tree 的 NodeStore](https://github.com/dolthub/dolt/blob/main/go/store/prolly/tree/node.go) 接口：

```go
type NodeStore interface {
    Read(addr hash.Hash) (node.Node, error)
    ReadMany(addrs []hash.Hash) (Channel, error)
    Write(nodes []node.Node) ([]hash.Hash, error)
    Pool() pool.Pool
    Format() *types.Format
    PurgeCaches()
}
```

> **F-121**

### 3.3 不可变映射（StaticMap）

[tree/map.go](https://github.com/dolthub/dolt/blob/main/go/store/prolly/tree/map.go)：

```go
type StaticMap[K, V, O ordering.Ordering] interface {
    Mutate() MutableMap[K, V, O]
    Get(key K) (V, bool, error)
    Has(key K) (bool, error)
    IterAll() (Iterator, error)
    HashOf() (hash.Hash, error)
}
```

### 3.4 可变映射（MutableMap）

[tree/mutable_map.go](https://github.com/dolthub/dolt/blob/main/go/store/prolly/tree/mutable_map.go)：

```go
type MutableMap[K, V, O] struct {
    Edits *skip.List  // 追加的编辑记录
    Static M           // 底层不可变映射
}

func (m *MutableMap) Put(key K, value V) error
func (m *MutableMap) Delete(key K) error
func (m *MutableMap) Get(key K) (V, bool, error)
func (m *MutableMap) Mutations() (*skip.List, error)
```

### 3.5 AddressMap

[address_map.go](https://github.com/dolthub/dolt/blob/main/go/store/prolly/address_map.go) 实现 dataset 名→地址的映射树，file id 为 `"ADRM"`。

> **F-122 ~ F-124**

---

## 四、Flatbuffer 序列化

### 4.1 核心数据结构

[go/serial/fileidentifiers.go](https://github.com/dolthub/dolt/blob/main/go/serial/fileidentifiers.go) 定义了 21 个 `.fbs` 文件的 file id 常量：

| File ID | 文件名 | 用途 |
|---------|--------|------|
| `"STRT"` | `storeroot.fbs` | Store 根节点 |
| `"DCMT"` | `commit.fbs` | Commit 对象 |
| `"RTVL"` | `rootvalue.fbs` | Root 值（表集合） |
| `"DTBL"` | `table.fbs` | 表定义 |
| `"ADRM"` | `addressmap.fbs` | 地址映射树 |
| `"CMCL"` | `commitclosure.fbs` | Commit 闭包（祖先链） |
| `"DTAG"` | `tag.fbs` | 标签 |
| `"WRST"` | `workingset.fbs` | 工作集 |
| `"BLOB"` | `blob.fbs` | Blob 数据 |

> **F-126 ~ F-127**

### 4.2 Commit 结构

[commit.fbs](https://github.com/dolthub/dolt/blob/main/go/serial/commit.fbs)：

```flatbuffers
table Commit {
    hash: [byte];          // 20 字节内容哈希
    parents: [byte];       // 父 commit 哈希数组
    committer: string;     // 提交者姓名
    email: string;         // 提交者邮箱
    message: string;       // 提交消息
    stats: Stats;          // 变更统计
}
```

### 4.3 RootValue 结构

[rootvalue.fbs](https://github.com/dolthub/dolt/blob/main/go/serial/rootvalue.fbs)：

```flatbuffers
table RootValue {
    tables: [Hash];        // 表名 → 根哈希映射
    indexes: [Hash];       // 索引根哈希
    foreignKeys: [ForeignKey];
    constraints: [Constraint];
}
```

> **F-128 ~ F-129**

---

## 五、DoltDB 高层句柄

### 5.1 DoltDB 结构

[doltdb.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/doltdb/doltdb.go) 是 Dolt 的核心句柄：

```go
type DoltDB struct {
    db              hooksDatabase
    vrw             types.ValueReadWriter
    ns              tree.NodeStore
    databaseName    string
    commitCache     *lru.Cache[hash.Hash, *OptionalCommit]
}
```

> **F-131**

### 5.2 核心解析方法

| 方法 | 行号 | 功能 |
|------|------|------|
| `Resolve(hash)` | :532 | 自动判断类型（commit/tag/workingset） |
| `ResolveHash(hash)` | :561 | 解析为 Commit |
| `ResolveCommitRef(refStr)` | :634 | 解析引用字符串为 Commit |
| `ResolveWorkingSet(refStr)` | :760 | 解析引用字符串为 WorkingSet |

**负向证据**：源码中**不存在** `ResolveCommit()` 和 `ResolveRootValue()` 方法。

> **F-132 ~ F-133**

### 5.3 构造模式

```go
func DoltDBFromCS(cs chunks.ChunkStore, name string) (*DoltDB, error) {
    vrw := types.NewValueStore(cs)
    ns := tree.NewNodeStore(cs)
    db := datas.NewDatabase(vrw, ns)
    return NewDoltDB(db, name), nil
}
```

> **F-134**

---

## 六、Commit 模型

### 6.1 Commit 结构

[commit.go](https://github.com/dolthub/dolt/blob/main/go/store/datas/commit.go)：

```go
type Commit struct {
    val  types.Value   // 工作集值
    addr hash.Hash   // 内容哈希
    height uint64    // commit 高度
}
```

> **F-117 ~ F-118**

### 6.2 Commit 高度计算

```go
// commit.height = max(parent heights) + 1
func (c *Commit) Height() uint64 {
    maxParentHeight := uint64(0)
    for _, parentAddr := range c.Parents() {
        parent := c.store.Commit(parentAddr)
        if parent.Height() > maxParentHeight {
            maxParentHeight = parent.Height()
        }
    }
    return maxParentHeight + 1
}
```

### 6.3 Parent Closure

`parent_closure` 写入 NodeStore（file id `"CMCL"`），支持 O(log n) 祖先查询。这使 `dolt log` 和 `has_ancestor()` 函数能够高效遍历提交历史。

> **F-119 ~ F-120**

---

## 七、源码阅读路径

推荐阅读顺序：

```
store/datas/database.go（Database 接口）
    ↓
store/datas/commit.go（Commit 模型）
    ↓
store/nbs/README.md + store.go（NBS 架构）
    ↓
store/prolly/doc.go（Prolly Tree 设计）
    ↓
store/prolly/tree/map.go（不可变映射）
    ↓
store/prolly/tree/mutable_map.go（可变映射）
    ↓
serial/fileidentifiers.go（Flatbuffer 标识）
    ↓
libraries/doltcore/doltdb/doltdb.go（DoltDB 句柄）
```

> **F-187**

---

## 八、关键设计决策

### 8.1 为什么用 Prolly Tree 而非 B+ Tree？

| 特性 | B+ Tree | Prolly Tree |
|------|---------|-------------|
| 寻址方式 | 位置寻址 | 值寻址 |
| 版本快照 | 需完整复制 | copy-on-write |
| 行级 diff | O(n) 遍历 | O(n) 合并 |
| 并发写入 | 锁竞争 | 无锁 append |

> **F-125**

### 8.2 为什么用 Flatbuffer 而非 Protobuf？

- Flatbuffer 支持零拷贝读取，适合存储层频繁序列化/反序列化场景
- 无需解析即可访问嵌套字段，降低 CPU 开销

> **F-128 ~ F-130**

---

*本文档基于源码事实（F-157~F-182）生成，信源距离 ①。*
