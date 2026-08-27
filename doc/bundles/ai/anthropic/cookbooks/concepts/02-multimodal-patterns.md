---
type: concept
title: "多模态模式"
description: "Claude Vision 能力实践模式：图片输入最佳实践、图表/PPT 解读、OCR 表单文字提取、PDF 处理、多模态提示词技巧等 Cookbook 中的视觉处理方案。"
tags: [multimodal, vision, ocr, pdf, images, charts, powerpoint, image-generation]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# 多模态模式

Claude 的多模态（Multimodal）能力——特别是 Vision（视觉）——让它不仅能处理文本，还能"看懂"图片、图表、PDF、PPT 等视觉内容。Cookbooks 提供了从基础视觉入门到高级应用的完整示例，本文档提炼其中的可复用模式。

与 SDK 文档侧重 API 参数不同，本文聚焦于**实践层面的方法论**：什么样的图片效果好、如何提示 Claude 解读图表、OCR 的最佳实践、PDF 处理流程等。

## Vision 能力概述

Claude 的 Vision 能做什么？Cookbooks 覆盖的场景包括：

| 能力 | 说明 | 代表 Cookbook |
|------|------|--------------|
| 图片内容理解 | 描述图片中的物体、场景、人物 | Vision 入门 |
| 图表/数据可视化解读 | 看懂柱状图、折线图、饼图、散点图 | 图表解读 |
| 文档 OCR | 提取图片中的印刷/手写文字 | 表单/文字提取 |
| PPT/幻灯片理解 | 解读幻灯片内容、结构、要点 | PPT 解读 |
| 表单/票据识别 | 识别发票、收据、表格中的结构化信息 | 表单提取 |
| PDF 文档问答 | 上传 PDF 并基于内容回答问题 | PDF 上传与解析 |
| UI 截图分析 | 理解网页/APP 界面、发现 UI 问题 | Vision 最佳实践 |
| 图片生成配合 | 生成 Stable Diffusion 提示词 | 图片生成集成 |

### 支持的图片格式

| 格式 | MIME 类型 | 推荐 |
|------|----------|------|
| JPEG/JPG | `image/jpeg` | ✅ 首选，照片类 |
| PNG | `image/png` | ✅ 首选，截图/图表/文字类 |
| GIF | `image/gif` | ⚠️ 仅第一帧 |
| WebP | `image/webp` | ✅ 支持 |
| BMP | `image/bmp` | ❌ 不推荐，转 PNG |

> 💡 **实践建议**：照片用 JPEG（更小），文字/图表/截图用 PNG（无损清晰）。

## 图片输入最佳实践

### 图片大小与质量

Cookbooks 中的经验总结：

| 维度 | 建议 | 原因 |
|------|------|------|
| **分辨率** | 最长边 1568px 左右最佳 | Claude 会自动缩放，太大浪费 token |
| **文件大小** | 建议 < 5MB | 太大上传慢，且没有明显质量收益 |
| **文字清晰度** | 文字高度至少 20px | 小于这个值 OCR 准确率显著下降 |
| **裁剪** | 只保留相关区域 | 减少干扰信息，提高准确率 |
| **对比度** | 确保文字和背景有足够对比度 | 浅色文字在浅色背景上识别率低 |

### 图片输入的两种方式

Cookbooks 展示了两种传图方式，根据场景选择：

**方式一：base64 编码嵌入（推荐，简单场景）**

```python
import base64
from anthropic import Anthropic

client = Anthropic()

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

# 读取图片
image_data = encode_image("chart.png")
media_type = "image/png"  # 根据实际格式调整

response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                },
            },
            {
                "type": "text",
                "text": "请描述这张图片中的内容。"
            }
        ],
    }]
)
```

**方式二：URL 方式（图片已在网络上）**

```python
response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "https://example.com/chart.png"
                }
            },
            {
                "type": "text",
                "text": "解读这个图表。"
            }
        ]
    }]
)
```

> ⚠️ URL 方式要求图片可公开访问，无需认证。

