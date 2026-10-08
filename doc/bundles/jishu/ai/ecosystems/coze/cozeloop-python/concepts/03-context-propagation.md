---
type: concept
title: "上下文传播"
description: "理解 CozeLoop 的上下文传播机制：ContextVar 隐式传播、跨线程传播（child_of）、跨服务传播（HTTP header），以及 Baggage 的使用。"
tags: [context, propagation, contextvar, baggage, cross-thread, cross-service, header]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-046
    title: "ContextVar 上下文管理"
  - id: F-cl-049
    title: "跨服务 header 传播"
  - id: F-cl-051
    title: "Baggage 传播"
---

# 上下文传播

上下文传播是 Tracing 系统的核心能力——它确保在复杂的调用链中，新创建的 Span 能正确地关联到其父 Span，形成完整的调用树。CozeLoop 支持三种传播场景：同一线程/协程内的隐式传播、跨线程传播、跨服务（跨进程）传播。

## 隐式上下文传播（同一线程/协程）

### 基于 ContextVar + 双向链表

CozeLoop 使用 Python 的 `contextvars.ContextVar`（变量名 `loop_span`）存储当前活跃的 Span 链。与传统栈结构不同，内部维护一个**双向链表**（DoublyLinkedList）：

```
ContextVar("loop_span") → DoublyLinkedList
                           ├── Node(span1) ← head
                           ├── Node(span2)
                           └── Node(span3) ← tail (当前最新 span)
```

**为什么使用双向链表而不是栈？** 栈结构要求 Span 必须按 LIFO 顺序 finish，但实际场景中父 span 可能在子 span 之前 finish（如异步场景、手动管理）。双向链表允许任意位置的节点被删除，链表自动维护相邻节点关系。

### 自动父子关系建立

在同一线程/协程中，调用 `start_span()` 时：

1. 从 ContextVar 获取双向链表
2. 取链表尾部节点作为父 span
3. 创建新 span（继承 trace_id、parent_span_id 指向父 span、继承 baggage）
4. 将新 span 追加到链表尾部
5. 更新 ContextVar

这意味着嵌套的 `start_span()` 调用自动建立父子关系，无需手动传递 span 引用：

```python
import cozeloop

# 自动创建 trace 根 span
with cozeloop.start_span("root", "main_span") as root:
    # 自动成为 root 的子 span
    with cozeloop.start_span("step1", "custom") as step1:
        step1.set_output("step1 done")
        # 自动成为 step1 的子 span（即 root 的孙 span）
        with cozeloop.start_span("detail", "custom") as detail:
            detail.set_output("detail done")
    # 自动成为 root 的子 span（与 step1 同级）
    with cozeloop.start_span("step2", "model") as step2:
        step2.set_model_provider("openai")
        step2.set_output("llm result")
```

生成的 Trace 树结构：

```
root (main_span)
├── step1 (custom)
│   └── detail (custom)
└── step2 (model)
```

### @observe 装饰器的自动传播

`@observe` 装饰器内部调用 `start_span()`，因此同样享受自动上下文传播：

```python
from cozeloop.decorator import observe

@observe(span_type="model", tags={"model_provider": "openai"})
def llm_call(prompt):
    return call_openai(prompt)

@observe(name="rag_pipeline")
def rag(question):
    docs = retrieve(question)      # 如果 retrieve 也被 @observe 装饰，自动成为子 span
    answer = llm_call(question)    # 自动成为 rag_pipeline 的子 span
    return answer
```

### ContextVar 与 asyncio

Python 的 `contextvars` 模块天然支持 asyncio：每个 Task 有独立的 context 副本，在 async/await 切换时自动保存和恢复。因此在异步代码中，隐式传播同样有效：

```python
@observe
async def async_llm_call(prompt):
    response = await async_openai.chat.completions.create(...)
    return response

@observe
async def async_pipeline():
    # await 切换时 context 自动保存/恢复，子 span 关系正确
    result = await async_llm_call("hello")
    return result
```

### 获取当前 Span

使用 `get_span_from_context()` 获取当前上下文中最新的 span：

```python
from cozeloop import get_span_from_context

@observe
def my_function():
    current_span = get_span_from_context()
    current_span.set_tags({"dynamic_key": "value"})
    current_span.set_baggage({"request_id": "abc123"})
```

