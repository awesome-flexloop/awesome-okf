---
type: Example
title: 中间件与测试
description: 演示 CORSMiddleware 跨域配置、GZipMiddleware 压缩、自定义 BaseHTTPMiddleware 请求日志、BackgroundTasks 后台任务，以及使用 TestClient 和 dependency_overrides 编写完整测试用例。
tags: [fastapi, example, middleware, cors, testing]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: applications-source
    resource: /references/applications.md
    title: applications 模块源码信源
  - id: middleware-source
    resource: /references/middleware-exceptions.md
    title: middleware 与 exceptions 模块信源
  - id: routing-source
    resource: /references/routing.md
    title: routing 模块源码信源
---

# 中间件与测试

本示例演示 FastAPI v0.141.1 的中间件配置与测试实践。FastAPI 的中间件模块（`fastapi.middleware`）是对 Starlette 中间件的薄再导出层（F-092、F-093），不在本地重写实现。中间件在 `build_middleware_stack` 中按 ServerErrorMiddleware→用户中间件→ExceptionMiddleware→AsyncExitStackMiddleware→router 的顺序反向包裹（F-011）。测试使用从 Starlette 再导出的 `TestClient`（F-128），配合 `dependency_overrides` 实现依赖替换。

## 场景说明

构建一个带中间件链的任务管理 API：

1. **CORS 中间件**：允许前端开发服务器跨域访问
2. **GZip 中间件**：压缩大于 500 字节的响应
3. **自定义日志中间件**：记录每个请求的方法、路径、状态码和耗时
4. **后台任务**：创建任务后异步发送通知
5. **完整测试**：使用 TestClient 测试正常流程、校验错误、404 异常和依赖替换

## 完整代码

```python
import time
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        print(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.4f}s)"
        )
        return response


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    priority: int = Field(default=1, ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: int
    completed: bool = False


class NotificationService:
    def send(self, task_id: int, title: str) -> None:
        print(f"[Notification] Task {task_id} created: {title}")


def get_notification_service() -> NotificationService:
    return NotificationService()


tasks_db: dict[int, dict] = {}
_next_id = 1

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    notifier: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict:
    global _next_id
    task_id = _next_id
    _next_id += 1
    record = {
        "id": task_id,
        "title": task.title,
        "priority": task.priority,
        "completed": False,
    }
    tasks_db[task_id] = record
    background_tasks.add_task(notifier.send, task_id, task.title)
    return record


@router.get("/", response_model=list[TaskResponse])
def list_tasks() -> list[dict]:
    return list(tasks_db.values())


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> dict:
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return tasks_db[task_id]


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int) -> dict:
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    tasks_db[task_id]["completed"] = True
    return tasks_db[task_id]


app = FastAPI(
    title="任务管理 API",
    version="1.0.0",
    description="中间件与测试示例",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(RequestLogMiddleware)

app.include_router(router)
```

