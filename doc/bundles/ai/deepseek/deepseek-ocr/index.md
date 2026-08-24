---
type: bundle
okf_version: "0.2"
scope: deepseek-ocr
name: deepseek-ocr
version: "1.0.0"
source: https://github.com/deepseek-ai/DeepSeek-OCR
description: DeepSeek-OCR——Contexts Optical Compression 视觉文本压缩 OCR 多模态大模型，基于 SAM+CLIP 双编码器和动态分块策略实现高效文档识别
---

# DeepSeek-OCR

**DeepSeek-OCR**（论文标题：*DeepSeek-OCR: Contexts Optical Compression*）是 DeepSeek 团队发布的开源 OCR 多模态大模型。它从 LLM 中心视角重新审视视觉编码器的设计，通过双编码器（SAM ViT-B + CLIP-L）和动态分块策略（全局缩略图 + 局部高分辨率裁剪块），实现了高效的文档图像文字识别与理解。

- **论文**：arXiv:2510.18234
- **发布时间**：2025年10月20日
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-OCR`
- **作者**：Haoran Wei, Yaofeng Sun, Yukun Li
- **基础架构**：DeepSeek-VL2 + DeepSeek-V2/V3 语言模型

## 核心特性

- **双编码器视觉编码**：SAM ViT-B 提取低层视觉特征 + CLIP-L 提取高层语义特征，拼接后线性投影到语言空间
- **动态分辨率分块（Gundam 模式）**：全局 1024×1024 缩略图 + n×640×640 局部裁剪块，兼顾布局与细节
- **多种推理模式**：支持 Tiny/Small/Base/Large 固定分辨率和 Gundam 动态分辨率
- **两种部署方式**：HuggingFace Transformers 快速上手，vLLM 高吞吐生产部署
- **多任务支持**：文档转 Markdown、纯文本 OCR、图表解析、图像描述、引用定位等

## 快速开始

```python
from transformers import AutoModel, AutoTokenizer
import torch, os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

tokenizer = AutoTokenizer.from_pretrained('deepseek-ai/DeepSeek-OCR', trust_remote_code=True)
model = AutoModel.from_pretrained(
    'deepseek-ai/DeepSeek-OCR',
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
).eval().cuda().to(torch.bfloat16)

res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file='your_image.jpg',
    output_path='./output/',
    base_size=1024, image_size=640, crop_mode=True,
    save_results=True
)
```

## 相关项目

| 项目 | 路径 | 关系 |
|---|---|---|
| DeepSeek-OCR-2 | [/deepseek/deepseek-ocr2/](/ai/deepseek/deepseek-ocr2/) | 升级版，采用 Visual Causal Flow 架构和 Qwen2 解码器编码器 |

## 文档导航

### 核心概念

- [总览](/ai/deepseek/deepseek-ocr/concepts/overview) — DeepSeek-OCR 定位、Contexts Optical Compression 理念、双编码器架构
- [使用模式](/ai/deepseek/deepseek-ocr/concepts/usage-modes) — HuggingFace vs vLLM 部署对比、选择指南

### API 参考

- [API 参考](/ai/deepseek/deepseek-ocr/references/api) — DeepseekOCRForCausalLM、DeepseekOCRProcessor、图像处理函数
- [推理配置与使用指南](/ai/deepseek/deepseek-ocr/references/inference-config) — 分辨率模式、vLLM/HF 配置、Prompt 参考

### 使用示例

- [图片 OCR](/ai/deepseek/deepseek-ocr/examples/image-ocr) — 单图/批量图片 OCR 完整代码
- [PDF OCR](/ai/deepseek/deepseek-ocr/examples/pdf-ocr) — PDF 文档批量推理与性能调优

## 目录结构

```
deepseek-ocr/
├── concepts/              # 核心概念（2 篇）
├── references/            # API/配置参考（2 篇）
├── examples/              # 使用示例（2 篇）
└── index.md               # 本文件
```

```{toctree}
:hidden:

concepts/index
examples/index
references/index
```
