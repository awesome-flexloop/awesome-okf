---
type: concept
scope: omlmd
name: model-metadata
version: "0.1.6"
source: https://github.com/containers/omlmd/blob/main/omlmd/model_metadata.py
description: ModelMetadata 双格式（JSON+YAML）序列化机制
---

# ModelMetadata 双格式

`ModelMetadata` 是 omlmd 的核心数据类，使用 Python `@dataclass` 定义，支持 JSON 和 YAML 双格式序列化，满足不同场景的使用需求。

## 数据结构

### 字段定义

```python
from dataclasses import dataclass, field
from typing import Any

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

### 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `str \| None` | 模型名称 |
| `description` | `str \| None` | 模型描述 |
| `author` | `str \| None` | 作者信息 |
| `customProperties` | `dict[str, Any] \| None` | 自定义属性字典，用于存储任意扩展元数据（如 accuracy、license 等） |
| `uri` | `str \| None` | 模型 URI |
| `model_format_name` | `str \| None` | 模型格式名称（如 "sklearn"、"onnx"、"pytorch"） |
| `model_format_version` | `str \| None` | 模型格式版本 |

所有字段均为可选，默认为 `None`，`customProperties` 默认为空字典。

## 序列化机制

ModelMetadata 提供三种序列化输出格式：

### 1. JSON 格式

`to_json()` 方法输出带缩进的 JSON 字符串：

```python
def to_json(self) -> str:
    return json.dumps(self.to_dict(), indent=4)
```

示例输出：

```json
{
    "name": "Iris Classifier",
    "description": "A simple sklearn classifier for Iris dataset",
    "author": "John Doe",
    "customProperties": {
        "accuracy": 0.97,
        "license": "Apache-2.0"
    },
    "uri": null,
    "model_format_name": "sklearn",
    "model_format_version": "1.3.0"
}
```

### 2. YAML 格式

`to_yaml()` 方法输出 YAML 字符串：

```python
def to_yaml(self) -> str:
    return yaml.dump(self.to_dict(), default_flow_style=False)
```

示例输出：

```yaml
name: Iris Classifier
description: A simple sklearn classifier for Iris dataset
author: John Doe
customProperties:
  accuracy: 0.97
  license: Apache-2.0
uri: null
model_format_name: sklearn
model_format_version: 1.3.0
```

### 3. OCI 注解格式

`to_annotations_dict()` 方法将元数据转换为 OCI 注解字典，用于写入 OCI Manifest 的 annotations 字段：

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

**关键设计**：
- 字符串值直接作为注解值
- `None` 值跳过
- 非字符串值（如 dict、number）序列化为 JSON，并添加 `+json` 后缀标记（遵循 OCI 注解约定）

示例输出：

```python
{
    "name": "Iris Classifier",
    "description": "A simple sklearn classifier for Iris dataset",
    "author": "John Doe",
    "customProperties+json": "{\"accuracy\": 0.97, \"license\": \"Apache-2.0\"}",
    "model_format_name": "sklearn",
    "model_format_version": "1.3.0"
}
```

### 4. 字典格式

`to_dict()` 方法使用 `dataclasses.asdict()` 转换为普通字典：

```python
def to_dict(self) -> dict[str, Any]:
    return asdict(self)
```

## 反序列化机制

### 从 JSON 反序列化

```python
@staticmethod
def from_json(json_str: str) -> "ModelMetadata":
    data = json.loads(json_str)
    return ModelMetadata(**data)
```

### 从 YAML 反序列化

```python
@staticmethod
def from_yaml(yaml_str: str) -> "ModelMetadata":
    data = yaml.safe_load(yaml_str)
    return ModelMetadata(**data)
```

### 从字典反序列化

`from_dict()` 方法具有智能字段处理能力：未知字段自动归入 `customProperties`：

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

这意味着在推送时可以直接传递任意关键字参数，未定义的字段会自动成为自定义属性：

```python
omlmd.push("localhost:8080/model:v1", "model.joblib",
           name="My Model",
           accuracy=0.95,        # 自动进入 customProperties
           license="MIT")       # 自动进入 customProperties
```

## 空值检查

`is_empty()` 方法检查元数据是否为空（用于判断是否需要复用现有元数据文件）：

```python
def is_empty(self) -> bool:
    return all(getattr(self, f.name) is None for f in fields(ModelMetadata) if f.name != "customProperties") and not self.customProperties
```

即：所有标准字段均为 `None`，且 `customProperties` 为空字典时才视为空。

## 文件反序列化

`deserialize_mdfile()` 函数提供自动格式检测的文件反序列化：

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

**策略**：先尝试 JSON 解析，失败则尝试 YAML 解析，都失败则抛出异常。CLI 中使用此函数读取 `-m/--metadata` 参数指定的元数据文件。

## 双格式设计考量

为什么同时推送 JSON 和 YAML 两种元数据文件？

1. **兼容性**：不同工具偏好不同格式——jq 等工具天然支持 JSON，人类编辑更偏好 YAML
2. **互操作性**：两种格式内容完全一致，消费端可以任选其一
3. **约定优于配置**：文件名固定为 `model_metadata.omlmd.json` 和 `model_metadata.omlmd.yaml`，无需额外协商

## 使用示例

创建和序列化元数据：

```python
from omlmd.model_metadata import ModelMetadata

md = ModelMetadata(
    name="Iris Classifier",
    author="John Doe",
    model_format_name="sklearn",
    model_format_version="1.3.0",
    customProperties={"accuracy": 0.97, "license": "Apache-2.0"}
)

print("JSON:")
print(md.to_json())

print("\nYAML:")
print(md.to_yaml())

print("\nAnnotations:")
print(md.to_annotations_dict())
```

从文件加载：

```python
from omlmd.model_metadata import deserialize_mdfile

data = deserialize_mdfile("metadata.yaml")
md = ModelMetadata.from_dict(data)
```
