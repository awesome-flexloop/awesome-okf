---
type: reference
scope: deep-ep
name: 事件系统
version: "2.1.0"
source: deep_ep/utils/event.py, deep_ep/_C (EventHandle)
description: EventOverlap 和 EventHandle 事件系统 API，用于计算-通信重叠、CUDA 流同步和钩子注册
---

# 事件系统 API 参考

DeepEP 的事件系统由两个类构成：
- **`EventHandle`**：C 扩展层封装的底层 CUDA 事件句柄，从 `deep_ep._C` 导入
- **`EventOverlap`**：Python 层包装器，提供上下文管理器语法、回调钩子和自动流等待，是用户主要交互的接口

## EventOverlap 类

定义在 `deep_ep/utils/event.py:8-96`。

### 构造函数

```python
EventOverlap(
    event: Optional[EventHandle] = None,
    extra_tensors: Optional[Tuple[torch.Tensor, ...]] = None,
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `event` | `Optional[EventHandle]` | 底层 CUDA 事件句柄；为 None 时需要后续设置 |
| `extra_tensors` | `Optional[Tuple[torch.Tensor, ...]]` | 额外张量元组，用于模拟 `record_stream`（兼容 CUDA Graph） |

### 核心方法

#### current_stream_wait()

```python
event_overlap.current_stream_wait(release_handle: bool = False) -> None
```

让当前流（`torch.cuda.current_stream()`）等待事件完成。

执行流程：
1. 调用 `self.event.current_stream_wait()` 插入流等待
2. 若注册了 `hook_after_wait` 回调，在等待后执行回调并清空
3. 若 `release_handle=True`，等待后释放事件引用（`self.event = None`）

**注意**：V2 中 `EventHandle` 内部也存储了需要记录流的张量，等待后删除 `self.event` 即可释放这些张量。但多流等待场景建议手动管理生命周期。

#### register_hook_after_wait()

```python
event_overlap.register_hook_after_wait(hook_after_wait: Callable) -> None
```

注册在 `current_stream_wait()` 后执行的回调。同一实例只能注册一个回调（重复注册会 assert 失败）。

典型用途：确定性 dispatch 排序——dispatch 内核在通信流上执行，排序在当前流上等待通信完成后执行，通过钩子自动插入排序操作。

### 上下文管理器支持

`EventOverlap` 支持 Python `with` 语法：

```python
with event_overlap:
    # 此代码块在当前流上执行
    # 退出 with 时自动调用 current_stream_wait()
    do_something()
```

进入 `__enter__` 返回 `self`；退出 `__exit__` 时若 `self.event is not None`，调用 `current_stream_wait(release_handle=self._release_handle_by_call)`。

### __call__() 配置 release_handle

```python
event_overlap(release_handle: bool = False) -> EventOverlap
```

配置上下文管理器使用时的 `release_handle` 行为，返回 `self`（不创建新包装对象）：

```python
with event_overlap(release_handle=True):
    expert_output = expert_forward(recv_x)
# 退出后事件句柄自动释放
```

### 内部状态

| 属性 | 类型 | 说明 |
|------|------|------|
| `event` | `Optional[EventHandle]` | 底层 CUDA 事件 |
| `extra_tensors` | `Optional[Tuple[Tensor, ...]]` | 额外张量（V2 中已较少使用） |
| `hook_after_wait` | `Optional[Callable]` | 等待后回调（单次执行） |
| `_release_handle_by_call` | `bool` | __call__ 设置的 release_handle 标志 |

---

## EventHandle 类

`EventHandle` 是 C 扩展导出的底层 CUDA 事件句柄类，封装 CUDA 事件的记录、等待和资源管理。

### 主要方法（C++ 绑定）

| 方法 | 说明 |
|------|------|
| `current_stream_wait()` | 让当前 CUDA 流等待此事件 |
| `record(stream)` | 在指定流上记录事件 |
| `sync()` | CPU 侧阻塞等待事件完成 |

ElasticBuffer 的 `capture()` 静态方法创建 EventHandle：

```python
# ElasticBuffer.capture() 等价于
EventHandle()  # 在当前流上捕获事件
```

---

## 典型使用模式

### 模式 1：基本计算-通信重叠

```python
# Dispatch 在通信流上执行（非阻塞）
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx, ...)

# 当前流可以做不依赖 recv_x 的工作
prepare_next_batch()

# 等待 dispatch 完成后使用 recv_x
with event:
    expert_output = expert_model(recv_x)
```

### 模式 2：链式事件等待

```python
# 前一个通信事件完成后才开始下一个
event1 = buffer.dispatch(x1, ...)[-1]
recv_x2, _, _, handle2, event2 = buffer.dispatch(
    x2, ..., previous_event=event1.event
)
```

### 模式 3：钩子回调

```python
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx, ...)
event.register_hook_after_wait(lambda: print("dispatch 完成"))
with event:
    output = expert_model(recv_x)  # 等待后先执行钩子，再执行此行
```

### 模式 4：异步模式

```python
# async_with_compute_stream=True：dispatch 不阻塞计算流
recv_x, _, _, handle, event = buffer.dispatch(
    x, topk_idx, ..., async_with_compute_stream=True
)
# 计算流继续执行，需要 recv_x 时显式等待
event.current_stream_wait()
```

---

## 相关参考

- [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic)
- [计算-通信重叠示例](/deepseek/deep-ep/examples/event-overlap)
- [Dispatch/Combine 概念](/deepseek/deep-ep/concepts/dispatch-combine)
