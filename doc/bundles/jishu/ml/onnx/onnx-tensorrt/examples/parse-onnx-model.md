---
type: example
title: "使用解析器加载 ONNX 模型到 TensorRT 网络：构建 engine 与推理"
description: "完整的 ONNX 模型加载流程：创建 Logger、Builder、Network、Parser，解析模型，配置 Builder 参数，构建 Engine，执行推理，含错误处理和动态形状配置"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/01-parsing-pipeline.md, ../concepts/04-error-diagnostics.md]
  references: [../references/parser-api.md, ../references/core-utilities.md]
---

# 使用解析器加载 ONNX 模型到 TensorRT 网络：构建 engine 与推理

## 目标

演示完整的 ONNX 模型推理流程：从磁盘加载 ONNX 模型，通过 onnx-tensorrt 解析到 TensorRT 网络定义，配置构建参数，构建优化引擎，在 GPU 上执行推理。

## 前提条件

- TensorRT 11.2+
- CUDA 11.0+
- 已编译安装 onnx-tensorrt（nvonnxparser 库）
- 一个有效的 ONNX 模型文件（如 ResNet50）

## 完整代码

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project(onnx_trt_inference LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找依赖
find_package(CUDA REQUIRED)
find_package(TensorRT REQUIRED)  # 需要配置 TensorRT_DIR

add_executable(onnx_inference main.cpp)

target_include_directories(onnx_inference PRIVATE
    ${CUDA_INCLUDE_DIRS}
    ${TensorRT_INCLUDE_DIRS}
)

target_link_libraries(onnx_inference PRIVATE
    ${CUDA_LIBRARIES}
    ${TensorRT_LIBRARIES}
    nvonnxparser      # onnx-tensorrt 解析器库
    cudart
)
```

### main.cpp

```cpp
#include "NvInfer.h"
#include "NvOnnxParser.h"
#include <cuda_runtime_api.h>
#include <fstream>
#include <iostream>
#include <memory>
#include <vector>
#include <algorithm>
#include <cassert>

// ============================================================
// 1. Logger 实现
//    TensorRT 和 Parser 都通过 ILogger 输出日志
// ============================================================
class Logger : public nvinfer1::ILogger {
public:
    void log(Severity severity, const char* msg) noexcept override {
        // 过滤 INFO 级别以下的消息（可根据需要调整）
        if (severity <= Severity::kWARNING) {
            std::cerr << "[TRT] " << msg << std::endl;
        }
    }
};

// ============================================================
// 2. RAII 资源管理辅助
//    使用智能指针自动管理 TensorRT 对象生命周期
// ============================================================
struct TRTDestroy {
    template <typename T>
    void operator()(T* obj) const {
        if (obj) obj->destroy();
    }
};

template <typename T>
using TRTUniquePtr = std::unique_ptr<T, TRTDestroy>;

// 读取文件到内存
std::vector<char> readFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    assert(file.good() && "Failed to open file");
    size_t size = file.tellg();
    std::vector<char> buffer(size);
    file.seekg(0);
    file.read(buffer.data(), size);
    return buffer;
}

