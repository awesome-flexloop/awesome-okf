---
title: create_qa_flow()
type: reference
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/flow.py
related:
  - /pocketflow/tutorial-video-qa/references/get-question-node
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/concepts/linear-qa-pipeline
  - /pocketflow/pocketflow-core/references/flow
---

# create_qa_flow()

`create_qa_flow()` 是一个工厂函数，负责创建并返回配置好的问答流程（Flow）对象。它实例化所有节点，建立节点间的连接关系，并返回以 GetQuestionNode 为起点的 Flow。

## 函数签名

```python
def create_qa_flow():
    """Create and return a question-answering flow."""
```

- **参数**：无
- **返回**：`pocketflow.Flow` — 配置好的问答流程对象，起始节点为 GetQuestionNode

## 源码实现

```python
from pocketflow import Flow
from nodes import GetQuestionNode, AnswerNode

def create_qa_flow():
    """Create and return a question-answering flow."""
    # 创建节点实例
    get_question_node = GetQuestionNode()
    answer_node = AnswerNode()

    # 顺序连接节点
    get_question_node >> answer_node

    # 创建并返回流程，指定起始节点
    return Flow(start=get_question_node)
```

## 执行步骤

函数内部执行以下三个步骤：

1. **实例化节点**：创建 `GetQuestionNode` 和 `AnswerNode` 的实例
2. **建立连接**：使用 `>>` 运算符建立从 GetQuestionNode 到 AnswerNode 的默认边（default transition）
3. **创建 Flow**：以 GetQuestionNode 为起始节点创建 Flow 对象并返回

## 流程拓扑

```
get_question_node (GetQuestionNode)
        │
        │ default (>>)
        ▼
  answer_node (AnswerNode)
        │
        ▼
      (结束)
```

- 只有一条边：GetQuestionNode → AnswerNode（default）
- AnswerNode 没有后继节点，执行完后流程终止

## 模块级实例

`flow.py` 在模块级别还创建了一个预实例化的流程对象：

```python
qa_flow = create_qa_flow()
```

可以直接导入使用：

```python
from flow import qa_flow

shared = {"question": "What is AI?", "answer": None}
qa_flow.run(shared)
print(shared["answer"])
```

## 使用方式

### 方式一：使用工厂函数（推荐）

每次调用创建新的流程实例，避免状态污染：

```python
from flow import create_qa_flow

qa_flow = create_qa_flow()
shared = {"question": "What is Python?", "answer": None}
qa_flow.run(shared)
```

### 方式二：使用模块级实例

直接导入预创建的流程实例：

```python
from flow import qa_flow

shared = {}
qa_flow.run(shared)
```

## 运行流程

创建 Flow 后，通过 `flow.run(shared)` 启动执行：

```python
shared = {
    "question": "In one sentence, what's the end of universe?",
    "answer": None
}
qa_flow = create_qa_flow()
qa_flow.run(shared)
print("Question:", shared["question"])
print("Answer:", shared["answer"])
```

Flow 执行时，会从 start 节点（GetQuestionNode）开始，按连接关系依次执行每个节点，直到没有后继节点为止。

## 扩展建议

如果需要扩展流程（如增加质量校验、多轮对话等），应修改此函数来添加新节点和连接：

```python
def create_qa_flow():
    get_question_node = GetQuestionNode()
    answer_node = AnswerNode()
    validate_node = ValidateNode()  # 新增校验节点

    get_question_node >> answer_node >> validate_node
    validate_node - "retry" >> answer_node  # 校验不通过时重试
    validate_node - "pass" >> None          # 校验通过时结束

    return Flow(start=get_question_node)
```

## 源码位置

flow.py#L4-L16
