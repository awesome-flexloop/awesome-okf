---
type: reference
title: "compose.py/parser.py/printer.py/version_converter.py/inliner.py：图组合、解析打印、版本转换与内联"
description: "merge_models/add_prefix 图组合、parse_model/parse_graph 文本解析、to_text 打印、convert_version 版本转换、inline_local_functions 函数内联"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/compose.py"
    facts: [F-065, F-066, F-067, F-068]
  - path: "external/libs/models/onnx/onnx/onnx/parser.py"
    facts: [F-069]
  - path: "external/libs/models/onnx/onnx/onnx/parser.cc"
    facts: []
  - path: "external/libs/models/onnx/onnx/onnx/printer.py"
    facts: [F-070]
  - path: "external/libs/models/onnx/onnx/onnx/version_converter.py"
    facts: [F-071]
  - path: "external/libs/models/onnx/onnx/onnx/inliner.py"
    facts: [F-076, F-077]
---

# compose.py/parser.py/printer.py/version_converter.py/inliner.py：图组合、解析打印、版本转换与内联

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnx/compose.py` | Python 模块 | 图组合：merge_models、add_prefix、add_prefix_graph |
| `onnx/parser.py` | Python 模块 | 文本解析：parse_model/parse_graph/parse_function/parse_node（委托 C++） |
| `onnx/parser.cc` | C++ 实现 | onnxtxt 格式的词法分析和语法解析 |
| `onnx/printer.py` | Python 模块 | 文本打印：to_text（委托 C++） |
| `onnx/version_converter.py` | Python 模块 | 版本转换：convert_version（委托 C++） |
| `onnx/inliner.py` | Python 模块 | 函数内联：inline_local_functions、inline_selected_functions |

## 关键事实登记

### F-065：merge_models 前提条件

**信源**：`onnx/compose.py` L353-L441

```python
def merge_models(model1: ModelProto, model2: ModelProto, ...) -> ModelProto:
```

合并两个模型的前提条件：
1. **ir_version 相同**：两个模型必须具有相同的 ir_version
2. **opset_import 兼容**：同一域的 opset 版本必须完全相同
3. **metadata_props 兼容**：同名 key 的值必须相同（不冲突）
4. **functions 不重名**：两个模型的局部函数不能有 (domain, name, overload) 三元组冲突

合并时合并两个模型的 graph：node、input、output、initializer、value_info、sparse_initializer 均合并。

### F-066：check_overlapping_names 名字冲突检测

**信源**：`onnx/compose.py` L22-L88；L200-L210

```python
def check_overlapping_names(
    g1: GraphProto, g2: GraphProto, ...
) -> list[str]:
```

`merge_graphs` 在连接两个图前调用此函数检查名字冲突：
- 检查 edge（节点输出名）冲突
- 检查 value_info 名冲突
- 检查 initializer 名冲突
- 检查 sparse_initializer 名冲突

存在冲突时抛出 ValueError，建议使用 `add_prefix` 为其中一个图添加前缀。

### F-067：add_prefix_graph 前缀添加与子图递归处理

**信源**：`onnx/compose.py` L445-L565

```python
def add_prefix_graph(
    graph: GraphProto,
    prefix: str,
    nodes: bool = True,
    edges: bool = True,
    inputs: bool = True,
    outputs: bool = True,
    initializers: bool = True,
    value_infos: bool = True,
    rename_edges: bool = True,
    inplace: bool = False,
) -> GraphProto:
```

关键行为：
- 可选择性地为 nodes、edges、inputs、outputs、initializers、value_infos 添加前缀
- **空名字不添加前缀**
- `rename_edges=True` 时重命名节点间连接的边名，但**跳过图输出名**（由 `rename_outputs` 参数单独处理）
- **递归处理子图属性**：当节点包含 `g`（GraphProto）或 `graphs`（GraphProto列表）类型的属性时，递归调用 add_prefix_graph

### F-068：add_prefix 模型级前缀添加

**信源**：`onnx/compose.py` L568-L620

```python
def add_prefix(
    model: ModelProto,
    prefix: str,
    rename_functions: bool = False,
    **kwargs: Any,
) -> ModelProto:
```

在 add_prefix_graph 基础上额外支持：
- `rename_functions` 参数：当为 True 时，对模型局部函数（functions 字段）的名字也添加前缀
- 其他 kwargs 传递给 add_prefix_graph

### F-069：Python parser 四个解析函数

**信源**：`onnx/parser.py` L14-L73

```python
def parse_model(text: str) -> ModelProto: ...
def parse_graph(text: str) -> GraphProto: ...
def parse_function(text: str) -> FunctionProto: ...
def parse_node(text: str) -> NodeProto: ...
```

所有函数的行为：
1. 委托给 C++ 解析器：`onnx.onnx_cpp2py_export.parser`
2. C++ 解析器返回三元组 `(success: bool, msg: str, proto_str: bytes)`
3. 解析失败时（success=False）抛出 ParseError 异常，msg 包含错误信息
4. 解析成功时，从 proto_str 反序列化为对应类型的 protobuf 对象

### F-070：printer.to_text 文本打印

**信源**：`onnx/printer.py` L10-L21

```python
def to_text(proto: Message) -> str:
```

根据 proto 类型分别调用 C++ 实现：
- ModelProto → `model_to_text`
- FunctionProto → `function_to_text`
- GraphProto → `graph_to_text`
- NodeProto → `node_to_text`

返回人类可读的 onnxtxt 格式字符串。

### F-071：version_converter.convert_version

**信源**：`onnx/version_converter.py` L17-L39

```python
def convert_version(model: ModelProto, target_version: int) -> ModelProto:
```

- 接受 ModelProto 和目标 opset 版本号（int）
- 将 ModelProto 序列化为字节串后委托给 C++ 实现：`onnx.onnx_cpp2py_export.version_converter.convert_version`
- C++ 端执行算子版本适配（opset adapter），将旧版本算子转换为新版本等价形式
- 返回新的 ModelProto

### F-076：inline_local_functions 递归内联

**信源**：`onnx/inliner.py` L11-L27

```python
def inline_local_functions(
    model: ModelProto,
    convert_version: bool = True,
) -> ModelProto:
```

- 将模型中所有对模型局部函数（model.functions）的调用递归内联展开
- `convert_version=True` 时在必要处进行版本转换以确保兼容性
- 内联后模型不再依赖 functions 字段（但 functions 字段保留）
- 递归处理：内联后新产生的函数调用也会被内联

### F-077：inline_selected_functions 选择性内联

**信源**：`onnx/inliner.py` L30-L60

```python
def inline_selected_functions(
    model: ModelProto,
    function_ids: list[tuple[str, str, str]] | None = None,
    exclude: bool = False,
    inline_schema_functions: bool = False,
) -> ModelProto:
```

- `function_ids`：`(domain, name, overload)` 三元组列表
- `exclude=False`（默认）：仅内联列表中指定的函数
- `exclude=True`：内联列表**外**的所有函数（即排除列表中的函数不内联）
- `inline_schema_functions`：是否内联 OpSchema 注册的函数体（非模型局部函数）
