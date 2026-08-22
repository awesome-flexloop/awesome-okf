---
type: concept
title: "形状推断实现"
description: "InferenceContext 接口、InferenceFunction 注册、DataPropagationFunction 数据传播、ShapeInferenceOptions 选项、kMaxMaterializedRank 限制、Python infer_shapes() 用法"
sources:
  references: [../references/shape-inference.md, ../references/op-schema.md]
  facts: [F-060, F-061, F-062, F-063, F-064]
---

# 形状推断实现

## 核心理解

形状推断（Shape Inference）是 ONNX 的核心能力之一：给定计算图和输入形状，自动推断所有中间张量和输出张量的形状与类型。形状推断在 C++ 层实现，通过 `InferenceContext` 抽象接口为每个算子提供统一的推断 API。推断结果写入 `GraphProto.value_info` 字段，是模型验证、优化和后端编译的基础。

## 机制详解

### InferenceContext 抽象接口

每个算子的形状推断函数接收 `InferenceContext&` 参数，通过该接口读取输入信息、写入输出类型（F-060）：

```cpp
class InferenceContext {
public:
  // 读取属性
  virtual const AttributeProto* getAttribute(const string& name) const = 0;

  // 读取输入类型（数量/类型/数据）
  virtual size_t getNumInputs() const = 0;
  virtual const TypeProto* getInputType(size_t index) const = 0;
  virtual const TensorProto* getInputData(size_t index) const = 0;

  // 写入输出类型
  virtual size_t getNumOutputs() const = 0;
  virtual TypeProto* getOutputType(size_t index) = 0;

  // 子图推断（If/Loop/Scan 等算子需要递归推断子图）
  virtual GraphInferencer* getGraphAttributeInferencer(
      const string& attr_name) = 0;
};
```

推断函数的工作模式：
1. 从 `getInputType()` 读取输入类型和形状
2. 从 `getAttribute()` 读取算子属性（如 Conv 的 kernel_shape、strides）
3. 根据算子语义计算输出形状
4. 通过 `getOutputType()` 获取可修改的 TypeProto 并设置输出形状/类型

### InferenceFunction 注册

每个算子版本通过 `TypeAndShapeInferenceFunction()` 注册其推断函数（F-061）：

```cpp
using InferenceFunction = std::function<void(InferenceContext&)>;

// 在 OpSchema 注册时绑定
OpSchema("Conv")
  .SinceVersion(11)
  // ... 输入输出声明
  .TypeAndShapeInferenceFunction([](InferenceContext& ctx) {
    // Conv 形状推断逻辑：
    // output_size = (input_size + pad_begin + pad_end - kernel) / stride + 1
    propagateElemTypeFromInputToOutput(ctx, 0, 0);
    convPoolShapeInference(ctx, ...);
  });
```

`dummyInferenceFunction` 是空实现，作为没有注册推断函数的算子的默认值——它不推断任何信息。

### 数据传播（Data Propagation）

除了形状推断，ONNX 还支持数据传播（F-061）：

```cpp
using DataPropagationFunction = std::function<void(DataPropagationContext&)>;
```

数据传播函数在启用时可以将常量输入数据（如 Shape 算子的输入是已知形状的张量）传播到输出，产生更精确的结果：
- 例如 Shape 算子：如果输入形状完全静态已知，数据传播可以将输出（形状值）计算为常量张量
- 这使得后续的 Reshape 等算子可以获得精确的输出形状

数据传播通过 `DataPropagationFunction()` 注册到 OpSchema，在 `enable_data_propagation=true` 时执行。

### ShapeInferenceOptions 三个选项

```cpp
struct ShapeInferenceOptions {
  bool check_type = false;
  int error_mode = 0;
  bool enable_data_propagation = false;
};
```

| 选项 | 默认值 | 作用 |
|------|--------|------|
| `check_type` | false | 设为 true 时，检查输入输出类型是否与 TypeConstraint 声明一致 |
| `error_mode` | 0 | 0=宽松模式（遇到错误继续处理其他节点）；1=严格模式（节点级错误立即抛异常） |
| `enable_data_propagation` | false | 启用 DataPropagationFunction 进行数据传播，可获得更精确的形状 |

不同场景使用不同选项组合：

| 场景 | check_type | error_mode | data_prop |
|------|-----------|------------|-----------|
| 快速推断（默认） | false | 0 | false |
| full_check 验证 | true | 1 | false |
| 常量折叠优化 | true | 1 | true |

