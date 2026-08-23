---
type: example
title: "重试与管道示例"
description: "max_retries/throws 配置、pipeline 组合、Results 中间件获取结果的完整代码与流程分析"
tags: [dramatiq, example, retry, pipeline, results, group]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/built-in-middleware.md, ../references/error-hierarchy.md]
  facts: [F-022, F-071, F-072, F-073, F-083, F-085, F-086, F-088, F-089, F-090, F-091, F-095]
---

# 重试与管道示例

## 重试配置

```python
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries

broker = RedisBroker()
broker.add_middleware(Retries(max_retries=5, min_backoff=1000, max_backoff=30000))
dramatiq.set_broker(broker)

@dramatiq.actor(max_retries=3, min_backoff=2000)
def flaky_task(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.status_code

@dramatiq.actor(throws=(ValueError,))
def validation_task(data):
    if not data.get("valid"):
        raise ValueError("Invalid data")  # 不会重试，直接 nack
    return process(data)
```

### 重试流程

1. `flaky_task` 第一次执行抛出 `requests.ConnectionError`
2. WorkerThread.process_message 捕获异常，塞入 message._exception
3. `emit_after("process_message", message, exception=e)`
4. Retries.after_process_message（逆序第一个执行）：
   - 异常不匹配 throws（未设置）
   - `retries = message.options.setdefault("retries", 0)` → 0
   - `message.options["retries"] = 1`
   - `message.options["traceback"] = traceback.format_exc(limit=30)`
   - `retries(1) < max_retries(3)` → 需要重试
   - `compute_backoff(1, factor=2000, max_backoff=30000)` → 约 4000ms（含 jitter）
   - `broker.enqueue(message, delay=4000)` 重新入队
5. 消息被路由到 `.DQ` 延迟队列，设置 `eta = current_millis() + 4000`
6. ConsumerThread.handle_message 发现 eta，放入内存 delay_queue
7. handle_delayed_messages 等待 eta 到期后，重新 enqueue 到主队列
8. 消息再次被消费，`message.options["retries"]` 为 1
9. 若连续失败 3 次（retries >= max_retries），`message.fail()` → nack → DLQ

### throws 行为

`validation_task` 抛出 `ValueError` 时：
- Retries 检查 `isinstance(exception, throws)` 为 True
- 记录 info 日志 "Aborting message"
- `message.fail()` → 不重试，直接 nack

### 使用 Retry 异常

```python
@dramatiq.actor(max_retries=10)
def conditional_task():
    if should_retry_later():
        raise dramatiq.Retry("Try again later", delay=5000)  # 5秒后重试
```

`Retry` 异常：
- 不被记录为 error（WorkerThread 中 isinstance(e, Retry) 跳过 error 日志）
- 若指定 `delay`，Retries 使用该延迟而非计算指数退避

## Pipeline 管道

```python
import dramatiq
from dramatiq.brokers.stub import StubBroker

broker = StubBroker()
dramatiq.set_broker(broker)

@dramatiq.actor
def fetch(url):
    response = requests.get(url)
    return response.text

@dramatiq.actor
def parse(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string

@dramatiq.actor
def store(title):
    db.save(title)
    return title

# 构造管道：fetch → parse → store
pipe = fetch.message("https://example.com") | parse.message() | store.message()
pipe.run()
```

### Pipeline 构造过程

1. `fetch.message("https://example.com")` 创建 Message(args=("https://example.com",))
2. `| parse.message()` 调用 `Message.__or__` → `pipeline([msg1, msg2])`
3. `| store.message()` 调用 `pipeline.__or__` → `pipeline([msg1, msg2, msg3])`
4. pipeline 构造函数中，对相邻消息对设置：
   ```python
   msg1.options["pipe_target"] = msg2.asdict()
   msg2.options["pipe_target"] = msg3.asdict()
   ```
5. `pipe.run()` 只 enqueue 第一个消息（msg1）

### Pipeline 执行流程

1. Worker 执行 `fetch("https://example.com")`，返回 HTML 字符串
2. Pipelines.after_process_message（在 Retries 之后执行）：
   - 读取 `message.options["pipe_target"]`（msg2 的 dict）
   - `Message(**message_data)` 反序列化为 msg2
   - `pipe_ignore` 非 True，将 result 追加到 args：`msg2.args = (html,)`
   - `broker.enqueue(msg2)`
3. Worker 执行 `parse(html)`，返回 title 字符串
4. Pipelines 将 result 追加到 msg3.args：`msg3.args = (title,)`
5. Worker 执行 `store(title)`，无 pipe_target，管道结束

### pipe_ignore

```python
@dramatiq.actor(pipe_ignore=True)
def log_result(result):
    logger.info(result)
    # 不将 result 传递给下游
```

## Results 结果获取

```python
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

result_backend = RedisBackend()
broker.add_middleware(Results(backend=result_backend, result_ttl=3600000))

@dramatiq.actor(store_results=True)
def expensive_calculation(n):
    return n * n

# 发送并获取结果
message = expensive_calculation.send(42)

# 非阻塞（结果未就绪则抛 ResultMissing）
try:
    result = message.get_result(backend=result_backend, block=False)
except ResultMissing:
    print("Not ready yet")

# 阻塞等待（最多 10 秒）
result = message.get_result(backend=result_backend, block=True, timeout=10000)
print(result)  # 1764
```

### 结果存储流程

1. actor 执行成功，返回值 `1764`
2. Results.after_process_message（在 Retries/Pipelines/Callbacks 之后执行）：
   - 查找 `store_results`：message.options → actor.options → middleware 默认
   - `store_results=True` 且 exception is None
   - `backend.store_result(message, 1764, result_ttl=3600000)`
3. RedisBackend._store：
   - key = MD5(`dramatiq-results:default:expensive_calculation:{message_id}`)
   - pipeline: DELETE key → LPUSH key encoded_result → PEXPIRE key 3600000
4. `message.get_result(block=True)`：
   - BRPOPLPUSH key key timeout（阻塞等待，弹出再推回）
   - unwrap_result 检测无 `__t` 标记，直接返回 1764

### 失败结果

```python
@dramatiq.actor(store_results=True)
def failing_task():
    raise RuntimeError("boom")

message = failing_task.send()
try:
    message.get_result(backend=result_backend, block=True, timeout=5000)
except ResultFailure as e:
    print(e)  # "actor raised RuntimeError: boom"
```

Results.after_nack 调用 `backend.store_exception`，存储 `{"__t": "dramatiq.results.Result", "exn": {"type": "RuntimeError", "msg": "boom"}}`。get_result 时 unwrap_result 检测到标记，抛出 ResultFailure。

## group 并行组合

```python
from dramatiq import group

# 并行执行多个任务
g = group([
    fetch.message(f"https://example.com/page/{i}")
    for i in range(10)
])
g.run()

# 等待全部完成
g.wait(timeout=60000)

# 获取所有结果
results = list(g.get_results(block=True, timeout=60000))
```

group 并行 enqueue 所有子消息，通过 Results 中间件查询每个消息的结果来判断完成状态。`add_completion_callback` 可注册所有子任务完成后的回调 actor（依赖 GroupCallbacks 中间件和 Barrier 速率限制器）。
