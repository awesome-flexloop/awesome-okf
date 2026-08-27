---
type: Example
title: 基础 CRUD API
description: 使用 FastAPI 构建内存数据存储的完整增删改查 API，展示路径参数、查询参数、请求体模型、响应模型过滤、HTTPException 错误处理与 APIRouter 路由组织。
tags: [fastapi, example, crud, router, pydantic]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/applications.md
    title: FastAPI v0.141.1 源码信源
  - id: routing-source
    resource: /references/routing.md
    title: routing 模块源码信源
  - id: params-source
    resource: /references/params.md
    title: params 模块源码信源
---

# 基础 CRUD API

本示例演示如何使用 FastAPI v0.141.1 构建一个完整的商品管理 CRUD API。代码基于内存字典存储，无需数据库即可运行，覆盖了路径参数声明、查询参数分页、Pydantic 请求体校验、`response_model` 响应过滤、`HTTPException` 错误处理以及 `APIRouter` 模块化路由组织等核心能力。

## 场景说明

假设我们正在开发一个电商后台的商品管理模块，需要提供以下接口：

- `POST /items/`：创建新商品
- `GET /items/`：分页查询商品列表
- `GET /items/{item_id}`：按 ID 查询单个商品
- `PUT /items/{item_id}`：全量更新商品
- `DELETE /items/{item_id}`：删除商品

所有数据存储在进程内存中，重启后丢失。生产环境应替换为真实数据库。

## 完整代码

```python
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    tags: list[str] = []


items_db: dict[int, dict] = {}
next_id: int = 1

router = APIRouter(prefix="/items", tags=["items"])


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建商品",
)
def create_item(item: ItemCreate) -> dict:
    global next_id
    item_id = next_id
    next_id += 1
    items_db[item_id] = {"id": item_id, **item.model_dump()}
    return items_db[item_id]


@router.get(
    "/",
    response_model=list[ItemResponse],
    summary="查询商品列表",
)
def list_items(
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回的最大记录数")] = 10,
) -> list[dict]:
    all_items = list(items_db.values())
    return all_items[skip : skip + limit]


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="查询单个商品",
)
def get_item(
    item_id: Annotated[int, Path(ge=1, description="商品 ID")],
) -> dict:
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return items_db[item_id]


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="更新商品",
)
def update_item(
    item_id: Annotated[int, Path(ge=1, description="商品 ID")],
    item: ItemUpdate,
) -> dict:
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    stored = items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    stored.update(update_data)
    items_db[item_id] = stored
    return stored


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除商品",
)
def delete_item(
    item_id: Annotated[int, Path(ge=1, description="商品 ID")],
) -> None:
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    del items_db[item_id]


app = FastAPI(
    title="商品管理 API",
    version="1.0.0",
    description="基于 FastAPI v0.141.1 的基础 CRUD 示例",
)
app.include_router(router)
```

## 代码解析

### 应用创建与路由委托

`app = FastAPI(...)` 创建应用实例（F-006）。`FastAPI` 继承自 `Starlette`，构造时接收 `title`、`version`、`description` 等元数据参数（F-007），这些信息最终出现在自动生成的 OpenAPI 文档中。FastAPI 内部将路由管理委托给 `self.router = APIRouter(...)`（F-009），因此 `@app.get`/`@app.post` 等装饰器本质上是 `add_api_route` 的快捷方式（F-015）。

### APIRouter 模块化组织

`APIRouter(prefix="/items", tags=["items"])` 创建独立路由器（F-034）。通过 `prefix` 为所有路由统一添加路径前缀，`tags` 用于 OpenAPI 文档分组。`app.include_router(router)` 将子路由挂载到主应用。这种组合模式支持大型项目按业务模块拆分路由文件。

### 路径参数与查询参数

`Path(ge=1)` 声明路径参数（F-041），`Path` 继承自 `Param(FieldInfo)`（F-039），断言参数必须有值——路径参数不能有默认值。`Query(ge=0)` 声明查询参数（F-042），支持默认值和校验约束。`Annotated[int, Query(...)]` 是 v0.141 推荐的写法，将类型注解与参数元数据绑定（F-051）。

### 请求体与响应模型

`ItemCreate`/`ItemUpdate`/`ItemResponse` 均继承 Pydantic `BaseModel`。FastAPI 的 `analyze_param` 会自动将非标量类型注解推断为 Body 参数（F-061），无需显式写 `Body()`。`response_model=ItemResponse`（F-030）在 `_populate_api_route_state` 中设置路由状态，响应经 `serialize_response` 序列化时按 `ItemResponse` 字段过滤——即使内部存储包含多余字段，输出也只包含模型声明的字段（F-020）。

### HTTPException 错误处理

`HTTPException(status_code, detail, headers)` 继承自 Starlette 的同名异常（F-101）。构造函数接收三个参数，FastAPI 在 `__init__` 中注册了默认的 `http_exception_handler`（F-010），自动将异常转换为 JSON 响应 `{"detail": "..."}`。

### 状态码

`status.HTTP_201_CREATED` 和 `status.HTTP_204_NO_CONTENT` 从 `starlette.status` 重新导出（F-002）。204 状态码不允许响应体，FastAPI 在非流式分支中检测后设置 `response.body = b""`（F-027、F-115）。

## 运行方式

```bash
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
```

启动后访问：

- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc
- OpenAPI JSON：http://127.0.0.1:8000/openapi.json

## 源码溯源

| API/概念 | 源码位置 | 事实编号 |
|---------|---------|---------|
| `FastAPI` 类定义 | `applications.py:39-42` | F-006 |
| `FastAPI.__init__` 参数 | `applications.py:58-872` | F-007 |
| `self.router = APIRouter(...)` | `applications.py:937-999` | F-009 |
| 默认异常处理器注册 | `applications.py:1003-1012` | F-010 |
| `add_api_route` 委托 | `applications.py:1165-1220` | F-015 |
| `APIRouter` 类 | `routing.py:2282-2519` | F-034 |
| `_populate_api_route_state` | `routing.py:961-1037` | F-030 |
| `serialize_response` | `routing.py:301-342` | F-020 |
| 非流式响应处理 | `routing.py:705-750` | F-027 |
| `Param(FieldInfo)` 基类 | `params.py:26-134` | F-039 |
| `Path` 类 | `params.py:137-218` | F-041 |
| `Query` 类 | `params.py:221-300` | F-042 |
| `Annotated[..., Doc(...)]` | `param_functions.py:13-2280` | F-051 |
| `analyze_param` 自动推断 | `dependencies/utils.py:381-547` | F-061 |
| `HTTPException` | `exceptions.py:17-83` | F-101 |
| `status` 重新导出 | `__init__.py:5` | F-002 |
| `is_body_allowed_for_status_code` | `utils.py:26-40` | F-115 |

## 相关概念

- [FastAPI 应用类](../concepts/01-application.md)
- [路由系统与请求处理管线](../concepts/02-routing-system.md)
- [路径操作与端点执行](../concepts/03-path-operations.md)
- [参数声明与类型系统](../concepts/05-parameter-declaration.md)
- [请求体与表单/文件处理](../concepts/06-request-body.md)
- [响应模型与序列化](../concepts/07-response-model.md)
