---
type: reference
title: "convert_sklearn / to_onnx：转换入口 API"
description: "sklearn-onnx 的两个核心转换入口函数 convert_sklearn 和 to_onnx 的签名、参数、主流程与源码信源登记"
sources:
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/convert.py"
    facts: [F-002, F-003, F-004, F-005, F-027]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/__init__.py"
    facts: [F-001, F-002, F-005]
---

# convert_sklearn / to_onnx：转换入口 API

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `skl2onnx/__init__.py` | 包入口 | 版本元信息、顶层 API 导出、`supported_converters()` 触发注册 |
| `skl2onnx/convert.py` | 核心转换模块 | `convert_sklearn()`、`to_onnx()`、`wrap_as_onnx_mixin()` 实现；副作用导入触发 shape_calculator 和 converter 注册 |

## 版本与元信息（F-001）

**信源**：`skl2onnx/__init__.py`

```python
__version__ = "1.21.0"
__producer__ = "skl2onnx"
__domain__ = "ai.onnx"
__max_supported_opset__ = 25
```

- 生产者标识为 `"skl2onnx"`，写入 ONNX ModelProto 的 `producer_name` 字段。
- 默认域为 `"ai.onnx"`（主 ONNX 域），`ai.onnx.ml` 作为 ML 域按需引入。
- 最高支持 opset 25，对应 IR_VERSION 10。

## 顶层导出 API（F-002）

**信源**：`skl2onnx/__init__.py`

模块导出三个核心转换函数：

| 函数 | 用途 |
|------|------|
| `convert_sklearn` | 完整控制的转换入口，接受 17 个参数 |
| `to_onnx` | 简化封装，支持从训练数据自动推断 `initial_types` |
| `wrap_as_onnx_mixin` | 动态将普通 sklearn 模型包装为支持代数 API 的 Mixin 实例 |

注册相关导出：`update_registered_converter`、`get_model_alias`、`update_registered_parser`、`parse_sklearn_submodel`、`get_latest_tested_opset_version`。

## convert_sklearn 函数（F-003）

**信源**：`skl2onnx/convert.py` L19-L237

### 函数签名

```python
def convert_sklearn(
    model,
    name=None,
    initial_types=None,
    doc_string="",
    target_opset=None,
    targeted_onnx=None,
    custom_conversion_functions=None,
    custom_shape_calculators=None,
    custom_parsers=None,
    options=None,
    intermediate=False,
    white_op=None,
    black_op=None,
    verbose=0,
    final_types=None,
    dtype=None,
    keep_initializers_as_inputs=None,
):
```

### 核心参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | sklearn estimator | 待转换的 sklearn 模型对象 |
| `initial_types` | `List[Tuple[str, DataType]]` | 输入变量名与类型声明，必填（除非 model 有 `infer_initial_types`） |
| `name` | str | ONNX 模型图名称，默认 uuid4 生成 |
| `target_opset` | int/dict | 目标 opset 版本，默认 `get_latest_tested_opset_version()` |
| `doc_string` | str | 写入 ModelProto 的文档字符串 |
| `custom_conversion_functions` | dict | 用户自定义 converter 覆盖，key 为 sklearn 类或别名字符串 |
| `custom_shape_calculators` | dict | 用户自定义 shape_calculator 覆盖 |
| `custom_parsers` | dict | 用户自定义 parser 覆盖 |
| `options` | dict | 转换器选项，支持 `{type(model): opts}` 和 `{id(model): opts}` 两级 |
| `intermediate` | bool | True 时返回 `(onnx_model, topology)` 元组 |
| `white_op`/`black_op` | set/list | 白/黑名单 ONNX 算子类型过滤 |
| `final_types` | list | 输出类型/名称覆盖声明 |
| `dtype` | numpy dtype | 强制 initializer 数据类型 |

### 主流程

```
convert_sklearn(model, ...)
  │
  ├─ 1. 校验 initial_types（必填检查）
  ├─ 2. 生成默认 name（uuid4）
  ├─ 3. 设置默认 target_opset
  ├─ 4. parse_sklearn_model(model, initial_types, ...)
  │     → 将 sklearn 对象树递归解析为 Topology IR
  │     → 返回 Topology 实例（含 Scope/Operator/Variable）
  ├─ 5. convert_topology(topology, model_name, ...)
  │     → 创建 ModelComponentContainer
  │     → topology.convert_operators(container)（数据流调度）
  │     → make_model_from_container() 组装 ModelProto
  └─ 6. 返回：
        intermediate=False → onnx_model (ModelProto)
        intermediate=True  → (onnx_model, topology)
```

## to_onnx 函数（F-004）

**信源**：`skl2onnx/convert.py` L240-L342

`to_onnx` 是 `convert_sklearn` 的简化封装，核心差异：

1. **Mixin 检测**：若 model 是 `OnnxOperatorMixin` 实例，直接调用 `model.to_onnx()`。
2. **自动类型推断**：通过 `guess_initial_types(X, initial_types)` 从训练数据 X 推断 `initial_types`：
   - `np.ndarray` → 取第一行 `X[:1]`，dtype 映射到 TensorType，shape[0] 设为 None（batch 维度）
   - pandas DataFrame → 每列一个输入，列名为变量名，shape=[None,1]
   - list → 直接作为 initial_types 使用
3. **默认 name**：`"ONNX(%s)" % model.__class__.__name__`
4. **opset 修正**：返回前强制修正 opset_import 中主域版本号与 target_opset 一致。

### 函数签名

```python
def to_onnx(
    model,
    X=None,
    name=None,
    initial_types=None,
    target_opset=None,
    options=None,
    white_op=None,
    black_op=None,
    verbose=0,
    final_types=None,
    dtype=None,
    keep_initializers_as_inputs=None,
    # ... 其他参数透传给 convert_sklearn
):
```

## wrap_as_onnx_mixin（F-027）

**信源**：`skl2onnx/convert.py` L345-L360

通过 `skl2onnx.algebra.sklearn_ops.find_class()` 查找与 model 类对应的 `OnnxOperatorMixin` 子类，然后：
1. `object.__new__(cl)` 创建新实例（绕过 `__init__`）
2. `__setstate__` 将 model 的状态复制进去
3. 设置 `op_version` 属性

这允许将普通 sklearn 模型"包装"为支持代数 API 的对象，无需继承。

## 模块导入副作用注册（F-005）

**信源**：`skl2onnx/convert.py` L15-L16

```python
from . import shape_calculators
from . import operator_converters
```

这两个副作用导入在模块加载时执行所有 shape_calculator 和 converter 的 `register_*` 调用，填充 `_converter_pool` 和 `_shape_calculator_pool`。`__init__.py` 中的 `supported_converters()` 也通过相同导入确保注册完成。
