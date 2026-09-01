---
type: Concept
title: 生命周期阶段
description: Module的prepare/start/stop三阶段生命周期详解，阶段并行协调机制、done()的正确用法、超时控制和后台任务处理。
tags: [lifecycle, prepare, start, stop, phases, done, timeout]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
---

## 三阶段模型

每个Module经历三个串行生命周期阶段：

```
prepare → start → [运行中] → stop
```

| 阶段 | 方法 | 典型用途 | 阶段完成条件 |
|------|------|---------|-------------|
| **prepare** | `prepare()` | 注册路由、获取框架资源、初始化配置 | 所有子模块prepare完成 + 当前模块prepared Event被设置 |
| **start** | `start()` | 发布服务、启动后台任务、执行业务逻辑 | 所有子模块start完成 + 当前模块started Event被设置 |
| **stop** | `stop()` | 停止后台任务、释放资源 | 所有子模块stop完成 + 当前模块stopped Event被设置 |

三个阶段之间是**全屏障同步**：必须等所有模块完成当前阶段后，才统一进入下一阶段。

## 阶段执行流程

### prepare阶段

1. 根模块进入 `__aenter__`，调用 `initialize()` 递归实例化所有子模块
2. 创建 `AsyncExitStack` 和 `create_task_group()`
3. 设置 `_phase = "preparing"`
4. 为每个子模块设置 `_task_group`、`_phase`、`_exceptions`，并行启动所有子模块的 `_prepare()` 任务
5. 同时启动当前模块的 `_prepare_and_done()` 任务
6. 等待 `_all_prepared()`（递归等待所有子模块和自身的 `prepared` Event）
7. 如果超时，为未完成模块添加TimeoutError

### start阶段

1. 设置 `_phase = "starting"`
2. 并行启动所有子模块的 `_start()` 和自身的 `_start_and_done()`
3. 等待 `_all_started()`
4. 超时处理同上
5. 如果无异常，打印 `"Application running"` 日志

### stop阶段

1. 设置 `_phase = "stopping"`
2. **先逆序执行**所有 `_context_manager_exits` 退出回调
3. 并行启动子模块的 `_stop()` 和自身的 `_stop_and_done()`
4. 等待 `_all_stopped()`
5. 设置 `_exit` Event，cancel task group
6. 关闭 `AsyncExitStack`
7. 打印异常日志和 `"Application stopped"`

## done()：标记阶段完成

`done()` 方法是阶段完成的关键：

```python
def done(self) -> None:
    if self._phase == "preparing":
        self.prepared.set()
    elif self._phase == "starting":
        self.started.set()
    else:  # stopping
        self._is_stopping = True
        self._task_group.start_soon(self._finish)
```

### 自动调用done

框架的 `_prepare_and_done()` 和 `_start_and_done()` 方法在调用用户的 `prepare()`/`start()` 后，如果对应的Event尚未设置，会**自动调用 `done()`**。

这意味着：
- 如果你的 `prepare()`/`start()`/`stop()` 是同步执行完就返回的普通方法（不启动长驻任务），你**不需要**调用 `done()`——框架会自动标记阶段完成
- 如果你的方法启动了**后台任务**（如服务器、事件循环），必须**显式调用 `self.done()`**

### 后台任务必须调用done

错误写法（会超时）：

```python
class MyModule(Module):
    async def start(self):
        # ❌ 这个方法永远不会返回，start阶段永远无法完成
        await anyio.sleep(float("inf"))
```

正确写法：

```python
class MyModule(Module):
    async def start(self):
        async with anyio.create_task_group() as tg:
            tg.start_soon(self.long_running_task)
            self.done()  # ✅ 立即标记start阶段完成

    async def long_running_task(self):
        await anyio.sleep(float("inf"))
```

核心规则：**启动后台任务后立即调用 `done()`**，让框架知道当前模块已"就绪"。

## prepare阶段的特殊用途

prepare阶段在start阶段之前执行，主要用于需要在服务启动前完成的操作。最典型的场景是**路由注册**：

- `FastAPIModule` 在prepare阶段发布FastAPI app实例
- Router模块在prepare阶段获取app并注册路由
- `ServerModule` 在start阶段获取app并启动服务器

这样保证了：所有路由注册完成后，服务器才开始监听请求。

```python
class RouterModule(Module):
    async def prepare(self):
        # prepare阶段：注册路由（此时服务器尚未启动）
        app = await self.get(FastAPI)

        @app.get("/")
        def read_root():
            return {"Hello": "World"}

    # 不需要start/stop方法，框架自动标记完成
```

## 超时控制

### 默认超时

每个阶段默认超时1秒。如果模块的生命周期方法在超时时间内未完成（既没有return也没有调用done()），框架会为该模块添加 `TimeoutError` 到异常列表。

### 配置超时

```python
class MyModule(Module):
    def __init__(self, name):
        super().__init__(
            name,
            prepare_timeout=5.0,   # prepare阶段5秒超时
            start_timeout=10.0,    # start阶段10秒超时
            stop_timeout=3.0,      # stop阶段3秒超时
        )
```

或使用全局启动超时（覆盖prepare+start总时间）：

```python
root_module = MyApp("app")
root_module._global_start_timeout = 30.0
root_module.run()
```

CLI参数设置超时：

```bash
fps myapp:Main --timeout 30 --stop-timeout 5
```

### 超时错误信息

超时错误会明确指出哪个模块在哪个阶段超时：

```
TimeoutError: Module timed out while starting: root_module.database
```

## 异常处理

如果任何模块在prepare或start阶段抛出异常：
1. 异常被捕获并添加到 `_exceptions` 列表
2. 设置 `_exit` Event触发应用关闭
3. stop阶段仍会执行（清理资源）
4. 退出时打印所有异常的critical级别日志

stop阶段的异常同样被收集但不会阻止其他模块的停止流程。

## 后台任务与生命周期

启动后台任务的标准模式：

```python
class ServerModule(Module):
    async def start(self):
        app = await self.get(FastAPI)

        async with anyio.create_task_group() as tg:
            # 启动服务器（长驻任务）
            server_task = await tg.start(
                partial(serve, app, config, shutdown_trigger=..., mode="asgi"),
                return_handle=True,
            )

            async def stop_server():
                self.shutdown_event.set()
                await server_task

            # 注册停止时的清理回调
            self.add_teardown_callback(stop_server)
            self.done()  # 标记start阶段完成
```

关键要点：
1. 后台任务必须在 `create_task_group` 内启动
2. 启动后立即调用 `self.done()` 通知框架当前模块已就绪
3. 通过 `add_teardown_callback` 注册停止逻辑
4. 停止回调负责触发shutdown_event并等待server任务结束

## 停止流程细节

stop阶段的执行顺序：

1. 先逆序执行所有 `_context_manager_exits`（通过 `context_manager()`/`async_context_manager()` 注册的同步/异步上下文管理器的 `__exit__`/`__aexit__`）
2. 并行执行所有子模块的 `_stop()` 任务
3. 各模块的 `_stop_and_done()` 调用用户的 `stop()` 方法
4. `_drop_and_wait_values()`：drop所有acquired values → 关闭Context（关闭SharedValues → 执行teardown callbacks）→ 设置stopped Event
5. 等待所有模块stopped
6. 取消task group，关闭exit stack

这保证了资源的优雅关闭：先停止接收新工作 → 等待进行中的任务完成 → 释放借用资源 → 执行teardown回调。

## 相关概念

- [模块系统](02-module-system.md)
- [上下文与共享值](03-context-sharing.md)
- [可插拔Web服务器](07-web-modules.md)
- [后台任务处理模式](../examples/03-web-server.md)
