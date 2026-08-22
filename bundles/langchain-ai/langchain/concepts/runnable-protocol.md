---
type: concept
title: Runnable 协议
description: Runnable 抽象基类的执行方法族、组合原语、装饰器链与 RunnableConfig 配置传播机制
tags: [langchain, runnable, protocol, lcel, composition]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-core
    resource: /references/core-abstractions.md
    title: 核心抽象源码信源
---

# Runnable 协议

`Runnable`（`runnables/base.py:133`）是 langchain-core 最核心的抽象，定义为 `class Runnable(ABC, Generic[Input, Output])`。它是一个"可执行工作单元"——可以被调用、批处理、流式传输、转换和组合。所有核心组件（提示词、模型、解析器、工具、检索器）都继承自 `Runnable` 或其子类 `RunnableSerializable`。

## 执行方法族

`Runnable` 定义了四组对应方法，每组都有同步和异步（`a` 前缀）版本：

| 方法 | 输入 | 输出 | 说明 |
|---|---|---|---|
| `invoke(input, config=None)` | 单个 `Input` | `Output` | 同步执行（抽象方法，必须实现） |
| `ainvoke(input, config=None)` | 单个 `Input` | `Output` | 异步执行，默认在线程池跑 `invoke` |
| `batch(inputs, config=None, *, return_exceptions=False)` | `list[Input]` | `list[Output]` | 批量并行，默认线程池 |
| `abatch(inputs, ...)` | `list[Input]` | `list[Output]` | 异步批量 |
| `stream(input, config=None)` | 单个 `Input` | `Iterator[Output]` | 同步流式，默认 `yield invoke()` |
| `astream(input, config=None)` | 单个 `Input` | `AsyncIterator[Output]` | 异步流式 |
| `astream_log(input, ..., diff=True)` | 单个输入 | `AsyncIterator[RunLogPatch]` | 流式日志补丁 |
| `astream_events(input, ..., version="v2")` | 单个输入 | `AsyncIterator[StreamEvent]` | 流式事件（v1/v2） |
| `stream_events(...)` | 单个输入 | `Iterator[StreamEvent]` | 同步流式事件 |
| `transform(input_iter, config=None)` | `Iterator[Input]` | `Iterator[Output]` | 迭代器到迭代器转换 |

### 默认实现的降级策略

关键设计：子类**只需实现 `invoke`**（抽象方法，`runnables/base.py:885`），其余方法由基类提供"能用但不最优"的默认实现：

- `ainvoke`（第907行）：`await run_in_executor(config, self.invoke, ...)`，在线程池中执行同步版本。
- `batch`（第930行）：通过 `get_executor_for_config` 在线程池中并行调用 `invoke`；当只有1个输入时跳过线程池直接调用。
- `stream`（第1193行）：`yield self.invoke(input, config, **kwargs)`，不支持原生流式的组件退化为单次产出。
- `astream`（第1214行）：`yield await self.ainvoke(...)`。

需要原生性能的组件再选择性 override：
- 模型 override `_generate`/`_stream` 提供原生批处理和流式。
- `RunnableSequence`/`RunnableParallel` override `transform`/`stream` 实现管道级流式。

## Schema 自省

每个 Runnable 暴露输入/输出/配置的 schema：

- `input_schema` 属性（第375行）：返回 Pydantic 模型，描述输入结构。
- `output_schema` 属性（第451行）：描述输出结构。
- `get_input_schema(config)` / `get_output_schema(config)`：可按 config 生成 schema。
- `config_specs` 属性（第530行）：返回 `list[ConfigurableFieldSpec]`，描述可运行时配置的字段。
- `config_schema(*, include=None)`（第534行）：生成配置的 Pydantic 模型。
- `get_graph(config)`（第593行）：返回执行图 `Graph`，用于可视化。
- `InputType`/`OutputType` 属性（第309、344行）：类型对象而非实例。

## 组合原语

### 管道：`|` 与 `RunnableSequence`

`__or__`/`__ror__`（第628-724行）支持将 Runnable、字典、可调用对象通过 `|` 组合，构造 `RunnableSequence`：

```python
from langchain_core.runnables import RunnableLambda

sequence = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 2)
sequence.invoke(1)  # 4
```

`RunnableSequence`（第3075行）的 `steps` 属性返回子 Runnable 列表，`invoke`（第3430行）依次执行每个 step。

### 并行：字典与 `RunnableParallel`

在序列中使用字典字面量会自动构造 `RunnableParallel`（第3864行），所有分支接收相同输入并并行执行：

```python
sequence = RunnableLambda(lambda x: x + 1) | {
    "mul_2": RunnableLambda(lambda x: x * 2),
    "mul_5": RunnableLambda(lambda x: x * 5),
}
sequence.invoke(1)  # {'mul_2': 4, 'mul_5': 10}
```

### 其他组合方法

- `pipe(*others)`（第724行）：显式管道，等价于 `|`。
- `pick(keys)`（第773行）：从字典输出中选取一个或多个键。
- `assign(**kwargs)`（第836行）：向字典输出追加键值对（值可以是 Runnable 或 Callable）。
- `map()`（第2165行）：返回 `RunnableEach`，对输入序列逐元素应用。

## 函数适配：RunnableLambda 与 RunnableGenerator

