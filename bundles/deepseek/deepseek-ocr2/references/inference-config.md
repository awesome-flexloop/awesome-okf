---
type: reference
scope: deepseek-ocr2
name: inference-config
description: DeepSeek-OCR-2 推理配置与使用指南
---

# 推理配置与使用指南

本文档描述 DeepSeek-OCR-2 的推理配置与使用方式，重点标注与 v1 的差异。

## 分辨率模式

DeepSeek-OCR-2 简化为单一动态分辨率模式：

| 模式 | base_size | image_size | crop_mode | 视觉 token 数 |
|---|---|---|---|---|
| **Default（默认）** | 1024 | 768 | True | (0~6)×144 + 256 |

**与 v1 的差异：**
- v1 支持 Tiny/Small/Base/Large 固定分辨率 + Gundam 动态分辨率共 5 种模式
- v2 仅保留动态分辨率模式，默认 image_size 从 640 提升至 **768**
- 视觉 token 计算更紧凑：移除了 `image_newline` 导致的额外 token 开销
- 最大裁剪块数固定为 6（v1 可设为 9）

**视觉 token 计算公式（v2）：**
- 全局视图：`h × w`，其中 `h = w = ceil(1024/16/4)` = 16，即 16×16 = 256 tokens
- 局部视图（n 个 tile）：`(h2 × num_h) × (w2 × num_w)`，其中 `h2 = w2 = ceil(768/16/4)` = 12
- 最终加 1 个 view_separator token

## 环境要求

与 v1 基本一致：
- CUDA 11.8+
- PyTorch 2.6.0 + torchvision 0.21.0
- vLLM 0.8.5
- flash-attn 2.7.3
- Python 3.12.9

## vLLM 推理

### 代码示例

```python
from vllm import LLM, SamplingParams
from process.image_process import DeepseekOCR2Processor  # 注意使用 v2 处理器
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR-2",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
)

image = Image.open("path/to/image.png").convert("RGB")
prompt = "<image>\n<|grounding|>Convert the document to markdown."

model_input = [{"prompt": prompt, "multi_modal_data": {"image": image}}]

sampling_param = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    skip_special_tokens=False,
)

outputs = llm.generate(model_input, sampling_param)
for output in outputs:
    print(output.outputs[0].text)
```

### vLLM 脚本入口

| 脚本 | 用途 |
|---|---|
| `run_dpsk_ocr2_image.py` | 单张图像流式输出 |
| `run_dpsk_ocr2_pdf.py` | PDF 批量推理（速度与 v1 持平） |
| `run_dpsk_ocr2_eval_batch.py` | OmniDocBench v1.5 基准评测 |

### config.py 配置

```python
BASE_SIZE = 1024
IMAGE_SIZE = 768            # v2 默认 768（v1 为 640）
CROP_MODE = True
MIN_CROPS = 2
MAX_CROPS = 6               # v2 固定上限 6
MAX_CONCURRENCY = 100
NUM_WORKERS = 64
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR-2'
INPUT_PATH = '/your/image/path/'
OUTPUT_PATH = '/your/output/path/'
PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'
```

## HuggingFace 推理

```python
from transformers import AutoModel, AutoTokenizer
import torch, os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

model_name = 'deepseek-ai/DeepSeek-OCR-2'
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
)
model = model.eval().cuda().to(torch.bfloat16)

prompt = "<image>\n<|grounding|>Convert the document to markdown. "
res = model.infer(
    tokenizer,
    prompt=prompt,
    image_file='your_image.jpg',
    output_path='your/output/dir',
    base_size=1024,
    image_size=768,         # v2 使用 768
    crop_mode=True,
    save_results=True
)
```

### model.infer() 参数差异

| 参数 | v1 | v2 |
|---|---|---|
| `image_size` 默认值 | 640 | **768** |
| `test_compress` 参数 | 支持 | **已移除** |

## Prompt 参考

v2 精简了 prompt 选项，主要支持两种：

| 场景 | Prompt |
|---|---|
| 文档转 Markdown | `<image>\n<\|grounding\|>Convert the document to markdown.` |
| 纯文本 OCR | `<image>\nFree OCR.` |

v1 中的 `OCR this image.`、`Parse the figure.`、`Describe this image in detail.`、`Locate` 等 prompt 在 v2 中未在 README 中列出，可能通过默认 markdown prompt 统一处理。

## v1 到 v2 迁移指南

1. **模型路径**：从 `deepseek-ai/DeepSeek-OCR` 改为 `deepseek-ai/DeepSeek-OCR-2`
2. **image_size 参数**：从 640 改为 768（HF `model.infer()` 和 config.py 均需修改）
3. **NGramLogitsProcessor**：v2 官方示例未提及 `NGramPerReqLogitsProcessor`，但如有表格重复问题仍可尝试使用
4. **Prompt**：使用精简后的两种 prompt，不再需要 grounding 相关的复杂 prompt
5. **分辨率模式**：v2 无需选择模式，默认动态分辨率即最佳配置
6. **test_compress**：HF 推理中移除了 `test_compress` 参数
