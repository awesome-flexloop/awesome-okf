---
type: reference
title: "9个转换入口与延迟导入机制"
description: "onnxmltools 顶层 __init__.py 导出的9个 convert_xxx 入口函数签名、统一参数模式、延迟导入依赖检查、委托路径与源码信源登记"
sources:
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/__init__.py"
    facts: [F-001, F-002]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/main.py"
    facts: [F-003, F-004, F-005, F-006, F-007, F-008, F-009]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/utils.py"
    facts: [F-005]
---

# 9个转换入口与延迟导入机制

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnxmltools/__init__.py` | 包入口 | 版本元信息、顶层 API 导出（9个 convert_xxx + load/save_model） |
| `onnxmltools/convert/main.py` | 核心调度模块 | 9个 convert_xxx 函数实现、延迟导入、依赖检查、委托分发 |
| `onnxmltools/convert/common/utils.py` | 工具模块 | `xxx_installed()` 依赖检查函数族 |

## 版本与生产者元信息（F-001）

**信源**：`onnxmltools/__init__.py` L9-L14

```python
__version__ = "1.17.0"
__producer__ = "OnnxMLTools"
__domain__ = "onnxml"
__model_version__ = 0
```

- `__producer__ = "OnnxMLTools"` 写入 ONNX ModelProto 的 `producer_name` 字段。
- `__domain__ = "onnxml"` 作为默认域标识。
- 包版本 1.17.0，模型版本初始为 0。

## 顶层导出的9个转换器入口（F-002）

**信源**：`onnxmltools/__init__.py` L16-L26

顶层 `__init__.py` 导出9个框架转换函数和2个模型I/O工具函数：

| 函数 | 目标框架 | 转换路径 |
|------|----------|----------|
| `convert_coreml` | CoreML | 自有 Topology IR |
| `convert_keras` | Keras/TF | TF<2.0→keras2onnx; TF≥2.0→tf2onnx |
| `convert_lightgbm` | LightGBM | 自有 Topology IR（树模型） |
| `convert_sklearn` | scikit-learn | **完全委托给 skl2onnx** |
| `convert_sparkml` | Spark MLlib | 自有 Topology IR |
| `convert_tensorflow` | TensorFlow | tf2onnx 图级转换 |
| `convert_xgboost` | XGBoost | 自有 Topology IR（树模型） |
| `convert_h2o` | H2O MOJO | 自有 Topology IR（GBM树模型） |
| `convert_catboost` | CatBoost | **直接调用 CatBoost 内置导出** |
| `load_model` / `save_model` | I/O工具 | Protobuf 二进制序列化 |

## 统一参数签名模式（F-003）

**信源**：`onnxmltools/convert/main.py` L9-L18, L204-L216

除 `convert_catboost` 和 `convert_tensorflow` 外，所有转换器共享统一参数签名：

```python
def convert_xxx(
    model,
    name=None,
    initial_types=None,
    doc_string="",
    target_opset=None,
    targeted_onnx=None,
    custom_conversion_functions=None,
    custom_shape_calculators=None,
):
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | 框架模型对象 | 待转换的原始模型 |
| `name` | str | ONNX 图名称，默认 uuid4 生成 |
| `initial_types` | `List[Tuple[str, DataType]]` | 输入变量类型声明（树模型必填） |
| `doc_string` | str | 模型文档字符串 |
| `target_opset` | int | 目标 ONNX opset 版本，默认 `min(15, onnx_opset_version())` |
| `targeted_onnx` | 旧版对象 | **已废弃**，触发 DeprecationWarning |
| `custom_conversion_functions` | dict | 用户自定义转换器覆盖 |
| `custom_shape_calculators` | dict | 用户自定义形状计算器覆盖 |

### targeted_onnx 废弃警告（F-004）

**信源**：`onnxmltools/convert/main.py` L19-L22, L217-L220

所有转换器在 `targeted_onnx is not None` 时发出 `DeprecationWarning`：

```python
warnings.warn(
    "targeted_onnx is deprecated. Please use 'target_opset' instead.",
    DeprecationWarning,
)
```

## 延迟导入与依赖检查模式（F-005）

**信源**：`onnxmltools/convert/main.py` L23-L28; `onnxmltools/convert/common/utils.py` L6-L175

每个转换器入口遵循"先检查再导入"的两阶段模式：

