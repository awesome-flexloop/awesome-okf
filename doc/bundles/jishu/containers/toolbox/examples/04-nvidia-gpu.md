---
type: Example
title: "NVIDIA GPU 容器实战：CDI 自动透传与验证"
description: "从主机驱动前提到容器内 nvidia-smi/CUDA 验证的完整路径：CDI spec 自动生成、cdi-nvidia.json 传递、符号链接与 ldconfig 钩子、版本不匹配排障。"
tags: [toolbx, toolbox, nvidia, gpu, cdi, cuda, nvml, nvidia-smi, example]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T14:20:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T14:20:00+08:00 }
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

# NVIDIA GPU 容器实战：CDI 自动透传与验证

Toolbx 的 GPU 透传是全自动的：满足主机前提后无需任何 `--device` 参数，`toolbox enter` 会生成 CDI spec 并在容器引导时挂载。本篇给出前置条件、验证步骤与排障路径，机制原理见 [/concepts/09-nvidia-cdi.md](../concepts/09-nvidia-cdi.md)。

## 主机前提

1. **专有 NVIDIA 驱动已加载**（开源 Nouveau 不适用）：主机执行 `nvidia-smi` 正常，内核模块与用户态库版本一致。
2. **NVIDIA Container Toolkit 组件存在**：Toolbx 通过 go-nvlib/go-nvml 探测、用 nvidia-container-toolkit 的 nvcdi 库生成 spec；发行版通常随驱动容器支持包安装。
3. **较新的 Podman 与 Toolbx**：CDI 支持在 0.2 之后版本完整（NEWS 0.2 要求 nvidia-container-toolkit ≥ 1.17.8，修复 CVE-2025-23266/23267）。
4. rootless 下还需 subuid/subgid 范围正确（见 [/examples/01-first-toolbox.md](01-first-toolbox.md)）。

无 NVIDIA 硬件、驱动未加载、WSL 等平台会静默跳过——普通容器不会出现任何 GPU 相关报错。

## 第一步：创建并进入容器（无特殊参数）

```bash
toolbox create -c gpu-dev
toolbox enter -c gpu-dev
```

进入过程中主机侧自动执行：NVML 初始化 → 生成 CDI spec → 写入 `$XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json`（容器内可见同路径）→ 入口程序读取并应用 mounts 与 hooks。

用 `-vv` 可观察全过程：

```bash
toolbox -vv enter -c gpu-dev
# 日志包含 "Generating Container Device Interface for NVIDIA"
# 与 "Applying Container Device Interface for NVIDIA"
```

## 第二步：验证设备与库

```bash
# 设备节点（来自 /dev:/dev:rslave 与 CDI mounts）
⬢[user@gpu-dev ~]$ ls -l /dev/nvidia* /dev/dri 2>/dev/null

# nvidia-smi：主机工具经 /run/host 也可直接调用
⬢[user@gpu-dev ~]$ /run/host/usr/bin/nvidia-smi

# 动态链接缓存已包含 GPU 库目录（update-ldcache 钩子）
⬢[user@gpu-dev ~]$ test -f /etc/ld.so.conf.d/toolbx-nvidia.conf && cat /etc/ld.so.conf.d/toolbx-nvidia.conf
/usr/lib64/nvidia
/usr/lib64/nvidia/xorg
```

`create-symlinks` 钩子建立的设备/库符号链接可在容器内直接 `ls -l` 核对（夹具中形如 `<target>::<link>` 的映射）。

## 第三步：容器内安装 CUDA 工作负载

容器内只装用户态开发包（驱动内核模块在主机）：

```bash
⬢[user@gpu-dev ~]$ sudo dnf install -y gcc
# CUDA Toolkit（编译/运行时，版本与主机驱动兼容区间参考 NVIDIA 兼容表）
⬢[user@gpu-dev ~]$ sudo dnf install -y cuda-toolkit
⬢[user@gpu-dev ~]$ nvcc --version
```

最小验证程序：

```c
// hello.cu
#include <stdio.h>
__global__ void kernel() { printf("GPU kernel OK from Toolbx\n"); }
int main() { kernel<<<1,1>>>(); cudaDeviceSynchronize(); return 0; }
```

```bash
⬢[user@gpu-dev ~]$ nvcc hello.cu -o hello && ./hello
GPU kernel OK from Toolbx
```

机器学习工作负载（PyTorch 等）同理：主机驱动 + 容器内框架，`python -c "import torch; print(torch.cuda.is_available())"` 应返回 True。

## 观察 CDI spec（理解发生了什么）

```bash
# 主机侧（普通用户）
cat "$XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json" | python3 -m json.tool | head -40
```

spec 的 `containerEdits` 含三段：

- `env`：注入容器的 NVIDIA 环境变量（enter/run 时通过 exec --env 传递）；
- `mounts`：主机 GPU 库/设备目录，容器内目标自动加 `/run/host` 前缀 bind；
- `hooks`：createContainer 钩子，仅 `nvidia-cdi-hook create-symlinks`（建链接）与 `nvidia-cdi-hook update-ldcache`（写 ld.so.conf 并 ldconfig）被入口实现。

该文件每次 enter/run 重新生成，驱动升级后无需重建容器。

## 故障排查

| 现象 | 诊断 | 处理 |
|------|------|------|
| `the proprietary NVIDIA driver's kernel and user space don't match` | NVML 返回 LIB_RM_VERSION_MISMATCH | 主机更新后未重启/内核模块与库版本错位；查主机 `journalctl -b`、重装匹配驱动并重启 |
| `failed to initialize NVIDIA Management Library` | 其他 NVML 初始化错误 | 主机 `nvidia-smi` 是否可用；检查 nvidia-container-toolkit 安装 |
| 容器内 `nvidia-smi` 找不到但主机正常 | spec 未生成或未应用 | `toolbox -vv enter` 看日志；确认 `$XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json` 存在；该容器是否旧版工具创建（可重建） |
| 启动即 `symbol lookup error: ... nvml...` | 工具二进制被错误地以 `-z now` 链接 | 使用发行版官方 toolbox 包；自编译走 Meson/go-build-wrapper 默认 lazy 链接 |
| `nvidia-smi` 正常但 CUDA 程序失败 | 容器内 CUDA 用户态版本超出主机驱动支持 | 安装与主机驱动兼容的 cuda-toolkit 版本 |
| Tegra/Jetson 平台 | 走 IsTegraSystem 分支 | 行为与 dGPU 一致，确保 nvcdi 版本 ≥1.17.8 |

## 与系统测试对照

`230-cdi.bats` 的 `cdi: Smoke test` 先放入 `cdi-empty.json` 再 `toolbox run true`：若文件被真实硬件生成的 spec 覆盖则 skip 硬件无关断言，否则验证空 spec 下不产生任何符号链接与 `/etc/ld.so.conf.d/toolbx-nvidia.conf` 改动。想确认"无 GPU 时系统安静"，这一用例是权威参考。

## 相关概念与示例

- [/concepts/09-nvidia-cdi.md](../concepts/09-nvidia-cdi.md)
- [/concepts/07-init-container.md](../concepts/07-init-container.md)
- [/examples/05-system-tests.md](05-system-tests.md)
