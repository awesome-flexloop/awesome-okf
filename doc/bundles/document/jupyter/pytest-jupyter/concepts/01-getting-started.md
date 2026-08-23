---
okf_version: "0.2"
type: concept
title: "5分钟快速上手"
description: "安装 pytest-jupyter、配置 conftest.py、编写并运行第一个 Jupyter 测试用例。"
tags: [getting-started, installation, conftest, first-test, quickstart, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/README.md"
    title: "README.md"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pyproject.toml"
    title: "pyproject.toml"
  - id: conftest-example
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/tests/conftest.py"
    title: "tests/conftest.py"
---

# 5分钟快速上手

本文档带你在5分钟内完成 pytest-jupyter 的安装、配置和第一个测试用例的编写运行。

## 第一步：安装

根据你需要测试的Jupyter组件层级，选择对应的安装方式：

### 仅安装核心功能（Core层）

```bash
pip install pytest-jupyter
```

这将安装 `pytest>=7.0` 和 `jupyter_core>=5.7`，提供环境隔离、临时目录、asyncio支持等基础fixtures。

### 安装客户端功能（Core + Client层）

```bash
pip install "pytest-jupyter[client]"
```

额外安装 `jupyter_client>=7.4.0`、`nbformat>=5.3`、`ipykernel>=6.14`，提供内核启动和ZMQ管理fixtures。

### 安装服务端功能（Core + Client + Server层·推荐）

```bash
pip install "pytest-jupyter[server]"
```

额外安装 `jupyter_server>=1.21`（含tornado），提供完整的ServerApp生命周期管理、HTTP/WebSocket测试客户端。Server插件自动包含Client和Core的所有功能。

[F-004]

## 第二步：配置 conftest.py

在你的测试目录根部创建 `conftest.py`，声明需要加载的pytest-jupyter插件：

```python
# tests/conftest.py

# 按需选择加载的插件：
pytest_plugins = [
    # "pytest_jupyter",                      # 仅core（与下面二选一）
    # "pytest_jupyter.jupyter_client",       # core + client
    "pytest_jupyter.jupyter_server",         # core + client + server + tornasync（推荐）
]
```

> **提示**：`pytest_jupyter` 和 `pytest_jupyter.jupyter_core` 是等价的（因为`__init__.py`中做了`from .jupyter_core import *`）。加载`jupyter_server`会自动获得所有层的fixtures。

pytest-jupyter 自身的测试使用了以下配置作为参考：

```python
# pytest-jupyter 自带的 tests/conftest.py
import os
os.environ["JUPYTER_PLATFORM_DIRS"] = "1"
pytest_plugins = [
    "pytest_jupyter",
    "pytest_jupyter.jupyter_server",
    "pytest_jupyter.jupyter_client",
]
```

[F-005]

## 第三步：编写第一个测试

### 示例1：测试环境隔离（Core层）

```python
# tests/test_basic.py
import os
from jupyter_core import paths

def test_jupyter_environment_isolated(jp_environ):
    """测试Jupyter环境被正确隔离到临时目录"""
    # jp_environ fixture自动monkeypatch了所有Jupyter环境变量和路径
    data_dir = paths.jupyter_data_dir()
    # 数据目录应该在临时路径下（而非用户真实目录）
    assert os.path.exists(data_dir)
    print(f"Jupyter data dir (isolated): {data_dir}")
```

### 示例2：测试Jupyter Server API（Server层·异步测试）

```python
# tests/test_server_api.py
from http import HTTPStatus

async def test_server_openapi_spec(jp_fetch):
    """测试Jupyter Server的OpenAPI spec端点"""
    # jp_fetch自动处理base URL、认证token、URL编码
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == HTTPStatus.OK
    # response.body是bytes，可以解析为YAML/JSON
    assert b"openapi" in response.body or b"swagger" in response.body
```

### 示例3：测试内核启动（Client层）

```python
# tests/test_kernel.py

async def test_echo_kernel(jp_start_kernel):
    """测试echo内核能否启动并回显消息"""
    # 启动echo内核（快速回显内核，非完整IPython）
    km, kc = await jp_start_kernel("echo")
    assert km.kernel_name == "echo"

    # 发送执行请求
    msg = await kc.execute("hello world", reply=True)
    assert msg["content"]["status"] == "ok"

    # 测试结束后jp_start_kernel自动清理内核和ZMQ资源
```

[F-032]

## 第四步：运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看某个插件提供的所有fixtures
pytest --fixtures -p pytest_jupyter.jupyter_server

# 运行特定测试文件
pytest tests/test_server_api.py -v

# 带超时保护（推荐，防止测试挂起）
pytest tests/ -v --timeout=30
```

pytest-jupyter 的 pyproject.toml 中配置了默认超时为10秒（`timeout = 10`），使用`thread`方法。

[F-004]

## 验证可用Fixtures

安装并配置完成后，可以通过以下命令确认插件加载成功：

```bash
pytest --fixtures | grep jp_
```

你应该能看到所有以 `jp_` 开头的fixtures，包括：

- Core层：`jp_asyncio_loop`, `jp_home_dir`, `jp_data_dir`, `jp_config_dir`, `jp_environ`, `jp_kernel_dir`, `echo_kernel_spec`
- Client层：`jp_zmq_context`, `jp_start_kernel`
- Server层：`jp_serverapp`, `jp_fetch`, `jp_ws_fetch`, `jp_configurable_serverapp`, `jp_create_notebook`, `jp_auth_header`, `jp_base_url`, `jp_http_port`, `jp_root_dir`, `jp_template_dir`, `jp_server_cleanup`, `jp_server_authorizer`, `send_request`

## 常见问题

### Q: 为什么看到警告"The server plugin has not been installed"？

**A**：你在conftest中加载了`pytest_jupyter.jupyter_server`但没有安装server extras。运行：
```bash
pip install "pytest-jupyter[server]"
```

[F-070]

### Q: 可以与 pytest-asyncio 同时使用吗？

**A**：pytest-jupyter 使用自己的异步测试运行机制（通过`pytest_pyfunc_call`钩子），与pytest-asyncio可能存在冲突。官方建议不要同时使用。如果需要在fixture中运行异步代码，可以使用`jp_asyncio_loop.run_until_complete()`。

### Q: 测试中可以使用真实的用户Jupyter配置吗？

**A**：不推荐。`jp_environ` fixture默认将所有Jupyter路径隔离到临时目录。如果需要测试特定配置，可以通过`jp_configurable_serverapp`的config参数传入自定义配置。

### Q: 为什么默认base_url是"/a%40b/"？

**A**：这是故意设计的。`%40`是`@`的URL编码，用于测试框架是否正确处理包含URL编码字符的base URL场景。可以通过覆盖`jp_base_url` fixture自定义。

[F-075]

---

**下一步阅读：**
- [架构总览](/concepts/02-architecture-overview.md) — 深入理解插件加载机制、fixture依赖链和设计哲学
- [Core插件详解](/concepts/03-core-plugin.md) — 环境隔离和异步测试基础设施
- [Server插件详解](/concepts/05-server-plugin.md) — Jupyter Server测试全攻略
