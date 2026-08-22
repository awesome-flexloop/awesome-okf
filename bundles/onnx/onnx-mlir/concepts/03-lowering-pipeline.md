---
type: concept
title: "Dialect 转换管线：ONNX→Krnl→Affine→LLVM"
description: "ONNX-MLIR 完整的 Dialect 转换管线——ONNX 预处理 Passes、ONNX→Krnl lowering、Krnl→Affine 循环转换、Krnl→LLVM 最终转换（含运行时函数生成）、MLIR Pass 与外部 LLVM 工具链的边界、Linalg 替代路径"
sources:
  references: [../references/dialects-runtime.md, ../references/compiler-entry.md]
  facts: [F-002, F-011, F-019, F-020, F-021, F-022, F-023, F-024]
---

# Dialect 转换管线：ONNX→Krnl→Affine→LLVM

## 核心理解

ONNX-MLIR 的编译过程本质是一条**多级 Dialect lowering 流水线**——每个阶段将 IR 从更高层次的 Dialect 转换为更低层次的 Dialect，逐步消除抽象，最终生成 LLVM IR 和目标代码。整个管线由 `src/Compiler/CompilerPasses.cpp` 中的一系列 `add*Passes()` 函数编排，每个函数负责一个 Dialect 层级之间的转换。

理解 lowering 管线的关键是理解两个边界：
1. **MLIR Pass 内部边界**：ONNX→Krnl→Affine→LLVM Dialect 的转换全部在 MLIR Pass Manager 内部完成（内存中）
2. **MLIR 与外部工具链的边界**：LLVM Dialect→LLVM IR bitcode→目标文件→共享库通过进程外调用 LLVM 工具链完成

## 完整管线总览

```
阶段 1: ONNX Dialect 内部变换（addONNXToMLIRPasses）
┌──────────────────────────────────────────────────────────────┐
│ ONNX ModuleOp（FrontendDialectTransformer 导入后）            │
│ → Decompose → Recompose → ShapeInference → ConstProp        │
│ → ONNXOpTransform → SimplifyShape → StandardFuncReturn      │
│ → SymbolDCE → ONNXCSE → FusionTransform → SetNodeName       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
阶段 2: ONNX → Krnl（addONNXToKrnlPasses）
┌──────────────────────────────────────────────────────────────┐
│ createONNXPreKrnlVerifyPass（验证）                           │
│ 各 ONNX Op → Krnl Op lowering（按 Math/NN/Tensor/RNN/       │
│   ControlFlow 分目录实现）                                    │
│ O3: tiling + SIMD + 并行化启用                               │
│ canonicalization                                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
阶段 3: Krnl → Affine/SCF（addKrnlToAffinePasses）
┌──────────────────────────────────────────────────────────────┐
│ ConvertKrnlToAffine:                                         │
│   krnl.define_loops/iterate → affine.for 嵌套               │
│   krnl.block → 外层tile循环+内层point循环                    │
│   krnl.permute → 调整affine.for嵌套顺序                      │
│   krnl.unroll → affine.for unroll                            │
│   krnl.parallel → affine.parallel                            │
│ 消除仅写不读的局部 MemRef 分配                                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
阶段 4: Affine/SCF → LLVM Dialect（addKrnlToLLVMPasses）
┌──────────────────────────────────────────────────────────────┐
│ VectorToSCF → LowerAffine → LowerKrnlRegion                 │
│ → ProcessScfParallelPrivate（并行时）                         │
│ → BufferLoopHoisting → BufferDeallocation                   │
│ → BufferizationToMemRef → SCFToOpenMP（并行时）              │
│ → FoldMemRefAlias → VectorToLLVM                             │
│ → ConvertKrnlToLLVM ★（最终转换+运行时函数生成）              │
│ → ReconcileUnrealizedCasts → Canonicalizer                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼ translateModuleToLLVMIR()
阶段 5: MLIR 外部（进程外工具链）
┌──────────────────────────────────────────────────────────────┐
│ writeBitcodeToFile → opt（bitcode优化）→ llc（.o生成）       │
│ → cxx（共享库链接）→ jar（JNI打包，可选）                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         自描述共享库
```

