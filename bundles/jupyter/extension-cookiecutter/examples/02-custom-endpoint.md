---
type: Example
title: 添加自定义 API 端点
description: 以 PingHandler 为基础，演示如何添加多个自定义 API 端点，包括路径参数、POST 请求、请求体验证和错误处理。
tags: [example, custom-endpoint, rest-api, post, crud]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: handler-py
    resource: /references/handler-source.md
    title: PingHandler 请求处理器源码解析
---

## 概述

本示例演示如何在模板生成的项目基础上添加多个 REST API 端点，实现一个简单的内存数据存储服务。我们将创建一个 "items" CRUD 接口。

## 步骤 1：创建新的 Handler

在 `my_extension/handlers.py` 中添加 ItemsHandler 和 ItemHandler：

```python
import json
import uuid
import tornado
from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler


# 简单的内存存储（生产环境应使用数据库）
_ITEMS = {}


class PingHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def ping_response(self):
        return self.settings["ping_response"]

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"ping_response": self.ping_response}))


class ItemsHandler(ExtensionHandlerMixin, APIHandler):
    """处理 /items 集合端点"""

    @tornado.web.authenticated
    def get(self):
        """GET /items - 列出所有 items"""
        limit = int(self.get_argument("limit", default="10"))
        items = list(_ITEMS.values())[:limit]
        self.finish(json.dumps({"items": items, "total": len(_ITEMS)}))

    @tornado.web.authenticated
    def post(self):
        """POST /items - 创建新 item"""
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid JSON body"}))
            return

        name = data.get("name")
        if not name:
            self.set_status(400)
            self.finish(json.dumps({"error": "name is required"}))
            return

        item_id = str(uuid.uuid4())[:8]
        item = {"id": item_id, "name": name, "value": data.get("value", 0)}
        _ITEMS[item_id] = item

        self.set_status(201)
        self.finish(json.dumps(item))


class ItemHandler(ExtensionHandlerMixin, APIHandler):
    """处理 /items/{id} 单个资源端点"""

    @tornado.web.authenticated
    def get(self, item_id):
        """GET /items/{id} - 获取单个 item"""
        item = _ITEMS.get(item_id)
        if item is None:
            self.set_status(404)
            self.finish(json.dumps({"error": f"Item {item_id} not found"}))
            return
        self.finish(json.dumps(item))

    @tornado.web.authenticated
    def put(self, item_id):
        """PUT /items/{id} - 更新 item"""
        if item_id not in _ITEMS:
            self.set_status(404)
            self.finish(json.dumps({"error": f"Item {item_id} not found"}))
            return

        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid JSON body"}))
            return

        item = _ITEMS[item_id]
        if "name" in data:
            item["name"] = data["name"]
        if "value" in data:
            item["value"] = data["value"]
        self.finish(json.dumps(item))

    @tornado.web.authenticated
    def delete(self, item_id):
        """DELETE /items/{id} - 删除 item"""
        if item_id not in _ITEMS:
            self.set_status(404)
            self.finish(json.dumps({"error": f"Item {item_id} not found"}))
            return

        del _ITEMS[item_id]
        self.set_status(204)
        self.finish()
```

## 步骤 2：注册路由

修改 `my_extension/extension.py`，在 handlers 列表中添加新路由：

```python
from traitlets import Unicode
from jupyter_server.extension.application import ExtensionApp
from .handlers import PingHandler, ItemsHandler, ItemHandler


class Extension(ExtensionApp):

    name = "my_extension"
    handlers = [
        ("my-extension/ping", PingHandler),
        ("my-extension/items", ItemsHandler),
        (r"my-extension/items/(\w+)", ItemHandler),  # 正则捕获 item_id
    ]

    ping_response = Unicode(default_value="pong").tag(config=True)

    def initialize_settings(self):
        self.settings.update({
            "ping_response": self.ping_response,
        })
```

注意路径参数的正则表达式 `(\w+)`——它匹配字母、数字和下划线，捕获的值作为参数传给 Handler 方法。

## 步骤 3：添加测试

