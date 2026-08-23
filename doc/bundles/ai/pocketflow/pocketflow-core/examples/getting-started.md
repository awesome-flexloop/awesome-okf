---
title: 快速开始
type: example
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
  - /pocketflow/pocketflow-core/concepts/operator-chaining
---

# 快速开始：第一个 PocketFlow 程序

本示例演示 PocketFlow 的核心概念：定义节点、连接流程、条件分支和循环。

## 最简线性管道

```python
from pocketflow import Node, Flow

# 1. 定义节点
class SetValue(Node):
    def prep(self, shared):
        shared["value"] = 0

class Increment(Node):
    def prep(self, shared):
        shared["value"] += 1

class Double(Node):
    def prep(self, shared):
        shared["value"] *= 2

# 2. 连接节点
set_val = SetValue()
inc = Increment()
double = Double()

set_val >> inc >> double  # 线性管道

# 3. 创建并运行流程
flow = Flow(start=set_val)
shared = {}
flow.run(shared)

print(shared["value"])  # 输出: 2  (0+1)*2
```

## 条件分支

```python
from pocketflow import Node, Flow

class CheckValue(Node):
    def post(self, shared, prep_res, exec_res):
        if shared["value"] > 10:
            return "big"
        else:
            return "small"

class HandleBig(Node):
    def prep(self, shared):
        shared["result"] = f"Big: {shared['value']}"

class HandleSmall(Node):
    def prep(self, shared):
        shared["result"] = f"Small: {shared['value']}"

check = CheckValue()
big = HandleBig()
small = HandleSmall()

check - "big" >> big
check - "small" >> small

flow = Flow(start=check)
shared = {"value": 15}
flow.run(shared)
print(shared["result"])  # 输出: Big: 15
```

## 循环（自环）

```python
from pocketflow import Node, Flow

class CountDown(Node):
    def post(self, shared, prep_res, exec_res):
        if shared["count"] > 0:
            return "continue"
        else:
            return "done"

class Decrement(Node):
    def prep(self, shared):
        shared["count"] -= 1

start = CountDown()
dec = Decrement()
end = Node()  # 终止节点

start - "continue" >> dec
dec >> start          # 回到 start 形成循环
start - "done" >> end

flow = Flow(start=start)
shared = {"count": 5}
flow.run(shared)
# count 依次变为 4,3,2,1,0，然后结束
print(shared["count"])  # 输出: 0
```

## 带重试的 API 调用

```python
from pocketflow import Node, Flow
import random

class FetchData(Node):
    def __init__(self):
        super().__init__(max_retries=3)

    def exec(self, prep_res):
        if random.random() < 0.6:
            raise ConnectionError("Network error")
        return {"data": [1, 2, 3]}

    def exec_fallback(self, prep_res, exc):
        return {"data": [], "error": str(exc)}

    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res

fetch = FetchData()
flow = Flow(start=fetch)
shared = {}
flow.run(shared)
print(shared["result"])
```

## 运行验证

所有示例均为纯 Python 代码，无需额外依赖：

```bash
pip install pocketflow
python example.py
```
