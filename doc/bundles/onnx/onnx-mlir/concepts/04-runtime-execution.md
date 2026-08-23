---
type: concept
title: "运行时执行模型：ExecutionSession 与自描述共享库"
description: "ONNX-MLIR 的运行时模型——run_main_graph 统一 C ABI、ExecutionSession 动态加载共享库、OMTensor/OMTensorList 张量容器、自描述共享库的元数据查询机制、多入口点与 tag 符号管理、信号处理与错误恢复"
sources:
  references: [../references/dialects-runtime.md]
  facts: [F-025, F-026, F-027, F-028, F-029]
---

# 运行时执行模型：ExecutionSession 与自描述共享库

## 核心理解（I-03 洞察）

ONNX-MLIR 的编译产物不是传统深度学习编译器那样的"黑盒二进制+元数据文件"组合，而是一个**自描述的共享库**。单个 `.so`/`.dll`/`.dylib` 文件包含：
1. 模型推理代码（`run_main_graph` 函数）
2. 模型签名（输入/输出名称、类型、维度）
3. 编译信息（编译器版本、优化级别、目标架构）
4. 多入口点发现机制

运行时通过 `dlopen`/`LoadLibrary` 动态加载共享库，通过 `dlsym`/`GetProcAddress` 查找符号，不需要编译时生成的头文件，不需要额外的 JSON 元数据文件。这种"一个文件即部署单元"的设计使得模型热加载和服务化部署极其简洁。

## 运行时架构分层

```
┌──────────────────────────────────────────────────────────────┐
│                  多语言绑定层                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Python   │  │ C++      │  │ C        │  │ Java     │     │
│  │ PyExecutionSession│ExecutionSession│OnnxMlirRuntime│JNI │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
├───────┼─────────────┼─────────────┼─────────────┼───────────┤
│       │             │   核心运行时  │             │           │
│       └─────────────┴──────┬──────┴─────────────┘           │
│                            │                                 │
│               ┌────────────┴────────────┐                   │
│               │   ExecutionSession      │                   │
│               │  (C++ 运行时核心类)      │                   │
│               │                         │                   │
│               │ · 动态库加载(dlopen)     │                   │
│               │ · 符号解析(dlsym)        │                   │
│               │ · 入口点切换             │                   │
│               │ · 信号处理(runDebug)     │                   │
│               └────────────┬────────────┘                   │
│                            │                                 │
│               ┌────────────┴────────────┐                   │
│               │   OMTensor /            │                   │
│               │   OMTensorList          │                   │
│               │  (张量数据结构)          │                   │
│               └────────────┬────────────┘                   │
├────────────────────────────┼─────────────────────────────────┤
│              操作系统动态链接器                                │
│         dlopen/dlsym (POSIX)                                 │
│         LoadLibrary/GetProcAddress (Windows)                │
├──────────────────────────────────────────────────────────────┤
│              编译产物（自描述共享库）                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 导出符号：                                            │    │
│  │ · run_main_graph(OMTensorList*) → OMTensorList*     │    │
│  │ · run_main_graph_<tag>(OMTensorList*) → OMTensorList*│    │
│  │ · omQueryEntryPoints() → const char**               │    │
│  │ · omInputSignature(const char*) → const char*       │    │
│  │ · omOutputSignature(const char*) → const char*      │    │
│  │ · omCompilationInfo() → const char*                 │    │
│  │ · omInstrumentPrint() （可选）                       │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 统一 C ABI：run_main_graph

所有编译后的模型导出**统一的 C 函数签名**（F-025）：

```c
#include "OnnxMlirRuntime.h"

// 主入口点
OMTensorList *run_main_graph(OMTensorList *input_tensors);