在 `my_extension/tests/test_handlers.py` 中添加新端点的测试：

```python
import json
import pytest


async def test_get(jp_fetch):
    response = await jp_fetch("my-extension/ping")
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {"ping_response": "pong"}


async def test_create_item(jp_fetch):
    """测试创建 item"""
    response = await jp_fetch(
        "my-extension/items",
        method="POST",
        body=json.dumps({"name": "test item", "value": 42}),
        headers={"Content-Type": "application/json"},
    )
    assert response.code == 201
    payload = json.loads(response.body)
    assert "id" in payload
    assert payload["name"] == "test item"
    assert payload["value"] == 42


async def test_list_items(jp_fetch):
    """测试列出 items"""
    # 先创建一个 item
    await jp_fetch(
        "my-extension/items",
        method="POST",
        body=json.dumps({"name": "item1"}),
        headers={"Content-Type": "application/json"},
    )

    response = await jp_fetch("my-extension/items")
    assert response.code == 200
    payload = json.loads(response.body)
    assert "items" in payload
    assert payload["total"] >= 1


async def test_get_item(jp_fetch):
    """测试获取单个 item"""
    # 先创建
    create_resp = await jp_fetch(
        "my-extension/items",
        method="POST",
        body=json.dumps({"name": "item2"}),
        headers={"Content-Type": "application/json"},
    )
    item_id = json.loads(create_resp.body)["id"]

    # 获取
    response = await jp_fetch(f"my-extension/items/{item_id}")
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["id"] == item_id
    assert payload["name"] == "item2"


async def test_get_nonexistent_item(jp_fetch):
    """测试获取不存在的 item 返回 404"""
    with pytest.raises(Exception):
        await jp_fetch("my-extension/items/nonexistent-id")


async def test_create_item_invalid_json(jp_fetch):
    """测试发送无效 JSON 返回 400"""
    with pytest.raises(Exception):
        await jp_fetch(
            "my-extension/items",
            method="POST",
            body="not json",
            headers={"Content-Type": "application/json"},
        )
```

## 步骤 4：运行测试

```bash
pytest -v
```

预期所有测试通过。注意：由于 `_ITEMS` 是模块级字典，测试间共享状态，这在简单示例中是可接受的。生产环境应使用 pytest fixture 隔离数据。

## 步骤 5：手动测试

启动 Jupyter Server：
```bash
jupyter server --autoreload
```

使用 curl 测试 API：

```bash
TOKEN=<your-token>
BASE=http://localhost:8888

# Ping
curl $BASE/my-extension/ping?token=$TOKEN

# 创建 item
curl -X POST $BASE/my-extension/items?token=$TOKEN \
  -H "Content-Type: application/json" \
  -d '{"name":"hello","value":100}'

# 列出 items
curl $BASE/my-extension/items?token=$TOKEN

# 获取单个 item（替换 ID）
curl $BASE/my-extension/items/<item-id>?token=$TOKEN

# 更新 item
curl -X PUT $BASE/my-extension/items/<item-id>?token=$TOKEN \
  -H "Content-Type: application/json" \
  -d '{"value":200}'

# 删除 item
curl -X DELETE $BASE/my-extension/items/<item-id>?token=$TOKEN
```

## 关键知识点

1. **路径参数用正则捕获组**：`(r"my-extension/items/(\w+)", ItemHandler)`，捕获值传给方法参数
2. **每个 HTTP 动词一个方法**：get、post、put、delete
3. **错误处理**：JSON 解析错误返回 400，资源不存在返回 404
4. **状态码**：创建成功 201，删除成功 204，成功查询 200
5. **`self.get_argument()`**：获取 URL 查询参数
6. **`self.request.body`**：获取请求体（bytes 类型，需 json.loads）

## 相关概念

- [API Handler 开发](/concepts/05-api-handlers.md)
- [ExtensionApp 开发](/concepts/04-extension-app.md)
- [测试策略](/concepts/07-testing.md)
- [基础 Ping 扩展示例](/examples/01-basic-ping-extension.md)
