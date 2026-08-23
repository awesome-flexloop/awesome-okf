---
type: reference
title: "内置中间件详解"
description: "AgeLimit/TimeLimit/ShutdownNotifications/Callbacks/Pipelines/Retries 的参数、actor_options 与钩子逻辑"
tags: [dramatiq, reference, middleware, retries, pipelines, callbacks]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/middleware.py"
    facts: [F-066]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/__init__.py"
    facts: [F-067]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/age_limit.py"
    facts: [F-068]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/time_limit.py"
    facts: [F-069, F-074]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/shutdown.py"
    facts: [F-070]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/callbacks.py"
    facts: [F-072]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/pipelines.py"
    facts: [F-073]
  - path: "external/libs/remote/dramatiq/dramatiq/middleware/retries.py"
    facts: [F-071]
---

# 内置中间件详解

## AgeLimit

**文件**：`middleware/age_limit.py`

丢弃在队列中存活过久的消息。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_age` | `None`（无限） | 消息最大存活时间（毫秒） |

**actor_options**：`{"max_age"}`

**逻辑**：`before_process_message` 中检查 `current_millis() - message.message_timestamp >= max_age`，若超时则 `message.fail()` 并抛出 `SkipMessage`。消息最终进入 DLQ。

## TimeLimit

**文件**：`middleware/time_limit.py`

限制 actor 最大执行时间，超时则在工作线程中注入 `TimeLimitExceeded` 异常。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `time_limit` | `600000`（10分钟） | 最大执行时间（毫秒），`float("inf")` 禁用 |
| `interval` | `1000`（1秒） | 检查间隔（毫秒），gevent 模式下无效 |

**actor_options**：`{"time_limit"}`

**逻辑**：
- `after_process_boot` 启动超时管理器后台线程
- `before_process_message` 注册当前线程的截止时间（`monotonic() + ttl/1000`）
- `after_process_message`/`after_skip_message` 移除超时
- 管理器线程每秒检查所有注册的截止时间，超时则调用 `raise_thread_exception(thread_id, TimeLimitExceeded)`
- 仅支持 CPython（通过 `ctypes.PyThreadState_SetAsyncExc`），无法取消系统调用
- gevent 模式下使用 `gevent.Timeout` 协作式超时

`TimeLimitExceeded` 继承 `Interrupt`（BaseException 子类），不被普通 `except Exception` 捕获。

## ShutdownNotifications

**文件**：`middleware/shutdown.py`

Worker 进程收到关闭信号时，向正在执行的 actor 注入 `Shutdown` 异常，使其可以优雅清理。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `notify_shutdown` | `False` | 是否默认通知所有 actor |

**actor_options**：`{"notify_shutdown"}`

**逻辑**：
- `before_process_message`：若 actor/message 启用了 notify_shutdown，将当前线程 ID 加入通知集合
- `after_process_message`/`after_skip_message`：从通知集合移除
- `before_worker_shutdown`：遍历通知集合，对每个线程调用 `raise_thread_exception(thread_id, Shutdown)`
- gevent 模式下使用 `greenlet.kill(Shutdown, block=False)`

选项优先级：message.options → actor.options → middleware 默认值。

## Callbacks

**文件**：`middleware/callbacks.py`

在 actor 成功或失败后向指定 actor 发送回调消息。

**actor_options**：`{"on_success", "on_failure"}`

**逻辑**（`after_process_message`）：
- 成功（exception is None）：查找 `on_success` actor，发送 `target_actor.send(message.asdict(), result)`
- 失败：查找 `on_failure` actor，发送 `target_actor.send(message.asdict(), {"type": exc_type, "message": str(exc)})`

回调 actor 名可在 actor 声明时设置或通过 `send_with_options` 覆盖。Actor 实例在 `message_with_options` 中自动转换为 actor_name 字符串。

## Pipelines

**文件**：`middleware/pipelines.py`

将 actor 的输出传递给管道中的下一个 actor。

**actor_options**：`{"pipe_target", "pipe_ignore"}`

**逻辑**（`after_process_message`）：
- 若消息有 `pipe_target` 选项（dict 形式的 Message），将其反序列化为 Message
- 若 `pipe_ignore` 非 True，将当前 result 追加到 next_message 的 args 末尾
- 调用 `broker.enqueue(next_message)`
- 异常或消息失败时不触发管道传递

`pipe_target` 由 `pipeline` 组合类在构造时自动设置。

## Retries

**文件**：`middleware/retries.py`

自动重试失败的消息，使用指数退避。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_retries` | `20` | 最大重试次数，None 表示无限 |
| `min_backoff` | `15000`（15秒） | 最小退避时间（毫秒） |
| `max_backoff` | `86400000*7`（7天） | 最大退避时间（毫秒） |
| `retry_when` | `None` | 自定义谓词 `(attempts, exception) -> bool` |

**actor_options**：`{"max_retries", "min_backoff", "max_backoff", "retry_when", "throws", "on_retry_exhausted"}`

**逻辑**（`after_process_message`）：

1. 无异常直接返回
2. 异常匹配 `throws` 选项：`message.fail()` 不重试
3. 递增 `message.options["retries"]`，记录 traceback 和 requeue_timestamp
4. 判断是否耗尽：
   - 有 `retry_when` 谓词：调用谓词决定
   - 无谓词：`retries >= max_retries` 时 fail
5. 重试耗尽时：`message.fail()`，若有 `on_retry_exhausted` 则发送通知
6. 未耗尽时：
   - 若异常是 `Retry` 且有 `delay`，使用该 delay
   - 否则用 `compute_backoff(retries, factor=min_backoff, max_backoff=max_backoff)` 计算
   - `broker.enqueue(message, delay=delay)` 重新入队

### Retry 异常

`dramatiq.Retry(message="", delay=None)` 是特殊异常：
- 行为与普通异常一样触发重试
- 不会被记录为 error 日志
- 可通过 `delay` 参数指定重试延迟（毫秒）

### throws 选项

`throws` 可以是异常类或异常类元组。匹配的异常不会触发重试，直接 nack。适合业务逻辑中"预期失败"的场景。

## 默认中间件顺序的意义

```text
AgeLimit → TimeLimit → ShutdownNotifications → Callbacks → Pipelines → Retries
```

before 顺序（从外到内）：
1. AgeLimit 先检查年龄，过期则跳过所有内层
2. TimeLimit 注册超时保护
3. ShutdownNotifications 注册关闭通知
4. Callbacks/Pipelines 的 before 是 no-op
5. Retries 的 before 是 no-op

after 顺序（从内到外）：
1. **Retries 最先**：看到异常决定是否重试，若重试则后续 Callbacks/Pipelines 不执行
2. **Pipelines 第二**：若未重试且成功，传递结果给下游
3. **Callbacks 第三**：若未重试，触发成功/失败回调
4. ShutdownNotifications 移除通知
5. TimeLimit 移除超时
6. AgeLimit 的 after 是 no-op
