---
type: Reference
title: "libpod 核心与外部协同库"
description: "libpod Runtime/Container/Pod/Volume 四大实体 + SQLite/BoltDB 持久化 + containers/{storage,image,buildah,common/libnetwork} 四核心协同库调用链与源码信源。"
tags: [podman, libpod, runtime, container, pod, volume, sqlite, boltdb, containers-storage, containers-image, buildah, libnetwork, oci-runtime]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T10:20:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T10:20:00+08:00 }
status: stable
stale_after: 2027-09-07
---

# libpod 核心与外部协同库

本信源登记簿记录 Podman 最底层（libpod 核心 + 四大 containers/* 依赖）的代码结构与调用关系，是 [/concepts/00-introduction.md](../concepts/00-introduction.md)、[/concepts/01-commands.md](../concepts/01-commands.md)、[/concepts/02-rootless.md](../concepts/02-rootless.md)、[/concepts/04-quadlet-kube.md](../concepts/04-quadlet-kube.md) 四篇概念文档的底层事实依据。

## 一、libpod/ —— 容器/Pod/Volume 核心

### 1.1 Runtime：单例总控

| 事实编号 | 内容 | 原始位置 |
|---------|------|---------|
| F-L1 | `type Runtime struct` 包含：store（containers/storage 句柄）、storageConfig、ociRuntime（crun/runc）、rootless 标志、containerDB + podDB + volumeDB（三个 BoltDB/SQLite DB 句柄）、eventer（事件流，写 journald/file/log） | libpod/runtime.go Runtime 结构体 |
| F-L2 | Runtime 的唯一构造方式是 `libpod.NewRuntime(ctx, options...)`：检查内核 feature（namespace/cgroup/overlay）→ 初始化 storage → 打开 BoltDB/SQLite → 枚举已存在容器/Pod/卷 的 state → 返回可操作 Runtime | libpod/runtime.go NewRuntime 函数 |
| F-L3 | **Platform 约束**：Runtime 的完整功能仅 Linux / FreeBSD 有实现；macOS/Windows `podman` 命令会检测本地不支持 → 自动连 podman machine 的 SSH tunnel，不会走到真正的 NewRuntime（它们的 libpod 代码被 build tag 排除） | libpod/runtime_other.go（空桩实现） + build tags |

### 1.2 Container：实体 + 状态机

| 事实编号 | 内容 | 原始位置 |
|---------|------|---------|
| F-L4 | `type Container struct`（真正的结构体字段**不直接对外导出**，读写都通过 DB 事务 + getter/setter 方法），逻辑字段包括：ID、Name、Image/ID、MountPoint、State（结构体 Running/Stopped/Paused/Created/Configured）、OCI config.json 路径、cgroup 路径、PodID（若属于 Pod） | libpod/container.go Container 定义 + libpod/define/container.go State 枚举 |
| F-L5 | 生命周期方法：`ctr.Create(ctx, spec)` → write DB + 写 OCI bundle；`ctr.Start(ctx)` → 调 ociRuntime.CreateContainer + 调 ociRuntime.StartContainer；`ctr.Stop(ctx, timeout)` → SIGTERM → 超时 SIGKILL；`ctr.Exec(ctx, opts)` → 用 OCI runtime 标准的 exec 路径（cgroup/namespace join） | libpod/container_internal_linux.go Create/Start/Stop/Exec 系列 |
| F-L6 | **conmon 附加进程**：`Start` 实际是在 ctr 和 oci runtime 之间再 fork 出 conmon（或 conmon-rs）——它持有 pty、负责 stdout/stderr 环形缓冲日志、tty detach 快捷键、容器退出码记录；这也是为什么 `podman logs -f` 即使 podman 命令退出了也不丢日志的原因 | libpod/container_internal_linux.go start() 内部 conmon 启动段 |

### 1.3 Pod：容器集合控制器

| 事实编号 | 内容 | 原始位置 |
|---------|------|---------|
| F-L7 | `type Pod struct`：ID/Name/Label + InfraContainerID（infra pause 容器句柄） + SharedNamespaces（Network/UTS/IPC/PID 哪些共享） + containers map（业务容器 ID 集合） + 资源限制（Pod 级 cgroup） | libpod/pod.go Pod 定义 |
| F-L8 | `pod.Start(ctx)` = 先 Start infra（获取 net ns + routes） → 再并行 Start 业务容器（infra 存活则业务容器 join net ns）；`pod.Stop` 反向：先杀所有业务容器 → 再杀 infra（释放 net ns） | libpod/pod_internal.go Start/Stop |
| F-L9 | Pod 级 stats/top/logs = 并发查询 infra + 每个业务容器，然后聚合显示；`podman pod ps` 的 STATUS 字段按最低状态（如一个业务容器 exited 就整 Pod Degraded） | libpod/pod.go 聚合方法 |

### 1.4 Volume：命名持久化卷

| 事实编号 | 内容 | 原始位置 |
|---------|------|---------|
| F-L10 | `type Volume struct` 对应一个 `_volumes/<name>` 目录：Driver（默认 local）、MountLabel（SELinux 标签）、Options（UID/GID/quota 等）、VolumeDB 句柄（记录谁引用了它，防止被 prune） | libpod/volume.go + libpod/runtime_volume.go |
| F-L11 | `runtime.Volume.Create()` 调 `containers/storage` 层创建目录并写 label；prune 时反向遍历所有容器的 Mounts，未被引用且未命名的匿名卷才会被删 | libpod/runtime_volume.go PruneVolumes |

### 1.5 持久化 DB：SQLite 与 BoltDB 双模

| 事实编号 | 内容 | 原始位置 |
|---------|------|---------|
| F-L12 | **历史原因两种后端**：老版本默认 BoltDB（`libpod/bolt_state.go`），v5+ 新增 SQLite（`libpod/sqlite_state.go`）作为默认；两者通过 `State` 接口抽象，方法集完全相同（Container/Pod/Volume 的 Save/Get/Delete/List） | libpod/state.go State 接口定义 |
| F-L13 | 每个 Container/Pod/Volume 的完整状态（JSON 序列化后的 State 结构体 + OCI 路径 + 退出码 + 健康检查历史）**只存在 DB 中**，不存分散文件；因此 `podman system reset` = 删所有 DB + 卸所有 mount | libpod/sqlite_state.go 事务 + JSON BLOB 列 |

## 二、containers/storage —— 文件系统层与镜像层存储

> 本库独立于 Podman 仓库开发，位于 vendor/github.com/containers/storage/。以下事实以 Podman v6.x 依赖的稳定版本为准（Grep 验证通过）。

| 事实编号 | 内容 | 调用链位置 |
|---------|------|-----------|
| F-S1 | **GraphDriver 抽象**：overlay（默认）/ vfs / devicemapper / btrfs / zfs；rootless 下 overlay 用 fuse-overlayfs（通过 `storage.conf` 的 `mount_program=/usr/bin/fuse-overlayfs` 启用） | vendor/github.com/containers/storage/drivers/* |
| F-S2 | Layer → Image → Container 三级模型：`Layer` = 单个差异 tar（可写/只读）；`Image` = 多层链 + metadata（config JSON digest）；`Container` = 某 Image 创建出来的可写层 + MountPoint（实际挂载位置） | storage/store.go Store 接口 |
| F-S3 | Podman 的 `podman image build`（Buildah 内）每一步 RUN → 调 storage.CreateLayer + storage.ApplyDiff；`podman commit` = 把可写 container 层的 diff 提交成新 image 顶层 layer | pkg/domain/infra/abi/images.go Commit → storage.SetImageData |
| F-S4 | Rootless 的 subuid/subgid 映射在 storage 层生效：`--storage-opt ignore_chown_errors` 控制 UID 映射失败的宽松/严格模式 | storage/opts.go + RootlessFlags |

## 三、containers/image —— 镜像传输（5 协议）

| 事实编号 | 内容 | 调用链位置 |
|---------|------|-----------|
| F-I1 | `transports.All` 实现 5 种前缀：`docker://`（registry V2）、`docker-archive:`、`oci-archive:`、`dir:`（OCI 目录）、`containers-storage:`（本地 storage） | vendor/github.com/containers/image/v5/transports/alltransports |
| F-I2 | `podman pull` = image.Copy(ctx, srcRef(registry), dstRef(storage))；Copy 过程中会解析 manifest list（多架构镜像）→ 按 `--platform` 选匹配 arch 的 manifest，再拉每层 blob + config | pkg/domain/infra/abi/images.go Pull → image.Copy |
| F-I3 | `podman push` 反向：src=containers-storage → dst=docker://；`podman save/load` = docker-archive: 或 oci-archive: ↔ storage 的互拷 | pkg/domain/infra/abi/images.go Push、Save、Load |
| F-I4 | 认证走 `containers/image/pkg/docker/config`：~/.config/containers/auth.json 或 `--authfile`；与 docker.io 的 login 逻辑和 Docker CLI 完全一致 | pkg/domain/infra/abi/images.go Login、Logout |

## 四、containers/buildah —— 镜像构建

| 事实编号 | 内容 | 调用链位置 |
|---------|------|-----------|
| F-B1 | `podman build` = Buildah 作为 Go 库直接调用（`buildah.Builder`）：解析 Containerfile/Dockerfile 指令 → 每个 FROM 拉镜像 → 每条 RUN 起临时容器执行命令然后 commit 中间层 | pkg/domain/infra/abi/images.go Build → buildah.NewBuilder → builder.Run() |
| F-B2 | `--build-arg / --target / --no-cache / --platform / -f Containerfile:tag` 等 40+ 个 flags 都是 Buildah 原生参数；Podman CLI 只是封装了一层 entities.BuildOptions → buildah.BuildOptions | pkg/specgen 或直接在 abi/images.go 参数传递 |
| F-B3 | BuildKit 替代方案：Podman 不跑 BuildKit daemon，纯进程内（可并发多条 build，但是 go routine 级并发）；因此不需要 buildx 插件，跨平台构建由 `--platform linux/arm64` + qemu-user-static binfmt 完成 | 架构与代码检查：vendor/buildah 包内无 gRPC/daemon client |

## 五、containers/common/libnetwork —— 网络管理

| 事实编号 | 内容 | 调用链位置 |
|---------|------|-----------|
| F-N1 | Netavark 网络栈（v4+ 默认）：`containers/common/libnetwork` 定义 Network/NetworkDriver 接口；Podman 调 `netavark` 二进制（它再调 netlink 写 veth pair / bridge / iptables-nft / aardvark-dns） | pkg/domain/infra/abi/networking.go → netavark JSON API |
| F-N2 | rootless 下不创建真实 bridge，默认 slirp4netns/pasta：Podman 在宿主机起 slirp4netns 进程，把 user namespace 内的 tap fd 转发到宿主机 socket；端口发布由 slirp4netns/pasta 监听宿主机 fd，再转发进 net ns | libpod/networking_linux.go slirp4netns 启动段 |
| F-N3 | `--network container:name` 共享另一个容器的 net ns；`--network pod` 加入 Pod 的 net ns（infra 持有的那个）；`--network host` 直接用宿主机 net ns（rootless 下被 user namespace 隔离，效果略不同） | libpod/container_internal_linux.go Network namespace setup |

## 六、OCI runtime：crun 与 runc

| 事实编号 | 内容 | 调用链位置 |
|---------|------|-----------|
| F-O1 | Podman 不直接启动容器进程，而是先写完整 OCI `config.json` + `runtime-linux.json` 到 bundle 目录，再 execve `crun run`（或 `/usr/sbin/runc`），由它完成 namespace clone、capability 降权、挂载 proc/sys/dev、最终 execve 容器内 PID 1 | libpod/oci/* + libpod/container_internal_linux.go start() 中 ociRuntime 调用段 |
| F-O2 | crun 是 C 写的轻量 runtime，内存占用 <1MB、启动速度显著比 Go 写的 runc 快；RHEL 9 系列默认 crun，Fedora 默认 crun，Ubuntu 默认 runc（可在 containers.conf 改 `runtime` 字段） | containers.conf(5) 与 `podman info --format '{{.Host.OCIRuntime.Name}}'` 验证 |

## 七、协同调用链总览（podman run 的下半球）

```text
  pkg/domain/infra/abi ContainerEngine.Run(opts)
        │
        ├─► specgen.NewSpecGenerator 生成 Spec
        │
        ├─► libpod.Runtime.NewContainer(spec)  ←── 写 containerDB (SQLite)
        │        │
        │        ├─► containers/storage CreateLayer + Mount (rootless 用 fuse-overlayfs)
        │        └─► 写入 OCI bundle 目录 (config.json)
        │
        ├─► libpod.Container.Start(ctx)
        │        │
        │        ├─► containers/common/libnetwork → 调 netavark / slirp4netns 建 net ns
        │        ├─► fork/exec conmon 持有 pty + 日志缓冲
        │        └─► execve crun run $BUNDLE  ←── OCI runtime 最终完成 namespace/cgroup/挂载/PID 1 exec
        │
        ├─► cgroup v2 delegation 设置 memory.max / cpu.weight / pids.max （rootless）
        └─► 把 ExitCode 通道 + Health 定时器写回 containerDB 事务
```

## 相关文档
- [/concepts/00-introduction.md](../concepts/00-introduction.md) — 四层架构图（第三层 libpod / 第四层 containers/*）
- [/concepts/02-rootless.md](../concepts/02-rootless.md) — user namespace / fuse-overlayfs / slirp4netns / cgroup v2 细节
- [/concepts/01-commands.md](../concepts/01-commands.md) — 上层命令到本层的映射
- [/references/cli-domain-source.md](cli-domain-source.md) — CLI + Domain 上两层源码信源
