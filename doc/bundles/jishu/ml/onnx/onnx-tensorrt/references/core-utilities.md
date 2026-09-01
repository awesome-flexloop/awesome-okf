---
type: reference
title: "核心工具类：ShapedWeights/OnnxAttrs/TensorOrWeights/WeightsContext/BFloat16/Status"
description: "onnx-tensorrt 核心工具数据结构：变体类型、权重视图、属性访问、内存管理、特殊浮点类型、错误状态的信源登记"
sources:
  - path: "external/libs/models/onnx/onnx-tensorrt/TensorOrWeights.hpp"
    facts: [F-020]
  - path: "external/libs/models/onnx/onnx-tensorrt/ShapedWeights.hpp"
    facts: [F-021]
  - path: "external/libs/models/onnx/onnx-tensorrt/ShapedWeights.cpp"
    facts: [F-021]
  - path: "external/libs/models/onnx/onnx-tensorrt/OnnxAttrs.hpp"
    facts: [F-022]
  - path: "external/libs/models/onnx/onnx-tensorrt/OnnxAttrs.cpp"
    facts: [F-022]
  - path: "external/libs/models/onnx/onnx-tensorrt/WeightsContext.hpp"
    facts: [F-024]
  - path: "external/libs/models/onnx/onnx-tensorrt/bfloat16.hpp"
    facts: [F-025]
  - path: "external/libs/models/onnx/onnx-tensorrt/bfloat16.cpp"
    facts: [F-025]
  - path: "external/libs/models/onnx/onnx-tensorrt/Status.hpp"
    facts: [F-027, F-028]
  - path: "external/libs/models/onnx/onnx-tensorrt/errorHelpers.hpp"
    facts: [F-028]
  - path: "external/libs/models/onnx/onnx-tensorrt/ImporterContext.hpp"
    facts: [F-023, F-032]
  - path: "external/libs/models/onnx/onnx-tensorrt/importerUtils.hpp"
    facts: [F-017, F-032, F-033]
---

# 核心工具类：ShapedWeights/OnnxAttrs/TensorOrWeights/WeightsContext/BFloat16/Status

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `TensorOrWeights.hpp` | 头文件 | `TensorOrWeights` 变体类型：ITensor* 或 ShapedWeights |
| `ShapedWeights.hpp/cpp` | 头/实现 | `ShapedWeights` 非拥有权重视图，可隐式转换为 nvinfer1::Weights |
| `OnnxAttrs.hpp/cpp` | 头/实现 | `OnnxAttrs` 节点属性访问器，模板特化 get<T>() |
| `WeightsContext.hpp` | 头文件 | `WeightsContext` 权重内存所有权管理、类型转换、mmap |
| `bfloat16.hpp/cpp` | 头/实现 | `BFloat16` BF16 浮点类型，手工位操作实现 |
| `Status.hpp` | 头文件 | `Status`/`IParserError` 错误状态，ErrorCode 枚举，OnnxTrtException |
| `errorHelpers.hpp` | 头文件 | 错误处理宏：ONNXTRT_TRY/CATCH/CHECK、MAKE_ERROR |
| `ImporterContext.hpp` | 头文件 | `ImporterContext` 中央解析上下文，持有所有状态 |
| `importerUtils.hpp/cpp` | 头/实现 | NameScope RAII、通用 helper 函数 |

## 关键事实登记

### F-020：TensorOrWeights 核心变体类型

**信源**：`TensorOrWeights.hpp`

`TensorOrWeights` 基于 `std::variant<nvinfer1::ITensor*, ShapedWeights>` 实现，是解析过程中数据流的核心载体。它有三种状态：

```
TensorOrWeights 三态:
  ├─ ITensor* (非nullptr) → 已转换为 TensorRT 网络张量
  ├─ ShapedWeights        → 尚未转换的静态权重
  └─ ITensor* (nullptr)   → 缺失的可选输入（null 状态）
```

类型判断方法：

| 方法 | 含义 |
|------|------|
| `is_tensor()` | 是 ITensor* 且非 nullptr |
| `is_weights()` | 是 ShapedWeights |
| `isNullTensor()` | 是 ITensor* 且为 nullptr（可选输入缺失） |
| `isFp32()`/`isFp16()`/`isBFp16()` | 检查 FP32/FP16/BF16 数据类型 |
| `isInt32()`/`isInt64()`/`isInt8()`/`isUint8()`/`isInt4()`/`isBool()`/`isFp8()` | 检查整数/量化数据类型 |

