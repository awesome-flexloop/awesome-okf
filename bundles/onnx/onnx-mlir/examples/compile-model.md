---
type: example
title: "编译 ONNX 模型为共享库并使用 Python 运行时推理"
description: "端到端示例：使用 onnx-mlir 命令行编译器将 ONNX 模型编译为自描述共享库，通过 Python 运行时（PyRuntime）加载并执行推理，包含输入验证、签名查询和结果解析"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/03-lowering-pipeline.md, ../concepts/04-runtime-execution.md, ../concepts/05-compiler-options.md]
  references: [../references/compiler-entry.md, ../references/dialects-runtime.md]
---

# 编译 ONNX 模型为共享库并使用 Python 运行时推理

## 目标

将一个 ONNX 模型（以简单的 MatMul+Add 模型为例）使用 `onnx-mlir` 编译器编译为自描述共享库（.so/.dll），然后使用 Python 运行时 `PyRuntime` 加载编译后的模型并执行推理。

## 前置条件

- 已安装 ONNX-MLIR（`onnx-mlir` 命令在 PATH 中）
- LLVM 工具链（`opt`、`llc`）在 PATH 中，版本与 ONNX-MLIR 编译时使用的 LLVM commit 匹配
- Python 3.8+，已编译安装 `PyRuntime` 模块（ONNX-MLIR build 目录下的 `build/lib/PyRuntime.so`）
- numpy 已安装

## 步骤 1：准备或获取 ONNX 模型

首先创建一个简单的 ONNX 模型用于演示。我们创建一个计算 `Y = X * W + B`（矩阵乘+偏置加）的模型：

```python
# create_model.py
import numpy as np
import onnx
from onnx import helper, TensorProto

# 定义张量形状：X(1, 4) @ W(4, 3) + B(3) -> Y(1, 3)
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 4])
W = helper.make_tensor_value_info("W", TensorProto.FLOAT, [4, 3])
B = helper.make_tensor_value_info("B", TensorProto.FLOAT, [3])
Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3])

# MatMul 节点
matmul_node = helper.make_node("MatMul", ["X", "W"], ["MatMul_out"], name="matmul")
# Add 节点
add_node = helper.make_node("Add", ["MatMul_out", "B"], ["Y"], name="add")

# 创建图和模型
graph = helper.make_graph(
    [matmul_node, add_node],
    "matmul_add_model",
    [X, W, B],  # 输入：X（动态数据）+ W（权重）+ B（偏置）
    [Y],
)

model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
model.ir_version = 8

# 保存模型
onnx.save(model, "matmul_add.onnx")
print("模型已保存到 matmul_add.onnx")
```

运行创建模型：

```bash
python create_model.py
```

> **说明**：实际使用中，你的 ONNX 模型可能来自训练框架导出（PyTorch `torch.onnx.export()`、TensorFlow `tf2onnx`、skl2onnx 等），不需要手动创建。

## 步骤 2：编译 ONNX 模型

使用 `onnx-mlir` 命令将 ONNX 模型编译为共享库：

```bash
# 基本编译：O3 优化，输出共享库（默认 EmitLib）
onnx-mlir -O3 matmul_add.onnx -o matmul_add

# 查看编译阶段输出
# [0/6]  0.00s ( 0.00s) ONNX To MLIR
# [1/6]  0.12s ( 0.12s) MLIR To LLVM IR
# [2/6]  0.15s ( 0.03s) LLVM BC To Object
# [3/6]  0.28s ( 0.13s) Object To Shared Lib
# 编译成功
```

编译产物：
- Linux：`matmul_add.so`
- macOS：`matmul_add.dylib`
- Windows：`matmul_add.dll`

### 编译选项说明

```bash
# 调试模式：O0 + 边界检查 + IR 打印
onnx-mlir -O0 --enable-bind-check --print-ir=after matmul_add.onnx -o matmul_add_dbg

# 针对本机 CPU 优化
onnx-mlir -O3 --march=native matmul_add.onnx -o matmul_add_native

# 交叉编译到 aarch64（需要 aarch64 工具链）
onnx-mlir -O3 --mtriple=aarch64-linux-gnu --march=armv8-a model.onnx -o model_arm64

# 多模型部署时指定 tag（避免符号冲突）
onnx-mlir -O3 --tag=model1 model1.onnx -o model1
onnx-mlir -O3 --tag=model2 model2.onnx -o model2

# 输出 LLVM IR（调试 lowering 结果）
onnx-mlir -O3 --EmitLLVMIR matmul_add.onnx -o matmul_add
# 生成 matmul_add.ll 文本文件

# 输出 MLIR（查看 Krnl/Affine 级 IR）
onnx-mlir -O3 --EmitMLIR matmul_add.onnx -o matmul_add
# 生成 matmul_add.mlir 文本文件
```

