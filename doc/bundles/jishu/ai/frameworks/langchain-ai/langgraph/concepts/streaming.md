---
type: concept
scope: langgraph
name: streaming
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 流式处理——七种流模式、StreamWriter、消息 token 流、v2 流部分类型
---

# 流式处理（Streaming）

LangGraph 提供丰富的流式输出能力，支持从完整状态到 token 级消息的多种粒度。流通过 `stream()`/`astream()` 方法访问，由 `stream_mode` 参数控制。

## 流模式

`StreamMode = Literal["values", "updates", "checkpoints", "tasks", "debug", "messages", "custom"]`

### values

每步后输出完整状态：

```python
for state in graph.stream(input, stream_mode="values"):
    print(state)  # 完整状态 dict
```

产出 `ValuesStreamPart`：

```python
{
    "type": "values",
    "ns": tuple[str, ...],      # 子图命名空间
    "data": OutputT,            # 完整状态
    "interrupts": tuple[Interrupt, ...],
}
```

### updates

每步输出各节点的增量更新（默认模式）：

```python
for update in graph.stream(input, stream_mode="updates"):
    print(update)  # {"node_name": {"key": value}}
```

产出 `UpdatesStreamPart`：

```python
{
    "type": "updates",
    "ns": tuple[str, ...],
    "data": dict[str, Any],    # 节点名 → 更新值
}
```

多节点并行执行时更新分别产出。可能包含 `__interrupt__` 和 `__metadata__` 特殊键。

### messages

LLM token 级消息流：

```python
for msg, metadata in graph.stream(input, stream_mode="messages"):
    print(msg.content, end="", flush=True)
```

产出 `MessagesStreamPart`：

```python
{
    "type": "messages",
    "ns": tuple[str, ...],
    "data": tuple[AnyMessage, dict[str, Any]],  # (消息块, 元数据)
}
```

metadata 包含 `langgraph_step`、`langgraph_node`、`langgraph_triggers`、`langgraph_checkpoint_ns` 等。由 `StreamMessagesHandler` 从 LLM 回调中捕获 token。

### custom

节点内通过 `StreamWriter` 发射的自定义数据：

```python
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer({"progress": 50})
    return {"result": "done"}

for chunk in graph.stream(input, stream_mode="custom"):
    print(chunk)  # {"progress": 50}
```

`StreamWriter = Callable[[Any], None]`，通过 `get_stream_writer()` 或节点参数注入。未使用 `stream_mode="custom"` 时是 no-op。

### checkpoints

检查点创建事件：

```python
for cp in graph.stream(input, stream_mode="checkpoints"):
    print(cp["values"], cp["next"])
```

产出 `CheckpointStreamPart`，data 为 `CheckpointPayload`（含 config、metadata、values、next、parent_config、tasks）。

### tasks

任务开始和完成事件：

```python
for event in graph.stream(input, stream_mode="tasks"):
    if "result" in event["data"]:
        print(f"Task {event['data']['name']} done")
```

产出 `TasksStreamPart`，data 为 `TaskPayload`（id、name、input、triggers）或 `TaskResultPayload`（id、name、error、interrupts、result）。

### debug

同时产出 checkpoints 和 tasks 事件，用于调试：

```python
for event in graph.stream(input, stream_mode="debug"):
    if event["type"] == "checkpoint": ...
    elif event["type"] == "task": ...
    elif event["type"] == "task_result": ...
```

产出 `DebugStreamPart`，data 为带 step、timestamp、type 标签的调试负载。

## 多模式流

可以同时请求多个流模式：

```python
for stream_name, chunk in graph.stream(input, stream_mode=["updates", "messages"]):
    if stream_name == "messages":
        print(chunk[0].content, end="")
    else:
        print(chunk)
```

也可使用 `astream_events(version="v3")` 获取统一的 LangChain 事件流。v3 内部通过 `StreamMux` 和 `StreamTransformer` 组合多种模式。

## v2 流部分

使用 `version="v2"` 时，所有流产出统一为带类型标签的 `StreamPart`：

```python
async for part in graph.astream(input, version="v2"):
    if part["type"] == "values":
        part["data"]  # OutputT
    elif part["type"] == "messages":
        part["data"]  # (BaseMessage, dict)
```

`StreamPart` 是所有流部分类型的判别联合，用 `part["type"]` 窄化类型。

`invoke()` 使用 `version="v2"` 时返回 `GraphOutput(value, interrupts)` 而非裸值。

## StreamWriter

`StreamWriter` 是接受单参数的可调用对象，在节点内通过两种方式获取：

1. **参数注入**：节点函数声明 `writer: StreamWriter` 参数
2. **函数获取**：调用 `get_stream_writer()`

```python
# 方式1：参数注入
def node(state, writer: StreamWriter):
    writer("starting...")
    ...

# 方式2：运行时获取
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer({"step": 1})
```

StreamWriter 依赖 contextvar 传播，Python < 3.11 在 async 上下文中可能不可用。

## push_message

`push_message()` 是专门用于消息的手动流写入：

```python
from langgraph.graph.message import push_message

push_message(AIMessage(content="Processing..."))
```

它同时写入 messages 流和状态通道，支持 `state_key` 参数指定通道名。

## StreamTransformer

`StreamTransformer` 是 v3 流事件系统的扩展点，可以在流数据传递给消费者前进行转换。编译时通过 `transformers` 参数传入：

```python
graph = builder.compile(transformers=[MyTransformer()])
```

内建 transformer 包括：
- `LifecycleTransformer`：生命周期事件
- `MessagesTransformer`：消息流处理
- `SubgraphTransformer`：子图命名空间传播
- `ValuesTransformer`：状态值转换

## 子图流

子图的流产出带有命名空间前缀 `ns`，格式为元组如 `("parent", "subgraph", "0")`。数字部分表示 Send 创建的并行任务索引。

`DuplexStream` 将父图流和子图流合并，根据模式标签分发到正确的消费者。

## 相关概念

- Pregel 引擎 — 流在超步中的产出时机
- 消息图 — messages 流模式与 token 输出
- 状态图 — stream_mode 参数传递
- API 参考 — stream 方法签名
