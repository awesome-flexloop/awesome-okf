---
title: ONNX 导出与部署
type: concept
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/data-pipeline
---

# ONNX 导出与部署

Torch-RecHub 提供非侵入式 ONNX 导出能力，模型代码无需任何修改即可导出为 ONNX 格式，支持双塔分塔导出、动态 batch/序列维度和 INT8/FP16 量化。

## Trainer 层导出接口

每个 Trainer 都提供 `export_onnx()` 方法：

```python
# CTR / 多任务模型
trainer.export_onnx("model.onnx", opset_version=14, dynamic_batch=True)

# 双塔匹配模型：可分塔导出
trainer.export_onnx("user_tower.onnx", mode="user")
trainer.export_onnx("item_tower.onnx", mode="item")
trainer.export_onnx("full_model.onnx")  # mode=None 导出完整模型

# 序列生成模型（HSTU）
seq_trainer.export_onnx("hstu.onnx", seq_length=50, vocab_size=10000)
```

通用参数：
- `output_path`：输出文件路径
- `opset_version`：ONNX opset 版本（默认14）
- `dynamic_batch`：启用动态 batch 维度（默认 True）
- `device`：导出设备（默认 'cpu'，最大兼容性）
- `verbose`：打印导出详情
- `onnx_export_kwargs`：透传给 `torch.onnx.export` 的额外参数

## ONNXExporter 核心类

```python
from torch_rechub.utils.onnx_export import ONNXExporter

exporter = ONNXExporter(model, device='cpu')
success = exporter.export(
    output_path="model.onnx",
    mode=None,
    dummy_input=None,       # 自动生成
    batch_size=2,
    seq_length=10,
    opset_version=14,
    dynamic_batch=True,
)
```

导出流程：
1. 初始化时调用 `extract_feature_info(model)` 通过反射提取特征元信息
2. 根据 mode 选择导出全部特征 / user_features / item_features
3. 用 `generate_dummy_input` 按特征类型生成 dummy tensor
4. 用 `ONNXWrapper` 包装模型，将位置参数转回 dict
5. 配置 dynamic_axes 支持动态 batch 和序列长度
6. 优先尝试 dynamo 导出器，失败自动回退 legacy 导出器
7. 导出完成后恢复模型原始 mode

## ONNXWrapper

解决 ONNX 不支持 dict 输入的问题：

```python
from torch_rechub.utils.onnx_export import ONNXWrapper

wrapper = ONNXWrapper(model, input_names=["user_id", "item_id", "hist"])
# ONNX 导出生成位置参数图，但实际调用时 wrapper 转回 dict
output = wrapper(user_id_tensor, item_id_tensor, hist_tensor)
```

- 构造时设置模型的 mode（用于双塔分塔导出）
- forward 将 `*args` 按 input_names 重组为 dict 后调用原始模型
- 若模型返回 `(prediction, scalar_loss)` 元组，自动只取 prediction
- `restore_mode()` 恢复模型原始 mode

## 特征反射与 dummy input 生成

### extract_feature_info

遍历模型上约定命名的属性提取特征：

```python
from torch_rechub.utils.model_utils import extract_feature_info

info = extract_feature_info(model)
# info = {
#   'features': [...],          # 全部去重特征
#   'input_names': [...],       # 有序特征名
#   'input_types': {...},       # 特征名 -> 类型名
#   'user_features': [...],     # 用户侧特征
#   'item_features': [...],     # 物品侧特征
# }
```

识别的属性名包括：features、deep_features、fm_features、wide_features、linear_features、cross_features、user_features、item_features、history_features、target_features、neg_item_feature 等。

### generate_dummy_input

按特征类型生成正确形状的 tensor：
- `SparseFeature` → `torch.randint(0, vocab_size, (batch_size,))`
- `SequenceFeature` → `torch.randint(0, vocab_size, (batch_size, seq_length))`
- `DenseFeature` → `torch.randn(batch_size, embed_dim)`

### generate_dynamic_axes

生成 ONNX 动态轴配置：
- 所有输入的第0维标记为 "batch_size"
- SequenceFeature 的第1维标记为 "seq_length"
- 输出第0维标记为 "batch_size"

## 动态导出器选择

导出器根据是否需要动态轴自动选择导出路径：
- **需要动态轴**：优先使用 legacy 导出器（`dynamo=False`），因为 dynamo 对 dynamic_axes 的支持在不同 PyTorch 版本间不一致
- **不需要动态轴**：优先使用 dynamo 导出器（`dynamo=True`），以获得更好的算子覆盖
- 用户可通过 `onnx_export_kwargs={"dynamo": True/False}` 强制指定

## ONNX 量化

```python
from torch_rechub.utils.quantization import quantize_model

# INT8 动态量化（推荐 CPU 部署 MLP 密集型模型）
quantize_model("model_fp32.onnx", "model_int8.onnx", mode="int8")

# FP16 转换（推荐 GPU 部署）
quantize_model("model_fp32.onnx", "model_fp16.onnx", mode="fp16", keep_io_types=True)
```

INT8 选项：
- `per_channel`：逐通道量化（默认 False）
- `reduce_range`：缩减量化范围
- `weight_type`："qint8"（有符号，默认）或 "quint8"（无符号）
- `optimize_model`：量化前运行 ORT 图优化
- 支持指定 `op_types_to_quantize`、`nodes_to_quantize`、`nodes_to_exclude`

FP16 选项：
- `keep_io_types=True`：保持模型输入输出为 float32，仅内部权重转 FP16

## 向量检索服务

导出双塔 ONNX 模型后，可用 `serving/` 模块构建向量索引：

```python
from torch_rechub.serving import builder_factory

# 创建 Annoy 构建器
builder = builder_factory("annoy", d=64, metric="angular", n_trees=10)

# 从嵌入构建索引
with builder.from_embeddings(item_embeddings) as indexer:
    ids, distances = indexer.query(user_embeddings, top_k=50)
    indexer.save("item_index.bin")

# 从文件加载
with builder.from_index_file("item_index.bin") as indexer:
    ids, distances = indexer.query(user_embeddings, top_k=50)
```

三种后端：
- **annoy**：`AnnoyBuilder(d, metric, n_trees, threads, searchk)`
- **faiss**：`FaissBuilder`，支持 flat/ivf/hnsw 索引类型，L2/内积度量
- **milvus**：`MilvusBuilder`，基于 Milvus 分布式向量数据库

架构：
- `BaseBuilder`：抽象构建器，`from_embeddings()` 和 `from_index_file()` 返回上下文管理器
- `BaseIndexer`：抽象索引器，`query(embeddings, top_k)` 返回 (ids, distances)，`save(path)` 持久化
