---
type: example
title: "自定义 Span 追踪与高级场景"
description: "掌握自定义 Span 创建、父子嵌套、跨线程传播、跨服务 header 传播、Baggage 使用、异常处理、多模态数据上报等高级 Tracing 场景。"
tags: [custom-span, parent-child, cross-thread, cross-service, baggage, error-handling, multimodal, advanced]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: examples/parent_child
    title: "examples/trace/parent_child.py"
  - id: examples/transfer
    title: "examples/trace/transfer_between_services.py"
  - id: examples/multi_modality
    title: "examples/trace/multi_modality.py"
  - id: F-cl-033
    title: "Span 接口"
---

# 自定义 Span 追踪与高级场景

本示例覆盖自定义 Span 创建的各种高级场景：父子 Span 嵌套、跨线程传播、跨服务 HTTP header 传播、Baggage 使用、异常处理、多模态数据上报等。

## 场景 1：父子 Span 嵌套

在同一线程中，`start_span()` 自动从 ContextVar 获取当前活跃 Span 作为父 Span，无需手动传递：

```python
import logging
import time
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

# 根 Span
with client.start_span("pipeline", "main_span") as root:
    root.set_input("用户请求：帮我总结这篇文章")
    root.set_user_id_baggage("user_001")

    # 步骤 1：预处理（自动成为 root 的子 Span）
    with client.start_span("preprocess", "custom") as pre:
        pre.set_input("原始文本...")
        time.sleep(0.1)
        pre.set_output("清洗后的文本...")

    # 步骤 2：检索（自动成为 root 的子 Span）
    with client.start_span("retrieve", "retriever") as ret:
        ret.set_input("查询：文章要点")
        time.sleep(0.2)
        ret.set_output(["相关文档1", "相关文档2", "相关文档3"])

    # 步骤 3：LLM 调用（自动成为 root 的子 Span）
    with client.start_span("llm_generate", "model") as llm:
        llm.set_model_provider("openai")
        llm.set_model_name("gpt-4")
        llm.set_input("基于文档生成摘要...")
        time.sleep(1)
        llm.set_start_time_first_resp(int((time.time() - 0.5) * 1000000))
        llm.set_input_tokens(500)
        llm.set_output_tokens(200)
        llm.set_output("这是文章的摘要...")

    # 步骤 4：后处理（自动成为 root 的子 Span）
    with client.start_span("postprocess", "custom") as post:
        post.set_input("原始摘要...")
        time.sleep(0.1)
        post.set_output("格式化后的最终摘要")

    root.set_output("最终摘要...")

client.flush()
```

生成的 Trace 树：

```
pipeline (main_span)
├── preprocess (custom)
├── retrieve (retriever)
├── llm_generate (model)
└── postprocess (custom)
```

## 场景 2：跨线程 Span 传播

Python 的 `threading.Thread` 创建的新线程有独立的 ContextVar，需要通过 `child_of` 参数显式传递父 Span：

```python
import threading
import time
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

def background_render(span_context):
    """在后台线程中执行渲染任务"""
    # 使用 child_of 指定父 Span Context
    with client.start_span("background_render", "custom", child_of=span_context) as span:
        span.set_input("渲染任务参数")
        time.sleep(2)  # 模拟耗时渲染
        span.set_output("渲染结果")

def main_pipeline():
    root = client.start_span("main_pipeline", "main_span")
    root.set_input("用户请求")
    root.set_baggage({"request_id": "req-123"})

    # 主流程
    with client.start_span("main_process", "custom") as proc:
        proc.set_input("处理中")
        time.sleep(0.5)
        proc.set_output("处理完成")

    # 启动后台线程——将 root span 作为 SpanContext 传入
    # Span 对象实现了 SpanContext 接口，可以直接传入
    t = threading.Thread(target=background_render, args=(root,))
    t.start()

    # 主线程中的 root span 可以先 finish
    # 后台线程的 span 仍然是 root 的子 span（通过 trace_id + parent_span_id 关联）
    root.set_output("主流程完成，后台渲染中")
    root.finish()

    # 等待后台线程完成
    t.join()
    client.flush()

main_pipeline()
client.close()
```

