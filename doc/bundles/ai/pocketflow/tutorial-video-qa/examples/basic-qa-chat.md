---
title: 基础问答聊天
type: example
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/
related:
  - /pocketflow/tutorial-video-qa/concepts/linear-qa-pipeline
  - /pocketflow/tutorial-video-qa/concepts/llm-integration-pattern
  - /pocketflow/tutorial-video-qa/references/get-question-node
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/references/create-qa-flow
  - /pocketflow/tutorial-video-qa/references/call-llm
---

# 基础问答聊天

本示例展示如何使用本教程项目构建一个完整的终端问答聊天程序。程序启动后，用户在终端输入问题，AI 通过 LLM 生成回答并显示。

## 环境准备

### 1. 安装依赖

```bash
pip install pocketflow openai
```

### 2. 配置 API Key

**Windows PowerShell**：
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

**Linux / macOS**：
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

## 完整代码

以下是项目自带的完整示例（main.py）：

```python
from flow import create_qa_flow

def main():
    shared = {
        "question": "In one sentence, what's the end of universe?",
        "answer": None
    }

    qa_flow = create_qa_flow()
    qa_flow.run(shared)
    print("Question:", shared["question"])
    print("Answer:", shared["answer"])

if __name__ == "__main__":
    main()
```

> **注意**：`main.py` 中预设了一个问题，但实际运行时 `GetQuestionNode.exec()` 会通过 `input()` 覆盖 `shared["question"]`，因为 GetQuestionNode 的 exec 会从终端读取新的用户输入。

## 交互式运行

直接运行项目：

```bash
cd PocketFlow-Tutorial-Video-Generator
python main.py
```

运行后终端会显示提示：

```
Enter your question:
```

输入问题后按回车，等待 LLM 返回回答：

```
Enter your question: What is machine learning?
Question: What is machine learning?
Answer: Machine learning is a subset of artificial intelligence that enables systems to automatically learn and improve from experience without being explicitly programmed, by using algorithms that analyze data to identify patterns and make decisions or predictions.
```

## 代码拆解

### 步骤 1：创建节点

nodes.py 定义了两个节点类：

```python
from pocketflow import Node
from utils.call_llm import call_llm

class GetQuestionNode(Node):
    def exec(self, _):
        user_question = input("Enter your question: ")
        return user_question

    def post(self, shared, prep_res, exec_res):
        shared["question"] = exec_res
        return "default"

class AnswerNode(Node):
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        return call_llm(question)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

### 步骤 2：连接流程

flow.py 组装节点为 Flow：

```python
from pocketflow import Flow
from nodes import GetQuestionNode, AnswerNode

def create_qa_flow():
    get_question_node = GetQuestionNode()
    answer_node = AnswerNode()
    get_question_node >> answer_node
    return Flow(start=get_question_node)
```

### 步骤 3：运行流程

main.py 初始化 shared 并运行：

```python
from flow import create_qa_flow

shared = {"question": None, "answer": None}
qa_flow = create_qa_flow()
qa_flow.run(shared)
print("Answer:", shared["answer"])
```

## 执行流程详解

```
1. qa_flow.run(shared) 启动流程
2. 进入 GetQuestionNode
   ├─ prep: 未重写，返回 None
   ├─ exec: input("Enter your question: ") 阻塞等待用户输入
   │         用户输入 "What is Python?"
   └─ post: shared["question"] = "What is Python?"
            返回 "default"
3. Flow 根据 "default" 找到 AnswerNode
4. 进入 AnswerNode
   ├─ prep: 返回 shared["question"] = "What is Python?"
   ├─ exec: call_llm("What is Python?") → 调用 OpenAI API
   │         返回 "Python is a high-level programming language..."
   └─ post: shared["answer"] = "Python is a high-level..."
            返回 None（无后继节点）
5. Flow 结束
6. print(shared["answer"]) 输出结果
```

## 变体：预设问题（跳过交互式输入）

如果不想使用 `input()` 交互式输入，可以创建一个不依赖终端输入的版本：

```python
from pocketflow import Node, Flow
from utils.call_llm import call_llm

class PresetQuestionNode(Node):
    """直接使用 shared 中预设的问题，无需终端输入"""
    def post(self, shared, prep_res, exec_res):
        # 不调用 input()，使用 shared 中已有的问题
        if not shared.get("question"):
            raise ValueError("No question provided in shared")
        return "default"

class AnswerNode(Node):
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        return call_llm(question)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res

# 创建流程
preset_q = PresetQuestionNode()
answer = AnswerNode()
preset_q >> answer
flow = Flow(start=preset_q)

# 运行
shared = {"question": "Explain quantum computing in simple terms.", "answer": None}
flow.run(shared)
print(shared["answer"])
```

## 变体：多轮对话

在基础示例上扩展循环，实现多轮对话：

```python
from pocketflow import Node, Flow
from utils.call_llm import call_llm

class ChatInputNode(Node):
    def exec(self, _):
        user_input = input("You: ")
        return user_input

    def post(self, shared, prep_res, exec_res):
        if exec_res.lower() in ("quit", "exit", "bye"):
            return "exit"
        shared["history"].append({"role": "user", "content": exec_res})
        return "chat"

class ChatAnswerNode(Node):
    def prep(self, shared):
        return shared["history"]

    def exec(self, history):
        client = __import__("openai").OpenAI()
        r = client.chat.completions.create(model="gpt-4o", messages=history)
        return r.choices[0].message.content

    def post(self, shared, prep_res, exec_res):
        shared["history"].append({"role": "assistant", "content": exec_res})
        print(f"AI: {exec_res}")
        return "continue"

# 连接节点
chat_in = ChatInputNode()
chat_ans = ChatAnswerNode()
end = Node()  # 终止节点

chat_in - "chat" >> chat_ans
chat_in - "exit" >> end
chat_ans - "continue" >> chat_in  # 循环回输入节点

flow = Flow(start=chat_in)
shared = {"history": []}
flow.run(shared)
print("Goodbye!")
```

运行效果：
```
You: Hi, who are you?
AI: Hello! I'm an AI assistant...
You: What can you do?
AI: I can help answer questions, explain concepts...
You: bye
Goodbye!
```

## 常见问题

**Q: 报错 `AuthenticationError` 怎么办？**
A: 检查 `OPENAI_API_KEY` 环境变量是否正确设置，以及 API Key 是否有效。

**Q: 可以使用其他模型吗？**
A: 可以，修改 [call_llm()](../references/call-llm.md) 中的 `model` 参数，或修改 `base_url` 指向其他兼容 OpenAI 格式的 API 端点。

**Q: 如何添加重试机制？**
A: 让 AnswerNode 继承 Node 时设置 `max_retries`，并实现 `exec_fallback` 方法，详见 [LLM 集成模式](../concepts/llm-integration-pattern.md)。
