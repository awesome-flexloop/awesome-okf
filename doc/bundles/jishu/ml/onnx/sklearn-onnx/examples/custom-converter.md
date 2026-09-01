---
type: example
title: "自定义转换器开发：两种模式对比"
description: "通过两种方式开发自定义 sklearn 估计器的 ONNX 导出：传统三件套（parser+shape_calculator+converter）和 OnnxOperatorMixin 代数API模式"
sources:
  concepts: [../concepts/03-converter-registration.md, ../concepts/04-onnx-operator-algebra.md, ../concepts/00-overall-architecture.md]
  references: [../references/registration-algebra.md, ../references/convert-api.md]
---

# 自定义转换器开发：两种模式对比

## 目标

为自定义 sklearn 估计器开发 ONNX 导出能力。本示例实现一个简单的自定义变换（`ThresholdApplier`：将小于阈值的元素置零），通过两种方式实现 ONNX 导出：
1. **传统三件套模式**：手动编写 parser + shape_calculator + converter 三个函数
2. **OnnxOperatorMixin 模式**：继承 Mixin 类，只需实现一个 `to_onnx_operator()` 方法

通过对比理解两种模式的优劣和适用场景。

## 模式一：传统三件套模式

### 1. 定义自定义估计器

```python
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class ThresholdApplier(BaseEstimator, TransformerMixin):
    """将小于阈值的元素置零（类似 ReLU 但阈值可配置）"""
    
    def __init__(self, threshold=0.0):
        self.threshold = threshold
    
    def fit(self, X, y=None):
        # 无训练参数，直接返回 self
        return self
    
    def transform(self, X):
        return np.where(X >= self.threshold, X, 0.0).astype(X.dtype)
```

### 2. 编写 Shape Calculator

```python
from skl2onnx.common.data_types import FloatTensorType

def threshold_shape_calculator(operator):
    """推断输出形状：与输入形状相同"""
    # 输入类型和形状
    input_type = operator.inputs[0].type
    # 输出类型和形状与输入一致
    operator.outputs[0].type = type(input_type)(input_type.shape)
```

### 3. 编写 Converter

```python
def threshold_converter(scope, operator, container):
    """生成 ONNX 节点实现阈值逻辑"""
    # 获取输入输出名称
    input_name = operator.inputs[0].onnx_name
    output_name = operator.outputs[0].onnx_name
    
    # 获取阈值
    threshold = operator.raw_operator.threshold
    
    # 方法：使用 ONNX 算子组合实现 np.where(X >= threshold, X, 0)
    # 1. 创建阈值常量
    threshold_name = scope.get_unique_variable_name('threshold')
    container.add_initializer(
        threshold_name,
        onnx_proto.TensorProto.FLOAT,
        [1],
        np.array([threshold], dtype=np.float32)
    )
    
    # 2. 创建零常量
    zero_name = scope.get_unique_variable_name('zero')
    container.add_initializer(
        zero_name,
        onnx_proto.TensorProto.FLOAT,
        [1],
        np.array([0.0], dtype=np.float32)
    )
    
    # 3. X >= threshold → Greater
    greater_name = scope.get_unique_variable_name('greater')
    container.add_node(
        'Greater',
        [input_name, threshold_name],
        greater_name,
        name=scope.get_unique_operator_name('Greater')
    )
    
    # 4. Where(greater, X, 0)
    container.add_node(
        'Where',
        [greater_name, input_name, zero_name],
        output_name,
        name=scope.get_unique_operator_name('Where')
    )
```

需要导入 onnx proto：

```python
from onnx import TensorProto as onnx_proto
```

### 4. 注册转换器

```python
from skl2onnx import update_registered_converter

update_registered_converter(
    ThresholdApplier,                  # sklearn 类
    'SklearnThresholdApplier',         # 别名
    threshold_shape_calculator,        # shape calculator
    threshold_converter,               # converter
)
```

### 5. 使用自定义转换器

```python
from skl2onnx import convert_sklearn, to_onnx
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as rt

# 训练（fit 无实际操作）
model = ThresholdApplier(threshold=0.5)
model.fit(np.array([[1.0, -0.5], [0.3, 2.0]], dtype=np.float32))

# 转换
initial_types = [('input', FloatTensorType([None, 2]))]
onnx_model = convert_sklearn(model, initial_types=initial_types, target_opset=15)

# 推理验证
sess = rt.InferenceSession(onnx_model.SerializeToString(),
                            providers=['CPUExecutionProvider'])
X_test = np.array([[1.0, -0.5, 0.3, 2.0]], dtype=np.float32).reshape(-1, 2)
sklearn_out = model.transform(X_test)
onnx_out = sess.run(None, {'input': X_test})[0]

print("sklearn output:\n", sklearn_out)
print("ONNX output:\n", onnx_out)
# 两者应该一致：[[1.0, 0.0], [0.0, 2.0]]
```

