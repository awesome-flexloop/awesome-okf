---
type: Concept
title: Python SDK
description: >
  openai-codex 是 Codex CLI 的官方 Python SDK，支持同步和异步客户端，
  通过子进程 JSON-RPC 驱动 Rust 二进制。本文详解其架构、API 接口、
  认证方式、沙箱控制与程序化 agent 调用。
tags: [openai-codex, python, sdk, api, async, json-rpc, programmatic]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Python SDK

`openai-codex` 是 Codex CLI 的官方 Python SDK，允许开发者以编程方式启动 Codex 线程、运行 turn、流式获取进度、控制工作区访问。SDK 通过子进程 JSON-RPC 与固定版本的 Rust 二进制通信。

## 包配置

```toml
[project]
name = "openai-codex"
version = "0.0.0-dev"
requires-python = ">=3.10"
dependencies = [
  "pydantic>=2.12",
  "openai-codex-cli-bin==0.147.0",
]

[build-system]
requires = ["uv_build>=0.11.19,<0.12"]
build-backend = "uv_build"
```

关键设计：
- 要求 Python 3.10+
- 使用 `uv_build` 构建后端（而非 setuptools）
- 固定依赖 `openai-codex-cli-bin==0.147.0`，确保 SDK 与经过测试的 Rust 二进制版本配对
- 运行时依赖只有 `pydantic`（数据验证）和原生二进制包

## 架构

```
┌──────────────────────────────────────┐
│  Python 应用代码                      │
├──────────────────────────────────────┤
│  openai-codex SDK                    │
│  ┌────────────┐  ┌────────────────┐  │
│  │ Codex (同步)│  │ AsyncCodex     │  │
│  │ Thread     │  │ AsyncThread    │  │
│  └─────┬──────┘  └───────┬────────┘  │
│        └──────┬───────────┘          │
│          CodexClient                  │
│          (JSON-RPC over stdio)        │
├──────────────────────────────────────┤
│  codex 二进制 (Rust, 子进程)          │
│  app-server (stdio JSON-RPC)         │
└──────────────────────────────────────┘
```

SDK 本身不实现任何 agent 逻辑。它：
1. 定位 `codex` 二进制（从 `codex_cli_bin` 包或 `CodexConfig.codex_bin`）
2. 以 `app-server` 模式启动子进程
3. 通过 stdin/stdout 发送 JSON-RPC 2.0 消息
4. 将响应解析为 Pydantic 模型
5. 管理线程、turn、通知的生命周期

## 公共 API

### 导出的主要类型

```python
from openai_codex import (
    # 客户端
    Codex,              # 同步客户端
    AsyncCodex,         # 异步客户端
    CodexConfig,        # 客户端配置

    # 线程与 turn
    Thread,             # 同步线程
    AsyncThread,        # 异步线程
    TurnHandle,         # 同步 turn 句柄
    AsyncTurnHandle,    # 异步 turn 句柄
    TurnResult,         # turn 结果

    # 输入
    Input,              # 联合输入类型
    TextInput,          # 文本输入
    ImageInput,         # 图像输入（URL）
    LocalImageInput,    # 本地图像
    SkillInput,         # skill 调用输入
    MentionInput,       # @mention 输入
    RunInput,           # 运行输入

    # 配置
    Sandbox,            # 沙箱预设
    ApprovalMode,       # 审批模式

    # 登录
    ChatgptLoginHandle,
    DeviceCodeLoginHandle,

    # 错误
    CodexError,
    CodexRpcError,
    TransportClosedError,
    RetryLimitExceededError,
    retry_on_overload,
)
```

### 同步客户端

`Codex` 类在构造时启动运行时连接，支持上下文管理器：

```python
class Codex:
    def __init__(self, config: CodexConfig | None = None) -> None:
        self._client = CodexClient(config=config)
        self._client.start()
        self._init = validate_initialize_metadata(self._client.initialize())

    def __enter__(self) -> "Codex": ...
    def __exit__(self, _exc_type, _exc, _tb) -> None: ...
    def close(self) -> None: ...

    def thread_start(self, ...) -> Thread: ...
    def login_chatgpt(self) -> ChatgptLoginHandle: ...
    def login_api_key(self, key: str) -> None: ...
```

### 沙箱控制

```python
class Sandbox(str, Enum):
    read_only = "read-only"
    workspace_write = "workspace-write"
    full_access = "full-access"
```

