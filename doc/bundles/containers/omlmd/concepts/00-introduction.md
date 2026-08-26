---
type: concept
scope: omlmd
name: introduction
version: "0.1.6"
source: https://github.com/containers/omlmd
description: OMLMD 定位与 OCI Artifact 媒体类型
---

# OMLMD 介绍

## 什么是 OMLMD

OMLMD（OCI Artifact for ML model & metadata）是 containers 组织开发的开源工具链，提供蓝图、模式和工具集（Python SDK + CLI），用于利用 OCI Artifact 和容器注册表来存储、分发和管理 ML 模型及其元数据。

- **版本**：0.1.6
- **作者**：Matteo Mortari
- **许可证**：Apache-2.0
- **Python 支持**：3.9、3.10、3.11、3.12
- **核心依赖**：oras-py（OCI 注册表客户端）、PyYAML、Click、Cloup

## 设计定位

传统的 ML 模型分发面临以下问题：
1. **模型文件与元数据分离**：模型权重存储在对象存储，元数据分散在文档或数据库中
2. **版本管理困难**：缺乏统一的版本控制机制
3. **分发不标准**：没有利用成熟的容器注册表生态

OMLMD 通过 OCI Artifact 规范解决这些问题：
- 将 ML 模型文件和元数据打包为标准 OCI Artifact
- 复用现有容器注册表（Docker Registry、Quay、zot、Distribution Registry 等）
- 支持模型版本管理、签名、权限控制等容器生态能力
- 提供 CLI 和 Python SDK 两种使用方式

## OCI Artifact 媒体类型

OMLMD 定义了两种自定义媒体类型来区分不同内容层：

| 媒体类型 | 常量名 | 用途 | 文件名模式 |
|---|---|---|---|
| `application/x-mlmodel` | `MIME_APPLICATION_MLMODEL` | ML 模型文件层 | 用户指定的模型文件（如 `model.joblib`、`model.onnx`） |
| `application/x-config` | `MIME_APPLICATION_CONFIG` | 元数据配置层 | `model_metadata.omlmd.json`、`model_metadata.omlmd.yaml` |

### 常量定义

```python
FILENAME_METADATA_JSON = "model_metadata.omlmd.json"
FILENAME_METADATA_YAML = "model_metadata.omlmd.yaml"
MIME_APPLICATION_CONFIG = "application/x-config"
MIME_APPLICATION_MLMODEL = "application/x-mlmodel"
```

### Artifact 结构

一个完整的 OMLMD OCI Artifact 包含三层：

```
┌─────────────────────────────────────────┐
│ Manifest Config (application/x-config)  │ ← 指向主元数据文件
├─────────────────────────────────────────┤
│ Layer 1: model.file (application/x-mlmodel) │ ← ML 模型权重
├─────────────────────────────────────────┤
│ Layer 2: model_metadata.omlmd.json      │ ← JSON 格式元数据
│          (application/x-config)         │
├─────────────────────────────────────────┤
│ Layer 3: model_metadata.omlmd.yaml      │ ← YAML 格式元数据
│          (application/x-config)         │
└─────────────────────────────────────────┘
```

## 架构组件

OMLMD 由以下核心组件构成：

| 模块 | 职责 |
|---|---|
| `ModelMetadata` | 元数据数据类，支持 JSON/YAML 双格式序列化 |
| `OMLMDRegistry` | 扩展 oras-py 的注册表客户端，支持按媒体类型过滤下载 |
| `Helper` | 高层 API 门面，封装推送/拉取/爬取等常用操作 |
| `Listener` | 观察者模式接口，用于监听推送事件 |
| `CLI` | 基于 Click + Cloup 的命令行界面 |

## 支持的注册表

OMLMD 基于 oras-py，理论上兼容所有符合 OCI Distribution Spec 的注册表，包括：
- Distribution Registry（开源参考实现）
- Quay
- zot
- Docker Registry
- 云厂商注册表（AWS ECR、GCP GAR、Azure ACR 等）

## 快速体验

安装后即可使用：

```bash
pip install omlmd
```

CLI 推送示例：

```bash
omlmd push localhost:8080/my-model:v1 model.joblib -m metadata.yaml
```

Python SDK 示例：

```python
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push("localhost:8080/my-model:v1", "model.joblib",
           name="My Model", author="Me", accuracy=0.95)
```

## 进一步阅读

- [ModelMetadata 双格式](/containers/omlmd/concepts/01-model-metadata) — 元数据结构与序列化机制
- [Helper 类与 Listener 模式](/containers/omlmd/concepts/02-helpers-listener) — 高层 API 与事件监听
- [OMLMDRegistry 扩展](/containers/omlmd/concepts/03-registry) — oras-py 扩展实现
