---
type: reference
title: "Dramatiq 源码事实采集（R 阶段）"
description: "从 dramatiq v2.2.0 源码中提取的 96 条编号事实，每条标注源文件与行号，覆盖顶层 API、Actor、Broker、Worker、Middleware、Message、Encoder、CLI、Results、组合原语等模块"
sources:
  - id: dramatiq-source
    resource: https://github.com/Bogdanp/dramatiq
    title: Dramatiq GitHub Repository (v2.2.0)
generated: { by: "reference_agent/trae-solo", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
---

# Dramatiq 源码事实采集（R 阶段）

> 以下事实均从 dramatiq v2.2.0 源码直接提取，零推测。每条标注 `[文件:行号]`。

## 一、顶层 API 与全局 Broker

- **F-001**：`dramatiq/__init__.py` 从 `.actor` 导入 `Actor` 和 `actor`，从 `.broker` 导入 `Broker`/`Consumer`/`MessageProxy`/`get_broker`/`set_broker`，从 `.composition` 导入 `group`/`pipeline`，从 `.encoder` 导入 `Encoder`/`JSONEncoder`/`PickleEncoder`，从 `.message` 导入 `Message`/`get_encoder`/`set_encoder`，从 `.worker` 导入 `Worker`/`ConsumerThread`/`WorkerThread`。[__init__.py:22-43]

- **F-002**：`__version__ = "2.2.0"`。[__init__.py:89]

- **F-003**：`__getattr__` 对已废弃的 `ConnectionError` 名称发出 `DeprecationWarning`，返回 `BrokerConnectionError`，计划在 v3.0.0 移除。[__init__.py:92-101]

- **F-004**：全局 broker 实例存储在模块级变量 `global_broker: Optional[Broker] = None`。[broker.py:35]

- **F-005**：`get_broker()` 惰性初始化全局 broker：先尝试创建 `RabbitmqBroker(host="127.0.0.1", port=5672, heartbeat=5, connection_attempts=5, blocked_connection_timeout=30)`，若 `ImportError`（pika 未安装）则回退到 `RedisBroker()`。[broker.py:38-70]

- **F-006**：`set_broker(broker)` 直接将传入的 broker 赋值给模块级 `global_broker`。[broker.py:73-80]

## 二、Actor 装饰器与 Actor 类

- **F-007**：`Actor` 类继承 `Generic[P, R]`，`__init__` 接收关键字参数 `fn`/`broker`/`actor_name`/`queue_name`/`priority`/`options`，若 `actor_name` 已在 `broker.actors` 中则抛出 `ValueError`。[actor.py:49-75]

- **F-008**：`Actor.__init__` 中，若 `fn` 是协程函数（`iscoroutinefunction(fn)` 为 True），则用 `async_to_sync(fn)` 包装；否则直接赋值 `self.fn = fn`。[actor.py:78]

- **F-009**：`Actor.__init__` 末尾调用 `self.broker.declare_actor(self)` 将自身注册到 broker。[actor.py:84]

- **F-010**：`Actor.send(*args, **kwargs)` 调用 `self.send_with_options(args=args, kwargs=kwargs)`。[actor.py:140-150]

- **F-011**：`Actor.send_with_options` 接收 `delay` 参数（`timedelta` 或毫秒整数），将 `timedelta` 转换为毫秒，调用 `self.message_with_options` 构造 Message，再调用 `self.broker.enqueue(message, delay=delay)`。[actor.py:152-179]

- **F-012**：`Actor.__call__(*args, **kwargs)` 同步执行底层函数 `self.fn(*args, **kwargs)`，用 `time.perf_counter()` 记录执行耗时并 debug 日志，不经过 broker 或中间件管道。[actor.py:181-197]

- **F-013**：`actor` 装饰器函数支持两种调用方式：无括号 `@dramatiq.actor`（`fn` 非 None）和带括号 `@dramatiq.actor(queue_name="...")`（`fn` 为 None，返回 `decorator` 函数）。[actor.py:239-321]

- **F-014**：`actor` 装饰器的默认参数：`queue_name="default"`、`priority=0`、`actor_name=None`、`broker=None`、`actor_class=Actor`。[actor.py:239-248]

- **F-015**：装饰器内部 `decorator` 函数中，`actor_name` 默认为 `fn.__name__`；用正则 `r"[a-zA-Z_][a-zA-Z0-9._-]*"` 校验 queue_name；`broker` 默认为 `get_broker()`；校验 `options` 键必须是 `broker.actor_options` 的子集，否则抛出 `ValueError`。[actor.py:292-308]

- **F-016**：`Actor.message_with_options` 中，若 `options` 中的 `on_failure`/`on_success` 值是 `Actor` 实例，则转换为其 `actor_name` 字符串；若非 `None`/`str`/`Actor` 则抛出 `TypeError`。[actor.py:124-131]

- **F-017**：`GenericActor` 使用元类 `generic_actor`，非抽象子类（`Meta.abstract` 非 True）在类定义时自动实例化并通过 `actor()` 装饰器注册；子类通过实现 `perform()` 方法定义任务逻辑，`__call__` 委托给 `perform`。[generic.py:23-113]

## 三、Message 类与序列化

- **F-018**：`Message` 是 `@dataclasses.dataclass(frozen=True)` 的不可变泛型类 `Generic[R]`，字段包括 `queue_name: str`、`actor_name: str`、`args: tuple`、`kwargs: dict`、`options: dict`、`message_id: str`（默认 `uuid4()`）、`message_timestamp: int`（默认 `int(time.time()*1000)`）。[message.py:63-84]

- **F-019**：`Message.__post_init__` 强制将 `args` 转为 tuple（因为 frozen dataclass，使用 `object.__setattr__`）。[message.py:86-91]

- **F-020**：`Message.encode()` 调用全局 `global_encoder.encode(self.asdict())` 返回 `bytes`；`Message.decode(data)` 调用 `global_encoder.decode(data)` 后构造 Message，失败时抛出 `DecodeError`。[message.py:106-123]

- **F-021**：`Message.copy(**attributes)` 使用 `dataclasses.replace` 创建副本，并将 `options` 与新属性合并（`{**self.options, **new_options}`）。[message.py:125-128]

- **F-022**：`Message.__or__` 运算符将两个 Message 组合成 `pipeline([self, other])`，支持 `msg1 | msg2` 管道语法。[message.py:93-95]

- **F-023**：`Message.get_result(backend=None, block=False, timeout=None)` 若未指定 backend，则从全局 broker 的 Results 中间件获取 backend，调用 `backend.get_result`。[message.py:130-167]

- **F-024**：全局编码器 `global_encoder` 默认是 `JSONEncoder()`，通过 `get_encoder()`/`set_encoder()` 访问和替换。[message.py:33,38-55]

- **F-025**：`Encoder` 是 `abc.ABC`，定义抽象方法 `encode(data: MessageData) -> bytes` 和 `decode(data: bytes) -> MessageData`。[encoder.py:31-42]

- **F-026**：`JSONEncoder.encode` 使用 `json.dumps(data, separators=(",", ":")).encode("utf-8")`（紧凑无空格）；`decode` 先 UTF-8 解码再 `json.loads`，解码失败抛出 `DecodeError`。[encoder.py:45-60]

- **F-027**：`PickleEncoder` 使用 `pickle.dumps`/`pickle.loads`，文档警告"不安全，勿用于不可信数据"。[encoder.py:63-75]

## 四、Broker 抽象基类

- **F-028**：`Broker.__init__` 初始化 `self.actors = {}`、`self.queues = {}`（子类改为 set）、`self.delay_queues = set()`、`self.actor_options = set()`、`self.middleware = []`；若未传入 middleware，则实例化 `default_middleware` 列表中的所有中间件类，并逐个调用 `add_middleware`。[broker.py:98-111]

- **F-029**：`Broker.emit_before(signal, *args, **kwargs)` 将信号名加 `"before_"` 前缀，按 middleware 列表正序调用对应方法，`MiddlewareError` 直接抛出，其他异常记录 critical 日志但不中断。[broker.py:113-121]

- **F-030**：`Broker.emit_after(signal, *args, **kwargs)` 将信号名加 `"after_"` 前缀，按 middleware 列表**逆序**调用对应方法，所有异常仅记录 critical 日志不抛出。[broker.py:123-129]

- **F-031**：`Broker.add_middleware` 支持 `before`/`after` 参数控制插入位置；重复添加同类 middleware 会发出 warning；添加后将 middleware 的 `actor_options` 合并到 broker 的 `actor_options` 集合，并对已声明的 actor/queue/delay_queue 调用 `after_declare_*` 钩子。[broker.py:131-192]

- **F-032**：`Broker.declare_actor(actor)` 是具体方法（非抽象），依次调用 `emit_before("declare_actor", actor)` → `declare_queue(actor.queue_name)` → `self.actors[actor.actor_name] = actor` → `emit_after("declare_actor", actor)`。[broker.py:213-223]

- **F-033**：`Broker` 的抽象方法包括 `consume`、`declare_queue`、`enqueue`、`flush`、`flush_all`、`join`，均抛出 `NotImplementedError`。[broker.py:197-329]

- **F-034**：`Broker.get_actor(actor_name)` 从 `self.actors` 字典查找，找不到抛出 `ActorNotFound`。[broker.py:246-261]

- **F-035**：`Broker.get_results_backend()` 遍历 middleware 查找 `Results` 实例，返回其 `backend`；找不到则抛出 `RuntimeError("The broker doesn't have a results backend.")`。[broker.py:290-303]

- **F-036**：`Consumer` 抽象基类定义 `__iter__`（返回 self）、`ack`、`nack`、`requeue`（默认 no-op）、`__next__`（返回 `MessageProxy | None`）、`close`（默认 no-op）。[broker.py:332-384]

- **F-037**：`MessageProxy` 包装 Message，持有 `failed: bool = False`、`_exception`、`_message`；通过 `__getattr__` 透明代理 Message 的所有属性；提供 `fail()`、`stuff_exception()`、`clear_exception()` 方法。[broker.py:387-438]

## 五、RedisBroker

- **F-038**：`RedisBroker.__init__` 接收 `namespace="dramatiq"`、`maintenance_chance=1000`（百万分之一千的概率触发维护）、`heartbeat_timeout=60000`、`dead_message_ttl=86400000*7`（7天）；`self.queues` 是 `set()`；通过 `redis.Redis(**parameters)` 创建客户端；加载 `brokers/redis/` 目录下的 Lua 脚本（`dispatch.lua`、`maxstack.lua`）。[redis.py:91-115]

- **F-039**：`RedisBroker.enqueue` 为每条消息生成唯一的 `redis_message_id`（`uuid4()`，存入 `message.options`），因为消息重试时 `message_id` 不变但 Redis 中需要唯一 ID；延迟消息路由到 `.DQ` 队列并设置 `eta` 选项；最终通过 `self.do_enqueue(queue_name, redis_message_id, message.encode())` 入队。[redis.py:150-186]

- **F-040**：`RedisBroker` 使用 `__getattr__` 魔术方法将 `do_<command>` 调用（如 `do_enqueue`/`do_ack`/`do_nack`/`do_fetch`/`do_requeue`/`do_purge`/`do_qsize`）分派到 Lua 脚本 `dispatch`，通过 `self._dispatch(command)` 返回闭包执行。[redis.py:259-287]

- **F-041**：`dispatch.lua` 中，`enqueue` 命令将消息数据 `hset` 到 `$namespace:$queue.msgs` 哈希，将 message_id `rpush` 到 `$namespace:$queue` 列表。[dispatch.lua:145-150]

- **F-042**：`dispatch.lua` 中，`fetch` 命令从队列列表 `lpop` 最多 prefetch 个 message_id，将其 `sadd` 到 `$namespace:__acks__.$worker_id.$queue_name` 集合（未确认集合），再 `hmget` 返回消息数据。[dispatch.lua:154-173]

- **F-043**：`dispatch.lua` 中，`ack` 命令从 acks 集合 `srem` message_id，若成功则从 `.msgs` 哈希 `hdel` 删除消息数据。[dispatch.lua:191-196]

- **F-044**：`dispatch.lua` 中，`nack` 命令从 acks 集合移除 message_id，将消息数据从 `.msgs` 哈希 `hget` 后 `zadd` 到 `$namespace:$queue.XQ` 有序集合（DLQ），并 `hset` 到 `.XQ.msgs` 哈希，再从原 `.msgs` 删除。[dispatch.lua:200-212]

- **F-045**：`dispatch.lua` 维护逻辑中，每次调用有概率触发：从 `__heartbeats__` 有序集合找出超时（`timestamp - heartbeat_timeout`）的死亡 worker，将其未 ack 的消息 `rpush` 回队列；从 DLQ 有序集合删除超过 `dead_message_ttl` 的消息。[dispatch.lua:110-141]

- **F-046**：`_RedisConsumer.__next__` 先从本地 `message_cache` 弹出消息；缓存空时调用 `do_fetch` 批量拉取；无消息时用 `compute_backoff` 渐进式长轮询（最大 backoff 为 timeout）。[redis.py:334-373]

## 六、RabbitmqBroker

- **F-047**：`RabbitmqBroker.__init__` 接收 `confirm_delivery=False`、`max_priority`（0-255）、`url`/`parameters`/`**kwargs`（pika 连接参数）；`self.queues` 和 `self.queues_pending` 都是 `set()`；使用 `threading.local()` 的 `self.state` 存储线程局部连接和 channel。[rabbitmq.py:108-155]

- **F-048**：`RabbitmqBroker` 的 `connection` 属性惰性创建 `pika.BlockingConnection`，`channel` 属性惰性创建 `pika.BlockingChannel`，若 `confirm_delivery=True` 则在 channel 上调用 `confirm_delivery()`；两者都是线程局部的。[rabbitmq.py:161-215]

- **F-049**：`RabbitmqBroker._declare_queue` 调用 `channel.queue_declare(queue=queue_name, durable=True, arguments={"x-dead-letter-exchange": "", "x-dead-letter-routing-key": xq_name(queue_name)})`，将死信路由到 `.XQ` 队列；若设置了 `max_priority` 则添加 `x-max-priority` 参数。[rabbitmq.py:327-354]

- **F-050**：`RabbitmqBroker.enqueue` 对延迟消息路由到 `.DQ` 队列并设置 `eta`；调用 `channel.basic_publish(exchange="", routing_key=queue_name, body=message.encode(), properties=pika.BasicProperties(delivery_mode=2, priority=...), mandatory=confirm_delivery)`；连接错误时最多重试 `MAX_ENQUEUE_ATTEMPTS=6` 次。[rabbitmq.py:356-426]

- **F-051**：`_RabbitmqConsumer` 创建独立的 `pika.BlockingConnection` 和 channel，调用 `channel.basic_qos(prefetch_count=prefetch)`，用 `channel.consume(queue_name, inactivity_timeout=timeout/1000)` 获取迭代器；`ack`/`nack` 通过 `connection.add_callback_threadsafe` 线程安全地调用 `channel.basic_ack`/`channel.basic_nack(requeue=False)`。[rabbitmq.py:519-610]

- **F-052**：`_RabbitmqConsumer.requeue` 是 no-op，因为"RabbitMQ 在消费者断开时自动将未 ack 消息重新入队"。[rabbitmq.py:576-579]

## 七、StubBroker

- **F-053**：`StubBroker` 使用 Python 标准库 `queue.Queue` 作为内存队列，`self.queues[queue_name] = Queue()`，`dead_letters_by_queue` 是 `defaultdict(list)`。[stub.py:34-52]

- **F-054**：`StubBroker.enqueue` 延迟消息设置 `eta` 选项后放入 `.DQ` 队列，非延迟消息直接 `queue.put(message.encode())`。[stub.py:97-126]

- **F-055**：`StubBroker.join` 循环等待主队列和延迟队列的 `unfinished_tasks` 归零；若 `fail_fast=True`（默认），遇到死信消息则重新抛出该消息的异常。[stub.py:146-196]

- **F-056**：`_StubConsumer` 使用 `threading.Semaphore(value=prefetch)` 控制预取槽位；`ack` 调用 `queue.task_done()` 并释放信号量；`nack` 除 `task_done` 外将消息追加到 `dead_letters` 列表。[stub.py:199-230]

## 八、Worker 线程模型

- **F-057**：`Worker.__init__` 接收 `broker`、`queues`（可选白名单）、`worker_timeout=1000ms`、`worker_threads=8`；`self.queue_prefetch = min(worker_threads*2, 65535)`，`self.delay_prefetch = min(worker_threads*1000, 65535)`；`self.work_queue` 是 `PriorityQueue`。[worker.py:79-103]

- **F-058**：`Worker.start()` 先 `emit_before("worker_boot")`，创建内部 `_WorkerMiddleware` 并添加到 broker（用于在 queue 声明时自动创建 ConsumerThread），启动 `worker_threads` 个 `WorkerThread`，最后 `emit_after("worker_boot")`。[worker.py:105-116]

- **F-059**：`ConsumerThread` 继承 `Thread(daemon=True)`，`run()` 主循环：调用 `broker.consume()` 获取 consumer 迭代器，遍历消息调用 `handle_message`，每次迭代后调用 `handle_delayed_messages` 检查延迟消息是否到期；遇到 `BrokerConnectionError` 时重置 delay_queue 并在 `CONSUMER_RESTART_DELAY=3000ms` 后重启。[worker.py:296-344]

- **F-060**：`ConsumerThread.handle_message` 检查消息 `options` 中是否有 `eta`：有则放入 `self.delay_queue`（PriorityQueue，优先级为 eta 时间戳），无则查找 actor 后放入 `self.work_queue`（PriorityQueue，优先级为 `actor.priority`）；actor 不存在时标记 `message.fail()` 并 post_process。[worker.py:364-398]

- **F-061**：`ConsumerThread.handle_delayed_messages` 遍历 delay_queue，若 `eta > current_millis()` 则放回并 break；否则将消息 `copy(queue_name=q_name(...))` 并删除 `eta` 选项，重新 `broker.enqueue`。[worker.py:346-362]

- **F-062**：`WorkerThread.run()` 循环从 `self.work_queue.get(timeout)` 获取 `_WorkQueueItem`，调用 `process_message`；`process_message` 依次执行 `emit_before("process_message")` → `actor(*args, **kwargs)` → `emit_after("process_message", result=res)`，捕获 `SkipMessage`/`BaseException` 后通过 `emit_after("skip_message")`/`emit_after("process_message", exception=e)` 通知中间件，finally 中调用 consumer 的 `post_process_message` 并 `work_queue.task_done()`。[worker.py:522-613]

- **F-063**：`ConsumerThread.post_process_message` 根据 `message.failed` 调用 `consumer.nack()` 或 `consumer.ack()`，前后分别 `emit_before("nack"/"ack")` 和 `emit_after`；遇到 `BrokerConnectionError` 时每 5 秒无限重试。[worker.py:400-452]

- **F-064**：`Worker.stop(timeout)` 先停 WorkerThread 再停 ConsumerThread（保持 consumer 存活以发送心跳），join 所有线程后将 work_queue 中未处理消息按 queue 分组调用 `consumer.requeue_messages`，最后关闭 consumer 并 `emit_after("worker_shutdown")`。[worker.py:141-188]

- **F-065**：`_WorkQueueItem` 是 `@dataclass(frozen=True, slots=True, eq=True, order=True)`，字段为 `priority: int`、`message: MessageProxy`（`compare=False`）、`_queued_time: int`（`default_factory=time.monotonic_ns`）；PriorityQueue 按 priority 排序，相同 priority 按入队时间 FIFO。[worker.py:255-269]

## 九、Middleware 中间件体系

- **F-066**：`Middleware` 基类定义了完整的钩子集合（默认均为 no-op）：`before_ack`/`after_ack`/`before_nack`/`after_nack`/`before_declare_actor`/`after_declare_actor`/`before_declare_queue`/`after_declare_queue`/`after_declare_delay_queue`/`before_enqueue`/`after_enqueue`/`before_delay_message`/`before_process_message`/`after_process_message`/`after_skip_message`/`after_process_boot`/`before_worker_boot`/`after_worker_boot`/`before_worker_shutdown`/`after_worker_shutdown`/`after_consumer_thread_boot`/`before_consumer_thread_shutdown`/`after_worker_thread_boot`/`before_worker_thread_shutdown`；`actor_options` 属性默认返回空集合，`forks` 属性默认返回空列表。[middleware/middleware.py:40-153]

- **F-067**：`default_middleware` 列表（按顺序）：`AgeLimit`、`TimeLimit`、`ShutdownNotifications`、`Callbacks`、`Pipelines`、`Retries`。[middleware/__init__.py:56-63]

- **F-068**：`AgeLimit` 中间件在 `before_process_message` 中检查 `current_millis() - message.message_timestamp >= max_age`，若超时则 `message.fail()` 并抛出 `SkipMessage`；提供 actor 选项 `max_age`。[middleware/age_limit.py:27-54]

- **F-069**：`TimeLimit` 中间件在 `before_process_message` 中通过 `manager.add_timeout(thread_id, limit)` 注册截止时间，`after_process_message` 中移除；后台线程 `_CtypesTimeoutManager` 每秒检查超时线程，通过 `raise_thread_exception(thread_id, TimeLimitExceeded)` 注入异常；默认 `time_limit=600000ms`（10分钟）；提供 actor 选项 `time_limit`。[middleware/time_limit.py:46-139]

- **F-070**：`ShutdownNotifications` 中间件在 `before_worker_shutdown` 时对所有注册了通知的工作线程注入 `Shutdown` 异常；通过 actor 选项 `notify_shutdown` 控制（默认 False）。[middleware/shutdown.py:40-133]

- **F-071**：`Retries` 中间件在 `after_process_message` 中处理异常：若异常匹配 `throws` 选项则直接 `message.fail()`；否则递增 `message.options["retries"]`，记录 traceback 和 requeue_timestamp；超过 `max_retries`（默认 20）则 `fail()` 并可发送到 `on_retry_exhausted` actor；否则用 `compute_backoff` 计算指数退避延迟（`min_backoff=15000ms`，`max_backoff=7天`），调用 `broker.enqueue(message, delay=delay)` 重新入队。[middleware/retries.py:37-148]

- **F-072**：`Callbacks` 中间件在 `after_process_message` 中：成功时发送到 `on_success` actor（参数为 `message.asdict(), result`），失败时发送到 `on_failure` actor（参数为 `message.asdict(), {"type":..., "message":...}`）。[middleware/callbacks.py:23-58]

- **F-073**：`Pipelines` 中间件在 `after_process_message` 中检查 `message.options["pipe_target"]`，将其反序列化为 Message，若 `pipe_ignore` 非 True 则将 result 追加到 next_message 的 args，调用 `broker.enqueue(next_message)`。[middleware/pipelines.py:23-58]

- **F-074**：`raise_thread_exception(thread_id, exception)` 仅在 CPython 上可用，通过 `ctypes.pythonapi.PyThreadState_SetAsyncExc` 在目标线程中异步注入异常；异常仅在线程下次获取 GIL 时触发，无法取消系统调用。[threading.py:62-90]

## 十、CLI 与多进程

- **F-075**：`cli.main()` 使用 `argparse` 解析参数：`broker`（位置参数，格式 `module` 或 `module:variable`）、`--processes/-p`（默认 CPU 核数）、`--threads/-t`（默认 8）、`--path/-P`（默认 `.`）、`--queues/-Q`、`--pid-file`、`--log-file`、`--watch`、`--verbose`、`--use-spawn`、`--fork-function/-f`、`--worker-shutdown-timeout`（默认 600000ms）。[cli.py:167-287]

- **F-076**：`import_broker(value)` 用 `importlib.import_module` 导入模块，若值含 `:` 则解析变量名（支持点号链式属性访问如 `app.broker`）；若变量是 callable 则调用它（用于初始化 broker）；若为 None 则使用 `get_broker()`；若非 Broker 实例则抛出 `ImportError`。[cli.py:117-143]

- **F-077**：主进程在 fork worker 子进程前调用 `try_block_signals()` 阻塞 SIGINT/SIGTERM/SIGHUP/SIGBREAK；worker 子进程中重新设置信号处理：SIGINT 忽略，SIGTERM/SIGHUP 设置 `running=False` 优雅退出，第二次收到信号则 `sys.exit(RET_KILLED)` 强制退出。[cli.py:290-306,413-430]

- **F-078**：`worker_process` 函数中：调用 `import_broker` 导入 broker → `broker.emit_after("process_boot")` → 导入额外 modules → 创建 `Worker(broker, queues=args.queues, worker_threads=args.threads)` 并 `start()` → 循环 `time.sleep(1)` 直到 running=False → `worker.stop()` → `broker.close()`。[cli.py:413-480]

- **F-079**：主进程将所有子进程的 stdout/stderr 重定向到 `multiprocessing.Pipe`，由独立的 `log_watcher` 线程通过 `multiprocessing.connection.wait` 多路复用读取并写入日志文件或 stderr。[cli.py:383-410,605-635]

- **F-080**：SIGHUP 触发热重载：主进程的 `sighandler` 将 `reload_process=True`，停止所有子进程后通过 `os.execvp` 重新执行当前命令（`python -m dramatiq` 或原始 argv[0]）。[cli.py:648-706]

- **F-081**：`watcher.setup_file_watcher` 基于 `watchdog` 库，默认监听 `*.py` 文件变化，检测到事件时向当前进程发送 `SIGHUP`；忽略 `opened` 和 `closed_no_write` 事件以避免不必要重启。[watcher.py:12-56]

- **F-082**：`__main__.py` 仅 5 行：`from dramatiq.cli import main` + `sys.exit(main())`，支持 `python -m dramatiq` 入口。[__main__.py:18-25]

## 十一、Results 结果后端

- **F-083**：`ResultBackend` ABC 提供 `get_result(message, block=False, timeout=10000)` 模板方法：循环调用子类 `_get(key)`，结果为 `Missing` 且 block=True 时用 `compute_backoff` 退避重试直到超时（抛出 `ResultTimeout`），非阻塞时抛出 `ResultMissing`。[results/backend.py:45-125]

- **F-084**：`ResultBackend.build_message_key` 生成 `namespace:queue_name:actor_name:message_id` 字符串，默认对其 MD5 哈希作为 key；`use_namespace_prefix_keys=True` 时使用明文 key。[results/backend.py:151-169]

- **F-085**：`Results` 中间件提供 actor 选项 `store_results` 和 `result_ttl`（默认 600000ms=10分钟）；`after_process_message` 中若 `store_results=True` 且无异常，调用 `backend.store_result`；`after_nack` 中若失败则调用 `backend.store_exception`。[results/middleware.py:28-117]

- **F-086**：`RedisBackend` 使用 Redis List 存储结果：`_store` 通过 pipeline `delete` → `lpush`（编码后的结果）→ `pexpire`（TTL）；阻塞获取用 `brpoplpush(key, key, timeout)`，非阻塞用 `lindex(key, 0)`。[results/backends/redis.py:25-110]

- **F-087**：`StubBackend` 使用类变量字典 `results: dict[str, tuple[Optional[str], Optional[float]]] = {}` 存储编码数据和过期时间，`_get` 检查 `time.monotonic() < expiration`。[results/backends/stub.py:26-51]

- **F-088**：`wrap_result(res)` 是 no-op（前向兼容）；`wrap_exception(e)` 返回 `{"__t": "dramatiq.results.Result", "exn": {"type":..., "msg":...}}`；`unwrap_result(res)` 检测到 `__t` 标记则抛出 `ResultFailure`。[results/result.py:25-48]

## 十二、组合原语与工具函数

- **F-089**：`pipeline` 类接收 Message/pipeline 的可迭代对象，将每个 message 的 `pipe_target` 设置为下一个 message 的 `asdict()`；支持 `|` 运算符追加；`run()` 将第一个消息 enqueue。[composition.py:31-123]

- **F-090**：`group` 类并行执行多个子任务，`completion_callbacks` 机制依赖可选的 `GroupCallbacks` 中间件和 `Barrier` 速率限制器；`run()` 将所有子消息 enqueue，有回调时为每个子消息注入 `group_completion_uuid` 和 `group_completion_callbacks` 选项。[composition.py:181-324]

- **F-091**：`common.compute_backoff(attempts, factor=5, jitter=True, max_backoff=2000, max_exponent=32)` 计算指数退避：`backoff = factor * 2^min(attempts, max_exponent)`，jitter 时乘以 1-2 倍随机因子并在超限时回退到 max_backoff 的 50%-100%，返回 `(attempts+1, backoff_ms)`。[common.py:41-72]

- **F-092**：`common` 模块提供队列命名函数：`q_name` 去除 `.DQ`/`.XQ` 后缀返回规范名；`dq_name` 添加 `.DQ` 后缀（已在 DQ 上则不变）；`xq_name` 添加 `.XQ` 后缀（已在 XQ 上则不变）。[common.py:143-173]

- **F-093**：`async_to_sync` 包装器将 async 函数提交到全局 `EventLoopThread` 的事件循环执行并同步等待结果；若全局事件循环线程未设置（未添加 AsyncIO 中间件）则抛出 `RuntimeError`。[asyncio.py:57-71]

- **F-094**：`EventLoopThread` 继承 `threading.Thread`，在独立线程中运行 `asyncio.new_event_loop()`；`run_coroutine` 使用 `asyncio.run_coroutine_threadsafe` 提交协程，通过 0.1 秒超时轮询以捕获异步注入的 `Interrupt` 异常。[asyncio.py:74-189]

- **F-095**：错误体系：`DramatiqError`（基类）→ `BrokerError` → `ActorNotFound`/`QueueNotFound`/`BrokerConnectionError` → `ConnectionFailed`/`ConnectionClosed`；独立分支：`DecodeError`、`QueueJoinTimeout`、`RateLimitExceeded`、`Retry`（携带可选 `delay`）。[errors.py:24-100]

- **F-096**：`Canteen` 是基于 `ctypes.Structure` 的共享内存结构（1MB 缓冲区），用于主进程与 worker 子进程之间传递 middleware.forks 函数路径；`canteen_try_init` 使用 double-checked locking 确保只有一个 worker 初始化。[canteen.py:27-72]
