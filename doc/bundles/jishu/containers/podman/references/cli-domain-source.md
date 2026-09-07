---
type: Reference
title: "CLI 层与 Domain 层架构源码"
description: "cmd/podman Cobra 命令树、pkg/domain/entities 双接口（ContainerEngine/ImageEngine）、abi本地/tunnel远程双实现、pkg/specgen 规格生成器源码信源。"
tags: [podman, cli, cobra, pkg-domain, container-engine, image-engine, abi, tunnel, specgen, bindings]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T10:15:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T10:15:00+08:00 }
status: stable
stale_after: 2027-09-07
---

# CLI 层与 Domain 层架构源码

本信源登记簿逐文件核对 CLI 入口层、Domain 业务逻辑层与 SpecGenerator 规格生成器的关键 Go 源码事实，是 [/concepts/00-introduction.md](../concepts/00-introduction.md)、[/concepts/01-commands.md](../concepts/01-commands.md)、[/concepts/03-docker-compat.md](../concepts/03-docker-compat.md) 三篇概念文档与两个示例的源码依据。

## 一、cmd/podman/ —— Cobra 命令树

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-C1 | **根命令** 定义位置：`cmd/podman/root.go`，变量名 `rootCmd`，包 `package main`；包含 `PersistentFlags()` 中注册的全局 flags（`--url / --connection / --log-level / --root / --runroot / --storage-driver` 等） | cmd/podman/root.go L1-末尾 |
| F-C2 | **子命令注册方式**：在 root.go 的 `init()` 函数中逐个 `rootCmd.AddCommand(containercli.New())`，子命令按资源域拆分独立包（containercli / imagecli / podcli / networkcli / volumecli / secretcli / systemcli / manifestcli / kubecli / quadletcli / machinecli） | cmd/podman/root.go init() 函数体 |
| F-C3 | 每个子 CLI 包（如 `cmd/podman/container/`）提供 `New() *cobra.Command`，函数内定义 `Use / Short / Long / Example / RunE`，以及该命令的 flags 到 `*entities.XXXOptions` 结构体字段的 Cobra 绑定 | cmd/podman/container/run.go、cmd/podman/image/build.go 等示例 |
| F-C4 | RunE 典型模式三行：`flags := cmd.Flags() ; options := entities.RunOptions{...} ; registry.ContainerEngine().Run(registry.GetContext(), options)`——**绝不做业务逻辑**，纯胶水 | cmd/podman/container/run.go 的 RunE 闭包 |
| F-C5 | registry 包（`pkg/domain/infra/abi/registry.go` 或 tunnel 对应）提供 `ContainerEngine()` / `ImageEngine()` 两个函数，返回当前执行模式下（本地 abi 或远程 tunnel）的接口单例 | pkg/domain/infra/{abi,tunnel}/registry.go |
| F-C6 | podman vs podman-remote 两个二进制的区分：`cmd/podman/main.go` 与 `cmd/podman-remote/main.go`（或 build tag 控制）在程序启动时选不同的 registry 初始化——后者一开始就建立 HTTP 连接上下文 | cmd/podman/main.go vs cmd/podman-remote/main.go |

## 二、pkg/domain/entities/ —— 业务接口与数据结构

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-E1 | **两大接口**：`type ContainerEngine interface { ... }` 与 `type ImageEngine interface { ... }`；CLI 每条命令对应该接口中的一个方法（如 `Run / Create / Start / Stop / Exec / Logs / Build / Pull / Push`） | pkg/domain/entities/engine_container.go、engine_image.go |
| F-E2 | 每个方法入参是命名结构体（如 `RunOptions`、`BuildOptions`、`PullOptions`），字段 1:1 对应 CLI flags 与 REST API JSON；**字段命名 PascalCase** 方便 Cobra/JSON 双绑定 | pkg/domain/entities/types_container.go、types_image.go |
| F-E3 | 返回值统一使用 `*entities.Report` 家族（RunReport、BuildReport、PullReport…），字段严格对齐 Docker CLI 的输出，保证 `--format json` 兼容性 | pkg/domain/entities/reports_container.go 等 |
| F-E4 | Pod / Network / Volume / Secret / System / Manifest / Kube / Machine 各自在 `pkg/domain/entities/` 下有对应的接口文件，组织方式与 Container/Image 完全对称 | 目录 `pkg/domain/entities/*.go` |

## 三、pkg/domain/infra/abi/ —— 本地实现

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-A1 | **ContainerEngine 的本地实现** 结构体：`type ContainerEngine struct { *libpod.Runtime }`；直接嵌入 libpod.Runtime，因此所有方法都可以调 `ic.Libpod.Xxx` | pkg/domain/infra/abi/container.go 文件首 |
| F-A2 | `func (ic *ContainerEngine) Run(ctx, opts) (*RunReport, error)` 典型实现：opts 参数校验 → 通过 specgen 生成 Spec → `ic.Libpod.NewContainer(ctx, spec)` → `ctr.Start(ctx)` → 组装 RunReport 返回 | pkg/domain/infra/abi/container.go 中 Run 方法 |
| F-A3 | ImageEngine 对应方法：如 Pull 会调用 `containers/image` 库的传输 API；Build 会委托 `containers/buildah` 库；Save/Load 走 `containers/image` 5 种传输前缀 | pkg/domain/infra/abi/images.go |
| F-A4 | **无网络 I/O**：abi 路径上所有调用都是进程内函数调用；存储是 SQLite/BoltDB 本地文件 → 这是 daemonless 的保证 | 代码检查：abi 包 import 中不出现 net/http client 侧 |

