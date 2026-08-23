---
type: reference
title: "defs/schema.h/cc：OpSchema 算子注册机制"
description: "OpSchema 链式 API、FormalParameterOption、ONNX_OPERATOR_SET_SCHEMA 宏、OpSchemaRegistry 单例、TypeConstraint、FunctionBody、四个算子域"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/defs/schema.h"
    facts: [F-046, F-047, F-049, F-050, F-051]
  - path: "external/libs/models/onnx/onnx/onnx/defs/schema.cc"
    facts: []
  - path: "external/libs/models/onnx/onnx/onnx/common/constants.h"
    facts: [F-048, F-078, F-079]
---

# defs/schema.h/cc：OpSchema 算子注册机制

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnx/defs/schema.h` | C++ 头文件 | OpSchema 类定义、链式 API、注册宏、FormalParameterOption 枚举 |
| `onnx/defs/schema.cc` | C++ 实现 | OpSchema 方法实现、OpSchemaRegistry 单例实现 |
| `onnx/common/constants.h` | C++ 头文件 | 四个算子域常量定义、NormalizeDomain 函数 |

## 关键事实登记

### F-046：OpSchema 链式调用 API

**信源**：`onnx/defs/schema.h` L352-L582

OpSchema 类提供链式方法（返回 `*this`）用于声明算子：

```cpp
OpSchema& SinceVersion(int n);
OpSchema& NumInputs(int n);
OpSchema& NumOutputs(int n);
OpSchema& SetDoc(const char* doc);
OpSchema& SetDomain(const char* domain);
OpSchema& Attr(const char* name, const char* description, AttributeProto::AttributeType type, bool required);
OpSchema& Input(int n, const char* name, const char* description, const char* type_str, FormalParameterOption option = Single);
OpSchema& Output(int n, const char* name, const char* description, const char* type_str, FormalParameterOption option = Single);
OpSchema& TypeConstraint(const char* type_str, const DataTypeSet& allowed_types, const char* description);
OpSchema& AllowConsumed(const std::function<bool(int)>& consumed);
OpSchema& FunctionBody(const std::function<FunctionBodyBuildContext&, std::vector<NodeProto>&>&);
OpSchema& SetContextDependentFunctionBodyBuilder(ContextDependentFunctionBodyBuilder);
OpSchema& TypeAndShapeInferenceFunction(InferenceFunction);
OpSchema& DataPropagationFunction(DataPropagationFunction);
```

典型用法：
```cpp
OpSchema("Add")
  .SinceVersion(13)
  .SetDomain("")
  .SetDoc("Performs element-wise binary addition.")
  .Input(0, "A", "First operand.", "T")
  .Input(1, "B", "Second operand.", "T")
  .Output(0, "C", "Result.", "T")
  .TypeConstraint("T", {"tensor(float)", "tensor(int64)", ...}, "Constrain input/output types.")
  .TypeAndShapeInferenceFunction(...)
```

### F-047：FormalParameterOption 形参选项

**信源**：`onnx/defs/schema.h` L151-L162

```cpp
enum FormalParameterOption {
  Single = 0,    // 单个必选参数
  Optional = 1,  // 单个可选参数
  Variadic = 2   // 可变参数（最小元数由 min_arity 指定）
};
```

- `Single`：恰好一个输入/输出（默认）
- `Optional`：零个或一个输入/输出
- `Variadic`：零个或多个输入/输出，最小数量由 `min_arity` 字段控制

### F-048：ONNX_OPERATOR_SET_SCHEMA 宏和四个算子域

**信源**：`onnx/defs/schema.h` L1278-L1302；`onnx/common/constants.h` L13-L19

注册宏：
```cpp
#define ONNX_OPERATOR_SET_SCHEMA(name, ver, impl) \
  static OpSchemaRegisterOnce name##_ver##_op_schema_registration( \
      (impl).SetName(#name).SinceVersion(ver).Build())
```

四个算子域（定义于 `common/constants.h`）：

| 域常量 | 域字符串 | 说明 |
|--------|---------|------|
| ONNX_DOMAIN / AI_ONNX_DOMAIN | "" / "ai.onnx" | 标准算子域（两者等价，NormalizeDomain 统一为空字符串） |
| AI_ONNX_ML_DOMAIN | "ai.onnx.ml" | 传统机器学习算子域（树模型、SVM等） |
| AI_ONNX_TRAINING_DOMAIN | "ai.onnx.training" | 训练相关算子域（梯度、优化器等） |
| AI_ONNX_PREVIEW_DOMAIN | "ai.onnx.preview" | 预览/实验算子域 |

### F-049：OpSchemaRegistry 单例和自动注册

**信源**：`onnx/defs/schema.h` L911-L1046

- `OpSchemaRegistry` 是单例模式（通过 `Instance()` 静态方法访问），实现了 `ISchemaRegistry` 接口
- `OpSchemaRegisterOnce` 是 RAII 辅助类，在构造时自动将 OpSchema 注册到全局单例注册表
- 未显式调用 `SinceVersion()` 时，默认版本设为 1
- 查找方式：通过 `(domain, op_type, version)` 三元组查找对应的 OpSchema

### F-050：TypeConstraint 类型约束

**信源**：`onnx/defs/schema.h` L487-L582；L122-L126

类型约束机制：
1. `TypeConstraint(type_str, allowed_types, description)` 声明一个类型约束名（如 "T"）到允许的数据类型集合
2. `Input()`/`Output()` 方法通过类型字符串（如 "T"）引用声明的类型约束
3. 同一类型约束的所有输入输出必须具有相同的元素类型
4. `TypeConstraintParam` 存储单个约束参数，`TypeConstraintMap` 是约束名字到约束映射

### F-051：FunctionBody 函数体机制

**信源**：`onnx/defs/schema.h` L91-L95；L764-L818

OpSchema 支持两种函数体定义方式：

1. **FunctionBody（静态函数体）**：
   ```cpp
   OpSchema& FunctionBody(const std::function<void(FunctionBodyBuildContext&, std::vector<NodeProto>&)>& builder);
   ```
   提供一个构建函数，生成展开后的节点列表。

2. **ContextDependentFunctionBodyBuilder（上下文化函数体）**：
   注册一个函数体构建器，根据属性值或其他上下文信息动态决定函数体展开方式。这使得算子可以在不同属性配置下展开为不同的基础算子组合。

### F-078：域常量定义

**信源**：`onnx/common/constants.h` L13-L27

```cpp
constexpr const char* ONNX_DOMAIN = "";
constexpr const char* AI_ONNX_DOMAIN = "ai.onnx";
constexpr const char* AI_ONNX_ML_DOMAIN = "ai.onnx.ml";
constexpr const char* AI_ONNX_TRAINING_DOMAIN = "ai.onnx.training";
constexpr const char* AI_ONNX_PREVIEW_DOMAIN = "ai.onnx.preview";
```

### F-079：NormalizeDomain 域规范化

**信源**：`onnx/common/constants.h` L21-L27

- `NormalizeDomain()` 将 "ai.onnx" 转为 ""（空字符串）
- `IsOnnxDomain()` 检查域是否为 "" 或 "ai.onnx"（两者等价）
- proto 存储和注册表查找统一使用空字符串表示标准域
