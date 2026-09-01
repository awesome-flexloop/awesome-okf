---
type: concept
title: "Krnl Dialect：编译策略层中间表示"
description: "Krnl Dialect 的设计哲学——面向编译优化策略的中间层，循环优化操作集、内存操作、运行时桥接操作，以及与 Linalg 路径的对比（I-01 反常识洞察）"
sources:
  references: [../references/dialects-runtime.md]
  facts: [F-015, F-016, F-017, F-018, F-020, F-023]
---

# Krnl Dialect：编译策略层中间表示

## 核心理解（I-01 洞察）

Krnl Dialect 是 ONNX-MLIR **真正的架构创新**，但它不是"又一个张量计算 Dialect"。Krnl 的定位是**"编译策略层"**——它不表达张量计算语义（语义仍在 ONNX/Linalg Dialect 中），而是显式建模循环优化原语、内存操作和运行时桥接。

这与编译器设计的常识相反——传统 wisdom 认为"中间表示应保持语义中立、与优化策略解耦"。但 Krnl Dialect 恰恰将循环 tiling、permute、unroll、SIMD、parallel 等优化决策**编码进 IR 本身**（而非作为独立 Pass 操作）。这意味着 Op lowering 代码在生成 Krnl IR 时就已经做出了 tiling 大小、SIMD 宽度、循环顺序等决策。

**Krnl 既是 IR 又是优化策略载体**——这种"优化即IR"的设计是理解 ONNX-MLIR 性能调优的关键。

## Krnl Dialect 在流水线中的位置

```
ONNX Dialect（语义层：算子是什么）
    │
    │  ONNX Op lowering 时直接编码优化策略
    ▼
Krnl Dialect（策略层：如何优化执行）★
    │  循环定义/分块/重排/展开/SIMD/并行
    │  内存分配/拷贝/tile buffer
    │  运行时调用/入口点/插桩
    │
    ▼  KrnlToAffine Pass
Affine/SCF Dialect（标准层：MLIR 标准循环结构）
    │
    ▼  ... 继续 lowering 到 LLVM
```

ONNX-MLIR 源码注释明确说明了 Krnl 的定位（docs/LoweringCode.md）：

> "krnl dialect is our main dialect to lower ONNX operations into loops. This dialect is one step above the MLIR affine dialect."

"one step above affine" 意味着 Krnl 比 Affine Dialect 具有更高层次的抽象——它保留了优化意图，而 Affine 只是具体的循环嵌套。

## Dialect 依赖关系

Krnl Dialect 声明依赖 8 个 MLIR 内置 Dialect（F-015）：

```tablegen
def Krnl_Dialect : Dialect {
  let name = "krnl";
  let dependentDialects = [
    "::mlir::affine::AffineDialect",    // affine.for 循环
    "::mlir::arith::ArithDialect",      // 算术运算
    "::mlir::func::FuncDialect",        // 函数
    "::mlir::linalg::LinalgDialect",    // Linalg 互操作
    "::mlir::math::MathDialect",        // 数学函数
    "::mlir::memref::MemRefDialect",    // 内存管理
    "::mlir::scf::SCFDialect",          // 结构化控制流
    "::mlir::shape::ShapeDialect"       // 形状计算
  ];
}
```

依赖 Affine 和 SCF 是因为 Krnl 的循环操作最终会 lowering 到这些结构；依赖 MemRef 是因为 Krnl 的内存操作基于 MemRef 类型；依赖 Linalg 是为了支持与 Linalg 路径的混合 IR 模式。

## 循环优化操作集

Krnl 提供了一组面向循环优化的高级操作（F-016），每个操作对应一个特定的循环变换：

### 循环定义与迭代

| 操作 | 语义 | Lowering 目标 |
|------|------|---------------|
| `krnl.define_loops` | 定义一组循环维度（指定循环范围） | 不直接产生代码，为后续 iterate/block 提供句柄 |
| `krnl.iterate` | 嵌套循环执行体 | 等价于 nested `affine.for` |

```mlir
// Krnl 循环示例：二维循环遍历 MxN 矩阵
%i, %j = krnl.define_loops 2
krnl.iterate(%i, %j) from (%c0, %c0) to (%M, %N) {
  ^bb0(%iv0: index, %iv1: index):
    %val = krnl.load %A[%iv0, %iv1] : memref<?x?xf32>
    // ... 计算
    krnl.store %res, %B[%iv0, %iv1] : memref<?x?xf32>
}
```

