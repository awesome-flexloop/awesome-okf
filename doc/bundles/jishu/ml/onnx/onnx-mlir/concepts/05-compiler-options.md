---
type: concept
title: "编译选项体系与性能调优"
description: "ONNX-MLIR 的编译选项体系——O0-O3 优化级别实质差异、目标三元组/架构/CPU 配置、加速器插件选项（NNPA）、调试与剖析选项、LLVM 选项透传机制，以及多源选项优先级"
sources:
  references: [../references/compiler-entry.md, ../references/dialects-runtime.md]
  facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-031]
---

# 编译选项体系与性能调优

## 核心理解

ONNX-MLIR 的编译选项控制从 ONNX 模型到目标代码的整个 lowering 过程。理解选项体系对于性能调优、跨平台部署和调试至关重要。选项可以来自三个来源（命令行 > 配置文件 > 环境变量），覆盖优化级别、目标架构、加速器、调试分析、LLVM 透传等多个维度。

## 选项来源与优先级

编译选项可以来自三个来源（F-006），优先级从高到低：

```
┌─────────────────────────────────────┐
│ 1. 命令行参数（最高优先级）           │
│    onnx-mlir -O3 --march=x86-64 ... │
├─────────────────────────────────────┤
│ 2. 配置文件（omconfig.json）         │
│    --config-file=myconfig.json      │
├─────────────────────────────────────┤
│ 3. 环境变量（最低优先级）             │
│    ONNX_MLIR_FLAGS="-O3"            │
└─────────────────────────────────────┘
```

这种三源设计允许：
- **系统级默认**：通过系统配置文件设置站点默认选项
- **项目级配置**：通过项目配置文件设置项目特定选项
- **命令行覆盖**：单次编译时通过命令行覆盖任何默认值

## 优化级别（-O0/-O1/-O2/-O3）

优化级别是最常用的选项，控制整个管线的优化强度（F-008）：

| 级别 | Tiling（循环分块） | SIMD 向量化 | 并行化（OpenMP） | 适用场景 |
|------|---------------------|-------------|------------------|----------|
| `-O0`（默认） | ❌ | ❌ | ❌ | 调试、理解 IR、验证正确性 |
| `-O1` | ❌ | ❌ | ❌ | 基础 canonicalization |
| `-O2` | 部分 | 部分 | ❌ | 平衡编译时间和性能 |
| `-O3`（推荐） | ✅ | ✅ | ✅ | 生产部署、最佳性能 |

### O3 级别的实质影响

`-O3` 不仅仅是"更多优化"，它在 ONNX→Krnl lowering 阶段就改变了生成的 IR 结构：

1. **Tiling（循环分块）**：对 Conv/MatMul 等计算密集型算子生成 `krnl.block` 分块循环
   - 将大维度循环拆分为 tile 外层循环 + point 内层循环
   - Tile 大小根据目标 CPU 缓存大小选择
   - 显著提高缓存命中率

2. **SIMD 向量化**：生成 `krnl.vector_type_cast` 将标量操作转为向量操作
   - 内层循环使用向量加载/存储（SIMD width 根据 arch 选择）
   - 利用 CPU SIMD 指令（SSE/AVX/AVX2/AVX-512/NEON/ZVECTOR）
   - 理论加速比可达 SIMD width（如 AVX-512 可达 16x for f32）

3. **并行化**：对外层循环标记 `krnl.parallel`，lowering 到 OpenMP
   - 利用多核 CPU 并行执行
   - 外层循环通常是 batch/输出通道等维度

### 编译阶段数与优化级别

不同输出目标的编译阶段数不同（F-007）：

| 输出目标 | 阶段数 | 阶段内容 |
|----------|--------|----------|
| EmitONNXBasic/EmitONNXIR/EmitMLIR | 3 | 仅 MLIR Pass 管线 |
| EmitLLVMIR | 4 | + LLVM IR 翻译 |
| EmitObj | 5 | + opt + llc |
| EmitLib（默认） | 6 | + cxx 链接共享库 |
| EmitJNI | 8 | + JNI 包装 + jar 打包 |

编译阶段通过 `showCompilePhase()` 打印进度：

```
[0/6]  0.00s ( 0.00s) ONNX To MLIR
[1/6]  0.35s ( 0.35s) MLIR To LLVM IR
[2/6]  0.42s ( 0.07s) LLVM BC To Object
[3/6]  0.85s ( 0.43s) Object To Shared Lib
...
```

使用 `--enable-timing` 可以获得更详细的 Pass 级别计时报告。

## 目标架构选项

### 目标三元组（--mtriple）

```bash
--mtriple=<target-triple>
```

目标三元组遵循 LLVM 标准格式 `<arch><sub>-<vendor>-<sys>-<abi>`：

| 目标平台 | 三元组示例 |
|----------|-----------|
| Linux x86-64 | `x86_64-linux-gnu` |
| Linux aarch64 | `aarch64-linux-gnu` |
| macOS x86-64 | `x86_64-apple-darwin` |
| macOS ARM64 | `arm64-apple-darwin` |
| Windows x64 | `x86_64-pc-windows-msvc` |
| IBM z/Architecture (s390x) | `s390x-ibm-linux` |

