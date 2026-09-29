---
okf_version: "0.2"
type: reference
title: "第二章 Ollama 安装与配置"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C2/
tags: [chapter2, installation, macos, windows, linux, docker]
status: stable
---

# 第二章 Ollama 安装与配置

## 信源定位

- **源码路径**：`docs/C2/`（4 节）
- **在线阅读**：[第二章](https://datawhalechina.github.io/handy-ollama/#/C2/)
- **内容性质**：实操指南，覆盖四大平台的安装配置流程

## 章节结构

| 节 | 文件 | 核心内容 |
|----|------|----------|
| 2.1 | `1. Ollama 在 macOS 下的安装与配置.md` | macOS 安装包、Homebrew、Enchanted 第三方客户端 |
| 2.2 | `2. Ollama 在 Windows 下的安装与配置.md` | Windows 原生安装、WSL2、环境变量、系统托盘 |
| 2.3 | `3. Ollama 在 Linux 下的安装与配置.md` | 一键安装脚本 `curl -fsSL https://ollama.com/install.sh \| sh`、systemd 服务 |
| 2.4 | `4. Ollama 在 Docker 下的安装与配置.md` | `docker pull ollama/ollama`、CPU/Nvidia/AMD 镜像、端口映射、volume 持久化 |

## 关键事实

- Docker 镜像：`ollama/ollama`（CPU/Nvidia GPU）、`ollama/ollama:rocm`（AMD GPU）
- Docker 运行命令映射 11434 端口：`docker run -d -p 11434:11434 -v ollama:/root/.ollama ollama/ollama`
- Linux 安装后自动配置 systemd 服务
- Windows 安装后 Ollama 以后台服务方式运行
- 支持指定版本镜像（如 `ollama/ollama:0.3.0`）

## 关联概念

- [Ollama 架构与安装](../concepts/ollama-architecture-installation.md) — 四平台安装步骤的系统整理
- [生产部署实践](../concepts/production-deployment.md) — Docker 容器化的生产配置