// 多入口点/带tag的变体（由 --tag 编译选项生成）
OMTensorList *run_main_graph_<tag>(OMTensorList *input_tensors);
```

这个统一 ABI 意味着：
- **任何模型**都可以用同一个运行时加载——不需要为每个模型生成特定的头文件
- **任何语言**只要支持 C FFI 就可以调用模型推理
- **多模型**可以在同一进程中加载（通过 tag 机制避免符号冲突）

### 函数签名设计

`run_main_graph` 接收一个 `OMTensorList*`（输入张量列表），返回一个 `OMTensorList*`（输出张量列表）。输入列表中的张量顺序和类型必须匹配模型签名。

## OMTensor / OMTensorList：张量数据结构

`OMTensor` 是运行时张量的核心 C 结构（F-029），描述张量的元信息和数据指针：

```c
typedef struct OMTensor {
  int64_t *shape;        // 维度数组（如 [1, 3, 224, 224]）
  int64_t  rank;         // 秩（维度数，如 4）
  void    *dataPtr;      // 数据指针（指向实际数据内存）
  int64_t  dtype;        // 数据类型（ONNX_TYPE_FLOAT, ONNX_TYPE_INT64 等）
  int64_t  owning;       // 是否拥有数据所有权（1=runtime分配,0=外部借用）
  char    *name;         // 张量名称（可选）
  // ... 内部字段
} OMTensor;
```

`OMTensorList` 是 `OMTensor` 指针的数组容器：

```c
typedef struct OMTensorList {
  OMTensor **tensors;    // OMTensor 指针数组
  int64_t    size;       // 张量数量
} OMTensorList;
```

### 核心 C API

```c
// 创建张量（runtime 分配数据内存，owning=1）
OMTensor *omTensorCreate(int64_t *shape, int64_t rank,
                         OM_DATA_TYPE dtype, void *data, int64_t owning);

// 创建张量列表
OMTensorList *omTensorListCreate(OMTensor **tensors, int64_t size);
OMTensorList *omTensorListCreateWithOwnership(OMTensor **tensors, int64_t size,
                                              int64_t owning);

// 销毁
void omTensorDestroy(OMTensor *tensor);
void omTensorListDestroy(OMTensorList *list);

// 访问器
void *omTensorGetDataPtr(OMTensor *tensor);
int64_t *omTensorGetShape(OMTensor *tensor);
int64_t omTensorGetRank(OMTensor *tensor);
OM_DATA_TYPE omTensorGetDataType(OMTensor *tensor);

// 列表访问
OMTensor *omTensorListGetOmtByIndex(OMTensorList *list, int64_t index);
int64_t omTensorListGetSize(OMTensorList *list);
```

### 内存所有权

`owning` 字段决定内存管理策略：
- `owning=1`：OMTensor 拥有数据内存，`omTensorDestroy` 会释放数据
- `owning=0`：数据由外部管理（如 numpy 数组），OMTensor 只是包装器，不释放数据

Python 绑定时通常使用 `owning=0`（包装 numpy 数组，避免内存拷贝）。

## ExecutionSession：C++ 运行时核心

`ExecutionSession` 类是 C++ 运行时的核心类（F-026），封装了动态库加载、符号解析和推理执行：

```cpp
#include "ExecutionSession.hpp"
using namespace onnx_mlir;

// 创建会话：加载共享库
ExecutionSession session("./model.so");

