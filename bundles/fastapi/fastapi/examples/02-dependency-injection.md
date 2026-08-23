---
type: Example
title: 依赖注入实战
description: 演示 FastAPI 依赖注入系统的完整用法，包括函数依赖、类依赖、yield 生命周期依赖、子依赖嵌套、缓存去重、全局与路由级依赖以及测试中的 dependency_overrides 替换。
tags: [fastapi, example, dependency-injection, depends, testing]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: routing-source
    resource: /references/routing.md
    title: routing 模块源码信源
  - id: dependencies-source
    resource: /references/dependencies.md
    title: dependencies 模块源码信源
  - id: params-source
    resource: /references/params.md
    title: params 模块源码信源
---

# 依赖注入实战

本示例深入演示 FastAPI v0.141.1 的依赖注入系统。FastAPI 的依赖注入基于 `Depends` 数据类构建，在请求处理时递归求解依赖树（F-054、F-058），支持函数依赖、类依赖、`yield` 生命周期依赖，并通过 `use_cache` 在同一请求内去重。示例还展示了 `dependency_overrides` 在测试中无缝替换依赖的机制。

## 场景说明

构建一个文章管理 API，需要以下横切关注点：

1. **数据库会话**：每个请求获取一个数据库会话，请求结束后自动关闭（yield 依赖）
2. **认证鉴权**：从请求头解析 token，验证用户身份（子依赖嵌套）
3. **分页参数**：统一的分页查询参数（类依赖）
4. **请求日志**：全局依赖记录每个请求的路径和方法
5. **测试替换**：测试时将数据库替换为内存版本

## 完整代码

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.routing import APIRouter
from pydantic import BaseModel


class Database:
    def __init__(self) -> None:
        self.articles: dict[int, dict] = {}
        self._next_id = 1

    def insert(self, data: dict) -> dict:
        article_id = self._next_id
        self._next_id += 1
        record = {"id": article_id, **data}
        self.articles[article_id] = record
        return record

    def list(self, skip: int, limit: int) -> list[dict]:
        return list(self.articles.values())[skip : skip + limit]

    def get(self, article_id: int) -> dict | None:
        return self.articles.get(article_id)


db = Database()


def get_db():
    yield db


