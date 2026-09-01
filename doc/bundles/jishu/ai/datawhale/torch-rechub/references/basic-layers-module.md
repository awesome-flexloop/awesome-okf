---
title: 基础层与特征模块源码登记
type: reference
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/model-architecture
---

# 基础层与特征模块源码登记

登记 `torch_rechub/basic/` 下的核心类和函数。

## features.py

**路径**：`torch_rechub/basic/features.py`

| 类名 | 关键属性/方法 | 说明 |
|------|-------------|------|
| `SparseFeature` | name, vocab_size, embed_dim, shared_with, padding_idx, initializer; get_embedding_layer() | 稀疏类别特征 |
| `SequenceFeature` | 同 SparseFeature + pooling("mean"/"sum"/"concat") | 序列/多热特征 |
| `DenseFeature` | name, embed_dim=1 | 稠密数值特征 |

embed_dim 为 None 时调用 `get_auto_embedding_dim(vocab_size)`。

## layers.py

**路径**：`torch_rechub/basic/layers.py`

### 嵌入与输入

| 类名 | 说明 |
|------|------|
| `EmbeddingLayer` | 统一嵌入层，embed_dict=nn.ModuleDict，forward(x, features, squeeze_dim=False) |
| `InputMask` | 根据 padding_idx 生成掩码 |
| `PredictionLayer` | task_type="classification"用sigmoid，"regression"直接返回 |

### 基础组件

| 类名 | 说明 |
|------|------|
| `LR` | 逻辑回归 Linear(input_dim, 1) + 可选 sigmoid |
| `MLP` | 多层感知机，每层 Linear→BN→activation→Dropout，可选 output_layer |
| `FM` | 因子分解机二阶交互 |
| `CIN` | 压缩交互网络（xDeepFM） |
| `FFM` | 域感知因子分解机 |
| `CEN` | Compose-Excitation Network（FAT-DeepFFM） |

### 交叉网络

| 类名 | 说明 |
|------|------|
| `CrossLayer` | 单层 DCN 交叉 |
| `CrossNetwork` | DCN V1 交叉网络 |
| `CrossNetV2` | DCN V2 交叉网络 |
| `CrossNetMix` | DCN-Mix 低秩专家交叉网络 |

### 池化层

| 类名 | 说明 |
|------|------|
| `AveragePooling` | 掩码感知平均池化 |
| `SumPooling` | 掩码感知求和池化 |
| `ConcatPooling` | 不池化，保留序列维度 |

### 注意力与交互

| 类名 | 说明 |
|------|------|
| `SENETLayer` | SENet 特征门控 |
| `BiLinearInteractionLayer` | FFM 风格双线性交互（field_all/field_each/field_interaction） |
| `InteractingLayer` | AutoInt 多头自注意力交互层 |
| `ActivationUnit` | DIN 目标注意力（在 ranking/din.py 中） |

### 多兴趣

| 类名 | 说明 |
|------|------|
| `MultiInterestSA` | 自注意力多兴趣提取（ComirecSA） |
| `CapsuleNetwork` | 胶囊网络多兴趣提取（MIND/ComirecDR），bilinear_type 0/1/2 |

### HSTU 层

| 类名 | 说明 |
|------|------|
| `HSTULayer` | 单层 HSTU 序列转换单元，SiLU 激活、相对位置时间偏置、因果掩码 |
| `HSTUBlock` | HSTULayer 堆叠，外部残差连接 |

## activation.py

**路径**：`torch_rechub/basic/activation.py`

| 名称 | 类型 | 说明 |
|------|------|------|
| `Dice` | nn.Module | DIN 论文中的 Dice 激活，可学习 alpha |
| `activation_layer` | 函数 | 工厂函数，支持 sigmoid/relu/dice/prelu/softmax/leakyrelu |

## initializers.py

**路径**：`torch_rechub/basic/initializers.py`

| 类名 | 说明 |
|------|------|
| `RandomNormal(mean, std)` | 正态分布初始化嵌入 |
| `RandomUniform(minval, maxval)` | 均匀分布初始化 |
| `XavierNormal(gain)` | Xavier 正态初始化 |
| `XavierUniform(gain)` | Xavier 均匀初始化 |
| `Pretrained(weight, freeze)` | 加载预训练嵌入 |

所有初始化器通过 `__call__(vocab_size, embed_dim, padding_idx)` 返回 `nn.Embedding`。

## loss_func.py

**路径**：`torch_rechub/basic/loss_func.py`

| 类名 | 说明 |
|------|------|
| `RegularizationLoss` | 统一 L1/L2 正则，区分 embedding/dense 参数，跳过 norm 层 |
| `BPRLoss` | Bayesian Personalized Ranking 成对损失 |
| `HingeLoss` | 合页损失，可选排名加权 |
| `NCELoss` | 噪声对比估计损失 |
| `InBatchNCELoss` | 批内 NCE 损失 |

## callback.py

**路径**：`torch_rechub/basic/callback.py`

| 类名 | 说明 |
|------|------|
| `EarlyStopper` | 早停器，patience、best_auc、best_weights、trial_counter |

## metaoptimizer.py

**路径**：`torch_rechub/basic/metaoptimizer.py`

| 类名 | 说明 |
|------|------|
| `MetaBalance` | 多任务梯度平衡优化器，relax_factor=0.7, beta=0.9 |

## metric.py

**路径**：`torch_rechub/basic/metric.py`

| 函数 | 说明 |
|------|------|
| `auc_score(y_true, y_pred)` | AUC |
| `gauc_score(y_true, y_pred, users, weights)` | 分组加权 AUC |
| `topk_metrics(y_true, y_pred, topKs)` | NDCG/MRR/Recall/Hit/Precision |
| `ndcg_score/hit_score/mrr_score/recall_score/precision_score` | 单项指标便捷函数 |
| `log_loss(y_true, y_pred)` | 对数损失 |
| `diversity_score(y_pred, item_embeddings, topKs)` | Intra-List Diversity |
| `coverage_score(y_pred, all_items, topKs)` | 目录覆盖率 |
| `novelty_score(y_pred, item_popularity, topKs)` | 平均自信息 |

## tracking.py

**路径**：`torch_rechub/basic/tracking.py`

| 类名 | 说明 |
|------|------|
| `BaseLogger` | 抽象基类：log_metrics/log_hyperparams/finish |
| `WandbLogger` | Weights & Biases 适配器 |
| `SwanLabLogger` | SwanLab 适配器 |
| `TensorBoardXLogger` | TensorBoardX 适配器 |