```cpp
// TensorOrWeights.hpp - 核心定义（简化）
class TensorOrWeights {
    std::variant<nvinfer1::ITensor*, ShapedWeights> mVariant;
public:
    // 构造
    TensorOrWeights() : mVariant(static_cast<nvinfer1::ITensor*>(nullptr)) {}
    TensorOrWeights(nvinfer1::ITensor* tensor) : mVariant(tensor) {}
    TensorOrWeights(ShapedWeights weights) : mVariant(weights) {}

    // 状态查询
    bool is_tensor() const { return std::holds_alternative<ITensor*>(mVariant) && tensor() != nullptr; }
    bool is_weights() const { return std::holds_alternative<ShapedWeights>(mVariant); }
    bool isNullTensor() const { return std::holds_alternative<ITensor*>(mVariant) && tensor() == nullptr; }

    // 值访问
    nvinfer1::ITensor*& tensor() { return std::get<ITensor*>(mVariant); }
    ShapedWeights& weights() { return std::get<ShapedWeights>(mVariant); }
    // ... 类型查询方法
};
```

### F-021：ShapedWeights 非拥有权重视图

**信源**：`ShapedWeights.hpp`、`ShapedWeights.cpp`

`ShapedWeights` 表示带形状的 ONNX 权重数据，**不拥有底层数据**（所有权在 WeightsContext）：

```cpp
struct ShapedWeights {
    int32_t type;               // ONNX TensorProto_DataType
    void* values;               // 指向数据的指针（不拥有）
    nvinfer1::Dims shape;       // 维度信息
    const char* name;           // 权重名称

    // 可隐式转换为 TensorRT Weights 结构
    operator nvinfer1::Weights() const {
        return nvinfer1::Weights{convertDtype(type), values, count()};
    }

    // 计算元素总数（任一维度为 0 则总数为 0）
    int64_t count() const;
};
```

**关键设计**：
- 非拥有语义意味着 ShapedWeights 只是视图，底层内存由 WeightsContext 管理
- 任何算子导入函数中创建的临时权重必须通过 WeightsContext 分配
- `count()` 方法处理动态维度（任一维为 -1 则总数为 -1）

### F-022：OnnxAttrs 节点属性访问工具

**信源**：`OnnxAttrs.hpp`、`OnnxAttrs.cpp`

`OnnxAttrs` 构造时遍历 `NodeProto` 的所有 `attribute()` 构建 `unordered_map<string, AttributeProto const*>` 索引，通过模板特化的 `get<T>()` 方法提供类型安全的属性访问：

```cpp
class OnnxAttrs {
    std::unordered_map<std::string, const onnx::AttributeProto*> attrs;
    string_map<std::string> mLocalAttrMap; // LocalFunction 外部属性引用映射
public:
    OnnxAttrs(const NodeProto& node, IImporterContext* ctx, string_map<std::string> localAttrMap = {});

    // 模板特化 get<T>() 支持多种类型:
    template <typename T>
    T get(const std::string& key, const std::string& refAttrName = "") const;
};
```

`get<T>()` 支持的类型包括：
- 基础类型：`float`, `int32_t`, `int64_t`, `bool`, `std::string`
- 向量类型：`vector<int32_t>`, `vector<int64_t>`, `vector<float>`, `vector<string>`
- TRT 类型：`nvinfer1::Dims`, `nvinfer1::DimsHW`, `nvinfer1::Permutation`, `nvinfer1::DataType`
- 特殊类型：`ShapedWeights`, `vector<DataType>`, `ActivationType`, `ScaleMode`, `MatrixOperation`, `InterpolationMode`
- 子图类型：`GraphProto`

`ref_attr_name` 参数用于解析 LocalFunction 的外部属性引用（`ref_attr_name` 指向调用上下文中的属性名）。

### F-023：ImporterContext 中央解析上下文

**信源**：`ImporterContext.hpp`

`ImporterContext` 是解析过程中的中央上下文对象，持有所有解析状态：

