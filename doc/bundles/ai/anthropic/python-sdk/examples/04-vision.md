---
type: example
title: "视觉理解"
description: "使用Claude进行图片分析，包括本地图片base64编码、图片+文本混合、多图对比、OCR文字识别，以及PDF文档处理框架。"
tags: [vision, multimodal, image, ocr, pdf, base64, screenshot]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-016~F-023
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: concept-05
    resource: /python-sdk/concepts/05-vision-files.md
    title: "视觉理解与文件处理"
---

# 视觉理解

本示例演示 Claude 的多模态视觉理解能力，包括：本地图片读取与 base64 编码、图片内容分析、图片+文本混合提问、多图对比、OCR 文字识别、截图/图表分析，以及 PDF 文档处理框架。通过这些示例，你将学会如何构建能"看懂"图片的 AI 应用。

## 前置准备

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

准备一些测试图片（可以是截图、照片、图表等）放在脚本同目录下。

## 完整代码

```python
import os
import base64
from anthropic import Anthropic, APIStatusError


# ========== 图片编码工具函数 ==========

def encode_image(image_path: str) -> tuple[str, str]:
    """
    读取本地图片文件并编码为 base64，自动根据扩展名判断 media_type。

    Args:
        image_path: 图片文件路径

    Returns:
        (media_type, base64_data) 元组
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在：{image_path}")

    # 根据文件扩展名映射 MIME 类型
    ext_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    ext = os.path.splitext(image_path)[1].lower()
    media_type = ext_map.get(ext, "image/jpeg")

    # 以二进制模式读取文件，编码为 base64
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        base64_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    file_size_kb = len(image_bytes) / 1024
    print(f"[图片编码] {image_path} ({file_size_kb:.1f} KB, {media_type})")

    return media_type, base64_data


def encode_pdf(pdf_path: str) -> str:
    """
    读取本地 PDF 文件并编码为 base64。

    Args:
        pdf_path: PDF 文件路径

    Returns:
        base64 编码的 PDF 数据
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def create_image_content_block(image_path: str) -> dict:
    """
    从图片路径创建 image 类型的内容块。

    Args:
        image_path: 图片文件路径

    Returns:
        可直接放入 messages content 数组的内容块字典
    """
    media_type, image_data = encode_image(image_path)
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": image_data
        }
    }


def create_text_content_block(text: str) -> dict:
    """
    创建 text 类型的内容块。

    Args:
        text: 文本内容

    Returns:
        text 内容块字典
    """
    return {
        "type": "text",
        "text": text
    }


# ========== 核心视觉分析函数 ==========

def analyze_image(client: Anthropic, image_path: str, question: str, system_prompt: str = None) -> str:
    """
    分析单张图片并回答问题。

    Args:
        client: Anthropic 客户端
        image_path: 图片路径
        question: 关于图片的问题
        system_prompt: 可选的系统提示词

    Returns:
        Claude 的分析结果文本
    """
    image_block = create_image_content_block(image_path)
    text_block = create_text_content_block(question)

    messages = [
        {
            "role": "user",
            "content": [image_block, text_block]
        }
    ]

    kwargs = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": 2048,
        "messages": messages,
    }

    if system_prompt:
        kwargs["system"] = system_prompt

    message = client.messages.create(**kwargs)
    return message.content[0].text


def compare_images(client: Anthropic, image_path1: str, image_path2: str, question: str) -> str:
    """
    对比分析两张图片，找出差异或进行比较。

    Args:
        client: Anthropic 客户端
        image_path1: 第一张图片路径
        image_path2: 第二张图片路径
        question: 对比问题

    Returns:
        对比分析结果
    """
    content = [
        create_text_content_block("第一张图片："),
        create_image_content_block(image_path1),
        create_text_content_block("第二张图片："),
        create_image_content_block(image_path2),
        create_text_content_block(question),
    ]

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]

    system_prompt = """你是一位专业的图片对比分析师。
比较图片时请注意：
1. 逐一列出所有可见的差异点
2. 描述差异的具体位置和内容
3. 如果图片太小或看不清，直接说明
4. 不要编造你看不到的内容"""

    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2048,
        system=system_prompt,
        messages=messages,
    )

    return message.content[0].text


def ocr_image(client: Anthropic, image_path: str, extract_format: str = "text") -> str:
    """
    识别图片中的文字（OCR）。

    Args:
        client: Anthropic 客户端
        image_path: 图片路径
        extract_format: 提取格式，"text"（纯文本）或 "structured"（结构化）

    Returns:
        识别出的文字内容
    """
    if extract_format == "structured":
        question = """请识别这张图片中的所有文字，按原有的排版结构输出：
- 保持段落、换行、缩进
- 如果是表格，用 Markdown 表格格式还原
- 如果有标题、列表等结构，保留结构层次
- 不确定的文字用 [?] 标记"""
    else:
        question = """请逐字识别这张图片中的所有文字，只输出识别到的文字内容，不要添加任何解释、说明或其他内容。"""

    system_prompt = "你是一个专业的 OCR 引擎，专注于准确识别图片中的文字。"

    return analyze_image(client, image_path, question, system_prompt)


def analyze_chart(client: Anthropic, image_path: str) -> str:
    """
    分析图表/数据可视化图片。

    Args:
        client: Anthropic 客户端
        image_path: 图表图片路径

    Returns:
        图表分析结果
    """
    question = """请详细分析这个图表：
1. 首先说明图表类型（柱状图/折线图/饼图/流程图等）和标题
2. 描述坐标轴/图例的含义（如果有）
3. 提取关键数据点和数值
4. 总结数据显示的主要趋势、规律或异常
5. 给出你的洞察和结论"""

    system_prompt = """你是一位专业的数据分析师，擅长解读各种数据可视化图表。
分析图表时要客观准确，数据要尽量精确，不要臆测图表中没有的信息。"""

    return analyze_image(client, image_path, question, system_prompt)


def analyze_screenshot(client: Anthropic, image_path: str) -> str:
    """
    分析 UI 截图/界面截图，描述界面元素和状态。

    Args:
        client: Anthropic 客户端
        image_path: 截图路径

    Returns:
        界面分析结果
    """
    question = """请分析这个界面截图：
1. 这是什么类型的界面（网站/APP/软件/IDE等）？
2. 描述界面上的主要元素、按钮、菜单、文字内容
3. 当前界面显示的是什么内容或状态？
4. 有没有明显的错误提示、弹窗或通知？"""

    return analyze_image(client, image_path, question)


def analyze_pdf_framework(client: Anthropic, pdf_path: str, question: str) -> str:
    """
    PDF 文档分析框架（示例框架）。

    注意：PDF 支持需要使用 document 类型内容块。
    超长 PDF 建议分页处理，本示例展示单页/短文档处理方式。

    Args:
        client: Anthropic 客户端
        pdf_path: PDF 文件路径
        question: 关于 PDF 内容的问题

    Returns:
        文档分析结果
    """
    pdf_data = encode_pdf(pdf_path)

    content = [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": pdf_data
            }
        },
        create_text_content_block(question)
    ]

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]

    system_prompt = """你是一位专业的文档分析助手。
分析文档时：
1. 先简要总结文档主题和类型
2. 根据用户问题提取相关信息
3. 引用文档中的关键内容支持你的回答
4. 如果文档太长无法完整分析，告知用户"""

    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=4096,  # PDF 分析需要较大的 token 限制
        system=system_prompt,
        messages=messages,
    )

    return message.content[0].text


def multi_turn_vision_chat(client: Anthropic, image_path: str) -> None:
    """
    多轮对话中的视觉理解：先发图片提问，然后针对图片内容继续追问。
    Claude 会记住之前发送过的图片，不需要重复发送。

    Args:
        client: Anthropic 客户端
        image_path: 图片路径
    """
    messages = []

    # 第一轮：发送图片 + 第一个问题
    print("\n--- 多轮视觉对话演示 ---")
    print("（图片已发送）")

    content_round1 = [
        create_image_content_block(image_path),
        create_text_content_block("这张图片里有什么？请简要描述。")
    ]
    messages.append({"role": "user", "content": content_round1})

    response1 = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=messages,
    )
    reply1 = response1.content[0].text
    print(f"\n你：这张图片里有什么？请简要描述。")
    print(f"Claude：{reply1}")
    messages.append({"role": "assistant", "content": reply1})

    # 第二轮：追问，不需要重复发图片
    print("\n--- 第二轮追问（不重复发图片）---")
    messages.append({"role": "user", "content": "图片里有文字吗？如果有的话写的是什么？"})

    response2 = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=messages,
    )
    reply2 = response2.content[0].text
    print(f"你：图片里有文字吗？如果有的话写的是什么？")
    print(f"Claude：{reply2}")


# ========== 演示主函数 ==========

def vision_demo() -> None:
    """
    视觉功能演示。
    注意：运行前请准备测试图片，或修改路径指向你自己的图片文件。
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误：请先设置 ANTHROPIC_API_KEY 环境变量")
        return

    client = Anthropic()

    # ====== 检查测试图片是否存在 ======
    # 请替换为你自己的图片路径
    test_image = "test_image.jpg"  # 替换为实际图片路径
    test_image2 = "test_image2.png"  # 对比用第二张图
    test_pdf = "test_document.pdf"  # PDF 测试文件

    # 如果没有测试图片，打印使用说明
    has_test_image = os.path.exists(test_image)

    if not has_test_image:
        print("=" * 60)
        print("📷 视觉示例使用说明")
        print("=" * 60)
        print("本示例演示 Claude 的图片分析能力。要运行完整演示：")
        print()
        print("1. 准备一张测试图片（jpg/png/gif/webp），命名为 test_image.jpg")
        print("   放在脚本同目录下，或修改代码中的 test_image 变量")
        print()
        print("2. 可用的分析功能：")
        print("   - analyze_image()      ：单张图片问答")
        print("   - ocr_image()          ：OCR 文字识别")
        print("   - analyze_chart()      ：图表数据分析")
        print("   - analyze_screenshot() ：UI 截图分析")
        print("   - compare_images()     ：两张图片对比")
        print("   - multi_turn_vision_chat()：多轮视觉对话")
        print()
        print("3. 代码使用示例：")
        print('   result = analyze_image(client, "photo.jpg", "照片里有什么？")')
        print('   text = ocr_image(client, "document.png")')
        print('   analysis = analyze_chart(client, "sales_chart.png")')
        print()
        print("下面展示一个代码框架演示（不需要真实图片文件）...")
        print()

    # ====== 演示1：图片问答代码框架 ======
    print("=" * 60)
    print("示例 1：图片问答代码框架")
    print("=" * 60)
    print('''
# 使用方式：
from anthropic import Anthropic
import base64, os

client = Anthropic()

def ask_about_image(image_path, question):
    with open(image_path, "rb") as f:
        img_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    # 根据扩展名判断 media_type
    ext = os.path.splitext(image_path)[1].lower()
    media_type = {".jpg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text

# 调用：
# answer = ask_about_image("cat.jpg", "这只猫是什么颜色？在做什么？")
# print(answer)
''')

    # ====== 演示2：OCR 识别代码框架 ======
    print("=" * 60)
    print("示例 2：OCR 文字识别代码框架")
    print("=" * 60)
    print('''
def ocr(image_path):
    """识别图片中的所有文字"""
    with open(image_path, "rb") as f:
        img_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    media_type = {".jpg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2048,
        system="你是专业的OCR引擎，准确识别图片中的文字。",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                {"type": "text", "text": "逐字识别图片中的所有文字，保持原有格式。"}
            ]
        }]
    )
    return response.content[0].text
''')

    # ====== 如果有真实图片，运行实际演示 ======
    if has_test_image:
        print("=" * 60)
        print("检测到测试图片，运行实际演示...")
        print("=" * 60)

        try:
            # 单图分析
            print("\n--- 图片内容分析 ---")
            result = analyze_image(client, test_image, "请描述这张图片的内容，包括主要物体、颜色、场景等。")
            print(result)

            # OCR
            print("\n--- OCR 文字识别 ---")
            ocr_result = ocr_image(client, test_image)
            print(ocr_result[:500] + "..." if len(ocr_result) > 500 else ocr_result)

            # 多轮对话
            multi_turn_vision_chat(client, test_image)

        except APIStatusError as e:
            print(f"API 错误 ({e.status_code}): {e.message}")
        except Exception as e:
            print(f"运行出错：{type(e).__name__}: {e}")


if __name__ == "__main__":
    vision_demo()
```