class Pagination:
    def __init__(
        self,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        self.skip = skip
        self.limit = limit


class User(BaseModel):
    username: str
    role: str


def get_token(authorization: Annotated[str | None, Header(alias="Authorization")] = None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return authorization.removeprefix("Bearer ").strip()


def get_current_user(token: Annotated[str, Depends(get_token)]) -> User:
    fake_users = {
        "admin-token": User(username="admin", role="admin"),
        "reader-token": User(username="reader", role="reader"),
    }
    user = fake_users.get(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


class ArticleCreate(BaseModel):
    title: str
    content: str


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str


router = APIRouter(prefix="/articles", tags=["articles"])


@router.post(
    "/",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_article(
    article: ArticleCreate,
    database: Annotated[Database, Depends(get_db)],
) -> dict:
    return database.insert(article.model_dump())


@router.get("/", response_model=list[ArticleResponse])
def list_articles(
    pagination: Annotated[Pagination, Depends(Pagination)],
    database: Annotated[Database, Depends(get_db)],
) -> list[dict]:
    return database.list(skip=pagination.skip, limit=pagination.limit)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    database: Annotated[Database, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    record = database.get(article_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    return record


app = FastAPI(
    title="文章管理 API",
    version="1.0.0",
    dependencies=[Depends(get_token)],
)
app.include_router(router)
```

### 测试代码

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_article_admin():
    response = client.post(
        "/articles/",
        json={"title": "Hello", "content": "World"},
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hello"
    assert data["id"] == 1


def test_create_article_forbidden():
    response = client.post(
        "/articles/",
        json={"title": "Hello", "content": "World"},
        headers={"Authorization": "Bearer reader-token"},
    )
    assert response.status_code == 403


def test_list_articles():
    response = client.get(
        "/articles/?skip=0&limit=10",
        headers={"Authorization": "Bearer reader-token"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


app.dependency_overrides[get_db] = lambda: Database()


def test_with_overridden_db():
    response = client.get(
        "/articles/",
        headers={"Authorization": "Bearer reader-token"},
    )
    assert response.status_code == 200
    assert response.json() == []
```

## 代码解析

### Depends 数据类与工厂函数

`Depends(dependency=None, *, use_cache=True, scope=None)` 返回 `params.Depends` 数据类实例（F-052、F-048）。`dependency` 参数可以是函数、类或任何可调用对象。当 `dependency=None` 时，FastAPI 根据类型注解自动推断依赖目标。`use_cache=True`（默认）确保同一依赖在同一请求中只执行一次，结果缓存于 `dependency_cache`（F-064）。

### 函数依赖

`get_db()` 是一个生成器函数依赖。`get_token()` 和 `get_current_user()` 是普通函数依赖。FastAPI 通过 `_is_coroutine_callable`、`_is_gen_callable`、`_is_async_gen_callable` 检测可调用对象类型（F-055），这些检测经 `lru_cache(maxsize=4096)` 缓存以提升性能。

### yield 依赖与 AsyncExitStack 生命周期

`get_db()` 使用 `yield` 返回数据库会话。`solve_dependencies` 在求解时将生成器依赖按 `scope` 注册到 AsyncExitStack（F-064）。FastAPI 在 `request_response` 中建立两层栈：`fastapi_inner_astack`（request 级）和 `fastapi_function_astack`（function 级）（F-018）。`_get_computed_scope` 对生成器 callable 自动返回 `"request"`（F-056），意味着 yield 依赖在响应完全发送后才执行清理代码（`yield` 之后的部分），确保数据库连接等资源正确释放。

### 类依赖

`Pagination` 类作为依赖使用时，FastAPI 调用其 `__init__` 方法，将查询参数注入构造参数，然后返回类实例。类依赖本质上是可调用对象依赖，FastAPI 分析类的 `__init__` 签名来构建依赖树（F-058）。

### 子依赖嵌套

`get_current_user` 依赖 `get_token`，`require_admin` 依赖 `get_current_user`。`get_dependant` 对 `Depends` 类型参数递归调用自身构建子 `Dependant`（F-058），形成依赖树。`solve_dependencies` 以后序遍历递归求解——先求解最深层子依赖，再逐层向上（F-064）。当多个端点依赖 `get_current_user` 而后者又依赖 `get_token` 时，`use_cache=True` 确保 `get_token` 只执行一次。

### 全局依赖与路由级依赖

`FastAPI(dependencies=[Depends(get_token)])` 设置应用级全局依赖（F-007），应用到所有路由。`@router.post(..., dependencies=[Depends(require_admin)])` 设置路由级依赖（F-036），仅应用于该路由。`APIRouter.add_api_route` 合并 router 级和路由级 dependencies 列表（F-036）。`dependencies` 参数中的依赖会被执行但返回值不注入端点函数——适合鉴权等只需副作用的场景。

### dependency_overrides 测试替换

`app.dependency_overrides = {}` 在 `__init__` 中初始化为空字典（F-009）。测试中设置 `app.dependency_overrides[get_db] = lambda: Database()` 后，`solve_dependencies` 在求解依赖时检查该字典，若原依赖存在覆盖则使用替换值（F-064）。替换发生在求解时的任意节点，无需重建路由树，测试结束后清空字典即可恢复。

## 运行方式

```bash
pip install fastapi uvicorn pydantic httpx
uvicorn main:app --reload
```

测试请求：

```bash
curl -H "Authorization: Bearer admin-token" http://127.0.0.1:8000/articles/
curl -X POST http://127.0.0.1:8000/articles/ \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","content":"内容"}'
```

## 源码溯源

| API/概念 | 源码位置 | 事实编号 |
|---------|---------|---------|
| `Depends` 数据类 | `params.py:745-749` | F-048 |
| `Depends()` 工厂函数 | `param_functions.py:2283-2369` | F-052 |
| `Dependant` 数据类 | `dependencies/models.py:31-51` | F-054 |
| 可调用类型检测缓存 | `dependencies/models.py:58-226` | F-055 |
| scope 自动推断 | `dependencies/models.py:229-234` | F-056 |
| `get_dependant` 递归构建 | `dependencies/utils.py:271-347` | F-058 |
| `solve_dependencies` 求解 | `dependencies/utils.py:586-731` | F-064 |
| 双层 AsyncExitStack | `routing.py:121-160` | F-018 |
| `dependency_overrides` 初始化 | `applications.py:937-999` | F-009 |
| 全局 dependencies 参数 | `applications.py:58-872` | F-007 |
| 路由级 dependencies 合并 | `routing.py:2889-2971` | F-036 |
| `APIRouter` 类 | `routing.py:2282-2519` | F-034 |

## 相关概念

- [依赖注入系统](/concepts/04-dependency-injection.md)
- [参数声明与类型系统](/concepts/05-parameter-declaration.md)
- [路由系统与请求处理管线](/concepts/02-routing-system.md)
- [FastAPI 应用类](/concepts/01-application.md)
