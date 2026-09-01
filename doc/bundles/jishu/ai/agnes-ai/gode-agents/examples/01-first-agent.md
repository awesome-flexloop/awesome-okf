---
type: Example
title: 创建第一个 ToolCallingAgent
description: 从零开始创建一个简单的ToolCallingAgent并运行对话任务
tags: [入门, HelloWorld, ToolCallingAgent]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: models-source
    resource: /references/models-api.md
    title: Models API 参考
---

# 创建第一个 ToolCallingAgent

## 概述

本示例演示如何从零开始创建一个最简单的 `ToolCallingAgent`，并运行基本的问答对话。你将了解智能体的基本构成（模型 + 工具列表）、如何调用 `run()` 执行任务、如何通过 `verbosity_level` 控制日志输出，以及如何通过 `agent.memory.steps` 查看执行过程。

这个示例解决的核心问题：**如何用最少的代码让一个 LLM 驱动的智能体跑起来**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents：`pip install codified-smolagents`
- Hugging Face API Token（设置环境变量 `HF_TOKEN`，或在代码中直接传入）
- 网络连接（用于调用 Hugging Face Inference API）

```bash
pip install codified-smolagents huggingface-hub
```

## 完整代码

```python
"""
示例 01: 创建第一个 ToolCallingAgent
演示：创建模型 → 创建无工具 Agent → 运行问答 → 查看 memory.steps → 控制日志级别
"""

from codified_smolagents import ToolCallingAgent, HfApiModel
from codified_smolagents.monitoring import LogLevel

# ============================================================
# 第一步：创建模型实例
# ============================================================
# HfApiModel 默认使用 Qwen/Qwen2.5-Coder-32B-Instruct 模型
# token 参数会自动从环境变量 HF_TOKEN 读取，也可以显式传入
model = HfApiModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    # token="hf_xxxxxxxxxx",  # 如果未设置环境变量，在此处传入
)

# ============================================================
# 第二步：创建 ToolCallingAgent（无工具版本）
# ============================================================
# 不传入任何工具时，Agent 只能依靠模型自身知识回答问题
# FinalAnswerTool 会被自动添加，用于输出最终答案
agent = ToolCallingAgent(
    tools=[],           # 空工具列表：Agent 只能对话，不能调用外部工具
    model=model,        # 语言模型实例
    max_steps=5,        # 最大执行步数（简单问答不需要太多步）
    verbosity_level=LogLevel.INFO,  # 日志级别：OFF / ERROR / INFO / DEBUG
)

# ============================================================
# 第三步：运行任务
# ============================================================
# agent.run() 接受任务字符串，返回最终答案（str 类型）
result = agent.run("请用一句话解释什么是 ReAct 框架。")

print("=" * 60)
print("🤖 Agent 的回答：")
print(result)
print("=" * 60)

# ============================================================
# 第四步：查看执行步骤 (memory.steps)
# ============================================================
print("\n📋 执行步骤详情：")
for i, step in enumerate(agent.memory.steps):
    print(f"\n--- Step {i + 1} ---")
    print(f"  步骤类型: {type(step).__name__}")
    if hasattr(step, 'model_output') and step.model_output:
        # 截取模型输出的前200个字符
        preview = step.model_output[:200] + "..." if len(step.model_output) > 200 else step.model_output
        print(f"  模型输出: {preview}")
    if hasattr(step, 'final_answer') and step.final_answer:
        print(f"  最终答案: {step.final_answer}")

# ============================================================
# 第五步：对比不同 verbosity_level
# ============================================================
print("\n" + "=" * 60)
print("🔇 测试 LogLevel.OFF（静默模式）：")
agent_quiet = ToolCallingAgent(
    tools=[],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.OFF,  # 不输出任何日志
)
result_quiet = agent_quiet.run("1+1等于几？")
print(f"静默模式回答: {result_quiet}")

print("\n🔊 测试 LogLevel.DEBUG（调试模式）：")
agent_debug = ToolCallingAgent(
    tools=[],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.DEBUG,  # 输出最详细的调试信息
)
result_debug = agent_debug.run("Python 中 list 和 tuple 的区别是什么？")
print(f"调试模式回答: {result_debug}")
```

## 运行说明

1. 确保已设置 `HF_TOKEN` 环境变量，或在代码中填入你的 Hugging Face API Token。
2. 将代码保存为 `01_first_agent.py`。
3. 运行：`python 01_first_agent.py`

