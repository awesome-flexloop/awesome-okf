---
type: concept
title: "序列化/反序列化与外部数据"
description: "_Registry 注册表架构、四种序列化格式、2GiB protobuf 限制、外部数据机制、三层安全防御、load/save API 用法"
sources:
  references: [../references/serialization.md]
  facts: [F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-011, F-012, F-073, F-075]
---

# 序列化/反序列化与外部数据

## 核心理解

ONNX 的序列化系统采用**注册表架构**，通过可扩展的 _Registry 管理多种格式。标准 protobuf 二进制格式是唯一强制支持的交换格式，但 ONNX 也内置了 textproto、JSON 和实验性 onnxtxt 格式。2 GiB 的 protobuf 硬限制通过外部数据机制突破——大模型的张量数据存储在模型文件外的独立文件中，通过三层安全防御防止路径遍历攻击。

## 机制详解

### _Registry 注册表架构

序列化通过 `_Registry` 类实现可扩展的格式管理（F-039）：

```
┌─────────────────────────────────────────────┐
│               _Registry (单例)              │
│                                             │
│  _serializers: {                           │
│    "protobuf"  → _ProtobufSerializer,       │
│    "textproto" → _TextProtoSerializer,      │
│    "json"      → _JsonSerializer,           │
│    "onnxtxt"   → _TextualSerializer         │
│  }                                          │
│                                             │
│  _extension_to_format: {                   │
│    ".onnx"    → "protobuf",                 │
│    ".pb"      → "protobuf",                 │
│    ".txtpb"   → "textproto",                │
│    ".json"    → "json",                     │
│    ".onnxtxt" → "onnxtxt",                  │
│    ...                                      │
│  }                                          │
└─────────────────────────────────────────────┘
         ↑ register()
         │
  ProtoSerializer 子类
```

核心方法：
- `register(serializer)`：注册新的序列化器（自动关联扩展名）
- `get(format)`：按格式名获取序列化器
- `get_format_from_file_extension(ext)`：从文件扩展名推断格式名

这种设计允许第三方扩展自定义序列化格式，而无需修改核心代码。

### 四种内置序列化格式

| 格式 | 类 | 扩展名 | 说明 | 适用场景 |
|------|-----|--------|------|---------|
| protobuf | _ProtobufSerializer | .onnx, .pb | 标准二进制 protobuf 格式 | 生产部署、框架交换（默认格式） |
| textproto | _TextProtoSerializer | .txtpb, .textproto, .prototxt, .pbtxt | Protobuf 文本格式 | 调试、人工查看（体积大） |
| json | _JsonSerializer | .json, .onnxjson | JSON 格式（通过 protobuf json_format） | Web应用、日志记录 |
| onnxtxt | _TextualSerializer | .onnxtxt, .onnxtext | ONNX 自定义文本格式（实验性） | 实验性功能，不推荐生产 |

**重要警告**：onnxtxt 格式在序列化/反序列化时会发出实验性警告（F-042），API 可能变更，不应用于生产环境。

### load_model：模型加载

```python
def load_model(
    f: Union[IO[bytes], str, os.PathLike],
    format: Optional[str] = None,
    load_external_data: bool = True,
) -> ModelProto:
```

参数说明（F-043）：
- `f`：file-like 对象、文件路径字符串、或 PathLike 对象
- `format`：格式名，未指定时从文件扩展名推断，无法推断时默认为 "protobuf"
- `load_external_data`：是否自动加载外部数据文件中的张量数据（默认 True）

```python
import onnx

# 从文件加载（自动推断格式）
model = onnx.load("model.onnx")

# 从文件加载（指定格式）
model = onnx.load("model.txtpb", format="textproto")

# 从字节流加载
with open("model.onnx", "rb") as f:
    model = onnx.load(f)

# 不加载外部数据（仅加载结构）
model = onnx.load("large_model.onnx", load_external_data=False)
```

**向后兼容别名**（F-045）：`onnx.load` = `onnx.load_model`。

### save_model：模型保存

```python
def save_model(
    proto: ModelProto,
    f: Union[IO[bytes], str, os.PathLike],
    format: Optional[str] = None,
    save_as_external_data: bool = False,
    all_tensors_to_one_file: bool = True,
    location: Optional[str] = None,
    size_threshold: int = 1024,
    convert_attribute: bool = False,
) -> None:
```

外部数据相关参数（F-044）：
- `save_as_external_data`：是否将张量数据保存到外部文件
- `all_tensors_to_one_file`：所有张量保存到单个外部文件（vs 每个张量一个文件）
- `location`：外部数据文件名（默认使用模型名+.data）
- `size_threshold`：数据大小 >= 阈值（字节）时才转为外部数据（默认 1024）

```python
import onnx

# 标准保存（单文件 .onnx，仅适用于 <2GiB 模型）
onnx.save(model, "model.onnx")

# 保存为外部数据格式（大模型必须）
onnx.save_model(
    model,
    "model_dir/model.onnx",
    save_as_external_data=True,
    all_tensors_to_one_file=True,
    location="model.weights",  # 权重文件名
    size_threshold=0,          # 0=所有张量都外部化
)

# 保存为其他格式
onnx.save(model, "model.json", format="json")
onnx.save(model, "model.pbtxt", format="textproto")
```

**向后兼容别名**：`onnx.save` = `onnx.save_model`。

### 2 GiB 硬限制

Protobuf 序列化有 2 GiB 硬限制（F-035, F-041）：

```python
MAXIMUM_PROTOBUF = 2147483647  # 2^31 - 1 bytes ≈ 2 GiB
```

