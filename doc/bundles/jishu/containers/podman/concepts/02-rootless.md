---
type: Concept
title: "Rootless 容器安全模型"
description: "user namespace 映射、fuse-overlayfs 存储、slirp4netns 网络、cgroup v2 资源限制、禁用 --privileged 原则与常见问题排查。"
tags: [podman, rootless, security, user-namespace, cgroup-v2, fuse-overlayfs, slirp4netns]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:40:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:40:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: libpod
    resource: /references/libpod-source.md
    title: libpod 核心与外部协同库源码
---

# Rootless 容器安全模型

Rootless（无根）模式是 Podman 最具差异化的安全特性：**普通非特权用户（非 root、不在 wheel/docker 组）可以直接创建和运行容器**，容器内的 root 用户被映射到宿主机的普通 UID 范围，从内核层面隔离了容器对宿主机的提权路径。

## 前置条件（最小化内核与发行版要求）

| 组件 | 最低要求 | 说明 |
|------|---------|------|
| 内核版本 | ≥ 5.14（推荐 ≥ 5.19+） | cgroup v2  delegation、overlayfs 下层白名单、user namespace 数量上限放宽 |
| 发行版 | RHEL 9 / CentOS Stream 9 / Fedora 37+ / Debian 12 / Ubuntu 22.04.3+ | 打包了新内核与 fuse-overlayfs、shadow-utils 新版 |
| shadow-utils | ≥ 4.9 | 提供 `subuid`、`subgid` 管理 |
| fuse-overlayfs | ≥ 1.10 | 用户态 overlayfs（rootless 存储驱动） |
| slirp4netns | ≥ 1.2 | 用户态网络栈（port_netns_mode=slirp4netns） |
| crun | （推荐）替代 runc | 更低内存占用、更快启动；支持 cgroup v2 更好 |

```bash
# RHEL 9 / CentOS Stream 9 一键安装依赖
sudo dnf install -y fuse-overlayfs slirp4netns crun shadow-utils
```

## 核心机制一：user namespace UID/GID 映射

Rootless 的本质是**把宿主机普通用户的 65536 个连续 UID/GID 区间分配给容器 user namespace**，使得容器内看到的 `uid=0(root)` 实际上对应宿主机上 `uid=100000` 这样的普通用户。

### Step 1：配置 subuid/subgid
/etc/subuid 和 /etc/subgid 规定每个用户可拥有的 subordinate ID 区间。格式：

```
# /etc/subuid（每行 = 用户:起始UID:数量）
devops:100000:65536
# /etc/subgid
devops:100000:65536
```

修改后必须执行：
```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 devops
```

### Step 2：验证映射生效
```bash
$ podman info --format '{{.Host.Security.Rootless}}'
true
$ podman unshare cat /proc/self/uid_map
         0       1000          1
         1     100000      65536
# 解读：容器内 uid 0 → 宿主机 uid 1000（当前用户本身）；1~65535 → 100000~165535
```

### --userns 选项说明

| 选项 | 作用 |
|------|------|
| `--userns=auto`（默认） | 自动从 subuid 区间挑一段空闲的 |
| `--userns=keep-id` | 容器内 uid 与运行用户 uid 完全一致（开发卷挂载最常用） |
| `--userns=host` | 禁用 user namespace 映射（特权模式，不推荐） |
| `--uidmap / --gidmap` | 手工指定精确映射 |

> 开发场景的"卷宿主机文件不属主"问题：用 `--userns=keep-id` 或 `podman unshare chown -R ...` 解决。

## 核心机制二：fuse-overlayfs 用户态存储驱动

Overlayfs 是 Linux 内核的联合文件系统，**但 rootless 用户无权挂载内核原生 overlayfs**（需要 CAP_SYS_ADMIN）。Podman 通过 fuse-overlayfs 提供等价功能：

```text
   ┌──────────────────────────────────┐
   │      容器写操作（upper 层）        │
   │  ~/.local/share/containers/.../diff/
   ├──────────────────────────────────┤
   │ fuse-overlayfs (FUSE 用户态进程)  │ ← ↓ 对容器看起来像单个文件系统
   ├──────────────────────────────────┤
   │  镜像层（lower 层，只读，解压）    │
   │  ~/.local/share/containers/.../overlay-layers/
   └──────────────────────────────────┘
```

