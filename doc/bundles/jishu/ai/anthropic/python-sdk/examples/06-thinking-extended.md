---
type: example
title: "Extended Thinking与高级参数"
description: "使用Extended Thinking（扩展思考）提高推理质量，包括thinking参数配置、thinking内容块读取、提示缓存框架、采样参数调整及相关约束。"
tags: [thinking, extended-thinking, reasoning, cache-control, temperature, sampling, advanced]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-016~F-023
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: concept-02
    resource: /python-sdk/concepts/02-messages-basics.md
    title: "Messages API 基础"
  - id: concept-03
    resource: /python-sdk/concepts/03-streaming.md
    title: "流式响应处理"
---

# Extended Thinking与高级参数

本示例演示 Anthropic Python SDK 的高级功能，重点是 Extended Thinking（扩展思考）能力——让 Claude 在回答前先进行更深入的结构化思考，显著提升复杂推理任务的准确性。此外还包括：采样参数（temperature/top_p/top_k）调整、提示缓存（cache_control）框架，以及这些高级参数的使用约束。

## Extended Thinking 是什么

Extended Thinking 是 Claude 的一项高级推理能力。启用后，Claude 会在给出最终答案前先生成一段"思考过程"，类似于人类解决复杂问题时的草稿演算。这段思考过程：
- 对模型可见（用于提升回答质量）
- 对开发者可见（你可以读取，用于调试、审计、展示推理链）
- 不直接作为最终回答呈现给用户

适合开启 Extended Thinking 的场景：数学题、逻辑推理、复杂代码问题、多步骤分析、需要仔细推敲的决策任务。

## 前置准备

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

> ⚠️ **注意**：Extended Thinking 是较新的功能，需要使用支持该功能的模型（如 Claude Opus 4、Claude 3.7 Sonnet 及之后的模型）。使用前请确认你使用的模型版本支持此功能。

## 完整代码

```python
import os
import json
from anthropic import Anthropic


# ========== Extended Thinking 基础用法 ==========

def chat_with_thinking(client: Anthropic, question: str, thinking_budget: int = 2048) -> dict:
    """
    使用 Extended Thinking 进行对话，返回思考过程和最终回答。

    Args:
        client: Anthropic 客户端
        question: 用户问题
        thinking_budget: 思考 token 预算（至少 1024）

    Returns:
        包含 thinking（思考过程）和 answer（最终回答）的字典
    """
    # 启用 Extended Thinking
    # 注意：启用 thinking 时，temperature 必须设置为 1（这是硬性约束）
    message = client.messages.create(
        model="claude-3-7-sonnet-latest",  # 使用支持 thinking 的模型
        max_tokens=4096,  # 需要给思考和回答留足够的 token
        messages=[
            {"role": "user", "content": question}
        ],
        # 核心：启用 Extended Thinking
        thinking={
            "type": "enabled",
            "budget_tokens": thinking_budget,  # 思考过程的最大 token 数
        },
        # ⚠️ 重要约束：启用 thinking 时 temperature 必须为 1
        temperature=1.0,
    )

    # 解析响应：content 中会有 thinking 和 text 两种内容块
    thinking_text = ""
    answer_text = ""

    for block in message.content:
        if block.type == "thinking":
            # 思考过程块
            thinking_text = block.thinking
        elif block.type == "text":
            # 最终回答文本块
            answer_text = block.text

    return {
        "thinking": thinking_text,
        "answer": answer_text,
        "stop_reason": message.stop_reason,
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }
    }


# ========== 数学推理：Extended Thinking 的典型场景 ==========

def math_reasoning_demo(client: Anthropic):
    """
    演示 Extended Thinking 在数学推理题上的效果。
    复杂多步计算是 Extended Thinking 最能发挥优势的场景之一。
    """
    print("=" * 60)
    print("Extended Thinking 演示：数学推理")
    print("=" * 60)

    question = """一个农夫有鸡和兔子共35只，关在同一个笼子里。
已知笼子里总共有94只脚。
请问鸡和兔子各有多少只？
请一步步思考，给出详细的解题过程。"""

    print(f"\n问题：{question}\n")
    print("-" * 60)

    # 用 Extended Thinking 解答
    result = chat_with_thinking(client, question, thinking_budget=1024)

    if result["thinking"]:
        print("【Claude 的思考过程】")
        print(result["thinking"])
        print("-" * 60)

    print("【最终回答】")
    print(result["answer"])
    print("-" * 60)
    print(f"Token 使用：输入 {result['usage']['input_tokens']} / 输出 {result['usage']['output_tokens']}")


# ========== 代码分析：Extended Thinking 用于复杂调试 ==========

def code_analysis_demo(client: Anthropic):
    """
    演示用 Extended Thinking 分析代码问题。
    """
    print("\n" + "=" * 60)
    print("Extended Thinking 演示：代码问题分析")
    print("=" * 60)

    code_question = """分析以下 Python 代码有什么问题，如何修复：

```python
def factorial(n):
    if n == 0:
        return 0
    else:
        return n * factorial(n)

