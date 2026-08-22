---
type: reference
title: "shape_inference.h/cc/shape_inference.py：形状推断实现"
description: "InferenceContext 接口、InferenceFunction/DataPropagationFunction 注册、ShapeInferenceOptions、kMaxMaterializedRank、Python infer_shapes() 封装"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/defs/shape_inference.h"
    facts: [F-060, F-061, F-062, F-063]
  - path: "external/libs/models/onnx/onnx/onnx/defs/shape_inference.cc"
    facts: []
  - path: "external/libs/models/onnx/onnx/onnx/shape_inference.py"
    facts: [F-064]
---

# shape_inference.h/cc/shape_inference.py：形状推断实现

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnx/defs/shape_inference.h` | C++ 头文件 | InferenceContext 抽象类、InferenceFunction/DataPropagationFunction 类型定义、ShapeInferenceOptions |
| `onnx/defs/shape_inference.cc` | C++ 实现 | 形状推断核心逻辑、符号传播、算子推断函数实现 |
| `onnx/shape_inference.py` | Python 模块 | infer_shapes() 函数，委托 C++ 实现 |

## 关键事实登记

### F-060：InferenceContext 抽象类接口

**信源**：`onnx/defs/shape_inference.h` L92-L130

```cpp
class InferenceContext {
public:
  virtual const AttributeProto* getAttribute(const std::string& name) const = 0;
  virtual size_t getNumInputs() const = 0;
  virtual const TypeProto* getInputType(size_t index) const = 0;
  virtual const TensorProto* getInputData(size_t index) const = 0;
  virtual size_t getNumOutputs() const = 0;
  virtual TypeProto* getOutputType(size_t index) = 0;
  virtual GraphInferencer* getGraphAttributeInferencer(const std::string& attr_name) = 0;
  virtual const SparseTensorProto* getInputSparseType(size_t index) const;
  virtual ~InferenceContext() = default;
};
```

InferenceContext 为每个算子的形状推断函数提供统一接口：
- **读取输入类型**：`getInputType(index)` 获取输入的 TypeProto
- **读取输入数据**：`getInputData(index)` 获取静态已知的输入张量数据（用于常量折叠和数据传播）
- **写入输出类型**：`getOutputType(index)` 返回可修改的 TypeProto，推断函数设置输出形状/类型
- **读取属性**：`getAttribute(name)` 获取节点属性值
- **子图推断**：`getGraphAttributeInferencer()` 获取子图属性的推断器（用于 If/Loop 等）

### F-061：InferenceFunction 与 DataPropagationFunction

**信源**：`onnx/defs/shape_inference.h` L154-L162

```cpp
using InferenceFunction = std::function<void(InferenceContext&)>;
using DataPropagationFunction = std::function<void(DataPropagationContext&)>;

// 空实现作为默认推断函数（不推断任何形状信息）
void dummyInferenceFunction(InferenceContext& ctx);
```

- **InferenceFunction**：每个算子注册的形状/类型推断函数，接收 InferenceContext 引用，设置输出类型
- **DataPropagationFunction**：数据传播函数，在启用数据传播时使用，将输入数据传播到输出（用于常量折叠场景）
- **dummyInferenceFunction**：空实现，不推断任何信息，作为未注册推断函数的算子的默认值

### F-062：ShapeInferenceOptions

**信源**：`onnx/defs/shape_inference.h` L26-L38

```cpp
struct ShapeInferenceOptions {
  bool check_type = false;           // 检查输入输出类型相等性
  int error_mode = 0;                // 0=不抛节点级错误, 1=抛节点级错误
  bool enable_data_propagation = false;  // 启用数据传播
};
```

三个选项的语义：
- `check_type`：当设置为 true 时，推断过程中验证输入类型与 TypeConstraint 声明的一致性
- `error_mode`：0 = 遇到错误时继续处理其他节点（宽松模式）；1 = 遇到错误立即抛出异常（严格模式）
- `enable_data_propagation`：启用时，DataPropagationFunction 将常量输入数据传播到输出，允许更精确的形状推断（如 Shape 算子输出具体值）

### F-063：kMaxMaterializedRank 常量

**信源**：`onnx/defs/shape_inference.h` L24

```cpp
constexpr int kMaxMaterializedRank = 1024;
```

限制形状推断中物化（materialize）的最大秩为 1024。这是一个安全防护，防止恶意构造的模型导致无界 protobuf 消息物化（如 Reshape 到无限维度）。

### F-064：Python infer_shapes() 函数

**信源**：`onnx/shape_inference.py` L32-L70

```python
def infer_shapes(
    model: ModelProto,
    check_type: bool = False,
    strict_mode: bool = False,
    data_prop: bool = False,
) -> ModelProto:
```

参数映射到 C++ ShapeInferenceOptions：
- `check_type` → `check_type`：类型检查
- `strict_mode` → `error_mode=1`（严格模式，节点级错误抛异常）
- `data_prop` → `enable_data_propagation`：启用数据传播

实现方式：
1. 将输入 ModelProto 序列化为字节串
2. 委托给 C++ 绑定：`onnx.onnx_cpp2py_export.shape_inference.infer_shapes`
3. C++ 端执行形状推断，结果写入 graph 的 `value_info` 字段
4. 反序列化返回新的 ModelProto

注意：infer_shapes 返回新的 ModelProto（对副本进行推断），不修改原始模型。
