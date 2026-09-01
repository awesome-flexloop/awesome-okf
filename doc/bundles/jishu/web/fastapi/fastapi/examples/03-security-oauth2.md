---
type: Example
title: OAuth2 密码流认证
description: 完整演示 OAuth2 Password Bearer 认证流程，包括登录获取 token、Security scopes 权限控制、HTTPBearer 认证方案以及 get_authorization_scheme_param 凭证解析。
tags: [fastapi, example, security, oauth2, authentication]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: security-source
    resource: /references/security.md
    title: security 模块源码信源
  - id: params-source
    resource: /references/params.md
    title: params 模块源码信源
  - id: dependencies-source
    resource: /references/dependencies.md
    title: dependencies 模块源码信源
---

# OAuth2 密码流认证

本示例演示 FastAPI v0.141.1 的安全认证体系。FastAPI 在 `fastapi.security` 模块中提供了 OAuth2、HTTP Bearer/Basic/Digest 等认证方案，它们均继承自 `SecurityBase`（F-080），通过 `__call__` 方法作为依赖注入端点。本示例完整展示登录→签发 token→携带 token 访问受保护端点→基于 scope 的权限校验流程。

## 场景说明

构建一个用户认证系统：

1. 用户通过 `POST /token` 提交用户名密码（表单格式），验证通过后获得 access token
2. `GET /users/me` 需要登录，返回当前用户信息
3. `GET /admin/dashboard` 需要 `admin` scope，普通用户无法访问
4. 同时演示 `HTTPBearer` 方案和 `get_authorization_scheme_param` 底层解析

## 完整代码

```python
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.routing import APIRouter
from pydantic import BaseModel


SECRET_KEY = "example-secret-key-not-for-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": "fakehash-alice-secret",
        "scopes": ["user:read"],
    },
    "admin": {
        "username": "admin",
        "hashed_password": "fakehash-admin-secret",
        "scopes": ["user:read", "admin"],
    },
}


def fake_hash_password(password: str) -> str:
    return f"fakehash-{password}"


def fake_create_token(subject: str, scopes: list[str], expires_delta: timedelta) -> str:
    payload = f"{subject}:{','.join(scopes)}:{expires_delta.total_seconds()}"
    return payload


def fake_decode_token(token: str) -> dict:
    try:
        subject, scopes_str, _ = token.split(":")
        return {"sub": subject, "scopes": scopes_str.split(",") if scopes_str else []}
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class User(BaseModel):
    username: str
    scopes: list[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user:read": "Read user information",
        "admin": "Admin access",
    },
)

bearer_scheme = HTTPBearer()


def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    payload = fake_decode_token(token)
    username = payload.get("sub")
    if username is None or username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_dict = fake_users_db[username]
    user = User(username=user_dict["username"], scopes=user_dict["scopes"])
    for scope in security_scopes.scopes:
        if scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Requires scope: {scope}",
            )
    return user


router = APIRouter(tags=["authentication"])


@router.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user_dict = fake_users_db.get(form_data.username)
    if user_dict is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    if fake_hash_password(form_data.password) != user_dict["hashed_password"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token = fake_create_token(
        subject=user_dict["username"],
        scopes=form_data.scopes.split() if form_data.scopes else user_dict["scopes"],
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@router.get("/users/me", response_model=User)
def read_users_me(
    current_user: Annotated[
        User,
        Security(get_current_user, scopes=["user:read"]),
    ],
) -> User:
    return current_user


@router.get("/admin/dashboard")
def admin_dashboard(
    current_user: Annotated[
        User,
        Security(get_current_user, scopes=["admin"]),
    ],
) -> dict:
    return {
        "message": f"Welcome admin {current_user.username}",
        "admin_data": "sensitive",
    }


@router.get("/auth/inspect")
def inspect_auth_header(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    scheme, param = get_authorization_scheme_param(
        f"{credentials.scheme} {credentials.credentials}"
    )
    return {
        "scheme": scheme,
        "token_preview": param[:10] + "..." if len(param) > 10 else param,
    }


app = FastAPI(
    title="OAuth2 认证示例",
    version="1.0.0",
    description="OAuth2 Password Bearer 流程演示",
)
app.include_router(router)
```

## 代码解析

### OAuth2PasswordBearer 方案

`OAuth2PasswordBearer(tokenUrl="token", scopes={...})` 创建认证方案实例（F-090）。它继承自 `OAuth2`（F-089），构造时将 `tokenUrl` 和 `scopes` 组装为 password flow dict 传入父类。作为依赖调用时，`__call__` 方法从请求的 `Authorization` 头提取 Bearer token，校验 `scheme.lower() == "bearer"` 后返回 token 字符串。`tokenUrl` 仅用于 OpenAPI 文档中的"Try it out"按钮，不影响运行时路由。

### OAuth2PasswordRequestForm 表单