### kMaxMaterializedRank 安全限制

```cpp
constexpr int kMaxMaterializedRank = 1024;
```

形状推断中物化（即创建具体的维度列表）的最大秩为 1024（F-063）。这是一个安全防护，防止：
1. 恶意构造的模型通过 Reshape 到极高维张量导致无界内存分配
2. 形状推断过程中的 bug 导致维度数爆炸

### Python 端 infer_shapes()

```python
def infer_shapes(
    model: ModelProto,
    check_type: bool = False,
    strict_mode: bool = False,
    data_prop: bool = False,
) -> ModelProto:
```

Python API 将参数映射到 C++ ShapeInferenceOptions（F-064）：
- `check_type` → `check_type`
- `strict_mode=True` → `error_mode=1`
- `data_prop` → `enable_data_propagation`

执行流程：
1. 将 ModelProto 序列化为字节串
2. 调用 C++ `onnx_cpp2py_export.shape_inference.infer_shapes`
3. C++ 端执行形状推断，遍历图中节点按拓扑序调用各算子的 InferenceFunction
4. 推断结果写入 `graph.value_info`
5. 返回新的 ModelProto（对副本操作，不修改原模型）

```python
# 基本用法
import onnx

model = onnx.load("model.onnx")
inferred_model = onnx.shape_inference.infer_shapes(model)

# 严格模式 + 类型检查
inferred_model = onnx.shape_inference.infer_shapes(
    model, check_type=True, strict_mode=True
)

# 启用数据传播（更精确但更慢）
inferred_model = onnx.shape_inference.infer_shapes(
    model, data_prop=True
)

# 访问推断后的中间值类型
for vi in inferred_model.graph.value_info:
    print(f"{vi.name}: {vi.type.tensor_type.elem_type}")
    shape = [
        d.dim_value if d.dim_value else d.dim_param
        for d in vi.type.tensor_type.shape.dim
    ]
    print(f"  shape: {shape}")
```

### 形状推断数据流

```
ModelProto
    │
    ↓
┌─────────────────────────────────────────┐
│      Shape Inference Engine (C++)        │
│                                         │
│  1. 构建符号表：从 graph.input 和        │
│     graph.initializer 收集已知类型       │
│                                         │
│  2. 按拓扑序遍历节点：                   │
│     for node in topological_sort(graph): │
│       ├── 查找 OpSchema(domain, op, ver) │
│       ├── 创建 InferenceContextImpl      │
│       ├── 调用 InferenceFunction(ctx)    │
│       ├── 将输出类型加入符号表            │
│       └── (如果 data_prop)               │
│           调用 DataPropagationFunction   │
│                                         │
│  3. 递归处理子图属性（If/Loop/Scan）    │
│     使用 getGraphAttributeInferencer     │
│                                         │
│  4. 将推断结果写入 graph.value_info      │
└─────────────────────────────────────────┘
    │
    ↓
ModelProto' (带 value_info 的新模型)
```

## 关键洞察/反常识

1. **默认 infer_shapes 不做类型检查**：check_type=False 时，即使输入类型与算子声明不匹配，推断也可能"成功"（产生垃圾结果而非报错）。full_check 时 check_type=True。
2. **形状推断返回新模型，不修改原模型**：这是因为 C++ 端对序列化后的副本进行推断。如果需要更新原模型，必须使用返回值。
3. **value_info 推断前通常是空的**：刚加载或刚构建的模型通常没有中间值的类型信息，必须调用 infer_shapes 才能填充。
4. **子图需要递归推断**：If/Loop/Scan 等包含子图属性的算子，推断时需要递归推断子图内部的形状。InferenceContext 提供 getGraphAttributeInferencer 用于此目的。
5. **数据传播≠常量折叠**：数据传播只在形状推断过程中使用常量数据来计算更精确的形状，不会在图中插入常量节点或执行实际计算。

## 关联概念

- [算子定义与注册机制 OpSchema](05-operator-schema.md) — InferenceFunction 如何注册到 OpSchema
- [模型检查器 Checker](07-model-checker.md) — full_check 模式如何使用形状推断
- [计算图模型](03-computation-graph.md) — value_info 在图结构中的作用
- [模型加载、检查与形状推断](../examples/load-check-model.md) — infer_shapes 的实际使用示例
