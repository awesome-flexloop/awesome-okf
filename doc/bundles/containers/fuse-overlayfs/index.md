---
type: OKF
title: fuse-overlayfs 教程
description: fuse-overlayfs 用户空间 OverlayFS 的完整源码级教程——FUSE与OverlayFS基础、NodeArena+InodeTable节点管理、Copy-up三级优化（reflink→sendfile→read/write）、Whiteout与目录合并、Rootless无根容器配置
tags: [fuse-overlayfs, fuse, overlayfs, filesystem, rust, rootless-containers, containers, podman, buildah, copy-up, whiteout]
version: "2.0.0"
source: https://github.com/containers/fuse-overlayfs
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# fuse-overlayfs 教程

fuse-overlayfs 是用 Rust 编写的用户空间 OverlayFS（叠加文件系统）实现，通过 FUSE 框架运行，是 Podman、Buildah 等容器工具无根（rootless）模式的核心存储驱动。它允许非特权用户在不修改只读 lower 层的前提下，透明地叠加多个目录层并提供统一的可写文件系统视图。

fuse-overlayfs v2.0.0 基于 Rust 2024 edition 开发，要求 libfuse >= 3.2.1，Linux 内核 >= 4.18.0（用户命名空间支持）。核心设计亮点包括三级 copy-up 性能优化（reflink→sendfile→read/write）、Arena 模式节点管理、双向 inode 映射、严格的 unsafe 隔离和无 panic 错误处理策略。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门篇：**
- [00-FUSE与OverlayFS基础](concepts/00-introduction.md) — FUSE原理、OverlayFS三层结构（lower/upper/workdir）、copy-up/whiteout基本概念、项目架构、开发约束
- [04-挂载选项与运行时统计](concepts/04-mount-options.md) — OverlayConfig完整配置、19个FUSE透传选项、UID/GID映射、SIGUSR1统计、性能调优

**核心篇：**
- [01-节点与inode管理](concepts/01-node-inode.md) — NodeArena竞技场、OvlNode叠加节点、InodeTable双向映射、OvlIno硬链接聚合、DirState惰性加载、FNV-1a哈希
- [02-Copy-up三级优化策略](concepts/02-copyup.md) — FICLONE reflink O(1)复制、sendfile零拷贝、1MB read/write兜底、workdir+rename原子性、不同文件类型处理
- [03-whiteout与目录合并](concepts/03-whiteout.md) — 三种whiteout形式、.wh.前缀、char 0/0、opaque不透明目录、多层目录合并算法

### [实践示例](examples/index.md)
- [01-基本挂载使用](examples/01-basic-mount.md) — 编译安装、三层目录准备、挂载验证、copy-up/whiteout直观体验、卸载、多下层变体 ⭐入门
- [02-Rootless模式配置](examples/02-rootless.md) — 用户命名空间、/etc/subuid配置、uidmap/gidmap映射、Podman/Buildah集成、排障脚本 ⭐⭐进阶

### [信源参考](references/index.md)
- [README与项目元信息](references/readme-source.md) — 版本依赖、编译安装、命令行选项、开发规则
- [OverlayFs核心API](references/overlay-source.md) — OverlayFs、OverlayInner结构体、FUSE Filesystem trait实现、能力协商
- [节点与Inode管理API](references/node-source.md) — NodeArena、OvlNode、InodeTable、OvlIno、DirState完整API
- [Copy-up机制API](references/copyup-source.md) — copy_data三级策略、copy_xattr、create_node_directory、完整copyup流程

## 🚀 快速开始

### 编译安装

```bash
git clone https://github.com/containers/fuse-overlayfs.git
cd fuse-overlayfs
cargo build --release
sudo cp target/release/fuse-overlayfs /usr/local/bin/
```

### 最简挂载

