---
type: Concept
title: 异步模式
description: open_async/send_input_async、async with、asyncio 集成——使用异步 API 并发连接多设备
tags: [scrapli, async, asyncio, concurrency, parallel]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 异步模式

scrapli2 为每个 IO 操作同时提供同步和异步方法。异步方法以 `_async` 后缀命名，基于 Python `asyncio` 事件循环实现。

## 异步上下文管理器

```python
import asyncio
from scrapli import Cli, AuthOptions, TransportBinOptions

async def main():
    async with Cli(
        host="192.168.1.1",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        result = await cli.send_input_async("show version")
        print(result.result)

asyncio.run(main())
```

`async with` 调用 `__aenter__`（内部 `await self.open_async()`）和 `__aexit__`（内部 `await self.close_async()`）。

## 异步方法清单

`Cli` 和 `Netconf` 的每个 IO 操作都有异步版本：

| 同步方法 | 异步方法 |
|---------|---------|
| `open()` | `open_async()` |
| `close()` | `close_async()` |
| `send_input()` | `send_input_async()` |
| `send_inputs()` | `send_inputs_async()` |
| `send_inputs_from_file()` | `send_inputs_from_file_async()` |
| `send_prompted_input()` | `send_prompted_input_async()` |
| `enter_mode()` | `enter_mode_async()` |
| `get_prompt()` | `get_prompt_async()` |
| `read_with_callbacks()` | `read_with_callbacks_async()` |

异步方法的签名与同步方法完全一致，返回相同的 `Result` 对象。

> **注意**：`read()`、`write()`、`write_and_return()`、`write_return()` 没有异步版本，因为它们只操作已填充的缓冲区或写入数据，不涉及等待 IO。

## 异步实现机制

异步版本并非用线程池包装同步方法。同步和异步方法共享相同的 Zig 层操作逻辑，区别仅在于等待操作完成的方式：

- **同步**：`wait_for_available_operation_result()` 使用 `select.select()` 阻塞轮询 poll fd（超时 0.1 秒）
- **异步**：`wait_for_available_operation_result_async()` 使用 `loop.add_reader()` 注册 fd 可读回调，通过 `asyncio.wait_for()` 实现超时

两种方式都通过同一个 poll fd 接收 Zig 层的完成信号（4 字节的 operation_id）。这意味着异步模式在单线程内实现真正的并发等待，不消耗线程池资源。

## 并发连接多设备

使用 `asyncio.gather()` 并发连接多台设备：

```python
import asyncio
from scrapli import Cli, AuthOptions

DEVICES = [
    "192.168.1.1",
    "192.168.1.2",
    "192.168.1.3",
]

async def connect_and_get_version(host: str) -> str:
    async with Cli(
        host=host,
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        result = await cli.send_input_async("show version")
        return f"{host}: {result.result[:80]}"

async def main():
    tasks = [connect_and_get_version(h) for h in DEVICES]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

asyncio.run(main())
```

## 异步回调

`read_with_callbacks_async()` 要求使用 `callback_async` 而非 `callback`：

```python
async def handle_prompt(cli, recent, full):
    cli.write_and_return("y")

callbacks = [
    ReadCallback(
        name="confirm",
        contains="Confirm?",
        callback_async=handle_prompt,
        completes=True,
    ),
]

result = await cli.read_with_callbacks_async(callbacks, initial_input="reload")
```

如果在异步方法中设置了同步 `callback` 而非 `callback_async`，会在运行时抛出 `OperationException("callback_async is None, cannot proceed")`。

## 异步取消

异步操作支持两种取消方式：

### Cancel 对象

```python
from scrapli.ffi_types import Cancel

cancel = Cancel()

async def monitor():
    await asyncio.sleep(5)
    cancel.cancel()

async def main():
    asyncio.create_task(monitor())
    try:
        result = await cli.send_input_async("long command", cancel=cancel)
    except CancelledException:
        print("操作被取消")
```

### asyncio 任务取消

当协程任务被 asyncio 取消时，`wait_for_available_operation_result_async` 会捕获 `CancelledError`，自动调用 `cancel.cancel()` 通知 Zig 层中止操作，然后重新抛出异常。这确保了 Zig 层的资源被正确清理。

## 异步 NETCONF

`Netconf` 的所有 RPC 方法同样有异步版本：

```python
from scrapli import Netconf, AuthOptions
from scrapli.netconf import DatastoreType

async def main():
    async with Netconf(
        host="192.168.1.1",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as nc:
        config = await nc.get_config_async(source=DatastoreType.RUNNING)
        print(config.result)

        await nc.edit_config_async(
            config="<config>...</config>",
            target=DatastoreType.CANDIDATE,
        )
        await nc.commit_async()
```

## 同步与异步混用

同一个 `Cli`/`Netconf` 实例不建议在同步和异步方法间混用。每个实例持有一个 Zig 对象指针，操作是有状态的。应为每个并发任务创建独立的驱动实例（可通过 `copy.copy(cli)` 安全复制选项配置）：

```python
import copy

cli_template = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
)

# 每个任务使用独立副本
cli1 = copy.copy(cli_template)
cli2 = copy.copy(cli_template)
```

`Cli.__copy__` 创建新的 Cli 实例但共享 options 对象（假设 options 在对象生命周期内不被修改）。

## 性能考量

- 异步模式在 IO 密集型场景（同时连接数十/数百台设备）下显著优于同步模式
- 每个连接的 Zig 层操作在独立线程中执行（由 libscrapli 管理），Python asyncio 仅负责等待完成信号
- 异步轮询间隔为 0.1 秒（`WAKEUP_FD_POLL_INTERVAL_S = 0.1`），与同步模式相同

跨束参考：
- [asyncssh 异步连接](../../asyncssh/concepts/02-async-connection.md) — 纯 asyncio SSH 库的并发模型对比
