---
title: AnswerNode
type: reference
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/nodes.py
related:
  - /pocketflow/tutorial-video-qa/references/get-question-node
  - /pocketflow/tutorial-video-qa/references/call-llm
  - /pocketflow/tutorial-video-qa/concepts/linear-qa-pipeline
  - /pocketflow/tutorial-video-qa/concepts/llm-integration-pattern
  - /pocketflow/pocketflow-core/references/node
---

# AnswerNode

`AnswerNode` 继承自 PocketFlow 的 `Node` 类，负责调用 LLM 生成问题的回答。它是问答流水线的处理节点，从 shared 字典读取问题，调用 [call_llm()](call-llm.md) 生成回答，并将结果写回 shared。

## 类定义

```python
from pocketflow import Node
from utils.call_llm import call_llm

class AnswerNode(Node):
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        return call_llm(question)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

## 继承关系

```
pocketflow.Node → AnswerNode
```

## 生命周期方法

### `prep(self, shared)`

从 shared 字典中读取前序节点存储的问题。

- **参数**：`shared` (`dict`) — 流程共享字典
- **返回**：`str` — `shared["question"]` 的值，即用户问题文本
- **读取的键**：`shared["question"]` (`str`)

### `exec(self, question)`

调用 LLM 生成回答。

- **参数**：`question` (`str`) — prep 返回的用户问题文本
- **返回**：`str` — LLM 生成的回答文本
- **行为**：调用 [call_llm(question)](call-llm.md) 函数，该函数内部使用 OpenAI API 调用 gpt-4o 模型生成回答
- **异常**：可能抛出网络异常、API 认证异常等（当前未配置重试）

### `post(self, shared, prep_res, exec_res)`

将 LLM 生成的回答存储到 shared 字典。

- **参数**：
  - `shared` (`dict`) — 流程共享字典
  - `prep_res` (`str`) — prep 返回的问题文本（此处未使用）
  - `exec_res` (`str`) — exec 返回的 LLM 回答文本
- **返回**：`None`（隐式返回），Flow 找不到后继节点后终止
- **副作用**：设置 `shared["answer"] = exec_res`

> **注意**：`post` 方法未显式返回 action 字符串，隐式返回 `None`。由于 AnswerNode 没有通过 `>>` 连接后继节点，Flow 会正常终止。如果需要连接更多节点，应返回 `"default"` 并建立连接。

## shared 字典读写

| 操作 | 键 | 值类型 | 说明 |
|------|-----|--------|------|
| 读取 | `"question"` | `str` | 由 GetQuestionNode 写入的用户问题 |
| 写入 | `"answer"` | `str` | LLM 生成的回答文本 |

## 在流程中的位置

```python
# flow.py
get_question_node = GetQuestionNode()
answer_node = AnswerNode()
get_question_node >> answer_node  # AnswerNode 是流水线的终点
```

`AnswerNode` 是流程的终止节点，没有后继节点。Flow 执行完 AnswerNode 后，调用者从 `shared["answer"]` 获取最终结果。

## 构造参数

`AnswerNode` 未定义自定义 `__init__` 方法，使用 Node 的默认构造参数：

```python
answer_node = AnswerNode()  # max_retries 默认为 1
```

如需启用重试机制，可以在实例化后设置或创建子类：

```python
class RetryAnswerNode(AnswerNode):
    def __init__(self):
        super().__init__(max_retries=3)
```

## 典型输出

exec 返回值示例（取决于问题和 LLM 响应）：

```
"The end of the universe, according to current cosmological models, is likely the heat death, where the universe reaches maximum entropy and no thermodynamic free energy remains to sustain processes that increase entropy."
```

## 源码位置

[nodes.py#L15-L26](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/nodes.py#L15-L26)