print(factorial(5))
```

请仔细思考：
1. 这段代码想实现什么功能？
2. 存在哪些 bug？
3. 给出修复后的代码和解释。"""

    print(f"\n任务：分析代码问题\n")
    print("-" * 60)

    result = chat_with_thinking(client, code_question, thinking_budget=2048)

    if result["thinking"]:
        print("【思考过程】")
        print(result["thinking"])
        print("-" * 60)

    print("【分析结果】")
    print(result["answer"])


# ========== 流式模式下的 Extended Thinking ==========

def streaming_thinking_demo(client: Anthropic, question: str):
    """
    流式模式下使用 Extended Thinking。
    你可以实时看到思考过程和最终回答的生成。

    Args:
        client: Anthropic 客户端
        question: 用户问题
    """
    print("\n" + "=" * 60)
    print("流式 Extended Thinking 演示")
    print("=" * 60)
    print(f"\n问题：{question}\n")
    print("-" * 60)

    thinking_accumulated = ""
    answer_accumulated = ""
    current_block_type = None

    # 流式模式同样支持 thinking
    with client.messages.stream(
        model="claude-3-7-sonnet-latest",
        max_tokens=4096,
        messages=[{"role": "user", "content": question}],
        thinking={
            "type": "enabled",
            "budget_tokens": 2048,
        },
        temperature=1.0,
    ) as stream:
        print("【思考过程（实时）】")
        for event in stream:
            if event.type == "content_block_start":
                # 新内容块开始，判断是 thinking 还是 text
                if event.content_block.type == "thinking":
                    current_block_type = "thinking"
                    print("\n💭 ", end="", flush=True)
                elif event.content_block.type == "text":
                    current_block_type = "text"
                    print("\n\n" + "-" * 60)
                    print("【最终回答（实时）】")
                    print("\n✓ ", end="", flush=True)

            elif event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    # 思考增量
                    thinking_text = event.delta.thinking
                    thinking_accumulated += thinking_text
                    print(thinking_text, end="", flush=True)
                elif event.delta.type == "text_delta":
                    # 回答增量
                    text = event.delta.text
                    answer_accumulated += text
                    print(text, end="", flush=True)

        # 流结束后获取最终消息
        final_msg = stream.get_final_message()
        print("\n" + "-" * 60)
        print(f"完成 | 输出 token：{final_msg.usage.output_tokens}")

    return {
        "thinking": thinking_accumulated,
        "answer": answer_accumulated
    }


# ========== 采样参数调整 ==========

def sampling_parameters_demo(client: Anthropic):
    """
    演示采样参数 temperature/top_p/top_k 的效果。
    这些参数控制生成的随机性和创造性。

    注意：启用 Extended Thinking 时 temperature 必须为 1，
    因此采样参数调整仅适用于不使用 thinking 的场景。
    """
    print("\n" + "=" * 60)
    print("采样参数调整演示")
    print("=" * 60)

    prompt = "给我三个有创意的 Python 项目点子，适合周末做。"

    configs = [
        {"name": "精确/确定性（temperature=0）", "temperature": 0.0, "top_p": 1.0},
        {"name": "平衡（temperature=0.7，推荐默认）", "temperature": 0.7, "top_p": 1.0},
        {"name": "创造性/随机（temperature=1.0）", "temperature": 1.0, "top_p": 1.0},
        {"name": "核采样（top_p=0.9，聚焦高概率词）", "temperature": 0.8, "top_p": 0.9},
    ]

    for config in configs:
        print(f"\n--- {config['name']} ---")
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
                temperature=config["temperature"],
                top_p=config["top_p"],
                # 注意：这里没有启用 thinking，所以可以自由调整 temperature
            )
            reply = message.content[0].text
            print(reply[:300] + "..." if len(reply) > 300 else reply)
        except Exception as e:
            print(f"（参数组合可能不受支持：{e}）")


# ========== 提示缓存（cache_control）使用框架 ==========

def prompt_caching_framework(client: Anthropic):
    """
    提示缓存（Prompt Caching）使用框架。

    提示缓存可以缓存重复使用的大型系统提示词、文档上下文等，
    显著降低延迟和成本。cache_control 参数标记哪些内容块需要缓存。

    注意：这是一个框架示例，实际缓存效果和计费需要参考 Anthropic 最新文档。
    """
    print("\n" + "=" * 60)
    print("提示缓存框架示例（概念演示）")
    print("=" * 60)

    print("""
提示缓存核心概念：
1. 使用 cache_control 参数标记可缓存的内容块
2. 缓存的内容在多次请求间复用，减少重复处理
3. 适合缓存：大型系统提示词、长文档上下文、RAG检索结果
4. 缓存内容放在 messages 或 system 的前面部分

基本使用模式：

# 系统提示词缓存
system_prompt = [
    {
        "type": "text",
        "text": "你是一个资深Python专家...（长系统提示词）",
        "cache_control": {"type": "ephemeral"}  # 标记为可缓存
    }
]

# 多轮对话中缓存固定上下文
messages = [
    # 第一条消息包含大型上下文，标记缓存
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "这是一份很长的文档...（大型上下文）",
                "cache_control": {"type": "ephemeral"}
            }
        ]
    },
    # 后续对话围绕这份文档提问，缓存命中
    {"role": "assistant", "content": "好的，我已阅读文档。"},
    {"role": "user", "content": "文档的第3章讲了什么？"}
]

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    system=system_prompt,
    messages=messages,
)
""")


# ========== Extended Thinking 与工具调用结合框架 ==========

def thinking_with_tools_framework():
    """
    Extended Thinking 与工具调用结合的框架示例。
    Claude 可以先思考是否需要调用工具、调用哪个工具、参数是什么，
    然后再发起工具调用，提升复杂工具使用场景的准确性。
    """
    print("\n" + "=" * 60)
    print("Extended Thinking + 工具调用框架（概念演示）")
    print("=" * 60)

    print("""
Extended Thinking 可以与工具调用无缝结合。流程：
1. Claude 先思考（thinking block）：分析问题、判断是否需要工具、选择工具
2. 然后发起工具调用（tool_use block）或直接回答（text block）
3. 工具结果返回后，Claude 可以再次思考，决定下一步

伪代码示例：

tools = [
    {
        "name": "get_stock_price",
        "description": "获取股票当前价格",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "股票代码"}
            },
            "required": ["symbol"]
        }
    }
]

message = client.messages.create(
    model="claude-3-7-sonnet-latest",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "AAPL和GOOGL现在股价差多少？我应该买哪个？"}
    ],
    tools=tools,
    thinking={"type": "enabled", "budget_tokens": 2048},
    temperature=1.0,
)

# 响应中可能包含：
# 1. thinking block：分析需要查询两支股票价格才能比较
# 2. tool_use blocks：同时调用 get_stock_price(AAPL) 和 get_stock_price(GOOGL)
# （并行工具调用）
""")


# ========== 主函数 ==========

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误：请先设置 ANTHROPIC_API_KEY 环境变量")
        print()
        print("本示例包含多个演示：")
        print("1. math_reasoning_demo()    - 数学推理（需要支持 thinking 的模型）")
        print("2. code_analysis_demo()    - 代码分析（需要支持 thinking 的模型）")
        print("3. streaming_thinking_demo() - 流式 thinking（需要支持 thinking 的模型）")
        print("4. sampling_parameters_demo() - 采样参数（无需特殊模型）")
        print("5. prompt_caching_framework() - 提示缓存框架（概念演示）")
        print("6. thinking_with_tools_framework() - 工具结合框架（概念演示）")
        return

    client = Anthropic()

    # ====== 采样参数演示（不需要 thinking 模型支持，可直接运行）======
    try:
        sampling_parameters_demo(client)
    except Exception as e:
        print(f"采样参数演示出错：{e}")

    # ====== 提示缓存和工具结合框架（概念演示，无需API调用）======
    prompt_caching_framework(client)
    thinking_with_tools_framework()

    # ====== Extended Thinking 演示（需要支持该功能的模型）======
    print("\n" + "=" * 60)
    print("尝试运行 Extended Thinking 演示...")
    print("（如果你使用的模型不支持 thinking，会显示错误信息——这是正常的）")
    print("=" * 60)

    try:
        # 数学推理
        math_reasoning_demo(client)

        # 代码分析
        code_analysis_demo(client)

        # 流式 thinking（注释掉避免过长输出，取消注释体验）
        # streaming_thinking_demo(
        #     client,
        #     "9.11和9.9哪个数字更大？为什么很多人会答错？"
        # )

    except Exception as e:
        print(f"\nExtended Thinking 演示提示：{type(e).__name__}")
        print(f"这通常是因为：")
        print(f"1. 你使用的模型不支持 Extended Thinking（需要较新的模型如 Claude 3.7+）")
        print(f"2. 或者你的 API 账号没有该功能访问权限")
        print(f"\n错误详情：{str(e)[:200]}")
        print()
        print("其他演示（采样参数、缓存框架）不受影响，仍可正常学习参考。")


if __name__ == "__main__":
    main()
```

