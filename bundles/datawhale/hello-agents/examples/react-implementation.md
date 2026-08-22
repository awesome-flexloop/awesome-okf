---
title: ReAct范式从零实现
type: example
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/agent-paradigms-react
  - /datawhale/hello-agents/references/chapter04-classic-paradigms
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/第四章%20智能体经典范式构建.md
---

# ReAct范式从零实现

本示例展示ReAct（Reasoning + Acting）范式的核心实现，包括LLM客户端封装和Thought→Action→Observation循环。

## 环境准备

```bash
pip install openai python-dotenv
```

`.env`配置：
```bash
LLM_API_KEY="YOUR-API-KEY"
LLM_MODEL_ID="YOUR-MODEL"
LLM_BASE_URL="YOUR-URL"
```

## LLM客户端封装

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class HelloAgentsLLM:
    def __init__(self, model=None, apiKey=None, baseUrl=None, timeout=None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        collected_content = []
        for chunk in response:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            collected_content.append(content)
        print()
        return "".join(collected_content)
```

## ReAct核心循环

ReAct的关键是通过提示工程引导模型输出固定轨迹：

```
Thought: 分析当前情况，制定下一步
Action: 工具名[参数]
Observation: 工具返回结果
...（循环）
Thought: 我已经找到最终答案
Final Answer: 最终回答
```

### 提示词设计要点
1. 明确告知模型可用的工具及其参数格式
2. 要求模型严格遵循Thought/Action/Observation格式
3. 在Action后暂停执行，调用工具获取Observation
4. 将Observation追加到消息历史，继续循环

### 循环结构

```python
class ReActAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.messages = []

    def run(self, query: str, max_steps: int = 10) -> str:
        self.messages.append({"role": "user", "content": query})

        for step in range(max_steps):
            response = self.llm.think(self.messages)
            self.messages.append({"role": "assistant", "content": response})

            if "Final Answer:" in response:
                return response.split("Final Answer:")[-1].strip()

            action = self._parse_action(response)
            if action and action["tool"] in self.tools:
                observation = self.tools[action["tool"]].run(action["args"])
                self.messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })
            else:
                self.messages.append({
                    "role": "user",
                    "content": "Observation: 工具不存在，请检查Action格式"
                })

        return "达到最大步数限制"
```

## 工程挑战

从零实现ReAct会暴露框架帮你处理的问题：
- 模型输出格式解析的鲁棒性（非标准格式处理）
- 工具调用失败的重试与错误恢复
- 防止Agent陷入死循环（最大步数限制）
- 上下文长度管理（长对话的历史截断）

这些正是第七章构建HelloAgents框架时需要系统化解决的问题。

## 配套代码

完整代码位于教程第四章，包括：
- ReAct范式完整实现
- Plan-and-Solve范式实现
- Reflection范式实现
- 搜索工具和计算工具定义
