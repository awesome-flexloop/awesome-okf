---
type: concept
title: "视觉理解与文件处理"
description: "掌握 Claude 多模态能力：图片输入的 base64 编码格式、支持的媒体类型、图片+文本混合消息、PDF 文档处理，以及通过 client.files API 上传和管理文件附件。"
tags: [vision, multimodal, image, pdf, files, upload, base64, attachments]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-007
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-016~F-025
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
---

# 视觉理解与文件处理

Claude 是多模态（Multimodal）大语言模型，不仅能处理文本，还能"看懂"图片、理解 PDF 文档内容。通过在消息中传入图片或文件，你可以让 Claude 分析图表、识别手写文字、解读截图、审阅文档、提取图片中的信息，构建更强大的 AI 应用。

本文档将讲解 Claude 的视觉理解能力、图片输入格式、支持的媒体类型、图片+文本混合消息、PDF 处理，以及 SDK 提供的文件上传 API。

## 多模态能力概述

Claude 3 及之后的模型（Sonnet、Haiku、Opus 系列）都具备视觉理解能力，可以直接接受图片作为输入。常见的视觉应用场景包括：

- **图片问答**：上传一张图片，询问图片内容
- **图表/数据可视化分析**：让 Claude 解读柱状图、折线图、饼图、流程图
- **OCR 文字识别**：识别图片中的印刷体或手写文字
- **截图/界面理解**：分析 UI 截图、网页截图、代码截图
- **文档审阅**：上传 PDF 文档，让 Claude 总结、翻译或回答文档相关问题
- **图片对比**：上传多张图片，让 Claude 比较差异

视觉能力在 Messages API 中原生支持——只需要在消息的 `content` 数组中使用 `image` 类型的内容块即可，不需要额外启用特殊的 API 端点或参数。

## 图片输入格式：base64 编码

Anthropic Messages API 主要通过 **base64 编码** 接收图片。与一些其他 API 支持直接传入图片 URL 不同，Anthropic SDK 要求你将图片读取为字节，编码为 base64 字符串后嵌入到消息中。

> 💡 **关于 URL 图片**：如果你的图片在网络上，需要先用 HTTP 客户端（如 `httpx`、`requests`）下载图片字节，然后再编码为 base64。SDK 不直接支持 URL 图片输入，这是出于安全和可靠性考虑——避免服务器端发起外部请求。

### image 内容块格式

在消息 content 数组中，图片使用如下格式的内容块：

```python
{
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": "image/jpeg",  # 或 image/png, image/gif, image/webp
        "data": "iVBORw0KGgoAAAANSUhEUgAA..."  # base64 编码的图片数据
    }
}
```

| 字段 | 说明 |
|------|------|
| `type` | 固定为 `"image"`，表示这是一个图片内容块 |
| `source.type` | 固定为 `"base64"`，表示使用 base64 编码 |
| `source.media_type` | 图片的 MIME 类型，必须是支持的格式之一 |
| `source.data` | base64 编码的图片字节字符串（不含 `data:image/...;base64,` 前缀） |

### 支持的图片格式

Claude 支持以下图片格式：

| MIME 类型 | 文件扩展名 | 说明 |
|-----------|-----------|------|
| `image/jpeg` | `.jpg`, `.jpeg` | JPEG 格式，适合照片 |
| `image/png` | `.png` | PNG 格式，支持透明背景，适合截图、图表 |
| `image/gif` | `.gif` | GIF 格式（仅静态帧，不支持动画） |
| `image/webp` | `.webp` | WebP 格式，现代图片格式，压缩率高 |

### 将本地图片编码为 base64

在 Python 中，读取本地图片并编码为 base64 的标准方式：

```python
import base64
from anthropic import Anthropic

client = Anthropic()

def encode_image(image_path: str) -> str:
    """读取本地图片文件并返回 base64 编码字符串"""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

# 示例：分析一张本地图片
image_data = encode_image("screenshot.png")

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "请描述这张图片的内容，特别注意界面上的文字和按钮。"
                }
            ]
        }
    ]
)

print(message.content[0].text)
```

**关键点**：
- 使用 `"rb"` 模式读取文件（二进制模式）
- 使用 `base64.standard_b64encode()` 进行编码
- 编码后需要 `.decode("utf-8")` 转换为字符串
- 不要在 data 前加 `data:image/png;base64,` 前缀，只放纯 base64 字符串