如果上下文中没有 span（或客户端未初始化），返回 `NOOP_SPAN`。

## 跨线程传播

### 问题：线程不共享 ContextVar

Python 的 `threading.Thread` 创建的新线程有独立的 ContextVar 上下文，父线程中的 span 链不会自动传播到子线程。因此在新线程中直接调用 `start_span()` 会创建一个新的 trace（根 span），而不是父线程中 span 的子 span。

### 解决方案：child_of 参数

通过 `child_of` 参数显式传递 SpanContext，在新线程中创建子 span：

```python
import threading
import cozeloop

def background_task(span_context):
    """在新线程中执行任务"""
    # 使用 child_of 指定父 span context
    with cozeloop.start_span("background_task", "custom", child_of=span_context) as span:
        span.set_output("background done")

# 主线程
with cozeloop.start_span("main", "main_span") as root_span:
    root_span.set_output("main done")
    # 将 root_span 作为 SpanContext 传递给子线程
    t = threading.Thread(target=background_task, args=(root_span,))
    t.start()
    t.join()
```

**关键点**：
- `child_of` 参数接受 `SpanContext`（只需要 trace_id、span_id、baggage），而 Span 本身实现了 SpanContext 接口，因此可以直接传入 Span 对象
- 子线程中的 span 会继承 trace_id（保持同一 trace）、parent_span_id 指向传入的 span、继承 baggage
- 子线程中后续的 start_span() 调用会在该线程的 ContextVar 链表上继续嵌套

### 使用 to_header()/from_header() 跨线程

跨线程也可以使用 header 序列化方式（与跨服务一致）：

```python
def background_task(headers):
    span_context = cozeloop.get_span_from_header(headers)
    with cozeloop.start_span("background", "custom", child_of=span_context) as span:
        span.set_output("done")

with cozeloop.start_span("main", "main_span") as root:
    headers = root.to_header()
    t = threading.Thread(target=background_task, args=(headers,))
    t.start()
```

不过对同进程内的跨线程场景，直接传 Span/SpanContext 更简洁。

## 跨服务传播（HTTP Header）

### Header 格式

跨服务传播使用两个自定义 HTTP header：

**X-Cozeloop-Traceparent**：携带 trace 标识

```
X-Cozeloop-Traceparent: {version:02x}-{trace_id}-{span_id}-{flags:02x}
```

示例：
```
X-Cozeloop-Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

格式解析：
- `version`（2位十六进制）：trace 上下文版本，当前为 00
- `trace_id`（32位十六进制）：Trace ID
- `span_id`（16位十六进制）：父 Span ID
- `flags`（2位十六进制）：标志位，01=已采样

**X-Cozeloop-Tracestate**：携带 baggage（逗号分隔的 URL 编码 k=v 对）

```
X-Cozeloop-Tracestate: key1=val1,key2=val2
```

示例（URL 编码后）：
```
X-Cozeloop-Tracestate: product_id=123456,user_id=user001
```

### 发送方：注入 Header

在调用下游服务前，从当前 span 获取 header 并注入 HTTP 请求：

```python
import cozeloop
import httpx

def call_service_b(input_data):
    with cozeloop.start_span("call_service_b", "custom") as span:
        span.set_input(input_data)
        # 获取当前 span 的 header
        headers = span.to_header()
        # headers = {
        #     "X-Cozeloop-Traceparent": "00-{trace_id}-{span_id}-01",
        #     "X-Cozeloop-Tracestate": "product_id=123456,..."
        # }

        # 发起 HTTP 请求时携带这些 header
        response = httpx.post(
            "http://service-b/api/process",
            json=input_data,
            headers=headers,  # 注入 trace header
        )
        span.set_output(response.json())
        return response.json()
```

**自动注入**：SDK 内部的 HTTP 客户端（用于上报 span 和调用 Prompt API）自动通过 `header_injector` 注入当前 span 的 header，使 SDK 自身的 HTTP 调用也被纳入 trace 链。

### 接收方：提取 Header

在下游服务中，从请求 header 解析 SpanContext 并作为根 span 的父级：

```python
from cozeloop import new_client, get_span_from_header

client = new_client()

def handle_request(request):
    # 从请求 header 中提取 SpanContext
    span_context = get_span_from_header(dict(request.headers))

    # 创建服务 B 的根 span，作为服务 A span 的子 span
    with client.start_span("service_b_root", "main_span", child_of=span_context) as root:
        result = process_request(request.json())
        root.set_output(result)
        return result