**预期输出示例**：
```
============================================================
🤖 Agent 的回答：
ReAct 框架是一种将推理（Reasoning）和行动（Acting）交织进行的大语言模型提示框架...
============================================================

📋 执行步骤详情：

--- Step 1 ---
  步骤类型: ActionStep
  模型输出: Thought: 用户想了解 ReAct 框架...
  最终答案: ReAct 框架是一种将推理（Reasoning）和行动（Acting）交织进行...

🔇 测试 LogLevel.OFF（静默模式）：
静默模式回答: 1+1等于2。

🔊 测试 LogLevel.DEBUG（调试模式）：
[DEBUG] ...详细的调试日志...
调试模式回答: Python 中 list 是可变的...
```

## 代码解析

### 1. 创建模型 `HfApiModel`

```python
model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
```

- `HfApiModel` 通过 Hugging Face Inference API 调用远程模型，无需本地 GPU。
- `model_id` 指定要使用的模型，默认为 `"Qwen/Qwen2.5-Coder-32B-Instruct"`。
- `token` 参数用于认证，默认从环境变量 `HF_TOKEN` 读取。

### 2. 创建 Agent `ToolCallingAgent`

```python
agent = ToolCallingAgent(
    tools=[],
    model=model,
    max_steps=5,
    verbosity_level=LogLevel.INFO,
)
```

- `tools`：工具列表。传入空列表时，Agent 只能进行对话（自动包含 `FinalAnswerTool`）。
- `model`：语言模型实例，所有 Agent 都需要一个模型来驱动推理。
- `max_steps`：最大 ReAct 循环步数，防止无限循环。简单问答通常 1-3 步即可完成。
- `verbosity_level`：日志级别，使用 `LogLevel` 枚举：
  - `LogLevel.OFF`：静默，不输出任何日志
  - `LogLevel.ERROR`：只输出错误
  - `LogLevel.INFO`：输出关键步骤信息（默认）
  - `LogLevel.DEBUG`：输出完整调试信息

### 3. 运行任务 `agent.run()`

```python
result = agent.run("请用一句话解释什么是 ReAct 框架。")
```

- `run(task)` 是启动智能体的主入口，接收任务描述字符串。
- 内部执行 ReAct 循环：思考（Thought）→ 行动（Action）→ 观察（Observation），直到得出最终答案。
- 返回值为最终答案字符串（通过 deque 取最后一步的 `final_answer`）。

### 4. 查看步骤 `agent.memory.steps`

```python
for step in agent.memory.steps:
```

- `agent.memory` 是 `AgentMemory` 实例，存储了整个对话过程的所有步骤。
- `steps` 是步骤列表，每个步骤包含 `model_output`（模型原始输出）、`final_answer`（最终答案，如果该步为最终步）等属性。
- 这对于调试和理解 Agent 的行为非常有用。

## 扩展练习

1. **添加自定义任务**：尝试让 Agent 回答更复杂的问题，如"解释量子计算的基本原理"，观察需要多少步才能完成。

2. **流式运行**：将 `stream=True` 传入 `run()` 方法，体验逐步输出的效果：
   ```python
   for step_output in agent.run("写一首关于AI的短诗", stream=True):
       print(step_output)
   ```

3. **调整 max_steps**：将 `max_steps` 设为 1，观察 Agent 在严格限制下的行为。

4. **使用 reset 参数**：在连续对话中使用 `run(task, reset=True)` 清除之前的记忆，开始全新对话。

5. **覆盖 max_steps**：在 `run()` 中传入 `max_steps` 参数覆盖构造函数的设置：
   ```python
   result = agent.run("复杂问题...", max_steps=10)
   ```

## 相关链接

- [MultiStepAgent 与 ReAct 循环](../concepts/03-multi-step-agent.md) — 深入理解多步智能体的执行循环
- [ToolCallingAgent 机制](../concepts/05-tool-calling-agent.md) — 了解 JSON 工具调用的工作原理
- [内存系统](../concepts/04-memory-system.md) — AgentMemory 和 MemoryStep 的详细设计
- [模型层概述](../concepts/09-model-layer.md) — 了解各种模型后端
- [Agents API 参考](../references/agents-api.md) — ToolCallingAgent 和 MultiStepAgent 的完整参数说明
- [Models API 参考](../references/models-api.md) — HfApiModel 的完整 API 文档
