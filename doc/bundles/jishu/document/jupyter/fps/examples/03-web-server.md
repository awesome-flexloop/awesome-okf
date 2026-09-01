---
type: Example
title: 可插拔Web服务器
description: 使用FastAPIModule和ServerModule构建模块化Web应用，演示prepare阶段注册路由与start阶段启动服务器的协作。
tags: [example, web, fastapi, server, routing]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/web-source.md
    title: docs/guide.md A pluggable web server
  - id: fps-web-py
    resource: /references/web-source.md
    title: src/fps/web/fastapi.py and src/fps/web/server.py
---

## 概述

本示例使用FPS内置的 `FastAPIModule` 和 `ServerModule` 构建一个可插拔的Web服务器。路由注册与服务器启动通过生命周期阶段自动协调。

## 完整代码

创建 `server.py`：

```python
from fastapi import FastAPI
from fps import Module
from fps.web.fastapi import FastAPIModule
from fps.web.server import ServerModule
from pydantic import BaseModel

class Config(BaseModel):
    key: str = "count"
    value: int = 3

class Router(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.config = Config(**kwargs)

    async def prepare(self):
        app = await self.get(FastAPI)

        @app.get("/")
        def read_root():
            return {self.config.key: self.config.value}

class Main(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(FastAPIModule, "fastapi")
        self.add_module(ServerModule, "server")
        self.add_module(Router, "router")
```

## 运行

```bash
fps server:Main
```

打开浏览器访问 `http://127.0.0.1:8000`，返回：

```json
{"count": 3}
```

通过CLI修改配置：
```bash
fps server:Main --set router.key=items --set router.value=42
# 访问返回 {"items": 42}
```

类型错误会被Pydantic捕获：
```bash
fps server:Main --set router.value=foo
# RuntimeError: Cannot instantiate module 'root_module.router':
#   1 validation error for Config
#   value
#     Input should be a valid integer...
```

## 代码解析

### 为什么在prepare阶段注册路由

```python
async def prepare(self):
    app = await self.get(FastAPI)

    @app.get("/")
    def read_root():
        return {self.config.key: self.config.value}
```

路由注册放在 `prepare()` 而非 `start()` 中，是因为：
- `FastAPIModule` 在prepare阶段发布FastAPI app（通过 `self.put(self.app)`）
- `ServerModule` 在start阶段获取app并启动服务器
- prepare阶段在start阶段之前完成，确保所有路由在服务器启动前注册完毕

这是FPS三阶段生命周期的典型应用：**prepare用于框架资源的注册和配置，start用于服务启动**。

### 模块协作流程

```
prepare阶段（并行）:
  FastAPIModule.prepare() → put(FastAPI app)
  Router.prepare() → get(FastAPI) → 注册路由
  ServerModule 无prepare方法

start阶段（并行）:
  FastAPIModule.start() → 可选注册/routes端点
  Router.start() → 无操作（空start自动标记完成）
  ServerModule.start() → get(FastAPI) → 启动anycorn服务器 → done()
```

### Pydantic配置校验

```python
class Config(BaseModel):
    key: str = "count"
    value: int = 3

class Router(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.config = Config(**kwargs)
```

使用Pydantic BaseModel接收配置参数，可以获得：
- 自动类型转换和校验
- 默认值支持
- 清晰的错误信息
- `--help-all` 自动生成配置文档

### 自定义端口和主机

通过CLI参数修改服务器配置：
```bash
fps server:Main --set server.port=8080 --set server.host=0.0.0.0
```

## 扩展：多路由模块

可以添加多个路由模块，它们各自独立注册路由：

```python
class UsersRouter(Module):
    async def prepare(self):
        app = await self.get(FastAPI)

        @app.get("/users")
        def list_users():
            return [{"id": 1, "name": "Alice"}]

class Main(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(FastAPIModule, "fastapi")
        self.add_module(ServerModule, "server", port=8000)
        self.add_module(Router, "root_router")
        self.add_module(UsersRouter, "users_router")
```

## 关键要点

- 路由注册在prepare阶段完成，服务器在start阶段启动——生命周期阶段保证了正确的顺序
- FastAPIModule发布FastAPI实例，其他模块通过 `await self.get(FastAPI)` 获取并添加路由
- Pydantic BaseModel用于配置参数获得自动校验
- 多个路由模块可以独立添加，互不耦合
- ServerModule的 `done()` 必须在启动服务器任务后立即调用（源码中已处理）

## 相关概念

- [Web模块](../concepts/07-web-modules.md)
- [生命周期阶段](../concepts/04-lifecycle-phases.md)
- [配置系统](../concepts/05-configuration-system.md)
- [模块间共享对象](02-sharing-objects.md)
- [声明式配置应用](04-declarative-config.md)
