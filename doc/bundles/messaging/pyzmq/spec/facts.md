---
type: reference
title: "pyzmq 事实清单（R 阶段）"
description: "从 pyzmq 源码中提取的 118 条编号事实，每条标注源文件与行号，覆盖顶层包、sugar、_future、asyncio、backend、constants、error、auth、eventloop、green、devices、log、utils 等模块"
sources:
  - path: "external/libs/remote/pyzmq/zmq/"
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
---

# pyzmq 事实清单（R 阶段）

> 源码位置：`external/libs/remote/pyzmq/`
> 产出位置：`projects/awesome-okf-xs/bundles/messaging/pyzmq/spec/facts.md`
> 原则：零推测，每条事实标注源文件与行号。

## 一、顶层包结构与导出

- **F-001**：`zmq/__init__.py` 在 Windows 上通过 `_libs_on_path()` 上下文管理器临时把 `pyzmq.libs/` 目录加入 `PATH`，以解决 conda-forge Python ≥3.8 的 DLL 解析问题；非 Windows 平台直接 yield。源：`zmq/__init__.py:13-45`
- **F-002**：顶层导入顺序为 `backend` → `constants`（`from .constants import *`）→ `backend.*` → `sugar` → `sugar.*`，即后端先加载，常量与 sugar 层随后聚合。源：`zmq/__init__.py:51-58`
- **F-003**：`zmq.COPY_THRESHOLD = 65536`（64KB），是 zero-copy 与 copy 模式的默认分界阈值。源：`zmq/__init__.py:82`
- **F-004**：`zmq.DRAFT_API` 是布尔值，要求运行时加载的 libzmq 与 pyzmq 构建时均启用 draft，计算式为 `backend.has('draft') and backend.PYZMQ_DRAFT_API`。源：`zmq/__init__.py:86`
- **F-005**：`__all__` 由 `get_includes`/`COPY_THRESHOLD`/`DRAFT_API` 加上 `constants.__all__`、`sugar.__all__`、`backend.__all__` 三部分拼接而成。源：`zmq/__init__.py:88-97`
- **F-006**：`get_includes()` 返回用于 Cython 链接 pyzmq 的 include 目录列表，包含父目录、`utils/` 子目录及可选的 `include/` 目录。源：`zmq/__init__.py:61-70`
- **F-007**：sugar 包的 `__init__.py` 从 `zmq.backend` 导入 `proxy`，并聚合 `context/frame/poll/socket/tracker/version` 子模块的 `__all__`；同时把 `error` 模块的名字也通过 `from zmq.error import *` 导出。源：`zmq/sugar/__init__.py:8-37`
- **F-008**：`zmq.sugar.device(device_type, frontend, backend)` 是已废弃的 `zmq.proxy` 别名，内部直接调用 `proxy(frontend, backend)`。源：`zmq/sugar/__init__.py:14-21`

## 二、sugar.Context

- **F-009**：`Context` 类继承自 `zmq.backend.Context`（C 扩展基类）与 `AttributeSetter` mixin，并泛型化于 `_SocketType`；类属性 `_socket_class = Socket` 决定 `ctx.socket()` 创建的 Socket 子类，子类可覆写以替换 Socket 类型（如 asyncio.Context 替换为 asyncio.Socket）。源：`zmq/sugar/context.py:40,79`
- **F-010**：`Context.__init__` 支持三种调用形态：`Context(io_threads=1)`、`Context(other_context)`（位置参数 shadow）、`Context(shadow=addr)`；若传入的是 Context 实例则自动取其 `underlying` 地址。源：`zmq/sugar/context.py:81-116`
- **F-011**：`Context` 维护 `self.sockopts = {}` 字典，用于存储通过 `ctx.setsockopt()` 设置的"默认 socket 选项"，新建 socket 时会把这些选项批量应用到新 socket 上。源：`zmq/sugar/context.py:115,356-363`
- **F-012**：`Context` 用 `WeakSet()`（`self._sockets`）跟踪所有由其创建的 socket 弱引用，用于 `destroy()` 时统一关闭。源：`zmq/sugar/context.py:77,116,279-287`
- **F-013**：`Context.__del__` 在非 shadow、非进程退出、未关闭时调用 `self.destroy()`（而非 `term()`），并发出 `ResourceWarning`；v24 起从 `term()` 改为 `destroy()` 以避免 socket 未关导致的挂起。源：`zmq/sugar/context.py:118-140`
- **F-014**：`Context` 支持上下文管理器协议，`__enter__` 返回 self，`__exit__` 调用 `self.destroy()`（先设 `_warn_destroy_close=True` 再关闭所有 socket）。源：`zmq/sugar/context.py:160-166`
- **F-015**：`Context.instance()` 是类方法，返回全局单例 Context；使用双重检查锁（`_instance_lock`），并在 fork 后（`_instance_pid != os.getpid()`）或单例已关闭时重建。源：`zmq/sugar/context.py:206-241`
- **F-016**：`Context.term()` 直接调用 `super().term()`（后端 C 实现），文档说明会中断阻塞调用并等待所有 socket 关闭与消息发送完成（受 LINGER 控制）。源：`zmq/sugar/context.py:243-264`
- **F-017**：`Context.destroy(linger=None)` 遍历 `_sockets` 弱引用集合，对未关闭 socket 可选设置 LINGER 后调用 `s.close()`，最后调用 `self.term()`；文档警告该方法非线程安全。源：`zmq/sugar/context.py:289-322`
- **F-018**：`Context.socket(socket_type, socket_class=None, **kwargs)` 在 closed 时抛 `ZMQError(ENOTSUP)`；默认用 `self._socket_class` 实例化，随后把 `self.sockopts` 中的默认选项应用到新 socket（忽略不适用选项的 ZMQError），并通过 `_add_socket` 加入弱引用集合。源：`zmq/sugar/context.py:324-365`
- **F-019**：`Context.setsockopt(opt, value)` / `getsockopt(opt)` 操作的是 `self.sockopts` 字典（默认选项），而非直接调用 C 层；这是 v13 新增的"为新 socket 设默认选项"机制。源：`zmq/sugar/context.py:367-379`
- **F-020**：`Context._set_attr_opt(name, opt, value)` 区分 ContextOption（调 `self.set`）与 SocketOption（存入 `self.sockopts`）；`_get_attr_opt` 对 ContextOption 调 `self.get`，对 SocketOption 查 `sockopts` 字典。源：`zmq/sugar/context.py:381-398`
- **F-021**：`Context.shadow(address)` 类方法通过 `cls(shadow=address)` 创建对已有 libzmq context 的影子包装；`__copy__`/`__deepcopy__` 均返回 shadow 副本。源：`zmq/sugar/context.py:168-187`

