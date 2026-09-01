---
type: reference
title: "编译器入口：onnx-mlir.cpp 驱动与编译流程"
description: "onnx-mlir 命令行入口 main() 函数执行流程、CompilerUtils 编译阶段管理、CompilerOptions 编译选项体系的信源登记"
sources:
  - path: "src/onnx-mlir.cpp"
    facts: [F-004, F-006]
  - path: "src/Compiler/CompilerUtils.cpp"
    facts: [F-005, F-007, F-011, F-030]
  - path: "src/Compiler/CompilerUtils.hpp"
    facts: [F-007]
  - path: "src/Compiler/CompilerOptions.hpp"
    facts: [F-008, F-009, F-010]
  - path: "include/onnx-mlir/Compiler/OMCompilerTypes.h"
    facts: [F-003]
---

# 编译器入口：onnx-mlir.cpp 驱动与编译流程

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `src/onnx-mlir.cpp` | 驱动程序 | 命令行入口 `main()` 函数，MLIR 选项注册、配置加载、参数解析、编译调度 |
| `src/Compiler/CompilerUtils.cpp` | 编译工具 | 输入文件处理、编译阶段编排、外部工具链调度（opt/llc/cxx/jar）、输出文件生成 |
| `src/Compiler/CompilerUtils.hpp` | 工具头文件 | 编译阶段枚举、showCompilePhase() 阶段打印、compileModule() API 声明 |
| `src/Compiler/CompilerOptions.hpp` | 选项定义 | 所有编译选项的 llvm::cl 声明（优化级别、目标架构、调试选项等） |
| `include/onnx-mlir/Compiler/OMCompilerTypes.h` | 类型定义 | EmissionTargetType 7种输出目标枚举 |

## 关键事实登记

### F-004：命令行入口 main() 执行流程

**信源**：`src/onnx-mlir.cpp` L29-L164

`main()` 函数执行完整的编译器初始化和调度流程：

1. **注册 MLIR 命令行选项**：`mlir::registerAsmPrinterCLOptions()`、`mlir::registerMLIRContextCLOptions()`、`mlir::registerPassManagerCLOptions()` 等
2. **加载配置文件**：读取 `omconfig.json`（由 `--config-file` 指定或默认路径）
3. **解析命令行参数**：`llvm::cl::ParseCommandLineOptions()` 解析，环境变量 `ONNX_MLIR_FLAGS` 作为附加选项源
4. **初始化编译器配置**：设置目标三元组、优化级别、输出类型等
5. **创建 MLIRContext**：支持多线程（`MLIRContext` 构造时可启用 `threading`）
6. **加载 Dialect**：注册 ONNX、Krnl、Linalg、Affine、SCF、LLVM 等所有需要的 Dialect
7. **导入 ONNX 模型**：通过 `FrontendDialectTransformer` 将 protobuf 转为 ONNX Dialect ModuleOp
8. **运行 Pass 管线**：根据 EmissionTargetType 运行对应 lowering passes
9. **输出目标文件**：根据输出类型生成 IR/bitcode/.o/.so/.jar

```cpp
// 简化的 main() 流程（src/onnx-mlir.cpp）
int main(int argc, char *argv[]) {
  // 1. 注册MLIR命令行选项
  mlir::registerAsmPrinterCLOptions();
  mlir::registerMLIRContextCLOptions();
  mlir::registerPassManagerCLOptions();
  // ...

  // 2. 加载配置文件 + 解析参数
  // 优先级：命令行 > 配置文件 > ONNX_MLIR_FLAGS 环境变量
  loadConfigFile(configFilePath);
  llvm::cl::ParseCommandLineOptions(argc, argv, "ONNX-MLIR\n");

  // 3. 创建MLIRContext并加载Dialect
  mlir::MLIRContext context;
  context.loadDialect<
      mlir::ONNXDialect, mlir::KrnlDialect, mlir::func::FuncDialect,
      mlir::arith::ArithDialect, mlir::linalg::LinalgDialect,
      // ...更多Dialect
      >();

  // 4. 导入ONNX模型 → 运行Pass管线 → 输出
  processInputFile(inputFilename, context, outputBaseName, emissionTarget);
  return 0;
}
```

### F-005/F-030：输入文件处理与 ONNX 模型导入

**信源**：`src/Compiler/CompilerUtils.cpp` L686-L743

输入文件类型由文件扩展名决定：

| 扩展名 | 类型 | 处理方式 |
|--------|------|----------|
| `.onnx` | ONNX protobuf 二进制 | `FrontendDialectTransformer::ImportFrontendModelFile()` |
| `.onnxtext` | ONNX 文本格式 | 同上（文本模式） |
| `.json` | JSON 格式 | 从 JSON 导入 |
| `.mlir` | MLIR 文本 IR | `parseSourceFile()` 直接解析 MLIR |
| `-` | 标准输入 | 从 stdin 读取 |

安全检查：拒绝硬链接（通过 `nlink > 1` 检测），防止 CVE-2026-34446 路径遍历攻击。

`ImportFrontendModelFile()` / `ImportFrontendModelArray()` 是 ONNX 前端导入的核心 API，将 ONNX protobuf（文件或内存缓冲区）转换为 ONNX Dialect MLIR ModuleOp，支持 `ImportOptions` 控制 verbose 输出、类型使用、版本转换、形状信息、维度参数、op 排序等选项。

### F-003/F-007：7 种输出目标与编译阶段

**信源**：`include/onnx-mlir/Compiler/OMCompilerTypes.h` L24-L32；`src/Compiler/CompilerUtils.hpp` L42-L52