## 模式一：图表/PPT 解读模式

**适用场景**：让 Claude 看懂数据可视化图表（柱状图、折线图、饼图等）、PPT 幻灯片，提取关键信息和洞察。

### 提示词框架

Cookbook 中效果最好的图表解读提示词结构：

```python
def analyze_chart_prompt(chart_type: str = "自动识别") -> str:
    return f"""请分析这张{chart_type}图表，按以下结构输出：

1. **图表主题**：这张图表是关于什么的？标题和主要结论是什么？
2. **坐标轴/图例**：X轴、Y轴分别代表什么？单位是什么？图例说明是什么？
3. **关键数据点**：
   - 最大值是多少？在什么位置/时间？
   - 最小值是多少？在什么位置/时间？
   - 是否有明显的异常值或拐点？
4. **趋势分析**：整体趋势是上升、下降还是平稳？是否有周期性？
5. **关键洞察**：从这张图可以得出哪些重要结论？（至少3点）
6. **数据局限性**：这张图有没有可能误导人的地方？缺失什么信息？

请尽量引用具体数值，不要泛泛而谈。"""
```

### PPT 解读的特殊处理

PPT 通常有多页，需要逐页处理：

```python
def analyze_ppt_slide(slide_image_path: str, slide_number: int, total_slides: int) -> str:
    """分析单页 PPT"""
    prompt = f"""这是演示文稿的第 {slide_number}/{total_slides} 页。

请提取：
1. **页面标题**：本页的核心主题
2. **核心要点**：页面上的所有 bullet points 和关键文字（尽量准确还原）
3. **视觉元素**：有什么图表、图片、表格？它们想表达什么？
4. **页面逻辑**：这页在整个演示中起什么作用？（背景/论点/数据/结论）

如果页面有表格，请以 Markdown 表格形式还原数据。"""

    # 调用 Vision API
    return call_vision_api(slide_image_path, prompt)
```

### 提高图表解读准确率的技巧

Cookbook 中验证过的技巧：

1. **指定图表类型**：如果知道是柱状图就说"柱状图"，比"这张图"准确率高
2. **要求引用数值**：明确要求"不要只说'增长很多'，要说'从 X 增长到 Y，增长了 Z%'"
3. **让 Claude 找异常**："有什么数据点看起来不符合整体趋势？"
4. **分步骤提问**：先问基础数据，再问洞察，不要一次问太多
5. **高清图片**：图表文字一定要清晰，模糊的数字会被看错

## 模式二：OCR / 表单提取模式

**适用场景**：从图片中提取文字，特别是结构化的表单、发票、收据、身份证、表格等。

### 通用 OCR 提示词

```python
OCR_PROMPT = """请对这张图片进行 OCR（光学字符识别），提取其中的所有文字。

要求：
1. 按原文顺序提取所有可见文字，包括标题、正文、注释、页码
2. 保持原有排版结构（段落、列表、标题层级）
3. 如果有表格，使用 Markdown 表格格式还原
4. 如果有印章、手写签名，标注[印章]、[签名]
5. 看不清楚的文字标注[模糊]，不要猜测
6. 不要添加图片中没有的内容，也不要省略任何可见文字"""
```

### 结构化表单提取（关键模式）

对于发票、收据等结构化表单，**不要只做 OCR**——直接让 Claude 提取结构化 JSON：

```python
EXTRACT_INVOICE_PROMPT = """请从这张发票图片中提取以下信息，以 JSON 格式返回：

{
  "invoice_number": "发票号码",
  "invoice_date": "开票日期（YYYY-MM-DD）",
  "seller": {
    "name": "销售方名称",
    "tax_id": "纳税人识别号"
  },
  "buyer": {
    "name": "购买方名称",
    "tax_id": "纳税人识别号"
  },
  "items": [
    {
      "name": "商品/服务名称",
      "quantity": 数量,
      "unit_price": 单价,
      "amount": 金额,
      "tax_rate": "税率"
    }
  ],
  "total_amount": "价税合计",
  "total_tax": "税额合计"
}

只返回 JSON，不要其他解释。数值字段使用数字类型，不要用字符串。"""
```

