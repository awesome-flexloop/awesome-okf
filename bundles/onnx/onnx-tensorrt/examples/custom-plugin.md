---
type: example
title: "自定义插件处理不支持的算子"
description: "为 onnx-tensorrt 编写自定义 TensorRT 插件、注册 IPluginCreator、通过 FallbackPluginImporter 自动导入、构建版本兼容引擎的完整流程"
sources:
  concepts: [../concepts/02-op-registration-plugin.md, ../concepts/03-weights-memory-model.md, ../concepts/04-error-diagnostics.md]
  references: [../references/parser-api.md, ../references/core-utilities.md]
---

# 自定义插件处理不支持的算子

## 目标

当 ONNX 模型包含 onnx-tensorrt 不支持的算子时（UNSUPPORTED_NODE 错误），编写一个 TensorRT 自定义插件来实现该算子，并通过 FallbackPluginImporter 机制让解析器自动识别和加载。

本文以一个简单的自定义算子 `MyCustomAdd`（带缩放因子的加法：`output = alpha * (input1 + input2)`）为例，演示完整流程。

## 插件实现的架构

```
┌─────────────────────────────────────────────────────────────┐
│                  自定义插件体系                              │
├─────────────────────────────────────────────────────────────┤
│  IPluginV3OneNetwork/Builder/Ready/Runtime                   │
│    └─ MyCustomAddPlugin (插件实现)                          │
│       ├─ supportsFormatCombination()                        │
│       ├─ configurePlugin()                                  │
│       ├─ enqueue() (GPU kernel)                             │
│       └─ getOutputShapes()                                  │
│                                                             │
│  IPluginCreatorV3One                                        │
│    └─ MyCustomAddPluginCreator (插件工厂)                   │
│       ├─ getPluginName() → "MyCustomAdd"                    │
│       ├─ getPluginVersion() → "1"                           │
│       ├─ getPluginNamespace() → "custom_namespace"          │
│       ├─ createPlugin() (从属性创建)                        │
│       └─ deserializePlugin() (从序列化数据恢复)             │
│                                                             │
│  注册: REGISTER_TENSORRT_PLUGIN(MyCustomAddPluginCreator)   │
│    └─ 静态初始化 → PluginRegistry 全局注册                  │
│                                                             │
│  ONNX 节点:                                                  │
│    node {                                                    │
│      input: "a"  input: "b"  output: "c"                    │
│      op_type: "MyCustomAdd"                                 │
│      attribute { name: "alpha" f: 0.5 }                     │
│      attribute { name: "plugin_namespace" s: "custom_ns" }  │
│    }                                                         │
│    └─ FallbackPluginImporter 查找 → 创建插件                │
└─────────────────────────────────────────────────────────────┘
```

## 完整代码

### my_custom_add_plugin.cu

