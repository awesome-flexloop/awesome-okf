---
type: Concept
title: 视频生成 API
description: 视频生成接口（/v1/videos）完整指南，包含异步任务机制、文生视频、图生视频、结果轮询最佳实践
tags: [视频生成, Video Generation, 文生视频, 图生视频, 异步任务, 轮询]
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

# 视频生成 API

AgnesAI视频生成API提供文生视频（Text-to-Video）、图生视频（Image-to-Video）、多图视频和关键帧动画能力。视频生成采用**异步任务模式**：提交请求后返回`video_id`，需要轮询获取生成结果。

**端点**：`POST https://apihub.agnes-ai.com/v1/videos`

**支持模型**：
- `agnes-video-v2.0`：支持文生视频、图生视频、多图输入、关键帧动画

> 事实溯源：F-011、F-021

## 异步任务机制

视频生成是耗时操作（通常需要几十秒到几分钟），因此采用两步流程：

```
1. 提交生成任务 → 立即返回 video_id
2. 使用 video_id 轮询结果 → 任务完成后返回视频URL
```

**重要提示**：使用返回的 `video_id` 轮询结果，不要使用 `task_id`（遗留工作流）。

> 事实溯源：F-012、F-023、F-024

## 文生视频基础调用

### 提交任务

```python
import os
import requests
import time

API_KEY = os.getenv("AGNES_API_KEY")
BASE_URL = "https://apihub.agnes-ai.com/v1"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 步骤1：提交视频生成任务
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "日落时分，一只猫在海滩上行走，柔和的海浪，温暖的金色光线，真实的运动效果",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24,
}

response = requests.post(
    f"{BASE_URL}/videos",
    headers=headers,
    json=payload
)
response.raise_for_status()
task_data = response.json()
video_id = task_data["video_id"]
print(f"任务已提交，video_id: {video_id}")
```

### curl提交示例

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "日落时分，一只猫在海滩上行走，柔和的海浪，温暖的金色光线，真实的运动效果",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

> 事实溯源：README.md L162-174

## 轮询获取结果

提交任务后，使用`video_id`轮询结果端点：

**结果查询端点**：`GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`

```python
# 步骤2：轮询结果
def poll_video_result(video_id, poll_interval=5, max_wait=300):
    """
    轮询视频生成结果
    :param video_id: 任务返回的video_id
    :param poll_interval: 轮询间隔（秒），建议≥5秒
    :param max_wait: 最大等待时间（秒）
    """
    poll_url = f"https://apihub.agnes-ai.com/agnesapi?video_id={video_id}"
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        result = requests.get(poll_url, headers=headers)
        result.raise_for_status()
        data = result.json()
        
        status = data.get("status")
        
        if status == "completed":
            print("视频生成完成！")
            return data.get("video_url")
        elif status == "failed":
            error = data.get("error", "未知错误")
            raise Exception(f"视频生成失败: {error}")
        elif status in ["queued", "processing"]:
            print(f"任务状态: {status}，等待中...")
            time.sleep(poll_interval)
        else:
            print(f"未知状态: {status}")
            time.sleep(poll_interval)
    
    raise TimeoutError(f"等待超过{max_wait}秒，任务未完成")

# 使用示例
video_url = poll_video_result(video_id)
print(f"视频URL: {video_url}")
```

> 事实溯源：F-012、F-023

## 核心参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 固定为 `agnes-video-v2.0` |
| `prompt` | string | 是 | 视频内容描述提示词 |
| `height` | integer | 是 | 视频高度（像素），如768 |
| `width` | integer | 是 | 视频宽度（像素），如1152 |
| `num_frames` | integer | 否 | 总帧数，如121（约5秒@24fps） |
| `frame_rate` | integer | 否 | 帧率，常用24fps |
| `image` | string | 否 | 图生视频时的参考图片（Base64或URL） |
| `keyframes` | array | 否 | 关键帧列表，用于关键帧动画 |

## 视频时长计算

```
视频时长（秒） = num_frames / frame_rate
```

常见配置：
- 5秒短视频：121帧 @ 24fps
- 10秒视频：241帧 @ 24fps

> 事实溯源：README.md L171-172（示例中使用121帧@24fps）

## 图生视频

传入参考图片作为视频首帧，模型基于图片内容生成动态视频：

```python
import base64

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "agnes-video-v2.0",
    "prompt": "镜头缓慢推近，人物微微笑，头发随风飘动",
    "image": encode_image("reference.jpg"),  # 参考图片
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24,
}
```

## 轮询最佳实践

1. **轮询间隔**：建议5秒以上，不要过于频繁轮询，避免触发429限流
2. **超时设置**：根据视频长度设置合理超时，5秒视频通常30-60秒完成
3. **指数退避**：遇到429或5xx错误时使用指数退避重试
4. **状态处理**：明确处理queued/processing/completed/failed四种状态
5. **视频下载**：URL可能有有效期，生成完成后及时下载到本地存储

> 事实溯源：F-025（视频模型Free用户实际RPM仅为1）

## 配额说明

视频配额按**生成秒数**计算，而非请求次数：
- Free/Starter/Plus/Pro计划：均为500秒/天
- Token Plan：5 RPM，500秒/天

> 事实溯源：F-025、F-028~F-030

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 长时间停留在queued | 服务繁忙，队列较长 | 耐心等待，或降低视频分辨率/帧数重试 |
| 轮询返回404 | video_id错误或过期 | 检查video_id是否正确，任务结果可能已过期 |
| 生成失败 | 提示词违规、参数错误、资源不足 | 检查提示词是否符合规范，调整分辨率重试 |

## 相关概念

- [图像生成API](04-image-generation.md)
- [速率限制与配额](06-rate-limits.md)
- [错误处理与重试](07-error-handling.md)
- [视频生成示例](../examples/video-generation.md)
