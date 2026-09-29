---
type: reference
scope: deepseek-ocr2
name: api
description: DeepSeek-OCR-2 模型类、处理器与编码器 API 参考
---

# DeepSeek-OCR-2 API 参考

本文档描述 DeepSeek-OCR-2 vLLM 推理实现中的核心类与函数，重点标注与 v1 的差异。

## 模型类

### DeepseekOCR2ForCausalLM

vLLM 推理入口类，继承自 `nn.Module`，实现 `SupportsMultiModal` 和 `SupportsPP` 接口。

```python
class DeepseekOCR2ForCausalLM(nn.Module, SupportsMultiModal, SupportsPP)
```

**与 v1（DeepseekOCRForCausalLM）的关键差异：**

| 组件 | v1 (DeepSeek-OCR) | v2 (DeepSeek-OCR-2) |
|---|---|---|
| 高层视觉编码器 | CLIP-L (`build_clip_l`) | Qwen2 Decoder-as-Encoder (`build_qwen2_decoder_as_encoder`) |
| 特征拼接方式 | CLIP 特征 + SAM 特征 concat → 2048 维 | 直接投影 Qwen2 输出 → 896 维 |
| Projector 输入维度 | 2048 | 896 |
| Projector 输出维度 | 1280 | 1280 |
| `image_newline` 参数 | 存在（2D tile 换行标记） | **已移除** |
| 视觉编码范式 | 纯编码器（CLIP 双向注意力） | **Visual Causal Flow**（Qwen2 因果注意力） |

**核心组件：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `sam_model` | SAM ViT-B | SAM 视觉编码器（与 v1 相同），提取低层特征 |
| `qwen2_model` | CustomQwen2Decoder | Qwen2 解码器改造的编码器（D2E），使用混合因果/非因果注意力 |
| `projector` | MlpProjector | 线性投影层，输入维度 896，输出 1280 |
| `language_model` | vLLM registered model | DeepSeek 语言模型 |
| `view_seperator` | nn.Parameter | 全局视图与局部视图分隔符嵌入 |

**权重映射：**
- 视觉权重：`sam_model`/`qwen2_model`/`projector`/`view_seperator` 去掉 `model.` 前缀
- 语言模型权重：添加 `language.` 前缀
- 注意 v2 使用 `qwen2_model` 而非 v1 的 `vision_model`

**主要方法：** 与 v1 接口一致（`_parse_and_validate_image_input`、`_pixel_values_to_embedding`、`_process_image_input`、`get_multimodal_embeddings`、`get_input_embeddings`、`forward`、`load_weights`）。

### 视觉编码流程差异

```
v1: SAM → CLIP-L → concat(CLIP[:,1:], SAM_flatten) → MlpProjector(2048→1280)
v2: SAM → Qwen2-D2E(SAM_features) → MlpProjector(896→1280)
```

v2 的 `_pixel_values_to_embedding` 不再进行 CLIP 和 SAM 特征的拼接，而是将 SAM 特征直接输入 Qwen2 解码器，经因果流处理后直接投影。token 布局中也移除了 `image_newline`，局部特征和全局特征直接展平后拼接。

### DeepseekOCR2ProcessingInfo

与 v1 类似，但关键参数调整：

```python
class DeepseekOCR2ProcessingInfo(BaseProcessingInfo)
```

**差异：**
- 小图判定阈值：v1 为 640px，v2 为 **768px**
- `get_image_size_with_most_features()` 返回 `768×2`（v1 为 `640×2`）
- 视觉 token 计算：v2 全局视图为 `h * w`（不加 1），局部视图为 `(h2*num_h) * (w2*num_w)`（不加 1）

### DeepseekOCR2MultiModalProcessor

与 v1 结构相同，使用 `DeepseekOCR2Processor` 作为 HF 处理器。

### DeepseekOCR2DummyInputsBuilder

与 v1 结构相同，使用 `DeepseekOCR2Processor`。

## 处理器类

### DeepseekOCR2Processor

HuggingFace 兼容的图像处理器。

```python
class DeepseekOCR2Processor(ProcessorMixin)
```

**与 v1（DeepseekOCRProcessor）的差异：**

| 参数 | v1 默认值 | v2 默认值 |
|---|---|---|
| `image_size` | 640 | **768** |
| `base_size` | 1024 | 1024 |
| 小图判定阈值 | 640 | **768** |
| token 序列格式 | 全局包含 `+1`（newline），局部分块包含 `+1` | 移除额外 `+1`，更紧凑 |
| 支持裁剪块范围 | min=2, max=6 | min=2, max=6（max=6 为硬性上限） |

**主要方法：** 与 v1 一致（`encode`、`decode`、`process_one`、`__call__`、`tokenize_with_images`）。

### ImageTransform

与 v1 完全相同。

## 图像处理函数

### count_tiles

```python
def count_tiles(orig_width, orig_height, min_num=2, max_num=6, image_size=768) -> Tuple[int, int]
```

与 v1 逻辑相同，但默认 `image_size=768`。

### dynamic_preprocess

```python
def dynamic_preprocess(image, min_num=2, max_num=6, image_size=768) -> Tuple[List[Image.Image], Tuple[int, int]]
```

与 v1 逻辑相同，但默认 `image_size=768`。

### find_closest_aspect_ratio

与 v1 完全相同。

## 编码器组件

### build_sam_vit_b

与 v1 相同，SAM ViT-B 编码器。

### build_qwen2_decoder_as_encoder

```python
def build_qwen2_decoder_as_encoder() -> CustomQwen2Decoder
```

**v2 新增组件**，将 Qwen2 解码器改造为视觉编码器（D2E: Decoder-to-Encoder）。

```python
class CustomQwen2Decoder(nn.Module):
    def __init__(
        self,
        decoder_layer: int = 24,
        hidden_dimension: int = 896,
        num_attention_heads: int = 14,
        num_key_value_heads: int = 2,
        intermediate_size: int = 4864,
        vocab_size: int = 151936,
        attn_implementation: str = "sdpa",
        ...
    )
```

**核心特点：**
- 基于 Qwen2 解码器架构（24 层，896 隐维，14 头注意力，GQA 2 KV 头）
- 使用 `token_type_ids` 区分非因果（0）和因果（1）注意力区域
- **不支持** flash_attention_2（自定义注意力掩码需要 sdpa/eager）
- 删除了 `embed_tokens` 层，接收 SAM 特征作为输入
- 实现了 Visual Causal Flow：在特征序列中混合使用双向和因果注意力

### MlpProjector

与 v1 类似，但 `input_dim=896`（v1 为 2048），`n_embed=1280`。

## 配置参数（config.py）

| 参数 | v1 默认 | v2 默认 | 说明 |
|---|---|---|---|
| `BASE_SIZE` | 1024 | 1024 | 全局视图尺寸 |
| `IMAGE_SIZE` | 640 | **768** | 局部裁剪块尺寸 |
| `CROP_MODE` | True | True | 动态裁剪 |
| `MAX_CROPS` | 6（max:9） | **6（max:6）** | 最大裁剪块数 |
| `MODEL_PATH` | `deepseek-ai/DeepSeek-OCR` | **`deepseek-ai/DeepSeek-OCR-2`** | 模型路径 |
| `PROMPT` | 支持多种 prompt | 精简为 2 种 | 默认 prompt |
