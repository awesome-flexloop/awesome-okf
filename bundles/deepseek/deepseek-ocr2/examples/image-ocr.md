---
type: example
scope: deepseek-ocr2
name: image-ocr
description: 使用 DeepSeek-OCR-2 对图片进行 OCR 识别
---

# 图片 OCR 示例

本文展示如何使用 DeepSeek-OCR-2 对图片进行 OCR 识别。

## HuggingFace 快速开始

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
).eval().cuda().to(torch.bfloat16)

# 文档转 Markdown（默认推荐）
res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file='document.jpg',
    output_path='./output/',
    base_size=1024,
    image_size=768,       # v2 使用 768
    crop_mode=True,
    save_results=True
)

# 纯文本 OCR（忽略布局）
res = model.infer(
    tokenizer,
    prompt="<image>\nFree OCR.",
    image_file='document.jpg',
    output_path='./output/',
    base_size=1024,
    image_size=768,
    crop_mode=True,
    save_results=True
)
```

## vLLM 批量推理

```python
from vllm import LLM, SamplingParams
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR-2",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
)

images = [
    Image.open("doc1.png").convert("RGB"),
    Image.open("doc2.png").convert("RGB"),
]
prompt = "<image>\n<|grounding|>Convert the document to markdown."
inputs = [{"prompt": prompt, "multi_modal_data": {"image": img}} for img in images]

outputs = llm.generate(
    inputs,
    SamplingParams(temperature=0.0, max_tokens=8192, skip_special_tokens=False)
)
for i, out in enumerate(outputs):
    print(f"=== Document {i+1} ===")
    print(out.outputs[0].text)
```

## 与 v1 代码的对比

```python
# v1 代码
model = AutoModel.from_pretrained('deepseek-ai/DeepSeek-OCR', ...)
res = model.infer(tokenizer, prompt=prompt, image_file=img,
                  output_path=out, base_size=1024, image_size=640,
                  crop_mode=True, save_results=True, test_compress=True)

# v2 代码（只需修改 3 处）
model = AutoModel.from_pretrained('deepseek-ai/DeepSeek-OCR-2', ...)  # 1. 模型名
res = model.infer(tokenizer, prompt=prompt, image_file=img,
                  output_path=out, base_size=1024, image_size=768,    # 2. image_size
                  crop_mode=True, save_results=True)                   # 3. 移除 test_compress
```
