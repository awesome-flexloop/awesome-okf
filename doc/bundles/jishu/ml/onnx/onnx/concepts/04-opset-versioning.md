---
type: concept
title: "Opset版本机制与算子域"
description: "IR_VERSION 演进、VERSION_TABLE 表驱动版本映射、四个算子域（标准/ML/训练/预览）、NormalizeDomain 规范化、find_min_ir_version_for 查表"
sources:
  references: [../references/onnx-proto.md, ../references/helper-api.md, ../references/op-schema.md]
  facts: [F-020, F-023, F-024, F-031, F-048, F-072, F-078, F-079, F-080]
---

# Opset版本机制与算子域

## 核心理解

ONNX 的版本管理是一个**表驱动的兼容映射系统**，而非简单的版本号递增。理解 IR 版本（IR_VERSION）与算子集版本（opset version）的关系、四个算子域的划分、以及 VERSION_TABLE 的作用，是正确创建和转换模型的关键。手动设置 ir_version 而不匹配 opset 版本是常见错误。

## 机制详解

### 三层版本概念

ONNX 有三个独立但相关的版本维度：

```
ONNX 生态版本
├── ONNX Release Version (如 1.16.0, 1.23.0)
│   └── Python 包版本，对应一组工具和默认版本
│
├── IR_VERSION (如 8, 9, 10, ..., 14)
│   └── Protobuf IR 规范版本，决定 proto 字段和语义
│       └── 存储在 ModelProto.ir_version (字段1)
│
└── Opset Version (如 ai.onnx v21, ai.onnx.ml v4)
    └── 每个算子域的算子集版本
        └── 存储在 ModelProto.opset_import[] (字段8)
            └── OperatorSetIdProto: {domain, version}
```

关键关系：**IR_VERSION 和 Opset Version 不是独立的**——每个 IR 版本对各域 opset 版本有最低要求。

### VERSION_TABLE：版本映射表

VERSION_TABLE（F-031）维护了从 ONNX 1.0 到最新版本的完整映射，每行格式为：

```python
# VERSION_TABLE 条目示例
(
    release_version,   # ONNX 发布版本（如 "1.23.0"）
    ir_version,        # 对应的 IR 版本（如 14）
    ai_onnx_version,   # 标准域 opset 版本（如 25）
    ai_onnx_ml_version, # ML域 opset 版本（如 5）
    ai_onnx_training_version, # 训练域 opset 版本（如 1）
)
```

关键版本映射：

| Release | IR | ai.onnx | ai.onnx.ml | ai.onnx.training |
|---------|-----|---------|------------|-----------------|
| 1.0 | 3 | 1 | 1 | - |
| 1.3 | 3 | 8 | 1 | - |
| 1.6 | 6 | 11 | 2 | - |
| 1.8 | 7 | 13 | 2 | - |
| 1.10 | 8 | 15 | 2 | 1 |
| 1.12 | 8 | 17 | 3 | 1 |
| 1.14 | 9 | 19 | 4 | 1 |
| 1.16 | 10 | 21 | 4 | 1 |
| 1.20 | 12 | 23 | 5 | 1 |
| 1.23.0 | 14 | 25 | 5 | 1 |

### 四个算子域

ONNX 定义了四个算子域（F-048, F-078）：

| 域常量 | 域字符串 | NormalizeDomain | 说明 |
|--------|---------|-----------------|------|
| ONNX_DOMAIN | `""` (空字符串) | `""` | **标准算子域**：神经网络核心算子（Conv, MatMul, Add, Relu...） |
| AI_ONNX_DOMAIN | `"ai.onnx"` | `""` | 标准域的别名，等价于 `""` |
| AI_ONNX_ML_DOMAIN | `"ai.onnx.ml"` | `"ai.onnx.ml"` | **ML域**：传统机器学习算子（TreeEnsemble, SVM, OneHotEncoder...） |
| AI_ONNX_TRAINING_DOMAIN | `"ai.onnx.training"` | `"ai.onnx.training"` | **训练域**：训练相关算子（Gradient, Adam...） |
| AI_ONNX_PREVIEW_DOMAIN | `"ai.onnx.preview"` | `"ai.onnx.preview"` | **预览域**：实验性算子，API可能变更 |

**NormalizeDomain 规范化**（F-079）：
- 将 `"ai.onnx"` 转换为 `""`（空字符串）
- `IsOnnxDomain()` 检查域是否为 `""` 或 `"ai.onnx"`（两者等价）
- Protobuf 存储和注册表查找统一使用空字符串
- 模型中 `opset_import` 的 domain 字段为空字符串或缺失时，表示标准域