## 三、sugar.Socket

- **F-022**：`Socket` 继承自 `zmq.backend.Socket`（C 扩展基类）与 `AttributeSetter`，并泛型化于 `_SocketReturnT_co`；类属性 `_repr_cls = "zmq.Socket"`。源：`zmq/sugar/socket.py:83,198`
- **F-023**：`Socket.__init__` 支持 `Socket(ctx, type)`、`Socket(shadow=addr)`、`Socket(other_socket)` 三种形态；shadow 另一 Socket 时会保留其 `context` 引用；初始化后通过 `self.get(zmq.TYPE)` 查询实际类型并设置 `_type_name`。源：`zmq/sugar/socket.py:113-184`
- **F-024**：`Socket.bind(addr)` 调用 `super().bind(addr)`，在 ZMQError 时把地址追加到 `strerror`；返回 `_SocketContext` 上下文管理器，退出时自动 `unbind`；`_bind_cm` 会通过 `LAST_ENDPOINT` 获取实际绑定地址以支持端口 0 随机端口。源：`zmq/sugar/socket.py:279-326`
- **F-025**：`Socket.connect(addr)` 同样返回 `_SocketContext`，退出时自动 `disconnect`；`_SocketContext` 根据 kind（bind/connect）决定退出时调 unbind 还是 disconnect。源：`zmq/sugar/socket.py:52-77,328-352`
- **F-026**：`Socket` 是上下文管理器，`__enter__` 返回 self，`__exit__` 调用 `self.close()`。源：`zmq/sugar/socket.py:212-220`
- **F-027**：`Socket.setsockopt = SocketBase.set`、`getsockopt = SocketBase.get`，即直接把后端 C 方法赋值为同名方法，未做 Python 层包装。源：`zmq/sugar/socket.py:375-376`
- **F-028**：`Socket.__setattr__` 特判 `subscribe`/`unsubscribe` 键（大小写不敏感），把字符串值编码为 utf8 后调用 `self.set(zmq.SUBSCRIBE/UNSUBSCRIBE, value)`，从而允许 `socket.subscribe = b"topic"` 语法。源：`zmq/sugar/socket.py:378-392`
- **F-029**：`Socket.subscribe(topic)` / `unsubscribe(topic)` 接受 str 或 bytes，str 自动编码为 utf8，然后调用 `self.set(zmq.SUBSCRIBE/UNSUBSCRIBE, topic)`。源：`zmq/sugar/socket.py:405-425`
- **F-030**：`Socket.set_string(option, optval, encoding='utf-8')` 把 unicode 字符串编码后调 `self.set`；`get_string(option, encoding)` 校验选项类型为 bytes 后解码；别名 `setsockopt_string`/`setsockopt_unicode` 等同。源：`zmq/sugar/socket.py:427-469`
- **F-031**：`Socket.send(data, flags=0, copy=True, track=False, routing_id=None, group=None)` 参数：`flags` 可为 0/NOBLOCK/SNDMORE；`copy=True` 返回 None，`copy=False` 或传入 Frame 返回 `MessageTracker`；`routing_id`（SERVER 套接字）与 `group`（RADIO 套接字）为 draft 参数，非 Frame 数据会被包装成 Frame。源：`zmq/sugar/socket.py:587-713`
- **F-032**：`Socket.send_multipart(msg_parts, flags=0, copy=True, track=False, **kwargs)` 先对每个 part 做 buffer 接口类型检查，然后对除最后一部分外的所有 part 加 `zmq.SNDMORE` 标志发送，最后一部分不带 SNDMORE。源：`zmq/sugar/socket.py:715-767`
- **F-033**：`Socket.recv_multipart(flags=0, copy=True, track=False)` 先 recv 第一部分，然后循环检查 `getsockopt(zmq.RCVMORE)` 直到没有更多部分，返回 list。源：`zmq/sugar/socket.py:785-818`
- **F-034**：`Socket.send_string(u, flags=0, copy=True, encoding='utf-8', **kwargs)` 校验 `u` 为 str 后编码并调 `self.send`；别名 `send_unicode`。源：`zmq/sugar/socket.py:920-946`
- **F-035**：`Socket.recv_string(flags=0, encoding='utf-8')` 调用 `self.recv(flags)` 后通过 `_deserialize` 用 lambda 解码；别名 `recv_unicode`。源：`zmq/sugar/socket.py:948-971`
- **F-036**：`Socket.send_pyobj(obj, flags=0, protocol=DEFAULT_PROTOCOL, **kwargs)` 用 `pickle.dumps(obj, protocol)` 序列化后发送；文档警告 pickle 反序列化不可信消息有代码执行风险。源：`zmq/sugar/socket.py:973-1003`
- **F-037**：`Socket.recv_pyobj(flags=0)` 用 `pickle.loads` 反序列化；`DEFAULT_PROTOCOL` 取 `pickle.DEFAULT_PROTOCOL`，旧版 Python 回退到 `pickle.HIGHEST_PROTOCOL`。源：`zmq/sugar/socket.py:39-42,1005-1034`
- **F-038**：`Socket.send_json(obj, flags=0, **kwargs)` 用 `zmq.utils.jsonapi.dumps` 序列化为 UTF-8 bytes；`routing_id`/`group` 关键字参数被提取后透传给 `send`。源：`zmq/sugar/socket.py:1036-1053`
- **F-039**：`Socket.recv_json(flags=0, **kwargs)` 通过 `_deserialize` 调用 `jsonapi.loads`；`_deserialize(recvd, load)` 是可被子类覆写的反序列化钩子（Future 子类覆写以链式 Future）。源：`zmq/sugar/socket.py:820-840,1055-1076`
- **F-040**：`Socket.poll(timeout=None, flags=POLLIN)` 创建 `self._poller_class()`（默认 `Poller`），注册自身后 poll，返回事件位掩码（0 表示超时）；socket 已关闭时抛 `ZMQError(ENOTSUP)`。源：`zmq/sugar/socket.py:1078-1108`
- **F-041**：`Socket.get_monitor_socket(events=None, addr=None)` 要求 libzmq ≥4；默认地址为 `inproc://monitor.s-{FD}`，默认事件为 `EVENT_ALL`；内部调用 `self.monitor(addr, events)` 并创建一个 PAIR socket connect 到该地址；已存在时返回缓存的 `_monitor_socket`。源：`zmq/sugar/socket.py:1110-1155`
- **F-042**：`Socket.disable_monitor()` 置空 `_monitor_socket` 并调用 `self.monitor(None, 0)` 注销监控。源：`zmq/sugar/socket.py:1157-1164`
- **F-043**：`Socket.bind_to_random_port(addr, min_port=49152, max_port=65536, max_tries=100)` 在默认范围时通过绑定 `addr:*` 让 OS 选端口并从 `LAST_ENDPOINT` 解析；否则随机尝试端口，遇 EADDRINUSE 或 Windows EACCES 重试，超过次数抛 `ZMQBindError`。源：`zmq/sugar/socket.py:471-525`
- **F-044**：`Socket.hwm` 是 property，getter 优先返回 `SNDHWM`，失败回退 `RCVHWM`；setter 同时设置 `sndhwm` 和 `rcvhwm`。源：`zmq/sugar/socket.py:527-581`
- **F-045**：`Socket.fileno()` 返回 `self.FD`（edge-triggered 文件描述符），文档强调事件必须被消费否则不会再次触发。源：`zmq/sugar/socket.py:394-403`