// ============================================================
// 3. 主流程
// ============================================================
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <model.onnx>" << std::endl;
        return 1;
    }
    const std::string onnxPath = argv[1];

    Logger logger;

    // ----------------------------------------------------------
    // 步骤 1: 创建 Builder
    // ----------------------------------------------------------
    TRTUniquePtr<nvinfer1::IBuilder> builder(
        nvinfer1::createInferBuilder(logger));
    assert(builder && "Failed to create builder");

    // ----------------------------------------------------------
    // 步骤 2: 创建 Network Definition
    //          kEXPLICIT_BATCH 表示使用显式批量维度（ONNX 要求）
    // ----------------------------------------------------------
    const auto networkFlags = 0U
        | (1U << static_cast<uint32_t>(
            nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH));

    TRTUniquePtr<nvinfer1::INetworkDefinition> network(
        builder->createNetworkV2(networkFlags));
    assert(network && "Failed to create network");

    // ----------------------------------------------------------
    // 步骤 3: 创建 Parser 并解析 ONNX 模型
    // ----------------------------------------------------------
    TRTUniquePtr<nvonnxparser::IParser> parser(
        nvonnxparser::createParser(*network, logger));
    assert(parser && "Failed to create parser");

    // （可选）设置解析器标志
    // 例如启用插件覆盖:
    // parser->setFlag(nvonnxparser::OnnxParserFlag::kENABLE_PLUGIN_OVERRIDE);

    // 从文件解析 ONNX 模型
    // verbosity 级别: 0=静默, 1=错误, 2=警告+错误, ...
    bool parsed = parser->parseFromFile(onnxPath.c_str(),
                                        static_cast<int>(nvinfer1::ILogger::Severity::kWARNING));

    // ---- 错误处理 ----
    if (!parsed) {
        std::cerr << "Failed to parse ONNX model: " << onnxPath << std::endl;
        std::cerr << "Number of errors: " << parser->getNbErrors() << std::endl;
        for (int i = 0; i < parser->getNbErrors(); i++) {
            const nvonnxparser::IParserError* error = parser->getError(i);
            std::cerr << "  Error " << i << ":"
                      << " code=" << static_cast<int>(error->code())
                      << " node=" << error->nodeName()
                      << " op=" << error->nodeOperator()
                      << " desc=" << error->desc()
                      << " at " << error->file() << ":" << error->line()
                      << std::endl;
            // 如果错误发生在 LocalFunction 内部，打印调用栈
            for (int j = 0; j < error->localFunctionStackSize(); j++) {
                std::cerr << "    in function: " << error->localFunctionStack(j) << std::endl;
            }
        }
        return 1;
    }

    // ---- （可选）子图支持度查询 ----
    // 如果 supportsModelV2 返回 PARTIAL_SUPPORTED，可以查询哪些子图可用
    // 注意：parse 已经完成了完整构建，这里仅演示 API
    // int nbSubgraphs = parser->getNbSubgraphs();
    // for (int i = 0; i < nbSubgraphs; i++) {
    //     std::cout << "Subgraph " << i << " supported: "
    //               << parser->isSubgraphSupported(i) << std::endl;
    // }

    // ----------------------------------------------------------
    // 步骤 4: 配置 Builder 参数
    // ----------------------------------------------------------
    TRTUniquePtr<nvinfer1::IBuilderConfig> config(
        builder->createBuilderConfig());
    assert(config && "Failed to create builder config");

    // 设置最大工作空间大小（1GB）
    config->setMemoryPoolLimit(nvinfer1::MemoryPoolType::kWORKSPACE, 1U << 30);

    // 设置精度模式（按需启用）
    // config->setFlag(nvinfer1::BuilderFlag::kFP16);  // 启用 FP16
    // config->setFlag(nvinfer1::BuilderFlag::kINT8);  // 启用 INT8（需要校准器）

    // ---- 动态形状配置（如果模型有动态维度）----
    // 需要为每个动态输入创建 OptimizationProfile
    // 以下示例假设第一个输入是图像，形状为 [N, 3, H, W]，其中 N/H/W 动态
    int nbInputs = network->getNbInputs();
    if (nbInputs > 0) {
        nvinfer1::ITensor* input = network->getInput(0);
        nvinfer1::Dims inputDims = input->getDimensions();

        // 检查是否有动态维度（-1）
        bool hasDynamicDims = false;
        for (int i = 0; i < inputDims.nbDims; i++) {
            if (inputDims.d[i] == -1) hasDynamicDims = true;
        }

        if (hasDynamicDims) {
            auto* profile = builder->createOptimizationProfile();

            // 设置最小/最优/最大形状
            // 以 [N, 3, H, W] 为例
            nvinfer1::Dims minDims = inputDims;
            nvinfer1::Dims optDims = inputDims;
            nvinfer1::Dims maxDims = inputDims;

            // 批量维度
            if (inputDims.d[0] == -1) {
                minDims.d[0] = 1;
                optDims.d[0] = 4;
                maxDims.d[0] = 8;
            }
            // 空间维度 H, W
            for (int i = 2; i < inputDims.nbDims; i++) {
                if (inputDims.d[i] == -1) {
                    minDims.d[i] = 224;
                    optDims.d[i] = 224;
                    maxDims.d[i] = 224;
                }
            }

            profile->setDimensions(input->getName(),
                                   nvinfer1::OptProfileSelector::kMIN, minDims);
            profile->setDimensions(input->getName(),
                                   nvinfer1::OptProfileSelector::kOPT, optDims);
            profile->setDimensions(input->getName(),
                                   nvinfer1::OptProfileSelector::kMAX, maxDims);

            config->addOptimizationProfile(profile);
        }
    }

    // ---- （可选）版本兼容引擎：序列化插件 ----
    // int nbVCPlugins = parser->getNbVCPluginLibraries();
    // if (nbVCPlugins > 0) {
    //     std::vector<std::string> vcPluginPaths(nbVCPlugins);
    //     for (int i = 0; i < nbVCPlugins; i++) {
    //         vcPluginPaths[i] = parser->getVCPluginLibrary(i);
    //         std::cout << "VC Plugin: " << vcPluginPaths[i] << std::endl;
    //     }
    //     // 将插件序列化到引擎中（版本兼容模式）
    //     config->setPluginsToSerialize(
    //         const_cast<const char**>(vcPluginPaths.data()), nbVCPlugins);
    // }

    // ----------------------------------------------------------
    // 步骤 5: 构建 Engine
    // ----------------------------------------------------------
    std::cout << "Building TensorRT engine (this may take a while)..." << std::endl;

    TRTUniquePtr<nvinfer1::IHostMemory> engineData(
        builder->buildSerializedNetwork(*network, *config));
    assert(engineData && "Failed to build engine");

    std::cout << "Engine built successfully! Size: "
              << engineData->size() / (1024*1024) << " MB" << std::endl;

    // ----------------------------------------------------------
    // 步骤 6: 反序列化 Engine 用于推理
    //          （实际部署中通常将 engineData 保存到文件，
    //           运行时直接加载）
    // ----------------------------------------------------------
    TRTUniquePtr<nvinfer1::IRuntime> runtime(
        nvinfer1::createInferRuntime(logger));
    assert(runtime && "Failed to create runtime");

    // ---- （可选）加载插件库 ----
    // 如果引擎使用了自定义插件，需要在反序列化前加载
    // for (const auto& pluginPath : vcPluginPaths) {
    //     runtime->getPluginRegistry().loadLibrary(pluginPath.c_str());
    // }

    TRTUniquePtr<nvinfer1::ICudaEngine> engine(
        runtime->deserializeCudaEngine(engineData->data(), engineData->size()));
    assert(engine && "Failed to deserialize engine");

    // ----------------------------------------------------------
    // 步骤 7: 保存 Engine 到文件（可选）
    // ----------------------------------------------------------
    // {
    //     std::ofstream engineFile("model.engine", std::ios::binary);
    //     engineFile.write(static_cast<const char*>(engineData->data()),
    //                      engineData->size());
    // }

    // ----------------------------------------------------------
    // 步骤 8: 执行推理
    // ----------------------------------------------------------
    TRTUniquePtr<nvinfer1::IExecutionContext> execContext(
        engine->createExecutionContext());
    assert(execContext && "Failed to create execution context");

    // ---- 设置实际输入形状（动态形状时必须）----
    // 例如：使用 batch=1 的输入
    // nvinfer1::Dims actualDims = inputDims;
    // actualDims.d[0] = 1;
    // execContext->setInputShape(input->getName(), actualDims);

    // ---- 分配设备内存 ----
    int nbIOTensors = engine->getNbIOTensors();
    std::vector<void*> deviceBuffers(nbIOTensors);
    std::vector<size_t> bufferSizes(nbIOTensors);

    for (int i = 0; i < nbIOTensors; i++) {
        const char* tensorName = engine->getIOTensorName(i);
        nvinfer1::Dims dims = execContext->getTensorShape(tensorName);
        nvinfer1::DataType dtype = engine->getTensorDataType(tensorName);

        // 计算元素数量
        size_t elemCount = 1;
        for (int d = 0; d < dims.nbDims; d++) {
            elemCount *= (dims.d[d] == -1 ? 1 : dims.d[d]);
        }

        // 计算字节大小（简化：按数据类型大小）
        size_t elemSize = 4;  // 默认 float32
        switch (dtype) {
            case nvinfer1::DataType::kHALF:  elemSize = 2; break;
            case nvinfer1::DataType::kINT8:  elemSize = 1; break;
            case nvinfer1::DataType::kINT32: elemSize = 4; break;
            case nvinfer1::DataType::kBOOL:  elemSize = 1; break;
            // FP32 和其他默认为 4 字节
        }
        bufferSizes[i] = elemCount * elemSize;

        // 分配 GPU 内存
        cudaMalloc(&deviceBuffers[i], bufferSizes[i]);
    }

    // ---- 准备输入数据 ----
    // 实际使用时从图像预处理、数据加载等获取输入
    // 这里用全零数据作为示例
    int inputIdx = 0;  // 第一个 IO tensor 通常是输入
    std::vector<char> inputData(bufferSizes[inputIdx], 0);
    cudaMemcpy(deviceBuffers[inputIdx], inputData.data(),
               bufferSizes[inputIdx], cudaMemcpyHostToDevice);

    // ---- 设置 tensor 地址 ----
    for (int i = 0; i < nbIOTensors; i++) {
        const char* tensorName = engine->getIOTensorName(i);
        execContext->setTensorAddress(tensorName, deviceBuffers[i]);
    }

    // ---- 异步推理 ----
    cudaStream_t stream;
    cudaStreamCreate(&stream);

    bool inferSuccess = execContext->enqueueV3(stream);
    assert(inferSuccess && "Inference failed");

    // ---- 拷贝输出结果回主机 ----
    int outputIdx = nbIOTensors - 1;  // 最后一个通常是输出
    std::vector<char> outputData(bufferSizes[outputIdx]);
    cudaMemcpyAsync(outputData.data(), deviceBuffers[outputIdx],
                    bufferSizes[outputIdx], cudaMemcpyDeviceToHost, stream);

    cudaStreamSynchronize(stream);

    // ---- 处理输出 ----
    // 将 outputData reinterpret_cast 为对应类型（float* 等）
    // 进行后处理（softmax、NMS 等）
    const float* output = reinterpret_cast<const float*>(outputData.data());
    // ... 后处理逻辑 ...

    std::cout << "Inference completed successfully!" << std::endl;

    // ----------------------------------------------------------
    // 步骤 9: 清理资源
    // ----------------------------------------------------------
    cudaStreamDestroy(stream);
    for (int i = 0; i < nbIOTensors; i++) {
        cudaFree(deviceBuffers[i]);
    }

    std::cout << "Done." << std::endl;
    return 0;
}
```

## 编译与运行

```bash
# 编译
mkdir build && cd build
cmake .. -DTensorRT_DIR=/path/to/TensorRT/cmake
make -j$(nproc)