### 测试代码

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_task():
    response = client.post(
        "/tasks/",
        json={"title": "Learn FastAPI", "priority": 3},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["priority"] == 3
    assert data["completed"] is False
    assert "id" in data


def test_create_task_validation_error():
    response = client.post(
        "/tasks/",
        json={"title": "", "priority": 10},
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) >= 1


def test_list_tasks():
    client.post("/tasks/", json={"title": "Task A"})
    client.post("/tasks/", json={"title": "Task B"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_task_not_found():
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 99999 not found"


def test_complete_task():
    create_resp = client.post("/tasks/", json={"title": "Complete me"})
    task_id = create_resp.json()["id"]
    response = client.post(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_cors_headers():
    response = client.get(
        "/tasks/",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_process_time_header():
    response = client.get("/tasks/")
    assert "x-process-time" in response.headers


class MockNotifier:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    def send(self, task_id: int, title: str) -> None:
        self.calls.append((task_id, title))


def test_dependency_override():
    mock_notifier = MockNotifier()
    app.dependency_overrides[get_notification_service] = lambda: mock_notifier

    response = client.post(
        "/tasks/",
        json={"title": "Test with mock", "priority": 2},
    )
    assert response.status_code == 201

    mock_notifier.send = lambda *a, **kw: None
    app.dependency_overrides.clear()
```

## 代码解析

### 中间件栈构建顺序

`app.add_middleware(...)` 将中间件加入 `user_middleware` 列表。FastAPI 在 `build_middleware_stack` 中按固定顺序构建中间件链（F-011）：最外层是 `ServerErrorMiddleware`（捕获未处理异常返回 500），然后是用户添加的中间件（按添加顺序反向包裹），接着是 `ExceptionMiddleware`（处理 HTTPException 和系统异常），再是 `AsyncExitStackMiddleware`（管理依赖的异步上下文栈），最内层是 router。因此后添加的中间件更靠近应用层、先执行请求逻辑。

### CORSMiddleware 跨域配置

`CORSMiddleware` 从 `starlette.middleware.cors` 再导出（F-092）。FastAPI 的 `middleware/cors.py` 仅含一行导入语句，不做任何重写（F-138、F-139），保持与上游 Starlette 完全同步。配置参数包括 `allow_origins`（允许的源列表）、`allow_credentials`（是否允许携带 cookie）、`allow_methods`（允许的 HTTP 方法）、`allow_headers`（允许的请求头）。中间件自动处理预检请求（OPTIONS）并在响应中添加 CORS 头。

### GZipMiddleware 响应压缩

`GZipMiddleware` 同样是单行再导出（F-093、F-140、F-141）。`minimum_size=500` 指定仅压缩大于 500 字节的响应体，避免对小响应产生不必要的压缩开销。中间件检查请求的 `Accept-Encoding` 头，客户端支持 gzip 时才压缩并设置 `Content-Encoding: gzip`。

### 自定义 BaseHTTPMiddleware

`RequestLogMiddleware` 继承 Starlette 的 `BaseHTTPMiddleware`，重写 `async def dispatch(self, request, call_next)` 方法。`call_next(request)` 调用下游中间件和路由并返回 Response。在 `call_next` 前后可以分别执行请求预处理和响应后处理逻辑。本示例在响应头中添加 `X-Process-Time`，并在控制台打印请求日志。`BaseHTTPMiddleware` 是 Starlette 提供的标准中间件基类，FastAPI 完整兼容。

### BackgroundTasks 后台任务

`BackgroundTasks` 从 `fastapi.background` 导入并在 `__init__.py` 公开导出（F-003）。它继承自 `StarletteBackgroundTasks`，重写 `add_task(func, *args, **kwargs)` 方法，使用 `ParamSpec` 保留函数参数类型签名（F-152、F-153）。通过在端点参数中声明 `background_tasks: BackgroundTasks`，FastAPI 自动注入实例（F-059 中 `add_non_field_param_to_dependency` 识别 `StarletteBackgroundTasks` 类型）。`background_tasks.add_task(notifier.send, task_id, task.title)` 注册后台任务，任务在响应发送后执行，适合发送通知、写入日志等非阻塞操作。

### TestClient 测试客户端

`TestClient` 从 `starlette.testclient` 再导出（F-128、F-148、F-149），FastAPI 不做子类化或扩展。它基于 httpx 构建，提供与 requests 库兼容的 API：`get`、`post`、`put`、`delete` 等方法发送请求，返回 Response 对象。测试中通过 `response.status_code` 断言状态码，`response.json()` 解析 JSON 响应，`response.headers` 检查响应头。

### 校验错误测试

发送空 title 和越界 priority（10 > 5）时，Pydantic 校验失败，FastAPI 返回 422 状态码。默认的 `RequestValidationError` 处理器在 `__init__` 中注册（F-010），响应体的 `detail` 字段包含错误列表，每个错误含 `loc`（错误位置）、`msg`（错误消息）、`type`（错误类型）。

### dependency_overrides 测试替换

`app.dependency_overrides = {}` 在应用构造时初始化（F-009）。测试中设置 `app.dependency_overrides[get_notification_service] = lambda: mock_notifier` 后，`solve_dependencies` 在求解依赖时检查覆盖字典，使用 mock 对象替代真实服务（F-064）。这使得测试可以不依赖外部服务（如邮件服务器、数据库）。测试结束后调用 `app.dependency_overrides.clear()` 恢复原始依赖。替换在运行时生效，无需重建应用或路由。

## 运行方式

```bash
pip install fastapi uvicorn pydantic httpx
uvicorn main:app --reload
```

运行测试：

```bash
pip install pytest
pytest test_main.py -v
```

## 源码溯源

| API/概念 | 源码位置 | 事实编号 |
|---------|---------|---------|
| `CORSMiddleware` 再导出 | `middleware/cors.py:1` | F-092 |
| `GZipMiddleware` 再导出 | `middleware/gzip.py:1` | F-093 |
| CORS 模块薄再导出细节 | `middleware/cors.py:1` | F-138, F-139 |
| GZip 模块薄再导出细节 | `middleware/gzip.py:1` | F-140, F-141 |
| 中间件栈构建顺序 | `applications.py:1020-1068` | F-011 |
| 默认异常处理器注册 | `applications.py:1003-1012` | F-010 |
| `BackgroundTasks` 类 | `background.py:11-61` | F-127 |
| `BackgroundTasks` ParamSpec | `background.py:6-8,40-53` | F-152 |
| BackgroundTasks 方法重写 | `background.py:11-61` | F-153 |
| `TestClient` 再导出 | `testclient.py:1` | F-128 |
| TestClient 不做扩展 | `testclient.py:1` | F-148, F-149 |
| `dependency_overrides` 初始化 | `applications.py:937-999` | F-009 |
| 依赖覆盖求解逻辑 | `dependencies/utils.py:586-731` | F-064 |
| BackgroundTasks 参数注入 | `dependencies/utils.py:350-371` | F-059 |
| `HTTPException` | `exceptions.py:17-83` | F-101 |

## 相关概念

- [中间件与 CORS](/concepts/10-middleware-cors.md)
- [异常处理与校验错误](/concepts/11-exception-handling.md)
- [测试与高级并发](/concepts/13-testing-advanced.md)
- [FastAPI 应用类](/concepts/01-application.md)
- [依赖注入系统](/concepts/04-dependency-injection.md)
