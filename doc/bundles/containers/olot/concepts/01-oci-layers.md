---
type: Concept
title: OCI 层操作与四元组注解
description: 深入理解 olot 如何操作 OCI 镜像层、层的 tar/gzip 打包，以及四元组内容注解机制
tags: [oci, layers, annotations, tar, gzip]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: oci-source
    resource: /bundles/containers/olot/references/oci-source.md
    title: "olot OCI 模块源码信源"
  - id: basics
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/basics.py"
    title: "olot/basics.py 核心实现"
---

# OCI 层操作与四元组注解

olot 的核心功能是操作 OCI image layout 目录结构，将本地文件打包为新的镜像层并追加到现有镜像中。本文深入解析层的创建过程和四元组注解机制。

## OCI Image Layout 结构

一个标准的 OCI layout 目录包含以下结构：

```
ocilayout/
├── oci-layout          # 版本标记文件，内容固定为 {"imageLayoutVersion": "1.0.0"}
├── index.json          # 根索引文件，指向镜像 manifest 或 index
└── blobs/
    └── sha256/
        ├── <hash1>     # 各种 blob：manifest、config、layer tar 文件等
        ├── <hash2>
        └── ...
```

所有内容（manifest、config、layers）都以 SHA256 哈希作为文件名存储在 `blobs/sha256/` 目录下，这是一种内容寻址存储（Content-Addressable Storage）。

## 层创建流程

当调用 `oci_layers_on_top()` 添加模型文件时，执行以下步骤：

### 1. 输入验证与规范化

- 将所有路径转换为 `Path` 对象并解析为绝对路径
- 检查 `root_dir` 时，验证所有 model_files 确实在 root_dir 下
- 检查 modelcard 是否被误包含在 model_files 中
- 验证 OCI layout 目录格式正确
- 自动转换 Docker 格式 manifest 为 OCI 格式

### 2. 遍历现有 manifest 和 index

- 读取 `index.json` 根索引
- 递归解析所有嵌套的 index（多架构镜像情况）
- 收集所有需要更新的 image manifest
- 过滤掉 attestation manifest（如 in-toto  attestation）

### 3. 为每个文件创建层

对于普通模型文件，调用 `tarball_from_file()` 创建未压缩的 tar 层：
- 文件在 tar 包内的路径为 `/models/<filename>`
- 使用 `root_dir` 时保留子目录结构，如 `/models/onnx/model.onnx`
- 计算 tar 文件的 SHA256 哈希作为 layer digest
- 计算 tar 解包内容的 SHA256 哈希作为 diff_id（用于 rootfs）
- 将 tar 文件写入 `blobs/sha256/<layer_digest>`

对于 ModelCarD（README.md），调用 `targz_from_file()` 创建 gzip 压缩的层：
- 自动添加 `io.opendatahub.modelcar.layer.type: modelcard` 注解
- 压缩后的 tar.gz 作为层 blob

### 4. 更新每个 manifest

对每个找到的 image manifest：
1. 读取并解析对应的 config blob
2. 为每个新层创建 `ContentDescriptor`，包含正确的 mediaType
   - 普通层：`application/vnd.oci.image.layer.v1.tar`
   - 压缩层：`application/vnd.oci.image.layer.v1.tar+gzip`
3. 将层描述符追加到 `manifest.layers` 列表
4. 将新层的 diff_id 追加到 `config.rootfs.diff_ids`
5. 添加 history 条目记录层的创建时间和创建者
6. 添加层内容四元组注解
7. 添加自定义 labels 和 annotations（如果提供）
8. 重新序列化 config 和 manifest
9. 计算新的 SHA256 哈希，重命名 blob 文件
10. 更新 config 和 manifest 的 digest 引用

### 5. 更新索引链

- 如果有父 index，更新其中指向 manifest 的 digest
- 重新计算 index 的哈希并更新
- 一路更新回根 `index.json`

### 6. （可选）添加 ModelPack manifest

当 `add_modelpack=True` 时：
- 创建 ModelPack 专用的 model config
- 创建使用 ModelPack MediaType 的独立 manifest
- 将这个新 manifest 添加到多架构 index 中
- 标记 `io.opendatahub.modelcar.manifest.type: modelpack` 注解

## 四元组内容注解

每个层都自动添加四个标准注解，用于记录原始文件的元信息。这些注解存储在层描述符的 `annotations` 字段中。

| 注解键 | 说明 | 示例值 |
|--------|------|--------|
| `olot.layer.content.digest` | 原始文件的 SHA256 哈希（不是 tar 或 tar.gz 的哈希） | `sha256:abc123...` |
| `olot.layer.content.type` | 输入类型：`file` 或 `directory` | `file` |
| `olot.layer.content.inlayerpath` | 层在容器文件系统中展开后的完整路径 | `/models/model.joblib` |
| `olot.layer.content.name` | 原始文件的basename | `model.joblib` |

此外，所有层都会添加：
- `org.opencontainers.image.title`：层的标题（同 name）
- `io.opendatahub.author: olot`：manifest 级别标记作者
- `io.opendatahub.layers.modelcard`：指向 ModelCarD 层的 digest（如果有 modelcard）

### 四元组注解的用途

1. **溯源**：可以从镜像层追溯到原始文件的哈希和路径
2. **验证**：对比原始文件哈希，确认文件完整性
3. **工具链集成**：其他工具可以读取这些注解了解层内容
4. **调试**：排查问题时快速了解每个层包含什么文件

## MediaType 对照

| 内容类型 | MediaType | 说明 |
|---------|-----------|------|
| Image Manifest | `application/vnd.oci.image.manifest.v1+json` | 单架构镜像清单 |
| Image Index | `application/vnd.oci.image.index.v1+json` | 多架构镜像索引 |
| 未压缩层 | `application/vnd.oci.image.layer.v1.tar` | 普通 tar 格式层 |
| Gzip 压缩层 | `application/vnd.oci.image.layer.v1.tar+gzip` | ModelCarD 使用的压缩层 |
| 空内容 | `application/vnd.oci.empty.v1+json` | 空 JSON `{}` |
| Runtime Config | `application/vnd.oci.image.config.v1+json` | 容器运行时配置 |

## 相关概念

- [olot 定位与 ModelCar 标准](/bundles/containers/olot/concepts/00-introduction.md)：项目整体介绍
- [后端抽象层](/bundles/containers/olot/concepts/02-backends.md)：镜像拉取推送的后端实现
- [命令行基本使用](/bundles/containers/olot/examples/01-cli-usage.md)：CLI 操作示例