## 四、pkg/domain/infra/tunnel/ —— 远程实现

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-T1 | 结构体：`type ContainerEngine struct { ClientCtx context.Context }`，它只持有一个已建立的 HTTP 上下文（包含 server URL、TLS 配置、身份认证） | pkg/domain/infra/tunnel/container.go 文件首 |
| F-T2 | `Run(ctx, opts)` 在 tunnel 里的实现：把 opts 结构体序列化为 HTTP 查询参数 + multipart body → 调 `pkg/bindings.ContainerRun(ic.ClientCtx, opts)` → 得到的 bytes Report 再反序列化为 `*entities.RunReport` | pkg/domain/infra/tunnel/container.go 中 Run 方法 |
| F-T3 | 每个 CLI 命令 → abi 函数 ↔ tunnel 函数 ↔ pkg/bindings 函数 ↔ pkg/api 服务端路由 形成**四路一形**的严格同构；因此本地用户看到的行为和 remote 调用者完全一致（兼容承诺的核心） | 目录对齐：{abi,tunnel}/container.go 中方法名一一对应 |
| F-T4 | 支持三种 HTTP 传输层：UDS（unix://）、SSH（http+ssh://，由 ssh.Config + net.Conn 桥接）、TCP/HTTP（需 --tls-verify）——与 system-connection 三种 URL 对齐 | pkg/bindings/connection.go |

## 五、pkg/bindings/ —— 稳定 Go 客户端库

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-B1 | **稳定性承诺**：该包 API 向后兼容（abi/tunnel 实现层可自由改）；外部 Go 项目（如 podman-py 的底层其实可类比它、以及各种 K8s operator/CI 工具）直接依赖 bindings 而非 libpod | pkg/bindings/README.go doc 注释 |
| F-B2 | 包结构与命令域对应：`bindings/containers/*`、`bindings/images/*`、`bindings/pods/*` …；每个 `.go` 文件内导出的函数 = 一个命令的远程调用（入参 options 结构体与 entities 对齐） | pkg/bindings/containers/run.go 等 |
| F-B3 | 返回错误使用 Podman 定义的错误码映射（404 → NotFound、409 → Conflict…），与 Docker SDK 错误语义对齐，确保上层应用不会因改引擎而出现错误分支差异 | pkg/bindings/errors.go |

## 六、pkg/specgen/ —— 规格生成器

| 事实编号 | 内容 | 原始文件 / 路径 |
|---------|------|----------------|
| F-S1 | `type SpecGenerator struct` 包含几百个字段：从名称、镜像、命令、env、端口、卷、capability、SELinux、cgroup 资源、健康检查，到 Pod 级共享 namespace、infra 配置，所有能影响 OCI config.json 的值都集中在这里 | pkg/specgen/generate/specgen.go |
| F-S2 | **CLI flags 归并**：在 pkg/domain/infra/abi 中接收到 entities.Options 后，第一步就是 `spec := specgen.NewSpecGenerator(opts.Name, opts.Terminal)` 再把几十个字段赋过去；避免了每条命令各写一遍 OCI 组装逻辑 | pkg/domain/infra/abi/container.go 的 Create/Run 开头 |
| F-S3 | **PodSpecGenerator** 同构；Quadlet .container 单元、K8s YAML → Podman 内部对象的转换最终也落到 SpecGenerator 再到 OCI runtime-spec，这是 Quadlet 与 Kube Play 能复用 90% 容器逻辑的关键 | pkg/specgen/generate/podspec.go、pkg/kube/* 转换包 |

## 七、CLI→Domain 执行路径图示

```text
用户: podman run -d --name web -p 80:80 -e FOO=bar --memory=1g nginx
        │
        ▼
 cmd/podman/root.go → PersistentFlags 解析 --connection
        │
        ▼
 cmd/podman/container/run.go → RunE 把 flags → entities.RunOptions
        │
        ├── 本地模式 ──► pkg/domain/infra/abi.ContainerEngine.Run
        │                    │
        │                    └──► specgen.NewSpecGenerator → 字段赋值 → ctr.Start → RunReport
        │
        └── 远程模式 ──► pkg/domain/infra/tunnel.ContainerEngine.Run
                             │
                             └──► pkg/bindings.ContainerRun → HTTP → 远端 pkg/api → 远端 abi
                                                                        └── JSON → 反序列化为 RunReport
```

## 相关文档
- [/concepts/00-introduction.md](../concepts/00-introduction.md) — 四层架构图
- [/concepts/03-docker-compat.md](../concepts/03-docker-compat.md) — Docker 兼容性具体落地位置
- [/references/readme-source.md](readme-source.md) — 顶层目录总览 + docs 工程
- [/references/libpod-source.md](libpod-source.md) — libpod 核心 + containers/* 依赖库
