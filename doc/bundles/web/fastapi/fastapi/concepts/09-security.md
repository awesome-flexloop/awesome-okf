---
type: Concept
title: 安全与认证机制
description: 详解 SecurityBase 基类、HTTPBasic/HTTPBearer/HTTPDigest 认证体系、OAuth2 密码模式与 Bearer Token、Security 依赖的 scopes 参数、Authorization 头解析及安全方案如何注入 OpenAPI。
tags: [fastapi, security, authentication, oauth2, http-basic, http-bearer, openapi]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/security.md
    title: FastAPI v0.141.1 源码信源
---

# 安全与认证机制

FastAPI 提供了一套声明式的安全与认证工具，所有安全方案均继承自 `SecurityBase` 基类，既是依赖注入提供者又是 OpenAPI 安全方案描述符。框架内置 HTTP Basic、HTTP Bearer、HTTP Digest 和 OAuth2 四种认证方案，通过 `Security()` 依赖声明（支持 `scopes` 权限范围），自动在 OpenAPI 文档中生成对应的 securitySchemes。安全方案的核心设计是"依赖即文档"——同一个安全类实例同时完成运行时凭证提取和 OpenAPI schema 生成。

## SecurityBase 基类

`SecurityBase` 是所有安全方案的基类（F-080），定义在 `fastapi/security/base.py`：

```python
from fastapi.openapi.models import SecurityBase as SecurityBaseModel

class SecurityBase:
    model: SecurityBaseModel
    scheme_name: str
```

该类无 `__init__` 方法（F-145），类体仅声明两个类属性注解：
- `model`：OpenAPI 安全方案模型实例（来自 `openapi/models.py` 中的 40 个模型类之一）
- `scheme_name`：安全方案名称字符串，用于 OpenAPI components.securitySchemes 的键

子类通过设置这两个属性将自身注册为 OpenAPI 安全方案。`SecurityBase` 本身不实现 `__call__`，认证逻辑由各子类自行实现，使其同时满足 FastAPI 依赖注入协议（可调用对象）和 OpenAPI 描述协议。

## HTTPBase 与凭证模型

`HTTPBase` 继承 `SecurityBase`，是 HTTP 认证方案的通用基类（F-083）：

```python
class HTTPBase(SecurityBase):
    def __init__(
        self,
        *,
        scheme: str,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
```

核心方法：
- **`make_authenticate_headers()`**：返回 `{"WWW-Authenticate": scheme.title()}`，用于 401 响应的 `WWW-Authenticate` 头
- **`make_not_authenticated_error()`**：返回 401 `HTTPException`，携带 `WWW-Authenticate` 头
- **`__call__(request)`**：通过 `get_authorization_scheme_param` 从 `Authorization` 头提取 scheme 和 param，返回 `HTTPAuthorizationCredentials`；当 `auto_error=True` 且凭证缺失或 scheme 不匹配时自动抛出 401 异常

两种凭证模型：

**`HTTPBasicCredentials`**（F-081）：Pydantic BaseModel，含 `username: str` 和 `password: str` 两个字段。

**`HTTPAuthorizationCredentials`**（F-082）：Pydantic BaseModel，含 `scheme: str` 和 `credentials: str` 两个字段，是 `HTTPBase.__call__` 的返回类型，也是 HTTP Bearer/Digest 的凭证载体。

## HTTPBasic

`HTTPBasic` 继承 `HTTPBase`，实现 HTTP Basic Access Authentication（F-084）：

- `model.scheme` 固定为 `"basic"`
- `__init__` 额外支持 `realm` 参数，用于 `WWW-Authenticate: Basic realm="..."` 头
- `__call__` 校验 `scheme.lower() == "basic"`，然后使用 `b64decode` 解码 credentials，按第一个 `:` 分割为 username 和 password，返回 `HTTPBasicCredentials`

```python
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

@app.get("/users/me")
async def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username}
```

## HTTPBearer

`HTTPBearer` 继承 `HTTPBase`，实现 Bearer Token 认证（F-085）：

```python
class HTTPBearer(HTTPBase):
    def __init__(
        self,
        *,
        bearerFormat: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
```

- `__call__` 校验 `scheme.lower() == "bearer"`，返回 `HTTPAuthorizationCredentials(scheme="bearer", credentials="<token>")`
- `bearerFormat` 参数提示 token 格式（如 JWT、OAuth 等），写入 OpenAPI schema

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer(bearerFormat="JWT")

