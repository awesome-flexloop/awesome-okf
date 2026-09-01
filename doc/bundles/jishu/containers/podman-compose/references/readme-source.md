---
type: Reference
title: podman-compose 官方 README
description: podman-compose 项目官方 README 文档信源
tags: [podman, compose, documentation, source]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:source-verification", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# podman-compose 官方 README

## 项目概述

podman-compose 是 [Compose Spec](https://compose-spec.io/) 的一个实现，使用 [Podman](https://podman.io/) 作为后端。项目聚焦于：

* rootless（无根模式）
* daemon-less 进程模型（直接执行 podman 命令，无需运行守护进程）

## 依赖项

项目仅依赖：

* `podman`
* [podman dnsname plugin](https://github.com/containers/dnsname)：通常在 `podman-plugins` 或 `podman-dnsname` 发行版包中，这些包默认不会被安装，需要手动安装。这使得同一 CNI 网络上的容器能够相互解析。当 podman 使用 netavark 作为网络后端时不需要此插件。
* Python 3.9 或更新版本
* [PyYAML](https://pyyaml.org/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

项目主体是单个 Python 文件脚本，可以直接放入 PATH 执行。

## 参考规范

* [spec.md](https://github.com/compose-spec/compose-spec/blob/master/spec.md)
* [docker-compose compose-file-v3](https://docs.docker.com/compose/compose-file/compose-file-v3/)
* [docker-compose compose-file-v2](https://docs.docker.com/compose/compose-file/compose-file-v2/)

## 替代方案

如[这篇文章](https://fedoramagazine.org/use-docker-compose-with-podman-to-orchestrate-containers-on-fedora/)所述，可以设置 `podman.socket` 并使用未经修改的 `docker-compose` 与该 socket 通信，但在这种情况下会失去进程模型优势（例如 `docker-compose build` 会将可能很大的上下文 tarball 发送到守护进程）。

对于类生产环境的单机容器化环境，可考虑：

- [k3s](https://k3s.io) | [k3s github](https://github.com/rancher/k3s)
- [MiniKube](https://minikube.sigs.k8s.io/)

对于真正的多节点集群，请查看任何生产级 OpenShift/Kubernetes 发行版，如 [OKD](https://www.okd.io/)。

## 版本说明

如果使用旧版本 `podman`（3.1.0 之前），可能需要使用旧版 `podman-compose` `0.1.x` 分支。旧版 0.1.x 分支使用映射和变通方法来补偿 rootless 限制。

现代 podman 版本（>=3.4）没有这些限制，因此可以使用最新稳定的 1.x 分支。

如果从 `podman-compose` 版本 `0.1.x` 升级，全局选项 `-t` 不再用于设置映射类型（如 `hostnet`）。如果需要该行为，请以标准方式传递，例如在 YAML 中使用 `network_mode: host`。

## 安装

### Pip

从 PyPI 安装最新稳定版本：

```bash
pip3 install podman-compose
```

传入 `--user` 以在普通用户主目录内安装，无需 root 权限。

或从 GitHub 安装最新开发版本：

```bash
pip3 install https://github.com/containers/podman-compose/archive/main.tar.gz
```

### 软件包仓库

podman-compose 可从以下软件包仓库获取：

Debian：

```bash
sudo apt install podman-compose
```

Fedora（从 f31 开始）仓库：

```bash
sudo dnf install podman-compose
```

Homebrew：

```bash
brew install podman-compose
```

### 使用本地 docker/podman 生成二进制文件

此脚本将下载仓库，使用 [Dockerfile](https://github.com/containers/podman-compose/blob/main/Dockerfile) 生成二进制文件，并将二进制文件放置在调用此脚本的目录中：

```bash
sh -c "$(curl -sSL https://raw.githubusercontent.com/containers/podman-compose/main/scripts/download_and_build_podman-compose.sh)"
```

### 手动安装

```bash
curl -o /usr/local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose
```

或安装在用户主目录内：

```bash
curl -o ~/.local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x ~/.local/bin/podman-compose
```

## 测试

podman-compose 通过单元测试和集成测试进行测试。

单元测试可通过以下方式运行：

```shell
python3 -m unittest discover tests/unit
```

集成测试可通过以下方式运行：

```shell
python3 -m unittest discover tests/integration
```
