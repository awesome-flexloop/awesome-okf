---
okf_version: "0.2"
type: example
title: "Jupyter Server API测试"
description: "使用jp_fetch和jp_ws_fetch测试Jupyter Server REST API和WebSocket通道，包括kernels、contents、sessions等端点。"
tags: [server, api-testing, jp-fetch, jp-ws-fetch, http, websocket, rest-api, kernels]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: test-server
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/tests/test_jupyter_server.py"
    title: "tests/test_jupyter_server.py"
  - id: jupyter-server-source
    resource: "/references/jupyter-server-source.md"
    title: "Server插件源码信源"
---

# Jupyter Server API测试

本文档演示如何使用pytest-jupyter的Server插件测试Jupyter Server的REST API和WebSocket通道。

## 前置条件

```bash
pip install "pytest-jupyter[server]"
```

```python
# conftest.py
pytest_plugins = ["pytest_jupyter.jupyter_server"]
```

## 示例1：测试Server基本信息

```python
from http import HTTPStatus

async def test_server_instance(jp_serverapp):
    """测试ServerApp正确启动"""
    from jupyter_server.serverapp import ServerApp
    assert isinstance(jp_serverapp, ServerApp)
    # Server已经启动
    assert jp_serverapp.web_app is not None

async def test_openapi_spec(jp_fetch):
    """测试获取OpenAPI spec端点"""
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == HTTPStatus.OK
    # spec.yaml返回YAML格式的API文档
    assert b"swagger" in response.body or b"openapi" in response.body

async def test_get_status(jp_fetch):
    """测试获取服务器状态"""
    response = await jp_fetch("api", "status", method="GET")
    assert response.code == HTTPStatus.OK
    import json
    status = json.loads(response.body)
    assert "connections" in status or "kernels" in status or "started" in status
```

## 示例2：Kernel生命周期测试

```python
import json
from http import HTTPStatus

async def test_create_kernel(jp_fetch):
    """测试创建kernel"""
    response = await jp_fetch(
        "api", "kernels",
        method="POST",
        body=json.dumps({"name": "python3"})
    )
    assert response.code == HTTPStatus.CREATED
    kernel = json.loads(response.body)
    assert "id" in kernel
    assert kernel["name"] == "python3"
    return kernel["id"]

async def test_list_kernels(jp_fetch):
    """测试列出kernels"""
    # 先创建一个kernel
    r = await jp_fetch(
        "api", "kernels",
        method="POST",
        body="{}"
    )
    kid = json.loads(r.body.decode())["id"]

    # 列出kernels
    response = await jp_fetch("api", "kernels", method="GET")
    assert response.code == HTTPStatus.OK
    kernels = json.loads(response.body)
    assert isinstance(kernels, list)
    assert any(k["id"] == kid for k in kernels)

async def test_get_kernel(jp_fetch):
    """测试获取单个kernel信息"""
    # 创建kernel
    r = await jp_fetch(
        "api", "kernels",
        method="POST",
        body="{}"
    )
    kid = json.loads(r.body.decode())["id"]

    # 获取kernel信息
    response = await jp_fetch("api", "kernels", kid, method="GET")
    assert response.code == HTTPStatus.OK
    kernel = json.loads(response.body)
    assert kernel["id"] == kid
    assert "connections" in kernel
    assert kernel["connections"] == 0  # 没有WebSocket连接时为0

async def test_delete_kernel(jp_fetch):
    """测试删除kernel"""
    r = await jp_fetch(
        "api", "kernels",
        method="POST",
        body="{}"
    )
    kid = json.loads(r.body.decode())["id"]

    # 删除kernel
    response = await jp_fetch("api", "kernels", kid, method="DELETE")
    assert response.code == HTTPStatus.NO_CONTENT or response.code == HTTPStatus.OK
```

## 示例3：WebSocket通道测试

```python
import json

async def test_kernel_websocket(jp_fetch, jp_ws_fetch):
    """测试通过WebSocket与kernel通信"""
    # 1. 创建kernel
    r = await jp_fetch(
        "api", "kernels",
        method="POST",
        body="{}"
    )
    kid = json.loads(r.body.decode())["id"]

    # 2. 建立WebSocket连接
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    try:
        # 3. 通过WebSocket发送execute_request
        import uuid
        msg_id = uuid.uuid4().hex
        msg_type = "execute_request"
        content = {"code": "print('hello from test')", "silent": False}

        await ws.write_message(json.dumps({
            "header": {
                "msg_id": msg_id,
                "msg_type": msg_type,
                "version": "5.3",
            },
            "parent_header": {},
            "metadata": {},
            "content": content,
            "channel": "shell",
        }))

        # 4. 接收消息（等待响应）
        for _ in range(20):  # 最多读20条消息
            raw = await ws.read_message()
            if raw is None:
                break
            msg = json.loads(raw)
            # 等待execute_reply或idle状态
            if (msg.get("msg_type", "") == "execute_reply" and
                msg.get("parent_header", {}).get("msg_id") == msg_id):
                assert msg["content"]["status"] == "ok"
                break
            if (msg.get("msg_type", "") == "status" and
                msg.get("content", {}).get("execution_state") == "idle"):
                break
    finally:
        ws.close()
```

