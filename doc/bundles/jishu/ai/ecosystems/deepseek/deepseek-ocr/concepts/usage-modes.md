---
type: concept
scope: deepseek-ocr
name: usage-modes
description: DeepSeek-OCR 两种推理部署模式——HuggingFace Transformers 与 vLLM 的对比与选择
---

# 使用模式：HuggingFace vs vLLM

DeepSeek-OCR 提供两种推理部署方式，分别面向不同的使用场景。

## 对比总览

| 维度 | HuggingFace Transformers | vLLM |
|---|---|---|
| **适用场景** | 快速原型、单图调试、研究 | 高吞吐生产部署、批量处理、PDF 推理 |
| **吞吐量** | 低（串行生成） | 高（~2500 tokens/s on A100-40G for PDF） |
| **安装复杂度** | 简单（pip install transformers） | 需要特定 vLLM whl 包 |
| **批处理** | 有限支持 | 原生支持 continuous batching |
| **流式输出** | 需自行实现 | 内置支持 |
| **NGram 去重** | 模型内置 | 需额外 LogitsProcessor |
| **代码入口** | `model.infer()` | `LLM.generate()` |

## HuggingFace Transformers 模式

### 架构特点

HF 模式使用模型自带的 `infer()` 方法，内部集成了完整的图像处理 pipeline：

1. **图像加载与预处理**：直接在模型内部完成，包括动态裁剪、全局/局部视图构建
2. **视觉编码**：SAM + CLIP 双编码器前向传播
3. **自回归生成**：使用 HuggingFace generate API，支持 `flash_attention_2`
4. **结果后处理**：可选保存为 Markdown 文件

### 适用场景

- 初次体验和功能验证
- 单张/少量图片的 OCR 任务
- 学术研究和模型微调
- 本地开发调试

### 关键参数

```python
model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file="path/to/image.jpg",
    output_path="output/dir",
    base_size=1024,      # 全局视图尺寸
    image_size=640,      # 局部块尺寸
    crop_mode=True,      # 动态裁剪
    save_results=True,   # 保存结果
    test_compress=True   # 测试压缩率
)
```

## vLLM 模式

### 架构特点

vLLM 模式将 DeepSeek-OCR 注册为 vLLM 多模态模型，获得生产级推理能力：

1. **PagedAttention**：高效 KV Cache 管理，支持长上下文
2. **Continuous Batching**：动态批处理，吞吐量显著提升
3. **多模态 Processor**：自定义 `DeepseekOCRMultiModalProcessor` 处理图像输入
4. **NGram 重复抑制**：通过 `NGramPerReqLogitsProcessor` 防止表格中 `<td>` 等标签重复
5. **Prefix Caching 禁用**：`enable_prefix_caching=False`，避免多模态场景缓存问题

### 适用场景

- PDF 文档批量 OCR
- 高并发 API 服务部署
- 基准评测（OmniDocBench 等）
- 需要流式输出的应用

### 关键配置

```python
llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,        # 必须禁用
    mm_processor_cache_gb=0,           # 禁用处理器缓存
    logits_processors=[NGramPerReqLogitsProcessor]  # 防重复
)

sampling_param = SamplingParams(
    temperature=0.0,                   # OCR 任务使用贪心解码
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,                # N-gram 窗口大小
        window_size=90,                # 检测窗口大小
        whitelist_token_ids={128821, 128822},  # <td>, </td> 白名单
    ),
    skip_special_tokens=False,         # 保留特殊 token
)
```

### vLLM 脚本模式

仓库提供三个现成脚本：

| 脚本 | 输入 | 输出 | 特点 |
|---|---|---|---|
| `run_dpsk_ocr_image.py` | 单张图片路径 | 流式文本 | 交互式 |
| `run_dpsk_ocr_pdf.py` | PDF 文件路径 | JSONL 结果 | ~2500 tokens/s 并发 |
| `run_dpsk_ocr_eval_batch.py` | 评测集目录 | 评测结果 | 批量 benchmark |

使用前需在 `config.py` 中设置 `INPUT_PATH` 和 `OUTPUT_PATH`。

## 模式选择建议

```
快速试用/单图处理
    └──→ HuggingFace transformers（model.infer()）

批量 PDF/高吞吐/API 服务
    └──→ vLLM（LLM.generate() + NGramPerReqLogitsProcessor）

学术研究/微调实验
    └──→ HuggingFace transformers（灵活控制）
```

## 注意事项

1. **vLLM 与 Transformers 环境兼容**：vLLM 0.8.5 要求 transformers>=4.51.1，但 HF 代码固定使用 transformers==4.46.3。如需同一环境运行两者，可忽略版本冲突警告
2. **显存管理**：Gundam 模式（6 个裁剪块）峰值显存较高，可通过降低 `MAX_CROPS`（如设为 4）或 `MAX_CONCURRENCY` 减少显存占用
3. **Prompt 格式**：HF 模式和 vLLM 模式的 prompt 格式一致，均以 `<image>` 开头后跟任务指令
