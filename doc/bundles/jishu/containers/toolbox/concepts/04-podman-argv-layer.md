---
type: Concept
title: "Podman/Skopeo 调用层：Toolbx 作为外部 CLI 编排器"
description: "Toolbx 不含容器运行时逻辑：pkg/shell 执行模型、pkg/podman 对子命令的 argv 封装、JSON 双形态适配、版本门控与 skopeo 镜像探测。"
tags: [toolbx, toolbox, podman, skopeo, argv, exec, json, architecture]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T11:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T11:30:00+08:00 }
status: stable
stale_after: 2027-09-11
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
    title: 实现层源码地图
  - id: cmd
    resource: /references/cmd-source.md
    title: src/cmd/ 命令行接口与核心命令
---

# Podman/Skopeo 调用层：Toolbx 作为外部 CLI 编排器

阅读 Toolbx 源码首先要建立一个架构认知：**Toolbx 二进制自身不含任何容器运行时能力**。它不链接 libpod、不连接守护进程、不操作 namespace/cgroup，它做的全部事情是把用户意图翻译成 `podman`、`skopeo`、`flatpak-spawn`、`p11-kit`、`mount` 等外部命令的参数数组（argv），执行它们，再解析其 JSON 输出。GOALS.md 把这一点列为明确的非目标："不支持多容器运行时，专用 Podman；重大特性应推入 Podman 上游"。

本篇对应 [/concepts/02-workflow.md](02-workflow.md) 中用户可见命令的**实现层**。

## pkg/shell：唯一的进程执行出口

所有外部命令都经 `pkg/shell` 的 4 个函数执行（`src/pkg/shell/shell.go`）：

| 函数 | 语义 |
|------|------|
| `Run(name, stdin, stdout, stderr, arg...)` | 执行，退出码非 0 即返回 error |
| `RunContext` | 带 context 的版本 |
| `RunWithExitCode` / `RunContextWithExitCode` | 返回 `(exitCode, error)`，保留退出码语义 |

其实现就是 `exec.CommandContext` 包装，但有两个刻意设计：

1. **退出码透传**：子进程以非零状态退出时，返回该退出码且 `err=nil`；只有命令不存在（`exec.ErrNotFound`）或启动失败才构造 error。这让调用方可以精确区分"容器不存在（podman 退出码 1）"与"podman 没装"。
2. **debug 自动接管 stderr**：stderr 传 nil 且日志级别 ≥ debug 时自动接到 `os.Stderr`，所以 `toolbox -vv` 能看到全部子进程原始输出。

## pkg/podman：命令映射全表

`pkg/podman/podman.go` 把 Toolbx 的每个容器/镜像操作一一映射到 podman 子命令，且**所有调用统一带 `--log-level <level>` 前缀**（级别由 `--log-podman` 打开）：

| Toolbx 函数 | 实际执行 | 关键语义 |
|-------------|---------|---------|
| `ContainerExists` | `podman container exists <name>` | 查重 |
| `GetContainers` | `podman ps --all --format json --sort names` | 取全部容器后按标签过滤 |
| `InspectContainer` | `podman inspect --format json --type container` | 取入口命令/PID/挂载/标签 |
| `Start` | `podman start` | 启动已停止容器 |
| `RemoveContainer` | `podman rm [--force]` | 退出码 1=不存在，2=运行中 |
| `LogsContext` | `podman logs --follow --since <unix>` | 流式跟随入口日志 |
| `SystemMigrate` | `podman system migrate [--new-runtime]` | cgroups/OCI 运行时迁移 |
| `ImageExists` | `podman image exists` | 镜像查重 |
| `InspectImage` | `podman inspect --type image` | RepoTags/标签 |
| `Pull` | `podman pull [--authfile]` | 拉取 |
| `RemoveImage` | `podman rmi [--force]` | 退出码 1=不存在，2=有依赖子镜像 |
| `GetVersion` | `podman version --format json` | 兼容有无 `Client` 对象两种结构，进程内缓存 |

