---
title: 示例索引
id: examples-index
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
---

# 示例索引

本目录包含 Jupyter Docker Stacks 的实用示例，从基础运行到高级 CI/CD 集成。

## 示例列表

| 编号 | 示例 | 难度 | 预计时间 | 核心内容 |
|------|------|------|----------|----------|
| [01](01-basic-run.md) | 基础运行示例 | 入门 | 10 分钟 | Docker 启动、端口映射、目录挂载、Token/密码认证 |
| [02](02-custom-image.md) | 自定义镜像构建 | 中级 | 20 分钟 | Dockerfile 编写、mamba/pip 安装、多阶段构建、Hooks |
| [03](03-gpu-cuda.md) | GPU/CUDA 加速 | 中级 | 15 分钟 | PyTorch/TensorFlow GPU 镜像、多 GPU、Docker Compose |
| [04](04-ci-integration.md) | CI/CD 集成 | 高级 | 30 分钟 | GitHub Actions、自动化测试、Makefile、多架构构建 |
| [05](05-recipes.md) | 常用配方集锦 | 中级 | 25 分钟 | SSL/Dask/Spark/数据库/多语言 Kernel 等实用配方 |

## 学习路径建议

### 初学者路径

```
01-basic-run → 02-custom-image → 05-recipes
```

先掌握基础运行，再学习自定义镜像构建，最后查阅常用配方解决具体问题。

### 数据科学家路径

```
01-basic-run → 02-custom-image → 03-gpu-cuda → 05-recipes
```

重点掌握 GPU 加速环境配置和常用数据科学工具链。

### DevOps/平台工程师路径

```
01-basic-run → 02-custom-image → 04-ci-integration → 03-gpu-cuda
```

重点掌握 CI/CD 流水线、自动化测试和多架构构建。

## 前置知识

- 基础 Docker 命令（`docker run`、`docker build`、`docker ps`）
- 基本命令行操作
- 了解 Jupyter Notebook/Lab 基本使用

## 示例约定

- 所有示例中的日期标签 `2026-07-28` 应替换为实际使用的版本标签
- 命令中的 `${PWD}` 表示当前工作目录（PowerShell 中使用 `${PWD}`，bash 中使用 `$(pwd)`）
- Dockerfile 示例假设构建上下文在包含 Dockerfile 的目录中

```{toctree}
:maxdepth: 7

01-basic-run
02-custom-image
03-gpu-cuda
04-ci-integration
05-recipes
```
