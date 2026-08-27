---
type: Concept
title: Web模块
description: FPS内置的FastAPIModule和ServerModule实现可插拔Web服务器，支持模块化路由注册和ASGI服务器生命周期管理。
tags: [web, fastapi, anycorn, asgi, server, http]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:54:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:54:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-web-py
    resource: /references/web-source.md
    title: src/fps/web/fastapi.py and src/fps/web/server.py
---

## Web模块概述

FPS提供两个内置Web模块：
- **FastAPIModule**：创建/持有一个FastAPI应用实例，在prepare阶段将其发布到Context
- **ServerModule**：在start阶段获取FastAPI实例，使用anycorn启动ASGI服务器

这两个模块通过Context的put/get机制协作，分离了"应用构建"和"服务运行"两个关注点。其他模块可以在prepare阶段获取FastAPI实例注册路由，无需关心服务器如何启动。

## 安装依赖

Web功能需要额外安装可选依赖：

```bash
pip install "fps[fastapi,anycorn]"
```

依赖版本要求：
- `fastapi >= 0.137.2, < 1.0.0`
- `anycorn >= 0.19.0, < 0.21.0`

## FastAPIModule

### 构造参数

```python
from fps.web.fastapi import FastAPIModule

class FastAPIModule(Module):
    def __init__(
        self,
        name: str,
        *,
        app: FastAPI | None = None,
        debug: bool | None = None,
        routes_url: str | None = None,
        openapi_url: str | None = "/openapi.json",
    ): ...
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `name` | 必填 | 模块名称 |
| `app` | `None` | 外部传入的FastAPI实例；为None时自动创建 |
| `debug` | `__debug__` | FastAPI的debug模式，默认取Python的`__debug__`值 |
| `routes_url` | `None` | 如果设置，注册一个GET端点返回所有路由列表 |
| `openapi_url` | `"/openapi.json"` | OpenAPI schema的URL路径，设为None禁用 |

### 生命周期行为

- **prepare阶段**：调用 `self.put(self.app)` 将FastAPI实例发布到Context（类型为 `FastAPI`）
- **start阶段**：如果设置了 `routes_url`，遍历所有路由并注册返回路由列表的端点

### 自定义FastAPI实例

可以传入预配置的FastAPI实例：

```python
from fastapi import FastAPI
from fps.web.fastapi import FastAPIModule

custom_app = FastAPI(title="My API", version="1.0")
fastapi_module = FastAPIModule("fastapi", app=custom_app)
```

### routes_url功能

设置 `routes_url` 后，FastAPIModule会在start阶段自动注册一个端点返回所有路由信息：

```python
FastAPIModule("fastapi", routes_url="/routes")
```

返回格式：
```json
[
  {"path": "/api/users", "name": "get_users", "methods": ["GET"]},
  {"path": "/ws", "name": "websocket", "methods": ["WEBSOCKET"]},
  {"path": "/static", "name": "static", "methods": ["MOUNT"]}
]
```

支持三种路由类型：
- `Route`（普通HTTP路由）：methods为HTTP方法列表
- `APIWebSocketRoute`（WebSocket）：methods为 `["WEBSOCKET"]`
- `Mount`（挂载子应用/静态文件）：methods为 `["MOUNT"]`

## ServerModule

### 构造参数

```python
from fps.web.server import ServerModule

class ServerModule(Module):
    def __init__(
        self,
        name: str,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        websocket_permessage_deflate: bool = True,
    ): ...
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `name` | 必填 | 模块名称 |
| `host` | `"127.0.0.1"` | 绑定地址 |
| `port` | `8000` | 监听端口 |
| `websocket_permessage_deflate` | `True` | WebSocket permessage-deflate压缩 |

### 生命周期行为

- **start阶段**：
  1. `await self.get(FastAPI)` 获取FastAPI实例（由FastAPIModule在prepare阶段发布）
  2. 创建 `anycorn.Config`，设置bind地址、WebSocket压缩、loglevel="WARN"
  3. 在task_group中启动 `anycorn.serve(app, config, shutdown_trigger=..., mode="asgi")`
  4. 注册teardown_callback：设置shutdown_event并等待server任务结束
  5. 调用 `self.done()` 标记启动完成

- **stop阶段**：teardown_callback被触发，设置shutdown_event通知anycorn优雅关闭

## 协作模式

典型的Web应用组装方式：

```python
from fps import Module
from fps.web.fastapi import FastAPIModule
from fps.web.server import ServerModule

class MyWebApp(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(FastAPIModule, "fastapi")
        self.add_module(ServerModule, "server", port=8000)
        self.add_module(MyRouter, "router")
```

模块执行顺序保证：
1. **prepare阶段**（并行）：
   - FastAPIModule.prepare → 发布FastAPI app
   - MyRouter.prepare → 获取FastAPI app，注册路由
   - ServerModule无prepare方法
2. **start阶段**（并行）：
   - FastAPIModule.start → 可选注册routes端点
   - MyRouter.start → 可启动其他后台任务
   - ServerModule.start → 获取app，启动anycorn服务器，调用done()

这确保了**所有路由在服务器启动前注册完毕**。

## 编写路由模块

路由模块应在prepare阶段获取FastAPI实例并注册路由：

```python
from fastapi import FastAPI
from fps import Module
from pydantic import BaseModel

class Message(BaseModel):
    content: str

class ChatRouter(Module):
    async def prepare(self):
        app = await self.get(FastAPI)

        @app.get("/")
        async def root():
            return {"message": "Hello from FPS"}

        @app.post("/chat")
        async def chat(msg: Message):
            return {"echo": msg.content}
```

## 静态文件与挂载

FastAPIModule的routes_url功能支持检测Mount类型的路由，静态文件挂载正常工作：

```python
from fastapi.staticfiles import StaticFiles

class StaticRouter(Module):
    async def prepare(self):
        app = await self.get(FastAPI)
        app.mount("/static", StaticFiles(directory="static"), name="static")
```

## WebSocket支持

```python
class WSRouter(Module):
    async def prepare(self):
        app = await self.get(FastAPI)

        @app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"Echo: {data}")
```

## 完整示例

```python
from fastapi import FastAPI
from fps import Module
from fps.web.fastapi import FastAPIModule
from fps.web.server import ServerModule

class APIRouter(Module):
    async def prepare(self):
        app = await self.get(FastAPI)

        @app.get("/api/health")
        async def health():
            return {"status": "ok"}

class MainApp(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(FastAPIModule, "fastapi", routes_url="/routes")
        self.add_module(ServerModule, "server", host="0.0.0.0", port=8000)
        self.add_module(APIRouter, "api")
```

运行：
```bash
fps main:MainApp
```

访问 `http://127.0.0.1:8000/api/health` 返回 `{"status":"ok"}`，访问 `http://127.0.0.1:8000/routes` 返回路由列表。

## 相关概念

- [模块系统](02-module-system.md)
- [生命周期阶段](04-lifecycle-phases.md)
- [配置系统](05-configuration-system.md)
- [可插拔Web服务器示例](../examples/03-web-server.md)
