---
type: concept
title: "算子定义与注册机制 OpSchema"
description: "OpSchema 链式 API、FormalParameterOption 形参选项、ONNX_OPERATOR_SET_SCHEMA 宏、OpSchemaRegistry 单例注册表、TypeConstraint 类型约束、FunctionBody 函数体机制"
sources:
  references: [../references/op-schema.md]
  facts: [F-046, F-047, F-048, F-049, F-050, F-051, F-078, F-079, F-080]
---

# 算子定义与注册机制 OpSchema

## 核心理解

ONNX 算子系统基于 **OpSchema 类 + 全局单例注册表** 实现。每个算子的每个版本都有一个独立的 OpSchema 条目，通过链式调用 API 声明算子的输入输出、属性、类型约束、形状推断函数等信息。算子注册通过 `ONNX_OPERATOR_SET_SCHEMA` 宏在静态初始化时自动完成，运行时通过 `(domain, op_type, version)` 三元组查找。

## 机制详解

### OpSchema 链式 API

OpSchema 使用链式调用（Fluent Interface）模式声明算子签名（F-046）：

```cpp
// 典型的算子注册模式（以 Add 算子为例）
ONNX_OPERATOR_SET_SCHEMA(
    Add, 13,
    OpSchema()
        .SetDomain("")
        .SetDoc("Performs element-wise binary addition.")
        .Input(0, "A", "First operand.", "T")
        .Input(1, "B", "Second operand.", "T")
        .Output(0, "C", "Result, has same element type as two inputs.", "T")
        .TypeConstraint("T", OpSchema::numeric_types_for_math_reduction(),
                        "Constrain input and output types to numeric tensors.")
        .TypeAndShapeInferenceFunction([](InferenceContext& ctx) {
            // 形状推断逻辑
            propagateElemTypeFromInputToOutput(ctx, 0, 0);
            broadcastShapeInference(ctx);
        })
);
```

链式方法一览：

| 方法 | 作用 |
|------|------|
| `SetName(name)` | 设置算子名（由宏自动设置） |
| `SinceVersion(n)` | 设置算子版本（由宏自动设置） |
| `SetDomain(domain)` | 设置算子域（默认标准域""） |
| `SetDoc(doc)` | 设置文档字符串 |
| `Attr(name, desc, type, required)` | 声明属性参数 |
| `Input(n, name, desc, type_str, option)` | 声明第n个输入 |
| `Output(n, name, desc, type_str, option)` | 声明第n个输出 |
| `TypeConstraint(type_str, types, desc)` | 声明类型约束 |
| `TypeAndShapeInferenceFunction(fn)` | 注册形状推断函数 |
| `FunctionBody(builder)` | 注册静态函数体 |
| `SetContextDependentFunctionBodyBuilder(builder)` | 注册上下文化函数体构建器 |
| `AllowConsumed(fn)` | 声明允许原地修改的输入 |

### FormalParameterOption：形参选项

输入输出参数支持三种选项（F-047）：

```cpp
enum FormalParameterOption {
  Single = 0,    // 默认：恰好一个输入/输出
  Optional = 1,  // 零个或一个（可以不连接）
  Variadic = 2   // 零个或多个（可变参数，min_arity 控制最小数量）
};
```

- **Single**：该位置必须提供一个输入/输出（如 Add 的两个输入都是 Single）
- **Optional**：该输入可以省略（空字符串 "" 表示未连接，如 Clip 的 min/max 输入是 Optional）
- **Variadic**：接受可变数量的输入/输出（如 Concat 接受任意数量的张量输入，Sum 接受可变数量输入）

```python
# Optional 输入示例：Clip 算子可以只传 input，不传 min/max
node = make_node("Clip", ["X", "", ""], ["Y"])  # min/max 为空字符串
# 或者
node = make_node("Clip", ["X"], ["Y"])  # 只传一个输入
```

### ONNX_OPERATOR_SET_SCHEMA 注册宏

```cpp
#define ONNX_OPERATOR_SET_SCHEMA(name, ver, impl) \
  static OpSchemaRegisterOnce name##_ver##_op_schema_registration( \
      (impl).SetName(#name).SinceVersion(ver).Build())
```

宏展开后创建一个静态的 `OpSchemaRegisterOnce` 对象，其构造函数将 OpSchema 注册到全局注册表（F-048）。这是**静态初始化注册模式**——算子在程序启动（共享库加载）时自动注册，无需手动调用注册函数。

### OpSchemaRegistry 单例注册表

OpSchemaRegistry 是全局单例（F-049）：

```
┌─────────────────────────────────────────────┐
│        OpSchemaRegistry (Singleton)          │
│                                             │
│  内部存储：                                  │
│  map<(domain, op_type),                    │
│      map<version, const OpSchema*>>         │
│                                             │
│  核心方法：                                  │
│  ├── Instance() → 获取单例                  │
│  ├── GetSchema(domain, op_type, version)    │
│  │   → 查找 (domain, op_type, version)      │
│  │   → 返回 const OpSchema*                 │
│  └── GetRegisteredSchema(domain, ...)       │
│      → 带错误处理的查找                      │
└─────────────────────────────────────────────┘
         ↑ 注册 (静态初始化时)
         │
  ONNX_OPERATOR_SET_SCHEMA 宏
  OpSchemaRegisterOnce 构造函数
```

