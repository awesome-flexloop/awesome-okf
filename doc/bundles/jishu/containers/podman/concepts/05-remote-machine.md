---
type: Concept
title: "跨平台远程连接与 podman machine"
description: "podman-remote 客户端、system-connection 命名连接（UDS/SSH/TCP）、podman machine init/start/ssh、macOS/Windows/WSL2 差异。"
tags: [podman, remote, podman-remote, podman-machine, connection, ssh, wsl2, qemu, cross-platform]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:55:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:55:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: cli-domain
    resource: /references/cli-domain-source.md
    title: CLI 层与 Domain 层架构源码
---

# 跨平台远程连接与 podman machine

Podman 严格来说是** Linux 专属运行时**：所有容器操作最终要调用 Linux 内核的 namespace、cgroup、overlayfs、netfilter。因此在 macOS、Windows 上需要一层"Podman Machine"（轻量 Linux 虚拟机）；同时在任何平台上都可以把 CLI（本地或远程）指到另一台 Linux 上的 Podman API 服务端——这两套机制合起来实现了 Podman 的跨平台与远程管理。

## 一、两种执行模式：Local vs Remote

```text
  模式 1（本地 Local）                         模式 2（远程 Remote）
┌──────────────────────┐                 ┌──────────────────┐     SSH/UDS/TCP    ┌──────────────┐
│  podman CLI (Linux)  │ ──abi 直调──▶    │  pkg/domain/abi   │ ────────────────▶  │ 远端 Linux    │
│                      │    （同进程）    │   + libpod       │    (pkg/bindings)  │  podman       │
│  Linux 内核          │                   │                  │                    │  system service│
└──────────────────────┘                 └──────────────────┘                    └──────┬───────┘
                                                                                        ▼
                                                                               Linux 内核运行容器
```

| 模式 | 二进制 | 连接方式 | 典型场景 |
|------|-------|---------|---------|
| **Local** | `podman` | 无（pkg/domain/infra/abi 直调） | Linux 服务器、WSL2 发行版内 |
| **Remote** | `podman-remote` 或 `podman --connection` | 通过 HTTP（pkg/domain/infra/tunnel → pkg/bindings → 网络） | macOS / Windows / CI 节点 → 远端 Podman |

> 在 macOS / Windows 上分发的 `podman` 其实就是 `podman-remote`，默认自动连到本地 podman machine。

## 二、system-connection：命名连接管理

`podman system connection` 是连接管理的统一入口，支持三种传输协议，按安全性排序：

| 协议 | URL 格式 | 安全性 | 场景 |
|------|---------|--------|------|
| **Unix domain socket (UDS)** | `unix:///run/user/$UID/podman/podman.sock` | 最高（本地文件权限） | 同机 rootless；WSL2 宿主机 → WSL2 虚拟机 |
| **SSH 隧道** | `ssh://user@host[:port]/path/to/socket` | 高（ssh 协议，默认 key 认证） | 跨主机 LAN / 公网；macOS → 远端 Linux 服务器 |
| **TCP** | `tcp://host:port` 或 `http://host:port` | 低（明文，需额外 TLS） | 仅内网可信环境；一般 front TLS 反代 |

### 添加命名连接

```bash
# 1. SSH 隧道连远端（最常用）
podman system connection add \
  --default \
  --identity ~/.ssh/id_ed25519 \
  prod-server \
  ssh://devops@10.20.30.40:22/run/user/1001/podman/podman.sock

# 2. 本机 rootless 默认 socket（一般自动配）
podman system connection add local uds:///run/user/$UID/podman/podman.sock

# 3. TCP + TLS 示例（需服务端 podman system service --tls-verify ...）
podman system connection add insecure-tcp tcp://127.0.0.1:8888
```

### 连接管理命令

```bash
podman system connection list                     # 列出所有（含 default）
podman system connection default prod-server      # 改默认
podman system connection rename prod-server prod  # 重命名
podman system connection remove old-connection     # 删除
podman system connection reload                    # 重新从 containers.conf 加载
```

### 使用连接

```bash
# 方式 1：按连接名切换（只影响本次）
podman --connection prod-server ps
podman --connection prod-server pull nginx

# 方式 2：改环境变量（脚本场景）
export CONTAINER_CONNECTION=prod-server
export CONTAINER_HOST=ssh://devops@10.20.30.40:22/run/user/1001/podman/podman.sock
podman ps     # 自动走远程

# 方式 3：默认连接（持久化）
podman system connection default prod-server
podman ps     # 走 prod-server
```

> 服务端配置：被远程连接的 Linux 节点需要 `systemctl --user enable --now podman.socket`（rootless 推荐）——用 socket 激活，无客户端时不占资源。

## 三、podman machine：macOS / Windows / 非 Linux 开发机

Podman Machine 是一个开箱即用的最小化 Fedora CoreOS（FCOS）QEMU 虚拟机，预装：内核、cgroup v2、fuse-overlayfs、slirp4netns、Podman 服务端 + podman.socket。开发者只管在本机敲 `podman run`，底层所有真正的容器操作都在这个 VM 里完成。

### 虚拟机后端对比

| 平台 | 默认后端 | 可选后端 | 说明 |
|------|---------|---------|------|
| **macOS (Intel/Apple Silicon)** | Apple Hypervisor.framework | QEMU, libkrun | Apple Silicon 用 aarch64 FCOS 镜像，原生性能好 |
| **Windows 10/11** | WSL2 | Hyper-V, QEMU | WSL2 模式下 Podman 直接装在 WSL2 发行版里，最省资源 |
| **Linux（很少用 machine）** | QEMU/KVM | — | 一般直接用本地 Podman，除非跑隔离的测试集群 |

### 基本操作流程（macOS 示例）

