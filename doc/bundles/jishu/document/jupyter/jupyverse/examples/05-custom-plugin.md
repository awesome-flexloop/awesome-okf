---
type: Example
title: "自定义插件开发"
description: "从零创建一个简单的 Jupyverse 插件，添加自定义 API 端点，演示 FPS Module 生命周期和依赖注入。"
tags: [plugin, development, fps, custom, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: plugin_dev
    resource: /concepts/12-plugin-development.md
    title: 插件开发指南
  - id: fps
    resource: /concepts/03-fps-module-system.md
    title: FPS 模块系统
---

# 自定义插件开发

本示例演示如何创建一个简单的 Jupyverse 插件，添加一个自定义问候 API 端点。

## 项目结构

```
fps-hello/
├── pyproject.toml
└── src/
    └── fps_hello/
        ├── __init__.py
        ├── config.py
        └── main.py
```

## 1. 配置文件：pyproject.toml

```toml
[project]
name = "fps-hello"
version = "0.1.0"
description = "A simple hello-world plugin for Jupyverse"
requires-python = ">=3.10"
dependencies = [
    "fps>=0.6.3",
    "jupyverse-api>=0.14.0",
    "fastapi",
]

[project.entry-points."jupyverse.modules"]
hello = "fps_hello.main:HelloModule"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/fps_hello"]
```

## 2. 配置类：src/fps_hello/config.py

```python
from jupyverse_api.config import Config

class HelloConfig(Config):
    greeting: str = "Hello"
    default_name: str = "World"
```

## 3. 模块入口：src/fps_hello/main.py

```python
from typing import Any
from fps import Module
from fastapi import APIRouter, Depends
from jupyverse_api.app import App
from jupyverse_auth import Auth, User
from jupyverse_api.router import Router
from .config import HelloConfig


class _HelloService(Router):
    """问候服务，提供 /api/hello 端点。"""

    def __init__(self, app: App, auth: Auth, config: HelloConfig):
        super().__init__(app=app)
        self.config = config
        router = APIRouter()

        @router.get("/api/hello")
        async def hello(
            name: str | None = None,
            user: User = Depends(auth.current_user()),
        ) -> dict[str, Any]:
            target = name or config.default_name
            # 使用认证后的用户名（如果有）
            if user.username:
                target = user.name or user.username
            return {
                "message": f"{config.greeting}, {target}!",
                "from": "fps-hello-plugin"
            }

        @router.get("/api/hello/greet/{name}")
        async def greet_person(
            name: str,
            user: User = Depends(auth.current_user()),
        ) -> dict[str, str]:
            return {"greeting": f"{config.greeting}, {name}!"}

        self.include_router(router)


class HelloModule(Module):
    """FPS 模块入口，管理 HelloService 的生命周期。"""

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name)
        self.config = HelloConfig(**kwargs)

    async def prepare(self) -> None:
        # 注册配置
        self.put(self.config, HelloConfig)

        # 获取依赖
        app = await self.get(App)
        auth = await self.get(Auth)  # type: ignore[type-abstract]

        # 创建服务
        service = _HelloService(app, auth, self.config)

        # 注册服务（可被其他模块获取）
        self.put(service, _HelloService)

        self.done()
```

## 4. 初始化文件：src/fps_hello/__init__.py

```python
"""fps-hello: A simple Jupyverse plugin."""
```

## 5. 安装插件

```bash
cd fps-hello
pip install -e .
```

## 6. 启动 Jupyverse

```bash
jupyverse
```

插件会被自动发现并加载。

## 7. 测试端点

```bash
# 基本问候
curl http://127.0.0.1:8000/api/hello
# → {"message": "Hello, World!", "from": "fps-hello-plugin"}

# 自定义名称
curl "http://127.0.0.1:8000/api/hello?name=Jupyverse"
# → {"message": "Hello, Jupyverse!", "from": "fps-hello-plugin"}

# 路径参数
curl http://127.0.0.1:8000/api/hello/greet/Developer
# → {"greeting": "Hello, Developer!"}
```

## 8. 自定义配置

使用 `--set` 覆盖配置：

```bash
jupyverse --set "hello.greeting=Welcome" --set "hello.default_name=Friend"

curl http://127.0.0.1:8000/api/hello
# → {"message": "Welcome, Friend!", "from": "fps-hello-plugin"}
```

## 进阶：添加 WebSocket 端点

```python
# 在 _HelloService.__init__ 中添加
@router.websocket("/api/hello/ws")
async def hello_ws(websocket, auth: Auth = Depends(auth.websocket_auth())):
    await websocket.accept()
    while True:
        name = await websocket.receive_text()
        await websocket.send_text(f"{config.greeting}, {name}!")
```

## 进阶：使用后台任务

```python
from anyio import create_task_group, sleep

class _HelloService(Router):
    def __init__(self, ...):
        # ... 路由注册 ...
        self._running = True

    async def background_tick(self):
        while self._running:
            print("Hello plugin tick")
            await sleep(60)

    async def stop(self):
        self._running = False


class HelloModule(Module):
    async def prepare(self):
        service = _HelloService(...)
        self.put(service, _HelloService, teardown_callback=service.stop)

        async with create_task_group() as tg:
            tg.start_soon(service.background_tick)
            self.done()
```
