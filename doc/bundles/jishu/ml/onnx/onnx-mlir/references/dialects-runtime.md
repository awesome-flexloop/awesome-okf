---
type: reference
title: "Dialect 定义与运行时：ONNX/Krnl Dialect 与 ExecutionSession"
description: "ONNX Dialect 和 Krnl Dialect 的 TableGen 定义核心字段、Dialect 转换管线 Pass 编排、ExecutionSession 运行时动态加载与推理执行的信源登记"
sources:
  - path: "src/Dialect/ONNX/ONNX.td"
    facts: [F-012, F-013, F-014]
  - path: "src/Dialect/Krnl/Krnl.td"
    facts: [F-015]
  - path: "src/Compiler/CompilerPasses.cpp"
    facts: [F-002, F-019, F-020, F-021, F-022, F-023, F-024, F-031]
  - path: "src/Conversion/KrnlToLLVM/ConvertKrnlToLLVM.hpp"
    facts: [F-022]
  - path: "src/Runtime/ExecutionSession.hpp"
    facts: [F-026, F-027, F-028]
  - path: "include/OnnxMlirRuntime.h"
    facts: [F-025, F-029]
  - path: "include/onnx-mlir/Runtime/OMEntryPoint.h"
    facts: [F-027]
  - path: "src/Accelerators/Accelerator.hpp"
    facts: [F-031]
---

# Dialect 定义与运行时：ONNX/Krnl Dialect 与 ExecutionSession

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `src/Dialect/ONNX/ONNX.td` | TableGen 定义 | ONNX Dialect 声明、ONNXTensorEncodingAttr 自定义属性、ONNX Op 接口声明 |
| `src/Dialect/Krnl/Krnl.td` | TableGen 定义 | Krnl Dialect 声明、循环优化/内存/运行时辅助 Op 定义 |
| `src/Compiler/CompilerPasses.cpp` | Pass 编排 | 所有 lowering Pass 的注册与编排（ONNX→Krnl→Affine→LLVM）、加速器 Pass 插入点 |
| `src/Conversion/KrnlToLLVM/ConvertKrnlToLLVM.hpp` | 转换声明 | KrnlToLLVM Pass 入口点预处理、运行时函数生成、C 包装函数 |
| `src/Runtime/ExecutionSession.hpp` | 运行时核心 | ExecutionSession C++ 类：动态库加载、符号解析、推理执行、信号处理 |
| `include/OnnxMlirRuntime.h` | 运行时 C API | OMTensor/OMTensorList C 结构体与 API、run_main_graph 统一签名 |
| `include/onnx-mlir/Runtime/OMEntryPoint.h` | 入口点 API | omQueryEntryPoints/omInputSignature/omOutputSignature API |
| `src/Accelerators/Accelerator.hpp` | 加速器基类 | 可插拔加速器架构定义、Accelerator 基类接口 |

## 关键事实登记

### F-012：ONNX Dialect 声明

**信源**：`src/Dialect/ONNX/ONNX.td` L37-L57

```tablegen
def ONNX_Dialect : Dialect {
  let name = "onnx";
  let cppNamespace = "::mlir";
  let dependentDialects = ["::mlir::func::FuncDialect"];
  let useDefaultAttributePrinterParser = 0;  // 自定义属性解析/打印
  let hasConstantMaterializer = 1;           // 常量物化器
}
```

ONNX Dialect 在 `::mlir` C++ 命名空间下注册，仅依赖 func Dialect，不使用默认属性打印器（自定义 `ONNXTensorEncodingAttr` 等），支持常量物化。

### F-013：ONNX Op TableGen 定义体系

**信源**：`src/Dialect/ONNX/ONNX.td` L11-L16

ONNX 操作通过 TableGen 定义，主定义文件为 `ONNX.td`，非标准扩展操作定义在 `AdditionalONNXOps.td`。每个 ONNX 操作实现两个核心接口：

- `ShapeInferenceOpInterface`：形状推断接口
- `ShapeHelperOpInterface`：形状辅助接口