## 示例4：查询参数与自定义Headers

```python
async def test_with_query_params(jp_fetch):
    """测试带查询参数的请求"""
    response = await jp_fetch(
        "api", "kernels",
        method="GET",
        params={"state": "idle"}  # 查询参数
    )
    assert response.code == HTTPStatus.OK

async def test_with_custom_headers(jp_fetch):
    """测试自定义请求头（jp_auth_header会自动合并）"""
    response = await jp_fetch(
        "api", "spec.yaml",
        method="GET",
        headers={"X-Custom-Header": "test-value"}
    )
    assert response.code == HTTPStatus.OK
```

## 示例5：POST请求带Body

```python
async def test_create_notebook_via_api(jp_fetch, jp_root_dir):
    """测试通过API创建notebook"""
    # 创建新notebook
    response = await jp_fetch(
        "api", "contents",
        method="POST",
        body=json.dumps({
            "type": "notebook",
            "path": "",
        })
    )
    assert response.code == HTTPStatus.CREATED
    nb_info = json.loads(response.body)
    assert "name" in nb_info
    assert "path" in nb_info

async def test_save_notebook(jp_fetch, jp_create_notebook):
    """测试保存notebook内容"""
    # 先创建一个notebook
    nb = jp_create_notebook("test.ipynb")

    # 通过API保存
    response = await jp_fetch(
        "api", "contents", "test.ipynb",
        method="PUT",
        body=json.dumps({
            "type": "notebook",
            "content": nb,
            "format": "json",
        })
    )
    assert response.code == HTTPStatus.OK
```

## 示例6：使用send_request简化测试

```python
async def test_send_request_util(send_request):
    """测试send_request fixture（只返回状态码）"""
    # send_request自动选择HTTP或WebSocket，返回状态码
    code = await send_request("api/spec.yaml", method="GET")
    assert code == HTTPStatus.OK

    # 404测试
    code = await send_request("api/nonexistent", method="GET")
    assert code == HTTPStatus.NOT_FOUND
```

## 示例7：jp_create_notebook使用

```python
async def test_create_and_read_notebook(jp_fetch, jp_create_notebook):
    """测试创建notebook并通过API读取"""
    # 创建notebook文件
    nb = jp_create_notebook("my_notebook.ipynb")
    assert "nbformat" in nb
    assert nb["nbformat"] == 4

    # 通过API读取
    response = await jp_fetch("api", "contents", "my_notebook.ipynb", method="GET")
    assert response.code == HTTPStatus.OK
    content = json.loads(response.body)
    assert content["type"] == "notebook"
```

## 示例8：测试认证与授权

```python
async def test_authorizer_integration(jp_serverapp, jp_server_authorizer, jp_fetch):
    """测试自定义授权器"""
    from pytest_jupyter.jupyter_server import _Authorizer

    # 创建授权器实例
    auth = jp_server_authorizer(parent=jp_serverapp)
    assert isinstance(auth, _Authorizer)

    # 测试URL规范化
    assert auth.normalize_url("foo") == "/foo"
    assert auth.normalize_url(f"{jp_serverapp.base_url}foo") == "/foo"

    # 测试URL到资源匹配
    assert auth.match_url_to_resource("/api/kernels") == "kernels"
    assert auth.match_url_to_resource("/api/shutdown") == "server"

    # 设置权限
    auth.permissions = {"actions": ["read"], "resources": ["spec"]}
    jp_serverapp.authorizer_class = jp_server_authorizer

    # 有read权限的请求应该成功
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == HTTPStatus.OK
```

## HTTP方法映射

jp_fetch支持标准HTTP方法，通过`method`参数指定：

| method | 典型用途 |
|--------|---------|
| `GET` | 获取资源（kernels列表、notebook内容、status） |
| `POST` | 创建资源（创建kernel、创建session、执行代码） |
| `PUT` | 更新资源（保存notebook、重命名） |
| `PATCH` | 部分更新 |
| `DELETE` | 删除资源（删除kernel、删除文件） |

## 运行测试

```bash
pytest tests/test_server_api.py -v --timeout=60
```

## 常见问题

### Q: 为什么有时收到500错误？
检查jp_logging_stream的输出——ServerApp日志被重定向到那里，DEBUG级别日志能帮助定位问题。

### Q: WebSocket连接超时？
jp_ws_fetch设置了120秒connect_timeout，确保测试中正确消费WebSocket消息，避免队列阻塞。

### Q: 测试间状态污染？
jp_server_cleanup是autouse fixture，每个测试后清理ServerApp。如果还有问题，检查是否在测试中修改了全局状态。

## 相关概念

- [Server插件详解](/concepts/05-server-plugin.md) — jp_fetch/jp_ws_fetch完整API
- [Fixture工厂模式](/concepts/08-fixture-factories.md) — 请求工厂的设计模式
- [自定义Server配置](04-custom-server-config.md) — 如何自定义ServerApp配置
