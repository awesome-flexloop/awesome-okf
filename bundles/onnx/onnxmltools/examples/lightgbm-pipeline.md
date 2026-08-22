---
type: example
title: "LightGBM Pipeline转换实战：zipmap/split/without_onnx_ml选项"
description: "LightGBM模型转换完整实战：训练LightGBM分类器→convert_lightgbm转换→zipmap选项对比→split大数精度控制→without_onnx_ml纯ONNX转换→onnxruntime推理验证"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/02-conversion-pipeline.md, ../concepts/04-type-system.md, ../concepts/05-tree-models.md]
  references: [../references/convert-entry.md, ../references/registration-types.md]
---

# LightGBM Pipeline转换实战：zipmap/split/without_onnx_ml选项

## 目标

将训练好的 LightGBM 模型转换为 ONNX 格式，掌握 LightGBM 特有的三个参数（zipmap/split/without_onnx_ml）的使用方法，并验证预测一致性。

## 前置条件

```bash
pip install lightgbm onnxmltools onnxruntime numpy scikit-learn
# 可选（without_onnx_ml 需要）
pip install hummingbird-ml
```

## 示例1：基础分类器转换

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from onnxmltools.convert import convert_lightgbm
from onnxmltools.utils import save_model
from onnxconverter_common.data_types import FloatTensorType
import onnxruntime as ort

# 1. 训练模型
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data.astype(np.float32), data.target, test_size=0.2, random_state=42
)

model = LGBMClassifier(n_estimators=50, max_depth=6, learning_rate=0.1, verbose=-1)
model.fit(X_train, y_train)

# 2. 转换为 ONNX（30个特征）
initial_types = [("input", FloatTensorType([None, 30]))]
onnx_model = convert_lightgbm(
    model,
    initial_types=initial_types,
    target_opset=15,
    zipmap=True,  # 默认True，输出概率字典
)

save_model(onnx_model, "lightgbm_breast_cancer.onnx")

# 3. 检查输出结构
for output in onnx_model.graph.output:
    print(f"输出: {output.name}, 类型: {output.type}")

# 4. 推理验证
sess = ort.InferenceSession("lightgbm_breast_cancer.onnx")
input_name = sess.get_inputs()[0].name

test_sample = X_test[:5]
onnx_outputs = sess.run(None, {input_name: test_sample})
# onnx_outputs[0]: label（类别标签）
# onnx_outputs[1]: probabilities（如果zipmap=True，这是字典序列）

lgbm_pred = model.predict(test_sample)
lgbm_proba = model.predict_proba(test_sample)

print("LightGBM 预测标签:", lgbm_pred)
print("ONNX    预测标签:", onnx_outputs[0])
```

## 示例2：zipmap选项对比

`zipmap` 参数控制概率输出的格式：

```python
# zipmap=True（默认）：输出ZipMap算子，概率为字典序列 {0: prob0, 1: prob1}
onnx_model_zipmap = convert_lightgbm(
    model, initial_types=initial_types, zipmap=True
)
# 输出: label(Int64[N]), probabilities(Map[N, {Int64→Float32}])
# ONNX Runtime输出: [array([0,1,...]), [ {0:0.95, 1:0.05}, {0:0.1, 1:0.9}, ... ]]

# zipmap=False：不输出ZipMap，概率直接为2D张量
onnx_model_tensor = convert_lightgbm(
    model, initial_types=initial_types, zipmap=False
)
# 输出: label(Int64[N]), probabilities(Float32[N, num_classes])
# ONNX Runtime输出: [array([0,1,...]), array([[0.95,0.05],[0.1,0.9],...], dtype=float32)]

# zipmap=False更适合程序化推理，避免字典解析开销
sess = ort.InferenceSession(onnx_model_tensor.SerializeToString())
results = sess.run(None, {input_name: test_sample})
labels = results[0]
probs = results[1]  # 直接是numpy数组，shape=(5,2)
print("概率矩阵shape:", probs.shape)
print("概率矩阵:\n", probs)
```

### zipmap=False 的内部实现

当 `zipmap=False` 时，转换器不生成 ZipMap 算子，而是在概率张量后加一个 `Mul(1.0)` 恒等算子（这是为了保持输出变量结构一致）。在推理时直接得到 numpy 数组，比字典序列更高效。

## 示例3：split精度控制

当树数量很多时（如1000棵树），float32精度累积可能导致预测偏差。`split` 参数将大树林拆分为多段，每段用float64累加：

```python
from lightgbm import LGBMRegressor
import numpy as np

# 训练一个大树林（500棵树）
np.random.seed(42)
X = np.random.randn(1000, 10).astype(np.float32)
y = np.random.randn(1000).astype(np.float32)
model = LGBMRegressor(n_estimators=500, max_depth=8, learning_rate=0.05, verbose=-1)
model.fit(X, y)

initial_types = [("input", FloatTensorType([None, 10]))]

# 不使用split（默认）：所有树在一个TreeEnsemble中
onnx_model_no_split = convert_lightgbm(
    model, initial_types=initial_types, zipmap=False
)

