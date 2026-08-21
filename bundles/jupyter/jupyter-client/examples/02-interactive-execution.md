---
okf_version: "0.2"
type: example
title: "交互式执行与标准输入"
description: "使用 execute_interactive 处理代码输出和 stdin 输入请求、output_hook/stdin_hook 回调、input() 函数支持"
tags: ["interactive-execution", "execute-interactive", "output-hook", "stdin-hook", "input", "user-interaction"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: client-source
    resource: /references/client-source.md
    title: 客户端核心信源
  - id: channels-system
    resource: /concepts/03-channels-system.md
    title: 五通道系统
---

# 交互式执行与标准输入

本例演示 `execute_interactive()` 方法的使用，它封装了消息轮询、输出处理和 stdin 输入请求处理，是处理交互式代码执行的推荐方式。

## 示例代码

```python
"""
jupyter_client 交互式执行示例
演示 execute_interactive、output_hook 和 stdin_hook 的使用
"""
from jupyter_client import start_new_kernel
import sys


def create_output_hook(verbose=True):
    """创建输出处理钩子"""
    def output_hook(msg):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]

        if msg_type == "stream":
            # stdout/stderr 输出
            stream = content["name"]
            text = content["text"]
            if verbose:
                if stream == "stdout":
                    sys.stdout.write(f"[OUT] {text}")
                else:
                    sys.stderr.write(f"[ERR] {text}")
            else:
                sys.stdout.write(text)
                if not text.endswith("\n"):
                    sys.stdout.flush()

        elif msg_type == "execute_result":
            # 执行结果
            data = content["data"]
            if "text/plain" in data:
                print(f"[RESULT] {data['text/plain']}")

        elif msg_type == "display_data":
            # 富媒体显示
            data = content["data"]
            if "text/plain" in data:
                print(f"[DISPLAY] {data['text/plain']}")
            if "image/png" in data:
                print(f"[IMAGE] PNG data ({len(data['image/png'])} chars)")

        elif msg_type == "error":
            # 错误
            print(f"\n[ERROR] {content['ename']}: {content['evalue']}")
            for line in content.get("traceback", []):
                print(f"  {line}")

        elif msg_type == "status":
            # 状态变化
            state = content["execution_state"]
            if verbose:
                print(f"[STATUS] {state}")

        elif msg_type == "execute_input":
            # 正在执行的代码
            if verbose:
                code = content["code"][:50]
                print(f"[INPUT] Executing: {code}...")

    return output_hook


def create_stdin_hook(input_provider=None):
    """创建标准输入处理钩子"""
    if input_provider is None:
        def default_input(prompt):
            return input(prompt)
        input_provider = default_input

    def stdin_hook(msg):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]

        if msg_type == "input_request":
            # 内核请求用户输入
            prompt = content.get("prompt", "")
            password = content.get("password", False)

            if password:
                import getpass
                user_input = getpass.getpass(prompt)
            else:
                user_input = input_provider(prompt)

            # 回传输入
            kc.input(user_input)

    return stdin_hook


def main():
    print("=== 交互式执行示例 ===\n")

    # 1. 启动内核
    km, kc = start_new_kernel(kernel_name="python3", startup_timeout=30)

    try:
        # 示例1: 简单交互式执行
        print("--- 示例1: 带 output_hook 的执行 ---")
        reply = kc.execute_interactive(
            """
import sys
print("Hello from kernel!")
print("This is stdout", file=sys.stdout)
print("This is stderr", file=sys.stderr)
x = 42
x
""",
            timeout=30,
            output_hook=create_output_hook(verbose=True),
        )
        print(f"Reply status: {reply['content']['status']}")

        # 示例2: 处理 stdin 输入（input()函数）
        print("\n--- 示例2: 处理 stdin 输入 ---")
        print("（以下代码会请求输入，示例中使用预设输入）")

        # 使用预设输入而非真的等待用户输入
        presets = iter(["Alice", "30"])

        def preset_input(prompt):
            print(prompt, end="")
            try:
                val = next(presets)
                print(val)
                return val
            except StopIteration:
                return ""

        reply = kc.execute_interactive(
            """
name = input("What is your name? ")
age = input("How old are you? ")
print(f"Hello, {name}! You are {age} years old.")
""",
            timeout=30,
            output_hook=create_output_hook(verbose=False),
            stdin_hook=create_stdin_hook(preset_input),
            allow_stdin=True,
        )
        print(f"Reply status: {reply['content']['status']}")

        # 示例3: 长输出进度显示
        print("\n--- 示例3: 进度输出 ---")
        reply = kc.execute_interactive(
            """
import time
for i in range(5):
    print(f"Step {i+1}/5...", flush=True)
    time.sleep(0.5)
print("Done!")
""",
            timeout=30,
            output_hook=create_output_hook(verbose=False),
        )

        # 示例4: 错误处理
        print("\n--- 示例4: 执行错误 ---")
        reply = kc.execute_interactive(
            """
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(f"factorial(5) = {factorial(5)}")
print(f"factorial(-1) = {factorial(-1)}")
""",
            timeout=30,
            output_hook=create_output_hook(verbose=True),
        )
        print(f"Reply status: {reply['content']['status']}")

    finally:
        kc.stop_channels()
        km.shutdown_kernel()
        print("\n=== Done ===")


if __name__ == "__main__":
    main()
```

## 关键点说明

### execute_interactive 的工作原理

`execute_interactive()` 内部使用 `zmq.Poller` 同时监听 iopub 和 stdin socket：

1. 发送 execute_request 到 shell 通道
2. 创建 Poller 监听 iopub（输出消息）和 stdin（输入请求）
3. 收到 iopub 消息 → 调用 output_hook 回调
4. 收到 stdin 消息 → 调用 stdin_hook 回调
5. 收到 `status: idle` 且 parent msg_id 匹配 → 返回 shell reply

### output_hook

`output_hook` 接收原始消息字典，可以处理所有 iopub 消息类型：
- `stream`: stdout/stderr 文本输出
- `execute_result`: 执行结果（最后表达式的值）
- `display_data`: 富媒体显示（HTML/PNG/SVG等）
- `error`: 错误信息（含 traceback）
- `status`: 执行状态变化（busy/idle/starting）
- `execute_input`: 正在执行的代码（用于历史记录）
- `clear_output`: 请求清除当前输出

### stdin_hook

`stdin_hook` 处理内核发来的 `input_request` 消息：
- `content["prompt"]`: 输入提示字符串
- `content["password"]`: 是否为密码输入（应隐藏回显）
- 处理完毕后必须调用 `kc.input(user_input)` 回传用户输入

### allow_stdin 参数

执行代码时需要显式设置 `allow_stdin=True`（或设置 `kc.allow_stdin = True`），否则内核发送的 `input_request` 会被忽略。

## Poller 并发模型

`execute_interactive` 的核心轮询逻辑：

```python
poller = zmq.Poller()
poller.register(iopub_socket, zmq.POLLIN)
if allow_stdin:
    poller.register(stdin_socket, zmq.POLLIN)

while True:
    events = dict(poller.poll(timeout_ms))
    if iopub_socket in events:
        msg = iopub_channel.get_msg()
        # ... 处理输出或判断 idle 退出
    if stdin_socket in events:
        msg = stdin_channel.get_msg()
        # ... stdin_hook 处理输入请求
```

## 相关文档

- [五通道系统](../concepts/03-channels-system.md)（stdin通道）
- [客户端体系](../concepts/05-client-hierarchy.md)
- [基本代码执行](01-basic-execution.md)
