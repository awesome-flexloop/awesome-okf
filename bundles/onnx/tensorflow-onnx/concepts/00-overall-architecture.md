---
type: concept
title: "tf2onnx 整体架构：三阶段图转换流水线"
description: "tf2onnx 的整体架构设计：以 ONNX Protobuf 为内部 IR 的三阶段图转换流水线（Loader→Rewriter→Mapper→Optimizer），从模型加载到 ONNX 输出的完整路径"
sources:
  references: [../references/convert-entry.md, ../references/graph-rewriter.md, ../references/opset-mapping.md]
  facts: [F-001, F-004, F-005, F-011, F-012, F-013, F-014, F-022, F-023, F-025, F-033]
  insights: [I-002, I-003]
---

# tf2onnx 整体架构：三阶段图转换流水线

## 核心理解

tf2onnx 不是一个简单的"算子 A 映射为算子 B"的查表工具，而是一个**三阶段图转换流水线**系统。它将 TensorFlow 模型（Keras、SavedModel、GraphDef、TFLite、TF.js）转换为 ONNX 格式的过程，分解为三个性质完全不同的阶段，通过统一的 Graph 对象在阶段间传递。

整个系统的核心设计哲学是**"目标即 IR"**：不引入自定义中间表示，而是直接在 ONNX Protobuf 之上构建图操作 API，转换完成时图已经是合法的 ONNX 格式。

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     转换入口（Python API / CLI）                  │
│    from_keras / from_saved_model / from_function / from_graph_def│
│    from_tflite / python -m tf2onnx.convert                      │
├─────────────────────────────────────────────────────────────────┤
│                     Loader：模型加载与冻结                         │
│  tf_loader（from_saved_model / from_checkpoint / from_keras）    │
│  → 获取 concrete function → freeze_session → frozen GraphDef     │
├─────────────────────────────────────────────────────────────────┤
│              Protobuf 1:1 转换（tensorflow_to_onnx）              │
│  TF NodeDef → ONNX NodeProto（类型名保持 TF 原名）                 │
│  → 创建 Graph 对象（Node/Graph 包装 ONNX proto）                  │
│  → compute_const_folding_using_tf（TF 层面常量折叠）               │
├─────────────────────────────────────────────────────────────────┤
│           Stage 1: Rewriter（子图重写·模式匹配）                   │
│  pre-rewriters：20+ 重写器顺序执行                                │
│  ├─ fused op 拆分（FusedBatchNorm, BiasAdd+Conv）                 │
│  ├─ RNN 子图识别（LSTM, GRU）                                     │
│  ├─ 布局转换（Transpose 插入/消除）                                │
│  └─ numpy 常量折叠                                                │
│  → 子图递归应用（contained_graphs）                                │
├─────────────────────────────────────────────────────────────────┤
│           Stage 2: Mapper（单算子映射·版本注册表）                 │
│  tensorflow_onnx_mapping 遍历所有节点                             │
│  ├─ ops_mapping = tf_op.create_mapping(opset_version)            │
│  │  └─ @tf_op 装饰器注册的版本化处理器（version_N 方法）            │
│  ├─ DirectOp（pass）：Abs, Relu, Exp, Tanh...                   │
│  ├─ 重命名映射（onnx_op）：RealDiv→Div                           │
│  └─ 复杂映射：Conv, BatchNorm, MatMul（需设置属性/广播处理）       │
├─────────────────────────────────────────────────────────────────┤
│           Stage 3: Optimizer（ONNX 图优化·语义无关）               │
│  optimize_graph 迭代执行 12 个优化器直到收敛                        │
│  ├─ 布局优化：TransposeOptimizer                                │
│  ├─ 常量折叠：ConstFoldOptimizer                                 │
│  ├─ 冗余消除：IdentityOptimizer, MergeDuplicatedNodes            │
│  ├─ 算子融合：BackToBackOptimizer, GlobalPoolOptimizer           │
│  └─ late_rewriters：Target 平台条件后处理                         │
├─────────────────────────────────────────────────────────────────┤
│                     Output：ONNX ModelProto                      │
│  Graph.make_model() → 构建 ModelProto                            │
│  ├─ opset_imports（主 domain + ML domain + extra_opset）         │
│  ├─ IR 版本设置（根据 opset 自动选择）                             │
│  └─ ExternalTensorStorage（大模型外部存储）                        │
└─────────────────────────────────────────────────────────────────┘
```

## 三阶段流水线详解

### 为什么需要三阶段而非一步到位？

直觉上模型转换就是"每个算子查表映射"。但 tf2onnx 揭示了一个关键洞察：**大部分复杂度不在单算子映射，而在复合算子识别和子图替换**。

| 阶段 | 处理对象 | 核心操作 | 是否感知 TF 语义 |
|------|----------|----------|-----------------|
| **Rewriter** | 子图（多个节点组成的模式） | 模式匹配 + 子图替换 | ✅ 是（识别 TF 特定算子组合） |
| **Mapper** | 单个节点 | 1:1 或 1:N 算子映射 | ✅ 是（TF op → ONNX op） |
| **Optimizer** | ONNX 图 | 通用图变换 | ❌ 否（纯 ONNX 图优化，可独立复用） |

**阶段顺序不可调换**：
- Rewriter 必须在 Mapper 之前：Mapper 只处理单节点映射，无法识别子图模式（如 FusedBatchNorm 在 ONNX 中是多个算子的组合）
- Optimizer 必须在 Mapper 之后：优化器操作的是纯 ONNX 图，不能有 TF 类型名的节点残留

### 包结构与懒加载机制

tf2onnx 使用 PEP 562 `__getattr__` 实现子模块懒加载，避免 `python -m tf2onnx.convert` 启动时的 RuntimeWarning：

```python
# tf2onnx/__init__.py
__getattr__ = _make_lazy_getattr({
    "utils": "tf2onnx.utils",
    "graph_matcher": "tf2onnx.graph_matcher",
    "graph": "tf2onnx.graph",
    "graph_builder": "tf2onnx.graph_builder",
    "tfonnx": "tf2onnx.tfonnx",
    "shape_inference": "tf2onnx.shape_inference",
    "schemas": "tf2onnx.schemas",
    "tf_utils": "tf2onnx.tf_utils",
    "tf_loader": "tf2onnx.tf_loader",
    "convert": "tf2onnx.convert",
})
```

但算子注册模块是**立即导入**的（非懒加载），因为 `@tf_op` 装饰器需要在转换前完成注册：

```python
# tf2onnx/tfonnx.py
# 立即导入以触发算子注册
from tf2onnx.onnx_opset import custom_opsets, onnx_opset, tflite_handlers
from tf2onnx import rewriter  # 通配符导入所有重写函数
```

## 关键设计决策

### 决策一：ONNX Protobuf 作为 IR（洞察三）

tf2onnx 选择将目标格式（ONNX Protobuf）直接作为内部 IR，而非设计自定义 IR：

- **第一步就是 1:1 转换**：`tflist_to_onnx` 将 TF NodeDef 直接转为 ONNX NodeProto，类型名暂时保持 TF 原名
- **逐步修正**：后续阶段逐步将"伪 ONNX 节点"修正为真正的 ONNX 算子
- **零序列化开销**：转换完成时 Graph 对象已经持有完整的 ONNX 图结构，`make_model()` 只是设置元数据
- **可调试性**：任何时刻都可以将当前图序列化为 ONNX 模型进行检查

**代价**：映射阶段图中混合 TF 类型名和 ONNX 类型名的节点，需要 `skip_conversion` 标记区分。

### 决策二：装饰器注册而非条件分支（洞察一）

多 opset 版本兼容不是通过 `if opset >= N` 条件判断实现的，而是通过注册表版本堆叠：

- 每个算子版本处理器独立声明（`version_6`、`version_13`）
- `create_mapping` 在运行时一次性构建版本映射表
- 新增 opset 支持是纯增量操作（添加 `version_18` 方法），不修改现有代码

### 决策三：优化器与映射解耦

ONNX 图优化器完全不知道图来自 TF，它只操作 ONNX 图。这意味着：
- 优化器可以独立于 tf2onnx 使用（onnxruntime 也有类似优化器）
- 新增 TF 算子不影响优化逻辑
- 优化器可以被其他 ONNX 转换工具复用

## 支持范围

| 特性 | 支持范围 |
|------|----------|
| 源格式 | TensorFlow 2.x (Keras/SavedModel/GraphDef/ConcreteFunction)、TFLite、TF.js（实验性） |
| ONNX opset | opset 14-18（官方测试），opset 6-13（理论可用），默认 opset 15 |
| Python | 3.10-3.12 |
| TensorFlow | 2.13+ |
| Target 平台 | rs4/rs5/rs6 (Windows ML)、caffe2、tensorrt、nhwc (channels last) |

## 关联概念

- [转换流水线详解：Loader→Rewriter→Mapper→Optimizer](01-conversion-pipeline.md) — 深入每个阶段的执行细节
- [装饰器驱动的版本化算子注册表](02-versioned-opset-registry.md) — 理解 @tf_op 注册机制
- [图重写与模式匹配](03-graph-rewriting.md) — 理解 Rewriter 阶段的模式匹配
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解 Node/Graph 类的图操作能力
- [ONNX 图优化器](05-optimizers.md) — 理解 Optimizer 阶段的 12 个优化器
- [数据布局、类型系统与 Target 适配](06-data-layout-types.md) — 理解 NHWC/NCHW 转换与类型映射
