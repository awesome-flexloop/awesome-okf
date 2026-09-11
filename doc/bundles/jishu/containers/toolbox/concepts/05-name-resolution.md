---
type: Concept
title: "镜像与发行版名称解析机制"
description: "Distro 注册表驱动的四发行版支持：默认值/配置文件/CLI 三级优先级、全限定镜像构造、release 校验规则、容器命名与 toolbox.conf。"
tags: [toolbx, toolbox, distro, fedora, rhel, ubuntu, arch, registry, viper, resolution]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T11:45:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T11:45:00+08:00 }
status: stable
stale_after: 2027-09-11
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
    title: 实现层源码地图
  - id: docs-man
    resource: /references/docs-man-source.md
    title: 官方手册、设计目标与版本演进信源
---

# 镜像与发行版名称解析机制

`toolbox create --distro ubuntu --release 24.04` 最终为什么会去拉 `quay.io/toolbx/ubuntu-toolbox:24.04`？默认容器名 `fedora-toolbox-44` 从哪里来？本篇拆解 `pkg/utils` 中的名称解析器——这是 Toolbx 多发行版支持的核心，也是理解 [/concepts/02-workflow.md](02-workflow.md) 默认命名规则的实现层。

## Distro 注册表：用数据结构而非 switch 支持发行版

`pkg/utils/utils.go` 用一张 4 项注册表描述全部支持发行版，每项 7 个字段：

| distro key | 容器名前缀 | 镜像 basename | 必须显式 release | 全限定镜像 | release 规则 |
|---|---|---|---|---|---|
| `arch` | `arch-toolbox` | `arch-toolbox` | 否 | `quay.io/toolbx/<image>` | 仅 `latest`/`rolling`，归一化为 latest |
| `fedora` | `fedora-toolbox` | `fedora-toolbox` | 是 | `registry.fedoraproject.org/<image>` | 正整数，接受 `f36`/`F36` 前缀 |
| `rhel` | `rhel-toolbox` | `toolbox` | 是 | `registry.access.redhat.com/ubi<major>/<image>` | `<major>.<minor>`，如 8.5、9.3 |
| `ubuntu` | `ubuntu-toolbox` | `ubuntu-toolbox` | 是 | `quay.io/toolbx/<image>` | `YY.MM`：年 ≥4 不超过两位且无前导零，月 01-12 |

注意两个易错点：

- RHEL 镜像 basename 是 `toolbox`（不是 rhel-toolbox），最终形如 `registry.access.redhat.com/ubi9/toolbox:9.3`；major 版本号由 release 点号前半段切出。
- Arch 的 `ReleaseRequired=false`：`--distro arch` 不需要 release，默认 `latest`。

## 默认值如何确定：os-release 探测与 Fedora 兜底

包初始化时读取 `/etc/os-release` 的 `ID` 与 `VERSION_ID`：

- 主机 ID 命中注册表（如 `fedora`/`ubuntu`）→ 默认 distro=主机 ID、默认 release=主机版本、默认容器名前缀同步切换；
- 主机不被识别（如 Debian、openSUSE）→ 兜底常量 `fedora` + `44` + 前缀 `fedora-toolbox`；
- `ContainerNameDefault` 最终为 `<前缀>-<release>`，如主机是 Fedora 44 即 `fedora-toolbox-44`。

这解释了官方 man page 的表述："主机不被支持时回退到 Fedora 镜像"。

## 三级优先级与 ResolveContainerAndImageNames

create/enter/run 都经过同一个解析器，输入 5 个参数（container、distroCLI、imageCLI、releaseCLI 及来源标记），优先级为：

```
命令行选项  >  配置文件 general.*  >  主机探测默认值
```

关键规则（`ResolveContainerAndImageNames`）：

1. 非默认发行版且该发行版 `ReleaseRequired`（Fedora/RHEL/Ubuntu）时，release 必须由 CLI 或配置给出，否则报 `option '--release' is needed`；
2. 默认镜像名 = `<ImageBasename>:<release>`；
3. 指定 `--image` 时，release 取镜像 tag，无 tag 回落默认 release；
4. 未指定容器名时，容器名 = 镜像 basename 对应的前缀 + `-` + tag（冒号换连字符），再用正则 `[a-zA-Z0-9][a-zA-Z0-9_.-]*` 校验；
5. `--distro` 与 `--image`、`--image` 与 `--release` 两两互斥（在 create 命令层判定）。

配置文件还允许 `general.image` 整体覆盖镜像（仅当 CLI 未指定 distro/release 时生效），此时 release 从镜像 tag 反推。

## 镜像引用的语法工具

解析器配套四个字符串工具，决定"本地查找还是远程拉取"：

- `ImageReferenceHasDomain`：第一段含 `.` 或 `:`，或恰为 `localhost`，才算带 registry；
- `ImageReferenceCanBeID`：`^[a-f0-9]{6,64}$` 视为可能的镜像 ID；
- `ImageReferenceGetBasename`/`GetTag`/`GetDomain`：切分 registry/repo/tag。

拉取侧（create.go `pullImage`）的查找顺序为：镜像 ID 本地存在 → 原名本地存在 → `localhost/<name>` 本地存在 → 全限定名本地存在 → 交互式确认后从 registry 拉取。无域名的 `<basename>:<release>` 经 `GetFullyQualifiedImageFromDistros` 按发行版映射 registry。

## toolbox.conf：持久化默认值

配置为 TOML，仅支持 `[general]` 段三个键（与 CLI 同名）：

```toml
[general]
distro = "fedora"
release = "44"
# image = "registry.fedoraproject.org/fedora-toolbox:44"
```

查找顺序（后者覆盖前者）：

1. `/etc/containers/toolbox.conf`（发行版/管理员全局）；
2. `$XDG_CONFIG_HOME/containers/toolbox.conf`（用户级，实际通常为 `~/.config/containers/toolbox.conf`）。

viper 依次 `MergeInConfig`；解析完成后会重算一次默认容器名。注意代码中读取路径是 `containers/toolbox.conf`，而 `data/config/toolbox.conf` 是随仓库分发的注释样例。

## 子 UID/GID 校验：rootless 的启动闸门

名称解析之外，preRun 还在主机上做一项 rootless 前置检查：`ValidateSubIDRanges` 通过 cgo `dlopen` libsubid，依次调用 `subid_get_gid_ranges` 与 `subid_get_uid_ranges`（先按用户名、失败再按 UID）。root 用户、容器内部、completion 命令三种场景跳过；普通用户若无 subuid/subgid 范围直接报错并提示查 `subgid(5)`/`subuid(5)`/`usermod(8)` 手册。这是 [/examples/01-first-toolbox.md](../examples/01-first-toolbox.md) 常见问题中 subuid 配置的代码依据。

## 环境变量白名单：43 个变量的确定性透传

exec 时不把主机环境全量带进容器，而是维护一张 43 个变量的白名单（`preservedEnvironmentVariables`，脚本实测计数），且**只转发主机上实际已设置的变量**，逐一生成 `--env=NAME=VALUE`。覆盖：终端显示（TERM/DISPLAY/WAYLAND_DISPLAY/XAUTHORITY/VTE_VERSION）、D-Bus 与 SSH、XDG 全家（15 个 XDG_*）、KDE/Konsole（6 个）、HIST*（6 个）、语言与用户身份（LANG/HOME/USER/SHELL/TOOLBOX_PATH）等。

## 相关概念

- [/concepts/04-podman-argv-layer.md](04-podman-argv-layer.md)
- [/concepts/06-create-argv.md](06-create-argv.md)
- [/examples/03-multi-distro.md](../examples/03-multi-distro.md)
