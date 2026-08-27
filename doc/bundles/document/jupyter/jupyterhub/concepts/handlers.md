---
type: Concept
title: JupyterHub HTTP Handlers 请求处理层
description: JupyterHub 基于 Tornado 的 HTTP 请求处理体系——BaseHandler 基类、页面处理器、API 处理器、认证中间件与静态资源处理器
tags: [jupyterhub, tornado, http, handlers, web, api, authentication]
sources:
  - id: handlers-source
    resource: https://github.com/jupyterhub/jupyterhub/tree/6.0.0b2/jupyterhub/handlers
    title: jupyterhub/handlers/ (v6.0.0b2)
generated: { by: reference_agent/source-code-to-okf-wiki, at: "2026-08-22" }
status: stable
stale_after: "2027-08-22"
---

# JupyterHub HTTP Handlers 请求处理层

> 源码位置：`jupyterhub/handlers/`（页面处理器）与 `jupyterhub/apihandlers/`（API 处理器）

## Handler 体系概述

JupyterHub 的 HTTP 请求处理层基于 **Tornado Web Framework** 的 `RequestHandler` 构建，承担所有 Hub 与用户浏览器、单用户服务器、外部服务之间的 HTTP 通信。整个 Handler 体系分为三大层次：

```
tornado.web.RequestHandler
└── BaseHandler (handlers/base.py)           # 基类：认证、模板、权限、公共属性
    ├── 页面处理器 (handlers/pages.py)        # HTML 页面渲染
    │   ├── RootHandler, HomeHandler, SpawnHandler, ...
    ├── 认证处理器 (handlers/login.py)        # 登录/登出
    │   ├── LoginHandler, LogoutHandler
    ├── 静态资源处理器 (handlers/static.py)   # 静态文件与 Logo
    │   ├── CacheControlStaticFilesHandler, LogoHandler
    ├── 指标处理器 (handlers/metrics.py)      # Prometheus 指标
    └── APIHandler (apihandlers/base.py)     # API 基类：JSON 响应、Token 认证
        ├── 用户 API (apihandlers/users.py)
        ├── 代理 API (apihandlers/proxy.py)
        ├── 服务 API (apihandlers/services.py)
        ├── 分组 API (apihandlers/groups.py)
        ├── 认证/Token API (apihandlers/auth.py)
        ├── Hub 管理 API (apihandlers/hub.py)
        └── 共享 API (apihandlers/shares.py)
```

### 核心设计特征

- **异步处理**：所有 Handler 方法使用 `async/await` 原生协程
- **认证统一入口**：`prepare()` 阶段完成用户身份识别，`get_current_user()` 支持异步
- **双认证模式**：页面处理器默认仅接受 Cookie 认证；API 处理器同时接受 Cookie 和 Token（Authorization header）认证
- **XSRF 防护**：自定义 XSRF Token 机制，Token 与登录状态绑定
- **CSP 安全策略**：默认 `frame-ancestors 'none'`，API 端点附加 `default-src 'none'`
- **范围权限（Scopes）**：基于 RBAC 的细粒度权限检查，装饰器 `@needs_scope(scope)` 控制访问

---

## BaseHandler 基类

**位置**：handlers/base.py

`BaseHandler` 是所有处理器的公共基类，继承自 `tornado.web.RequestHandler`，提供以下核心能力：

### 认证与用户获取

| 方法/属性 | 说明 |
|-----------|------|
| `prepare()` | 请求预处理钩子：在 `get()`/`post()` 之前调用，完成 `get_current_user()`、角色/Scope 解析、XSRF 检查；数据库错误时自动回滚 |
| `get_current_user()` | 获取当前认证用户（异步），支持 Cookie 和 Token 两种模式 |
| `get_current_user_token()` | 从 `Authorization: token <value>` 或 `Bearer <value>` 头解析 API Token，验证后返回对应的 User 或 Service 对象 |
| `_user_for_cookie()` | 从安全 Cookie 中还原用户身份，验证 `cookie_id` 有效性 |
| `get_auth_token()` | 从 Authorization header 提取原始 token 字符串 |
| `get_token()` | 带 LRU 缓存的 token 查询，调用 `orm.APIToken.find()` 查找 ORM 令牌对象 |
| `refresh_auth()` | 刷新用户认证信息，调用 `authenticator.refresh_user()`，按 `auth_refresh_age` 控制刷新频率 |

