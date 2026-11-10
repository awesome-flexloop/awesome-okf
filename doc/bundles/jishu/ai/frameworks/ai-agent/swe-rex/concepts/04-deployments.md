---
type: Concept
title: "部署矩阵：七种环境的生命周期与差异"
description: "Local、Docker/Podman、Modal、Fargate、Daytona、Remote、Dummy 七种部署的启动链路、默认参数、网络暴露方式、清理策略与选型对照"
tags: [swe-rex, deployment, docker, modal, fargate, daytona, podman]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:42:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-019 ~ F-038"
---

# 部署矩阵：七种环境的生命周期与差异

七个部署类共享 `AbstractDeployment` 契约，但各自的“启动”是一套不同的资源编排：Docker 跑容器、Modal 建 Sandbox、Fargate 建 ECS task、Daytona 建沙箱、Local 直接开进程、Remote 连现成 server、Dummy 返回假数据。差异集中在镜像、端口、token、超时与清理；命令执行语义完全一致。

## 总览

| 部署 | 配置类 | 运行时 | 隔离 | 启动成本 | 网络暴露 | 事实 |
|---|---|---|---|---|---|---|
| Local | `LocalDeploymentConfig` | `LocalRuntime` | 无 | 毫秒 | 进程内 | F-019 |
| Docker/Podman | `DockerDeploymentConfig` | `RemoteRuntime` | 容器 | 秒~分钟（拉镜像） | `-p port:8000` | F-020 |
| Modal | `ModalDeploymentConfig` | `RemoteRuntime` | 云沙箱 | 秒~分钟 | tunnel URL | F-025 |
| Fargate | `FargateDeploymentConfig` | `RemoteRuntime` | 云容器 | 分钟 | 公网 IP + 8880 | F-030 |
| Daytona | `DaytonaDeploymentConfig` | `RemoteRuntime` | 云沙箱 | 秒~分钟 | preview link | F-031 |
| Remote | `RemoteDeploymentConfig` | `RemoteRuntime` | 取决于服务端 | 毫秒 | 现成 URL | F-033 |
| Dummy | `DummyDeploymentConfig` | `DummyRuntime` | 无 | 零 | 无 | F-034 |

所有配置类都 `extra="forbid"`（F-036）：拼错字段会直接报错，而不是静默忽略。

## Local：最薄的包装

```python
from swerex.deployment.local import LocalDeployment

deployment = LocalDeployment()
await deployment.start()   # 创建 LocalRuntime
runtime = deployment.runtime
await deployment.stop()    # runtime.close()
```

`LocalDeployment.start()` 只有一行：`self._runtime = LocalRuntime(logger=self.logger)`（F-019）。没有沙箱，命令直接在本机执行。`docs/usage.md` 第8-10行明确警告不要在本机跑 `rm -rf /`。

`is_alive()` 在未启动时返回 `IsAliveResponse(False, "Runtime is None.")`，不抛异常（F-019）。

## Docker / Podman：最常用的沙箱

### 启动链路

`DockerDeployment.start()`（F-020）：

1. `_pull_image()`：按 `pull` 策略拉镜像；失败抛 `DockerPullError`（F-087）。
2. 若 `python_standalone_dir` 非空，构建 standalone Python 镜像（F-022）；否则直接用配置镜像。
3. `find_free_port()` 分配端口（F-090）。
4. 生成容器名（镜像名净化 + UUID）与 token。
5. `docker run --rm -p <port>:8000 --name <name> <image> <start-cmd>`。
6. `RemoteRuntime(host=docker_internal_host, port=port, auth_token=token)`。
7. `_wait_until_alive(startup_timeout)`（F-088）。

### 启动命令与 fallback

```bash
swerex-remote --auth-token <token> || (
  python3 -m pip install pipx &&
  python3 -m pipx ensurepath &&
  pipx run swe-rex --auth-token <token>
)
```

（F-021）镜像里没有 `swe-rex` 时，回退到 pipx 临时安装。这要求容器能访问 PyPI；离线环境应预装 `swe-rex` 或使用 `python_standalone_dir`。

### 默认参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `image` | `python:3.11` | 容器镜像 |
| `startup_timeout` | `180.0` | 等 runtime alive |
| `pull` | `missing` | `never`/`always`/`missing` |
| `remove_container` | `True` | 停止时删容器 |
| `remove_images` | `False` | 停止时删镜像 |
| `container_runtime` | `docker` | 可切 `podman` |
| `exec_shell` | `["/bin/sh","-c"]` | 启动命令外壳 |
| `docker_internal_host` | `http://127.0.0.1` | 客户端连容器内 server 的 host |

（F-023）`docker_args` 可追加任意 `docker run` 参数；`--platform` 会被迁移到 `platform` 字段，同时指定两者报 `ValueError`（F-024）。

### 停止

`stop()` 先 `runtime.close()`，再 `docker kill`，最多三次 `kill()` + `wait(5)`，最后按需 `rmi`（F-020）。即使容器已被 `--rm` 删除，`docker kill` 失败也只记 warning。

### Podman