当 protobuf 消息的字节大小超过此限制时：
- 序列化时抛出 `ValueError`，提示使用 `save_as_external_data`
- 这是 protobuf 库本身的限制，不是 ONNX 特有的
- 大型模型（如 LLM、大型视觉模型）几乎总是超过此限制，必须使用外部数据

### 外部数据机制

当 `data_location=EXTERNAL` 时，张量数据存储在 protobuf 消息外部（F-011, F-012）：

```
model.onnx (protobuf, 结构定义)
├── graph.node[]        ← 计算节点（始终在onnx文件内）
├── graph.input[]       ← 输入定义（始终在onnx文件内）
├── graph.output[]      ← 输出定义（始终在onnx文件内）
└── graph.initializer[] ← 权重张量
    ├── data_location = EXTERNAL
    ├── external_data:
    │   ├── location = "model.weights"
    │   ├── offset = 0
    │   └── length = 1048576
    └── (无 float_data/int32_data/raw_data)

model.weights (原始二进制, 张量数据)
├── [0 ~ 1048576): tensor1 的 raw_data
├── [1048576 ~ ...):   tensor2 的 raw_data
└── ...
```

external_data 字段的键值对（F-011）：
- `"location"`（必需）：外部数据文件的相对路径
- `"offset"`（可选）：数据在文件中的字节偏移量
- `"length"`（可选）：数据字节长度
- `"checksum"`（可选）：数据校验和

### 外部数据三层安全防御

加载外部数据时，`external_data_helper.py` 实现了三层安全检查（F-073）：

```
┌─────────────────────────────────────────────┐
│ 第一层：属性白名单                          │
│ _ALLOWED_EXTERNAL_DATA_KEYS = {            │
│   "location", "offset", "length",          │
│   "checksum", "basepath"                   │
│ }                                          │
│ → 忽略未知键，防止属性注入攻击              │
├─────────────────────────────────────────────┤
│ 第二层：参数类型验证                        │
│ ExternalDataInfo.__init__:                 │
│ → offset 和 length 必须为非负整数           │
│ → 防止负偏移/长度导致越界读取               │
├─────────────────────────────────────────────┤
│ 第三层：文件大小验证                        │
│ load_external_data_for_tensor:             │
│ → 验证文件实际大小 >= offset + length       │
│ → 防止读取超出文件范围的数据                │
└─────────────────────────────────────────────┘

C++ Checker 额外防御（verify_path_containment）：
→ 路径规范化（weakly_canonical）
→ 禁止路径包含 ".." 组件
→ 验证路径不超出模型目录
→ 防止路径遍历攻击（../../../etc/passwd）
```

### numpy_helper.to_array：张量转 numpy

```python
from onnx import numpy_helper

# TensorProto → numpy array
arr = numpy_helper.to_array(tensor_proto)
```

`to_array()` 的完整行为（F-075）：
1. 检测 `data_location == EXTERNAL`，若使用外部数据则自动加载
2. 有 `raw_data` 时：按小端序解释字节，大端系统自动 byteswap
3. 无 `raw_data` 时：从类型特定存储字段读取
4. 4-bit 类型解包：每字节拆分为2个4位值
5. 2-bit 类型解包：每字节拆分为4个2位值

反向转换：
```python
# numpy array → TensorProto
tensor = numpy_helper.from_array(arr, name="my_tensor")
```

### __repr__ 覆写

ModelProto 和 GraphProto 覆写了 `__repr__` 方法（F-081），提供人类可读的摘要信息：

```python
print(model)
# 输出：
# ir_version: 8
# opset_import: {"": 15}
# producer_name: "pytorch"
# producer_version: "2.0"
# graph: [3 inputs, 1 outputs, 120 nodes, 50 initializers]
# functions: [0 functions]
```

## 格式选择决策树

```
保存模型
  │
  ├── 模型大小 < 2 GiB？
  │     ├── 是 → save_as_external_data=False (.onnx)
  │     └── 否 → 必须使用外部数据 ↓
  │
  ├── 需要人工阅读/调试？
  │     ├── 是 → format="textproto" 或 "json"
  │     └── 否 → format="protobuf"（默认）
  │
  └── 部署到生产环境？
        ├── 是 → 始终使用 protobuf 二进制格式（最小最快）
        └── 否 → 根据需要选择
```

## 关键洞察/反常识

1. **大模型不能用单文件 .onnx**：2 GiB 限制是 protobuf 的硬限制，不是建议。超过 2 GiB 的模型保存时必然失败，必须使用外部数据。
2. **外部数据路径是相对路径**：location 必须是相对于模型文件的路径，移动模型目录时需要同时移动 .onnx 文件和外部数据文件。
3. **load_external_data 默认 True**：加载时默认读取外部数据，如果外部数据文件不存在会报错。只检查模型结构时可设为 False。
4. **onnxtxt 是实验性的**：会发出警告，格式不稳定，不要在生产中使用。
5. **安全检查是强制的**：三层防御 + C++ 路径验证不能绕过，这是防止恶意模型文件读取任意文件的安全特性。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — TensorProto 的 external_data/data_location 字段定义
- [张量类型系统](02-tensor-type-system.md) — 七种存储字段和外部数据的关系
- [模型检查器 Checker](07-model-checker.md) — 外部数据路径安全验证
- [Python Helper API 详解](09-python-helpers.md) — make_tensor 的 raw_data 存储策略
- [模型加载、检查与形状推断](../examples/load-check-model.md) — load_model + check_model 完整流程
