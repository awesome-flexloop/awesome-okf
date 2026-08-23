---
type: concept
title: "转换器注册：别名→实现三级映射、shape_calculator 配对"
description: "sklearn-onnx 的注册体系：双池设计（converter pool + shape_calculator pool）、别名命名规则与别名合并、update_registered_converter 一站式注册、四级查找优先级链、options 两级作用域"
sources:
  references: [../references/registration-algebra.md, ../references/topology-ir.md]
  facts: [F-013, F-014, F-015, F-028, F-012, F-034, F-029]
---

# 转换器注册：别名→实现三级映射、shape_calculator 配对

## 核心理解

sklearn-onnx 的注册体系不是简单的 `{sklearn_class: convert_function}` 字典，而是一套精巧的别名抽象层。理解这套体系的关键是认识到：**别名（alias）是注册的主键，sklearn 类名通过映射表关联到别名，converter 和 shape_calculator 以别名为 key 配对注册**。这种设计解决了 sklearn 类爆炸问题、支持外部库扩展、允许灵活的选项作用域控制。

## 三级映射体系

从 sklearn 类到最终 converter 函数，经历三级映射：

```
sklearn 类（如 LogisticRegression, RidgeClassifier, LinearSVC...）
    │
    │  第一级：sklearn_operator_name_map（别名映射表）
    │  多个语义等价的 sklearn 类 → 同一个别名
    ▼
算子别名（如 "SklearnLinearClassifier"）
    │
    │  第二级：_converter_pool / _shape_calculator_pool（双注册池）
    │  别名 → RegisteredConverter / shape_calculator 函数
    ▼
实现函数（如 convert_sklearn_linear_classifier）
    │
    │  第三级：四级查找优先级链
    │  用户自定义 → 模型自带方法 → 全局注册池
    ▼
实际执行的函数
```

## 别名命名规则

默认规则：`"Sklearn" + sklearn类名`

| sklearn 类 | 默认别名 |
|-----------|---------|
| `LogisticRegression` | `"SklearnLogisticRegression"` |
| `PCA` | `"SklearnPCA"` |
| `StandardScaler` | `"SklearnScaler"` |
| `KMeans` | `"SklearnKMeans"` |

但更重要的是**别名合并**——多个语义等价的 sklearn 类共享同一别名。

## 别名合并：解决类爆炸

sklearn 有 100+ 可转换类，但通过别名合并，converter 实现只有约 60 个。典型的合并案例：

### SklearnLinearRegressor

一个 converter/shape_calculator 对服务于近 30 种线性回归器：

- `LinearRegression`
- `Ridge`、`RidgeCV`
- `Lasso`、`LassoCV`、`LassoLars`、`LassoLarsCV`、`LassoLarsIC`
- `ElasticNet`、`ElasticNetCV`
- `BayesianRidge`、`ARDRegression`
- `SGDRegressor`
- `PassiveAggressiveRegressor`
- `RANSACRegressor`（线性基回归器时）
- `TheilSenRegressor`
- `HuberRegressor`
- 以及其他线性回归变体...

### SklearnLinearClassifier

一个 converter/shape_calculator 对服务于多种线性分类器：

- `LogisticRegression`、`LogisticRegressionCV`
- `RidgeClassifier`、`RidgeClassifierCV`
- `LinearSVC`、`LinearSVR`
- `SGDClassifier`
- `Perceptron`
- `PassiveAggressiveClassifier`
- `BernoulliNB`
- `AdaBoostClassifier`（默认基分类器）
- `BaggingClassifier`（线性基分类器）
- ...

别名合并的依据是这些类在 ONNX 层面使用相同的计算模式（线性变换 + 后处理），只是训练算法不同，而训练好的模型参数（`coef_`、`intercept_`）结构一致。

## 双注册池设计

注册体系维护两个独立的字典（"双池"）：