```

**注意**：`get_span_from_header()` 总是返回一个 SpanContext 对象（即使 header 无效或为空）。如果 header 无效（格式错误、trace_id 不是 32 位十六进制等），返回 NoopSpan。如果 header 为空，返回空的 SpanContext（trace_id=""，span_id=""），此时 `start_span(child_of=empty_context)` 的行为取决于 SpanContext 的 trace_id 是否有效——如果无效，会创建新 trace。

### Baggage 的跨服务传播

通过 `set_baggage()` 设置的 baggage 会自动包含在 `to_header()` 的 Tracestate 中，从 header 解析时自动恢复：

```python
# 服务 A
with cozeloop.start_span("request", "main_span") as span:
    span.set_baggage({"product_id": "123456", "user_id": "user001"})
    headers = span.to_header()
    # Tracestate 包含: product_id=123456,user_id=user001
    call_service_b(headers)

# 服务 B
span_context = get_span_from_header(headers)
with client.start_span("service_b", "main_span", child_of=span_context) as root:
    # baggage 自动继承：product_id 和 user_id 可通过 root.baggage 访问
    print(root.baggage)  # {"product_id": "123456", "user_id": "user001"}

    # 在服务 B 中创建的子 span 也自动继承 baggage
    with client.start_span("sub_operation", "custom") as sub:
        print(sub.baggage)  # 同样包含 product_id 和 user_id
```

## Baggage 详解

### 什么是 Baggage

Baggage 是随调用链自动传播的键值对元数据，与普通标签的区别在于：

| 特性 | 普通标签 (tags) | Baggage |
|------|----------------|---------|
| 当前 Span 可见 | ✅ | ✅ |
| 子 Span 自动继承 | ❌ | ✅ |
| 跨线程传播 | ❌ 需手动传 | ✅ 通过 child_of |
| 跨服务传播 | ❌ | ✅ 通过 to_header/from_header |
| 用途 | 记录操作元数据 | 传播全局标识信息 |

### Baggage 使用场景

适合放入 Baggage 的信息：
- `user_id`：用户标识（可通过 `set_user_id_baggage()` 便捷设置）
- `message_id`：消息标识（`set_message_id_baggage()`）
- `thread_id`：会话/线程标识（`set_thread_id_baggage()`）
- `request_id`：请求 ID
- `product_id`：产品/租户 ID
- `environment`：环境标识（注意：有专门的 `set_deployment_env()` 方法）

不适合放入 Baggage 的信息：
- 业务数据（input/output 应使用 set_input/set_output）
- 大量数据（Baggage 通过 HTTP header 传播，大小受限）
- 敏感信息（API Key、密码等）

### Baggage 约束

- Key 不能包含特殊字符 `=` 和 `,`（这两个字符用于序列化格式）
- Value 会经过 URL 编码，可以包含特殊字符
- Key 和 Value 都受标签大小限制（默认 1024 字节）
- Baggage 项数量建议控制在合理范围（通常 <10 项），避免 HTTP header 过大

### 便捷方法

SDK 为三个常用的 baggage 字段提供了便捷方法，它们同时设置标签和 baggage：

```python
span.set_user_id_baggage("user_123")      # 标签 user_id + baggage user_id
span.set_message_id_baggage("msg_456")    # 标签 message_id + baggage message_id
span.set_thread_id_baggage("thread_789")  # 标签 thread_id + baggage thread_id
```

对应地，也有只设置标签不传播的方法：

```python
span.set_user_id("user_123")       # 仅标签
span.set_message_id("msg_456")     # 仅标签
span.set_thread_id("thread_789")   # 仅标签
```

## start_new_trace 参数

默认情况下，`start_span()` 会自动从 context 中查找父 span。使用 `start_new_trace=True` 可以强制创建新 trace：

```python
with cozeloop.start_span("outer", "main_span") as outer:
    # outer 是 trace A 的根 span

    with cozeloop.start_span("independent", "custom", start_new_trace=True) as ind:
        # ind 是一个全新 trace（trace B）的根 span，不是 outer 的子 span
        pass
```

这在某些场景下有用，如后台任务不想与前台请求关联到同一 trace。
