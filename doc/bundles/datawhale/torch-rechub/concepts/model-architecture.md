---
title: 模型体系
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/onnx-export
---

# 模型体系

Torch-RecHub 的模型按推荐系统任务范式组织为四大类，全部继承自 `torch.nn.Module`，统一接收 `dict[str, Tensor]` 作为 forward 输入。

## 模型分类

### 排序模型 (models/ranking/)

面向点击率（CTR）预估等单目标排序任务，输出经过 sigmoid 的概率值。

| 模型类 | 论文/来源 | 核心特点 |
|--------|----------|---------|
| `DeepFM` | IJCAI'2017 | LR + FM + DNN 三部分端到端联合训练 |
| `WideDeep` | DLRS'2016 | Wide 线性部分 + Deep MLP |
| `DCN` / `DCNv2` | ADKDD'2017 / WWW'2021 | Cross Network 显式高阶特征交叉 |
| `DIN` | KDD'2018 | ActivationUnit 目标注意力捕捉用户兴趣多样性 |
| `DIEN` | AAAI'2019 | GRU + AUGRU 兴趣进化 |
| `AutoInt` | CIKM'2019 | Multi-head Self-Attention 自动特征交互 |
| `FiBiNet` | RecSys'2019 | SENET + Bilinear Interaction |
| `BST` | DLP-KDD'2019 | Transformer 编码用户行为序列 |
| `AFM` | IJCAI'2017 | Attention-based FM |
| `DeepFFM` / `FatDeepFFM` | — | Field-aware FM + CEN |
| `EDCN` | — | 深度交叉网络变体 |

### 匹配/召回模型 (models/matching/)

面向候选物品召回，以双塔架构为主，输出用户/物品嵌入向量或相似度分数。

| 模型类 | 核心特点 |
|--------|---------|
| `DSSM` | 用户塔 + 物品塔 MLP，L2 归一化后内积 |
| `FaceBookDSSM` | Facebook 风格 DSSM 变体 |
| `YoutubeDNN` | YouTube 深度召回网络 |
| `MIND` | Capsule Network 多兴趣提取 |
| `ComirecSA` / `ComirecDR` | 自注意力/胶囊路由多兴趣 |
| `GRU4Rec` | GRU 序列推荐 |
| `NARM` | Neural Attentive Session-based |
| `SASRec` | Self-Attentive Sequential Recommendation |
| `SINE` | 稀疏兴趣多兴趣网络 |
| `STAMP` | Short-Term Attention/Memory Priority |
| `YoutubeSBC` | YouTube Sampled-Batch Contrastive |

### 多任务模型 (models/multi_task/)

| 模型类 | 核心特点 |
|--------|---------|
| `SharedBottom` | 共享底层 + 任务独立塔 |
| `MMOE` | 多专家 + 每任务门控（softmax） |
| `PLE` | 多层 CGC，任务特定专家 + 共享专家 |
| `ESMM` | 基于 CTR→CVR 任务依赖，CTCVR = CTR × CVR |
| `AITM` | Adaptive Information Transfer Multi-task |

### 生成式模型 (models/generative/)

| 模型类 | 核心特点 |
|--------|---------|
| `HSTUModel` | Hierarchical Sequential Transduction Unit，生成式序列推荐 |
| `HLLMModel` | Hierarchical Large Language Model for Recommendation |
| `RQVAEModel` | Residual Quantized VAE，语义 ID 生成 |
| `TIGERModel` | 生成式检索（需 transformers 可选依赖） |

## 统一输入契约

所有排序、匹配、多任务模型的 forward 签名为：

```python
def forward(self, x: dict[str, torch.Tensor]) -> torch.Tensor:
```

其中 `x` 的 key 对应特征对象的 `name` 属性。序列特征值形状为 `(B, L)`，稀疏特征为 `(B,)`，稠密特征为 `(B, embed_dim)`。

多任务模型输出形状为 `(B, n_task)`；双塔模型在 `mode=None` 时输出相似度分数，在 `mode="user"/"item"` 时输出对应塔嵌入。

## 模型构造约定

模型构造函数普遍接收：
- `features` / `user_features` / `item_features`：特征描述符列表
- `task_types`：多任务模型的任务类型列表
- `mlp_params` / `expert_params` / `tower_params_list`：MLP 配置字典，包含 `dims`、`activation`、`dropout`、`output_layer`

MLP 配置示例：
```python
mlp_params = {"dims": [256, 128], "dropout": 0.2, "activation": "relu", "output_layer": True}
```

## 基础构建块

模型通过组合 `basic/layers.py` 中的层构建：
- `EmbeddingLayer`：统一嵌入查找与池化
- `MLP`：带 BN/激活/Dropout 的多层感知机
- `FM`、`CIN`、`CrossNetwork`：特征交叉
- `PredictionLayer`：分类/回归输出适配
- `CapsuleNetwork`、`MultiInterestSA`：多兴趣提取
- `HSTULayer`/`HSTUBlock`：生成式序列编码