# 使用split=100：每100棵树一组，用double累加
onnx_model_split = convert_lightgbm(
    model, initial_types=initial_types, zipmap=False, split=100
)

# 对比精度
sess_no_split = ort.InferenceSession(onnx_model_no_split.SerializeToString())
sess_split = ort.InferenceSession(onnx_model_split.SerializeToString())

test_sample = X[:100]
pred_lgbm = model.predict(test_sample)
pred_no_split = sess_no_split.run(None, {"input": test_sample})[0].ravel()
pred_split = sess_split.run(None, {"input": test_sample})[0].ravel()

print("无split 最大误差:", np.max(np.abs(pred_lgbm - pred_no_split)))
print("split=100 最大误差:", np.max(np.abs(pred_lgbm - pred_split)))
```

### split的内部实现

```
split=100时生成的ONNX图结构：

input → TreeEnsembleRegressor(tree_0_99) → Cast(double) ─┐
      → TreeEnsembleRegressor(tree_100_199) → Cast(double) ┼─ Sum(double) → Cast(float) → output
      → TreeEnsembleRegressor(tree_200_299) → Cast(double) ┤
      → TreeEnsembleRegressor(tree_300_399) → Cast(double) ┤
      → TreeEnsembleRegressor(tree_400_499) → Cast(double) ─┘
```

- 每N棵树为一组TreeEnsembleRegressor
- 每组输出cast到float64
- Sum(double)累加所有组
- 最终cast回float32

这减少了float32加法中的精度损失（float32有效精度约7位十进制数）。

## 示例4：without_onnx_ml — Hummingbird纯ONNX转换

某些推理引擎（如移动端推理框架）不支持ONNX-ML域算子（TreeEnsemble/ZipMap等），此时可以使用 `without_onnx_ml=True` 将模型转换为纯ONNX算子：

```python
# 需要安装 hummingbird-ml
# pip install hummingbird-ml

onnx_model_pure = convert_lightgbm(
    model,
    initial_types=initial_types,
    zipmap=False,
    without_onnx_ml=True,  # 启用Hummingbird后处理
)

# 检查是否还有ONNX-ML域算子
ml_ops = [node for node in onnx_model_pure.graph.node 
          if node.domain == "ai.onnx.ml"]
print(f"ONNX-ML域算子数量: {len(ml_ops)}")  # 应该为0
```

启用后，Hummingbird将TreeEnsemble等ONNX-ML算子转换为纯ONNX核心算子（If/Gather/MatMul/Mul等）的组合，兼容性更好但模型体积可能更大。

## 示例5：排序任务（LGBMRanker）

```python
import numpy as np
from lightgbm import LGBMRanker
from onnxmltools.convert import convert_lightgbm
from onnxconverter_common.data_types import FloatTensorType
import onnxruntime as ort

# 构造排序数据（简化示例）
np.random.seed(42)
n_samples, n_features = 200, 10
X = np.random.randn(n_samples, n_features).astype(np.float32)
y = np.random.randint(0, 5, size=n_samples).astype(np.float32)
group = np.array([50]*4, dtype=np.int64)  # 4组，每组50个样本

model = LGBMRanker(n_estimators=20, max_depth=4, verbose=-1)
model.fit(X, y, group=group)

initial_types = [("input", FloatTensorType([None, 10]))]
onnx_model = convert_lightgbm(model, initial_types=initial_types, zipmap=False)

sess = ort.InferenceSession(onnx_model.SerializeToString())
pred_onnx = sess.run(None, {"input": X[:10]})[0].ravel()
pred_lgbm = model.predict(X[:10])

print("排序得分最大误差:", np.max(np.abs(pred_lgbm - pred_onnx)))
```

LGBMClassifier、LGBMRegressor、LGBMRanker 都注册到同一个 `convert_lightgbm` 函数，内部根据模型类型自动分发。

## 要点解析

### LightGBM三个特有参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `zipmap` | `True` | True→输出ZipMap概率字典；False→输出概率张量 |
| `split` | `None` | None→所有树一个算子；整数N→每N棵树一组，double累加 |
| `without_onnx_ml` | `False` | True→调用Hummingbird转为纯ONNX算子 |

### Booster自动包装

传入原生 `lightgbm.Booster` 对象时会被自动包装为 `WrappedBooster`，无需手动处理：

```python
# 使用原生API训练
import lightgbm as lgb
dtrain = lgb.Dataset(X_train, label=y_train)
booster = lgb.train({'objective': 'binary', 'verbose': -1}, dtrain, num_boost_round=50)

# 直接传入Booster，自动包装
onnx_model = convert_lightgbm(booster, initial_types=initial_types)
```

### initial_types必填

LightGBM在 `initial_types is None` 时直接抛 ValueError，必须显式声明。特征数必须与训练数据一致。

## 延伸阅读

- 树模型编码详解：[树模型转换范式](../concepts/05-tree-models.md)
- 转换流水线原理：[编译流水线五阶段](../concepts/02-conversion-pipeline.md)
- XGBoost转换示例：[XGBoost模型转ONNX](xgboost-conversion.md)
