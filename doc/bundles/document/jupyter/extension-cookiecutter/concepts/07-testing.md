---
type: Concept
title: 测试策略
description: 掌握 pytest-jupyter 异步测试基础设施、jp_fetch fixture 使用、conftest.py 配置模式、以及如何为扩展 Handler 编写有效的单元测试和集成测试。
tags: [testing, pytest, pytest-jupyter, async, jp-fetch, conftest]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: test-source
    resource: /references/test-source.md
    title: 测试源码解析
---

## 测试栈概述

模板使用以下测试工具链：

| 工具 | 版本 | 作用 |
|------|------|------|
| pytest | >=7.0 | 测试框架 |
| pytest-jupyter[server] | >=0.6 | Jupyter Server 测试插件，提供异步 fixture |
| pytest-asyncio | （pytest-jupyter 依赖） | 异步测试支持 |

核心依赖是 `pytest-jupyter[server]`，它为测试 Jupyter Server 扩展提供了一整套基础设施，无需手动启动/管理 Jupyter Server 实例。

## conftest.py 配置

每个项目需要一个 `conftest.py` 文件来配置测试环境：

```python
import pytest

pytest_plugins = ["jupyter_server.pytest_plugin"]

@pytest.fixture
def jp_server_config(jp_server_config):
     return {"ServerApp": {"jpserver_extensions": {"my_extension": True}}}
```

### pytest_plugins

```python
pytest_plugins = ["jupyter_server.pytest_plugin"]
```

这行注册 `jupyter_server.pytest_plugin`，它提供以下关键 fixture：

| Fixture | 作用 |
|---------|------|
| `jp_fetch` | **最常用**——异步 HTTP 客户端，向测试服务器发送请求并返回响应 |
| `jp_server_config` | 服务器配置 fixture，可被覆盖 |
| `jp_serverapp` | 启动后的 ServerApp 实例引用 |
| `jp_start` | 手动控制服务器启动/停止 |
| `jp_ws_fetch` | WebSocket 客户端（kernel 测试用） |
| `jp_base_url` | 服务器基础 URL |

### jp_server_config 覆盖

```python
@pytest.fixture
def jp_server_config(jp_server_config):
     return {"ServerApp": {"jpserver_extensions": {"my_extension": True}}}
```

这是 pytest fixture 覆盖模式：
- 参数中的 `jp_server_config` 是原始 fixture（由插件提供）
- 返回值是新的配置字典，**覆盖**默认配置
- 在 `ServerApp.jpserver_extensions` 中设置扩展名为 `True`，确保测试时启用扩展

注意：fixture 名称必须与原 fixture 相同（`jp_server_config`），才能正确覆盖。

## 编写异步测试

### 基本模式

```python
import json
import pytest

async def test_ping_endpoint(jp_fetch):
    # 发送 GET 请求
    response = await jp_fetch("my-extension/ping")

    # 验证状态码
    assert response.code == 200

    # 解析 JSON 响应
    payload = json.loads(response.body)

    # 验证响应内容
    assert payload == {"ping_response": "pong"}
```

关键点：
- 测试函数使用 `async def`（异步函数）
- `jp_fetch` 参数由 fixture 自动注入
- 使用 `await` 等待异步 HTTP 响应
- `response.code` 是 HTTP 状态码（整数）
- `response.body` 是 bytes 类型，需要 `json.loads()` 解析

### jp_fetch 详细用法

```python
# GET 请求（默认）
response = await jp_fetch("my-extension/ping")

# POST 请求带 JSON body
response = await jp_fetch(
    "my-extension/data",
    method="POST",
    body=json.dumps({"name": "test"}),
    headers={"Content-Type": "application/json"},
)

# PUT 请求
response = await jp_fetch(
    "my-extension/items/abc",
    method="PUT",
    body=json.dumps({"value": 42}),
)

# DELETE 请求
response = await jp_fetch(
    "my-extension/items/abc",
    method="DELETE",
)

# 带查询参数
response = await jp_fetch(
    "my-extension/items",
    params={"limit": "10", "offset": "0"},
)
```

