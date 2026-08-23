---
type: reference
scope: deepseek-ocr
name: inference-config
description: DeepSeek-OCR vLLM 推理配置与 HuggingFace 使用指南
---

# 推理配置与使用指南

本文档描述 DeepSeek-OCR 的两种推理方式（vLLM 与 HuggingFace Transformers）的配置与使用方法。

## 分辨率模式

DeepSeek-OCR 支持固定分辨率和动态分辨率两种模式：

| 模式名称 | base_size | image_size | crop_mode | 视觉 token 数 | 说明 |
|---|---|---|---|---|---|
| Tiny | 512 | 512 | False | 64 | 最小分辨率，适合简单场景 |
| Small | 640 | 640 | False | 100 | 小分辨率 |
| Base | 1024 | 1024 | False | 256 | 基准分辨率 |
| Large | 1280 | 1280 | False | 400 | 大分辨率 |
| **Gundam（默认）** | 1024 | 640 | True | n×144+256 | 动态分辨率，0~6 个 640×640 局部块 + 1 个 1024×1024 全局视图 |

**视觉 token 计算公式（Gundam 模式）：**
- 全局视图：`h × (w+1)`，其中 `h = w = ceil(base_size/patch_size/downsample_ratio)` = 16，即 16×17 = 272 tokens
- 局部视图（n 个 tile）：`(num_h × h2) × (num_w × w2 + 1)`，其中 `h2 = w2 = ceil(image_size/patch_size/downsample_ratio)` = 10
- 最终加 1 个 view_separator token

## vLLM 推理配置

### 环境要求

- CUDA 11.8+
- PyTorch 2.6.0 + torchvision 0.21.0
- vLLM 0.8.5（推荐使用官方 whl 包）
- flash-attn 2.7.3
- Python 3.12.9

### 安装步骤

```bash
conda create -n deepseek-ocr python=3.12.9 -y
conda activate deepseek-ocr
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl
pip install -r requirements.txt
pip install flash-attn==2.7.3 --no-build-isolation
```

### 上游 vLLM（2025/10/23 后）

```bash
uv venv && source .venv/bin/activate
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

### vLLM 代码示例

```python
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

image = Image.open("path/to/image.png").convert("RGB")
prompt = "<image>\nFree OCR."

model_input = [{"prompt": prompt, "multi_modal_data": {"image": image}}]

sampling_param = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,
        window_size=90,
        whitelist_token_ids={128821, 128822},  # <td>, </td>
    ),
    skip_special_tokens=False,
)

outputs = llm.generate(model_input, sampling_param)
for output in outputs:
    print(output.outputs[0].text)
```

### vLLM 脚本入口

| 脚本 | 用途 | 吞吐量 |
|---|---|---|
| `run_dpsk_ocr_image.py` | 单张图像流式输出 | 交互式 |
| `run_dpsk_ocr_pdf.py` | PDF 批量推理 | ~2500 tokens/s (A100-40G) |
| `run_dpsk_ocr_eval_batch.py` | 基准评测批量推理 | 最高吞吐 |

### config.py 关键配置项

```python
BASE_SIZE = 1024          # 全局视图尺寸
IMAGE_SIZE = 640          # 局部裁剪块尺寸
CROP_MODE = True          # 启用动态裁剪
MIN_CROPS = 2             # 最少裁剪块
MAX_CROPS = 6             # 最多裁剪块（GPU 显存不足时降低此值）
MAX_CONCURRENCY = 100     # PDF 并发数（显存不足时降低）
NUM_WORKERS = 64          # 图像预处理线程数
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR'
INPUT_PATH = ''           # 输入路径（PDF/图片/评测集）
OUTPUT_PATH = ''          # 输出路径
PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'
```

## HuggingFace Transformers 推理

### 代码示例

```python
from transformers import AutoModel, AutoTokenizer
import torch
import os

os.environ["CUDA_VISIBLE_DEVICES"] = '0'
model_name = 'deepseek-ai/DeepSeek-OCR'

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
)
model = model.eval().cuda().to(torch.bfloat16)

prompt = "<image>\n<|grounding|>Convert the document to markdown. "
image_file = 'your_image.jpg'
output_path = 'your/output/dir'

res = model.infer(
    tokenizer,
    prompt=prompt,
    image_file=image_file,
    output_path=output_path,
    base_size=1024,
    image_size=640,
    crop_mode=True,
    save_results=True,
    test_compress=True
)
```

### model.infer() 参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `tokenizer` | AutoTokenizer | 必填 | 分词器实例 |
| `prompt` | str | 必填 | 推理 prompt，须包含 `<image>` |
| `image_file` | str | 必填 | 图像文件路径 |
| `output_path` | str | 必填 | 结果输出目录 |
| `base_size` | int | 1024 | 全局视图基准尺寸 |
| `image_size` | int | 640 | 局部裁剪块尺寸 |
| `crop_mode` | bool | True | 是否启用动态裁剪 |
| `save_results` | bool | False | 是否保存结果到文件 |
| `test_compress` | bool | False | 是否测试压缩率 |

## Prompt 参考

| 场景 | Prompt |
|---|---|
| 文档转 Markdown | `<image>\n<\|grounding\|>Convert the document to markdown.` |
| 通用 OCR | `<image>\n<\|grounding\|>OCR this image.` |
| 纯文本 OCR（无布局） | `<image>\nFree OCR.` |
| 图表解析 | `<image>\nParse the figure.` |
| 图像描述 | `<image>\nDescribe this image in detail.` |
| 定位引用 | `<image>\nLocate <\|ref\|>xxxx<\|/ref\|> in the image.` |

## 依赖列表（requirements.txt）

| 包 | 版本 |
|---|---|
| transformers | 4.46.3 |
| tokenizers | 0.20.3 |
| PyMuPDF | - |
| img2pdf | - |
| einops | - |
| easydict | - |
| addict | - |
| Pillow | - |
| numpy | - |
