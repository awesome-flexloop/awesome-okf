---
type: Reference
title: fps.web 模块源码信源
description: fps Web模块（FastAPIModule和ServerModule）源码登记，对应src/fps/web/fastapi.py和src/fps/web/server.py
tags: [web, fastapi, anycorn, server]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-web-py
    resource: /references/web-source.md
    title: src/fps/web/fastapi.py and src/fps/web/server.py
---

## 源码位置

- `src/fps/web/fastapi.py` — FastAPIModule，约54行
- `src/fps/web/server.py` — ServerModule（anycorn服务器），约50行

## 可选依赖

Web功能需要安装可选依赖：
- `fastapi >=0.137.2,<1.0.0`
- `anycorn >=0.19.0,<0.21.0`

安装命令：`pip install "fps[fastapi,anycorn]"` 或 `pip install "fps[web]"`（注：web是meta extra还是需要单独安装fastapi+anycorn）

## FastAPIModule API

| API | 签名 | 行号 |
|-----|------|------|
| `FastAPIModule` | `class FastAPIModule(Module)` | fastapi.py L10 |
| `FastAPIModule.__init__` | `(name: str, *, app: FastAPI\|None=None, debug: bool\|None=None, routes_url: str\|None=None, openapi_url: str\|None="/openapi.json")` | L11 |
| `FastAPIModule.prepare()` | `() -> None`（async） | L27 |
| `FastAPIModule.start()` | `() -> None`（async） | L30 |

### FastAPIModule 行为

- `prepare()`阶段：调用`self.put(self.app)`发布FastAPI实例，让其他模块可以在prepare阶段获取app并注册路由
- `start()`阶段：如果设置了`routes_url`，遍历所有路由（使用`iter_route_contexts`），分类收集：
  - `APIWebSocketRoute` → methods: `["WEBSOCKET"]`
  - `routing.Mount` → methods: `["MOUNT"]`
  - `routing.Route` → methods: HTTP方法列表
  - 注册GET端点返回routes JSON列表

## ServerModule API

| API | 签名 | 行号 |
|-----|------|------|
| `ServerModule` | `class ServerModule(Module)` | server.py L12 |
| `ServerModule.__init__` | `(name: str, *, host: str="127.0.0.1", port: int=8000, websocket_permessage_deflate: bool=True)` | L13 |
| `ServerModule.start()` | `() -> None`（async） | L27 |

### ServerModule 行为

- `start()`阶段：
  - 通过`await self.get(FastAPI)`获取FastAPIModule发布的app实例
  - 创建`anycorn.Config`，设置bind地址、websocket压缩、loglevel="WARN"
  - 在task_group中启动`anycorn.serve(app, config, shutdown_trigger=..., mode="asgi")`
  - 注册teardown_callback：设置`shutdown_event`并等待server任务结束
  - 调用`self.done()`标记启动完成（因为server是长驻任务）

## 协作关系

```
FastAPIModule (prepare阶段发布FastAPI app)
    ↓ put(FastAPI)
Router模块 (prepare阶段获取app，注册路由)
    ↓
ServerModule (start阶段获取app，启动anycorn服务器)
```

关键顺序：路由注册必须在ServerModule启动服务器之前完成，这通过prepare→start两阶段分离保证——FastAPIModule和Router都在prepare阶段操作app，ServerModule在start阶段启动服务器。
