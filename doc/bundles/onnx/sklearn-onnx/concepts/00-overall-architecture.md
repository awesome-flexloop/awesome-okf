---
type: concept
title: "sklearn-onnx 整体架构：四阶段类编译器管线"
description: "sklearn-onnx 不是简单的 sklearn→ONNX 直接翻译器，而是一套类编译器架构：解析→拓扑IR→数据流调度→ONNX组装四阶段管线"
sources:
  references: [../references/convert-api.md, ../references/topology-ir.md, ../references/registration-algebra.md]
  facts: [F-003, F-009, F-011, F-016, F-022, F-023]
---

# sklearn-onnx 整体架构：四阶段类编译器管线

## 核心理解

sklearn-onnx（skl2onnx）不是简单地遍历 sklearn 模型然后直接调用 `onnx.helper` 生成节点，而是构建了一套完整的**类编译器中间表示（IR）管线**。从 sklearn 对象到 ONNX 模型，数据经历四个阶段的变换：

```
┌──────────────────────────────────────────────────────────────┐
│                    convert_sklearn() 入口                     │
│              接收 model + initial_types + options             │
├──────────────────────────────────────────────────────────────┤
│  阶段1：Parse（解析）                                          │
│  parse_sklearn_model()                                        │
│  sklearn 对象树 → 递归遍历 → Topology IR（粗粒度）              │
│  · 每个 sklearn 估计器 → 一个 Operator 节点（非 ONNX 算子）     │
│  · 估计器间数据连接 → Variable 边                              │
│  · Scope 管理命名空间                                          │
├──────────────────────────────────────────────────────────────┤
│  阶段2：Shape Inference（形状推断）                            │
│  convert_operators() 数据流调度中自动执行                       │
│  当 Operator 所有 inputs 都"就绪"（is_fed=True）时：           │
│  · 调用 shape_calculator 推断输出类型/形状                     │
│  · 输出 Variable 标记为 is_fed=True                           │
├──────────────────────────────────────────────────────────────┤
│  阶段3：Convert（转换）                                        │
│  在数据流调度中紧接 shape_calculator 之后执行                   │
│  调用 converter 函数，向 ModelComponentContainer 追加：         │
│  · 细粒度 ONNX NodeProto（一个 sklearn Operator → 多个节点）   │
│  · TensorProto（权重 initializer）                             │
│  · ValueInfoProto（输入输出声明）                               │
├──────────────────────────────────────────────────────────────┤
│  阶段4：Assemble（组装）                                       │
│  convert_topology()                                           │
│  · 拓扑排序 ensure_topological_order()                         │
│  · make_model_from_container() 组装 ModelProto                │
│  · 设置 ir_version / producer_name / opset_import             │
│  · 可选 remove_identity 删除冗余节点                           │
│  · 递归处理 local_functions（FunctionProto）                   │
└──────────────────────────────────────────────────────────────┤
                      ↓
               ONNX ModelProto
```

## 为什么需要中间表示？

直觉上 scikit-learn 模型大多是线性 Pipeline 结构，似乎可以"一遍遍历直接生成 ONNX"。但 sklearn-onnx 选择了类编译器架构，原因有三：

### 1. 复合模型需要图层面决策

Pipeline 中间步骤的 classifier 需要关闭 zipmap（避免中间步骤输出字典序列），ColumnTransformer 需要列切片和条件合并（多列输入先 Concat 再送 OneHotEncoder 等特例），FeatureUnion 需要并行分支和加权 Concat。这些都需要在**图层面**做全局决策，而非逐个估计器独立处理。

### 2. ShapeCalculator 和 Converter 解耦

类型推断和代码生成是两个独立注册的函数，且可以被用户分别覆盖（四级优先级链）。这意味着用户可以只替换类型推断逻辑而不改代码生成，反之亦然。直接翻译模式无法实现这种解耦。

### 3. Converter 可以动态追加 Operator

在转换过程中，converter 函数可以向拓扑中**追加新的 Operator**（如隐式类型转换 Cast、预处理 Concat 等）。调度算法以固定点迭代方式运行，直到所有 Operator 都被评估。这种"代码生成时可以修改 IR"的能力是直接翻译做不到的。

## 粗粒度 IR vs 细粒度节点

sklearn-onnx 的一个关键设计是**两级粒度分离**：

| 层级 | 粒度 | 构成 | 阶段 |
|------|------|------|------|
| Topology IR | 粗粒度 | Operator（对应 sklearn 估计器）、Variable（数据流） | Parse 阶段构建 |
| ONNX Graph | 细粒度 | NodeProto（对应 ONNX 标准算子）、TensorProto（权重） | Convert 阶段展开 |

例如，一个 `SklearnLinearClassifier` Operator 在 Convert 阶段可能展开为：
- `ai.onnx.ml.LinearClassifier` 节点（或 MatMul + Add + Softmax 的等价组合）
- 若干 Constant 初始值（系数矩阵、截距向量）
- 可选的 ZipMap 节点（输出字典化）
- 可选的 Cast/Identity 节点

这种粗粒度→细粒度的展开，正是编译器中"IR 降级（lowering）"的经典模式。

## 关键组件一览

| 组件 | 文件 | 职责 |
|------|------|------|
| `convert_sklearn()` | `convert.py` | 总入口，编排四阶段流程 |
| `parse_sklearn_model()` | `_parse.py` | 阶段1：递归解析 sklearn 对象树为 Topology |
| `Topology` | `common/_topology.py` | IR 容器，持有 Scopes 和 raw_model |
| `Scope` | `common/_topology.py` | 命名空间，管理唯一命名 |
| `Variable` | `common/_topology.py` | 数据流节点（IR 图的边） |
| `Operator` | `common/_topology.py` | 粗粒度算子节点（IR 图的顶点） |
| `ModelComponentContainer` | `common/_container.py` | ONNX 图构建器，收集细粒度节点 |
| `convert_topology()` | `common/_topology.py` | 阶段2-4：调度 + 组装 |
| 注册池 | `common/_registration.py` | converter/shape_calculator 双池 |
| `OnnxOperator` | `algebra/onnx_operator.py` | 嵌入式 DSL（替代手写 converter 的高层 API） |

## 模块导入即注册

一个容易被忽略的架构细节：转换器的注册发生在**模块导入时**，通过导入副作用完成。`convert.py` 顶部的两行：

```python
from . import shape_calculators
from . import operator_converters
```

触发 `shape_calculators/` 和 `operator_converters/` 下所有模块的导入，每个模块在文件底部调用 `register_converter()`/`register_shape_calculator()` 完成自注册。这意味着**导入 `skl2onnx` 包本身就完成了所有内置转换器的注册**，无需显式初始化调用。

## 关联概念

- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — 深入四阶段的具体执行细节
- [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](02-topology-ir.md) — 中间表示的核心类详解
- [转换器注册：别名→实现三级映射、shape_calculator配对](03-converter-registration.md) — 注册体系与别名合并机制
