---
type: reference
title: "注册机制（register_converter）与 OnnxOperator 代数 API"
description: "sklearn-onnx 的转换器注册机制（register_converter/register_shape_calculator/update_registered_converter、双池设计、别名映射）以及 OnnxOperator 嵌入式 DSL（ClassFactory 类工厂、延迟求值、OnnxOperatorMixin）的源码信源登记"
sources:
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/common/_registration.py"
    facts: [F-013]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/_supported_operators.py"
    facts: [F-014, F-015]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/operator_converters/__init__.py"
    facts: [F-028]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/algebra/onnx_ops.py"
    facts: [F-025]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/algebra/onnx_operator.py"
    facts: [F-025]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/algebra/onnx_operator_mixin.py"
    facts: [F-026]
---

# 注册机制（register_converter）与 OnnxOperator 代数 API

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `common/_registration.py` | 注册核心 | `_converter_pool`、`_shape_calculator_pool` 双池、`register_converter`/`register_shape_calculator` 函数、`RegisteredConverter` 包装类 |
| `_supported_operators.py` | 别名映射 | `sklearn_operator_name_map` 构建、别名合并规则、`update_registered_converter` 一次性注册入口 |
| `operator_converters/__init__.py` | 模块导入触发 | 通过 60+ 个模块级导入触发注册副作用 |
| `algebra/onnx_ops.py` | 类工厂 | `ClassFactory` 动态生成每个 ONNX 算子的 Python 类 |
| `algebra/onnx_operator.py` | DSL 基类 | `OnnxOperator` 基类、延迟求值、`GraphState`/`GraphStateVar` |
| `algebra/onnx_operator_mixin.py` | Mixin 桥接 | `OnnxOperatorMixin` 将 DSL 与 sklearn BaseEstimator 桥接 |

## 注册机制——双池设计（F-013）

**信源**：`common/_registration.py` L1-L104

### 两个全局注册池

```python
_converter_pool = {}        # key: 算子别名字符串, value: RegisteredConverter 实例
_shape_calculator_pool = {} # key: 算子别名字符串, value: shape calculator 函数
```

### register_converter

```python
def register_converter(operator_name, conversion_function,
                       overwrite=False, options=None):
```

- 默认不允许覆盖（`overwrite=False`），重复注册同名算子抛 RuntimeError
- 注册时通过 `check_signature()` 校验函数签名一致性：converter 函数必须接受 `(scope, operator, container)` 三个参数
- `options` 字典声明该转换器支持的选项及其允许值

### register_shape_calculator

```python
def register_shape_calculator(operator_name, calculator_function, overwrite=False):
```

- 同理，shape_calculator 函数必须接受 `(operator)` 一个参数

### RegisteredConverter 包装类

`RegisteredConverter` 包装实际转换函数，在 `__call__` 时：
1. 通过 `args[2]._get_allowed_options(args[1].raw_operator)` 获取允许的选项
2. 校验用户传入的 options 是否在允许范围内
3. 调用实际转换函数

## 算子别名映射规则（F-014）

**信源**：`_supported_operators.py` L396-L559

### 默认命名规则

sklearn 类 → `"Sklearn" + 类名`：

| sklearn 类 | 默认别名 |
|-----------|---------|
| `LogisticRegression` | `"SklearnLogisticRegression"` |
| `PCA` | `"SklearnPCA"` |
| `StandardScaler` | `"SklearnScaler"` |

### 别名合并

多个语义等价的 sklearn 类共享同一别名，共享 converter/shape_calculator：

| 共享别名 | 覆盖的 sklearn 类（部分） |
|---------|------------------------|
| `"SklearnLinearRegressor"` | `LinearRegression`、`Ridge`、`Lasso`、`ElasticNet`、`BayesianRidge`、`ARDRegression`、`SGDRegressor` 等近 30 个类 |
| `"SklearnLinearClassifier"` | `LogisticRegression`、`RidgeClassifier`、`LinearSVC`、`SGDClassifier`、`Perceptron`、`AdaBoostClassifier`（默认基分类器）、`BaggingClassifier`（线性基分类器）、`BernoulliNB` 等 |
| `"SklearnSVC"` | `SVC`、`NuSVC` |
| `"SklearnSVR"` | `SVR`、`NuSVR` |

这解决了 sklearn 类爆炸问题——100+ 可转换类只需约 60 个 converter 实现。

## update_registered_converter——一站式注册（F-015）

**信源**：`_supported_operators.py` L562-L628

```python
def update_registered_converter(model, alias, shape_fct, convert_fct,
                                overwrite=True, parser=None, options=None):
```

一次性完成四件事：

