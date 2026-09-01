---
type: Reference
title: QM 项目 README 与 man 手册信源
description: QM 项目官方 README.md 和 qm.8.md man 手册，包含项目定位、安装、SELinux、BlueChi、OOM 策略等核心信息
tags: [readme, documentation, official, manpage]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/README.md"
    title: "QM 官方 README.md"
  - id: manpage
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/qm.8.md"
    title: "QM man 手册 qm.8.md"
---

# QM 项目 README 与 man 手册信源

## 信源内容摘要

本信源来自 QM 项目根目录的 README.md 和 qm.8.md man 手册源文件。

### 项目定位

QM（Quality Management）是一个容器化环境，用于运行功能安全质量管理软件，主要面向汽车 ASIL（Automotive Safety Integrity Level）场景研究。AutoSD 不是认证安全产品，QM 在 AutoSD 环境中仅用于研究和学习目的。

QM 使用 cgroups、namespaces、安全隔离等容器技术，防止 QM 内进程干扰系统上其他进程。QM 运行自己版本的 systemd 和 Podman，不仅隔离应用和容器，也隔离 systemd 和 Podman 命令本身。

软件安装在 `/usr/lib/qm/rootfs` 目录下，自动与主机隔离，内部可进一步使用 Podman 运行嵌套容器。

### 安装流程

安装 QM 软件包后，执行 `/usr/share/qm/setup` 脚本：
- 安装 selinux-policy-targeted、podman、systemd、bluechi 包
- 启用并启动 qm.service（Podman Quadlet 服务）

### SELinux 策略

QM 包含独立的 SELinux 策略：
- QM 进程运行在 `qm_t` 域
- 容器与 `qm_t` 进程及其他容器互相隔离
- 排障命令：`ausearch -m avc -ts recent | audit2why`、`journalctl -t setroubleshoot`

### OOM 分数调整三级策略

| 层级 | oom_score_adj | 终止优先级 |
|------|---------------|-----------|
| QM 容器 | 500 | 较低优先级终止 |
| QM 内嵌套容器 | 750 | 较高优先级终止 |
| ASIL 应用 | -1 到 -1000（-1000 免疫 OOM killer） | 极低优先级终止 |
| 其他进程 | 0（默认） | 默认优先级 |

自定义嵌套容器 OOM 分数需要添加 `SYS_RESOURCE` 能力（默认 DropCapability 包含 sys_boot，不包含 SYS_RESOURCE）。

### BlueChi 集成

- BlueChi 是 systemd 服务控制器，用于高监管要求的多节点环境
- QM 内 bluechi-agent 基于主机 `/etc/bluechi/agent.conf` 配置
- 节点名前自动添加 "qm." 前缀
- 可通过 `/usr/lib/qm/rootfs/etc/bluechi/agent.conf.d/` 目录自定义配置

### 常用操作命令

```bash
# 进入 QM 环境
podman exec -ti qm sh

# 在 QM 内安装额外包
dnf --installroot=/usr/lib/qm/rootfs install <package>

# 查看 QM 服务状态
systemctl status qm.service

# 查看 SELinux 上下文
id -Z  # 应显示 system_u:system_r:qm_t:s0

# 修改 MemoryHigh 配置（drop-in 方式）
mkdir -p /etc/containers/systemd/qm.container.d/
# 创建 .conf 文件设置 MemoryHigh=2G
systemctl daemon-reload
systemctl restart qm.service
```
