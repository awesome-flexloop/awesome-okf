---
type: concept
title: "OnnxOperator 代数 API：嵌入式 DSL、类工厂、延迟求值、三件套自动生成"
description: "sklearn-onnx 的 OnnxOperator 代数 API 通过 ClassFactory 动态生成 ONNX 算子类、延迟求值构建 AST、OnnxOperatorMixin 自动桥接 sklearn，让自定义转换器只需一个 to_onnx_operator 方法"
sources:
  references: [../references/registration-algebra.md, ../references/convert-api.md]
  facts: [F-025, F-026, F-027, F-004, F-012]
---

# OnnxOperator 代数 API：嵌入式 DSL、类工厂、延迟求值、三件套自动生成

## 核心理解

sklearn-onnx 在 `skl2onnx.algebra` 子包中实现了一套**嵌入式 DSL（领域特定语言）**，它表面上看起来像 PyTorch 那样的 eager API（重载算术运算符、支持链式调用），实际上是在**构造延迟求值的 AST（抽象语法树）**。结合 `OnnxOperatorMixin`，用户只需实现一个 `to_onnx_operator()` 方法返回 DSL 表达式树，mixin 就会自动提供 parser、shape_calculator、converter 三者的默认实现——将自定义转换器的代码量从三个函数缩减为一个方法。

## 从手动 converter 到代数 API

### 传统方式：手写三件套

自定义一个 sklearn 兼容估计器的 ONNX 导出，传统上需要写三个函数：

```python
# 1. Parser：声明输出变量
def my_parser(scope, model, inputs, custom_parsers=None):
    # 声明输出变量，处理 ZipMap 等
    ...

# 2. Shape Calculator：推断输出形状
def my_shape_calculator(operator):
    operator.outputs[0].type = FloatTensorType([None, 1])

# 3. Converter：手动拼 ONNX 节点
def my_converter(scope, operator, container):
    op = operator.raw_operator
    coef_name = scope.get_unique_variable_name('coef')
    container.add_initializer(coef_name, onnx_proto.TensorProto.FLOAT,
                              [1, op.n_features_], op.coef_.flatten())
    container.add_node('MatMul',
                       [operator.inputs[0].onnx_name, coef_name],
                       operator.outputs[0].onnx_name, ...)
```

然后通过 `update_registered_converter()` 注册这三个函数。

### 代数 API 方式：一个方法

使用 OnnxOperatorMixin，只需实现一个方法：

```python
from skl2onnx.algebra.onnx_operator_mixin import OnnxOperatorMixin
from skl2onnx.algebra.onnx_ops import OnnxMatMul, OnnxAdd, OnnxSigmoid

class MyLinearModel(OnnxOperatorMixin, BaseEstimator, RegressorMixin):
    op_version = 15  # 目标 opset
    
    def fit(self, X, y):
        # 正常训练逻辑
        self.coef_ = ...
        self.intercept_ = ...
        return self
    
    def to_onnx_operator(self, inputs=None, outputs=None,
                         target_opset=None, options=None):
        # 用代数 API 拼出计算图——返回的是 AST，不是立即执行
        X = inputs[0]
        Y = OnnxMatMul(X, self.coef_.astype(np.float32), op_version=target_opset)
        Y = OnnxAdd(Y, self.intercept_.astype(np.float32), op_version=target_opset)
        return Y
```

parser、shape_calculator、converter 三者由 Mixin 自动提供。

## ClassFactory：动态生成算子类

`onnx_ops.py` 在模块加载时，通过 `ClassFactory` 为每个 ONNX 算子动态生成一个 Python 类：

```python
def ClassFactory(class_name, op_name, inputs, outputs,
                 input_range=None, output_range=None,
                 domain=None, attr_names=None, **kwargs):
    """动态生成继承自 OnnxOperator 的算子类"""
    # class_name: Python 类名（如 "Abs", "MatMul", "LinearClassifier"）
    # op_name: ONNX 算子名（如 "Abs", "MatMul", "LinearClassifier"）
    # domain: 算子域（None=ai.onnx, "ai.onnx.ml"=ML域）
    # attr_names: 该算子的属性名列表
    ...
```

生成的类具有以下特性：

1. **类名即算子名**：`OnnxMatMul` 对应 ONNX `MatMul`，`OnnxAdd` 对应 `Add`，`OnnxLinearClassifier` 对应 `ai.onnx.ml:LinearClassifier`
2. **继承自 OnnxOperator**：共享基类的 `add_to()`、`to_onnx()`、运算符重载等功能
3. **构造函数签名**：位置参数为输入，关键字参数为属性

