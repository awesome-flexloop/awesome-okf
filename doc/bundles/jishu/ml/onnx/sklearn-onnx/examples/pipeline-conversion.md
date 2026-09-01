---
type: example
title: "Pipeline 完整转换：预处理+分类器串联"
description: "构建包含 StandardScaler + PCA + LogisticRegression 的 Pipeline，转换为 ONNX，验证预处理和分类在 ONNX 中完整执行"
sources:
  concepts: [../concepts/01-conversion-pipeline.md, ../concepts/05-pipeline-feature-union.md, ../concepts/02-topology-ir.md]
  references: [../references/convert-api.md, ../references/topology-ir.md]
---

# Pipeline 完整转换：预处理+分类器串联

## 目标

构建一个典型的 sklearn Pipeline（标准化→降维→分类），转换为单个 ONNX 模型，使得整个预处理+推理流程在 ONNX Runtime 中端到端执行，无需在部署侧复刻 Python 预处理逻辑。

## 完整代码

### 1. 构建并训练 Pipeline

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# 加载数据
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data.astype(np.float32),
    iris.target,
    test_size=0.2,
    random_state=42
)

# 构建 Pipeline：标准化 → PCA降维 → 逻辑回归分类
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=2)),
    ('clf', LogisticRegression(max_iter=200, multi_class='ovr'))
])

# 训练
pipe.fit(X_train, y_train)
print("Pipeline accuracy:", pipe.score(X_test, y_test))
# 示例输出: Pipeline accuracy: 0.9333...
```

### 2. 转换为 ONNX

```python
from skl2onnx import convert_sklearn, to_onnx
from skl2onnx.common.data_types import FloatTensorType

# 方法1：使用 convert_sklearn（手动声明 initial_types）
initial_types = [('input', FloatTensorType([None, 4]))]

onnx_model = convert_sklearn(
    pipe,
    name='IrisPipeline',
    initial_types=initial_types,
    target_opset=15,
    # options 可以按步骤设置不同选项
    options={
        id(pipe.named_steps['clf']): {'zipmap': False},  # 分类器输出张量
    }
)

# 方法2：使用 to_onnx（从训练数据自动推断 initial_types）
# onnx_model = to_onnx(pipe, X_train[:1].astype(np.float32), target_opset=15)
```

### 3. 检查模型结构

```python
import onnx

onnx.checker.check_model(onnx_model)
print("Model is valid!")

# 查看节点数量（每个 sklearn 步骤展开为多个 ONNX 节点）
print(f"Number of nodes: {len(onnx_model.graph.node)}")
print(f"Number of initializers: {len(onnx_model.graph.initializer)}")

# 列出所有节点的 op_type
print("\nNode types:")
for i, node in enumerate(onnx_model.graph.node):
    print(f"  {i}: {node.op_type} (domain: {node.domain or 'ai.onnx'})")
# 示例输出包含: Scaler → MatMul → Add → LinearClassifier (ai.onnx.ml) 等节点

# 查看输入输出
print("\nInputs:", [i.name for i in onnx_model.graph.input])
print("Outputs:", [o.name for o in onnx_model.graph.output])
# zipmap=False 时输出: ['label', 'probabilities']
# zipmap=True 时输出: ['output_label', 'output_probability']
```

### 4. 保存模型

```python
onnx.save(onnx_model, 'iris_pipeline.onnx')
```

### 5. ONNX Runtime 推理

```python
import onnxruntime as rt

sess = rt.InferenceSession('iris_pipeline.onnx', providers=['CPUExecutionProvider'])

input_name = sess.get_inputs()[0].name
output_names = [o.name for o in sess.get_outputs()]
print(f"Input: {input_name}")
print(f"Outputs: {output_names}")

# 注意：直接输入原始数据（4维），不需要手动做 scaler.transform 或 pca.transform
# 预处理已经嵌入到 ONNX 模型中！
results = sess.run(output_names, {input_name: X_test[:5]})

print("\nPredictions (first 5):")
for i in range(5):
    label = results[0][i][0]
    proba = results[1][i]
    print(f"  Sample {i}: label={label}, proba={proba}")
```

### 6. 一致性验证

```python
# sklearn 预测（原始数据 → scaler → pca → clf 全流程）
sklearn_labels = pipe.predict(X_test)
sklearn_probas = pipe.predict_proba(X_test)

# ONNX 预测（原始数据 → ONNX模型内全流程）
onnx_labels = sess.run([output_names[0]], {input_name: X_test})[0].flatten()
onnx_probas = sess.run([output_names[1]], {input_name: X_test})[0]

# label 一致性
label_match = np.mean(sklearn_labels == onnx_labels)
print(f"Label match: {label_match:.4f}")