三档预设映射到底层 wire 策略：

| SDK 预设 | wire 类型 | 文件系统权限 |
|----------|-----------|-------------|
| `Sandbox.read_only` | `readOnly` | 只读 |
| `Sandbox.workspace_write` | `workspaceWrite` | 工作区可写（默认） |
| `Sandbox.full_access` | `dangerFullAccess` | 完全访问（危险） |

## 认证

SDK 复用已有的 Codex 认证，也支持显式登录：

### ChatGPT 浏览器登录

```python
with Codex() as codex:
    login = codex.login_chatgpt()
    print(login.auth_url)      # 打开浏览器访问
    print(login.wait().success)
```

### 设备码登录

```python
with Codex() as codex:
    login = codex.login_chatgpt_device_code()
    print(login.verification_url)
    print(login.user_code)
    login.wait()
```

### API Key

```python
with Codex() as codex:
    codex.login_api_key("sk-...")
```

## 生成的协议模型

SDK 包含从 app-server v2 协议自动生成的 Pydantic 模型：

```
sdk/python/src/openai_codex/generated/
├── __init__.py
├── v2_all.py                    # 所有 v2 请求/响应/通知模型
└── notification_registry.py     # 通知类型注册表
```

这些模型通过 datamodel-code-generator 从 JSON Schema 生成，与 Rust 的 `app-server-protocol` crate 保持同步。关键模型包括：

- `ThreadStartParams` / `ThreadStartResponse`
- `TurnStartParams` / `TurnStartResponse`
- `ThreadListParams` / `ThreadListResponse`
- `TurnCompletedNotification`
- `AgentMessageDeltaNotification`
- `AskForApproval` 相关类型

## 消息路由

底层 client 使用 `MessageRouter` 管理 JSON-RPC 请求/响应和服务器通知：

- 请求通过唯一 ID 匹配响应
- 通知（如 turn 进度、agent 消息 delta）通过注册的回调分发
- `Notification` 联合类型支持所有已知通知类型，未知通知降级为 `UnknownNotification`

## 模块结构

```
sdk/python/src/openai_codex/
├── __init__.py              # 公共 API 导出
├── api.py                   # Codex / AsyncCodex 高级接口
├── client.py                # CodexClient 同步底层客户端
├── async_client.py          # AsyncCodexClient 异步底层客户端
├── _sandbox.py              # Sandbox 枚举与 wire 映射
├── _approval_mode.py        # ApprovalMode 配置
├── _login.py                # 登录流程
├── _run.py                  # TurnResult 收集逻辑
├── _goal.py                 # Goal 操作状态
├── _inputs.py               # 输入类型标准化
├── _message_router.py       # JSON-RPC 消息路由
├── _initialize_metadata.py  # 初始化元数据验证
├── models.py                # 基础模型（Notification 等）
├── errors.py                # 错误类型层次
├── retry.py                 # 重载重试逻辑
├── types.py                 # 通用类型
└── generated/               # 自动生成的协议模型
```

## 错误处理

SDK 定义了完整的错误层次：

```python
class CodexError(Exception): ...
class TransportClosedError(CodexError): ...
class JsonRpcError(CodexError): ...
class ParseError(JsonRpcError): ...
class InvalidRequestError(JsonRpcError): ...
class MethodNotFoundError(JsonRpcError): ...
class InvalidParamsError(JsonRpcError): ...
class InternalRpcError(JsonRpcError): ...
class ServerBusyError(JsonRpcError): ...
class CodexRpcError(CodexError): ...
class RetryLimitExceededError(CodexError): ...
```

`is_retryable_error()` 和 `retry_on_overload` 装饰器提供自动重试能力。

## 开发与测试

```bash
cd sdk/python
uv sync                     # 安装依赖
uv run pytest               # 运行测试
uv run ruff check .         # lint
uv run ruff format .        # 格式化
```

测试使用 pytest，包含真实 app-server 集成测试（`test_real_app_server_integration.py`）。

## 相关概念

- [Rust 核心与 TUI](./02-rust-core-tui.md)
- [Node.js CLI 入口](./03-nodejs-cli.md)
- [沙箱执行模型](./04-sandbox-execution.md)
- [工作区架构](./01-workspace-architecture.md)
- [简介](./00-introduction.md)
