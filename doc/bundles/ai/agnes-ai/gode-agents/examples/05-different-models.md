---
type: Example
title: 使用不同模型后端
description: 配置和切换HfApiModel/LiteLLMModel/OpenAIServerModel/TransformersModel等后端
tags: [模型, 后端, 配置]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: models-source
    resource: /references/models-api.md
    title: Models API 参考
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
---

# 使用不同模型后端

## 概述

本示例演示如何配置和切换 codified-smolagents 支持的多种模型后端，包括 Hugging Face Inference API（HfApiModel）、OpenAI 兼容 API（OpenAIServerModel）、LiteLLM 统一接口（LiteLLMModel）以及本地 GPU 推理（TransformersModel）。所有模型类都继承自统一的 `Model` 基类，切换后端只需更换模型实例，Agent 代码无需任何修改。

这个示例解决的核心问题：**如何根据需求（成本、速度、隐私、模型能力）选择和配置最合适的 LLM 后端**。

## 前置条件

根据使用的模型后端，安装对应的依赖：

```bash
# 基础安装（包含 HfApiModel 支持）
pip install codified-smolagents huggingface-hub

# OpenAI 兼容 API 支持
pip install openai

# LiteLLM 支持（数百个提供商）
pip install 'codified-smolagents[litellm]'

# 本地 Transformers 模型支持（需要 GPU）
pip install 'codified-smolagents[transformers]' torch
```

需要准备的 API Key（按需）：
- `HF_TOKEN`：Hugging Face API Token
- `OPENAI_API_KEY`：OpenAI API Key（或其他兼容服务的 Key）
- 其他提供商的 API Key（Anthropic、Groq 等，通过 LiteLLM 使用）

## 完整代码

