---
type: Example
title: Rootless 模式配置
description: 无根容器（rootless container）场景下 fuse-overlayfs 的完整配置：用户命名空间、UID/GID 映射、subuid/subgid、Podman/Buildah 集成、常见权限问题排查
tags: [example, rootless, rootless-containers, uid-mapping, user-namespace, podman, buildah, bash]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# Rootless 模式配置

**Rootless（无根）容器**是指以普通非特权用户身份运行容器，无需 root 权限。fuse-overlayfs 是无根容器的核心存储驱动，通过 FUSE 和用户命名空间（user namespace）实现完全非特权的叠加文件系统。

本示例详细讲解：
- 什么是用户命名空间和 UID/GID 映射
- 如何配置 /etc/subuid 和 /etc/subgid
- fuse-overlayfs 的 uidmap/gidmap 选项
- 与 Podman/Buildah 集成
- 手动挂载无根 OverlayFS
- 常见权限问题排查

> **前置知识**：建议先阅读 [基本挂载使用](01-basic-mount.md) 和 [挂载选项与运行时统计](../concepts/04-mount-options.md)。

---

## 1. 为什么需要 Rootless 模式

传统容器运行时（如 Docker 早期版本）需要 root 权限，带来安全风险：
- 容器逃逸可能直接获得宿主机 root 权限
- 挂载文件系统需要 CAP_SYS_ADMIN 能力
- 端口 < 1024 需要 root

Rootless 模式通过以下 Linux 内核特性实现非特权运行：
- **用户命名空间（User Namespaces）**：UID/GID 映射，容器内 root 映射到宿主机普通用户
- **FUSE**：用户空间文件系统，无需内核挂载权限
- **Network Namespace**：slirp4netns/pasta 提供非特权网络

fuse-overlayfs 在无根架构中的位置：

```
┌─────────────────────────────────────────────────────────┐
│  普通用户进程（非 root）                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  容器进程（容器内 root: UID 0）                     │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  应用进程                                    │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  用户命名空间: UID 0 → 100000                     │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │  fuse-overlayfs 进程（普通用户运行）                │  │
│  │  - 通过 FUSE 提供叠加文件系统                       │  │
│  │  - UID/GID 映射处理                                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. UID/GID 映射基础

### 2.1 核心概念

用户命名空间建立了容器内外的 UID/GID 映射关系：

```
容器内（User Namespace）    ────映射────   宿主机
UID 0 (root)                ──────────→   100000
UID 1 (bin)                 ──────────→   100001
UID 2 (daemon)              ──────────→   100002
...
UID 65535                   ──────────→   165535
```

映射语法：`container_id:host_id:range`

| 字段 | 说明 | 示例值 |
|------|------|--------|
| container_id | 容器内起始 ID | 0 |
| host_id | 宿主机起始 ID | 100000 |
| range | 映射的 ID 数量 | 65536 |

示例 `0:100000:65536` 表示：
- 容器内 UID 0 ↔ 宿主机 UID 100000
- 容器内 UID 1 ↔ 宿主机 UID 100001
- ...
- 容器内 UID 65535 ↔ 宿主机 UID 165535

### 2.2 subuid/subgid 配置

Linux 通过 `/etc/subuid` 和 `/etc/subgid` 文件为每个用户分配可映射的 ID 范围：

```bash
# 查看当前用户的 subuid 范围
cat /etc/subuid | grep $USER
# 输出示例: xinzo:100000:65536

# 查看 subgid
cat /etc/subgid | grep $USER
# 输出示例: xinzo:100000:65536
```

这表示用户 `xinzo` 被分配了 65536 个 ID：从 100000 到 165535。

#### 配置 subuid/subgid（如果没有）

```bash
# 以 root 身份执行
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER

# 或者直接编辑 /etc/subuid 和 /etc/subgid
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid
```

> **注意**：不同用户的范围不能重叠。多个用户时依次递增，如第二个用户用 165536-231071。

### 2.3 查看可用映射范围

```bash
# 工具：uidmap 包提供了这些命令
sudo apt install uidmap  # Debian/Ubuntu
sudo dnf install shadow-utils  # Fedora

# 查看当前用户可用的 subuid 范围
cat /etc/subuid | grep ^$USER:

