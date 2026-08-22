---
title: 数据管道
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/trainer-system
---

# 数据管道

Torch-RecHub 提供从原始交互数据到 DataLoader 的完整工具链，涵盖数据集封装、序列特征构造、负采样和大数据流式读取。

## Dataset 类

### TorchDataset

标准训练数据集，封装特征字典和标签：

```python
from torch_rechub.utils.data import TorchDataset
from torch.utils.data import DataLoader

dataset = TorchDataset(x_dict, y_array)
loader = DataLoader(dataset, batch_size=16, shuffle=True)
# 迭代返回 ({feature_name: tensor}, label_tensor)
```

### PredictDataset

推理用数据集，只含特征无标签：

```python
from torch_rechub.utils.data import PredictDataset
dataset = PredictDataset(x_dict)
```

### SeqDataset

序列生成模型数据集，返回四元组：

```python
from torch_rechub.utils.data import SeqDataset
dataset = SeqDataset(seq_tokens, seq_positions, targets, seq_time_diffs)
# __getitem__ 返回 (LongTensor, LongTensor, LongTensor, LongTensor)
```

### EmbDataset

加载预训练嵌入文件（.npy 或 .pt）：

```python
from torch_rechub.utils.data import EmbDataset
dataset = EmbDataset("embeddings.npy")  # 支持 .npy / .pt
emb = dataset[0]  # torch.FloatTensor
```

### ParquetIterableDataset

流式读取 Parquet 文件，支持大数据场景和多 worker 分片：

```python
from torch_rechub.data.dataset import ParquetIterableDataset

ds = ParquetIterableDataset(
    file_paths=["train1.parquet", "train2.parquet"],
    columns=["user_id", "item_id", "label"],
    batch_size=1024,
)
loader = DataLoader(ds, batch_size=None)  # batch_size=None 因为已按批产出
for batch in loader:
    # batch: dict[str, Tensor]
```

多 worker 时自动按 worker_id 切分文件列表，每个 worker 构建独立的 PyArrow Dataset/Scanner。通过 `pa_array_to_tensor` 将 PyArrow Array 转为 PyTorch Tensor，支持标量和定长嵌套列表。

## DataGenerator

### DataGenerator（排序/单任务）

```python
from torch_rechub.utils.data import DataGenerator

dg = DataGenerator(x, y)
train_dl, val_dl, test_dl = dg.generate_dataloader(
    x_val=x_val, y_val=y_val,
    x_test=x_test, y_test=y_test,
    batch_size=256, num_workers=4,
)
# 或自动按比例切分
train_dl, val_dl, test_dl = dg.generate_dataloader(
    split_ratio=(0.8, 0.1, 0.1),
    batch_size=256,
)
```

### MatchDataGenerator（匹配/召回）

```python
from torch_rechub.utils.data import MatchDataGenerator

dg = MatchDataGenerator(x, y)
train_dl, test_user_dl, all_item_dl = dg.generate_dataloader(
    x_test_user, x_all_item, batch_size=256,
)
```

生成三个 DataLoader：训练集、测试用户集、全量物品集（用于物品嵌入推理）。

### SequenceDataGenerator（序列生成）

```python
from torch_rechub.utils.data import SequenceDataGenerator

gen = SequenceDataGenerator(seq_tokens, seq_positions, targets, seq_time_diffs)
train_loader, val_loader, test_loader = gen.generate_dataloader(
    batch_size=32, split_ratio=(0.7, 0.1, 0.2),
)
```

## 数据转换工具

### df_to_dict

将 pandas DataFrame 转为模型输入字典：

```python
from torch_rechub.utils.data import df_to_dict
x_dict = df_to_dict(df)  # {col_name: np.ndarray}
```

### pad_sequences

等价于 Keras 的序列填充：

```python
from torch_rechub.utils.data import pad_sequences
padded = pad_sequences(sequences, maxlen=50, padding='pre', truncating='pre', value=0.)
```

支持 pre/post 填充和截断方向。

### gen_model_input

合并用户/物品画像到交互数据，并自动填充 hist_ 和 tag_ 前缀的序列列：

```python
from torch_rechub.utils.match import gen_model_input
input_dict = gen_model_input(
    df, user_profile, "user_id",
    item_profile, "item_id",
    seq_max_len=50,
)
```

## 序列特征生成

### generate_seq_feature（排序场景）

为 DIN/DIEN 等排序模型构造滑动窗口序列特征和负样本：

```python
from torch_rechub.utils.data import generate_seq_feature
train, val, test = generate_seq_feature(
    data, user_col="user_id", item_col="item_id", time_col="time",
    item_attribute_cols=["cate_id"],
    min_item=2, max_len=50,
)
```

逻辑：按用户分组、按时间排序、滑动窗口构造历史序列，每个正样本配一个负样本，最后两条交互分别作为 val/test。

### generate_seq_feature_match（召回场景）

为 DSSM/MIND 等召回模型构造序列特征，支持三种训练模式：

```python
from torch_rechub.utils.match import generate_seq_feature_match
train_df, test_df = generate_seq_feature_match(
    data, user_col="user_id", item_col="item_id", time_col="time",
    sample_method=0,   # 负采样方法 0-3
    mode=0,            # 0=point-wise, 1=pair-wise, 2=list-wise
    neg_ratio=4,       # 负样本比例
    min_item=2,
)
```

## 负采样

### negative_sample（离线）

四种负采样方法：
- `method_id=0`：均匀随机采样
- `method_id=1`：word2vec 频次采样（count^0.75 加权）
- `method_id=2`：log(count+1) 加权采样
- `method_id=3`：腾讯 RALM 采样

### inbatch_negative_sampling（在线/批内）

在训练 batch 内采样负例，无需全局负采样表：

```python
from torch_rechub.utils.match import inbatch_negative_sampling, gather_inbatch_logits

scores = user_emb @ item_emb.t()  # (B, B)
neg_idx = inbatch_negative_sampling(scores, neg_ratio=4, hard_negative=False)
logits = gather_inbatch_logits(scores, neg_idx)  # (B, 1+K)
```

- 对角线为正例，非对角线为候选负例
- `hard_negative=True` 时选择分数最高的 top-k 负例
- 支持 `sampler_seed` 控制可复现性