## 运行方式

```bash
# 先准备一张测试图片命名为 test_image.jpg 放在同目录，或修改代码中的路径
python 04-vision.py
```

## 代码解析

### 图片编码的关键点

```python
with open(image_path, "rb") as f:
    image_bytes = f.read()
    base64_data = base64.standard_b64encode(image_bytes).decode("utf-8")
```

几个容易出错的地方：

1. **使用 `"rb"` 模式**：必须以二进制模式读取，不能用默认的文本模式 `"r"`，否则会出现编码错误。

2. **不要加 data URI 前缀**：`source.data` 只放纯 base64 字符串，不要加 `data:image/jpeg;base64,` 前缀。SDK 会自动处理。

3. **正确的 media_type**：必须与图片实际格式匹配：
   - `.jpg`/`.jpeg` → `image/jpeg`
   - `.png` → `image/png`
   - `.gif` → `image/gif`
   - `.webp` → `image/webp`

### content 数组结构：多模态消息的核心

与纯文本对话不同，视觉输入时 `content` 不再是简单的字符串，而是**内容块数组**：

```python
"content": [
    {"type": "image", "source": {...}},  # 图片块
    {"type": "text", "text": "问题..."}   # 文本块
]
```

内容块可以任意混合和排列，Claude 会按顺序"阅读"所有内容。常见的组合：
- 一张图片 + 一个问题（最常见）
- 文本说明 + 多张图片 + 问题
- 多张图片交替 + 文本（对比场景）

