---
type: Example
title: textual 示例：@work 后台任务与 Worker.StateChanged 消息
description: 用 textual 的 @work 装饰器演示 async 与 thread 后台任务、Worker.StateChanged 消息更新界面，以及 cancel 取消与异常处理。
tags: [textualize, textual, tui, example, worker, work, async]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# textual 示例：@work 后台任务与 Worker.StateChanged 消息

## 概述

Textual 的 `Worker` 体系把耗时任务移到后台，避免阻塞 UI 主循环：`@work` 装饰的方法在实例上被调用时**立即返回一个 `Worker` 对象**并注册到 `App.workers`（`WorkerManager`），任务体则在事件循环任务（`async def`）或线程池（普通函数 + `thread=True`）中执行。Worker 每次状态变化都向所属节点投递 `Worker.StateChanged` 消息。本示例演示：

- **异步 worker**：`@work` 装饰 `async def`，用 `asyncio.sleep` 模拟分批加载，循环中直接更新 `Log`。
- **线程 worker**：`@work(thread=True)` 装饰普通阻塞函数（`time.sleep` 模拟同步阻塞），线程内更新 UI 必须经 `App.call_from_thread` 调度回主循环。
- **状态消息**：`on_worker_state_changed` 处理器按 `WorkerState`（PENDING/RUNNING/SUCCESS/CANCELLED/ERROR）更新状态 `Label`；按钮触发 `worker.cancel()`；另用一个 `exit_on_error=False` 的失败任务演示异常不退出应用。

## 可运行示例

```python
import asyncio
import time

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Label, Log
from textual.worker import Worker, WorkerState, get_current_worker


class WorkerDemo(App):
    """@work 后台任务与 Worker.StateChanged 消息示例。"""

    BINDINGS = [Binding("q", "quit", "退出")]

    CSS = """
    #title {
        margin: 1 2;
        text-style: bold;
        color: $accent;
    }
    #buttons {
        height: auto;
        margin: 0 2 1 2;
    }
    #status {
        margin: 0 2;
        text-style: bold;
    }
    #log {
        margin: 0 2;
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._current_worker: Worker | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Worker 后台任务演示", id="title")
        with Horizontal(id="buttons"):
            yield Button("异步任务（async）", id="start-async", variant="success")
            yield Button("线程任务（thread）", id="start-thread", variant="primary")
            yield Button("失败任务（exit_on_error=False）", id="start-fail", variant="warning")
            yield Button("取消当前任务", id="cancel", variant="error")
        yield Label("状态：空闲", id="status")
        yield Log(id="log")
        yield Footer()

    # ① 异步 worker：协程作为 asyncio 任务跑在事件循环里，
    #    与 UI 同线程，可直接 await、直接更新界面。
    @work(name="async-loader")
    async def load_data_async(self) -> None:
        log = self.query_one("#log", Log)
        for step in range(1, 6):
            await asyncio.sleep(0.7)  # 模拟分批异步加载
            log.write_line(f"[async] 已加载第 {step}/5 批数据")
        log.write_line("[async] 异步任务完成")

    # ② 线程 worker：普通阻塞函数在线程池执行；
    #    非协程函数必须显式 thread=True，否则装饰时抛 WorkerDeclarationError。
    @work(thread=True, name="blocking-job")
    def blocking_job(self) -> None:
        # 线程内通过 ContextVar 取到当前 Worker（用于协作式取消判断）
        worker = get_current_worker()
        log = self.query_one("#log", Log)  # 只读查询可以在线程里做
        for step in range(1, 6):
            time.sleep(0.7)  # 模拟阻塞式调用（同步 IO / 计算）
            if worker.is_cancelled:
                # 线程内不能直接碰 widget，须调度回事件循环线程
                self.app.call_from_thread(log.write_line, "[thread] 收到取消信号，提前结束")
                return
            self.app.call_from_thread(log.write_line, f"[thread] 阻塞计算第 {step}/5 步完成")
        self.app.call_from_thread(log.write_line, "[thread] 线程任务完成")

    # ③ 异常演示：exit_on_error=False 时任务抛异常只让状态变为 ERROR，
    #    默认 exit_on_error=True 会把异常交给 App._handle_exception（通常退出应用）。
    @work(exit_on_error=False, name="failing-job")
    async def failing_job(self) -> None:
        await asyncio.sleep(0.5)
        raise RuntimeError("故意抛出的异常：exit_on_error=False 时应用不会退出")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "start-async":
            # 被 @work 装饰的方法在实例上调用即启动 worker 并返回 Worker 对象
            self._current_worker = self.load_data_async()
        elif button_id == "start-thread":
            self._current_worker = self.blocking_job()
        elif button_id == "start-fail":
            self._current_worker = self.failing_job()
        elif button_id == "cancel":
            if self._current_worker is not None and not self._current_worker.is_finished:
                self._current_worker.cancel()
                self.query_one("#log", Log).write_line(
                    f"已请求取消 worker {self._current_worker.name!r}"
                )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Worker 每次状态变化都会向所属节点 post StateChanged 消息。

        该消息 bubble=False、namespace="worker"，处理器命名为
        on_worker_state_changed（与官方 docs/examples 一致）。
        """
        state_text = {
            WorkerState.PENDING: "已排队",
            WorkerState.RUNNING: "运行中",
            WorkerState.SUCCESS: "成功完成",
            WorkerState.CANCELLED: "已取消",
            WorkerState.ERROR: "出错",
        }.get(event.state, event.state.name)
        self.query_one("#status", Label).update(
            f"状态：{state_text}（worker={event.worker.name!r}）"
        )
        if event.state == WorkerState.ERROR:
            # Worker.error 保存任务抛出的异常对象
            self.query_one("#log", Log).write_line(
                f"[error] worker {event.worker.name!r} 异常：{event.worker.error!r}"
            )


if __name__ == "__main__":
    WorkerDemo().run()
```