**注意**：
- `body` 参数接受字符串（需要先 `json.dumps()` 序列化）
- `params` 是查询参数字典，值必须是字符串
- URL 路径不要以 `/` 开头（jp_fetch 会自动拼接基础 URL）
- 路径中使用连字符版本的包名（与 handlers 注册一致）

### 测试不同 HTTP 状态码

`jp_fetch` 对于非 2xx 响应会抛出异常。要测试错误响应：

```python
async def test_not_found(jp_fetch):
    with pytest.raises(Exception) as exc_info:
        await jp_fetch("my-extension/nonexistent")
    assert exc_info.value.code == 404
```

或者使用 `raise_error=False`（如果 pytest-jupyter 版本支持）：

```python
response = await jp_fetch("my-extension/nonexistent", raise_error=False)
assert response.code == 404
```

## 测试配置覆盖

可以在测试中通过 fixture 覆盖扩展配置：

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

配置类名是 Extension 类的类名（如 `Extension`、`MyExtension`），与 traitlets 配置系统一致。

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest my_extension/tests/test_handlers.py

# 运行特定测试函数
pytest my_extension/tests/test_handlers.py -k "test_get"

# 详细输出
pytest -v

# 显示 print 输出
pytest -s
```

## 测试组织

推荐的测试文件结构：

```
my_extension/
└── tests/
    ├── __init__.py
    ├── conftest.py          # 可选：测试专用 fixtures
    ├── test_handlers.py     # Handler 测试
    ├── test_extension.py    # Extension 配置测试
    └── test_utils.py        # 工具函数测试
```

### 测试文件命名

- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 测试类以 `Test` 开头（可选，函数式测试更常见）

### 测试分类

| 测试类型 | 测试内容 | 工具 |
|---------|---------|------|
| **Handler 测试** | API 端点请求/响应 | jp_fetch + pytest |
| **配置测试** | traitlets 配置项行为 | 覆盖 jp_server_config |
| **工具函数测试** | 纯 Python 函数 | 标准 pytest（不需要 jp_fetch） |
| **集成测试** | 多端点交互 | jp_fetch + 复杂 fixture |

## 测试 Handler 的完整示例

```python
import json
import pytest


async def test_get_item(jp_fetch):
    """测试获取单个 item"""
    response = await jp_fetch("my-ext/items/item1")
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["id"] == "item1"


async def test_create_item(jp_fetch):
    """测试创建 item"""
    response = await jp_fetch(
        "my-ext/items",
        method="POST",
        body=json.dumps({"name": "new item"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.code == 201
    payload = json.loads(response.body)
    assert "id" in payload
    assert payload["name"] == "new item"


async def test_create_item_invalid_json(jp_fetch):
    """测试发送无效 JSON"""
    with pytest.raises(Exception):
        await jp_fetch(
            "my-ext/items",
            method="POST",
            body="not json",
            headers={"Content-Type": "application/json"},
        )


async def test_delete_item(jp_fetch):
    """测试删除 item"""
    response = await jp_fetch(
        "my-ext/items/item1",
        method="DELETE",
    )
    assert response.code == 204
```

## 常见测试问题

### 扩展未加载

如果测试报错 404 或扩展未找到，检查：
1. conftest.py 中 `jp_server_config` 是否正确设置了 `jpserver_extensions`
2. 包名是否使用下划线（Python 模块名），不是连字符
3. 是否以 `pip install -e ".[test]"` 安装了测试依赖

### jp_fetch 路径 404

确保 URL 路径：
- 不以 `/` 开头
- 使用连字符版本的包名（如 `my-extension/ping`，不是 `my_extension/ping`）
- 与 extension.py 中 handlers 注册的路径一致

### 异步测试不运行

确保：
- 安装了 `pytest-jupyter[server]`（包含 pytest-asyncio）
- 测试函数使用 `async def`
- conftest.py 中声明了 `pytest_plugins = ["jupyter_server.pytest_plugin"]`

## 相关概念

- [API Handler 开发](05-api-handlers.md)
- [构建系统详解](08-build-system.md)
- [测试源码解析](../references/test-source.md)
