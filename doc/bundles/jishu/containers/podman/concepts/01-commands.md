---
type: Concept
title: "核心命令分层与资源模型"
description: "Podman 9 大命令域、容器/镜像/Pod 资源状态机、生命周期操作、查询与批量清理模式。"
tags: [podman, commands, lifecycle, state-machine, containers, images, pods]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:35:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:35:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: cli-domain
    resource: /references/cli-domain-source.md
    title: CLI 层与 Domain 层架构源码
---

# 核心命令分层与资源模型

Podman 的命令体系遵循**名词 + 动词**的 POSIX 风格分层（如 `podman container ls`），同时保留 Docker 兼容的扁平别名（如 `podman ps`）。所有命令围绕 9 大资源域展开，每个资源有完整的状态机与 CRUD 操作集。

## 9 大命令域组织原则

```text
podman <domain> <action> [flags] [args]
│       │        │
│       │        └── 动词：create / start / stop / rm / ls / inspect / prune ...
│       └────────── 名词域：container / image / pod / network / volume / secret / system / manifest / kube+quadlet
└────────────────── 入口二进制
```

### 扁平别名（Docker 兼容层）
为了降低 Docker 用户的迁移成本，高频命令提供了**无域扁平别名**：

| 完整分层命令 | Docker 兼容别名 |
|------------|--------------|
| `podman container run` | `podman run` |
| `podman container create` | `podman create` |
| `podman container ls` | `podman ps` / `podman container list` |
| `podman container exec` | `podman exec` |
| `podman image ls` | `podman images` |
| `podman image pull` | `podman pull` |
| `podman image build` | `podman build` |
| `podman pod ps` | `podman pod list` |

## 容器（Container）状态机与生命周期

容器是 Podman 最核心的资源，其状态机严格遵循 OCI runtime-spec 规范：

```text
  ┌─────────┐  create   ┌──────────┐  start   ┌──────────┐
  │ (不存在) │ ───────▶ │ Created  │ ───────▶ │ Running  │
  └─────────┘           └──────────┘          └────┬─────┘
                         ▲                         │
                         │ init / mount              │ exec / logs / kill
                         │                           ▼
                      ┌──┴──────┐  pause  ┌──────────┐
                      │ Stopped │ ◀────── │ Paused   │
                      └────┬────┘  resume └──────────┘
                           │
              stop / kill  │  start
                           ▼
                      再次运行 ◀─┘
                    (exit_code 持久化)
```

### 生命周期操作清单

| 操作 | 典型命令 | 作用 |
|------|---------|------|
| **创建** | `podman create` | 写入磁盘数据库、准备 rootfs、分配网络，不启动进程 |
| **启动** | `podman start` | 调用 OCI runtime（crun/runc）fork 出容器内 PID 1 |
| **一步到位** | `podman run` | = create + start + 可选 `-d`/`--rm`/`--name` |
| **暂停** | `podman pause` | 发送 SIGSTOP 给所有容器内进程（cgroup freezer） |
| **恢复** | `podman unpause` | 解除 freeze |
| **停止** | `podman stop` | 先发 SIGTERM → 等待 `--stop-timeout`（默认 10s）→ SIGKILL |
| **强杀** | `podman kill` | 直接发信号（默认 SIGKILL，可 `--signal` 指定） |
| **重启** | `podman restart` | stop → start |
| **进入** | `podman exec` | 在运行中容器内 fork 新进程（PID namespace 内） |
| **日志** | `podman logs -f` | 读取 conmon 记录的 stdout/stderr 环形缓冲 |
| **删除** | `podman rm` | 删除数据库记录、卸载 rootfs、清理网络；`-f` 先杀再删 |
| **批量清理** | `podman container prune` | 删除所有停止状态的容器；`-f` 跳过确认 |

### 查询四件套（所有资源通用）

| 查询命令 | 等价语义 | 典型 flags |
|---------|---------|-----------|
| `podman <res> exists` | 存在性布尔 | `--external`（含外部资源） |
| `podman <res> ls` / `list` | 列表过滤 | `--filter key=value`、`--format json`、`-a` 全部、`-q` 仅 ID |
| `podman <res> inspect` | 完整 JSON/YAML | `--format {{.GoTemplate}}`、`--size`（显示磁盘大小） |
| `podman <res> diff` | 文件层变更 | 对比容器创建后 vs 当前的文件增删改（A/C/D 标记） |