### 从网络获取图片

如果图片在 URL 上，需要先下载再编码：

```python
import httpx
import base64

def encode_image_from_url(url: str) -> tuple[str, str]:
    """从 URL 下载图片并返回 (media_type, base64_data)"""
    response = httpx.get(url)
    response.raise_for_status()
    
    # 从 Content-Type 头获取媒体类型，或根据 URL 扩展名判断
    media_type = response.headers.get("content-type", "image/jpeg")
    image_data = base64.standard_b64encode(response.content).decode("utf-8")
    
    return media_type, image_data

# 使用
media_type, image_data = encode_image_from_url("https://example.com/photo.jpg")

content_block = {
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": media_type,
        "data": image_data
    }
}
```

## 图片+文本混合消息

视觉输入几乎总是与文本一起使用——你需要用文字告诉 Claude 要对图片做什么。图片和文本块可以任意混合排列在 `content` 数组中：

### 单张图片 + 文本问题

最常见的形式：一张图片配一个问题。

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": chart_data}},
            {"type": "text", "text": "这个图表显示了什么趋势？关键数据点有哪些？"}
        ]
    }
]
```

### 多张图片

一次可以传入多张图片，Claude 会同时分析所有图片：

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "比较这两张图片的差异："},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img1_data}},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img2_data}},
            {"type": "text", "text": "请列出所有不同之处。"}
        ]
    }
]
```

### 多轮对话中的图片

在多轮对话中，图片可以出现在任意 user 消息中。注意：图片是消息历史的一部分，会占用 token。如果图片只在某一轮需要，不需要在后续消息中重复发送。

```python
messages = [
    # 第一轮：发送图片+问题
    {
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": photo_data}},
            {"type": "text", "text": "这张照片里有什么动物？"}
        ]
    },
    # Claude 回复
    {
        "role": "assistant",
        "content": "这张照片里有一只橘猫，正趴在窗台上晒太阳..."
    },
    # 第二轮：针对图片追问，不需要重复发图片
    {
        "role": "user",
        "content": "它看起来开心吗？环境是室内还是室外？"
    }
]
```

Claude 在多轮对话中能"记住"之前发送过的图片，不需要每次都重新发送。

## PDF 文档支持

除了图片，Claude 还支持直接处理 PDF 文档。PDF 使用专门的 `base64_pdf_source` 类型：

```python
import base64

def encode_pdf(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

pdf_data = encode_pdf("report.pdf")

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": "请总结这份报告的要点，列出关键结论。"
                }
            ]
        }
    ]
)
```

PDF 处理的注意事项：
- PDF 会被转换为图片进行视觉处理，超长文档可能需要分页处理
- 建议设置较大的 `max_tokens`（如 4096 或更高）给文档分析留出足够输出空间
- 扫描版 PDF（图片形式）也能识别，但文字版 PDF 效果更好

## 文件上传 API：client.files

SDK 通过 `client.files` 资源提供文件上传和管理功能（在 `client` 上是懒加载属性）。Files API 允许你将文件上传到 Anthropic 服务器，然后在消息中引用这些文件作为附件。

> 💡 **何时使用 Files API vs 直接 base64**：
> - **直接 base64**：简单、一次性使用、不需要持久化文件——大多数视觉场景推荐这种方式
> - **Files API**：文件较大、需要重复使用多个消息、要在 Agent/Session 中共享文件——适合这种场景

### FileMetadata 对象结构

上传的文件以 `FileMetadata` 对象表示，包含以下核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 文件唯一标识符 |
| `filename` | `str` | 原始文件名 |
| `size_bytes` | `int` | 文件大小（字节数） |
| `mime_type` | `str` | 文件 MIME 类型 |
| `created_at` | `datetime` | 文件创建时间 |
| `expires_at` | `datetime \| None` | 文件过期时间 |

### Files API 主要方法

`client.files` 资源提供文件管理方法：

| 方法 | 用途 |
|------|------|
| `files.upload(file, expires_in_seconds)` | 上传文件 |
| `files.list()` | 列出已上传的文件（分页） |
| `files.retrieve_metadata(file_id)` | 获取指定文件的元数据 |
| `files.download(file_id)` | 下载文件内容 |
| `files.delete(file_id)` | 删除文件 |

