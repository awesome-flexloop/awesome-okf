---
type: Concept
title: 网络与存储卷
description: Podman网络与存储卷命令详解，CNI/netavark网络栈、Volume结构、命名卷与绑定挂载、rootless网络
tags: [podman, concept, network, volume, netavark, cni, rootless, mount, storage]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 网络命令概览

`cmd/podman/networks/` 目录包含 11 个网络管理命令，负责容器网络的创建、连接、断开、查询和删除。网络是容器与容器、容器与外部世界通信的基础设施。

所有网络命令在 `podman network` 父命令下。

### 网络命令分类

| 分类 | 命令 | 说明 |
|------|------|------|
| **生命周期** | `create` | 创建新网络 |
| | `rm` | 删除网络 |
| | `reload` | 重载网络配置（重启时重新应用网络规则） |
| **连接管理** | `connect` | 将容器连接到网络 |
| | `disconnect` | 将容器从网络断开 |
| **状态查询** | `list` / `network` | 列出网络 |
| | `inspect` | 查看网络详细配置 |
| | `exists` | 检查网络是否存在 |
| **清理** | `prune` | 清理未使用的网络 |
| **更新** | `update` | 更新网络配置 |

## CNI 与 netavark 网络栈

Podman 的容器网络由网络后端负责配置，Podman 支持两种网络栈后端。

### netavark：默认网络栈

netavark 是 containers 社区开发的现代容器网络栈，是 Podman 的默认网络后端：

| 特性 | netavark |
|------|----------|
| **编写语言** | Rust |
| **设计目标** | 专为 Podman 设计，替代 CNI |
| **网络驱动** | bridge（默认）、macvlan、ipvlan、host、none |
| **IP 地址管理** | 内置 IPAM（IP 地址管理），无需额外 DHCP |
| **端口转发** | 内置 rootless 端口转发支持 |
| **IPv6** | 原生双栈支持 |
| **DNS** | 内置容器 DNS 解析（容器名互通） |
| **性能** | 更轻量、更快、内存占用更低 |

netavark 的网络配置存储在 `/etc/containers/networks/`（root）或 `$HOME/.config/containers/networks/`（rootless）。

### CNI：兼容模式

CNI（Container Network Interface）是 Kubernetes 采用的容器网络标准，Podman 保留了对 CNI 的兼容性支持：

- 当检测到 CNI 配置目录时自动使用 CNI 后端
- 支持所有标准 CNI 插件（bridge、portmap、firewall、tuning 等）
- 适合需要复用 Kubernetes CNI 插件生态的场景
- 配置位于 `/etc/cni/net.d/`

### 网络相关源码

网络相关代码分布在 libpod 网络层：

| 文件 | 职责 |
|------|------|
| `libpod/networking_common.go` | 网络配置公共逻辑 |
| `libpod/networking_linux.go` | Linux 平台网络实现 |
| `libpod/networking_freebsd.go` | FreeBSD 平台网络实现 |
| `libpod/networking_pasta_linux.go` | pasta 网络模式（rootless） |
| `libpod/networking_rootlessport.go` | rootless 端口转发实现 |
| `libpod/networking_machine.go` | Podman Machine 虚拟机网络 |

## 网络命令详解

### 创建网络：create

| 命令 | 说明 |
|------|------|
| `create` | 创建自定义网络 |

```bash
podman network create mynetwork
podman network create --driver bridge --subnet 10.88.0.0/16 mynet
podman network create --ipv6 mynet-ipv6
podman network create --internal isolated-net
podman network create --gateway 10.88.0.1 --subnet 10.88.0.0/16 mynet
```

常用标志：
- `--driver, -d`：网络驱动（bridge/macvlan/ipvlan/host/none）
- `--subnet`：指定子网 CIDR
- `--gateway`：指定网关 IP
- `--ip-range`：指定容器 IP 分配范围
- `--ipv6`：启用 IPv6
- `--internal`：创建内部网络（无外部连接）
- `--dns`：自定义 DNS 服务器
- `--label`：添加元数据标签

默认创建的是 bridge 网络，容器间可通过名称互访，有独立的网络命名空间。

### 连接与断开：connect / disconnect

| 命令 | 说明 |
|------|------|
| `connect` | 将运行中或已停止的容器连接到网络 |
| `disconnect` | 将容器从网络断开 |

```bash
podman network connect mynetwork myapp
podman network connect --ip 10.88.0.100 mynet myapp
podman network disconnect mynetwork myapp
podman network disconnect -f mynetwork myapp
```

