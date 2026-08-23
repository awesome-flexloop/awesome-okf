---
type: example
scope: deepseek-ocr
name: image-ocr
description: 使用 DeepSeek-OCR 对图片进行 OCR 识别的完整示例
---

# 图片 OCR 示例

本文展示如何使用 DeepSeek-OCR 对单张图片进行 OCR 识别。

## 前置条件

- 已安装 PyTorch 2.6.0 (CUDA 11.8)
- GPU 显存 ≥ 16GB（Gundam 模式）
- 模型已下载或可通过 HuggingFace 自动下载

## 方式一：HuggingFace 快速推理

```python
from transformers import AutoModel, AutoTokenizer
import torch
import os

os.environ["CUDA_VISIBLE_DEVICES"] = '0'

# 加载模型和分词器
model_name = 'deepseek-ai/DeepSeek-OCR'
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
)
model = model.eval().cuda().to(torch.bfloat16)

# 文档转 Markdown
prompt = "<image>\n<|grounding|>Convert the document to markdown. "
result = model.infer(
    tokenizer,
    prompt=prompt,
    image_file='document.jpg',
    output_path='./output/',
    base_size=1024,
    image_size=640,
    crop_mode=True,
    save_results=True
)
print(result)
```

## 方式二：vLLM 批量推理

```python
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image

# 初始化模型
llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

# 准备批量输入
image_1 = Image.open("doc1.png").convert("RGB")
image_2 = Image.open("doc2.png").convert("RGB")
prompt = "<image>\nFree OCR."

inputs = [
    {"prompt": prompt, "multi_modal_data": {"image": image_1}},
    {"prompt": prompt, "multi_modal_data": {"image": image_2}},
]

# 推理参数
sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,
        window_size=90,
        whitelist_token_ids={128821, 128822},
    ),
    skip_special_tokens=False,
)

# 执行推理
outputs = llm.generate(inputs, sampling_params)
for i, output in enumerate(outputs):
    print(f"=== Image {i+1} ===")
    print(output.outputs[0].text)
```

## 不同任务的 Prompt 选择

```python
# 场景1：文档识别（带格式转 Markdown）
prompt = "<image>\n<|grounding|>Convert the document to markdown. "

# 场景2：纯文本提取（忽略布局）
prompt = "<image>\nFree OCR. "

# 场景3：通用图像文字识别
prompt = "<image>\n<|grounding|>OCR this image. "

# 场景4：图表/图形解析
prompt = "<image>\nParse the figure. "

# 场景5：详细图像描述
prompt = "<image>\nDescribe this image in detail. "
```

## 分辨率模式选择

```python
# 小图片（≤640px）- 快速模式
result = model.infer(tokenizer, prompt=prompt, image_file=img,
                     output_path=out, base_size=640, image_size=640,
                     crop_mode=False)

# 标准文档 - Gundam 模式（默认推荐）
result = model.infer(tokenizer, prompt=prompt, image_file=img,
                     output_path=out, base_size=1024, image_size=640,
                     crop_mode=True)

# 大分辨率文档 - Large 模式（显存需求更高）
result = model.infer(tokenizer, prompt=prompt, image_file=img,
                     output_path=out, base_size=1280, image_size=1280,
                     crop_mode=False)
```