```python
# 使用示例：构建 MatMul(X, W) + b 的表达式
from skl2onnx.algebra.onnx_ops import OnnxMatMul, OnnxAdd

# X 是输入变量名或另一个 OnnxOperator
# W 是 numpy 数组（自动转为 initializer）
# op_version 指定目标 opset
Y = OnnxMatMul(X, W, op_version=15)
Z = OnnxAdd(Y, b, op_version=15)
```

## OnnxOperator 基类：延迟求值 AST

OnnxOperator 构造时**不立即生成 ONNX 节点**，而是构建一个延迟求值的表达式树：

```python
class OnnxOperator:
    def __init__(self, *args, op_version=None, output_names=None,
                 domain=None, **kwargs):
        self.inputs = args       # 位置参数：输入（字符串或其他 OnnxOperator）
        self.kwargs = kwargs     # 关键字参数：算子属性
        self.op_version = op_version
        self.output_names = output_names
        self.domain = domain
        self.state = GraphState()  # 图状态管理（延迟求值上下文）
```

### add_to()：从 AST 到 ONNX 节点

`add_to(scope, container, operator=None, run_converters=True)` 是关键方法，它递归地将整个表达式树展开为对 `container.add_node()` 的调用：

```python
def add_to(self, scope, container, operator=None, run_converters=True):
    # 1. 递归处理所有输入 OnnxOperator（先处理依赖）
    for inp in self.inputs:
        if isinstance(inp, OnnxOperator):
            inp.add_to(scope, container, operator, run_converters)
    
    # 2. 收集输入的 ONNX 名称
    input_names = []
    for inp in self.inputs:
        if isinstance(inp, str):
            input_names.append(inp)
        elif isinstance(inp, OnnxOperator):
            input_names.append(inp.output_name)
        elif isinstance(inp, np.ndarray):
            # numpy 数组自动添加为 initializer
            init_name = scope.get_unique_variable_name(...)
            container.add_initializer(init_name, ...)
            input_names.append(init_name)
    
    # 3. 生成唯一输出名
    output_name = scope.get_unique_variable_name(self.op_name)
    
    # 4. 向 container 添加 NodeProto
    container.add_node(self.op_name, input_names, [output_name],
                       op_domain=self.domain,
                       op_version=self.op_version,
                       **self.kwargs)
    
    self.output_name = output_name
```

### to_onnx()：独立模型生成

`to_onnx(inputs, outputs=None, target_opset=None, ...)` 可以独立构建一个小型 ONNX 模型，主要用于 shape inference：

```python
# 构建一个临时 ONNX 模型用于形状推断
small_model = onnx_expr.to_onnx(
    inputs=[('input', FloatTensorType([None, 4]))],
    target_opset=15
)
# 用 onnx.shape_inference 推断输出形状
inferred = onnx.shape_inference.infer_shapes(small_model)
```

### 运算符重载

OnnxOperator 重载了 Python 运算符，可以像写 numpy 表达式一样写 ONNX 计算图：

```python
# 通过运算符重载组合算子
Y = X * 2 + 1            # Mul → Add
Y = -X                    # Neg
Y = X @ W                 # MatMul
Y = X[0]                  # 索引（多输出算子）
```

多输出算子（如 `LinearClassifier` 输出 label 和 probabilities）通过 `OnnxOperatorItem` 支持索引：

```python
classifier = OnnxLinearClassifier(X, coefficients=..., intercepts=..., op_version=1)
label = classifier[0]      # 第一个输出
proba = classifier[1]      # 第二个输出
```

## OnnxOperatorMixin：三件套自动桥接

`OnnxOperatorMixin` 是连接 sklearn BaseEstimator 和 OnnxOperator DSL 的桥梁。

### 子类契约

子类必须：

| 要求 | 说明 |
|------|------|
| 继承 `OnnxOperatorMixin` | 多继承：`class MyModel(OnnxOperatorMixin, BaseEstimator, ...)` |
| 设置 `op_version` 属性 | 目标 opset 版本号（如 `op_version = 15`） |
| 实现 `to_onnx_operator()` | 返回 OnnxOperator 表达式树 |
| 可选：`enumerate_initial_types()` | 提供输入类型声明（替代 initial_types 参数） |

### 自动提供的三方法

Mixin 自动为子类提供三个关键方法：

#### 1. onnx_converter（优先级3的 converter）

```python
def onnx_converter(self, scope, operator, container):
    # 获取输入
    inputs = [i.onnx_name for i in operator.inputs]
    # 调用 to_onnx_operator 构建 AST
    op = self.to_onnx_operator(inputs=inputs,
                                outputs=[o.onnx_name for o in operator.outputs],
                                target_opset=container.target_opset,
                                options=container.get_options(self))
    # 将 AST 添加到 container
    op.add_to(scope, container, operator)
```

