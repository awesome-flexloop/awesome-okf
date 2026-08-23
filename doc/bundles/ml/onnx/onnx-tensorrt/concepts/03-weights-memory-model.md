---
type: concept
title: "权重内存模型：ShapedWeights 非拥有语义、WeightsContext 内存管理、UINT8/DOUBLE/INT64 自动降级、BFloat16 手工位操作"
description: "onnx-tensorrt 权重管理子系统详解：TensorOrWeights 变体三态、ShapedWeights 非拥有视图、WeightsContext 所有权与类型转换、外部权重 mmap、BFloat16 round-to-even 舍入、临时权重分配规范"
sources:
  references: [../references/parser-api.md, ../references/core-utilities.md]
  facts: [F-005, F-020, F-021, F-024, F-025, F-026, F-008]
---

# 权重内存模型：ShapedWeights 非拥有语义、WeightsContext 内存管理、UINT8/DOUBLE/INT64 自动降级、BFloat16 手工位操作

## 核心理解

与通常理解的"权重是张量的附属数据"不同，onnx-tensorrt 将权重管理设计为**独立子系统**。核心抽象是 `TensorOrWeights` 变体类型——在解析过程中，一个 ONNX 张量要么是已转换为 TensorRT 网络张量的 `ITensor*`，要么是尚未转换的静态权重 `ShapedWeights`。`ShapedWeights` 是**非拥有视图**，底层内存全部由 `WeightsContext` 统一管理。

理解权重系统的关键在于：**ShapedWeights 不拥有数据**——这意味着任何在算子导入函数中创建的临时权重都必须通过 WeightsContext 分配，否则会出现悬挂指针。同时，类型自动降级（UINT8→INT32、DOUBLE→FLOAT、INT64→INT32）是静默发生的，用户可能意识不到精度损失。

## TensorOrWeights：权重/张量变体

### 三态设计

```cpp
// TensorOrWeights 基于 std::variant<ITensor*, ShapedWeights>
// 实际有三种状态:

状态 1: ITensor* (非nullptr)
  └─ 表示已转换为 TensorRT 网络张量
  └─ is_tensor() == true
  └─ 通过 .tensor() 访问 ITensor*

状态 2: ShapedWeights
  └─ 表示静态权重数据（尚未添加到网络中）
  └─ is_weights() == true
  └─ 通过 .weights() 访问 ShapedWeights

状态 3: ITensor* (nullptr)
  └─ 表示缺失的可选输入
  └─ isNullTensor() == true
  └─ 对应 ONNX 中空字符串的可选输入
```

### 权重→张量的转换

在算子导入函数中，当需要将 ShapedWeights 作为层输入时，必须先转换为 ITensor*。这通过 `convertToTensor()` helper 函数完成：

```cpp
// importerUtils.hpp/cpp
nvinfer1::ITensor* convertToTensor(ImporterContext* ctx,
                                    TensorOrWeights& tw,
                                    const std::string& name) {
    if (tw.is_tensor()) {
        return tw.tensor();  // 已经是张量，直接返回
    }
    if (tw.is_weights()) {
        // 权重：创建 Constant 层
        return addConstantLayer(ctx, tw.weights(), name);
    }
    // nullptr → 错误
    throw ...;
}
```

`addConstantLayer()` 创建一个 `IConstantLayer`，将 ShapedWeights 包装为网络中的常量层。为了去重，相同名称的常量层会被缓存（ConstantLayerCache）。

### 数据类型查询方法

TensorOrWeights 提供了丰富的类型查询方法，覆盖所有 TensorRT 支持的数据类型：

| 方法 | 对应 ONNX 类型 | TensorRT 类型 |
|------|---------------|--------------|
| `isFp32()` | FLOAT | DataType::kFLOAT |
| `isFp16()` | FLOAT16 | DataType::kHALF |
| `isBFp16()` | BFLOAT16 | DataType::kBF16 |
| `isInt32()` | INT32 | DataType::kINT32 |
| `isInt64()` | INT64 | —（自动降级为 INT32） |
| `isInt8()` | INT8 | DataType::kINT8 |
| `isUint8()` | UINT8 | —（特殊处理） |
| `isInt4()` | INT4 | DataType::kINT4 |
| `isBool()` | BOOL | DataType::kBOOL |
| `isFp8()` | FLOAT8E4M3FN/FLOAT8E5M2 | DataType::kFP8 |

