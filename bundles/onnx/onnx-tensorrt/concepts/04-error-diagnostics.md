---
type: concept
title: "错误处理与诊断：15种ErrorCode、异常+错误列表双轨、子图分区报告"
description: "onnx-tensorrt 错误处理体系详解：OnnxTrtException 异常模型、ONNXTRT_TRY/CATCH 边界宏、Status/IParserError 丰富上下文信息、15 种 ErrorCode 分类、子图分区报告算法、DLA 能力验证模式、常见错误排查路径"
sources:
  references: [../references/parser-api.md, ../references/core-utilities.md]
  facts: [F-006, F-007, F-011, F-027, F-028, F-029]
---

# 错误处理与诊断：15种ErrorCode、异常+错误列表双轨、子图分区报告

## 核心理解

onnx-tensorrt 采用**异常+错误列表双轨**错误处理机制：内部使用异常（`OnnxTrtException`）进行控制流跳转，公共 API 边界使用 `ONNXTRT_TRY/ONNXTRT_CATCH_RECORD` 宏捕获异常并将错误记录到错误列表，避免异常穿越 C API 边界。`Status` 类携带丰富的上下文信息（错误码、描述、文件名、行号、函数名、节点索引/名称/操作类型、局部函数调用栈），远超标准异常的信息量。

理解错误处理系统的关键在于：**解析器不会遇到第一个错误就停止**——静态检查错误通过异常抛出，但被 parseGraph 的 ONNXTRT_TRY 块捕获后记录，继续处理后续节点。这使得 `supportsModelV2()` 能够报告所有不支持的节点，而不仅仅是第一个。

## ErrorCode：15 种错误类型

```cpp
enum class ErrorCode : int {
    kSUCCESS = 0,                       // 成功（无错误）

    // 系统级错误
    kINTERNAL_ERROR = 1,                // 内部错误（不应该发生的情况）
    kMEM_ALLOC_FAILED = 2,              // 内存分配失败

    // 模型加载错误
    kMODEL_DESERIALIZE_FAILED = 3,      // 模型反序列化失败（protobuf 解析错误）

    // 参数验证错误
    kINVALID_VALUE = 4,                 // 无效参数值
    kINVALID_GRAPH = 5,                 // 无效图结构
    kINVALID_NODE = 6,                  // 无效节点

    // 不支持错误
    kUNSUPPORTED_GRAPH = 7,             // 不支持的图结构
    kUNSUPPORTED_NODE = 8,              // 不支持的节点（最常见）
    kUNSUPPORTED_NODE_ATTR = 9,         // 不支持的节点属性
    kUNSUPPORTED_INPUT = 10,            // 不支持的输入
    kUNSUPPORTED_DATATYPE = 11,         // 不支持的数据类型
    kUNSUPPORTED_DYNAMIC_SHAPE = 12,    // 不支持的动态形状
    kUNSUPPORTED_SHAPE = 13,            // 不支持的形状

    // Refit 错误
    kREFIT_FAILED = 14,                 // 权重重拟合失败
};
```

### 错误分类与常见原因

| 类别 | ErrorCode | 常见原因 | 排查方向 |
|------|-----------|---------|---------|
| **系统错误** | INTERNAL_ERROR | 解析器内部 bug、空指针、断言失败 | 检查 TensorRT/onnx-tensorrt 版本兼容性 |
| | MEM_ALLOC_FAILED | GPU/CPU 内存不足 | 减小 batch size、检查模型大小 |
| **加载错误** | MODEL_DESERIALIZE_FAILED | ONNX 文件损坏、非 protobuf 格式、版本不兼容 | 用 onnx.checker.check_model() 验证模型 |
| **无效错误** | INVALID_VALUE | 参数超出合法范围（如负 kernel size） | 检查模型属性值 |
| | INVALID_GRAPH | 图结构有环、输入未连接 | 用 onnx.helper.check_model 验证 |
| | INVALID_NODE | 节点缺少必要输入/属性 | 检查节点定义 |
| **不支持错误** | UNSUPPORTED_NODE | **最常见**——算子无内置实现且无插件 | 检查是否需要自定义插件，或使用 opset 兼容版本 |
| | UNSUPPORTED_NODE_ATTR | 算子的某个属性值不支持 | 检查属性是否在支持范围内 |
| | UNSUPPORTED_INPUT | 输入类型/形状不支持 | 检查输入数据类型和形状 |
| | UNSUPPORTED_DATATYPE | 使用了 DOUBLE/INT64/STRING 等不支持类型 | 检查是否有类型降级警告 |
| | UNSUPPORTED_DYNAMIC_SHAPE | 动态维度在不支持动态形状的层中使用 | 检查动态形状配置 |
| | UNSUPPORTED_SHAPE | 形状参数不合法（如负数维度） | 检查输入形状定义 |
| **Refit** | REFIT_FAILED | 权重名称/形状不匹配、引擎未标记可 refit | 检查 RefitRecord 输出 |

