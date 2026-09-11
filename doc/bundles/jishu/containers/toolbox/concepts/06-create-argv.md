---
type: Concept
title: "podman create argv 全景解剖：透传机制的实现"
description: "create.go 构造的 14 个 namespace/安全参数、6 条固定挂载与条件 socket 挂载、userns 策略、toolbox.sh 注入，以及拉取确认交互。"
tags: [toolbx, toolbox, podman-create, mount, namespace, privileged, dbus, socket, bind-mount]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T12:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T12:00:00+08:00 }
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

# podman create argv 全景解剖：透传机制的实现

[/concepts/01-pass-through.md](01-pass-through.md) 从用户视角列出了十类透传资源。本篇从实现视角回答"这些资源究竟通过哪条 podman 参数进入容器"。`src/cmd/create.go` 的 `createContainer` 把容器定义组装为一条完整的 `podman create` argv——理解它，就掌握了 Toolbx 与普通 `podman create` 的全部差异。

## argv 三段结构

```
podman --log-level <level> create [全局段] <镜像全名> [entry point 段]
```

- 全局段：namespace、安全、环境变量、volume；
- 镜像全名：经 [/concepts/05-name-resolution.md](05-name-resolution.md) 解析与 RepoTags 反查（跳过 latest 标签）得到的全限定名；
- entry point 段：`toolbox --log-level debug init-container --gid ... --home ... --shell ... --uid ... --user ... [--home-link] [--media-link] [--mnt-link]`。

## namespace 与安全参数（14 项）

| 参数 | 含义 | 透传意图 |
|------|------|---------|
| `--cgroupns host` | 共享主机 cgroup 命名空间 | 资源限制、systemd 可见性 |
| `--dns none` | 不生成容器 DNS 配置 | 直接用主机 /etc/resolv.conf（入口再做链接） |
| `--hostname toolbx` | 固定主机名 | 配合 myhostname NSS 模块 |
| `--ipc host` | 共享 IPC 命名空间 | 共享内存、信号量 |
| `--label com.github.containers.toolbox=true` | 身份标签 | list/ps 过滤依据 |
| `--name <container>` | 容器名 | 解析器产出 |
| `--network host` | 共享网络栈 | 免端口映射、Avahi、主机 CA |
| `--no-hosts` | 不管理 /etc/hosts | 交由入口链接到主机版本 |
| `--pid host` | 共享 PID 命名空间 | 可看到/调试主机进程 |
| `--privileged` | 特权容器 | 设备访问、mount 能力 |
| `--security-opt label=disable` | 关闭 SELinux 标签隔离 | 主机文件双向访问 |
| `--ulimit host` | 继承主机 ulimits | 编译等工作负载不受限 |
| `--userns host\|keep-id` | root=host，普通用户=keep-id | rootless UID 映射 |
| `--user root:root` | 容器内初始以 root 启动 | 入口需要 root 做 useradd/mount |

另有条件项：podman ≥ 2.1.0 追加 `--mount type=devpts,destination=/dev/pts`（独立 PTY 空间）。

## 固定挂载（6 条）

| Volume | 说明 |
|--------|------|
| `/:/run/host:rslave` | 主机根文件系统逃生口（rslave 传播挂载事件） |
| `/dev:/dev:rslave` | 完整设备树（USB/GPU/磁盘） |
| `<dbus-system-socket>:<同路径>` | D-Bus 系统总线 socket |
| `<home 真实路径>:<同路径>:rslave` | 用户主目录（先 EvalSymlinks 规范化，保证容器内外路径一致） |
| `<TOOLBOX_PATH>:/usr/bin/toolbox:ro` | 主机 toolbox 二进制只读注入（容器内不需安装） |
| `<runtimeDirectory>:<同路径>` | XDG_RUNTIME_DIR（普通用户）或 /run（root 用户） |

## 条件挂载：运行时发现而非硬编码

