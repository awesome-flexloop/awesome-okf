---
okf_version: "0.2"
type: example
title: 快速创建 Agent 并运行
description: 使用 VeADK 的 Agent 和 Runner 类快速创建一个 LLM Agent，配置模型参数，通过 Runner.run() 执行对话，支持多轮会话和流式输出
tags: [veadk-python, example, quickstart, agent, runner, chat, llm]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/agent-and-runner.md
  - /concepts/model-configuration.md
sources:
  - id: veadk-python-self
    resource: /references/veadk-python-sources.md
    title: veadk-python 源码参考
---

# 快速创建 Agent 并运行

## 场景说明

本示例演示如何使用 VeADK（Volcengine Agent Development Kit）快速创建一个 LLM Agent。VeADK 的核心设计是 `Agent`（持有模型和指令）+ `Runner`（驱动对话执行）的分离架构。`Agent` 定义了模型选择、系统指令、工具集等静态配置，`Runner` 负责会话管理、记忆存取、调用执行等运行时逻辑。这是使用 VeADK 的入门基础。

**前置条件**：
- Python ≥ 3.10
- 已安装 veadk-python（`pip install veadk-python`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务（火山引擎方舟、OpenAI、DeepSeek、Ollama 等）
- 设置模型 API Key 环境变量（如 `OPENAI_API_KEY` 或 `ARK_API_KEY`）

## 完整代码示例

```python
"""
quickstart-agent.py
演示：使用 VeADK 创建 Agent 并通过 Runner 运行对话
"""

import asyncio
import os

# ── 步骤 1：导入核心类 ──
from veadk import Agent, Runner


# ── 步骤 2：创建 Agent 实例 ──

def create_agent() -> Agent:
    """
    创建一个配置好的 Agent 实例。

    Agent 继承自 Google ADK 的 LlmAgent，包含模型配置、
    系统指令、工具集、记忆模块等所有静态定义。
    """
    agent = Agent(
        # ── 基本标识 ──
        name="assistant",                    # Agent 名称（唯一标识）
        description="一个友好的中文助手",      # Agent 描述（A2A 场景使用）
        instruction=(                        # 系统指令（System Prompt）
            "你是一个乐于助人的 AI 助手。"
            "请用中文回答用户的问题，回答要简洁准确。"
            "如果不确定答案，请诚实说明，不要编造信息。"
        ),

        # ── 模型配置 ──
        model=os.getenv("VEADK_MODEL", "gpt-4o-mini"),  # 模型名称
        # model_name 也可直接指定
        # model_name="doubao-pro-32k",
        # model_provider="openai",                        # 模型提供商
        # model_api_base="https://ark.cn-beijing.volces.com/api/v3",  # API 端点
        # model_api_key=os.getenv("ARK_API_KEY", ""),     # API Key

        # ── 工具配置（可选）──
        tools=[],  # 不添加额外工具，纯对话模式
    )
    return agent


# ── 步骤 3：单轮对话 ──

async def single_turn_demo():
    """最简单的单轮对话示例。"""
    agent = create_agent()

    # Runner 驱动 Agent 执行
    runner = Runner(
        agent=agent,
        app_name="quickstart_demo",   # 应用名（用于会话隔离、日志标识）
        user_id="demo_user",          # 默认用户 ID
    )

    # runner.run() 是异步方法，返回最终文本答案
    answer = await runner.run(
        messages="用一句话介绍火山引擎（Volcengine）。",
        session_id="demo-session-1",   # 会话 ID（同 ID 共享上下文）
    )
    print(f"[单轮对话] Agent 回答: {answer}")
    return answer


# ── 步骤 4：多轮对话 ──

async def multi_turn_demo():
    """
    多轮对话示例。

    使用相同的 session_id，Runner 会自动维护对话历史，
    Agent 可以理解上下文中的指代关系。
    """
    agent = create_agent()
    runner = Runner(agent=agent, app_name="quickstart_demo")
    session_id = "multi-turn-session"

    # 第一轮
    answer1 = await runner.run(
        messages="我叫小明，是一名 Python 开发者。",
        session_id=session_id,
    )
    print(f"\n[多轮-1] 你: 我叫小明，是一名 Python 开发者。")
    print(f"[多轮-1] Agent: {answer1}")

    # 第二轮（Agent 应记住"小明"和"Python 开发者"）
    answer2 = await runner.run(
        messages="你还记得我叫什么吗？我做什么工作的？",
        session_id=session_id,
    )
    print(f"\n[多轮-2] 你: 你还记得我叫什么吗？我做什么工作的？")
    print(f"[多轮-2] Agent: {answer2}")

    # 第三轮
    answer3 = await runner.run(
        messages="推荐一本适合进阶的 Python 书籍。",
        session_id=session_id,
    )
    print(f"\n[多轮-3] 你: 推荐一本适合进阶的 Python 书籍。")
    print(f"[多轮-3] Agent: {answer3}")


# ── 步骤 5：流式输出 ──

async def streaming_demo():
    """
    流式输出示例。

    使用 runner.run_async() 可以获得事件流，
    实时获取 Agent 的输出增量，适合聊天界面。
    """
    agent = create_agent()
    runner = Runner(agent=agent, app_name="quickstart_demo")
    session_id = "streaming-session"

    print("\n[流式对话] Agent: ", end="", flush=True)

    # run_async 返回异步事件生成器
    async for event in runner.run_async(
        message="请用三句话介绍人工智能的发展历史。",
        session_id=session_id,
    ):
        # 事件包含不同类型：delta（增量文本）、thinking（思考）、tool_call等
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text, end="", flush=True)

    print()  # 换行


# ── 步骤 6：自定义模型配置 ──

async def custom_model_demo():
    """
    使用自定义模型配置（如本地 Ollama、DeepSeek 等）。

    通过 model_provider 和 model_api_base 可以接入任何
    兼容 OpenAI API 格式的模型服务。
    """
    agent = Agent(
        name="local_agent",
        instruction="你是一个简洁的助手，用中文回答。",
        # 接入本地 Ollama
        # model_name="qwen2.5:7b",
        # model_provider="openai",
        # model_api_base="http://localhost:11434/v1",
        # model_api_key="ollama",  # Ollama 不需要真实 key

        # 接入 DeepSeek
        model_name="deepseek-chat",
        model_provider="openai",
        model_api_base="https://api.deepseek.com/v1",
        model_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    )

    runner = Runner(agent=agent, app_name="custom_model_demo")
    answer = await runner.run(
        messages="你好，你是什么模型？",
        session_id="custom-model-session",
    )
    print(f"\n[自定义模型] Agent: {answer}")


# ── 主入口 ──

async def main():
    print("=== VeADK 快速入门示例 ===\n")

    # 1. 单轮对话
    await single_turn_demo()

    # 2. 多轮对话
    await multi_turn_demo()

    # 3. 流式输出
    await streaming_demo()

    # 4. 自定义模型（需要配置对应 API Key）
    # await custom_model_demo()

    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
```