## 步骤 3：使用 Python 运行时执行推理

### 方式一：使用 PyRuntime（推荐）

```python
# run_inference.py
import sys
import numpy as np

# 将 ONNX-MLIR build 目录加入 Python 路径
# 实际路径根据你的 ONNX-MLIR build 目录调整
sys.path.insert(0, "/path/to/onnx-mlir/build/lib")
from PyRuntime import OMExecutionSession

# 1. 加载编译后的模型
session = OMExecutionSession("./matmul_add.so")

# 2. 查询模型签名（自描述特性）
print("输入签名:", session.signature)
# 输入签名包含输入/输出的名称、类型和维度信息

# 查询入口点
print("可用入口点:", session.entry_points)
# ['run_main_graph']

# 3. 准备输入数据
# 注意：输入 numpy 数组的 dtype 和 shape 必须与模型签名匹配
# X: float32[1, 4]
X = np.array([[1.0, 2.0, 3.0, 4.0]], dtype=np.float32)
# W: float32[4, 3]（权重）
W = np.array([[0.1, 0.2, 0.3],
              [0.4, 0.5, 0.6],
              [0.7, 0.8, 0.9],
              [1.0, 1.1, 1.2]], dtype=np.float32)
# B: float32[3]（偏置）
B = np.array([0.01, 0.02, 0.03], dtype=np.float32)

# 4. 执行推理
# 输入是 numpy 数组列表，顺序与模型输入顺序一致
outputs = session.run([X, W, B])

# 5. 获取结果
Y = outputs[0]
print("输出形状:", Y.shape)  # (1, 3)
print("输出数据:", Y)

# 6. 验证结果（与 numpy 计算对比）
expected = X @ W + B
print("期望结果:", expected)
print("结果匹配:", np.allclose(Y, expected, rtol=1e-5))
```

运行推理：

```bash
python run_inference.py
```

### 方式二：使用 C++ ExecutionSession API

```cpp
// run_inference.cpp
#include <iostream>
#include <vector>
#include "ExecutionSession.hpp"
#include "OnnxMlirRuntime.h"

int main() {
    // 1. 创建执行会话（加载共享库）
    onnx_mlir::ExecutionSession session("./matmul_add.so");

    // 2. 查询签名
    std::cout << "输入签名: " << session.inputSignature() << std::endl;
    std::cout << "输出签名: " << session.outputSignature() << std::endl;

    // 3. 准备输入数据
    // 创建输入张量（owning=0：数据由 numpy/外部管理）
    int64_t shape_X[] = {1, 4};
    float data_X[] = {1.0f, 2.0f, 3.0f, 4.0f};
    OMTensor *tensor_X = omTensorCreate(shape_X, 2, ONNX_TYPE_FLOAT,
                                         data_X, 0);

    int64_t shape_W[] = {4, 3};
    float data_W[] = {0.1f, 0.2f, 0.3f,
                      0.4f, 0.5f, 0.6f,
                      0.7f, 0.8f, 0.9f,
                      1.0f, 1.1f, 1.2f};
    OMTensor *tensor_W = omTensorCreate(shape_W, 2, ONNX_TYPE_FLOAT,
                                         data_W, 0);

    int64_t shape_B[] = {3};
    float data_B[] = {0.01f, 0.02f, 0.03f};
    OMTensor *tensor_B = omTensorCreate(shape_B, 1, ONNX_TYPE_FLOAT,
                                         data_B, 0);

    OMTensor *inputs[] = {tensor_X, tensor_W, tensor_B};
    OMTensorList *inputList = omTensorListCreate(inputs, 3);

    // 4. 执行推理
    OMTensorList *outputList = session.run(inputList);

    // 5. 获取结果
    OMTensor *output = omTensorListGetOmtByIndex(outputList, 0);
    float *result = (float *)omTensorGetDataPtr(output);
    int64_t *outShape = omTensorGetShape(output);
    int64_t outRank = omTensorGetRank(output);

    std::cout << "输出秩: " << outRank << ", 形状: [";
    for (int i = 0; i < outRank; i++) {
        std::cout << outShape[i] << (i < outRank - 1 ? ", " : "");
    }
    std::cout << "]" << std::endl;

    std::cout << "输出数据: [";
    for (int i = 0; i < outShape[outRank - 1]; i++) {
        std::cout << result[i] << (i < outShape[outRank - 1] - 1 ? ", " : "");
    }
    std::cout << "]" << std::endl;

    // 6. 清理
    omTensorListDestroy(outputList);
    omTensorListDestroy(inputList);
    omTensorDestroy(tensor_X);
    omTensorDestroy(tensor_W);
    omTensorDestroy(tensor_B);

    return 0;
}
```

