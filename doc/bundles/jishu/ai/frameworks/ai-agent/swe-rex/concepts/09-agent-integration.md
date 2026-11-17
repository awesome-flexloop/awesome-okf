---
type: Concept
title: "作为 Agent 执行后端：接入模式、工具映射与并行"
description: "把 SWE-ReX 接进 agent 循环的四种模式：一次性命令、持久会话、工具调用映射、并行 worker；含错误处理、资源清理与与 mini-SWE-agent 的边界"
tags: [swe-rex, agent-integration, tool-calling, agent-loop, parallel]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:47:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-039 ~ F-068、F-094 ~ F-095"
  - id: official-docs
    resource: /references/official-docs-source.md
    title: "README 谱系与用法"
---

# 作为 Agent 执行后端：接入模式、工具映射与并行

SWE-ReX 不包含模型调用，它只提供“执行”这一半。接入 agent 时，你要做的是：把模型输出的动作翻译成 `BashAction`/`Command`，把 `BashObservation` 翻译回模型可读的观察，并管理 deployment 的生命周期。

## 四种接入模式

| 模式 | 用的方法 | 状态 | 适用 |
|---|---|---|---|
| 一次性命令 | `execute(Command)` | 无 | 安装依赖、跑测试、读版本 |
| 持久会话 | `create_session` + `run_in_session` | 有 | 多步编辑/构建、`cd`、环境变量 |
| 交互式 | `run_in_session` + `is_interactive_*` | 有 | REPL、调试器、分页器 |
| 文件同步 | `read_file`/`write_file`/`upload` | 无 | 注入补丁、取回产物 |

大多数 coding agent 用“持久会话 + 文件同步”组合：用 session 跑命令，用 `write_file` 写入模型生成的代码，用 `read_file` 取回结果。

## 最小 agent 循环

下面是一个**执行层**的完整示例。`policy` 是占位函数，代表你的模型/规则，SWE-ReX 不关心它怎么实现。

```python
import asyncio
from swerex.deployment.docker import DockerDeployment
from swerex.exceptions import CommandTimeoutError, NonZeroExitCodeError
from swerex.runtime.abstract import (
    BashAction, CreateBashSessionRequest,
)

async def run_agent(policy, task: str, max_steps: int = 20):
    deployment = DockerDeployment(image="python:3.12", startup_timeout=180)
    await deployment.start()
    runtime = deployment.runtime
    try:
        await runtime.create_session(CreateBashSessionRequest(session="main"))
        history = []
        for _ in range(max_steps):
            command = policy(task=task, history=history)   # 你的模型调用
            if command is None:
                break
            try:
                obs = await runtime.run_in_session(BashAction(
                    command=command,
                    session="main",
                    timeout=120,
                    check="raise",
                ))
                history.append({"command": command, "output": obs.output, "exit_code": obs.exit_code})
            except NonZeroExitCodeError as e:
                history.append({"command": command, "error": str(e)})
            except CommandTimeoutError as e:
                history.append({"command": command, "timeout": str(e)})
        return history
    finally:
        await deployment.stop()

asyncio.run(run_agent(policy=lambda **_: "echo hello", task="demo"))
```

关键点：

1. `start()` 必须在 `runtime` 之前；否则 `DeploymentNotStartedError`（F-017）。
2. session 名固定为 `"main"`，所有命令共享状态（F-049）。
3. `timeout` 显式设置；默认 `None` 会无限等（F-042）。
4. `check="raise"` 让非零退出码变异常；想自己处理退出码就改 `"silent"`（F-042）。
5. `finally: await deployment.stop()` 保证容器清理；`__del__` 只是兜底（F-018）。

## 工具调用映射

如果 agent 用 JSON 工具调用，通常只暴露一个 `bash` 工具：

```json
{
  "name": "bash",
  "description": "Run a shell command in the sandbox. State persists across calls.",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {"type": "string"},
      "timeout": {"type": "number", "default": 120}
    },
    "required": ["command"]
  }
}
```

执行端：

```python
async def bash_tool(runtime, command: str, timeout: float = 120) -> dict:
    try:
        obs = await runtime.run_in_session(BashAction(
            command=command, session="main", timeout=timeout, check="raise",
        ))
        return {"output": obs.output, "exit_code": obs.exit_code}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}
```