### 系统提示词提升视觉效果

视觉任务中，好的系统提示词能显著提升输出质量：

| 任务类型 | 系统提示词要点 |
|---------|--------------|
| 通用图片问答 | "客观描述，不确定的内容说明" |
| OCR | "逐字识别，保持排版，不确定用[?]标记" |
| 图表分析 | "先描述图表类型，再列数据点，最后总结趋势" |
| 截图分析 | "描述界面类型、元素、状态、错误提示" |

给 Claude 明确的"操作步骤"，它会按你的要求结构化输出。

### 多轮视觉对话：图片不需要重复发送

```python
# 第一轮：发送图片 + 问题
messages.append({
    "role": "user",
    "content": [image_block, text_block_q1]
})
# ... 获取回复 ...

# 第二轮：只发文本问题即可！
messages.append({
    "role": "user",
    "content": "图片里有什么文字？"  # Claude 仍然记得之前的图片
})
```

图片已经在消息历史中，Claude 在后续轮次中仍然能够"看到"并引用图片内容。重复发送图片不仅浪费 token，还可能导致上下文混乱。

### PDF 处理注意事项

PDF 使用 `document` 类型而非 `image` 类型：

```python
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": pdf_base64_data
    }
}
```

PDF 使用建议：
- 设置较大的 `max_tokens`（建议 4096 或更高），文档分析通常需要较多输出
- 超长 PDF（几十页以上）建议分页处理，单页或短文档可直接发送
- 扫描版 PDF（图片形式）也能识别，但文字版 PDF 效果更好
- 代码中给出的是框架示例，实际使用时替换为真实 PDF 路径

