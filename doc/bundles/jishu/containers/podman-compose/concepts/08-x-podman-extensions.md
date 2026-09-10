---
type: Concept
title: x-podman 扩展字段全解
description: 官方 Extensions 文档视角系统梳理 podman-compose 对 Compose 格式的全部 x-podman 扩展：容器/密钥/网络/Pod 字段与 Docker Compose 兼容开关
tags: [podman, compose, x-podman, extensions, compatibility, networking, secrets]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: docs
    resource: /references/docs-source.md
    title: podman-compose docs/ 与 completion/ 信源登记（Extensions.md）
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# x-podman 扩展字段全解

Compose Spec 是跨运行时的中立格式，但 Podman 有自己的能力面（用户命名空间映射、rootfs 直跑、pasta/slirp4netns 网络模式、SELinux 重标记等）。podman-compose 的官方桥接方案是 **`x-podman` 前缀扩展字段**：标准字段保持纯净、可被其他实现忽略，Podman 独有能力全部挂在 `x-podman.*` 下。本文按官方 Extensions 文档逐域梳理，并与源码实现对照。

> 设计约定（Compose Spec 的 `x-*` 扩展命名空间）：任何实现遇到不认识的 `x-*` 顶层/字段键都应忽略，因此同一份 compose 文件带 x-podman 字段仍可在 docker-compose 下运行（只是这些字段不生效）。

## 容器级扩展

| 字段 | 作用 | 翻译结果（源码对照） |
|------|------|---------------------|
| `x-podman.uidmaps` | 以给定 UID 映射在新用户命名空间运行容器 | 逐项 `--uidmap` |
| `x-podman.gidmaps` | 同上，GID 映射 | 逐项 `--gidmap` |
| `x-podman.rootfs` | 不经镜像管理，直接使用外部托管的 rootfs | `--rootfs <路径>`；此时 image 字段被忽略并告警 |
| `x-podman.no_hosts` | 不创建容器内 /etc/hosts | `--no-hosts`（源码快照中 up 命令另有全局 `--no-hosts` 旗标，属 1.6.0 之后的未发布变更） |
| `x-podman.passwd` | 配合 `--user` 时是否允许 Podman 改写 /etc/passwd 与 /etc/group | `--passwd=true/false`，默认 true |

rootfs 直跑示例：

```yaml
services:
  my_service:
    command: ["/bin/busybox"]
    x-podman.rootfs: "/path/to/rootfs"
```

> 历史陷阱（源码硬校验）：旧式顶层 `x-podman:` 字典写法已在 1.2.0 迁移为扁平的 `x-podman.*` 字段；若在服务下直接写 `x-podman:` 字典，翻译层会直接报错提示改用 `x-podman.uidmaps`/`x-podman.gidmaps`。

## 密钥级扩展

| 字段 | 作用 |
|------|------|
| `x-podman.relabel`（挂在 secret 定义上） | 文件密钥 bind 挂载时的 SELinux 重标记：`z`（共享标签）或 `Z`（私有标签，仅当前容器可用） |

```yaml
secrets:
  custom-secret:
    x-podman.relabel: Z
```

源码中 run 路径把它拼进挂载选项（基础选项固定 `ro,rprivate,rbind`，追加 `,z` 或 `,Z`）；非法值（非 z/Z）报错。该选项解决 rootless/SELinux 环境下容器进程无权读取宿主密钥文件的常见问题。

## 网络级扩展

挂在顶层 `networks` 的网络定义上：

| 字段 | 作用 | 翻译结果 |
|------|------|---------|
| `x-podman.disable_dns` | 为该网络禁用 DNS 插件 | `podman network create --disable-dns` |
| `x-podman.dns` | 指定网络的 nameserver 列表 | `--dns <逗号分隔>`；与 disable_dns 互斥 |
| `x-podman.routes` | 为网络添加附加路由 | 逐项 `--route`（1.5.0 起） |

`x-podman.dns` 示例（同网络容器共用指定 DNS）：

```yaml
networks:
  my_network:
    x-podman.dns:
      - "10.1.2.3"
      - "10.1.2.4"
```

`x-podman.routes` 示例（阻断到指定子网的连通，路由指向 127.0.0.1）：

```yaml
networks:
  my_network:
    x-podman.routes:
      - "10.2.3.4,127.0.0.1"
```

## 服务网络配置中的扩展

挂在服务的 `networks.<网络名>` 配置块内：

| 字段 | 作用 |
|------|------|
| `x-podman.mac_address` | 指定该网络接口的 MAC（向后兼容；Compose Spec 现已标准化 `mac_address`，新写法推荐标准键） |
| `x-podman.interface_name` | 指定容器内该网络接口的接口名（翻译为 `interface_name=<名>`） |

多网络场景下，容器级 `mac_address` 只应用到第一个网络（依赖 dict 插入顺序）；**容器级 MAC 与网络级 MAC 同时声明会直接报错**。标准网络级字段还有 `ipv4_address` → `ip=`、`ipv6_address` → `ip6=`、`aliases` → `alias=`。