编译器支持 7 种输出目标类型（按 lowering 深度递增）：

| 输出类型 | 阶段数 | 产物 | 说明 |
|----------|--------|------|------|
| `EmitONNXBasic` | 3 | `.onnx` 基本 IR | 仅前端导入后的基本 ONNX IR |
| `EmitONNXIR` | 3 | `.mlir` ONNX Dialect IR | ONNX 预处理 Pass 后的 IR |
| `EmitMLIR` | 3 | `.mlir` MLIR 内置 Dialect IR | Krnl/Linalg lowering 后的 IR |
| `EmitLLVMIR` | 4 | `.ll` LLVM IR Dialect | LLVM Dialect IR |
| `EmitObj` | 5 | `.o` / `.obj` | 目标文件 |
| `EmitLib` | 6 | `.so` / `.dylib` / `.dll` | 共享库（**默认**） |
| `EmitJNI` | 8 | `.jar` | Java JNI jar 包 |

每个编译阶段通过 `showCompilePhase()` 打印进度：

```
[阶段号/总阶段数] 累计时间 (耗时) 阶段名称
```

### F-006：编译选项三源优先级

**信源**：`src/onnx-mlir.cpp` L40-L64

编译器选项来自三个来源，优先级从高到低：

1. **命令行参数**（最高优先级）：如 `-O3`、`--mtriple=x86_64-linux-gnu`
2. **配置文件**：`omconfig.json` 或 `--config-file` 指定的 JSON 文件
3. **环境变量**（最低优先级）：`ONNX_MLIR_FLAGS` 环境变量

### F-008：优化级别

**信源**：`src/Compiler/CompilerOptions.hpp` L46；`src/Compiler/CompilerPasses.cpp` L321-L324

| 级别 | 说明 | 关键优化 |
|------|------|----------|
| `-O0` | 默认级别，无优化 | 无 tiling、无 SIMD、无并行 |
| `-O1` | 基础优化 | 基础 canonicalization |
| `-O2` | 中级优化 | 更多 Pass |
| `-O3` | 推荐最高级别 | Tiling（循环分块）+ SIMD 向量化 + 并行化 |

### F-009：目标架构选项

**信源**：`src/Compiler/CompilerOptions.hpp` L50-L61, L105-L108, L148-L150

| 选项 | 用途 |
|------|------|
| `--mtriple=<triple>` | 目标三元组（如 `x86_64-linux-gnu`） |
| `--march=<arch>` | 目标架构（如 `x86-64`, `z16`） |
| `--mcpu=<cpu>` | 目标 CPU（已废弃，由 march 替代） |
| `--maccel=<accel>` | 目标加速器（如 `NNPA`） |
| `--Xopt <opts>` | 传递选项给 LLVM `opt` |
| `--Xllc <opts>` | 传递选项给 LLVM `llc` |
| `--mllvm <opts>` | 传递选项给 LLVM 后端 |

### F-010：调试/分析选项

**信源**：`src/Compiler/CompilerOptions.hpp` L130-L180

| 选项 | 用途 |
|------|------|
| `--print-ir[=after/before/all]` | 在 Pass 前后打印 IR |
| `--preserve-mlir` | 保留 MLIR 中间文件 |
| `--preserve-llvmir` | 保留 LLVM IR 中间文件 |
| `--preserve-bitcode` | 保留 LLVM bitcode 文件 |
| `--instrument-stage=<stage>` | 在指定阶段插桩 |
| `--profile-ir=<stage>` | 对指定阶段 IR 进行性能剖析 |
| `--enable-timing` | 输出 Pass 计时报告 |
| `--enable-bind-check` | 启用边界检查 |
| `--verify-input-tensors` | 验证输入张量 |

### F-011：外部 LLVM 工具链调度

**信源**：`src/Compiler/CompilerUtils.cpp` L298-L578

MLIR Pass 管线完成后，编译器调用外部 LLVM 工具链完成最终代码生成：

```
MLIR Pass 管线（内存中，ONNX→...→LLVM Dialect）
    │
    ▼ translateModuleToLLVMIR()
LLVM IR（内存中 Module）
    │
    ▼ writeBitcodeToFile()  （genLLVMBitcode）
LLVM bitcode 文件 (.bc)
    │
    ▼ 调用系统 opt  ← --Xopt 透传选项
优化后的 bitcode
    │
    ▼ 调用系统 llc  ← --Xllc 透传选项   （genModelObject）
目标文件 (.o/.obj)
    │
    ▼ 调用系统 cxx (g++/clang++/cl) ← 平台条件编译  （genSharedLib）
共享库 (.so/.dylib/.dll)
    │（EmitJNI 时继续）
    ▼ 编译 JNI C 包装器 + 调用 jar  （genJniJar）
JNI jar 包 (.jar)
```

`Command` 类封装外部进程调用，处理平台差异（Windows 下使用 `cmd /c`，POSIX 下直接 fork/exec）。

## 代码引用

```cpp
// CompilerUtils.hpp - 编译阶段枚举（简化）
enum class CompilePhase {
  ONNXToMLIR,     // Stage 1: ONNX → MLIR (Krnl/Linalg)
  MLIRToLLVMIR,   // Stage 2: MLIR → LLVM IR
  LLVMBitcode,    // Stage 3: LLVM IR → bitcode (opt)
  ModelObject,    // Stage 4: bitcode → .o (llc)
  SharedLib,      // Stage 5: .o → .so/.dll (cxx)
  JniJar,         // Stage 6+: .so + JNI wrapper → .jar
};

void showCompilePhase(CompilePhase phase, int totalPhases,
                      const std::string& phaseName);
```
