# 示例文档索引

本目录 5 篇示例，从本地到容器到远程到 agent 循环。

```{toctree}
:hidden:
:maxdepth: 2

01-local-hello-world
02-docker-sandbox
03-remote-server
04-agent-loop
05-parallel-deployments
```

| 示例 | 部署 | 主题 |
|---|---|---|
| [01 本地 Hello World](01-local-hello-world.md) | Local | 一次命令 + 持久 session |
| [02 Docker 沙箱](02-docker-sandbox.md) | Docker/Podman | 容器启动、日志、排障 |
| [03 手动远程 server](03-remote-server.md) | Remote | `swerex-remote` + `RemoteRuntime` |
| [04 Agent 循环](04-agent-loop.md) | Docker | 策略/执行分离、异常回传 |
| [05 并行部署](05-parallel-deployments.md) | Docker/Modal/Fargate | 信号量限流、任务隔离 |

> 这些示例与官方文档命令一致，但**未在本机逐条执行**；首次运行请先确认 Docker/网络/凭证。
