---
okf_version: "0.2"
type: example
title: "多内核并行执行"
description: "使用 MultiKernelManager 启动多个内核并行执行代码、AsyncMultiKernelManager 异步并发管理内核"
tags: ["multi-kernel", "parallel-execution", "multikernelmanager", "async-multi-kernel", "concurrent"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: multi-kernel-manager
    resource: /concepts/07-multi-kernel-manager.md
    title: 多内核管理
  - id: async-threading
    resource: /concepts/11-async-and-threading.md
    title: 异步与线程模型
---

# 多内核并行执行

本例演示使用 `MultiKernelManager` 同时管理多个内核实例，实现并行代码执行。包括同步多内核管理和异步并发管理两种方式。

## 示例代码

```python
"""
jupyter_client 多内核并行执行示例
演示 MultiKernelManager 和 AsyncMultiKernelManager 的使用
"""
import concurrent.futures
import time


# ============ 示例1: 同步 MultiKernelManager ============

def example_sync_multi_kernel():
    """使用 MultiKernelManager 同步管理多个内核"""
    from jupyter_client import MultiKernelManager

    print("=== 同步多内核示例 ===\n")

    mkm = MultiKernelManager()

    try:
        # 启动3个Python内核
        kernel_ids = []
        for i in range(3):
            kid = mkm.start_kernel(kernel_name="python3")
            kernel_ids.append(kid)
            print(f"Started kernel {i}: {kid}")

        print(f"\nActive kernels: {mkm.list_kernel_ids()}\n")

        # 在每个内核中执行不同的任务
        tasks = [
            ("kernel-0", "import time; time.sleep(1); result = 'A'" ),
            ("kernel-1", "import time; time.sleep(2); result = 'B'" ),
            ("kernel-2", "import time; time.sleep(1); result = 'C'" ),
        ]

        # 顺序执行（对比）
        print("--- 顺序执行 ---")
        start = time.time()
        for kid, code in zip(kernel_ids, [t[1] for t in tasks]):
            kc = mkm.client(kid)
            kc.start_channels()
            kc.wait_for_ready(timeout=10)
            msg_id = kc.execute(code)
            while True:
                msg = kc.get_iopub_msg(timeout=10)
                if (msg["parent_header"].get("msg_id") == msg_id and
                    msg["header"]["msg_type"] == "status" and
                    msg["content"]["execution_state"] == "idle"):
                    break
            reply = kc.get_shell_msg(timeout=5)
            kc.stop_channels()
        print(f"Sequential time: {time.time() - start:.2f}s")

        # 使用线程池并行执行
        print("\n--- 并行执行（线程池）---")

        def run_on_kernel(kid, code):
            kc = mkm.client(kid)
            kc.start_channels()
            kc.wait_for_ready(timeout=10)
            msg_id = kc.execute(code)
            while True:
                msg = kc.get_iopub_msg(timeout=10)
                if (msg["parent_header"].get("msg_id") == msg_id and
                    msg["header"]["msg_type"] == "status" and
                    msg["content"]["execution_state"] == "idle"):
                    break
            reply = kc.get_shell_msg(timeout=5)
            kc.stop_channels()
            return reply["content"]["status"]

        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = {
                pool.submit(run_on_kernel, kid, code): name
                for (name, code), kid in zip(tasks, kernel_ids)
            }
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                status = future.result()
                elapsed = time.time() - start
                print(f"  {name} finished in {elapsed:.2f}s, status={status}")

        print(f"Parallel total time: {time.time() - start:.2f}s")
        # 注意：并行执行总时间应该约等于最慢任务的时间（~2s）而非总时间（~4s）

    finally:
        mkm.shutdown_all(now=True)
        print("\nAll kernels shut down.")


# ============ 示例2: 异步 AsyncMultiKernelManager ============

def example_async_multi_kernel():
    """使用 AsyncMultiKernelManager 异步管理多个内核"""
    import asyncio
    from jupyter_client import AsyncMultiKernelManager

    print("\n=== 异步多内核示例 ===\n")

    async def execute_on_kernel(km, code, kernel_id):
        """在指定内核上执行代码"""
        kc = km.client(kernel_id)
        kc.start_channels()
        try:
            await kc._async_wait_for_ready(timeout=10)
            msg_id = kc.execute(code)

            while True:
                msg = await kc._async_get_iopub_msg(timeout=10)
                if (msg["parent_header"].get("msg_id") == msg_id and
                    msg["header"]["msg_type"] == "status" and
                    msg["content"]["execution_state"] == "idle"):
                    break
            reply = await kc._async_get_shell_msg(timeout=5)
            return reply["content"]["status"]
        finally:
            kc.stop_channels()

    async def main():
        mkm = AsyncMultiKernelManager()
        try:
            # 并发启动多个内核
            print("Starting kernels...")
            start = time.time()
            kernel_ids = await asyncio.gather(
                mkm.start_kernel(kernel_name="python3"),
                mkm.start_kernel(kernel_name="python3"),
                mkm.start_kernel(kernel_name="python3"),
            )
            print(f"Started 3 kernels in {time.time() - start:.2f}s")
            print(f"Kernel IDs: {kernel_ids}")

            # 并发执行代码
            codes = [
                "import time; time.sleep(1); 'task1 done'",
                "import time; time.sleep(2); 'task2 done'",
                "import time; time.sleep(1); 'task3 done'",
            ]

            print("\nExecuting code concurrently...")
            start = time.time()
            results = await asyncio.gather(*[
                execute_on_kernel(mkm, code, kid)
                for code, kid in zip(codes, kernel_ids)
            ])
            elapsed = time.time() - start
            print(f"All tasks completed in {elapsed:.2f}s")
            print(f"Results: {results}")
            # 总时间应约为最慢任务时间（~2s）

            # 查询内核信息
            print("\nKernel info:")
            for kid in kernel_ids:
                info = mkm.kernel_info(kid)
                print(f"  {kid[:8]}...: name={info['name']}")

        finally:
            await mkm.shutdown_all(now=True)
            print("\nAll kernels shut down.")

    asyncio.run(main())


# ============ 示例3: 内核信息查询 ============

def example_kernel_info():
    """演示内核信息查询"""
    from jupyter_client import MultiKernelManager

    print("\n=== 内核信息查询示例 ===\n")

    mkm = MultiKernelManager()
    try:
        kid1 = mkm.start_kernel(kernel_name="python3")
        kid2 = mkm.start_kernel(kernel_name="python3")

        # 列出所有内核
        print(f"Total kernels: {len(mkm.list_kernel_ids())}")
        for kid in mkm.list_kernel_ids():
            info = mkm.kernel_info(kid)
            print(f"  Kernel: {info['id'][:8]}...")
            print(f"    Name: {info['name']}")

        # 关闭一个内核
        mkm.shutdown_kernel(kid1)
        print(f"\nAfter shutting down one kernel: {len(mkm.list_kernel_ids())} remaining")

    finally:
        mkm.shutdown_all(now=True)


if __name__ == "__main__":
    example_sync_multi_kernel()
    example_async_multi_kernel()
    example_kernel_info()
```

## 预期输出

```
=== 同步多内核示例 ===

Started kernel 0: abc123...
Started kernel 1: def456...
Started kernel 2: ghi789...

Active kernels: ['abc123...', 'def456...', 'ghi789...']

--- 顺序执行 ---
Sequential time: 4.xx s

--- 并行执行（线程池）---
  kernel-0 finished in 1.xx s, status=ok
  kernel-2 finished in 1.xx s, status=ok
  kernel-1 finished in 2.xx s, status=ok
Parallel total time: 2.xx s

All kernels shut down.

=== 异步多内核示例 ===

Starting kernels...
Started 3 kernels in 1.xx s
Kernel IDs: ['...', '...', '...']

Executing code concurrently...
All tasks completed in 2.xx s
Results: ['ok', 'ok', 'ok']

Kernel info:
  ...: name=python3
  ...: name=python3
  ...: name=python3

All kernels shut down.
```

## 关键点说明

### 同步 vs 异步多内核

| 特性 | MultiKernelManager | AsyncMultiKernelManager |
|------|-------------------|------------------------|
| 启动内核 | 阻塞，顺序启动 | `await asyncio.gather()` 并发启动 |
| 执行代码 | 需要线程池实现并行 | `await asyncio.gather()` 原生并发 |
| 关闭内核 | `shutdown_all()` 阻塞 | `await shutdown_all()` 异步 |
| 线程安全 | 每个 KernelManager 独立 | 单 event loop 线程 |

### 并行执行原理

- **同步并行**：每个内核的 client 在线程池中独立运行，每个线程有自己的 ZMQ socket，互不干扰（ZMQ Context 线程安全，Socket 不共享）
- **异步并发**：在同一个 event loop 中使用 `asyncio.gather()` 等待多个内核的消息，通过 `zmq.asyncio.Poller` 多路复用

### 线程安全注意

每个 `KernelClient` 实例只在创建它的线程中使用。多线程场景下，每个线程创建自己的 client：

```python
def worker(kernel_id):
    kc = mkm.client(kernel_id)  # 每个线程独立的 client
    kc.start_channels()
    # ... 使用 kc ...
    kc.stop_channels()
```

不要在多个线程间共享同一个 KernelClient 实例。

### 资源清理

- `shutdown_all(now=True)` 强制关闭所有内核
- 建议使用 try/finally 确保清理
- MultiKernelManager 的 `__del__` 和 atexit 注册提供兜底清理

## 相关文档

- [多内核管理](../concepts/07-multi-kernel-manager.md)
- [异步与线程模型](../concepts/11-async-and-threading.md)
- [内核管理器](../concepts/06-kernel-manager.md)
