---
type: concept
title: 回调系统
description: BaseCallbackHandler 的 Mixin 组合、CallbackManager 同步/异步双树、RunManager 层级与 BaseTracer 追踪机制
tags: [langchain, callbacks, tracing, handler, manager]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-rc
    resource: /references/runnables-callbacks.md
    title: 回调、追踪与检索源码信源
---

# 回调系统

回调系统是 langchain-core 的横切关注点，用于在组件执行的生命周期中插入自定义逻辑——日志记录、进度追踪、流式输出、LangSmith 追踪等。系统由三部分组成：Handler（事件处理器）、Manager（回调管理器，负责传播）、Tracer（追踪器，构建 Run 树）。同步和异步使用两棵完全独立的类树。

## Mixin 组合的 Handler 体系

`BaseCallbackHandler`（`callbacks/base.py:496`）通过多继承组合6个 Mixin：

```
BaseCallbackHandler(
    LLMManagerMixin,          # on_llm_new_token / on_llm_end / on_llm_error / on_stream_event
    ChainManagerMixin,        # on_chain_end / on_chain_error / on_agent_action / on_agent_finish
    ToolManagerMixin,         # on_tool_end / on_tool_error
    RetrieverManagerMixin,    # on_retriever_end / on_retriever_error
    CallbackManagerMixin,     # on_llm_start / on_chat_model_start / on_retriever_start / on_chain_start / on_tool_start
    RunManagerMixin,          # on_text / on_retry / on_custom_event
)
```

### 各 Mixin 的事件方法

| Mixin | 行号 | 关键方法 |
|---|---|---|
| `RetrieverManagerMixin` | 24 | `on_retriever_error`、`on_retriever_end` |
| `LLMManagerMixin` | 62 | `on_llm_new_token`（token 流）、`on_llm_end(response: LLMResult)`、`on_llm_error`、`on_stream_event` |
| `ChainManagerMixin` | 169 | `on_chain_end(outputs)`、`on_chain_error`、`on_agent_action`、`on_agent_finish` |
| `ToolManagerMixin` | 241 | `on_tool_end(output)`、`on_tool_error` |
| `CallbackManagerMixin` | 279 | 各组件的 `*_start`（接收 serialized、输入、run_id、tags、metadata） |
| `RunManagerMixin` | 435 | `on_text`、`on_retry`、`on_custom_event` |

事件遵循 `on_<component>_start` → （`on_llm_new_token`/`on_text` 等中间事件）→ `on_<component>_end`/`on_<component>_error` 的生命周期。

### BaseCallbackHandler 字段与过滤

| 成员 | 行号 | 说明 |
|---|---|---|
| `raise_error: bool = False` | 506 | handler 内异常是否抛出 |
| `run_inline: bool = False` | 509 | 是否在当前线程内联执行（避免死锁） |
| `ignore_llm` | 513 | 忽略 LLM 事件 |
| `ignore_retry` | 518 | 忽略重试事件 |
| `ignore_chain` | 523 | 忽略链事件 |
| `ignore_agent` | 528 | 忽略 agent 事件 |
| `ignore_retriever` | 533 | 忽略检索事件 |
| `ignore_chat_model` | 538 | 忽略聊天模型事件 |
| `ignore_custom_event` | 543 | 忽略自定义事件 |

所有 `ignore_*` 属性默认返回 `False`，子类可 override 为 `True` 以过滤不关心的事件类型，减少开销。

### AsyncCallbackHandler

`AsyncCallbackHandler`（第548行）继承 `BaseCallbackHandler`，为每个事件提供 async 版本（空实现）：
- `on_llm_start`（第551行）接收 `prompts: list[str]`（传统 LLM）。
- `on_chat_model_start`（第580行）接收 `messages: list[list[BaseMessage]]`（聊天模型，双层列表：多个 prompt × 多轮消息）。
- `on_llm_end`（第655行）接收 `response: LLMResult`。
- `on_custom_event`（第980行）用于自定义事件。

自定义异步 handler 继承 `AsyncCallbackHandler`，只 override 需要的 async 方法。

## CallbackManager 双树

`callbacks/manager.py` 定义了同步和异步两棵独立的管理器树：

### 基类 BaseCallbackManager

`BaseCallbackManager`（`callbacks/base.py:1004`）维护 handler 列表和标签/元数据：

| 方法 | 行号 | 说明 |
|---|---|---|
| `__init__(handlers, inheritable_handlers, parent_run_id, *, tags, inheritable_tags, metadata, inheritable_metadata)` | 1007 | 区分可继承/不可继承两类 |
| `copy()` | 1039 | 复制管理器 |
| `merge(other)` | 1051 | 合并两个管理器 |
| `is_async` | 1107 | 是否异步 |
| `add_handler` / `remove_handler` | 1111 / 1127 | 增删 handler |
| `set_handlers` / `set_handler` | 1138 / 1154 | 批量设置 |
| `add_tags` / `remove_tags` | 1167 / 1185 | 标签管理 |
| `add_metadata` / `remove_metadata` | 1197 / 1218 | 元数据管理 |

handler、tags、metadata 各分为 inheritable（传播到子 run）和 non-inheritable（仅当前 run）两类。