```cpp
#include "NvInfer.h"
#include "NvInferRuntime.h"
#include "NvInferPluginUtils.h"
#include <cuda_runtime.h>
#include <cstring>
#include <vector>
#include <string>
#include <cassert>
#include <iostream>

using namespace nvinfer1;
using namespace nvinfer1::plugin;

// ============================================================
// 1. 插件实现：MyCustomAddPlugin
//    实现 output = alpha * (input1 + input2)
//    使用 IPluginV3One 接口（最新版插件 API）
// ============================================================
class MyCustomAddPlugin : public IPluginV3,
                          public IPluginV3OneBuild,
                          public IPluginV3OneRuntime {
public:
    // ---- 构造/析构 ----
    MyCustomAddPlugin(float alpha) : mAlpha(alpha) {}
    MyCustomAddPlugin(float alpha, int32_t batchSize) : mAlpha(alpha), mBatchSize(batchSize) {}

    // 从序列化数据构造
    MyCustomAddPlugin(const void* data, size_t length) {
        const char* d = static_cast<const char*>(data);
        std::memcpy(&mAlpha, d, sizeof(mAlpha));
        d += sizeof(mAlpha);
        std::memcpy(&mBatchSize, d, sizeof(mBatchSize));
    }

    ~MyCustomAddPlugin() override = default;

    // ---- IPluginV3 接口 ----
    IPluginCapability* getCapabilityInterface(PluginCapabilityType type) noexcept override {
        if (type == PluginCapabilityType::kBUILD) return static_cast<IPluginV3OneBuild*>(this);
        if (type == PluginCapabilityType::kRUNTIME) return static_cast<IPluginV3OneRuntime*>(this);
        return nullptr;
    }

    IPluginV3* clone() noexcept override {
        auto* p = new MyCustomAddPlugin(mAlpha, mBatchSize);
        p->mInputDims[0] = mInputDims[0];
        p->mInputDims[1] = mInputDims[1];
        return p;
    }

    AsciiChar const* getPluginNamespace() const noexcept override {
        return mNamespace.c_str();
    }

    void setPluginNamespace(AsciiChar const* ns) noexcept override {
        mNamespace = ns;
    }

    // ---- IPluginV3OneBuild 接口 ----
    int32_t getNbOutputs() const noexcept override { return 1; }

    int32_t configurePlugin(DynamicPluginTensorDesc const* in, int32_t nbInputs,
                            DynamicPluginTensorDesc const* out, int32_t nbOutputs) noexcept override {
        assert(nbInputs == 2 && nbOutputs == 1);
        // 保存输入维度
        mInputDims[0] = in[0].desc.dims;
        mInputDims[1] = in[1].desc.dims;
        return 0;
    }

    bool supportsFormatCombination(int32_t pos,
                                    DynamicPluginTensorDesc const* inOut,
                                    int32_t nbInputs,
                                    int32_t nbOutputs) noexcept override {
        // 支持线性格式、FP32 类型
        return inOut[pos].desc.format == TensorFormat::kLINEAR
            && inOut[pos].desc.type == DataType::kFLOAT;
    }

    int32_t getOutputDataTypes(DataType* outputTypes, int32_t nbOutputs,
                                DataType const* inputTypes, int32_t nbInputs) const noexcept override {
        outputTypes[0] = DataType::kFLOAT;
        return 0;
    }

    int32_t getOutputShapes(DimsExprs const* inputs, int32_t nbInputs,
                            DimsExprs const* shapeInputs, int32_t nbShapeInputs,
                            DimsExprs* outputs, int32_t nbOutputs,
                            IExprBuilder& exprBuilder) noexcept override {
        // 输出形状与第一个输入相同（广播语义简化版）
        outputs[0] = inputs[0];
        return 0;
    }

    size_t getWorkspaceSize(DynamicPluginTensorDesc const* inputs, int32_t nbInputs,
                            DynamicPluginTensorDesc const* outputs, int32_t nbOutputs) const noexcept override {
        return 0;  // 不需要额外工作空间
    }

    int32_t getTailSize() const noexcept override { return 0; }

    // ---- IPluginV3OneRuntime 接口 ----
    int32_t enqueue(PluginTensorDesc const* inputDesc, PluginTensorDesc const* outputDesc,
                    void const* const* inputs, void* const* outputs,
                    void* workspace, cudaStream_t stream) noexcept override;

    IPluginV3* attachToContext(IPluginResourceContext* context) noexcept override {
        return clone();
    }

    PluginFieldCollection const* getFieldsToSerialize() noexcept override {
        mDataToSerialize.clear();
        mDataToSerialize.emplace_back("alpha", &mAlpha, PluginFieldType::kFLOAT32, 1);
        mDataToSerialize.emplace_back("batch_size", &mBatchSize, PluginFieldType::kINT32, 1);
        mFCToSerialize.nbFields = mDataToSerialize.size();
        mFCToSerialize.fields = mDataToSerialize.data();
        return &mFCToSerialize;
    }

    size_t getSerializationSize() const noexcept override {
        return sizeof(mAlpha) + sizeof(mBatchSize);
    }

    void serialize(void* buffer) const noexcept override {
        char* d = static_cast<char*>(buffer);
        std::memcpy(d, &mAlpha, sizeof(mAlpha));
        d += sizeof(mAlpha);
        std::memcpy(d, &mBatchSize, sizeof(mBatchSize));
    }

    void terminate() noexcept override {}

private:
    float mAlpha = 1.0f;
    int32_t mBatchSize = 0;
    Dims mInputDims[2]{};
    std::string mNamespace = "custom_namespace";
    std::vector<PluginField> mDataToSerialize;
    PluginFieldCollection mFCToSerialize{};
};

// ---- GPU Kernel ----
__global__ void customAddKernel(const float* input1, const float* input2,
                                 float* output, float alpha, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        output[idx] = alpha * (input1[idx] + input2[idx]);
    }
}

int32_t MyCustomAddPlugin::enqueue(PluginTensorDesc const* inputDesc,
                                    PluginTensorDesc const* outputDesc,
                                    void const* const* inputs, void* const* outputs,
                                    void* workspace, cudaStream_t stream) noexcept {
    const float* input1 = static_cast<const float*>(inputs[0]);
    const float* input2 = static_cast<const float*>(inputs[1]);
    float* output = static_cast<float*>(outputs[0]);

    // 计算元素总数
    int n = 1;
    for (int i = 0; i < inputDesc[0].dims.nbDims; i++) {
        n *= inputDesc[0].dims.d[i];
    }

    int blockSize = 256;
    int gridSize = (n + blockSize - 1) / blockSize;
    customAddKernel<<<gridSize, blockSize, 0, stream>>>(input1, input2, output, mAlpha, n);

    return cudaGetLastError() == cudaSuccess ? 0 : -1;
}

// ============================================================
// 2. 插件工厂：MyCustomAddPluginCreator
//    负责创建插件实例，被 FallbackPluginImporter 使用
// ============================================================
class MyCustomAddPluginCreator : public IPluginCreatorV3One {
public:
    MyCustomAddPluginCreator() {
        mPluginAttributes.clear();
        mPluginAttributes.emplace_back("alpha", nullptr, PluginFieldType::kFLOAT32, 1);
        mFC.nbFields = mPluginAttributes.size();
        mFC.fields = mPluginAttributes.data();
    }

    AsciiChar const* getPluginName() const noexcept override {
        return "MyCustomAdd";
    }

    AsciiChar const* getPluginVersion() const noexcept override {
        return "1";
    }

    PluginFieldCollection const* getFieldNames() noexcept override {
        return &mFC;
    }

    IPluginV3* createPlugin(AsciiChar const* name,
                             PluginFieldCollection const* fc,
                             TensorRTPhase phase) noexcept override {
        float alpha = 1.0f;
        for (int i = 0; i < fc->nbFields; i++) {
            if (std::strcmp(fc->fields[i].name, "alpha") == 0) {
                alpha = *static_cast<const float*>(fc->fields[i].data);
            }
        }
        return new MyCustomAddPlugin(alpha);
    }

    IPluginV3* deserializePlugin(AsciiChar const* name,
                                  void const* serialData, size_t serialLength) noexcept override {
        return new MyCustomAddPlugin(serialData, serialLength);
    }

    void setPluginNamespace(AsciiChar const* ns) noexcept override {
        mNamespace = ns;
    }

    AsciiChar const* getPluginNamespace() const noexcept override {
        return mNamespace.c_str();
    }

private:
    std::string mNamespace = "custom_namespace";
    std::vector<PluginField> mPluginAttributes;
    PluginFieldCollection mFC{};
};

// ============================================================
// 3. 注册插件到 TensorRT PluginRegistry
//    静态初始化时自动注册，无需手动调用
// ============================================================
REGISTER_TENSORRT_PLUGIN(MyCustomAddPluginCreator);
```

