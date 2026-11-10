---
type: Concept
title: "运行时与执行语义：Local、Remote、Dummy 的同一契约"
description: "AbstractRuntime 九个方法的精确语义、execute 与 run_in_session 的差异、文件与上传行为、并发模型，以及实现自定义 Runtime 的最小步骤"
tags: [swe-rex, runtime, localruntime, remoteruntime, dummyruntime, concurrency]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:43:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-039 ~ F-071"
---

# 运行时与执行语义：Local、Remote、Dummy 的同一契约

`AbstractRuntime` 是 SWE-ReX 的真正 API 面。九个方法定义了 agent 能对沙箱做的一切；三个实现（Local、Remote、Dummy）只是把这些方法落到不同传输上。

## 九个方法

| 方法 | 输入 | 输出 | 语义 | 事实 |
|---|---|---|---|---|
| `is_alive` | `timeout` | `IsAliveResponse` | 存活探测，可 `bool()` | F-040 |
| `create_session` | `CreateSessionRequest` | `CreateSessionResponse` | 创建命名 shell | F-041 |
| `run_in_session` | `Action` | `Observation` | 在 session 里跑命令 | F-042、F-044 |
| `close_session` | `CloseSessionRequest` | `CloseSessionResponse` | 关闭并移除 session | F-046 |
| `execute` | `Command` | `CommandResponse` | 一次性子进程 | F-045 |
| `read_file` | `ReadFileRequest` | `ReadFileResponse` | 读文本 | F-046 |
| `write_file` | `WriteFileRequest` | `WriteFileResponse` | 写文本（自动建父目录） | F-046、F-061 |
| `upload` | `UploadRequest` | `UploadResponse` | 文件/目录传输 | F-046、F-061、F-068 |
| `close` | — | `CloseResponse` | 关闭 runtime | F-046 |

## `execute` vs `run_in_session`

这是最容易混淆的一组方法。

| 维度 | `execute(Command)` | `run_in_session(BashAction)` |
|---|---|---|
| 进程模型 | `subprocess.run` 子进程 | 持久 bash + pexpect |
| 状态 | 无状态；每次新进程 | 状态保留（`cd`、`export`、alias） |
| 输入 | `str` 或 `list[str]` | `str`（shell 命令） |
| 交互式 | 不支持 | 支持（`is_interactive_*`） |
| 超时 | `Command.timeout` | `BashAction.timeout` |
| 退出码 | `CommandResponse.exit_code` | `BashObservation.exit_code` |
| 输出 | `stdout` / `stderr` 分开 | `output` 合并（含 ANSI 清洗） |
| 适用 | 独立命令、脚本、一次性检查 | 多步操作、REPL、调试器 |

`execute` 的 `Command` 字段（F-045）：

```python
Command(
    command=["echo", "hello"],   # list 推荐，自动转义
    timeout=10,
    shell=False,
    check=False,
    env={"FOO": "bar"},
    cwd="/tmp",
    merge_output_streams=False,
)
```

`shell=True` 时 `command` 可为字符串，语义与 `subprocess.run(shell=True)` 一致。`merge_output_streams=True` 时 stderr 并入 stdout，`stderr` 为空（F-060）。

## LocalRuntime 的实现细节

### 创建会话

```python
await runtime.create_session(CreateBashSessionRequest(
    session="default",
    startup_source=["/etc/profile"],
    startup_timeout=1.0,
))
```

- 同名重复创建抛 `SessionExistsError`（F-050）。
- 只接受 `CreateBashSessionRequest`；其他 `session_type` 抛 `ValueError`。
- `startup_source` 里的文件会被 `source`，随后重置 PS1（F-052）。

### 执行与错误

- session 不存在：`SessionDoesNotExistError`（F-051）。
- 语法错误：`BashIncorrectSyntaxError`，带 bash stdout/stderr（F-058）。
- 超时：`CommandTimeoutError`（F-053）。
- 非零退出码 + `check="raise"`：`NonZeroExitCodeError`（F-053）。
- 退出码提取失败：`NoExitCodeError`（F-053）。

### 文件与上传

`read_file` 直接 `Path.read_text(encoding, errors)`；`write_file` 先 `mkdir(parents=True)` 再写；`upload` 目录 `copytree`、文件 `copy`（F-061）。

注意 `write_file` 固定用默认编码写入，不接收 `encoding` 参数；`read_file` 接收。读写非 UTF-8 内容时要在调用方处理。

## RemoteRuntime 的实现细节

### 连接与超时

```python
RemoteRuntime(
    host="http://127.0.0.1",
    port=8000,
    auth_token="<token>",
    timeout=0.15,
)
```

