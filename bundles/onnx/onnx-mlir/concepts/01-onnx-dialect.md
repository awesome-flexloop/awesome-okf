---
type: concept
title: "ONNX Dialect：ONNX 算子的 MLIR 表示"
description: "ONNX Dialect 的命名空间、TableGen 操作定义体系、ShapeInference 接口、ONNXTensorEncodingAttr 自定义布局属性，以及 ONNX 级别的预处理 Pass"
sources:
  references: [../references/dialects-runtime.md, ../references/compiler-entry.md]
  facts: [F-012, F-013, F-014, F-024, F-030]
---

# ONNX Dialect：ONNX 算子的 MLIR 表示

## 核心理解

ONNX Dialect 是 ONNX-MLIR 中对 ONNX 算子集的 MLIR 原生表示。它将 ONNX 规范定义的每个算子（Op）映射为 MLIR 中的一个 Operation，使得 ONNX 计算图可以在 MLIR 的基础设施上进行分析、优化和 lowering。ONNX Dialect 处于 lowering 流水线的**最顶层（语义层）**，保持 ONNX 算子的完整语义，执行与硬件无关的图级优化。

## Dialect 声明

ONNX Dialect 通过 TableGen 声明（F-012）：

```tablegen
def ONNX_Dialect : Dialect {
  let name = "onnx";                     // 文本形式：onnx.Add, onnx.Conv 等
  let cppNamespace = "::mlir";           // C++ 命名空间
  let dependentDialects = ["::mlir::func::FuncDialect"];
  let useDefaultAttributePrinterParser = 0;  // 自定义属性解析/打印
  let hasConstantMaterializer = 1;           // 支持常量物化
}
```

关键设计决策：
- **自定义属性打印器**：因为 ONNX 算子有大量自定义属性（如 `ONNXTensorEncodingAttr`），不使用默认属性打印器
- **常量物化器**：支持在 folding 过程中将常量属性具体化为 MLIR 常量操作
- **仅依赖 func Dialect**：ONNX 层不依赖 Affine/Linalg/MemRef 等更底层的 Dialect，保持语义层的纯净

## Op 定义体系

### TableGen 文件组织

ONNX 算子的 TableGen 定义分布在两个文件中（F-013）：

| 文件 | 内容 |
|------|------|
| `src/Dialect/ONNX/ONNX.td` | 主定义文件，包含标准 ONNX 算子 |
| `src/Dialect/ONNX/AdditionalONNXOps.td` | 非标准扩展算子 |

每个 ONNX Op 对应 MLIR 中的一个 Op 类，命名遵循 `ONNX<OpName>Op` 模式：
- `onnx.Add` → `ONNXAddOp`
- `onnx.Conv` → `ONNXConvOp`
- `onnx.MatMul` → `ONNXMatMulOp`
- `onnx.Relu` → `ONNXReluOp`

### Op 接口

ONNX Op 实现两个核心接口以支持形状推断（F-013）：

| 接口 | 用途 |
|------|------|
| `ShapeInferenceOpInterface` | 定义形状推断逻辑，根据输入形状计算输出形状 |
| `ShapeHelperOpInterface` | 提供形状计算的辅助方法 |

这两个接口是 ONNX 级别形状推断 Pass 的基础——编译器需要在 lowering 之前确定张量形状，才能生成正确的循环结构和内存分配。

## ONNXTensorEncodingAttr：自定义布局编码

ONNX Dialect 提供 `ONNXTensorEncodingAttr` 自定义属性（F-014），用于描述数据布局变换。这是 ONNX-MLIR 实现 SIMD 向量化和 tiling 优化的关键 IR 机制。

### 属性参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `dataLayout` | DataLayout 枚举 | 数据布局类型（如 NCHW、NCHWxC 等） |
| `xFactor` | 整数 | X 方向（列方向）分块因子 |
| `yFactor` | 整数 | Y 方向（行方向）分块因子 |

### 设计目的

标准 MLIR 的 MemRef 类型支持通过 layout map 描述数据布局，但 ONNXTensorEncodingAttr 提供了更高层次的抽象，专门针对深度学习中常见的数据布局变换：

```
标准 NCHW 布局：
  [N, C, H, W]     → 连续内存存储

NCHWxC tiling 布局（SIMD 友好）：
  [N, C/xFactor, H, W, xFactor]  → 按 xFactor 分块，每块连续存储
  使得内层循环可以直接加载 SIMD 向量
```

当 O3 优化启用 tiling 和 SIMD 时，ONNX→Krnl lowering 会为相关张量附加此属性，后续 lowering Pass 根据此属性生成正确的内存访问模式。