不要把 `execute` 和 `run_in_session` 混在同一个工具里：前者无状态，后者有状态；模型需要知道“这条命令是否延续之前的环境”。

## 文件注入与产物取回

```python
from swerex.runtime.abstract import (
    Command, ReadFileRequest, UploadRequest, WriteFileRequest,
)

await runtime.write_file(WriteFileRequest(path="/tmp/patch.diff", content=patch_text))
await runtime.execute(Command(command=["git", "apply", "/tmp/patch.diff"], check=True))

# 目录上传（自动 zip）
await runtime.upload(UploadRequest(source_path="./fixtures", target_path="/tmp/fixtures"))

# 读回
content = (await runtime.read_file(ReadFileRequest(path="/tmp/result.txt"))).content
```

（F-046、F-061、F-068）

注意 `write_file` 固定默认编码写入（F-061）；二进制内容用 `upload`，不要用 `write_file`。

## 并行 worker

每个任务一个 deployment，互不共享 session 与端口：

```python
async def run_one(task):
    d = DockerDeployment(image="python:3.12", startup_timeout=180)
    await d.start()
    try:
        r = d.runtime
        await r.create_session(CreateBashSessionRequest())
        return await r.run_in_session(BashAction(command=task, timeout=300))
    finally:
        await d.stop()

async def run_many(tasks, concurrency=8):
    sem = asyncio.Semaphore(concurrency)
    async def wrapped(t):
        async with sem:
            return await run_one(t)
    return await asyncio.gather(*(wrapped(t) for t in tasks))
```

（F-020、F-049、F-090）每个 deployment 独立分配端口与 token；并发上限由你的机器/云配额决定，代码没有内置池。

> README 第15行称可并行 100 个 agent（F-094），这是产品表述，不是代码常量；实际并发受容器、内存、云配额限制。

## 错误处理策略

| 场景 | 建议 |
|---|---|
| 命令失败（非零退出） | `check="raise"` + 捕获 `NonZeroExitCodeError`，把 output 回给模型 |
| 命令超时 | 捕获 `CommandTimeoutError`，回给模型；需要时发 `BashInterruptAction` |
| 语法错误 | 捕获 `BashIncorrectSyntaxError`，把 `bash_stderr` 回给模型 |
| 连接失败 | `is_alive()` 返回 false；重建 deployment 或检查网络 |
| 部署启动失败 | 看容器日志；Docker 超时会自动 stop 并打日志（F-088） |
| 多步任务中途崩溃 | `finally` 清理；不要让容器泄漏 |

## 与 mini-SWE-agent 的边界

两者都来自 SWE-agent 生态，但抽象层级不同：

| 维度 | mini-SWE-agent | SWE-ReX |
|---|---|---|
| 定位 | 极简 agent 实现（约 100 行核心） | 执行后端 |
| 执行 | 本地 subprocess / 自带环境 | 可替换的 Deployment + Runtime |
| 状态 | 线性消息历史 | 多 session、持久 shell |
| 远程 | 不是核心 | Docker/Modal/Fargate/Daytona |
| 关系 | 可用 SWE-ReX 作为执行层 | 不包含 agent 循环 |

README 第25行说明 SWE-ReX 来自 SWE-agent 与 enigma 的实践（F-095），但没有声称 mini-SWE-agent 依赖它。接入时把 SWE-ReX 当作“可替换的 shell 后端”，agent 逻辑仍由你决定。

## 什么时候不该用 SWE-ReX

1. 你的 agent 只需要一次 `subprocess.run`，没有多步状态。
2. 你已经在用某个平台的官方 SDK（E2B/Daytona/Modal），且不需要统一接口。
3. 你在 Windows 原生环境跑，且不能装 WSL/Docker——`BashSession` 依赖 `/usr/bin/env bash` 与 pexpect（F-052）。
4. 你需要强安全隔离但不想管镜像/网络——SWE-ReX 提供的是接口，不是安全策略。

## 相关概念

- [项目总览](/concepts/00-project-overview.md)
- [会话模型](/concepts/02-session-model.md)
- [运行时与执行语义](/concepts/05-runtimes-and-execution.md)
- [Agent 循环示例](/examples/04-agent-loop.md)
- [并行部署示例](/examples/05-parallel-deployments.md)