## ShapedWeights：非拥有权重视图

### 结构与语义

```cpp
struct ShapedWeights {
    int32_t type;               // ONNX TensorProto_DataType（int32_t）
    void* values;               // 指向数据的指针（不拥有！）
    nvinfer1::Dims shape;       // 维度信息
    const char* name;           // 权重名称（可选，用于调试）

    // 隐式转换为 TensorRT Weights 结构
    operator nvinfer1::Weights() const {
        return nvinfer1::Weights{convertDtype(type), values, (int64_t)count()};
    }

    int64_t count() const {
        // 计算元素总数
        // 任一维度为 0 → 总数为 0
        // 任一维度为 -1（动态）→ 总数为 -1
        int64_t c = 1;
        for (int i = 0; i < shape.nbDims; i++) {
            if (shape.d[i] == 0) return 0;
            if (shape.d[i] == -1) return -1;
            c *= shape.d[i];
        }
        return c;
    }
};
```

**非拥有语义的关键含义**：
- `values` 指针指向的内存不由 ShapedWeights 管理
- 拷贝 ShapedWeights 只是浅拷贝（拷贝指针值）
- ShapedWeights 的生命周期不能超过底层数据的生命周期
- 底层数据的生命周期由 WeightsContext 管理

### 生命周期陷阱

这是编写自定义算子导入器时最容易出错的地方：

```cpp
// ❌ 错误：栈变量作为权重数据
DEFINE_BUILTIN_OP_IMPORTER(MyOp) {
    float data[] = {1.0f, 2.0f, 3.0f};  // 栈上分配！
    ShapedWeights w;
    w.values = data;  // 指向栈内存！
    w.shape = Dims{1, {3}};
    w.type = onnx::TensorProto::FLOAT;
    // 函数返回后，data 被销毁，w.values 成为悬挂指针！
    // ...
}

// ✅ 正确：通过 WeightsContext 分配
DEFINE_BUILTIN_OP_IMPORTER(MyOp) {
    std::vector<float> data = {1.0f, 2.0f, 3.0f};
    ShapedWeights w;
    w.type = onnx::TensorProto::FLOAT;
    w.shape = Dims{1, {3}};
    w.values = data.data();
    // 通过 WeightsContext 获取所有权
    w = ctx->getWeightsContext().ownWeights(w);  // 数据被拷贝到 WeightsContext 管理的缓冲
    // ...
}

// ✅ 更好：使用 createNamedTempWeights
DEFINE_BUILTIN_OP_IMPORTER(MyOp) {
    ShapedWeights w;
    w.type = onnx::TensorProto::FLOAT;
    w.shape = Dims{1, {3}};
    w = ctx->getWeightsContext().createNamedTempWeights(w, "my_op_weights");
    float* data = static_cast<float*>(w.values);
    data[0] = 1.0f; data[1] = 2.0f; data[2] = 3.0f;
    // ...
}
```

## WeightsContext：权重内存所有权管理者

### 核心设计

