---
okf_version: "0.2"
type: Concept
title: "WSL2 底座：双层配置、快照与文件系统双世界"
description: "WSL2 作为 Agent 开发环境 OS 层的机制要点——wsl.conf 与 .wslconfig 双层配置体系、systemd、networkingMode 网络模式、GPU 准虚拟化、export/import 快照，以及 /mnt/c（9P）与 Linux ext4 的文件系统双世界布局纪律"
tags: [WSL2, wsl-conf, wslconfig, systemd, mirrored-networking, GPU, 9P, DrvFs]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: ms-wsl-config
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config
    title: "WSL 中的高级设置配置（Microsoft Learn）"
---

# WSL2 底座：双层配置、快照与文件系统双世界

> 配置项与默认值均核验自 Microsoft Learn《WSL 中的高级设置配置》（2026-10-16 更新版）。WSL 安装、发行版管理与 CLI 基础见 [WSL 子系统中文教程](../../../systems/wsl/index.md)，本篇聚焦 Agent 环境视角的机制要点。

## 双层配置体系：wsl.conf 与 .wslconfig

| 维度 | `.wslconfig` | `wsl.conf` |
|------|-------------|-----------|
| 作用域 | 全部 WSL2 发行版的全局 VM 设置 | 单个发行版内部设置 |
| 位置 | `%UserProfile%\.wslconfig`（Windows 侧） | `/etc/wsl.conf`（发行版内） |
| 管什么 | VM 资源（内存/处理器/内核/网络模式/GPU） | systemd、自动挂载、interop、默认用户 |

Agent 环境的典型分工：**`.wslconfig` 定资源与网络边界**（一台机器上多个 Agent 实例互不挤占），**`wsl.conf` 定发行版行为**（systemd 开启、Windows PATH 是否注入）。

**8 秒规则**：配置修改需等子系统完全停止（关闭 shell 后约 8 秒）再重启才生效；`wsl --list --running` 可确认停止状态，`wsl --shutdown` 快速全量重启（慎用，会关闭所有发行版）。

## systemd：服务化插件的基座

现代 WSL（Microsoft Store 版）在多数发行版上默认运行 systemd：

```ini
# /etc/wsl.conf
[boot]
systemd=true
```

对 Agent 环境的意义：MCP Server、向量数据库、任务队列等**长驻服务**可以注册为 systemd 单元（用户级 `systemctl --user` 或系统级），随 WSL 启动自动拉起，而非散落在 tmux/后台进程里。`initTimeout`（默认 10000ms）控制 systemd 初始化等待。

## 网络模式：Agent 多进程通信的地基

`networkingMode` 可选值（`.wslconfig` 的 `[wsl2]` 节）：

| 模式 | 状态 | 特性 |
|------|------|------|
| `NAT`（默认） | 稳定 | WSL 独立子网；`localhostForwarding=true` 让 Windows 能访问 WSL 内 localhost 端口 |
| `mirrored` | Win11 22H2+ | 网络接口镜像宿主：localhost 双向互通、`ignoredPorts` 可让 Linux 绑定 Windows 已占端口、`hostAddressLoopback` 允许容器经宿主 IP 回连 |
| `consomme` | WSL 2.3.25+ 起作为 NAT 失败的回退 | 新式代理网络模式 |
| `bridged` | **已弃用**（WSL 2.4.5+） | 桥接模式 |
| `none` | — | 完全断网（隔离场景） |

Agent 场景要点：**mirrored 模式显著简化「Windows 宿主（IDE/Agent 客户端）↔ WSL 内 MCP Server」的 localhost 互通**，消除 NAT 模式下端口转发的时序坑。配套 `dnsTunneling`（默认 true）与 `autoProxy`（默认 true）分别改变 DNS 代理方式与继承 Windows HTTP 代理。

## GPU 准虚拟化：本地推理的可选加速

`[wsl2]` 的 `gpuSupport`（默认 true）允许 Linux 应用通过**准虚拟化**访问 Windows GPU；`wsl.conf` 的 `[gpu]` 节控制 `/usr/lib/wsl/lib` 加入 `LD_LIBRARY_PATH`（`appendLibPath`，默认 true）与 `ldconfig` 执行（`automount.ldconfig`，默认 true）。NVIDIA 场景下 Windows 端安装常规驱动，WSL 内安装 CUDA Toolkit 即可用（PyTorch 验证路径见官方 WSL CUDA 文档）。