## 四、sugar.Frame

- **F-046**：sugar 层 `Frame` 继承自后端 `FrameBase`（C 扩展，本身是 bytes 子类）与 `AttributeSetter`；`Message = Frame` 是保留的废弃别名。源：`zmq/sugar/frame.py:27,146-147`
- **F-047**：`Frame.__getitem__(key)` 把字典式访问 `frame['User-Id']` 映射到 `self.get(key)`；支持 int、str、bytes 键。源：`zmq/sugar/frame.py:75-83`
- **F-048**：`Frame.__repr__` 对大于 16 字节的消息只显示前 12 字节并附加 `...{n}{unit}` 后缀（B/kB/MB/GB）；模块名若为 `zmq.sugar.frame` 则显示为 `zmq`。源：`zmq/sugar/frame.py:85-110`
- **F-049**：`Frame.group` property（RADIO-DISH）与 `routing_id` property（CLIENT-SERVER）均要求 libzmq ≥4.2 且启用 draft API，通过 `_draft()` 辅助函数检查；底层调用 `self.get/set('group'/'routing_id')`。源：`zmq/sugar/frame.py:16-24,112-142`

## 五、sugar.Poller

- **F-050**：`Poller.__init__` 初始化 `self.sockets = []`（list of `(socket, flags)` 元组）与 `self._map = {}`（socket → 索引），用于 O(1) 查找与注册/注销。源：`zmq/sugar/poll.py:24-26`
- **F-051**：`Poller.register(socket, flags=POLLIN|POLLOUT)`：flags 非零时更新或追加；flags=0 等价于 unregister；支持 zmq.Socket 或任何有 `fileno()` 方法的原生 fd。源：`zmq/sugar/poll.py:31-60`
- **F-052**：`Poller.modify(socket, flags)` 直接委托给 `register`；`unregister(socket)` 弹出索引后需要把后续元素的索引整体减 1。源：`zmq/sugar/poll.py:62-78`
- **F-053**：`Poller.poll(timeout=None)` 把 None/负值转为 -1（无限等待），float 转 int，然后调用后端 `zmq_poll(self.sockets, timeout=timeout)`，返回 `[(socket, event_mask), ...]`；常用 `dict(poller.poll())` 转字典。源：`zmq/sugar/poll.py:80-106`
- **F-054**：`select(rlist, wlist, xlist, timeout=None)` 是兼容 `select.select()` 接口的封装，把秒级 timeout 转为毫秒，合并三个列表构造 flags，调用 `zmq_poll` 后再按 POLLIN/POLLOUT/POLLERR 拆分回三个列表。源：`zmq/sugar/poll.py:109-165`

