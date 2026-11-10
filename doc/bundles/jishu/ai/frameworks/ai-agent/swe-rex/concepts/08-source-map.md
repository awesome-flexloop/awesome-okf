---
type: Concept
title: "源码地图：模块、符号、调用链与扩展点"
description: "按文件与行号定位 SWE-ReX 的核心符号：部署启动链、会话执行链、协议转发链、数据契约、扩展点与测试地图；附行号口径说明"
tags: [swe-rex, source-map, symbols, call-chain, extension-points]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:46:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-001 ~ F-114"
---

# 源码地图：模块、符号、调用链与扩展点

本页是“要改代码时从哪下手”的索引。所有行号对应 commit `5c995c3`（`v1.4.0-18-g5c995c3`）。

## 模块职责

| 文件 | 行数 | 职责 | 关键符号 |
|---|---:|---|---|
| `src/swerex/__init__.py` | 5 | 版本与常量 | `__version__`、`PACKAGE_NAME`、`REMOTE_EXECUTABLE_NAME` |
| `src/swerex/__main__.py` | 4 | `python -m swerex` | 调用 `server.main` |
| `src/swerex/exceptions.py` | 52 | 异常体系 | 12 个异常类 |
| `src/swerex/server.py` | 221 | HTTP 服务 | `app`、`ResponseManager`、`main` |
| `deployment/abstract.py` | 60 | 部署契约 | `AbstractDeployment` |
| `deployment/config.py` | 229 | 部署配置 | 7 个 Config、`DeploymentConfig`、`get_deployment` |
| `deployment/local.py` | 73 | 本地部署 | `LocalDeployment` |
| `deployment/docker.py` | 334 | Docker/Podman | `DockerDeployment` |
| `deployment/modal.py` | 295 | Modal | `ModalDeployment`、`_ImageBuilder` |
| `deployment/fargate.py` | 187 | AWS Fargate | `FargateDeployment` |
| `deployment/daytona.py` | 170 | Daytona | `DaytonaDeployment` |
| `deployment/remote.py` | 73 | 远程包装 | `RemoteDeployment` |
| `deployment/dummy.py` | 49 | 测试替身 | `DummyDeployment` |
| `deployment/hooks/abstract.py` | 18 | Hook 契约 | `DeploymentHook`、`CombinedDeploymentHook` |
| `deployment/hooks/status.py` | 16 | 状态回调 | `SetStatusDeploymentHook` |
| `runtime/abstract.py` | 288 | 运行时契约与模型 | `AbstractRuntime`、`BashAction`、`Command` |
| `runtime/config.py` | 61 | 运行时配置 | 3 个 Config、`RuntimeConfig`、`get_runtime` |
| `runtime/local.py` | 478 | 本地执行 | `LocalRuntime`、`BashSession`、`_split_bash_command` |
| `runtime/remote.py` | 265 | HTTP 客户端 | `RemoteRuntime` |
| `runtime/dummy.py` | 94 | 预置输出 | `DummyRuntime` |
| `utils/aws.py` | 289 | AWS 资源 | 10 个函数 |
| `utils/aws_teardown.py` | 327 | AWS 清理 | 7 个函数 |
| `utils/free_port.py` | 25 | 端口分配 | `find_free_port` |
| `utils/log.py` | 68 | 日志 | `get_logger` |
| `utils/wait.py` | 34 | 轮询 | `_wait_until_alive` |

（行数为 `Get-Content` 计数，含空行；符号行号见下表。）

## 部署启动链

```text
DockerDeployment.start()                       docker.py:233
├── _pull_image()                              docker.py:133
│   ├── _is_image_available()                  docker.py:25
│   └── _pull_image()                          docker.py:37
├── _build_image()（可选）                      docker.py:196
├── find_free_port()                           free_port.py:11
├── _get_container_name()                      docker.py:76
├── _get_token()                               docker.py:117
├── _get_swerex_start_cmd()                    docker.py:120
├── subprocess.Popen([... docker run ...])     docker.py:277
├── RemoteRuntime.from_config()                docker.py:280
└── _wait_until_alive()                        docker.py:106
    └── _wait_until_alive()                    wait.py:6
        └── is_alive()                         docker.py:85
            └── RemoteRuntime.is_alive()       remote.py:128
```

对应事实：F-020、F-021、F-087、F-088、F-089、F-090。

## 会话执行链

```text
RemoteRuntime.run_in_session(action)           remote.py:203
└── _request("run_in_session", ...)            remote.py:165
    ├── uuid4 → X-Request-ID                   remote.py:173
    ├── POST http://host:port/run_in_session   remote.py:183
    └── _handle_response_errors()              remote.py:117
        └── _handle_transfer_exception()       remote.py:84

server.run_in_session(request: Action)         server.py:137
└── LocalRuntime.run_in_session(action)        local.py:403
    └── BashSession.run(action)                local.py:218
        ├── interrupt()                        local.py:186
        ├── _run_interactive()                 local.py:245
        └── _run_normal()                      local.py:274
            ├── _check_bash_command()          local.py:101
            ├── _split_bash_command()          local.py:59
            ├── shell.expect(PS1 or UNIQUE)    local.py:315
            └── echo EXITCODESTART$?           local.py:327
```

对应事实：F-051、F-053、F-055、F-056、F-057、F-058、F-064、F-065、F-077。

