---
type: Concept
title: 快速上手与 Compose Spec 兼容
description: podman-compose 项目介绍、安装方法与 Compose 规范兼容性说明
tags: [podman, compose, getting-started, installation, compatibility]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# 快速上手与 Compose Spec 兼容

podman-compose 是 [Compose 规范](https://compose-spec.io/) 的 Podman 后端实现，提供与 Docker Compose 类似的多容器应用编排能力，但采用无守护进程（daemon-less）和无根（rootless）优先的设计理念。

## 核心特性

podman-compose 专注于两个核心设计目标：

1. **rootless 支持**：无需 root 权限即可运行容器编排
2. **daemon-less 进程模型**：直接调用 podman CLI，不需要后台守护进程

项目主体是单个 Python 文件脚本 `podman_compose.py`，可以直接放入 PATH 执行，部署极其轻量。

## 环境要求

运行 podman-compose 需要满足以下依赖：

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| podman | >= 3.4（1.x分支） | 容器运行时 |
| Python | >= 3.9 | 运行环境 |
| PyYAML | - | YAML 配置解析 |
| python-dotenv | - | .env 文件支持 |
| podman dnsname 插件 | 可选 | CNI 网络容器域名解析（netavark 后端不需要） |

## 安装方法

### 使用 pip 安装（推荐）

安装最新稳定版本：

```bash
pip3 install podman-compose
```

安装到用户目录（无需 root）：

```bash
pip3 install --user podman-compose
```

安装开发版本：

```bash
pip3 install https://github.com/containers/podman-compose/archive/main.tar.gz
```

### 使用系统包管理器

Debian/Ubuntu：

```bash
sudo apt install podman-compose
```

Fedora：

```bash
sudo dnf install podman-compose
```

macOS (Homebrew)：

```bash
brew install podman-compose
```

### 手动安装（单文件部署）

直接下载单文件脚本：

```bash
curl -o ~/.local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x ~/.local/bin/podman-compose
```

## Compose Spec 兼容性

podman-compose 实现了 Compose 规范，支持标准的 `docker-compose.yml`/`compose.yaml` 配置文件。项目参考以下规范文档：

- [Compose Spec 官方规范](https://github.com/compose-spec/compose-spec/blob/master/spec.md)
- [Docker Compose v3 文件格式](https://docs.docker.com/compose/compose-file/compose-file-v3/)
- [Docker Compose v2 文件格式](https://docs.docker.com/compose/compose-file/compose-file-v2/)

大多数现有的 Docker Compose 配置文件可以直接在 podman-compose 下使用，无需修改。

## 版本说明

| 分支 | 兼容 Podman 版本 | 说明 |
|------|-----------------|------|
| 1.x | >= 3.4 | 推荐版本，无需 workaround |
| 0.1.x | < 3.1.0 | 旧版本，使用映射补偿 rootless 限制 |

从 0.1.x 升级到 1.x 时需要注意：全局 `-t` 选项已移除，网络模式映射应在 YAML 中使用标准字段 `network_mode: host`。

## 与 Docker Compose 的差异

与通过 `podman.socket` 使用原版 docker-compose 相比，podman-compose 的优势在于：

- 不经过守护进程转发，构建上下文等大文件无需 tarball 传输
- 原生 rootless 设计，权限模型更安全
- 进程模型更简单，故障排查更直接

## 验证安装

安装完成后，验证版本：

```bash
podman-compose --version
```

## 相关概念

- [daemon-less 架构](/concepts/01-daemonless-arch.md)
- [rootless 模式下的网络与卷](/concepts/02-rootless.md)
- [Compose 文件常见模式](/concepts/03-compose-patterns.md)
- [WordPress 部署示例](/examples/01-wordpress.md)