`OAuth2PasswordRequestForm` 使用 `Annotated` 声明六个 Form 字段（F-087）：`grant_type`（pattern 校验为 `"password"`）、`username`、`password`（format 为 password）、`scope`、`client_id`、`client_secret`。FastAPI 的依赖分析器识别 `Form` 类型参数，自动以 `application/x-www-form-urlencoded` 格式解析请求体（F-061、F-046）。`form_data.scopes` 是空格分隔的 scope 字符串。

### Security() 与 scopes 权限控制

`Security(dependency, scopes=["admin"])` 返回 `params.Security` 数据类（F-053、F-049）。`Security` 继承自 `Depends`，新增 `scopes: Sequence[str] | None` 字段。与 `Depends` 不同，`Security` 携带的 scope 信息会被 FastAPI 收集到 `Dependant.own_oauth_scopes` 和 `parent_oauth_scopes` 中（F-054），用于 OpenAPI 文档生成安全需求定义。

运行时，依赖函数通过声明 `security_scopes: SecurityScopes` 参数自动接收所需 scope 集合（由 `add_non_field_param_to_dependency` 识别并注入，F-059）。`SecurityScopes` 对象提供 `scopes`（list[str]）和 `scope_str`（空格分隔字符串）两个属性。本示例在 `get_current_user` 中遍历 `security_scopes.scopes`，逐一检查用户是否拥有所需权限，不满足时抛出 403 异常。同一端点的多个 Security 依赖声明的 scopes 会被聚合到同一个 SecurityScopes 对象中。

### HTTPBearer 方案

`HTTPBearer()` 继承自 `HTTPBase`（F-085），`__call__` 方法通过 `get_authorization_scheme_param` 提取凭证，校验 scheme 为 `"bearer"` 后返回 `HTTPAuthorizationCredentials(scheme=..., credentials=...)` 对象（F-082）。与 `OAuth2PasswordBearer` 返回原始 token 字符串不同，`HTTPBearer` 返回结构化凭证对象，适用于需要同时访问 scheme 和 token 的场景。

### get_authorization_scheme_param 底层解析

`get_authorization_scheme_param(authorization_header_value)` 是安全模块的底层工具函数（F-091）。它使用 `str.partition(" ")` 按第一个空格分割 Authorization 头值，返回 `(scheme, param.strip())` 元组。空输入返回 `("", "")` 而非抛异常（F-158），这种防御式设计使上层认证方案可以统一处理缺失/畸形头的情况。

### 认证流程时序

1. 客户端 POST `/token`，表单提交 username/password
2. 服务端验证凭证，签发包含 subject 和 scopes 的 token
3. 客户端后续请求在 `Authorization: Bearer <token>` 头中携带 token
4. `oauth2_scheme` 作为依赖提取并返回 token
5. `get_current_user` 解码 token 并加载用户
6. `Security(..., scopes=["admin"])` 声明所需权限，依赖函数校验用户 scope

## 运行方式

```bash
pip install fastapi uvicorn pydantic python-multipart
uvicorn main:app --reload
```

获取 token：

```bash
curl -X POST http://127.0.0.1:8000/token \
  -d "username=alice&password=alice-secret"
```

访问受保护端点：

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <token>"
```

管理员登录后访问 admin 端点：

```bash
curl -X POST http://127.0.0.1:8000/token \
  -d "username=admin&password=admin-secret&scope=admin"
```

## 源码溯源

| API/概念 | 源码位置 | 事实编号 |
|---------|---------|---------|
| `SecurityBase` 基类 | `security/base.py:1-6` | F-080 |
| `HTTPAuthorizationCredentials` | `security/http.py:29-66` | F-082 |
| `HTTPBase` | `security/http.py:69-102` | F-083 |
| `HTTPBearer` | `security/http.py:222-316` | F-085 |
| `OAuth2PasswordRequestForm` | `security/oauth2.py:59-327` | F-087 |
| `OAuth2` 基类 | `security/oauth2.py:330-430` | F-089 |
| `OAuth2PasswordBearer` | `security/oauth2.py:433-544` | F-090 |
| `get_authorization_scheme_param` | `security/utils.py:1-7` | F-091 |
| `Security` 数据类 | `params.py:752-754` | F-049 |
| `Security()` 工厂函数 | `param_functions.py:2372-2460` | F-053 |
| `Depends` 数据类 | `params.py:745-749` | F-048 |
| SecurityScopes 注入 | `dependencies/utils.py:350-371` | F-059 |
| Dependant scopes 字段 | `dependencies/models.py:31-51` | F-054 |

## 相关概念

- [安全与认证](../concepts/09-security.md)
- [依赖注入系统](../concepts/04-dependency-injection.md)
- [参数声明与类型系统](../concepts/05-parameter-declaration.md)
- [异常处理与校验错误](../concepts/11-exception-handling.md)
