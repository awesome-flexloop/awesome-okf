---
type: Example
title: "示例二：Docker 沙箱（DockerDeployment）"
description: "用 DockerDeployment 在容器里跑命令：镜像选择、启动日志解读、端口与 token、常见启动失败排查；附可运行脚本"
tags: [swe-rex, example, docker, sandbox, podman]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:48:30+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: usage-doc
    resource: /references/official-docs-source.md
    title: "docs/usage.md 第51-80行"
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-020 ~ F-024、F-101 ~ F-103"
---

# 示例二：Docker 沙箱（DockerDeployment）

`DockerDeployment` 把一个容器变成 SWE-ReX 的执行环境：容器内跑 `swerex-remote`，容器外 `RemoteRuntime` 通过映射端口连接。

## 完整代码

```python
import asyncio

from swerex.deployment.docker import DockerDeployment
from swerex.runtime.abstract import (
    BashAction,
    Command,
    CreateBashSessionRequest,
)

async def main():
    deployment = DockerDeployment(
        image="python:3.12",
        startup_timeout=180,
        pull="missing",
    )
    await deployment.start()
    try:
        runtime = deployment.runtime
        print(await runtime.is_alive())

        # 一次性命令
        print(await runtime.execute(Command(command=["python", "--version"])))

        # 持久会话
        await runtime.create_session(CreateBashSessionRequest(session="main"))
        await runtime.run_in_session(BashAction(command="cd /tmp", session="main"))
        await runtime.run_in_session(BashAction(command="pwd", session="main"))
        await runtime.run_in_session(BashAction(command="echo $PWD", session="main"))
    finally:
        await deployment.stop()

asyncio.run(main())
```

## 启动时发生了什么

1. `_pull_image()`：`pull="missing"` 时先 `docker inspect`，不存在才 `docker pull`（F-087）。
2. `find_free_port()`：绑定 `("", 0)` 找一个空闲端口，并在进程内注册去重（F-090）。
3. 生成容器名：镜像名只保留字母数字与 `-_ .`，拼 UUID（F-020）。
4. 生成 token：`uuid4()`（F-020）。
5. 运行：

```bash
docker run --rm -p <port>:8000 \
  --name python3.12-<uuid> \
  python:3.12 \
  /bin/sh -c "swerex-remote --auth-token <token> || (python3 -m pip install pipx && python3 -m pipx ensurepath && pipx run swe-rex --auth-token <token>)"
```

（F-021、F-102）

6. `RemoteRuntime(host="http://127.0.0.1", port=<port>, auth_token=<token>)`。
7. 每 0.25s 调 `is_alive`，直到成功或 `startup_timeout`（F-088、F-089）。

## 预期日志

```text
🦖 INFO     Pulling image 'python:3.12'
🦖 DEBUG    Found free port 59647
🦖 INFO     Starting container python3.12-<uuid> with image python:3.12 serving on port 59647
🦖 INFO     Starting runtime at 59647
🦖 INFO     Runtime started in 18.78s
```

（格式来自 `utils/log.py` 的 rich handler，F-091；示例数值来自 `docs/usage.md` 第67行，F-102。）

## 关键参数

| 参数 | 作用 | 建议 |
|---|---|---|
| `image` | 容器镜像 | 用带项目依赖的镜像，避免运行时装包 |
| `startup_timeout` | 等 alive 的上限 | 冷启动/大镜像调到 300 |
| `pull` | 拉取策略 | CI 用 `missing`，离线用 `never` |
| `python_standalone_dir` | 构建内置 Python 的镜像 | 镜像无 Python 时用；构建慢 |
| `container_runtime` | `docker` 或 `podman` | 无 Docker 的 Linux 用 podman |
| `docker_args` | 追加 `docker run` 参数 | 挂载、网络、资源限制 |
| `docker_internal_host` | 客户端连容器的 host | Docker-in-Docker 时设 `http://host.docker.internal` |

（F-023、F-024）

## Podman

```python
deployment = DockerDeployment(
    image="python:3.12",
    container_runtime="podman",
)
```

所有容器命令（`inspect`/`pull`/`run`/`kill`/`rmi`）都使用 `podman`（F-020、F-087）。

## 常见启动失败

| 日志/异常 | 原因 | 处理 |
|---|---|---|
| `DockerPullError` | 镜像不存在/无网络/私有仓库 | 先手动 `docker pull` |
| `swerex-remote: not found` 且 pipx 失败 | 容器无法访问 PyPI | 预装 `swe-rex` 或配镜像源 |
| `Runtime did not start within 180s` | 启动慢/端口不通 | 看容器 stdout/stderr；加大 timeout |
| 端口冲突 | 固定了 `port` | 删掉 `port` 让系统分配 |
| `permission denied` on docker socket | 用户不在 docker 组 | 配权限或用 rootless podman |

（F-087、F-088）

## 资源清理

`stop()` 会：

1. `runtime.close()`。
2. `docker kill <container>`（失败只 warning）。
3. 最多三次 `kill()` + `wait(5)`。
4. `remove_images=True` 时 `docker rmi`。

（F-020）`remove_container=True` 时 `docker run --rm` 已保证容器退出即删。

## 注意

示例中的 `finally` 很重要：即使命令抛异常，也要 `stop()`，否则容器可能残留。`AbstractDeployment.__del__` 只是兜底，不保证执行（F-018）。

## 相关文档

- [部署矩阵](/concepts/04-deployments.md)
- [会话模型](/concepts/02-session-model.md)
- [远程服务器示例](/examples/03-remote-server.md)