保存为 `worker_demo.py`，运行 `python worker_demo.py`：点按钮启动三种任务观察状态 Label 与日志；任务运行中点「取消当前任务」体验协作取消；「失败任务」会在日志区打印异常但应用不退出；`q` 退出。

## 讲解

### 1. @work 装饰器：调用即启动

`work(method=None, *, name="", group="default", exit_on_error=True, exclusive=False, description=None, thread=False)` 定义于 `src/textual/_work_decorator.py:74`。装饰器在**类定义时**校验：被装饰的不是协程函数且未设 `thread=True`，立即抛 `WorkerDeclarationError`（`_work_decorator.py:112-115`）——同步阻塞任务必须显式声明线程模式。装饰后的方法在实例上调用时，内部走 `DOMNode.run_worker(...)`（`src/textual/dom.py:496`）创建并注册 `Worker`，**返回值就是 `Worker` 对象**（`_work_decorator.py:139-151`），所以本例可以 `self._current_worker = self.load_data_async()` 留存句柄。`exclusive=True` 或 `group` 同名时，新 worker 会先取消同组旧 worker（`WorkerManager.add_worker`，`worker_manager.py:75-76`）。

### 2. 两种执行体与 StateChanged 状态机

`Worker(Generic[ResultType])` 定义于 `src/textual/worker.py:119`，构造签名 `__init__(node, work, *, name="", group="default", description="", exit_on_error=True, thread=False)`，构造末尾即 `post_message(StateChanged(self, PENDING))`（`worker.py:183`）；状态属性 `state` 的 setter 在变化时投递 `Worker.StateChanged(Message, bubble=False, namespace="worker")`（`worker.py:123/207-208`），消息携带 `worker` 与 `state` 字段。状态枚举 `WorkerState`：`PENDING=1 / RUNNING=2 / CANCELLED=3 / ERROR=4 / SUCCESS=5`（`worker.py:82-94`）。`Worker.run()`（`worker.py:346`）按 `_thread_worker` 分派：`thread=True` 走 `_run_threaded()`（`loop.run_in_executor` 线程池，`worker.py:326`），否则走 `_run_async()`（事件循环任务）。线程 worker 内**不能直接更新 widget**，须用 `App.call_from_thread(callback, *args)` 调度回主循环；异步 worker 与 UI 同线程，可直接操作。

### 3. cancel、异常与 WorkerManager

- `Worker.cancel()`（`worker.py:416`）置 `_cancelled=True`、取消 asyncio 任务并 set `cancelled_event`。异步任务会在下一个 await 点收到 `CancelledError`；线程任务无法被强杀，需自行用 `get_current_worker().is_cancelled`（或 `worker.cancelled_event`）协作退出，本例线程任务每步检查一次。
- 异常处理在 `Worker._run`（`worker.py:375-384`）：任务抛异常时状态变 `ERROR` 并记录到 `worker.error`；`exit_on_error=True`（默认）会包装成 `WorkerFailed` 交给 `App._handle_exception`，通常导致应用退出；设为 `False` 则只更新状态，界面可继续运行。
- `Worker.wait()`（`worker.py:423`）在 worker 内部调用抛 `DeadlockError`、对 `PENDING` worker 调用抛 `WorkerError`、`ERROR` 抛 `WorkerFailed`、`CANCELLED` 抛 `WorkerCancelled`。
- 管理器 `WorkerManager`（`src/textual/worker_manager.py:24`）经 `App.workers`（`app.py:959`）或 `DOMNode.workers`（`dom.py:478`）访问，提供 `cancel_all()`、`cancel_group(node, group)`、`cancel_node(node)`、`wait_for_complete()` 等批量操作；节点（widget/screen/app）卸载时其名下 worker 会被自动取消。

## 相关概念

- [19 · CSS 引擎、Worker 后台任务与 Driver 驱动层](/concepts/19-textual-css-worker-driver.md)
- [14 · 消息系统：Message / MessagePump 与派发约定](/concepts/14-textual-message-system.md)
- [15 · Reactive：validate → watcher → compute → refresh 链路](/concepts/15-textual-reactive.md)