- host 不以 `http` 开头时自动补 `http://` 并 warning（F-062）。
- `timeout` 是默认请求超时；单次调用可传 `timeout` 覆盖（F-063）。
- `port=None` 时只使用 host（F-063）。

### 请求与重试

`_request()`（F-064）：

1. 生成 `uuid4` → `X-Request-ID`。
2. 每次尝试新建 `aiohttp.ClientSession`（`force_close=True`，不复用连接）。
3. 失败重试 `num_retries` 次，延迟 0.1s 起指数退避 + 0–0.5s 抖动，上限 5s。
4. 成功后用 `output_class(**json)` 构造响应。

`num_retries` 默认 0；需要重试时必须显式传。由于 server 幂等是单槽（F-075），重试只对“最近一条请求”安全。

### 异常重建

见 [HTTP 协议](/concepts/03-http-protocol.md#异常传输http-511)。要点：511 → `_ExceptionTransfer` → 动态导入 → 重建原类型；失败退化为 `SwerexException`（F-065、F-066）。

### 上传目录

`upload()` 对目录打 zip，multipart 上传，server 解压（F-068、F-078）。大目录会产生临时 zip 文件；`TemporaryDirectory(ignore_cleanup_errors=True)` 用于规避 Windows 清理问题（源码注释提到 SWE-agent issue #1005）。

## DummyRuntime

```python
runtime = DummyRuntime()
runtime.run_in_session_outputs = [
    BashObservation(output="first", exit_code=0),
    BashObservation(output="second", exit_code=0),
]
```

- 列表模式按顺序 `pop(0)`；空列表抛 `DummyOutputsExhaustedError`（F-069）。
- 单值模式永远返回同一个 observation。
- `is_alive` 恒真；`execute` 返回空输出 + 0；文件/上传空操作（F-070）。

适合测试 agent 的状态机，不适合验证真实命令语义。

## 并发模型

### 同一 runtime 内

- `LocalRuntime.sessions` 是普通 dict（F-049）。并发 `create_session` 同名会有一个失败（`SessionExistsError`）。
- 不同 session 可并行执行；测试 `test_multiple_isolated_shells` 用 `asyncio.gather` 验证（F-109）。
- 同一 session 上的并发 `run_in_session` 没有锁；两个协程同时往同一个 pexpect 进程写会交错。需要串行化时由调用方加锁。

### 跨部署

每个 Deployment 实例独立：独立容器/沙箱、独立端口、独立 token。并行 N 个环境就是 N 个 deployment 对象；没有全局池或调度器。

### 线程与事件循环

`BashSession` 内部用 `time.sleep(0.5)`（`_eat_following_output`）与阻塞式 pexpect API；这些调用发生在 async 方法里，会阻塞事件循环。源码没有用 `run_in_executor` 包装。高并发场景下这是需要注意的实现细节（F-052、F-056）。

## 实现自定义 Runtime

最小骨架：

```python
from swerex.runtime.abstract import (
    AbstractRuntime, IsAliveResponse, CreateSessionRequest, CreateSessionResponse,
    Action, Observation, CloseSessionRequest, CloseSessionResponse,
    Command, CommandResponse, ReadFileRequest, ReadFileResponse,
    WriteFileRequest, WriteFileResponse, UploadRequest, UploadResponse, CloseResponse,
)

class MyRuntime(AbstractRuntime):
    async def is_alive(self, *, timeout=None):
        return IsAliveResponse(is_alive=True)

    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        ...

    async def run_in_session(self, action: Action) -> Observation:
        ...

    async def close_session(self, request: CloseSessionRequest) -> CloseSessionResponse:
        ...

    async def execute(self, command: Command) -> CommandResponse:
        ...

    async def read_file(self, request: ReadFileRequest) -> ReadFileResponse:
        ...

    async def write_file(self, request: WriteFileRequest) -> WriteFileResponse:
        ...

    async def upload(self, request: UploadRequest) -> UploadResponse:
        ...

    async def close(self) -> CloseResponse:
        ...
```

如果新后端能跑 HTTP，更省事的做法是复用 `RemoteRuntime`，只写 `AbstractDeployment` 把 server 启动起来并交出 `RemoteRuntime`——这正是 Docker/Modal/Fargate/Daytona 的模式。

## 相关概念

- [会话模型](/concepts/02-session-model.md)
- [部署矩阵](/concepts/04-deployments.md)
- [配置与扩展](/concepts/06-configuration-and-extension.md)
- [Agent 集成](/concepts/09-agent-integration.md)