## Status：丰富的错误上下文

`Status` 类实现了 `IParserError` 接口，每个错误携带比标准异常更丰富的上下文：

```cpp
class Status : public IParserError {
    ErrorCode mCode;                                    // 错误码
    std::string mDesc;                                  // 错误描述
    std::string mFile;                                  // 源文件名（如 "ModelImporter.cpp"）
    int mLine;                                          // 行号
    std::string mFunc;                                  // 函数名
    int mNodeIndex = -1;                                // ONNX 节点索引（-1=无节点上下文）
    std::string mNodeName;                              // 节点名称
    std::string mOpName;                                // 操作类型（如 "Conv"、"Relu"）
    std::vector<std::string> mLocalFunctionStack;       // 局部函数调用栈

public:
    // IParserError 接口方法
    ErrorCode code() const override;
    const char* desc() const override;
    const char* file() const override;
    int line() const override;
    const char* func() const override;
    int nodeIndex() const override;       // 出错节点在 graph 中的索引
    const char* nodeName() const override; // 节点名称
    const char* nodeOperator() const override; // 操作类型
    int localFunctionStackSize() const override;
    const char* localFunctionStack(int index) const override; // 函数调用栈
};
```

**LocalFunctionStack 的价值**：当错误发生在 LocalFunction 内部时，mLocalFunctionStack 记录了从顶层节点到当前函数的调用链，类似函数调用栈，帮助定位嵌套函数中的错误。

## 异常+错误列表双轨机制

### 内部轨道：异常控制流

```cpp
// 内部使用 OnnxTrtException 进行错误跳转
class OnnxTrtException : public std::exception {
    Status mStatus;
public:
    OnnxTrtException(Status status) : mStatus(std::move(status)) {}
    const Status& getStatus() const { return mStatus; }
    const char* what() const noexcept override { return mStatus.desc(); }
};
```

内部代码使用三个宏进行条件检查和异常抛出：

```cpp
// 基础检查：条件为假则抛出异常
#define ONNXTRT_CHECK(cond, error_code)                                        \
    do {                                                                       \
        if (!(cond)) {                                                         \
            throw OnnxTrtException(                                            \
                MAKE_ERROR(error_code, #cond, __FILE__, __LINE__, __FUNC__)); \
        }                                                                      \
    } while (0)

// 节点上下文检查：包含节点信息
#define ONNXTRT_CHECK_NODE(cond, error_code, node, node_idx)                   \
    do {                                                                       \
        if (!(cond)) {                                                         \
            throw OnnxTrtException(                                            \
                MAKE_NODE_ERROR(error_code, #cond, node, node_idx,             \
                                __FILE__, __LINE__, __FUNC__));               \
        }                                                                      \
    } while (0)

// 输入上下文检查：包含输入信息
// MAKE_INPUT_ERROR 宏用于输入相关错误
```

错误构造宏：

| 宏 | 上下文字段 | 使用场景 |
|----|-----------|---------|
| `MAKE_ERROR` | file/line/func + code/desc | 通用错误（非节点上下文） |
| `MAKE_NODE_ERROR` | + nodeIndex/nodeName/opName | 节点处理过程中的错误 |
| `MAKE_INPUT_ERROR` | + nodeIndex/nodeName/opName + input name | 输入相关错误 |

### 边界轨道：错误列表记录

在公共 API 边界（parse/parseFromFile/supportsModelV2 等），异常被捕获并转换为错误列表条目：

```cpp
// errorHelpers.hpp（简化）
#define ONNXTRT_TRY try {

#define ONNXTRT_CATCH_RECORD                                                 \
    }                                                                        \
    catch (const OnnxTrtException& e) {                                      \
        mErrors.emplace_back(e.getStatus());                                 \
    }                                                                        \
    catch (const std::exception& e) {                                        \
        mErrors.emplace_back(ErrorCode::kINTERNAL_ERROR, e.what(),           \
                             __FILE__, __LINE__, __FUNC__);                  \
    }
```

### ValueOrStatus 返回值模式

对于需要返回值但可能失败的函数，使用 `ValueOrStatus<T>` 模板类：