**关键点**：
- `child_of` 接受 `SpanContext` 对象（只需 trace_id、span_id、baggage）
- Span 对象本身实现了 `SpanContext` 接口，可以直接传入
- 子线程中的 span 继承 trace_id 和 baggage
- 父 span 不必等待子 span finish——trace 在后端通过 ID 关联

## 场景 3：跨服务 HTTP Header 传播

在微服务架构中，使用 `to_header()` 和 `get_span_from_header()` 在服务间传播 Trace 上下文。

### 服务 A（调用方）

```python
import httpx
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

def call_service_b(input_data):
    with client.start_span("call_service_b", "custom") as span:
        span.set_input(input_data)

        # 从当前 span 获取 propagation headers
        headers = span.to_header()
        # headers 包含：
        # - X-Cozeloop-Traceparent: 00-{trace_id}-{span_id}-01
        # - X-Cozeloop-Tracestate: key1=val1,key2=val2 (URL 编码的 baggage)

        # 发起 HTTP 请求时注入 header
        response = httpx.post(
            "http://service-b:8080/api/process",
            json={"data": input_data},
            headers=headers,
            timeout=10,
        )
        span.set_output(response.json())
        return response.json()

# 模拟调用
with client.start_span("service_a_handler", "main_span") as root:
    root.set_baggage({"product_id": "prod-001"})
    result = call_service_b("需要处理的数据")
    root.set_output(result)

client.flush()
client.close()
```

### 服务 B（被调用方）

```python
from flask import Flask, request, jsonify
from cozeloop import new_client, get_span_from_header
from cozeloop.logger import set_log_level
import logging

app = Flask(__name__)
set_log_level(logging.INFO)
client = new_client()

@app.route("/api/process", methods=["POST"])
def process():
    # 从请求 header 中提取 SpanContext
    span_context = get_span_from_header(dict(request.headers))

    # 创建服务 B 的根 span，作为服务 A span 的子 span
    with client.start_span("service_b_handler", "main_span", child_of=span_context) as root:
        data = request.json
        root.set_input(data)

        # 子 span 自动继承 baggage（如 product_id）
        print("Baggage:", root.baggage)  # {"product_id": "prod-001"}

        # 业务处理
        with client.start_span("business_logic", "custom") as biz:
            biz.set_input(data)
            result = {"status": "processed", "result": "done"}
            biz.set_output(result)

        root.set_output(result)
        client.flush()
        return jsonify(result)

if __name__ == "__main__":
    app.run(port=8080)
```

### Header 格式说明

**X-Cozeloop-Traceparent**：
```
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
│  │                                │                │
│  └── trace_id (32 hex)            └── span_id      └── flags (01=sampled)
└── version (00)
```

**X-Cozeloop-Tracestate**（Baggage）：
```
product_id=prod-001,user_id=user001
```
- 逗号分隔的 `key=value` 对
- value 经过 URL 编码（支持特殊字符）
- 自动传递给所有子 span

## 场景 4：Baggage 使用模式

Baggage 适合传播全局标识信息，会自动传递给所有子 span（包括跨线程和跨服务）：

```python
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

with client.start_span("request_handler", "main_span") as root:
    # 设置全局传播的 baggage
    root.set_user_id_baggage("user_12345")       # 用户 ID
    root.set_message_id_baggage("msg_67890")    # 消息 ID
    root.set_thread_id_baggage("thread_abc")    # 会话 ID
    root.set_baggage({
        "request_id": "req-xyz-001",
        "tenant_id": "tenant_999",
    })

    # baggage 自动传递给子 span
    with client.start_span("auth_check", "custom") as auth:
        print("Auth baggage:", auth.baggage)
        # {"user_id": "user_12345", "message_id": "msg_67890",
        #  "thread_id": "thread_abc", "request_id": "req-xyz-001",
        #  "tenant_id": "tenant_999"}
        auth.set_output("authenticated")

    with client.start_span("business_logic", "custom") as biz:
        # 在深层嵌套中也能访问 baggage
        print("Business baggage:", biz.baggage["user_id"])  # "user_12345"
        biz.set_output("done")

client.flush()
client.close()
```

