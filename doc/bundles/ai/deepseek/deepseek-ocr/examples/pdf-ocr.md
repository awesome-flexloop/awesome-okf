---
type: example
scope: deepseek-ocr
name: pdf-ocr
description: 使用 DeepSeek-OCR 对 PDF 文档进行批量 OCR 处理
---

# PDF OCR 示例

本文展示如何使用 DeepSeek-OCR 对 PDF 文档进行批量 OCR 处理。

## 前置条件

- 已安装 vLLM 环境（推荐用于 PDF 批量处理）
- 安装 PyMuPDF（`pip install PyMuPDF`）用于 PDF 转图像
- A100-40G 或同等显存 GPU（vLLM PDF 推理可达 ~2500 tokens/s）

## 方式一：使用官方脚本（推荐）

### 1. 修改配置文件

编辑 `DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py`：

```python
# 设置输入输出路径
INPUT_PATH = '/path/to/your/document.pdf'
OUTPUT_PATH = '/path/to/output/dir/'

# 根据显存调整并发
MAX_CONCURRENCY = 100  # 显存不足时降低此值（如 50）
MAX_CROPS = 6          # 最大裁剪块数（显存不足时降至 4）

# 设置 Prompt
PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'
```

### 2. 运行 PDF 推理脚本

```bash
cd DeepSeek-OCR-master/DeepSeek-OCR-vllm
python run_dpsk_ocr_pdf.py
```

输出为 JSONL 格式，每页结果包含识别出的文本内容。

## 方式二：自定义 PDF 处理流程

如果需要更灵活的 PDF 处理控制，可以自行编写脚本：

```python
import fitz  # PyMuPDF
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image
import io

# 初始化 vLLM 模型
llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

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

# PDF 转图像
def pdf_to_images(pdf_path, dpi=200):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        images.append(img)
    doc.close()
    return images

# 批量 OCR
pdf_path = "document.pdf"
images = pdf_to_images(pdf_path)

prompt = "<image>\n<|grounding|>Convert the document to markdown."
inputs = [{"prompt": prompt, "multi_modal_data": {"image": img}} for img in images]

# 分批推理（避免显存溢出）
batch_size = 4
all_results = []
for i in range(0, len(inputs), batch_size):
    batch = inputs[i:i+batch_size]
    outputs = llm.generate(batch, sampling_params)
    for j, output in enumerate(outputs):
        page_num = i + j + 1
        text = output.outputs[0].text
        all_results.append({"page": page_num, "text": text})
        print(f"Page {page_num} done")

# 保存结果
with open("output.jsonl", "w", encoding="utf-8") as f:
    for result in all_results:
        import json
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
```

## 性能调优建议

### 吞吐量优化

| 参数 | 默认值 | 调优建议 |
|---|---|---|
| `MAX_CONCURRENCY` | 100 | A100-40G 可用 100；24GB 显存建议 30~50 |
| `MAX_CROPS` | 6 | 标准文档 6 足够；简单文档可降至 4 提升速度 |
| `NUM_WORKERS` | 64 | 图像预处理线程数，CPU 核数充足时可保持默认 |
| `batch_size`（自定义脚本） | - | 根据显存调整，建议 2~8 |

### 质量优化

- **高分辨率扫描件**：将 dpi 提升至 300，使用 `CROP_MODE=True` + `MAX_CROPS=9`
- **简单文本文档**：使用 `Free OCR.` prompt 代替 markdown 转换 prompt，速度更快
- **表格密集型文档**：务必使用 `NGramPerReqLogitsProcessor` 防止 `<td>` 标签重复
- **多语言文档**：默认模型支持中英文，其他语言建议测试后使用

## 常见问题

1. **显存溢出**：降低 `MAX_CONCURRENCY` 或 `MAX_CROPS`；使用更小的分辨率模式
2. **表格识别错乱**：确保启用 `NGramPerReqLogitsProcessor`，设置 `whitelist_token_ids={128821, 128822}`
3. **PDF 页面模糊**：提高 PyMuPDF 渲染 DPI（默认 200，可尝试 300）
4. **输出被截断**：增大 `max_tokens`（默认 8192，复杂页面可设为 16384）