## 阶段 1：ONNX 预处理 Passes

`addONNXToMLIRPasses()`（F-024）在 ONNX Dialect 层内部执行图级优化，不改变 Dialect 层级。这些 Pass 是 lowering 前的必要准备：

### Pass 分类

| 类别 | Pass | 作用 |
|------|------|------|
| **规范化** | DecomposeONNXToONNX | 将高版本/不支持的 Op 分解为低版本等价组合 |
| | RecomposeONNXToONNX | 将分解模式重组为优化形式 |
| | SimplifyShapeRelatedOps | 简化形状计算相关 Op |
| | StandardFuncReturn | ONNXReturnOp → func::ReturnOp |
| **形状推断** | ShapeInference | 传播张量形状（后续 lowering 的基础） |
| **常量优化** | ConstProp | 折叠常量输入的 Op |
| | ONNXOpTransform | 动态迭代优化（多轮直到收敛） |
| **图变换** | ONNXHybridTransform | 根据 IR 特征动态选择优化 |
| | FusionOpTransform | 算子融合（如 Conv+Relu 融合） |
| **清理** | SymbolDCE | 消除不可达符号/死代码 |
| | ONNXCSEWithNodeName | 公共子表达式消除 |
| | SetONNXNodeName | 统一设置节点名称 |
| **调试** | InstrumentPass | 插桩（按需启用） |

### Pass 顺序的重要性

Pass 顺序不是任意的：
1. **Decompose 必须在 ShapeInference 之前**：分解后的 Op 才有形状推断实现
2. **ShapeInference 必须在 Fusion/ConstProp 之前**：这些优化需要形状信息
3. **CSE/DCE 在 Fusion 之后**：融合可能产生新的优化机会
4. **StandardFuncReturn 在最后**：确保后续 lowering 看到统一的 func.return

## 阶段 2：ONNX → Krnl Lowering

`addONNXToKrnlPasses()`（F-019）是最核心的 lowering 阶段，将 ONNX 张量算子转换为 Krnl 循环操作。

### 前置验证

```cpp
// 验证 ONNX Op 的合法性
pm.addNestedPass<func::FuncOp>(createONNXPreKrnlVerifyPass());
```

### Op 级别的 Lowering

每个 ONNX Op 的 lowering 通过 Conversion Pattern 实现，按类别组织：

```
src/Conversion/ONNXToKrnl/
├── Math/          # Add/Mul/Relu/Softmax/Sqrt/Exp/...
│   └── 逐元素算子通常直接映射为 krnl.iterate + krnl.load/store
├── NN/            # Conv/MatMul/Gemm/Pooling/BatchNorm/LRN/...
│   └── 核心算子使用 krnl.block(tiling) + krnl.vector_type_cast(SIMD)
│       + krnl.parallel(多线程) + krnl.matmul(专用内核)
├── Tensor/        # Reshape/Transpose/Concat/Split/Gather/...
│   └── 张量变换算子可能不需要循环，直接生成 MemRef 视图变换
├── RNN/           # LSTM/GRU/RNN
│   └── 序列算子生成复杂的 Krnl 循环结构
└── ControlFlow/   # If/Loop/Scan
    └── 控制流算子映射到 scf.if/scf.while + Krnl 区域
```

### O3 优化级别的影响

在 `-O3` 级别，ONNX→Krnl lowering 会：
- **启用 Tiling**：对 Conv/MatMul 等计算密集型 Op 生成 `krnl.block` 循环分块
- **启用 SIMD**：生成 `krnl.vector_type_cast` 向量化内层循环
- **启用并行**：对外层循环标记 `krnl.parallel`（映射到 OpenMP）

O0 级别则生成最直接的 Krnl 循环（无 tiling/SIMD/并行），便于调试。

## 阶段 3：Krnl → Affine/SCF

`addKrnlToAffinePasses()`（F-020）将 Krnl 的高层循环优化表示转换为 MLIR 标准循环结构：

```cpp
pm.addNestedPass<func::FuncOp>(
    krnl::createConvertKrnlToAffinePass(enableParallel));
```

