---
type: Concept
title: "HTTP 协议：10 个路由、认证、幂等与异常传输"
description: "SWE-ReX server 的完整线协议：路由到 Runtime 方法的映射、X-API-Key 认证、X-Request-ID 单槽幂等、HTTP 511 异常重建、multipart 上传与 CLI 参数"
tags: [swe-rex, protocol, fastapi, http, authentication, idempotency]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:41:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-047、F-064 ~ F-083"
---

# HTTP 协议：10 个路由、认证、幂等与异常传输

`swerex-remote` 启动后是一个 FastAPI 应用。它没有自己的业务状态，只把 HTTP 请求翻译成 `LocalRuntime` 方法调用。协议设计有三个值得注意的点：**认证是可选但启动参数必填**、**幂等是单槽缓存**、**异常以 511 反向传输**。

## 路由总表

| 方法 | 路径 | 请求模型 | 响应模型 | Runtime 方法 | 事实 |
|---|---|---|---|---|---|
| GET | `/` | — | `{"message": "hello world"}` | — | F-077 |
| GET | `/is_alive` | — | `IsAliveResponse` | `is_alive()` | F-040、F-077 |
| POST | `/create_session` | `CreateSessionRequest` | `CreateSessionResponse` | `create_session()` | F-041、F-077 |
| POST | `/run_in_session` | `Action` | `Observation` | `run_in_session()` | F-042、F-044、F-077 |
| POST | `/close_session` | `CloseSessionRequest` | `CloseSessionResponse` | `close_session()` | F-046、F-077 |
| POST | `/execute` | `Command` | `CommandResponse` | `execute()` | F-045、F-077 |
| POST | `/read_file` | `ReadFileRequest` | `ReadFileResponse` | `read_file()` | F-046、F-077 |
| POST | `/write_file` | `WriteFileRequest` | `WriteFileResponse` | `write_file()` | F-046、F-077 |
| POST | `/upload` | multipart | `UploadResponse` | 文件落盘/解压 | F-078 |
| POST | `/close` | — | `CloseResponse` | `close()` | F-046、F-077 |

请求与响应都是 Pydantic 模型，`serialize_model()` 优先 `model_dump()`，兼容旧版 `dict()`（F-080）。

## 认证：`X-API-Key`

server 用 `APIKeyHeader(name="X-API-Key")` 声明头（F-072），中间件逻辑（F-073）：

```python
if AUTH_TOKEN:
    api_key = await api_key_header(request)
    if api_key != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")
```

三个细节：

1. `AUTH_TOKEN` 为空时**完全不校验**。这是本地调试的便利，也是部署时必须避免的配置。
2. 启动参数 `--auth-token` 同时设了 `default=""` 与 `required=True`（F-079）。实际效果是必须显式传参，但可以传空字符串。
3. 缺少 header 时 FastAPI 的 `APIKeyHeader` 抛 403；header 不匹配时中间件抛 401。测试 `test_unauthenticated_request` 对 10 个路由断言 403（F-083）——因为未带 header 在进入路由前就被拦下。

> 安全提示：`DockerDeployment`/`ModalDeployment`/`FargateDeployment`/`DaytonaDeployment` 都会为每个环境生成 UUID token（F-021、F-025、F-030、F-031），客户端用同一 token 连接。自建 server 时不要复用固定 token。

## 幂等：单槽 `ResponseManager`

`RemoteRuntime._request()` 为每次请求生成 UUID，放入 `X-Request-ID`（F-064）。server 中间件读取该头（F-074）：

```text
if request_id in cache: return cached response
else: execute, read full body, rebuild Response, cache it
```

`ResponseManager` 只保存**最后一个** request id 与响应（F-075）。类 docstring 明确写：

> “Note that in the case of multiple concurrent clients, idempotency isn't guaranteed.”

这意味着：

1. 同一客户端网络抖动重发上一条请求 → 命中缓存，不会重复执行。
2. 两个并发请求 → 后一个覆盖前一个的槽位；重发较早的请求不会命中。
3. 重试超过一条之前 → 不会命中。

`_request()` 默认 `num_retries=0`（F-064），所以重试是调用方显式选择，不是自动行为；开启后延迟从 0.1s 指数退避，加 0–0.5s 抖动，上限 5s。

## 异常传输：HTTP 511