验证存储驱动：
```bash
$ podman info --format '{{.Store.GraphDriverName}}'
overlay
$ podman info --format '{{.Store.GraphStatus}}'
map[Backing Filesystem:xfs Native Overlay Diff:false Supports d_type:true Using metacopy:false]
# "Native Overlay Diff: false" 表示正在使用 fuse-overlayfs（正确）
```

**必须挂载 /dev/fuse**：rootless 容器的 `--device /dev/fuse` 是 fuse-overlayfs 工作的前提——这也是为什么 Podman 嵌套运行时必须显式透传该设备。

## 核心机制三：slirp4netns 用户态网络

Rootless 下用户无法创建 veth 网卡对（需要 net admin 能力），因此 Podman 使用 slirp4netns：

```text
  宿主机（普通用户）                      容器 net namespace
  ┌─────────────┐     slirp4netns       ┌──────────────┐
  │ TCP socket  │ ◄── 用户态 TCP/IP ───► │ eth0 10.0.2.x│
  │  :8080      │     (完全不需要        │ 默认 GW:10.0.2.2
  └─────────────┘      NET_ADMIN)       │ DNS: 10.0.2.3
                                         └──────────────┘
```

端口发布：`-p 8080:80` → slirp4netns 监听宿主机 0.0.0.0:8080，转发到容器 80。

### 网络模式对比

| 模式 | 说明 | 性能 | 备注 |
|------|------|------|------|
| `slirp4netns`（默认） | 用户态 | 中 | 无需特权，通用 |
| `pasta`（新，推荐） | 基于 passt | 高 | 替代 slirp4netns，性能更好 |
| `rootlesskit` | 另一种用户态栈 | 中 | Docker 也用 |

## 核心机制四：cgroup v2 资源限制

Rootless 容器的 CPU/内存限制必须使用 **cgroup v2 delegation**：systemd 把某 cgroup 子树的写权限委托给普通用户。

### 启用方式（必须一次）

```ini
# /etc/systemd/system/user@.service.d/delegate.conf
[Service]
Delegate=memory pids cpu cpuset hugetlb
```

重启后验证：
```bash
$ cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/cgroup.controllers
cpuset cpu memory hugetlb pids
```

### 用法（与 root 模式完全一致）
```bash
podman run --memory=1g --cpus=2 --pids-limit=512 --read-only-tmpfs=false nginx
```

### 常见坑：limits.conf 没开导致内存限制被拒绝
```conf
# /etc/security/limits.d/99-rootless.conf
@users        hard    memlock        4294967296
@users        hard    nofile         65535
root          hard    memlock        unlimited
```

## --privileged 的禁用原则

> 🚨 **Rootless 模式下严禁使用 `--privileged`**。

`--privileged` 在 rootless 下虽然不能直接拿到宿主机 root（user namespace 还在），但会打开以下危险开关：
- 绕过所有 Linux capability 白名单（给容器内进程 CAP_SYS_ADMIN / CAP_NET_ADMIN 等 40+ 权限）
- 取消 seccomp 系统调用过滤
- 取消 SELinux 隔离标签
- 允许挂载任意设备

正确做法：使用 `--cap-add` 精确添加需要的单个能力，或 `--security-opt label=type:spc_t` 放宽 SELinux（单维度）。

## 常见问题排查清单

| 现象 | 原因 | 修复 |
|------|------|------|
| `cannot find UID map for user xxx` | subuid/subgid 没配置 | `sudo usermod --add-subuids ...` 后重新登录 |
| `overlay: mount program didn't have enough privileges` | fuse-overlayfs 没装或 /dev/fuse 不可见 | 安装 fuse-overlayfs；嵌套时 `--device /dev/fuse` |
| `port bindings not available`（无法开低端口 <1024） | rootless 不能 bind <1024 | 开 sysctl：`net.ipv4.ip_unprivileged_port_start=80` |
| cgroup 限制无效 | delegation 没开 | 配置 `Delegate=` 后 reboot，或 `podman info` 查看 `CgroupVersion: v2` |
| 卷挂载的文件属主是 nobody | user namespace 映射冲突 | 用 `--userns=keep-id` 或 `podman unshare chown` |
| 镜像拉取报 "permission denied" 写 ~/.local/share | XDG_DATA_HOME 指向了 NFS / 只读目录 | 设 `export XDG_DATA_HOME=/path/to/local/disk` |

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — daemonless 架构基础
- [/concepts/03-docker-compat.md](03-docker-compat.md) — 与 docker rootless 对比
- [/examples/01-rootless-production.md](../examples/01-rootless-production.md) — 完整生产部署步骤