一个容器可以同时连接到多个网络，每个网络获得一个独立的网络接口和 IP 地址。`--ip` 可指定静态 IP，`-f` 强制断开。

### 列表与详情：list / inspect

| 命令 | 说明 |
|------|------|
| `list` / `network` | 列出所有网络 |
| `inspect` | 查看网络详细配置 |

```bash
podman network ls
podman network ls --filter driver=bridge
podman network ls -q
podman network inspect podman
podman network inspect --format "{{range .Subnets}}{{.Subnet}}{{end}}" mynet
```

默认网络 `podman`（bridge 驱动）在 Podman 初始化时自动创建，所有未指定网络的容器默认连接到此网络。

### 删除与清理：rm / prune

| 命令 | 说明 |
|------|------|
| `rm` | 删除指定网络 |
| `prune` | 清理所有未被容器使用的网络 |

```bash
podman network rm mynetwork
podman network rm -f mynetwork
podman network prune
podman network prune -f
```

默认网络 `podman` 不可删除。如果网络上仍有容器连接，`rm` 默认报错，需 `-f` 强制删除。

### 重载：reload

| 命令 | 说明 |
|------|------|
| `reload` | 重载网络配置，重新应用防火墙规则和端口映射 |

```bash
podman network reload myapp
podman network reload --all
```

当系统防火墙规则被重置（如 firewalld 重启）后，容器的端口映射可能失效。`reload` 重新配置所有网络规则。`--all` 重载所有运行中容器。

### 检查存在：exists

| 命令 | 说明 |
|------|------|
| `exists` | 检查网络是否存在（脚本友好） |

```bash
podman network exists mynetwork && echo "Network exists"
```

### 更新：update

| 命令 | 说明 |
|------|------|
| `update` | 更新已存在网络的部分配置 |

```bash
podman network update --add-dns 8.8.8.8 mynet
```

## 容器网络模式

创建容器时可通过 `--network` 标志指定网络模式：

| 模式 | 说明 |
|------|------|
| `--network bridge`（默认） | 连接到默认 bridge 网络（podman） |
| `--network <network-name>` | 连接到指定自定义网络 |
| `--network host` | 使用宿主机网络命名空间（无网络隔离） |
| `--network none` | 无网络（只有 loopback 接口） |
| `--network container:<name/id>` | 加入另一个容器的网络命名空间 |
| `--network private` | 创建新的私有网络命名空间（不连接默认网桥） |
| `--network slirp4netns` | rootless 模式下使用 slirp4netns 用户态网络栈 |
| `--network pasta` | rootless 模式下使用 pasta（Pack et SubT Ap）网络栈 |

### host 网络模式

`--network host` 让容器直接共享宿主机网络命名空间：
- 容器直接使用宿主机的网络接口
- 端口映射（`-p`）不生效，容器内进程直接占用宿主机端口
- 网络性能最高，但隔离性最低
- rootless 模式下也可用，但需要 pasta/slirp4netns 配合

### none 网络模式

`--network none` 为容器创建独立的网络命名空间但不配置任何网络：
- 只有 loopback（lo）接口
- 无外部网络访问
- 适合完全不需要网络的批处理任务

## rootless 网络

rootless 模式下，普通用户无法创建传统的 bridge 网络设备（需要 CAP_NET_ADMIN），Podman 采用特殊方案实现网络。

### pasta：推荐 rootless 网络

pasta（Pack et SubT Ap）是现代 rootless 网络方案：
- 在内核 5.4+ 上利用网络命名空间和路由实现
- 性能接近 rootful bridge 模式
- 支持 TCP/UDP 端口转发
- 自动处理 NDP/DHCPv6 等
- 是 rootless 模式的默认网络方案

### slirp4netns：兼容方案

slirp4netns 是经典的用户态 TCP/IP 网络栈：
- 在用户空间实现完整的 TCP/IP 协议栈
- 通过 TAP 设备与容器网络命名空间通信
- 性能略低于 pasta，但兼容性更好
- 支持端口转发

### rootless 端口转发

rootless 模式下的端口转发由 `rootlessport` 进程处理（源码 `libpod/networking_rootlessport.go`）：
- 非 root 用户无法直接绑定 1024 以下端口
- rootlessport 在用户空间监听端口并转发到容器
- 支持 `--publish 8080:80` 这样的端口映射
- 内核参数 `net.ipv4.ip_unprivileged_port_start` 控制特权端口边界（默认 1024）