```bash
# 1. 初始化：下载 FCOS 镜像，创建 100GB 磁盘、2 CPU、2GB RAM 的 VM（都可调）
podman machine init \
  --cpus 4 --memory 4096 --disk-size 120 \
  --rootful=false \
  my-dev-machine
# 会输出 SSH 配置、machine 名称、socket 路径

# 2. 启动（首次启动慢，因为要 resize FS + 安装包）
podman machine start my-dev-machine
# 30s 内看到："Machine init complete" 即成功

# 3. 验证：此时本机 podman 已经自动指向 VM
podman info --format '{{.Host.Os}} {{.Host.Arch}}'
# 输出：linux arm64 （在 Apple Silicon 上）

# 4. 交互式 SSH 进 VM（想看日志 / 调配置时）
podman machine ssh my-dev-machine
# 进去后就是正常的 Fedora CoreOS：rpm-ostree、systemctl 都可用
# 退出回到 mac：Ctrl+D 或 exit

# 5. 日常生命周期
podman machine list                        # 列出所有 VM
podman machine inspect my-dev-machine      # 看 CPU/内存/磁盘、SSH 配置
podman machine stop my-dev-machine         # 关机（不丢容器数据）
podman machine start my-dev-machine        # 再开机（容器自动恢复）
podman machine set --cpus=8 --memory=8192  # 调整配置（需要先 stop）
podman machine rm my-dev-machine           # 彻底删除！所有容器和镜像都会丢
```

### macOS / Linux 文件共享：卷挂载的坑

开发场景需要把 mac 本机的源码目录挂进容器。Podman machine 默认用 **virtiofs**（Apple Silicon 推荐）或 **9p**（Intel/QEMU）共享用户 `$HOME` 整个目录：

```bash
# 初始化时显式要求挂载多个目录：
podman machine init \
  --volume /Users/me/projects:/projects \
  --volume /Users/me/.cache/npm:/npm-cache:Z \
  my-machine
```

然后本机就可以直接：
```bash
podman run --rm -v /Users/me/projects/myapp:/app:Z -w /app node:20 npm run dev
# ↑ 这里路径是 mac 本地的；Podman 会自动把 virtiofs 共享的路径传给 VM 内的容器
```

> 常见坑：SELinux 上下文 —— 容器读不到挂进去的文件？加 `:z`（共享）或 `:Z`（私有）标签；`--userns=keep-id` 让容器 UID 与用户一致，避免属主 nobody。

### Windows 推荐：直接 WSL2 原生 Podman

Windows 10/11 22H2+ 上，**跳过 podman machine，直接在 WSL2 发行版里装原生 Podman** 体验最好：

```powershell
# Windows PowerShell（管理员）
wsl --install -d Ubuntu-24.04
# 重启后：
wsl -d Ubuntu-24.04
```

```bash
# 然后在 WSL2 Ubuntu 里（就是纯 Linux 了）
sudo apt update
sudo apt install -y podman fuse-overlayfs slirp4netns crun uidmap
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER
# 重新登录 WSL 即可；podman 直接用，无 VM
```

然后 Windows 侧 `podman-remote`（安装 Podman Desktop 获得）配置一个 WSL2 SSH/UDS 连接，直接连 Ubuntu 里的 Podman。

## 四、多 machine 场景 + 命名连接的组合用法

典型的企业开发桌面：3 个 machine 对应 3 个环境，用命名连接随时切换：

```bash
# 3 个 machine
podman machine init --cpus=2 --memory=2048 dev
podman machine init --cpus=4 --memory=4096 staging-copy   # 模拟生产规格
podman machine init --cpus=8 --memory=8192 perf           # 压测专用

# 给每个 machine 配命名连接（podman machine start 会自动配）
podman system connection list
# 会看到：
# dev         ssh://core@127.0.0.1:PORT1/run/user/...  default=true
# staging-copy ssh://core@127.0.0.1:PORT2/run/user/...
# perf        ssh://core@127.0.0.1:PORT3/run/user/...

# 一键切到压测环境
export CONTAINER_CONNECTION=perf
podman pull myapp:bench-1234
podman run --cpus=8 --memory=8g myapp:bench-1234
```

## 五、故障排查清单（跨平台最高频问题）

| 现象 | 排查 | 修复 |
|------|------|------|
| `connection refused` 连 machine socket | `podman machine list` 看 machine 是否 running；`ssh` 进去 `systemctl --user status podman.socket` | 没运行就 `podman machine start`；socket 没起就 `systemctl --user enable --now podman.socket` |
| machine 启动卡死在 "waiting for VM..." | 查看 `podman --log-level=debug machine start` 日志 | 常因旧镜像损坏：`podman machine rm xxx; podman machine init --image-path latest` |
| 卷挂载进去文件属主不对 / 找不到 | `podman machine inspect xxx` 看 Volumes 列表里真的包含了该路径 | 加挂：`podman machine stop; podman machine set --volume /new/path:/inside xxx; start` |
| macOS 构建超慢（npm/pip install） | virtiofs 小文件 IO 比本地慢 2-3 倍；SELinux 再乘 1.5 | 用 named volume（挂容器内）而不是 hostPath；`podman create volume cache && -v cache:/node_modules` |
| WSL2 可用内存越来越少 | WSL2 默认吃满 50% RAM 不回收 | `.wslconfig` 里加 `memory=8GB; processors=4; pageReporting=true` |
| SSH 连接远端提示 "no route to host" | 先 `ssh user@host` 直连，再 ssh 里 `ls /path/to/socket` 权限是该用户 | ssh 不通走网络；socket 不通开用户权限 + systemd user lingering |

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — abi/tunnel 双实现的由来
- [/concepts/03-docker-compat.md](03-docker-compat.md) — 与 DOCKER_HOST 兼容