### Baggage vs Tags 选择指南

| 场景 | 使用 Baggage | 使用 Tags |
|------|-------------|-----------|
| user_id/request_id 等全局标识 | ✅ | ❌ |
| 当前操作的特定参数 | ❌ | ✅ |
| 需要跨服务传递 | ✅ | ❌ |
| 需要跨线程传递 | ✅ | ❌（通过 child_of 隐式传递 baggage） |
| 只在当前 span 使用 | ❌ | ✅ |
| LLM 模型参数（temperature 等） | ❌ | ✅（call_options 或 set_tags） |

## 场景 5：异常处理

正确记录异常信息是 Tracing 的重要用途：

```python
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

ERR_CODE_LLM_TIMEOUT = 50001
ERR_CODE_INVALID_INPUT = 40001

def llm_call_with_retry(prompt, max_retries=3):
    span = client.start_span("llm_call", "model")
    try:
        span.set_model_provider("openai")
        span.set_model_name("gpt-4")
        span.set_input(prompt)

        for attempt in range(max_retries):
            try:
                result = call_openai_api(prompt)
                span.set_output(result)
                span.set_status_code(0)  # 显式设置成功
                return result
            except TimeoutError:
                if attempt == max_retries - 1:
                    raise
                continue
    except TimeoutError as e:
        span.set_error(str(e))           # 设置 error 标签
        span.set_status_code(ERR_CODE_LLM_TIMEOUT)  # 自定义错误码
        raise  # 重新抛出，不吞异常
    except ValueError as e:
        span.set_error(str(e))
        span.set_status_code(ERR_CODE_INVALID_INPUT)
        raise
    except Exception as e:
        span.set_error(e)  # 直接传异常对象
        # 未设置 status_code 时默认 -1
        raise
    finally:
        span.finish()

def call_openai_api(prompt):
    raise TimeoutError("OpenAI API timeout")

try:
    with client.start_span("request", "main_span") as root:
        root.set_input("test prompt")
        llm_call_with_retry("test prompt")
except Exception as e:
    print(f"请求失败: {e}")

client.flush()
client.close()
```

**最佳实践**：
- 始终使用 `try/except/finally` 模式，确保 `span.finish()` 在 finally 中调用
- 使用 `with` 语句更简洁（自动 finish + 自动记录异常）
- `set_error()` 会自动设置 status_code=-1（如果之前未设置非零值）
- 使用自定义错误码便于在平台上按错误类型筛选

## 场景 6：多模态数据上报

使用 `ModelInput`/`ModelOutput` 标准数据模型上报多模态内容（图片、文件），SDK 自动处理 base64 数据的文件上传：

```python
import logging
import base64
from cozeloop import new_client
from cozeloop.spec.tracespec import (
    ModelInput, ModelMessage, ModelMessagePart,
    ModelMessagePartType, ModelImageURL, ModelOutput,
    ModelChoice,
)
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
# 开启 ultra_large_report 以支持大文件/多模态上传
client = new_client(ultra_large_report=True)

with client.start_span("multimodal_chat", "model") as span:
    span.set_model_provider("openai")
    span.set_model_name("gpt-4-vision-preview")

    # 构建多模态输入
    with open("photo.png", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    input_data = ModelInput(messages=[
        ModelMessage(role="user", parts=[
            # 文本部分
            ModelMessagePart(
                type=ModelMessagePartType.TEXT,
                text="请描述这张图片",
            ),
            # 图片部分（base64）
            ModelMessagePart(
                type=ModelMessagePartType.IMAGE,
                image_url=ModelImageURL(
                    name="photo.png",
                    url=f"data:image/png;base64,{image_base64}",
                ),
            ),
        ]),
    ])
    span.set_input(input_data)

    # 模拟模型输出
    output_data = ModelOutput(choices=[
        ModelChoice(
            index=0,
            finish_reason="stop",
            message=ModelMessage(
                role="assistant",
                content="这是一张显示...的图片。",
            ),
        ),
    ])
    span.set_output(output_data)
    span.set_input_tokens(200)
    span.set_output_tokens(150)

client.flush()
client.close()
```