```cpp
template <typename T>
class ValueOrStatus {
    std::variant<T, Status> mData;
public:
    ValueOrStatus(T value) : mData(std::move(value)) {}
    ValueOrStatus(Status error) : mData(std::move(error)) {}

    bool isOk() const { return std::holds_alternative<T>(mData); }
    const T& value() const { return std::get<T>(mData); }
    const Status& error() const { return std::get<Status>(mData); }
    T&& takeValue() { return std::move(std::get<T>(mData)); }
};
```

这是 Rust 中 `Result<T, E>` 模式的 C++ 实现，避免了使用输出参数+返回值错误码的繁琐模式。

### 双轨机制流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    公共 API 边界                             │
│  parse() / parseFromFile() / supportsModelV2()              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ONNXTRT_TRY {                                       │   │
│  │   importModel() ──────────────────────────────┐     │   │
│  │     parseGraph()                              │     │   │
│  │       parseNode()                             │     │   │
│  │         ONNXTRT_CHECK(...) ← 条件失败抛异常    │     │   │
│  │         ONNXTRT_CHECK_NODE(...)               │     │   │
│  │         导入函数内部                            │     │   │
│  │           throw OnnxTrtException(...)          │     │   │
│  │     } ← parseGraph 的 ONNXTRT_TRY 捕获并记录   │     │   │
│  │   }                                             │     │   │
│  │ } ONNXTRT_CATCH_RECORD {                         │     │   │
│  │   mErrors.push_back(...) ← 异常转为错误列表条目  │     │   │
│  │ }                                               │     │   │
│  │                                                 │     │   │
│  │ logErrors() → 输出所有错误到 logger             │     │   │
│  │ reportSubgraphs() → 子图分区                    │     │   │
│  │ return mErrors.empty() ← bool 返回成功/失败     │     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**关键设计**：
1. **内部使用异常**：异常在 C++ 内部是最自然的错误传播方式，避免每层手动检查返回值
2. **边界捕获转换**：公共 API 是 C 兼容接口（通过 C 函数 `createNvOnnxParser_INTERNAL`），不能传播 C++ 异常，必须在边界捕获
3. **错误累积**：parseGraph 逐节点处理时捕获异常并记录，继续处理后续节点——这样能收集所有错误而非只看到第一个
4. **bool 返回值**：公共 API 返回 bool 表示整体成功/失败，详细错误通过 `getNbErrors()/getError()` 查询

## 错误查询 API

```cpp
// 查询错误数量
int getNbErrors() const;

// 获取第 i 个错误（返回 IParserError 接口指针）
const IParserError* getError(int index) const;

// 清除所有错误
void clearErrors();

// 遍历错误示例
for (int i = 0; i < parser->getNbErrors(); i++) {
    const IParserError* error = parser->getError(i);
    std::cerr << "Error " << i << ": "
              << "code=" << static_cast<int>(error->code())
              << " node=" << error->nodeName()
              << " op=" << error->nodeOperator()
              << " desc=" << error->desc()
              << " at " << error->file() << ":" << error->line()
              << std::endl;

    // 打印 LocalFunction 栈（如果有）
    for (int j = 0; j < error->localFunctionStackSize(); j++) {
        std::cerr << "  in function: " << error->localFunctionStack(j) << std::endl;
    }
}
```

## 子图分区报告

`reportSubgraphs()` 是 supportsModelV2 功能的核心，它将图中节点划分为"可支持"和"不支持"的子图：

### 算法详解

```
reportSubgraphs() 算法:

输入: 已解析的图（可能有部分节点失败）
输出: 子图列表，标记每个子图是否支持

步骤:
1. 收集错误节点集合
   errorNodes = { nodeIndex | 该节点在 parseNode 时出错 }

2. 收集不支持输入集合
   unsupportedInputs = { tensorName | 该张量来自错误节点的输出 }
   （注意：需要传播——如果一个张量的生产节点出错，所有消费该张量的节点
    也会因为输入不支持而失败）

3. 按拓扑序遍历节点，划分子图:
   currentSubgraph = []
   subgraphs = []

   for node in topoOrder:
       if (nodeIndex in errorNodes) OR
          (any(inputName in unsupportedInputs)):
           // 当前节点不可支持
           if currentSubgraph is not empty:
               subgraphs.append(currentSubgraph)
               currentSubgraph = []
           // 标记此节点的输出为不支持输入
           for outputName in node.outputs():
               unsupportedInputs.add(outputName)
       else:
           // 当前节点可支持
           currentSubgraph.append(nodeIndex)

   if currentSubgraph is not empty:
       subgraphs.append(currentSubgraph)

4. 判定整体支持度:
   if errorNodes.empty() and len(subgraphs) == 1:
       return kSUPPORTED
   elif errorNodes.empty():
       return kSUPPORTED（理论上不应出现，但安全处理）
   elif len(subgraphs) > 0:
       return kPARTIAL_SUPPORTED
   else:
       return kUNSUPPORTED
```

