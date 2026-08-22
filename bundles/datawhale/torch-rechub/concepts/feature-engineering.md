---
title: 特征工程
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/data-pipeline
---

# 特征工程

Torch-RecHub 采用**特征描述符（Feature Descriptor）**模式：用轻量对象描述特征的元信息（名称、词表大小、嵌入维度、池化方式），模型据此自动创建嵌入层。

## 三种特征类型

### SparseFeature

稀疏类别特征（如 user_id、item_id），对应单个类别 ID。

```python
from torch_rechub.basic.features import SparseFeature

user_id = SparseFeature(name="user_id", vocab_size=10000, embed_dim=16)
item_id = SparseFeature(name="item_id", vocab_size=5000, embed_dim=16, shared_with=None)
```

属性：
- `name`：特征名，对应输入 dict 的 key
- `vocab_size`：词表大小
- `embed_dim`：嵌入维度，为 None 时自动计算
- `shared_with`：共享另一特征的嵌入表（如历史物品与目标物品共享）
- `padding_idx`：填充索引，该位置嵌入为零向量
- `initializer`：嵌入初始化器，默认 `RandomNormal(0, 0.0001)`

### SequenceFeature

序列/多热特征（如用户点击历史 item_id 序列），需要池化。

```python
from torch_rechub.basic.features import SequenceFeature

hist_item = SequenceFeature(
    name="hist_item_id",
    vocab_size=5000,
    embed_dim=16,
    pooling="mean",       # 支持 "mean" / "sum" / "concat"
    padding_idx=0,
)
```

`pooling` 方式：
- `"mean"`：平均池化（默认），考虑 padding mask
- `"sum"`：求和池化，考虑 padding mask
- `"concat"`：不池化，保留序列维度 `(B, L, D)`

### DenseFeature

稠密数值特征（如年龄、价格），不经过嵌入层。

```python
from torch_rechub.basic.features import DenseFeature

price = DenseFeature(name="price", embed_dim=1)
```

`embed_dim` 默认为 1；若传入向量型稠密特征，可设为对应维度。

## 自动嵌入维度

当 `embed_dim=None` 时，调用 `get_auto_embedding_dim(vocab_size)`：

```python
embed_dim = int(6 * vocab_size ** 0.25)
```

该公式来自 DCN 论文，经验性地根据词表大小推荐嵌入维度。

## EmbeddingLayer

`EmbeddingLayer` 是所有模型的统一嵌入入口：

```python
from torch_rechub.basic.layers import EmbeddingLayer

embedding = EmbeddingLayer(features)

# 保持三维形状 (B, num_features, embed_dim)
sparse_emb = embedding(x, features, squeeze_dim=False)

# 展平拼接为 (B, num_features * embed_dim + num_dense)
flat_emb = embedding(x, features, squeeze_dim=True)
```

关键机制：
- 使用 `nn.ModuleDict`（`embed_dict`）按特征名存储嵌入表
- 自动跳过 `shared_with` 已注册的特征，实现嵌入共享
- 对 SequenceFeature 自动应用配置的池化层和 mask
- DenseFeature 直接从输入 dict 取值，不经过嵌入
- `squeeze_dim=True` 时将所有嵌入展平并与稠密值拼接

## InputMask

`InputMask` 根据特征的 `padding_idx` 生成掩码：

```python
mask = embedding.input_mask(x, seq_feature)  # (B, 1, L)
```

- 若设置了 `padding_idx`，值等于 padding_idx 的位置标记为无效
- 否则值为 -1 的位置标记为无效
- 掩码用于 AveragePooling/SumPooling 中忽略填充位

## 嵌入共享

通过 `shared_with` 实现嵌入表复用，典型场景：

```python
# 用户历史物品与目标物品共享物品嵌入表
hist_item = SequenceFeature("hist_item_id", vocab_size=5000, shared_with="item_id")
target_item = SparseFeature("item_id", vocab_size=5000)
```

这在 DIN、DSSM 等模型中是标准做法，可减少参数并保持语义一致性。

## 初始化器

`basic/initializers.py` 提供：
- `RandomNormal(mean, std)`：正态分布（默认）
- `RandomUniform(minval, maxval)`：均匀分布
- `XavierNormal(gain)` / `XavierUniform(gain)`：Xavier 初始化
- `Pretrained(embedding_weight, freeze)`：加载预训练嵌入
