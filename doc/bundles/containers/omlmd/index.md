---
type: bundle
okf_version: "0.2"
scope: omlmd
name: omlmd
version: "0.1.6"
source: https://github.com/containers/omlmd
description: OMLMD——利用 OCI Artifact 和容器注册表存储、分发 ML 模型与元数据的 Python SDK 和 CLI 工具链
---

# OMLMD

**OMLMD（OCI Artifact for ML model & metadata）** 是 containers 组织开发的开源工具链，提供蓝图、模式和工具集（Python SDK + CLI），利用 OCI Artifact 规范和容器注册表生态来存储、版本化和分发 ML 模型及其元数据。

- **版本**：0.1.6
- **作者**：Matteo Mortari (matteo.mortari@gmail.com)
- **许可证**：Apache-2.0
- **Python 支持**：3.9、3.10、3.11、3.12
- **核心依赖**：oras >= 0.2.23, < 0.3.0、pyyaml ^6.0.1、click ^8.1.7、cloup ^3.0.5

## 核心特性

- **标准 OCI Artifact**：将模型和元数据打包为标准 OCI Artifact，兼容 Docker Registry、Quay、zot、Distribution Registry 等
- **双格式元数据**：同时推送 JSON 和 YAML 两种格式的元数据，兼顾机器处理和人类可读性
- **媒体类型分层**：使用 `application/x-mlmodel` 标识模型层，`application/x-config` 标识元数据层，支持按类型过滤下载
- **双接口**：提供 Click + Cloup 构建的 CLI 和简洁的 Python SDK
- **观察者模式**：支持 Listener 监听器扩展，可自定义推送事件处理
- **批量爬取**：crawl 命令批量获取多个模型版本元数据，配合 jq 灵活查询
- **自定义属性**：customProperties 支持任意扩展元数据（指标、参数、许可证等）

## 快速开始

### 安装

```bash
pip install omlmd
```

### Python SDK 推送

```python
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push(
    "localhost:5000/ml/model:v1",
    "model.joblib",
    name="Iris Classifier",
    author="John Doe",
    model_format_name="sklearn",
    accuracy=0.97,
    license="Apache-2.0"
)
```

### CLI 推送

```bash
omlmd push --plain-http localhost:5000/ml/model:v1 model.joblib -m metadata.yaml
```

### 拉取模型

```python
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.pull("localhost:5000/ml/model:v1", outdir="./models")

# 仅拉取模型文件，跳过元数据
omlmd.pull("localhost:5000/ml/model:v1", outdir="./models",
           media_types=["application/x-mlmodel"])
```

### 批量爬取元数据

```python
crawl_result = omlmd.crawl([
    "localhost:5000/ml/model:v1",
    "localhost:5000/ml/model:v2",
    "localhost:5000/ml/model:v3"
])
```

## 文档导航

### 核心概念

- [介绍](/containers/omlmd/concepts/00-introduction) — OMLMD 定位、OCI Artifact 媒体类型、架构组件概览
- [ModelMetadata 双格式](/containers/omlmd/concepts/01-model-metadata) — 元数据结构、JSON/YAML/注解三种序列化格式、文件反序列化
- [Helper 类与 Listener 模式](/containers/omlmd/concepts/02-helpers-listener) — 高层 API 门面、push/pull/get_config/crawl 流程、观察者事件机制
- [OMLMDRegistry 扩展](/containers/omlmd/concepts/03-registry) — oras-py 扩展实现、按媒体类型过滤下载、配置层获取、OCI Manifest 结构

### API 参考

- [README 原始参考](/containers/omlmd/references/readme-source) — 项目概述、安装、官方示例
- [ModelMetadata 源码参考](/containers/omlmd/references/model-metadata-source) — ModelMetadata 类完整源码、字段说明、序列化方法
- [Provider 源码参考](/containers/omlmd/references/provider-source) — OMLMDRegistry 类实现、download_layers/get_config 方法

### 使用示例

- [CLI 推送模型元数据](/containers/omlmd/examples/01-cli-push) — CLI 完整工作流、push/pull/get config/crawl 命令详解、本地注册表测试、常见问题
- [Python SDK 自定义扩展](/containers/omlmd/examples/02-python-custom) — Python SDK 高级用法、自定义 Listener（日志/指标）、批量爬取与 jq 查询、scikit-learn 集成、自定义 Registry 扩展

## 目录结构

```
omlmd/
├── concepts/              # 核心概念（4 篇）
│   ├── 00-introduction.md
│   ├── 01-model-metadata.md
│   ├── 02-helpers-listener.md
│   ├── 03-registry.md
│   └── index.md
├── examples/              # 使用示例（2 篇）
│   ├── 01-cli-push.md
│   ├── 02-python-custom.md
│   └── index.md
├── references/            # 参考资料（3 篇）
│   ├── readme-source.md
│   ├── model-metadata-source.md
│   ├── provider-source.md
│   └── index.md
├── index.md               # 本文件
└── log.md                 # 生成日志
```

## 项目链接

| 资源 | 链接 |
|---|---|
| GitHub 仓库 | https://github.com/containers/omlmd |
| PyPI | https://pypi.org/project/omlmd |
| 官方文档 | https://containers.github.io/omlmd |
| YouTube 教程 | https://www.youtube.com/playlist?list=PLdbdefeRIj9SRbg6Hkr15GeyPH0qpk_ww |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
