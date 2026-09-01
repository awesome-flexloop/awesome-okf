---
type: Example
title: 基本挂载使用
description: 从零开始编译 fuse-overlayfs、准备层目录、执行挂载、验证读写、卸载的完整流程，包含单层/多下层/只读挂载等常见场景
tags: [example, beginner, mount, basic-usage, overlayfs, bash]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# 基本挂载使用

本示例带你从零开始体验 fuse-overlayfs 的基本用法：编译、准备层目录、挂载、验证读写、卸载。

学完本示例，你将掌握：
- 如何编译安装 fuse-overlayfs
- OverlayFS 三层目录（lower/upper/work）的作用
- 基本挂载命令
- 如何验证 copy-up 和 whiteout 机制
- 如何正确卸载
- 多下层、只读挂载等常见变体

> **前置知识**：建议先阅读 [FUSE 与 OverlayFS 基础](../concepts/00-introduction.md) 和 [挂载选项与运行时统计](../concepts/04-mount-options.md)。

---

## 1. 环境准备

### 1.1 系统要求

- Linux 内核 >= 4.18.0（用户命名空间支持）[F-004]
- libfuse >= 3.2.1 开发库
- Rust 工具链 >= 1.85.0

```bash
# Ubuntu/Debian 安装依赖
sudo apt install -y libfuse3-dev cargo rustc

# Fedora/RHEL 安装依赖
sudo dnf install -y fuse3-devel cargo rust
```

### 1.2 编译 fuse-overlayfs

```bash
git clone https://github.com/containers/fuse-overlayfs.git
cd fuse-overlayfs
cargo build --release
sudo cp target/release/fuse-overlayfs /usr/local/bin/

# 验证安装
fuse-overlayfs --version
```

---

## 2. 准备 OverlayFS 层目录

OverlayFS 需要三种目录：
- **lowerdir**（只读下层）：基础文件，可以有多个
- **upperdir**（可写上层）：所有修改保存在这里
- **workdir**（工作目录）：原子操作的临时空间，必须与 upperdir 同文件系统

### 2.1 创建工作目录结构

```bash
# 创建演示目录
mkdir -p ~/overlay-demo
cd ~/overlay-demo

# 创建三层目录：lower1（下层1）、lower2（下层2，基础层）、upper、work、merged（挂载点）
mkdir -p lower1 lower2 upper work merged
```

### 2.2 填充下层内容（模拟基础镜像）

```bash
# lower2 是最底层（基础系统）
echo "Hello from lower2 (base layer)" > lower2/base.txt
echo "Shared file from lower2" > lower2/shared.txt
mkdir lower2/docs
echo "Doc from lower2" > lower2/docs/readme.txt

# lower1 是叠加在 lower2 之上的层
echo "Hello from lower1 (patch layer)" > lower1/layer1.txt
echo "Shared file overridden by lower1" > lower1/shared.txt
mkdir lower1/bin
echo "#!/bin/sh" > lower1/bin/hello
echo "echo 'Hello from lower1 script'" >> lower1/bin/hello
chmod +x lower1/bin/hello
```

此时目录结构：
```
~/overlay-demo/
├── lower1/           # 下层1（较高优先级）
│   ├── layer1.txt
│   ├── shared.txt    # 覆盖 lower2 的同名文件
│   └── bin/
│       └── hello
├── lower2/           # 下层2（基础层，最低优先级）
│   ├── base.txt
│   ├── shared.txt    # 被 lower1 覆盖
│   └── docs/
│       └── readme.txt
├── upper/            # 空，可写层
├── work/             # 空，工作目录
└── merged/           # 空挂载点
```

---

## 3. 执行挂载

### 3.1 基本读写挂载

```bash
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work merged
```

> **注意**：lowerdir 中 `lower1:lower2` 的顺序——**最左边优先级最高**。先查找 lower1，找不到再找 lower2。

### 3.2 前台模式（调试用）

如果想在前台运行、看到日志输出：

```bash
# 先卸载之前的挂载
fusermount -u merged

# 前台 + 调试模式
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work,debug,foreground merged
```

