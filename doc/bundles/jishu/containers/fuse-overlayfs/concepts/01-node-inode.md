---
type: Concept
title: 节点与 inode 管理
description: NodeArena 节点竞技场、OvlNode 叠加节点、InodeTable inode 表、OvlIno inode 条目、DirState 目录状态、路径计算、FUSE inode 号分配策略
tags: [concept, node, inode, nodearena, inodetable, filesystem, data-structure, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: facts-fuse-overlayfs
    resource: "/.trae/specs/containers-okf-wiki/facts-fuse-overlayfs.md"
    title: fuse-overlayfs 可验证事实
  - id: node-source
    resource: "/bundles/containers/fuse-overlayfs/references/node-source.md"
    title: 节点与 Inode 管理 API 参考
---

# 节点与 inode 管理

fuse-overlayfs 使用两套互补的数据结构来管理文件系统对象：
- **NodeArena（节点竞技场）**：管理目录树结构，负责路径查找和目录遍历
- **InodeTable（inode 表）**：管理底层文件的身份标识，负责硬链接聚合和 FUSE inode 号分配

这两套结构通过 `NodeId` 和 `InodeKey` 相互关联，共同构成文件系统的内存表示。

---

## 基础标识类型

### NodeId：节点句柄 [F-014]

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct NodeId(pub u64);
```

`NodeId` 是目录树中节点的**不透明句柄**：
- 从 1 开始分配（0 作为无效值保留）
- 由 NodeArena 在插入节点时分配
- 全局唯一，永远不被复用（简化并发和缓存正确性）
- 通过 `parent` 指针形成树形结构

### InodeKey：底层文件身份 [F-014]

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct InodeKey {
    pub ino: u64,
    pub dev: u64,
}
```

`InodeKey` 唯一标识一个**底层文件系统对象**：
- `ino`：底层文件系统的 inode 号（来自 `stat.st_ino`）
- `dev`：底层文件系统的设备号（来自 `stat.st_dev`）
- 同设备同 inode = 同一文件（硬链接）
- 跨设备时即使 ino 相同也是不同文件（需要哈希）

---

## DirState：目录状态 [F-012]

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

每个节点要么是文件（`NotADir`），要么是目录（`Dir`）。

### 惰性目录加载

目录子项采用**惰性加载**策略：
1. 目录节点创建时 `loaded = false`，children 为空
2. 首次 `readdir` 或路径查找触发加载：从底层文件系统读取目录项
3. 加载完成后 `loaded = true`，缓存子项映射
4. 目录修改（create/delete/rename）实时更新缓存

`loaded` 标记的重要性：如果目录未加载，不能假设 children 包含了所有子项——需要合并多层目录内容。

### children：子节点映射

`FxHashMap<Vec<u8>, NodeId>` 将文件名字节映射到 NodeId：
- 使用 `Vec<u8>` 而非 `String`：文件名可能包含非 UTF-8 字节（Linux 允许任意字节序列除 `/` 和 `\0`）
- 使用 FxHash（rustc-hash）：比标准库 HashMap 快约 2-3 倍，适合字符串键
- 只包含当前层已访问或已修改的子项（未加载的子项需要时逐层查找）

### whiteouts：删除标记

`FxHashSet<Vec<u8>>` 记录目录中已被 whiteout 的文件名：
- 下层存在但被 upper 层 whiteout 的文件不出现在合并视图中
- whiteout 通过 `.wh.<name>` 文件或 char 0/0 设备实现

---

## OvlNode：叠加节点 [F-017]

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

`OvlNode` 表示叠加文件系统中的一个目录条目（文件、目录、符号链接等）。

### 关键状态字段

| 字段 | 说明 |
|------|------|
| `layer_idx` | **当前所在层**。0 = upper 层（已 copy-up 或新创建）；>0 = 仍在 lower 层 |
| `last_layer_idx` | 该文件最后存在的层索引。用于查找时从高到低遍历停止点 |
| `parent` | 父目录的 NodeId。根节点为 `None` |
| `name` | 文件名（字节）。根节点名为空 |
| `tmp_ino` / `tmp_dev` | 底层文件系统的 ino/dev 缓存，用于快速构造 InodeKey |
| `mode` | 文件类型与权限缓存（`S_IFREG`/`S_IFDIR`/... + 权限位） |

### Hidden 临时状态

copy-up 过程中使用临时状态保证原子性：
- `hidden = true`：节点正在 copy-up，临时文件在 workdir
- `hidden_path`：临时文件名
- `hidden_dirfd`：临时文件所在目录 fd（通常是 workdir）
- copy-up 完成后 rename 到目标位置，清除 hidden 标记

`Drop` trait 实现负责清理：如果节点被 drop 时仍处于 hidden 状态，自动删除 workdir 中的临时文件，避免泄漏 [F-018]。

### 节点方法

| 方法 | 用途 |
|------|------|
| `is_dir()` | 判断是否为目录（检查 dir_state） |
| `is_loaded()` / `mark_loaded()` / `mark_unloaded()` | 目录加载状态管理 |
| `get_child(name)` | 按文件名查找子节点 NodeId |
| `insert_child(name, id)` / `remove_child(name)` | 插入/移除子节点 |
| `is_whiteout(name)` / `insert_whiteout(name)` | whiteout 标记管理 |
| `children()` | 迭代当前已知子节点 |

---

## NodeArena：节点竞技场 [F-015]

```rust
pub struct NodeArena {
    nodes: FxHashMap<NodeId, OvlNode>,
    next_id: NodeId,
}
```

NodeArena 是所有 OvlNode 的所有者和分配器，使用 Arena 模式（竞技场分配）。

### 为什么叫 Arena

Arena（竞技场/区域分配）模式特点：
1. **集中分配**：所有节点在一个 HashMap 中统一管理
2. **稳定引用**：节点插入后不移动，NodeId 可安全作为句柄传递
3. **统计计数**：插入/删除时原子更新 `STAT_NODES` 计数器
4. **简单生命周期**：节点通过 NodeId 访问，不需要 Rust 引用计数的复杂性（避免 Rc/RefCell 的运行时开销和借用冲突）

### NodeArena API

| 方法 | 说明 | 统计更新 |
|------|------|---------|
| `new()` | 创建空 Arena，`next_id` 从 1 开始 | — |
| `insert(node)` | 插入新节点，分配 NodeId | `STAT_NODES += 1` |
| `get(id)` | 获取节点不可变引用 | — |
| `get_mut(id)` | 获取节点可变引用 | — |
| `remove(id)` | 移除节点 | `STAT_NODES -= 1` |
| `contains_key(id)` | 检查节点是否存在 | — |

### 为什么不直接用引用

Rust 的借用检查器不允许在存在多个可变引用时编译通过。FUSE 文件系统需要：
- 同时访问父节点和子节点
- 遍历目录时可能需要懒加载子节点
- 多线程并发操作（FUSE 多线程模式）

NodeId 作为不透明句柄配合 `RwLock<NodeArena>` 解决了这些问题。

---

## OvlIno：Inode 条目 [F-016]

```rust
pub struct OvlIno {
    pub nodes: FxHashSet<NodeId>,
    pub lookups: AtomicI64,
    pub mode: u32,
    pub fuse_ino: u64,
}
```

`OvlIno` 表示一个**唯一的底层文件**，聚合该文件的所有硬链接。

### 硬链接聚合

Linux 中硬链接（hard link）允许多个目录项指向同一个 inode。`nodes: FxHashSet<NodeId>` 记录所有指向此底层文件的 OvlNode：
- 多个路径指向同一文件 → 对应多个 OvlNode → 但共享同一个 OvlIno
- 属性修改（chmod/chown/utimens）通过 OvlIno 作用于所有硬链接
- nlink 计数 = nodes.len()

### FUSE lookup 计数

`lookups: AtomicI64` 是 FUSE 协议要求的**内核引用计数**：
- FUSE 通过 `lookup()`、`mkdir()`、`create()` 等操作"获取" inode
- 每次获取时 lookups +1
- 内核调用 `forget()` 时 lookups -1
- lookups 归零且没有节点引用时，可释放 OvlIno
- 使用 AtomicI64 支持无锁多线程操作

### fuse_ino：FUSE inode 号

每个 OvlIno 分配一个唯一的 `fuse_ino: u64`，这是 FUSE 协议中标识文件的号：
- 不能为 0 或 1（FUSE 保留值）
- 同设备时直接透传底层 ino（性能最优）
- 跨设备或冲突时使用哈希分配

---

## InodeTable：Inode 表 [F-019]

```rust
pub struct InodeTable {
    table: FxHashMap<InodeKey, Box<OvlIno>>,
    fuse_map: FxHashMap<u64, InodeKey>,
    same_device: bool,
    next_fallback: u64,
}
```

InodeTable 管理 InodeKey → OvlIno 的映射，以及 FUSE inode 反向映射。

### 双向映射

| 映射方向 | 用途 |
|---------|------|
| `table: InodeKey → OvlIno` | 按底层文件身份查找（lookup 时 stat 得到 ino+dev，查找是否已存在） |
| `fuse_map: fuse_ino → InodeKey` | FUSE `forget(fuse_ino)` 时反向查找对应哪个 OvlIno |

### same_device 与 inode 透传 [F-020]

`same_device` 标志在初始化时通过 `all_same_device(layers)` 检测：
- **true**（所有层在同一文件系统）：底层 ino 全局唯一 → 直接透传
- **false**（层跨设备）：不同设备可能有相同 ino → 需要哈希组合

```rust
pub fn compute_fuse_ino(ino: u64, dev: u64, same_device: bool) -> u64 {
    if same_device {
        // 同设备：直接用 ino，小值偏移
        if ino <= 1 {
            ino + 2
        } else {
            ino
        }
    } else {
        // 跨设备：FNV-1a 哈希(ino, dev)
        fnv1a_hash_64(ino, dev)
    }
}
```

### 冲突回退 next_fallback

如果哈希后得到的 fuse_ino 已被占用（极低概率冲突）：
- 从 `0x8000_0000_0000_0000`（高位为 1，避免与真实 ino 冲突）开始分配
- `next_fallback` 每次递增分配

### InodeTable 关键方法

| 方法 | 说明 |
|------|------|
| `get_or_insert(key, mode)` | 获取或创建 OvlIno；新条目分配 fuse_ino；`STAT_INODES += 1` |
| `inc_lookup(key)` / `dec_lookup(key)` | FUSE lookup 计数增减 |
| `remove(key)` | 移除 inode；`STAT_INODES -= 1` |
| `get_by_fuse(fuse_ino)` | 按 FUSE inode 反向查找 |

---

## 路径计算 [F-021]

```rust
pub fn compute_path(arena: &NodeArena, id: NodeId) -> Vec<u8>
```

通过父指针链从任意节点计算完整路径：

```
compute_path(arena, node_id):
  path = Vec::new()
  current = id
  while current is not root:
    node = arena.get(current)
    path.push(node.name)
    current = node.parent
  path.reverse()
  join with "/"
```

- 根节点返回 `b"."`
- 结果是相对根目录的路径字节
- 主要用于错误报告和调试，不用于热路径（热路径直接用 fd + openat 操作）

---

## FNV-1a 哈希 [F-022]

文件名哈希和跨设备 inode 哈希都使用 FNV-1a 算法：

```
FNV_OFFSET_BASIS = 0xcbf29ce484222325
FNV_PRIME        = 0x100000001b3

fnv1a(data):
  hash = FNV_OFFSET_BASIS
  for byte in data:
    hash = hash ^ byte
    hash = hash * FNV_PRIME
  return hash
```

选择 FNV-1a 原因：
- 对短字符串（文件名）计算速度极快
- 雪崩效应良好，冲突率低
- 实现简单（无需预计算表）

---

## 数据结构协作示例：lookup 流程

当 FUSE 内核发来 `lookup(parent_ino, name)` 请求时：

```
1. 从 fuse_map 找到 parent 对应的 InodeKey
2. 从 OvlIno.nodes 中找到该目录对应的 NodeId（或直接用 root_id 开始）
3. 在 parent 节点的 children 中查找 name
   ├─ 找到 → 返回已有 NodeId 对应的属性
   └─ 未找到：
4. 从 parent.layer_idx 开始，逐层向下查找：
   for layer in parent.layer_idx..layers.len():
     调用 layers[layer].lookup(parent_fd, name) → stat
     ├─ 找到且不是 whiteout：
     │   创建 InodeKey(stat.ino, stat.dev)
     │   inodes.get_or_insert(key, stat.mode)
     │   创建新 OvlNode，加入 arena
     │   parent.insert_child(name, new_id)
     │   返回属性
     └─ 是 whiteout：break（不继续找更低层）
5. 未找到任何层 → 返回 ENOENT
```

---

## 相关概念

- [FUSE 与 OverlayFS 基础](00-introduction.md) — 理解文件系统整体架构
- [Copy-up 三级优化策略](02-copyup.md) — copy-up 如何改变节点的 layer_idx
- [whiteout 与目录合并](03-whiteout.md) — whiteout 在 DirState 中的作用
- [挂载选项与运行时统计](04-mount-options.md) — STAT_NODES/STAT_INODES 统计输出