### 转换规则

| Krnl Op | Affine/SCF 对应 |
|---------|-----------------|
| `krnl.define_loops` + `krnl.iterate` | nested `affine.for` |
| `krnl.block(loops, by tileSizes)` | 外层 tile `affine.for` + 内层 point `affine.for` |
| `krnl.permute(loops, perm)` | 调整 `affine.for` 的嵌套顺序 |
| `krnl.unroll(loop)` | `affine.for` + unroll annotation |
| `krnl.parallel(loop)` | `affine.parallel`（→ OpenMP） |
| `krnl.load/store` | `memref.load/store` with affine indices |
| `krnl.memcpy/memset` | `memref.copy`/`memref.set` |
| `krnl.call` | `func.call`（MemRef 参数） |

### 额外优化

此阶段还执行：**消除仅写不读的局部 MemRef 分配**——这些是 lowering 过程中产生的临时缓冲区，实际存储可以被 SSA 值替代。

## 阶段 4：Krnl/Affine → LLVM Dialect（最终 Lowering）

`addKrnlToLLVMPasses()`（F-021）是最复杂的 lowering 阶段，包含十几个 Pass，按顺序执行：

```
VectorToSCF
    ↓  将向量操作转为 SCF 循环（便于后续 lowering）
LowerAffine
    ↓  affine.for/if → SCF 循环 + 标准算术
LowerKrnlRegion
    ↓  处理 Krnl 区域操作
ProcessScfParallelPrivate（仅并行时）
    ↓  处理 parallel 循环的私有变量
BufferLoopHoisting
    ↓  将 buffer 分配提升到循环外
BufferDeallocation
    ↓  自动插入 buffer 释放操作
BufferizationToMemRef
    ↓  将 tensor 操作转为 MemRef（one-shot bufferize 兼容）
SCFToOpenMP（仅并行时）
    ↓  scf.parallel → omp.parallel
FoldMemRefAlias
    ↓  折叠 MemRef 别名（简化内存访问）
VectorToLLVM
    ↓  向量操作 → LLVM 向量指令
ConvertKrnlToLLVM ★
    ↓  最终 Krnl→LLVM 转换（含入口点/运行时函数/C包装）
ReconcileUnrealizedCasts
    ↓  消除 unrealized_conversion_cast
Canonicalizer
    ↓  最终规范化
```

### ConvertKrnlToLLVM：最关键的最终转换

`createConvertKrnlToLLVMPass`（F-022）是整个管线的"最后一公里"，负责：

1. **入口点预处理**：
   - 为符号添加 tag 后缀（多模型加载避免冲突）
   - 清理参数属性

2. **运行时信息收集**：
   - 记录输入/输出 MemRef 类型（shape、dtype）
   - 生成 `omInputSignature`/`omOutputSignature` JSON

3. **入口点函数转换**：
   - `krnl.entry_point` 标记的函数 → 动态入口点函数
   - 入口函数签名从 MemRef 参数转换为 OMTensor 参数：
     ```
     内部函数：func @main_graph(%arg0: memref<?x?xf32>, ...)
              → 包装函数：OMTensorList* run_main_graph(OMTensorList*)
     ```
   - 包装函数负责 OMTensor → MemRef 的解包和 MemRef → OMTensor 的打包

4. **运行时元数据函数生成**：
   - `omQueryEntryPoints`：返回所有入口点名（NULL 终止的 C 字符串数组）
   - `omInputSignature`：返回 JSON 格式的输入签名（类型、维度、名称）
   - `omOutputSignature`：返回 JSON 格式的输出签名
   - `omCompilationInfo`：返回编译信息 JSON（编译器版本、优化级别、目标架构等）

5. **常量处理**：
   - 小常量：直接嵌入为 LLVM 全局变量
   - 大常量：存储到 `.lrodata` 段或外部文件（大模型支持）

6. **C 包装函数**：生成 C ABI 兼容的包装函数

## 阶段 5：外部 LLVM 工具链（I-02 洞察）