`debug` 和 `foreground` 选项说明参见 [挂载选项](../concepts/04-mount-options.md#debug调试模式)。

---

## 4. 验证合并视图

挂载成功后，`merged/` 目录呈现三层的合并视图。

### 4.1 查看文件列表

```bash
ls -la merged/
```

预期输出（文件来自不同层）：
```
drwxr-xr-x  merged/
├── base.txt      # 来自 lower2
├── shared.txt    # 来自 lower1（覆盖了 lower2 的版本）
├── layer1.txt    # 来自 lower1
├── bin/          # 来自 lower1
│   └── hello
└── docs/         # 来自 lower2
    └── readme.txt
```

### 4.2 验证上层优先

```bash
# 查看 shared.txt —— 应该显示 lower1 的版本
cat merged/shared.txt
# 输出: Shared file overridden by lower1

# 验证 lower2 的原始文件未被修改
cat lower2/shared.txt
# 输出: Shared file from lower2
```

### 4.3 运行脚本

```bash
merged/bin/hello
# 输出: Hello from lower1 script
```

---

## 5. 体验 Copy-up 机制

现在尝试修改 lower 层文件，观察 copy-up 如何工作。

### 5.1 修改 lower 层文件触发 copy-up

```bash
# 修改来自 lower1 的 layer1.txt
echo "Modified in upper!" > merged/layer1.txt

# 查看修改后的内容
cat merged/layer1.txt
# 输出: Modified in upper!

# 检查 upper 目录 —— 应该出现了 layer1.txt 的副本
ls upper/
# 应该看到: layer1.txt

# 检查原始 lower1 文件 —— 未被修改！
cat lower1/layer1.txt
# 输出: Hello from lower1 (patch layer)
```

这就是 copy-up 工作的直观体现：
1. 首次写入 `merged/layer1.txt` 时，fuse-overlayfs 将 `lower1/layer1.txt` 复制到 `upper/layer1.txt`
2. 后续读取/写入都作用于 upper 副本
3. lower1 的原始文件保持不变

### 5.2 创建新文件

```bash
echo "New file created in merged" > merged/newfile.txt
ls upper/
# newfile.txt 直接创建在 upper 层（不需要 copy-up）
```

### 5.3 创建目录

```bash
mkdir merged/newdir
touch merged/newdir/inside.txt
ls upper/
# newdir/ 也直接在 upper 创建
```

---

## 6. 体验 Whiteout 删除机制

### 6.1 删除 lower 层文件

```bash
# 删除来自 lower2 的 base.txt
rm merged/base.txt

# 验证合并视图中已不存在
ls merged/base.txt
# ls: cannot access 'merged/base.txt': No such file or directory

# 检查 upper 目录 —— 出现了 whiteout 标记
ls -la upper/
# 应该看到: .wh.base.txt  (这是 whiteout 标记文件)

# 验证 lower2 的原始文件仍然存在
cat lower2/base.txt
# 输出: Hello from lower2 (base layer)
```

`.wh.base.txt` 就是 whiteout 标记——它告诉 OverlayFS "base.txt 已被删除"，合并视图中隐藏 lower 层的同名文件。

### 6.2 在子目录中删除

```bash
rm merged/docs/readme.txt
ls upper/docs/
# .wh.readme.txt 被创建
ls merged/docs/
# 空目录（readme.txt 被 whiteout 遮盖）
```

### 6.3 验证 whiteout 本身不可见

```bash
ls -la merged/
# 注意：看不到任何 .wh. 开头的文件 —— 这些是内部实现细节，对用户隐藏
```

---

## 7. 查看运行时统计

fuse-overlayfs 支持通过 SIGUSR1 获取统计信息。

```bash
# 找到 fuse-overlayfs 进程
PID=$(pidof fuse-overlayfs)
echo "fuse-overlayfs PID: $PID"

# 发送 SIGUSR1 信号
kill -SIGUSR1 $PID

# 如果在前台运行，终端会显示统计信息；
# 如果在后台运行，可能需要查看系统日志或使用前台模式重跑
```

统计项说明参见 [运行时统计](../concepts/04-mount-options.md#运行时统计sigusr1)。

---

## 8. 卸载

```bash
# 使用 fusermount 卸载（FUSE 标准方式）
fusermount -u merged

# 或者使用 umount
sudo umount merged
```

卸载后：
- `merged/` 目录恢复为空
- `upper/` 保留了所有修改和 whiteout
- `work/` 中的临时文件被清理
- `lower1/`、`lower2/` 完全未改动

### 验证持久化

```bash
# 重新挂载（使用同一个 upper）
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work merged

# 之前的修改仍然存在
cat merged/layer1.txt      # 应该是 "Modified in upper!"
ls merged/newfile.txt      # 新文件仍然存在
ls merged/base.txt         # base.txt 仍然被删除
```

---

## 9. 常见挂载变体

### 9.1 多个下层（三层 lower）

```bash
fusermount -u merged

# 创建第三个 lower 层
mkdir -p lower0
echo "Top priority layer!" > lower0/top.txt
echo "Shared from lower0" > lower0/shared.txt

# 挂载三个 lower：优先级 lower0 > lower1 > lower2
fuse-overlayfs -o lowerdir=lower0:lower1:lower2,upperdir=upper,workdir=work merged

cat merged/shared.txt   # 来自 lower0（最高优先级）
# 输出: Shared from lower0
```

### 9.2 只读挂载（无 upperdir）

```bash
fusermount -u merged

# 不指定 upperdir 和 workdir：只读模式
fuse-overlayfs -o lowerdir=lower1:lower2 merged

# 尝试写入会失败
touch merged/readonly-test
# touch: cannot touch 'merged/readonly-test': Read-only file system
```

### 9.3 允许其他用户访问（allow_other）

```bash
fusermount -u merged

# 默认只有挂载者可以访问；allow_other 允许所有用户访问
# 注意：需要 /etc/fuse.conf 中启用 user_allow_other
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work,allow_other merged
```

### 9.4 禁用 writeback 缓存（调试用）

```bash
fusermount -u merged

# nowriteback 禁用内核写回缓存，每次 write 直接到用户空间
# 对性能有影响，但写操作立即可见，便于调试
fuse-overlayfs -o lowerdir=lower1:lower2,upperdir=upper,workdir=work,nowriteback,foreground,debug merged
```

---

## 10. 完整操作流程总结

```bash
# === 完整工作流示例 ===
# 1. 准备目录
mkdir -p /tmp/overlay/{low1,low2,up,work,mnt}
echo "file1" > /tmp/overlay/low1/a.txt
echo "file2" > /tmp/overlay/low2/b.txt

# 2. 挂载
fuse-overlayfs -o lowerdir=/tmp/overlay/low1:/tmp/overlay/low2,\
upperdir=/tmp/overlay/up,workdir=/tmp/overlay/work \
/tmp/overlay/mnt

# 3. 使用（读/写/删）
ls /tmp/overlay/mnt/
echo "modified" > /tmp/overlay/mnt/a.txt
rm /tmp/overlay/mnt/b.txt
echo "new" > /tmp/overlay/mnt/c.txt

# 4. 检查 upper 层
ls -la /tmp/overlay/up/
# 看到: a.txt, c.txt, .wh.b.txt

# 5. 卸载
fusermount -u /tmp/overlay/mnt
```

---

## 11. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| `fuse: device not found` | FUSE 内核模块未加载 | `sudo modprobe fuse` |
| `permission denied` | 无权限访问目录或 FUSE | 检查目录权限；非 root 需确认 user_allow_other |
| `invalid argument` | workdir 与 upperdir 跨文件系统 | workdir 和 upperdir 必须在同一挂载点 |
| `mountpoint is not empty` | 挂载点目录非空 | 使用空目录，或加 `-f` 强制挂载 |
| 卸载提示 `device busy` | 有进程正在访问挂载点 | `lsof merged/` 查找并关闭进程，或 `fusermount -uz` 强制卸载 |

---

**下一步**：继续学习 [rootless 模式配置](02-rootless.md)，了解无根容器场景下的 UID/GID 映射配置。