# 查看命名空间内的映射（在用户命名空间内执行）
# cat /proc/self/uid_map
#          0     100000      65536
```

---

## 3. fuse-overlayfs 的 UID 映射选项

fuse-overlayfs 通过 `uidmap` 和 `gidmap` 选项支持 UID/GID 转换。[F-009]

### 3.1 uidmap/gidmap 选项

```bash
-o uidmap=container_id:host_id:count,gidmap=container_id:host_id:count
```

典型容器映射：
```bash
-o uidmap=0:100000:65536 -o gidmap=0:100000:65536
```

这告诉 fuse-overlayfs：
- 来自 lower/upper 层的 UID 100000 应呈现为 UID 0（在 FUSE 响应中）
- 来自容器（FUSE 请求）的 UID 0 应转换为 100000 写入磁盘

### 3.2 多段映射

可以指定多段映射（用逗号分隔），但容器场景通常只有一段（0→subuid_start:65536）。

```bash
# 复杂场景示例（不常见）
-o uidmap=0:100000:1000,1000:200000:1000
```

### 3.3 squash_to_uid/squash_to_gid 简化模式

如果不需要保留原始所有者，可以将所有文件 squash 到单个 UID/GID：

```bash
-o squash_to_uid=1000 -o squash_to_gidOWN=1000
```

或者 squash 到 root（需在用户命名空间内）：
```bash
-o squash_to_root
```

---

## 4. 手动 Rootless 挂载示例

让我们手动演示无根模式下的 fuse-overlayfs 挂载。

### 4.1 准备目录

```bash
mkdir -p ~/rootless-demo/{lower,upper,work,merged}

# 创建 lower 文件，属主模拟"宿主机上的容器文件"
# 宿主机上这些文件属主是 100000（对应容器内 root）
echo "root file in container" > ~/rootless-demo/lower/root-file.txt
sudo chown 100000:100000 ~/rootless-demo/lower/root-file.txt

# 创建一个属主为当前用户的文件
echo "user file" > ~/rootless-demo/lower/user-file.txt
```

### 4.2 普通挂载（不转换） vs rootless 挂载对比

**普通挂载（无映射）**：
```bash
# 不使用 uidmap：宿主机看到的 UID 原样呈现
fuse-overlayfs -o lowerdir=~/rootless-demo/lower,upperdir=~/rootless-demo/upper,workdir=~/rootless-demo/work ~/rootless-demo/merged

ls -lan ~/rootless-demo/merged/
# 应该看到 root-file.txt 的 UID 是 100000（不是 0）
# 在宿主机上这是一个普通的"无名"UID（因为 /etc/passwd 中没有 100000）

fusermount -u ~/rootless-demo/merged
```

**带 UID 映射的挂载（rootless 模式）**：
```bash
# 获取你的 subuid 起始值
SUBUID=$(grep ^$USER: /etc/subuid | cut -d: -f2)
SUBGID=$(grep ^$USER: /etc/subgid | cut -d: -f2)
echo "subuid start: $SUBUID, subgid start: $SUBGID"

# 带映射挂载
fuse-overlayfs \
  -o lowerdir=$HOME/rootless-demo/lower,\
upperdir=$HOME/rootless-demo/upper,\
workdir=$HOME/rootless-demo/work,\
uidmap=0:$SUBUID:65536,\
gidmap=0:$SUBGID:65536 \
  $HOME/rootless-demo/merged

# 现在查看：UID 被正确转换了！
ls -lan ~/rootless-demo/merged/
# root-file.txt 的 UID 现在应该显示为 0（容器内的 root）
```

### 4.3 在用户命名空间内验证

要看到"容器内的视角"（文件属主为 root），需要进入用户命名空间：

```bash
# 使用 unshare 进入用户命名空间（需要 uidmap 包）
unshare --user --map-root-user --mount-proc

# 命名空间内，你的 UID 是 0
id
# uid=0(root) gid=0(root) groups=0(root)

# 现在查看挂载点——文件属主正确显示为 root
ls -lan ~/rootless-demo/merged/
# -rw-r--r-- 1 0 0 ... root-file.txt

# 在命名空间内创建文件（作为容器内 root）
echo "created as root in container" > ~/rootless-demo/merged/new-root-file.txt

# 退出命名空间
exit

# 在宿主机上查看：新文件的属主是 100000（映射后的 ID）
ls -lan ~/rootless-demo/upper/
# new-root-file.txt 的 UID 应该是 100000
```

### 4.4 卸载

```bash
fusermount -u ~/rootless-demo/merged
```

---

## 5. Podman 中的 fuse-overlayfs（无根模式）

Podman 原生支持无根模式，会自动配置 fuse-overlayfs。

### 5.1 配置 Podman 使用 fuse-overlayfs

Podman 的存储配置在 `~/.config/containers/storage.conf`：

```toml
[storage]
driver = "overlay"

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

或者使用全局配置 `/etc/containers/storage.conf`。

### 5.2 运行无根容器