这是 SWE-ReX 协议里最不寻常的部分。server 注册全局异常处理器（F-076）：

```python
_exc = _ExceptionTransfer(
    message=str(exc),
    class_path=type(exc).__module__ + "." + type(exc).__name__,
    traceback=traceback.format_exc(),
    extra_info=getattr(exc, "extra_info", {}),
)
return JSONResponse(status_code=511, content={"swerexception": _exc.model_dump()})
```

客户端 `_handle_response_errors()` 看到 511 就解析并调用 `_handle_transfer_exception()`（F-065、F-066）：

1. 若 `class_path` 是 `builtins.X`，从 `__builtins__` 取。
2. 否则尝试 `__import__(module)`；失败则退化为 `SwerexException(message)`。
3. 反射构造异常，设置 `extra_info`，`raise ... from None`。

效果：

```python
try:
    await runtime.run_in_session(BashAction(command="false"))
except NonZeroExitCodeError as e:
    ...  # 远程异常在本地仍是 NonZeroExitCodeError
```

`traceback` 会以 critical 级别打到客户端日志；`extra_info` 保留（例如 `BashIncorrectSyntaxError` 的 `bash_stdout`/`bash_stderr`）。

HTTP 异常（`HTTPException` / `StarletteHTTPException`）不进入 511 路径，直接交给 FastAPI 默认处理器（F-076）。

## 上传：multipart 与目录 zip

`/upload` 接收三个字段（F-078）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `file` | UploadFile | 文件内容 |
| `target_path` | Form str | 目标路径 |
| `unzip` | Form bool | 是否按 zip 解压到 `target_path` |

server 先写入临时目录，再：

- `unzip=True`：`zipfile.ZipFile.extractall(target_path)`，然后删除临时文件。
- `unzip=False`：`shutil.move(temp_file, target_path)`。

客户端 `RemoteRuntime.upload()`（F-068）对目录自动 `shutil.make_archive` 打 zip 并设 `unzip=true`；对文件直接上传并设 `unzip=false`。本地 `LocalRuntime.upload()` 则用 `copytree`/`copy`（F-061）。

## `is_alive` 的特殊语义

`RemoteRuntime.is_alive()`（F-067）与其他方法不同：连接失败、非 200 都返回 `IsAliveResponse(is_alive=False, message=...)`，不抛异常；只有 511 会重抛。

`IsAliveResponse.__bool__` 返回 `is_alive`（F-040），所以可以写：

```python
if await runtime.is_alive():
    ...
```

`_wait_until_alive()` 正是利用这一点轮询（F-089）：每 0.25s 调一次，直到 truthy 或超时。

## CLI 参数

`server.main()`（F-079）：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--host` | `0.0.0.0` | 绑定地址 |
| `--port` | `8000` | 监听端口 |
| `--auth-token` | `""`（required） | API key；必须显式传 |
| `-v/--version` | — | 单独使用，打印版本；与其他参数组合会报错退出 |

启动方式：

```bash
swerex-remote --port 8000 --auth-token <uuid>
# 或
python -m swerex --port 8000 --auth-token <uuid>
```

`__main__.py` 直接调用 `server.main()`（F-005、F-079）。

## 一个完整请求的样子

```http
POST /run_in_session HTTP/1.1
Host: 127.0.0.1:8000
X-API-Key: 1d87776a-1ab2-422e-bd80-fc34d810633f
X-Request-ID: 6f1c2f7e-...
Content-Type: application/json

{
  "command": "echo $MYVAR",
  "session": "default",
  "check": "raise",
  "action_type": "bash"
}
```

成功响应：

```json
{
  "output": "test\n",
  "exit_code": 0,
  "failure_reason": "",
  "expect_string": "SHELLPS1PREFIX",
  "session_type": "bash"
}
```

失败响应（HTTP 511）：

```json
{
  "swerexception": {
    "message": "Command 'false' failed with exit code 1...",
    "class_path": "swerex.exceptions.NonZeroExitCodeError",
    "traceback": "...",
    "extra_info": {}
  }
}
```

## 相关概念

- [架构分层](/concepts/01-architecture.md)
- [会话模型](/concepts/02-session-model.md)
- [失败模式与测试](/concepts/07-failure-modes-and-tests.md)
- [远程服务器示例](/examples/03-remote-server.md)
