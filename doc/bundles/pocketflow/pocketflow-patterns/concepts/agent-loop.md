---
title: Agent 循环模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-agent
related:
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
---

# Agent 循环模式（ReAct Loop）

Agent 循环是 PocketFlow 最经典的模式，实现了类似 ReAct（Reasoning + Acting）的自主决策循环：节点思考决定行动→执行行动→观察结果→回到思考，直到得出最终答案。

## 流程图

```
┌─────────────┐
│  DecideAction│ ←──────────────┐
│  (LLM决策)   │                │
└──────┬───────┘                │
       │                        │
    ┌──┴──┐                     │
    │action│                     │
    └──┬──┘                     │
  ┌────┴────┐                   │
  │         │                   │
"search"  "answer"              │
  │         │                   │
  ▼         ▼                   │
┌──────┐ ┌────────┐             │
│Search│ │ Answer │             │
│ Web  │ │(终止)  │             │
└──┬───┘ └────────┘             │
   │ "decide"                   │
   └────────────────────────────┘
```

## 核心节点

### DecideAction（决策节点）

LLM 根据当前上下文决定下一步行动：
- 返回 `"search"` → 需要搜索更多信息
- 返回 `"answer"` → 已有足够信息，生成答案

### SearchWeb（工具节点）

执行搜索，将结果写入 shared，然后返回 `"decide"` 回到决策节点。

### AnswerQuestion（终止节点）

生成最终答案，流程结束。

## 流程连接代码

```python
from pocketflow import Flow
from nodes import DecideAction, SearchWeb, AnswerQuestion

decide = DecideAction()
search = SearchWeb()
answer = AnswerQuestion()

decide - "search" >> search
decide - "answer" >> answer
search - "decide" >> decide  # 关键：搜索后回到决策节点

flow = Flow(start=decide)
```

## Shared 数据契约

```python
shared = {
    "question": "用户的问题",
    "search_results": [],     # SearchWeb追加的搜索结果
    "answer": None            # AnswerQuestion写入最终答案
}
```

## 变体：Supervisor 模式

在 Agent 循环外加一个监督节点，检查答案质量：

```python
agent_flow >> supervisor                    # Agent跑完后检查
supervisor - "retry" >> agent_flow          # 不合格则重新运行
supervisor - "pass" >> final_node           # 合格则结束
```

详见 [pocketflow-supervisor](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow/cookbook/pocketflow-supervisor/flow.py)。

## 适用场景

- 需要自主决策是否调用工具的聊天机器人
- 研究助手（搜索→阅读→再搜索→总结）
- 任何需要"思考-行动-观察"循环的场景

## Cookbook 对应示例

- `pocketflow-agent` — 基础研究Agent
- `pocketflow-deep-research` — 深度研究Agent（多轮搜索+摘要）
- `pocketflow-supervisor` — 带质量监督的Agent
- `pocketflow-browser-agent` — 浏览器Agent（视觉+DOM操作）
