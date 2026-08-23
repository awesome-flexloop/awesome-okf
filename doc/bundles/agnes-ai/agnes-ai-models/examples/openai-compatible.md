---
type: Example
title: OpenAI 兼容客户端配置
description: 最小化OpenAI兼容客户端配置示例，演示如何将现有OpenAI代码无缝迁移到AgnesAI
tags: [示例, OpenAI兼容, 迁移, SDK配置]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: example-openai
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/examples/python/openai_compatible.py
    title: 官方openai_compatible.py示例
---

# OpenAI 兼容客户端配置

AgnesAI完全兼容OpenAI API规范，这意味着你几乎不需要修改现有OpenAI代码，只需修改Base URL和API Key即可接入。

## 核心配置三要素

从OpenAI迁移到AgnesAI只需要修改三个地方：

| 配置项 | OpenAI官方 | AgnesAI |
|--------|-----------|---------|
| `base_url` | `https://api.openai.com/v1` | `https://apihub.agnes-ai.com/v1` |
| `api_key` | `sk-...`（OpenAI密钥） | AgnesAI平台获取的密钥 |
| `model` | `gpt-4o`、`gpt-3.5-turbo`等 | `agnes-2.5-flash`、`agnes-image-2.1-flash`等 |

## 最小可运行示例

```python
"""最小化OpenAI兼容AgnesAI客户端示例"""

import os
from openai import OpenAI


def main() -> None:
    # 唯一的区别：修改base_url为AgnesAI网关
    client = OpenAI(
        api_key=os.environ["AGNES_API_KEY"],
        base_url="https://apihub.agnes-ai.com/v1",  # ← 只需要改这里
    )

    # 以下代码与使用OpenAI官方SDK完全一致
    response = client.chat.completions.create(
        model="agnes-2.5-flash",  # ← 模型名改为AgnesAI模型
        messages=[
            {
                "role": "system",
                "content": "你是一个简洁的API集成助手。",
            },
            {
                "role": "user",
                "content": "给出API集成上线前的三项检查。",
            },
        ],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
```

## 兼容性功能矩阵

AgnesAI兼容以下OpenAI API功能：

| 功能 | 兼容状态 | 说明 |
|------|---------|------|
| Chat Completions | ✅ 完全兼容 | 支持流式、非流式、多轮对话 |
| Function Calling (Tools) | ✅ 完全兼容 | 工具调用格式与OpenAI一致 |
| Streaming (SSE) | ✅ 完全兼容 | 逐块返回delta内容 |
| Image Generation | ✅ 兼容 | `/v1/images/generations`端点 |
| Vision（图像理解） | ✅ 兼容 | 支持image_url输入 |
| Embeddings | ⚠️ 部分支持 | 参考最新官方文档 |
| Fine-tuning | ❌ 不支持 | 暂不支持微调API |
| Audio (TTS/STT) | ⚠️ 计划中 | 参考官方更新 |

## 现有项目无缝迁移

如果你已经有基于OpenAI SDK的项目，可以通过环境变量实现零代码修改迁移：

```bash
# Linux/macOS - 设置环境变量覆盖默认配置
export OPENAI_API_KEY="your_agnes_api_key"
export OPENAI_BASE_URL="https://apihub.agnes-ai.com/v1"

# 直接运行现有代码，无需修改
python your_existing_script.py
```

这是因为OpenAI Python SDK会自动读取 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY` 环境变量。

### 代码封装建议

为了支持多服务商切换，建议封装客户端创建逻辑：

```python
import os
from openai import OpenAI

def create_ai_client(provider="agnes"):
    """
    创建AI客户端，支持多服务商切换
    """
    configs = {
        "agnes": {
            "api_key": os.getenv("AGNES_API_KEY"),
            "base_url": "https://apihub.agnes-ai.com/v1",
            "default_model": "agnes-2.5-flash",
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-4o",
        },
    }
    
    config = configs[provider]
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )
    return client, config["default_model"]

# 使用示例
client, model = create_ai_client("agnes")
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## curl兼容示例

不使用SDK时，curl命令格式也与OpenAI完全一致：

```bash
# AgnesAI调用
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": "Hi"}]}'

# OpenAI调用（对比）
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}'
```

可以看到，除了base URL、API Key和model名称，其他完全一致。

## 兼容性注意事项

1. **模型命名空间不同**：不要使用OpenAI的模型名（如`gpt-4o`），必须使用AgnesAI的模型ID
2. **参数支持差异**：部分OpenAI特有的参数（如`response_format: json_object`等）参考官方文档确认是否支持
3. **上下文窗口差异**：不同模型有不同的上下文长度限制，参考模型目录文档
4. **速率限制不同**：AgnesAI的速率限制与OpenAI不同，需要相应调整并发策略

## 相关示例

- [Python对话补全示例](/examples/chat-completion.md)
- [流式对话示例](/examples/streaming-chat.md)
- [Agent工作流示例](/examples/agent-workflow.md)

## 相关概念

- [Agnes AI 简介](/concepts/00-introduction.md)
- [对话补全 API](/concepts/03-chat-completions.md)
- [速率限制与配额](/concepts/06-rate-limits.md)