### main.cpp（使用插件解析模型）

```cpp
#include "NvInfer.h"
#include "NvOnnxParser.h"
#include <iostream>
#include <memory>
#include <fstream>
#include <vector>
#include <cassert>

// Logger（同上一个示例）
class Logger : public nvinfer1::ILogger {
public:
    void log(Severity severity, const char* msg) noexcept override {
        if (severity <= Severity::kWARNING)
            std::cerr << "[TRT] " << msg << std::endl;
    }
};

struct TRTDestroy {
    template <typename T>
    void operator()(T* obj) const { if (obj) obj->destroy(); }
};
template <typename T>
using TRTUniquePtr = std::unique_ptr<T, TRTDestroy>;

// 关键：必须在创建 parser 之前链接插件库，
// 否则 REGISTER_TENSORRT_PLUGIN 的静态初始化不会执行！
// 如果插件编译为共享库，需要在运行时加载：
extern "C" void initMyCustomAddPlugin();  // 插件库中的初始化函数（可选）

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <model.onnx>" << std::endl;
        return 1;
    }

    Logger logger;

    // ---- 加载插件库（如果是动态链接）----
    // 方式 1：静态链接 → 插件已通过静态初始化注册，无需额外操作
    // 方式 2：动态加载 .so/.dll：
    // auto pluginRegistry = nvinfer1::getPluginRegistry();
    // pluginRegistry->loadLibrary("libmy_custom_add_plugin.so");

    // ---- 创建 builder/network/parser ----
    TRTUniquePtr<nvinfer1::IBuilder> builder(
        nvinfer1::createInferBuilder(logger));

    const auto flags = 1U << static_cast<uint32_t>(
        nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);
    TRTUniquePtr<nvinfer1::INetworkDefinition> network(
        builder->createNetworkV2(flags));

    TRTUniquePtr<nvonnxparser::IParser> parser(
        nvonnxparser::createParser(*network, logger));

    // ---- 解析模型 ----
    // FallbackPluginImporter 会在 PluginRegistry 中查找 "MyCustomAdd" 插件
    bool parsed = parser->parseFromFile(argv[1], 2);

    if (!parsed) {
        std::cerr << "Parse failed. Errors:" << std::endl;
        for (int i = 0; i < parser->getNbErrors(); i++) {
            auto* e = parser->getError(i);
            std::cerr << "  [" << static_cast<int>(e->code()) << "] "
                      << e->desc() << std::endl;
        }
        return 1;
    }

    // ---- 构建 engine ----
    TRTUniquePtr<nvinfer1::IBuilderConfig> config(
        builder->createBuilderConfig());
    config->setMemoryPoolLimit(nvinfer1::MemoryPoolType::kWORKSPACE, 1U << 30);

    // 重要：如果使用自定义插件，构建版本兼容引擎时必须序列化插件
    int nbVCPlugins = parser->getNbVCPluginLibraries();
    std::cout << "VC Plugin libraries needed: " << nbVCPlugins << std::endl;
    std::vector<std::string> vcPluginPaths(nbVCPlugins);
    for (int i = 0; i < nbVCPlugins; i++) {
        vcPluginPaths[i] = parser->getVCPluginLibrary(i);
        std::cout << "  " << vcPluginPaths[i] << std::endl;
    }

    if (nbVCPlugins > 0) {
        std::vector<const char*> vcPathCStrs(nbVCPlugins);
        for (int i = 0; i < nbVCPlugins; i++)
            vcPathCStrs[i] = vcPluginPaths[i].c_str();
        // 将插件序列化到引擎中，这样部署时无需单独加载插件库
        config->setPluginsToSerialize(vcPathCStrs.data(), nbVCPlugins);
    }

    TRTUniquePtr<nvinfer1::IHostMemory> engineData(
        builder->buildSerializedNetwork(*network, *config));
    assert(engineData && "Failed to build engine");

    std::cout << "Engine built successfully with custom plugin!" << std::endl;

    // ---- 保存 engine ----
    std::ofstream f("model_with_plugin.engine", std::ios::binary);
    f.write(static_cast<const char*>(engineData->data()), engineData->size());

    return 0;
}
```

