---
type: Reference
title: OverlayFs 核心文件系统 API 参考
description: src/overlay.rs 源码参考——OverlayFs、OverlayInner 核心结构体、FUSE Filesystem trait 实现、初始化流程、能力协商
tags: [reference, api, overlay, filesystem, fuse, core, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: fuse-overlay-overlay
    title: src/overlay.rs
    path: external/dao/action/Containers/fuse-overlayfs/src/overlay.rs
---

# OverlayFs 核心文件系统 API 参考

> 信源文件：[overlay.rs](file:///d:/spaces/SpecWeave/external/dao/action/Containers/fuse-overlayfs/src/overlay.rs)

本文档记录 fuse-overlayfs 核心文件系统实现的 API，包括 `OverlayFs` 结构体、内部状态 `OverlayInner`、以及 FUSE `Filesystem` trait 的实现。

---

## OverlayFs 结构体 [F-035]

fuse-overlayfs 的主文件系统对象，实现 `fuser::Filesystem` trait。

```rust
pub struct OverlayFs {
    config: OverlayConfig,
    inner: RwLock<OverlayInner>,
    open_files: RwLock<FxHashMap<u64, Arc<OwnedFd>>>,
    next_fh: AtomicU64,
    open_dirs: RwLock<FxHashMap<u64, Arc<DirHandle>>>,
    next_dh: AtomicU64,
    inode_backings: RwLock<FxHashMap<u64, (Arc<BackingId>, usize)>>,
    fh_to_ino: RwLock<FxHashMap<u64, u64>>,
    passthrough_enabled: AtomicBool,
    notifier: Arc<OnceLock<fuser::Notifier>>,
}
```

### 成员说明

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `OverlayConfig` | 挂载配置（lowerdir/upperdir/workdir 等） |
| `inner` | `RwLock<OverlayInner>` | 核心内部状态（读写锁保护） |
| `open_files` | `RwLock<FxHashMap<u64, Arc<OwnedFd>>>` | 已打开文件句柄表（fh → fd） |
| `next_fh` | `AtomicU64` | 下一个文件句柄号（从 1 开始） |
| `open_dirs` | `RwLock<FxHashMap<u64, Arc<DirHandle>>>` | 已打开目录句柄表 |
| `next_dh` | `AtomicU64` | 下一个目录句柄号（从 1 开始） |
| `inode_backings` | `RwLock<FxHashMap<u64, (Arc<BackingId>, usize)>>` | passthrough 模式的 inode 引用计数 |
| `fh_to_ino` | `RwLock<FxHashMap<u64, u64>>` | 文件句柄到 inode 的反向映射 |
| `passthrough_enabled` | `AtomicBool` | FUSE passthrough 功能是否启用 |
| `notifier` | `Arc<OnceLock<fuser::Notifier>>` | FUSE 通知器（用于失效缓存等） |

---

## OverlayInner 结构体 [F-036]

文件系统核心内部状态，包含层、节点、inode 表等。

```rust
struct OverlayInner {
    layers: Vec<OvlLayer>,
    inodes: InodeTable,
    nodes: NodeArena,
    root_id: NodeId,
    workdir_fd: RawFd,
    ino_passthrough: bool,
    overflow: OverflowIds,
    wd_counter: u64,
    can_mknod: bool,
}
```

### 成员说明

| 成员 | 类型 | 说明 |
|------|------|------|
| `layers` | `Vec<OvlLayer>` | 文件系统层栈（索引 0 为 upper，其余为 lower） |
| `inodes` | `InodeTable` | inode 表（管理底层 inode → FUSE inode 映射） |
| `nodes` | `NodeArena` | 节点竞技场（管理目录树中的所有节点） |
| `root_id` | `NodeId` | 根节点 ID |
| `workdir_fd` | `RawFd` | workdir 目录的文件描述符 |
| `ino_passthrough` | `bool` | 是否可以直接透传底层 inode 号（同设备时） |
| `overflow` | `OverflowIds` | 溢出 inode ID 分配器 |
| `wd_counter` | `u64` | 监视计数器（从 1 开始） |
| `can_mknod` | `bool` | 是否允许 mknod（由环境变量控制） |

---

## OverlayFs::new() [F-037]

构造函数，初始化文件系统实例。

```rust
pub fn new(config: OverlayConfig) -> Result<Self, String>
```

### 初始化流程

1. 调用 `init_layers()` 初始化层栈（upper 在索引 0）
2. 调用 `all_same_device()` 判断所有层是否在同一设备上，设置 `ino_passthrough`
3. 创建 `NodeArena` 和 `InodeTable`
4. 创建根节点：空名称、`layer_idx=0`、`is_dir=true`
5. `next_fh` 和 `next_dh` 初始化为 1
6. 打开 workdir 目录获取 `workdir_fd`
7. 检查 `FUSE_OVERLAYFS_DISABLE_OVL_WHITEOUT` 环境变量设置 `can_mknod`

---

## Filesystem trait 实现 [F-038]

`impl fuser::Filesystem for OverlayFs` 实现了 FUSE 回调。

### init() — 初始化协商

FUSE 挂载后首先调用，协商文件系统能力。

**启用的 FUSE 能力**：
- `FUSE_DONT_MASK`：不屏蔽文件模式
- `FUSE_SPLICE_READ` / `FUSE_SPLICE_WRITE` / `FUSE_SPLICE_MOVE`：splice 零拷贝
- `FUSE_PARALLEL_DIROPS`：并行目录操作
- `FUSE_HANDLE_KILLPRIV`：处理 setuid/setgid 位清除
- `FUSE_CACHE_SYMLINKS`：缓存符号链接
- `FUSE_DO_READDIRPLUS` / `FUSE_READDIRPLUS_AUTO`：readdirplus 优化

**条件启用的能力**：
- `FUSE_PASSTHROUGH`：passthrough 模式（与 writeback_cache 互斥；设置 `FUSE_OVERLAYFS_NO_PASSTHROUGH` 或 `fsync=0`/volatile 模式时禁用）
- `FUSE_WRITEBACK_CACHE`：writeback 缓存（配置 `writeback=true` 时）
- `FUSE_POSIX_ACL`：POSIX ACL 支持（配置 `noacl=false` 时）

### lookup() — 查找路径

解析路径名，查找或创建子节点。涉及：
- 检查 whiteout
- 逐层查找
- copy-up 触发（首次写入时）
- inode 分配与缓存

### getattr() / setattr() — 获取/设置属性

获取或设置文件属性（大小、模式、所有者、时间等）。

### readdir() / readdirplus() — 读取目录

遍历目录内容，合并多层目录项，处理 whiteout 和 opaque 标记。

### open() / release() — 打开/关闭文件

打开文件，分配文件句柄；支持 passthrough 模式直接传递底层 fd。

### read() / write() — 读写文件

读写文件内容；write 触发 copy-up。

### mkdir() / rmdir() — 创建/删除目录

创建目录触发 copy-up；删除目录通过 whiteout 机制实现。

### create() / unlink() — 创建/删除文件

创建文件在 upper 层；删除通过 whiteout 机制。

### rename() — 重命名

重命名操作，必要时 copy-up 源文件，处理 whiteout。

### link() / symlink() / readlink() — 链接操作

硬链接、符号链接创建与读取。

### chmod() / chown() / truncate() / utimens() — 元数据操作

元数据修改操作均触发 copy-up。

### getxattr() / setxattr() / listxattr() / removexattr() — 扩展属性

xattr 操作，过滤 trusted.overlay. 等内部属性。

### statfs() — 文件系统统计

返回文件系统统计信息。

---

## Whiteout 检测 [F-039]

fuse-overlayfs 支持三种 whiteout（白项，用于标记删除）形式：

| 形式 | 说明 |
|------|------|
| `.wh.<name>` 文件 | 同名文件被删除 |
| `.wh.` 前缀条目 | `.wh..wh..opq` 表示不透明目录（不合并下层） |
| char device (0,0) | 字符设备 0/0 作为 whiteout 标记 |

目录不透明（opaque）标记通过扩展属性实现：
- xattr 名：`trusted.overlay.opaque`
- 值：`y` 表示不透明目录

---

## 关键辅助方法

| 方法 | 说明 |
|------|------|
| `copy_up_if_needed()` | 必要时执行 copy-up（节点不在 upper 层且需要写入时） |
| `get_node()` | 根据 NodeId 获取节点引用 |
| `get_node_mut()` | 获取节点可变引用 |
| `lookup_child()` | 在节点下查找子节点，必要时从底层加载 |
| `do_lookup()` | 执行单层查找 |
| `node_from_path()` | 从路径创建节点 |
| `whiteout_name()` | 生成 whiteout 文件名（`.wh.` + name） |
| `is_whiteout_name()` | 判断文件名是否为 whiteout |
