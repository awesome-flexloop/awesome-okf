---
type: Example
title: "示例一：本地 Hello World（LocalDeployment）"
description: "用 LocalDeployment 跑通第一个 SWE-ReX 程序：一次命令、持久 session、环境变量跨调用保留；附逐行解释与预期输出"
tags: [swe-rex, example, local, quickstart, asyncio]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:48:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: usage-doc
    resource: /references/official-docs-source.md
    title: "docs/usage.md 第16-44行"
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-019、F-039 ~ F-045、F-099、F-100"
---

# 示例一：本地 Hello World（LocalDeployment）

这是官方教程的第一个例子（`docs/usage.md` 第16-44行，F-099）。它在本机直接执行命令，**没有沙箱**；只用于验证接口。

## 完整代码

```python
import asyncio

from swerex.deployment.local import LocalDeployment
from swerex.runtime.abstract import (
    BashAction,
    Command,
    CreateBashSessionRequest,
)

async def run_some_stuff(deployment):
    await deployment.start()
    runtime = deployment.runtime

    # 一次性命令：类似 subprocess.run()
    print(await runtime.execute(Command(command=["echo", "Hello, world!"])))

    # 创建持久 bash 会话
    await runtime.create_session(CreateBashSessionRequest())

    # 会话内命令：环境状态保留
    print(await runtime.run_in_session(BashAction(command="export MYVAR='test'")))
    print(await runtime.run_in_session(BashAction(command="echo $MYVAR")))

    await deployment.stop()

deployment = LocalDeployment()
asyncio.run(run_some_stuff(deployment))
```

## 预期输出

```text
stdout='Hello, world!\n' stderr='' exit_code=0
output='' exit_code=0 failure_reason='' expect_string='SHELLPS1PREFIX' session_type='bash'
output='test' exit_code=0 failure_reason='' expect_string='SHELLPS1PREFIX' session_type='bash'
```

（输出字段来自 `CommandResponse` 与 `BashObservation`，见 F-044、F-045；官方日志见 `docs/usage.md` 第67行附近，F-102。）

## 逐行解释

1. `LocalDeployment()` 只保存配置，不创建 runtime（F-019）。
2. `await deployment.start()` 创建 `LocalRuntime`（F-019）。
3. `runtime.execute(Command([...]))` 走 `subprocess.run`，无状态（F-060）。
4. `create_session(CreateBashSessionRequest())` 启动一个 pexpect bash，默认名 `default`（F-041、F-052）。
5. 第一条 `run_in_session` 执行 `export`，没有输出；第二条能读到 `$MYVAR`，证明状态保留（F-100）。
6. `stop()` 关闭所有 session（F-019、F-061）。

## 换成容器

只改两行：

```python
from swerex.deployment.docker import DockerDeployment

deployment = DockerDeployment(image="python:3.12")
```

其余代码不变（F-101）。Docker 版会拉镜像、分配端口、启动容器内 `swerex-remote`，然后返回 `RemoteRuntime`（F-020、F-021）。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `DeploymentNotStartedError` | 没 `start()` 就取 `runtime` | 先 `await start()` |
| `SessionExistsError` | 重复 `create_session` 同名 | 换名字或先关闭 |
| 输出含 ANSI 转义 | 命令带颜色 | `_strip_control_chars` 已清一部分；必要时关掉命令颜色 |
| 卡住不返回 | `timeout=None` | 给 `BashAction.timeout` 设值 |

## 注意

`LocalDeployment` 直接在本机执行，`rm -rf /` 会真的删文件。官方文档在第8-10行明确警告（F-099 所在的 usage.md 开头）。需要隔离请用 [Docker 示例](/examples/02-docker-sandbox.md)。

## 相关文档

- [项目总览](/concepts/00-project-overview.md)
- [会话模型](/concepts/02-session-model.md)
- [Docker 沙箱示例](/examples/02-docker-sandbox.md)
