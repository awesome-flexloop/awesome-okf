---
type: reference
scope: omlmd
name: model-metadata-source
version: "0.1.6"
source: https://github.com/containers/omlmd/blob/main/omlmd/model_metadata.py
description: ModelMetadata 类源码参考
---

# ModelMetadata 源码参考

`ModelMetadata` 是 omlmd 的核心数据类，用于表示 ML 模型元数据，支持 JSON 和 YAML 双格式序列化。

## 类定义

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Any

import yaml


@dataclass
class ModelMetadata:
    name: str | None = None
    description: str | None = None
    author: str | None = None
    customProperties: dict[str, Any] | None = field(default_factory=dict)
    uri: str | None = None
    model_format_name: str | None = None
    model_format_version: str | None = None
```

## 序列化方法

### to_json()

将元数据序列化为 JSON 字符串：

```python
def to_json(self) -> str:
    return json.dumps(self.to_dict(), indent=4)
```

### to_yaml()

将元数据序列化为 YAML 字符串：

```python
def to_yaml(self) -> str:
    return yaml.dump(self.to_dict(), default_flow_style=False)
```

### to_dict()

将元数据转换为字典：

```python
def to_dict(self) -> dict[str, Any]:
    return asdict(self)
```

### to_annotations_dict()

将元数据转换为 OCI 注解字典格式，非字符串值使用 `+json` 后缀标记：

```python
def to_annotations_dict(self) -> dict[str, str]:
    as_dict = self.to_dict()
    result = {}
    for k, v in as_dict.items():
        if isinstance(v, str):
            result[k] = v
        elif v is None:
            continue
        else:
            result[f"{k}+json"] = json.dumps(v)
    return result
```

## 反序列化方法

### from_json()

从 JSON 字符串创建 ModelMetadata：

```python
@staticmethod
def from_json(json_str: str) -> "ModelMetadata":
    data = json.loads(json_str)
    return ModelMetadata(**data)
```

### from_yaml()

从 YAML 字符串创建 ModelMetadata：

```python
@staticmethod
def from_yaml(yaml_str: str) -> "ModelMetadata":
    data = yaml.safe_load(yaml_str)
    return ModelMetadata(**data)
```

### from_dict()

从字典创建 ModelMetadata，未知字段自动归入 customProperties：

```python
@staticmethod
def from_dict(data: dict[str, Any]) -> "ModelMetadata":
    known_keys = {f.name for f in fields(ModelMetadata)}
    known_properties = {key: data.get(key) for key in known_keys if key in data}
    custom_properties = {
        key: value for key, value in data.items() if key not in known_keys
    }
    return ModelMetadata(**known_properties, customProperties=custom_properties)
```

## 辅助方法

### is_empty()

检查元数据是否为空：

```python
def is_empty(self) -> bool:
    return all(getattr(self, f.name) is None for f in fields(ModelMetadata) if f.name != "customProperties") and not self.customProperties
```

## 文件反序列化函数

### deserialize_mdfile()

从文件反序列化元数据，自动尝试 JSON 解析，失败则尝试 YAML 解析：

```python
def deserialize_mdfile(file):
    with open(file, "r") as file:
        content = file.read()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        pass

    raise ValueError(
        f"The file at {file} is neither a valid JSON nor a valid YAML file."
    )
```

## 常量定义

```python
FILENAME_METADATA_JSON = "model_metadata.omlmd.json"
FILENAME_METADATA_YAML = "model_metadata.omlmd.yaml"
MIME_APPLICATION_CONFIG = "application/x-config"
MIME_APPLICATION_MLMODEL = "application/x-mlmodel"
```
