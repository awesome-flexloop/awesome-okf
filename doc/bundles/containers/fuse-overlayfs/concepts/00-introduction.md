---
type: Concept
title: FUSE 与 OverlayFS 基础
description: FUSE（用户空间文件系统）与 OverlayFS（叠加文件系统）的核心概念、fuse-overlayfs 项目定位、架构分层与基本工作原理
tags: [concept, introduction, fuse, overlayfs, filesystem, rootless-containers, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: facts-fuse-overlayfs
    resource: "/.trae/specs/containers-okf-wiki/facts-fuse-overlayfs.md"
    title: fuse-overlayfs 可验证事实
  - id: readme-source
    resource: "/bundles/containers/fuse-overlayfs/references/readme-source.md"
    title: README 与项目元信息参考
---

# FUSE 与 OverlayFS 基础

## 什么是 FUSE

**FUSE（Filesystem in Userspace，用户空间文件系统）** 是 Linux 内核提供的一种机制，允许非特权用户在用户空间实现文件系统逻辑，而无需编写内核模块。FUSE 由内核模块 `fuse.ko` 和用户空间库 `libfuse` 组成。

FUSE 的工作原理：
1. 用户空间文件系统进程通过 `/dev/fuse` 与内核通信
2. 内核将 VFS（Virtual File System，虚拟文件系统）调用转发给用户空间进程
3. 用户空间进程处理请求后通过专用文件描述符回复内核
4. 内核将结果返回给调用进程

```
┌─────────────────────────────────────────────────────────┐
│                    用户进程                               │
│              (read/write/open/...)                       │
└────────────────────┬────────────────────────────────────┘
                     │ VFS 系统调用
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Linux 内核                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │  ext4    │    │  tmpfs   │    │  FUSE 内核模块    │  │
│  │  xfs     │    │  procfs  │    │  (/dev/fuse)     │  │
│  └──────────┘    └──────────┘    └────────┬─────────┘  │
└───────────────────────────────────────────┼─────────────┘
                                            │ /dev/fuse
                                            ▼
┌─────────────────────────────────────────────────────────┐
│               fuse-overlayfs 用户空间进程                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  OverlayFs 实现 lookup/readdir/read/write/...     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 什么是 OverlayFS

**OverlayFS（叠加文件系统）** 是一种联合挂载文件系统，它将多个目录（称为"层"）透明地叠加在一起，呈现为一个统一的文件系统视图。OverlayFS 从 Linux 3.18 开始合入内核主线，是 Docker/Podman 等容器技术的核心存储驱动。

### OverlayFS 的三层结构

| 层 | 名称 | 可写性 | 说明 |
|----|------|--------|------|
| 最上层 | upperdir（上层目录） | 可读写 | 所有修改都写入此层 |
| 中间 | workdir（工作目录） | 内部使用 | 原子操作的临时工作空间，必须与 upperdir 同文件系统 |
| 下层 | lowerdir（下层目录） | 只读 | 可以有多个，从后往前依次叠加 |

```
          ┌─────────────────────┐
          │     upperdir         │  ← 可写，所有修改在此
          └─────────┬───────────┘
                    │
          ┌─────────▼───────────┐
          │     workdir          │  ← 内部临时空间（原子 copy-up）
          └─────────────────────┘
          ┌─────────────────────┐
          │     lower1           │  ← 只读（最高优先级下层）
          └─────────┬───────────┘
                    │
          ┌─────────▼───────────┐
          │     lower2           │  ← 只读
          └─────────┬───────────┘
                    │
                    ...
                    │
          ┌─────────▼───────────┐
          │     lowerN           │  ← 只读（最底层）
          └─────────────────────┘
```

### Copy-up 机制

当需要修改 lower 层的文件时，OverlayFS 执行 **copy-up（拷贝上推）** 操作：
1. 将文件从 lower 层完整复制到 upper 层
2. 后续所有读写都作用于 upper 层副本
3. lower 层的原始文件保持不变

这是一个**惰性**操作——仅在首次修改时触发，而不是在挂载时预先复制所有文件。

### Whiteout 机制

为了实现"删除" lower 层文件的效果，OverlayFS 使用 **whiteout（白项）** 机制：
- 在 upper 层创建一个特殊标记（`.wh.<filename>` 文件或 char device 0/0）
- 读取目录时，带有 whiteout 标记的 lower 层文件被隐藏
- 整个目录不合并（opaque）通过 `trusted.overlay.opaque=y` xattr 标记

---

## fuse-overlayfs 是什么

**fuse-overlayfs** 是 OverlayFS 的 FUSE 用户空间实现，版本 2.0.0，用 Rust 编写，采用 GPL-2.0-or-later 许可证 [F-001][F-002]。

### 为什么需要 fuse-overlayfs

内核原生 OverlayFS 虽然性能好，但有以下限制：
- **需要 root 权限**挂载（或特定 CAP_SYS_ADMIN 能力）
- **无根容器（rootless containers）** 场景下无法使用
- 对用户命名空间（user namespace）中的 UID/GID 映射支持有限
- 需要较新内核（部分特性要求 4.x+）

fuse-overlayfs 解决了这些问题：
- ✅ 非特权用户可运行（通过 FUSE）
- ✅ 完整的 UID/GID 映射支持（容器无根模式）
- ✅ 可在不支持原生 OverlayFS 的文件系统上工作
- ✅ 提供运行时统计与调试能力

### 技术栈

| 组件 | 说明 |
|------|------|
| Rust 2024 edition | 编程语言（最低 Rust 1.85.0）[F-001] |
| fuser 0.17 | Rust FUSE 绑定（启用 abi-7-40） |
| libfuse >= 3.2.1 | 用户空间 FUSE 库 [F-004] |
| rustix | 安全的 Rust 系统调用封装 |
| parking_lot | 高性能锁实现 |
| rustc-hash (FxHash) | 快速哈希算法 |

### 开发约束 [F-008]

项目强制执行严格的安全规则：
1. **unsafe 代码隔离**：仅 `src/sys/` 目录允许使用 unsafe，其他模块必须用 safe Rust
2. **无 panic 策略**：禁止 `unwrap()`、`expect()`、`panic!()`——错误必须通过 `reply.error(errno)` 返回给内核，保证文件系统不崩溃
3. **正确的 errno**：所有错误必须映射到正确的 POSIX errno 值

---

## 源码架构

fuse-overlayfs 的源码组织在 `src/` 目录，共 12 个模块 [F-005][F-006][F-007]：

```
src/
├── main.rs          # 主入口：参数解析、挂载、daemonize、信号处理
├── overlay.rs       # 核心：OverlayFs 结构体 + FUSE Filesystem trait 实现
├── node.rs          # 节点/inode：NodeArena、OvlNode、InodeTable、OvlIno
├── copyup.rs        # Copy-up：reflink→sendfile→read/write 三级优化
├── config.rs        # 配置：OverlayConfig、命令行参数解析
├── layer.rs         # 层管理：OvlLayer、init_layers、DataSource
├── datasource.rs    # 数据源 trait：DataSource、DirIterator
├── direct.rs        # 直接访问：DirectAccess（openat2、statx）
├── whiteout.rs      # Whiteout：检测与处理
├── xattr.rs         # xattr：扩展属性常量与辅助函数
├── mapping.rs       # ID映射：UID/GID 用户命名空间映射
├── error.rs         # 错误：FsResult 错误类型
└── sys/             # 系统抽象层（仅这里允许 unsafe）
    ├── dir.rs       # 目录迭代
    ├── fs.rs        # 文件系统操作
    ├── handle.rs    # 文件句柄
    ├── io.rs        # IO 辅助
    ├── openat2.rs   # openat2 安全打开（RESOLVE_IN_ROOT）
    ├── process.rs   # 进程相关（geteuid 等）
    ├── statx.rs     # statx 系统调用
    └── xattr.rs     # xattr 系统调用
```

### 核心数据结构关系

```
OverlayFs
  ├── config: OverlayConfig
  ├── inner: RwLock<OverlayInner>
  │     ├── layers: Vec<OvlLayer>          ──→ 层栈（upper 在 [0]）
  │     ├── inodes: InodeTable             ──→ inode 映射表
  │     │     └── table: FxHashMap<InodeKey, OvlIno>
  │     │           └── nodes: FxHashSet<NodeId>
  │     ├── nodes: NodeArena               ──→ 节点竞技场
  │     │     └── nodes: FxHashMap<NodeId, OvlNode>
  │     │           ├── parent: Option<NodeId>
  │     │           ├── dir_state: DirState
  │     │           ├── layer_idx: usize
  │     │           └── ...
  │     ├── root_id: NodeId                ──→ 根节点
  │     └── workdir_fd: RawFd              ──→ workdir 目录 fd
  ├── open_files: FxHashMap<u64, OwnedFd>
  └── open_dirs: FxHashMap<u64, DirHandle>
```

---

## FUSE 能力协商

挂载时，fuse-overlayfs 与内核协商启用以下 FUSE 特性 [F-038]：

| 能力 | 说明 |
|------|------|
| `FUSE_DONT_MASK` | 文件模式不被 umask 屏蔽 |
| `FUSE_SPLICE_READ/WRITE/MOVE` | splice() 零拷贝 IO |
| `FUSE_PARALLEL_DIROPS` | 允许多线程并行目录操作 |
| `FUSE_HANDLE_KILLPRIV` | 自动处理 setuid/setgid 位清除 |
| `FUSE_CACHE_SYMLINKS` | 内核缓存符号链接内容 |
| `FUSE_DO_READDIRPLUS` / `FUSE_READDIRPLUS_AUTO` | readdirplus 优化（lookup + readdir 合并） |
| `FUSE_PASSTHROUGH` | passthrough 模式（直接传递底层 fd，高性能）— 条件启用 |
| `FUSE_WRITEBACK_CACHE` | writeback 缓存（延迟刷新）— 默认启用 |
| `FUSE_POSIX_ACL` | POSIX ACL 支持 — 除非指定 noacl |

---

## 相关概念

- [节点与 inode 管理](01-node-inode.md) — NodeArena 与 InodeTable 的详细设计
- [Copy-up 三级优化策略](02-copyup.md) — reflink→sendfile→read/write 性能优化详解
- [whiteout 与目录合并](03-whiteout.md) — whiteout 标记与 opaque 目录机制
- [挂载选项与运行时统计](04-mount-options.md) — 完整挂载选项与 SIGUSR1 统计