每个 ONNX Op 对应 MLIR 中的一个 Op 类（如 `onnx.Add` → `ONNXAddOp`），Op lowering 实现位于 `src/Conversion/ONNXToKrnl/` 目录下按类别分子目录（Math/NN/Tensor/RNN/ControlFlow）。

### F-014：ONNXTensorEncodingAttr 自定义布局编码

**信源**：`src/Dialect/ONNX/ONNX.td` L68-L100

`ONNXTensorEncodingAttr` 是 ONNX Dialect 的自定义属性，用于描述数据布局变换（如 NCHWxC tiling 布局），核心参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `dataLayout` | 枚举 | 数据布局类型（如 NCHW、NCHWxC） |
| `xFactor` | 整数 | X 方向分块因子 |
| `yFactor` | 整数 | Y 方向分块因子 |

该属性支持 SIMD 向量化所需的数据布局优化，是 O3 级别 tiling+SIMD 优化的关键 IR 表示。

### F-015：Krnl Dialect 声明

**信源**：`src/Dialect/Krnl/Krnl.td` L31-L45

```tablegen
def Krnl_Dialect : Dialect {
  let name = "krnl";
  let cppNamespace = "::mlir";
  let dependentDialects = [
    "::mlir::affine::AffineDialect",
    "::mlir::arith::ArithDialect",
    "::mlir::func::FuncDialect",
    "::mlir::linalg::LinalgDialect",
    "::mlir::math::MathDialect",
    "::mlir::memref::MemRefDialect",
    "::mlir::scf::SCFDialect",
    "::mlir::shape::ShapeDialect"
  ];
}
```

Krnl Dialect 依赖 8 个 MLIR 内置 Dialect（affine/arith/func/linalg/math/memref/scf/shape），是 ONNX 到 LLVM lowering 的核心中间 Dialect。

### F-016/F-017/F-018：Krnl Dialect 核心操作集

Krnl Dialect 提供三类核心操作：

**循环优化操作**：

| 操作 | 用途 |
|------|------|
| `krnl.define_loops` | 定义循环维度 |
| `krnl.iterate` | 嵌套循环（等价于 affine.for 嵌套） |
| `krnl.block` | 循环分块（tile） |
| `krnl.permute` | 循环重排（改变迭代顺序） |
| `krnl.unroll` | 循环展开 |
| `krnl.parallel` | 标记并行循环（映射到 OpenMP） |
| `krnl.matmul` | 专用矩阵乘内核（支持 tiling/SIMD） |

**内存操作**：

| 操作 | 用途 |
|------|------|
| `krnl.load` / `krnl.store` | MemRef 读写 |
| `krnl.memcpy` | 内存拷贝 |
| `krnl.memset` | 内存填充 |
| `krnl.global` | 全局常量（持有 dense elements 属性） |
| `krnl.copy_to_tile_buffer` / `krnl.copy_from_tile_buffer` | tile 缓冲区拷贝（支持 overread/padding） |
| `krnl.vector_type_cast` | 向量类型转换（用于 SIMD） |

**运行时辅助操作**：

| 操作 | 用途 |
|------|------|
| `krnl.call` | 调用外部 C 函数（参数已 lowering 为 MemRef） |
| `krnl.entry_point` | 标记 ONNX 模型主入口点 |
| `krnl.print_tensor` | 运行时打印张量（调试用） |
| `krnl.random_normal` | 随机正态分布生成 |
| `krnl.find_index` | 完美哈希表查找 |
| `krnl.instrument` | 运行时插桩点 |

### F-024：ONNX 预处理 Passes

**信源**：`src/Compiler/CompilerPasses.cpp` L78-L271

`addONNXToMLIRPasses()` 在 ONNX Dialect 层面执行一系列预处理 Pass，按执行顺序：

