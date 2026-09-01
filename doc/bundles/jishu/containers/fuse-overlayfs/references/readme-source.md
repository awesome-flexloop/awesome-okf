---
type: Reference
title: README 与项目元信息参考
description: fuse-overlayfs 项目 README、Cargo.toml、Makefile 与 man page 参考——项目定位、编译安装、命令行用法、版本依赖
tags: [reference, readme, metadata, installation, usage, fuse-overlayfs]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: fuse-overlayfs-readme
    title: README.md
    path: external/dao/action/Containers/fuse-overlayfs/README.md
  - id: fuse-overlayfs-cargo
    title: Cargo.toml
    path: external/dao/action/Containers/fuse-overlayfs/Cargo.toml
  - id: fuse-overlayfs-makefile
    title: Makefile
    path: external/dao/action/Containers/fuse-overlayfs/Makefile
  - id: fuse-overlayfs-man
    title: fuse-overlayfs.1.md
    path: external/dao/action/Containers/fuse-overlayfs/fuse-overlayfs.1.md
---

# README 与项目元信息参考

> 信源文件：README.md、Cargo.toml、Makefile、fuse-overlayfs.1.md

本文档记录 fuse-overlayfs 项目的基本定位、版本依赖、编译安装方法与命令行概览。

---

## 项目定位

fuse-overlayfs 是一个用户空间实现的 OverlayFS（Overlay Filesystem，叠加文件系统），通过 FUSE（Filesystem in Userspace，用户空间文件系统）框架运行。它为无根容器（rootless containers）提供了叠加文件系统能力，是 Podman、Buildah 等容器工具在无根模式下的核心存储驱动。

与内核原生 OverlayFS 相比，fuse-overlayfs 的优势：
- 无需 root 权限即可运行
- 支持用户命名空间中的 UID/GID 映射
- 可在不支持原生 OverlayFS 的文件系统上工作
- 提供额外的调试和统计能力

---

## 版本与依赖 [F-001][F-002][F-003][F-004]

| 项 | 值 |
|----|----|
| 项目名称 | fuse-overlayfs |
| 当前版本 | 2.0.0 |
| Rust 版本 | 2024 edition，最低要求 1.85.0 |
| 许可证 | GPL-2.0-or-later |
| 仓库地址 | https://github.com/containers/fuse-overlayfs |
| libfuse 要求 | >= v3.2.1 |
| 内核要求（用户命名空间） | >= v4.18.0 |

### Rust 依赖

| Crate | 版本 | 特性 |
|-------|------|------|
| fuser | 0.17.0 | abi-7-40 |
| rustix | 1.1 | process |
| libc | 0.2.183 | — |
| signal-hook | 0.3.18 | — |
| parking_lot | 0.12.5 | — |
| log | 0.4.29 | — |
| env_logger | 0.11.9 | — |
| thiserror | 2.0.18 | — |
| rustc-hash | 2.1.1 | — |

---

## 编译安装

### 使用 Cargo 编译

```bash
git clone https://github.com/containers/fuse-overlayfs.git
cd fuse-overlayfs
cargo build --release
sudo cp target/release/fuse-overlayfs /usr/local/bin/
```

### 使用 Makefile

```bash
make
sudo make install
```

Makefile 提供以下目标：
- `make`：编译 release 版本
- `make install`：安装到 PREFIX（默认 /usr/local）
- `make uninstall`：卸载
- `make clean`：清理构建产物

---

## 命令行概览

```bash
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work mountpoint
```

### 主要挂载选项

| 选项 | 说明 |
|------|------|
| `lowerdir=DIR[:DIR...]` | 只读下层目录，冒号分隔多个层 |
| `upperdir=DIR` | 可写上层目录 |
| `workdir=DIR` | 工作目录（必须与 upperdir 在同一文件系统） |
| `redirect_dir=on/off` | 重定向目录（当前仅支持 off） |
| `uidmap=UID_MAP` | UID 映射（容器用） |
| `gidmap=GID_MAP` | GID 映射（容器用） |
| `context=CTX` | SELinux 上下文 |
| `timeout=SECONDS` | 属性缓存超时（默认 1e9 秒） |
| `squash_to_uid=UID` | 将所有文件 squash 到指定 UID |
| `squash_to_gid=GID` | 将所有文件 squash 到指定 GID |
| `threaded` | 启用多线程 FUSE |
| `fsync` | 操作后 fsync（默认启用） |
| `writeback` | 启用 writeback 缓存（默认启用） |
| `disable_xattrs` | 禁用扩展属性支持 |
| `nfs_filehandles` | NFS 文件句柄模式 |
| `debug` | 启用调试输出 |
| `foreground` | 前台运行（不 daemonize） |
| `ino_t_32` | 使用 32 位 inode 号 |
| `static_nlink` | 静态 nlink 计数 |
| `volatile_mode` | 易失模式（禁用 fsync） |
| `noacl` | 禁用 POSIX ACL 支持 |

### FUSE 透传选项

以下选项直接透传给 libfuse [F-010]：

`allow_root`、`default_permissions`、`allow_other`、`suid`、`nosuid`、`dev`、`nodev`、`exec`、`noexec`、`atime`、`noatime`、`diratime`、`nodiratime`、`splice_write`、`splice_read`、`splice_move`、`kernel_cache`、`max_write=N`、`ro`、`rw`。

---

## 运行时统计

向进程发送 SIGUSR1 信号可输出运行时统计：

```bash
kill -SIGUSR1 <pid>
```

输出包括：
- 已分配节点数（STAT_NODES）
- 已分配 inode 数（STAT_INODES）
- passthrough 启用状态（STAT_PASSTHROUGH）

---

## 开发规则 [F-008]

项目强制执行以下开发约束：
1. **unsafe 代码隔离**：禁止在 `src/sys/` 目录之外使用 `unsafe` 代码
2. **无 panic 策略**：禁止使用 `unwrap()`、`expect()`、`panic!()`，所有错误必须通过 `reply.error(errno)` 报告给内核
3. **错误处理**：所有 FUSE 回调都必须返回正确的 errno 值