```
ImporterContext 核心成员:
├─ INetworkDefinition* mNetwork          — TensorRT 网络定义
├─ ILogger* mLogger                      — 日志器
├─ WeightsContext mWeightsCtx            — 权重内存管理器
├─ string_map<int64_t> mOpsetVersions    — opset 版本表（按 domain）
├─ StringMap<TensorOrWeights> mTensors   — 所有已解析张量/权重映射
├─ TensorLocationMap mTensorLocations    — 张量位置（GPU/DLA）
├─ TensorRangeMap mTensorRanges          — 动态范围（量化）
├─ TensorPrecisionMap mTensorPrecisions  — 张量精度设置
├─ NameSet mTensorNames                  — 已注册张量名集合（唯一性）
├─ NameSet mLayerNames                   — 已注册层名集合（唯一性）
├─ std::vector<std::string> mErrors      — 错误记录器包装
├─ ConstantLayerCache mConstantCache     — Constant 层缓存（去重）
├─ std::vector<std::string> mLogicalVCPluginLibraries — VC 插件逻辑名
├─ BaseNameScopeStack mBaseNameScopes    — 子图名称作用域栈
├─ StringMap<const FunctionProto*> mLocalFunctions — LocalFunctions 映射
├─ LocalFunctionStack mLocalFunctionStack — 局部函数调用栈
├─ StringList mGraphInputs               — 图输入名称列表
├─ StringList mGraphOutputs              — 图输出名称列表
└─ SuffixCounter mSuffixCounters         — 名称后缀计数器（重名去重）
```

### F-024：WeightsContext 权重内存管理

**信源**：`WeightsContext.hpp`

`WeightsContext` 负责所有权重数据的内存管理，**禁止拷贝和移动**：

```cpp
class WeightsContext {
    std::vector<std::unique_ptr<uint8_t[]>> mWeightBuffers; // 所有权重缓冲的 unique_ptr
    nvinfer1::IGpuAllocator* mAllocator;                    // GPU 分配器
    bool mInitializedOnDevice;                              // 是否已在设备上初始化
    std::vector<std::string> mExternalInitializers;         // 外部 initializer 列表

public:
    // 核心方法：
    ShapedWeights createNamedTempWeights(ShapedWeights weights, const std::string& name);
    ShapedWeights ownWeights(ShapedWeights weights);

    // 类型转换方法：
    ShapedWeights convertUINT8(ShapedWeights weights);      // UINT8 → INT32
    ShapedWeights convertDOUBLE(ShapedWeights weights);     // DOUBLE → FLOAT
    ShapedWeights convertINT64(ShapedWeights weights);      // INT64 → INT32
    ShapedWeights convertFp16ToFp32(ShapedWeights weights); // FP16 → FP32
    ShapedWeights convertBf16ToFp32(ShapedWeights weights); // BF16 → FP32

    // 外部权重：
    void* mmap(const std::string& path, size_t size, size_t offset); // mmap 外部权重文件
    ShapedWeights loadExternalInit(const std::string& path, const std::string& name,
                                    onnx::TensorProto& tensor);       // 加载外部 initializer
};
```

**类型自动降级规则**：
- UINT8 权重 → INT32（非 Q/DQ 节点）
- DOUBLE 权重 → FLOAT
- INT64 权重 → INT32
- FP16/BF16 → FP32（提升用于 CPU 计算）

外部大模型权重通过 `mmap()` 内存映射读取，避免全部加载到内存。

### F-025：BFloat16 手工位操作实现

**信源**：`bfloat16.hpp`、`bfloat16.cpp`

`BFloat16` 实现 Brain Floating Point 格式（1 位符号 + 8 位指数 + 7 位尾数），底层存储为 `uint16_t`。不依赖编译器 intrinsic 或库函数，纯手工位操作：

```
BF16 位布局:
┌──────┬──────────┬─────────────────┐
│ sign │ exponent │    mantissa      │
│  1   │    8     │        7         │
└──────┴──────────┴─────────────────┘
  bit15  bits14-7    bits6-0

FP32 位布局:
┌──────┬──────────┬────────────────────────┐
│ sign │ exponent │       mantissa          │
│  1   │    8     │           23            │
└──────┴──────────┴─────────────────────────┘
  bit31  bits30-23     bits22-0
```

float → BF16 转换（round-to-even 舍入）：

