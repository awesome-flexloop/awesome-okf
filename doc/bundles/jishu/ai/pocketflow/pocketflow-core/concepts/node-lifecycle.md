---
title: 节点生命周期
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/base-node
  - /pocketflow/pocketflow-core/references/node
---

# 节点生命周期

PocketFlow 的每个节点（Node/AsyncNode）都遵循 **prep → exec → post** 三阶段生命周期。这是框架最核心的抽象，所有业务逻辑都通过重写这三个方法实现。

## 三阶段模型

```
┌─────────────────────────────────────────────────┐
│                  Node.run(shared)                │
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │  prep()  │───→│  exec()  │───→│  post()  │   │
│  │ (读取)   │    │ (计算)   │    │ (写入)   │   │
│  └──────────┘    └──────────┘    └──────────┘   │
│       │              │              │            │
│    读shared     纯计算        写shared+返回action │
│    返回prep_res  返回exec_res                    │
└─────────────────────────────────────────────────┘
```

### prep — 读取与准备

```python
def prep(self, shared):
    """从 shared 读取数据，做执行前准备"""
    data = shared.get("input_data")
    return data  # 返回值传给 exec
```

**职责**：
- 从 `shared` 字典读取前序节点写入的数据
- 进行数据转换、校验、拆分
- 返回值作为 exec 的输入（prep_res）

**设计原则**：prep 只做"读"和"准备"，不做核心计算或外部调用。

### exec — 核心执行

```python
def exec(self, prep_res):
    """核心业务逻辑，纯计算或 I/O 调用"""
    result = process(prep_res)
    return result  # 返回值传给 post
```

**职责**：
- 实现节点的核心业务逻辑（LLM 调用、API 请求、数据处理等）
- 接收 prep_res 作为输入
- 是**唯一可以被重试**的阶段（受 max_retries 控制）

**设计原则**：exec 应尽量保持"纯"——不直接修改 shared，不决定分支走向，只做计算/调用并返回结果。

### post — 写入与分支决策

```python
def post(self, shared, prep_res, exec_res):
    """将结果写入 shared，决定下一个 action"""
    shared["output"] = exec_res
    return "success"  # 返回 action 字符串，决定走哪条边
```

**职责**：
- 将 exec 的结果写入 `shared` 字典，供后续节点读取
- 返回 action 字符串决定流程走向：
  - 返回 `None`（默认）→ 走 default 边（`>>`）
  - 返回字符串（如 `"success"`/`"error"`）→ 走对应条件边（`- "action" >>`）

**设计原则**：post 负责"写"和"决策"，不重复 exec 的计算逻辑。

## 数据流

```
shared 字典（贯穿全流程）
  │
  ├─ Node A: prep读 → exec计算 → post写结果A
  │                                    │
  ├─ Node B: prep读结果A → exec计算 → post写结果B
  │                                          │
  └─ Node C: prep读结果B → exec计算 → post写最终结果
```

- 节点间**不直接传递数据**，所有通信通过 `shared` 字典
- prep 从 shared 读取，post 向 shared 写入
- exec 的输入是 prep_res（节点内传递），不直接访问 shared

## 重试机制的位置

重试只发生在 exec 阶段：

```
prep(shared)  ← 只执行一次
  │
  ├─ exec(prep_res) → 成功 → post
  ├─ exec(prep_res) → 失败 → 重试（第1次）
  ├─ exec(prep_res) → 失败 → 重试（第2次）
  └─ exec_fallback(prep_res, exc) → post  ← 全部失败后降级
```

- prep 和 post **不参与重试**，无论重试多少次都只执行一次
- exec_fallback 在全部重试失败后执行一次，提供降级结果
- post 始终执行一次，无论 exec 是成功还是走了 fallback

## AsyncNode 的异步生命周期

异步节点将三个阶段改为 async 方法：

```python
async def prep_async(self, shared): ...
async def exec_async(self, prep_res): ...
async def post_async(self, shared, prep_res, exec_res): ...
```

调用链变为 `await prep_async → await exec_async → await post_async`，语义完全相同。

## 代码模板

```python
from pocketflow import Node

class MyNode(Node):
    def prep(self, shared):
        # 1. 读取准备
        return shared.get("input")

    def exec(self, prep_res):
        # 2. 核心执行（可重试）
        return do_work(prep_res)

    def post(self, shared, prep_res, exec_res):
        # 3. 写入 + 分支决策
        shared["result"] = exec_res
        return "default"  # 或 None，走默认边
```
