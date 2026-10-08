---
title: 服务与 ONNX 模块源码登记
type: reference
bundle: /datawhale/torch-rechub
related:
  - /datawhale/torch-rechub/concepts/onnx-export
---

# 服务与 ONNX 模块源码登记

登记 `torch_rechub/serving/` 和 `torch_rechub/utils/onnx_export.py`、`utils/quantization.py` 的源码接口。

## serving/ 子包

### serving/base.py

**路径**：`torch_rechub/serving/base.py`

| 类名 | 说明 |
|------|------|
| `BaseBuilder(abc.ABC)` | 向量索引构建器抽象基类 |
| `BaseIndexer(abc.ABC)` | 向量索引器抽象基类 |

`BaseBuilder` 抽象方法：
- `from_embeddings(embeddings: Tensor) -> ContextManager[BaseIndexer]`
- `from_index_file(index_file: FilePath) -> ContextManager[BaseIndexer]`

`BaseIndexer` 抽象方法：
- `query(embeddings: Tensor, top_k: int) -> tuple[Tensor, Tensor]`：返回 (ids, distances)
- `save(file_path: FilePath) -> None`

### serving/__init__.py

**路径**：`torch_rechub/serving/__init__.py`

| 名称 | 说明 |
|------|------|
| `builder_factory(model, **builder_config) -> BaseBuilder` | 工厂函数，model ∈ "annoy"/"faiss"/"milvus" |
| `AnnoyBuilder` | Annoy 后端构建器 |
| `FaissBuilder` | FAISS 后端构建器 |
| `MilvusBuilder` | Milvus 后端构建器 |

### serving/annoy.py

**路径**：`torch_rechub/serving/annoy.py`

| 类名 | 关键参数 |
|------|---------|
| `AnnoyBuilder(BaseBuilder)` | d（维度）、metric（angular/euclidean/dot）、n_trees=10、threads=-1、searchk=-1 |
| `AnnoyIndexer(BaseIndexer)` | 包装 annoy.AnnoyIndex，query 返回 (np.int64 ids, np.float32 distances) |

### serving/faiss.py

FAISS 后端构建器和索引器，支持 flat/ivf/hnsw 索引类型和 L2/内积度量。

### serving/milvus.py

Milvus 分布式向量数据库后端构建器和索引器。

## utils/onnx_export.py

**路径**：`torch_rechub/utils/onnx_export.py`

### ONNXWrapper

| 方法 | 说明 |
|------|------|
| `__init__(model, input_names, mode=None)` | 包装 dict 输入模型为位置参数模型；设置双塔 mode |
| `forward(*args)` | 将位置 args 按 input_names 重组为 dict 调用原始模型；剥离 scalar loss 元组 |
| `restore_mode()` | 恢复模型原始 mode |

### ONNXExporter

| 方法 | 说明 |
|------|------|
| `__init__(model, device='cpu')` | 初始化，调用 extract_feature_info |
| `export(output_path, mode, dummy_input, batch_size, seq_length, opset_version, dynamic_batch, verbose, onnx_export_kwargs) -> bool` | 执行导出 |
| `get_input_info(mode=None)` | 获取输入名、类型、形状信息 |
| `_build_dynamic_shapes(features)` | 为 dynamo 导出器构建 dynamic_shapes |

导出行为：
1. 根据 mode 选择 features（全量/user/item）
2. 创建 ONNXWrapper
3. 生成或使用 dummy_input
4. 配置 dynamic_axes（batch + seq 维度）
5. dynamo 优先，失败自动回退 legacy
6. finally 中恢复模型 mode

从 `model_utils.py` 重导出：
- `extract_feature_info`
- `generate_dummy_input`
- `generate_dummy_input_dict`
- `generate_dynamic_axes`

## utils/quantization.py

**路径**：`torch_rechub/utils/quantization.py`

| 函数 | 说明 |
|------|------|
| `quantize_model(input_path, output_path, mode='int8', ...) -> str` | ONNX 模型量化 |

### INT8 动态量化参数

- `per_channel=False`：逐通道量化
- `reduce_range=False`：缩减范围
- `weight_type="qint8"`：qint8 或 quint8
- `optimize_model=False`：ORT 图优化
- `op_types_to_quantize`、`nodes_to_quantize`、`nodes_to_exclude`、`extra_options`：高级选项

依赖：`onnxruntime.quantization.quantize_dynamic`、`QuantType`。

### FP16 转换参数

- `keep_io_types=True`：保持输入输出为 float32

依赖：`onnx` + `onnxconverter_common.float16.convert_float_to_float16`。

## Trainer 层的 export_onnx 方法

各 Trainer 的 `export_onnx` 方法均委托给 `ONNXExporter`，但有细微差异：

| Trainer | 文件 | 特殊参数 |
|---------|------|---------|
| `CTRTrainer.export_onnx` | ctr_trainer.py:189 | dummy_input, batch_size, seq_length, opset_version, dynamic_batch |
| `MatchTrainer.export_onnx` | match_trainer.py:266 | 额外 `mode="user"/"item"/None`，导出后恢复原始 mode |
| `MTLTrainer.export_onnx` | mtl_trainer.py:264 | 输出 [B, n_task] 多任务张量 |
| `SeqTrainer.export_onnx` | seq_trainer.py:267 | 位置参数 (seq_tokens, seq_time_diffs)，需 vocab_size，不经过 ONNXWrapper |
| `Trainer.export_onnx` (RQVAE) | rqvae_trainer.py:238 | 双输出 (output 重建 + indices 语义码)，包装 forward_for_export |