### ONNX 模型中的插件节点定义

要让 onnx-tensorrt 通过 FallbackPluginImporter 识别自定义插件，ONNX 节点需要包含特定属性。以下是创建包含自定义插件节点的 ONNX 模型的 Python 示例：

```python
import onnx
from onnx import helper, TensorProto

# 创建自定义算子节点
# 方式 1：使用 plugin_namespace 属性（推荐）
node = helper.make_node(
    'MyCustomAdd',           # op_type 必须与 getPluginName() 返回值一致
    inputs=['input_a', 'input_b'],
    outputs=['output_c'],
    alpha=0.5,               # 自定义属性：缩放因子
    plugin_namespace='custom_namespace',  # 必须与 getPluginNamespace() 返回值一致
    # plugin_version='1',    # 可选，默认是 "1"
)

# 方式 2：设置 kENABLE_PLUGIN_OVERRIDE flag（不需要 plugin_namespace 属性）
# node = helper.make_node(
#     'MyCustomAdd',
#     inputs=['input_a', 'input_b'],
#     outputs=['output_c'],
#     alpha=0.5,
# )
# parser->setFlag(OnnxParserFlag::kENABLE_PLUGIN_OVERRIDE);

# 创建图和模型
input_a = helper.make_tensor_value_info('input_a', TensorProto.FLOAT, [1, 3, 224, 224])
input_b = helper.make_tensor_value_info('input_b', TensorProto.FLOAT, [1, 3, 224, 224])
output_c = helper.make_tensor_value_info('output_c', TensorProto.FLOAT, [1, 3, 224, 224])

graph = helper.make_graph([node], 'custom_add_model', [input_a, input_b], [output_c])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
onnx.save(model, 'custom_add_model.onnx')
```

## 要点解析

### 1. 插件查找的三级顺序

FallbackPluginImporter 在 PluginRegistry 中查找插件时使用三级顺序：