## 六、sugar.MessageTracker

- **F-055**：`MessageTracker.__init__(*towatch)` 接受可变参数，每个参数可为 `threading.Event`、`MessageTracker` 或 `Frame`；Event 加入 `self.events`，MessageTracker 加入 `self.peers`，Frame 取其 `tracker` 属性加入 peers；传入未 tracked 的 Frame 抛 ValueError。源：`zmq/sugar/tracker.py:35-57`
- **F-056**：`MessageTracker.done` 属性遍历所有 events 检查 `is_set()`，并递归检查 peers 的 `done`；全部完成才返回 True。源：`zmq/sugar/tracker.py:59-68`
- **F-057**：`MessageTracker.wait(timeout=-1)` 顺序等待每个 Event 与 peer，超时（秒）则抛 `NotDone`；timeout 为 False 或负值时用一周（3600×24×7 秒）作为"永久"上限以避免无限阻塞。源：`zmq/sugar/tracker.py:70-111`
- **F-058**：模块级 `_FINISHED_TRACKER = MessageTracker()` 是一个无监控对象的已完成 tracker 单例，作为 zero-copy 小消息（小于 copy_threshold）发送后的返回值。源：`zmq/sugar/tracker.py:114`

## 七、attrsettr 描述符系统

- **F-059**：`AttributeSetter.__setattr__` 先检查 key 是否在实例 `__dict__` 或类/MRO 的 `__dict__`/`__annotations__` 中，是则普通 setattr；否则把 key 大写后从 `zmq.constants` 查常量，查到则调 `self._set_attr_opt(upper_key, opt, value)`。源：`zmq/sugar/attrsettr.py:17-37`
- **F-060**：`AttributeSetter.__getattr__` 把 key 大写后从 constants 查常量，查到则调 `self._get_attr_opt(upper_key, opt)`；若 ZMQError 的 errno 为 EINVAL/EFAULT（只写属性），转为 AttributeError。源：`zmq/sugar/attrsettr.py:43-64`
- **F-061**：`AttributeSetter._set_attr_opt` 默认调 `self.set(opt, value)`，`_get_attr_opt` 默认调 `self.get(opt)`；Context 覆写这两个方法以区分 context 选项与 socket 默认选项；`get`/`set` 本身在基类抛 NotImplementedError，由后端子类实现。源：`zmq/sugar/attrsettr.py:39-76`

## 八、_future 异步层