### make_model 与 make_model_gen_version 的版本策略

两个构造函数对版本的处理方式不同（F-023, F-024）：

```python
# make_model：总是使用最新版本
model = onnx.helper.make_model(graph)
# → ir_version = onnx.IR_VERSION（当前最新，即14）
# → opset_imports = [{"": onnx.defs.onnx_opset_version()}]（最新标准opset）

# make_model_gen_version：根据opset自动计算IR版本
model = onnx.helper.make_model_gen_version(
    graph,
    opset_imports=[onnx.helper.make_operatorsetid("", 11)]
)
# → ir_version = find_min_ir_version_for(opset_imports) = 6（对应onnx 1.6）
```

### find_min_ir_version_for：查表计算最小 IR 版本

```python
def find_min_ir_version_for(opset_imports: list[OperatorSetIdProto]) -> int:
```

算法（F-072）：
1. 从 OP_SET_ID_VERSION_MAP（VERSION_TABLE 派生）中查找每个域的 opset 版本对应的 IR 版本
2. 取各域所需 IR 版本的**最大值**
3. 确保 opset 版本在 VERSION_TABLE 中有记录

这意味着如果模型同时使用标准域 opset 15（需要 IR 8）和训练域 opset 1（需要 IR 8），最终 IR 版本为 8。

### Checker 中的版本校验

check_model 执行以下版本校验（F-033）：
1. `ir_version` 必须设置且 ≤ 当前 IR_VERSION
2. IR >= 3 时必须指定 opset_import
3. IR < 3 时**不能**有 opset_import（此时默认 opset 域版本为 1）
4. 每个节点的 op_type 在对应域的 opset 版本中必须存在

### OperatorStatus：算子稳定状态

```python
EXPERIMENTAL = 0  # 实验性算子，API可能变更
STABLE = 1        # 稳定算子
```

### 版本转换

当需要在不同 opset 版本间转换模型时，使用 version_converter：

```python
model = onnx.version_converter.convert_version(model, target_version=15)
```

convert_version（F-071）通过 C++ 实现的 adapter 机制将旧版本算子转换为新版本的等价表示。

## 版本关系图

```
                    ONNX Release 1.23.0
                         │
            ┌────────────┼────────────┐
            ↓            ↓            ↓
      IR_VERSION=14  ai.onnx=25  ai.onnx.ml=5
            │            │
            │    ┌───────┴───────┐
            ↓    ↓               ↓
    Protobuf     OpSchema     OpSchema
    fields      (v25)         ML(v5)
    available    │              │
    (all 14      ↓              ↓
     versions)  Registry:  Registry:
               (domain="",  (domain="ai.onnx.ml",
                op_type,     op_type,
                version=25)  version=5)

Checker 验证：
  model.ir_version ≤ IR_VERSION(14)  ✅
  opset_import[i].version 在注册表中存在 ✅
  节点引用的 op_type 在对应 (domain, version) 中存在 ✅
```

## 关键洞察/反常识

1. **ir_version 和 opset_version 绑定**：这是最常见的错误来源——手动设置 ir_version=8 但 opset 版本为 21 会导致 check_model 失败，因为 opset 21 需要 IR 10。正确做法是让 make_model 自动设置，或使用 make_model_gen_version 查表。
2. **"ai.onnx" 和 "" 是同一个域**：两者完全等价，NormalizeDomain 统一为空字符串。不要在模型中混用两种表示。
3. **版本转换不是万能的**：convert_version 只处理标准域算子的版本适配，不保证所有算子都能跨版本转换。自定义算子和 ML 域算子的转换可能需要手动处理。
4. **make_model 总是使用最新版本**：这意味着用最新 onnx 包创建的模型可能无法在旧版推理引擎上运行。需要兼容性时，使用 make_model_gen_version 指定较低的 opset 版本。
5. **多域模型需要所有域的 opset_import**：如果模型使用了标准域和ML域的算子，opset_import 必须包含两个域的条目，缺一不可。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — OperatorSetIdProto 和 IR_VERSION 的 proto 定义
- [算子定义与注册机制 OpSchema](05-operator-schema.md) — 算子如何注册到特定域和版本
- [模型检查器 Checker](07-model-checker.md) — 版本验证规则的详细说明
- [Python Helper API 详解](09-python-helpers.md) — make_model/make_model_gen_version/find_min_ir_version_for 用法
- [版本转换与函数内联](13-version-converter-inliner.md) — convert_version 和函数内联的详细机制
