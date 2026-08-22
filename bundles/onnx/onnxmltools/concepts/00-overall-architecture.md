---
type: concept
title: "onnxmltools 整体架构：9入口6自有IR+3委托的非对称转换工具"
description: "onnxmltools 的整体架构：9个转换入口中6个走自有Topology IR流水线、3个委托外部转换器的非对称设计，ONNX-ML传统ML算子集是IR实际能力边界"
sources:
  references: [../references/convert-entry.md, ../references/topology-ir.md, ../references/registration-types.md]
  facts: [F-002, F-006, F-007, F-008, F-009, F-015, F-019, F-023, F-030, F-031]
---

# onnxmltools 整体架构：9入口6自有IR+3委托的非对称转换工具

## 核心理解

onnxmltools 不是一个"所有框架共享统一内核"的转换器，而是一个**非对称架构**的转换工具集合：顶层导出9个 `convert_xxx` 函数，但实际有3条不同的转换路径：

1. **自有 Topology IR 路径（6个框架）**：CoreML、LightGBM、XGBoost、H2O、LibSVM、SparkML 先被解析为统一的 Topology 中间表示，经过编译优化后统一生成 ONNX ModelProto。
2. **委托路径（3个框架）**：sklearn 委托给 skl2onnx、Keras/TF 委托给 tf2onnx、CatBoost 直接调用内置导出——这些路径完全绕过 onnxmltools 的 IR。

```
┌──────────────────────────────────────────────────────────────────┐
│                    onnxmltools 顶层入口 (9个convert_xxx)          │
│  convert_coreml convert_lightgbm convert_xgboost convert_h2o ... │
│  convert_sklearn convert_keras convert_tensorflow convert_catboost│
└─────────┬───────────────────────────┬────────────────────────────┘
          │                           │
          │ 自有IR路径(6个)            │ 委托路径(3个)
          ▼                           ▼
┌─────────────────────┐    ┌──────────────────────────────┐
│  Parse（各框架解析器）│    │ sklearn → skl2onnx.convert   │
│  _parse.py          │    │ keras/TF → tf2onnx.convert   │
│  → Topology IR      │    │ catboost → model内置导出     │
└─────────┬───────────┘    └──────────────────────────────┘
          │
┌─────────▼───────────┐
│  Compile（五阶段）    │
│  _prune →           │
│  _resolve_duplicates│
│  → _fix_shapes →    │
│  _infer_all_types → │
│  _check_structure   │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Convert Topology   │
│  拓扑遍历+双池分发   │
│  → ModelComponent-  │
│    Container        │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  make_model_ex      │
│  opset合并+IR版本   │
│  映射+元数据填充    │
│  → ONNX ModelProto  │
└─────────────────────┘
```

## "多前端、一中端、一后端"的编译器架构（但实际有例外）

从自有 IR 路径看，onnxmltools 采用经典编译器架构：

- **前端（Parse）**：各框架的 `_parse.py` 将原始模型对象翻译为由 `Topology`/`Scope`/`Operator`/`Variable` 组成的通用 IR。
- **中端（Compile）**：`Topology.compile()` 执行五阶段优化——剪枝、identity消重、形状补全、类型推断、结构校验。
- **后端（Convert）**：`convert_topology()` 通过注册表分发 converter 函数，收集 ONNX 节点，最终组装 ModelProto。

但三个委托路径打破了这个统一架构：

| 入口 | 实际转换器 | 为什么不走自有IR |
|------|-----------|----------------|
| convert_sklearn | skl2onnx | sklearn 模型种类太多（100+估计器），skl2onnx 有更完善的转换器生态和代数API |
| convert_keras/tensorflow | tf2onnx | TensorFlow 算子语义远超 ONNX-ML 传统 ML 算子集，tf2onnx 是专门的图级转换器 |
| convert_catboost | CatBoost内置 | CatBoost 自己实现了 ONNX 导出，onnxmltools 仅做参数适配 |

## ONNX-ML 算子集是IR的实际能力边界

