---
type: bundle
okf_version: "0.2"
scope: deepseek-ocr2
name: deepseek-ocr2
version: "2.0.0"
source: https://github.com/deepseek-ai/DeepSeek-OCR-2
description: DeepSeek-OCR-2——Visual Causal Flow 视觉因果流 OCR 模型，采用 Qwen2 解码器改造编码器（D2E），实现类人视觉编码
---

# DeepSeek-OCR-2

**DeepSeek-OCR-2**（论文标题：*DeepSeek-OCR 2: Visual Causal Flow*）是 DeepSeek-OCR 的升级版，于 2026 年 1 月发布。核心创新是**视觉因果流（Visual Causal Flow）**机制——使用 Qwen2 解码器改造为视觉编码器（D2E: Decoder-to-Encoder），通过混合因果/非因果注意力实现更接近人类视觉处理的编码方式。

- **论文**：arXiv:2601.20552
- **发布时间**：2026年1月27日
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-OCR-2`
- **作者**：Haoran Wei, Yaofeng Sun, Yukun Li

## v1 → v2 核心改进

| 维度 | v1 (DeepSeek-OCR) | v2 (DeepSeek-OCR-2) |
|---|---|---|
| 视觉编码理念 | Contexts Optical Compression | **Visual Causal Flow** |
| 高层编码器 | CLIP-L（双向注意力） | **Qwen2-D2E**（混合因果/非因果注意力） |
| 特征维度 | 2048（SAM+CLIP拼接） | **896**（Qwen2单流输出） |
| 局部块尺寸 | 640×640 | **768×768** |
| 布局标记 | image_newline + view_separator | **仅 view_separator**（更紧凑） |
| 分辨率模式 | 5种 | **1种**（动态 0~6×768 + 1×1024） |
| Prompt 种类 | 7种 | **2种** |

## 核心特性

- **Visual Causal Flow**：Qwen2 解码器改造的 D2E 编码器，通过 token_type_ids 切换因果/非因果注意力，模拟人类阅读的序列化视觉处理
- **更高效的特征投影**：896 维直接投影至 1280 维（v1 为 2048→1280），减少参数量
- **更紧凑的视觉 token**：移除 image_newline 标记，token 序列更高效
- **更高的局部分辨率**：768×768 局部块（v1 为 640×640），细节识别更清晰
- **简化的使用方式**：单一动态分辨率模式，两种核心 prompt，开箱即用

## 快速开始

```python
from transformers import AutoModel, AutoTokenizer
import torch, os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

tokenizer = AutoTokenizer.from_pretrained('deepseek-ai/DeepSeek-OCR-2', trust_remote_code=True)
model = AutoModel.from_pretrained(
    'deepseek-ai/DeepSeek-OCR-2',
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
).eval().cuda().to(torch.bfloat16)

res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file='your_image.jpg',
    output_path='./output/',
    base_size=1024, image_size=768, crop_mode=True,
    save_results=True
)
```

## 相关项目

| 项目 | 路径 | 关系 |
|---|---|---|
| DeepSeek-OCR v1 | [/deepseek/deepseek-ocr/](/deepseek/deepseek-ocr/) | 前代版本，基于 CLIP 双编码器架构 |

## 文档导航

### 核心概念

- [总览](/deepseek/deepseek-ocr2/concepts/overview) — Visual Causal Flow 架构、Qwen2-D2E 设计、与 v1 的详细对比
- [使用模式与 v1 对比](/deepseek/deepseek-ocr2/concepts/usage-modes) — HF/vLLM 部署、v1→v2 迁移指南

### API 参考

- [API 参考](/deepseek/deepseek-ocr2/references/api) — DeepseekOCR2ForCausalLM、CustomQwen2Decoder、处理器类
- [推理配置](/deepseek/deepseek-ocr2/references/inference-config) — 分辨率模式、vLLM/HF 配置、迁移要点

### 使用示例

- [图片 OCR](/deepseek/deepseek-ocr2/examples/image-ocr) — HF/vLLM 图片推理代码
- [PDF OCR](/deepseek/deepseek-ocr2/examples/pdf-ocr) — PDF 批量推理

## 目录结构

```
deepseek-ocr2/
├── concepts/              # 核心概念（2 篇）
├── references/            # API/配置参考（2 篇）
├── examples/              # 使用示例（2 篇）
└── index.md               # 本文件
```
