---
type: concept
title: "配置、批量上报与性能"
description: "理解 CozeLoop 的批量上报引擎、队列配置、数据截断与超大数据上报策略、客户端生命周期管理，以及生产环境性能优化。"
tags: [configuration, batching, queue, performance, upload, lifecycle, optimization]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-053
    title: "TraceProvider 与批量上报"
  - id: F-cl-066
    title: "BatchSpanProcessor 队列管理"
  - id: F-cl-068
    title: "超大数据上报"
---

# 配置、批量上报与性能

本文档深入讲解 CozeLoop SDK 的批量上报机制、队列配置、数据截断策略、超大数据处理、客户端生命周期管理，以及生产环境的性能优化建议。

## 批量上报引擎

### 为什么需要批量上报

如果每个 Span 完成后立即发送 HTTP 请求，会导致：
- 大量 HTTP 请求开销（每个请求有 TCP 握手、TLS 协商等成本）
- 阻塞业务线程
- 高并发场景下可能压垮接收端

CozeLoop 采用**异步批量上报**模式：Span 完成后进入内存队列，后台 daemon 线程按批次聚合后发送。这显著降低了请求数量和业务线程的开销。

### 四队列架构

`BatchSpanProcessor` 维护四个独立队列，每个队列由一个专门的后台 daemon 线程消费：

```
┌──────────────────────────────────────────────────────┐
│                    你的代码                            │
│              span.finish()                            │
│                  │                                    │
│                  ▼                                    │
│           ┌──────────────┐                           │
│           │  Span 主队列  │ (max=1024, batch=100)    │
│           │    "span"    │ interval=1s, limit=4MB   │
│           └──────┬───────┘                           │
│                  │ 上报失败                           │
│                  ▼                                    │
│           ┌──────────────┐                           │
│           │ Span 重试队列 │ (max=512, batch=50)      │
│           │  "span_retry"│ interval=1s, limit=4MB   │
│           └──────┬───────┘                           │
│                  │ 上报成功（含文件数据）              │
│                  ▼                                    │
│           ┌──────────────┐                           │
│           │  File 主队列  │ (max=512, batch=1)      │
│           │   "file"     │ interval=5s, limit=100MB │
│           └──────┬───────┘                           │
│                  │ 上传失败                           │
│                  ▼                                    │
│           ┌──────────────┐                           │
│           │ File 重试队列 │ (max=512, batch=1)      │
│           │ "file_retry" │ interval=5s, limit=100MB │
│           └──────┬───────┘                           │
│                  │                                    │
└──────────────────┼────────────────────────────────────┘
                   ▼
           HTTP → CozeLoop API
           span: POST /v1/loop/traces/ingest
           file: POST /v1/loop/files/upload
```

### 队列参数详解

**Span 主队列**：
- 最大长度：1024（超过后新 span 被丢弃并记录日志）
- 触发条件：队列满 100 条 或 等待 1000ms（1秒），以先到者为准
- 单批大小限制：4MB（超过则拆批）
- 上报端点：`/v1/loop/traces/ingest`

**Span 重试队列**：
- 最大长度：512
- 触发条件：50 条 或 1000ms
- 重试策略：主队列上报失败的 span 进入此队列，二次上报失败则丢弃
- 单批大小限制：4MB

**File 主队列**：
- 最大长度：512
- 触发条件：1 条（每个文件独立上传）或 5000ms（5秒）
- 单批大小限制：100MB
- 上报端点：`/v1/loop/files/upload`（multipart/form-data）
- 用途：上传超大数据文本和多模态文件（base64 图片/文件）

**File 重试队列**：
- 最大长度：512
- 触发条件：1 条 或 5000ms
- 重试策略：同 Span 重试逻辑

### 队列工作线程

每个队列由一个 daemon 后台线程（`QueueWorkerThread`，继承自 `threading.Thread`）消费：

- 线程是 daemon 模式，主程序退出时自动终止（但 atexit 钩子会先 flush）
- 工作线程循环：等待事件信号或超时 → 从队列提取 batch → 调用 exporter 上报 → 处理失败重试
- 队列满时采用 **drop 策略**（而非阻塞）：新 span 直接丢弃并记录 `queue_full_drop_span` 指标日志

## 数据截断与超大数据上报

### 默认截断行为

为防止上报数据过大，SDK 对标签值进行截断：

| 数据类型 | 默认最大字节数 | 截断行为 |
|---------|-------------|---------|
| 普通标签值 | 1024 字节 | 截断到 1000 字符，记录截断 key |
| 标签 key | 1024 字节 | 截断 |
| input/output 值 | 1MB（1048576 字节） | 截断到 1000 字符，记录截断 key |
| 单 Span 标签数 | 50 个 | 超出的标签被忽略 |

截断时，被截断的 key 会记录在 `cut_off` 系统标签（list 类型）中，方便排查。

### 超大数据上报模式

