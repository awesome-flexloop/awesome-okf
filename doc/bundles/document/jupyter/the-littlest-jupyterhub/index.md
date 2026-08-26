---
title: The Littlest JupyterHub
description: TLJH 源码学习 Wiki —— 面向 1-100 用户的轻量级 JupyterHub 发行版
type: Bundle
tags: [jupyter, jupyterhub, tljh, multi-user, devops, data-science]
---

# The Littlest JupyterHub (TLJH)

**The Littlest JupyterHub** 是一个面向 1-100 用户规模的 JupyterHub 发行版，专为不具备系统管理员经验的用户设计。它在单台服务器上集成 JupyterHub、Traefik 反向代理、Conda 环境管理、多用户认证等组件，实现开箱即用的多用户 Notebook 服务。

## 快速导航

### 📖 概念文档（Concepts）

理解 TLJH 的核心架构和设计理念。

| 文档 | 说明 |
|------|------|
| [TLJH 简介](concepts/00-introduction.md) | TLJH 是什么、目标用户、支持平台、核心特性 |
| [安装指南](concepts/01-installation.md) | 在 Debian/Ubuntu 服务器上安装 TLJH |
| [架构概览与双环境模型](concepts/02-architecture.md) | 双 Conda 环境架构、systemd 服务模型、进程隔离 |
| [配置系统与 tljh-config](concepts/03-config-system.md) | YAML 配置、tljh-config CLI、Schema 校验、配置应用机制 |
| [用户管理与 SystemdSpawner](concepts/04-user-management.md) | 用户创建流程、权限管理、认证方式、资源限制 |
| [Traefik 代理与 HTTPS](concepts/05-traefik-proxy.md) | 文件代理模式、路由机制、Let's Encrypt、TLS 配置 |
| [插件系统](concepts/06-plugin-system.md) | pluggy 插件框架、8 个扩展点、插件开发 |
| [安装流程深度解析](concepts/07-installation-deep-dive.md) | Bootstrap 两阶段引导、Installer 完整流程 |

### 🛠️ 示例文档（Examples）

从实际操作中学习常见配置和使用场景。

| 文档 | 说明 |
|------|------|
| [基础安装与第一个用户](examples/01-basic-install.md) | 全新服务器安装 TLJH 并配置管理员 |
| [配置基础操作](examples/02-config-basics.md) | 用户管理、默认应用、网络、空闲清理 |
| [配置 GitHub OAuth 认证](examples/03-github-auth.md) | 使用 GitHub 账户登录 JupyterHub |
| [配置 HTTPS 与 Let's Encrypt](examples/04-https-letsencrypt.md) | 免费 SSL 证书启用 HTTPS |
| [开发一个简单 TLJH 插件](examples/05-custom-plugin.md) | 从零创建预装包+自定义配置的插件 |
| [设置用户资源限制](examples/06-resource-limits.md) | 内存/CPU 限制、cgroup、空闲清理 |

### 📚 信源文档（References）

基于源码的 API 参考文档，每条 API 均可溯源到具体源码位置。

| 文档 | 对应源码 |
|------|---------|
| [installer.py 信源](references/installer-source.md) | `tljh/installer.py` — 安装流程核心 |
| [config.py 信源](references/config-source.md) | `tljh/config.py` — 配置管理与 CLI |
| [configurer.py 信源](references/configurer-source.md) | `tljh/configurer.py` — YAML→Traitlets 桥接 |
| [hooks.py 信源](references/hooks-source.md) | `tljh/hooks.py` — 插件钩子规范 |
| [traefik.py 信源](references/traefik-source.md) | `tljh/traefik.py` — Traefik 代理管理 |
| [conda.py 信源](references/conda-source.md) | `tljh/conda.py` — Conda 环境管理 |
| [user.py 信源](references/user-source.md) | `tljh/user.py` — 系统用户/组管理 |
| [bootstrap.py 信源](references/bootstrap-source.md) | `bootstrap/bootstrap.py` — 零依赖引导 |
| [systemd.py 信源](references/systemd-source.md) | `tljh/systemd.py` — Systemd 服务封装 |
| [辅助模块信源](references/utility-modules-source.md) | utils/yaml/log/migrator/normalize/apt/user_creating_spawner |

### 📊 工作文档

| 文档 | 说明 |
|------|------|
| [源码事实清单](facts.md) | R阶段产出：305条零推测事实，每条指向具体源码行号 |
| [架构洞察](insights.md) | I阶段产出：5个核心洞察四元组 + 知识地图 |

## 学习路径

```
入门 → [简介](concepts/00-introduction.md) → [安装指南](concepts/01-installation.md) → [基础安装示例](examples/01-basic-install.md)
                                                                    ↓
核心 → [架构概览](concepts/02-architecture.md) → [配置系统](concepts/03-config-system.md) → [用户管理](concepts/04-user-management.md)
     → [Traefik代理](concepts/05-traefik-proxy.md) → [插件系统](concepts/06-plugin-system.md)
                                                                    ↓
高级 → [安装深度解析](concepts/07-installation-deep-dive.md) → 信源文档参考
```

## 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| JupyterHub | 5.x | 多用户 Notebook 服务核心 |
| Traefik | 3.6.5 | 反向代理和路由 |
| SystemdSpawner | 1.x | systemd 管理用户进程 |
| Miniforge | 24.7.1-2 | Conda 环境管理 |
| pluggy | 1.x | 插件框架 |
| Python | ≥3.9 | 运行时 |

## 源码信息

- **项目版本**：2.0.1.dev
- **源码路径**：`external/libs/jupyter/the-littlest-jupyterhub/`
- **上游仓库**：https://github.com/jupyterhub/the-littlest-jupyterhub
- **License**：3-Clause BSD

```{toctree}
:maxdepth: 7

concepts/00-introduction
concepts/01-installation
concepts/02-architecture
concepts/03-config-system
concepts/04-user-management
concepts/05-traefik-proxy
concepts/06-plugin-system
concepts/07-installation-deep-dive
examples/01-basic-install
examples/02-config-basics
examples/03-github-auth
examples/04-https-letsencrypt
examples/05-custom-plugin
examples/06-resource-limits
references/bootstrap-source
references/conda-source
references/config-source
references/configurer-source
references/hooks-source
references/installer-source
references/systemd-source
references/traefik-source
references/user-source
references/utility-modules-source
facts
insights
log
```