### 循环变换

| 操作 | 语义 | 优化目的 |
|------|------|----------|
| `krnl.block` | 循环分块（tiling） | 提高缓存局部性，将大循环拆为外层+内层tile |
| `krnl.permute` | 循环重排 | 改变迭代顺序（如行优先→列优先），优化内存访问模式 |
| `krnl.unroll` | 循环展开 | 消除循环开销，启用指令级并行 |
| `krnl.parallel` | 标记并行循环 | 映射到 OpenMP parallel for，利用多核 |

```mlir
// Tiling 示例：将 %i, %j 循环按 32x32 分块
%ib, %jb, %ii, %ji = krnl.block %i, %j by 32, 32
// 现在 %ib/%jb 是 tile 外层循环，%ii/%ji 是 tile 内层循环

// 并行化示例：标记外层循环可并行
krnl.parallel %ib
```

### 专用内核

| 操作 | 语义 | 说明 |
|------|------|------|
| `krnl.matmul` | 专用矩阵乘内核 | 内置 tiling + SIMD 支持，是 O3 优化的核心 |

`krnl.matmul` 是最复杂的 Krnl Op，它将矩阵乘的 tiling 策略、SIMD 向量化、缓存优化直接编码在单个 Op 中，而不是通过通用循环变换组合实现。这是"优化即IR"设计的典型体现——MatMul 的优化模式已经被充分研究，直接提供专用 Op 比通用变换组合更高效。

## 内存操作集

Krnl 提供了一组内存操作（F-017），构建在 MLIR MemRef 类型之上：

### 基本内存访问

| 操作 | 语义 |
|------|------|
| `krnl.load` | 从 MemRef 加载元素（支持 affine 下标） |
| `krnl.store` | 存储元素到 MemRef（支持 affine 下标） |

`krnl.load`/`krnl.store` 与 MLIR 标准 `memref.load`/`memref.store` 的区别在于它们支持 Krnl 特有的 tile 偏移和 SIMD 向量访问模式。

### 内存操作

| 操作 | 语义 |
|------|------|
| `krnl.memcpy` | 内存拷贝（类似 C memcpy） |
| `krnl.memset` | 内存填充（类似 C memset） |
| `krnl.global` | 全局常量（持有 dense elements 属性，用于模型权重） |

`krnl.global` 用于表示模型中的常量权重（initializer），在 Krnl→LLVM lowering 时被转换为 LLVM 全局变量。对于大模型，常量可能存储在独立文件中（`.lrodata` 段）。

### Tile 缓冲区操作

| 操作 | 语义 | 优化目的 |
|------|------|----------|
| `krnl.copy_to_tile_buffer` | 从原始 MemRef 拷贝到 tile 缓冲区 | 将计算所需的数据块拷贝到连续的快速内存 |
| `krnl.copy_from_tile_buffer` | 从 tile 缓冲区拷回 | 计算完成后写回结果 |
| `krnl.vector_type_cast` | 向量类型转换 | 将标量数组视图转换为 SIMD 向量类型 |

Tile buffer 操作支持 overread 和 padding 优化——当 tile 大小不整除维度时，边界 tile 可以读取超出边界的数据（通过 padding 填充），避免边界检查开销。

## 运行时桥接操作

Krnl 还提供了一组与运行时交互的操作（F-018）：

| 操作 | 语义 |
|------|------|
| `krnl.call` | 调用外部 C 函数（参数已 lowering 为 MemRef） |
| `krnl.entry_point` | 标记 ONNX 模型主入口点 |
| `krnl.print_tensor` | 运行时打印张量（调试用） |
| `krnl.random_normal` | 随机正态分布生成（调用运行时函数） |
| `krnl.find_index` | 完美哈希表查找（用于字符串/稀疏操作） |
| `krnl.instrument` | 运行时插桩点（性能剖析） |

`krnl.call` 是一个重要的"逃逸口"——它允许将某些 ONNX Op 的实现委托给外部 C 函数（如 BLAS 库），而不是生成纯 MLIR 循环。`krnl.entry_point` 在 Krnl→LLVM lowering 时被转换为 `run_main_graph` 入口函数。

## Krnl → Affine Lowering