```python
_converter_pool = {}         # key: 别名, value: RegisteredConverter 实例
_shape_calculator_pool = {}  # key: 别名, value: shape_calculator 函数
```

### 为什么要分两个池？

1. **独立替换**：用户可以只替换 shape_calculator（修改类型推断逻辑）而不改 converter（代码生成逻辑），反之亦然
2. **独立优先级**：四级查找链分别应用于两个池，可以有不同的自定义覆盖
3. **职责分离**：shape_calculator 只负责推断输出类型/形状，converter 只负责生成 ONNX 节点

### register_converter

```python
def register_converter(operator_name, conversion_function,
                       overwrite=False, options=None):
```

- `operator_name`：算子别名字符串
- `conversion_function`：转换函数，签名必须为 `(scope, operator, container)`
- `overwrite`：是否允许覆盖已注册的 converter（默认 False，重复注册抛异常）
- `options`：该转换器支持的选项声明，格式如 `{"zipmap": [True, False, "columns"], "nocl": [True, False]}`

注册时通过 `check_signature()` 校验函数签名一致性，防止传入错误签名的函数。

### register_shape_calculator

```python
def register_shape_calculator(operator_name, calculator_function, overwrite=False):
```

- `calculator_function`：形状计算函数，签名必须为 `(operator)`（只接收 operator 参数）
- 在函数体内设置 `operator.outputs[i].type = TensorType(...)`

### RegisteredConverter 包装类

`RegisteredConverter` 不是简单的函数包装，它在调用时会执行 options 校验：

```python
class RegisteredConverter:
    def __call__(self, scope, operator, container):
        # 1. 获取该 operator 实例允许的 options
        allowed = container._get_allowed_options(operator.raw_operator)
        # 2. 校验用户传入的 options 是否在允许范围内
        # 3. 调用实际的 conversion_function
        return self.converter(scope, operator, container)
```

这确保了用户不能传入转换器不支持的选项值。

## update_registered_converter——一站式注册

推荐使用 `update_registered_converter()` 完成注册，它一次性完成四件事：

```python
def update_registered_converter(model, alias, shape_fct, convert_fct,
                                overwrite=True, parser=None, options=None):
```

| 步骤 | 操作 | 对应 API |
|------|------|---------|
| 1 | 更新别名映射 | `sklearn_operator_name_map[model] = alias` |
| 2 | 注册 converter | `register_converter(alias, convert_fct, ...)` |
| 3 | 注册 shape_calculator | `register_shape_calculator(alias, shape_fct, ...)` |
| 4 | 注册 parser（可选） | `update_registered_parser(model, parser)` |

**自动 parser 推断**：若 options 中包含 `zipmap` 或 `output_class_labels` 键，自动使用 `_parse_sklearn_classifier` 作为 parser（处理分类器的 ZipMap 注入逻辑）。

### 自定义转换器注册示例

```python
from skl2onnx import update_registered_converter

# 为 MyCustomModel 注册转换器
def my_model_shape_calculator(operator):
    # 设置输出类型
    operator.outputs[0].type = FloatTensorType([None, 1])

def my_model_converter(scope, operator, container):
    # 生成 ONNX 节点
    op = operator.raw_operator
    container.add_node('Identity',
                       operator.inputs[0].onnx_name,
                       operator.outputs[0].onnx_name,
                       name=scope.get_unique_operator_name('Identity'))

update_registered_converter(
    MyCustomModel,                   # sklearn 类
    'SklearnMyCustomModel',          # 别名
    my_model_shape_calculator,       # shape calculator
    my_model_converter,              # converter
    options={'my_option': [True, False]}  # 支持的选项
)
```

## 导入副作用注册

内置转换器的注册通过模块导入副作用完成：

```python
# skl2onnx/operator_converters/__init__.py
from . import linear_classifier   # 触发 register_converter("SklearnLinearClassifier", ...)
from . import linear_regressor    # 触发 register_converter("SklearnLinearRegressor", ...)
from . import scaler              # 触发 register_converter("SklearnScaler", ...)
# ... 60+ 个导入
```