```python
"""
示例 05: 使用不同模型后端
演示：HfApiModel → OpenAIServerModel → LiteLLMModel → TransformersModel → 模型切换 → token计数
"""

import os
from codified_smolagents import ToolCallingAgent, CodeAgent
from codified_smolagents.models import (
    HfApiModel,
    OpenAIServerModel,
    LiteLLMModel,
    TransformersModel,
)
from codified_smolagents.monitoring import LogLevel


# 通用测试任务
TEST_TASK = "用三句话解释什么是大语言模型。"


def run_with_model(model, model_name: str, task: str = TEST_TASK):
    """使用指定模型创建并运行 Agent 的辅助函数。"""
    print(f"\n{'='*60}")
    print(f"🧠 使用模型: {model_name}")
    print(f"{'='*60}")
    agent = ToolCallingAgent(
        tools=[],
        model=model,
        max_steps=2,
        verbosity_level=LogLevel.OFF,
    )
    result = agent.run(task)
    print(f"回答: {result[:200]}")
    # 获取 token 计数
    token_counts = model.get_token_counts()
    print(f"Token 使用: 输入={token_counts.get('input_token_count', 'N/A')}, "
          f"输出={token_counts.get('output_token_count', 'N/A')}")
    return result


# ============================================================
# 1. HfApiModel（Hugging Face Inference API）
# ============================================================
print("1️⃣ HfApiModel - Hugging Face 托管推理 API")
print("-" * 60)
print("特点：无需本地GPU，免费额度可用，支持数千个开源模型")

model_hf = HfApiModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",  # 模型ID或推理端点URL
    token=os.getenv("HF_TOKEN"),                  # API Token
    timeout=120,                                   # 请求超时秒数
    # provider="hf-inference",                    # 可选：指定推理提供商
)
run_with_model(model_hf, "HfApiModel (Qwen2.5-Coder-32B-Instruct)")


# ============================================================
# 2. OpenAIServerModel（OpenAI 兼容 API）
# ============================================================
print("\n\n2️⃣ OpenAIServerModel - OpenAI 及兼容 API")
print("-" * 60)
print("特点：支持 OpenAI 官方 API，以及任何兼容 OpenAI 格式的服务")
print("  （如 vLLM、Ollama、Azure OpenAI、DeepSeek、Moonshot 等）")

# 2a. OpenAI 官方 API
if os.getenv("OPENAI_API_KEY"):
    model_openai = OpenAIServerModel(
        model_id="gpt-4o",                           # 模型名称
        api_base="https://api.openai.com/v1",        # API 基础 URL
        api_key=os.getenv("OPENAI_API_KEY"),         # API Key
        # organization="org-xxx",                    # 可选：组织ID
        # project="proj-xxx",                        # 可选：项目ID
    )
    run_with_model(model_openai, "OpenAIServerModel (GPT-4o)")
else:
    print("  ⚠️ 未设置 OPENAI_API_KEY，跳过 OpenAI 官方 API 测试")

# 2b. 使用本地 vLLM 或 Ollama（兼容 OpenAI 格式）
# 例如本地启动了 Ollama 服务：ollama run qwen2.5
model_local_ollama = OpenAIServerModel(
    model_id="qwen2.5:7b",
    api_base="http://localhost:11434/v1",  # Ollama 默认地址
    api_key="ollama",                       # Ollama 不需要真实 key，但不能为 None
)
# 如果本地没有运行 Ollama，这行会失败，所以用 try-except 包裹
try:
    run_with_model(model_local_ollama, "OpenAIServerModel (本地 Ollama/qwen2.5)")
except Exception as e:
    print(f"  ⚠️ 本地 Ollama 连接失败（请确认已启动 ollama serve）: {type(e).__name__}")

# 2c. 其他兼容服务示例（DeepSeek、Moonshot、通义千问等）
# model_deepseek = OpenAIServerModel(
#     model_id="deepseek-chat",
#     api_base="https://api.deepseek.com/v1",
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
# )


# ============================================================
# 3. LiteLLMModel（统一多提供商接口）
# ============================================================
print("\n\n3️⃣ LiteLLMModel - 通过 LiteLLM 访问数百个 LLM 提供商")
print("-" * 60)
print("特点：统一接口访问 OpenAI、Anthropic、Azure、Bedrock、Groq、Ollama 等")
print("  模型ID格式：'provider/model_name'，如 'anthropic/claude-3-5-sonnet'")

# 3a. Anthropic Claude（通过 LiteLLM）
if os.getenv("ANTHROPIC_API_KEY"):
    model_claude = LiteLLMModel(
        model_id="anthropic/claude-3-5-sonnet-20240620",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        # api_base=None,  # 可选：自定义 API 端点
    )
    run_with_model(model_claude, "LiteLLMModel (Claude 3.5 Sonnet)")
else:
    print("  ⚠️ 未设置 ANTHROPIC_API_KEY，跳过 Claude 测试")

# 3b. Groq（快速推理）
if os.getenv("GROQ_API_KEY"):
    model_groq = LiteLLMModel(
        model_id="groq/llama-3.1-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    run_with_model(model_groq, "LiteLLMModel (Groq/Llama-3.1-70B)")
else:
    print("  ⚠️ 未设置 GROQ_API_KEY，跳过 Groq 测试")

# 3c. 通过 LiteLLM 使用 Ollama
try:
    model_litellm_ollama = LiteLLMModel(
        model_id="ollama/qwen2.5:7b",
        api_base="http://localhost:11434",
    )
    run_with_model(model_litellm_ollama, "LiteLLMModel (Ollama/qwen2.5)")
except Exception as e:
    print(f"  ⚠️ LiteLLM+Ollama 连接失败: {type(e).__name__}")


# ============================================================
# 4. TransformersModel（本地 GPU 推理）
# ============================================================
print("\n\n4️⃣ TransformersModel - 本地 Transformers 模型推理")
print("-" * 60)
print("特点：完全本地运行，数据不离开机器，需要 GPU（推荐 8GB+ 显存）")

# 使用小模型进行本地测试
try:
    model_local = TransformersModel(
        model_id="HuggingFaceTB/SmolLM2-1.7B-Instruct",  # 小模型，适合演示
        device_map="auto",                                # 自动选择设备 (CUDA/CPU)
        # torch_dtype="auto",                             # 自动选择精度
        # trust_remote_code=False,                        # 是否信任远程代码
        max_new_tokens=500,                               # 最大生成 token 数
    )
    run_with_model(
        model_local,
        "TransformersModel (SmolLM2-1.7B-Instruct 本地)",
        task="用一句话解释什么是AI。",
    )
except ImportError:
    print("  ⚠️ 未安装 transformers 和 torch，跳过本地模型测试")
    print("  安装命令: pip install 'codified-smolagents[transformers]' torch")
except Exception as e:
    print(f"  ⚠️ 本地模型加载失败（可能是显存不足）: {type(e).__name__}: {e}")


# ============================================================
# 5. 模型切换对 Agent 的影响演示
# ============================================================
print("\n\n5️⃣ 模型切换：同一 Agent 代码使用不同模型")
print("-" * 60)
print("💡 Agent 代码完全不变，只需更换 model 参数即可切换后端！")

def create_agent_with_model(model):
    """创建一个带有计算器工具的 Agent。"""
    from codified_smolagents import tool

    @tool
    def calculator(expression: str) -> float:
        """
        计算数学表达式的值。
        Args:
            expression: 数学表达式，如 "2+3*4"
        """
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
        return float(eval(expression, {"__builtins__": {}}, allowed))

    return CodeAgent(
        tools=[calculator],
        model=model,
        additional_authorized_imports=["math"],
        max_steps=3,
        verbosity_level=LogLevel.OFF,
    )

# 同一个 Agent 定义，用 HfApiModel 运行
agent_hf = create_agent_with_model(HfApiModel(token=os.getenv("HF_TOKEN")))
print("\n使用 HfApiModel 计算:")
r1 = agent_hf.run("计算 (123 + 456) * 789 的值")
print(f"  结果: {r1[:150]}")

# 如果配置了 OpenAI，也可以快速切换
# agent_gpt = create_agent_with_model(OpenAIServerModel(model_id="gpt-4o", ...))
# r2 = agent_gpt.run("计算 (123 + 456) * 789 的值")


# ============================================================
# 6. Token 计数获取
# ============================================================
print("\n\n6️⃣ Token 计数统计")
print("-" * 60)

model_for_tokens = HfApiModel(token=os.getenv("HF_TOKEN"))
agent_tokens = ToolCallingAgent(
    tools=[],
    model=model_for_tokens,
    max_steps=2,
    verbosity_level=LogLevel.OFF,
)
_ = agent_tokens.run("1+1等于几？")

# 通过 model.get_token_counts() 获取最近一次调用的 token 用量
counts = model_for_tokens.get_token_counts()
print(f"最近一次模型调用:")
print(f"  输入 token 数: {counts.get('input_token_count', 'N/A')}")
print(f"  输出 token 数: {counts.get('output_token_count', 'N/A')}")
total = (counts.get('input_token_count', 0) or 0) + (counts.get('output_token_count', 0) or 0)
print(f"  总计: {total} tokens")

# 注意：last_input_token_count 和 last_output_token_count 只记录最后一次调用
# 完整对话的 token 消耗需要累积每次调用的计数
print("\n💡 提示：model.get_token_counts() 返回的是最近一次调用的计数")
print("  要获取整个对话的总消耗，需要在每步后累积计数")
print("  可以使用 step_callbacks 来自动记录每步的 token 用量")
```