## 卷命令概览

`cmd/podman/volumes/` 目录包含 13 个存储卷管理命令，负责持久化数据和跨容器共享文件。Volume 是容器数据持久化的推荐方式。

所有卷命令在 `podman volume` 父命令下。

### 卷命令分类

| 分类 | 命令 | 说明 |
|------|------|------|
| **生命周期** | `create` | 创建命名卷 |
| | `rm` | 删除卷 |
| | `reload` | 重载卷配置 |
| **状态查询** | `list` / `volume` | 列出卷 |
| | `inspect` | 查看卷详细信息 |
| | `exists` | 检查卷是否存在 |
| **挂载操作** | `mount` | 挂载卷到宿主机目录 |
| | `unmount` | 卸载卷 |
| **导入导出** | `export` | 导出卷内容为 tar 包 |
| | `import` | 从 tar 包导入卷内容 |
| **清理** | `prune` | 清理未使用的卷 |
| **重命名** | `rename` | 重命名卷 |

## Volume 结构

Volume 结构体定义在 `libpod/volume.go`，是 Podman 管理持久化数据的核心抽象。

### Volume 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `config` | `*VolumeConfig` | 卷静态配置（名称、驱动、选项、标签等） |
| `state` | `*VolumeState` | 卷运行时状态（挂载点、引用计数等） |
| `valid` | `bool` | 卷是否可用 |
| `runtime` | `*Runtime` | 反向引用 Runtime |
| `lock` | `lock.Locker` | 并发锁 |

Volume 采用与 Container/Pod 相同的设计模式：config/state 分离、锁保护、valid 标记生命周期。

### VolumeConfig 配置

| 字段 | 说明 |
|------|------|
| `Name` | 卷名称，唯一标识 |
| `Driver` | 卷驱动（默认 local） |
| `MountPoint` | 卷在宿主机上的挂载路径 |
| `CreatedTime` | 创建时间 |
| `Labels` | 用户自定义标签 |
| `Options` | 驱动特定选项 |
| `Scope` | 卷作用域（local/global） |
| `UID`/`GID` | rootless 模式下的 UID/GID 映射 |
| `Anonymous` | 是否为匿名卷（随机名称） |

卷相关源码文件：`libpod/volume.go`（结构定义）、`libpod/volume_inspect.go`（inspect输出）、`libpod/volume_internal.go`（内部方法）。

## 命名卷 vs 绑定挂载

Podman 支持两种数据挂载方式：命名卷（Named Volume）和绑定挂载（Bind Mount）。

### 命名卷

命名卷由 Podman 管理，生命周期独立于容器：

```bash
podman volume create mydata
podman run -v mydata:/data --name app1 myimage
podman run -v mydata:/shared --name app2 myimage
```

| 特性 | 命名卷 |
|------|--------|
| **管理** | 由 Podman 创建和管理 |
| **路径** | 存放在 Podman 管理目录（`/var/lib/containers/storage/volumes/` 或用户目录） |
| **生命周期** | 独立于容器，容器删除不影响卷 |
| **共享** | 可同时挂载到多个容器 |
| **驱动** | 支持多种卷驱动（local、nfs 等） |
| **权限** | 自动处理 UID/GID 映射（rootless 友好） |
| **备份** | 可通过 `podman volume export` 导出 |

### 绑定挂载

绑定挂载直接挂载宿主机目录到容器：

```bash
podman run -v /host/path:/container/path myimage
podman run -v ./config:/etc/app/config:ro,Z myimage
podman run --mount type=bind,src=/data,dst=/data myimage
```

| 特性 | 绑定挂载 |
|------|----------|
| **管理** | 由用户自行管理宿主机目录 |
| **路径** | 用户指定任意宿主机路径 |
| **生命周期** | 随宿主机文件存在而存在 |
| **共享** | 多容器可共享，但用户自行协调访问 |
| **权限** | 需要手动处理 SELinux 标签（:Z/:z） |
| **性能** | 直接映射，无额外开销 |
| **灵活性** | 可挂载单个文件 |

### 挂载标志

绑定挂载常用标志：
- `ro`：只读挂载
- `rw`：读写挂载（默认）
- `Z`：私有 SELinux 标签（只有当前容器可访问）
- `z`：共享 SELinux 标签（多个容器可共享）
- `:U`：自动 chown 到容器内 UID/GID（rootless 常用）

