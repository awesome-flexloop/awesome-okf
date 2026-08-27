---
type: Concept
title: 图像生成 API
description: 图像生成接口（/v1/images/generations）使用指南，包含文生图、图生图、尺寸参数、输出格式详解
tags: [图像生成, Image Generation, 文生图, 图生图, DALL-E兼容]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: model-catalog
    resource: /references/model-catalog.md
    title: Agnes AI 模型目录
---

# 图像生成 API

AgnesAI提供与OpenAI Images API兼容的图像生成接口，支持文生图（Text-to-Image）和图生图（Image-to-Image）能力。

**端点**：`POST https://apihub.agnes-ai.com/v1/images/generations`

**支持模型**：
- `agnes-image-2.1-flash`（推荐）：高密度视觉生成、图像编辑、灵活尺寸、URL或Data URI输入
- `agnes-image-2.0-flash`：快速图像生成、基础图像编辑

> 事实溯源：F-010、F-019、F-020

## 文生图基础调用

### Python示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://apihub.agnes-ai.com/v1",
)

response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="日出时分雾霭峡谷上方漂浮的发光城市，电影级写实风格，暖金色光线",
    size="1024x768",
    n=1,
)

# 获取生成的图片URL
image_url = response.data[0].url
print(f"生成图片: {image_url}")
```

### curl示例

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "日出时分雾霭峡谷上方漂浮的发光城市，电影级写实风格，暖金色光线",
    "size": "1024x768",
    "n": 1
  }'
```

> 事实溯源：README.md L149-158

## 核心参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 图像模型ID：`agnes-image-2.1-flash` 或 `agnes-image-2.0-flash` |
| `prompt` | string | 是 | 图像描述提示词，越详细生成效果越好 |
| `size` | string | 否 | 图像尺寸，支持多种分辨率，见下文尺寸列表 |
| `n` | integer | 否 | 生成图片数量，默认1 |
| `response_format` | string | 否 | 输出格式：`url`（默认）或 `b64_json`（Base64编码） |

## 支持的图像尺寸

不同分辨率有不同的速率限制：

| 尺寸分类 | 典型分辨率 | Free用户实际RPM | Token Plan实际RPM |
|---------|-----------|----------------|------------------|
| 1K | 1024x1024、1024x768等 | 20 | 100 |
| 2K | 2048x1536、2048x2048等 | 10 | 80 |
| 3K | 3072x... | 1 | 1 |
| 4K | 4096x... | 1 | 1 |

> 事实溯源：F-026、F-027

### 常用尺寸推荐

| 用途 | 推荐尺寸 |
|------|---------|
| 社交媒体帖子 | `1024x1024`（方形） |
| 文章配图 | `1024x768`（4:3横版） |
| 壁纸/高清素材 | `2048x1536`（2K） |
| 海报设计 | `1536x2048`（3:4竖版） |

## 输出格式

### URL格式（默认）

生成的图片会返回可访问的URL：

```json
{
  "data": [
    {
      "url": "https://cdn.agnes-ai.com/generated/xxx.png",
      "revised_prompt": "优化后的提示词..."
    }
  ]
}
```

URL有有效期限制，请及时下载到本地存储。

### Base64格式

设置 `response_format: "b64_json"` 直接返回Base64编码的图片数据，适合不需要持久化URL的场景：

```python
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="可爱的猫咪头像",
    size="512x512",
    response_format="b64_json",
)

import base64
img_data = base64.b64decode(response.data[0].b64_json)
with open("cat.png", "wb") as f:
    f.write(img_data)
```

## 图生图（Image-to-Image）

`agnes-image-2.1-flash` 支持图像编辑能力，传入参考图片和修改提示词即可实现图生图转换：

```python
import base64

# 读取本地图片并编码为Base64
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

response = client.images.edit(
    model="agnes-image-2.1-flash",
    image=encode_image("input.jpg"),
    prompt="将背景改为海边日落场景，保持人物不变",
    size="1024x1024",
)
```

> 事实溯源：F-020

## 提示词最佳实践

好的提示词通常包含以下要素：

1. **主体描述**：核心对象是什么（如"一只橘猫"、"未来城市"）
2. **风格描述**：艺术风格（如"电影级写实"、"水彩画"、"赛博朋克"）
3. **光线氛围**：光照条件（如"暖金色日落光线"、"霓虹灯光"、"柔和工作室灯光"）
4. **构图视角**：拍摄角度（如"俯拍"、"特写"、"广角全景"）
5. **质量修饰**：画质关键词（如"8K高清"、"细节丰富"、"专业摄影"）

## 相关概念

- [对话补全API](03-chat-completions.md)
- [视频生成API](05-video-generation.md)
- [速率限制与配额](06-rate-limits.md)
- [图像生成示例](../examples/image-generation.md)