如果不指定，使用宿主系统的默认三元组。

### 目标架构（--march）

```bash
--march=<arch>
```

指定目标 CPU 架构，影响 SIMD 宽度选择和指令调度：

| arch 值 | 说明 |
|---------|------|
| `x86-64` | 通用 x86-64（SSE2 基线） |
| `x86-64-v2/v3/v4` | x86-64 功能级别（含 AVX/AVX2/AVX-512） |
| `native` | 宿主 CPU（自动检测特性） |
| `z14/z15/z16` | IBM z 系列（含 VX/NNPA） |
| `armv8-a` | ARMv8 AArch64 |

`--mcpu` 选项已废弃，由 `--march` 替代。

### 加速器（--maccel）

```bash
--maccel=<accelerator>
```

启用加速器插件（F-031）：

| 加速器 | 说明 |
|--------|------|
| `NNPA` | IBM Telum 集成 AI 加速器（z/Architecture） |
| （无/不指定） | 仅使用 CPU |

每个加速器可以接管整个编译管线（通过 `Accelerator::addPasses()`），插入自定义 Dialect 和 Pass。NNPA 提供 ZHigh（高层）和 ZLow（低层）两个 Dialect，将 ONNX Op 直接 lowering 到 NNPA 硬件指令。

### LLVM 选项透传

编译器支持三种方式向外部 LLVM 工具链传递额外选项（F-009/F-011）：

| 选项 | 传递目标 | 示例 |
|------|----------|------|
| `--Xopt <opts>` | LLVM `opt` 工具 | `--Xopt="-loop-vectorize -force-vector-width=8"` |
| `--Xllc <opts>` | LLVM `llc` 工具 | `--Xllc="-mattr=+avx512f"` |
| `--mllvm <opts>` | LLVM 后端（opt+llc） | `--mllvm=-print-after-all` |

这些透传选项为高级用户提供了直接控制 LLVM 后端的能力，无需修改编译器源码。

## 输出选项

| 选项 | 缩写 | 说明 |
|------|------|------|
| `--EmitONNXBasic` | `-EmitONNXBasic` | 输出基本 ONNX IR |
| `--EmitONNXIR` | `-EmitONNXIR` | 输出 ONNX Dialect IR |
| `--EmitMLIR` | `-EmitMLIR` | 输出 MLIR 内置 Dialect IR |
| `--EmitLLVMIR` | `-EmitLLVMIR` | 输出 LLVM IR |
| `--EmitObj` | `-c` | 输出目标文件 .o |
| `--EmitLib` | （默认） | 输出共享库 .so/.dll |
| `--EmitJNI` | | 输出 JNI jar 包 |
| `--output=<base>` | `-o` | 输出文件基础名（不含扩展名） |
| `--tag=<tag>` | | 符号标签（多模型加载避免冲突） |

### 输出文件命名

`-o` 指定输出文件的基础名（不含扩展名），编译器自动添加扩展名：

```bash
onnx-mlir -O3 model.onnx -o mymodel
# 生成：mymodel.so（Linux）/ mymodel.dll（Windows）/ mymodel.dylib（macOS）

onnx-mlir -EmitLLVMIR model.onnx -o mymodel
# 生成：mymodel.ll

onnx-mlir --EmitJNI model.onnx -o mymodel
# 生成：mymodel.jar + libmymodeljni.so
```

### Tag 选项

`--tag` 选项为编译产物中的所有符号添加后缀：

```bash
onnx-mlir -O3 --tag=resnet resnet50.onnx -o resnet50
# 共享库导出符号：
#   run_main_graph_resnet
#   omQueryEntryPoints_resnet
#   omInputSignature_resnet
#   ...
```

多模型在同一进程中加载时**必须**使用不同 tag，否则会发生符号冲突。

## 调试与剖析选项

ONNX-MLIR 提供了丰富的调试和性能分析选项（F-010）：

### IR 查看选项

| 选项 | 用途 |
|------|------|
| `--print-ir[=after/before/all]` | 在 Pass 之前/之后/全部打印 IR |
| `--print-ir-after=<pass-name>` | 只在指定 Pass 后打印 IR |
| `--preserve-mlir` | 保留中间 MLIR 文件（.mlir） |
| `--preserve-llvmir` | 保留中间 LLVM IR 文件（.ll） |
| `--preserve-bitcode` | 保留 LLVM bitcode 文件（.bc） |

这些选项对于理解 lowering 过程、调试编译错误非常有用。例如：

```bash
# 查看 ONNX→Krnl lowering 前后的 IR
onnx-mlir --print-ir=before,after -EmitMLIR model.onnx

# 保留所有中间文件
onnx-mlir --preserve-mlir --preserve-llvmir --preserve-bitcode -O3 model.onnx
```

### 性能剖析选项

| 选项 | 用途 |
|------|------|
| `--enable-timing` | 输出 Pass 计时报告 |
| `--instrument-stage=<stage>` | 在指定编译阶段插桩 |
| `--profile-ir=<stage>` | 对指定阶段 IR 进行性能剖析 |
| `--instrument-op=<op-name>` | 对指定 Op 插桩 |