## 模式二：OnnxOperatorMixin 模式（推荐）

### 1. 定义估计器，继承 OnnxOperatorMixin

```python
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from skl2onnx.algebra.onnx_operator_mixin import OnnxOperatorMixin
from skl2onnx.common.data_types import FloatTensorType

class ThresholdApplierV2(OnnxOperatorMixin, BaseEstimator, TransformerMixin):
    """使用 OnnxOperatorMixin 的版本"""
    
    # 必须：设置目标 opset
    op_version = 15
    
    def __init__(self, threshold=0.0):
        self.threshold = threshold
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.where(X >= self.threshold, X, 0.0).astype(X.dtype)
    
    # 必须：实现 to_onnx_operator 方法
    def to_onnx_operator(self, inputs=None, outputs=None,
                         target_opset=None, options=None):
        """用 OnnxOperator 代数 API 构建计算图"""
        from skl2onnx.algebra.onnx_ops import (
            OnnxGreater, OnnxWhere
        )
        
        if inputs is None:
            raise ValueError("inputs is required")
        
        # inputs 是变量名列表（字符串）或 OnnxOperator 列表
        X = inputs[0]
        
        # 创建阈值常量
        threshold = np.array([self.threshold], dtype=np.float32)
        zero = np.array([0.0], dtype=np.float32)
        
        # 使用代数 API 构建表达式（延迟求值 AST）
        # X >= threshold
        greater = OnnxGreater(X, threshold, op_version=target_opset or self.op_version)
        # Where(greater, X, 0)
        result = OnnxWhere(greater, X, zero,
                           op_version=target_opset or self.op_version,
                           output_names=outputs)
        
        return result
```

### 2. 使用（无需手动注册！）

```python
# 训练
model_v2 = ThresholdApplierV2(threshold=0.5)
model_v2.fit(np.array([[1.0, -0.5]], dtype=np.float32))

# 转换：OnnxOperatorMixin 通过 onnx_converter() 方法自动注册
# 优先级高于全局注册池
onnx_model_v2 = convert_sklearn(
    model_v2,
    initial_types=[('input', FloatTensorType([None, 2]))],
    target_opset=15
)

# 或直接用 to_onnx() 快捷方法（Minin 自带）
onnx_model_v2 = model_v2.to_onnx(
    X=np.array([[1.0, -0.5]], dtype=np.float32),  # 用于推断 initial_types
    target_opset=15
)

# 验证
sess2 = rt.InferenceSession(onnx_model_v2.SerializeToString(),
                             providers=['CPUExecutionProvider'])
X_test = np.array([[1.0, -0.5], [0.3, 2.0]], dtype=np.float32)
onnx_out_v2 = sess2.run(None, {'input': X_test})[0]
print("ONNX (Mixin) output:\n", onnx_out_v2)
# [[1.0, 0.0], [0.0, 2.0]]
```

## 更简洁的代数 API 写法

使用 numpy 数组作为输入时，OnnxOperator 会自动将其转为 initializer，代码可以更紧凑：

```python
class ThresholdApplierV3(OnnxOperatorMixin, BaseEstimator, TransformerMixin):
    op_version = 15
    
    def __init__(self, threshold=0.0):
        self.threshold = threshold
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.where(X >= self.threshold, X, 0.0).astype(X.dtype)
    
    def to_onnx_operator(self, inputs=None, outputs=None,
                         target_opset=None, options=None):
        from skl2onnx.algebra.onnx_ops import OnnxGreater, OnnxWhere
        
        X = inputs[0]
        op = target_opset or self.op_version
        
        # numpy 数组自动转为 initializer，不需要手动 add_initializer
        thresh = np.array([self.threshold], dtype=np.float32)
        
        return OnnxWhere(
            OnnxGreater(X, thresh, op_version=op),
            X,
            np.array([0.0], dtype=np.float32),
            op_version=op,
            output_names=outputs
        )
```

## 在 Pipeline 中使用自定义转换器

两种方式定义的自定义转换器都可以无缝嵌入 Pipeline：

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 方式一的转换器需要先 update_registered_converter 注册
# update_registered_converter(ThresholdApplier, 'SklearnThresholdApplier', ...)

# 方式二的转换器（OnnxOperatorMixin）直接使用，无需注册
pipe = Pipeline([
    ('thresh', ThresholdApplierV2(threshold=0.0)),  # 自定义转换器
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression(max_iter=200))
])