```bash
# 准备层目录
mkdir -p lower upper work merged
echo "Hello from lower" > lower/hello.txt

# 挂载
fuse-overlayfs -o lowerdir=lower,upperdir=upper,workdir=work merged

# 读写
ls merged/
echo "Modified" > merged/hello.txt  # 触发 copy-up
ls upper/  # 可以看到 upper 层出现了 hello.txt 副本

# 卸载
fusermount -u merged
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🔓 无根支持 | 普通用户可运行，完整支持 UID/GID 映射，是 Podman/Buildah 无根模式的核心 |
| ⚡ 三级 copy-up | FICLONE reflink（O(1)）→ sendfile（零拷贝）→ 1MB read/write（兜底） |
| 🏗️ 安全 Rust | 严格的 unsafe 隔离（仅 src/sys/）、禁止 unwrap/expect/panic、所有错误返回 errno |
| 🔗 硬链接支持 | InodeTable 聚合同一底层文件的所有硬链接，正确维护 nlink 计数 |
| 📊 运行时统计 | SIGUSR1 输出 STAT_NODES/STAT_INODES/STAT_PASSTHROUGH 统计信息 |
| 🔀 FUSE 能力 | splice零拷贝、parallel dirops、writeback缓存、passthrough_fd、POSIX ACL |
| 🌐 多 lower 层 | 支持冒号分隔的多个只读下层，自动按优先级合并 |
| 📦 容器集成 | 原生支持 Podman/Buildah/Docker 无根模式，自动配置 xattr 权限模式 |

## 📖 推荐学习路径

1. **入门体验**：阅读 [00-FUSE与OverlayFS基础](concepts/00-introduction.md)，跟着 [01-基本挂载](examples/01-basic-mount.md) 动手，亲眼观察 copy-up 和 whiteout
2. **理解核心**：学习 [01-节点与inode管理](concepts/01-node-inode.md) 理解内存数据结构，然后深入 [02-Copy-up三级优化](concepts/02-copyup.md) 理解写入路径
3. **掌握机制**：学习 [03-whiteout与目录合并](concepts/03-whiteout.md) 理解读取和删除路径，配合 [信源参考](references/index.md) 对照源码
4. **容器实践**：学习 [04-挂载选项](concepts/04-mount-options.md) 和 [02-Rootless模式](examples/02-rootless.md)，配置 Podman 无根容器
5. **源码精读**：对照 [API 参考](references/index.md) 阅读 `src/` 目录源码，从 `overlay.rs` 开始，然后是 `node.rs`、`copyup.rs`

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户进程 (VFS 调用)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ /dev/fuse
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OverlayFs (Filesystem trait)                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  lookup/readdir/read/write/mkdir/unlink/... (FUSE回调)    │  │
│  └──────────────────────────────┬────────────────────────────┘  │
│                                 │ copy-up 触发                   │
│  ┌──────────────────────────────▼────────────────────────────┐  │
│  │  OverlayInner { layers, nodes, inodes, root_id, ... }     │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │ layers[]  │  │ NodeArena    │  │ InodeTable          │  │  │
│  │  │ (OvlLayer)│  │ (FxHashMap)  │  │ (InodeKey→OvlIno)   │  │  │
│  │  │ [0]=upper │  │  OvlNode     │  │  fuse_ino映射       │  │  │
│  │  │ [1..]=low │  │  parent/name │  │  hardlink聚合       │  │  │
│  │  └────┬─────┘  │  layer_idx   │  └─────────────────────┘  │  │
│  │       │        │  DirState    │                            │  │
│  │       ▼        └──────────────┘                            │  │
│  │  ┌─────────────────┐                                      │  │
│  │  │ copyup()        │                                      │  │
│  │  │ FICLONE→sendfile│                                      │  │
│  │  │ →read/write     │                                      │  │
│  │  └─────────────────┘                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │  DirectAccess (DataSource)                                 │  │
│  │  openat2(RESOLVE_IN_ROOT) / statx / xattr / NFS fh        │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  底层文件系统 (ext4/xfs/btrfs/...)  upper/lower/work 目录        │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 源码模块索引

| 文件 | 模块 | 核心职责 |
|------|------|---------|
| main.rs | 主入口 | 参数解析、挂载配置、daemonize、SIGUSR1处理 |
| overlay.rs | 核心FS | OverlayFs、FUSE回调、whiteout检测 |
| node.rs | 节点管理 | NodeArena、OvlNode、InodeTable、OvlIno |
| copyup.rs | Copy-up | 三级数据复制、原子rename、xattr复制 |
| config.rs | 配置 | OverlayConfig、参数解析、lowerdir解析 |
| layer.rs | 层管理 | OvlLayer、init_layers、DataSource初始化 |
| direct.rs | 直接访问 | DirectAccess、openat2安全打开、statx |
| datasource.rs | 数据源trait | DataSource、DirIterator trait定义 |
| whiteout.rs | Whiteout | whiteout检测与处理 |
| sys/ | 系统抽象 | 所有unsafe代码封装（目录/IO/打开/statx/xattr等） |

## 🔗 外部资源

- **GitHub 仓库**：[containers/fuse-overlayfs](https://github.com/containers/fuse-overlayfs)
- **Podman 无根文档**：[https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md](https://github.com/containers/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- **FUSE 文档**：[libfuse](https://github.com/libfuse/libfuse)
- **Linux OverlayFS 文档**：[kernel.org](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- **用户命名空间**：[user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