`--enable-timing` 输出类似：

```
===-------------------------------------------------------------------------===
                      ... Pass execution timing report ...
===-------------------------------------------------------------------------===
  Total Execution Time: 1.2345 seconds

   ---User Time---   --System Time--   ...  Pass Name
   0.3562 ( 28.9%)   0.0123 ( 12.1%)        ONNXToKrnl
   0.2891 ( 23.4%)   0.0089 (  8.8%)        ConvertKrnlToLLVM
   ...
```

`--instrument-stage` 和 `--profile-ir` 在运行时收集每个 Op 的执行时间，输出到 stderr 或通过 `omInstrumentPrint()` 获取。

### 验证与安全选项

| 选项 | 用途 |
|------|------|
| `--enable-bind-check` | 启用运行时边界检查（调试越界访问） |
| `--verify-input-tensors` | 运行时验证输入张量形状/类型是否匹配签名 |
| `--opt-report` | 输出优化报告 |

`--enable-bind-check` 在 O0 调试时特别有用，它在每个 `krnl.load`/`krnl.store` 前插入边界检查，越界时打印错误信息而非静默内存破坏。

### 其他选项

| 选项 | 用途 |
|------|------|
| `--use-linalg-path` | 启用 Linalg 替代 lowering 路径（实验性） |
| `--linalg-ops=<ops>` | 指定使用 Linalg lowering 的 Op 列表 |
| `--onnx-opset-version=<ver>` | 指定 ONNX opset 版本 |
| `--config-file=<path>` | 指定配置文件路径 |
| `--report-heap-usage` | 报告编译时堆内存使用 |
| `--allow-constant-heap` | 允许常量存储在堆上（大模型支持） |

## 常用调优场景

### 场景 1：生产部署最佳性能

```bash
onnx-mlir -O3 --march=native --mtriple=x86_64-linux-gnu \
  model.onnx -o model --tag=model1
```

- `-O3`：启用全部优化（tiling+SIMD+并行）
- `--march=native`：针对宿主 CPU 优化（使用 AVX/AVX2 等全部特性）
- `--tag`：为模型指定唯一符号后缀

### 场景 2：交叉编译到目标架构

```bash
# 交叉编译到 aarch64
onnx-mlir -O3 --mtriple=aarch64-linux-gnu --march=armv8-a \
  model.onnx -o model
```

需要确保安装了 aarch64 交叉编译工具链（包含 aarch64-linux-gnu-g++ 等）。

### 场景 3：调试编译错误

```bash
onnx-mlir -O0 --print-ir=all --preserve-mlir \
  --enable-bind-check model.onnx -o model
```

- `-O0`：关闭优化，生成最简 IR
- `--print-ir=all`：查看每个 Pass 前后的 IR
- `--preserve-mlir`：保留中间文件供检查
- `--enable-bind-check`：运行时检测越界

### 场景 4：性能剖析

```bash
onnx-mlir -O3 --enable-timing --instrument-stage=onnx-to-krnl \
  --profile-ir=krnl model.onnx -o model

# 运行模型（会输出剖析信息）
LD_LIBRARY_PATH=. ./run_model
```

### 场景 5：使用 NNPA 加速器

```bash
onnx-mlir -O3 --maccel=NNPA --mtriple=s390x-ibm-linux \
  --march=z16 model.onnx -o model
```

需要 z/Architecture 硬件（IBM Telum 处理器）和支持 NNPA 的 LLVM 工具链。

## 外部工具链依赖

ONNX-MLIR 不是自包含编译器，它依赖系统安装的外部工具链（F-011/I-02 洞察）：

| 工具 | 来源 | 用途 |
|------|------|------|
| `opt` | LLVM 项目 | LLVM bitcode 优化 |
| `llc` | LLVM 项目 | LLVM IR → 目标文件 |
| `c++` / `g++` / `clang++` | 系统 C++ 编译器 | 目标文件 → 共享库 |
| `jar` | JDK | JNI jar 打包（仅 EmitJNI） |

⚠️ **版本匹配至关重要**：ONNX-MLIR 依赖特定 commit 的 LLVM 项目。系统安装的 opt/llc 版本必须与编译 ONNX-MLIR 时使用的 LLVM commit 匹配，否则可能出现 bitcode 兼容性错误或代码生成错误。README.md 中明确标注了支持的 LLVM commit hash。

部署时验证工具链：

```bash
# 检查 opt/llc 版本
opt --version
llc --version

# 检查 C++ 编译器
c++ --version
```

## 关联概念

- [ONNX-MLIR 整体架构](00-overall-architecture.md) — 了解选项如何影响整体编译管线
- [Krnl Dialect：编译策略层](02-krnl-dialect.md) — 理解 O3 级别如何改变 Krnl IR 生成
- [Dialect 转换管线](03-lowering-pipeline.md) — 了解各优化 Pass 在管线中的位置
- [运行时执行模型](04-runtime-execution.md) — 了解 tag 选项和验证选项的运行时效果
- [编译 ONNX 模型为共享库](../examples/compile-model.md) — 端到端编译示例