### RunManager 层级

每次组件执行时，Manager 创建对应的 RunManager：

```
BaseRunManager(RunManagerMixin)              manager.py:490
├── RunManager(BaseRunManager)               manager.py:546
│   └── ParentRunManager(RunManager)         manager.py:599
└── AsyncRunManager(BaseRunManager, ABC)     manager.py:621
    └── AsyncParentRunManager(AsyncRunManager)  manager.py:683
```

组件特定的 RunManager：
- `CallbackManagerForLLMRun`（第705行）/ `AsyncCallbackManagerForLLMRun`（第806行）
- `CallbackManagerForChainRun`（第928行）/ `AsyncCallbackManagerForChainRun`（第1018行）
- `CallbackManagerForToolRun`（第1127行）/ `AsyncCallbackManagerForToolRun`（第1181行）
- `CallbackManagerForRetrieverRun`（第1248行）/ `AsyncCallbackManagerForRetrieverRun`（第1302行）

这些 RunManager 传给组件的 `_generate`/`_run`/`_get_relevant_documents` 等内部方法，组件可通过 `run_manager.get_child()` 创建子 run 的管理器，形成父子追踪树。

### 顶层 Manager

- `CallbackManager(BaseCallbackManager)`（第1377行）：同步顶层管理器，配置 handler 后随 `RunnableConfig` 传播。
- `AsyncCallbackManager(BaseCallbackManager)`（第1859行）：异步版本。

## 配置传播

回调通过 `RunnableConfig` 的 `callbacks` 字段传入（`runnables/config.py:92`）。结合 ContextVar `var_child_runnable_config`（第174行），父 Runnable 的 callbacks/tags/metadata 自动传播到子 Runnable——无需显式逐层传递。`COPIABLE_KEYS`（第142行）确保 `tags`、`metadata`、`callbacks`、`configurable` 被子调用继承和合并。

用户可通过以下方式接入回调：

```python
# 方式1：传入 invoke 的 config
chain.invoke(input, config={"callbacks": [my_handler], "tags": ["demo"]})")

# 方式2：with_config 绑定
configured = chain.with_config(callbacks=[my_handler])

# 方式3：组件构造时传入（如 model.callbacks）
```

## Tracer 追踪器

`BaseTracer`（`tracers/base.py:33`）继承 `_TracerCore` 和 `BaseCallbackHandler`，是构建追踪树的基类：

```python
class BaseTracer(_TracerCore, BaseCallbackHandler, ABC):
    def _persist_run(self, run: Run) -> None: ...    # 子类实现持久化
    def _start_trace(self, run: Run) -> None: ...
    def _end_trace(self, run: Run) -> None: ...
```

它实现所有 `on_*` 方法，将回调事件转换为 `Run` 对象（`tracers/schemas.py`），通过 `_persist_run` 钩子持久化（LangSmith tracer 发送到云端，文件 tracer 写本地等）。

`AsyncBaseTracer`（第551行）是异步版本，额外提供细粒度内部钩子：
- `_on_run_create`（第904行）、`_on_run_update`（第907行）
- `_on_llm_start`/`_on_llm_end`/`_on_llm_error`（第910-916行）
- `_on_chain_start`/`_on_tool_start`/`_on_retriever_start` 等

这些 `_on_*` 钩子在 `Run` 对象构建完成后调用，子类可 override 实现自定义处理而不必处理事件解析逻辑。

### 内置 Tracer

- `tracers/langchain.py`：`LangChainTracer`，发送到 LangSmith。
- `tracers/stdout.py`：打印到标准输出。
- `tracers/run_collector.py`：收集 Run 到列表（测试用）。
- `tracers/evaluation.py`：评估用 tracer。
- `tracers/event_stream.py`：`astream_events` 的底层实现。
- `tracers/log_stream.py`：`astream_log` 的底层实现。

## 自定义 Handler 示例

```python
from langchain_core.callbacks import BaseCallbackHandler

class TimingHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, *, run_id, **kwargs):
        print(f"LLM 开始: {run_id}")

    def on_llm_end(self, response, *, run_id, **kwargs):
        print(f"LLM 结束: {run_id}")

    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs):
        print(f"工具开始: {serialized.get('name')}")

    def on_tool_end(self, output, *, run_id, **kwargs):
        print(f"工具结束: {output}")

    def on_chain_error(self, error, *, run_id, **kwargs):
        print(f"链错误: {error}")

# 使用
chain.invoke(input, config={"callbacks": [TimingHandler()]})
```

异步场景继承 `AsyncCallbackHandler`，override `async def on_*` 方法。

## 相关概念

- [Runnable 协议](/ai/langchain-ai/langchain/concepts/runnable-protocol) —— RunnableConfig 中 callbacks 的传播
- [聊天模型](/ai/langchain-ai/langchain/concepts/chat-model) —— 模型执行触发 on_chat_model_start/end
- [工具抽象](/ai/langchain-ai/langchain/concepts/tool-abstraction) —— 工具执行触发 on_tool_start/end
- [检索器与向量库](/ai/langchain-ai/langchain/concepts/retriever-vectorstore) —— 检索触发 on_retriever_start/end
