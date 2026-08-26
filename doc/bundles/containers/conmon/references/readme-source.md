---
type: Reference
title: README 项目说明信源
description: conmon 项目 README.md 信源——OCI容器运行时监控器的定位、功能概述、构建依赖与安装方式
tags: [reference, readme, overview, conmon, oci]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-readme
    title: README.md
    path: external/dao/action/Containers/conmon/README.md
---

# README 项目说明信源

> 信源文件：[README.md](file:///d:/spaces/SpecWeave/external/dao/action/Containers/conmon/README.md)

本文档记录 conmon 项目 README.md 中描述的项目定位、核心功能、构建依赖和安装方式。

---

## 项目定位

conmon 是一个 OCI（Open Container Initiative）容器运行时监控器（container runtime monitor）。它是使用 C 语言编写的低内存占用守护进程，设计为容器管理器（如 Podman、CRI-O）和 OCI 运行时（如 runc、crun）之间的监控程序和通信工具，负责单个容器的生命周期管理。

## 核心功能

启动时 conmon 通常执行双 fork（double-fork）以守护进程化，与启动它的父进程分离。之后它将运行时作为自己的子进程启动。这使得管理进程可以在前台退出，但仍然能够监视并连接到子进程（容器）。

容器运行期间，conmon 执行两项主要任务：

1. **提供容器附加套接字**：保持容器标准流打开，并通过套接字转发，支持运行时附加（attach）到容器终端
2. **记录容器流日志**：将容器流的内容写入日志文件（或 systemd journal），以便在容器终止后读取

容器终止时，conmon 记录其退出时间和退出代码，供管理程序读取。

## 构建依赖

### Fedora/CentOS/RHEL 系

```bash
sudo yum install -y \
  gcc \
  git \
  glib2-devel \
  glibc-devel \
  systemd-devel \
  make \
  pkgconfig \
  runc
```

### Debian/Ubuntu 系

```bash
sudo apt-get install \
  gcc \
  git \
  libc6-dev \
  libglib2.0-dev \
  pkg-config \
  make \
  runc
```

## 构建与安装

```bash
make
```

安装选项（PREFIX 默认为 `/usr/local`）：

- `make install`：安装到 `$PREFIX/bin`，添加到系统 PATH
- `make podman`：安装到 `$PREFIX/libexec/podman`，用于覆盖 Podman 使用的 conmon 版本
- `make crio`：安装到 `$PREFIX/libexec/crio`，用于覆盖 CRI-O 使用的 conmon 版本

运行 conmon 需要已安装 OCI 兼容运行时（如 runc 或 crun）。

## 测试

```bash
make test
```

需要安装 `bats` 和 `socat` 包。

## 静态构建

可以通过 Nix 包管理器构建静态链接二进制：

```bash
nix build -f nix/
```
