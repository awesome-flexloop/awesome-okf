---
type: Concept
title: "5分钟快速上手"
description: "从拉取镜像到启动JupyterLab、挂载目录、切换前端的完整快速入门流程"
tags: [quickstart, docker-run, jupyterlab, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-readme, resource: "/references/dockerfiles.md", title: "README快速开始" }
  - { id: src-startup, resource: "/references/startup-scripts.md", title: "启动脚本" }
---

# 5分钟快速上手

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-started/get-docker/)
- 知道你要使用哪个镜像（参考[项目介绍](00-introduction.md)中的场景表）

## 第一步：启动 JupyterLab

最简单的启动命令：

```bash
docker run -p 10000:8888 quay.io/jupyter/scipy-notebook:2026-07-28
```

这条命令会：
1. 从 Quay.io 拉取 `jupyter/scipy-notebook:2026-07-28` 镜像（本地不存在时）
2. 启动容器运行 Jupyter Server（JupyterLab 前端）
3. 将容器内 8888 端口映射到主机 10000 端口

启动后在浏览器访问：

```
http://localhost:10000/?token=<token>
```

其中 `<token>` 是控制台打印的认证令牌。

## 第二步：挂载工作目录

使用 `-v` 参数挂载当前目录，让笔记本文件持久化到主机：

```bash
docker run -it --rm -p 10000:8888 -v "${PWD}":/home/jovyan/work quay.io/jupyter/datascience-notebook:2026-07-28
```

关键参数说明：

| 参数 | 作用 |
|------|------|
| `-it` | 交互式终端（保持STDIN打开，分配伪TTY） |
| `--rm` | 容器退出后自动删除容器（但挂载目录中的文件保留在主机） |
| `-v "${PWD}":/home/jovyan/work` | 将当前目录挂载到容器内 `/home/jovyan/work` |

> **注意**：默认的 Jupyter `root_dir` 是 `/home/jovyan`。新建笔记本默认保存在这里。要将工作目录设为挂载的 `work` 目录，需添加：
> ```bash
> start-notebook.py --ServerApp.root_dir=/home/jovyan/work
> ```

## 第三步：切换 Jupyter 前端

JupyterLab 是默认前端。切换到经典 Notebook：

```bash
docker run -p 8888:8888 -e DOCKER_STACKS_JUPYTER_CMD=notebook quay.io/jupyter/base-notebook
```

`DOCKER_STACKS_JUPYTER_CMD` 支持的值：

| 值 | 启动的前端 |
|----|----------|
| `lab`（默认） | JupyterLab |
| `notebook` | Jupyter Notebook v7 |
| `nbclassic` | NBClassic（经典Notebook界面） |
| `server` | 纯Jupyter Server（无前端） |
| `retro` | RetroLab（类Notebook的JupyterLab前端） |

## 常用启动选项

### 授予 sudo 权限

```bash
docker run -it --rm -p 8888:8888 -e GRANT_SUDO=yes --user root quay.io/jupyter/base-notebook
```

容器内可以使用 `sudo` 安装系统包（需要以 `--user root` 启动）。

### 自动重启

```bash
docker run -p 8888:8888 -e RESTARTABLE=yes quay.io/jupyter/base-notebook
```

Jupyter Server 崩溃后会自动重启。

### 使用固定Token（无随机生成）

```bash
docker run -p 8888:8888 quay.io/jupyter/base-notebook start-notebook.py --IdentityProvider.token=mysecret
```

### 传递额外参数

通过 `NOTEBOOK_ARGS` 环境变量传递 Jupyter 启动参数：

```bash
docker run -p 8888:8888 -e NOTEBOOK_ARGS="--NotebookApp.notebook_dir=/home/jovyan/work" quay.io/jupyter/base-notebook
```

## 镜像标签选择

镜像使用**日期标签**（如 `2026-07-28`）而非 `latest` 来保证可复现性。`latest` 标签指向周构建版本。

也可以使用更具体的标签：

```
quay.io/jupyter/base-notebook:aarch64-python-3.13.14   # ARM64 + 特定Python版本
quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28     # CUDA 12变体
```

## 相关概念

- [项目介绍](00-introduction.md)
- [镜像层级架构](02-image-hierarchy.md)
- [启动生命周期](07-startup-lifecycle.md)
- [Hook扩展与自定义](08-hooks-and-customization.md)