每个具体转换器模块在文件底部调用注册函数：

```python
# skl2onnx/operator_converters/linear_classifier.py
def convert_sklearn_linear_classifier(scope, operator, container):
    # ... 实现 ...

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

shape_calculators 目录同理。这意味着**导入 `skl2onnx` 包即完成所有内置转换器注册**，无需额外初始化。

## 四级查找优先级链

在转换时，`Topology.call_converter()` 和 `call_shape_calculator()` 使用相同的四级查找链：

```
优先级1（最高）: custom_conversion_functions[type(raw_operator)]
                 用户在 convert_sklearn(custom_conversion_functions=...) 中
                 按 sklearn 类精确指定的自定义函数

优先级2: custom_conversion_functions[operator.type]
         用户按算子别名指定的自定义函数（影响所有共享该别名的类）

优先级3: raw_operator.onnx_converter()
         模型对象自带的方法（OnnxOperatorMixin 提供）
         优先级高于全局注册池，实现"模型自带转换逻辑"

优先级4（最低）: _registration.get_converter(operator.type)
              全局注册池（内置转换器）
```

### 设计意图

- **优先级1>2**：按类型精确匹配优先于按别名匹配，允许用户为特定子类定制行为而不影响同别名的其他类
- **优先级3**：OnnxOperatorMixin 让模型"自带转换逻辑"，方法级注册优先级最高但低于用户显式自定义，尊重用户覆盖意图
- **优先级4**：内置转换器作为兜底

## Options 两级作用域

options 字典支持两级查找，实现细粒度的配置控制：

```python
options = {
    id(model1): {'zipmap': False},      # 实例级：特定 model1 实例
    type(model2): {'zipmap': 'columns'}, # 类级：所有 model2 类的实例
}
```

查找顺序：
1. `options.get(id(model), {})` —— 实例级（最高优先级）
2. `options.get(type(model), {})` —— 类级
3. `default_values` —— 默认值

合并后校验所有 key/value 在 `allowed_options` 范围内。

### 应用场景

Pipeline 中有两个 TfidfVectorizer，需要不同配置：

```python
pipe = Pipeline([
    ('tfidf1', TfidfVectorizer(ngram_range=(1,1))),
    ('tfidf2', TfidfVectorizer(ngram_range=(1,2))),
    ('clf', LogisticRegression())
])

options = {
    id(pipe.named_steps['tfidf1']): {'sep': [' ', '.']},
    id(pipe.named_steps['tfidf2']): {'sep': [' ']},
}
model_onnx = convert_sklearn(pipe, initial_types=..., options=options)
```

## 线性分类器转换器实例（F-029）

`convert_sklearn_linear_classifier` 的具体映射方式展示了注册体系的实际使用：

1. 从 `operator.raw_operator` 提取 `coef_`（系数矩阵）和 `intercept_`（截距向量）
2. 优先使用 `ai.onnx.ml` 域的 `LinearClassifier` 算子（若白名单允许）
3. 设置属性：
   - `coefficients`：系数矩阵展平
   - `intercepts`：截距向量
   - `multi_class`：0=二分类，1=多分类
   - `post_transform`：`LOGISTIC`（二分类）/`SOFTMAX`（多分类）/`NONE`
4. 二分类时将系数取负拼接以实现 one-vs-rest
5. 注册时声明支持的选项：`zipmap`、`nocl`（no class labels）、`raw_scores`

## 关联概念

- [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](02-topology-ir.md) — Operator 如何使用注册的 converter/shape_calculator
- [OnnxOperator代数API：嵌入式DSL、类工厂、延迟求值、三件套自动生成](04-onnx-operator-algebra.md) — OnnxOperatorMixin 如何实现"模型自带转换逻辑"（优先级3）
- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — 四级查找链在数据流调度中的应用
