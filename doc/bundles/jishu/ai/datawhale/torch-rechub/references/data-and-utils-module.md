---
title: 数据与工具模块源码登记
type: reference
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/data-pipeline
  - /datawhale/torch-rechub/concepts/tracking-and-visualization
---

# 数据与工具模块源码登记

登记 `torch_rechub/data/`、`torch_rechub/utils/` 下的数据处理、多任务优化、可视化等模块。

## data/ 子包

### data/dataset.py

**路径**：`torch_rechub/data/dataset.py`

| 类名 | 说明 |
|------|------|
| `ParquetIterableDataset(IterableDataset)` | 流式读取 Parquet 文件，多 worker 自动分片，输出 dict[str, Tensor] |

构造参数：`file_paths`、`columns=None`、`batch_size=1024`。

### data/convert.py

**路径**：`torch_rechub/data/convert.py`

| 函数 | 说明 |
|------|------|
| `pa_array_to_tensor(arr: pa.Array) -> Tensor` | PyArrow Array → PyTorch Tensor，支持标量和定长列表 |

## utils/data.py

**路径**：`torch_rechub/utils/data.py`

### Dataset 类

| 类名 | 说明 |
|------|------|
| `TorchDataset(Dataset)` | 封装 (x_dict, y)，__getitem__ 返回 (dict, label) |
| `PredictDataset(Dataset)` | 推理用，只含 x_dict |
| `SeqDataset(Dataset)` | 序列生成数据集，返回 (tokens, positions, time_diffs, target) |
| `EmbDataset(Dataset)` | 加载 .npy/.pt 嵌入文件 |
| `TigerSeqDataset(Dataset)` | TIGER 生成式检索数据集 |
| `Trie` | 前缀树，用于受限生成 |

### DataGenerator 类

| 类名 | 说明 |
|------|------|
| `DataGenerator` | 排序/单任务数据生成器，generate_dataloader 支持 split_ratio |
| `MatchDataGenerator` | 匹配数据生成器，生成 train/test_user/all_item 三个 loader |
| `SequenceDataGenerator` | 序列生成数据生成器，封装 SeqDataset |

### 工具函数

| 函数 | 说明 |
|------|------|
| `get_auto_embedding_dim(num_classes)` | `floor(6 * n^0.25)` 自动嵌入维度 |
| `get_loss_func(task_type)` | BCELoss / MSELoss |
| `get_metric_func(task_type)` | roc_auc_score / mean_squared_error |
| `df_to_dict(data)` | DataFrame → {col: np.ndarray} |
| `pad_sequences(sequences, maxlen, ...)` | 序列填充，等价 Keras |
| `generate_seq_feature(data, user_col, item_col, time_col, ...)` | 排序场景序列特征生成 |
| `create_seq_features(data, ...)` | 另一种序列特征构造（测试保留） |
| `neg_sample(click_hist, item_size)` | 非点击历史随机负采样 |
| `array_replace_with_dict(array, dic)` | 用字典映射替换数组值 |

## utils/match.py

**路径**：`torch_rechub/utils/match.py`

| 名称 | 类型 | 说明 |
|------|------|------|
| `gen_model_input(df, user_profile, user_col, item_profile, item_col, seq_max_len)` | 函数 | 合并画像 + 填充 hist_/tag_ 列 |
| `negative_sample(items_cnt_order, ratio, method_id)` | 函数 | 离线负采样，4种方法 |
| `inbatch_negative_sampling(scores, neg_ratio, hard_negative, generator)` | 函数 | 批内负例索引采样 |
| `gather_inbatch_logits(scores, neg_indices)` | 函数 | 提取正例+负例 logits |
| `generate_seq_feature_match(data, ..., sample_method, mode, neg_ratio)` | 函数 | 召回场景序列特征，point/pair/list-wise |
| `Annoy` | 类 | Annoy 向量检索引擎（fit/query） |
| `Faiss` | 类 | FAISS 向量检索引擎 |
| `Milvus` | 类 | Milvus 向量检索引擎 |

## utils/mtl.py

**路径**：`torch_rechub/utils/mtl.py`

| 名称 | 说明 |
|------|------|
| `shared_task_layers(model)` | 拆分共享层和任务层参数，支持 SharedBottom/MMOE/PLE/AITM |
| `MetaBalance(Optimizer)` | 梯度平衡优化器 |
| `gradnorm(loss_list, loss_weight, share_layer, initial_task_loss, alpha)` | GradNorm 自适应加权 |

## utils/model_utils.py

**路径**：`torch_rechub/utils/model_utils.py`

| 函数 | 说明 |
|------|------|
| `extract_feature_info(model)` | 反射提取模型特征列表、user/item 特征 |
| `generate_dummy_input(features, batch_size, seq_length, device)` | 按特征类型生成 dummy tensor 元组 |
| `generate_dummy_input_dict(features, ...)` | 生成 dict 形式 dummy input |
| `generate_dynamic_axes(input_names, output_names, seq_features)` | 生成 ONNX dynamic_axes 配置 |

## utils/visualization.py

**路径**：`torch_rechub/utils/visualization.py`

| 名称 | 说明 |
|------|------|
| `TORCHVIEW_AVAILABLE` | 布尔标志，torchview 是否可用 |
| `visualize_model(model, input_data, ..., save_path, dpi)` | 生成模型计算图 |
| `display_graph(graph, format)` | Jupyter 中展示 ComputationGraph |
| `_is_jupyter_environment()` | 检测是否在 Jupyter 环境 |

## utils/onnx_export.py

详见 服务与 ONNX 模块源码登记。

## utils/quantization.py

详见 服务与 ONNX 模块源码登记。

## types.py

**路径**：`torch_rechub/types.py`

| 类型 | 定义 |
|------|------|
| `FilePath` | `Union[str, os.PathLike]` |