此外 `pkg/skopeo/skopeo.go` 用 `skopeo inspect --format json docker://<target>` 只读解析 `LayersData[].Size`，供拉取确认时显示镜像总大小（见 [/concepts/06-create-argv.md](06-create-argv.md)）。

## JSON 双形态适配：为 Podman API 演进而写的 UnmarshalJSON

Toolbx 不依赖 Podman 的 Go 绑定，代价是必须自己处理 `ps`/`inspect` JSON 在 Podman V1→V2 之间的字段变迁。`containerPS.UnmarshalJSON` 里保留了三处兼容代码（注释引用了 [podman issue #6594](https://github.com/containers/podman/issues/6594)）：

- `Created`：V1 是 "5 minutes ago" 字符串，V2 是 Unix 秒（JSON 数字在 Go 里为 float64）；
- `Names`：V1 单字符串，V2 字符串数组；
- `State`/`Status`：状态文本从 `Status` 移到 `State`。

镜像侧的 `imageImages`/`imageInspect` 同理适配 `Created` 与两种 inspect 结构，并处理一镜像多 RepoTags 的展平（`flattenNames`）与无标签镜像的 `<none>`/短 ID 显示。

`Container` 接口暴露 12 个只读方法（`Name/Names/ID/Image/Status/Created/EntryPoint/EntryPointPID/Labels/Mounts/IsToolbx`），让上层命令不直接碰 JSON。

## Toolbx 容器如何被识别：双标签

无论 `ps` 还是 `images`，都只保留带 Toolbx 标签的对象，且新旧两个标签名都认：

```go
labels["com.github.containers.toolbox"] == "true"      // 现行
labels["com.github.debarshiray.toolbox"] == "true"    // 旧名兼容
```

这也是自定义镜像必须打 `com.github.containers.toolbox=true` 标签的原因——`toolbox list` 靠它过滤（见 [/concepts/03-custom-images.md](03-custom-images.md)）。

## 版本门控：运行时探测而非构建时依赖

因为不链接 Podman 库，Toolbx 无法在编译期知道宿主 Podman 版本，于是 `CheckVersion(required)` 在运行时 `podman version` 后用 `go-version` 做语义比较（当前 ≥ 要求即真）。代码中两处门控：

- podman ≥ 2.1.0 才给 create 加 `--mount type=devpts,destination=/dev/pts`；
- podman ≥ 1.8.1 才给 exec 加 `--detach-keys ""`。

同样的运行时适配还体现在 `startContainer`：启动失败信息含 "use system migrate to mitigate" 时，按主机 cgroups 版本选择 `runc`（v1）或 `crun`（v2）执行 `podman system migrate --new-runtime` 后重试。

## 容器内外的命令转发：flatpak-spawn

Toolbx 命令在容器内被再次调用时（例如脚本里在容器中执行 `toolbox enter`），不允许嵌套，而是经 `utils.ForwardToHost()` 拼装 `flatpak-spawn --host <TOOLBOX_PATH> <原参数>`（携带 43 个保留变量，见 [/concepts/05-name-resolution.md](05-name-resolution.md)）送回主机执行。容器内镜像里只需有 flatpak-spawn（Ubuntu 官方镜像专门做了 `/usr/bin/flatpak-spawn` 软链），主机二进制则通过 `TOOLBOX_PATH=/usr/bin/toolbox` 的只读挂载注入。

## 排障启示

理解调用层后，排障路径非常直接：

```bash
toolbox create -vv        # 打印完整 podman create argv 与子进程输出
toolbox -vv run <cmd>     # 打印 podman start/inspect/exec 全过程
```

`-v` 仅开 debug，`-vv` 额外打开 NVIDIA 库与 podman 自身日志。任何"Toolbx 行为异常"先看到对应 podman 原生命令，绝大多数问题（权限、镜像、cgroups、网络）都能在 argv 层面定位。

## 相关概念

- [/concepts/05-name-resolution.md](05-name-resolution.md)
- [/concepts/06-create-argv.md](06-create-argv.md)
- [/concepts/07-init-container.md](07-init-container.md)
- [/concepts/02-workflow.md](02-workflow.md)