当 input/output 数据超过 1MB 时，开启 `ultra_large_report=True` 可以避免截断：

```python
import cozeloop

client = cozeloop.new_client(
    ultra_large_report=True,  # 开启超大数据上报
    api_token="your_token",
    workspace_id="your_workspace",
)
```

开启后的行为：
- 文本数据：截断到 1000 字符保留在 span 标签中，完整内容通过文件上传接口单独上传
- 上传成功后，span 的 input/output 值替换为对象存储 key（格式为 ObjectStorage JSON）
- 多模态图片/文件（ModelImageURL/ModelFileURL 含 base64）：base64 数据自动提取为文件上传，URL 替换为对象存储 key
- 对象存储信息记录在 `ObjectStorage` 字段，包含 key、bucket、attachments 等信息

### 多模态数据处理

当使用 `ModelInput`/`ModelOutput` 数据模型时：

```python
from cozeloop.spec.tracespec import (
    ModelInput, ModelMessage, ModelMessagePart,
    ModelMessagePartType, ModelImageURL, ModelFileURL,
)

input_data = ModelInput(messages=[ModelMessage(role="user", parts=[
    ModelMessagePart(
        type=ModelMessagePartType.IMAGE,
        image_url=ModelImageURL(
            name="diagram.png",
            url="data:image/png;base64,iVBORw0KGgo...",  # base64 图片
        ),
    ),
    ModelMessagePart(
        type=ModelMessagePartType.FILE,
        file_url=ModelFileURL(
            name="data.csv",
            url="data:text/csv;base64,SGVsbG8s...",  # base64 文件
        ),
    ),
    ModelMessagePart(
        type=ModelMessagePartType.TEXT,
        text="分析这些文件",
    ),
])])
```

多模态处理规则：
- base64 编码的图片/文件（`data:` URL）→ 提取二进制数据上传文件
- HTTP URL 图片/文件（`http://` 或 `https://`）→ 保留原始 URL，不上传
- 纯文本 part → 正常记录

### 自定义截断阈值

通过 `TagTruncateConf` 自定义截断限制：

```python
from cozeloop.internal.trace.model.model import TagTruncateConf

tconf = TagTruncateConf(
    normal_field_max_byte=2048,              # 普通标签 2KB
    input_output_field_max_byte=5*1024*1024,  # input/output 5MB
)

client = cozeloop.new_client(tag_truncate_conf=tconf)
```

## 客户端生命周期管理

### 初始化

```python
import cozeloop

# 最简方式：使用环境变量
client = cozeloop.new_client()

# 显式传参
client = cozeloop.new_client(
    api_token="your_pat_token",
    workspace_id="your_workspace_id",
    api_base_url="https://api.coze.cn",
    ultra_large_report=False,
)
```

`new_client()` 行为：
- 内部使用 MD5 缓存，相同参数返回同一实例
- 创建 _LoopClient 实例（TraceClient + PromptClient）
- 初始化 HTTP 客户端、认证、TraceProvider（含 BatchSpanProcessor）、PromptProvider
- 注册 atexit 钩子（程序退出时自动 flush + close）
- 首个客户端创建后，模块级函数（`cozeloop.start_span()`、`cozeloop.flush()` 等）自动使用此客户端

### Flush（强制刷新）

在关键节点调用 `flush()` 确保所有 pending span 被上报：

```python
# 模块级
cozeloop.flush()

# 客户端级
client.flush()
```

`flush()` 行为：
- 阻塞等待所有队列中的 span/file 被处理并上报
- 等待时间受网络状况影响（span 上报超时 3s，文件上传超时 30s）
- 建议在程序退出前、请求处理完毕后、或关键操作完成后调用

### Close（关闭）

```python
# 模块级
cozeloop.close()

# 客户端级
client.close()
```

`close()` 行为：
1. 设置停止事件（stop_event）
2. 唤醒所有队列工作线程
3. 排空队列中的剩余 span/file 并上报
4. 等待工作线程结束（join）
5. 将全局客户端替换为 NoopClient（所有后续操作无副作用）
6. 移除 atexit 钩子

程序正常退出时 atexit 钩子自动调用 close。如果程序被强制杀死（SIGKILL），atexit 不会执行，内存中未上报的 span 会丢失。

### 客户端缓存

`new_client()` 基于参数 MD5 缓存客户端实例：

```python
client1 = cozeloop.new_client(api_token="t1", workspace_id="w1")
client2 = cozeloop.new_client(api_token="t1", workspace_id="w1")
# client1 is client2 → True（同一实例）

client3 = cozeloop.new_client(api_token="t2", workspace_id="w1")
# client3 is client1 → False（不同参数，新实例）
```

### Noop 降级

以下情况 SDK 进入 Noop 模式（所有 tracing 操作为空操作，不影响业务）：
- 客户端创建失败（缺少认证信息、参数无效）
- 客户端已关闭
- Span 创建时上下文无效
- `get_span_from_context()` 在无 active span 时调用

