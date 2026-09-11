---
type: Concept
title: "NVIDIA GPU 透传：CNCF CDI 的生成-传递-应用三段式"
description: "主机侧 go-nvlib/nvcdi 探测硬件生成 CDI spec、经 $XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json 传入容器、init-container 用 CDI 库应用 mounts/hooks，无硬件全程静默降级。"
tags: [toolbx, toolbox, nvidia, gpu, cdi, nvml, nvcdi, cdi-hook, ldconfig, symlink]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T13:20:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T13:20:00+08:00 }
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

# NVIDIA GPU 透传：CNCF CDI 的生成-传递-应用三段式

Toolbx 的 GPU 支持没有使用传统 `--device` 参数，也不在 `podman create` 时固化任何 GPU 配置（那样会受限于 OCI 不可变性，且旧容器无法获得新驱动适配）。它采用 [CNCF Container Device Interface](https://github.com/cncf-tags/container-device-interface) 模型，把流程拆成主机生成、运行目录传递、容器内应用三段。

## 第一段：主机侧生成 spec（pkg/nvidia）

每次 `toolbox enter`/`toolbox run` 在主机侧执行 `nvidia.GenerateCDISpec()`，探测链：

1. `info.HasDXCore()`：Windows DXCore 平台 → 直接 `ErrPlatformUnsupported`；
2. `info.HasNvml()` + `nvml.Init()`：
   - `ERROR_DRIVER_NOT_LOADED`：驱动未加载 → 静默跳过（普通无驱动机器）；
   - `ERROR_LIB_RM_VERSION_MISMATCH`：内核态与用户态驱动版本不一致 → **显式报错**，提示检查主机系统与 systemd journal；
   - 其他初始化错误 → 致命错误；
3. `info.IsTegraSystem()`：Tegra/Jetson 平台识别；
4. 既无 NVML 又非 Tegra → `ErrPlatformUnsupported`，GPU 特性整体跳过（用户零感知）；
5. 平台成立则 `nvcdi.New`（显式禁用 `HookEnableCudaCompat`）→ `GetCommonEdits()` → `nvspec.New` 产出标准 CDI spec（含 Env、Mounts、Hooks 的 ContainerEdits）。

spec 中的环境变量（如 `NVIDIA_VISIBLE_DEVICES` 类配置）在 exec 时直接追加到容器环境。

## 第二段：运行目录文件传递

容器首次启动（EntryPointPID ≤ 0）前，主机把 spec 序列化（`json.MarshalIndent`）写到：

```
$XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json
```

该目录已通过 create argv 的 runtimeDirectory 卷挂载进容器，因此**无需任何容器定义变更**就能把主机最新硬件拓扑送进入口程序。这与 [/concepts/07-init-container.md](07-init-container.md) 的运行时配置思想一致：绕开 create 时不可变性。

随后每次 enter/run 都会重新探测生成——驱动升级、GPU 热插拔后下次进入即生效。

## 第三段：容器内应用 spec（init-container）

入口程序用官方 `tags.cncf.io/container-device-interface` 库读取并校验 spec，分两类应用：

### Mounts

- 逐个 `cdi.Mount.Validate()`；空 Type 默认 `bind`，非 bind 类型跳过；
- 执行 rbind 时把 HostPath 自动加上 `/run/host` 前缀——spec 描述的是主机路径，容器内对应资源在 /run/host 下（如 `/run/host/usr/lib/...`）。

### Hooks（仅处理 createContainer 阶段钩子）

识别两种 `nvidia-cdi-hook` 子命令参数：

| 钩子 | 参数形态 | 应用动作 |
|------|---------|---------|
| `create-symlinks` | `--link <existingTarget>::<newLink>`（可多条） | 在容器内创建符号链接（newLink 必须绝对路径，父目录自动创建，已存在不报错） |
| `update-ldcache` | `--folder <dir>`（可多条，去重） | 写 `/etc/ld.so.conf.d/toolbx-nvidia.conf`（列出 GPU 库目录）后执行 `ldconfig`，刷新动态链接缓存 |

`ldconfig` 有兼容处理：容器无 `/etc/ld.so.cache` 时加 `-N`；无 `/etc/ld.so.conf.d` 时把目录作为参数直接传入。未知钩子名/参数只记 debug 日志并跳过，不中断引导。

## 失败矩阵与用户体验

| 主机情况 | 行为 |
|---------|------|
| 无 NVIDIA 硬件/无 NVML | 静默跳过，普通容器体验不受影响 |
| Tegra 系统 | 走 Tegra 分支生成 spec |
| 驱动未加载 | 静默跳过 |
| 内核/用户态驱动版本不匹配 | 明确错误终止，指向 journal |
| spec 文件缺失（旧容器/首次未生成） | 入口静默跳过挂载与钩子 |
| spec 中 mount/hook 非法 | 引导报错 "failed to load/apply CDI" |

"无硬件全程静默、有问题才出声"是该特性的设计原则——GPU 支持是可选插件而非基础路径。

## 与测试夹具的对应

系统测试 `230-cdi.bats` 用 29 个手写 JSON 夹具覆盖 spec 解析分支（`test/system/data/`，目录实测计数）：

- `cdi-empty.json`（1 个）：空 spec 冒烟（验证无硬件时不产生 ld.so.conf 改动）；
- `cdi-hooks-{00,01,02,10,11,12,14,15}.json`（8 个）：通用钩子处理；
- `cdi-hooks-create-symlinks-{00..08,30..37}.json`（17 个）：0/1/多条 `--link`、相对路径拒绝、缺参数等边界；
- `cdi-mounts-{10,11,12}.json`（3 个）：挂载类型与路径映射。

测试用夹具与主机实际生成的 cdi-nvidia.json 比对来判断"是否发现了真实 NVIDIA 硬件"（发现则 skip 对硬件无关断言）。

## 实战

完整操作步骤（驱动前提、容器创建、`nvidia-smi`/CUDA 验证、故障定位）见 [/examples/04-nvidia-gpu.md](../examples/04-nvidia-gpu.md)。

## 相关概念

- [/concepts/07-init-container.md](07-init-container.md)
- [/examples/04-nvidia-gpu.md](../examples/04-nvidia-gpu.md)
- [/concepts/10-build-and-tests.md](10-build-and-tests.md)
