---
type: Concept
title: "init-container 运行时引导与初始化戳记协议"
description: "隐藏入口命令如何在容器启动时反转 OCI 不可变性：用户同步、15 条 rbind、关键配置链接、Kerberos/PKCS#11/RPM 配置、CDI 应用与主机端戳记等待。"
tags: [toolbx, toolbox, init-container, entrypoint, rbind, useradd, krb5, pkcs11, rpm, fsnotify, stamp]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T12:20:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T12:20:00+08:00 }
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

# init-container 运行时引导与初始化戳记协议

`toolbox init-container` 是每个 Toolbx 容器的入口命令（`Hidden: true`，不面向人类直接调用）。官方 man page 用一整节解释它存在的理由：**OCI 容器定义在 create 时固化、不可变**，若全部配置都写在 `podman create` 参数里，新版 Toolbx 的改进就无法作用于旧容器。把配置移到"每次启动都在容器内运行的入口程序"，容器就从不可变定义变成每次启动重新成形的运行时环境。

本篇按代码执行顺序拆解引导过程（`src/cmd/initContainer.go`），以及主机侧如何等待引导完成。

## 输入参数

入口由 [/concepts/06-create-argv.md](06-create-argv.md) 的 argv 段传入：`--gid`（缺省取 uid）、`--home`（必填）、`--shell`（必填）、`--uid`（必填）、`--user`（必填）、`--home-link`/`--media-link`/`--mnt-link`（按主机符号链接布局决定），另有已废弃的 `--monitor-host`（保留解析但不做事）。

## 引导八步（严格按序）

1. **身份标记**：创建 `/run/.toolboxenv`（旧名，legacy 兼容）与 `/run/.toolbxenv`（新名）。外部程序据此识别 Toolbx 容器；`/run/.containerenv` 由 Podman 提供。
2. **测试钩子**：`TOOLBX_DELAY_ENTRY_POINT` 触发 sleep 延时，`TOOLBX_FAIL_ENTRY_POINT` 触发直接失败，仅系统测试用。
3. **关键配置文件链接主机**：当 `/run/host/etc` 存在，把容器内 `/etc/host.conf`、`/etc/hosts`、`/etc/localtime`、`/etc/resolv.conf` 重定向（符号链接）到 `/run/host/etc/` 对应文件；并从 localtime 解析时区写 `/etc/timezone`（localtime 缺失写 UTC）。
4. **路径符号链接**：按需把 `/media→/run/media`、`/mnt→/var/mnt`、（--home-link 时）`/home→/var/home` 对齐主机布局。
5. **15 条 rbind**（见下表）；若存在 `/sys/fs/selinux`，把它 bind 到 `/usr/share/empty` 清空容器内 SELinux 文件系统视图。
6. **用户同步**：主机用户名/UID/GID/主目录/Shell 不存在则 `useradd`（附加 sudo 或 wheel 组、`--no-create-home`、空密码），存在则 `usermod --append` 校正；随后 `passwd --delete root`（容器内 root 免密 sudo 体系的基础）。
7. **CDI 应用**：读 `$XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json`，应用 NVIDIA 挂载与钩子（见 [/concepts/09-nvidia-cdi.md](09-nvidia-cdi.md)）；文件不存在静默跳过。
8. **系统服务集成**：写 Kerberos KCM、PKCS#11、RPM 三类配置（见下节）。

### 15 条 rbind 清单

| 容器路径 | 主机来源（/run/host 下） | flags |
|---|---|---|
| `/etc/machine-id` | `etc/machine-id` | |
| `/run/libvirt` | `run/libvirt` | |
| `/run/systemd/journal` | `run/systemd/journal` | |
| `/run/systemd/resolve` | `run/systemd/resolve` | |
| `/run/systemd/sessions` | `run/systemd/sessions` | |
| `/run/systemd/system` | `run/systemd/system` | |
| `/run/systemd/users` | `run/systemd/users` | |
| `/run/udev/data` | `run/udev/data` | |
| `/run/udev/tags` | `run/udev/tags` | |
| `/tmp` | `tmp` | rslave |
| `/var/lib/flatpak` | `var/lib/flatpak` | |
| `/var/lib/libvirt` | `var/lib/libvirt` | |
| `/var/lib/systemd/coredump` | `var/lib/systemd/coredump` | |
| `/var/log/journal` | `var/log/journal` | |
| `/var/mnt` | `var/mnt` | rslave |