## 运行说明

1. 根据需要安装对应的依赖包。
2. 设置必要的环境变量（如 `HF_TOKEN`、`OPENAI_API_KEY` 等）。
3. 将代码保存为 `05_different_models.py`。
4. 运行：`python 05_different_models.py`

**预期输出（部分）**：
```
1️⃣ HfApiModel - Hugging Face 托管推理 API
------------------------------------------------------------
特点：无需本地GPU，免费额度可用，支持数千个开源模型

============================================================
🧠 使用模型: HfApiModel (Qwen2.5-Coder-32B-Instruct)
============================================================
回答: 大语言模型（LLM）是基于深度学习的自然语言处理模型...
Token 使用: 输入=120, 输出=85

2️⃣ OpenAIServerModel - OpenAI 及兼容 API
------------------------------------------------------------
特点：支持 OpenAI 官方 API，以及任何兼容 OpenAI 格式的服务...
```

> ⚠️ 未配置的 API 会跳过对应部分并显示提示信息，不会影响其他部分运行。

## 代码解析

### 1. 模型后端对比

| 模型类 | 需要安装 | 需要API Key | 运行位置 | 适用场景 |
|--------|---------|------------|---------|---------|
| `HfApiModel` | `huggingface_hub` | HF Token（免费） | HF 云端 | 快速上手、开源模型 |
| `OpenAIServerModel` | `openai` | 对应服务 Key | API 服务端 | OpenAI GPT、vLLM/Ollama 本地 |
| `LiteLLMModel` | `litellm` | 对应提供商 Key | API 服务端 | 多提供商切换、统一接口 |
| `TransformersModel` | `transformers`, `torch` | 无 | 本地 GPU/CPU | 隐私敏感、离线环境 |
| `VLLMModel` | `vllm` | 无 | 本地 GPU | 高吞吐本地推理 |
| `MLXModel` | `mlx-lm` | 无 | Apple Silicon | Mac 本地推理 |

### 2. HfApiModel 配置要点

```python
model = HfApiModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=None,           # 默认从 HF_TOKEN 环境变量读取
    timeout=120,          # 请求超时
    provider=None,        # 可选: "replicate"/"together"/"fal-ai"/"sambanova"/"hf-inference"
)
```

