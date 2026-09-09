---
type: concept
title: "EmbeddingModel：向量化接口全解"
description: "EmbeddingModel 构造参数（pooler/device/fp16/多卡 DataParallel）、encode 完整数据流（指令前缀→分词→CLS/mean pooling→L2 归一化），以及 device 解析的 xpu 支持。"
tags: [bcembedding, embedding, embeddingmodel, pooling, device, fp16]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: insights
    resource: /references/insights.md
    title: BCEmbedding 架构洞察与知识地图
---

# EmbeddingModel：向量化接口全解

`EmbeddingModel`（`BCEmbedding/models/embedding.py`）是本库的语义向量生成器，封装了分词、pooling、归一化的完整推理链路。理解它的关键是把**构造期**（设备与精度决策）和**推理期**（`encode` 数据流）分开看。

## 构造签名与加载方式

```python
EmbeddingModel(
    model_name_or_path='maidalun1020/bce-embedding-base_v1',
    pooler='cls',
    use_fp16=False,
    device=None,
    **kwargs
)
```

构造器内部以 `AutoTokenizer.from_pretrained` 与 `AutoModel.from_pretrained` 加载模型（F-bc-005），`**kwargs` 会原样透传给这两个调用（例如 `trust_remote_code`）。

### pooler：池化策略

`pooler` 仅允许 `'cls'` 与 `'mean'` 两个取值，断言失败信息为 `` `pooler` should be in ['cls', 'mean']. 'cls' is recommended! ``（F-bc-006）。默认 `'cls'` 且官方明确推荐 cls——这与 README 及模型卡的使用方式一致。

### device 解析逻辑

device 分支（F-bc-007）是 EmbeddingModel 最复杂的一段构造逻辑：

| 输入 | 解析结果 | 行为 |
|---|---|---|
| `None` | `cuda`（若 `torch.cuda.device_count()>0`）否则 `cpu` | 自动选择 |
| 数字字符串如 `'0'` | 格式化为 `'cuda:0'` | 指定单卡 |
| `'cpu'` / `'cuda'` / `'cuda:N'` | 原样使用 | 显式指定 |
| `'xpu'` | 原样使用 | 导入 `intel_extension_for_pytorch` 并执行 `ipex.optimize` |
| 其他 | — | 抛 `ValueError` |

device 确定后依次执行：`use_fp16=True` 时 `model.half()`；随后 `model.eval()` 并 `model.to(self.device)`；若 `num_gpus>1` 则以 `torch.nn.DataParallel` 包装（F-bc-008）。

**注意 xpu 分支是 EmbeddingModel 独有**——`RerankerModel` 的 device 分支没有 xpu 支持（F-bc-014），两个类在硬件适配上并不对称，详见 [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md) 的对比。

## encode 数据流

```python
encode(
    sentences,
    batch_size=256,
    max_length=512,
    normalize_to_unit=True,
    return_numpy=True,
    enable_tqdm=True,
    query_instruction="",
    **kwargs
)
```

`return_numpy=True` 时返回 numpy ndarray（F-bc-009）。完整数据流如下：

1. **多卡 batch 放大**：`num_gpus>1` 时 `batch_size` 先乘以 `num_gpus`（F-bc-012）。
2. **输入规范化**：`str` 输入先转为单元素 list（F-bc-010）。
3. **指令前缀拼接**：`query_instruction` 为非空字符串时，拼接为每条句子的前缀（F-bc-010）。对 BCE 自家模型应留空——README 声明 "does not need specific instructions"（F-bc-028）；该参数主要为第三方模型（BGE/e5）的适配而设，背景见 [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md)。
4. **分词**：按 batch 调用 `tokenizer(padding=True, truncation=True, max_length=max_length, return_tensors="pt")`，并将输入移至 device（F-bc-010）。`max_length=512` 为默认截断上限。
5. **前向推理**：`self.model(**inputs_on_device, return_dict=True)`。
6. **pooling**（F-bc-011）：
   - `pooler='cls'`：取 `outputs.last_hidden_state[:, 0]`，即首 token（CLS）位置的向量；
   - `pooler='mean'`：按 `attention_mask` 加权平均各 token 向量。
7. **归一化**：`normalize_to_unit=True` 时按行 L2 范数归一化（`embeddings / embeddings.norm(dim=1, keepdim=True)`），归一化后的向量可直接用点积近似余弦相似度（F-bc-011）。
8. **聚合输出**：各 batch 结果 `torch.cat(dim=0)` 后 `.numpy()` 返回（F-bc-011）。

## 典型调用

```python
from BCEmbedding import EmbeddingModel

model = EmbeddingModel(
    model_name_or_path="maidalun1020/bce-embedding-base_v1",
    pooler='cls',            # 官方推荐
    use_fp16=True,           # GPU 上可加速，CPU 上不建议
    device=None,             # 自动选择
)

embeddings = model.encode(
    ['句子一', '句子二'],
    batch_size=256,
    normalize_to_unit=True,  # 默认即为 True
)
# embeddings 为 numpy ndarray，形状 (2, hidden_dim)
```

## 注意事项

- **pooler 是模型语义的一部分**：加载同一权重但改用 `pooler='mean'` 会产生不同分布的向量，自建向量库后不应中途更换 pooler，否则新旧向量不可比。
- **max_length=512 是 token 级截断**（F-bc-010），超长文本在此被静默截断；如需长文档语义，应在外部做分块，而非依赖本类。
- **多卡行为是隐式的**：单条 `device='cuda'`（不指定卡号）且机器多卡时，`num_gpus` 取全部卡数并启用 DataParallel；此时 batch_size 会被自动放大（F-bc-012），显存占用需按 `batch_size × num_gpus` 估算。
- **xpu 依赖需自行安装**：`'xpu'` 分支在构造时才 `import intel_extension_for_pytorch`，未安装该扩展会在构造期抛 `ImportError`，而非安装期报错（F-bc-007）。

## 相关概念

- [/concepts/00-quickstart.md](/concepts/00-quickstart.md) — 安装与三种调用路径
- [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md) — RerankerModel（device 支持不对称的对照）
- [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md) — query_instruction 与指令字典