### 选择建议

| 场景 | 推荐方式 |
|------|----------|
| 数据库持久化 | 命名卷 |
| 配置文件挂载 | 绑定挂载 |
| 开发时代码热重载 | 绑定挂载 |
| 跨容器共享数据 | 命名卷 |
| 需要直接访问宿主机文件 | 绑定挂载 |
| 数据备份/迁移 | 命名卷（配合 export/import） |

## 卷命令详解

### 创建卷：create

| 命令 | 说明 |
|------|------|
| `create` | 创建命名卷 |

```bash
podman volume create mydata
podman volume create --label env=prod --label app=web webdata
podman volume create -o o=size=100m -o device=/dev/sdb1 btrfsvol
```

不指定名称时自动生成随机名称（匿名卷）。`-o` 传递驱动特定选项，local 驱动支持 uid、gid、size、o（挂载选项）等。

### 列表与详情：list / inspect

| 命令 | 说明 |
|------|------|
| `list` / `volume` | 列出所有卷 |
| `inspect` | 查看卷详细信息 |

```bash
podman volume ls
podman volume ls --filter dangling=true
podman volume ls -q
podman volume inspect mydata
podman volume inspect --format "{{.Mountpoint}}" mydata
```

inspect 返回卷名称、驱动、挂载点、创建时间、标签、选项等信息。`--filter dangling=true` 列出未被任何容器使用的卷。

### 挂载：mount / unmount

| 命令 | 说明 |
|------|------|
| `mount` | 将卷挂载到宿主机可访问路径 |
| `unmount` | 卸载已挂载的卷 |

```bash
podman volume mount mydata
podman volume mount
podman volume unmount mydata
podman volume unmount --all
```

挂载卷后可在宿主机直接访问卷内容，用于备份、检查或手动修改文件。无参数时列出所有已挂载卷的挂载点。

### 导入导出：export / import

| 命令 | 说明 |
|------|------|
| `export` | 将卷内容导出为 tar 归档 |
| `import` | 从 tar 归档导入内容到卷 |

```bash
podman volume export mydata -o mydata-backup.tar
podman volume export mydata | gzip > backup.tar.gz
podman volume import newvol mydata-backup.tar
cat backup.tar | podman volume import restoredvol -
```

`export` 将卷内所有文件打包为 tar，`import` 将 tar 内容解压到指定卷中。这是卷备份和迁移的主要方式。

### 删除与清理：rm / prune

| 命令 | 说明 |
|------|------|
| `rm` | 删除指定卷 |
| `prune` | 删除所有未使用的卷 |

```bash
podman volume rm mydata
podman volume rm -f mydata
podman volume prune
podman volume prune -f
```

正在被容器使用的卷默认无法删除，需 `-f` 强制删除。`prune` 删除所有未挂载到任何容器的卷，可释放磁盘空间。

### 重命名：rename

| 命令 | 说明 |
|------|------|
| `rename` | 重命名卷 |

```bash
podman volume rename old-name new-name
```

修改卷的名称，卷内容和挂载点不变。

### 重载：reload

| 命令 | 说明 |
|------|------|
| `reload` | 重载卷状态 |

```bash
podman volume reload
```

重新同步卷的状态信息，处理卷驱动变更或状态不一致的情况。

### 检查存在：exists

| 命令 | 说明 |
|------|------|
| `exists` | 检查卷是否存在（脚本友好） |

```bash
podman volume exists mydata && echo "Volume exists"
```

## 临时文件系统挂载：tmpfs

除了命名卷和绑定挂载，Podman 还支持 `--tmpfs` 挂载临时文件系统：

```bash
podman run --tmpfs /tmp:rw,noexec,nosuid,size=100m myimage
```

tmpfs 挂载存储在内存中，容器停止后数据丢失，适合存储敏感临时数据或需要高速临时存储的场景。

## 相关概念

- [容器基础](/concepts/04-container-basics.md) — Linux 命名空间隔离与 NetNS/MountNS 详解
- [Pod一等公民](/concepts/05-pod-first-class.md) — Pod内容器共享网络命名空间机制
- [容器操作命令](/concepts/07-container-commands.md) — run/create 命令的网络与挂载标志
- [Runtime运行时](/concepts/03-runtime.md) — Runtime网络栈与存储初始化
- [架构概览](/concepts/02-architecture-overview.md) — netavark网络后端与containers/storage存储层