### 上传文件示例

```python
from anthropic import Anthropic

client = Anthropic()

# 上传文件
with open("document.pdf", "rb") as f:
    file_obj = client.files.upload(
        file=f,
        expires_in_seconds=3600  # 1小时后过期
    )

print(f"文件上传成功，ID: {file_obj.id}")
print(f"文件名: {file_obj.filename}")
print(f"大小: {file_obj.size_bytes} bytes")

# 列出所有文件（自动分页）
for f in client.files.list():
    print(f"- {f.id}: {f.filename} ({f.size_bytes} bytes)")

# 获取文件元数据
retrieved = client.files.retrieve_metadata(file_obj.id)

# 删除文件
client.files.delete(file_obj.id)
```

文件上传后，可以在 Messages API 和 Beta Agents/Sessions 中通过文件 ID 引用。具体引用格式参见 API 参考文档。

## 视觉理解的注意事项与最佳实践

### 图片大小限制

- 单张图片建议不超过 5MB
- 如果图片过大，建议在上传前压缩或调整尺寸
- 图片分辨率不需要特别高——Claude 会自动处理，但过大的图片会增加请求时间和 token 消耗

### 图片质量建议

- **文字识别（OCR）**：确保文字清晰可读，避免模糊或过小的字体
- **图表分析**：图表要有清晰的坐标轴、标签和图例
- **截图**：尽量截取完整相关区域，避免过多无关内容
- **手写识别**：笔迹越清晰识别率越高，建议使用较高对比度

### Token 消耗

图片输入会消耗 token，具体数量取决于图片大小和复杂度。作为粗略参考：
- 一张普通照片大约消耗 1000-2000 个输入 token
- 图片 token 会计入 `usage.input_tokens`
- 多图会累加 token 消耗

### 系统提示词增强视觉效果

在系统提示词中明确视觉任务的要求，可以提升输出质量：

```python
system = """你是一位专业的图片分析助手。
- 描述图片时要客观准确，注明你能确认和不能确认的内容
- 如果图片中有文字，逐字转录重要文字
- 如果是图表，先描述图表类型，再列出关键数据点和趋势
- 如果图片模糊或看不清，直接告诉用户，不要猜测"""
```

### 视觉+工具结合

视觉能力可以与工具调用结合使用。例如：
1. 用户发送一张包含数据表格的图片
2. Claude 识别图片中的数据（视觉能力）
3. Claude 调用计算器工具进行计算（工具调用）
4. 返回计算结果和分析

```python
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    system="你是一个数据分析助手。看到图表数据后，用calculate工具进行计算。",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": chart_data}},
            {"type": "text", "text": "计算这三个季度的总销售额是多少？"}
        ]
    }],
    tools=tools  # 包含 calculate 工具
)
```

## 完整示例：图片分析助手

下面是一个可以分析本地图片文件的完整示例：

```python
import base64
import os
from anthropic import Anthropic, APIStatusError

def encode_image(image_path: str) -> tuple[str, str]:
    """编码图片，返回 (media_type, base64_data)"""
    ext_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    ext = os.path.splitext(image_path)[1].lower()
    media_type = ext_map.get(ext, "image/jpeg")
    
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    
    return media_type, data

def analyze_image(image_path: str, question: str) -> str:
    """分析图片并回答问题"""
    client = Anthropic()
    
    if not os.path.exists(image_path):
        return f"错误：文件不存在 {image_path}"
    
    media_type, image_data = encode_image(image_path)
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": question}
                ]
            }]
        )
        return message.content[0].text
    except APIStatusError as e:
        return f"API 错误 ({e.status_code}): {e.message}"

if __name__ == "__main__":
    result = analyze_image("chart.png", "请详细描述这个图表，包括标题、坐标轴、数据趋势和关键发现。")
    print(result)
```

## 相关概念

- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 理解消息 content 数组结构和 TextBlock 基础
- [工具调用（Function Calling）](/python-sdk/concepts/04-tool-use.md) — 学习如何将视觉识别与工具调用结合
- [多模态视觉示例](/python-sdk/examples/04-vision.md) — 更多可运行的图片分析、OCR、图表解读代码示例
- [Anthropic Python SDK 客户端入口与基础设施参考](/python-sdk/references/sdk-client.md) — client.files 资源的完整 API 参考
