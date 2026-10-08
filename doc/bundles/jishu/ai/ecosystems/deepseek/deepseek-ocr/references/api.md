---
type: reference
scope: deepseek-ocr
name: api
description: DeepSeek-OCR 模型类、处理器与图像处理函数 API 参考
---

# DeepSeek-OCR API 参考

本文档描述 DeepSeek-OCR vLLM 推理实现中的核心类与函数。

## 模型类

### DeepseekOCRForCausalLM

vLLM 推理入口类，继承自 `nn.Module`，实现 `SupportsMultiModal` 和 `SupportsPP` 接口。负责视觉编码与语言模型的端到端推理。

```python
class DeepseekOCRForCausalLM(nn.Module, SupportsMultiModal, SupportsPP)
```

**核心组件：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `sam_model` | SAM ViT-B | SAM（Segment Anything）视觉编码器，提取低层视觉特征 |
| `vision_model` | CLIP-L | CLIP Large 视觉编码器，提取高层语义特征 |
| `projector` | MlpProjector | 线性投影层，将 2048 维拼接特征投影至 1280 维语言模型嵌入空间 |
| `language_model` | vLLM registered model | DeepSeek 语言模型（V2/V3 架构，根据配置自动选择） |
| `image_newline` | nn.Parameter | 2D tile 布局中的换行标记嵌入 |
| `view_seperator` | nn.Parameter | 全局视图与局部视图之间的分隔符嵌入 |

**权重映射：**
- 前缀映射：`hf_to_vllm_mapper = WeightsMapper(orig_to_new_prefix={"language.": "language_model."})`
- 视觉相关权重（`sam_model`/`vision_model`/`projector`/`image_newline`/`view_seperator`）去掉 `model.` 前缀
- 语言模型权重添加 `language.` 前缀

**主要方法：**

- `_parse_and_validate_image_input(**kwargs)` — 解析并验证输入的 `pixel_values`、`images_crop`、`images_spatial_crop`
- `_pixel_values_to_embedding(pixel_values, images_crop, images_spatial_crop)` — 将图像张量转换为视觉嵌入
- `_process_image_input(image_input)` — 图像输入处理主入口，调用 `_pixel_values_to_embedding`
- `get_multimodal_embeddings(**kwargs)` — 获取多模态嵌入，供 vLLM 框架调用
- `get_input_embeddings(input_ids, multimodal_embeddings)` — 将视觉嵌入合并到语言模型输入嵌入中
- `forward(input_ids, positions, intermediate_tensors, inputs_embeds, **kwargs)` — 前向传播
- `load_weights(weights)` — 权重加载，处理视觉/语言模型权重映射

### DeepseekOCRProcessingInfo

vLLM 多模态处理信息类，提供 HF 配置、处理器、token 计算等元信息。

```python
class DeepseekOCRProcessingInfo(BaseProcessingInfo)
```

**主要方法：**

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `get_hf_config()` | DeepseekVLV2Config | 获取 HuggingFace 模型配置 |
| `get_hf_processor(**kwargs)` | DeepseekOCRProcessor | 获取图像处理器实例 |
| `get_supported_mm_limits()` | Mapping[str, Optional[int]] | 返回 `{"image": None}`，表示图像数量无上限 |
| `get_num_image_tokens(image_width, image_height, cropping)` | int | 计算给定图像尺寸对应的视觉 token 数 |
| `get_image_size_with_most_features()` | ImageSize | 返回产生最多特征的图像尺寸（640×2 或 1024×2） |

### DeepseekOCRMultiModalProcessor

vLLM 多模态处理器，处理 prompt 替换、图像字段映射、HF 处理器调用等。

```python
class DeepseekOCRMultiModalProcessor(BaseMultiModalProcessor[DeepseekOCRProcessingInfo])
```

**多模态字段配置：**

| 字段 | 配置 |
|---|---|
| `pixel_values` | batched("image") — 全局视图图像张量 |
| `images_spatial_crop` | batched("image") — 裁剪行列数 |
| `images_crop` | batched("image") — 局部视图裁剪块 |

### DeepseekOCRDummyInputsBuilder

构建虚拟输入供 vLLM Profiling 使用。

## 处理器类

### DeepseekOCRProcessor

HuggingFace 兼容的图像处理器，继承自 `ProcessorMixin`，负责图像预处理、动态裁剪、token 化。

```python
class DeepseekOCRProcessor(ProcessorMixin)
```

**核心参数（来自 config.py）：**