MLIR Pass 管线完成后（LLVM Dialect），编译器通过 `translateModuleToLLVMIR()` 将 MLIR LLVM Dialect Module 转换为 LLVM IR Module，然后进入进程外工具链阶段（F-011）：

```
LLVM Dialect Module（内存中）
    │
    ▼ mlir::translateModuleToLLVMIR()
LLVM IR Module（内存中，llvm::Module）
    │
    ▼ WriteBitcodeToFile()
LLVM bitcode 文件（model.bc）
    │
    ▼ Command("opt", ...)  ← --Xopt 透传选项
    │   opt -O3 model.bc -o model.opt.bc
优化后的 bitcode（model.opt.bc）
    │
    ▼ Command("llc", ...)  ← --Xllc 透传选项
    │   llc -filetype=obj model.opt.bc -o model.o
目标文件（model.o）
    │
    ▼ Command(cxx, ...)  ← 平台条件编译
    │   Linux:   c++ -shared -fPIC model.o -o model.so
    │   macOS:   c++ -dynamiclib model.o -o model.dylib (+ dsymutil)
    │   Windows: c++ /LD model.o /Fe:model.dll (+ .def/.lib)
共享库（model.so / model.dll / model.dylib）
    │
    │（EmitJNI 时继续）
    ▼ 编译 JNI C 包装器 + jar 打包
    │   cxx -c jni_wrapper.cpp -o jni_wrapper.o
    │   cxx -shared jni_wrapper.o model.so -o libmodeljni.so
    │   jar cf model.jar *.class libmodeljni.so model.so
JNI jar 包（model.jar）
```

`Command` 类封装了外部进程调用，处理平台差异（Windows 使用 `CreateProcess`，POSIX 使用 `fork/exec`）。

### 为什么不进程内完成？

根据 I-02 洞察，ONNX-MLIR 选择进程外调用 LLVM 工具链而非内建代码生成：

**优点**：
- 可通过 `-Xopt`/`-Xllc`/`-mllvm` 透传任意 LLVM 选项
- 复用系统链接器的平台特定逻辑（Windows 导出表、macOS dSYM、s390x 链接脚本）
- 编译时不需要链接整个 LLVM 后端（减少编译器本身的二进制大小）
- 可以使用系统安装的 LLVM（可能包含硬件厂商定制的后端）

**缺点**：
- 对 LLVM 版本严格依赖（README 明确指出依赖特定 LLVM commit）
- 跨进程序列化/反序列化 bitcode 有开销
- 部署时需要 LLVM 工具链在 PATH 中

## Linalg 替代路径

启用 `--use-linalg-path` 或 `--linalg-ops` 时，管线走 Linalg 路径（F-023）：

```
ONNX Dialect（预处理后）
    │
    ▼ addONNXToLinalgPasses()
    │   部分 ONNX Op → Linalg Op（如 Conv→linalg.conv, MatMul→linalg.matmul）
    ▼
Linalg + ONNX 混合 Dialect
    │
    ▼ addLinalgToAffinePasses()
    │   One-Shot Bufferize（tensor → memref）
    │   Linalg Op → Affine/SCF 循环
    │   剩余未转的 ONNX Op → Krnl Op（混合模式）
    ▼
Affine/SCF Dialect（可能包含少量 Krnl Op）
    │
    ▼ addKrnlToLLVMPasses()（复用同一下游管线）
    │
    ▼ ... → LLVM → 外部工具链 → 共享库
```

Linalg 路径目前是混合模式——并非所有 ONNX Op 都有 Linalg lowering，未转换的 Op 仍走 Krnl 路径。两条路径在 KrnlToLLVM 阶段汇合，统一生成运行时函数。

## 关联概念

- [ONNX-MLIR 整体架构](00-overall-architecture.md) — 管线在整体架构中的位置
- [ONNX Dialect](01-onnx-dialect.md) — 了解管线起点 ONNX Dialect
- [Krnl Dialect：编译策略层](02-krnl-dialect.md) — 深入了解管线核心中间层
- [运行时执行模型](04-runtime-execution.md) — 了解管线输出产物如何被加载执行
- [编译选项体系与性能调优](05-compiler-options.md) — 了解如何通过选项控制管线行为