## ONNX 级别预处理 Passes

在 lowering 到 Krnl 之前，编译器在 ONNX Dialect 层面执行一系列预处理 Pass（F-024），这些 Pass 不改变 Dialect 层级，只在 ONNX 语义层进行图变换：

```
导入的 ONNX ModuleOp
    │
    ▼ DecomposeONNXToONNX（分解不支持的 Op）
    │  例：将 ONNX 高版本 Op 分解为低版本等价组合
    │
    ▼ RecomposeONNXToONNX（重组 Op）
    │  将分解的模式重组为优化后的形式
    │
    ▼ ONNXHybridTransform（动态 Pass 管线）
    │  根据 IR 特征动态选择优化
    │
    ▼ ShapeInference（形状推断）★
    │  利用 ShapeInferenceOpInterface 传播形状信息
    │  这是后续所有 lowering 的基础
    │
    ▼ ConstProp（常量折叠）
    │  将常量输入的 Op 折叠为常量
    │
    ▼ ONNXOpTransform（动态迭代优化）
    │  迭代应用优化直到收敛
    │
    ▼ SimplifyShapeRelatedOps（简化形状相关 Op）
    │
    ▼ StandardFuncReturn
    │  ONNXReturnOp → func::ReturnOp（统一返回约定）
    │
    ▼ SymbolDCE（死代码消除）
    │
    ▼ ONNXCSEWithNodeName（公共子表达式消除）
    │
    ▼ FusionOpTransform（算子融合）
    │  将多个小 Op 融合为更少的大 Op
    │
    ▼ SetONNXNodeName（设置节点名称）
    │
    ▼ InstrumentPass（插桩，按需）
    │
预处理后的 ONNX ModuleOp（形状已知、常量已折叠、无死代码）
```

这些 Pass 的执行顺序非常重要：
1. **形状推断必须早于依赖形状的优化**：ConstProp、Fusion 等需要知道输出形状
2. **Decompose 必须早于 ShapeInference**：分解后的 Op 才有形状推断实现
3. **CSE 和 DCE 在 Fusion 之后**：融合可能产生新的公共子表达式
4. **StandardFuncReturn 在所有 ONNX 变换之后**：确保后续 lowering 看到统一的 func.return

## ONNX 前端导入

ONNX 模型的导入由 `FrontendDialectTransformer` 实现（F-030）：

```cpp
// 从文件导入
OwningOpRef<ModuleOp> module =
    ImportFrontendModelFile("model.onnx", context, importOptions);

// 从内存缓冲区导入
OwningOpRef<ModuleOp> module =
    ImportFrontendModelArray(onnxBinaryData, size, context, importOptions);
```

`ImportOptions` 控制导入行为：
- `verbose`：详细输出
- `useOnnxModelTypes`：是否使用 ONNX 模型的类型信息
- `keepCustomOp`：保留自定义 Op
- `sortNodeByName`：按名称排序节点（影响确定性）
- `dimParams`：维度参数映射（动态维度）

导入过程将 ONNX protobuf 中的 GraphProto、NodeProto、TensorProto 等结构转换为对应的 MLIR Operation、Value 和 Attribute。

## Op Lowering 的组织

每个 ONNX Op 的 Krnl lowering 实现在 `src/Conversion/ONNXToKrnl/` 目录下，按类别分子目录：

```
src/Conversion/ONNXToKrnl/
├── Math/          # 数学算子：Add/Mul/Relu/Softmax 等
├── NN/            # 神经网络算子：Conv/MatMul/Pooling/BatchNorm 等
├── Tensor/        # 张量算子：Reshape/Transpose/Concat/Split 等
├── RNN/           # 循环神经网络：LSTM/GRU/RNN 等
└── ControlFlow/   # 控制流：If/Loop/Scan 等
```

这种按类别组织的方式使得查找和修改特定算子的 lowering 逻辑非常直观。核心算子（Conv、MatMul 等）的 lowering 代码通常是最复杂的，因为它们需要在 Krnl IR 中编码 tiling、SIMD 和并行化策略。

## 关联概念

- [ONNX-MLIR 整体架构](00-overall-architecture.md) — 了解 ONNX Dialect 在整体流水线中的位置
- [Krnl Dialect：编译策略层中间表示](02-krnl-dialect.md) — 理解 ONNX Dialect 下一层的 Krnl Dialect
- [Dialect 转换管线](03-lowering-pipeline.md) — 了解 ONNX→Krnl lowering 的具体 Pass 编排