1. `DecomposeONNXToONNX`：分解不支持的 Op
2. `RecomposeONNXToONNX`：重组 Op
3. `ONNXHybridTransform`：动态 Pass 管线
4. `ShapeInference`：形状推断
5. `ConstProp`：常量折叠
6. `ONNXOpTransform`：动态迭代优化
7. `SimplifyShapeRelatedOps`：简化形状相关 Op
8. `StandardFuncReturn`：ONNXReturnOp → func::ReturnOp
9. `SymbolDCE`：死代码消除
10. `ONNXCSEWithNodeName`：公共子表达式消除
11. `FusionOpTransform`：Op 融合
12. `SetONNXNodeName`：设置节点名称
13. `InstrumentPass`：插桩（按需）

### F-019/F-020/F-021/F-022：Dialect 转换管线 Pass 编排

**信源**：`src/Compiler/CompilerPasses.cpp` L273-L571

核心转换管线（默认 Krnl 路径）：

```
ONNX Dialect（预处理后）
    │
    ▼ addONNXToKrnlPasses()  [Step 1]
    │   · createONNXPreKrnlVerifyPass（验证）
    │   · 各 ONNX Op → Krnl Op lowering
    │   · O3 时启用 tiling/SIMD/并行
    │   · canonicalization
    ▼
Krnl Dialect（含循环优化意图）
    │
    ▼ addKrnlToAffinePasses()  [Step 2]
    │   · createConvertKrnlToAffinePass(enableParallel)
    │   · krnl.iterate/block/permute/unroll → affine.for 嵌套
    │   · 消除仅写不读的局部 memref 分配
    ▼
Affine/SCF Dialect
    │
    ▼ addKrnlToLLVMPasses()  [Step 3]
    │   · VectorToSCF
    │   · LowerAffine
    │   · LowerKrnlRegion
    │   · ProcessScfParallelPrivate（并行时）
    │   · BufferLoopHoisting
    │   · BufferDeallocation
    │   · BufferizationToMemRef
    │   · SCFToOpenMP（并行时）
    │   · FoldMemRefAlias
    │   · VectorToLLVM
    │   · ConvertKrnlToLLVM（最终转换★）
    │   · ReconcileUnrealizedCasts
    │   · Canonicalizer
    ▼
LLVM Dialect
```

`createConvertKrnlToLLVMPass`（F-022）是最关键的最终转换 Pass，负责：
1. 入口点预处理（符号后缀、参数属性清理）
2. 运行时信息收集（输入输出 MemRef 类型记录）
3. KrnlEntryPointOp → 动态入口点函数（OMTensor 包装/解包）
4. 运行时函数生成：`omQueryEntryPoints`、`omInputSignature`、`omOutputSignature`、`omCompilationInfo`
5. 常量文件存储
6. C 包装函数生成
7. 大模型 `.lrodata` 段处理

### F-023：Linalg 替代路径

**信源**：`src/Compiler/CompilerPasses.cpp` L78-L101, L341-L430

启用 `--use-linalg-path` 或 `--linalg-ops` 时使用 Linalg 路径：

```
ONNX Dialect
    │
    ▼ addONNXToLinalgPasses()
    │   · 部分 ONNX Op → Linalg Op
    ▼
Linalg Dialect（混合IR：Linalg Op + 剩余 ONNX Op）
    │
    ▼ addLinalgToAffinePasses()
    │   · One-Shot Bufferize
    │   · Linalg Op → Affine/SCF
    │   · 剩余 ONNX Op → Krnl 路径
    ▼
Affine/SCF Dialect → 统一走 KrnlToLLVM Pass
```

混合 IR 模式下 Linalg Op 先转为 Affine，剩余 ONNX Op 走 Krnl 路径，最终统一通过 KrnlToLLVM pass 生成运行时函数。

### F-025/F-029：统一 C ABI 与张量数据结构

**信源**：`include/OnnxMlirRuntime.h` L45-L69

所有编译后的模型导出统一的 C 函数签名：

```c
// 统一推理入口点
OMTensorList *run_main_graph(OMTensorList *);

// 带 tag 后缀的多入口点
OMTensorList *run_main_graph_<tag>(OMTensorList *);
```

`OMTensor` 是运行时张量核心结构：

