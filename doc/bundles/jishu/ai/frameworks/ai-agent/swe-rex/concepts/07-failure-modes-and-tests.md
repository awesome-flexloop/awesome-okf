---
type: Concept
title: "失败模式与测试：12 类异常、超时链路与 89 个用例"
description: "SWE-ReX 的异常分类、常见失败场景与排查顺序、重试与幂等边界、测试地图（13 文件 89 用例）以及测试未覆盖的部分"
tags: [swe-rex, exceptions, failure-modes, testing, pytest]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-084 ~ F-093、F-109 ~ F-114"
---

# 失败模式与测试：12 类异常、超时链路与 89 个用例

SWE-ReX 的失败大多发生在四个位置：部署启动、连接、会话执行、文件传输。每一层都有明确的异常类型，排查时按层定位比读 agent 日志更快。

## 异常分类

`exceptions.py` 共 12 个类（F-084）：

| 异常 | 基类 | 触发条件 | 事实 |
|---|---|---|---|
| `SwerexException` | `Exception` | 所有 SWE-ReX 异常的根 | F-084 |
| `SessionNotInitializedError` | `SwerexException, RuntimeError` | shell 未初始化 | F-084 |
| `NonZeroExitCodeError` | `SwerexException, RuntimeError` | 命令非零退出 + `check="raise"` | F-053 |
| `BashIncorrectSyntaxError` | `SwerexException, RuntimeError` | `bash -n` 语法检查失败 | F-058 |
| `CommandTimeoutError` | `SwerexException, RuntimeError, TimeoutError` | 命令/交互式 expect 超时 | F-053、F-055 |
| `NoExitCodeError` | `SwerexException, RuntimeError` | 退出码提取失败或超时 | F-053 |
| `SessionExistsError` | `SwerexException, ValueError` | 同名 session 重复创建 | F-050 |
| `SessionDoesNotExistError` | `SwerexException, ValueError` | 操作不存在的 session | F-051 |
| `DeploymentNotStartedError` | `SwerexException, RuntimeError` | 未 `start()` 就取 `runtime` | F-017 |
| `DeploymentStartupError` | `SwerexException, RuntimeError` | 部署启动失败基类 | F-084 |
| `DockerPullError` | `DeploymentStartupError` | 镜像拉取失败 | F-087 |
| `DummyOutputsExhaustedError` | `SwerexException, RuntimeError` | Dummy 输出列表耗尽 | F-069 |

`CommandTimeoutError` 同时是 `TimeoutError`，所以既可以用 `except CommandTimeoutError`，也可以用 `except TimeoutError` 捕获（F-086）。

## 四层失败定位

### 第一层：部署启动

症状：`await deployment.start()` 抛异常或一直等到超时。

| 现象 | 可能原因 | 检查 | 事实 |
|---|---|---|---|
| `DockerPullError` | 镜像名错、无网络、私有仓库未登录 | `docker pull <image>` | F-087 |
| 启动超时 | 容器内没有 `swe-rex` 且 pipx 装不上 | 容器日志、PyPI 可达性 | F-021 |
| 端口冲突 | 固定端口被占用 | 去掉 `port` 让 `find_free_port` 分配 | F-090 |
| Modal/Fargate 超时 | 云配额、镜像构建慢、网络策略 | 平台控制台日志 | F-025、F-030 |
| `DeploymentNotStartedError` | 未 `start()` 就访问 `runtime` | 调用顺序 | F-017 |

Docker 的 `_wait_until_alive()` 超时会读取容器 stdout/stderr 打日志，然后 `stop()` 并重抛 `TimeoutError`（F-088）。所以启动失败时先看这段日志，通常能看到 `swerex-remote: command not found` 或 pip 安装错误。

### 第二层：连接

症状：`is_alive()` 返回 false，或请求超时。

- `RemoteRuntime.is_alive()` 连接失败不抛异常，返回 `is_alive=False` + message（F-067）。用 `if await runtime.is_alive():` 判断。
- `timeout` 默认 0.15s（F-071），冷启动或跨地域网络很容易超时。把 `timeout` 调到 5–30s 再试。
- `port=None` 时只连 host（F-063）；`host` 写 `http://127.0.0.1` 而 port 留空会连 80。

### 第三层：会话执行

| 异常 | 含义 | 处理 |
|---|---|---|
| `BashIncorrectSyntaxError` | 命令语法错 | 看 `extra_info["bash_stderr"]` |
| `CommandTimeoutError` | 命令没在 timeout 内结束 | 放大 timeout；交互式程序用 `expect`；卡死用 `BashInterruptAction` |
| `NoExitCodeError` | 退出码旁路失败 | 检查命令是否关闭了 shell、是否输出被截断 |
| `NonZeroExitCodeError` | 命令失败 | 看 output；需要容忍时改 `check="silent"` |
| `SessionDoesNotExistError` | session 名错/已关闭 | 先 `create_session` |