`mountBind` 的容错：源路径不存在则静默跳过；源是目录先 MkdirAll，是普通文件/socket 先造占位文件，再统一执行 `mount --rbind [-o flags]`。`redirectPath` 删除原路径时遇到 EBUSY 明确报"is a mount point"；主机侧若是指向不存在目标的绝对死链，会自动补 `/run/host` 前缀尝试自愈。

## 三类系统配置写入

- **Kerberos**：在 `/etc/krb5.conf.d/kcm_default_ccache` 写 `[libdefaults] default_ccache_name = KCM:`（文件已存在则跳过），配合 create 时挂载的 sssd-kcm.socket，使 `kinit` 凭据落在主机 KCM。
- **PKCS#11（主机 CA 证书透传）**：当镜像内有 `/etc/pkcs11/modules`、`p11-kit-client.so`（按发行版的 3 种路径探测）且主机 p11-kit server socket 存在时，写 `p11-kit-trust.module` 指向主机 server，并向三处投递环境保持配置：`/etc/ssh/sshd_config.d/90-toolbx.conf`（SetEnv）、`/etc/profile.d/toolbx-pkcs11.sh`（供 su）、`/etc/sudoers.d/90-toolbx-pkcs11`（Defaults env_keep，权限 0440）。
- **RPM**：写 `/usr/lib/rpm/macros.d/macros.toolbox`，定义 `%_netsharedpath /dev:/media:/mnt:/proc:/sys:/tmp:/var/lib/flatpak:/var/lib/libvirt`，告诉 RPM 这些 bind 挂载路径是"网络共享路径"，不归属任何软件包——避免容器内装包时误改主机挂载点。

## 引导完成后的常驻循环

入口程序不退出（它是容器 PID 1），完成写入后进入永久 `select`：

- **fsnotify watch `/run/host/etc`**：主机 `/etc/localtime` 变化时重新同步 `/etc/timezone`；
- **24 小时 ticker**：触发 `updatedb`（刷新 locate 数据库）；启动时也先跑一次；
- inotify 资源不足（EMFILE/ENFILE/ENOMEM/ENOSPC）时降级为不监视而非引导失败。

## 初始化戳记协议：主机端如何等待

enter/run 不能在引导完成前 exec，二者通过运行目录中的戳记文件握手：

```
$XDG_RUNTIME_DIR/toolbox/container-initialized-<entryPointPID>
```

1. 容器以 root 启动入口，入口最后创建戳记并 chown 给容器用户；
2. 主机端 `podman start` 后 inspect 取入口 PID，拼出戳记路径；
3. `ensureContainerIsInitialized`：优先 fsnotify watch 整个 toolbox 运行目录（戳记出现即唤醒），inotify 不可用或设置了 `TOOLBX_RUN_USE_POLLING` 时降级 1 秒轮询；
4. **25 秒硬超时**；期间用 `podman logs --follow --since` 流式跟随入口日志，按 logfmt 解析 `level`/`msg` 转发到本地 logger，`Error: ` 前缀行收集为致命错误；
5. 超时仍无戳记则报 "failed to initialize container"。

排障含义：`toolbox enter` 卡住最多 25 秒后失败时，错误细节来自入口日志转发；直接 `podman logs <container>` 可见 init-container 的全部 debug 输出。

## 旧容器兼容

inspect 发现入口命令不是 `toolbox`（更老的镜像）会直接拒绝并提示 "Recreate it with Toolbx version 0.0.97 or newer"；挂载中含 `/run/host/monitor` 的旧容器则走废弃路径，额外调用 `org.freedesktop.Flatpak.SessionHelper.RequestSession` 维持 localtime 同步并打印 deprecated 警告。

## 相关概念

- [/concepts/06-create-argv.md](06-create-argv.md)
- [/concepts/08-cross-distro-binary.md](08-cross-distro-binary.md)
- [/concepts/09-nvidia-cdi.md](09-nvidia-cdi.md)