**自动处理逻辑**：
- base64 编码的图片/文件（`data:` URL）→ 提取二进制数据，通过文件上传接口上传
- HTTP URL（`http://`/`https://`）→ 保留原始 URL，不上传
- 文本 part → 正常记录
- 上传成功后，input/output 中的对应位置替换为对象存储 key

## 场景 7：动态标签与条件追踪

运行时动态设置标签、根据条件丢弃 Span：

```python
import logging
from cozeloop import new_client, get_span_from_context
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

def process_item(item):
    with client.start_span("process_item", "tool") as span:
        span.set_input({"item_id": item["id"]})

        # 根据条件决定是否上报
        if item.get("skip_tracing"):
            span.discard()  # 丢弃此 span，不上报
            return process(item)

        # 动态设置标签
        span.set_tags({
            "item_type": item["type"],
            "item_priority": item.get("priority", 0),
        })

        result = process(item)
        span.set_output(result)
        return result

def process(item):
    return {"processed": True, "item_id": item["id"]}

items = [
    {"id": 1, "type": "text", "priority": 1},
    {"id": 2, "type": "image", "priority": 2},
    {"id": 3, "type": "skip", "skip_tracing": True},  # 这个不上报
    {"id": 4, "type": "text", "priority": 0},
]

with client.start_span("batch_process", "main_span") as root:
    for item in items:
        process_item(item)

client.flush()
client.close()
```

## 场景 8：强制创建新 Trace

使用 `start_new_trace=True` 在已有上下文中创建独立的 Trace（不与当前 trace 关联）：

```python
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

set_log_level(logging.INFO)
client = new_client()

with client.start_span("main_request", "main_span") as main:
    main.set_input("主请求")

    # 这是主 trace 的子 span
    with client.start_span("normal_child", "custom") as child:
        child.set_output("正常的子 span")

    # 这是一个独立的新 trace（不是 main 的子 span）
    with client.start_span("background_metric", "custom", start_new_trace=True) as metric:
        metric.set_input("性能指标采集")
        metric.set_output("指标已记录")

client.flush()
client.close()
```

## 场景 9：get_span_from_context 获取当前 Span

在函数内部获取当前活跃 span 以动态设置标签：

```python
from cozeloop import get_span_from_context
from cozeloop.decorator import observe

@observe(span_type="custom")
def business_function(data):
    # 获取 @observe 创建的 span
    current_span = get_span_from_context()

    # 动态添加标签
    current_span.set_tags({
        "data_length": len(data),
        "processing_mode": "fast",
    })

    if len(data) > 1000:
        current_span.set_tags({"large_input": True})

    result = do_work(data)

    # 动态设置 baggage
    current_span.set_baggage({"data_size_category": "large" if len(data) > 1000 else "small"})

    return result
```

如果上下文中没有 span（未在任何 start_span 或 @observe 内调用），`get_span_from_context()` 返回 NoopSpan，所有操作无副作用。

## 下一步

- 学习 [上下文传播](../concepts/03-context-propagation.md)深入理解传播机制
- 查看 [Tracing API 参考](../references/tracing-api.md)了解完整 Span 接口
- 阅读 [配置与批量上报](../concepts/04-configuration-batching.md)了解性能调优