| 参数 | 默认值 | 说明 |
|---|---|---|
| `image_size` | 640 | 局部裁剪块尺寸 |
| `base_size` | 1024 | 全局视图基准尺寸 |
| `patch_size` | 16 | ViT patch 大小 |
| `downsample_ratio` | 4 | 视觉特征下采样比例 |
| `image_token` | `<image>` | 图像占位符 token |
| `pad_token` | `<｜▁pad▁｜>` | 填充 token |

**主要方法：**

| 方法 | 说明 |
|---|---|
| `encode(text, bos, eos)` | 文本编码，可选添加 BOS/EOS |
| `decode(t, **kwargs)` | token 解码为文本 |
| `process_one(prompt, images, inference_mode)` | 处理单条样本，返回 input_ids/pixel_values/images_crop 等 |
| `__call__(prompt, images, inference_mode)` | 处理器调用入口，委托给 `process_one` |
| `tokenize_with_images(images, bos, eos, cropping)` | 核心方法：图像预处理 + 动态裁剪 + 构建图像 token 序列 |

**属性：**

| 属性 | 说明 |
|---|---|
| `image_token_id` | `<image>` token 的 ID |
| `bos_id` | BOS token ID |
| `eos_id` | EOS token ID |
| `pad_id` | PAD token ID |
| `image_transform` | ImageTransform 实例，执行 ToTensor + Normalize |

### ImageTransform

图像变换管线，执行 ToTensor 和可选的 Normalize。

```python
class ImageTransform:
    def __init__(self, mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5), normalize=True)
    def __call__(self, pil_img: Image.Image) -> torch.Tensor
```

## 图像处理函数

### count_tiles

```python
def count_tiles(orig_width, orig_height, min_num=2, max_num=6, image_size=640, use_thumbnail=False) -> Tuple[int, int]
```

计算图像的最佳裁剪分块比例（宽×高的 tile 数）。基于宽高比匹配最近的目标宽高比组合，不实际执行裁剪。

**参数：**
- `orig_width`, `orig_height`: 原始图像尺寸
- `min_num`, `max_num`: 最小/最大 tile 数量（默认 2~6）
- `image_size`: 每个 tile 的像素尺寸（默认 640）

**返回值：** `(num_width_tiles, num_height_tiles)` 元组。

### dynamic_preprocess

```python
def dynamic_preprocess(image, min_num=2, max_num=6, image_size=640, use_thumbnail=False) -> Tuple[List[Image.Image], Tuple[int, int]]
```

执行动态裁剪：将图像 resize 到目标尺寸后，按 image_size 分块切割。

**参数：** 同 `count_tiles`，额外接受 PIL Image。

**返回值：**
- `processed_images`: 裁剪后的 PIL Image 列表
- `target_aspect_ratio`: `(width_tiles, height_tiles)` 元组

### find_closest_aspect_ratio

```python
def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size) -> Tuple[int, int]
```

在候选比例集中寻找与给定宽高比最接近的比例。面积相同时优先选择面积利用率更高的比例。

## 编码器组件

### build_sam_vit_b

```python
def build_sam_vit_b() -> nn.Module
```

构建 SAM ViT-B 视觉编码器（来自 `deepencoder/sam_vary_sdpa.py`），使用 SDPA 注意力实现。提取低层视觉特征（SAM 特征维度为 256 或更高，flatten 后拼接）。

### build_clip_l

```python
def build_clip_l() -> nn.Module
```

构建 CLIP-Large 视觉编码器（来自 `deepencoder/clip_sdpa.py`），使用 SDPA 注意力。提取高层语义特征。

### MlpProjector

```python
class MlpProjector(nn.Module):
    def __init__(self, cfg: Dict)
```

线性投影层。DeepSeek-OCR 配置为 `projector_type="linear", input_dim=2048, n_embed=1280`，将 SAM+CLIP 拼接的 2048 维特征投影到 1280 维语言模型维度。

## 配置参数（config.py）

| 参数 | 默认值 | 说明 |
|---|---|---|
| `BASE_SIZE` | 1024 | 全局视图尺寸 |
| `IMAGE_SIZE` | 640 | 局部裁剪块尺寸 |
| `CROP_MODE` | True | 是否启用动态裁剪 |
| `MIN_CROPS` | 2 | 最少裁剪块数 |
| `MAX_CROPS` | 6 | 最多裁剪块数（最大可设 9） |
| `MAX_CONCURRENCY` | 100 | PDF 推理最大并发数 |
| `NUM_WORKERS` | 64 | 图像预处理工作线程数 |
| `MODEL_PATH` | `deepseek-ai/DeepSeek-OCR` | HuggingFace 模型路径 |
| `PROMPT` | `<image>\n<\|grounding\|>Convert the document to markdown.` | 默认推理 prompt |
