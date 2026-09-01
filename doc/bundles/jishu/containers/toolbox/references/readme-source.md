---
type: Reference
title: "README.md 项目概览与定位"
description: "Toolbx 项目 README 中的项目定位、OSTree 背景、功能特性、支持发行版与安装说明。"
tags: [toolbx, toolbox, readme, ostree, podman, containers, introduction]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:55:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:55:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: https://github.com/containers/toolbox/blob/main/README.md
    title: toolbox README.md
---

# README.md 项目概览

## 项目基本信息

- **二进制名称**：`toolbox`
- **项目规范名称**：Toolbx（曾用名 Toolbox、Fedora Toolbox）
- **Go 模块路径**：`github.com/containers/toolbox`
- **Go 版本要求**：1.22.0
- **描述**：Linux 上用于软件开发和主机故障排查的交互式命令行环境工具
- **底层技术**：构建于 Podman 和 OCI 标准容器技术之上
- **官方网站**：https://containertoolbx.org/
- **源码仓库**：https://github.com/containers/toolbox
- **许可证**：Apache-2.0

## 核心设计定位

Toolbx 特别适用于 OSTree-based 操作系统（Fedora CoreOS、Silverblue），这类系统：
- 不鼓励在主机上安装软件
- 通常不提供 DNF/YUM 等包管理器
- 主机文件系统不可变（immutable）

Toolbx 通过提供完全可变的容器环境解决这一问题，用户可以在容器内自由安装开发工具、编辑器和 SDK，例如 `yum install ansible`，而不会影响基础操作系统。

Toolbx 不强制要求使用 OSTree 系统，在 Fedora Workstation/Server 上同样可用。

## 主机资源透传清单

Toolbx 环境无缝访问以下主机资源：

| 资源类型 | 具体内容 |
|---------|---------|
| 用户目录 | 用户主目录（home directory） |
| 图形套接字 | Wayland 和 X11 套接字 |
| 网络 | 网络连接（含 Avahi 和 CA 证书） |
| 可移动设备 | USB 存储设备等 |
| 系统日志 | systemd journal |
| SSH | SSH agent |
| 进程间通信 | D-Bus 会话总线和系统总线 |
| 资源限制 | ulimits |
| 设备文件 | `/dev` 目录和 udev 数据库 |
| 主机逃生口 | `/run/host` 路径访问完整主机文件系统 |

## 支持的 Linux 发行版

默认情况下，Toolbx 尝试使用与主机发行版匹配的镜像创建容器。如果主机不受支持，则回退到 Fedora 镜像。

| 发行版 | 支持版本格式 |
|-------|------------|
| Arch Linux | `latest` 或 `rolling` |
| Fedora | `<release>` 或 `f<release>`（如 39 或 f39） |
| RHEL | `<major>.<minor>`（如 8.5、9.3） |
| Ubuntu | `<YY>.<MM>`（如 22.04、24.04） |

## 默认镜像

在 Fedora 系统上，Toolbx 基于 `fedora-toolbox` OCI 镜像创建容器。

## 安全说明

Toolbx 不提供超出常规主机命令行环境的额外安全承诺——容器内用户与主机上用户拥有相同的权限级别。

## 名称迁移说明

名称迁移工作正在进行中：
- 规范名称为 "Toolbx"（首字母大写 T，不含字母 o）
- Git 仓库名称仍为 `toolbox`
- 二进制名称仍为 `toolbox`
- 各发行版软件包名称可能仍为 `toolbox`
