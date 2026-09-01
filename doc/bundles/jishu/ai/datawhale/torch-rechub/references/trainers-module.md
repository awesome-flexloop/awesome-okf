---
title: Trainer 模块源码登记
type: reference
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/multi-task-learning
---

# Trainer 模块源码登记

登记 `torch_rechub/trainers/` 下所有 Trainer 类的源码位置和关键接口。

## CTRTrainer

- **文件**：`torch_rechub/trainers/ctr_trainer.py`
- **类**：`CTRTrainer(object)`
- **用途**：单任务 CTR 排序模型训练
- **默认损失**：`torch.nn.BCELoss`
- **默认评估**：`sklearn.metrics.roc_auc_score`
- **构造参数**：
  - `model`：nn.Module 模型
  - `optimizer_fn=torch.optim.Adam`
  - `optimizer_params={"lr": 1e-3, "weight_decay": 1e-5}`
  - `regularization_params={"embedding_l1":0, "embedding_l2":0, "dense_l1":0, "dense_l2":0}`
  - `scheduler_fn=None`、`scheduler_params=None`
  - `n_epoch=10`、`earlystop_patience=10`
  - `device="cpu"`、`gpus=[]`
  - `loss_mode=True`（True: 模型返回 pred；False: 返回 (pred, other_loss)）
  - `model_path="./"`、`model_logger=None`
- **公开方法**：
  - `fit(train_dataloader, val_dataloader=None)`
  - `train_one_epoch(data_loader, log_interval=10)`
  - `evaluate(model, data_loader)` → AUC
  - `predict(model, data_loader)` → 预测列表
  - `export_onnx(output_path, ...)`
  - `visualization(...)`

## MatchTrainer

- **文件**：`torch_rechub/trainers/match_trainer.py`
- **类**：`MatchTrainer(object)`
- **用途**：双塔召回/匹配模型训练
- **三种模式**：
  - mode=0：point-wise，BCELoss 或 CrossEntropyLoss（批内负采样时）
  - mode=1：pair-wise，BPRLoss
  - mode=2：list-wise，CrossEntropyLoss
- **批内负采样参数**：
  - `in_batch_neg=False`：启用批内负采样
  - `in_batch_neg_ratio=None`：每正例负例数
  - `hard_negative=False`：是否使用困难负例
  - `sampler_seed=None`：随机种子
- **公开方法**：
  - `fit(train_dataloader, val_dataloader=None)`
  - `evaluate(model, data_loader)` → AUC
  - `predict(model, data_loader)`
  - `inference_embedding(model, mode, data_loader, model_path)`：mode="user"/"item"，批量生成嵌入
  - `export_onnx(output_path, mode=None, ...)`：支持 mode="user"/"item" 分塔导出
  - `visualization(...)`

## MTLTrainer

- **文件**：`torch_rechub/trainers/mtl_trainer.py`
- **类**：`MTLTrainer(object)`
- **用途**：多任务学习模型训练（MMOE、PLE、SharedBottom、ESMM、AITM）
- **关键参数**：
  - `task_types`：列表，每项为 "classification" 或 "regression"
  - `adaptive_params`：自适应损失加权配置
    - `{"method": "uwl"}`：Uncertainty Weighting
    - `{"method": "metabalance"}`：MetaBalance 梯度平衡
    - `{"method": "gradnorm", "alpha": 0.16}`：GradNorm
  - `earlystop_taskid=0`：早停依据的任务 ID
- **公开方法**：
  - `fit(train_dataloader, val_dataloader, mode='base', seed=0)`：必须提供 val_dataloader
  - `evaluate(model, data_loader)` → 各任务分数列表
  - `predict(model, data_loader)`
  - `export_onnx(output_path, ...)`
  - `visualization(...)`
- **特殊处理**：ESMM 模型只计算 loss_list[1:]（跳过 cvr 任务）
- **模型保存**：`model_{mode}_{seed}.pth`

## SeqTrainer

- **文件**：`torch_rechub/trainers/seq_trainer.py`
- **类**：`SeqTrainer(object)`
- **用途**：序列生成模型（HSTU）训练
- **损失类型**：
  - `loss_type='cross_entropy'`（默认）：CrossEntropyLoss(ignore_index=0)
  - `loss_type='nce'`：NCELoss(temperature=0.1, ignore_index=0)
- **数据批次**：`(seq_tokens, seq_positions, seq_time_diffs, targets)`
- **公开方法**：
  - `fit(train_dataloader, val_dataloader=None)` → history dict
  - `evaluate(data_loader)` → (avg_loss, top1_accuracy)
  - `train_one_epoch(data_loader, log_interval=10)`
  - `export_onnx(output_path, batch_size=2, seq_length=50, vocab_size=None, ...)`
  - `visualization(seq_length=50, vocab_size=None, ...)`
- **关键内部方法**：
  - `_compute_next_token_loss(logits, seq_tokens, targets)`：自回归下一 token 损失，左填充感知

## RQVAE Trainer

- **文件**：`torch_rechub/trainers/rqvae_trainer.py`
- **类**：`Trainer(object)`（注意类名就是 Trainer）
- **用途**：RQVAE 语义 ID 生成模型训练
- **评估指标**：collision_rate（语义码碰撞率）
- **关键属性**：best_loss、best_collision_rate、best_loss_ckpt、best_collision_ckpt
- **公开方法**：
  - `fit(train_dataloader)`
  - `train_one_epoch(data_loader)` → (total_loss, total_recon_loss)
  - `evaluate(data_loader)` → collision_rate
  - `export_onnx(output_path, batch_size=2, ...)`：双输出（output + indices）
- **eval_step=50**：每50个 epoch 评估一次

## 共享依赖

- `EarlyStopper`（`basic/callback.py`）：所有 Trainer 的早停机制
- `RegularizationLoss`（`basic/loss_func.py`）：L1/L2 正则化
- `BaseLogger` 及实现（`basic/tracking.py`）：实验跟踪
- `ONNXExporter`（`utils/onnx_export.py`）：ONNX 导出
- `visualize_model`（`utils/visualization.py`）：模型可视化