## 快照与复制：`wsl --export / --import`

发行版可整体导出（tar 或 VHDX 格式）再导入为新的命名实例：

- **用途一（团队环境分发）**：装好全套系统依赖（CUDA、构建工具链）的发行版导出为基镜像，新成员 `wsl --import` 即得一致 OS 层。
- **用途二（实验快照）**：高风险实验前导出，失败后重导入回滚——OS 层的「git commit」。
- 配套：`defaultVhdSize`（默认 1TB 上限）、`[general]` 的 `distributionInstallPath`（默认 `%LocalAppData%\wsl`，可将新发行版落到专用盘）、`[experimental]` 的 `sparseVhd=true`（新 VHD 自动稀疏，配合 `autoMemoryReclaim=dropCache` 控制磁盘与内存回收）。

空闲自动关机：VM 层 `vmIdleTimeout`（默认 60000ms）与发行版层 `instanceIdleTimeout`（默认 15000ms，`-1` 禁用）——长驻 MCP 服务要么靠 systemd 拉活，要么显式放宽此值。

## 文件系统双世界：第一性能与安全边界

| 世界 | 路径 | 协议/实现 | 性能 | 权限模型 |
|------|------|----------|------|---------|
| Linux 原生 | `~/`、`/home` | ext4 in VHDX | 原生 | 完整 POSIX |
| Windows 挂载 | `/mnt/c` 等 | DrvFs（9P 协议跨 VM 边界） | 显著慢（社区测量：跨 OS 小文件 IO 慢一个量级，**社区口径非官方基准**） | `metadata` 选项默认关闭，Linux 权限元数据默认不落盘 |

**布局纪律（Agent 环境版）**：

1. **代码、venv、git 仓库、模型缓存一律放 Linux 文件系统**（`~/projects/...`）——`uv` 的缓存与虚拟环境是海量小文件 IO 的重灾区，放 `/mnt/c` 会把安装速度拖垮一个量级。
2. **成果物按需经 `\\wsl.localhost\<distro>\` 或 `explorer.exe .` 交换**到 Windows 侧（报告、截图），单向流动。
3. **安全侧考虑**：`/mnt/c` 默认把整块 Windows 系统盘挂进 Linux 命名空间；`[automount] enabled=false` 或收紧 `options`（`metadata,umask=077`）可收缩暴露面。`[interop]` 的 `appendWindowsPath=false` 还能阻止 Windows PATH 注入 `$PATH`，减少 Agent 工具发现时的「同名命令错绑」事故。
4. 实验性 `virtiofs=true`（需 `virtio` + `hostFileSystemAccess` 实验开关）是微软正在推进的 Windows 文件共享新通道，方向上用于改善跨文件系统体验。

## 与上层栈的衔接

- OS 层就绪后，解释器层交给 uv（见 [Python 运行时层](02-python-runtime-uv.md)）。
- VS Code Remote-WSL / Dev Containers 的「编辑器在 Windows、语言服务在 Linux」分工是 IDE 侧标准形态。
- WSL 容器（`wslc.exe`，独立于 `.wslconfig` 配置体系）与 MXC 的 WSLc 隔离后端（见 [microsoft-mxc-agent-containment](../../microsoft-mxc-agent-containment/index.md)）是 Agent 执行隔离的进阶选项。

## 关键要点回顾

- 双层配置：`.wslconfig` 管全局 VM（资源/网络/GPU），`wsl.conf` 管发行版（systemd/挂载/interop）。
- mirrored 网络模式 + systemd 是「Windows 宿主 ↔ WSL 内 MCP Server」长驻服务组合的推荐基座。
- `wsl --export/--import` 让 OS 层获得快照/分发/回滚能力——环境自由的第 1 层。
- 布局纪律：重 IO 资产全部留在 Linux ext4；`/mnt/c` 仅作交换区，且需评估安全暴露面。
