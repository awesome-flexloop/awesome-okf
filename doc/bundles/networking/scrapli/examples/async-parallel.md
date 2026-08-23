---
type: Example
title: 异步并行连接多设备
description: 使用 asyncio 和 send_input_async 并发连接多台网络设备，收集命令输出
tags: [scrapli, example, async, asyncio, parallel, concurrency]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 异步并行连接多设备

本例演示使用 scrapli2 的异步 API 和 `asyncio.gather()` 并发连接多台设备。

## 基本并行示例

```python
import asyncio
from scrapli import Cli, AuthOptions

DEVICES = [
    "192.168.1.1",
    "192.168.1.2",
    "192.168.1.3",
    "192.168.1.4",
    "192.168.1.5",
]

async def collect_version(host: str) -> dict:
    async with Cli(
        host=host,
        definition_file_or_name="cisco_iosxe",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        result = await cli.send_input_async("show version")
        return {
            "host": host,
            "failed": result.failed,
            "output": result.result,
            "elapsed": result.elapsed_time_seconds,
        }

async def main():
    tasks = [collect_version(h) for h in DEVICES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in results:
        if isinstance(r, Exception):
            print(f"错误: {r}")
        else:
            print(f"{r['host']}: {r['elapsed']:.2f}s (failed={r['failed']})")

asyncio.run(main())
```

## 并行执行多条命令

```python
import asyncio
from scrapli import Cli, AuthOptions

async def run_commands(host: str, commands: list[str]) -> dict:
    async with Cli(
        host=host,
        definition_file_or_name="cisco_iosxe",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        result = await cli.send_inputs_async(commands)
        return {"host": host, "result": result}

async def main():
    devices_commands = {
        "192.168.1.1": ["show version", "show ip route"],
        "192.168.1.2": ["show version", "show interfaces status"],
        "192.168.1.3": ["show version", "show vlan brief"],
    }

    tasks = [run_commands(h, cmds) for h, cmds in devices_commands.items()]
    results = await asyncio.gather(*tasks)

    for r in results:
        print(f"\n=== {r['host']} ===")
        for cmd, output in zip(r["result"].inputs, r["result"].results):
            print(f"$ {cmd}")
            print(output[:200])
            print()

asyncio.run(main())
```

## 使用 Semaphore 限制并发数

当设备数量较大时，使用 `asyncio.Semaphore` 限制并发连接数：

```python
import asyncio
from scrapli import Cli, AuthOptions

MAX_CONCURRENT = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

async def connect_device(host: str) -> str:
    async with semaphore:
        async with Cli(
            host=host,
            auth_options=AuthOptions(username="admin", password="admin"),
        ) as cli:
            result = await cli.send_input_async("show version")
            return f"{host}: {result.result.splitlines()[0]}"

async def main(hosts: list[str]):
    tasks = [connect_device(h) for h in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        print(r if not isinstance(r, Exception) else f"ERROR: {r}")

asyncio.run(main([f"192.168.1.{i}" for i in range(1, 51)]))
```

## 异步 NETCONF 并行

```python
import asyncio
from scrapli import Netconf, AuthOptions
from scrapli.netconf import DatastoreType

async def get_config(host: str) -> dict:
    async with Netconf(
        host=host,
        port=830,
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as nc:
        result = await nc.get_config_async(source=DatastoreType.RUNNING)
        return {"host": host, "config": result.result}

async def main():
    hosts = ["192.168.1.1", "192.168.1.2"]
    results = await asyncio.gather(*(get_config(h) for h in hosts))
    for r in results:
        print(f"{r['host']}: {len(r['config'])} bytes config")

asyncio.run(main())
```

## 取消长时间运行的操作

```python
import asyncio
from scrapli import Cli, AuthOptions
from scrapli.ffi_types import Cancel

async def main():
    async with Cli(
        host="192.168.1.1",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        cancel = Cancel()

        async def cancel_after():
            await asyncio.sleep(5)
            cancel.cancel()

        asyncio.create_task(cancel_after())

        try:
            result = await cli.send_input_async(
                "ping 192.168.1.100 repeat 100000",
                cancel=cancel,
            )
        except Exception as e:
            print(f"操作被取消或超时: {e}")

asyncio.run(main())
```

## 异常处理

```python
import asyncio
from scrapli import Cli, AuthOptions
from scrapli.exceptions import (
    TimeoutException,
    OperationException,
    FFIException,
)

async def safe_connect(host: str) -> dict:
    try:
        async with Cli(
            host=host,
            auth_options=AuthOptions(username="admin", password="admin"),
            session_options=SessionOptions(operation_timeout_s=10),
        ) as cli:
            result = await cli.send_input_async("show version")
            return {"host": host, "status": "ok", "output": result.result}
    except TimeoutException:
        return {"host": host, "status": "timeout"}
    except OperationException as e:
        return {"host": host, "status": "operation_error", "error": str(e)}
    except FFIException as e:
        return {"host": host, "status": "connection_error", "error": str(e)}

async def main():
    results = await asyncio.gather(
        *(safe_connect(h) for h in ["192.168.1.1", "192.168.1.2", "bad-host"]),
        return_exceptions=False,
    )
    for r in results:
        print(f"{r['host']}: {r['status']}")

asyncio.run(main())
```

## 异步回调读取

`read_with_callbacks_async` 要求使用 `callback_async`：

```python
import asyncio
from scrapli import Cli, AuthOptions, ReadCallback

async def on_prompt(cli, recent, full):
    cli.write_and_return("y")

async def main():
    async with Cli(
        host="192.168.1.1",
        auth_options=AuthOptions(username="admin", password="admin"),
    ) as cli:
        callbacks = [
            ReadCallback(
                name="confirm",
                contains="Proceed?",
                callback_async=on_prompt,
                completes=True,
            ),
        ]
        result = await cli.read_with_callbacks_async(
            callbacks,
            initial_input="reload",
        )
        print(result.result)

asyncio.run(main())
```

## 性能提示

- 异步模式适合 IO 密集型场景（数十到数百台设备）
- 每个连接在 Zig 层有独立线程，Python asyncio 仅负责等待完成信号
- 使用 `return_exceptions=True` 防止单台设备失败导致全部任务取消
- 大量设备时使用 `Semaphore` 控制并发数，避免文件描述符耗尽

相关文档：
- [异步模式](../concepts/05-async-mode.md)
- [Cli 驱动详解](../concepts/04-cli-driver.md)
- [asyncssh 并行连接](../../asyncssh/examples/parallel-connections.md) — 跨束对比
