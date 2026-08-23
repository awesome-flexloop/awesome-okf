---
type: Concept
title: "Handler 继承体系"
description: "从 AuthenticatedHandler 到 APIHandler 的三层继承链、认证装饰器、请求预处理与 JSON API 响应格式"
tags: [handlers, tornado, inheritance, request-pipeline, authentication, api]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: handlers
    resource: /references/handlers-source.md
    title: base/handlers.py 源码信源
---

# Handler 继承体系

Jupyter Server 的 HTTP 请求处理基于 Tornado 的 `RequestHandler`，通过三层继承链逐层叠加功能：认证 → 核心服务 → API。

## 继承树

```
tornado.web.RequestHandler
│
└── AuthenticatedHandler (L85)          # 第一层：认证基础
    │   - CORS 来源检查
    │   - Cookie 管理
    │   - 安全头设置
    │   - Token 认证判断
    │
    └── JupyterHandler (L276)           # 第二层：核心服务
    │   │   - Manager 属性访问
    │   │   - Jinja2 模板渲染
    │   │   - 事件日志
    │   │   - 配置访问
    │   │   - 用户信息
    │   │
    │   ├── APIHandler (L751)           # 第三层：REST API
    │   │   - JSON 请求/响应
    │   │   - 错误 JSON 格式
    │   │   - Content-Type 检查
    │   │
    │   ├── Template404 (L863)          # 404 页面
    │   ├── AuthenticatedFileHandler    # 认证静态文件
    │   ├── FileFindHandler             # 多路径静态文件
    │   ├── APIVersionHandler           # /api 版本端点
    │   ├── MainHandler                 # 根路径重定向
    │   ├── FilesRedirectHandler        # /files/ 重定向
    │   ├── RedirectWithParams          # 带参数重定向
    │   └── PrometheusMetricsHandler    # /metrics 端点
    │
    └── PublicStaticFileHandler (L1184) # 公开静态文件（无需认证）
```

## 第一层：AuthenticatedHandler

所有需要认证的 Handler 的基类，负责安全基础设置。

### 安全头设置

`set_default_headers()` 为每个响应设置安全头：

```python
headers["X-Content-Type-Options"] = "nosniff"
headers["Content-Security-Policy"] = "frame-ancestors 'self'; report-uri ..."
```

CSP（Content Security Policy）默认阻止 iframe 嵌套，防止点击劫持。用户可通过 `ServerApp.headers` 配置覆盖。

### 来源检查

`check_origin()` 方法验证请求来源：
- 如果 Handler 标记为 `skip_check_origin()`（如 Token 认证），跳过检查
- 否则验证 Origin/Referer 头与 Host 匹配
- OPTIONS 预检请求始终跳过来源检查

通过 `allow_origin` 配置项可以设置允许的跨域来源，支持通配符模式。

### 认证状态属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `token_authenticated` | bool | 请求是否通过 Token 认证 |
| `logged_in` | bool | 用户是否已登录（Cookie 有效） |
| `current_user` | User | 当前用户对象（v2.0 推荐方式） |
| `base_url` | str | 服务器 base URL 前缀 |

### Cookie 管理

v2.0 中 Cookie 操作委托给 `identity_provider`：
- `clear_login_cookie()` → `identity_provider.clear_login_cookie()`
- `set_login_cookie(user)` → `identity_provider.set_login_cookie()`

## 第二层：JupyterHandler

核心处理器基类，提供对所有 ServerApp Manager 和服务的访问。

### Manager 属性

在 `prepare()` 阶段从 `self.settings` 中获取 Manager 引用：

```python
@property
def contents_manager(self):
    return self.settings["contents_manager"]

@property
def kernel_manager(self):
    return self.settings["kernel_manager"]

@property
def session_manager(self):
    return self.settings["session_manager"]

@property
def config_manager(self):
    return self.settings["config_manager"]

@property
def identity_provider(self):
    return self.settings["identity_provider"]

@property
def authorizer(self):
    return self.settings["authorizer"]

@property
def event_logger(self):
    return self.settings["event_logger"]
```

这意味着在任何 JupyterHandler 子类中，都可以通过 `self.contents_manager` 等属性直接访问核心服务。

### 模板渲染

JupyterHandler 集成了 Jinja2 模板系统：

```python
def render_template(self, name, **ns):
    """渲染 Jinja2 模板"""
    template = self.jinja2_env.get_template(name)
    ns.update(self.template_namespace)
    return template.render(**ns)

@property
def template_namespace(self):
    """模板全局变量"""
    return {
        "base_url": self.base_url,
        "static_url": self.static_url,
        "token": self.token,
        ...
    }
```

内置模板位于 `jupyter_server/templates/`，包括 `main.html`、`error.html`、`login.html`、`logout.html`、`404.html`、`page.html`、`view.html`、`browser-open.html`。

### 请求预处理

`prepare()` 方法在每个请求处理前执行：

1. 获取当前用户（认证）
2. 检查来源（CORS）
3. 设置 xsrf_token（如果需要）
4. 记录访问日志