# probability 一致性
proba_diff = np.max(np.abs(sklearn_probas - onnx_probas))
print(f"Max probability difference: {proba_diff:.8f}")
# 期望输出: Max probability difference: 非常小（float32 精度内）
```

## 含 ColumnTransformer 的复杂 Pipeline

### 构建异构特征 Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import pandas as pd

# 模拟异构数据：数值列 + 分类列
X = pd.DataFrame({
    'age': [25.0, 30.0, 35.0, 40.0, 28.0] * 30,
    'income': [50000.0, 60000.0, 70000.0, 80000.0, 55000.0] * 30,
    'gender': ['M', 'F', 'M', 'F', 'M'] * 30,
})
y = np.array([0, 1, 1, 0, 0] * 30, dtype=np.int64)

# ColumnTransformer：不同列应用不同转换器
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), ['age', 'income']),
    ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), ['gender']),
])

# 完整 Pipeline
pipe_ct = Pipeline([
    ('preprocess', preprocessor),
    ('clf', LogisticRegression(max_iter=200))
])

pipe_ct.fit(X, y)
```

### 转换含 DataFrame 输入的 Pipeline

```python
from skl2onnx.common.data_types import FloatTensorType, StringTensorType

# DataFrame 多输入：每列一个输入
initial_types_ct = [
    ('age', FloatTensorType([None, 1])),
    ('income', FloatTensorType([None, 1])),
    ('gender', StringTensorType([None, 1])),
]

onnx_model_ct = convert_sklearn(
    pipe_ct,
    initial_types=initial_types_ct,
    target_opset=15,
    options={'zipmap': False}
)

onnx.save(onnx_model_ct, 'hetero_pipeline.onnx')
```

### 推理 DataFrame 输入的模型

```python
sess_ct = rt.InferenceSession('hetero_pipeline.onnx',
                               providers=['CPUExecutionProvider'])

# 每列单独构造输入
input_feed = {
    'age': X[['age']].values.astype(np.float32),
    'income': X[['income']].values.astype(np.float32),
    'gender': X[['gender']].values,  # StringTensorType 直接传 numpy str 数组
}

results_ct = sess_ct.run(None, input_feed)
print("Heterogeneous pipeline predictions shape:", results_ct[1].shape)
# 示例: (150, 2) — 150 样本，2 类概率
```

## 使用 to_onnx 简化流程

对于快速实验，可以使用 `to_onnx()` 自动推断 `initial_types`：

```python
# 从 numpy 数据自动推断
onnx_model = to_onnx(pipe, X_train[:1].astype(np.float32),
                     target_opset=15,
                     options={'zipmap': False})

# 从 DataFrame 自动推断
onnx_model_ct = to_onnx(pipe_ct, X[:1],  # 传第一行数据即可
                         target_opset=15,
                         options={'zipmap': False})
```

## intermediate=True 调试模式

当转换出错时，可以使用 `intermediate=True` 获取 Topology 对象，检查 IR 结构：

```python
onnx_model, topology = convert_sklearn(
    pipe,
    initial_types=initial_types,
    target_opset=15,
    intermediate=True  # 返回 (onnx_model, topology)
)

# 检查拓扑中的算子数量
print(f"Number of operators in topology: {len(topology)}")

# 遍历所有算子
for op in topology:
    print(f"  {op.type}: {len(op.inputs)} inputs → {len(op.outputs)} outputs")
# 输出包含:
#   SklearnScaler: 1 inputs → 1 outputs
#   SklearnPCA: 1 inputs → 1 outputs
#   SklearnLinearClassifier: 1 inputs → 2 outputs
```

## 要点解析

### Pipeline 转换的核心优势

将预处理和模型一起转换为 ONNX 的关键优势是**部署一致性**：
- 不需要在部署侧（C++/Java/Go/浏览器）重新实现 StandardScaler、PCA、OneHotEncoder 等预处理逻辑
- 避免 Python 预处理和部署侧预处理之间的数值差异
- 端到端的版本控制：模型和预处理代码在同一个 .onnx 文件中

### 中间步骤自动关闭 zipmap

Pipeline 中非最后一步的 classifier（如果有）会自动设置 `zipmap: False`，避免中间步骤输出字典序列破坏后续张量计算。只有最后一步的 classifier 保留 zipmap 设置。

### options 的按实例设置

`options` 字典可以按 `id(step)` 为 Pipeline 中不同步骤设置不同选项：

```python
options = {
    id(pipe.named_steps['clf']): {'zipmap': False, 'raw_scores': True},
    # 其他步骤使用默认选项
}
```

### ColumnTransformer 输入注意事项

ColumnTransformer 转换后的 ONNX 模型，输入名对应 DataFrame 列名（或输入名），数值列对应 FloatTensorType，字符串列对应 StringTensorType。推理时需要按名称分别传入每列的数据。

## 延伸阅读

- 了解 Pipeline/FeatureUnion/ColumnTransformer 的解析机制：见 [Pipeline/FeatureUnion/ColumnTransformer处理](../concepts/05-pipeline-feature-union.md)
- 学习分类器转换基础：见 [分类器转ONNX完整示例](classifier-conversion.md)
- 理解 Topology IR 调试：见 [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](../concepts/02-topology-ir.md)