编译 C++ 推理程序：

```bash
g++ -std=c++17 -O2 run_inference.cpp \
    -I/path/to/onnx-mlir/include \
    -I/path/to/onnx-mlir/build/include \
    -L./ -lmatmul_add \
    -Wl,-rpath,. \
    -o run_inference

./run_inference
```

### 方式三：纯 C API（极简部署）

```c
// run_inference_c.c
#include <stdio.h>
#include <dlfcn.h>
#include "OnnxMlirRuntime.h"

int main() {
    // 1. 手动加载共享库
    void *handle = dlopen("./matmul_add.so", RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "dlopen failed: %s\n", dlerror());
        return 1;
    }

    // 2. 查找 run_main_graph 符号
    typedef OMTensorList* (*run_fn)(OMTensorList*);
    run_fn run_main_graph = (run_fn)dlsym(handle, "run_main_graph");
    if (!run_main_graph) {
        fprintf(stderr, "dlsym failed: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }

    // 3. 创建输入张量
    int64_t shape_X[] = {1, 4};
    float data_X[] = {1.0f, 2.0f, 3.0f, 4.0f};
    OMTensor *tX = omTensorCreate(shape_X, 2, ONNX_TYPE_FLOAT, data_X, 0);

    int64_t shape_W[] = {4, 3};
    float data_W[] = {0.1f,0.2f,0.3f, 0.4f,0.5f,0.6f,
                      0.7f,0.8f,0.9f, 1.0f,1.1f,1.2f};
    OMTensor *tW = omTensorCreate(shape_W, 2, ONNX_TYPE_FLOAT, data_W, 0);

    int64_t shape_B[] = {3};
    float data_B[] = {0.01f, 0.02f, 0.03f};
    OMTensor *tB = omTensorCreate(shape_B, 1, ONNX_TYPE_FLOAT, data_B, 0);

    OMTensor *inputs[] = {tX, tW, tB};
    OMTensorList *inputList = omTensorListCreate(inputs, 3);

    // 4. 推理
    OMTensorList *outputList = run_main_graph(inputList);

    // 5. 输出结果
    OMTensor *output = omTensorListGetOmtByIndex(outputList, 0);
    float *res = (float*)omTensorGetDataPtr(output);
    printf("结果: [%.4f, %.4f, %.4f]\n", res[0], res[1], res[2]);

    // 6. 清理
    omTensorListDestroy(outputList);
    omTensorListDestroy(inputList);
    omTensorDestroy(tX);
    omTensorDestroy(tW);
    omTensorDestroy(tB);
    dlclose(handle);
    return 0;
}
```

## 步骤 4：验证与调试

### 验证计算正确性

```python
# verify.py
import numpy as np
import sys
sys.path.insert(0, "/path/to/onnx-mlir/build/lib")
from PyRuntime import OMExecutionSession

session = OMExecutionSession("./matmul_add.so")

# 多组随机输入验证
for _ in range(100):
    X = np.random.randn(1, 4).astype(np.float32)
    W = np.random.randn(4, 3).astype(np.float32)
    B = np.random.randn(3).astype(np.float32)

    outputs = session.run([X, W, B])
    expected = X @ W + B

    if not np.allclose(outputs[0], expected, rtol=1e-5):
        print("验证失败!")
        print("ONNX-MLIR:", outputs[0])
        print("NumPy:", expected)
        break
else:
    print("全部 100 组随机测试通过!")
```

### 查看中间 IR 用于调试

```bash
# 查看 ONNX Dialect IR（预处理后）
onnx-mlir -O3 --EmitONNXIR matmul_add.onnx -o matmul_add
cat matmul_add.onnxrt.mlir

# 查看 MLIR（Krnl/Affine 级别）
onnx-mlir -O3 --EmitMLIR matmul_add.onnx -o matmul_add
cat matmul_add.mlir

# 查看 LLVM IR
onnx-mlir -O3 --EmitLLVMIR matmul_add.onnx -o matmul_add
cat matmul_add.ll
```

### 使用 runDebug 捕获崩溃

