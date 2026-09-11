---
type: Reference
title: "官方手册、设计目标与版本演进信源（doc/、GOALS.md、NEWS）"
description: "Toolbx 10 个 man 页源文件、GOALS.md 设计取舍、NEWS 0.1.2-0.3 版本演进的信源登记，锚定 commit 81401f64。"
tags: [toolbx, toolbox, man-page, goals, news, reference, changelog]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T11:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T11:00:00+08:00 }
status: stable
stale_after: 2027-09-11
sources:
  - id: toolbox-repo-pinned
    resource: https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8
    title: containers/toolbox @81401f64（0.3-85-g81401f6，2026-08-05）
---

# 官方手册、设计目标与版本演进信源

本信源登记 Toolbx 仓库中**非代码**的权威叙述材料：man 页（由 go-md2man 构建）、设计目标文档与版本变更日志。这些材料用于校验实现层事实的"官方意图"，与 [source-code-map.md](source-code-map.md) 的代码证据互证。

## man 页源文件（doc/，10 个）

| 文件（section） | 信源 URL | 登记要点 |
|------|----------|---------|
| `toolbox.1.md`（1） | [blob/81401f64/doc/toolbox.1.md](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox.1.md) | 工具总览、4 个支持主机发行版（Arch/Fedora/RHEL ≥8.5/Ubuntu）与 distro-release 组合表、全局选项、8 个命令清单、安全边界声明 |
| `toolbox-create.1.md`（1） | [blob](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox-create.1.md) | entry point 设计动机（OCI 不可变性）、--authfile/--distro/--image/--release 互斥规则、容器标识（label 与 /run/.toolbxenv） |
| `toolbox-init-container.1.md`（1） | [blob](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox-init-container.1.md) | 容器内引导命令选项（--gid/--home/--home-link/--media-link/--mnt-link/--shell/--uid/--user）、--monitor-host 已废弃 |
| `toolbox-enter.1.md` / `toolbox-run.1.md`（1） | [enter](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox-enter.1.md) / [run](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox-run.1.md) | 交互进入与非交互执行的命令契约、--preserve-fds 语义 |
| `toolbox-list.1.md` / `toolbox-rm.1.md` / `toolbox-rmi.1.md`（1） | [doc/ 目录](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc) | 列表与删除命令契约（-c/-i、-a/-f） |
| `toolbox-help.1.md`（1） | [blob](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox-help.1.md) | 帮助命令 |
| `toolbox.conf.5.md`（5） | [blob](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/doc/toolbox.conf.5.md) | TOML 配置文件：仅 [general] 段 distro/image/release；/etc/containers/toolbox.conf → $XDG_CONFIG_HOME/containers/toolbox.conf 优先级 |

## 设计目标与版本演进

| 文件 | 信源 URL | 登记要点 |
|------|----------|---------|
| `GOALS.md` | [blob/81401f64/GOALS.md](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/GOALS.md) | 高层目标（Podman CLI 便利层、开发/调试/系统管理、多发行版）；三条非目标（仅 Podman、不堆功能、不做松耦合沙箱）；Silverblue/CoreOS/RHEL CoreOS 场景与 oc debug node 对齐 |
| `NEWS` | [blob/81401f64/NEWS](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/NEWS) | 0.3：mapstructure 安全升级、Flatpak SessionHelper 同步路径废弃、p11-kit ≥0.25.6 socket 配置；0.2：nvidia-container-toolkit ≥1.17.8（CVE-2025-23266/23267）、Go ≥1.22；0.1.2：主机 CA 证书（p11-kit server）引入、Ubuntu 25.04 |
| `CONTRIBUTING.md` / `SECURITY.md` / `CODE-OF-CONDUCT.md` | [仓库根](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8) | 贡献流程与安全策略（背景参考，本轮文档不直接引用） |

## 官方意图与代码证据的关键互证

- man page 称 entry point 运行时配置是为了"让新版 Toolbx 的改进作用于旧容器"——代码证据见 [source-code-map.md](source-code-map.md) 的 initContainer.go 登记（15 条 rbind 与引导序列）。
- man page 称"不承诺超出主机常规命令行环境的安全性"——与代码中 `--privileged --security-opt label=disable --pid host --userns keep-id` 互证。
- NEWS 中 p11-kit CA 证书特性（0.1.2 引入）与代码中 `configurePKCS11`/`startP11KitServer` 三处配置写入互证。
