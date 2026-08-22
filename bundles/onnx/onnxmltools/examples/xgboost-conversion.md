---
type: example
title: "XGBoost模型转ONNX：从训练到推理验证"
description: "完整的XGBoost分类/回归模型转ONNX流程：训练XGBoost模型→使用convert_xgboost转换→initial_types声明→onnxruntime推理验证→预测一致性对比"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/02-conversion-pipeline.md, ../concepts/04-type-system.md, ../concepts/05-tree-models.md]
  references: [../references/convert-entry.md, ../references/registration-types.md]
---

# XGBoost模型转ONNX：从训练到推理验证

## 目标

将训练好的 XGBoost 分类/回归模型转换为 ONNX 格式，使用 onnxruntime 推理，并验证预测结果与原模型一致。

## 前置条件

```bash
pip install xgboost onnxmltools onnxruntime numpy scikit-learn
```

## 示例1：XGBoost 分类器转换

### 完整代码

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from onnxmltools.convert import convert_xgboost
from onnxmltools.utils import save_model
from onnxconverter_common.data_types import FloatTensorType
import onnxruntime as ort

# 1. 训练 XGBoost 分类器
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data.astype(np.float32), iris.target, test_size=0.2, random_state=42
)

model = XGBClassifier(
    n_estimators=10,
    max_depth=3,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# 2. 转换为 ONNX
# initial_types 声明输入：batch维度可变(None)，特征数4
initial_types = [("input", FloatTensorType([None, 4]))]
onnx_model = convert_xgboost(
    model,
    initial_types=initial_types,
    target_opset=15,
    doc_string="XGBoost Iris Classifier",
)

# 3. 保存模型
save_model(onnx_model, "xgboost_iris.onnx")

# 4. 使用 onnxruntime 推理
sess = ort.InferenceSession("xgboost_iris.onnx")
input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name
prob_name = sess.get_outputs()[1].name

# 5. 对比预测结果
test_sample = X_test[:5]
onnx_pred = sess.run([label_name, prob_name], {input_name: test_sample})
onnx_labels = onnx_pred[0]
onnx_probs = onnx_pred[1]

sklearn_probs = model.predict_proba(test_sample)
sklearn_labels = model.predict(test_sample)

print("XGBoost 预测标签:", sklearn_labels)
print("ONNX    预测标签:", onnx_labels)
print("标签一致:", np.array_equal(sklearn_labels, onnx_labels))
print("概率最大误差:", np.max(np.abs(sklearn_probs - onnx_probs)))
```

### 预期输出

```
XGBoost 预测标签: [1 0 2 1 1]
ONNX    预测标签: [1 0 2 1 1]
标签一致: True
概率最大误差: 1.19e-07  # float32精度误差范围内
```

## 示例2：XGBoost 回归器转换

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from onnxmltools.convert import convert_xgboost
from onnxconverter_common.data_types import FloatTensorType
import onnxruntime as ort

# 1. 训练回归模型
diabetes = load_diabetes()
X_train, X_test, y_train, y_test = train_test_split(
    diabetes.data.astype(np.float32), diabetes.target.astype(np.float32),
    test_size=0.2, random_state=42
)

model = XGBRegressor(n_estimators=20, max_depth=4, learning_rate=0.1)
model.fit(X_train, y_train)

# 2. 转换为 ONNX（10个特征）
initial_types = [("input", FloatTensorType([None, 10]))]
onnx_model = convert_xgboost(model, initial_types=initial_types, target_opset=15)

# 3. 推理验证
sess = ort.InferenceSession(onnx_model.SerializeToString())
input_name = sess.get_inputs()[0].name

test_sample = X_test[:5]
onnx_pred = sess.run(None, {input_name: test_sample})[0].ravel()
sklearn_pred = model.predict(test_sample)

print("XGBoost 预测值:", sklearn_pred)
print("ONNX    预测值:", onnx_pred)
print("最大误差:", np.max(np.abs(sklearn_pred - onnx_pred)))
```

## 示例3：XGBoost Booster 原生对象转换

onnxmltools 支持直接转换 XGBoost 原生 Booster 对象：

```python
import xgboost as xgb
from onnxmltools.convert import convert_xgboost
from onnxconverter_common.data_types import FloatTensorType

# 使用原生XGBoost API训练
dtrain = xgb.DMatrix(X_train, label=y_train)
params = {'max_depth': 3, 'eta': 0.1, 'objective': 'multi:softprob',
          'num_class': 3, 'eval_metric': 'mlogloss'}
booster = xgb.train(params, dtrain, num_boost_round=10)

# Booster对象会被自动包装为WrappedBooster
initial_types = [("input", FloatTensorType([None, 4]))]
onnx_model = convert_xgboost(booster, initial_types=initial_types, target_opset=15)
```

## 要点解析

### initial_types 为什么是必填？

XGBoost 模型本身不携带输入特征数的元信息（Booster只知道feature_names和num_features，但不记录数据类型）。`initial_types` 明确告诉转换器：
- 输入变量名（`"input"`）
- 数据类型（`FloatTensorType` = float32）
- 形状（`[None, 4]` = batch可变，4个特征）

如果不传 `initial_types`，会直接抛 `ValueError`。

### 输出结构说明

XGBoost 分类器转换后有两个输出：
1. **label**（输出0）：预测类别标签（Int64张量）
2. **probabilities**（输出1）：各类别概率（Float32张量，shape=[N, num_classes]）

回归器只有一个输出：
1. **variable**（输出0）：预测值（Float32张量，shape=[N, 1]）

### target_opset 选择

- 默认 opset=15（`DEFAULT_OPSET_NUMBER`）
- 如果 onnx 版本较旧，会自动取 `min(15, onnx_opset_version())`
- 建议使用 opset≥11 以获得更好的广播支持

### 常见问题

**Q：为什么概率值有微小误差？**
A：XGBoost 内部使用 double 精度计算，ONNX 推理使用 float32，差异通常在 1e-6 量级，属于正常精度损失。

**Q：XGBRFClassifier/XGBRFRegressor 支持吗？**
A：支持。它们注册到同一个 `convert_xgboost` 函数，内部通过 isinstance 分发。

**Q：可以自定义opset吗？**
A：可以，传入 `target_opset` 参数即可。但要确保 onnxruntime 版本支持对应 opset。

## 延伸阅读

- 了解转换流水线：[编译流水线五阶段](../concepts/02-conversion-pipeline.md)
- 了解树模型编码：[树模型转换范式](../concepts/05-tree-models.md)
- 了解类型声明：[数据类型系统](../concepts/04-type-system.md)
- LightGBM 高级选项：[LightGBM Pipeline转换实战](lightgbm-pipeline.md)