## 镜像（Image）操作集

镜像没有状态机，但围绕**层（layer）**和**传输（transport）**展开：

| 类别 | 命令 | 说明 |
|------|------|------|
| **查询** | `images` / `image ls` / `image exists` / `image inspect` / `image tree` | 列表、存在性、完整属性、依赖层树 |
| **获取** | `pull` | 从 registry 拉取；`--platform linux/arm64` 选择多架构 |
| **发布** | `push` | 推到 registry；`--creds` / `--authfile` 认证 |
| **构建** | `build -t name:tag .` | 调用 buildah 从 Containerfile/Dockerfile 构建 |
| **流转** | `save -o file.tar` / `load -i file.tar` | OCI tar 归档的导出/导入（可 `--format oci-archive` / `docker-archive`） |
| **标签** | `tag src:old dst:new` / `untag name:tag` | 增加/删除本地标签 |
| **导入** | `import file.tar name:tag` | 从扁平 rootfs tar 导入为镜像（区别于 load 多层） |
| **搜索** | `search keyword` | 搜索 registry 中的镜像 |
| **差异** | `image diff id` | 显示某镜像层对父层的文件改动 |
| **签署** | `image sign` + `image trust` | cosign/sigstore 镜像签名与信任策略 |
| **SCP** | `image scp` | 跨主机通过 SSH 直接传镜像（免 registry） |
| **清理** | `image prune` / `rmi` | 清理 dangling（<none>:<none>）或全部未使用镜像 |

### 镜像传输协议（containers/image 支持）
Podman 继承了 containers/image 的 5 种镜像传输协议前缀：
- `docker://` — 标准 registry（默认）
- `docker-archive:` — Docker 格式 tar
- `oci-archive:` — OCI 格式 tar
- `dir:` — 本地目录（OCI layout）
- `containers-storage:` — 本地 Podman 存储层

## Pod（豆荚）资源模型

Pod 是一组共享网络、UTS、IPC namespace 的容器集合，是 Kubernetes Pod 的本地同构。Podman 是**首个原生支持 Pod 的 Docker 替代产品**。

| 操作 | 说明 |
|------|------|
| `podman pod create --name web` | 创建空 Pod（内含 infra pause 容器） |
| `podman run --pod web -d nginx` | 在已有 Pod 中加入业务容器 |
| `podman pod start/stop/kill/restart` | 整体启停 Pod 内所有容器 |
| `podman pod ps / inspect / logs` | 列表/详情/聚合日志（`-c` 指定容器） |
| `podman pod stats / top` | 资源统计、进程视图（聚合所有容器） |
| `podman pod prune / rm` | 清理停止的 Pod / 删除 Pod（会先删所有业务容器） |
| `podman pod clone` | 复制整个 Pod 规格并启动 |

**Infra 容器**：每个 Pod 里有一个 `k8s.gcr.io/pause` 等价的极小 infra 容器，它持有 namespace 和 cgroup 句柄，即使所有业务容器退出，Pod 的网络配置也不会消失。

## 通用批量清理：prune 模式

所有资源都提供 `prune` 子命令，用于**清理"不再被引用"的对象**。典型的释放空间流水线：

```bash
# 按依赖顺序：先清容器，再清 Pod，再清网络/卷/镜像
podman container prune -f
podman pod prune -f
podman network prune -f
podman volume prune -f        # 注意：默认不删命名卷，加 --filter=unused-for=168h
podman image prune -a -f       # -a 清理所有未被容器使用的镜像
podman system prune -a -f      # 一键调用以上所有（除卷需要显式 --volumes）
```

`system df` 先查看磁盘占用分布（镜像/容器/卷三栏 Size/Reclaimable），决定是否需要 prune。

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — 四层架构与代码库
- [/concepts/03-docker-compat.md](03-docker-compat.md) — Docker CLI 兼容差异
- [/examples/01-rootless-production.md](../examples/01-rootless-production.md) — 生产环境命令组合实战
