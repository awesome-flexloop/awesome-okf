---
type: concept
title: "ONNX-MLIR 整体架构：多级 Lowering 编译器"
description: "ONNX-MLIR 的整体架构——多级 lowering 流水线、Krnl/Linalg 双 lowering 路径、7种输出目标、MLIR Pass+外部LLVM工具链的分层协作模型"
sources:
  references: [../references/compiler-entry.md, ../references/dialects-runtime.md]
  facts: [F-001, F-002, F-003, F-011, F-023, F-030, F-031]
---

# ONNX-MLIR 整体架构：多级 Lowering 编译器

## 核心理解

ONNX-MLIR 是一个基于 LLVM/MLIR 技术栈的 **ONNX 模型编译器**，其核心使命是将 ONNX 计算图逐步 lower 为可以在目标硬件上执行的原生代码。与传统深度学习运行时（如 ONNX Runtime）通过解释执行算子不同，ONNX-MLIR 将整个模型编译为自包含的共享库（.so/.dll/.dylib），通过最小运行时加载执行。

项目贡献四个核心组件：
1. **ONNX Dialect**：ONNX 算子集的 MLIR Dialect 表示
2. **Krnl Dialect**：面向编译优化策略的自定义中间 Dialect
3. **编译器接口**：从 ONNX 到 MLIR/LLVM/C/Java 的完整 lowering 管线
4. **多语言运行时**：Python/C/C++/Java 运行时 API（ExecutionSession + OMTensor）

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        命令行入口 (onnx-mlir.cpp)                    │
│   注册选项 → 加载配置 → 解析参数 → 创建MLIRContext → 加载Dialect    │
├─────────────────────────────────────────────────────────────────────┤
│                        前端导入 (Frontend)                           │
│   FrontendDialectTransformer                                        │
│   .onnx/.onnxtext/.json/.mlir → ONNX Dialect ModuleOp               │
├─────────────────────────────────────────────────────────────────────┤
│                    ONNX 预处理 Passes (addONNXToMLIRPasses)          │
│   形状推断 → 常量折叠 → 算子分解/重组 → 融合 → CSE → DCE            │
├─────────────────────────────┬───────────────────────────────────────┤
│     Krnl 路径（默认）         │     Linalg 路径（--use-linalg-path）   │
│  addONNXToKrnlPasses()      │  addONNXToLinalgPasses()              │
│  ONNX Op → Krnl Op          │  ONNX Op → Linalg Op                  │
│  O3: tiling+SIMD+parallel   │  One-Shot Bufferize                   │
│         │                   │         │                              │
│         ▼                   │         ▼                              │
│  addKrnlToAffinePasses()    │  addLinalgToAffinePasses()            │
│  Krnl 循环 → affine.for     │  Linalg → Affine/SCF                  │
│         │                   │  剩余ONNX → Krnl 路径                 │
│         └───────┬───────────┘         │                              │
│                 ▼                     │                              │
│         Affine/SCF Dialect ◄──────────┘                              │
├─────────────────────────────────────────────────────────────────────┤
│              Krnl→LLVM 最终 Lowering (addKrnlToLLVMPasses)           │
│   VectorToSCF → LowerAffine → Bufferization → SCFToOpenMP          │
│   → ConvertKrnlToLLVM（入口点转换/运行时函数生成/C包装）             │
├─────────────────────────────────────────────────────────────────────┤
│              MLIR → LLVM IR (translateModuleToLLVMIR)                │
├─────────────────────────────────────────────────────────────────────┤
│              外部 LLVM 工具链（进程外调用）                           │
│   opt（bitcode优化）→ llc（目标代码生成）→ cxx（链接共享库）         │
│   → jar（JNI打包，可选）                                             │
├─────────────────────────────────────────────────────────────────────┤
│                     输出产物（自描述共享库）                          │
│   run_main_graph() + omQueryEntryPoints() + omInputSignature()      │
│   + omOutputSignature() + omCompilationInfo()                       │
├─────────────────────────────────────────────────────────────────────┤
│                     运行时 (ExecutionSession)                        │
│   dlopen/LoadLibrary → dlsym查找符号 → run_main_graph推理           │
│   OMTensor/OMTensorList 数据结构 → C/C++/Python/Java 绑定           │
└─────────────────────────────────────────────────────────────────────┘
```

## 多级 Lowering 流水线

编译器核心是**多级 Dialect lowering 流水线**（F-002）：

```
ONNX Dialect ──→ Krnl Dialect ──→ Affine/SCF ──→ LLVM Dialect ──→ LLVM IR ──→ 目标代码
   (语义层)       (策略层)        (标准循环)     (LLVM IR)      (bitcode)    (.so/.dll)
