---
type: Reference
title: "base/handlers.py 源码信源"
description: "Jupyter Server 基础 Handler 体系：AuthenticatedHandler、JupyterHandler、APIHandler 三层继承"
tags: [handlers, tornado, authentication, api, template]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/base/handlers.py
    title: jupyter_server/base/handlers.py
---

# base/handlers.py 源码信源

## Handler 继承体系

```
web.RequestHandler (Tornado)
└── AuthenticatedHandler (L85)
    └── JupyterHandler (L276)
        ├── APIHandler (L751)
        ├── Template404 (L863)
        ├── AuthenticatedFileHandler (L872)
        ├── FileFindHandler (L983)
        ├── APIVersionHandler (L1072)
        ├── MainHandler (L1104)
        ├── FilesRedirectHandler (L1116)
        ├── PrometheusMetricsHandler (L1169)
        └── RedirectWithParams (L1153)
```

### AuthenticatedHandler (L85)

带认证用户的 RequestHandler 基类。

**核心属性**：
- `base_url`: 从 settings 获取 base_url
- `content_security_policy`: CSP 策略，默认 `frame-ancestors 'self'`
- `token_authenticated` (property): 是否通过 Token 认证
- `logged_in` (property): 用户是否已登录
- `current_user` (property): 获取当前用户（通过 identity_provider）

**核心方法**：
- `set_default_headers()`: 设置 X-Content-Type-Options、CSP 等安全头
- `get_current_user()`: 获取当前用户（v2.0 废弃，使用 self.current_user）
- `skip_check_origin()`: 判断是否跳过来源检查（OPTIONS 请求跳过）
- `clear_login_cookie()`: 清除登录 Cookie（废弃，用 identity_provider 替代）
- `force_clear_cookie()`: 强制清除 Cookie
- `get_login_url()`: 获取登录 URL

### JupyterHandler (L276)

核心处理器基类，在 AuthenticatedHandler 基础上增加：

**核心属性**：
- `application`: ServerWebApplication 实例
- `config`: ServerApp 配置
- `contents_manager`: ContentsManager 实例
- `kernel_manager`: MappingKernelManager 实例
- `session_manager`: SessionManager 实例
- `kernel_spec_manager`: KernelSpecManager 实例
- `config_manager`: ConfigManager 实例
- `identity_provider`: IdentityProvider 实例
- `authorizer`: Authorizer 实例
- `event_logger`: EventLogger 实例
- `log`: 日志记录器
- `jinja2_env`: Jinja2 模板环境

**核心方法**：
- `prepare()`: 请求预处理，完成认证、CORS 检查
- `get_current_user()`: 从 identity_provider 获取用户
- `render_template(name, **ns)`: 渲染 Jinja2 模板
- `render(template_name, **kwargs)`: 渲染模板页面
- `write_error(status_code, **kwargs)`: 渲染错误页面
- `get_json_body()`: 解析请求体 JSON
- `get_body_argument()`: 获取请求体参数
- `set_login_cookie(user)`: 设置登录 Cookie
- `redirect(url, permanent=False, status=None)`: 重定向
- `static_url(path, include_version=True)`: 静态文件 URL
- `get_template_path()`: 获取模板路径

**装饰器方法**：
- `@web.authenticated`: 装饰器，要求认证
- `@authorized`: 装饰器，要求授权检查

### APIHandler (L751)

REST API 处理器基类，在 JupyterHandler 基础上增加：

**核心方法**：
- `prepare()`: API 预处理，检查 Content-Type
- `finish(chunk=None)`: 完成响应，处理 JSON 序列化
- `get_json_body()`: 获取 JSON 请求体（支持大文件）
- `write_error(status_code, **kwargs)`: JSON 格式错误响应
- `set_default_headers()`: 设置 JSON API 默认头
- `check_referer()`: 检查 Referer 头

**API 响应格式**：
- 成功：直接写入 JSON 数据
- 错误：`{"status": <status_code>, "message": <error_message>}`

### 其他 Handler

| Handler | 行号 | 说明 |
|---------|------|------|
| Template404 | L863 | 404 页面模板 Handler |
| AuthenticatedFileHandler | L872 | 需要认证的静态文件服务 |
| FileFindHandler | L983 | 多路径静态文件查找 |
| APIVersionHandler | L1072 | API 版本端点 `/api` |
| TrailingSlashHandler | L1084 | 尾部斜杠重定向 |
| MainHandler | L1104 | 根路径 `/` 处理器，重定向到 default_url |
| FilesRedirectHandler | L1116 | `/files/` 重定向处理 |
| RedirectWithParams | L1153 | 带参数重定向 |
| PrometheusMetricsHandler | L1169 | Prometheus 指标端点 `/metrics` |
| PublicStaticFileHandler | L1184 | 公开静态文件（无需认证） |

## 认证装饰器

从 `jupyter_server.auth.decorator` 导入：
- `@allow_unauthenticated`: 标记 Handler 方法无需认证
- `@authorized`: 标记需要授权检查
