---
title: 工作流与人机交互模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-cli-hitl
related:
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
---

# 工作流与人机交互模式

Workflow/HITL（Human-in-the-Loop）模式将人工决策嵌入自动化流程，适用于表单填写、审批、需要人工确认或输入的场景。

## 核心思想

在自动化Flow中插入"等待人工输入"的节点，该节点阻塞直到收到外部输入，然后继续流程。

```
┌────────┐    ┌──────────┐    ┌────────┐    ┌────────┐
│ 自动化  │───→│ 等待人工  │───→│ 自动化  │───→│ 完成   │
│ 节点   │    │ 输入节点  │    │ 节点   │    │        │
└────────┘    └──────────┘    └────────┘    └────────┘
                  │
              人工输入
           (CLI/Web/API)
```

## CLI HITL

通过命令行等待用户输入：

```python
class CLIInputNode(Node):
    def exec(self, prep_res):
        user_input = input("请确认/输入: ")
        return user_input

    def post(self, shared, prep_res, exec_res):
        shared["human_input"] = exec_res
        if exec_res == "quit":
            return "end"
        return "continue"
```

## FastAPI/Web HITL

通过HTTP API等待人工输入，使用异步轮询或WebSocket：

```
FastAPI Server
  ├─ POST /start    → 启动Flow（后台运行）
  ├─ GET  /status   → 查询当前等待的人工输入
  ├─ POST /input    → 提交人工输入，恢复Flow
  └─ WebSocket /ws  → 流式推送进度
```

Flow中的等待节点将结果存入shared，然后"暂停"等待外部触发。

## Gradio HITL

使用Gradio构建交互式界面，节点通过queue等待界面事件。

## FSM（有限状态机）模式

Streamlit/Gradio FSM将Flow建模为状态机，每个节点是一个状态，人工操作触发状态转移：

```
状态A (表单填写) ──提交──→ 状态B (预览) ──确认──→ 状态C (完成)
                              │
                            取消/修改
                              └──────→ 状态A
```

## Cookbook 对应示例

- `pocketflow-cli-hitl` — 命令行人机交互
- `pocketflow-fastapi-hitl` — FastAPI Web交互
- `pocketflow-fastapi-background` — 后台任务+进度查询
- `pocketflow-fastapi-websocket` — WebSocket流式交互
- `pocketflow-gradio-hitl` — Gradio交互式界面
- `pocketflow-streamlit-fsm` — Streamlit状态机
- `pocketflow-chat` — 基础聊天循环
- `pocketflow-chat-guardrail` — 带安全护栏的聊天
