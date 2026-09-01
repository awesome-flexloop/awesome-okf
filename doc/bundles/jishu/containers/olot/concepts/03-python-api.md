---
type: Concept
title: Python API 编程
description: 全面了解 olot 的 Python API，包括核心函数参数、枚举类型、模型提取函数等
tags: [python, api, programming, oci_layers_on_top, enums]
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
    title: "olot/basics.py"
  - id: enums
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/enums.py"
    title: "olot/enums.py"
  - id: cli
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/cli.py"
    title: "olot/cli.py"
---

# Python API 编程

olot 既可以作为 CLI 工具使用，也提供了完整的 Python API，可以直接集成到 Python 代码中。本文详细介绍所有公开 API 和编程模式。

## 安装

```bash
pip install olot

# 包含 oras-py 纯 Python 后端
pip install olot[oras-py]
```

## 核心函数：oci_layers_on_top()

这是 olot 最核心的函数，用于向 OCI layout 添加新的文件层。

### 函数签名

```python
from olot.basics import oci_layers_on_top

def oci_layers_on_top(
        ocilayout: str | os.PathLike,
        model_files: Sequence[os.PathLike],
        modelcard: os.PathLike | None = None,
        *,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        root_dir: str | os.PathLike | None = None,
        remove_originals: RemoveOriginals | None = None,
        add_modelpack: bool | None = None
) -> None
```

### 参数详解

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `ocilayout` | `str \| os.PathLike` | ✅ | - | OCI layout 目录路径 |
| `model_files` | `Sequence[os.PathLike]` | ✅ | - | 要添加为层的模型文件路径列表 |
| `modelcard` | `os.PathLike \| None` | ❌ | `None` | ModelCarD（README.md）路径 |
| `labels` | `dict[str, str] \| None` | ❌ | `None` | 添加到 OCI Image Config 的标签 |
| `annotations` | `dict[str, str] \| None` | ❌ | `None` | 添加到 OCI Image Manifest 的注解 |
| `root_dir` | `str \| os.PathLike \| None` | ❌ | `None` | 模型文件根目录，用于保留子目录结构 |
| `remove_originals` | `RemoveOriginals \| None` | ❌ | `None` | 添加后是否删除原始文件 |
| `add_modelpack` | `bool \| None` | ❌ | `None` | 是否添加 ModelPack manifest |

> **注意**：`*` 之后的参数（labels、annotations、root_dir 等）必须使用关键字参数传递。

### 参数使用细节

#### modelcard 参数

- 如果提供 modelcard，它会被 gzip 压缩后作为最后一层添加
- modelcard 层会自动标记 `io.opendatahub.modelcar.layer.type: modelcard` 注解
- manifest 中会添加 `io.opendatahub.layers.modelcard` 注解指向该层
- **重要**：不要将 modelcard 文件重复包含在 model_files 列表中，否则会产生重复层

#### root_dir 参数

这是一个容易踩坑的参数。当模型文件分布在子目录中时，必须使用 `root_dir`：

```python
# 不使用 root_dir：所有文件都平铺到 /models/ 下，同名文件会覆盖
model_files = [
    "./model/onnx/model.onnx",
    "./model/config.json"
]
# 结果：/models/model.onnx, /models/config.json（只有 basename）

# 使用 root_dir：保留子目录结构
model_files = [
    "./model/onnx/model.onnx",
    "./model/config.json"
]
oci_layers_on_top(
    ocilayout="./download",
    model_files=model_files,
    root_dir="./model"  # 关键！
)
# 结果：/models/onnx/model.onnx, /models/config.json
```

所有 model_files 必须位于 root_dir 目录下，否则会抛出 `ValueError`。

#### labels 参数

labels 会被添加到容器运行时配置中，可以通过 `docker inspect` 等工具查看：

```python
oci_layers_on_top(
    ocilayout="./download",
    model_files=["model.joblib"],
    labels={
        "org.opencontainers.image.title": "my-ml-model",
        "org.opencontainers.image.version": "1.0.0",
        "ml.framework": "scikit-learn",
        "ml.model-type": "classifier"
    }
)
```

#### annotations 参数

annotations 会被添加到每个架构的 OCI Image Manifest 上：

```python
oci_layers_on_top(
    ocilayout="./download",
    model_files=["model.joblib"],
    annotations={
        "io.opendatahub.model.name": "my-model",
        "io.opendatahub.model.version": "v1"
    }
)
```

注意：这与层的四元组注解不同——这是 manifest 级别的注解。

#### remove_originals 参数

控制是否在添加层后删除原始文件。使用枚举类型 `RemoveOriginals`：