# 运行
./onnx_inference model.onnx
```

## 要点解析

### 1. 为什么必须使用 kEXPLICIT_BATCH？

```cpp
const auto networkFlags =
    1U << static_cast<uint32_t>(
        nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);
```

ONNX 模型使用显式批量维度（即批量大小是输入形状的第一维，如 `[N, 3, 224, 224]`）。TensorRT 的旧 API 使用隐式批量（形状为 `[3, 224, 224]`，批量在运行时指定），但 onnx-tensorrt 要求使用显式批量模式。不设置此 flag 会导致解析失败。

### 2. parseFromFile 与 parse 的选择

| 方法 | 使用场景 |
|------|---------|
| `parseFromFile(path, verbosity)` | 模型文件在磁盘上，最简单 |
| `parse(data, size)` | 模型已经在内存中（如从网络下载、解密后） |
| 分步 API | 需要在解析前注入自定义权重（见下文） |

### 3. 分步 API：自定义权重注入

```cpp
// 如果需要在解析前替换权重（如加密权重解密）
parser->loadModelProto(modelData, modelSize);

// 注入自定义权重
std::vector<float> decryptedWeights = decrypt("conv1.weight.enc");
parser->loadInitializer("conv1.weight",
                         decryptedWeights.data(),
                         decryptedWeights.size() * sizeof(float));