## podman 特有的 network_mode 值

Compose 标准支持 `bridge/host/none/service/container`；podman-compose 额外透传：

| 值 | 含义 |
|----|------|
| `slirp4netns[:<选项>]` | rootless 用户态网络栈（slirp4netns），选项原样透传 |
| `pasta[:<选项>]` | 新版用户态网络栈（pasta），选项原样透传 |
| `ns:<选项>` | 复用指定命名空间 |
| `private` | 私有网络命名空间 |

选项字符串不做解析，原样拼到 `--network=` 后交给 podman。

## podman 特有的挂载类型

标准 `type: volume/bind/tmpfs` 之外，podman-compose 支持：

- **`glob`**（1.6.0 起）：按通配符批量挂载源路径；
- **`image`**（1.6.0 起）：从容器镜像挂载文件（`volume.type=image`，支持 `subpath`）。

这两种类型强制走 `--mount` 而非 `-v`（部分选项只有 --mount 能表达）。

## Docker Compose 兼容开关

行为差异通过**全局** `x-podman:` 段（注意：这是顶层元设置，与服务内的 `x-podman.*` 字段不同）调整，共 4 个键，每个都有等价环境变量 `PODMAN_COMPOSE_<大写键名>`：

| 键 | 环境变量 | 作用 |
|----|---------|------|
| `docker_compose_compat` | `PODMAN_COMPOSE_DOCKER_COMPOSE_COMPAT` | **元开关**：一键开启下面全部三项（仅填充未显式设置的项） |
| `name_separator_compat` | `PODMAN_COMPOSE_NAME_SEPARATOR_COMPAT` | 资源命名分隔符从下划线 `_` 改为连字符 `-`（对齐 docker-compose） |
| `default_net_name_compat` | `PODMAN_COMPOSE_DEFAULT_NET_NAME_COMPAT` | 默认外部网络名对齐 docker-compose（项目名剔除连字符后拼接） |
| `default_net_behavior_compat` | `PODMAN_COMPOSE_DEFAULT_NET_BEHAVIOR_COMPAT` | 无显式网络时的默认网络行为对齐 docker-compose |

### 默认网络行为差异（default_net_behavior_compat 的由来）

服务未声明 network_mode/networks 时，两者行为分歧：

| 顶层 networks | podman-compose 默认 | docker-compose |
|--------------|--------------------|----------------|
| 无 networks | default | default |
| 仅一个网络 net0 | 接入 net0 | default |
| 两个网络 net0/net1 | podman 网桥（`--network=bridge`） | default |
| 含名为 default 的网络 | default | default |

开启兼容后，podman-compose 也始终创建/接入 `<项目>_default` 网络。

```yaml
x-podman:
  docker_compose_compat: true
```

> 迁移方向提示：官方文档明确 `name_separator_compat` 与 `default_net_name_compat` 未来会翻转为默认 true 并最终移除——即长期目标是默认行为向 docker-compose 收敛，兼容开关只是过渡期的逃生门。

## 自定义 Pod 管理

| 全局键 | 环境变量 | 作用 |
|--------|---------|------|
| `in_pod` | `PODMAN_COMPOSE_IN_POD` | `true`（默认）用 `pod_<项目>`；`false` 不用 pod；字符串为自定义 pod 名。命令行 `--in-pod` 优先级最高 |
| `pod_args` | `PODMAN_COMPOSE_POD_ARGS` | 覆盖 pod 创建参数，默认 `["--infra=false", "--share="]`（无 infra 容器、不共享命名空间） |

典型场景：使用 `userns_mode: keep-id:uid=1000` 时需要关闭默认 pod（pod 与用户命名空间组合受限）：

```yaml
services:
  cont:
    image: example/image
    userns_mode: "keep-id:uid=1000"
x-podman:
  in_pod: false
```

自定义 pod 参数（如限制 CPU）：

```yaml
x-podman:
  pod_args: ["--infra=false", "--share=", "--cpus=1"]
```

设置优先级统一为：命令行 > compose 全局 x-podman > 默认值（源码 `resolve_pod_name`/`resolve_pod_args`/`_parse_x_podman_settings`）。未识别的 x-podman 键只告警不报错。

## 相关概念

- [CLI 翻译层与标签状态](05-cli-translation-layer.md)：x-podman 字段翻译成 argv 的实现位置
- [配置加载管线](06-config-pipeline.md)：全局 x-podman 设置与 PODMAN_COMPOSE_* 环境变量的解析
- [rootless 模式下的网络与卷](02-rootless.md)：slirp4netns/pasta 与 SELinux 重标记的 rootless 背景
- [版本演进与能力矩阵](09-version-evolution.md)：各扩展字段引入的版本时间线
- [官方文档信源登记](../references/docs-source.md)：Extensions.md 原文索引