### 子图查询 API

```cpp
// 查询子图数量
int getNbSubgraphs() const;

// 查询第 i 个子图是否支持
bool isSubgraphSupported(int index) const;

// 获取第 i 个子图包含的节点索引列表
int getSubgraphNodes(int index, int* nodes, int size) const;
```

**使用场景**：
1. **模型兼容性预检**：在实际构建引擎之前，用 supportsModelV2 检查模型是否可被 TensorRT 支持
2. **部分加速**：对于 PARTIAL_SUPPORTED 的模型，可以将支持的子图交给 TensorRT 加速，不支持的部分用其他框架执行
3. **定位问题算子**：通过子图边界确定哪些算子导致了不支持

## DLA 能力验证模式

设置 `kREPORT_CAPABILITY_DLA` flag 后，解析器会在每个节点导入后额外验证该层是否可在 DLA（Deep Learning Accelerator）上运行：

```cpp
parser->setFlag(OnnxParserFlag::kREPORT_CAPABILITY_DLA);
parser->supportsModelV2(modelData, modelSize);
// 此时 getError() 会包含 DLA 不支持的节点信息
```

配合 `kADJUST_FOR_DLA` flag，解析器还会自动调整不兼容的层（如插入必要的转换层）以适配 DLA 要求。

## 常见错误排查路径

### 1. UNSUPPORTED_NODE（最常见）

```
错误信息示例:
  [W] parsers/onnx/onnx2trt_utils.hpp:365: UNSUPPORTED_NODE:
      node[name: "...", op: "MyCustomOp"]: 
      No importer registered for op: MyCustomOp
```

排查步骤：
1. 确认 op_type 是否拼写正确
2. 确认 opset 版本是否支持该算子（TensorRT 11.2 支持 opset 7+）
3. 检查是否有对应的 TensorRT 插件可用
4. 如果没有内置实现也没有插件，需要编写自定义插件

### 2. UNSUPPORTED_DATATYPE

```
错误信息示例:
  UNSUPPORTED_DATATYPE: DataType DOUBLE is not supported
```

排查步骤：
1. 检查模型中是否有 DOUBLE/INT64 类型的权重或输入
2. 这些类型会被自动降级（DOUBLE→FLOAT、INT64→INT32），但中间张量如果是这些类型则会报错
3. 使用 onnxruntime 或 onnx 工具将模型转换为 FP32/INT32

### 3. UNSUPPORTED_DYNAMIC_SHAPE

```
错误信息示例:
  UNSUPPORTED_DYNAMIC_SHAPE: Node "Reshape_5" has dynamic shape
```

排查步骤：
1. 确认是否正确设置了优化 profile（optimization profile）
2. 某些层（如非支持动态形状的插件）确实不支持动态形状
3. 考虑使用静态形状或为不支持的层使用插件

### 4. MODEL_DESERIALIZE_FAILED

```
错误信息示例:
  MODEL_DESERIALIZE_FAILED: Failed to parse ONNX model
```

排查步骤：
1. 用 Python 验证模型有效性：
   ```python
   import onnx
   model = onnx.load("model.onnx")
   onnx.checker.check_model(model)
   ```
2. 确认 ONNX opset 版本与 TensorRT 版本兼容
3. 确认文件未损坏

### 5. INVALID_NODE

```
错误信息示例:
  INVALID_NODE: Node "Conv_3" has 2 inputs, expected at least 2
```

排查步骤：
1. 检查节点的输入数量是否正确
2. 检查必填属性是否提供
3. 用 onnx.checker 验证模型

## 关联概念

- [解析管线详解](01-parsing-pipeline.md) — 理解 parseGraph 中错误捕获与继续处理的机制
- [算子注册与插件扩展](02-op-registration-plugin.md) — 理解 UNSUPPORTED_NODE 错误的解决方案（编写插件）
- [权重内存模型](03-weights-memory-model.md) — 理解 UNSUPPORTED_DATATYPE 中的类型降级
- [解析器整体架构](00-overall-architecture.md) — 理解两遍式解析中错误收集的作用