把 `container_runtime="podman"` 即可；`_is_image_available`/`_pull_image`/`_remove_image` 都用该值作为命令（F-020、F-087）。容器内启动命令不变。

## Modal：Sandbox + tunnel

```python
deployment = ModalDeployment(
    image="python:3.12",
    startup_timeout=60,
    deployment_timeout=3600,
)
```

`start()`（F-025）：

1. `modal.Sandbox.create.aio("/usr/bin/env", "bash", "-c", start_cmd, image=..., timeout=deployment_timeout, unencrypted_ports=[8880])`。
2. `sandbox.tunnels.aio()` 取 8880 端口的 tunnel。
3. `RemoteRuntime(host=tunnel.url, timeout=runtime_timeout, auth_token=token)`。
4. 等待 alive，剩余启动超时按已耗时扣减。

镜像来源由 `_ImageBuilder.auto()` 决定（F-027）：`modal.Image`、Dockerfile 路径、ECR 地址、registry 名。`install_pipx=True` 会在镜像里装 pipx，供 fallback 使用。

默认 `runtime_timeout=60`、`deployment_timeout=3600`（F-026）。`deployment_timeout` 是硬止损：即使 agent 忘了 stop，Sandbox 也会在 1 小时后被杀。

## Fargate：ECS 资源编排最多

`start()`（F-030）会创建/复用：

1. ECS cluster（默认 `swe-rex-cluster`）。
2. IAM execution role（默认前缀 `swe-rex-execution-role`）。
3. Task definition（默认前缀 `swe-rex-task`）。
4. 默认 VPC 与子网。
5. 安全组（默认前缀 `swe-rex-deployment-sg`，开放配置端口）。
6. 提交 Fargate task，`tasks_running` waiter 等待。
7. 取公网 IP，`RemoteRuntime(host=public_ip, port=8880)`。

启动命令带 `timeout <container_timeout>s` 包裹（F-029），默认 900 秒；超时后容器自杀，避免僵尸 task。默认端口 8880（F-028）。

AWS 资源不会在 `stop()` 时全部删除：`stop()` 只 `stop_task`（F-030）。清理用 `swerex.utils.aws_teardown`（F-093），它会按 `swe-rex` 标签筛选 IAM role、task definition、cluster、security group，并要求确认（`get_confirmation`）。

> 成本提示：Fargate 按 task 运行时长计费；`container_timeout=900` 是兜底，不是建议运行时长。调试时优先用 Docker/Modal。

## Daytona：preview link

`start()`（F-031）：

1. `Daytona(DaytonaConfig(api_key, target))`。
2. `daytona.create(CreateSandboxFromImageParams(image=...))`。
3. 创建 session，`execute_session_command(..., runAsync=True)` 启动 server。
4. `sandbox.get_preview_link(port)` 得到完整 URL。
5. `RemoteRuntime(host=url, port=None)`。

`port=None` 是关键：preview link 已经是完整 URL，不能再拼端口（F-063）。

默认 `port=8000`、`container_timeout=900`、`runtime_timeout=60`、`target="us"`（F-032）。README 把 Daytona 标为 WIP（F-096），官方 mkdocs 导航也尚未收录（F-106）。

## Remote：连接已有 server

```python
deployment = RemoteDeployment(
    host="http://127.0.0.1",
    port=8000,
    auth_token="<token>",
    timeout=0.15,
)
await deployment.start()  # 只创建 RemoteRuntime，不启动新环境
```

`RemoteDeployment` 是纯薄包装（F-033）：`start()` 创建 `RemoteRuntime`，`stop()` 调 `close()`。适合“容器已经手动起好，只想用统一接口连过去”的调试场景。

`RemoteDeploymentConfig.auth_token` 必填；`host` 默认 `http://127.0.0.1`；`timeout` 默认 `0.15`（F-071）。

## Dummy：测试替身

`DummyDeployment` 在构造时就创建 `DummyRuntime`；`start()`/`stop()` 空操作；`runtime` 可读写（F-034）。`DummyRuntime.run_in_session_outputs` 可设为单个 `BashObservation` 或列表，列表模式每次 `pop(0)`，空列表抛 `DummyOutputsExhaustedError`（F-069）。

适合单测 agent 循环：不需要 Docker，也不产生真实副作用。

## 选型建议

| 场景 | 推荐 | 理由 |
|---|---|---|
| 本机快速验证 | Local | 零依赖、毫秒启动 |
| 需要隔离的可复现环境 | Docker | 镜像即环境，端口自动分配 |
| 无 Docker 的 macOS/Windows | Modal 或 Remote | 云端沙箱，不依赖本机容器 |
| 大规模并行评测 | Docker/Modal/Fargate | 每环境独立 token 与端口 |
| 已有容器/服务器 | Remote | 不重复编排 |
| 单元测试 | Dummy | 无副作用、输出可控 |

## 相关概念

- [架构分层](/concepts/01-architecture.md)
- [运行时与执行语义](/concepts/05-runtimes-and-execution.md)
- [配置与扩展](/concepts/06-configuration-and-extension.md)
- [Docker 沙箱示例](/examples/02-docker-sandbox.md)
- [并行部署示例](/examples/05-parallel-deployments.md)