## 逐步解释

### 步骤 1：导入核心类

VeADK 使用懒加载机制，从 `veadk` 包直接导入 `Agent` 和 `Runner`：
- `Agent`：定义 Agent 的静态配置（模型、指令、工具、记忆等）
- `Runner`：运行时执行引擎，管理会话、驱动 Agent 循环、处理记忆

### 步骤 2：创建 Agent 实例

`Agent` 继承自 Google ADK 的 `LlmAgent`，关键参数包括：

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | Agent 唯一名称，用于标识和 A2A 场景 |
| `description` | str | Agent 功能描述，用于 A2A 服务发现 |
| `instruction` | str | System Prompt，定义 Agent 行为和角色 |
| `model_name` | str/list[str] | 模型名称，支持模型列表（故障转移） |
| `model_provider` | str | 模型提供商（openai/anthropic 等，兼容 OpenAI 格式用 openai） |
| `model_api_base` | str | 模型 API 端点 URL |
| `model_api_key` | str | 模型 API 密钥 |
| `tools` | list | 工具列表（函数工具、MCP 工具等） |
| `sub_agents` | list | 子 Agent 列表（用于 Agent 委派） |
| `knowledgebase` | KnowledgeBase | 挂载知识库（自动添加检索工具） |
| `short_term_memory` | ShortTermMemory | 短期记忆配置 |
| `long_term_memory` | LongTermMemory | 长期记忆配置 |

如果不设置 `model_api_key`，VeADK 会自动从环境变量或配置文件解析。

### 步骤 3：单轮对话

