---
type: Example
title: "多发行版容器实战：Ubuntu、RHEL 与 Arch"
description: "基于名称解析机制创建非主机发行版容器：--distro/--release 组合、镜像 registry 差异、容器命名规则、toolbox.conf 持久化与并行多容器工作流。"
tags: [toolbx, toolbox, ubuntu, rhel, arch, multi-distro, toolbox.conf, example]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T14:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T14:00:00+08:00 }
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

# 多发行版容器实战：Ubuntu、RHEL 与 Arch

本篇演示 [/concepts/05-name-resolution.md](../concepts/05-name-resolution.md) 的实际用法：在一台主机上并行维护 Fedora（默认）、Ubuntu、RHEL、Arch 四种 Toolbx 容器。所有命令行为基于源码中 Distro 注册表与 release 校验规则，版本格式写错会在创建前被直接拒绝。

## 发行版-版本-镜像对照（源码事实）

| 命令行 distro | release 合法形式 | 实际拉取镜像 | 默认容器名 |
|---|---|---|---|
| `fedora` | `36`、`f36`、`F36` | `registry.fedoraproject.org/fedora-toolbox:<r>` | `fedora-toolbox-<r>` |
| `ubuntu` | `YY.MM`（月必须 01-12 两位） | `quay.io/toolbx/ubuntu-toolbox:<r>` | `ubuntu-toolbox-<r>` |
| `rhel` | `<major>.<minor>`（如 8.5、9.3） | `registry.access.redhat.com/ubi<major>/toolbox:<r>` | `rhel-toolbox-<r>` |
| `arch` | 可省略；`latest`/`rolling` 均可 | `quay.io/toolbx/arch-toolbox:latest` | `arch-toolbox-latest` |

## 场景一：创建并进入 Ubuntu 24.04 容器

```bash
# 非默认发行版必须同时给 --release，否则报 option '--release' is needed
toolbox create --distro ubuntu --release 24.04
# 等价：toolbox create -d ubuntu -r 24.04
# 首次会提示拉取 quay.io/toolbx/ubuntu-toolbox:24.04

toolbox enter --distro ubuntu --release 24.04
```

进入后提示符变为 `⬢`，验证发行版：

```bash
⬢[user@toolbox ~]$ cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 24.04 LTS"
NAME="Ubuntu"
⬢[user@toolbox ~]$ sudo apt-get update && sudo apt-get install -y build-essential
```

release 校验很严格，以下都会被 `parseReleaseUbuntu` 拒绝：年份前导零（`04.04` 写成两位年但小于 10）、月份单位数（`24.4`）、月份越界（`24.13`）。

## 场景二：RHEL UBI 容器（9.3）

```bash
toolbox create -d rhel -r 9.3
# 镜像解析为 registry.access.redhat.com/ubi9/toolbox:9.3
toolbox enter -d rhel -r 9.3
⬢[user@toolbox ~]$ sudo dnf install -y python3.12-devel gcc
```

注意 RHEL 的镜像 basename 是 `toolbox`（不是 rhel-toolbox），major 版本 9 从 release 切出；release 不带点（如 `9`）会被拒绝。

## 场景三：Arch 滚动容器

```bash
toolbox create -d arch           # ReleaseRequired=false，可省略 release
toolbox enter  -d arch
⬢[user@toolbox ~]$ sudo pacman -S --needed base-devel git
```

`-d arch -r rolling` 也合法，但内部归一化为 `latest`，容器名相同（`arch-toolbox-latest`），重复创建会提示容器已存在。

## 场景四：多容器并行与显式命名

并行维护多个容器时建议显式命名，避免不同版本容器混淆：

```bash
toolbox create -d ubuntu -r 22.04 -c ubuntu-lts
toolbox create -d ubuntu -r 24.04 -c ubuntu-new
toolbox create -d fedora -r 40   -c fedora-dev

toolbox list -c                  # 列出全部 Toolbx 容器（按名称排序）
toolbox enter -c ubuntu-lts
toolbox run -c fedora-dev go version
```

命名须匹配 `[a-zA-Z0-9][a-zA-Z0-9_.-]*`，即首字符为字母数字，其后可含下划线/点/连字符。

容器不存在时的 enter/run 行为（源码三分支，见 [/concepts/04-podman-argv-layer.md](../concepts/04-podman-argv-layer.md)）：本机零容器时询问是否自动创建；恰有一个其他容器时打印 "Entering container X instead" 并改入它；有多个容器时报错要求 `-c` 显式选择。

## 场景五：用 toolbox.conf 持久化默认发行版

不想每次敲 `-d/-r`，写 `~/.config/containers/toolbox.conf`：

```toml
[general]
distro = "ubuntu"
release = "24.04"
```

此后裸 `toolbox create` / `toolbox enter` 默认即 Ubuntu 24.04；CLI 选项仍可临时覆盖。优先级：CLI > 用户配置 > `/etc/containers/toolbox.conf`（管理员全局）> 主机探测默认值。注意配置文件路径是 `containers/toolbox.conf`，不是 `toolbox/toolbox.conf`。

`general.image` 还能整体指定自定义镜像（此时与 distro/release 互斥）：

```toml
[general]
image = "registry.fedoraproject.org/fedora-toolbox:40"
```

## 跨发行版一致性验证清单

在非 Fedora 容器内可依次验证透传机制（与发行版无关）：

- [ ] `pwd` 进入容器时与主机当前目录一致；
- [ ] `ls ~/.ssh` 可见主机密钥；
- [ ] `ls /run/host/usr/bin | head` 可见主机根文件系统；
- [ ] `test -f /run/.containerenv && test -f /run/.toolbxenv` 均成功；
- [ ] `readlink /etc/resolv.conf` 指向 `/run/host/etc/resolv.conf`；
- [ ] `getent hosts $(hostname)` 正常（Ubuntu 靠 myhostname NSS）；
- [ ] `sudo id` 可用（用户被加入 sudo 组，root 空密码）。

## 常见问题

| 现象 | 原因与处理 |
|------|-----------|
| `option '--release' is needed` | 非主机/非默认发行版必须带 `-r`（Arch 例外） |
| `invalid argument for '--release'` | 对照上表格式；Ubuntu 月份两位、RHEL 必须带点 |
| `options --distro and --image cannot be used together` | distro 与 image 互斥；自定义镜像直接用 `-i` |
| 私有 registry 镜像拉取失败 | `toolbox create --authfile ~/auth.json -i <image>`，认证文件用 `podman login` 生成 |
| 容器内没有新版 toolbox 行为 | toolbox 二进制由主机挂载注入（/usr/bin/toolbox:ro），升级主机工具版本即可，老容器无需重建 |

## 相关示例与概念

- [/examples/01-first-toolbox.md](01-first-toolbox.md)
- [/examples/02-custom-image.md](02-custom-image.md)
- [/concepts/05-name-resolution.md](../concepts/05-name-resolution.md)
- [/concepts/08-cross-distro-binary.md](../concepts/08-cross-distro-binary.md)
