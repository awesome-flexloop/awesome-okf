---
type: Example
title: "示例五：并行部署与任务隔离"
description: "用 asyncio 并发跑多个 DockerDeployment：信号量限流、每任务独立容器/端口/token、异常隔离与清理；附并发规模估算"
tags: [swe-rex, example, parallel, asyncio, concurrency, docker]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:55:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-020、F-049、F-071、F-090"
  - id: readme
    resource: /references/official-docs-source.md
    title: "README 并行表述"
---

# 示例五：并行部署与任务隔离

SWE-ReX 没有全局调度器；并行的单位就是 `Deployment` 实例。每个实例独立创建容器/沙箱、分配端口、生成 token，因此任务之间天然隔离。

## 完整代码

```python
import asyncio

from swerex.deployment.docker import DockerDeployment
from swerex.exceptions import CommandTimeoutError, NonZeroExitCodeError
from swerex.runtime.abstract import BashAction, CreateBashSessionRequest

async def run_task(task_id: int, command: str) -> dict:
    deployment = DockerDeployment(image="python:3.12", startup_timeout=180)
    try:
        await deployment.start()
        runtime = deployment.runtime
        await runtime.create_session(CreateBashSessionRequest(session="main"))
        obs = await runtime.run_in_session(
            BashAction(command=command, session="main", timeout=300, check="raise")
        )
        return {"task": task_id, "ok": True, "output": obs.output, "exit_code": obs.exit_code}
    except (NonZeroExitCodeError, CommandTimeoutError) as e:
        return {"task": task_id, "ok": False, "error": type(e).__name__, "message": str(e)}
    except Exception as e:
        return {"task": task_id, "ok": False, "error": type(e).__name__, "message": str(e)}
    finally:
        await deployment.stop()

async def run_many(tasks: list[str], concurrency: int = 8) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)

    async def wrapped(i: int, cmd: str) -> dict:
        async with sem:
            return await run_task(i, cmd)

    return await asyncio.gather(*(wrapped(i, cmd) for i, cmd in enumerate(tasks)))

async def main():
    tasks = [f"python -c 'print({i} * {i})'" for i in range(16)]
    results = await run_many(tasks, concurrency=4)
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
```

## 隔离维度

| 维度 | 隔离方式 | 事实 |
|---|---|---|
| 文件系统 | 每任务独立容器 | F-020 |
| 端口 | `find_free_port()` 进程内去重 | F-090 |
| 认证 | 每部署生成 UUID token | F-020 |
| 会话 | 每 runtime 独立 `dict[str, Session]` | F-049 |
| 进程 | 每部署独立容器进程 | F-020 |

任务之间不会共享环境变量、`cd`、临时文件；这是“并行跑评测”能成立的前提。

## 并发控制

`asyncio.Semaphore(concurrency)` 限制同时运行的部署数。没有它，`gather` 会一次性拉起所有容器，常见后果：

1. 端口耗尽（虽然 `find_free_port` 会重试 10 次，F-090）。
2. 内存/CPU 打满。
3. Docker daemon 卡顿，`startup_timeout` 误判。
4. 云配额超限（Fargate/Modal）。

建议初始并发 4–8，按机器资源调整。README 第15行称可并行 100 个 agent（F-094）——这是产品能力表述，实际规模取决于容器密度与镜像大小。

## 异常隔离

每个 `run_task` 自己捕获异常并返回结构化结果，`gather` 不会因为一个任务失败而取消其他任务。如果希望“一个失败全部取消”，改用 `asyncio.TaskGroup`（Python 3.11+）或在 `gather` 外层处理。

## 清理

每个任务在 `finally` 里 `stop()`：

- `runtime.close()`；
- `docker kill`；
- 容器 `--rm` 自动删除；
- 可选 `remove_images=True`（不推荐并发时开，会互相删镜像）。

（F-020）

## 换成 Modal/Fargate

只换部署类：

```python
from swerex.deployment.modal import ModalDeployment
deployment = ModalDeployment(image="python:3.12", startup_timeout=120, deployment_timeout=3600)
```

或：

```python
from swerex.deployment.fargate import FargateDeployment
deployment = FargateDeployment(image="python:3.12", port=8880, container_timeout=900)
```

其余代码不变（F-025、F-030）。云部署要注意配额与成本；Fargate 的 `container_timeout` 是硬止损，不是建议时长。

## 性能估算

| 阶段 | Docker | Modal | Fargate |
|---|---|---|---|
| 冷启动 | 拉镜像 + 1–20s | 1–60s | 30–120s |
| 热启动 | 1–5s | 1–10s | 30–60s |
| 单命令开销 | 毫秒~秒 | 毫秒~秒（网络） | 毫秒~秒（网络） |
| 清理 | 秒 | 秒 | 秒~分钟 |

数值来自源码默认超时与官方示例日志（F-023、F-026、F-028、F-102），不是基准测试结果；实际以你的网络与镜像为准。

## 相关文档

- [部署矩阵](/concepts/04-deployments.md)
- [运行时与执行语义](/concepts/05-runtimes-and-execution.md)
- [Agent 循环示例](/examples/04-agent-loop.md)
