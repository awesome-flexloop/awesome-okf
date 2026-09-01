---
type: Reference
title: 测试源码解析（conftest.py 与 test_handlers.py）
description: 解析 pytest-jupyter 测试基础设施、conftest.py 配置、jp_fetch fixture 用法和异步 API 测试模式。
tags: [reference, testing, pytest, pytest-jupyter, async-test]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: conftest-py
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/%7B%7Bcookiecutter.package_name%7D%7D/conftest.py
    title: conftest.py 模板源码
  - id: test-handlers-py
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/%7B%7Bcookiecutter.package_name%7D%7D/%7B%7Bcookiecutter.package_name%7D%7D/tests/test_handlers.py
    title: test_handlers.py 模板源码
---

## conftest.py 源码解析

```python
import pytest

pytest_plugins = ["jupyter_server.pytest_plugin"]

@pytest.fixture
def jp_server_config(jp_server_config):
     return {"ServerApp": {"jpserver_extensions": {"{{ cookiecutter.package_name | replace('-', '_') }}": True}}}
```

### pytest_plugins 声明

```python
pytest_plugins = ["jupyter_server.pytest_plugin"]
```

这行启用 `pytest-jupyter` 插件的 `server` 扩展（安装方式：`pip install "pytest-jupyter[server]>=0.6"`）。它提供了一系列 pytest fixtures：

| Fixture | 作用 |
|---------|------|
| `jp_server_config` | 配置 Jupyter Server 实例的 fixture（可重写） |
| `jp_fetch` | 异步 HTTP 客户端，向测试中的 Jupyter Server 发送请求 |
| `jp_start` | 启动/停止 Jupyter Server 生命周期管理 |
| `jp_ws_fetch` | WebSocket 客户端（用于 kernel 测试） |
| `jp_serverapp` | 对 ServerApp 实例的直接引用 |

### jp_server_config fixture 重写

```python
@pytest.fixture
def jp_server_config(jp_server_config):
     return {"ServerApp": {"jpserver_extensions": {"{{ cookiecutter.package_name | replace('-', '_') }}": True}}}
```

这是 pytest fixture 覆盖（override）模式：
1. 接收同名的 `jp_server_config` fixture 作为参数（pytest 依赖注入机制）
2. 返回一个配置字典，在 `ServerApp.jpserver_extensions` 中将当前扩展设为 `True`（启用）
3. pytest-jupyter 启动测试服务器时会加载此配置，确保扩展被加载

注意包名使用 `replace('-', '_')` 将连字符转为下划线，因为 Jupyter 配置系统中扩展注册名必须是 Python 标识符。

## tests/__init__.py

```python
"""Python unit tests for {{ cookiecutter.package_name }}."""
```

测试包的初始化文件，仅包含一个 docstring。

## tests/test_handlers.py 源码解析

```python
import json


async def test_get(jp_fetch):
    response = await jp_fetch("{{ cookiecutter.package_name | replace('_', '-') }}/ping")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "ping_response": "pong"
    }
```

### 异步测试函数

```python
async def test_get(jp_fetch):
```

- `async def` 声明异步测试函数，pytest-asyncio（pytest-jupyter 依赖）自动处理事件循环
- `jp_fetch` 参数由 pytest fixture 注入，是一个异步 HTTP 客户端

### jp_fetch 调用

```python
response = await jp_fetch("{{ cookiecutter.package_name | replace('_', '-') }}/ping")
```

- `jp_fetch(path)` 向测试 Jupyter Server 发送 GET 请求（默认方法）
- 路径参数使用连字符版本的包名（`replace('_', '-')`），与 Extension.handlers 中注册的 URL 一致
- `await` 等待异步响应
- `jp_fetch` 自动处理认证（使用测试 token），无需手动设置 Authorization 头

`jp_fetch` 支持更多参数：
```python
# POST 请求
response = await jp_fetch("my-ext/data", method="POST", body=json.dumps({"key": "value"}))

# 带查询参数
response = await jp_fetch("my-ext/items", params={"limit": "10"})

# 自定义请求头
response = await jp_fetch("my-ext/data", headers={"X-Custom": "value"})
```

### 响应断言

```python
assert response.code == 200
payload = json.loads(response.body)
assert payload == {
    "ping_response": "pong"
}
```

三步验证：
1. **HTTP 状态码**：期望 200（成功）
2. **响应体解析**：`response.body` 是 bytes 类型，需要 `json.loads()` 解析
3. **内容精确匹配**：验证返回 JSON 与预期完全一致

## 测试执行流程

pytest-jupyter 执行测试时的完整流程：

```
pytest 启动
  │
  ├─ 加载 conftest.py
  │    ├─ 注册 jupyter_server.pytest_plugin
  │    └─ 重写 jp_server_config fixture（启用扩展）
  │
  ├─ 发现 test_get() 测试函数
  │    │
  │    ├─ pytest-jupyter 自动启动 Jupyter Server 实例（后台）
  │    │    ├─ 加载 jp_server_config 配置
  │    │    ├─ 发现并加载扩展（通过 jpserver_extensions: {ext_name: true}）
  │    │    └─ Extension.initialize_settings() 执行
  │    │
  │    ├─ 注入 jp_fetch fixture（异步客户端）
  │    │
  │    ├─ 执行 test_get() 函数体
  │    │    ├─ await jp_fetch(".../ping") → 发送 HTTP GET
  │    │    │    └─ PingHandler.get() 执行
  │    │    │         ├─ @authenticated 检查（jp_fetch 自动带 token）
  │    │    │         ├─ self.ping_response property → settings["ping_response"]
  │    │    │         └─ self.finish(json.dumps({"ping_response": "pong"}))
  │    │    │
  │    │    ├─ assert response.code == 200 ✓
  │    │    ├─ payload = json.loads(response.body)
  │    │    └─ assert payload == {"ping_response": "pong"} ✓
  │    │
  │    └─ 测试通过
  │
  └─ pytest-jupyter 关闭 Jupyter Server
```

## 测试扩展模式

### 添加多个端点测试

```python
async def test_post_data(jp_fetch):
    response = await jp_fetch(
        "my-ext/data",
        method="POST",
        body=json.dumps({"name": "test"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.code == 201
    payload = json.loads(response.body)
    assert "id" in payload

async def test_not_found(jp_fetch):
    with pytest.raises(Exception):  # jp_fetch 对非 2xx 抛异常
        await jp_fetch("my-ext/nonexistent")
```

### 测试配置覆盖

```python
@pytest.fixture
def jp_server_config(jp_server_config):
    return {
        "ServerApp": {"jpserver_extensions": {"my_extension": True}},
        "Extension": {"ping_response": "custom value"}
    }

async def test_custom_config(jp_fetch):
    response = await jp_fetch("my-extension/ping")
    payload = json.loads(response.body)
    assert payload["ping_response"] == "custom value"
```

## 相关概念

- [测试策略详解](../concepts/07-testing.md)
- [API Handler 开发指南](../concepts/05-api-handlers.md)
- [ExtensionApp 源码解析](extension-app-source.md)
