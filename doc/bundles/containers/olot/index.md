---
okf_version: "0.2"
type: Index
title: olot - OCI Layers On Top
description: olot 是一个 Python 工具，用于向 OCI 兼容镜像追加文件层，特别适用于 KServe ModelCar ML 模型打包
tags: [olot, oci, containers, modelcar, kserve, ml]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: facts
    resource: "file:///d:/spaces/SpecWeave/.trae/specs/containers-okf-wiki/facts-olot.md"
    title: "olot 项目事实清单"
  - id: readme
    resource: /bundles/containers/olot/references/readme-source.md
    title: "olot 项目 README 信源"
---

# olot - OCI Layers On Top

**olot**（"oci layers on top"）是一个轻量级 Python 工具，用于向 OCI（Open Container Initiative）兼容镜像追加文件层。它是 KServe ModelCar 标准的参考实现，让 ML 模型打包无需 Docker 环境，直接操作标准 OCI image layout。

- **版本**：1.2.2
- **Python 要求**：>= 3.10
- **PyPI**：[https://pypi.org/p/olot](https://pypi.org/p/olot)
- **核心依赖**：click, pydantic
- **支持后端**：skopeo CLI、oras cp CLI、oras-py（纯 Python）

## 快速开始

### 安装

```bash
pip install olot

# 包含纯 Python 后端（无外部工具依赖）
pip install olot[oras-py]
```

### CLI 三步打包 ModelCar

```bash
# 1. 拉取基础镜像
skopeo copy docker://quay.io/mmortari/hello-world-wait:latest oci:download:latest

# 2. 添加模型层和 ModelCarD
olot download --modelcard README.md model.joblib

# 3. 推送镜像
skopeo copy oci:download:latest docker://quay.io/your/model:v1
```

### Python API 示例

```python
from olot.basics import oci_layers_on_top
from olot.backend.skopeo import skopeo_pull, skopeo_push

skopeo_pull("quay.io/mmortari/hello-world-wait:latest", "./download")
oci_layers_on_top("./download", ["model.joblib"], modelcard="README.md")
skopeo_push("./download", "quay.io/your/model:v1")
```

## 文档导航

### [概念文档 Concepts](/bundles/containers/olot/concepts/index.md)

按学习路径排列的核心概念：

| 主题 | 说明 |
|------|------|
| [olot 定位与 ModelCar 标准](/bundles/containers/olot/concepts/00-introduction.md) | 项目介绍、解决的问题、ModelCar 标准 |
| [OCI 层操作与四元组注解](/bundles/containers/olot/concepts/01-oci-layers.md) | OCI layout 结构、层创建流程、四元组注解机制 |
| [后端抽象层](/bundles/containers/olot/concepts/02-backends.md) | skopeo/oras/oras-py 三种后端对比与 API |
| [Python API 编程](/bundles/containers/olot/concepts/03-python-api.md) | 完整的 Python API 参数详解、枚举、辅助函数 |

### [示例文档 Examples](/bundles/containers/olot/examples/index.md)

可直接复制使用的实战示例：

| 示例 | 说明 |
|------|------|
| [命令行基本使用](/bundles/containers/olot/examples/01-cli-usage.md) | CLI 完整工作流，含验证步骤和常见问题 |
| [Python API 打包模型](/bundles/containers/olot/examples/02-python-api.md) | Python 脚本集成，含 skopeo/oras-py 两种后端、自动后端检测、异常处理 |

### [信源 References](/bundles/containers/olot/references/index.md)

所有文档内容的可验证信源：

| 信源 | 内容 |
|------|------|
| [readme-source.md](/bundles/containers/olot/references/readme-source.md) | 项目官方 README 摘要 |
| [oci-source.md](/bundles/containers/olot/references/oci-source.md) | OCI 层操作、四元组注解、MediaType 源码 |
| [backend-source.md](/bundles/containers/olot/references/backend-source.md) | 三种后端实现的函数签名和说明 |

## 核心特性

- ✅ **无需 Docker daemon**：直接操作文件系统上的 OCI layout
- ✅ **多后端支持**：skopeo CLI、oras cp CLI、纯 Python oras-py
- ✅ **保留目录结构**：`--root-dir` 参数保留子目录层级
- ✅ **层内容注解**：每个层自动添加四元组注解记录原始文件元数据
- ✅ **ModelPack 支持**：可生成 ModelPack manifest 用于多架构索引
- ✅ **Docker 格式兼容**：自动转换 Docker distribution manifest
- ✅ **CLI + Python API 双模式**：既可以命令行使用，也可以代码集成

## 适用场景

- 在 CI/CD 流水线中自动打包 ML 模型
- 没有 Docker 环境的轻量级/受限环境
- 需要程序化控制镜像构建过程
- KServe ModelCar 模式的模型发布
- 向任意 OCI 镜像追加文件（不仅限于 ML 模型）

## 项目结构

```
olot/
├── olot/                    # 主包
│   ├── __init__.py
│   ├── basics.py            # 核心函数 oci_layers_on_top()
│   ├── cli.py               # Click CLI 入口
│   ├── constants.py         # 层注解四元组常量
│   ├── enums.py             # 枚举类型定义
│   ├── oci_artifact.py      # OCI artifact 支持
│   ├── backend/             # 后端抽象层
│   │   ├── skopeo.py        # skopeo CLI 后端
│   │   ├── oras_py.py       # oras-py Python 后端
│   │   └── oras_cp.py       # oras cp CLI 后端
│   ├── oci/                 # OCI 数据结构
│   │   ├── oci_common.py    # MediaType 定义
│   │   ├── oci_config.py    # Config 模型
│   │   ├── oci_image_index.py    # Image Index
│   │   ├── oci_image_layout.py   # Layout 验证
│   │   └── oci_image_manifest.py # Image Manifest
│   ├── modelpack/           # ModelPack 支持
│   ├── dockerdist/          # Docker distribution 格式转换
│   └── utils/               # 工具函数
├── tests/                   # 测试
├── e2e/                     # 端到端测试
├── docs/                    # 项目文档
├── README.md
├── pyproject.toml
└── Makefile
```

## 更新日志

完整变更记录见 [log.md](/bundles/containers/olot/log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