`Runner` 是无状态执行器，关键参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `agent` | Agent | 要运行的 Agent 实例 |
| `app_name` | str | 应用名（用于会话存储路径隔离） |
| `user_id` | str | 默认用户 ID（可被 run() 参数覆盖） |
| `short_term_memory` | ShortTermMemory | 短期记忆（不传则使用内存存储） |

`runner.run()` 方法：
- `messages`：用户消息（字符串或消息列表）
- `session_id`：会话 ID（同 ID 共享对话历史）
- `user_id`：用户 ID（覆盖默认值）
- 返回值：最终文本响应（str）

### 步骤 4：多轮对话

多轮对话的关键是**使用相同的 `session_id`**：
- Runner 自动维护会话历史（通过 ShortTermMemory 存储）
- 相同 session_id 的后续消息会携带之前的上下文
- 不同 session_id 的对话完全隔离
- 不指定 session_id 时使用临时会话（不持久化）

### 步骤 5：流式输出

`runner.run_async()` 返回异步事件生成器，产生 ADK Event 对象：
- `event.content.parts` 包含响应片段
- `part.text` 是增量文本内容
- 可实时输出到 UI，提供打字机效果
- 还可以监听 `tool_call`、`thinking` 等事件类型

### 步骤 6：自定义模型配置

VeADK 通过 LiteLLM 接入模型，任何兼容 OpenAI Chat Completions API 的服务都可使用：
- 本地 Ollama：`model_api_base="http://localhost:11434/v1"`，`model_api_key="ollama"`
- DeepSeek：`model_api_base="https://api.deepseek.com/v1"`
- 火山方舟：`model_api_base="https://ark.cn-beijing.volces.com/api/v3"`
- vLLM/llama.cpp 等本地部署：设置对应 base_url 即可

## 输出结果

运行脚本后，预期输出类似：

```
=== VeADK 快速入门示例 ===

[单轮对话] Agent 回答: 火山引擎（Volcengine）是字节跳动推出的云服务平台，提供计算、存储、AI大模型等一站式云服务能力。

[多轮-1] 你: 我叫小明，是一名 Python 开发者。
[多轮-1] Agent: 你好小明！很高兴认识你，一位 Python 开发者。有什么我可以帮助你的吗？

[多轮-2] 你: 你还记得我叫什么吗？我做什么工作的？
[多轮-2] Agent: 你当然记得！你叫小明，是一名 Python 开发者。😊

[多轮-3] 你: 推荐一本适合进阶的 Python 书籍。
[多轮-3] Agent: 推荐《流畅的 Python》（Fluent Python）第二版，适合进阶开发者深入理解 Python 的特性和最佳实践。

[流式对话] Agent: 人工智能的发展历史可以追溯到1956年达特茅斯会议，当时"人工智能"一词被正式提出...
```

## 注意事项

1. **异步编程**：VeADK 的 Runner 是全异步设计，`run()` 和 `run_async()` 都是 async 方法，必须在 `asyncio.run()` 或异步环境中调用。

2. **session_id 的重要性**：多轮对话必须使用相同的 session_id。建议使用有意义的命名（如 `user_123_chat`），避免使用随机字符串导致调试困难。

3. **模型 API Key**：如果不显式传入 `model_api_key`，VeADK 会按优先级从 `model_api_key_name` → 环境变量 → 配置文件解析。建议生产环境通过环境变量注入，不要硬编码。

4. **模型名称格式**：使用火山方舟（Ark）时，`model_name` 通常是端点 ID（如 `ep-2024xxxx-xxxxx`）；使用 OpenAI 时是模型名（如 `gpt-4o-mini`）。

5. **tools 默认为空**：创建 Agent 时 `tools=[]` 表示不挂载任何工具，Agent 只能进行纯文本对话。需要工具调用能力时需显式添加。

6. **app_name 隔离**：不同 app_name 的会话存储相互隔离，一个应用不会访问到另一个应用的会话数据。

7. **环境变量优化**：VeADK 默认设置 `LITELLM_LOCAL_MODEL_COST_MAP=True`，避免每次导入 LiteLLM 时下载模型成本映射表（可节省约 10 秒导入时间）。

8. **ShortTermMemory 可选**：Runner 不传 short_term_memory 时会自动创建内存会话服务。组合 Agent（Sequential/Parallel）需要显式传入 ShortTermMemory。