```bash
# 无根运行容器（不需要 sudo）
podman run --rm -it alpine sh

# 容器内你是 root
/ # id
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),7(lp)

# 在容器内创建文件
/ # echo "hello from rootless container" > /tmp/test.txt
/ # ls -la /tmp/test.txt
-rw-r--r--    1 root     root            0 Jan  1 00:00 /tmp/test.txt
/ # exit
```

### 5.3 检查 Podman 的 fuse-overlayfs 参数

可以查看 Podman 是如何调用 fuse-overlayfs 的：

```bash
# 找到 fuse-overlayfs 进程
ps aux | grep fuse-overlayfs

# 输出示例（参数很长）：
# fuse-overlayfs -o lowerdir=/home/xxx/.local/share/containers/storage/overlay/l/XXX:/home/xxx/.local/share/containers/storage/overlay/l/YYY,upperdir=/home/xxx/.local/share/containers/storage/overlay/ZZZ/diff,workdir=/home/xxx/.local/share/containers/storage/overlay/ZZZ/work,uidmap=0:100000:65536,gidmap=0:100000:65536,... /home/xxx/.local/share/containers/storage/overlay/ZZZ/merged
```

可以看到 Podman 自动传入了 `uidmap=0:100000:65536,gidmap=0:100000:65536` 参数。

---

## 6. Buildah 中的 fuse-overlayfs

Buildah（构建容器镜像）无根模式同样使用 fuse-overlayfs：

```bash
# 无根构建镜像
buildah bud -t myimage .

# 或者挂载工作容器
buildah from alpine
container=$(buildah from alpine)
buildah run $container -- id
# uid=0(root) ...
```

---

## 7. 直接使用 Rootless Docker（可选）

Docker 也可以配置 rootless 模式（dockerd-rootless-setuptool.sh），同样使用 fuse-overlayfs 作为存储驱动。

```bash
# 设置 Docker 无根模式（需要安装 docker-ce-rootless-extras）
dockerd-rootless-setuptool.sh install

# 然后直接运行 docker（无需 sudo）
docker run --rm -it alpine sh
```

---

## 8. 常见问题与排障

### 8.1 "No subuid ranges found for user"

**错误**：
```
writing to /proc/self/gid_map: Operation not permitted
```
或
```
newuidmap: Could not find mapping for user
```

**原因**：用户没有配置 subuid/subgid 范围。

**解决**：
```bash
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER
# 重新登录后生效
```

### 8.2 "fusermount: option allow_other only allowed if 'user_allow_other' is set in /etc/fuse.conf"

**原因**：非 root 用户使用 `allow_other` 需要 FUSE 配置允许。

**解决**：
```bash
# 编辑 /etc/fuse.conf，取消注释 user_allow_other
sudo sh -c 'echo "user_allow_other" >> /etc/fuse.conf'
```

### 8.3 文件属主显示为 "nobody" 或数字 ID

**原因**：
1. 没有配置正确的 uidmap/gidmap
2. 在用户命名空间外查看（宿主机视角）
3. subuid 范围配置不正确

**解决**：
- 确保挂载时指定了正确的 uidmap/gidmap 参数
- 在用户命名空间内（`unshare --user --map-root-user`）验证容器视角
- 检查 `/etc/subuid` 和 `/etc/subgid` 范围与挂载参数一致

### 8.4 "Permission denied" 访问 lower 文件

**原因**：
- 下层目录/文件权限不允许当前用户访问
- 容器镜像层的权限问题

**解决**：
```bash
# 确保你对所有层目录有访问权限
ls -la ~/.local/share/containers/storage/overlay/
# 如果是手动准备的目录，确保目录权限是 755 或 700
chmod -R u+rwX ~/rootless-demo/
```

### 8.5 "invalid argument" — workdir 跨文件系统

**原因**：workdir 和 upperdir 不在同一文件系统。

**解决**：确保 upper 和 work 在同一个挂载点下（不能一个在 ext4，一个在 tmpfs 或 NFS）。

### 8.6 Podman 报错 "mount helper 'overlay' is not available for rootless"

**原因**：没有安装 fuse-overlayfs，或配置不正确。

**解决**：
```bash
# 安装 fuse-overlayfs
sudo apt install fuse-overlayfs  # Debian/Ubuntu
sudo dnf install fuse-overlayfs  # Fedora

# 或者从源码编译（见示例01）
```

检查 Podman 存储配置：
```bash
cat ~/.config/containers/storage.conf
# 确保 mount_program 指向正确的 fuse-overlayfs 路径
```

### 8.7 性能问题