## 服务端转发链

```text
@app.post("/run_in_session")                   server.py:137
├── authenticate middleware                    server.py:67
├── handle_request_id middleware               server.py:77
│   ├── ResponseManager.get_response()         server.py:54
│   └── ResponseManager.set_response()         server.py:59
├── runtime.run_in_session(action)             server.py:139
└── exception_handler（异常时）                 server.py:105
    └── JSONResponse(status_code=511)          server.py:119
```

对应事实：F-073、F-074、F-075、F-076、F-080。

## 数据契约

| 模型 | 字段 | 位置 |
|---|---|---|
| `IsAliveResponse` | `is_alive`, `message` | `runtime/abstract.py:8` |
| `CreateBashSessionRequest` | `startup_source`, `session`, `session_type`, `startup_timeout` | `runtime/abstract.py:23` |
| `BashAction` | `command`, `session`, `timeout`, `is_interactive_command`, `is_interactive_quit`, `check`, `error_msg`, `expect` | `runtime/abstract.py:51` |
| `BashInterruptAction` | `session`, `timeout=0.2`, `n_retry=3`, `expect` | `runtime/abstract.py:90` |
| `BashObservation` | `output`, `exit_code`, `failure_reason`, `expect_string` | `runtime/abstract.py:109` |
| `Command` | `command`, `timeout`, `shell`, `check`, `error_msg`, `env`, `cwd`, `merge_output_streams` | `runtime/abstract.py:143` |
| `CommandResponse` | `stdout`, `stderr`, `exit_code` | `runtime/abstract.py:179` |
| `ReadFileRequest` | `path`, `encoding`, `errors` | `runtime/abstract.py:185` |
| `WriteFileRequest` | `content`, `path` | `runtime/abstract.py:202` |
| `UploadRequest` | `source_path`, `target_path` | `runtime/abstract.py:211` |
| `_ExceptionTransfer` | `message`, `class_path`, `traceback`, `extra_info` | `runtime/abstract.py:224` |

## 扩展点

| 想改什么 | 改哪里 | 注意 |
|---|---|---|
| 新增部署平台 | `deployment/config.py` + 新文件 + `DeploymentConfig` 联合 | 必须实现 `start/stop/is_alive/runtime/add_hook` |
| 新增运行时实现 | `runtime/abstract.py` 子类 + `runtime/config.py` | 9 个方法全部实现 |
| 新增 session 类型 | `CreateBashSessionRequest` 的 `session_type` 判别 + `LocalRuntime.create_session` | 目前只有 `bash` |
| 改命令终止判定 | `BashSession._run_normal` / `_run_interactive` | 会影响所有 session 命令 |
| 改异常传输 | `server.exception_handler` + `RemoteRuntime._handle_transfer_exception` | 两端协议同步改 |
| 改幂等 | `ResponseManager` | 单槽改多槽会影响内存与并发语义 |
| 加部署进度回调 | `DeploymentHook.on_custom_step` + 各部署 `self._hooks` | 同步回调，勿阻塞 |
| 改日志格式 | `utils/log.py` | rich handler；环境变量控制级别/时间 |
| 加云资源清理 | `utils/aws_teardown.py` | 按标签筛选，务必保留确认 |

## 测试地图

| 测试文件 | 目标符号 | 用例数 |
|---|---|---:|
| `tests/conftest.py` | `RemoteRuntime`、`swerex.server.app` | 0（fixture） |
| `tests/test_server.py` | 10 路由、认证 | 3 |
| `tests/test_execution.py` | `RemoteRuntime` 全方法 | 50 |
| `tests/test_runtime.py` | `_split_bash_command`、`_check_bash_command` | 12 |
| `tests/test_local_runtime.py` | 同上（本地） | 2 |
| `tests/test_get_deployment.py` | `get_deployment` 6 个分支 | 6 |
| `tests/test_local_deployment.py` | `LocalDeployment` | 1 |
| `tests/test_dummy_deployment.py` | `DummyDeployment` | 1 |
| `tests/test_remote_deployment.py` | `RemoteDeployment` | 1 |
| `tests/test_docker_deployment.py` | `DockerDeployment` | 9 |
| `tests/test_modal_deployment.py` | `ModalDeployment` | 2 |
| `tests/test_fargate_deployment.py` | `FargateDeployment` | 2 |

（F-012、F-081、F-109 ~ F-113）

## 行号口径与阅读建议

1. 行号来自 `Select-String` 的 1-based 计数，对应 commit `5c995c3`；上游前进后会漂移。
2. 模块行数是 `(Get-Content).Count`，包含空行；不要与非空行口径混用（F-009）。
3. 读代码顺序建议：`runtime/abstract.py`（契约）→ `runtime/local.py`（实现）→ `server.py`（传输）→ `runtime/remote.py`（客户端）→ `deployment/docker.py`（编排）。
4. 改任何协议模型时，同时改 server、RemoteRuntime、测试三处；Pydantic 的 `discriminator` 会让不兼容变更在反序列化时立刻暴露。

## 相关概念

- [架构分层](/concepts/01-architecture.md)
- [会话模型](/concepts/02-session-model.md)
- [配置与扩展](/concepts/06-configuration-and-extension.md)
- [源码信源登记](/references/source-code-map.md)
