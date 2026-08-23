---
type: Reference
title: security — FastAPI 源码信源
description: 安全认证模块，涵盖 SecurityBase 基类、HTTP Basic/Bearer/Digest 认证、OAuth2 密码模式及 Authorization 头解析工具
tags: [fastapi, source, security]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/security.md
    title: FastAPI v0.141.1 源码
---

# security 源码信源

## 基本信息
- **源码路径**: `fastapi/security/base.py`、`fastapi/security/http.py`、`fastapi/security/oauth2.py`、`fastapi/security/utils.py`
- **版本**: 0.141.1
- **事实范围**: F-080 ~ F-091, F-144, F-145, F-157, F-158

## 公开 API 清单

### 类
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `SecurityBase` | — | 类属性 `model: SecurityBaseModel`、`scheme_name: str`；无 `__init__` | F-080, F-144, F-145 |
| `HTTPBasicCredentials` | `BaseModel` | `username: str`、`password: str` | F-081 |
| `HTTPAuthorizationCredentials` | `BaseModel` | `scheme: str`、`credentials: str` | F-082 |
| `HTTPBase` | `SecurityBase` | `__init__(scheme, scheme_name, description, auto_error=True)`、`__call__(request)`、make_authenticate_headers、make_not_authenticated_error | F-083 |
| `HTTPBasic` | `HTTPBase` | model.scheme 固定 "basic"；`__init__` 支持 realm；`__call__` 解析 base64 | F-084 |
| `HTTPBearer` | `HTTPBase` | `__init__(bearerFormat, scheme_name, description, auto_error)`；`__call__` 校验 bearer | F-085 |
| `HTTPDigest` | `HTTPBase` | model.scheme 固定 "digest"；`__call__` 校验 digest | F-086 |
| `OAuth2` | `SecurityBase` | `__init__(flows=OAuthFlowsModel(), scheme_name, description, auto_error=True)`；`__call__` 返回 Authorization 头原值 | F-089 |
| `OAuth2PasswordBearer` | `OAuth2` | `__init__(tokenUrl, scheme_name, scopes, description, auto_error, refreshUrl)`；`__call__` 校验 bearer 返回 token | F-090 |
| `OAuth2PasswordRequestForm` | — | grant_type/username/password/scope/client_id/client_secret 六个 Form 字段 | F-087 |
| `OAuth2PasswordRequestFormStrict` | `OAuth2PasswordRequestForm` | grant_type 改为无默认值必填 | F-088 |

### 函数
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `get_authorization_scheme_param` | `get_authorization_scheme_param(authorization_header_value: str \| None) -> tuple[str, str]` | F-091, F-157, F-158 |

## 关键实现细节

### SecurityBase 基类（F-080, F-144, F-145）
- 首行从 `fastapi.openapi.models` 导入 `SecurityBase as SecurityBaseModel`
- `class SecurityBase` 无 `__init__` 方法
- 类体仅声明两个类属性注解：`model: SecurityBaseModel` 和 `scheme_name: str`

### HTTPBasicCredentials（F-081）
`class HTTPBasicCredentials(BaseModel)` 字段：`username: str`、`password: str`。

### HTTPAuthorizationCredentials（F-082）
`class HTTPAuthorizationCredentials(BaseModel)` 字段：`scheme: str`、`credentials: str`。

### HTTPBase（F-083）
`class HTTPBase(SecurityBase)`：
- `__init__` 接受 scheme/scheme_name/description/auto_error=True
- `make_authenticate_headers` 返回 `{"WWW-Authenticate": scheme.title()}`
- `make_not_authenticated_error` 返回 401 HTTPException
- `__call__(request)` 通过 `get_authorization_scheme_param` 提取凭证，返回 `HTTPAuthorizationCredentials`

### HTTPBasic（F-084）
`class HTTPBasic(HTTPBase)`：
- model.scheme 固定 "basic"
- `__init__` 支持 realm
- `__call__` 校验 `scheme.lower()=="basic"`
- 使用 `b64decode` 解析后按 `:` 分割 username/password

### HTTPBearer（F-085）
`class HTTPBearer(HTTPBase)`：
- `__init__` 接受 bearerFormat/scheme_name/description/auto_error
- `__call__` 校验 `scheme.lower()=="bearer"`

### HTTPDigest（F-086）
`class HTTPDigest(HTTPBase)`：
- model.scheme 固定 "digest"
- `__call__` 校验 `scheme.lower()=="digest"`

### OAuth2PasswordRequestForm（F-087）
用 `Annotated` 声明六个 Form 字段：
- `grant_type: str | None = Form(pattern="^password$")`
- `username: str = Form()`
- `password: str = Form(json_schema_extra={"format":"password"})`
- `scope: str = Form()`
- `client_id: str | None = Form()`
- `client_secret: str | None = Form()`

### OAuth2PasswordRequestFormStrict（F-088）
继承 `OAuth2PasswordRequestForm`，将 `grant_type` 改为无默认值的必填 `Form(pattern="^password$")`。

### OAuth2（F-089）
`class OAuth2(SecurityBase)`：
- `__init__` 接受 flows（默认 `OAuthFlowsModel()`）/scheme_name/description/auto_error=True
- `make_not_authenticated_error` 返回 401 带 `WWW-Authenticate: Bearer`
- `__call__(request)` 返回 Authorization 头原值

### OAuth2PasswordBearer（F-090）
`class OAuth2PasswordBearer(OAuth2)`：
- `__init__` 接受 tokenUrl/scheme_name/scopes=None/description/auto_error=True/refreshUrl=None
- 构造 password flow dict 传入 `super().__init__`
- `__call__` 校验 `scheme.lower()=="bearer"` 并返回 param（token）

### get_authorization_scheme_param（F-091, F-157, F-158）
`get_authorization_scheme_param(authorization_header_value: str | None) -> tuple[str, str]`：
- 模块无任何 import 语句，仅定义此一个函数
- 空值返回 `("", "")`
- 否则使用 `str.partition(" ")` 按首个空格分割
- 返回 `(scheme, param.strip())`
- 空输入直接返回 `("", "")` 而非抛异常

## 相关信源
- [dependencies.md](dependencies.md) — SecurityScopes 注入、Security depends 处理
- [params.md](params.md) — Security/Depends 数据类定义
- [openapi.md](openapi.md) — SecurityBase 等 OpenAPI 安全模型
