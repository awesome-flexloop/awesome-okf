---
type: example
title: "TinyAgent 智能体工具调用"
bundle: /datawhale/happy-llm
description: "第七章 Agent 实践：实现 ReAct 推理循环、工具注册与调用，含 Streamlit Web Demo"
sources: https://github.com/datawhalechina/happy-llm/tree/main/docs/chapter7/Agent
related:
  - /datawhale/happy-llm/concepts/agent-intelligent-agent
  - /datawhale/happy-llm/concepts/grpo-reinforcement-learning
tags: [agent, react, tool-calling, streamlit]
status: stable
---

# TinyAgent 智能体工具调用

## 概述

本示例对应 Happy-LLM 第七章 7.3 节，代码位于 `docs/chapter7/Agent/`。TinyAgent 是一个最小可用的智能体实现，展示了 ReAct 推理-行动循环、工具定义与注册、多轮工具调用的核心机制。

## 环境准备

```bash
pip install -r docs/chapter7/Agent/requirements.txt
```

CPU 即可体验，联网能力按具体工具配置。

## 代码结构

| 文件 | 职责 |
|------|------|
| `src/core.py` | Agent 核心：推理循环、Prompt 组装、响应解析、工具调度 |
| `src/tools.py` | 工具定义：工具名称、描述、参数 schema、执行函数 |
| `src/utils.py` | 工具函数：LLM 调用、输出解析 |
| `src/__init__.py` | 包初始化 |
| `demo.py` | 命令行演示 |
| `web_demo.py` | Streamlit Web 界面 |

## Agent 核心实现

### 工具定义（tools.py）

每个工具包含名称、描述、参数和执行函数：

```python
class Tool:
    def __init__(self, name, description, parameters, function):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

# 示例：搜索工具
search_tool = Tool(
    name="search",
    description="搜索互联网获取信息",
    parameters={"query": "搜索关键词"},
    function=search_function
)
```

工具的描述是 LLM 选择工具的依据，需要清晰说明工具用途和适用场景。

### 推理循环（core.py）

ReAct 范式的核心是 Thought→Action→Observation 循环：

```python
class Agent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {t.name: t for t in tools}

    def run(self, query, max_steps=5):
        messages = [self._build_system_prompt(), {"role": "user", "content": query}]

        for step in range(max_steps):
            response = self.llm.chat(messages)
            action = self._parse_action(response)

            if action.is_final:
                return action.answer

            # 执行工具
            tool = self.tools[action.name]
            observation = tool.function(**action.args)

            # 将观察结果加入对话
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"观察结果：{observation}"})

        return "达到最大步数限制"
```

### System Prompt

System Prompt 是 Agent 行为的"操作系统"，定义输出格式和可用工具：

```
你是一个智能助手，可以使用以下工具：

{tool_descriptions}

请按以下格式回应：
思考：分析当前情况，决定下一步
行动：工具名称(参数)
观察：工具返回结果（由系统提供）
...
最终答案：给出最终回答
```

## 运行方式

### 命令行演示

```bash
python demo.py
```

在命令行中与 Agent 交互，观察其推理过程和工具调用。

### Web 界面

```bash
streamlit run web_demo.py
```

启动 Streamlit Web 界面，可视化 Agent 的思考过程、工具调用和结果。

## 学习要点

1. **ReAct 范式**：Thought（推理）→ Action（行动）→ Observation（观察）的交替循环
2. **工具描述即 API 文档**：LLM 根据工具描述决定何时使用哪个工具，描述质量直接影响效果
3. **输出解析**：需要可靠地从 LLM 输出中解析工具名称和参数，可使用 JSON 格式或正则
4. **多轮上下文管理**：每步的 Thought/Action/Observation 都加入对话历史，LLM 基于完整轨迹决策
5. **停止条件**：达到最大步数或 LLM 判断信息足够给出最终答案

## 从 TinyAgent 到 Agentic RL

TinyAgent 的工具调用能力来自 Prompt Engineering 和 SFT 模型的指令遵循能力。当 Agent 需要在复杂环境（搜索引擎、代码解释器）中通过多轮交互完成任务时，监督数据难以覆盖所有轨迹，这就是第八章 Agentic RL 的动机：

- **Search-R1**：搜索引擎环境，模型通过 RL 学习多轮搜索策略
- **ReTool**：代码解释器环境，模型通过 RL 学习生成和执行代码

通过 GRPO 等强化学习算法，模型在环境中尝试、获得奖励、更新策略，自主学会更优的工具使用方式。

## 延伸阅读

- [Agent 智能体](../concepts/agent-intelligent-agent.md)——完整概念解析
- [GRPO 强化学习](../concepts/grpo-reinforcement-learning.md)——Agentic RL 的训练算法
- [TinyRAG 检索增强生成](rag-tinyrag.md)——RAG 可作为 Agent 的检索工具