1. 更新 `sklearn_operator_name_map[model] = alias`（别名映射）
2. 调用 `register_converter(alias, convert_fct, overwrite=overwrite, options=options)`
3. 调用 `register_shape_calculator(alias, shape_fct, overwrite=overwrite)`
4. 若提供 `parser` 则调用 `update_registered_parser(model, parser)`
   - 若 options 含 `zipmap` 或 `output_class_labels`，自动使用 `_parse_sklearn_classifier` 作为 parser

## 导入副作用注册模式（F-028）

**信源**：`operator_converters/__init__.py` L1-L76

```python
# operator_converters/__init__.py
from . import linear_classifier
from . import linear_regressor
from . import scaler
# ... 60+ 个模块级导入
```

每个具体转换器模块在模块底部调用注册：

```python
# operator_converters/linear_classifier.py（示例）
def convert_sklearn_linear_classifier(scope, operator, container):
    # ... 转换逻辑 ...

register_converter(
    "SklearnLinearClassifier",
    convert_sklearn_linear_classifier,
    options={
        "zipmap": [True, False, "columns"],
        "nocl": [True, False],
        "raw_scores": [True, False],
    }
)
```

同理 `shape_calculators/__init__.py` 导入所有 shape calculator 模块，每个模块在底部调用 `register_shape_calculator(...)`。

## OnnxOperator 代数 API——类工厂模式（F-025）

**信源**：`algebra/onnx_ops.py` L19-L100、`algebra/onnx_operator.py` L140-L200

### ClassFactory 动态类生成

`onnx_ops.py` 在模块加载时，通过 `ClassFactory` 为每个 ONNX 算子（包括 `ai.onnx` 和 `ai.onnx.ml` 域）动态生成一个 Python 类：

```python
def ClassFactory(class_name, op_name, inputs, outputs,
                 input_range=None, output_range=None,
                 domain=None, attr_names=None, **kwargs):
    # 动态创建继承自 OnnxOperator 的类
    # 类名即算子名（如 Abs、MatMul、LinearClassifier）
```

生成的类继承自 `OnnxOperator` 基类，每个类对应一个 ONNX 算子。

### OnnxOperator 基类

| 方法/属性 | 说明 |
|-----------|------|
| `__init__(*args, op_version=None, output_names=None, domain=None, **kwargs)` | 位置参数为输入（变量名字符串或其他 OnnxOperator 实例），关键字参数为算子属性 |
| `add_to(scope, container, operator=None, run_converters=True)` | 将自身（及递归输入）添加到 container 中，生成 NodeProto |
| `to_onnx(inputs, outputs=None, target_opset=None, ...)` | 独立生成小型 ONNX 模型（用于形状推断） |
| 运算符重载 | 通过 `OnnxOperatorItem` 支持索引多输出（如 `op[0]`、`op[1]`） |

### 延迟求值机制

OnnxOperator 构造时**不立即生成 ONNX 节点**，而是构建延迟求值的计算图描述（AST）。内部使用 `GraphState`/`GraphStateVar` 管理图状态，直到调用 `add_to()` 时才递归展开为 `container.add_node()` 调用。

## OnnxOperatorMixin——sklearn 估计器桥接（F-026）

**信源**：`algebra/onnx_operator_mixin.py` L15-L241

`OnnxOperatorMixin` 是供用户自定义 sklearn 兼容估计器继承的 Mixin 类。

### 子类必须实现的方法

| 方法 | 说明 |
|------|------|
| `to_onnx_operator(inputs, outputs=None, target_opset=None, options=None)` | **必须由子类重载**，返回 OnnxOperator 实例（DSL 表达式树） |

### Mixin 自动提供的方法

| 方法 | 默认实现 |
|------|---------|
| `to_onnx(X, name, options, ...)` | 调用 `convert_sklearn(self, ...)` |
| `onnx_parser(scope, inputs, custom_parsers=None)` | 默认通过 `to_onnx_operator()` 的输出名推断输出列表 |
| `onnx_shape_calculator(operator)` | 默认通过构建临时 ONNX 模型 + `onnx.shape_inference.infer_shapes` 推断输出形状；若 `to_onnx_operator` 未实现则回退到父 sklearn 类的 shape_calculator |
| `onnx_converter(scope, operator, container)` | 默认通过 `to_onnx_operator().add_to()` 将算子添加到 container；若未实现则回退到父 sklearn 类的 converter |

### 子类必须设置的属性

```python
op_version = None  # 必须设置为目标 opset 号（如 15、17、21）
```

可选实现 `enumerate_initial_types()` 提供输入类型声明。

### 自动三件套

使用 OnnxOperatorMixin 后，用户**只需实现 `to_onnx_operator()` 一个方法**，mixin 自动提供 parser、shape_calculator、converter 三者的默认实现：
- parser → 从 OnnxOperator 输出名推断
- shape_calculator → 构建临时模型 → onnx.shape_inference 推断
- converter → OnnxOperator.add_to() 生成节点