```cpp
class WeightsContext {
    // 禁止拷贝和移动
    WeightsContext(const WeightsContext&) = delete;
    WeightsContext& operator=(const WeightsContext&) = delete;

    // 所有权重缓冲的 unique_ptr 向量
    std::vector<std::unique_ptr<uint8_t[]>> mWeightBuffers;

public:
    // 拥有外部权重数据（拷贝到内部管理的缓冲）
    ShapedWeights ownWeights(ShapedWeights weights);

    // 创建命名临时权重（分配新缓冲）
    ShapedWeights createNamedTempWeights(ShapedWeights weights, const std::string& name);

    // 类型转换方法（返回指向新缓冲的 ShapedWeights）
    ShapedWeights convertUINT8(ShapedWeights weights);      // UINT8 → INT32
    ShapedWeights convertDOUBLE(ShapedWeights weights);     // DOUBLE → FLOAT
    ShapedWeights convertINT64(ShapedWeights weights);      // INT64 → INT32
    ShapedWeights convertFp16ToFp32(ShapedWeights weights); // FP16 → FP32
    ShapedWeights convertBf16ToFp32(ShapedWeights weights); // BF16 → FP32

    // 外部权重文件支持
    void* mmap(const std::string& path, size_t size, size_t offset);
    ShapedWeights loadExternalInit(const std::string& path,
                                    const std::string& name,
                                    onnx::TensorProto& tensor);
};
```

### 内存模型图

```
┌─────────────────────────────────────────────────────────────┐
│                    WeightsContext 内存模型                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  mWeightBuffers: vector<unique_ptr<uint8_t[]>>              │
│  ┌───┬─────────────────────────────────────────────────┐   │
│  │ 0 │ unique_ptr → [initializer 0 data ...]          │   │
│  │ 1 │ unique_ptr → [initializer 1 data ...]          │   │
│  │ 2 │ unique_ptr → [converted UINT8→INT32 data ...]  │   │ ← 类型转换产生新缓冲
│  │ 3 │ unique_ptr → [converted DOUBLE→FLOAT data ...] │   │
│  │ 4 │ unique_ptr → [temp weights for Conv bias ...]  │   │ ← createNamedTempWeights
│  │ 5 │ unique_ptr → [mmap'd external weights ...]     │   │ ← 外部权重
│  │...│ ...                                             │   │
│  └───┴─────────────────────────────────────────────────┘   │
│          ▲                       ▲                          │
│          │                       │                          │
│    ShapedWeights            ShapedWeights                   │
│    (values→buffer[0])      (values→buffer[2])              │
│    (initializer view)      (converted view)                │
│                                                             │
│  关键点:                                                     │
│  - 所有数据缓冲由 unique_ptr 管理，WeightsContext 析构时     │
│    自动释放所有内存                                          │
│  - ShapedWeights 只是视图，不拥有数据                        │
│  - 类型转换不修改原数据，而是创建新缓冲                      │
│  - ownWeights() 会拷贝数据到新缓冲                          │
└─────────────────────────────────────────────────────────────┘
```

## 类型自动降级规则

TensorRT 不支持 ONNX 的所有数据类型作为计算类型。onnx-tensorrt 在解析过程中自动执行类型降级，这些降级是**静默的**（只有日志警告，不报错）：

| ONNX 类型 | TensorRT 支持？ | 自动降级为 | 降级时机 | 精度影响 |
|-----------|----------------|-----------|---------|---------|
| FLOAT (FP32) | ✅ 原生支持 | — | — | 无 |
| FLOAT16 (FP16) | ✅ 原生支持 | — | — | 无 |
| BFLOAT16 (BF16) | ✅ 原生支持 | — | — | 无 |
| INT32 | ✅ 原生支持 | — | — | 无 |
| INT8 | ✅ 原生支持 | — | — | 无 |
| INT4 | ✅ 原生支持 | — | — | 无 |
| BOOL | ✅ 原生支持 | — | — | 无 |
| FP8 (E4M3/E5M2) | ✅ 原生支持 | — | — | 无 |
| **DOUBLE (FP64)** | ❌ 不支持 | **FLOAT (FP32)** | WeightsContext::convertDOUBLE | 精度损失（64→32位） |
| **INT64** | ❌ 计算类型不支持 | **INT32** | WeightsContext::convertINT64 | 值域缩小（64→32位） |
| **UINT8** | ❌ 非Q/DQ上下文中不支持 | **INT32** | WeightsContext::convertUINT8 | 值域变化（无符号→有符号） |
| COMPLEX64/128 | ❌ 不支持 | 错误 | — | 不支持 |
| STRING | ❌ 不支持 | 错误 | — | 不支持 |