（F-053、F-055、F-058、F-084）

### 第四层：文件传输

- `read_file` 对不存在文件抛 `FileNotFoundError`（`Path.read_text` 原样抛出；测试 `test_read_non_existent_file` 覆盖，F-109）。
- `write_file` 自动建父目录（F-061）。
- `upload` 源路径不存在抛 `ValueError`（F-068）。
- 目录上传依赖 zip/unzip；Windows 临时目录清理问题用 `ignore_cleanup_errors=True` 规避（F-068）。

## 重试与幂等边界

`_request(num_retries=N)` 的重试逻辑（F-064）：

```text
attempt 0 → fail → sleep 0.1 + jitter
attempt 1 → fail → sleep 0.2 + jitter
...
上限 5s
```

但 server 端幂等只记最后一次请求（F-075）。因此：

1. 单客户端、顺序请求：重试安全。
2. 多客户端并发：重试可能重复执行。
3. 重试非“最近一条”：不会命中缓存。

需要严格幂等时，在 agent 层自己做 request key 与结果存储；不要依赖 `X-Request-ID`。

## 测试地图

13 个测试文件、89 个用例（F-011、F-012）：

| 文件 | 用例 | 覆盖 |
|---|---:|---|
| `test_execution.py` | 50 | 端到端 HTTP：alive、文件、execute、session、退出码、交互式、bashlex、上传、多 session |
| `test_runtime.py` | 12 | `_split_bash_command` 与 `_check_bash_command` 单元测试 |
| `test_docker_deployment.py` | 9 | Docker 启动/停止/执行 |
| `test_get_deployment.py` | 6 | 配置 → 部署类映射 |
| `test_server.py` | 3 | alive、hello、10 路由未认证 403 |
| `test_fargate_deployment.py` | 2 | Fargate 路径（需 AWS 凭证） |
| `test_local_runtime.py` | 2 | 本地 runtime 基础 |
| `test_modal_deployment.py` | 2 | Modal 路径（需 Modal 凭证） |
| `test_dummy_deployment.py` | 1 | Dummy 全流程 |
| `test_local_deployment.py` | 1 | Local 生命周期 |
| `test_remote_deployment.py` | 1 | Remote 包装 |

测试基础设施（F-081、F-082）：

```python
# conftest.py：真实起一个 uvicorn server
swerex.server.AUTH_TOKEN = "testkey"
uvicorn.run(swerex.server.app, host="127.0.0.1", port=port, log_level="error")
```

`remote_server` 是 session 级 fixture；`remote_runtime` 与 `runtime_with_default_session` 是函数级，结束时关闭。`_Action`/`_Command` 子类把默认 timeout 设为 5 秒（F-082）。

## 测试覆盖的空白

1. **云部署默认不跑**：Modal/Fargate 测试需要凭证，CI 通常跳过或标记；不能把“测试全绿”理解为云路径已验证。
2. **并发同一 session**：没有测试覆盖两个协程同时 `run_in_session` 同一 session 的交错。
3. **超大输出**：只测了 1MB 文件读取（F-109），没有测命令输出截断/内存压力。
4. **Windows 本机**：`BashSession` 依赖 `/usr/bin/env bash` 与 pexpect，Windows 原生不支持；测试实际在 Linux/WSL 环境跑。
5. **Daytona**：没有 `test_daytona_deployment.py`（F-012），只有配置映射测试。
6. **安全**：没有针对命令注入、路径穿越的负向测试；`upload` 的 `target_path` 直接用于文件系统操作（F-078）。

## 一个最小排障脚本

```python
import asyncio
from swerex.deployment.docker import DockerDeployment

async def main():
    d = DockerDeployment(image="python:3.12", startup_timeout=120)
    try:
        await d.start()
        print("alive:", bool(await d.is_alive()))
        r = d.runtime
        print(await r.execute(__import__("swerex.runtime.abstract", fromlist=["Command"]).Command(
            command=["python", "--version"])))
    finally:
        await d.stop()

asyncio.run(main())
```

先确认 `alive`，再跑一条最短命令；两步都过，才怀疑 agent 逻辑。

## 相关概念

- [会话模型](/concepts/02-session-model.md)
- [HTTP 协议](/concepts/03-http-protocol.md)
- [源码地图](/concepts/08-source-map.md)
- [验证报告](/references/verification.md)