```cpp
// bfloat16.cpp（简化）
BFloat16::BFloat16(float v) {
    uint32_t bits;
    std::memcpy(&bits, &v, 4);

    if ((bits & 0x7f800000u) != 0x7f800000u) {
        // 有限数：round-to-even 舍入
        // 加上 0x7FFF + (尾数第16位) 后截断高16位
        bits += 0x7FFFu + ((bits >> 16) & 1u);
        mBits = static_cast<uint16_t>(bits >> 16);
    } else {
        // NaN/Inf：直接截断高16位
        mBits = static_cast<uint16_t>(bits >> 16);
    }
}
```

BF16 → float 转换：直接将 bits 左移 16 位后 memcpy 为 float。

### F-026：UINT8 权重处理规则

**信源**：`ModelImporter.cpp`

UINT8 权重的处理取决于上下文：

| 上下文 | 处理方式 |
|--------|----------|
| 非 Q/DQ 节点的 UINT8 权重 | 自动转换为 INT32（`WeightsContext::convertUINT8`） |
| Constant 节点输出 UINT8 | 允许保留 UINT8 类型 |
| 设置 kENABLE_UINT8_AND_ASYMMETRIC_QUANTIZATION_DLA | QuantizeLinear/Gather 输出允许 UINT8 |
| 网络输出 UINT8 | 允许 |
| 其他情况 | 抛出 `UNSUPPORTED_NODE` 错误 |

```cpp
// ModelImporter.cpp L365-396（简化）
// 非 Q/DQ 节点的 UINT8 权重自动转换
if (input.is_weights() && input.weights().type == ::ONNX_NAMESPACE::TensorProto::UINT8) {
    if (node.op_type() != "QuantizeLinear" && node.op_type() != "DequantizeLinear") {
        input = ctx->getWeightsContext().convertUINT8(input.weights());
    }
}
```

### F-027：ErrorCode 与 Status 错误模型

**信源**：`NvOnnxParser.h`、`Status.hpp`

15 种 ErrorCode 枚举：

```cpp
enum class ErrorCode : int {
    kSUCCESS = 0,
    kINTERNAL_ERROR = 1,              // 内部错误
    kMEM_ALLOC_FAILED = 2,            // 内存分配失败
    kMODEL_DESERIALIZE_FAILED = 3,    // 模型反序列化失败
    kINVALID_VALUE = 4,               // 无效值
    kINVALID_GRAPH = 5,               // 无效图
    kINVALID_NODE = 6,                // 无效节点
    kUNSUPPORTED_GRAPH = 7,           // 不支持的图
    kUNSUPPORTED_NODE = 8,            // 不支持的节点
    kUNSUPPORTED_NODE_ATTR = 9,       // 不支持的节点属性
    kUNSUPPORTED_INPUT = 10,          // 不支持的输入
    kUNSUPPORTED_DATATYPE = 11,       // 不支持的数据类型
    kUNSUPPORTED_DYNAMIC_SHAPE = 12,  // 不支持的动态形状
    kUNSUPPORTED_SHAPE = 13,          // 不支持的形状
    kREFIT_FAILED = 14,               // refit 失败
};
```

`Status` 类实现了 `IParserError` 接口，携带丰富的上下文信息：

```cpp
class Status : public IParserError {
    ErrorCode mCode;
    std::string mDesc;           // 错误描述
    std::string mFile;           // 源文件名
    int mLine;                   // 行号
    std::string mFunc;           // 函数名
    int mNodeIndex;              // 节点索引（-1 表示无）
    std::string mNodeName;       // 节点名
    std::string mOpName;         // 操作类型
    std::vector<std::string> mLocalFunctionStack; // 局部函数堆栈
    // ...
};
```

### F-028：异常+错误列表双轨错误处理

**信源**：`errorHelpers.hpp`、`Status.hpp`

错误处理采用异常+错误列表双轨机制：

```
┌─────────────────────────────────────────────────────┐
│              错误处理双轨机制                         │
├─────────────────────────────────────────────────────┤
│  内部轨道（异常）:                                    │
│  ├─ ONNXTRT_CHECK(cond, code)                       │
│  │   条件为假 → 抛出 OnnxTrtException(Status)       │
│  ├─ ONNXTRT_CHECK_NODE(cond, code, node, idx)       │
│  │   条件为假 → 抛出含节点信息的异常                 │
│  └─ MAKE_ERROR/MAKE_NODE_ERROR/MAKE_INPUT_ERROR     │
│      构造不同上下文的 Status 对象                    │
│                                                      │
│  边界轨道（错误列表）:                                │
│  ├─ ONNXTRT_TRY { ... }                             │
│  │   包裹可能抛出异常的代码                          │
│  └─ ONNXTRT_CATCH_RECORD { ... }                    │
│      捕获异常 → 记录到 mErrors 向量 → 不继续传播     │
│                                                      │
│  返回值模式:                                         │
│  └─ ValueOrStatus<T> → T 或 Status 错误             │
└─────────────────────────────────────────────────────┘
```

