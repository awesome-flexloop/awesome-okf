---
type: Concept
title: "项目介绍"
description: "Jupyter Docker Stacks 是什么、提供哪些镜像、适用场景、与官方仓库的关系"
tags: [jupyter, docker, introduction, overview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-readme, resource: "/references/dockerfiles.md", title: "README与Dockerfile索引" }
---

# Jupyter Docker Stacks 项目介绍

Jupyter Docker Stacks 是 Jupyter 官方维护的一组**即用型 Docker 镜像**，内含 Jupyter 应用和交互式计算工具。它不是单个镜像，而是一套按层级递进构建的镜像家族，从最小化的基础操作系统到包含 Python/R/Julia/Spark/PyTorch/TensorFlow 的全功能科学计算环境。[^src-readme]

## 能做什么

使用 Jupyter Docker Stacks 镜像，你可以：

- **启动个人 Jupyter Server**：默认使用 JupyterLab 前端，一条命令即可运行
- **部署团队 JupyterHub**：支持 JupyterHub 单用户服务器模式
- **切换经典 Notebook 前端**：通过环境变量切换回经典 Jupyter Notebook
- **构建自定义镜像**：以官方镜像为基础，编写自己的 Dockerfile 扩展功能

## 核心特性

- **多架构支持**：同时发布 `x86_64` 和 `aarch64`（ARM64/Apple Silicon）平台镜像
- **层级化设计**：12个镜像按依赖关系分层，按需选择
- **多语言支持**：Python（默认）、R、Julia 三语言内核
- **GPU 支持**：PyTorch 和 TensorFlow 提供 CUDA 变体镜像
- **自动重启**：通过 `RESTARTABLE=yes` 支持崩溃自动重启
- **Hook 扩展**：启动时自动执行 `/usr/local/bin/start-notebook.d/` 和 `before-notebook.d/` 目录下的脚本
- **安全默认**：非 root 用户 `jovyan`（UID 1000）运行，tini 作为 PID 1 回收僵尸进程

## 镜像仓库

自 2023-10-20 起，镜像仅发布到 **Quay.io**：

```
quay.io/jupyter/docker-stacks-foundation
quay.io/jupyter/base-notebook
quay.io/jupyter/minimal-notebook
quay.io/jupyter/scipy-notebook
quay.io/jupyter/r-notebook
quay.io/jupyter/julia-notebook
quay.io/jupyter/datascience-notebook
quay.io/jupyter/pytorch-notebook
quay.io/jupyter/tensorflow-notebook
quay.io/jupyter/pyspark-notebook
quay.io/jupyter/all-spark-notebook
```

Docker Hub 上的旧镜像不再更新。

## 适用场景

| 场景 | 推荐镜像 |
|------|---------|
| 最小化 Jupyter 环境，自行安装包 | base-notebook |
| Python 科学计算（pandas/scipy/matplotlib） | scipy-notebook |
| 数据科学全栈（Python+R+Julia） | datascience-notebook |
| R 语言统计分析 | r-notebook |
| Julia 科学计算 | julia-notebook |
| 深度学习（PyTorch GPU） | pytorch-notebook（CUDA变体） |
| 深度学习（TensorFlow GPU） | tensorflow-notebook（CUDA变体） |
| 大规模数据处理（Spark） | pyspark-notebook / all-spark-notebook |
| 自定义镜像基础层 | docker-stacks-foundation |

## 技术栈概览

- **基础 OS**：Ubuntu 24.04 (Noble Numbat)
- **Python 版本**：3.13（默认）
- **包管理器**：Mamba（基于 Conda 兼容的 libsolv 求解器）
- **Jupyter 组件**：JupyterLab、Notebook v7+、NBClassic、JupyterHub-SingleUser
- **容器引擎**：Docker（启用 BuildKit），兼容 Apple Container Framework
- **许可证**：BSD 3-Clause

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [镜像层级架构](02-image-hierarchy.md)
- [启动生命周期](07-startup-lifecycle.md)
