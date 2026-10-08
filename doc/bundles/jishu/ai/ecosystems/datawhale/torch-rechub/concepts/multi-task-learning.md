---
title: 多任务学习
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/trainer-system
---

# 多任务学习

Torch-RecHub 提供从共享底层到专家门控的多任务模型族系，以及三种自适应损失加权策略，由 `MTLTrainer` 统一训练。

## 模型族系

### SharedBottom

最简单的多任务架构：共享底层 MLP，每个任务有独立的塔 MLP。

```python
from torch_rechub.models.multi_task import SharedBottom

model = SharedBottom(
    features=features,
    task_types=["classification", "regression"],
    bottom_params={"dims": [256, 128]},
    tower_params_list=[{"dims": [64]}, {"dims": [64]}],
)
```

共享参数：embedding + bottom_mlp；任务参数：towers + predict_layers。

### MMOE (Multi-gate Mixture-of-Experts)

KDD'2018，每个任务有独立的门控网络，对多个共享专家进行加权组合：

```python
from torch_rechub.models.multi_task import MMOE

model = MMOE(
    features=features,
    task_types=["classification", "classification"],
    n_expert=3,
    expert_params={"dims": [256, 128], "activation": "relu"},
    tower_params_list=[{"dims": [64]}, {"dims": [64]}],
)
```

结构：
- n_expert 个专家 MLP（共享）
- n_task 个门控 MLP，输出 softmax 权重（维度 n_expert）
- n_task 个塔 MLP，输入为专家输出的加权和
- 每个塔后接 PredictionLayer

forward 输出形状 `(B, n_task)`，每列对应一个任务的预测。

### PLE (Progressive Layered Extraction)

RecSys'2020，通过多层 CGC（Customized Gate Control）渐进式分离共享和任务特定知识：

```python
from torch_rechub.models.multi_task import PLE

model = PLE(
    features=features,
    task_types=["classification", "classification"],
    n_level=2,
    n_expert_specific=2,
    n_expert_shared=1,
    expert_params={"dims": [256, 128]},
    tower_params_list=[{"dims": [64]}, {"dims": [64]}],
)
```

CGC 层结构：
- 每个任务有 `n_expert_specific` 个任务特定专家
- 有 `n_expert_shared` 个共享专家
- 每个任务的门控在"自己的特定专家 + 所有共享专家"上做 softmax
- 非最后一层还有一个共享门控，在"所有任务特定专家 + 共享专家"上做 softmax
- 多层 CGC 堆叠，最后一层输出送入各任务塔

### ESMM

Entire Space Multi-task Model，利用 CTR→CVR 的任务依赖关系：

```python
from torch_rechub.models.multi_task import ESMM
model = ESMM(features, task_types=["classification", "classification", "classification"], ...)
```

在 MTLTrainer 中被特殊处理：只计算后两个任务（CTR、CTCVR）的损失，不直接监督 CVR 任务。CTCVR = CTR × CVR。

### AITM

Adaptive Information Transfer Multi-task，通过信息迁移模块在任务间传递知识。

## 自适应损失加权

MTLTrainer 通过 `adaptive_params` 支持三种方法：

### UWL (Uncertainty Weighting)

Kendall et al. 2018，学习每个任务的不确定性权重：

```python
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "uwl"})
```

损失为 `2 * loss_i * exp(-w_i) + w_i`，其中 w_i 为可学习参数。同方差不确定性越大，任务权重越低。

### MetaBalance

通过梯度缩放平衡各任务梯度的范数：

```python
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "metabalance"})
```

- 使用独立的 `MetaBalance` 优化器处理共享层
- 对每个任务的梯度做移动平均（beta=0.9）
- 辅助任务梯度按 `norm[0]/norm[i] * relax_factor` 缩放
- relax_factor 默认 0.7，控制缩放强度
- 使用独立的 share_optimizer 和 task_optimizer

### GradNorm

Chen et al. 2018，动态调整任务权重使梯度范数趋于一致：

```python
trainer = MTLTrainer(model, task_types, adaptive_params={"method": "gradnorm", "alpha": 0.16})
```

- 在最后一个共享层（2D 权重矩阵）上计算各任务梯度范数
- 计算逆训练率 `loss_i(t) / loss_i(0)`
- 通过 GradNorm 损失调整任务权重
- alpha 控制任务平衡强度（默认0.16）
- 每步后对权重归一化

## 参数拆分

`shared_task_layers(model)` 函数根据模型类型精确拆分共享参数和任务参数：

| 模型 | 共享层 | 任务层 |
|------|--------|--------|
| SharedBottom | embedding + bottom_mlp | towers + predict_layers |
| MMOE | embedding + experts | gates + towers + predict_layers |
| PLE | embedding + cgc_layers | towers + predict_layers |
| AITM | embedding + bottoms | info_gates + towers + aits |

这是 MetaBalance 等方法正确工作的基础。

## 训练要点

- `task_types` 列表决定每个任务的损失函数（BCELoss/MSELoss）和评估指标（roc_auc/mean_squared_error）
- `earlystop_taskid` 指定用哪个任务的验证指标做早停
- MTLTrainer.fit 必须提供 val_dataloader
- 模型保存命名为 `model_{mode}_{seed}.pth`，支持多次实验对比
- ESMM 模型在训练循环中有特殊损失计算逻辑