### 认证模式开关

| 类属性 | 默认值 | 说明 |
|--------|--------|------|
| `_accept_cookie_auth` | `True` | 是否接受 Cookie 认证 |
| `_accept_token_auth` | `False` | 是否接受 Token 认证（APIHandler 设为 True） |

### 公共设置属性（通过 `self.settings` 访问）

| 属性 | 说明 |
|------|------|
| `self.db` | SQLAlchemy 数据库会话 |
| `self.users` | 用户字典 `{name: User}` |
| `self.services` | 服务字典 `{name: Service}` |
| `self.hub` | Hub 实例对象 |
| `self.app` | JupyterHub 应用实例 |
| `self.proxy` | 代理实例 |
| `self.authenticator` | 认证器实例 |
| `self.oauth_provider` | OAuth 提供者实例 |
| `self.config` | 配置对象 |
| `self.base_url` | Hub 基础 URL 路径 |
| `self.log` | 日志器（Tornado app_log） |

### 模板渲染

- `render_template(name, **kwargs)`：渲染 Jinja2 HTML 模板
- `get_content_type()`：默认返回 `'text/html'`（APIHandler 覆盖为 `'application/json'`）

### 安全头部

- `set_default_headers()`：设置 `X-JupyterHub-Version`、CORS 头、Content-Security-Policy
- 默认 CSP：`frame-ancestors 'none'; report-uri <hub>/security/csp-report`

### 请求后处理

- `finish()`：请求结束时检查 `db.dirty`，如有未提交的脏对象则回滚事务，防止异常导致的数据不一致

### 活动记录

- `_record_activity(obj, timestamp=None)`：记录 ORM 对象（User/APIToken）的 `last_activity`，按 `activity_resolution` 设置节流，避免过于频繁的数据库写入

---

## 页面处理器（pages.py）

**位置**：handlers/pages.py

页面处理器负责渲染 HTML 页面，所有页面 Handler 继承 `BaseHandler`，默认使用 Cookie 认证。

### RootHandler — 根路径重定向

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 根路径智能重定向 |

逻辑：
1. 若配置了 `default_url`（支持 callable），按配置重定向
2. 已登录用户：重定向到用户服务器或主页
3. 未登录用户：重定向到登录页，携带 `?next=<current_url>` 参数

### HomeHandler — 用户主页

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/home` | GET | `@web.authenticated` | 用户主控制面板 |

功能：
- 检查用户运行中的服务器状态（`poll_and_notify`）
- 有活跃服务器时重定向到 `/user/:name`
- 无活跃服务器时引导至 `/spawn/:name` 启动页
- 渲染 `home.html` 模板，展示用户服务器列表、命名服务器管理、认证状态

### SpawnHandler — 服务器启动页面

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/spawn(/:name)` | GET/POST | `@web.authenticated` | 启动/配置单用户服务器 |

功能：
- GET：渲染 Spawn 选项表单（`spawn.html`）
- POST：提交选项并触发服务器启动，处理 Spawn 异常

### SpawnPendingHandler — 服务器启动等待页

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/spawn-pending(/:name)` | GET | `@web.authenticated` | 服务器启动进度等待页 |

功能：
- 轮询服务器启动状态
- 启动成功后重定向到用户服务器
- 超时/失败时显示错误信息

### AdminHandler — 管理面板

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/admin` | GET | `@web.authenticated` + admin 权限 | 管理员控制面板 |

功能：用户管理、启动/停止服务器、Token 管理等（需 admin 角色）。

