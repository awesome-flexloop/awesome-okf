---
title: Trainer 系统
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/multi-task-learning
  - /datawhale/torch-rechub/concepts/onnx-export
  - /datawhale/torch-rechub/concepts/tracking-and-visualization
---

# Trainer 系统

Torch-RecHub 按任务范式提供四类 Trainer，每个 Trainer 封装完整的训练循环、验证、早停、模型保存，并统一提供 ONNX 导出和可视化方法。

## CTRTrainer

单任务 CTR 预估训练器，适用于 DeepFM、DIN、DCN 等排序模型。

```python
from torch_rechub.trainers import CTRTrainer

trainer = CTRTrainer(
    model=model,
    optimizer_fn=torch.optim.Adam,
    optimizer_params={"lr": 1e-3, "weight_decay": 1e-5},
    n_epoch=10,
    earlystop_patience=5,
    device="cuda:0",
    model_path="./checkpoints/",
    loss_mode=True,
)
trainer.fit(train_dataloader, val_dataloader)
```

关键参数：
- `loss_mode=True`：模型 forward 只返回预测值，损失用 BCELoss
- `loss_mode=False`：模型 forward 返回 `(y_pred, other_loss)` 元组，附加损失会加到总损失
- `regularization_params`：配置 embedding_l1/l2、dense_l1/l2 正则系数
- `gpus=[0,1]`：多 GPU DataParallel 训练

默认损失：`torch.nn.BCELoss`；默认评估：`sklearn.metrics.roc_auc_score`。

## MatchTrainer

匹配/召回训练器，支持三种训练模式。

```python
from torch_rechub.trainers import MatchTrainer

trainer = MatchTrainer(
    model=dssm_model,
    mode=0,              # 0=point-wise, 1=pair-wise, 2=list-wise
    in_batch_neg=False,  # 批内负采样
    device="cuda:0",
)
```

三种模式：
- **mode=0 (point-wise)**：BCELoss（无批内负采样时）或 CrossEntropyLoss（批内负采样时），标签为 0/1
- **mode=1 (pair-wise)**：BPRLoss，模型需返回 `(pos_score, neg_score)`
- **mode=2 (list-wise)**：CrossEntropyLoss，softmax 多分类

批内负采样（in-batch negative sampling）：
```python
trainer = MatchTrainer(
    model=dssm_model,
    mode=0,
    in_batch_neg=True,
    in_batch_neg_ratio=4,
    hard_negative=False,
    sampler_seed=42,
)
```
要求模型实现 `user_tower(x)` 和 `item_tower(x)` 方法返回 2D 嵌入。通过 `inbatch_negative_sampling` 从 batch 内其他物品采样负例，`hard_negative=True` 时选择相似度最高的 top-k 作为困难负例。

推理嵌入：
```python
user_emb = trainer.inference_embedding(model, "user", user_loader, "./checkpoints/")
item_emb = trainer.inference_embedding(model, "item", item_loader, "./checkpoints/")
```

## MTLTrainer

多任务学习训练器，适用于 MMOE、PLE、SharedBottom、ESMM、AITM。

```python
from torch_rechub.trainers import MTLTrainer

trainer = MTLTrainer(
    model=mmoe_model,
    task_types=["classification", "regression"],
    n_epoch=20,
    device="cuda:0",
)
trainer.fit(train_dataloader, val_dataloader)
```

特点：
- `task_types` 列表指定每个任务是 "classification" 还是 "regression"
- 自动按任务类型选择损失（BCELoss/MSELoss）和指标（roc_auc_score/mean_squared_error）
- `earlystop_taskid` 指定以哪个任务的指标做早停（默认第0个任务）
- 输出形状 `(B, n_task)`，验证时按任务分别计算指标

自适应损失加权：
```python
# Uncertainty Weighting (Kendall et al.)
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "uwl"})

# MetaBalance 梯度平衡
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "metabalance"})

# GradNorm
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "gradnorm", "alpha": 0.16})
```

ESMM 特殊处理：当模型是 ESMM 实例时，只计算后两个任务（ctr、ctcvr）的损失，跳过第一个 cvr 任务。

## SeqTrainer

序列生成模型训练器，适用于 HSTU 等生成式推荐模型。

```python
from torch_rechub.trainers import SeqTrainer

trainer = SeqTrainer(
    model=hstu_model,
    n_epoch=30,
    device="cuda:0",
    loss_type="cross_entropy",  # 或 "nce"
)
trainer.fit(train_loader, val_loader)
```

数据批次为四元组：`(seq_tokens, seq_positions, seq_time_diffs, targets)`。

损失模式：
- `cross_entropy`（默认）：自回归下一 token 预测，忽略 padding 位
- `nce`：NCE 损失，需配置 temperature 和 ignore_index

`_compute_next_token_loss` 实现左填充感知的下一 token 预测：位置 i 预测位置 i+1，最后位置预测 held-out target，PAD→item 的转移被掩码。

## 共享训练机制

### EarlyStopper

```python
from torch_rechub.basic.callback import EarlyStopper
stopper = EarlyStopper(patience=10)
```
验证指标超过历史最佳时保存权重副本，连续 patience 轮无提升则停止训练。

### RegularizationLoss

```python
from torch_rechub.basic.loss_func import RegularizationLoss
reg = RegularizationLoss(embedding_l1=0.0, embedding_l2=1e-5, dense_l1=0.0, dense_l2=1e-5)
```
自动区分 Embedding 参数和 dense 参数，跳过 BatchNorm/LayerNorm 等归一化层参数。

### 学习率调度

通过 `scheduler_fn` 和 `scheduler_params` 传入 PyTorch 调度器（如 StepLR），在每个 epoch 结束时 step。

### 多 GPU

`gpus=[0,1]` 时自动用 `nn.DataParallel` 包装模型；保存和导出时通过 `.module` 获取原始模型。

### 模型保存

- CTRTrainer/MatchTrainer/SeqTrainer 保存为 `model.pth`
- MTLTrainer 保存为 `model_{mode}_{seed}.pth`，支持多组实验
