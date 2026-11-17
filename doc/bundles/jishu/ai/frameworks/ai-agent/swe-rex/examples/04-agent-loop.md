---
type: Example
title: "示例四：把 SWE-ReX 接进 Agent 循环"
description: "一个可执行的最小 agent 执行循环：策略函数占位、BashAction 工具、异常回传、步数上限与资源清理；不依赖任何 LLM SDK"
tags: [swe-rex, example, agent-loop, tool-calling, error-handling]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:49:30+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-042、F-044、F-053、F-084"
  - id: integration-concept
    resource: /concepts/09-agent-integration.md
    title: "接入模式与工具映射"
---

# 示例四：把 SWE-ReX 接进 Agent 循环

这个例子只实现**执行侧**：一个 `policy` 占位函数代表模型，SWE-ReX 负责跑命令并把观察回传。你可以把 `policy` 换成任意 LLM 调用。

## 完整代码

```python
import asyncio
from typing import Any

from swerex.deployment.docker import DockerDeployment
from swerex.exceptions import CommandTimeoutError, NonZeroExitCodeError
from swerex.runtime.abstract import (
    BashAction,
    CreateBashSessionRequest,
)

async def run_agent(policy, task: str, max_steps: int = 20) -> list[dict[str, Any]]:
    deployment = DockerDeployment(image="python:3.12", startup_timeout=180)
    await deployment.start()
    runtime = deployment.runtime
    history: list[dict[str, Any]] = []
    try:
        await runtime.create_session(CreateBashSessionRequest(session="main"))
        for step in range(max_steps):
            command = policy(task=task, history=history)
            if command is None:
                break
            try:
                obs = await runtime.run_in_session(
                    BashAction(command=command, session="main", timeout=120, check="raise")
                )
                history.append({
                    "step": step,
                    "command": command,
                    "output": obs.output,
                    "exit_code": obs.exit_code,
                })
            except NonZeroExitCodeError as e:
                history.append({"step": step, "command": command, "error": str(e)})
            except CommandTimeoutError as e:
                history.append({"step": step, "command": command, "timeout": str(e)})
    finally:
        await deployment.stop()
    return history


def naive_policy(task: str, history: list[dict[str, Any]]) -> str | None:
    """演示用策略：只跑三条命令。真实场景替换为模型调用。"""
    commands = ["pwd", "ls -la", "python --version"]
    return commands[len(history)] if len(history) < len(commands) else None


async def main():
    result = await run_agent(naive_policy, task="inspect the workspace")
    for item in result:
        print(item)

if __name__ == "__main__":
    asyncio.run(main())
```

## 设计要点

### 1. 策略与执行分离

`policy(task, history)` 只返回下一条命令或 `None`。SWE-ReX 不关心策略是规则、LLM 还是随机；这让执行层可以单独测试（用 `DummyRuntime` 或固定策略）。

### 2. 一个 session 贯穿任务

`session="main"` 保证 `cd`、环境变量、虚拟环境激活在步骤间保留（F-049、F-100）。如果想要每步全新环境，改用 `execute`。

### 3. 异常转成观察

```python
except NonZeroExitCodeError as e:
    history.append({"error": str(e)})
```

`NonZeroExitCodeError` 的消息包含命令、退出码和输出（F-053）。对模型来说，这比“工具调用失败”更有信息量。

### 4. 超时是策略的一部分

`timeout=120` 是每条命令的上限。超时抛 `CommandTimeoutError`（F-053）。如果某类命令经常超时，可以在策略层换成 `check="silent"` + 更短 timeout，或发 `BashInterruptAction`。

### 5. 资源清理放 `finally`

`await deployment.stop()` 在异常路径也会执行；否则容器可能残留（F-018 只是兜底）。

## 运行前准备

1. 安装：`pip install swe-rex`。
2. 本机有 Docker，且当前用户能 `docker run`。
3. 首次运行会拉 `python:3.12`，需要网络。

## 预期输出

```text
{'step': 0, 'command': 'pwd', 'output': '/\n', 'exit_code': 0}
{'step': 1, 'command': 'ls -la', 'output': 'total ...\n', 'exit_code': 0}
{'step': 2, 'command': 'python --version', 'output': 'Python 3.12.x\n', 'exit_code': 0}
```

（容器内工作目录默认 `/`；实际输出随镜像变化。）

## 换成真实模型

把 `policy` 改成：

```python
def policy(task, history):
    response = my_llm(messages=build_messages(task, history), tools=[bash_tool_schema])
    return parse_bash_command(response)  # 返回字符串或 None
```

工具 schema 见 [Agent 集成](/concepts/09-agent-integration.md#工具调用映射)。SWE-ReX 不提供 `my_llm`，也不解析模型输出——这是刻意留给上层的。

## 变体：用 DummyRuntime 单测策略

```python
from swerex.deployment.dummy import DummyDeployment
from swerex.runtime.abstract import BashObservation

deployment = DummyDeployment()
deployment.runtime.run_in_session_outputs = [
    BashObservation(output="ok", exit_code=0),
    BashObservation(output="", exit_code=1),
]
```

这样可以在不启容器的情况下验证策略的状态机（F-069、F-070）。

## 相关文档

- [Agent 集成](/concepts/09-agent-integration.md)
- [会话模型](/concepts/02-session-model.md)
- [并行部署示例](/examples/05-parallel-deployments.md)
