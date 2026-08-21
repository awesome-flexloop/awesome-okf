---
okf_version: "0.2"
type: example
title: "基本代码执行"
description: "使用 BlockingKernelClient 启动内核、执行代码、收集 stdout/result/error、关闭内核的完整示例"
tags: ["basic-execution", "blocking-client", "execute", "get-iopub-msg", "hello-world"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: getting-started
    resource: /concepts/01-getting-started.md
    title: 5分钟快速上手
  - id: client-hierarchy
    resource: /concepts/05-client-hierarchy.md
    title: 客户端体系
---

# 基本代码执行

本例演示使用 `BlockingKernelClient` 完成最基础的代码执行流程：启动内核 → 连接通道 → 执行代码 → 收集输出 → 关闭内核。

## 示例代码

```python
"""
jupyter_client 基本代码执行示例
使用 BlockingKernelClient 执行代码并收集所有输出
"""
from jupyter_client import KernelManager
import atexit


def execute_code(km, code: str, timeout: float = 30) -> dict:
    """执行代码并返回执行结果"""
    kc = km.client()
    kc.start_channels()
    try:
        kc.wait_for_ready(timeout=timeout)

        # 发送执行请求
        msg_id = kc.execute(code)

        # 收集输出
        outputs = []
        result = None
        error_info = None
        execution_count = None

        while True:
            msg = kc.get_iopub_msg(timeout=timeout)
            parent_id = msg["parent_header"].get("msg_id")

            # 只处理当前请求的消息
            if parent_id != msg_id:
                continue

            msg_type = msg["header"]["msg_type"]
            content = msg["content"]

            if msg_type == "stream":
                outputs.append({
                    "type": "stream",
                    "name": content["name"],
                    "text": content["text"],
                })
            elif msg_type == "execute_result":
                result = content["data"].get("text/plain", "")
                execution_count = content.get("execution_count")
            elif msg_type == "display_data":
                outputs.append({
                    "type": "display",
                    "data": content["data"],
                })
            elif msg_type == "error":
                error_info = {
                    "ename": content["ename"],
                    "evalue": content["evalue"],
                    "traceback": content["traceback"],
                }
            elif msg_type == "status" and content["execution_state"] == "idle":
                # 执行完毕
                break

        # 获取 shell reply 获取 execution_count
        reply = kc.get_shell_msg(timeout=5)
        if reply["parent_header"].get("msg_id") == msg_id:
            execution_count = reply["content"].get("execution_count", execution_count)

        return {
            "msg_id": msg_id,
            "execution_count": execution_count,
            "outputs": outputs,
            "result": result,
            "error": error_info,
            "status": "error" if error_info else "ok",
        }
    finally:
        kc.stop_channels()


def main():
    # 1. 创建内核管理器并启动内核
    km = KernelManager(kernel_name="python3")
    km.start_kernel()
    atexit.register(km.shutdown_kernel)

    # 2. 执行简单打印
    print("=== 示例1: Hello World ===")
    result = execute_code(km, "print('Hello, Jupyter!')\n2 + 2")
    print(f"Status: {result['status']}")
    for out in result["outputs"]:
        print(f"[{out['name']}] {out['text']}", end="")
    print(f"Result: {result['result']}")
    print(f"Execution count: {result['execution_count']}")

    # 3. 执行富输出（HTML/Markdown）
    print("\n=== 示例2: 富输出 ===")
    result = execute_code(km, """
from IPython.display import HTML, Markdown, display
display(Markdown("### This is **Markdown**"))
display(HTML("<p style='color:red'>This is <b>HTML</b></p>"))
42
""")
    for out in result["outputs"]:
        if out["type"] == "display":
            print(f"[display] data keys: {list(out['data'].keys())}")
    print(f"Result: {result['result']}")

    # 4. 执行错误代码
    print("\n=== 示例3: 错误处理 ===")
    result = execute_code(km, "1 / 0")
    print(f"Status: {result['status']}")
    if result["error"]:
        print(f"Error: {result['error']['ename']}: {result['error']['evalue']}")
        for tb_line in result["error"]["traceback"][-3:]:
            print(f"  {tb_line}")

    # 5. 多表达式执行
    print("\n=== 示例4: 变量持久化 ===")
    execute_code(km, "x = 10\ny = 20")
    result = execute_code(km, "x + y")
    print(f"x + y = {result['result']}")  # 30

    # 6. 清理
    km.shutdown_kernel()
    atexit.unregister(km.shutdown_kernel)
    print("\n=== Kernel shut down ===")


if __name__ == "__main__":
    main()
```

## 预期输出

```
=== 示例1: Hello World ===
Status: ok
[stdout] Hello, Jupyter!
Result: 4
Execution count: 1

=== 示例2: 富输出 ===
[display] data keys: ['text/markdown', 'text/plain']
[display] data keys: ['text/html', 'text/plain']
Result: 42

=== 示例3: 错误处理 ===
Status: error
Error: ZeroDivisionError: division by zero
  ...

=== 示例4: 变量持久化 ===
x + y = 30

=== Kernel shut down ===
```

## 关键点说明

1. **消息过滤**：通过 `parent_header.msg_id` 过滤属于当前请求的消息，避免其他请求的消息干扰
2. **idle 状态判定**：iopub 通道收到 `status: idle` 表示当前请求处理完毕
3. **shell reply**：execute_reply 通过 shell 通道获取，包含 execution_count 和 status
4. **资源清理**：使用 `atexit` 确保异常退出时内核也会被关闭
5. **内核状态**：内核在多次 execute 之间保持变量状态（同一个内核进程）

## 相关文档

- [5分钟快速上手](../concepts/01-getting-started.md)
- [客户端体系](../concepts/05-client-hierarchy.md)
- [五通道系统](../concepts/03-channels-system.md)
