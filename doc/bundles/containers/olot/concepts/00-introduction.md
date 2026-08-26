---
type: Concept
title: olot 定位与 ModelCar 标准
description: 了解 olot 是什么、解决什么问题，以及 ModelCar OCI 镜像标准的基本概念
tags: [introduction, modelcar, oci, overview]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/olot/references/readme-source.md
    title: "olot 项目 README 信源"
---

# olot 定位与 ModelCar 标准

olot（发音类似 "oh-lot"，全称 "oci layers on top"）是一个轻量级 Python 工具，专门用于向已有的 OCI（Open Container Initiative）兼容镜像追加文件层。它的核心设计目标是简化 ML/AI 模型的容器化打包流程，是 KServe ModelCar 标准的参考实现之一。

## 项目基本信息

| 属性 | 值 |
|------|----|
| 包名 | `olot` |
| 版本 | 1.2.2 |
| Python 版本要求 | >= 3.10 |
| 核心依赖 | click >= 8.1.7, pydantic >= 2.10.3 |
| CLI 入口 | `olot` 命令 |
| PyPI 地址 | https://pypi.org/p/olot |

## olot 解决什么问题

传统上，将 ML 模型打包到容器镜像需要编写 Dockerfile、构建镜像，这一过程存在以下痛点：

1. **需要 Docker 环境**：构建过程依赖 Docker daemon
2. **重复构建**：基础镜像不变但模型更新时需要重新构建整个镜像
3. **学习曲线**：需要掌握 Dockerfile 语法和最佳实践
4. **CI/CD 复杂**：在流水线中集成容器构建需要额外配置

olot 的解决方案是：
- 基于标准 OCI image layout 格式直接操作镜像
- 不需要 Docker daemon，纯文件系统操作
- 支持三种后端（skopeo/oras/oras-py）适配不同环境
- 既可以作为 CLI 工具使用，也提供 Python API

## ModelCar 标准

ModelCar 是 KServe 提出的将 ML 模型打包为 OCI 镜像的标准模式。在 ModelCar 模式下：

- 模型文件存放在容器内的 `/models/` 目录
- ModelCarD（模型卡片）是一个 `README.md` 文件，包含模型元数据
- 模型文件作为独立的 OCI 层追加到基础镜像之上
- 镜像可以被 KServe 等推理服务框架直接拉取和使用

### ModelCar 镜像结构

```
基础镜像（ubi-micro/busybox等）
└── 模型层 1（model.safetensors）
    └── 模型层 2（config.json）
        └── 模型层 N（tokenizer.json等）
            └── ModelCarD 层（README.md，gzip 压缩）
```

## 典型工作流

使用 olot 打包 ModelCar 的标准三步流程：

```bash
# 步骤 1：拉取基础镜像到本地 OCI layout
skopeo copy docker://quay.io/mmortari/hello-world-wait:latest oci:download:latest

# 步骤 2：使用 olot 追加模型层
olot download --modelcard README.md model.joblib

# 步骤 3：推送更新后的镜像到 registry
skopeo copy oci:download:latest docker://quay.io/mmortari/model:latest
```

## 核心特性

- **纯 Python 操作**：核心逻辑不依赖外部工具（可选 oras-py 后端）
- **多后端支持**：skopeo CLI、oras cp CLI、oras-py Python 库
- **保留目录结构**：通过 `--root-dir` 参数保留模型文件的子目录结构
- **层内容注解**：每个层自动添加四元组注解，记录原始文件信息
- **ModelPack 支持**：可选生成 ModelPack manifest 用于多架构索引
- **Docker 格式兼容**：自动转换 Docker distribution manifest 格式为 OCI 格式

## 适用场景

- 在 CI/CD 流水线中自动打包 ML 模型
- 没有 Docker 环境的轻量级环境
- 需要程序化控制镜像构建过程
- KServe ModelCar 模式的模型发布
- 向任意 OCI 镜像追加文件（不仅限于 ML 模型）

## 相关概念

- [OCI 层操作与四元组注解](/bundles/containers/olot/concepts/01-oci-layers.md)：了解 olot 如何操作 OCI 层
- [后端抽象层](/bundles/containers/olot/concepts/02-backends.md)：了解三种后端的区别和选择
- [Python API 编程](/bundles/containers/olot/concepts/03-python-api.md)：在代码中集成 olot