- **F-062**：`_Async` mixin 定义 `_current_loop`、`_Future`、`_get_loop()`（检测 loop 变化并重新初始化 IO）、`_default_loop()`（子类实现）、`_init_io_state(loop)`（默认空操作）。源：`zmq/_future.py:43-70`
- **F-063**：`_AsyncPoller` 继承 `_Async` 与 `zmq.Poller`；其 `poll(timeout=-1)` 返回 Awaitable/Future：timeout=0 时立即尝试非阻塞 poll；否则创建 watcher Future，对 zmq.Socket 调 `_add_recv_event/_add_send_event`，对原生 fd 调 `_watch_raw_socket`，事件就绪后用 `super().poll(0)` 取结果。源：`zmq/_future.py:73-189`
- **F-064**：`_AsyncSocket` 继承 `_Async` 与 `zmq.Socket[Future]`；内部维护 `_recv_futures`/`_send_futures` 两个 `deque`，以及 `_shadow_sock`（一个影子同步 Socket 用于实际非阻塞调用）。源：`zmq/_future.py:201-238`
- **F-065**：`_AsyncSocket.recv/recv_multipart/recv_into/send/send_multipart` 均返回 Future/Awaitable，而非直接返回数据；它们通过 `_add_recv_event`/`_add_send_event` 入队。源：`zmq/_future.py:270-335`
- **F-066**：`_add_recv_event` 对带 `DONTWAIT` 标志的调用短路：直接在 `_shadow_sock` 上非阻塞 recv 并立即 set_result/set_exception；否则根据 `RCVTIMEO` 添加超时定时器，把 `_FutureEvent` 加入 deque，并通过 `_add_io_state(POLLIN)` 注册读事件。源：`zmq/_future.py:470-523`
- **F-067**：`_add_send_event` 在队列为空时先尝试用 `DONTWAIT` 非阻塞发送，成功则立即完成 Future；EAGAIN 且未要求 DONTWAIT 时降级为异步等待；否则根据 `SNDTIMEO` 加超时并入队，注册 POLLOUT。源：`zmq/_future.py:525-584`
- **F-068**：`_handle_recv`/`_handle_send` 从 deque 弹出第一个未完成 Future，用 `DONTWAIT` 在 shadow socket 上实际执行 recv/send，成功 set_result，失败 set_exception；kind 为 `'poll'` 时只 signal ready。源：`zmq/_future.py:586-667`
- **F-069**：`_AsyncSocket._deserialize(recvd, load)` 覆写为链式 Future：创建新 Future，在 recvd Future 完成时执行 load 并传递结果/异常，同时把取消事件从新 Future 传播回 recvd。源：`zmq/_future.py:337-377`
- **F-070**：`_AsyncSocket.close()` 先取消所有未完成的 recv/send Future，清理 IO 状态，再调用 `super().close()`。源：`zmq/_future.py:245-260`

## 九、asyncio 集成

- **F-071**：`zmq.asyncio._AsyncIO` mixin 设置 `_Future = asyncio.Future`、`_READ = selectors.EVENT_READ`、`_WRITE = selectors.EVENT_WRITE`；`_default_loop()` 调 `asyncio.get_running_loop()`，无运行 loop 时发 RuntimeWarning 并回退 `get_event_loop()`。源：`zmq/asyncio.py:101-116`
- **F-072**：`zmq.asyncio.Socket` 继承 `_AsyncIO` 与 `_future._AsyncSocket`；`_init_io_state` 通过 `selector.add_reader(self._fd, callback)` 注册，`_clear_io_state` 用 `remove_reader` 注销。源：`zmq/asyncio.py:138-161`
- **F-073**：`zmq.asyncio.Poller` 继承 `_AsyncIO` 与 `_AsyncPoller`；`_watch_raw_socket` 用 `selector.add_reader/add_writer`，`_unwatch_raw_sockets` 用 `remove_reader/remove_writer`；类属性 `Poller._socket_class = Socket`。源：`zmq/asyncio.py:119-135,164`
- **F-074**：`zmq.asyncio.Context` 继承 `zmq.Context[Socket]`，覆写 `_socket_class = Socket`，并重置 `_instance = None` 以避免与基类 Context 共享单例。源：`zmq/asyncio.py:167-181`
- **F-075**：Windows 上若当前 loop 是 `ProactorEventLoop`（无 add_reader），`_get_selector_windows` 尝试用 tornado 的 `AddThreadSelectorEventLoop` 包装，并 patch loop.close 以清理 selector 线程；找不到 tornado 则抛 RuntimeError。非 Windows 用 `_get_selector_noop` 直接返回原 loop。源：`zmq/asyncio.py:30-98`
- **F-076**：`ZMQEventLoop` 与 `install()` 自 pyzmq 17 起已废弃，pyzmq 可直接在任意 asyncio event loop 上工作。源：`zmq/asyncio.py:184-215`

## 十、后端选择与 CFFI

