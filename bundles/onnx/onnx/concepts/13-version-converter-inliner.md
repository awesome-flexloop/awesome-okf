---
type: concept
title: "版本转换与函数内联"
description: "convert_version 跨版本转换、inline_local_functions 递归内联、inline_selected_functions 选择性内联、FunctionProto 与模型局部函数的关系"
sources:
  references: [../references/compose-parser-printer.md, ../references/op-schema.md, ../references/onnx-proto.md]
  facts: [F-071, F-076, F-077, F-016, F-017, F-051]
---

# 版本转换与函数内联

## 核心理解

ONNX 提供两个重要的模型变换工具：**版本转换器**（version_converter）和**函数内联器**（inliner）。版本转换器将模型从一个 opset 版本转换到另一个版本，解决不同推理引擎支持不同 opset 版本的兼容性问题。函数内联器将模型中的函数调用展开为内联的基础算子节点，简化推理引擎的实现负担。两者都在 C++ 层实现核心逻辑，Python 端提供薄层封装。

## 机制详解

### 版本转换器 convert_version

```python
from onnx import version_converter

converted_model = version_converter.convert_version(
    model: ModelProto,
    target_version: int,
) -> ModelProto
```

**工作方式**（F-071）：
1. 将 ModelProto 序列化为字节串
2. 委托给 C++ 实现：`onnx_cpp2py_export.version_converter.convert_version`
3. C++ 端执行算子版本适配（adapter）
4. 返回新的 ModelProto

#### 版本适配原理

同一算子的不同 opset 版本在 OpSchema 注册表中是独立条目（F-049）。版本转换器的工作是：
1. 对于每个节点，查找源版本和目标版本的 OpSchema 差异
2. 如果有 adapter 规则，将旧版本算子转换为新版本等价形式
3. 可能需要插入额外的节点来表达语义差异

```
版本转换示意（opset 10 → opset 14）：

源模型 (opset 10):
  Node: Clip(data, min, max)  ← Clip-v10 只有 data 输入，min/max 通过属性
       │
       ↓ convert_version(target=14)
       │
转换后 (opset 14):
  Node: Clip(data, min_const, max_const)  ← Clip-v14 min/max 为输入
  + Constant 节点提供 min/max 值
```

典型版本差异：
- Clip：属性 → 输入（v10→v11）
- BatchNormalization：spatial 属性移除
- Resize：coordinate_transformation_mode 等属性语义变更
- TopK：k 从属性变为输入

**限制**：
- 版本转换主要支持**标准域**（ai.onnx）算子
- 并非所有版本对都有双向 adapter
- 自定义算子和 ML 域算子可能需要手动处理
- 转换后建议用 `check_model(full_check=True)` 验证

### 函数内联 inline_local_functions

```python
from onnx import inliner

inlined_model = inliner.inline_local_functions(
    model: ModelProto,
    convert_version: bool = True,
) -> ModelProto
```

**功能**（F-076）：将模型中所有对**模型局部函数**（model.functions 中的 FunctionProto）的调用递归内联展开。

#### 什么是函数？

ONNX 中有两种"函数"概念：

1. **OpSchema 函数体**（F-051）：在算子注册时通过 `FunctionBody()` 定义，是标准算子的内置展开规则。例如 Selu 算子可以定义为 `Elu → Scale → Shift` 的组合。这些函数体在所有使用该 opset 版本的模型中隐式可用。

2. **模型局部函数**（F-007, F-016）：在 ModelProto.functions 字段中定义，是模型自带的自定义函数。允许模型定义自定义算子为基础算子的组合。

```
模型使用局部函数的结构：

ModelProto
├── opset_import: ["" : 17]
├── graph:
│   └── node: MyCustomOp(X, Y) → Z
│       (domain="", op_type="MyCustomOp")  ← 调用局部函数
└── functions:
    └── FunctionProto(name="MyCustomOp", domain="")
        ├── input: ["X", "Y"]
        ├── output: ["Z"]
        └── node: [
            Add(X, Y) → tmp,
            Relu(tmp) → Z
          ]
```

#### 内联过程

`inline_local_functions` 的工作流程：
1. 遍历图中所有节点
2. 对于引用模型局部函数的节点，找到对应的 FunctionProto
3. 将函数体的节点列表插入图中，替换函数调用节点
4. 正确处理属性绑定（函数的 attribute 参数 → 调用节点的属性值）
5. 递归处理：内联后新产生的函数调用也会被内联
6. `convert_version=True` 时在必要处执行版本转换以确保兼容

