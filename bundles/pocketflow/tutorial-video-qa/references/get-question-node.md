---
title: GetQuestionNode
type: reference
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/nodes.py
related:
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/concepts/linear-qa-pipeline
  - /pocketflow/pocketflow-core/references/node
---

# GetQuestionNode

`GetQuestionNode` 继承自 PocketFlow 的 `Node` 类，负责从终端用户获取问题输入。它是问答流水线的起始节点。

## 类定义

```python
from pocketflow import Node

class GetQuestionNode(Node):
    def exec(self, _):
        user_question = input("Enter your question: ")
        return user_question

    def post(self, shared, prep_res, exec_res):
        shared["question"] = exec_res
        return "default"
```

## 继承关系

```
pocketflow.Node → GetQuestionNode
```

## 生命周期方法

### `exec(self, _)`

执行用户输入获取。

- **参数**：`_` — prep 的返回值（此节点未实现 prep，使用默认值）
- **返回**：`str` — 用户从终端输入的问题文本
- **行为**：
  1. 在终端显示提示 `"Enter your question: "`
  2. 阻塞等待用户输入
  3. 返回用户输入的字符串

> **注意**：此节点的 `exec` 方法包含阻塞 I/O 操作（`input()`），不适合在异步或 Web 服务环境中直接使用。在 Web 场景中，应替换为从 HTTP 请求中获取问题。

### `post(self, shared, prep_res, exec_res)`

将用户问题存储到 shared 字典，并指定流转到下一个节点。

- **参数**：
  - `shared` (`dict`) — 流程共享字典
  - `prep_res` — prep 返回值（此节点未实现 prep）
  - `exec_res` (`str`) — exec 返回的用户问题文本
- **返回**：`str` — 固定返回 `"default"`，沿默认边流转到 AnswerNode
- **副作用**：设置 `shared["question"] = exec_res`

### `prep(self, shared)`

此节点**未重写** `prep` 方法，使用 PocketFlow Node 的默认实现（返回 `None`）。因为 `exec` 的参数为 `_`（忽略），不需要从 shared 读取任何数据。

## shared 字典读写

| 操作 | 键 | 值类型 | 说明 |
|------|-----|--------|------|
| 写入 | `"question"` | `str` | 用户输入的问题文本 |

此节点不读取 shared 中的任何数据。

## 在流程中的位置

```python
# flow.py
get_question_node = GetQuestionNode()
answer_node = AnswerNode()
get_question_node >> answer_node  # default 边连接
```

`GetQuestionNode` 是流程的起始节点（`Flow(start=get_question_node)`），通过默认边连接到 [AnswerNode](answer-node.md)。

## 典型输出

exec 返回值示例：

```
"In one sentence, what's the end of universe?"
```

## 源码位置

[nodes.py#L4-L13](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/nodes.py#L4-L13)
