---
title: 实验跟踪与可视化
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/trainer-system
---

# 实验跟踪与可视化

Torch-RecHub 提供统一的实验日志接口和模型结构可视化能力，并内置丰富的推荐系统评估指标。

## 实验跟踪

### BaseLogger 接口

所有 logger 继承 `BaseLogger`，实现三个方法：

```python
from torch_rechub.basic.tracking import BaseLogger

class MyLogger(BaseLogger):
    def log_metrics(self, metrics, step=None): ...
    def log_hyperparams(self, params): ...
    def finish(self): ...
```

通过 Trainer 的 `model_logger` 参数传入，可为单个 logger 或列表：

```python
trainer = CTRTrainer(model, model_logger=wandb_logger)
# 或多个 logger
trainer = CTRTrainer(model, model_logger=[wandb_logger, tb_logger])
```

Trainer 在训练开始时记录超参数，每个 epoch 记录训练损失、学习率、验证指标，训练结束时调用 finish()。

### WandbLogger

Weights & Biases 跟踪：

```python
from torch_rechub.basic.tracking import WandbLogger

logger = WandbLogger(
    project="recommendation",
    name="deepfm_criteo",
    config={"lr": 1e-3, "epochs": 10},
    tags=["ctr", "deepfm"],
)
```

需安装 `wandb`（`pip install torch-rechub[tracking]`）。

### SwanLabLogger

SwanLab 跟踪：

```python
from torch_rechub.basic.tracking import SwanLabLogger

logger = SwanLabLogger(
    project="recommendation",
    experiment_name="dssm_ml1m",
    config={"mode": 0},
)
```

### TensorBoardXLogger

TensorBoard 跟踪：

```python
from torch_rechub.basic.tracking import TensorBoardXLogger

logger = TensorBoardXLogger(log_dir="./runs/exp1", comment="deepfm")
```

超参数以文本形式写入，数值指标以 scalar 写入。

## 模型可视化

### Trainer 接口

每个 Trainer 提供 `visualization()` 方法：

```python
graph = trainer.visualization(
    depth=4,
    show_shapes=True,
    expand_nested=True,
    save_path="model_arch.png",
    dpi=300,
)
```

参数：
- `depth`：可视化深度，-1 显示全部层（默认3）
- `show_shapes`：显示张量形状
- `expand_nested`：展开嵌套模块
- `save_path`：保存路径（.pdf/.svg/.png），None 时在 Jupyter 内联显示或用系统查看器打开
- `dpi`：输出分辨率（默认300，适合论文）
- `batch_size`/`seq_length`：自动生成 dummy input 的参数

### 独立函数

```python
from torch_rechub.utils.visualization import visualize_model, display_graph

graph = visualize_model(model, depth=4, save_path="arch.pdf")
display_graph(graph)  # Jupyter 中展示
```

底层基于 torchview.draw_graph，自动通过 `extract_feature_info` 提取模型特征并生成 dummy input。dict 输入会被包装为 tuple 以避免 torchview 将 dict 解包为 kwargs。

需安装 `torchview` 和系统 `graphviz`（`pip install torch-rechub[visualization]`）。

## 评估指标

### 准确率指标

`basic/metric.py` 提供：

- `auc_score(y_true, y_pred)`：AUC
- `gauc_score(y_true, y_pred, users, weights=None)`：按用户分组加权 AUC
- `log_loss(y_true, y_pred)`：对数损失

### Top-K 排序指标

```python
from torch_rechub.basic.metric import topk_metrics

results = topk_metrics(y_true, y_pred, topKs=(5, 10))
# results = {
#   'NDCG': ['NDCG@5: 0.xxxx', 'NDCG@10: 0.xxxx'],
#   'MRR': [...], 'Recall': [...], 'Hit': [...], 'Precision': [...]
# }
```

输入格式：`y_true` 和 `y_pred` 为 `{user_id: [item_id_list]}` 字典。便捷函数：`ndcg_score`、`hit_score`、`mrr_score`、`recall_score`、`precision_score`。

### 超越准确率指标

- `diversity_score(y_pred, item_embeddings, topKs)`：Intra-List Diversity，推荐列表内物品间平均余弦距离
- `coverage_score(y_pred, all_items, topKs)`：目录覆盖率，被推荐物品占全量物品的比例
- `novelty_score(y_pred, item_popularity, topKs)`：平均自信息 `-log2(popularity)`，衡量推荐长尾程度

### 任务类型默认指标

`get_loss_func` 和 `get_metric_func` 按任务类型返回默认函数：
- classification：BCELoss + roc_auc_score
- regression：MSELoss + mean_squared_error