真正"走通"自有 IR 流水线的6个框架有一个共同特点：**它们的算子都落在 ONNX-ML 传统 ML 算子集内**：

- **LightGBM/XGBoost/H2O/LibSVM**：本质上都是树模型和线性模型，映射到 `TreeEnsembleClassifier`/`TreeEnsembleRegressor`/`LinearClassifier`/`LinearRegressor`
- **CoreML**：传统 ML 部分（GLM/SVM/Scaler/OneHotEncoder/TreeEnsemble等）与 ONNX-ML 高度对齐，是 IR 覆盖最全面的前端（15个顶层算子+40+神经网络层算子）
- **SparkML**：Pipeline 中的特征工程和分类/回归算子映射到 ONNX-ML

神经网络层算子（Conv/LSTM/BatchNormalization等）虽然 CoreML 的 neural_network 子包也做了支持，但这部分能力与深度学习专用转换器（tf2onnx/torch.onnx）相比非常有限。

这揭示了一个架构现实：**onnxmltools 的核心价值在于 ONNX-ML 传统机器学习模型的转换**，特别是 GBDT 树模型和广义线性模型。深度学习模型应该使用框架专用的转换器。

## RawModelContainer 多态封装

不同框架的模型对象差异巨大，onnxmltools 通过 `RawModelContainer` 多态基类统一封装：

```python
class RawModelContainer:
    """抽象基类"""
    @property
    def input_names(self): ...
    @property
    def output_names(self): ...

class LightGbmModelContainer(RawModelContainer):
    """封装 LightGBM Booster/LGBMClassifier 等"""
class XGBoostModelContainer(RawModelContainer):
    """封装 XGBoost Booster/XGBClassifier 等"""
class CoremlModelContainer(RawModelContainer):
    """封装 CoreML spec protobuf"""
```

LightGBM 和 XGBoost 的原生 `Booster` 对象在传入时会被自动包装为 `WrappedBooster` 类以适配容器接口。

## 设计洞察

1. **门面聚合而非统一内核**：onnxmltools 顶层是一个 facade，将多个独立转换器聚合在统一 API 后面，降低用户学习成本。
2. **IR 面向 ONNX-ML 而非全 ONNX**：Topology IR 的 Variable/Operator/Scope 设计面向传统 ML 算子（树模型、GLM、特征工程），不追求覆盖深度学习算子。
3. **树模型共享模板是IR统一的关键**：LightGBM/XGBoost/H2O 共享 `tree_ensemble.py` 的属性对模板，在 IR 层面映射到相同的 TreeEnsemble 算子，这是多框架统一的基础。
4. **委托是务实的工程决策**：sklearn→skl2onnx、TF/Keras→tf2onnx 的委托避免了重复造轮子，也承认了不同转换器生态的边界。

## 关键参数说明

所有自有IR路径的转换器共享核心参数：

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | 是 | 框架原生模型对象 |
| `initial_types` | LightGBM/XGBoost/LibSVM必填 | 输入变量声明，如 `[("input", FloatTensorType([None, 4]))]` |
| `target_opset` | 否 | 默认15，自动取 `min(15, onnx_opset_version())` |
| `name` | 否 | 默认 uuid4 生成唯一名称 |
| `custom_conversion_functions` | 否 | 自定义算子覆盖，优先级高于注册表 |
| `custom_shape_calculators` | 否 | 自定义形状计算器，须与converter配对 |

## 关联概念

- [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](01-topology-ir.md) — 深入理解IR的核心数据结构
- [编译流水线五阶段：createTopology→compile→convert_topology→make_model](02-conversion-pipeline.md) — 了解完整的编译流程
- [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 了解算子注册和查找机制
- [数据类型系统：四层DataType、TensorType维度规格、三向类型猜测](04-type-system.md) — 了解类型体系
- [树模型转换范式：LightGBM/XGBoost/CoreML算子集与属性模板](05-tree-models.md) — 了解树模型转换的共性
