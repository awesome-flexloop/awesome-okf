---
title: 线性问答流水线
type: concept
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/
related:
  - /pocketflow/tutorial-video-qa/references/get-question-node
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/references/create-qa-flow
---

# 线性问答流水线

线性问答流水线（Linear QA Pipeline）是 PocketFlow 中最基础的流程模式，所有节点通过 `>>` 运算符顺序连接，每个节点的 `post` 方法返回 `"default"`（或 `None`），沿默认边流转到下一个节点。

## 两阶段结构

本教程的问答流水线采用经典的**输入→处理**两阶段结构：

```
┌─────────────────────┐      default       ┌─────────────────────┐
│  GetQuestionNode    │ ──────────────────→ │     AnswerNode      │
│                     │                    │                     │
│  exec: 读取用户输入  │                    │  exec: 调用 LLM     │
│  post: 存储问题     │                    │  post: 存储回答     │
└─────────────────────┘                    └─────────────────────┘
        ↓ shared["question"]                     ↓ shared["answer"]
```

### 第一阶段：问题获取（GetQuestionNode）

- **exec**：调用 `input()` 从终端读取用户问题文本
- **post**：将问题文本存入 `shared["question"]`，返回 `"default"` 流转到下一节点

### 第二阶段：回答生成（AnswerNode）

- **prep**：从 `shared["question"]` 读取前一节点存储的问题
- **exec**：将问题传递给 `call_llm()` 函数，调用 LLM API 生成回答
- **post**：将 LLM 返回的回答存入 `shared["answer"]`，流程结束

## 数据流转：shared 字典

节点间通过 `shared` 字典进行数据传递，这是 PocketFlow 中节点通信的唯一机制：

| 阶段 | 操作 | shared 状态变化 |
|------|------|----------------|
| 流程启动前 | 初始化 | `{"question": ..., "answer": None}` |
| GetQuestionNode.post | 写入问题 | `{"question": "用户输入的问题", "answer": None}` |
| AnswerNode.prep | 读取问题 | — |
| AnswerNode.exec | LLM 推理 | — |
| AnswerNode.post | 写入回答 | `{"question": "...", "answer": "LLM生成的回答"}` |
| 流程结束 | 调用者读取 | `shared["answer"]` 即为最终结果 |

## prep→exec→post 三阶段分工

在流水线中，每个节点的三个生命周期方法承担不同职责：

| 方法 | 职责 | 典型操作 |
|------|------|---------|
| `prep(shared)` | 数据准备 | 从 shared 读取前序节点输出，准备 exec 所需参数 |
| `exec(prep_res)` | 核心计算 | 执行业务逻辑（I/O 操作、LLM 调用、数据处理等） |
| `post(shared, prep_res, exec_res)` | 结果存储 | 将 exec 结果写回 shared，决定下一个 action |

这种分工使得每个方法职责单一，便于测试和复用。

## 与其他流程模式的对比

线性流水线是最简单的流程模式，除此之外 PocketFlow 还支持：

- **条件分支**：post 返回不同 action 字符串，走不同分支（`node - "action" >> next_node`）
- **循环**：后继节点指回前面的节点，直到 post 返回退出 action
- **嵌套**：Flow 本身也是 Node，可以嵌入另一个 Flow 中

本教程 intentionally 保持最简线性结构，作为 PocketFlow 入门的第一步。

## 扩展方向

基于此线性流水线，可以扩展出更复杂的问答系统：

1. **多轮对话**：在 AnswerNode 之后增加循环，回到 GetQuestionNode 实现连续对话
2. **质量校验**：在 AnswerNode 后增加校验节点，根据回答质量决定重试或输出
3. **上下文记忆**：在 shared 中维护对话历史列表，每次 LLM 调用携带历史记录
4. **多模型路由**：根据问题类型（代码/数学/常识）路由到不同的回答节点