配合 JSON 模式使用效果最佳（参见 [高级技巧 - JSON 模式](/cookbooks/concepts/04-advanced-techniques.md)）。

### 提高 OCR 准确率的 Cookbook 经验

1. **预处理图片**：
   - 调整对比度，让文字更清晰
   - 裁剪掉无关的边框和背景
   - 对于歪斜的图片先转正
   - 分辨率不要太低（300DPI 等效最佳）

2. **提示词技巧**：
   - 明确告诉 Claude 这是什么类型的文档（"这是一张增值税发票"）
   - 给出字段示例，Claude 会按你给的格式提取
   - 如果有固定格式，提供一个模板
   - 要求"看不清晰的标注[模糊]"比猜测效果好——后续可以人工复核

3. **常见陷阱**：
   - 数字 0 和字母 O、数字 1 和字母 l/I 容易混淆——对于金额类字段，结合上下文校验
   - 盖章覆盖的文字可能识别错误——提示 Claude 注意
   - 多页文档逐页处理，不要拼接成长图

## 模式三：PDF 处理模式

**适用场景**：上传 PDF 文档，基于 PDF 内容问答、总结、提取信息。Cookbook 中的 PDF 示例提供了完整的处理流程。

### PDF 处理的标准流程

```
PDF 文件
    ↓
┌─────────────────────────────────┐
│  步骤1：PDF 转图片              │
│  （使用 pdf2image/PyMuPDF）     │
│  每页转成一张高清图片           │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  步骤2：逐页 Vision 理解        │
│  用 Claude Vision 分析每页内容  │
│  可选：提取文字、生成摘要       │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  步骤3：构建向量索引（可选）    │
│  如果需要问答，将每页内容向量化 │
│  存入向量数据库                │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  步骤4：问答/总结/分析          │
│  根据需求使用对应功能           │
└─────────────────────────────────┘
```

### 代码实现骨架

```python
from pathlib import Path
import fitz  # PyMuPDF
from anthropic import Anthropic
import base64

client = Anthropic()

def pdf_to_images(pdf_path: str, dpi: int = 200) -> list[tuple[bytes, str]]:
    """将 PDF 每页转成 PNG 图片"""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        images.append((img_bytes, f"第{page.number + 1}页"))
    doc.close()
    return images

def analyze_pdf_page(image_bytes: bytes, page_name: str) -> str:
    """分析单页 PDF 内容"""
    b64_data = base64.b64encode(image_bytes).decode()
    
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64_data
                    }
                },
                {
                    "type": "text",
                    "text": f"请提取这页（{page_name}）的所有文字内容，保持原有结构。"
                }
            ]
        }]
    )
    return response.content[0].text

# 使用：完整 PDF 处理
def process_pdf(pdf_path: str) -> list[str]:
    pages = pdf_to_images(pdf_path)
    page_texts = []
    for img_bytes, page_name in pages:
        text = analyze_pdf_page(img_bytes, page_name)
        page_texts.append(f"=== {page_name} ===\n{text}")
    return page_texts
```

### PDF 处理的最佳实践

1. **DPI 选择**：200 DPI 是性价比最高的选择——150 可能模糊，300 太占 token
2. **长 PDF 处理**：超过 20 页的 PDF 建议先做 RAG（参见 [RAG 模式](/cookbooks/concepts/03-rag-patterns.md)），不要把所有页面塞到一次请求里
3. **混合方案**：对于有文字层的 PDF，先用 `PyMuPDF` 直接提取文字层，只把扫描页/图片页用 Vision 处理，效果更好更省 token
4. **表格处理**：PDF 中的表格用 Vision 比直接提取文字层效果好——Claude 能理解表格的视觉结构

## 模式四：图片生成（配合 Stable Diffusion）

**适用场景**：让 Claude 生成高质量的 Stable Diffusion 提示词，再调用 SD 生成图片。Cookbook 展示了 LLM + 扩散模型的配合模式。