```

每一层 lowering 的职责清晰分离：
- **ONNX Dialect**：保持 ONNX 算子语义，执行与硬件无关的图级优化（形状推断、常量折叠、算子融合）
- **Krnl Dialect**：显式编码循环优化策略（tiling、permute、unroll、SIMD、parallel），是 ONNX-MLIR 的核心创新层
- **Affine/SCF**：将 Krnl 优化意图翻译为 MLIR 标准循环结构，执行 bufferization 和内存管理
- **LLVM Dialect**：最终降级到 LLVM IR 级别，生成运行时桥接代码
- **LLVM IR → 目标代码**：通过外部工具链（opt/llc/cxx）完成

## Krnl vs Linalg：双 Lowering 路径

ONNX-MLIR 提供两条从 ONNX 到 LLVM 的 lowering 路径（F-023）：

### Krnl 路径（默认，更成熟）

Krnl 路径通过自定义 Krnl Dialect 显式表达循环优化意图。每个 ONNX Op 的 lowering 代码（位于 `src/Conversion/ONNXToKrnl/`）在生成 Krnl IR 时直接做出 tiling 大小、SIMD 宽度、循环顺序等决策。这种"优化即IR"的设计耦合度高但直接高效。

### Linalg 路径（实验性，向主流靠拢）

Linalg 路径利用 MLIR 社区的 Linalg Dialect 和 One-Shot Bufferize，遵循更主流的 "tensor-level op + transform dialect" 范式。目前实现为混合模式：部分 Op 转 Linalg，剩余 Op 仍走 Krnl，最终统一通过 KrnlToLLVM Pass 生成运行时函数。

| 维度 | Krnl 路径 | Linalg 路径 |
|------|-----------|-------------|
| 成熟度 | 默认，更成熟 | 实验性 |
| 优化方式 | lowering 时直接编码到 IR | 通过通用 transform pass |
| 与 MLIR 主流关系 | ONNX-MLIR 独创 | 对齐 MLIR 社区范式 |
| 启用方式 | 默认 | `--use-linalg-path` 或 `--linalg-ops` |
| Bufferization | 手动管理 | One-Shot Bufferize |

## 7 种输出目标

编译器支持 7 种输出目标（F-003），按 lowering 深度排列：

| 目标 | 扩展名 | 阶段数 | 用途 |
|------|--------|--------|------|
| EmitONNXBasic | `.mlir` | 3 | 查看前端导入后的基本 ONNX IR（调试） |
| EmitONNXIR | `.mlir` | 3 | 查看 ONNX 预处理后的 Dialect IR（调试） |
| EmitMLIR | `.mlir` | 3 | 查看 Krnl/Affine 级 MLIR IR（调试） |
| EmitLLVMIR | `.ll` | 4 | 查看 LLVM IR Dialect（调试） |
| EmitObj | `.o`/`.obj` | 5 | 编译到目标文件（需自行链接） |
| EmitLib | `.so`/`.dll`/`.dylib` | 6 | **默认**——编译到自描述共享库（部署用） |
| EmitJNI | `.jar` | 8 | 编译到 Java JNI jar 包（Java 部署） |

IR 输出目标（前4种）用于调试和理解 lowering 过程，二进制输出目标（后3种）用于实际部署。

## MLIR Pass + 外部工具链的分层协作

ONNX-MLIR 并非在 MLIR Pass Manager 内完成端到端编译，而是采用**"MLIR 变换器 + LLVM 工具链调度器"**的复合架构（洞察二）：

1. **MLIR Pass 阶段（内存中）**：从 ONNX Dialect 逐步 lowering 到 LLVM Dialect，通过 `translateModuleToLLVMIR()` 转为 LLVM IR Module
2. **外部工具链阶段（进程外）**：
   - `opt`：LLVM bitcode 优化
   - `llc`：LLVM IR → 目标文件
   - `cxx`（系统 C++ 编译器）：目标文件 → 共享库（处理平台特定链接逻辑）
   - `jar`：JNI 打包（可选）

这种设计的优点：
- 可通过 `--Xopt`/`--Xllc`/`--mllvm` 直接透传任意 LLVM 选项
- 复用系统链接器的平台特定逻辑（Windows .def/.lib、macOS dsymutil 等）
- 编译时不需要链接整个 LLVM 后端

缺点是需要系统安装匹配版本的 LLVM 工具链，且对 LLVM 版本有严格依赖。

## 加速器插件架构

ONNX-MLIR 支持可插拔加速器（F-031），通过 `src/Accelerators/` 目录下的 `Accelerator` 基类扩展。每个加速器可以：
- 注册自定义 Dialect（如 NNPA 的 ZHigh/ZLow Dialect）
- 通过 `accel->addPasses()` 接管整个编译管线（在任意阶段插入 Pass）
- 提供专用 lowering 路径

内置 NNPA（IBM Telum 集成 AI 加速器）是参考实现，针对 z/Architecture 的 AI 加速器提供定制编译支持。通过 `--maccel=NNPA` 启用。

## 编译产物：自描述共享库

编译输出的共享库不是黑盒二进制，而是**自描述可执行模块**（洞察三）：
- 导出 `run_main_graph()` 统一推理入口点（C ABI）
- 导出 `omQueryEntryPoints()` 枚举所有入口点
- 导出 `omInputSignature()`/`omOutputSignature()` 返回 JSON 格式签名
- 导出 `omCompilationInfo()` 返回编译信息 JSON

单个 .so/.dll 文件就是完全自包含的部署单元，运行时通过 `dlopen` 动态加载，不需要头文件或额外元数据文件。

## 关联概念

- [ONNX Dialect：ONNX 算子的 MLIR 表示](01-onnx-dialect.md) — 理解语义层 Dialect 的设计
- [Krnl Dialect：编译策略层中间表示](02-krnl-dialect.md) — 理解核心创新层 Krnl 的设计哲学
- [Dialect 转换管线：ONNX→Krnl→Affine→LLVM](03-lowering-pipeline.md) — 深入 lowering Pass 编排
- [运行时执行模型：ExecutionSession 与自描述共享库](04-runtime-execution.md) — 理解运行时加载与推理
- [编译选项体系与性能调优](05-compiler-options.md) — 了解优化级别和目标配置
