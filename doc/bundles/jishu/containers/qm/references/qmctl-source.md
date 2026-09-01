---
type: Reference
title: qmctl 管理工具信源
description: qmctl 命令行工具的 Python 实现、Shell 包装脚本和 man 手册，提供 QM 容器检查、命令执行、文件复制等功能
tags: [qmctl, cli, tool, python, management]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: qmctl-readme
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/tools/qmctl/README.md"
    title: "qmctl README.md"
  - id: qmctl-py
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/tools/qmctl/qmctl.py"
    title: "qmctl.py Python 实现"
  - id: qmctl-shell
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/tools/qmctl/qmctl"
    title: "qmctl Shell 包装脚本"
  - id: tools-scripts
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/tools/"
    title: "tools/ 目录下其他 Shell 工具"
---

# qmctl 管理工具信源

## 信源内容摘要

本信源来自 QM 项目 `tools/qmctl/` 目录下的工具实现，以及 `tools/` 根目录下的辅助脚本。

### qmctl 工具概述

qmctl 提供一个简单的接口来检查 QM 容器命名空间、监控 cgroups 和 systemd 资源，以及在 QM 容器内运行命令。

**运行要求**：
- Python 3.6+
- 已安装并配置 Podman
- 可选：argcomplete 用于 tab 补全

### qmctl 主要命令

**show 子命令** - 显示容器信息：

```bash
qmctl show                        # 显示原始容器配置
qmctl show all                    # 显示所有支持的信息（实时 cgtop 除外）
qmctl show unix-domain-sockets    # 检查 UNIX 域套接字
qmctl show shared-memory          # 查看共享内存段
qmctl show namespaces             # 查看容器命名空间
qmctl show available-devices      # 检查已配置的设备
qmctl show resources              # 实时流式显示 systemd-cgtop
```

**exec 子命令** - 在 QM 容器内运行命令：

```bash
qmctl exec uname -a
qmctl exec ls /dev --json
```

**execin 子命令** - 在 QM 内的嵌套容器中运行命令：

```bash
qmctl execin alpine uname -a
qmctl execin alpine ls /dev --json
```

**cp 子命令** - 在主机和 QM 之间复制文件：

```bash
qmctl cp README.md qm:/tmp
qmctl cp qm:/tmp/README.md ./
```

**全局选项**：

```bash
qmctl --verbose show    # 详细输出模式
```

### tools/ 根目录辅助 Shell 工具

| 工具 | 功能 |
|------|------|
| `qm-rootfs` | 输出 QM rootfs 位置（安装时配置） |
| `qm-storage-settings` | 配置初始 QM 存储设置 |
| `qm-is-ostree` | 检测是否运行在 OSTree 系统上 |
| `comment-tz-local` | 时区本地注释工具 |
| `version-update` | 版本更新工具 |

### qm-storage-settings 配置内容

- `${ROOTFS}/etc/containers/storage.conf`：
  - 取消注释 `additionalimagestores`
  - 添加 `/var/lib/shared` 到 `additionalimagestores`
  - 取消注释并设置 `transient_store = true`
- `${ROOTFS}/etc/containers/containers.conf`：
  - 添加 `[engine]` 段和 `TMPDIR` 配置

### Tab 补全启用

```bash
pip install argcomplete
activate-global-python-argcomplete --user
```