```python
def convert_lightgbm(model, ...):
    # 阶段1：运行时依赖检查
    if not utils.lightgbm_installed():
        raise RuntimeError("lightgbm is not installed.")
    # 阶段2：延迟导入转换实现
    from .lightgbm.convert import convert
    return convert(model, name=name, initial_types=initial_types, ...)
```

这种设计确保：
1. **按需安装**：不安装某框架不影响其他框架的转换功能
2. **快速失败**：缺少依赖时立即给出明确错误信息
3. **避免循环导入**：子模块只在需要时加载

`utils.py` 为每个框架提供 `xxx_installed()` 函数，内部使用 try-import 模式检查：

```python
def lightgbm_installed():
    try:
        import lightgbm  # noqa
        return True
    except ImportError:
        return False
```

## 六条转换路径详解

### 路径1：convert_sklearn — 完全委托 skl2onnx（F-006）

**信源**：`onnxmltools/convert/main.py` L243-L277

`convert_sklearn` 不使用 onnxmltools 自有 Topology IR，而是直接委托：

```python
def convert_sklearn(model, ...):
    if not utils.sklearn_installed():
        raise RuntimeError("scikit-learn not installed.")
    if not utils.skl2onnx_installed():
        raise RuntimeError("skl2onnx is not installed.")
    from skl2onnx.convert import convert_sklearn as _convert_sklearn
    return _convert_sklearn(model, name=name, initial_types=initial_types, ...)
```

onnxmltools 在此路径中仅是一个 facade/门面，skl2onnx 才是真正实现者。

### 路径2：convert_keras — TF版本双路分发（F-007）

**信源**：`onnxmltools/convert/main.py` L42-L149

```python
def convert_keras(model, ...):
    if tf_version < (2, 0):
        # 旧路径：keras2onnx
        from keras2onnx import convert_keras as _convert
        return _convert(model, ...)
    else:
        # 新路径：tf2onnx
        from tf2onnx.convert import from_keras
        # 将 initial_types 映射为 tf.TensorSpec
        # 废弃 custom_conversion_functions/custom_shape_calculators/default_batch_size
        return from_keras(model, input_signature=specs, ...)
```

TF≥2.0 路径中，Float/Double/Int64/Int32/String/BooleanTensorType 被映射为对应的 `tf.TensorSpec(shape, dtype)`。

### 路径3：convert_catboost — 内置导出转发（F-008）

**信源**：`onnxmltools/convert/main.py` L185-L201

`convert_catboost` 是唯一不经过 Topology IR 也不走 tf2onnx 的原生转换器：

```python
def convert_catboost(model, ...):
    if not utils.catboost_installed():
        raise RuntimeError("catboost is not installed.")
    export_params = {
        "onnx_doc_string": doc_string,
        "onnx_graph_name": name or "catboost",
    }
    return model.convert_to_onnx_object(
        initial_types=initial_types,
        target_opset=target_opset,
        export_parameters=export_params,
    )
```

它直接调用 CatBoost 模型对象的 `convert_to_onnx_object` 方法，onnxmltools 仅做参数适配。

### 路径4：convert_tensorflow — tf2onnx图级转换（F-009）

**信源**：`onnxmltools/convert/main.py` L363-L454

```python
def convert_tensorflow(frozen_graph_def, ...):
    # 经 _convert_tf_wrapper 调用 tf2onnx 流水线：
    # 1. tfonnx.process_tf_graph() 处理冻结图
    # 2. optimize_graph() 图优化
    # 3. make_model() 生成 ModelProto
```

支持参数：`input_names`、`output_names`、`debug_mode`、`custom_op_conversions` 等，完全走 tf2onnx 内部流水线。

### 路径5：自有IR路径 — CoreML/LightGBM/XGBoost/H2O/LibSVM/SparkML

这六个框架遵循统一的"Parse→Compile→Convert"流水线：
1. `parse_xxx()` 将原始模型解析为 Topology IR
2. `topology.compile()` 执行五阶段优化
3. `convert_topology()` 生成 ONNX ModelProto

详见 [转换流水线](../concepts/02-conversion-pipeline.md) 概念文档。

### 路径6：模型I/O工具（F-037）

`load_model`/`save_model` 基于 Protobuf 二进制序列化：
- `save_model(model, path)` → 校验 ModelProto → `SerializeToString()` → 写文件
- `load_model(path)` → 读文件 → `ModelProto.ParseFromString()` → 返回 ModelProto
- 辅助函数：`set_model_domain`、`set_model_version`、`set_model_doc_string`