// 执行推理
std::vector<OMTensor*> inputs = { ... };
std::vector<OMTensor*> outputs = session.run(inputs);
```

### 动态库加载机制

`ExecutionSession` 构造时执行：

1. **加载共享库**：
   - POSIX：`dlopen(sharedLibPath, RTLD_NOW | RTLD_LOCAL)`
   - Windows：`llvm::sys::DynamicLibrary::getPermanentLibrary()`（内部 LoadLibrary）

2. **查找固定符号**（F-026）：

| 符号 | dlsym 查找 | 函数类型 | 用途 |
|------|-----------|----------|------|
| `omQueryEntryPoints` | 必选 | `const char** (*)()` | 获取所有入口点名 |
| `omInputSignature` | 必选 | `const char* (*)(const char*)` | 获取指定入口点的输入签名 JSON |
| `omOutputSignature` | 必选 | `const char* (*)(const char*)` | 获取指定入口点的输出签名 JSON |
| `omCompilationInfo` | 必选 | `const char* (*)()` | 获取编译信息 JSON |
| `run_main_graph` | 默认入口点 | `OMTensorList* (*)(OMTensorList*)` | 推理函数 |
| `omInstrumentPrint` | 可选 | `void (*)()` | 插桩数据打印 |

3. **入口点初始化**：默认入口点为 `"run_main_graph"`，可通过 `setEntryPoint()` 切换

### 多入口点支持

一个编译后的模型可以包含多个入口点（F-027）。通过编译时指定多个 `--tag` 选项生成。

```cpp
// 查询所有入口点
std::vector<std::string> entryPoints = session.queryEntryPoints();
// 返回：["run_main_graph", "run_main_graph_train", "run_main_graph_eval"]

// 切换入口点
session.setEntryPoint("run_main_graph_train");

// 获取当前入口点的签名
std::string inputSig = session.inputSignature();
std::string outputSig = session.outputSignature();
```

### JSON 自描述签名

`omInputSignature()` 和 `omOutputSignature()` 返回 JSON 格式的张量签名（F-027），包含类型、维度和名称：

```json
// 输入签名示例（ResNet50）
[
  {"name": "input", "type": "float32", "dims": [1, 3, 224, 224]},
  {"name": "image_shape", "type": "int64", "dims": [2]}
]

// 输出签名示例
[
  {"name": "output", "type": "float32", "dims": [1, 1000]}
]
```

`omCompilationInfo()` 返回编译信息：

```json
{
  "compiler_version": "0.0.1",
  "optimization_level": "O3",
  "target_triple": "x86_64-linux-gnu",
  "target_arch": "x86-64",
  "accelerator": "NONE",
  "onnx_opset_version": 17
}
```

这些 JSON 签名使得运行时可以在**没有模型定义文件**的情况下验证输入、构建输出张量，实现真正的"一个 .so 文件即完整部署单元"。

### 信号处理与错误恢复

`ExecutionSession` 提供 `runDebug()` 方法（F-028），在 POSIX 系统上支持信号处理器：

```cpp
try {
  auto outputs = session.runDebug(inputs);
} catch (const ExecutionSessionException &e) {
  // 模型执行崩溃（SIGSEGV/SIGBUS/SIGFPE/SIGILL/SIGABRT）
  // 注意：信号处理后内存可能已损坏，不建议继续使用该会话
  std::cerr << "Model execution crashed: " << e.what() << std::endl;
}
```

实现机制：
- `runDebug()` 在推理前注册信号处理器（`sigaction`）
- 使用 `setjmp` 设置恢复点
- 如果信号被捕获，通过 `longjmp` 回到恢复点并抛出 `ExecutionSessionException`
- 标记会话内存可能已损坏

⚠️ 警告：信号处理后，共享库中的全局状态可能不一致，应销毁会话并重新加载。

### Tag 符号管理

多模型并发加载时，必须使用 `--tag` 选项为每个模型指定唯一符号后缀（I-03 行动建议）：

```bash
# 编译两个模型，指定不同 tag
onnx-mlir --tag=resnet -O3 resnet50.onnx -o resnet50
onnx-mlir --tag=bert   -O3 bert.onnx     -o bert

# 两个模型的符号分别为：
# libre50net.so: run_main_graph_resnet, omQueryEntryPoints_resnet, ...
# libbert.so:    run_main_graph_bert,   omQueryEntryPoints_bert,   ...
```

编译器在 `CompilerUtils.cpp` 中包含 tag 验证逻辑（F-026 相关），确保 tag 是合法的 C 标识符。如果不指定 tag，所有模型导出相同符号名，多模型加载时会发生符号冲突。

## Python 运行时

Python 绑定通过 `PyExecutionSession` 类提供（在 `src/Runtime/PyExecutionSession.hpp`），底层使用 C API，与 numpy 零拷贝互操作：

```python
from PyRuntime import OMExecutionSession
import numpy as np

