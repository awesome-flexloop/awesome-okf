---
type: concept
title: "转换器注册与分发：双注册池、导入副作用、委托路径"
description: "onnxmltools 的算子注册机制：双注册池（converter/shape_calculator）设计、导入副作用注册模式、字符串key弱类型风险、custom参数扩展点与不对称性、转换器与形状计算器的配对约束"
sources:
  references: [../references/registration-types.md, ../references/topology-ir.md, ../references/convert-entry.md]
  facts: [F-010, F-011, F-012, F-013, F-014, F-039, F-006, F-007, F-008, F-009]
---

# 转换器注册与分发：双注册池、导入副作用、委托路径

## 核心理解

onnxmltools 使用极简的插件注册机制实现算子分发：两个模块级全局字典作为注册池，各算子模块在文件底部调用注册函数，`convert.py` 通过 import 语句触发"导入副作用"完成注册。转换时通过字符串类型名在注册池中查找对应的 converter/shape_calculator 函数并调用。

关键设计特点是**双注册池**——每个算子必须同时注册"转换器"（负责生成ONNX节点）和"形状计算器"（负责推断输出形状），二者缺一不可。

## 双注册池设计

`_registration.py` 维护两个独立的模块级字典：

```python
_converter_pool = {}         # operator_type → converter_function
_shape_calculator_pool = {}  # operator_type → shape_calculator_function
```

四对操作函数：

| 函数 | 功能 | 覆盖行为 |
|------|------|----------|
| `register_converter(type, func)` | 注册转换器 | 默认不允许覆盖（overwrite=False时抛ValueError） |
| `get_converter(type)` | 查找转换器 | 未注册抛ValueError |
| `register_shape_calculator(type, func)` | 注册形状计算器 | 默认不允许覆盖 |
| `get_shape_calculator(type)` | 查找形状计算器 | 未注册抛ValueError |

**为什么需要双注册池？** 转换和形状推断是两个独立的阶段：
- **形状推断阶段**（compile的`_infer_all_types`）：只需要知道每个算子的输出形状和类型，不需要生成ONNX节点
- **转换阶段**（convert_topology的拓扑遍历）：需要实际生成ONNX节点，同时可能创建新变量

将两者分离允许：
1. 形状推断在不生成ONNX节点的情况下完成（用于类型检查和优化）
2. 不同算子可以共享形状计算器（如多个分类器使用相同的输出形状逻辑）

## 导入副作用注册模式（F-011）

注册不是通过显式的注册表维护，而是通过**模块导入的副作用**完成：

```
convert.py 被调用时：
  from . import operator_converters, shape_calculators   ← 这行触发注册
    ↓
operator_converters/__init__.py：
  from . import LightGbm   ← 导入算子模块
    ↓
LightGbm.py 文件底部：
  register_converter('LgbmClassifier', convert_lightgbm)  ← 执行注册
  register_converter('LgbmRegressor', convert_lightgbm)
  register_shape_calculator('LgbmClassifier', calculate_lightgbm_classifier_output_shapes)
  ...
```

这种模式的特点：
- **优点**：添加新算子只需创建一个文件并在底部加注册调用，无需修改中央注册表
- **缺点**：注册时机完全依赖导入顺序；如果某个 `convert.py` 忘记 import 子模块，所有算子查找都会失败
- **隐式传递**：xgboost/convert.py 中注释掉了 `# from . import shape_calculators`，但因为 `operator_converters/XGBoost.py` 内部间接导入了 shape_calculators 才没有出问题——这是脆弱的隐式依赖

## 注册策略：多对一映射与内部分发（F-012, F-013）

多个 operator 类型可以注册到同一个转换函数，内部通过 `isinstance` 再分发：

### LightGBM：4个类型→2个函数

```python
# LgbmClassifier、LgbmRegressor、LgbmRanker 都注册到 convert_lightgbm
register_converter('LgbmClassifier', convert_lightgbm)
register_converter('LgbmRegressor', convert_lightgbm)
register_converter('LgbmRanker', convert_lightgbm)
register_converter('LgbmZipMap', convert_lgbm_zipmap)
```

`convert_lightgbm` 内部检查 operator 的类型（通过 `operator.type` 字符串或 `operator.raw_operator` 的类），分发到分类/回归/排序的不同处理逻辑。

### XGBoost：4个类型→1个函数

```python
register_converter('XGBClassifier', convert_xgboost)
register_converter('XGBRFClassifier', convert_xgboost)
register_converter('XGBRegressor', convert_xgboost)
register_converter('XGBRFRegressor', convert_xgboost)
```

`convert_xgboost` 内部根据 `isinstance(raw_operator, ...)` 分发到 `XGBClassifierConverter` 或 `XGBRegressorConverter`。

### CoreML：15个顶层类型+40+神经网络层（F-014）

CoreML 是注册算子最多的前端：
- 顶层15个传统ML算子：ArrayFeatureExtractor、DictVectorizer、FeatureVectorizer、GLMClassifier、GLMRegressor、Identity、Imputer、Normalizer、OneHotEncoder、Scaler、SVC、SVR、TensorToLabel、TensorToProbabilityMap、TreeEnsemble
- `neural_network/` 子包40+神经网络层算子

## 调度分发逻辑

