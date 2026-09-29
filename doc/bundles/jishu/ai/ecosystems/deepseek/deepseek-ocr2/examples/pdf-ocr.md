---
type: example
scope: deepseek-ocr2
name: pdf-ocr
description: 使用 DeepSeek-OCR-2 对 PDF 文档进行批量 OCR 处理
---

# PDF OCR 示例

本文展示如何使用 DeepSeek-OCR-2 对 PDF 文档进行批量 OCR。

## 使用官方脚本

### 1. 修改配置文件

编辑 `DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/config.py`：

```python
BASE_SIZE = 1024
IMAGE_SIZE = 768              # v2 为 768（v1 为 640）
CROP_MODE = True
MIN_CROPS = 2
MAX_CROPS = 6                 # v2 上限为 6
MAX_CONCURRENCY = 100
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR-2'  # 注意模型名

INPUT_PATH = '/path/to/document.pdf'
OUTPUT_PATH = '/path/to/output/'

PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'
```

### 2. 运行 PDF 推理

```bash
cd DeepSeek-OCR2-master/DeepSeek-OCR2-vllm
python run_dpsk_ocr2_pdf.py
```

吞吐量约为 ~2500 tokens/s（A100-40G，与 v1 持平）。

## 自定义 PDF 处理

```python
import fitz  # PyMuPDF
from vllm import LLM, SamplingParams
from PIL import Image
import io, json

# 初始化 vLLM
llm = LLM(
    model="deepseek-ai/DeepSeek-OCR-2",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
)

params = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    skip_special_tokens=False,
)

# PDF 转图像
def pdf_to_images(pdf_path, dpi=200):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        images.append(img)
    doc.close()
    return images

# 批量处理
images = pdf_to_images("document.pdf", dpi=200)
prompt = "<image>\n<|grounding|>Convert the document to markdown."
inputs = [{"prompt": prompt, "multi_modal_data": {"image": img}} for img in images]

batch_size = 4  # v2 局部块更大，适当减小 batch_size
results = []
for i in range(0, len(inputs), batch_size):
    batch = inputs[i:i+batch_size]
    outputs = llm.generate(batch, params)
    for j, out in enumerate(outputs):
        results.append({"page": i+j+1, "text": out.outputs[0].text})

with open("output.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
```

## 注意事项

- v2 的 image_size 为 768（比 v1 的 640 大），相同数量裁剪块下显存占用略高
- 如遇显存不足，降低 `MAX_CONCURRENCY` 或 `batch_size`
- v2 简化了 prompt，统一使用 markdown 转换即可
