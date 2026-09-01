---
type: Reference
title: 节点与 Inode 管理 API 参考
description: src/node.rs 源码参考——NodeArena、OvlNode、InodeTable、OvlIno、NodeId、InodeKey、DirState 完整 API 与数据结构
tags: [reference, api, node, inode, nodearena, inodetable, directory, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: fuse-overlay-node
    title: src/node.rs
    path: external/dao/action/Containers/fuse-overlayfs/src/node.rs
---

# 节点与 Inode 管理 API 参考

> 信源文件：node.rs

本文档记录 fuse-overlayfs 的节点（Node）与 inode 管理 API，包括 `NodeArena`（节点竞技场）、`OvlNode`（叠加节点）、`InodeTable`（inode 表）、`OvlIno`（inode 条目）等核心数据结构。

---

## 全局统计原子变量 [F-013]

用于 SIGUSR1 运行时统计报告。

```rust
pub static STAT_NODES: AtomicU64;
pub static STAT_INODES: AtomicU64;
pub static STAT_PASSTHROUGH: AtomicBool;
```

| 变量 | 类型 | 说明 |
|------|------|------|
| `STAT_NODES` | `AtomicU64` | 当前已分配节点总数 |
| `STAT_INODES` | `AtomicU64` | 当前已分配 inode 总数 |
| `STAT_PASSTHROUGH` | `AtomicBool` | passthrough 模式是否启用 |

---

## 基础类型定义

### NodeId [F-014]

节点 ID 不透明句柄，非零值。

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct NodeId(pub u64);
```

### InodeKey [F-014]

底层文件系统 inode + 设备号键，唯一标识一个底层文件。

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct InodeKey {
    pub ino: u64,
    pub dev: u64,
}
```

---

## DirState 枚举 [F-012]

目录状态，区分文件和目录，存储目录子项。

```rust
pub enum DirState {
    NotADir,
    Dir {
        children: FxHashMap<Vec<u8>, NodeId>,
        whiteouts: FxHashSet<Vec<u8>>,
        loaded: bool,
    },
}
```

### 变体说明

| 变体 | 说明 |
|------|------|
| `NotADir` | 非目录节点（普通文件、符号链接、特殊文件） |
| `Dir { children, whiteouts, loaded }` | 目录节点 |

### Dir 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `children` | `FxHashMap<Vec<u8>, NodeId>` | 子节点映射：文件名 → NodeId |
| `whiteouts` | `FxHashSet<Vec<u8>>` | whiteout 文件名集合（已删除项） |
| `loaded` | `bool` | 是否已从底层文件系统加载完整目录列表 |

---

## OvlNode 结构体 [F-017]

叠加文件系统节点，表示目录树中的一个条目。

```rust
pub struct OvlNode {
    pub parent: Option<NodeId>,
    pub dir_state: DirState,
    pub layer_idx: usize,
    pub last_layer_idx: usize,
    pub tmp_ino: u64,
    pub tmp_dev: u64,
    pub name: Vec<u8>,
    pub hidden_path: Option<String>,
    pub hidden_dirfd: i32,
    pub name_hash: u64,
    pub n_links: usize,
    pub mode: u32,
    pub do_unlink: bool,
    pub do_rmdir: bool,
    pub hidden: bool,
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `parent` | `Option<NodeId>` | 父节点 ID（根节点为 None） |
| `dir_state` | `DirState` | 目录状态（文件/目录/子项/whiteout） |
| `layer_idx` | `usize` | 节点当前所在层索引（0 = upper） |
| `last_layer_idx` | `usize` | 节点最后存在的层索引 |
| `tmp_ino` | `u64` | 底层文件系统 inode 号 |
| `tmp_dev` | `u64` | 底层文件系统设备号 |
| `name` | `Vec<u8>` | 文件名（字节） |
| `hidden_path` | `Option<String>` | 隐藏节点的临时文件路径（rename 前） |
| `hidden_dirfd` | `i32` | 隐藏节点所在目录 fd（默认 -1） |
| `name_hash` | `u64` | 文件名 FNV-1a 哈希 |
| `n_links` | `usize` | 硬链接计数 |
| `mode` | `u32` | 文件模式（类型 + 权限） |
| `do_unlink` | `bool` | 标记：需要 unlink（copy-up 时使用） |
| `do_rmdir` | `bool` | 标记：需要 rmdir（copy-up 时使用） |
| `hidden` | `bool` | 标记：节点是否为隐藏临时状态 |

### OvlNode 方法 [F-018]

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `new(...)` | `Self` | 构造新节点 |
| `is_dir(&self)` | `bool` | 判断是否为目录 |
| `is_loaded(&self)` | `bool` | 目录子项是否已加载 |
| `mark_loaded(&mut self)` | `()` | 标记目录子项已加载 |
| `mark_unloaded(&mut self)` | `()` | 标记目录子项未加载（失效缓存） |
| `get_child(&self, name: &[u8])` | `Option<NodeId>` | 获取子节点 ID |
| `children(&self)` | `impl Iterator<Item = (&Vec<u8>, &NodeId)>` | 迭代子节点 |
| `children_mut(&mut self)` | `&mut FxHashMap<Vec<u8>, NodeId>` | 获取子节点映射可变引用 |
| `insert_child(&mut self, name: Vec<u8>, id: NodeId)` | `()` | 插入子节点 |
| `remove_child(&mut self, name: &[u8])` | `Option<NodeId>` | 移除子节点 |
| `is_whiteout(&self, name: &[u8])` | `bool` | 检查文件名是否在 whiteout 集合中 |
| `insert_whiteout(&mut self, name: Vec<u8>)` | `()` | 添加 whiteout 标记 |

### Drop 实现 [F-018]

`impl Drop for OvlNode` 在节点销毁时清理资源：
- 如果 `hidden_path` 存在且 `hidden` 为 true：
  - 目录：`unlinkat` with `AT_REMOVEDIR`
  - 文件：普通 `unlinkat`

---

## NodeArena 结构体 [F-015]

节点竞技场（Arena），负责所有 OvlNode 的分配、存储和生命周期管理。

```rust
pub struct NodeArena {
    nodes: FxHashMap<NodeId, OvlNode>,
    next_id: NodeId,
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `nodes` | `FxHashMap<NodeId, OvlNode>` | 节点存储：NodeId → OvlNode |
| `next_id` | `NodeId` | 下一个待分配的节点 ID（从 1 开始） |

### NodeArena 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `new()` | `Self` | 创建新的空 NodeArena，next_id 从 1 开始 |
| `insert(&mut self, node: OvlNode)` | `NodeId` | 插入节点，分配新 NodeId；插入时 `STAT_NODES.fetch_add(1)` |
| `get(&self, id: NodeId)` | `Option<&OvlNode>` | 获取节点不可变引用 |
| `get_mut(&mut self, id: NodeId)` | `Option<&mut OvlNode>` | 获取节点可变引用 |
| `remove(&mut self, id: NodeId)` | `Option<OvlNode>` | 移除节点；移除时 `STAT_NODES.fetch_sub(1)` |
| `contains_key(&self, id: NodeId)` | `bool` | 检查节点是否存在 |

---

## OvlIno 结构体 [F-016]

Inode 条目，管理同一个底层文件的所有硬链接节点和 FUSE inode 号。

```rust
pub struct OvlIno {
    pub nodes: FxHashSet<NodeId>,
    pub lookups: AtomicI64,
    pub mode: u32,
    pub fuse_ino: u64,
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `nodes` | `FxHashSet<NodeId>` | 共享此 inode 的所有硬链接节点集合 |
| `lookups` | `AtomicI64` | FUSE lookup 引用计数（内核引用计数） |
| `mode` | `u32` | 文件模式（用于快速返回，无需重新 stat） |
| `fuse_ino` | `u64` | 分配给 FUSE 内核的 inode 号 |

---

## InodeTable 结构体 [F-019]

Inode 表，管理底层文件系统 inode 到 FUSE inode 的映射。

```rust
pub struct InodeTable {
    table: FxHashMap<InodeKey, Box<OvlIno>>,
    fuse_map: FxHashMap<u64, InodeKey>,
    same_device: bool,
    next_fallback: u64,
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `table` | `FxHashMap<InodeKey, Box<OvlIno>>` | 主映射：InodeKey(ino+dev) → OvlIno |
| `fuse_map` | `FxHashMap<u64, InodeKey>` | 反向映射：FUSE inode → InodeKey |
| `same_device` | `bool` | 是否所有层在同一设备上（决定 inode 号生成策略） |
| `next_fallback` | `u64` | 冲突回退计数器，初始值 `0x8000_0000_0000_0000` |

### InodeTable 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `new(same_device: bool)` | `Self` | 创建新的 InodeTable |
| `get(&self, key: InodeKey)` | `Option<&OvlIno>` | 按 InodeKey 查找 |
| `get_mut(&mut self, key: InodeKey)` | `Option<&mut OvlIno>` | 按 InodeKey 查找可变引用 |
| `get_by_fuse(&self, fuse_ino: u64)` | `Option<&OvlIno>` | 按 FUSE inode 查找 |
| `get_or_insert(&mut self, key: InodeKey, mode: u32)` | `&mut OvlIno` | 获取或插入 inode 条目；新条目分配 fuse_ino；插入时 `STAT_INODES.fetch_add(1)` |
| `remove(&mut self, key: InodeKey)` | `Option<Box<OvlIno>>` | 移除 inode 条目；移除时 `STAT_INODES.fetch_sub(1)` |
| `inc_lookup(&self, key: InodeKey)` | `()` | 增加 lookup 计数 |
| `dec_lookup(&self, key: InodeKey)` | `bool` | 减少 lookup 计数；返回计数是否归零 |

---

## 辅助函数

### compute_fuse_ino() [F-020]

```rust
pub fn compute_fuse_ino(ino: u64, dev: u64, same_device: bool) -> u64
```

计算分配给 FUSE 内核的 inode 号：
- **同设备模式**（`same_device = true`）：直接使用底层 ino；若 ino <= 1，加 2 避免保留值（0 和 1）
- **跨设备模式**（`same_device = false`）：使用 FNV-1a 哈希算法组合 ino 和 dev
- **保证**：结果永不为 0 或 1（FUSE 保留值）

### compute_path() [F-021]

```rust
pub fn compute_path(arena: &NodeArena, id: NodeId) -> Vec<u8>
```

通过父指针链从节点计算完整路径：
- 根节点返回 `b"."`
- 子节点从当前节点向上遍历，拼接 parent/name
- 返回从根到节点的完整相对路径（字节）

### FNV-1a 哈希 [F-022]

文件名哈希使用 FNV-1a 算法：
- `FNV_OFFSET_BASIS = 0xcbf29ce484222325`
- `FNV_PRIME = 0x100000001b3`