```
内联前:
  graph.node: [MyCustomOp(X, Y) → Z]
  model.functions: [MyCustomOp: [Add(X,Y)→tmp, Relu(tmp)→Z]]

内联后:
  graph.node: [
    Add(X, Y) → tmp_MyCustomOp,  ← 名字可能添加后缀避免冲突
    Relu(tmp_MyCustomOp) → Z
  ]
  model.functions: []  (或保留但不再被引用)
```

### 选择性内联 inline_selected_functions

```python
from onnx import inliner

result_model = inliner.inline_selected_functions(
    model: ModelProto,
    function_ids: Optional[List[Tuple[str, str, str]]] = None,
    exclude: bool = False,
    inline_schema_functions: bool = False,
) -> ModelProto
```

**参数**（F-077）：
- `function_ids`：`(domain, name, overload)` 三元组列表，指定目标函数
- `exclude=False`（默认）：仅内联列表中指定的函数（白名单模式）
- `exclude=True`：内联列表**外**的所有函数（黑名单模式）
- `inline_schema_functions`：是否同时内联 OpSchema 注册的函数体（如 Selu、SoftmaxV11 等）

```python
# 示例1：只内联特定函数
model = inliner.inline_selected_functions(
    model,
    function_ids=[("", "MyCustomOp", "")],
    exclude=False,
)

# 示例2：内联除了指定函数外的所有函数
model = inliner.inliner.inline_selected_functions(
    model,
    function_ids=[("", "KeepThisFunction", "")],
    exclude=True,
)

# 示例3：同时内联 schema 定义的函数（如 Selu、Softmax）
model = inliner.inline_local_functions(model)
# inline_local_functions 默认不内联 schema functions
# 要内联 schema functions:
model = inliner.inline_selected_functions(
    model,
    function_ids=[],
    exclude=True,                # 内联所有局部函数
    inline_schema_functions=True # 也内联 schema 函数
)
```

### 函数调用循环检测

Checker 在验证模型时检测函数调用循环（F-038）：

```
非法的循环调用：
  A 调用 B，B 调用 A ──→ 内联会无限递归
  A 调用 B，B 调用 C，C 调用 A ──→ 间接循环
```

check_model 会检测并拒绝此类模型，防止内联器无限递归。

### 典型使用场景

```python
import onnx
from onnx import version_converter, inliner, checker, shape_inference

# 场景1：将模型降级到旧版本兼容旧推理引擎
model = onnx.load("new_model.onnx")  # opset 17
old_model = version_converter.convert_version(model, target_version=11)
checker.check_model(old_model, full_check=True)
onnx.save(old_model, "model_opset11.onnx")

# 场景2：内联所有局部函数，简化推理引擎实现
model = onnx.load("model_with_functions.onnx")
inlined = inliner.inline_local_functions(model)
checker.check_model(inlined, full_check=True)
onnx.save(inlined, "model_inlined.onnx")

# 场景3：完整预处理管线（加载→版本转换→内联→验证→推断）
model = onnx.load("model.onnx")
model = version_converter.convert_version(model, target_version=15)
model = inliner.inline_local_functions(model)
model = shape_inference.infer_shapes(model, check_type=True, strict_mode=True)
checker.check_model(model, full_check=True)
onnx.save(model, "model_ready.onnx")
```

## 关键洞察/反常识

1. **版本转换可能改变图结构**：convert_version 不只是改版本号——它可能插入额外的 Constant 节点、重连输入输出、替换算子类型。转换后的图可能与原图结构不同，但语义等价。
2. **内联不是必须的**：推理引擎可以选择直接支持函数调用（保留 functions 字段），也可以要求内联后的模型。ONNX Runtime 等主流引擎通常支持函数调用，但某些轻量级引擎可能需要预内联。
3. **inline_local_functions 只处理模型局部函数**：OpSchema 定义的标准函数体（如 MeanVarianceNormalization 的展开）默认不被内联。需要使用 `inline_selected_functions` 并设置 `inline_schema_functions=True`。
4. **递归内联可能导致图膨胀**：多层函数嵌套内联后，节点数可能大幅增加。这是内联的固有代价。
5. **函数 ≠ 子图**：FunctionProto 的 body（node 列表）和子图属性（GRAPH 类型的 attribute）是不同的概念。函数是"宏展开"式的替换，子图是运行时条件/循环执行的图体。内联处理函数但不处理子图。

## 关联概念

- [Opset版本机制与算子域](04-opset-versioning.md) — IR_VERSION 和 opset 版本的关系
- [算子定义与注册机制 OpSchema](05-operator-schema.md) — FunctionBody 函数体机制
- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — FunctionProto 的字段定义
- [模型检查器 Checker](07-model-checker.md) — 函数调用循环检测