- **F-077**：`zmq/backend/__init__.py` 若环境变量 `PYZMQ_BACKEND` 为 `cython`/`cffi` 则强制选择；否则 CPython 默认先尝试 cython 再回退 cffi，PyPy 顺序相反；第一个后端 import 失败时尝试第二个，第二个 ImportError 则抛出原始错误。源：`zmq/backend/__init__.py:11-31`
- **F-078**：`select_backend(name)` 用 `importlib.import_module` 导入后端模块，从模块中提取 `public_api` 列表所列名字（Context/Socket/Frame/Message/proxy/proxy_steerable/zmq_poll/strerror/zmq_errno/has/curve_keypair/curve_public/zmq_version_info/IPC_PATH_MAX_LEN/PYZMQ_DRAFT_API）外加私有 `monitored_queue`，组成命名空间字典。源：`zmq/backend/select.py:9-41`
- **F-079**：CFFI 后端 `__init__.py` 从 `._cffi` 导入 `ffi` 和 `lib as C`，并聚合 `_poll/context/devices/error/message/socket/utils` 子模块；`zmq_version_info()` 通过 `ffi.new('int*')` 分配三个 int 指针，调用 `C.zmq_version` 后返回元组。源：`zmq/backend/cffi/__init__.py:7-23`
- **F-080**：CFFI `Context` 用 `C.zmq_ctx_new()` 创建上下文，`C.zmq_ctx_set/get` 设置/获取选项，`C.zmq_ctx_destroy` 终止；shadow 模式用 `ffi.cast("void *", shadow)` 转换地址；`underlying` 属性返回 `int(ffi.cast('size_t', self._zmq_ctx))`。源：`zmq/backend/cffi/context.py:13-74`
- **F-081**：CFFI `Socket.set(option, value)` 用 `SocketOption(option)._opt_type` 判断类型（int/int64/bytes/fd），通过 `initialize_opt_pointer` 构造对应 C 指针，调用 `C.zmq_setsockopt`；unicode 字符串被拒绝（要求 bytes）。源：`zmq/backend/cffi/socket.py:213-241`
- **F-082**：CFFI `Socket.get(option)` 根据 `_opt_type` 分配指针，调用 `C.zmq_getsockopt`，再用 `value_from_opt_pointer` 转回 Python 值；对 thread-safe socket 的 FD 选项有 draft `zmq_poller_fd` 回退逻辑。源：`zmq/backend/cffi/socket.py:243-312`
- **F-083**：CFFI `Socket.send(data, flags=0, copy=False, track=False)`：copy=True 且非 Frame 时调 `_send_copy`（`zmq_msg_init_size` + memcpy + `zmq_msg_send`）；否则用 Frame 的 zero-copy 路径 `_send_frame`（`frame.fast_copy()` 后 `zmq_msg_send`），小于 `copy_threshold` 的消息自动走 copy 路径并返回 `_FINISHED_TRACKER`。源：`zmq/backend/cffi/socket.py:314-365`
- **F-084**：CFFI `Socket.recv(flags=0, copy=True, track=False)`：copy=True 时 `zmq_msg_init` + `zmq_msg_recv` + `ffi.buffer` 复制 bytes + `zmq_msg_close`；copy=False 时创建 `zmq.Frame(track=track)` 并在其上 recv，返回 Frame。源：`zmq/backend/cffi/socket.py:367-389`
- **F-085**：CFFI `Socket.monitor(addr, events=-1)` 在 events<0 时用 `EVENT_ALL`，addr=None 时传 `ffi.NULL`，调用 `C.zmq_socket_monitor`。源：`zmq/backend/cffi/socket.py:409-432`
- **F-086**：CFFI `Frame` 在 zero-copy 模式下通过 `C.zmq_wrap_msg_init_data` 注册 `free_python_msg` 回调，并使用 `zhint` 结构体持有 garbage collector 的 id、mutex 与 PULL socket 指针，实现 libzmq 释放内存时通知 Python GC。源：`zmq/backend/cffi/message.py:105-140`
- **F-087**：CFFI `Frame.fast_copy()` 创建新空 Frame 并调用 `C.zmq_msg_copy` 增加 zmq_msg 引用计数（不复制数据），同时共享 `_data`/`_buffer`/`tracker`/`tracker_event`。源：`zmq/backend/cffi/message.py:203-220`
- **F-088**：CFFI 错误模块 `strerror(errno)` = `ffi.string(C.zmq_strerror(errno)).decode()`；`zmq_errno = C.zmq_errno` 直接绑定 C 函数。源：`zmq/backend/cffi/error.py:10-14`

## 十一、constants 与 error

- **F-089**：`constants.py` 用 `IntEnum`/`IntFlag` 定义所有常量类别：`Errno`、`ContextOption`、`SocketType`、`SocketOption`、`MessageOption`、`Flag`、`PollEvent`、`DeviceType`、`SecurityMechanism`、`Event` 等。源：`zmq/constants.py:16-446`
- **F-090**：`SocketOption` 的 `__new__` 接受 `(value, opt_type=_OptType.int)`，把 `_opt_type` 附加到枚举成员上，供后端判断 setsockopt/getsockopt 的指针类型（int/int64/bytes/fd）。源：`zmq/constants.py:138-151`
- **F-091**：constants 模块在枚举定义之后有 `# AUTOGENERATED_BELOW_HERE` 标记，把所有枚举成员又展开为模块级常量（如 `POLLIN = PollEvent.POLLIN`、`ROUTER = SocketType.ROUTER`），以支持 `from zmq.constants import *` 与旧式 `zmq.POLLIN` 访问。源：`zmq/constants.py:449-717`
- **F-092**：`ZMQError` 继承 `ZMQBaseError`；`__init__(errno=None, msg=None)` 在 errno 为 None 时调 `zmq_errno()` 获取，msg 为 None 时调 `strerror(errno)`；实例属性为 `errno`（int|None）与 `strerror`（str）；`__str__` 返回 strerror。源：`zmq/error.py:31-82`
- **F-093**：`ContextTerminated` 固定包装 `zmq.ETERM`，`Again` 固定包装 `zmq.EAGAIN`，`InterruptedSystemCall` 包装 EINTR 并继承 `InterruptedError`；这三者构造函数忽略传入的 errno/msg 参数。源：`zmq/error.py:103-156`
- **F-094**：`_check_rc(rc, errno=None, error_without_errno=True)` 是内部工具：rc==-1 时根据 errno 抛 `InterruptedSystemCall`(EINTR)、`Again`(EAGAIN)、`ContextTerminated`(ETERM) 或通用 `ZMQError`。源：`zmq/error.py:159-180`
- **F-095**：`ZMQVersionError` 缓存全局 `_zmq_version`，`__str__` 返回 `"{msg} requires libzmq >= {min_version}, have {version}"`；`_check_version(min_version_info, msg)` 在版本不足时抛此异常。源：`zmq/error.py:187-231`