**关键设计**：
- 同一算子的不同版本是**完全独立**的 OpSchema 条目
- 查找通过 (domain, op_type, version) 三元组精确匹配
- 未调用 SinceVersion() 时默认版本为 1
- 算子版本升级时，不是修改旧版本 OpSchema，而是注册一个新版本条目

### TypeConstraint 类型约束

TypeConstraint 实现了类型多态（F-050）：

```cpp
// 1. 声明类型约束 "T"
.TypeConstraint("T",
    {"tensor(float)", "tensor(double)", "tensor(int32)", "tensor(int64)"},
    "Constrain to numeric types.")

// 2. 输入输出通过类型字符串引用
.Input(0, "A", "First input.", "T")
.Input(1, "B", "Second input.", "T")
.Output(0, "C", "Output.", "T")
```

机制：
1. `TypeConstraint(type_str, allowed_types, desc)` 将类型名（如 "T"）映射到允许的类型集合
2. 所有引用同一类型字符串的输入输出**必须具有相同的元素类型**
3. 一个算子可以声明多个类型约束（如 "T1"、"T2"）
4. checker 验证实际输入输出类型是否满足约束

```
TypeConstraint 关系：

  "T" → {float, double, int32, int64, float16, bfloat16, ...}
         │
         ├── Input[0] ("A") 类型必须是 "T" 中的一种
         ├── Input[1] ("B") 类型必须是 "T" 中的一种
         └── Output[0] ("C") 类型必须是 "T" 中的一种
         且：Input[0]、Input[1]、Output[0] 的实际类型必须完全相同
```

### FunctionBody 函数体机制

OpSchema 支持将算子定义为其他基础算子的组合（F-051）：

1. **静态 FunctionBody**：
   ```cpp
   .FunctionBody([](FunctionBodyBuildContext& ctx,
                    std::vector<NodeProto>& nodes) {
       // 展开为基础算子节点
       nodes.push_back(/* 基础节点 */);
   })
   ```
   函数体是固定的，与属性值无关。

2. **ContextDependentFunctionBodyBuilder**：
   ```cpp
   .SetContextDependentFunctionBodyBuilder(
       [](const FunctionBodyBuildContext& ctx,
          const OpSchema& schema,
          FunctionProto& function_proto) -> bool {
           // 根据属性值动态生成函数体
           if (ctx.getAttribute("some_attr")) { ... }
           return true;
       })
   ```
   函数体依赖属性值，不同属性配置展开为不同的算子组合。

函数体机制使得高层算子（如 Selu、Hardmax）可以用基础算子（Exp、Mul、Add 等）组合定义，简化了推理引擎的实现——引擎只需要实现基础算子，函数体算子可以自动展开。

### 四个域的算子注册

```
标准域 (domain=""):
  Conv, MatMul, Add, Relu, Softmax, BatchNormalization, ...
  ai.onnx v1~v25

ML域 (domain="ai.onnx.ml"):
  TreeEnsembleClassifier, LinearClassifier, SVMClassifier,
  OneHotEncoder, LabelEncoder, ...
  ai.onnx.ml v1~v5

训练域 (domain="ai.onnx.training"):
  Gradient, AdamOptimizer, SGD, Momentum, ...
  ai.onnx.training v1

预览域 (domain="ai.onnx.preview"):
  实验性算子（如某些新的注意力机制算子）
```

## 关键洞察/反常识

1. **版本不是继承，而是独立条目**：Add-v7 和 Add-v13 在注册表中是两个完全独立的 OpSchema，不存在"Add 基类 + v13 扩展"的关系。这就是为什么版本转换本质上是 adapter 模式——在不同版本的 OpSchema 之间映射。
2. **类型约束是名字匹配，不是位置匹配**：输入输出的类型一致性通过类型约束字符串（如"T"）关联，不是通过位置自动推断。所有引用"T"的输入输出必须类型相同。
3. **函数体≠子图**：FunctionBody 是 OpSchema 层面的算子展开机制，在模型加载/优化时展开为基础算子。它不同于 GRAPH 属性（子图是模型的一部分，运行时条件执行）。
4. **注册是静态初始化**：所有内置算子在 .so/.dll 加载时通过静态对象构造函数自动注册，不需要手动初始化注册表。自定义算子需要在运行时显式注册。
5. **shape_inference 函数是 OpSchema 的一部分**：每个算子版本都有自己的形状推断函数，版本升级时形状推断逻辑也可能改变。

## 关联概念

- [Opset版本机制与算子域](04-opset-versioning.md) — 算子版本与 IR 版本的关系、四个域的定义
- [形状推断实现](06-shape-inference.md) — InferenceContext 和形状推断函数的工作方式
- [模型检查器 Checker](07-model-checker.md) — checker 如何使用 OpSchema 验证模型
- [自定义算子注册示例](../examples/custom-operator.md) — 如何在 Python 中创建使用自定义算子的模型