## 运行方式

```bash
python 06-thinking-extended.py
```

## 代码解析

### 启用 Extended Thinking：thinking 参数

```python
message = client.messages.create(
    model="claude-3-7-sonnet-latest",
    max_tokens=4096,
    messages=[...],
    thinking={
        "type": "enabled",
        "budget_tokens": 2048,  # 思考预算
    },
    temperature=1.0,  # 必须是 1！
)
```

核心参数说明：

| 参数 | 说明 | 约束 |
|------|------|------|
| `thinking.type` | 固定为 `"enabled"` 启用思考 | - |
| `thinking.budget_tokens` | 思考过程的最大 token 数 | 最小值约为 1024，根据问题复杂度调整 |
| `temperature` | 采样温度 | **启用 thinking 时必须为 1.0**（硬性约束） |
| `max_tokens` | 总输出上限 | 需要足够大，同时容纳思考过程+最终回答 |

### budget_tokens 如何设置

思考预算决定了 Claude 可以"花多少 token 思考"：

| 问题类型 | 建议 budget_tokens |
|---------|-------------------|
| 简单推理/判断 | 1024 |
| 中等数学题/代码分析 | 2048 |
| 复杂多步推理/难题 | 4096 或更高 |

注意：思考 token 也计入输出 token 费用。简单问题不要设置过大的预算。

