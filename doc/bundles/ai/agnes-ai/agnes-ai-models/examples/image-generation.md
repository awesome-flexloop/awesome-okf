---
type: Example
title: 图像生成示例
description: 文生图完整示例，包含请求发送、结果获取、URL/Base64输出处理
tags: [示例, Python, 图像生成, 文生图]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: example-image
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/examples/python/image_generation.py
    title: 官方image_generation.py示例
---

# 图像生成示例

本示例演示如何调用AgnesAI图像生成API创建图片，兼容OpenAI Images API格式。

## 基础文生图示例

```python
"""Agnes AI 文生图示例"""

import os
from openai import OpenAI


def main() -> None:
    client = OpenAI(
        api_key=os.environ["AGNES_API_KEY"],
        base_url="https://apihub.agnes-ai.com/v1",
    )

    # 调用图像生成API
    response = client.images.generate(
        model="agnes-image-2.1-flash",  # 推荐使用2.1版本
        prompt=(
            "一个干净的AI API网关仪表盘产品风格图片，"
            "现代界面设计，明亮的工作室灯光"
        ),
        size="1024x1024",  # 方形尺寸
        n=1,               # 生成1张图
    )

    # 获取结果（兼容URL或Base64输出）
    image = response.data[0]
    result = getattr(image, "url", None) or getattr(image, "b64_json", None)
    print(f"生成结果: {result}")


if __name__ == "__main__":
    main()
```

## 保存图片到本地

获取URL后下载图片到本地：

```python
import requests
import os

def download_image(url, save_path="generated_image.png"):
    """下载生成的图片到本地"""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"图片已保存到: {os.path.abspath(save_path)}")

# 使用示例
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="可爱的橘猫在阳光下睡觉，水彩画风格",
    size="1024x1024",
)
image_url = response.data[0].url
download_image(image_url, "cat.png")
```

## Base64输出模式

不需要URL时可以直接获取Base64编码，适合立即使用无需下载的场景：

```python
import base64

response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="赛博朋克风格的城市夜景",
    size="1024x768",
    response_format="b64_json",  # 返回Base64
)

# 解码保存
img_data = base64.b64decode(response.data[0].b64_json)
with open("cyberpunk.png", "wb") as f:
    f.write(img_data)
```

## 批量生成多张图

设置 `n>1` 一次生成多张：

```python
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="不同风格的logo设计：简约科技风",
    size="1024x1024",
    n=4,  # 生成4张图供选择
)

for i, image in enumerate(response.data):
    print(f"图片{i+1}: {image.url}")
```

注意：批量生成会消耗更多配额，且受RPM速率限制约束。

## 提示词建议

为了获得更好的生成效果，提示词中建议包含：

```python
good_prompt = """
主体：一只穿着宇航服的柯基犬在月球上
风格：皮克斯动画风格，3D渲染
光线：柔和的宇宙星光，地球反射的蓝色光芒
构图：中景镜头，低角度拍摄
画质：8K高清，细节丰富，电影级质感
""".strip()

response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt=good_prompt,
    size="1024x1024",
)
```

## curl调用示例

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "日出时分雾霭峡谷上方漂浮的发光城市，电影级写实风格",
    "size": "1024x768",
    "n": 1
  }'
```

## 常见问题

| 问题 | 解决方法 |
|------|---------|
| 图片URL过期 | URL有时效性，生成后及时下载到本地，使用b64_json模式避免此问题 |
| 生成内容被拒绝 | 提示词可能违反内容政策，修改描述避免敏感内容 |
| 3K/4K分辨率报错 | 高分辨率RPM限制极低（1 RPM），降低到1K/2K或等待重试 |

## 相关示例

- [Python对话补全示例](/examples/chat-completion.md)
- [视频生成示例](/examples/video-generation.md)
- [Agent工作流示例](/examples/agent-workflow.md)

## 相关概念

- [图像生成 API](/concepts/04-image-generation.md)
- [速率限制与配额](/concepts/06-rate-limits.md)
