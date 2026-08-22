---
type: Reference
title: "JupyverseModule 主模块信源"
description: "jupyverse 顶级模块，继承 FPS FastAPIModule，负责应用初始化、CORS 配置、服务器启动和生命周期管理。"
tags: [module, fastapi, lifecycle, cors, server]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/main/__init__.py
    title: jupyverse_api/main/__init__.py
---

# JupyverseModule 主模块信源

## AppModule

```python
class AppModule(Module):
    def __init__(self, name: str, *, mount_path: str | None = None):
        super().__init__(name)
        self.mount_path = mount_path

    async def prepare(self) -> None:
        app = await self.get(FastAPI)
        _app = App(app, mount_path=self.mount_path)
        self.put(_app)
```

AppModule 在 prepare 阶段获取 FastAPI 实例，包装为 App 实例后注册到容器。

## JupyverseModule

```python
class JupyverseModule(FastAPIModule):
    def __init__(self, name: str, **kwargs):
        self.jupyverse_config = JupyverseConfig(**kwargs)
        # debug 模式下设置 structlog 日志级别为 DEBUG
        # 创建 Lifespan 实例
        # 如果 start_server=True，添加 FPS ServerModule
```

### prepare() 阶段

1. 调用 `super().prepare()` 完成 FastAPI 基础设置
2. 获取 App 实例
3. 如果配置了 `allow_origins`，添加 CORS 中间件
4. 创建并注册 `QueryParams`、`Host`、`Lifespan` 实例

### start() 阶段

1. 通过 `create_task_group` 并行启动 `super().start()`
2. 等待服务器启动（`server.started.wait()`）
3. 合并查询参数，构建访问 URL
4. 记录日志 "Server running"，如果 `open_browser=True` 则打开浏览器

### stop() 阶段

```python
async def stop(self) -> None:
    self.lifespan.shutdown_request.set()
```

设置关闭事件，通知所有等待该事件的任务清理退出。

## 核心数据类

### JupyverseConfig

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| start_server | bool | True | 是否启动 HTTP 服务器 |
| host | str | "127.0.0.1" | 监听地址 |
| port | int | 8000 | 监听端口 |
| websocket_permessage_deflate | bool | False | WebSocket 压缩 |
| allow_origins | Json[list[str]] | [] | CORS 允许源 |
| open_browser | bool | False | 自动打开浏览器 |
| query_params | Json[dict[str,str]] | {} | URL 查询参数 |
| debug | bool | False | 调试模式 |
| openapi_url | str\|None | "/openapi.json" | OpenAPI 文档路径 |
| routes_url | str\|None | None | 路由信息路径 |

### Lifespan

```python
class Lifespan:
    def __init__(self):
        self.shutdown_request = Event()
```

使用 anyio Event 作为关闭信号，各插件可通过等待此事件实现优雅关闭。

### QueryParams / Host

```python
class QueryParams(BaseModel):
    d: dict[str, str]

class Host(BaseModel):
    url: str
```
