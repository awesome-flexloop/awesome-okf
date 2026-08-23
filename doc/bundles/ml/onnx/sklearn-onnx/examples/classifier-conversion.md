---
type: example
title: "分类器转 ONNX：LogisticRegression 完整示例"
description: "训练一个 LogisticRegression 分类器，通过 convert_sklearn 转换为 ONNX，保存、加载、推理验证的完整流程"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/01-conversion-pipeline.md, ../concepts/05-pipeline-feature-union.md]
  references: [../references/convert-api.md, ../references/topology-ir.md]
---

# 分类器转 ONNX：LogisticRegression 完整示例

## 目标

训练一个 scikit-learn `LogisticRegression` 分类器（Iris 数据集），使用 `convert_sklearn` 转换为 ONNX 模型，保存到文件，加载后用 ONNX Runtime 推理，并与 sklearn 原始预测结果对比验证。

## 环境准备

```python
# 安装依赖
# pip install scikit-learn skl2onnx onnx onnxruntime numpy
```

## 完整代码

### 1. 训练 sklearn 模型

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# 加载数据
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data.astype(np.float32),  # ONNX 通常使用 float32
    iris.target,
    test_size=0.2,
    random_state=42
)

# 训练模型
clf = LogisticRegression(max_iter=200, multi_class='ovr')
clf.fit(X_train, y_train)

# 验证 sklearn 预测
print("sklearn accuracy:", clf.score(X_test, y_test))
# 示例输出: sklearn accuracy: 1.0
```

### 2. 转换为 ONNX 模型

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# 声明初始类型：输入名为 "input"，shape=[batch_size, 4]
# None 表示 batch 维度动态
initial_types = [('input', FloatTensorType([None, 4]))]

# 转换
onnx_model = convert_sklearn(
    clf,                          # sklearn 模型
    name='LogisticRegressionIris', # 模型名称（可选）
    initial_types=initial_types,   # 输入类型声明（必填）
    target_opset=15,               # 目标 opset 版本
    # options={'zipmap': False},   # 可选：关闭 ZipMap，输出原始张量
)
```

### 3. 检查 ONNX 模型

```python
import onnx

# 检查模型有效性
onnx.checker.check_model(onnx_model)
print("ONNX model is valid!")

# 查看模型信息
print("IR version:", onnx_model.ir_version)
print("Producer:", onnx_model.producer_name, onnx_model.producer_version)
print("Domain:", onnx_model.domain)
print("Opset imports:", [(opset.domain, opset.version) for opset in onnx_model.opset_import])
# 示例输出:
# IR version: 8
# Producer: skl2onnx 1.21.0
# Domain: ai.onnx
# Opset imports: [('', 15), ('ai.onnx.ml', 1)]

# 查看输入输出
print("\nInputs:")
for inp in onnx_model.graph.input:
    print(f"  {inp.name}: {inp.type}")

print("\nOutputs:")
for out in onnx_model.graph.output:
    print(f"  {out.name}: {out.type}")
# 示例输出（zipmap=True 默认）:
# Inputs:
#   input: float32[None,4]
# Outputs:
#   output_label: int64[None,1]
#   output_probability: seq(map(int64,float32))  ← ZipMap 输出字典序列
```

### 4. 保存和加载

```python
# 保存
onnx.save(onnx_model, 'logreg_iris.onnx')

# 加载
loaded_model = onnx.load('logreg_iris.onnx')
```

### 5. 用 ONNX Runtime 推理

```python
import onnxruntime as rt

# 创建推理会话
sess = rt.InferenceSession('logreg_iris.onnx', providers=['CPUExecutionProvider'])

# 获取输入输出名称
input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name
prob_name = sess.get_outputs()[1].name

print(f"Input: {input_name}")
print(f"Output label: {label_name}")
print(f"Output probability: {prob_name}")

# 推理
pred_onx = sess.run(
    [label_name, prob_name],
    {input_name: X_test[:5]}  # 取前5个样本测试
)

print("\nONNX predictions (first 5):")
for i in range(5):
    label = pred_onx[0][i][0]  # label 是 [[0], [1], ...] 格式
    proba = pred_onx[1][i]     # proba 是 [{0: p0, 1: p1, 2: p2}, ...] 字典列表
    print(f"  Sample {i}: label={label}, probabilities={proba}")
```