## 十二、decorators

- **F-096**：`zmq.decorators` 提供 `@context()` 与 `@socket(socket_type)` 装饰器，基于 `_Decorator` 通用工厂；wrapper 内用 `with target(*dec_args, **dec_kwargs) as obj` 创建 Context/Socket 并注入被装饰函数参数。源：`zmq/decorators.py:47-97`
- **F-097**：`_SocketDecorator` 在调用时从 kwargs/args 中查找 `zmq.Context` 实例（参数名由 `context_name` 指定，默认 `'context'`），找不到则用 `zmq.Context.instance()`，返回 `context.socket` 作为 target。源：`zmq/decorators.py:132-175`

## 十三、auth 认证

- **F-098**：`zmq.auth.__init__` 仅从 `.base` 与 `.certs` 导出；`Authenticator` 基类在 `start()` 中创建 `zmq.REP` socket 绑定到 `inproc://zeromq.zap.01`（ZAP 标准端点），linger=1。源：`zmq/auth/__init__.py:12-13`、`zmq/auth/base.py:81-86`
- **F-099**：`Authenticator.allow(*addresses)` 与 `deny(*addresses)` 互斥（同时用抛 ValueError）；NULL 机制下未被 deny 的地址允许，PLAIN/CURVE 即使地址 allow 仍需认证。源：`zmq/auth/base.py:94-119,256-317`
- **F-100**：`Authenticator.configure_plain(domain='*', passwords=None)` 把 `{username: password}` 字典按 domain 存入 `self.passwords`；`configure_curve(domain, location)` 从目录加载 `*.key` 公钥证书，`CURVE_ALLOW_ANY`（`'*'`）表示允许所有客户端。源：`zmq/auth/base.py:121-159`
- **F-101**：`Authenticator.handle_zap_message(msg)` 是 async 方法，解析 ZAP 请求（version/request_id/domain/address/identity/mechanism + credentials），按 NULL/PLAIN/CURVE/GSSAPI 分支认证，通过 `_send_zap_reply` 回复 200/400 状态码；CURVE 认证调用 `await self._authenticate_curve`。源：`zmq/auth/base.py:224-322`
- **F-102**：`Authenticator.curve_user_id(client_public_key)` 默认返回公钥的 z85 编码作为 User-Id，可被子类覆写为自定义映射。源：`zmq/auth/base.py:195-214`
- **F-103**：`ThreadAuthenticator` 在后台线程运行 ZAP 处理：`start()` 创建 PAIR pipe（`inproc://{id(self)}.inproc`），启动 `AuthenticationThread`（daemon），线程内新建 asyncio event loop，用 `zmq.asyncio.Poller` 同时监听 pipe 与 zap_socket。源：`zmq/auth/thread.py:19-118`
- **F-104**：`AsyncioAuthenticator` 在当前 asyncio loop 中启动 `__handle_zap` 任务，用 `zmq.asyncio.Poller` 监听 zap_socket；`stop()` 取消任务、注销 poller、关闭 socket。源：`zmq/auth/asyncio.py:19-63`
- **F-105**：`certs.load_certificates(directory='.')` glob 目录下所有 `*.key` 文件，调用 `load_certificate` 提取公钥，返回 `{public_key_bytes: True}` 字典；`create_certificates(key_dir, name, metadata)` 用 `zmq.curve_keypair()` 生成密钥对并写入 `.key`/`.key_secret` 文件。源：`zmq/auth/certs.py:61-137`

## 十四、eventloop / green / devices / log / utils