- `model_id` 可以是 Hugging Face 上的模型 ID，也可以是自定义 Inference Endpoint URL。
- `provider` 参数用于选择 HF Inference API 的后端推理提供商。

### 3. OpenAIServerModel 配置要点

```python
model = OpenAIServerModel(
    model_id="gpt-4o",
    api_base="https://api.openai.com/v1",  # 任何兼容 OpenAI 格式的端点
    api_key="sk-xxx",
)
```

- 关键在于 `api_base` 参数，更换为不同的 URL 即可对接各种兼容服务：
  - vLLM 本地：`http://localhost:8000/v1`
  - Ollama：`http://localhost:11434/v1`
  - DeepSeek：`https://api.deepseek.com/v1`
  - 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`

### 4. LiteLLMModel 配置要点

```python
model = LiteLLMModel(
    model_id="anthropic/claude-3-5-sonnet-20240620",  # provider/model 格式
    api_key=None,        # 自动从对应环境变量读取
    api_base=None,       # 自定义端点
)
```

- LiteLLM 支持 100+ LLM 提供商，`model_id` 格式为 `provider/model_name`。
- 以 `ollama/`、`groq/`、`cerebras/` 开头的模型会自动设置 `flatten_messages_as_text=True`。
- 需要安装：`pip install 'codified-smolagents[litellm]'`

### 5. TransformersModel 配置要点

```python
model = TransformersModel(
    model_id="HuggingFaceTB/SmolLM2-1.7B-Instruct",
    device_map="auto",       # 自动检测 CUDA/CPU
    torch_dtype=None,        # 数据类型，如 torch.bfloat16
    trust_remote_code=False,
    max_new_tokens=5000,
)
```

- 支持自回归语言模型和视觉语言模型（VLM）。
- `device_map="auto"` 会自动使用 GPU（如可用），否则使用 CPU（会很慢）。
- 对于视觉语言模型加载失败时自动回退到纯文本模型。

### 6. 统一接口与 token 计数

所有模型类都继承自 `Model` 基类，提供统一接口：
- `model(messages, stop_sequences, tools_to_call_from)` → `ChatMessage`
- `model.get_token_counts()` → `{"input_token_count": int, "output_token_count": int}`
- `model.to_dict()` / `Model.from_dict()` → 序列化/反序列化

`ChatMessage` 数据结构：
- `role`: 消息角色（user/assistant/system/tool-call/tool-response）
- `content`: 文本内容
- `tool_calls`: 工具调用列表（`ChatMessageToolCall` 对象）
- `raw`: 原始 API 响应（不参与序列化）

## 扩展练习

1. **多模型对比**：创建同一任务，分别用 2-3 个不同模型运行，对比回答质量和速度。

2. **模型路由**：实现一个简单的模型路由器，根据任务复杂度自动选择模型：
   ```python
   def route_model(task: str) -> Model:
       if len(task) > 500 or any(kw in task for kw in ["分析", "研究", "复杂"]):
           return LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
       else:
           return HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
   ```

3. **使用 Azure OpenAI**：尝试 `AzureOpenAIServerModel`，配置 `azure_endpoint` 和 `api_version`。

4. **使用 Amazon Bedrock**：如果有 AWS 账号，尝试 `AmazonBedrockServerModel` 调用 Nova 或 Claude 模型。

5. **Token 计数回调**：使用 `step_callbacks` 累积整个对话的 token 消耗：
   ```python
   total_tokens = {"input": 0, "output": 0}
   def count_tokens(step_result):
       counts = model.get_token_counts()
       total_tokens["input"] += counts.get("input_token_count", 0) or 0
       total_tokens["output"] += counts.get("output_token_count", 0) or 0
   agent = ToolCallingAgent(tools=[], model=model, step_callbacks=[count_tokens])
   ```

6. **序列化模型配置**：使用 `model.to_dict()` 保存配置，`Model.from_dict()` 恢复：
   ```python
   config = model.to_dict()
   import json
   print(json.dumps(config, indent=2))  # 注意：api_key/token 不会被导出
   ```

## 相关链接

- [模型层概述](/concepts/09-model-layer.md) — Model 基类设计和多后端架构
- [工具调用智能体](/concepts/05-tool-calling-agent.md) — 模型 function calling 与工具调用
- [代码执行智能体](/concepts/06-code-agent.md) — 模型代码生成与 CodeAgent
- [Models API 参考](/references/models-api.md) — 所有模型类的完整参数和方法
- [Agents API 参考](/references/agents-api.md) — Agent 构造中 model 参数的使用