### Token 消耗参考

图片输入会消耗 token，大致参考：
- 一张普通截图/照片：约 1000-2000 输入 token
- 图片 token 计入 `message.usage.input_tokens`
- 图片越大、细节越多，token 消耗越高
- 多张图片的 token 消耗累加

### 支持的图片格式

| 格式 | MIME 类型 | 最佳用途 |
|------|----------|---------|
| JPEG | `image/jpeg` | 照片、复杂图像（有损压缩，文件小） |
| PNG | `image/png` | 截图、图表、UI 界面（无损，支持透明） |
| GIF | `image/gif` | 简单图形（仅静态帧，不支持动画） |
| WebP | `image/webp` | 现代格式，压缩率高（推荐用于网络图片） |

**建议**：照片用 JPEG，截图/图表/文字图片用 PNG。

## 常见应用场景代码模板

### 场景 1：代码截图识别与解释

```python
system = """你是一位资深程序员。用户发送代码截图后：
1. 识别代码语言和内容
2. 解释代码的功能和逻辑
3. 指出可能存在的 bug 或问题
4. 给出改进建议"""

result = analyze_image(client, "code_screenshot.png", "解释这段代码", system)
```

### 场景 2：手写笔记转文字

```python
system = """你是手写文字识别专家。
- 尽可能准确识别手写内容
- 保持段落结构
- 实在看不清的用 [?] 标记，不要猜测"""

notes = ocr_image(client, "handwritten_notes.jpg")
```

