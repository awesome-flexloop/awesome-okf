---
type: Example
title: Python SDK 使用
description: >
  openai-codex Python SDK 的安装与使用示例：同步/异步客户端、线程管理、
  turn 执行、流式进度、认证、沙箱控制与程序化 agent 构建。
tags: [openai-codex, python, sdk, api, async, programmatic, examples]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Python SDK 使用

本文展示 `openai-codex` Python SDK 的常见使用模式。SDK 提供同步和异步两种客户端，通过子进程 JSON-RPC 驱动 Codex Rust 二进制。

## 安装

```bash
pip install openai-codex
```

SDK 会自动安装固定版本的 `openai-codex-cli-bin`（Rust 二进制）作为依赖。要求 Python 3.10+。

## 快速开始

### 最小示例

```python
from openai_codex import Codex

with Codex() as codex:
    thread = codex.thread_start()
    result = thread.run("Explain this repository in three bullets.")
    print(result.final_response)
```

`thread.run()` 返回 `TurnResult`，包含：
- `final_response`：agent 的最终文本回复
- `items`：收集到的响应项
- `token_usage`：token 使用统计

### 异步版本

```python
import asyncio
from openai_codex import AsyncCodex

async def main():
    async with AsyncCodex() as codex:
        thread = await codex.thread_start()
        result = await thread.run("Summarize the README.")
        print(result.final_response)

asyncio.run(main())
```

## 认证

SDK 自动复用已有的 Codex 认证。也可显式登录：

### ChatGPT 浏览器登录

```python
from openai_codex import Codex

with Codex() as codex:
    login = codex.login_chatgpt()
    print(f"Open this URL to log in: {login.auth_url}")
    result = login.wait()
    print(f"Login successful: {result.success}")
```

### 设备码登录

```python
with Codex() as codex:
    login = codex.login_chatgpt_device_code()
    print(f"Visit: {login.verification_url}")
    print(f"Enter code: {login.user_code}")
    login.wait()
```

### API Key

```python
with Codex() as codex:
    codex.login_api_key("sk-your-api-key-here")
```

## 沙箱控制

通过 `Sandbox` 枚举控制文件系统访问级别：

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    # 只读：agent 可以读文件但不能修改
    thread = codex.thread_start(sandbox=Sandbox.read_only)
    result = thread.run("What version of React is in package.json?")

    # 工作区可写（默认）：可以修改工作区内的文件
    thread2 = codex.thread_start(sandbox=Sandbox.workspace_write)
    result2 = thread2.run("Fix all TypeScript errors")

    # 完全访问：无文件系统限制（谨慎使用）
    thread3 = codex.thread_start(sandbox=Sandbox.full_access)
    result3 = thread3.run("Run npm install and fix any peer dependency issues")
```

## 输入类型

### 纯文本

```python
from openai_codex import TextInput

result = thread.run(TextInput("Write a function to sort a list"))
```

### 多模态输入

```python
from openai_codex import Input, TextInput, LocalImageInput

result = thread.run(Input([
    TextInput("Describe what's in this screenshot and suggest UI improvements"),
    LocalImageInput(path="./screenshot.png"),
]))
```

### Skill 调用

```python
from openai_codex import SkillInput, TextInput

result = thread.run(Input([
    SkillInput(name="test-tui"),
    TextInput("Run the TUI test skill"),
]))
```

### Mention 输入

```python
from openai_codex import MentionInput

result = thread.run(MentionInput(
    plugin_id="my-plugin",
    mention="@my-tool",
))
```

## 线程管理

### 列出线程

```python
with Codex() as codex:
    response = codex.thread_list()
    for thread in response.threads:
        print(f"{thread.id}: {thread.title or '(untitled)'}")
```

### 恢复已有线程

```python
thread = codex.thread_resume(thread_id="abc-123")
result = thread.run("Continue from where we left off")
```

### 分叉线程

基于已有线程创建新的对话分支：

```python
forked = codex.thread_fork(thread_id="abc-123")
result = forked.run("Try a different approach instead")
```

### 归档与删除

```python
codex.thread_archive(thread_id="abc-123")
codex.thread_unarchive(thread_id="abc-123")
codex.thread_delete(thread_id="abc-123")
```

### 设置线程名称

```python
codex.thread_set_name(thread_id="abc-123", name="Auth refactoring")
```

## 流式获取进度

使用 `TurnHandle` 实时获取 agent 的输出和事件：

```python
with Codex() as codex:
    thread = codex.thread_start()

    with thread.run_stream("Write a Python web scraper") as handle:
        for event in handle:
            # 处理流式事件（agent 消息增量、工具调用等）
            print(event)

    result = handle.result
    print(result.final_response)