### UINT8 的特殊处理

UINT8 是最复杂的类型，因为它在量化上下文中合法，但在普通计算中不支持：

```
UINT8 处理逻辑（parseNode 第 3 层）:
  输入是 ShapedWeights 且 type == UINT8:
    ├─ 节点是 QuantizeLinear/DequantizeLinear
    │   └─ 保留 UINT8（量化/反量化操作合法）
    │
    ├─ kENABLE_UINT8_AND_ASYMMETRIC_QUANTIZATION_DLA 置位
    │   └─ 允许 UINT8 在 DLA 量化路径中使用
    │
    ├─ Constant 节点输出
    │   └─ 允许 UINT8（常量可以保持 UINT8）
    │
    └─ 其他情况
        └─ 自动转换为 INT32（convertUINT8）

  中间张量是 UINT8:
    ├─ 网络输出
    │   └─ 允许
    ├─ QuantizeLinear 输出（启用 DLA flag 时）
    │   └─ 允许
    ├─ Gather 输出（启用 DLA flag 时）
    │   └─ 允许
    └─ 其他
        └─ 抛出 UNSUPPORTED_NODE 错误
```

### FP16/BF16 提升转换

在 CPU 端进行权重预处理（如 BatchNorm 折叠、常量折叠）时，FP16 和 BF16 权重需要提升到 FP32 才能进行精确计算：

```
FP16/BF16 提升路径:
  ShapedWeights(FP16)
    → convertFp16ToFp32()
    → ShapedWeights(FP32, 新缓冲)
    → CPU 计算
    → 结果可转换回 FP16/BF16（通过 TRT 层设置精度）
```

## BFloat16：手工位操作实现

BF16（Brain Floating Point）是 16 位浮点格式，位布局为 1 位符号 + 8 位指数 + 7 位尾数（与 FP32 的高 16 位兼容）。onnx-tensorrt 不依赖编译器 intrinsic 或库函数，而是纯手工位操作实现：

```
BF16 与 FP32 的位布局关系:

FP32: S EEEEEEEE MMMMMMMMMMMMMMMMMMMMMMM  (32 bits)
      0 1      8 9                     31

BF16: S EEEEEEEE MMMMMMM                  (16 bits)
      0 1      8 9                    15

BF16 是 FP32 的高 16位截断版本——指数位完全相同，
这意味着 BF16 与 FP32 有相同的数值范围（~1e-38 到 ~3e38），
但尾数精度从 23 位降到 7 位（约 3 位十进制精度）。
```

### float → BF16 转换（round-to-even 舍入）

```cpp
// bfloat16.cpp（简化）
BFloat16::BFloat16(float v) {
    uint32_t bits;
    std::memcpy(&bits, &v, sizeof(bits));

    // 检查是否为 NaN 或 Inf
    if ((bits & 0x7F800000u) != 0x7F800000u) {
        // 有限数：round-to-even 舍入
        // 舍入逻辑：加上 0x7FFF + (bits>>16 & 1)
        //   - 0x7FFF 是半最大偏移（类似加 0.5 四舍五入）
        //   - (bits>>16 & 1) 是当前 BF16 尾数最低位（LSB）
        //   - 当剩余尾数恰好在中间值时，LSB=1 进位、LSB=0 舍去 → round-to-even
        bits += 0x7FFFu + ((bits >> 16) & 1u);
    }
    // NaN/Inf 直接截断（不需要舍入）
    mBits = static_cast<uint16_t>(bits >> 16);
}
```

round-to-even（银行家舍入）的原理：当浮点数恰好落在两个 BF16 可表示值的中间时，选择尾数为偶数（LSB=0）的那个值。这避免了传统四舍五入在统计上引入的正偏差。

### BF16 → float 转换

```cpp
// bfloat16.cpp（简化）
float BFloat16::operator float() const {
    // 将 16 位 BF16 bits 左移 16 位，放到 32 位 FP32 的高 16 位
    uint32_t bits = static_cast<uint32_t>(mBits) << 16;
    float result;
    std::memcpy(&result, &bits, sizeof(result));
    return result;
}
```

