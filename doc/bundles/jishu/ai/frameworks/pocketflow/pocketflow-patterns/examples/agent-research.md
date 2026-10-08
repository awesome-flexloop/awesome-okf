---
title: 研究Agent完整示例
type: example
bundle: pocketflow-patterns
source: cookbook/pocketflow-agent
related:
  - /pocketflow/pocketflow-patterns/concepts/agent-loop
---

# 研究Agent完整示例

构建一个自动研究Agent：接收研究问题，自主搜索网页，判断是否已有足够信息，最终生成答案。

## 节点定义

```python
from pocketflow import Node, Flow
from utils import call_llm, search_web

class DecideAction(Node):
    """决策节点：判断下一步是搜索还是回答"""
    def prep(self, shared):
        question = shared["question"]
        context = shared.get("search_results", [])
        return question, context

    def exec(self, inputs):
        question, context = inputs
        if not context:
            return "search"  # 无搜索结果，先搜索
        prompt = f"""Question: {question}
Search results so far: {context}
Should we search more or answer? Reply with exactly one word: 'search' or 'answer'."""
        decision = call_llm(prompt).strip().lower()
        return decision if decision in ("search", "answer") else "search"

    def post(self, shared, prep_res, exec_res):
        return exec_res  # "search" 或 "answer"

class SearchWeb(Node):
    """搜索节点：执行网页搜索"""
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        results = search_web(question)
        return results

    def post(self, shared, prep_res, exec_res):
        if "search_results" not in shared:
            shared["search_results"] = []
        shared["search_results"].append(exec_res)
        return "decide"  # 回到决策节点

class AnswerQuestion(Node):
    """回答节点：基于搜索结果生成答案"""
    def prep(self, shared):
        return shared["question"], shared.get("search_results", [])

    def exec(self, inputs):
        question, context = inputs
        prompt = f"""Question: {question}
Search results: {context}
Please provide a comprehensive answer based on the search results."""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

## 流程连接

```python
def create_research_agent():
    decide = DecideAction()
    search = SearchWeb()
    answer = AnswerQuestion()

    decide - "search" >> search
    decide - "answer" >> answer
    search - "decide" >> decide  # 搜索后回到决策

    return Flow(start=decide)
```

## 运行

```python
flow = create_research_agent()
shared = {"question": "What is PocketFlow framework?"}
flow.run(shared)
print(shared["answer"])
```

## 增强版：Supervisor质量检查

```python
class SupervisorNode(Node):
    """监督节点：检查答案质量"""
    def prep(self, shared):
        return shared["question"], shared["answer"]

    def exec(self, inputs):
        question, answer = inputs
        prompt = f"""Question: {question}
Answer: {answer}
Is this answer comprehensive and accurate? Reply 'pass' or 'retry'."""
        return call_llm(prompt).strip().lower()

    def post(self, shared, prep_res, exec_res):
        if exec_res == "pass":
            return "done"
        shared["search_results"] = []  # 清空结果重新搜索
        return "retry"

# 外层流程：Agent → Supervisor
agent_flow = create_research_agent()
supervisor = SupervisorNode()

agent_flow >> supervisor
supervisor - "retry" >> agent_flow

supervised_flow = Flow(start=agent_flow)
```