```python
from olot.basics import RemoveOriginals

oci_layers_on_top(
    ocilayout="./download",
    model_files=["model.joblib"],
    remove_originals=RemoveOriginals.DEFAULT  # 只删除 model_files
    # 或 remove_originals=RemoveOriginals.ALL  # 包括 modelcard
)
```

> **警告**：当 `modelcard in model_files` 且设置了 `remove_originals` 时会抛出 ValueError，因为这会在处理 modelcard 之前删除它。

#### add_modelpack 参数

设置为 `True` 时，会为多架构镜像添加额外的 ModelPack manifest：

```python
oci_layers_on_top(
    ocilayout="./download",  # 必须是多架构（含 index）的 layout
    model_files=["model.joblib"],
    add_modelpack=True
)
```

**限制**：不能对单架构（只有 manifest，没有 index）的 OCI layout 添加 ModelPack，否则抛出 ValueError。如果已经存在 ModelPack manifest，此参数会被自动忽略并发出警告。

## 枚举类型

### RemoveOriginals

控制原始文件删除行为：

```python
from olot.enums import RemoveOriginals

RemoveOriginals.DEFAULT  # "default" - 只删除 model_files 中的文件
RemoveOriginals.ALL      # "all" - 包括 modelcard 也删除
```

### LayerInputType

标识输入类型（内部使用）：

```python
from olot.enums import LayerInputType

LayerInputType.FILE       # "file" - 输入是文件
LayerInputType.DIRECTORY  # "directory" - 输入是目录
```

### CustomStrEnum

自定义字符串枚举基类，提供 `values()` 类方法返回所有枚举值的列表：

```python
from olot.enums import CustomStrEnum

class MyEnum(CustomStrEnum):
    A = "a"
    B = "b"

MyEnum.values()  # ["a", "b"]
```

## 其他公开函数

### crawl_ocilayout_blobs_to_extract()

从已有的 ModelCar OCI 镜像中提取 `/models/` 目录下的内容。这是添加层的逆操作。

**函数签名：**
```python
def crawl_ocilayout_blobs_to_extract(
    ocilayout: Path,
    output_path: Path,
    tar_filter_dir: str = "/models"
) -> list[str]
```

**参数：**
- `ocilayout`：OCI layout 目录路径
- `output_path`：提取目标目录
- `tar_filter_dir`：要提取的目录前缀，默认为 `"/models"`

**返回值：** 提取出的文件路径列表

**示例：**
```python
from pathlib import Path
from olot.basics import crawl_ocilayout_blobs_to_extract

extracted = crawl_ocilayout_blobs_to_extract(
    Path("./download"),
    Path("./extracted-model"),
    tar_filter_dir="/models"
)
print(f"Extracted files: {extracted}")
```

**限制**：当前只支持根索引中只有一个 manifest 的 ModelCar 镜像。

### write_empty_config_in_ocilayoyt()

一个小工具函数，在 OCI layout 的 blobs 目录中写入空的 JSON config `{}`。用于规避 skopeo 无法读取内联空 config 的限制。

```python
from pathlib import Path
from olot.basics import write_empty_config_in_ocilayoyt

write_empty_config_in_ocilayoyt(Path("./new-layout"))
```

> **注意**：函数名中有个拼写错误（`ocilayoyt` 应为 `ocilayout`），这是源码中的实际命名，使用时注意。

## 日志控制

olot 使用标准 Python `logging` 模块。可以通过设置日志级别来获取详细的调试输出：

```python
import logging

# 启用 DEBUG 级别日志（同 CLI -v/--verbose）
logging.basicConfig(level=logging.DEBUG)

# 或者只启用 olot 的日志
logging.getLogger("olot").setLevel(logging.DEBUG)
```

DEBUG 级别会输出：
- 函数参数详情
- manifest 和 config 的哈希变更
- 每个层的处理过程
- 索引更新链路

## 异常类型

olot 主要抛出标准 Python 异常：

- `ValueError`：参数错误（如 model_file 不在 root_dir 下、单架构 layout 尝试 add_modelpack 等）
- `FileNotFoundError`：文件路径不存在
- `json.JSONDecodeError`：OCI layout 中的 JSON 文件损坏
- `pydantic.ValidationError`：manifest/config 数据结构不符合 OCI 规范

## 相关概念

- [后端抽象层](02-backends.md)：后端选择与 API
- [OCI 层操作与四元组注解](01-oci-layers.md)：层创建内部机制
- [Python API 打包模型](../examples/02-python-api.md)：完整的端到端示例