### 解析响应：thinking 内容块

启用 thinking 后，响应的 `content` 数组中会多出一种内容块类型：

```python
for block in message.content:
    if block.type == "thinking":
        thinking_text = block.thinking  # Claude 的思考过程
        print("思考：", thinking_text)
    elif block.type == "text":
        answer_text = block.text       # 最终回答
        print("回答：", answer_text)
```

思考过程和最终回答是分开的内容块。你可以：
- **调试时**：打印思考过程，理解 Claude 如何推理
- **生产环境**：只展示最终回答给用户，思考过程用于内部审计/日志
- **教学场景**：同时展示思考和回答，帮助用户学习推理方法

### 流式模式下处理 thinking

流式模式下，你会按顺序收到：
1. `content_block_start`（type="thinking"）→ 思考开始
2. 多个 `content_block_delta`（type="thinking_delta"）→ 思考过程流式输出
3. `content_block_stop` → 思考结束
4. `content_block_start`（type="text"）→ 回答开始
5. 多个 `content_block_delta`（type="text_delta"）→ 回答流式输出

这让你可以实现"实时显示思考中..."的效果。

### 采样参数详解

不使用 thinking 时，你可以调整以下采样参数控制输出风格：

| 参数 | 范围 | 作用 | 推荐值 |
|------|------|------|--------|
| `temperature` | 0.0 ~ 1.0+ | 控制随机性。0=确定性/重复，1=最大创造性 | 0.7（默认） |
| `top_p` | 0.0 ~ 1.0 | 核采样。只从累积概率达到 p 的最小词集中选择 | 1.0（关闭） |
| `top_k` | 整数 | 只从概率最高的 k 个词中选择 | 模型默认 |

**参数选择指南**：

| 场景 | temperature | 说明 |
|------|-------------|------|
| 事实问答/代码生成 | 0.0 ~ 0.3 | 需要精确、确定性输出 |
| 通用对话/写作 | 0.5 ~ 0.8 | 平衡准确性和创造性 |
| 创意写作/头脑风暴 | 0.9 ~ 1.0 | 需要多样性和新颖想法 |

### temperature=1 的硬性约束

