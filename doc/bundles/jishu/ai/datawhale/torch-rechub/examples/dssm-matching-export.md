---
title: DSSM 召回训练与 ONNX 导出
type: example
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/onnx-export
  - /datawhale/torch-rechub/concepts/data-pipeline
---

# DSSM 召回训练与 ONNX 导出

本示例演示使用 DSSM 双塔模型进行物品召回，包括批内负采样训练、嵌入推理、分塔 ONNX 导出和向量索引构建。

## 1. 定义特征

```python
from torch_rechub.basic.features import SparseFeature, SequenceFeature

user_features = [
    SparseFeature("user_id", vocab_size=100000, embed_dim=32),
    SparseFeature("gender", vocab_size=3, embed_dim=8),
    SequenceFeature("hist_item_id", vocab_size=50000, embed_dim=32, pooling="mean", padding_idx=0),
]
item_features = [
    SparseFeature("item_id", vocab_size=50000, embed_dim=32),
    SparseFeature("cate_id", vocab_size=1000, embed_dim=8),
]
```

注意：`hist_item_id` 可以通过 `shared_with="item_id"` 与物品塔的 item_id 共享嵌入表。

## 2. 构造 DSSM 模型

```python
from torch_rechub.models.matching import DSSM

user_params = {"dims": [256, 128, 64], "activation": "relu", "dropout": 0.1}
item_params = {"dims": [256, 128, 64], "activation": "relu", "dropout": 0.1}

model = DSSM(
    user_features=user_features,
    item_features=item_features,
    user_params=user_params,
    item_params=item_params,
    temperature=1.0,
)
```

DSSM 的两个塔分别是 MLP，输出经过 L2 归一化。`mode=None` 时 forward 返回内积 sigmoid 分数；`mode="user"`/`"item"` 时只返回对应塔嵌入。

## 3. 训练（point-wise + 批内负采样）

```python
from torch_rechub.trainers import MatchTrainer

trainer = MatchTrainer(
    model=model,
    mode=0,
    in_batch_neg=True,
    in_batch_neg_ratio=4,
    hard_negative=False,
    optimizer_fn=torch.optim.Adam,
    optimizer_params={"lr": 1e-3},
    n_epoch=10,
    earlystop_patience=5,
    device="cuda:0",
    model_path="./checkpoints/dssm/",
)

trainer.fit(train_dataloader, val_dataloader)
```

三种训练模式：
- `mode=0` point-wise：BCELoss 或批内负采样 CrossEntropyLoss
- `mode=1` pair-wise：BPRLoss，模型返回 `(pos_score, neg_score)`
- `mode=2` list-wise：CrossEntropyLoss

批内负采样要求模型实现 `user_tower(x)` 和 `item_tower(x)` 方法返回 2D 嵌入。

## 4. 推理用户/物品嵌入

```python
# 加载最佳模型并批量生成嵌入
user_embeddings = trainer.inference_embedding(
    model, "user", user_dataloader, "./checkpoints/dssm/"
)
item_embeddings = trainer.inference_embedding(
    model, "item", item_dataloader, "./checkpoints/dssm/"
)
```

`inference_embedding` 会自动设置 `model.mode`，加载权重，批量推理后 `torch.cat` 拼接。

## 5. 分塔导出 ONNX

```python
# 导出用户塔（在线用户 embedding 推理）
trainer.export_onnx(
    "user_tower.onnx",
    mode="user",
    opset_version=14,
    dynamic_batch=True,
)

# 导出物品塔（离线批量物品 embedding 生成）
trainer.export_onnx(
    "item_tower.onnx",
    mode="item",
    opset_version=14,
    dynamic_batch=True,
)
```

导出过程：
1. 通过反射提取 `user_features` / `item_features`
2. 临时设置 `model.mode = "user"/"item"`
3. `ONNXWrapper` 将位置参数转回 dict
4. 生成 dummy input（SparseFeature → [B]，SequenceFeature → [B, L]）
5. 导出后自动恢复原始 mode

## 6. ONNX 量化

```python
from torch_rechub.utils.quantization import quantize_model

# INT8 动态量化（CPU 部署）
quantize_model("user_tower.onnx", "user_tower_int8.onnx", mode="int8")

# FP16 转换（GPU 部署）
quantize_model("item_tower.onnx", "item_tower_fp16.onnx", mode="fp16")
```

## 7. 构建向量检索索引

```python
from torch_rechub.serving import builder_factory

# 使用 Annoy 构建物品索引
builder = builder_factory("annoy", d=64, metric="angular", n_trees=10)

with builder.from_embeddings(item_embeddings) as indexer:
    # 查询 top-50 最近邻
    ids, distances = indexer.query(user_embeddings, top_k=50)
    # 保存索引
    indexer.save("item_index.bin")

# 从文件加载索引查询
with builder.from_index_file("item_index.bin") as indexer:
    ids, distances = indexer.query(new_user_emb, top_k=50)
```

也可使用 `"faiss"`（支持 IVF/HNSW）或 `"milvus"`（分布式）后端。

## 完整数据流

```
原始交互数据
    ↓ generate_seq_feature_match / gen_model_input
DataFrame → df_to_dict → x_dict
    ↓ MatchDataGenerator.generate_dataloader
DataLoader (x_dict, y)
    ↓ MatchTrainer.fit
DSSM 模型训练（in-batch negative sampling）
    ↓ trainer.inference_embedding
user_embeddings / item_embeddings
    ↓ builder_factory + from_embeddings
Annoy/FAISS/Milvus 向量索引
    ↓ indexer.query
Top-K 推荐结果
```