- **`RunnableLambda`**（第4703行）：将任意 Python 函数包装为 Runnable。自动推断输入 schema（从函数签名和类型注解）。`deps` 属性（第5069行）返回函数闭包中引用的其他 Runnable。
- **`RunnableGenerator`**（第4399行）：将生成器函数包装为 Runnable，支持 `transform`/`stream` 原生流式。
- **`RunnablePassthrough`**（`runnables/passthrough.py`）：透传输入，常用于 `assign` 构造字典。
- **`RunnableAssign`**（`runnables/passthrough.py`）：`assign` 的底层实现。

## 装饰器链

`Runnable` 提供一组返回新 Runnable 包装器的方法（不修改原对象）：

| 方法 | 行号 | 作用 |
|---|---|---|
| `bind(**kwargs)` | 1851 | 绑定 kwargs 到每次调用，返回 `RunnableBinding` |
| `with_config(config, **kwargs)` | 1885 | 绑定配置（tags/metadata/callbacks 等） |
| `with_retry(...)` | 2101 | 重试包装（退避策略、可重试异常） |
| `with_fallbacks(handlers, ...)` | 2188 | 降级包装，失败时切换到备用 Runnable |
| `with_listeners(...)` | 1910 | 同步生命周期监听器 |
| `with_alisteners(...)` | 1982 | 异步生命周期监听器 |
| `with_types(*, input_type, output_type)` | 2079 | 覆盖输入/输出类型 |
| `as_tool(args_schema, *, name, description, arg_types)` | 2708 | beta：将 Runnable 转为 `BaseTool` |

`RunnableSerializable`（第2827行）额外提供：
- `configurable_fields(**kwargs)`（第2855行）：将初始化参数声明为可运行时通过 `config["configurable"]` 覆盖。
- `configurable_alternatives(which, *, default_key, **kwargs)`（第2913行）：声明可运行时替换的替代实现。

`RunnableBindingBase`（第5851行）是 `bind`/`with_config` 的产物基类，持有 `bound: Runnable`、`kwargs`、`config` 三个字段。

## RunnableConfig 配置传播

`RunnableConfig`（`runnables/config.py:57`）是 `TypedDict(total=False)`，包含8个字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `tags` | `list[str]` | 标签，传播到子调用和回调 |
| `metadata` | `dict[str, Any]` | 元数据，值需 JSON 可序列化 |
| `callbacks` | `Callbacks` | 回调处理器列表 |
| `run_name` | `str` | tracer 运行名称 |
| `max_concurrency` | `int \| None` | 最大并行数 |
| `recursion_limit` | `int` | 最大递归次数，默认 25 |
| `configurable` | `dict[str, Any]` | `configurable_fields` 的运行时值 |
| `run_id` | `uuid.UUID \| None` | 运行 UUID |

### ContextVar 自动传播

配置传播不通过显式参数逐层传递，而是通过 `var_child_runnable_config`（`config.py:174`）这个 `ContextVar`。父 Runnable 调用子 Runnable 时，配置通过 `merge_configs`（第431行）合并后设置到 ContextVar，子组件自动继承并可追加。`COPIABLE_KEYS`（第142行）定义了可继承的键：`tags`、`metadata`、`callbacks`、`configurable`。

常用辅助函数：
- `ensure_config(config)`（第255行）：补全默认值。
- `get_config_list(config, length)`（第311行）：将单配置展开为列表（批处理用）。
- `patch_config(config, **kwargs)`（第357行）：局部修补。
- `merge_configs(*configs)`（第431行）：合并多个配置。

## RunnableSerializable

`RunnableSerializable(Serializable, Runnable[Input, Output])`（第2827行）组合了 Runnable 协议和 Serializable 序列化能力。所有具体组件（BaseChatModel、BaseTool、BasePromptTemplate、BaseRetriever 等）都继承自此基类，因此既能被执行也能被 `to_json()` 序列化。

## 代码示例

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# 1. 基本组合
runnable = (
    RunnableLambda(lambda x: x + 1)
    | RunnableLambda(lambda x: x * 2)
    | RunnableLambda(lambda x: {"result": x})
)
assert runnable.invoke(1) == {"result": 4}

# 2. bind 与 with_config
bound = RunnableLambda(lambda x: x["base"] + x["add"]).bind(add=10)
assert bound.invoke({"base": 5}) == 15

configured = bound.with_config(tags=["demo"], run_name="add_demo")
configured.invoke({"base": 5})

# 3. with_retry / with_fallbacks
retrying = runnable.with_retry(stop_after_attempt=3)
fallback = runnable.with_fallbacks([RunnableLambda(lambda x: {"result": -1})])

# 4. map 逐元素处理
mapper = RunnableLambda(lambda x: x * 2).map()
assert mapper.invoke([1, 2, 3]) == [2, 4, 6]

# 5. assign 追加字段
enriched = RunnablePassthrough().assign(doubled=RunnableLambda(lambda x: x * 2))
assert enriched.invoke(3) == {"doubled": 6}  # RunnablePassthrough 透传 + assign
```

## 相关概念

- [总览](/langchain-ai/langchain/concepts/overview) —— Runnable 在整体架构中的位置
- [消息类型](/langchain-ai/langchain/concepts/message-types) —— 模型输入输出数据结构
- [工具抽象](/langchain-ai/langchain/concepts/tool-abstraction) —— BaseTool 本身也是 RunnableSerializable
- [回调系统](/langchain-ai/langchain/concepts/callback-system) —— 配置中 callbacks 的处理机制
