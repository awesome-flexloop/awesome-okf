---
type: concept
title: "文本解析器与打印器"
description: "onnxtxt 文本格式、parse_model/parse_graph/parse_function/parse_node 解析函数、to_text 打印、TextualSerializer 实验性警告"
sources:
  references: [../references/compose-parser-printer.md, ../references/serialization.md]
  facts: [F-069, F-070, F-042]
---

# 文本解析器与打印器

## 核心理解

ONNX 提供了文本格式的解析和打印能力，使得模型可以用人类可读的文本形式表示和编辑。核心是 onnxtxt 格式——一种类 Python 语法的 ONNX 文本表示——以及对应的 parser（解析器）和 printer（打印器）。所有解析和打印功能在 Python 端都委托给 C++ 实现。需要注意的是 onnxtxt 格式目前是**实验性**的，API 和格式可能变更。

## 机制详解

### 四个解析函数

Python parser 模块提供四个解析函数，覆盖从单个节点到完整模型的不同粒度（F-069）：

```python
from onnx import parser

# 解析完整模型
model = parser.parse_model(text: str) -> ModelProto

# 解析计算图
graph = parser.parse_graph(text: str) -> GraphProto

# 解析函数定义
func = parser.parse_function(text: str) -> FunctionProto

# 解析单个节点
node = parser.parse_node(text: str) -> NodeProto
```

所有函数的工作方式：
1. 接收文本字符串
2. 委托给 C++ 解析器（`onnx.onnx_cpp2py_export.parser`）
3. C++ 返回三元组 `(success: bool, error_msg: str, proto_bytes: bytes)`
4. 失败时抛出 `ParseError` 异常，包含错误信息
5. 成功时从 proto_bytes 反序列化为对应类型的 protobuf 对象

### onnxtxt 文本格式

onnxtxt 格式使用类 Python 语法描述 ONNX 模型。简单示例：

```python
# 解析一个简单的计算图
graph_text = '''
<
  doc_string: "A simple linear model"
>
agraph (float[1,3] X, float[3,1] W, float[1,1] B) => (float[1,1] Y) {
    hidden = MatMul(X, W)
    Y = Add(hidden, B)
}
'''

graph = onnx.parser.parse_graph(graph_text)
```

格式要点：
- **图签名**：`agraph (输入) => (输出) { 节点列表 }`
- **输入/输出声明**：`类型[形状] 名字`，如 `float[1,3] X`
- **动态维度**：使用符号名，如 `float[N,3] X`
- **节点定义**：`输出 = OpType(输入1, 输入2)`
- **属性**：`输出 = OpType<attr_name=value>(输入)`
- **初始器**：可以在图体内使用 `initializer` 声明
- **元数据**：`< key: value >` 块放在定义前

### to_text 打印

```python
from onnx import printer

text = printer.to_text(proto) -> str
```

根据 proto 类型自动选择 C++ 打印函数（F-070）：

| proto 类型 | C++ 函数 |
|-----------|---------|
| ModelProto | model_to_text |
| GraphProto | graph_to_text |
| FunctionProto | function_to_text |
| NodeProto | node_to_text |

```python
import onnx

model = onnx.load("model.onnx")

# 打印完整模型
print(onnx.printer.to_text(model))

# 打印单个节点
node = model.graph.node[0]
print(onnn.printer.to_text(node))
```

### 序列化集成

onnxtxt 格式通过 _TextualSerializer 集成到序列化框架中（F-042）：

```python
# 保存为 onnxtxt 格式
onnx.save(model, "model.onnxtxt", format="onnxtxt")

# 从 onnxtxt 加载
model = onnx.load("model.onnxtxt", format="onnxtxt")
```

**实验性警告**：_TextualSerializer 反序列化时会发出 `UserWarning`，提示该格式是实验性的：
```
UserWarning: The onnxtxt format is experimental and may change in future versions.
```

### 错误处理

解析失败时会抛出 `onnx.parser.ParseError`，包含行号和错误描述：

```python
from onnx import parser

try:
    model = parser.parse_model(invalid_text)
except parser.ParseError as e:
    print(f"解析错误: {e}")
    # 输出示例："Error in parsing: Node: 'Output Y not found in graph'"
```

### 典型使用场景

```python
import onnx
from onnx import parser, printer

# 场景1：快速创建简单模型进行测试
test_model = parser.parse_model('''
<
  ir_version: 8,
  opset_import: [ "" : 17 ]
>
test_model (float[1,3] X) => (float[1,2] Y) {
    W = Constant <value_float = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]>()
    W_reshaped = Reshape(W, shape)
    shape = Constant <value_ints = [3, 2]>()
    Y = MatMul(X, W_reshaped)
}
''')
onnx.checker.check_model(test_model, full_check=True)

# 场景2：打印模型查看结构
model = onnx.load("complex_model.onnx")
with open("model_text.txt", "w") as f:
    f.write(printer.to_text(model))

# 场景3：快速检查某个节点
for node in model.graph.node:
    if node.op_type == "Conv":
        print(printer.to_text(node))
```

## 关键洞察/反常识

1. **onnxtxt ≠ textproto**：onnxtxt 是 ONNX 自定义的文本格式（类Python语法），textproto 是 Protobuf 标准文本格式。两者完全不同，文件扩展名和解析方式都不同。
2. **实验性警告不要忽略**：onnxtxt 格式可能在未来版本中变更，不应用于生产环境的模型存储。生产环境始终使用 protobuf 二进制格式。
3. **parser 返回的是 protobuf 对象**：parse_model 返回标准的 ModelProto，与从 .onnx 文件加载的对象完全相同——可以进行 check_model、shape_inference、save 等所有标准操作。
4. **文本格式体积大**：onnxtxt 和 textproto 格式比二进制 protobuf 大很多（通常 3-10倍），只适合调试和小规模模型。

## 关联概念

- [序列化/反序列化与外部数据](08-serialization.md) — _Registry 序列化框架和格式选择
- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — parser 输出的 message 结构
- [Python Helper API 详解](09-python-helpers.md) — 对比 make_* 构造方式，parser 是另一种模型构造途径