- **F-106**：`zmq.eventloop` 自 pyzmq 17 起废弃，`ioloop.py` 直接从 `tornado.ioloop` re-export，`ZMQIOLoop = IOLoop`；`ZMQStream` 仍保留用于基于 tornado IOLoop 的回调式消息收发，构造时若传入 `_AsyncSocket` 子类会发 RuntimeWarning 并 shadow 回基础 `zmq.Socket`。源：`zmq/eventloop/ioloop.py:1-32`、`zmq/eventloop/zmqstream.py:98-114`
- **F-107**：`zmq.eventloop.future` 提供 tornado 版异步 Socket/Poller：`_AsyncTornado` mixin 设置 `_Future = _TornadoFuture`（恢复 cancel 能力）、`_READ/_WRITE = IOLoop.READ/WRITE`，`_default_loop` 返回 `IOLoop.current()`。源：`zmq/eventloop/future.py:53-78`
- **F-108**：`zmq.green` 通过 `import zmq.green as zmq` 使用；`_Context` 继承 `zmq.Context` 并设 `_socket_class = _Socket`，重置 `_instance`；`_Socket` 覆写 send/recv/recv_into/send_multipart/recv_multipart/get/set，用 gevent `AsyncResult` 在 EAGAIN 时让出当前 greenlet 而非阻塞线程。源：`zmq/green/core.py:44-334`、`zmq/green/__init__.py:33-42`
- **F-109**：`zmq.green._Socket` 用 `get_hub().loop.io(socket.FD, 1)` 监听 zmq FD，`__state_changed` 回调查询 `EVENTS` 并 set `__readable`/`__writable` AsyncResult；send/recv 循环用 `DONTWAIT` + EAGAIN 重试 + `_wait_read/_wait_write` 让出。源：`zmq/green/core.py:95-128,204-265`
- **F-110**：`zmq.green._Poller` 覆写 `poll`：先非阻塞 `super().poll(0)`，无事件时用 gevent `select.select` 等待 FD（带 1.33 秒 bug 超时兜底），避免阻塞整个 OS 线程。源：`zmq/green/poll.py:10-101`
- **F-111**：`zmq.devices.Device` 接受 socket 类型（而非实例），通过 `bind_in/connect_in/setsockopt_in`（及 `_out` 对应方法）排队配置；`_setup_sockets` 在运行时创建 Context 与两个 Socket，`run_device` 调用 `zmq.proxy(ins, outs)`。源：`zmq/devices/basedevice.py:15-237`
- **F-112**：`ThreadDevice` 用 `threading.Thread` 在后台运行 Device，`ProcessDevice` 用 `multiprocessing.Process` 且 `context_factory = Context`（而非 `Context.instance`）以避免 fork 后复用父进程 Context。源：`zmq/devices/basedevice.py:273-307`
- **F-113**：`ProxyBase` 增加第三个监控 socket（`mon_type`，默认 PUB），提供 `bind_mon/connect_mon/setsockopt_mon`；`run_device` 调用 `zmq.proxy(ins, outs, mons)`；`Proxy/ThreadProxy/ProcessProxy` 通过多继承组合 ProxyBase 与 Device/ThreadDevice/ProcessDevice。源：`zmq/devices/proxydevice.py:10-103`
- **F-114**：`PUBHandler` 继承 `logging.Handler`，构造时接受已有 PUB socket 或地址字符串（后者内部创建 Context+PUB socket 并 bind）；`emit` 把日志记录格式化为 `[root_topic.]LEVEL[.subtopic]` 主题与消息体的两帧 multipart 消息，通过 `socket.send_multipart([btopic, bmsg])` 发布。源：`zmq/log/handlers.py:81-215`
- **F-115**：`PUBHandler.formatters` 是按日志级别（DEBUG/INFO/WARN/ERROR/CRITICAL）映射到不同 Formatter 的字典；`setFormatter(fmt, level=NOTSET)` 可单独设置某级别或全部级别的格式。源：`zmq/log/handlers.py:104-130,164-182`
- **F-116**：`TopicLogger` 继承 `logging.Logger`，所有 log 方法签名变为 `(level, topic, msg, ...)`，内部把 `topic + "::" + msg` 传给基类方法，配合 PUBHandler 中 `str(record.msg).split("::", 1)` 解析子主题。源：`zmq/log/handlers.py:218-281`
- **F-117**：`zmq.utils.jsonapi.dumps(o, **kwargs)` = `json.dumps(o, **kwargs).encode("utf8")`，`loads(s, **kwargs)` 接受 bytes/str，bytes 先 utf8 解码再 `json.loads`；pyzmq 22.2 起不再尝试可选 JSON 库，无条件用标准库。源：`zmq/utils/jsonapi.py:20-35`
- **F-118**：`zmq.utils.strtypes` 自 pyzmq 23 起废弃，提供 `cast_bytes`/`cast_unicode` 及别名 `b`/`u`，并显式声明 `bytes = bytes`、`unicode = str`、`basestring = (str,)` 以兼容旧代码。源：`zmq/utils/strtypes.py:15-53`

## 事实统计

- 总计：**118 条**编号事实（F-001 ~ F-118）
- 覆盖文件：`zmq/__init__.py`、`zmq/sugar/`（6 文件）、`zmq/_future.py`、`zmq/asyncio.py`、`zmq/backend/`（含 cffi 5 文件）、`zmq/constants.py`、`zmq/error.py`、`zmq/decorators.py`、`zmq/auth/`（5 文件）、`zmq/eventloop/`（4 文件）、`zmq/green/`（3 文件）、`zmq/devices/`（3 文件）、`zmq/log/handlers.py`、`zmq/utils/`（2 文件）