# 加载模型
session = OMExecutionSession("./model.so")

# 准备输入（numpy 数组，owning=0 零拷贝包装）
input_tensor = np.random.randn(1, 3, 224, 224).astype(np.float32)

# 推理（输入/输出均为 numpy 数组列表）
outputs = session.run([input_tensor])

# 输出
predictions = outputs[0]  # numpy array, shape (1, 1000)
```

Python 运行时还支持：
- `session.signature()`：获取输入/输出签名
- `session.entry_points()`：获取所有入口点
- `session.set_entry_point(name)`：切换入口点

## C API 直接使用

对于极简部署场景（嵌入式、C 环境），可以不链接 ExecutionSession C++ 类，直接使用 C API：

```c
#include <dlfcn.h>
#include "OnnxMlirRuntime.h"

// 手动加载
void *handle = dlopen("./model.so", RTLD_NOW);
typedef OMTensorList* (*run_fn)(OMTensorList*);
run_fn run_main_graph = (run_fn)dlsym(handle, "run_main_graph");

// 创建输入
int64_t shape[] = {1, 3, 224, 224};
float *data = malloc(1*3*224*224 * sizeof(float));
OMTensor *input = omTensorCreate(shape, 4, ONNX_TYPE_FLOAT, data, 0);
OMTensor *inputs[] = {input};
OMTensorList *inputList = omTensorListCreate(inputs, 1);

// 推理
OMTensorList *outputList = run_main_graph(inputList);

// 获取结果
OMTensor *output = omTensorListGetOmtByIndex(outputList, 0);
float *result = (float*)omTensorGetDataPtr(output);

// 清理
omTensorListDestroy(outputList);
omTensorListDestroy(inputList);
dlclose(handle);
```

## Java 运行时

当使用 `EmitJNI` 输出目标时，编译器额外生成 JNI 包装层和 Java 类：
1. 编译模型到共享库（`libmodel.so`）
2. 生成 JNI C 包装代码（`model_jni.c`）
3. 编译 JNI 包装并链接到共享库（`libmodeljni.so`）
4. 编译 Java 类并打包为 jar（`model.jar`）

Java 应用通过 JNI 调用推理，使用 `com.ibm.onnx_mlir.OMTensor` 和 `com.ibm.onnx_mlir.OMModel` 类。

## 部署优势

自描述共享库模型带来了显著的部署优势：

| 特性 | ONNX-MLIR | 传统方案（ONNX Runtime/TensorRT） |
|------|-----------|----------------------------------|
| 部署单元 | 单个 .so/.dll 文件 | engine 文件 + 运行时库 + 元数据 |
| 调用方式 | C ABI 直接调用 | 通过运行时 API 加载和执行 |
| 热加载 | dlopen/dlclose 即可 | 需要运行时实例管理 |
| 签名发现 | 内嵌 JSON 查询函数 | 需要额外元数据文件或编译时 header |
| 多模型 | tag 符号后缀隔离 | 需要独立运行时实例 |
| 跨语言 | C FFI 统一 | 各语言绑定维护成本 |
| 性能 | 原生代码，无解释开销 | 运行时解释/内核调度开销 |

## 关联概念

- [ONNX-MLIR 整体架构](00-overall-architecture.md) — 运行时在整体架构中的位置
- [Dialect 转换管线](03-lowering-pipeline.md) — 了解运行时函数如何在 KrnlToLLVM 阶段生成
- [编译选项体系与性能调优](05-compiler-options.md) — 了解 tag 选项和优化级别对运行时的影响
- [编译 ONNX 模型为共享库](../examples/compile-model.md) — 端到端编译和推理示例