### 6. 验证一致性

```python
# 对比 sklearn 和 ONNX 的预测结果
sklearn_labels = clf.predict(X_test)
sklearn_probas = clf.predict_proba(X_test)

onnx_labels = sess.run([label_name], {input_name: X_test})[0].flatten()

# label 一致性
label_match = np.mean(sklearn_labels == onnx_labels)
print(f"Label match: {label_match:.4f}")
# 期望输出: Label match: 1.0000

# probability 一致性（需要关闭 zipmap 才能直接对比张量）
# 如果 zipmap=True，onnx 输出是字典序列，需要手动提取
onnx_prob_dicts = sess.run([prob_name], {input_name: X_test})[0]
onnx_probas = np.array([[d[c] for c in range(3)] for d in onnx_prob_dicts])

proba_diff = np.max(np.abs(sklearn_probas - onnx_probas))
print(f"Max probability difference: {proba_diff:.8f}")
# 期望输出: Max probability difference: 0.00000... (数值精度内一致)
```

### 7. 使用 zipmap=False 输出原始张量

如果不想输出字典序列，关闭 zipmap：

```python
onnx_model_nozip = convert_sklearn(
    clf,
    initial_types=initial_types,
    target_opset=15,
    options={'zipmap': False}  # 关闭 ZipMap
)

# 保存后用 onnxruntime 推理，输出直接是张量
sess2 = rt.InferenceSession(onnx_model_nozip.SerializeToString(),
                            providers=['CPUExecutionProvider'])
outputs2 = sess2.run(None, {'input': X_test[:5]})
labels_nozip = outputs2[0]   # int64 tensor
probas_nozip = outputs2[1]   # float32 tensor [None, 3]

print("Labels shape:", labels_nozip.shape)   # (5, 1)
print("Probas shape:", probas_nozip.shape)   # (5, 3)
print("Probas (first sample):", probas_nozip[0])
```

## 要点解析

### initial_types 为什么必填？

ONNX 模型需要在计算图中声明输入类型和形状。sklearn 模型本身不知道输入的 shape 和 dtype（`fit()` 时 X 可以是 numpy 数组、DataFrame、list 等），因此必须显式声明。

### FloatTensorType vs DoubleTensorType

sklearn 默认使用 float64（double），但 ONNX 部署通常使用 float32 以获得更好的性能和兼容性。如果训练时使用 float64 数据，转换时声明 `FloatTensorType` 会自动在模型中插入 Cast 节点将输入从 float32 转为 float64（但更推荐训练时就使用 float32）。

### zipmap 选项的选择

| 场景 | 推荐 zipmap |
|------|-------------|
| 与 ONNX ML 工具链集成、需要类名到概率的映射 | `True`（默认） |
| Pipeline 中间步骤 | `False`（已自动处理） |
| 需要张量输入的后续处理 | `False` |
| 某些推理引擎不支持 Sequence(Map) | `"columns"` 或 `False` |

### target_opset 的选择

- 不指定时使用 `get_latest_tested_opset_version()`（skl2onnx 1.21.0 默认测试到的版本）
- 如果部署环境使用较旧的 onnxruntime，可能需要指定较低的 opset
- opset 15 是较常用的折中选择（支持大多数算子且 onnxruntime 1.10+ 均支持）

## 延伸阅读

- 了解转换管线内部：见 [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](../concepts/01-conversion-pipeline.md)
- 学习 Pipeline 转换：见 [Pipeline 完整转换](pipeline-conversion.md)
- 开发自定义转换器：见 [自定义转换器开发](custom-converter.md)