### TokenPageHandler — Token 管理页面

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/token` | GET/POST | `@web.authenticated` | API Token 管理界面 |

功能：展示用户已有的 Token 列表、创建新 Token、撤销 Token。

### AcceptShareHandler — 接受共享

| 路由 | 方法 | 装饰器 | 说明 |
|------|------|--------|------|
| `/accept-share` | GET | — | 接受笔记本共享邀请 |

功能：处理共享码兑换，验证后建立 Share 关系并重定向到共享服务器。

### HealthCheckHandler — 健康检查

| 路由 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | Hub 健康状态端点（无需认证） |

返回简单的健康状态响应，用于负载均衡器/容器编排的存活探测。

### ProxyErrorHandler — 代理错误

| 路由 | 方法 | 说明 |
|------|------|------|
| 代理错误页 | GET | 渲染代理错误页面（超时/连接失败等） |

---

## 认证处理器（login.py）

**位置**：handlers/login.py

### LoginHandler — 登录

| 路由 | 方法 | 说明 |
|------|------|------|
| `/login` | GET/POST | 用户登录页面与表单处理 |

功能：
- GET：渲染登录页面
- POST：处理登录表单提交，调用 Authenticator 验证凭据，设置安全 Cookie
- 支持自定义 Authenticator 的登录逻辑

### LogoutHandler — 登出

| 路由 | 方法 | 说明 |
|------|------|------|
| `/logout` | GET | 清除用户会话 Cookie |

功能：清除登录 Cookie，重定向到登录页。

---

## API 处理器（apihandlers/）

**位置**：apihandlers/

所有 API 处理器继承自 `APIHandler`（`apihandlers/base.py`），该基类在 `BaseHandler` 基础上增加：
- **JSON 响应**：`get_content_type()` 返回 `application/json`
- **Token 认证启用**：`_accept_token_auth = True`
- **严格 CSP**：`default-src 'none'`
- **分页支持**：通过 `application/jupyterhub-pagination+json` Media Type 协商
- **内容类型检查**：`check_post_content_type()` 验证 POST 请求的 Content-Type 为 `application/json`

### 用户 API（users.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `SelfAPIHandler` | `GET /user` | 获取当前认证用户信息 |
| `UserListAPIHandler` | `GET/POST /users` | 用户列表查询、创建用户 |
| `UserAPIHandler` | `GET/PATCH/DELETE /users/:name` | 用户 CRUD 操作 |
| `UserTokenListAPIHandler` | `GET/POST /users/:name/tokens` | 用户 Token 列表、创建 Token |
| `UserTokenAPIHandler` | `GET/DELETE /users/:name/tokens/:token_id` | 获取/撤销指定 Token |
| `UserServerAPIHandler` | `POST/DELETE /users/:name/servers(/:server_name)` | 启动/停止用户服务器 |
| `UserAdminAccessAPIHandler` | `POST /users/:name/admin-access` | 管理员访问用户服务器 |
| `SpawnProgressAPIHandler` | `GET /users/:name/servers(/:server_name)/progress` | 服务器启动进度事件流（SSE） |
| `ActivityAPIHandler` | `POST /users/:name/activity` | 更新用户活动时间 |

### 代理 API（proxy.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `ProxyAPIHandler` | `GET/POST/DELETE /proxy(/:path)` | 代理路由管理 API——创建、查询、删除代理路由表条目 |

这是可配置代理（Configurable HTTP Proxy）与 Hub 通信的核心 API，用于动态注册单用户服务器和服务的路由。

### 认证/Token API（auth.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `TokenAPIHandler` | `POST /authorizations/token`、`GET /authorizations/token/:token` | Token 获取/验证（OAuth 2.0 兼容） |
| `CookieAPIHandler` | `GET /authorizations/cookie/:cookie_name/:cookie_value` | 通过 Cookie 值获取用户信息（服务间认证） |
| `OAuthAuthorizeHandler` | `GET/POST /oauth2/authorize` | OAuth 2.0 授权端点 |
| `OAuthTokenHandler` | `POST /oauth2/token` | OAuth 2.0 令牌端点 |

### 服务 API（services.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `ServiceListAPIHandler` | `GET/POST /services` | 服务列表、创建服务 |
| `ServiceAPIHandler` | `GET/PATCH/DELETE /services/:name` | 服务 CRUD 操作 |

### 分组 API（groups.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `GroupListAPIHandler` | `GET/POST /groups` | 分组列表、创建分组 |
| `GroupAPIHandler` | `GET/DELETE /groups/:name` | 获取/删除分组 |
| `GroupUsersAPIHandler` | `POST/DELETE /groups/:name/users` | 添加/移除分组成员 |
| `GroupPropertiesAPIHandler` | `GET/PUT /groups/:name/properties` | 获取/设置分组属性 |

### Hub 管理 API（hub.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `ShutdownAPIHandler` | `POST /shutdown` | 关闭 Hub |
| `RootAPIHandler` | `GET /` | API 根端点，返回版本和链接信息 |
| `InfoAPIHandler` | `GET /info` | Hub 详细信息（版本、Python 版本、认证器等） |

### 共享 API（shares.py）

| Handler | 路由模式 | 说明 |
|---------|----------|------|
| `UserShareListAPIHandler` | `GET/POST /users/:name/shares` | 用户共享列表、创建共享 |
| `UserShareAPIHandler` | `GET/DELETE /users/:name/shares/:share_id` | 获取/删除用户共享 |
| `GroupShareListAPIHandler` | `GET/POST /groups/:name/shares` | 组共享列表 |
| `GroupShareAPIHandler` | `GET/DELETE /groups/:name/shares/:share_id` | 组共享管理 |
| `ServerShareAPIHandler` | `GET /users/:name/servers/:server_name/shares` | 服务器共享查询 |
| `ServerShareCodeAPIHandler` | `POST/GET /users/:name/servers/:server_name/share-codes` | 创建/查询共享码 |

---

## 认证中间件

### @web.authenticated 装饰器

Tornado 内置的认证装饰器，用于保护需要登录的 Handler 方法。当 `self.current_user` 为 `None` 时，自动重定向到登录页面（页面处理器）或返回 403 错误（API 处理器）。

### get_current_user() 异步认证流程

`prepare()` 方法在请求处理前调用 `await self.get_current_user()`，该方法的解析顺序为：

1. **Token 认证**（`_accept_token_auth=True` 时）：
   - 从 `Authorization` 头解析 token（支持 `token <value>` 和 `Bearer <value>` 两种格式）
   - 查询 `orm.APIToken.find(db, token)` 验证哈希
   - Token 有效则返回关联的 User 或 Service 对象
   - 标记 `self._token_authenticated = True`（跳过 XSRF 检查）

2. **Cookie 认证**（`_accept_cookie_auth=True` 时）：
   - 从安全 Cookie（`<cookie_name>`）中解密 `cookie_id`
   - 查询 `orm.User` 表匹配 `cookie_id`
   - 无效/过期 Cookie 自动清除
   - 首次认证后调用 `refresh_auth()` 刷新用户信息（按 `auth_refresh_age` 节流）

3. **认证失败**：`self.current_user` 设为 `None`

### Scope 权限检查

API 端点使用 `@needs_scope(scope)` 装饰器进行细粒度权限控制，检查当前用户/服务/Token 所拥有的 scope 是否满足请求所需权限。Scope 支持 `!server=user/name` 等过滤器格式实现服务器级粒度控制。

### XSRF 防护

- 安全方法（GET/HEAD/OPTIONS）豁免 XSRF 检查
- Token 认证请求跳过 XSRF（Token 本身即为凭证）
- Cookie 认证的 POST/PUT/DELETE 请求必须携带有效 XSRF Token
- XSRF Token 与登录用户绑定（`session_id:user_cookie_id`），登录后自动失效旧 Token

---

## 静态资源处理器（static.py）

**位置**：handlers/static.py

### CacheControlStaticFilesHandler

继承 `tornado.web.StaticFileHandler`，为不带版本查询参数（`?v=<hash>`）的静态资源设置 `Cache-Control: no-cache`，带版本参数的资源则允许长缓存，确保版本更新时客户端能获取最新资源。

### LogoHandler

继承 `StaticFileHandler`，专门用于服务 JupyterHub Logo 图片，支持自定义 Logo 配置。

---

## 指标处理器（metrics.py）

提供 Prometheus 格式的指标端点，暴露运行中的服务器数量、启动/停止耗时、登录时长、代理操作耗时等指标，供监控系统采集。

---

## Handler 注册与路由

所有 Handler 在 Hub 应用初始化时注册到 Tornado Application 的 URL 路由表中。路由分为两类：

1. **Hub 前缀路由**：以 `hub.base_url`（默认为 `/hub/`）为前缀的 Hub 自身路由（登录、管理、API 等）
2. **代理路由**：`/user/:name/...` 等用户服务器路由由 Configurable HTTP Proxy 转发到对应单用户服务器，Hub 仅处理 `/hub/` 前缀下的路由

---

## 源码溯源

- Handler 基类：handlers/base.py
- 页面处理器：handlers/pages.py
- 登录处理器：handlers/login.py
- 静态资源：handlers/static.py
- API 基类：apihandlers/base.py
- API 处理器目录：apihandlers/
  - users.py
  - proxy.py
  - services.py
  - groups.py
  - auth.py
  - hub.py
  - shares.py
