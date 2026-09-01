---
type: Concept
title: Copy-up 三级优化策略
description: Copy-up 机制详解、reflink（FICLONE）写时复制、sendfile 零拷贝、read/write 缓冲区三级回退策略、xattr 复制、目录创建、原子 rename 保证
tags: [concept, copy-up, copyup, reflink, sendfile, ficlone, zero-copy, performance, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: facts-fuse-overlayfs
    resource: "/.trae/specs/containers-okf-wiki/facts-fuse-overlayfs.md"
    title: fuse-overlayfs 可验证事实
  - id: copyup-source
    resource: "/bundles/containers/fuse-overlayfs/references/copyup-source.md"
    title: Copy-up 机制 API 参考
---

# Copy-up 三级优化策略

Copy-up（拷贝上推）是 OverlayFS 的核心机制。当首次修改 lower 层的只读文件时，fuse-overlayfs 将该文件完整复制到 upper 可写层，后续修改作用于 upper 副本。为了最大化性能，fuse-overlayfs 实现了三级数据复制策略，按性能从高到低自动降级。

---

## 为什么需要 Copy-up

OverlayFS 的核心设计原则：
- **lower 层永远只读**：这保证了基础镜像的完整性（容器镜像、基础层等）
- **修改只发生在 upper 层**：所有创建、修改、删除操作都记录在 upper
- **首次写入时复制**：不预复制所有文件，按需复制，节省时间和空间

```
挂载时视图：                    写入 /foo 后：
┌───────────┐                  ┌───────────┐
│  upper    │  ← 空            │  upper    │  ← /foo (副本)
└─────┬─────┘                  └─────┬─────┘
      │                              │
┌─────▼─────┐                  ┌─────▼─────┐
│  lower    │  ← /foo, /bar    │  lower    │  ← /foo (原始, 未变), /bar
└───────────┘                  └───────────┘
      ▲                              ▲
      │                              │
  合并视图:                      合并视图:
  /foo → lower                   /foo → upper(副本)
  /bar → lower                   /bar → lower
```

### 触发 Copy-up 的操作 [F-030]

| 操作类型 | 具体操作 | 是否触发 copy-up |
|---------|---------|----------------|
| **只读操作** | read, readdir, getattr, lookup, readlink, statfs | ❌ 否 |
| **数据修改** | write, truncate | ✅ 是 |
| **元数据修改** | chmod, chown, utimens | ✅ 是 |
| **扩展属性** | setxattr, removexattr | ✅ 是 |
| **名称修改** | rename（源文件） | ✅ 是 |
| **删除操作** | unlink, rmdir（需创建 whiteout） | ✅ 是 |
| **新建操作** | mkdir, create, mknod, symlink, link | ❌ 直接在 upper 创建 |

Copy-up 是**惰性**（lazy）的——只在实际需要写入时才执行，挂载时不做任何复制工作。

---

## 三级数据复制策略 [F-028]

```rust
fn copy_data(sfd: RawFd, dfd: RawFd, size: i64) -> FsResult<()> {
    // 第一级：FICLONE (reflink)
    if try_ficlone(sfd, dfd).is_ok() { return Ok(()); }

    // 第二级：sendfile
    if try_sendfile(sfd, dfd, size).is_ok() { return Ok(()); }

    // 第三级：read/write 循环（兜底）
    copy_read_write(sfd, dfd)
}
```

### 第一级：FICLONE（reflink 写时复制）

```rust
let ret = unsafe { libc::ioctl(dfd, libc::FICLONE, sfd) };
if ret == 0 {
    return Ok(());
}
```

**FICLONE** 是 Linux 提供的 reflink（写时复制克隆）ioctl：

| 特性 | 说明 |
|------|------|
| **速度** | 瞬时完成（O(1) 操作） |
| **原理** | 不实际复制数据块，仅增加文件系统块引用计数 |
| **磁盘占用** | 0（克隆后两个文件共享数据块，修改时才分配新块） |
| **前提条件** | 源和目标在同一文件系统，且该文件系统支持 reflink |

**支持 reflink 的文件系统**：
- Btrfs（默认支持）
- XFS（需 `reflink=1` 挂载选项）
- ZFS（2.2.0+，支持 block cloning）
- Bcachefs

不支持时 ioctl 返回 EXDEV（跨设备）或 EOPNOTSUPP（不支持），自动降级到下一级。

### 第二级：sendfile 零拷贝

```rust
let mut remaining = size;
while remaining > 0 {
    let ret = unsafe { libc::sendfile(dfd, sfd, null_mut(), remaining as usize) };
    if ret > 0 {
        remaining -= ret as i64;
    } else {
        break; // sendfile 失败，降级
    }
}
if remaining == 0 {
    return Ok(());
}
```

**sendfile()** 系统调用在内核空间直接在两个文件描述符之间复制数据：

| 特性 | 说明 |
|------|------|
| **速度** | 快（比 read/write 快约 2-3 倍） |
| **原理** | 数据不进入用户空间，直接在内核页缓存间复制 |
| **磁盘占用** | 需要实际复制数据块 |
| **前提条件** | 源必须是可 mmap 的文件（普通文件），目标通常需要是管道或 socket，但 Linux 内核也支持文件到文件的 sendfile |

sendfile 失败场景：
- 源文件不支持 sendfile（某些特殊文件系统或设备）
- 跨文件系统某些边界情况
- 内核版本不支持文件到文件 sendfile

失败后自动降级到第三级。

### 第三级：read/write 循环（兜底方案）

```rust
const BUF_SIZE: usize = 1024 * 1024; // 1MB
let mut buf = vec![0u8; BUF_SIZE];
loop {
    let n = read(sfd, &mut buf)?;
    if n == 0 { break; } // EOF

    let mut written = 0;
    while written < n {
        let w = write(dfd, &buf[written..n])?;
        written += w;
    }
}
```

最通用的方案，适用于所有情况：

| 特性 | 说明 |
|------|------|
| **速度** | 中等（受用户态/内核态拷贝开销影响） |
| **缓冲区** | 1MB 堆缓冲区（平衡内存占用和系统调用次数） |
| **适用范围** | 所有文件系统、所有文件类型 |
| **注意** | 处理 `write()` 的部分写入（short write） |

### 三级策略对比

| 策略 | 系统调用 | 时间复杂度 | 额外磁盘 | 支持条件 |
|------|---------|-----------|---------|---------|
| **FICLONE (reflink)** | `ioctl(FICLONE)` | O(1) | 0 | Btrfs/XFS/ZFS/Bcachefs 同文件系统 |
| **sendfile** | `sendfile()` | O(n) 内核态 | 完整副本 | 常规文件，内核支持 |
| **read/write** | `read()` + `write()` | O(n) 用户态 | 完整副本 | 所有情况 |

---

## Copy-up 完整流程 [F-030]

对于普通文件，完整的 copy-up 流程如下：

```
                    ┌──────────────────────────┐
                    │  节点在 lower 层          │
                    │  (layer_idx > 0)         │
                    └────────────┬─────────────┘
                                 │ 触发写入
                                 ▼
                    ┌──────────────────────────┐
                    │ 1. 生成临时文件名         │
                    │    (在 workdir 中)        │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 2. openat 源文件 (lower) │
                    │    O_RDONLY              │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 3. openat 临时文件        │
                    │    O_WRONLY|O_CREAT|O_EXCL│
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 4. copy_data(sfd, dfd)   │
                    │    reflink → sendfile → r/w│
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 5. futimens()            │
                    │    设置时间戳             │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 6. copy_xattr(sfd, dfd)  │
                    │    复制扩展属性           │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 7. fchmod()              │
                    │    设置权限              │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 8. renameat() 原子替换    │
                    │    临时名 → upper 目标名  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 9. 更新节点状态           │
                    │    layer_idx = 0         │
                    │    更新 tmp_ino/tmp_dev  │
                    └──────────────────────────┘
```

### 为什么用 workdir + rename？

这是 OverlayFS 保证**原子性**和**一致性**的关键设计：

1. **原子性**：`rename()` 在 POSIX 中是原子操作——其他进程要么看到旧文件，要么看到新文件，不会看到中间状态
2. **崩溃一致性**：如果 copy-up 中途进程崩溃，临时文件留在 workdir 中（不影响合并视图），下次可清理
3. **并发安全**：O_EXCL 创建临时文件保证同一时间只有一个进程执行 copy-up（避免"惊群"复制同一文件）

### 为什么按这个顺序？

| 步骤 | 顺序原因 |
|------|---------|
| 先 copy_data | 数据复制最耗时，若失败不影响属性 |
| 再 futimens | 时间戳在数据之后（数据写入会改变 mtime/atime） |
| 再 copy_xattr | xattr 可能影响权限解释 |
| 再 fchmod | 最后设置权限，避免过早开放权限导致安全窗口 |
| 最后 rename | 原子发布——只有当文件完全就绪时才对合并视图可见 |

---

## 不同文件类型的 Copy-up [F-030]

`copyup()` 函数根据文件类型（`mode & S_IFMT`）执行不同的复制逻辑：

### 目录（S_ISDIR）

调用 `create_node_directory()` 递归创建：
- 不复制目录内容（目录内容通过多层合并呈现，子文件按需 copy-up）
- 只在 upper 层创建同名空目录
- 使用 RENAME_EXCHANGE 处理与已存在目录合并

### 符号链接（S_ISLNK）

```rust
// 1. readlinkat 读取链接目标
let target = readlinkat(lower_fd, name, ...);
// 2. symlinkat 在 workdir 创建临时符号链接
symlinkat(target, workdir_fd, temp_name);
// 3. 复制 xattr、设置时间戳
// 4. renameat 到 upper
```

- 符号链接没有"内容"需要复制，只需要重新创建链接即可
- 符号链接的权限位无意义（始终 0777）

### 特殊文件（S_ISCHR / S_ISBLK / S_ISFIFO / S_ISSOCK）

```rust
// 1. fstatat 获取 rdev（设备号）
let stat = fstatat(lower_fd, name, ...);
// 2. mknodat 在 workdir 创建特殊文件
mknodat(workdir_fd, temp_name, stat.st_mode, stat.st_rdev);
// 3. 复制 xattr、fchmod、设置时间戳
// 4. renameat 到 upper
```

- 字符设备、块设备需要 rdev 标识哪个设备
- FIFO（管道）和 socket 只需要创建正确类型，不需要 rdev
- 特殊文件不占数据块，创建是瞬时的

---

## copy_xattr：扩展属性复制 [F-027]

```rust
fn copy_xattr(sfd: RawFd, dfd: RawFd) -> FsResult<()>
```

扩展属性（xattr）的复制需要**过滤内部属性**：

| 前缀 | 用途 | 是否复制 |
|------|------|---------|
| `trusted.overlay.` | OverlayFS 内部标记（opaque 等） | ❌ 跳过 |
| `user.overlay.` | OverlayFS 用户空间内部 | ❌ 跳过 |
| `overlay.` | 其他 overlay 内部属性 | ❌ 跳过 |
| `security.*` | SELinux/SMACK 安全上下文 | ✅ 复制 |
| `trusted.*`（其他） | 其他受信任属性 | ✅ 复制 |
| `user.*`（其他） | 用户定义属性 | ✅ 复制 |
| `system.*` | 系统属性（如 POSIX ACL） | ✅ 复制 |

为什么跳过 overlay 内部 xattr？这些属性是 OverlayFS 自己用来标记 whiteout、opaque 等状态的，属于实现细节，不是文件数据的一部分。

---

## create_node_directory：目录创建 [F-029]

目录 copy-up 比普通文件复杂，因为可能涉及多层合并：

1. 检查父目录是否已在 upper 层（没有则先 copy-up 父目录——递归）
2. 生成临时名
3. 在 workdir `mkdirat()` 创建临时目录
4. 复制目录的 xattr 和 mode
5. 尝试 `renameat2(RENAME_NOREPLACE)` 原子移动到 upper
   - 如果目标已存在（来自其他层）：使用 `RENAME_EXCHANGE` 交换
6. 对于 RENAME_EXCHANGE 情况：交换后原临时目录（现在是 lower 的"幻影"）需要清理

目录不递归复制内容——子文件和子目录保持原样，在被访问时再按需 copy-up。

---

## Copy-up 后的状态更新

copy-up 成功后，节点被标记为"已上推"：

```rust
node.layer_idx = 0;                      // 现在在 upper 层
node.tmp_ino = new_stat.st_ino;          // upper 层的新 inode
node.tmp_dev = upper_layer.st_dev();     // upper 层的设备号
node.hidden = false;                     // 清除临时标记
node.hidden_path = None;                 // 清除临时路径
node.do_unlink = false;                  // 清理临时标记
node.do_rmdir = false;                   // 清理临时标记
```

**注意**：copy-up 后 InodeKey 改变了（tmp_ino/tmp_dev 是 upper 层的新值）。InodeTable 需要：
- 为新 key 创建或更新 OvlIno
- 旧 key 的 OvlIno 减少引用
- fuse_ino 保持不变（用户态看到的文件身份不变）

---

## 性能优化要点

| 优化 | 效果 |
|------|------|
| **三级回退策略** | 优先使用最快的可用方法，reflink 命中时性能有数量级提升 |
| **惰性 copy-up** | 只复制实际修改的文件，而不是整个 lower 层 |
| **workdir 原子 rename** | 避免部分复制文件被看到，减少锁持有时间 |
| **1MB 缓冲区** | 平衡系统调用次数和内存占用 |
| **跳过内部 xattr** | 避免复制无关元数据 |
| **目录不递归** | 创建空目录即可，子项按需 copy-up |

---

## 相关概念

- [FUSE 与 OverlayFS 基础](00-introduction.md) — OverlayFS 层结构与 copy-up 动机
- [节点与 inode 管理](01-node-inode.md) — copy-up 如何改变节点的 layer_idx 和 InodeKey
- [whiteout 与目录合并](03-whiteout.md) — 删除操作如何通过 whiteout 实现（也触发 copy-up）
- [挂载选项与运行时统计](04-mount-options.md) — volatile_mode 对 fsync 的影响
