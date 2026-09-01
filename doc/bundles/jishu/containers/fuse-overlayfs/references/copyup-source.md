---
type: Reference
title: Copy-up 机制 API 参考
description: src/copyup.rs 源码参考——copy-up 三级优化策略、copy_data 数据复制、copy_xattr 属性复制、create_node_directory 目录创建、完整 copyup 流程
tags: [reference, api, copyup, copy-up, reflink, sendfile, xattr, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: fuse-overlay-copyup
    title: src/copyup.rs
    path: external/dao/action/Containers/fuse-overlayfs/src/copyup.rs
---

# Copy-up 机制 API 参考

> 信源文件：copyup.rs

本文档记录 fuse-overlayfs 的 copy-up（拷贝上推）机制 API。Copy-up 是 OverlayFS 的核心操作：当首次修改下层（lower）只读文件时，将其完整复制到上层（upper）可写层，后续修改作用于上层副本。

---

## Copy-up 策略概览

fuse-overlayfs 实现了三级优化的数据复制策略，按性能从高到低自动降级：

```
1. FICLONE (reflink)  ──→  2. sendfile  ──→  3. read/write 循环
   (内核级写时复制)        (零拷贝)          (1MB 缓冲区)
```

| 策略 | 系统调用/技术 | 性能 | 前提条件 |
|------|--------------|------|---------|
| reflink | `FICLONE` ioctl | 瞬时（O(1)，不实际复制数据） | 底层文件系统支持（Btrfs、XFS、ZFS） |
| sendfile | `sendfile()` | 高（内核空间零拷贝） | 两个 fd 之间可建立管道 |
| read/write | `read()` + `write()` 循环 | 中（1MB 缓冲区） | 所有文件系统（兜底方案） |

---

## copy_xattr() — 扩展属性复制 [F-027]

```rust
fn copy_xattr(sfd: RawFd, dfd: RawFd) -> FsResult<()>
```

将源文件的扩展属性（xattr，extended attributes）复制到目标文件。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `sfd` | `RawFd` | 源文件描述符 |
| `dfd` | `RawFd` | 目标文件描述符 |

### 过滤规则

复制时跳过以下 OverlayFS 内部使用的 xattr 前缀：
- `trusted.overlay.`
- `user.overlay.`
- `overlay.`

这些 xattr 由 OverlayFS 自身管理（如 opaque 标记、whiteout 等），不应复制。

### 流程

1. 调用 `flistxattr(sfd, ...)` 获取源文件 xattr 列表
2. 遍历列表中的每个 xattr 名：
   - 若名以跳过前缀开头，跳过
   - 否则调用 `fgetxattr(sfd, name, ...)` 获取值
   - 调用 `fsetxattr(dfd, name, value, ...)` 设置到目标文件
3. 全部成功返回 `Ok(())`

---

## copy_data() — 数据内容复制 [F-028]

```rust
fn copy_data(sfd: RawFd, dfd: RawFd, size: i64) -> FsResult<()>
```

将源文件的数据内容复制到目标文件，实现三级回退策略。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `sfd` | `RawFd` | 源文件描述符（只读） |
| `dfd` | `RawFd` | 目标文件描述符（只写） |
| `size` | `i64` | 源文件大小（字节） |

### 三级复制策略实现

#### 第一级：FICLONE（reflink）

```rust
// 尝试 ioctl FICLONE
let ret = unsafe { libc::ioctl(dfd, libc::FICLONE, sfd) };
if ret == 0 {
    return Ok(());
}
```

`FICLONE` 是 Linux 的写时复制（Copy-on-Write）克隆 ioctl：
- 不实际复制数据块，仅增加文件系统引用计数
- 源和目标必须在同一支持 reflink 的文件系统上
- 成功时瞬间完成，O(1) 时间复杂度
- 失败（如不支持、跨文件系统）时 fallthrough 到下一级

#### 第二级：sendfile

```rust
let mut remaining = size;
while remaining > 0 {
    let ret = unsafe {
        libc::sendfile(
            dfd,
            sfd,
            null_mut(),
            remaining as usize,
        )
    };
    if ret > 0 {
        remaining -= ret as i64;
    } else if ret < 0 {
        // sendfile 失败，break 到 read/write 回退
        break;
    }
}
if remaining == 0 {
    return Ok(());
}
```

`sendfile()` 在两个文件描述符之间直接在内核空间复制数据：
- 避免用户空间和内核空间之间的数据拷贝
- 比 read/write 循环快约 2-3 倍
- 在某些特殊 fd（如管道、某些设备）上可能失败
- 失败时 fallthrough 到最后一级

#### 第三级：read/write 循环（兜底）

```rust
let mut buf = vec![0u8; 1024 * 1024]; // 1MB 缓冲区
loop {
    let n = read(sfd, &mut buf)?;
    if n == 0 {
        break;
    }
    let mut written = 0;
    while written < n {
        let w = write(dfd, &buf[written..n])?;
        written += w;
    }
}
```

最通用的兜底方案：
- 1MB 大小的堆缓冲区
- 循环 read 直到 EOF
- 处理 write 可能返回部分写入的情况
- 适用于所有文件系统和文件类型

---

## create_node_directory() — 目录递归创建 [F-029]

```rust
pub fn create_node_directory(
    layers: &[OvlLayer],
    workdir_fd: RawFd,
    parent: &OvlNode,
    name: &[u8],
    mode: u32,
) -> FsResult<()>
```

在 upper 层递归创建目录，用于 copy-up 目录时使用。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `layers` | `&[OvlLayer]` | 层栈 |
| `workdir_fd` | `RawFd` | workdir 目录 fd |
| `parent` | `&OvlNode` | 父目录节点（必须在 upper 层） |
| `name` | `&[u8]` | 要创建的目录名 |
| `mode` | `u32` | 目录权限模式 |

### 实现策略

在 workdir 中创建临时目录后原子性 rename 到 upper 层，支持与已存在目录交换：

1. 生成临时名（如 `.{name}#{random}`）
2. 在 workdir 中 `mkdirat()` 创建临时目录
3. 复制下层目录的 xattr（如需要）
4. 尝试 `renameat2()` with `RENAME_NOREPLACE` 原子移动到 upper 层
   - 若目标已存在（来自其他层）：使用 `RENAME_EXCHANGE` 交换
5. 设置正确的 mode、时间戳等属性

> **为什么用 workdir 临时文件？** OverlayFS 要求 copy-up 是原子操作：文件先在 workdir 完整创建，再 rename 到 upper，避免其他进程看到不完整状态。

---

## copyup() — 完整 Copy-up 入口 [F-030]

```rust
pub fn copyup(
    layers: &[OvlLayer],
    workdir_fd: RawFd,
    node: &mut OvlNode,
) -> FsResult<()>
```

执行完整的 copy-up 操作，将节点从当前层复制到 upper 层（索引 0）。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `layers` | `&[OvlLayer]` | 层栈 |
| `workdir_fd` | `RawFd` | workdir 目录 fd |
| `node` | `&mut OvlNode` | 要 copy-up 的节点（可变引用，copy-up 后更新 layer_idx） |

### 按文件类型分支处理

#### 目录（S_ISDIR）

调用 `create_node_directory()` 递归创建到 upper 层。

#### 符号链接（S_ISLNK）

1. 在源层 `readlinkat()` 读取链接目标
2. 在 workdir 临时名 `symlinkat()` 创建符号链接
3. `renameat()` 原子移动到 upper
4. 复制 xattr
5. 设置时间戳

#### 特殊文件（S_ISCHR / S_ISBLK / S_ISFIFO / S_ISSOCK）

1. `fstatat()` 获取源文件的 rdev（设备号）
2. 在 workdir 临时名 `mknodat()` 创建特殊文件
3. `renameat()` 原子移动到 upper
4. 复制 xattr
5. `fchmod()` 设置权限
6. 设置时间戳

#### 普通文件（S_ISREG）

```
源层 open(O_RDONLY) ─┐
                     ├─→ workdir 临时文件 open(O_WRONLY|O_CREAT|O_EXCL)
                     │    │
                     │    ├─→ copy_data(sfd, dfd, size)  // 三级数据复制
                     │    ├─→ futimens(dfd, ...)         // 设置时间戳
                     │    ├─→ copy_xattr(sfd, dfd)       // 复制扩展属性
                     │    └─→ fchmod(dfd, mode)          // 设置权限
                     │
                     └─→ renameat(临时名 → upper目标名)  // 原子替换
```

### Copy-up 完成后的状态更新

copy-up 成功后，更新节点状态：
- `node.layer_idx = 0`（标记为已在 upper 层）
- 更新 `tmp_ino` 和 `tmp_dev` 为 upper 层的新值
- 清除 `hidden`、`do_unlink`、`do_rmdir` 标记

---

## Copy-up 触发时机

Copy-up 是惰性的——仅当首次执行**修改操作**时触发：

| 操作 | 是否触发 copy-up |
|------|----------------|
| `read()` / `readdir()` / `getattr()` / `lookup()` | 否（只读操作） |
| `write()` / `truncate()` | 是 |
| `mkdir()` / `create()` / `mknod()` / `symlink()` | 是（新文件直接在 upper 创建） |
| `unlink()` / `rmdir()` | 是（需要创建 whiteout） |
| `rename()` | 是（源文件需要 copy-up） |
| `chmod()` / `chown()` / `utimens()` | 是（元数据修改） |
| `setxattr()` / `removexattr()` | 是（xattr 修改） |

---

## 错误处理

所有 copy-up 函数返回 `FsResult<()>`，错误时设置对应的 errno：
- `EIO`：IO 错误
- `ENOSPC`：磁盘空间不足
- `EPERM` / `EACCES`：权限不足
- `EROFS`：upper 层只读（异常情况）