// 执行解析
parser->parseModelProto();
```

### 4. 动态形状配置要点

- 使用 `createOptimizationProfile()` 为动态输入设置 min/opt/max 形状
- `min` 是可接受的最小形状（影响内存分配）
- `opt` 是 Builder 优化的目标形状（性能最优的形状）
- `max` 是可接受的最大形状（影响内存分配）
- 推理时通过 `setInputShape()` 设置实际运行时形状
- 多个 profile 可通过 `addOptimizationProfile()` 添加（需配合 `setOptimizationProfileAsync()` 使用）

### 5. 错误处理最佳实践

```cpp
// 解析失败时遍历所有错误，而不仅仅是第一个
if (!parsed) {
    for (int i = 0; i < parser->getNbErrors(); i++) {
        auto* error = parser->getError(i);
        // 打印完整上下文：节点名、操作类型、描述、源码位置
        std::cerr << error->nodeName() << " (" << error->nodeOperator()
                  << "): " << error->desc() << std::endl;
    }
}
```

### 6. supportsModelV2 预检流程

在实际生产环境中，可以在构建引擎前先进行支持度预检：

```cpp
// 创建临时网络和解析器做预检
auto tempNetwork = builder->createNetworkV2(networkFlags);
auto tempParser = nvonnxparser::createParser(*tempNetwork, logger);

// 从内存预检（不构建引擎）
auto modelData = readFile(onnxPath);
bool supported = tempParser->supportsModelV2(modelData.data(), modelData.size());

if (!supported) {
    // 检查不支持的子图
    for (int i = 0; i < tempParser->getNbSubgraphs(); i++) {
        if (!tempParser->isSubgraphSupported(i)) {
            int nbNodes = tempParser->getSubgraphNodes(i, nullptr, 0);
            std::vector<int> nodes(nbNodes);
            tempParser->getSubgraphNodes(i, nodes.data(), nbNodes);
            std::cerr << "Unsupported subgraph " << i
                      << " has " << nbNodes << " nodes" << std::endl;
        }
    }
    // 决定：是否加载额外插件、是否需要模型修改等
}
```

## 延伸阅读

- 学习插件开发：见 [自定义插件处理不支持的算子](custom-plugin.md)
- 理解解析管线：[解析管线详解](../concepts/01-parsing-pipeline.md)
- 理解错误处理：[错误处理与诊断](../concepts/04-error-diagnostics.md)
- 理解权重管理：[权重内存模型](../concepts/03-weights-memory-model.md)