### write_error 错误处理

重写 Tornado 的 `write_error()` ，使用 Jinja2 模板渲染美观的错误页面。错误处理会根据请求的 Accept 头选择 HTML 或 JSON 格式。

## 第三层：APIHandler

REST API 端点的基类，自动处理 JSON 序列化。

### 内容类型检查

`prepare()` 中检查 POST/PUT/PATCH 请求的 Content-Type 是否为 `application/json`。

### JSON 请求体

`get_json_body()` 方法解析请求体为 JSON：

```python
def get_json_body(self):
    if not self.request.body:
        return None
    return json.loads(self.request.body)
```

### JSON 响应

`finish()` 方法被增强：如果传入的是 dict/list，自动序列化为 JSON 并设置 `Content-Type: application/json`。

### 错误响应

API 错误统一格式：

```python
def write_error(self, status_code, **kwargs):
    self.set_header("Content-Type", "application/json")
    message = kwargs.get("reason", responses.get(status_code, "Unknown"))
    self.finish(json.dumps({
        "status": status_code,
        "message": message,
    }))
```

返回示例：
```json
{
    "status": 404,
    "message": "Not Found"
}
```

### API 版本端点

`APIVersionHandler` 在 `/api` 路径返回 API 版本信息：

```json
{
    "version": "2.21.0",
    "jupyter_server_version": "2.21.0"
}
```

## 装饰器

### @allow_unauthenticated

标记 Handler 方法不需要认证，即使整个 Handler 默认需要认证：

```python
class MyHandler(JupyterHandler):
    @allow_unauthenticated
    def get(self):
        # 无需认证即可访问
        self.finish("public info")
```

### @authorized

标记需要授权检查的方法，会调用 `authorizer.is_authorized()` 检查用户是否有权执行操作：

```python
class ContentsAPIHandler(APIHandler):
    @authorized
    def post(self, path):
        # 需要授权检查
        ...
```

### @web.authenticated

Tornado 内置装饰器，要求用户已认证。未认证时重定向到登录页。

## 请求处理流程

```
客户端请求到达
    │
    ▼
set_default_headers()  → 设置安全头
    │
    ▼
prepare()             → 认证、CORS、预处理
    │
    ├── 未认证 → 重定向登录页或返回 403
    │
    ▼ 已认证
get()/post()/put()/delete() → 业务逻辑
    │
    ├── 调用 self.contents_manager / kernel_manager 等
    ├── render_template() → HTML 响应
    └── finish(json_data) → JSON 响应
    │
    ▼
on_finish()           → 请求完成（日志记录、指标采集）
```

## 内置 Handler 路由

| 路由模式 | Handler | 说明 |
|---------|---------|------|
| `/` | MainHandler | 根路径，重定向到 default_url |
| `/api` | APIVersionHandler | API 版本 |
| `/api/status` | APIStatusHandler | 服务器状态 |
| `/api/me` | IdentityHandler | 当前用户信息 |
| `/api/contents(.*)` | ContentsHandler | 文件/目录 CRUD |
| `/api/kernels(.*)` | MainKernelHandler | 内核管理 |
| `/api/kernels/([^/]+)/channels` | KernelWebSocketHandler | 内核 WebSocket |
| `/api/sessions(.*)` | SessionHandler | 会话管理 |
| `/api/config(.*)` | ConfigHandler | 配置管理 |
| `/api/terminals(.*)` | TerminalAPIHandler | 终端 API |
| `/api/nbconvert(.*)` | NbconvertPostHandler | Notebook 转换 |
| `/api/events/subscribe` | SubscribeWebsocket | 事件订阅 |
| `/metrics` | PrometheusMetricsHandler | Prometheus 指标 |
| `/login` | LoginFormHandler | 登录页面 |
| `/logout` | LogoutHandler | 登出 |
| `/files/(.*)` | FilesHandler | 文件下载 |
| `/static/(.*)` | FileFindHandler | 静态文件 |
| `/view/(.*)` | ViewHandler | Notebook HTML 预览 |
| `/(favicon\.ico)` | FileFindHandler | 网站图标 |

## 自定义 Handler

编写扩展时，继承 JupyterHandler 或 APIHandler：

```python
from jupyter_server.base.handlers import APIHandler

class MyExtensionHandler(APIHandler):
    @property
    def my_service(self):
        return self.settings["my_service"]

    def get(self, resource_id):
        data = self.my_service.get_resource(resource_id)
        self.finish(json.dumps(data))

    @web.authenticated
    def post(self, resource_id):
        body = self.get_json_body()
        result = self.my_service.create_resource(body)
        self.set_status(201)
        self.finish(json.dumps(result))
```

## 相关概念

- [认证授权系统](05-auth-system.md) — IdentityProvider 和 Authorizer 详解
- [内容管理服务](07-contents-service.md) — ContentsHandler 背后的业务逻辑
- [扩展系统](10-extension-system.md) — 如何添加自定义 Handler
