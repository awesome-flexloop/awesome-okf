---
type: concept
scope: deepseek-ocr2
name: usage-modes
description: DeepSeek-OCR-2 使用模式——HuggingFace 与 vLLM 部署，以及 v1→v2 迁移要点
---

# 使用模式与 v1 对比

DeepSeek-OCR-2 同样支持 HuggingFace Transformers 和 vLLM 两种部署方式，但在架构细节和默认参数上有重要变化。

## 部署模式对比

| 维度 | HuggingFace Transformers | vLLM |
|---|---|---|
| **适用场景** | 快速验证、研究调试 | 高吞吐生产部署、批量 PDF 处理 |
| **模型加载** | `AutoModel.from_pretrained` | `LLM(model="deepseek-ai/DeepSeek-OCR-2")` |
| **推理入口** | `model.infer()` | `llm.generate()` |
| **关键差异** | image_size 默认 768 | 处理器为 DeepseekOCR2Processor |
| **速度** | 串行生成 | PDF 吞吐与 v1 持平 |

## HuggingFace 模式要点

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

res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file='your_image.jpg',
    output_path='./output/',
    base_size=1024,
    image_size=768,      # v2 默认 768（v1 为 640）
    crop_mode=True,
    save_results=True
    # 注意：v2 移除了 test_compress 参数
)
```

## vLLM 模式要点

```python
from vllm import LLM, SamplingParams
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR-2",  # 注意模型名
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
)

image = Image.open("doc.png").convert("RGB")
prompt = "<image>\n<|grounding|>Convert the document to markdown."

outputs = llm.generate(
    [{"prompt": prompt, "multi_modal_data": {"image": image}}],
    SamplingParams(temperature=0.0, max_tokens=8192, skip_special_tokens=False)
)
print(outputs[0].outputs[0].text)
```

### vLLM 脚本

| 脚本 | 用途 |
|---|---|
| `run_dpsk_ocr2_image.py` | 单图流式输出 |
| `run_dpsk_ocr2_pdf.py` | PDF 批量推理 |
| `run_dpsk_ocr2_eval_batch.py` | OmniDocBench v1.5 评测 |

## v1 到 v2 关键差异

### 架构层面

- **高层编码器**：CLIP-L（双向注意力）→ Qwen2-D2E（混合因果/非因果注意力，Visual Causal Flow）
- **特征维度**：2048（SAM+CLIP拼接）→ 896（Qwen2直接输出）
- **布局标记**：image_newline + view_separator → 仅 view_separator（更紧凑）
- **注意力实现**：v2 的 D2E 不支持 flash_attention_2（自定义掩码需要 sdpa）

### 参数层面

| 参数 | v1 | v2 |
|---|---|---|
| 模型路径 | `deepseek-ai/DeepSeek-OCR` | `deepseek-ai/DeepSeek-OCR-2` |
| image_size 默认 | 640 | **768** |
| MAX_CROPS 上限 | 9 | **6** |
| 小图阈值 | ≤640px 不裁剪 | ≤**768**px 不裁剪 |
| Prompt 种类 | 7种 | **2种** |
| test_compress 参数 | 支持 | **已移除** |
| 分辨率模式 | 5种（Tiny/Small/Base/Large/Gundam） | **1种**（动态 0~6×768 + 1×1024） |

### Prompt 简化

v2 只需两种 prompt：

```python
# 文档转 Markdown（默认）
'<image>\n<|grounding|>Convert the document to markdown.'

# 纯文本 OCR（无格式）
'<image>\nFree OCR.'
```

## 升级建议

1. **直接替换**：将模型名从 `DeepSeek-OCR` 改为 `DeepSeek-OCR-2`
2. **调整 image_size**：HF 推理和 config.py 中将 640 改为 768
3. **简化 prompt**：统一使用 markdown 转换 prompt
4. **验证显存**：v2 局部块更大（768 vs 640），注意显存占用
5. **移除 test_compress**：HF 调用中删除该参数
