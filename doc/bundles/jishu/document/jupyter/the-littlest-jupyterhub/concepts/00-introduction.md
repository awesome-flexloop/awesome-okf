---
title: The Littlest JupyterHub 简介
description: 了解 TLJH 是什么、目标用户、支持平台和核心特性
type: Concept
tags: [concept, intro, jupyterhub, tljh, overview]
sources:
  - id: tljh-readme
    title: README.md
  - id: tljh-setup
    title: setup.py
---

# The Littlest JupyterHub 简介

**The Littlest JupyterHub（TLJH）** 是一个面向1-100用户规模的 JupyterHub 发行版，专为不具备系统管理员经验的用户设计。

## 什么是 TLJH？

TLJH 是 JupyterHub 的一个"小而全"发行版，在单台服务器上为1-100名用户提供 Jupyter Notebook/Lab 环境。它将 JupyterHub、反向代理（Traefik）、Conda 环境管理、多用户认证等组件整合为一个开箱即用的系统。

## 目标用户

TLJH 的目标受众是"不认为自己是系统管理员"的用户——例如教育工作者、研究团队负责人、数据科学团队管理者。这些用户需要为学生或团队成员提供 Notebook 服务，但不想手动配置 JupyterHub 的各个组件。

## 支持平台

- **操作系统**：Debian 和 Ubuntu LTS 版本
- **架构**：amd64（x86_64）和 arm64（aarch64）

## 核心特性

1. **一键安装**：通过 bootstrap 脚本完成从系统依赖到服务启动的全流程安装
2. **双环境架构**：Hub 环境运行管理组件，User 环境为所有用户提供 Notebook 计算
3. **声明式配置**：通过 `tljh-config` 命令和 YAML 文件管理配置，无需手写 Python
4. **多种认证方式**：内置 FirstUse/Native/LDAP/TMP/OAuth 等多种认证器
5. **插件扩展**：基于 pluggy 框架的插件系统，支持通过 Python 包扩展功能
6. **HTTPS 支持**：内置 Let's Encrypt 自动证书和手动证书配置
7. **资源限制**：可配置每个用户的内存和 CPU 限制

## 技术栈

| 组件 | 用途 |
|------|------|
| JupyterHub 5.x | 多用户 Notebook 服务核心 |
| Traefik 3.x | 反向代理和路由 |
| SystemdSpawner | 以 systemd 服务管理用户进程 |
| Conda/Mamba | Python 环境和包管理 |
| pluggy | 插件框架 |

## 版本信息

- 当前版本：2.0.1.dev
- Python 要求：≥3.9
- License：3-Clause BSD

## 下一步

- [安装指南](01-installation.md)：在服务器上安装 TLJH
- [架构概览](02-architecture.md)：理解 TLJH 的双环境架构