## 超时配置

| 操作 | 默认超时 | 说明 |
|------|---------|------|
| Span 上报（POST /traces/ingest） | 3 秒 | 普通批量上报 |
| 文件上传（POST /files/upload） | 30 秒 | 大文件上传需要更长超时 |
| execute_prompt（PTaaS） | 600 秒（10分钟） | LLM 推理耗时较长 |

可以通过自定义 `httpx.Client` 修改超时：

```python
import httpx
import cozeloop

custom_http = httpx.Client(
    timeout=httpx.Timeout(5.0, connect=3.0),  # 5秒读超时，3秒连接超时
)
client = cozeloop.new_client(
    api_token="token",
    workspace_id="ws",
    http_client=custom_http,
)
```

## 自定义队列配置

通过 `QueueConf` 调整队列参数：

```python
from cozeloop.internal.trace.model.model import QueueConf

qconf = QueueConf(
    span_queue_length=2048,              # span 队列长度，默认 1024
    span_max_export_batch_length=200,    # 单批最大 span 数，默认 100
)
client = cozeloop.new_client(trace_queue_conf=qconf)
```

注意：过大的队列会增加内存占用，过大的批量会增加单次请求失败导致的数据丢失量。建议根据实际 QPS 和网络状况调整。

## 生产环境性能优化建议

### 1. 及时关闭客户端

在长驻进程中（Web 服务、Worker），客户端应在进程启动时创建一次，在进程退出时关闭。不要在每个请求中创建/关闭客户端：

```python
# ✅ 正确：应用启动时初始化
client = cozeloop.new_client()

# ❌ 错误：每个请求创建新客户端
@app.post("/chat")
def chat(request):
    client = cozeloop.new_client()  # 重复创建开销大
    # ...
    client.close()
```

### 2. 合理使用 baggage

Baggage 会随 header 传播到所有下游服务，避免放入大量数据：

```python
# ✅ 正确：只放必要的标识
span.set_user_id_baggage("user_123")
span.set_thread_id_baggage("thread_456")

# ❌ 错误：放入业务数据
span.set_baggage({"large_data": huge_json_string})
```

### 3. 避免在高频路径上设置过多标签

每个标签都有类型校验、截断处理开销。对高频操作（如循环内），只设置关键标签：

```python
# ✅ 简洁
for item in items:
    with cozeloop.start_span("process_item", "tool") as span:
        span.set_input(item.id)
        process(item)

# ❌ 过度设置
for item in items:
    with cozeloop.start_span("process_item", "tool") as span:
        span.set_input(item.to_dict())  # 大对象序列化开销
        span.set_tags({"index": i, "count": len(items), ...})  # 过多标签
```

### 4. 流式调用传 stream_options

使用 OpenAI 流式 API 时，设置 `stream_options={"include_usage": True}`，否则最后一个 chunk 不包含 usage 信息，SDK 无法自动统计 token：

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    stream=True,
    stream_options={"include_usage": True},  # 关键！
)
```

### 5. 大文本考虑 ultra_large_report

对 input/output 超过 1MB 的场景（如长文档处理、大对话历史），开启 `ultra_large_report=True` 避免数据截断：

```python
client = cozeloop.new_client(ultra_large_report=True)
```

注意：这会增加额外的文件上传请求，对延迟敏感的场景需评估。

### 6. 异步场景使用异步 API

在 asyncio 应用中，使用异步版本的 API：

```python
# 使用 AsyncOpenAI wrapper
from openai import AsyncOpenAI
client = openai_wrapper(AsyncOpenAI(...))

# 异步 Prompt API
result = await client.aexecute_prompt(...)
```

### 7. 进程退出前 flush

在脚本或批处理任务结束前调用 flush 或 close，确保数据上报：

```python
def main():
    cozeloop.new_client()
    run_pipeline()
    cozeloop.flush()  # 确保数据上报
    cozeloop.close()

if __name__ == "__main__":
    main()
```

## 完成事件监控

注册 `trace_finish_event_processor` 回调监控上报状态：

```python
from cozeloop.internal.trace.model.model import FinishEventInfo

def event_monitor(info: FinishEventInfo):
    """
    event_type 值：
    - "queue_manager.span_entry.rate"    span 入队
    - "queue_manager.file_entry.rate"    file 入队
    - "exporter.span_flush.rate"         span 上报完成
    - "exporter.file_flush.rate"         file 上传完成
    """
    if info.is_event_fail:
        # 上报失败，记录监控指标或告警
        log.warning(
            f"上报失败: type={info.event_type}, "
            f"count={info.item_num}, msg={info.detail_msg}"
        )

client = cozeloop.new_client(trace_finish_event_processor=event_monitor)
```

这可以用于监控上报成功率、队列丢弃率、上报延迟等指标。
