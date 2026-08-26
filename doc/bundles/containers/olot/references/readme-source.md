---
type: Reference
title: olot 项目 README 信源
description: olot 项目官方 README 文档，包含项目介绍、CLI 使用示例和 Python API 示例
tags: [readme, documentation, official]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/README.md"
    title: "olot 官方 README.md"
---

# olot 项目 README 信源

## 信源内容摘要

本信源来自 olot 项目根目录的 README.md 文件，版本 v1.2.2。

### 项目定位

olot（oci layers on top）是一个基于 Python 的工具，用于向 OCI 兼容镜像追加层（文件）。它设计用于与命令行工具（如 skopeo、oras）配合使用，也原生支持 oras Python 库作为纯 Python 后端（无需外部 Skopeo/CLI 工具）。

### 典型工作流

1. 使用 skopeo/oras 等工具拉取基础镜像到 OCI layout 格式
2. 使用 olot 添加 ML 模型层和 ModelCarD 元数据
3. 使用 skopeo/oras 将更新后的镜像推送到远程仓库

### CLI 关键命令

```bash
# 拉取镜像
skopeo copy --multi-arch all docker://${OCI_REGISTRY_SOURCE} oci:${IMAGE_DIR}:latest

# 添加模型层
uv run olot $IMAGE_DIR --modelcard README.md model.joblib

# 推送镜像
skopeo copy --multi-arch all oci:${IMAGE_DIR}:latest docker://${OCI_REGISTRY_DESTINATION}
```

### Python API 关键函数

- `oci_layers_on_top()`: 核心函数，向 OCI layout 添加层
- `skopeo_pull()`/`skopeo_push()`: skopeo 后端
- `oras_py_pull()`/`oras_py_push()`: oras-py 纯 Python 后端

### 验证命令

```bash
podman run --rm -it $OCI_REGISTRY_DESTINATION ls -la /models/
```
