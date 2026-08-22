---
type: reference
title: "serialization.py/external_data_helper.py/numpy_helper.py：序列化与外部数据"
description: "load/save API、_Registry 注册表架构、四种序列化器、2GiB 限制、外部数据机制、三层安全防御、numpy_helper 张量转换"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/__init__.py"
    facts: [F-043, F-044, F-045, F-080, F-081]
  - path: "external/libs/models/onnx/onnx/onnx/serialization.py"
    facts: [F-039, F-040, F-041, F-042]
  - path: "external/libs/models/onnx/onnx/onnx/external_data_helper.py"
    facts: [F-073]
  - path: "external/libs/models/onnx/onnx/onnx/numpy_helper.py"
    facts: [F-075]
---

# serialization.py/external_data_helper.py/numpy_helper.py：序列化与外部数据

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnx/__init__.py` | Python 模块 | load_model/save_model 顶层 API、向后兼容别名、__repr__ 覆写 |
| `onnx/serialization.py` | Python 模块 | _Registry 注册表、四种序列化器实现 |
| `onnx/external_data_helper.py` | Python 模块 | 外部数据加载/保存、三层安全防御 |
| `onnx/numpy_helper.py` | Python 模块 | TensorProto ↔ numpy 数组转换、外部数据支持、亚字节类型解包 |

## 关键事实登记

### F-039：_Registry 注册表架构

**信源**：`onnx/serialization.py` L51-L91

```python
class _Registry:
    def __init__(self):
        self._serializers: dict[str, ProtoSerializer] = {}
        self._extension_to_format: dict[str, str] = {}

    def register(self, serializer: ProtoSerializer) -> None: ...
    def get(self, fmt: str) -> ProtoSerializer: ...
    def get_format_from_file_extension(self, ext: str) -> str | None: ...
```

- `_serializers`：格式名 → 序列化器对象映射
- `_extension_to_format`：文件扩展名 → 格式名映射
- 支持通过 `register()` 方法扩展自定义序列化格式

### F-040：四种内置序列化器

**信源**：`onnx/serialization.py` L94-L212

| 格式名 | 序列化器类 | 扩展名 | 说明 |
|--------|-----------|--------|------|
| protobuf | _ProtobufSerializer | .onnx, .pb | 标准二进制 protobuf 格式（默认） |
| textproto | _TextProtoSerializer | .txtpb, .textproto, .prototxt, .pbtxt | Protobuf 文本格式 |
| json | _JsonSerializer | .json, .onnxjson | JSON 格式（通过 protobuf json_format） |
| onnxtxt | _TextualSerializer | .onnnxtxt, .onnxtext | ONNX 自定义文本格式（实验性） |

所有序列化器在模块加载时通过 `_registry.register()` 自动注册。

### F-041：_ProtobufSerializer 的 2GiB 限制检查

**信源**：`onnx/serialization.py` L100-L110

```python
def serialize_proto(self, proto: Message) -> bytes:
    if proto.ByteSize() > MAXIMUM_PROTOBUF:
        raise ValueError(
            "Message exceeds ... protobuf's hard limit of 2GB. "
            "Please use save_as_external_data..."
        )
    return proto.SerializeToString()
```

序列化前检查 proto 字节大小，超过 2GiB 时抛出 ValueError，提示使用外部数据。

### F-042：_TextualSerializer 实验性警告

**信源**：`onnx/serialization.py` L183-L204

_TextualSerializer 反序列化时：
1. 发出 `UserWarning` 警告该格式为实验性
2. 根据 proto 类型分别调用解析器：
   - ModelProto → `onnx.parser.parse_model`
   - GraphProto → `onnx.parser.parse_graph`
   - FunctionProto → `onnx.parser.parse_function`
   - NodeProto → `onnx.parser.parse_node`

### F-043：load_model 函数

**信源**：`onnx/__init__.py` L210-L239

```python
def load_model(
    f: IO[bytes] | str | os.PathLike,
    format: str | None = None,
    load_external_data: bool = True,
) -> ModelProto:
```

- 支持 file-like 对象、字符串路径、PathLike 对象
- `format` 未指定时从文件扩展名推断，无法推断默认为 "protobuf"
- `load_external_data=True` 时自动从模型所在目录加载外部张量数据

### F-044：save_model 函数

**信源**：`onnx/__init__.py` L299-L349

```python
def save_model(
    proto: ModelProto,
    f: IO[bytes] | str | os.PathLike,
    format: str | None = None,
    save_as_external_data: bool = False,
    all_tensors_to_one_file: bool = True,
    location: str | None = None,
    size_threshold: int = 1024,
    convert_attribute: bool = False,
) -> None:
```

- `save_as_external_data=True`：将张量数据序列化到外部文件
- `all_tensors_to_one_file=True`：所有张量保存到单个外部文件
- `size_threshold=1024`：数据大小 >= 阈值（字节）时才转为外部数据
- `location`：外部数据文件名（默认模型名+.data）

### F-045：向后兼容别名

**信源**：`onnx/__init__.py` L372-L375

```python
load = load_model
load_from_string = load_model_from_string
save = save_model
```

### F-073：external_data_helper 三层安全防御

**信源**：`onnx/external_data_helper.py` L35-L57；L60-L100

第一层——属性白名单：
```python
_ALLOWED_EXTERNAL_DATA_KEYS = {"location", "offset", "length", "checksum", "basepath"}
```
忽略未知键，防止注入攻击。

第二层——参数验证：
`ExternalDataInfo.__init__` 验证 `offset` 和 `length` 为非负整数。

第三层——文件大小验证：
`load_external_data_for_tensor` 验证文件实际大小 >= offset + length，防止越界读取。

### F-075：numpy_helper.to_array 张量转换

**信源**：`onnx/numpy_helper.py` L187-L298

`to_array()` 函数：
1. 检测 `uses_external_data`，若使用外部数据则调用 `load_external_data_for_tensor` 加载
2. 有 `raw_data` 时：按小端序解释字节，大端系统上自动 byteswap
3. 无 `raw_data` 时：从类型特定存储字段（float_data/int32_data等）读取
4. 支持 4-bit 类型（UINT4/INT4）解包：每字节拆分为2个4位值
5. 支持 2-bit 类型（UINT2/INT2）解包：每字节拆分为4个2位值

### F-080：OperatorStatus 常量

**信源**：`onnx/__init__.py` L21-L22

```python
EXPERIMENTAL = 0
STABLE = 1
```

### F-081：__repr__ 覆写

**信源**：`onnx/__init__.py` L378-L470

- ModelProto 的 `__repr__` 显示：ir_version、opset_import（显示为 `{domain: version}` 字典）、domain、producer_name、producer_version、graph 节点数量、functions 数量
- GraphProto 的 `__repr__` 显示：name、inputs/outputs/initializers/nodes/value_info 数量