```python
from PyRuntime import OMExecutionSession
import numpy as np

session = OMExecutionSession("./model.so")

# 使用 run_debug 模式（C++ runDebug 的 Python 绑定）
# 崩溃时抛出异常而非段错误
try:
    outputs = session.run([input_data])  # 可能有 run_debug 方法名差异
except RuntimeError as e:
    print(f"模型执行崩溃: {e}")
    # 注意：崩溃后不应继续使用该 session
```

## 常见问题与解决

### Q1: 编译报错 "opt: command not found"

**原因**：LLVM `opt` 工具不在 PATH 中。ONNX-MLIR 需要外部 LLVM 工具链完成代码生成。

**解决**：
```bash
# 确保 LLVM 工具链在 PATH 中
export PATH=/path/to/llvm/bin:$PATH

# 验证
opt --version
llc --version
```

### Q2: 运行时 "cannot open shared object file"

**原因**：共享库依赖路径问题。

**解决**：
```bash
# 方式1：设置 LD_LIBRARY_PATH
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
python run_inference.py

# 方式2：编译时设置 rpath（C++ 程序）
g++ ... -Wl,-rpath,/path/to/model/dir

# 方式3：使用绝对路径加载
session = OMExecutionSession("/absolute/path/to/matmul_add.so")
```

### Q3: Python 导入错误 "No module named PyRuntime"

**原因**：PyRuntime 未安装或不在 Python 路径中。

**解决**：
```bash
# 方式1：将 build/lib 加入 PYTHONPATH
export PYTHONPATH=/path/to/onnx-mlir/build/lib:$PYTHONPATH

# 方式2：在 Python 脚本中添加路径
import sys
sys.path.insert(0, "/path/to/onnx-mlir/build/lib")
```

### Q4: 多模型加载符号冲突

**原因**：多个模型编译时未指定 tag，导出相同符号名。

**解决**：
```bash
# 编译时指定不同 tag
onnx-mlir -O3 --tag=modela model_a.onnx -o model_a
onnx-mlir -O3 --tag=modelb model_b.onnx -o model_b

# Python 中分别加载
session_a = OMExecutionSession("./model_a.so", entry_point_name="run_main_graph_modela")
session_b = OMExecutionSession("./model_b.so", entry_point_name="run_main_graph_modelb")
```

### Q5: 输入形状不匹配错误

**原因**：输入 numpy 数组的 shape 或 dtype 与模型期望不符。

**解决**：
```python
# 先查询签名
session = OMExecutionSession("./model.so")
print(session.signature)  # 查看输入/输出的类型和形状

# 确保输入数组 dtype 正确（通常是 np.float32）
# 确保输入数组 shape 与签名一致
```

## 要点解析

### 为什么编译产物是共享库而不是可执行文件？

共享库（.so/.dll）设计使模型推理可以嵌入到任意宿主程序中（Python服务、C++应用、Java服务等），通过统一的 C ABI（`run_main_graph`）调用。宿主程序只需要动态加载库并传递张量，不需要链接到模型特定的代码。

### 自描述特性如何简化部署？

传统 DL 编译器部署需要：编译产物 + 元数据文件 + 头文件。ONNX-MLIR 的自描述共享库将所有信息（签名、入口点、编译信息）嵌入到 .so 文件本身，通过 `omInputSignature()` 等函数查询。Python 运行时 `session.signature` 就是调用这些内嵌函数。这使得：
- 热加载：监控目录，发现新 .so 即可加载服务
- 无 schema 部署：不需要预定义输入/输出格式
- 自验证：运行时可自动检查输入是否匹配签名

### O0 vs O3 性能差异

在本例中（小矩阵乘），O3 的 tiling/SIMD/并行优化可能因为模型太小而体现不出优势。但对于大模型（如 ResNet50、BERT）：
- O0：直接生成最朴素的循环，无缓存优化，无 SIMD
- O3：对 Conv/MatMul 生成 tiling 循环（缓存友好）+ SIMD 向量化（AVX/AVX2/AVX-512/NEON）+ OpenMP 多核并行
- 性能差异可达 10x~100x（取决于模型和硬件）

## 延伸阅读

- 理解整体架构：[ONNX-MLIR 整体架构](../concepts/00-overall-architecture.md)
- 深入 lowering 管线：[Dialect 转换管线](../concepts/03-lowering-pipeline.md)
- 运行时模型细节：[运行时执行模型](../concepts/04-runtime-execution.md)
- 编译选项参考：[编译选项体系与性能调优](../concepts/05-compiler-options.md)