```
查找顺序:
  1. (plugin_name, plugin_version="1", plugin_namespace="custom_namespace")
     → 节点属性中指定 plugin_namespace 时使用
     
  2. (plugin_name, plugin_version="1", node.domain())
     → 如果 plugin_namespace 为空且 node.domain() 非空，使用 domain 作为 namespace
     
  3. 如果都找不到，且启用了 kENABLE_PLUGIN_OVERRIDE:
     → 在所有 namespace 中查找同名插件
```

**常见问题**：插件注册了 `custom_namespace` 但 ONNX 节点没有设置 `plugin_namespace` 属性，导致查找失败。务必确保 ONNX 节点的 `plugin_namespace` 属性值与插件 Creator 的 `getPluginNamespace()` 返回值一致。

### 2. 属性传递机制

ONNX 节点的属性通过 `PluginFieldCollection` 传递给 `createPlugin()`：

```cpp
// ONNX 节点属性:
//   alpha = 0.5 (float)
//   plugin_namespace = "custom_ns" (string，保留属性，不传给插件)

// createPlugin 收到的 fc:
//   fields[0] = { name: "alpha", data: &0.5f, type: kFLOAT32, length: 1 }

IPluginV3* createPlugin(AsciiChar const* name,
                         PluginFieldCollection const* fc,
                         TensorRTPhase phase) noexcept {
    float alpha = 1.0f;  // 默认值
    for (int i = 0; i < fc->nbFields; i++) {
        if (std::strcmp(fc->fields[i].name, "alpha") == 0) {
            alpha = *static_cast<const float*>(fc->fields[i].data);
        }
    }
    return new MyCustomAddPlugin(alpha);
}
```

注意：`plugin_namespace`、`plugin_version` 等保留属性会被解析器拦截，不会出现在 fc 中。

### 3. 权重管理注意事项

如果自定义算子有权重输入（如 Conv 中的 filter/bias），权重在传给插件时是 ShapedWeights 形式，需要在 enqueue 前确保权重数据在 GPU 上：

```cpp
// 如果权重是 ShapedWeights（CPU 内存），需要拷贝到 GPU
// onnx-tensorrt 的插件路径会自动处理 Constant 层的权重转换，
// 但如果直接在插件中操作权重，需要通过 WeightsContext 管理
```

### 4. 版本兼容引擎的插件序列化

构建 VC（Version Compatible）引擎时，必须序列化插件：

```cpp
// 获取解析过程中使用的插件库
int nbVCPlugins = parser->getNbVCPluginLibraries();
std::vector<const char*> paths(nbVCPlugins);
for (int i = 0; i < nbVCPlugins; i++)
    paths[i] = parser->getVCPluginLibrary(i);

// 将插件序列化到引擎
config->setPluginsToSerialize(paths.data(), nbVCPlugins);
```

这样部署时不需要单独分发插件 .so/.dll 文件，引擎文件已包含插件代码。

### 5. Creator 接口版本选择

FallbackPluginImporter 支持三种 Creator 版本：

| Creator 接口版本 | 对应插件类 | 适用场景 |
|-----------------|-----------|---------|
| IPluginCreator (V1) | IPluginV2/V2Ext/V2IOExt | 旧版插件，兼容性最好 |
| IPluginCreatorV3One | IPluginV3One | **推荐**，最新 API，支持动态形状 |
| IPluginCreatorV3Quick | IPluginV3Quick | 快速构建场景，限制较多 |

新插件推荐使用 IPluginV3One + IPluginCreatorV3One。

### 6. 静态链接 vs 动态链接

| 链接方式 | 注册时机 | 部署要求 |
|---------|---------|---------|
| 静态链接 | 程序启动时（静态初始化） | 插件代码在主程序中，无需额外文件 |
| 动态链接（.so/.dll） | 调用 `loadLibrary()` 时 | 需要分发插件库文件，或序列化到引擎中 |

如果使用动态链接，必须在创建 parser **之前**加载插件库：

```cpp
// 必须在创建 parser 之前！
auto registry = nvinfer1::getPluginRegistry();
registry->loadLibrary("libmy_custom_add_plugin.so");

// 然后再创建 parser
auto parser = nvonnxparser::createParser(*network, logger);
```

## 延伸阅读

- 理解插件分发机制：[算子注册与插件扩展](../concepts/02-op-registration-plugin.md)
- 理解权重在插件中的处理：[权重内存模型](../concepts/03-weights-memory-model.md)
- 基础解析流程：[使用解析器加载 ONNX 模型](parse-onnx-model.md)
- TensorRT 官方插件文档：参考 TensorRT Developer Guide 的 Plugin 章节
