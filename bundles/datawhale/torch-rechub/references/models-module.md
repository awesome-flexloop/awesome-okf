---
title: 模型模块源码登记
type: reference
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/multi-task-learning
---

# 模型模块源码登记

登记 `torch_rechub/models/` 下所有模型类的源码位置和关键接口。

## 排序模型 (models/ranking/)

| 类名 | 文件 | 关键构造参数 |
|------|------|-------------|
| `WideDeep` | `models/ranking/widedeep.py` | wide_features, deep_features, mlp_params |
| `DeepFM` | `models/ranking/deepfm.py` | deep_features, fm_features, mlp_params |
| `DCN` | `models/ranking/dcn.py` | features, n_cross_layers, mlp_params |
| `DCNv2` | `models/ranking/dcn_v2.py` | features, n_cross_layers, mlp_params, structure |
| `DIN` | `models/ranking/din.py` | features, history_features, target_features, mlp_params, attention_mlp_params |
| `DIEN` | `models/ranking/dien.py` | features, history_features, neg_history_features, ... |
| `AutoInt` | `models/ranking/autoint.py` | features, attn_params, mlp_params |
| `FiBiNet` | `models/ranking/fibinet.py` | features, senet_params, bilinear_type, mlp_params |
| `BST` | `models/ranking/bst.py` | features, history_features, target_features, ... |
| `AFM` | `models/ranking/afm.py` | features, attention_params |
| `DeepFFM` | `models/ranking/deepffm.py` | linear_features, cross_features, ... |
| `FatDeepFFM` | `models/ranking/deepffm.py` | linear_features, cross_features, ... |
| `EDCN` | `models/ranking/edcn.py` | features, n_cross_layers, ... |

子包导出：`models/ranking/__init__.py`，`__all__` 列出 13 个公开类。

## 匹配模型 (models/matching/)

| 类名 | 文件 | 关键特点 |
|------|------|---------|
| `DSSM` | `models/matching/dssm.py` | 双塔 MLP，user_tower()/item_tower() 方法 |
| `FaceBookDSSM` | `models/matching/dssm_facebook.py` | Facebook 风格 DSSM |
| `YoutubeDNN` | `models/matching/youtube_dnn.py` | YouTube 召回网络 |
| `YoutubeSBC` | `models/matching/youtube_sbc.py` | Sampled-Batch Contrastive |
| `MIND` | `models/matching/mind.py` | CapsuleNetwork 多兴趣，bilinear_type=0 |
| `ComirecSA` | `models/matching/comirec.py` | MultiInterestSA 自注意力多兴趣 |
| `ComirecDR` | `models/matching/comirec.py` | CapsuleNetwork(bilinear_type=2) 多兴趣 |
| `GRU4Rec` | `models/matching/gru4rec.py` | GRU 会话推荐 |
| `NARM` | `models/matching/narm.py` | Neural Attentive Session-based |
| `SASRec` | `models/matching/sasrec.py` | Self-Attentive Sequential Recommendation |
| `SINE` | `models/matching/sine.py` | Sparse Interest NEtwork |
| `STAMP` | `models/matching/stamp.py` | Short-Term Attention/Memory Priority |

子包导出：`models/matching/__init__.py`，`__all__` 列出 12 个公开类。

## 多任务模型 (models/multi_task/)

| 类名 | 文件 | 关键构造参数 |
|------|------|-------------|
| `SharedBottom` | `models/multi_task/shared_bottom.py` | features, task_types, bottom_params, tower_params_list |
| `MMOE` | `models/multi_task/mmoe.py` | features, task_types, n_expert, expert_params, tower_params_list |
| `PLE` | `models/multi_task/ple.py` | features, task_types, n_level, n_expert_specific, n_expert_shared, expert_params, tower_params_list |
| `ESMM` | `models/multi_task/esmm.py` | cvr_features, ctr_features, ... |
| `AITM` | `models/multi_task/aitm.py` | features, task_types, ... |

辅助类：`CGC`（在 `ple.py` 中），PLE 的定制门控层。

子包导出：`models/multi_task/__init__.py`。

## 生成式模型 (models/generative/)

| 类名 | 文件 | 说明 |
|------|------|------|
| `HSTUModel` | `models/generative/hstu.py` | HSTU 序列生成，基于 HSTUBlock |
| `HLLMModel` | `models/generative/hllm.py` | Hierarchical LLM for Recommendation |
| `RQVAEModel` | `models/generative/rqvae.py` | Residual Quantized VAE |
| `TIGERModel` | `models/generative/tiger.py` | 延迟导入，需 generative 可选依赖 |

子包导出：`models/generative/__init__.py`，TIGERModel 通过 `__getattr__` 懒加载。

## 模型共同约定

1. 全部继承 `torch.nn.Module`
2. forward 接收 `x: dict[str, Tensor]`（序列生成模型除外，接收位置参数）
3. 特征通过构造函数传入特征描述符列表
4. 内部使用 `EmbeddingLayer` 管理嵌入
5. 双塔模型实现 `user_tower(x)` / `item_tower(x)` 方法并暴露 `mode` 属性