#### 2. onnx_shape_calculator（优先级3的 shape calculator）

Mixin 默认的 shape_calculator 利用 `onnx.shape_inference.infer_shapes` 实现自动形状推断：

```python
def onnx_shape_calculator(self, operator):
    # 1. 收集输入类型
    input_types = [(v.onnx_name, v.type) for v in operator.inputs]
    # 2. 构建临时小型 ONNX 模型
    op = self.to_onnx_operator(inputs=[v.onnx_name for v in operator.inputs],
                                target_opset=self.op_version)
    small_model = op.to_onnx(inputs=input_types, target_opset=self.op_version)
    # 3. 用 onnx.shape_inference 推断输出形状
    inferred = onnx.shape_inference.infer_shapes(small_model)
    # 4. 将推断结果设置到 operator.outputs
    for output, inferred_type in zip(operator.outputs, inferred.graph.output):
        output.type = TensorType.from_onnx_type(inferred_type.type)
```

若 `to_onnx_operator` 未实现，则回退到父 sklearn 类的 shape_calculator。

#### 3. onnx_parser（默认 parser）

默认通过 `to_onnx_operator()` 的输出名推断输出列表。对于分类器，若 options 中声明了 zipmap，自动使用分类器 parser。

### to_onnx() 快捷方法

Mixin 还提供了 `to_onnx()` 方法：

```python
model = MyLinearModel().fit(X_train, y_train)
onnx_model = model.to_onnx(X_train, target_opset=15)
```

内部仍然调用 `convert_sklearn(self, ...)`——代数 API 不是独立路径，最终还是走回 Topology 管线，OnnxOperator 只是生成 Operator 节点的一种方式。

## wrap_as_onnx_mixin：动态混入

对于无法修改源码的已有 sklearn 模型类，可以使用 `wrap_as_onnx_mixin()` 动态包装：

```python
from skl2onnx import to_onnx, wrap_as_onnx_mixin

# 将普通 sklearn 模型包装为支持代数 API 的实例
wrapped = wrap_as_onnx_mixin(sklearn_model, target_opset=15)
onnx_model = to_onnx(wrapped, X_train)
```

实现原理：
1. 通过 `skl2onnx.algebra.sklearn_ops.find_class()` 查找与 model 类对应的 OnnxOperatorMixin 子类
2. `object.__new__(cl)` 创建新实例（绕过 `__init__`）
3. `__setstate__` 将原 model 的状态复制到新实例
4. 设置 `op_version` 属性

## GraphState / GraphStateVar：延迟求值状态管理

OnnxOperator 内部使用 `GraphState` 和 `GraphStateVar` 管理延迟求值的图状态：

- `GraphState`：持有当前图构建上下文中的变量映射、已添加的节点等
- `GraphStateVar`：表示延迟求值中的变量引用，在 `add_to()` 调用时解析为具体的 ONNX 名称

这使得 OnnxOperator 表达式可以在不知道输入 shape 的情况下先搭好图结构，在实际 `add_to()` 时才解析所有引用。

## 代数 API 的适用场景与限制

### 适用场景

1. **自定义 sklearn 估计器**：继承 OnnxOperatorMixin 快速实现 ONNX 导出
2. **复杂 converter 内部**：在 converter 函数内用 onnx_ops 构建子图，替代裸 `container.add_node()`，提高可读性
3. **快速原型验证**：用 DSL 快速拼出计算图验证思路

### 限制

1. **shape_inference 性能开销**：Mixin 默认的 shape_calculator 需要构建临时 ONNX 模型并调用 `infer_shapes`，有一定性能开销。对性能敏感或形状推断可能失败的场景，建议手写 shape_calculator
2. **不覆盖所有 ONNX 算子**：ClassFactory 生成了大部分标准算子，但最新或冷门算子可能需要手动用 `container.add_node()`
3. **最终仍走 Topology 管线**：代数 API 不是独立的转换路径，OnnxOperatorMixin.onnx_converter() 最终还是通过 Topology 四级查找链被调用
4. **op_version 必须显式指定**：每个 OnnxOperator 构造时需要 `op_version` 参数，或在 Mixin 子类设置 `op_version` 属性

## 关联概念

- [转换器注册：别名→实现三级映射、shape_calculator配对](03-converter-registration.md) — OnnxOperatorMixin 对应四级查找链的优先级3
- [自定义转换器开发](../examples/custom-converter.md) — 使用 OnnxOperatorMixin 开发自定义转换器的完整示例
- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — 代数 API 如何融入四阶段管线