三类服务 socket **不是写死路径**，而是连接主机 D-Bus systemd，查询对应 socket 单元的 `Listen` 属性，取 `SOCK_STREAM` 且为绝对路径者再 EvalSymlinks：

- Avahi：`avahi-daemon.socket`；
- KCM（Kerberos 凭据缓存）：`sssd-kcm.socket`；
- PC/SC（智能卡）：`pcscd.socket`。

主机未运行该服务时静默跳过（debug 日志记录），所以同一 argv 模板能自适应最小化系统与桌面系统。

可移动介质路径还要区分符号链接布局（Silverblue 等系统的路径是链接）：

| 主机路径情况 | 处理 |
|-------------|------|
| `/media` 是指向 `/run/media` 的符号链接 | 不传挂载，给入口加 `--media-link`（容器内造同名链接） |
| `/media` 是普通目录 | bind `/media:/media:rslave` |
| `/mnt` → `/var/mnt` | `--mnt-link`，否则 bind `/mnt:/mnt:rslave` |
| `/run/media` 存在 | 直接 bind `/run/media:/run/media:rslave` |
| `/home` 是指向 `/var/home` 的符号链接 | 加 `--home-link` |

此外若主机存在 `/etc/profile.d/toolbox.sh` 或 `/usr/share/profile.d/toolbox.sh`（后者为 Meson 默认安装位置），将其只读挂到容器 `/etc/profile.d/toolbox.sh`，保证容器内 ⬢ 提示符逻辑随主机版本更新（见 [/concepts/08-cross-distro-binary.md](08-cross-distro-binary.md)）。

## 环境变量透传（create 阶段）

- `TOOLBOX_PATH=<主机二进制绝对路径>`：固定注入，容器内递归调用/转发主机都靠它；
- `XDG_RUNTIME_DIR=<...>`：普通用户注入（root 用户在容器侧自行计算 /run）；
- `TOOLBX_DELAY_ENTRY_POINT` / `TOOLBX_FAIL_ENTRY_POINT`：若主机设置则透传，**仅供测试**（让入口延时/失败，模拟引导竞争条件）。

## 拉取确认：镜像大小的竞速交互

镜像本地不存在时，`pullImage` 的交互值得一提：

1. `-y` 或 registry 为 localhost：不询问直接拉；
2. stdin/stdout 非终端：直接报错要求加 `--assumeyes`（脚本环境安全默认）；
3. 交互式：`showPromptForDownload` 分两阶段——并发启动 `skopeo inspect` 求镜像层大小总和（`docker/go-units` 人类可读化）与 y/N 输入竞速；大小先返回就带大小提示，用户先作答就用占位提示；
4. 输入处理用 termios 切 raw 模式（VMIN=1、关 ECHO/ICANON），配合 eventfd+poll 实现可被 context 取消的读行，期间丢弃竞态输入；
5. 创建/拉取过程用 briandowns/spinner 显示进度（debug 级别关闭，避免污染日志）。

## 一张图对照用户视角

```
用户感知（01-pass-through）          create.go 实现位置
─────────────────────────────       ──────────────────────────
主目录/cwd                          home volume :rslave + exec --workdir
网络/Avahi/CA                       --network host + avahi socket
D-Bus 系统总线                      dbus system socket volume
/dev/udev/USB/GPU                   --privileged + /dev:/dev:rslave
ulimits                             --ulimit host
主机文件系统逃生口                  /:/run/host:rslave
Kerberos KCM/智能卡                 sssd-kcm.socket / pcscd.socket 条件挂载
⬢ 提示符/欢迎语                     toolbox.sh 只读挂载
容器内可用 toolbox 命令             TOOLBOX_PATH:/usr/bin/toolbox:ro
```

容器侧的二次挂载（15 条 rbind）发生在入口命令中，见 [/concepts/07-init-container.md](07-init-container.md)。

## 相关概念

- [/concepts/01-pass-through.md](01-pass-through.md)
- [/concepts/05-name-resolution.md](05-name-resolution.md)
- [/concepts/07-init-container.md](07-init-container.md)