@app.get("/protected")
async def protected(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    token = credentials.credentials
    return {"token": token}
```

## HTTPDigest

`HTTPDigest` 继承 `HTTPBase`，实现 HTTP Digest Access Authentication（F-086）：

- `model.scheme` 固定为 `"digest"`
- `__call__` 校验 `scheme.lower() == "digest"`，返回 `HTTPAuthorizationCredentials`
- Digest 认证的加密验证（nonce、response 哈希等）需开发者自行实现，FastAPI 仅提供凭证提取和 OpenAPI 描述

## OAuth2 体系

### OAuth2 基类

`OAuth2` 继承 `SecurityBase`，是 OAuth2 认证方案的基类（F-089）：

```python
class OAuth2(SecurityBase):
    def __init__(
        self,
        *,
        flows: OAuthFlowsModel | dict[str, Any] = OAuthFlowsModel(),
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
```

- `flows` 描述 OAuth2 流程配置（authorizationCode、clientCredentials、password、implicit）
- `make_not_authenticated_error()` 返回 401 异常，携带 `WWW-Authenticate: Bearer` 头
- `__call__(request)` 返回 `Authorization` 头的原始值（完整字符串），不解析 scheme 或 token

### OAuth2PasswordBearer

`OAuth2PasswordBearer` 继承 `OAuth2`，实现 OAuth2 密码模式（Resource Owner Password Credentials Grant）的 Bearer Token 提取（F-090）：

```python
class OAuth2PasswordBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
        refreshUrl: str | None = None,
    ):
```

- `tokenUrl`：客户端获取 token 的端点 URL（相对路径），写入 OpenAPI schema
- `scopes`：权限范围字典，键为 scope 名称，值为描述
- `refreshUrl`：刷新 token 的端点 URL
- 构造时创建 password flow dict `{"tokenUrl": tokenUrl, "scopes": scopes}` 传入 `super().__init__`
- `__call__` 校验 `scheme.lower() == "bearer"` 并返回 param（token 字符串）

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read current user", "items": "Read items"},
)

@app.get("/users/me")
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
```

### OAuth2PasswordRequestForm

`OAuth2PasswordRequestForm` 是密码模式的登录表单模型（F-087），用 `Annotated` 声明六个 Form 字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `grant_type` | `str \| None` | 授权类型，pattern=`^password$`，可选 |
| `username` | `str` | 用户名（必填） |
| `password` | `str` | 密码（必填，format="password"） |
| `scope` | `str` | 权限范围字符串（空格分隔） |
| `client_id` | `str \| None` | 客户端 ID |
| `client_secret` | `str \| None` | 客户端密钥 |

`OAuth2PasswordRequestFormStrict`（F-088）继承前者，将 `grant_type` 改为无默认值的必填字段。

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return {"access_token": form_data.username, "token_type": "bearer"}
```

## Security 依赖与 scopes

`Security` 是一个冻结数据类，继承 `Depends`（F-049），新增 `scopes: Sequence[str] | None = None` 字段：

```python
@dataclass(frozen=True)
class Security(Depends):
    scopes: Sequence[str] | None = None
```

`Security()` 工厂函数（F-053）创建 `params.Security` 实例。与 `Depends()` 的区别在于 `scopes` 参数声明该端点所需的权限范围。框架将 scopes 存入 `Dependant.own_oauth_scopes`（F-054），在 OpenAPI 生成时写入 operation 的 security 字段，并在运行时通过 `SecurityScopes` 参数注入供端点校验。

```python
from fastapi import Security
from fastapi.security import SecurityScopes

@app.get("/items/")
async def read_items(
    security_scopes: SecurityScopes,
    token: Annotated[str, Security(oauth2_scheme, scopes=["items", "read"])],
):
    if "items" not in security_scopes.scopes:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return {"token": token}
```

`Dependant` 数据类中与安全相关的字段（F-054）：
- `security_scopes_param_name`：`SecurityScopes` 参数的名称（如果端点声明了该参数）
- `own_oauth_scopes`：当前依赖自身声明的 scopes
- `parent_oauth_scopes`：从父依赖继承的 scopes

## get_authorization_scheme_param

`get_authorization_scheme_param` 是 Authorization 头解析的工具函数（F-091, F-157, F-158）：

```python
def get_authorization_scheme_param(
    authorization_header_value: str | None,
) -> tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param.strip()
```

使用 `str.partition(" ")` 按**第一个**空格分割，确保 token 中包含空格时不会被错误拆分。空输入返回 `("", "")` 而非抛异常。scheme 保留原始大小写，由调用方执行 `.lower()` 比较。

## 安全方案注入 OpenAPI

安全方案通过 Dependant 树传播到 OpenAPI 生成：

1. `get_dependant` 分析端点签名时，遇到 `Security` 依赖将 scopes 存入 `Dependant.own_oauth_scopes`
2. 子依赖的 scopes 通过 `parent_oauth_scopes` 向上累积
3. `get_openapi_path` 调用 `_get_openapi_security_definitions` 从 Dependant 树中提取所有安全方案
4. 安全方案的 `model` 属性（`SecurityBaseModel` 子类）序列化为 OpenAPI components.securitySchemes
5. 每个 operation 的 security 字段引用所需 scheme 名称和 scopes

`SecurityBase.model` 类型为 `SecurityBaseModel`（从 `fastapi.openapi.models` 导入，F-080），后者是 OpenAPI 模型层中定义的安全方案基类，包含 `HTTPBase`、`HTTPBearer`、`OAuth2`、`APIKey`、`OpenIdConnect` 等子类（F-076）。

## 相关概念

- [依赖注入系统](/concepts/04-dependency-injection.md)
- [OpenAPI 文档生成](/concepts/08-openapi-generation.md)
- [参数声明系统](/concepts/05-parameter-declaration.md)
- [异常处理与校验错误](/concepts/11-exception-handling.md)
- [FastAPI 应用类与生命周期](/concepts/01-application.md)