### 转换阶段调度（convert_topology）

```python
for operator in topological_operator_iterator():
    if operator.type in topology.custom_conversion_functions:
        # 用户自定义转换器优先
        topology.custom_conversion_functions[operator.type](scope, operator, container)
    else:
        # 从注册池查找
        get_converter(operator.type)(scope, operator, container)
```

### 形状推断阶段调度（_infer_all_types）

```python
for operator in 拓扑顺序:
    if operator.type in topology.custom_shape_calculators:
        # 用户自定义形状计算器优先
        topology.custom_shape_calculators[operator.type](operator)
    elif operator.type in topology.custom_conversion_functions:
        pass  # ⚠️ Keras特殊通道：如果只注册了converter没注册shape_calculator，静默跳过
    else:
        operator.infer_types()  # → get_shape_calculator(operator.type)(operator)
```

### Operator.infer_types（F-039）

```python
def infer_types(self):
    get_shape_calculator(self.type)(self)
```

直接从 `_shape_calculator_pool` 查找对应函数，传入 operator 自身（函数通过 `operator.inputs`/`operator.outputs` 访问变量类型信息）。

## custom参数的不对称风险

`custom_conversion_functions` 和 `custom_shape_calculators` 是用户扩展的入口，但两者处理不对称：

| 场景 | 转换阶段 | 形状推断阶段 | 结果 |
|------|----------|-------------|------|
| 同时注册converter+shape_calculator | ✅ 使用自定义converter | ✅ 使用自定义shape_calculator | 正确 |
| 只注册converter（非Keras） | ✅ 使用自定义converter | ⚠️ 走pass分支（静默跳过） | **输出形状可能错误** |
| 只注册shape_calculator | ❌ 从池中查找converter（未注册报错） | ✅ 使用自定义shape_calculator | 转换阶段失败 |
| 都不注册 | ✅ 从池中查找 | ✅ 从池中查找 | 正常（内置算子） |

⚠️ **关键注意事项**：编写自定义算子时，**必须同时提供 converter 和 shape_calculator**，二者缺一不可。`pass` 分支是为 Keras 转换器（走 tf2onnx 不依赖形状推断）保留的特殊通道，对其他场景是潜在 bug 源。

## 字符串key弱类型风险

注册池使用字符串作为 key，这带来弱类型风险：

1. **拼写错误无法静态检测**：`register_converter("LgbmClassifier", ...)` 和 `register_converter("lgbmclassifier", ...)` 会被视为不同算子，只能在运行时 `get_converter` 抛出 "Unsupported conversion for operator" 时才发现。
2. **类型名约定不统一**：CoreML 使用 `ArrayFeatureExtractor`（大驼峰），LightGBM 使用 `LgbmClassifier`（Lgbm缩写），XGBoost 使用 `XGBClassifier`（XGB缩写），没有统一的命名规范。

## 三条委托路径

除了自有IR的注册分发路径，还有三条不经过注册池的委托路径：

### 路径1：sklearn → skl2onnx（F-006）

`convert_sklearn` 完全委托给 skl2onnx，onnxmltools 没有 sklearn 的 operator_converters 或 shape_calculators。skl2onnx 有自己的双注册池和更完善的别名合并机制（30+线性回归器共享同一别名）。

### 路径2：Keras/TensorFlow → tf2onnx（F-007, F-009）

- Keras（TF≥2.0）：调用 `tf2onnx.convert.from_keras`，将 initial_types 映射为 tf.TensorSpec
- TensorFlow：调用 `tf2onnx.tfonnx.process_tf_graph` + `optimize_graph` + `make_model` 流水线

这两条路径将 custom_conversion_functions 映射为 tf2onnx 的 custom_op_conversions。

### 路径3：CatBoost → 内置导出（F-008）

直接调用 `catboost.utils.convert_to_onnx_object`，是最简单的"一行转发"。

## 形状计算器校验工具

`shape_calculator.py` 提供通用校验函数，帮助编写形状计算器：

```python
def check_input_and_output_numbers(operator, input_count_range=None, output_count_range=None):
    """校验输入/输出个数，支持(最小,最大)范围或精确数字"""

def check_input_and_output_types(operator, good_input_types=None, good_output_types=None):
    """校验输入/输出类型是否在白名单中"""
```

## 设计洞察

1. **注册机制是极简的插件系统**：两个字典+四个函数，没有复杂的抽象基类或装饰器，但足够满足多框架扩展需求。
2. **导入副作用是Pythonic但脆弱的**：利用Python模块导入的执行特性实现自动注册，简洁但依赖导入顺序和完整性。
3. **双池配对约束必须遵守**：converter和shape_calculator是不可分割的一对，遗漏任何一个都会导致运行时错误。
4. **custom参数的pass分支是技术债**：为Keras预留的特殊通道破坏了双池对称设计，在非Keras场景可能导致静默错误。

## 关联概念

- [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](01-topology-ir.md) — 了解Operator/Variable如何被调度
- [编译流水线五阶段：createTopology→compile→convert_topology→make_model](02-conversion-pipeline.md) — 了解形状推断和转换在流水线中的位置
- [数据类型系统：四层DataType、TensorType维度规格、三向类型猜测](04-type-system.md) — 了解形状计算器操作的类型对象
