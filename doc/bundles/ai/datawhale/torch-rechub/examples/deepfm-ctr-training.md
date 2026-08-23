---
title: DeepFM CTR 训练示例
type: example
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/data-pipeline
---

# DeepFM CTR 训练示例

本示例演示使用 torch-rechub 在 Criteo 风格数据集上训练 DeepFM CTR 预估模型的完整流程。

## 1. 定义特征

```python
import torch
from torch_rechub.basic.features import SparseFeature, DenseFeature

sparse_features = [
    SparseFeature("user_id", vocab_size=100000, embed_dim=16),
    SparseFeature("item_id", vocab_size=50000, embed_dim=16),
    SparseFeature("cate_id", vocab_size=1000, embed_dim=8),
]
dense_features = [
    DenseFeature("price"),
    DenseFeature("age"),
]
all_features = sparse_features + dense_features
```

## 2. 构造模型

```python
from torch_rechub.models.ranking import DeepFM

mlp_params = {"dims": [256, 128], "dropout": 0.2, "activation": "relu", "output_layer": True}

model = DeepFM(
    deep_features=all_features,
    fm_features=sparse_features,
    mlp_params=mlp_params,
)
```

DeepFM 由三部分组成：
- `LR`：一阶线性交互
- `FM`：二阶特征交互
- `MLP`：深度高阶交互

最终输出 `sigmoid(y_linear + y_fm + y_deep)`。

## 3. 准备数据

```python
import numpy as np
from torch_rechub.utils.data import DataGenerator, df_to_dict

# 假设 df 是预处理好的 DataFrame，包含特征列和 label 列
x = df_to_dict(df.drop(columns=["label"]))
y = df["label"].values

dg = DataGenerator(x, y)
train_dl, val_dl, test_dl = dg.generate_dataloader(
    split_ratio=(0.8, 0.1, 0.1),
    batch_size=256,
    num_workers=4,
)
```

## 4. 训练

```python
from torch_rechub.trainers import CTRTrainer

trainer = CTRTrainer(
    model=model,
    optimizer_fn=torch.optim.Adam,
    optimizer_params={"lr": 1e-3, "weight_decay": 1e-5},
    scheduler_fn=torch.optim.lr_scheduler.StepLR,
    scheduler_params={"step_size": 5, "gamma": 0.5},
    n_epoch=15,
    earlystop_patience=5,
    device="cuda:0",
    model_path="./checkpoints/deepfm/",
    regularization_params={"embedding_l2": 1e-5, "dense_l2": 1e-5},
)

trainer.fit(train_dl, val_dl)
```

训练过程中：
- 每个 epoch 输出训练损失和验证 AUC
- 验证 AUC 连续 5 轮无提升则早停
- 最佳模型权重保存到 `./checkpoints/deepfm/model.pth`

## 5. 预测

```python
preds = trainer.predict(model, test_dl)
```

## 6. 导出 ONNX

```python
trainer.export_onnx(
    "deepfm.onnx",
    opset_version=14,
    dynamic_batch=True,
    verbose=True,
)
```

## 7. 模型可视化

```python
trainer.visualization(depth=4, save_path="deepfm_arch.png", dpi=300)
```

## 关键 API 对照

| 步骤 | API | 所属模块 |
|------|-----|---------|
| 特征定义 | `SparseFeature` / `DenseFeature` | basic.features |
| 模型构造 | `DeepFM(deep_features, fm_features, mlp_params)` | models.ranking |
| 数据加载 | `DataGenerator(x, y).generate_dataloader(...)` | utils.data |
| 训练 | `CTRTrainer(...).fit(train, val)` | trainers |
| 导出 | `trainer.export_onnx(path)` | trainers（委托 ONNXExporter） |
| 可视化 | `trainer.visualization(...)` | trainers（委托 visualize_model） |