BF16→FP32 转换是精确的（零扩展），不会丢失信息——因为 BF16 的所有值都是 FP32 的子集。

## 外部权重与 mmap

对于大型模型（如大语言模型），权重数据可能远大于模型结构，ONNX 支持将权重存储在外部文件中。onnx-tensorrt 通过 `mmap`（内存映射）读取外部权重：

```
外部权重加载流程:
  1. 加载 ModelProto（不含外部权重数据）
  2. 遇到引用外部数据的 initializer:
     a. 读取 external_data 字段（包含文件名、偏移量、长度）
     b. WeightsContext::mmap(path, size, offset)
     c. mmap 将文件的指定区域映射到内存
     d. ShapedWeights.values 指向 mmap 区域
  3. 解析完成后
     └─ mmap 区域在 WeightsContext 析构时 munmap
```

mmap 的优势：
- **惰性加载**：操作系统按需分页加载，不全部加载到内存
- **大模型支持**：支持超过内存大小的模型（靠虚拟内存和页面交换）
- **零拷贝**：直接使用 mmap 区域的数据作为 ShapedWeights.values

## 分步 API 与自定义权重注入

`loadModelProto()` + `loadInitializer()` + `parseModelProto()` 分步 API 允许在解析前替换权重：

```cpp
// 自定义权重注入示例
IParser* parser = createParser(*network, logger);

// 步骤 1：加载模型 proto（不解析）
parser->loadModelProto(modelData, modelSize);

// 步骤 2：注入自定义权重（如解密后的权重、量化后的权重）
std::vector<float> customWeightData = decryptWeights("weights.bin");
parser->loadInitializer("conv1.weight",
                         customWeightData.data(),
                         customWeightData.size() * sizeof(float));

// 步骤 3：执行解析（使用注入的权重而非模型中的原始权重）
parser->parseModelProto();
```

`loadInitializer()` 将权重数据注入到 ModelProto 的 initializer 中，覆盖原有的 initializer 条目或添加新条目。这适用于：
- **权重加密**：模型文件中的权重是加密的，运行时解密后注入
- **权重量化**：将 FP32 权重量化为 INT8/FP16 后注入
- **外部权重存储**：权重不在 ONNX 文件中，而是从数据库/远程加载
- **权重微调**：A/B 测试不同权重的效果

## Refittable 权重与 IParserRefitter

`IParserRefitter` 接口支持对已构建的引擎进行权重重拟合（refit），无需重新构建引擎：

```
Refit 流程:
  1. 构建引擎时标记权重为可 refit
  2. 创建 IRefitter 对象
  3. 创建 IParserRefitter
  4. refitFromBytes()/refitFromFile():
     a. 解析新模型的权重
     b. 通过 IRefitter 更新引擎中的权重
     c. IRefitterObserver 回调输出 RefitRecord
  5. refitCudaEngine() 完成更新
```

RefitRecord 包含 6 种 RefitTransformKind，描述权重如何从 ONNX 转换到 TRT 引擎：
- **IDENTITY**：直接映射（如卷积权重）
- **DOUBLE_TO_FLOAT**：双精度→单精度降级
- **BATCH_NORM_FOLD_SCALE/BIAS**：BatchNorm 折叠后的缩放/偏置
- **CONSTANT_NODE**：Constant 节点权重
- **CONSTANT_OF_SHAPE**：ConstantOfShape 权重

## 关联概念

- [解析管线详解](01-parsing-pipeline.md) — 理解 initializer 导入和 parseNode 中 UINT8 自动转换的位置
- [算子注册与插件扩展](02-op-registration-plugin.md) — 理解 NodeImporter 函数中权重分配的合约
- [错误处理与诊断](04-error-diagnostics.md) — 理解类型不支持错误的报告机制
- [解析器整体架构](00-overall-architecture.md) — 理解 TensorOrWeights 在数据流中的核心地位