### 场景 3：电商商品图分析

```python
system = """你是电商商品分析助手。分析商品图片后输出：
- 商品类别
- 主要颜色和款式
- 可见的品牌标识
- 商品状态（新品/二手等）"""
```

### 场景 4：与工具调用结合（视觉+计算）

视觉能力可以和工具调用结合使用，实现"看图→识别数据→计算→回答"的完整链路：

```python
# Claude 识别图表中的数据 → 调用 calculate 工具计算 → 返回结果
response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {...}},
            {"type": "text", "text": "计算三个季度的总销售额"}
        ]
    }],
    tools=[calculate_tool]  # 包含计算器工具
)
```

## 常见问题

1. **图片格式错误**：确保 `media_type` 与文件实际格式一致。如果不确定，用 `image/jpeg` 作为默认值（JPEG 兼容性最好）。

2. **图片太大导致请求失败**：单张图片建议不超过 5MB。过大的图片请先压缩或调整尺寸。

3. **Claude 说看不清图片**：检查图片是否模糊、文字是否过小。OCR 场景建议文字高度至少 20 像素以上。

4. **可以直接传图片 URL 吗？** SDK 不支持直接传 URL。需要先用 `httpx` 或 `requests` 下载图片字节，再编码为 base64。这样做是为了安全性和可靠性（避免服务端发起外部请求）。

5. **GIF 动画支持吗？** 不支持动画，只处理 GIF 的第一帧（静态图像）。需要处理视频请用其他方案。

6. **base64 编码后字符串太长怎么办？** 这是正常的——base64 编码会比原文件大约 33%。如果图片过大，先压缩图片再发送。

## 相关概念

- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 理解 content 数组和消息结构
- [视觉理解与文件处理概念](/python-sdk/concepts/05-vision-files.md) — 视觉能力原理、Files API 上传、更多最佳实践
- [工具调用实战](03-tool-use.md) — 学习如何将视觉识别与工具调用结合
- [AWS Bedrock与Google Vertex后端](05-bedrock-vertex.md) — 下一个示例：多云部署