Krnl 循环操作最终通过 `addKrnlToAffinePasses()` 转换为标准 MLIR 结构（F-020）：

```mlir
// Krnl IR（含优化意图）
%i, %j = krnl.define_loops 2
%ib, %jb, %ii, %ji = krnl.block %i, %j by 32, 32
krnl.parallel %ib
krnl.iterate(%ib, %jb, %ii, %ji) ...

// 降低到 Affine（具体循环结构）
affine.parallel for %ib = 0 to #M_tile {
  affine.for %jb = 0 to #N_tile {
    affine.for %ii = 0 to 32 {
      affine.for %ji = 0 to 32 {
        // 具体计算
      }
    }
  }
}
```

KrnlToAffine Pass 还执行一个重要优化：**消除仅写不读的局部 MemRef 分配**——这些通常是 lowering 过程中产生的临时变量，不需要实际分配内存。

## Krnl vs Linalg：两种设计哲学的对比

这是 I-01 洞察的核心——Krnl 路径与 Linalg 路径代表了深度学习编译器设计的两种哲学：

| 维度 | Krnl 路径 | Linalg 路径 |
|------|-----------|-------------|
| 优化时机 | lowering 时编码到 IR | 通过后续 transform pass 应用 |
| 抽象层次 | 接近循环实现（高耦合） | 张量级语义（低耦合） |
| 优化策略 | 手写 lowering 模式 | 通用 Linalg transform |
| 成熟度 | 默认，更成熟 | 实验性，向 MLIR 主流靠拢 |
| 灵活性 | 每个 Op 可独立调优 | 统一框架，通用优化 |
| Bufferization | 手动（DialectBuilder 模式） | One-Shot Bufferize（自动） |
| SIMD 策略 | krnl.vector_type_cast 手动向量化 | Linalg vectorization pass |
| 并行化 | krnl.parallel 标记 → OpenMP | SCF parallel → OpenMP |

**为什么 Krnl 是必要的？**

尽管 Linalg 代表 MLIR 社区的主流方向，但 Krnl 路径有其存在的理由：

1. **确定性性能**：手写 lowering 模式确保关键算子（Conv/MatMul）的性能可预测
2. **专用优化**：`krnl.matmul` 等专用 Op 可以编码领域专家的优化经验
3. **渐进式开发**：不需要等待 Linalg 生态成熟即可支持新算子
4. **调试友好**：Krnl IR 比 Linalg IR 更接近最终循环结构，便于理解和调试

**性能调优应关注什么？**

根据 I-01 洞察，ONNX-MLIR 的性能调优不应只关注 Pass Pipeline 配置，而应深入 `src/Conversion/ONNXToKrnl/` 下各 Op lowering 代码中 Krnl 循环的构造方式——特别是 `MatMul.cpp`、`Conv.cpp`、`Pooling.cpp` 等核心算子，因为这些代码决定了：
- 循环分块大小（tile size）
- SIMD 化条件
- 并行化决策
- 内存访问模式

## DialectBuilder 模式

Krnl Op 的构造在 lowering 代码中大量使用 **DialectBuilder 模式**——通过辅助类（如 `KrnlBuilder`、`MemRefBuilder`、`VectorBuilder`）封装 Krnl Op 的创建细节，使 lowering 代码更简洁可读：

```cpp
// 简化的 lowering 代码示例
KrnlBuilder createKrnl(rewriter, loc);
MemRefBuilder createMemRef(rewriter, loc);

// 定义循环
ValueRange loops = createKrnl.defineLoops(rank);
// 循环迭代
createKrnl.iterate(loops, lbs, ubs,
    [&](KrnlBuilder &ck, ValueRange indices) {
      // 计算体
      Value val = ck.load(inputMemRef, indices);
      // ...
      ck.store(result, outputMemRef, indices);
    });
```

## 关联概念

- [ONNX-MLIR 整体架构](00-overall-architecture.md) — 了解 Krnl 在双路径架构中的位置
- [ONNX Dialect](01-onnx-dialect.md) — 了解 Krnl 的上一层：ONNX 语义 Dialect
- [Dialect 转换管线](03-lowering-pipeline.md) — 了解 Krnl→Affine→LLVM 的具体转换流程
- [编译选项体系与性能调优](05-compiler-options.md) — 了解 O3 级别如何激活 Krnl 级别的 tiling/SIMD/并行