无根模式下的 fuse-overlayfs 相比内核原生 OverlayFS 有性能开销，但以下方法可以优化：

| 优化 | 方法 |
|------|------|
| **使用 writeback 缓存** | 默认启用，确保不指定 `nowriteback` |
| **增大 max_write** | `-o max_write=1048576` 减少写系统调用 |
| **使用 threaded** | 默认启用，多线程处理请求 |
| **同文件系统** | upper 和 lower 在同一支持 reflink 的文件系统（Btrfs/XFS），copy-up 使用 FICLONE 瞬时完成 |
| **启用 passthrough** | 支持时自动启用，直接传递底层 fd 给内核 |

---

## 9. 完整 Rootless 挂载脚本

以下脚本演示完整的手动无根 OverlayFS 挂载流程：

```bash
#!/bin/bash
set -euo pipefail

DEMO_DIR="$HOME/rootless-overlay-demo"

# 清理
cleanup() {
    if mountpoint -q "$DEMO_DIR/merged"; then
        fusermount -u "$DEMO_DIR/merged" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# 获取 subuid 范围
SUBUID=$(grep ^$USER: /etc/subuid | head -1 | cut -d: -f2)
SUBGID=$(grep ^$USER: /etc/subgid | head -1 | cut -d: -f2)
if [ -z "$SUBUID" ]; then
    echo "Error: No subuid range configured for $USER"
    echo "Run: sudo usermod --add-subuids 100000-165535 $USER"
    exit 1
fi

# 创建目录结构
rm -rf "$DEMO_DIR"
mkdir -p "$DEMO_DIR"/{lower,upper,work,merged}

# 模拟容器镜像层（宿主机上属主为 subuid）
echo "Hello from container root (UID 0 → host $SUBUID)" > "$DEMO_DIR/lower/hello.txt"
sudo chown $SUBUID:$SUBGID "$DEMO_DIR/lower/hello.txt" 2>/dev/null || {
    echo "Note: Could not chown (not root). File will be owned by current user."
    echo "This is fine for basic testing."
}

echo "Mounting with uidmap=0:$SUBUID:65536,gidmap=0:$SUBGID:65536"

# 挂载 fuse-overlayfs
fuse-overlayfs \
    -o lowerdir="$DEMO_DIR/lower",upperdir="$DEMO_DIR/upper",workdir="$DEMO_DIR/work" \
    -o uidmap=0:$SUBUID:65536,gidmap=0:$SUBGID:65536 \
    -o allow_other \
    "$DEMO_DIR/merged"

echo "Mounted at $DEMO_DIR/merged"
echo ""
echo "=== Host perspective (outside user namespace) ==="
ls -lan "$DEMO_DIR/merged/"
echo ""
echo "=== Container perspective (inside user namespace) ==="
echo "Run: unshare --user --map-root-user ls -lan $DEMO_DIR/merged/"
echo ""
echo "Press Enter to unmount and exit..."
read
```

使用方法：
```bash
chmod +x rootless-mount.sh
./rootless-mount.sh
```

---

## 10. 安全注意事项

无根模式比有 root 权限的容器安全得多，但仍需注意：

| 注意事项 | 说明 |
|---------|------|
| **用户命名空间隔离** | 即使容器内是 root，在宿主机上只是普通用户，无法修改系统文件 |
| **FUSE 安全** | FUSE 挂载默认只允许挂载者访问；`allow_other` 需谨慎使用 |
| **subuid 范围不重叠** | 确保不同用户的 subuid 范围不重叠，否则可能越权访问 |
| **setuid 二进制** | 无根容器中 setuid 通常被禁用（nosuid），避免提权 |
| **内核版本** | 使用较新内核（5.x+）获得更好的用户命名空间支持 |

---

## 关键选项回顾

| 选项 | 用途 |
|------|------|
| `uidmap=0:SUBUID:65536` | 容器 UID 0 → 宿主机 SUBUID 起 65536 个 ID |
| `gidmap=0:SUBGID:65536` | 同上，GID 映射 |
| `squash_to_uid=UID` | 将所有文件 squash 到单一 UID（简化场景） |
| `squash_to_root` | Squash 到 UID 0（需在用户命名空间内） |
| `allow_other` | 允许其他用户访问挂载点 |
| `default_permissions` | 内核权限检查（默认启用） |

**相关阅读**：
- [基本挂载使用](01-basic-mount.md) — 基本挂载与 copy-up/whiteout 验证
- [挂载选项与运行时统计](../concepts/04-mount-options.md) — 完整挂载选项参考
- [FUSE 与 OverlayFS 基础](../concepts/00-introduction.md) — FUSE 与 OverlayFS 基本原理