```c
typedef struct OMTensor {
  int64_t *shape;       // 维度数组
  int64_t  rank;        // 秩
  void    *data;        // 数据指针
  int64_t  dtype;       // 数据类型（ONNX_TYPE枚举）
  int64_t  owning;      // 是否拥有数据所有权
  // ...更多内部字段
} OMTensor;

typedef struct OMTensorList {
  OMTensor **tensors;   // 张量指针数组
  int64_t    size;      // 张量数量
} OMTensorList;
```

运行时 API 提供创建/销毁函数：`omTensorCreate()`、`omTensorListCreate()`、`omTensorDestroy()` 等。

### F-026/F-027/F-028：ExecutionSession 运行时核心

**信源**：`src/Runtime/ExecutionSession.hpp` L34-L196

`ExecutionSession` 是 C++ 运行时的核心类，负责：

1. **动态库加载**：Windows 使用 `llvm::sys::DynamicLibrary`（内部 LoadLibrary/GetProcAddress），POSIX 使用 `dlopen/dlsym`
2. **符号解析**：通过 dlsym 查找以下固定符号：

| 符号 | 类型 | 用途 |
|------|------|------|
| `omQueryEntryPoints` | 函数 | 返回 NULL 终止的入口点名数组 |
| `omInputSignature` | 函数 | 返回 JSON 格式输入签名 |
| `omOutputSignature` | 函数 | 返回 JSON 格式输出签名 |
| `omCompilationInfo` | 函数 | 返回 JSON 格式编译信息 |
| `omInstrumentPrint` | 函数 | 插桩数据打印（如果启用） |
| `run_main_graph`/`run_main_graph_<tag>` | 函数 | 推理入口点 |

3. **多入口点支持**：`setEntryPoint(name)` 切换入口点
4. **JSON 签名自描述**：`inputSignature()`/`outputSignature()` 返回含类型、维度、名称的 JSON
5. **信号处理**：`runDebug()` 在 POSIX 上捕获 SIGSEGV/SIGBUS/SIGFPE/SIGILL/SIGABRT，通过 setjmp/longjmp 恢复并抛出异常（标记内存可能已损坏）

### F-031：加速器插件架构

**信源**：`src/Compiler/CompilerPasses.cpp` L1027-L1034；`src/Accelerators/Accelerator.hpp`

编译器支持可插拔加速器架构：
- `Accelerator` 基类定义在 `src/Accelerators/Accelerator.hpp`
- 内置 NNPA（IBM Telum 集成 AI 加速器，z/Architecture），提供 ZHigh/ZLow Dialect 和专用 Pass 管线
- 加速器通过 `--maccel` 选项启用
- 每个加速器可通过 `accel->addPasses()` 独立控制整个编译管线（可以在任意阶段插入自定义 Dialect 和 Pass）

## 代码引用

```cpp
// ExecutionSession.hpp - 动态加载符号的函数指针类型（简化）
typedef OMTensorList *(*run_main_graph_signature)(OMTensorList *);
typedef const char **(*omQueryEntryPoints_signature)();
typedef const char *(*omSignature_signature)(const char *);
typedef const char *(*omCompilationInfo_signature)();

class ExecutionSession {
public:
  ExecutionSession(const std::string &sharedLibPath,
                   const std::string &entryPointName = "run_main_graph");
  ~ExecutionSession();

  std::vector<std::string> queryEntryPoints() const;
  void setEntryPoint(const std::string &name);
  const std::string inputSignature() const;
  const std::string outputSignature() const;
  const std::string compilationInfo() const;
  std::vector<OMTensor *> run(const std::vector<OMTensor *> &inputs);
  std::vector<OMTensor *> runDebug(const std::vector<OMTensor *> &inputs);

private:
  void *handle;  // dlopen/LoadLibrary 返回的句柄
  run_main_graph_signature runMainGraphFunc;
  omQueryEntryPoints_signature queryEntryPointsFunc;
  omSignature_signature inputSignatureFunc;
  omSignature_signature outputSignatureFunc;
  omCompilationInfo_signature compilationInfoFunc;
  // ...信号处理相关成员
};
```