```cpp
// errorHelpers.hpp（简化）
#define ONNXTRT_TRY try {
#define ONNXTRT_CATCH_RECORD                                                                 \
    } catch (const OnnxTrtException& e) {                                                    \
        mErrors.emplace_back(e.getStatus());                                                 \
    } catch (const std::exception& e) {                                                      \
        mErrors.emplace_back(ErrorCode::kINTERNAL_ERROR, e.what());                          \
    }

#define ONNXTRT_CHECK(cond, code)                                                            \
    do {                                                                                     \
        if (!(cond)) {                                                                       \
            throw OnnxTrtException(MAKE_ERROR(code, #cond));                                 \
        }                                                                                    \
    } while (0)

#define ONNXTRT_CHECK_NODE(cond, code, node, idx)                                            \
    do {                                                                                     \
        if (!(cond)) {                                                                       \
            throw OnnxTrtException(MAKE_NODE_ERROR(code, #cond, node, idx));                 \
        }                                                                                    \
    } while (0)
```

公共 API 边界（parse/parseFromFile/supportsModelV2 等）使用 ONNXTRT_TRY/ONNXTRT_CATCH_RECORD 宏捕获异常，将错误记录到 mErrors 向量后正常返回 bool 值，避免异常穿越 C API 边界。

### F-032：NameScope RAII 名称作用域

**信源**：`importerUtils.hpp`、`ImporterContext.hpp`

`NameScope` 是 RAII 类，封装 `pushBaseNameScope()/popBaseNameScope()`，用于子图（If/Loop/Scan/LocalFunction）的名称作用域管理：

```cpp
// 用法
{
    NameScope scope(ctx, node);  // 入栈：保存被遮蔽的外部同名张量
    // ... 递归解析子图节点 ...
}  // 出栈：恢复被遮蔽的外部张量，清除本作用域引入的新名称
```

`BaseNameScopeStack` 维护 `vector<StringMap<pair<bool, TensorOrWeights>>>`，栈中每项是一个作用域的名称映射：
- `bool=true`：该作用域新引入的名称
- `bool=false`：被遮蔽的外层同名张量（保存旧值以在出栈时恢复）

### F-033：Helper 函数分层

**信源**：`importerUtils.hpp/cpp`

通用 helper 函数按算子类别分文件组织：

| 文件 | 职责 |
|------|------|
| `importerUtils.hpp/cpp` | 通用 helper：unaryHelper、elementwiseHelper、activationHelper、poolingHelper、scaleHelper、broadcastTensors、convertToTensor、identity、addClip、addScale 等 |
| `AttentionHelpers.cpp` | 注意力机制算子（MultiHeadAttention 等） |
| `ConditionalHelpers.cpp` | If 条件算子 |
| `LoopHelpers.cpp` | Loop 循环算子 |
| `RNNHelpers.cpp` | RNN/LSTM/GRU 循环网络 |
| `ShapeTensor.cpp` | 形状张量计算（Shape/Gather/Concat 等形状推理） |
| `weightUtils.cpp` | 权重工具（类型转换、常量创建等） |

## 代码引用

```cpp
// importerUtils.hpp - addConstantLayer 模式（简化）
// 将 ShapedWeights 转换为 ITensor* 的标准模式
nvinfer1::ITensor* addConstantLayer(ImporterContext* ctx,
                                     ShapedWeights weights,
                                     const std::string& name) {
    // 1. 查找缓存
    auto it = ctx->constantCache().find(name);
    if (it != ctx->constantCache().end()) {
        return it->second->getOutput(0);
    }
    // 2. 创建 Constant 层
    nvinfer1::IConstantLayer* constant
        = ctx->network()->addConstant(weights.shape, weights);
    constant->setName(name.c_str());
    // 3. 缓存并返回
    ctx->constantCache()[name] = constant;
    return constant->getOutput(0);
}
```