启用 Extended Thinking 时，`temperature` 必须设置为 `1.0`，这是一个硬性约束。原因是：
- Extended Thinking 机制内部已经通过思考过程实现了高质量推理
- 强制 temperature=1 保证思考过程的充分探索
- 如果需要更确定的输出，可以在思考完成后通过其他方式控制，但 API 层面必须设为 1

### 提示缓存（cache_control）框架

提示缓存是一项优化功能，核心思想是：对于重复出现在多个请求中的大型内容（长系统提示词、RAG 文档、代码库上下文等），标记为可缓存，服务端缓存处理结果，后续请求复用：

```python
system_prompt = [
    {
        "type": "text",
        "text": "你是一个...（很长的系统提示词）",
        "cache_control": {"type": "ephemeral"}  # 标记可缓存
    }
]
```

缓存的好处：
- **降低延迟**：缓存内容不需要每次重新处理，首 token 时间更快
- **降低成本**：缓存命中的 token 计费可能有优惠（参考官方定价）
- **支持更长上下文**：通过缓存大型固定内容，留出更多 token 给实际对话

适合缓存的内容：
- 长系统提示词（如角色设定、代码规范文档）
- RAG 检索到的大型文档上下文
- Few-shot 示例（如果很长）
- 多轮对话中不变化的前期上下文

> 提示：具体的缓存 TTL、计费规则、支持的内容类型请参考 Anthropic 最新官方文档——该功能可能在持续演进中。

### Extended Thinking 与工具调用

Extended Thinking 与工具调用可以完美结合：

1. Claude 先在 thinking block 中分析："用户问股价差，我需要查 AAPL 和 GOOGL 两个价格"
2. 然后输出 tool_use blocks，并行调用两个工具
3. 工具结果返回后，Claude 再次思考："AAPL 是 $150，GOOGL 是 $140..."
4. 最终输出 text block 回答用户问题并给出建议

这种"先思考再调用工具"的模式能显著减少工具调用错误（如参数错误、不必要的调用），提升复杂 agent 场景的可靠性。

## Extended Thinking 使用约束与注意事项

1. **模型要求**：需要支持 Extended Thinking 的模型版本（如 Claude 3.7 Sonnet、Claude Opus 4 及更新版本）

2. **temperature 约束**：必须设为 1.0

3. **max_tokens 要足够大**：需要同时容纳思考过程+最终回答。思考过程本身可能占用数百到数千 token

4. **token 计费**：思考过程的 token 也计入输出 token 费用，简单问题不要开

5. **不是所有场景都需要**：对于简单问答、闲聊等场景，Extended Thinking 反而会增加延迟和成本，不需要开启

6. **何时应该开启**：
   - ✅ 数学题、逻辑推理题
   - ✅ 复杂代码调试、多步算法
   - ✅ 需要权衡利弊的决策分析
   - ✅ 需要仔细规划的 agent 任务
   - ❌ 简单问答、闲聊、翻译、摘要

## 常见问题

1. **为什么我用 thinking 时报错 "temperature must be 1"？** 这是硬性约束，启用 thinking 时必须显式设置 `temperature=1.0`。

2. **thinking 内容用户应该看到吗？** 取决于场景：教学/透明场景可以展示；普通聊天应用通常只展示最终回答，思考过程用于开发者调试。

3. **可以强制不显示某些 thinking 内容吗？** thinking 块是结构化返回的，你可以自由选择在 UI 中展示或隐藏。

4. **budget_tokens 设得越大越好吗？** 不是。简单问题设大预算会浪费 token 和时间。从 1024 开始，根据问题复杂度调整。

5. **提示缓存一定能命中吗？** 缓存是尽力而为（best-effort）的，不保证 100% 命中。设计时做好缓存未命中的兜底。

6. **可以同时使用 thinking + tools + streaming 吗？** 可以！所有功能可以组合使用，SDK 完整支持。

## 相关概念

- [Messages API 基础](../concepts/02-messages-basics.md) — 理解消息格式和内容块结构
- [流式对话](02-streaming-chat.md) — 学习流式响应的事件处理（thinking 流式同样基于此机制）
- [工具调用实战](03-tool-use.md) — 工具调用基础，可与 thinking 结合
- [基础对话](01-basic-chat.md) — messages.create 基础参数回顾
- [Anthropic Python SDK 消息 API 与流式处理参考](../references/messages-api.md) — thinking 参数的 API 参考
