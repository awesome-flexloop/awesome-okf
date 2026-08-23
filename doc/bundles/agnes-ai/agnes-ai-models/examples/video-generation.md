---
type: Example
title: 视频生成示例
description: 视频异步生成完整示例，包含任务提交、轮询等待、结果获取的完整流程
tags: [示例, Python, 视频生成, 异步任务, 轮询]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: example-video
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/examples/python/video_generation.py
    title: 官方video_generation.py示例
---

# 视频生成示例

视频生成是异步API，需要先提交任务获取video_id，然后轮询查询结果。本示例演示完整的视频生成流程。

## 完整可运行示例

```python
"""Agnes AI 文生视频：任务提交 + 轮询完整示例"""

import os
import time
from typing import Any

import requests


API_KEY = os.environ["AGNES_API_KEY"]
API_ROOT = "https://apihub.agnes-ai.com"


def request_json(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    """带认证的HTTP请求封装"""
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {API_KEY}"
    headers["Content-Type"] = "application/json"

    response = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    response.raise_for_status()
    return response.json()


def create_video(prompt: str, width: int = 1152, height: int = 768, 
                num_frames: int = 121, frame_rate: int = 24) -> str:
    """
    提交视频生成任务
    :return: video_id 用于轮询结果
    """
    payload = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "height": height,
        "width": width,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }

    data = request_json("POST", f"{API_ROOT}/v1/videos", json=payload)
    video_id = data.get("video_id") or data.get("id")
    if not video_id:
        raise RuntimeError(f"响应中未包含video_id: {data}")
    return video_id


def poll_video(video_id: str, poll_interval: int = 5, max_wait: int = 300) -> dict[str, Any]:
    """
    轮询视频生成结果
    :param video_id: 任务返回的video_id
    :param poll_interval: 轮询间隔（秒），建议≥5秒
    :param max_wait: 最大等待时间（秒）
    :return: 生成完成的结果数据
    """
    for attempt in range(max_wait // poll_interval):
        data = request_json("GET", f"{API_ROOT}/agnesapi", 
                          params={"video_id": video_id})
        status = str(data.get("status", "")).lower()
        
        # 完成状态
        if status in {"succeeded", "success", "completed", "done"}:
            return data
        # 失败状态
        if status in {"failed", "error", "cancelled"}:
            raise RuntimeError(f"视频生成失败: {data}")
        # 等待中
        print(f"[{attempt*poll_interval}s] 状态: {status}，继续等待...")
        time.sleep(poll_interval)

    raise TimeoutError(f"等待超时（{max_wait}秒），video_id={video_id}")


def download_video(video_url: str, save_path: str = "output.mp4") -> None:
    """下载视频到本地"""
    print(f"正在下载视频: {video_url}")
    response = requests.get(video_url, timeout=120, stream=True)
    response.raise_for_status()
    
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"视频已保存到: {os.path.abspath(save_path)}")


def main() -> None:
    # 步骤1：提交视频生成任务
    prompt = (
        "电影级产品镜头：发光的AI模型目录界面，"
        "流畅的镜头运动，真实的光影效果"
    )
    print(f"提交任务，prompt: {prompt[:50]}...")
    video_id = create_video(prompt)
    print(f"任务已创建，video_id: {video_id}")

    # 步骤2：轮询等待结果
    print("开始轮询结果...")
    result = poll_video(video_id, poll_interval=5)
    
    # 步骤3：获取并下载视频
    video_url = result.get("video_url") or result.get("url")
    if video_url:
        download_video(video_url)
    else:
        print(f"结果数据: {result}")


if __name__ == "__main__":
    main()
```

## 视频时长计算

```
视频时长 = num_frames / frame_rate
```

常用配置参考：

| 时长 | num_frames | frame_rate | 文件大小（约） |
|------|-----------|------------|--------------|
| 5秒短视频 | 121 | 24fps | 2-5MB |
| 10秒视频 | 241 | 24fps | 5-10MB |
| 30秒视频 | 721 | 24fps | 15-30MB |

> 注意：视频越长，生成时间越久，配额消耗越多。建议从短视频开始测试。

## 带重试的健壮版轮询

生产环境建议添加错误重试逻辑：

```python
import random

def poll_video_with_retry(video_id, poll_interval=5, max_wait=300, max_retries=3):
    """带网络错误重试的轮询"""
    start_time = time.time()
    retries = 0
    
    while time.time() - start_time < max_wait:
        try:
            data = request_json("GET", f"{API_ROOT}/agnesapi", 
                              params={"video_id": video_id})
            retries = 0  # 成功请求后重置重试计数
            status = str(data.get("status", "")).lower()
            
            if status in {"succeeded", "success", "completed", "done"}:
                return data
            if status in {"failed", "error", "cancelled"}:
                raise RuntimeError(f"视频生成失败: {data}")
                
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries > max_retries:
                raise
            # 网络错误退避重试
            delay = poll_interval * (2 ** retries) + random.uniform(0, 1)
            print(f"网络错误: {e}，{delay:.1f}秒后重试...")
            time.sleep(delay)
            continue
            
        time.sleep(poll_interval)
    
    raise TimeoutError(f"等待超时")
```

## curl调用示例

### 提交任务

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "日落时分，一只猫在海滩上行走，柔和的海浪，暖金色光线",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

### 轮询结果

```bash
curl "https://apihub.agnes-ai.com/agnesapi?video_id=YOUR_VIDEO_ID" \
  -H "Authorization: Bearer $AGNES_API_KEY"
```

## 最佳实践

1. **轮询间隔不要太短**：建议5秒以上，避免浪费请求和触发限流
2. **设置合理超时**：5秒视频通常30-60秒完成，设置5分钟超时足够
3. **及时下载视频**：视频URL可能有有效期，生成完成后立即下载
4. **处理所有状态**：明确处理queued/processing/completed/failed状态
5. **从短视频开始**：先用5秒视频（121帧）测试流程，确认无误再延长
6. **视频配额按秒算**：注意500秒/天的配额限制，测试时不要浪费

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 一直queued不处理 | 服务繁忙 | 耐心等待，或错峰使用，降低分辨率重试 |
| 429限流 | 轮询太频繁或RPM用完 | 增加轮询间隔到5秒以上 |
| 生成失败 | 提示词违规、参数错误 | 检查提示词内容，调整分辨率重试 |
| 视频下载失败 | URL过期 | 重新生成或及时下载 |

## 相关示例

- [图像生成示例](/examples/image-generation.md)
- [Python对话补全示例](/examples/chat-completion.md)
- [Agent工作流示例](/examples/agent-workflow.md)

## 相关概念

- [视频生成 API](/concepts/05-video-generation.md)
- [错误处理与调试](/concepts/07-error-handling.md)
- [速率限制与配额](/concepts/06-rate-limits.md)