### 为什么用 Claude 写提示词？

直接写 Stable Diffusion 提示词需要经验，而 Claude：
- 理解自然语言描述，自动转换成 SD 偏好的关键词格式
- 自动补充质量词（masterpiece, best quality, detailed...）
- 能理解风格描述（"赛博朋克风格"、"吉卜力画风"）
- 可以进行多轮优化——"把光调亮一点"、"换个角度"

### Claude 提示词生成器模式

```python
SD_PROMPT_GENERATOR = """你是一位专业的 Stable Diffusion 提示词专家。
根据用户的自然语言描述，生成高质量的 SD 提示词。

输出格式（只返回这个 JSON，不要其他内容）：
{
  "prompt": "正向提示词（英文，逗号分隔关键词，包含质量词、风格、主体、细节、光照、视角）",
  "negative_prompt": "负向提示词（英文，要避免的元素：低质量、模糊、畸形等）",
  "parameters": {
    "width": 宽度（建议 1024 或 768）,
    "height": 高度（建议 1024 或 768）,
    "steps": 步数（建议 20-30）,
    "cfg_scale": CFG Scale（建议 7-9）,
    "sampler": "采样器名称（建议 DPM++ 2M Karras）"
  }
}

记住：
- 正向提示词从最重要的关键词开始
- 始终包含质量提升词：masterpiece, best quality, highly detailed, 8k
- 负向提示词包含：low quality, worst quality, blurry, deformed, ugly, bad anatomy
- 根据描述自动推断合适的分辨率和构图"""
```

## 多模态提示词通用技巧

从所有 Cookbook 视觉示例中提炼的通用技巧：

### 1. 具体 > 笼统

❌ "描述这张图"
✅ "描述这张图中的产品：颜色、材质、形状、上面的文字、和什么物体放在一起"

### 2. 给 Claude 一个"角色"

❌ "这是什么？"
✅ "你是一位资深数据分析师，请解读这个销售图表..."
✅ "你是一位专业的会计，请从这张发票中提取..."

角色暗示会让 Claude 的输出更专业、更符合预期。

### 3. 给出输出格式

明确告诉 Claude 你想要什么格式：Markdown 表格、JSON、要点列表、固定模板。Vision 也支持 JSON 模式。

### 4. 多图对比

Claude 支持在一次请求中传入多张图片，可以用来做：
- 图片对比（"这两张图有什么区别？"）
- 多页文档（"把这三页 PPT 的要点整合起来"）
- 顺序推理（"按时间顺序描述这组图片展示的过程"）

```python
content = [
    {"type": "image", "source": {"type": "base64", ...}},  # 图1
    {"type": "image", "source": {"type": "base64", ...}},  # 图2
    {"type": "text", "text": "对比这两张 UI 截图，列出所有视觉差异。"}
]
```

### 5. 思考链提示

复杂视觉推理任务，让 Claude 先描述再推理：

```
先描述你在图片中看到了什么，再基于这些观察回答我的问题。
思考过程要分步骤写出来。
```

## Token 成本提示

Vision 是比较"贵"的能力，Cookbook 中的成本控制经验：
- 一张 1568px 的图片大约消耗 1600 个 input token
- 控制图片分辨率，不要传超大图
- 裁剪掉无关区域，只保留需要分析的部分
- PDF 处理时，先用低分辨率快速扫描定位到相关页面，再对关键页面用高分辨率分析

## 相关概念

- [Cookbook 导览](/cookbooks/concepts/00-overview.md) — 回到 Cookbooks 总览
- [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md) — 多模态 + 工具调用的组合模式
- [RAG 与知识检索模式](/cookbooks/concepts/03-rag-patterns.md) — PDF 处理后续做 RAG 的完整流程
- [高级技巧 - JSON 模式](/cookbooks/concepts/04-advanced-techniques.md) — 结构化输出配合 Vision 提取表单
- [Python SDK - 视觉与文件处理](/python-sdk/concepts/05-vision-files.md) — Vision API 的底层 SDK 参考