```

异步版本：

```python
async with AsyncCodex() as codex:
    thread = await codex.thread_start()

    async with thread.run_stream("Explain async/await") as handle:
        async for event in handle:
            print(event)

    result = await handle.result
```

## 审批模式

控制 agent 执行操作时的审批行为：

```python
from openai_codex import ApprovalMode

# 自动批准安全操作
thread = codex.thread_start(approval_mode=ApprovalMode.auto)

# 每次操作都询问
thread = codex.thread_start(approval_mode=ApprovalMode.always_ask)

# 永不批准（只读探索）
thread = codex.thread_start(approval_mode=ApprovalMode.never)
```

## 配置 CodexConfig

通过 `CodexConfig` 自定义二进制路径和其他设置：

```python
from openai_codex import Codex, CodexConfig

config = CodexConfig(
    codex_bin="/usr/local/bin/codex",  # 自定义二进制路径
)

with Codex(config=config) as codex:
    print(codex.metadata)  # 访问 initialize 响应元数据
```

## 错误处理

```python
from openai_codex import (
    Codex,
    CodexError,
    TransportClosedError,
    ServerBusyError,
    RetryLimitExceededError,
    retry_on_overload,
)

try:
    with Codex() as codex:
        thread = codex.thread_start()
        result = thread.run("hello")
except ServerBusyError:
    print("Server is overloaded, please retry later")
except RetryLimitExceededError:
    print("Max retries exceeded")
except TransportClosedError:
    print("Connection to codex binary lost")
except CodexError as e:
    print(f"Codex error: {e}")
```

### 自动重试

使用 `retry_on_overload` 装饰器自动处理服务器重载：

```python
@retry_on_overload(max_retries=3)
def run_agent(prompt: str):
    with Codex() as codex:
        thread = codex.thread_start()
        return thread.run(prompt)
```

## 完整示例：代码审查工具

```python
from openai_codex import Codex, Sandbox, Input, TextInput
import subprocess

def review_changes():
    diff = subprocess.check_output(["git", "diff", "--staged"], text=True)

    with Codex() as codex:
        thread = codex.thread_start(sandbox=Sandbox.read_only)
        result = thread.run(Input([
            TextInput(
                "Review the following staged git diff. "
                "Identify bugs, security issues, and style problems. "
                "Be concise.\n\n"
                f"```diff\n{diff}\n```"
            ),
        ]))
        return result.final_response

if __name__ == "__main__":
    print(review_changes())
```

## 完整示例：批量文件处理

```python
import asyncio
from openai_codex import AsyncCodex, Sandbox

async def process_file(codex: AsyncCodex, filepath: str):
    thread = await codex.thread_start(sandbox=Sandbox.workspace_write)
    result = await thread.run(f"Add docstrings to all public functions in {filepath}")
    return filepath, result.final_response

async def main():
    files = ["src/auth.py", "src/api.py", "src/models.py"]
    async with AsyncCodex() as codex:
        tasks = [process_file(codex, f) for f in files]
        results = await asyncio.gather(*tasks)
        for filepath, response in results:
            print(f"=== {filepath} ===")
            print(response)

asyncio.run(main())
```

## 获取帮助

```python
import openai_codex

help(openai_codex)
help(openai_codex.Codex)
help(openai_codex.Thread)
```

或在命令行：

```bash
python -m pydoc openai_codex
python -m pydoc openai_codex.Codex
```

## 相关示例

- [CLI 基本使用](01-basic-usage.md)

## 相关概念

- [Python SDK](../concepts/06-python-sdk.md)
- [Rust 核心与 TUI](../concepts/02-rust-core-tui.md)
- [沙箱执行模型](../concepts/04-sandbox-execution.md)
- [工作区架构](../concepts/01-workspace-architecture.md)
