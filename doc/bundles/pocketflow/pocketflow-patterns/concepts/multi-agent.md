---
title: 多智能体协作模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-multi-agent
related:
  - /pocketflow/pocketflow-core/concepts/async-parallel
  - /pocketflow/pocketflow-patterns/concepts/agent-loop
---

# 多智能体协作模式

多智能体模式让多个 Agent 各自运行独立的 Flow，通过 asyncio.Queue 等机制进行消息通信，实现角色分工、对抗/协作、层级监督等复杂交互。

## 三种协作拓扑

### 1. 双向通信（Taboo Game）

两个Agent通过双队列交替发送消息：

```
┌─────────┐  hint   ┌─────────┐
│ Hinter  │────────→│ Guesser │
│         │←────────│         │
└─────────┘  guess  └─────────┘
     │                    │
     └─── asyncio.gather ─┘
         (并发运行两个Flow)
```

```python
hinter_flow = AsyncFlow(start=hinter)
guesser_flow = AsyncFlow(start=guesser)

# 自环持续运行
hinter - "continue" >> hinter
guesser - "continue" >> guesser

# 并发运行
await asyncio.gather(
    hinter_flow.run_async(shared),
    guesser_flow.run_async(shared)
)
```

关键：每个Agent是一个带自环的独立Flow，通过`asyncio.Queue`在shared中传递消息。

### 2. Supervisor 层级监督

一个监督Agent管理多个工作Agent：

```
┌────────────┐
│ Supervisor │──→ Worker A
│ (审核/分配) │──→ Worker B
└─────┬──────┘──→ Worker C
      │ "retry"
      └────────→ (重新执行)
```

通过Flow嵌套实现：内层Flow是Worker循环，外层是Supervisor检查。

### 3. Debate 对抗辩论

两个Agent轮流发言，评判节点决定胜负：

```
┌──────┐   ┌──────┐
│Pro   │←→│Con   │
└──┬───┘   └──┬───┘
   └──→Judge←─┘
         │
       胜负
```

## Shared 通信模式

多Agent通过shared中的Queue或数据结构通信：

```python
shared = {
    "hinter_queue": asyncio.Queue(),
    "guesser_queue": asyncio.Queue(),
    "message_history": [],
    "state": "playing"
}
```

在prep_async中await队列消息，在post_async中put回复。

## Cookbook 对应示例

- `pocketflow-multi-agent` — Taboo游戏双Agent通信
- `pocketflow-supervisor` — Supervisor监督Worker
- `pocketflow-debate` — 多轮辩论
- `pocketflow-communication` — Agent间消息传递
- `pocketflow-a2a` — Agent-to-Agent协议