# 训练
from sklearn.datasets import load_iris
iris = load_iris()
pipe.fit(iris.data.astype(np.float32), iris.target)

# 转换整个 Pipeline
onnx_pipe = to_onnx(pipe, iris.data[:1].astype(np.float32),
                     target_opset=15,
                     options={'zipmap': False})

# 验证
sess_pipe = rt.InferenceSession(onnx_pipe.SerializeToString(),
                                 providers=['CPUExecutionProvider'])
onnx_pred = sess_pipe.run(None, {'X': iris.data[:5].astype(np.float32)})[0]
sklearn_pred = pipe.predict(iris.data[:5].astype(np.float32))
print("sklearn:", sklearn_pred)
print("ONNX:", onnx_pred.flatten())
```

## 两种模式对比

| 对比维度 | 传统三件套 | OnnxOperatorMixin |
|---------|-----------|-------------------|
| 代码量 | 需要 3 个函数（parser/shape/converter） | 只需 1 个方法（`to_onnx_operator`） |
| 注册方式 | 需要 `update_registered_converter()` 全局注册 | 继承即可，无需显式注册 |
| Shape 推断 | 手写 shape_calculator | 默认通过 `onnx.shape_inference` 自动推断 |
| Parser | 简单模型可省略，分类器需手写 | 默认从输出名推断 |
| 节点生成 | 裸调 `container.add_node()` | 用 OnnxOperator DSL 组合，更可读 |
| 常量处理 | 手动 `add_initializer()` | numpy 数组自动转换 |
| 灵活性 | 完全控制每个细节 | 受限于 onnx_ops 覆盖的算子 |
| 性能开销 | 无额外开销 | shape_inference 构建临时模型有开销 |
| 适用场景 | 需要精确控制、性能敏感、复杂逻辑 | 快速原型、简单算子组合、自定义估计器 |

## 手写 shape_calculator（Mixin 模式可选）

如果默认的 shape_inference 方式不适用（性能敏感或形状推断失败），可以在 Mixin 子类中显式覆盖 `onnx_shape_calculator`：

```python
class ThresholdApplierV4(OnnxOperatorMixin, BaseEstimator, TransformerMixin):
    op_version = 15
    
    def __init__(self, threshold=0.0):
        self.threshold = threshold
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.where(X >= self.threshold, X, 0.0).astype(X.dtype)
    
    def to_onnx_operator(self, inputs=None, outputs=None,
                         target_opset=None, options=None):
        from skl2onnx.algebra.onnx_ops import OnnxGreater, OnnxWhere
        X = inputs[0]
        op = target_opset or self.op_version
        thresh = np.array([self.threshold], dtype=np.float32)
        return OnnxWhere(
            OnnxGreater(X, thresh, op_version=op),
            X,
            np.array([0.0], dtype=np.float32),
            op_version=op,
            output_names=outputs
        )
    
    # 可选：覆盖默认 shape_calculator，避免 infer_shapes 开销
    def onnx_shape_calculator(self):
        def shape_calculator(operator):
            operator.outputs[0].type = FloatTensorType(operator.inputs[0].type.shape)
        return shape_calculator
```

## 常见错误与调试

### 错误1："Missing shape calculator"

原因：没有注册 shape_calculator 且模型没有 `onnx_shape_calculator()` 方法。
解决：使用 `update_registered_converter()` 注册，或继承 OnnxOperatorMixin。

### 错误2："Not all operators have been evaluated"

原因：数据流调度中某些 Operator 的 inputs 始终未被 fed（is_fed 不满足），通常是 parser 没有正确连接输入输出。
解决：检查 parser 逻辑，确保每个 Operator 的 inputs 都来自前序 Operator 的 outputs 或根输入。使用 `intermediate=True` 获取 Topology 对象检查 IR。

### 错误3：shape_inference 失败

原因：OnnxOperatorMixin 默认使用 onnx.shape_inference 推断形状，某些复杂算子组合可能推断失败。
解决：手写 `onnx_shape_calculator()` 返回显式的形状计算函数。

### 错误4：op_version 未设置

原因：OnnxOperatorMixin 子类忘记设置 `op_version` 属性。
解决：在类中设置 `op_version = 15`（或其他目标版本），或在 `to_onnx_operator` 中处理 `target_opset` 参数。

## 延伸阅读

- [OnnxOperator代数API：嵌入式DSL、类工厂、延迟求值、三件套自动生成](../concepts/04-onnx-operator-algebra.md) — 深入理解代数 API 的工作原理
- [转换器注册：别名→实现三级映射、shape_calculator配对](../concepts/03-converter-registration.md) — 注册体系详解
- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](../concepts/01-conversion-pipeline.md) — 理解自定义转换器在管线中的位置
