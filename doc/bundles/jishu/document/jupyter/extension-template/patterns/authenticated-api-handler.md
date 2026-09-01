---
type: Pattern
title: 认证 API Handler 模式
description: Jupyter Server 扩展中安全的 API 端点模式，所有 HTTP 方法必须加认证装饰器，并在 CI 中自动检查。
tags: [security, authentication, apihandler, tornado, jupyter-server]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:36:00Z" }
status: stable
source: extension-template
applicability: Jupyter Server 扩展、Tornado Web 应用
---

# 认证 API Handler 模式

## 问题

Jupyter Server 是多用户环境中的 Web 服务，如果 API 端点缺少认证，任何能访问服务器的人（包括通过 CSRF 攻击的恶意网页）都可以执行任意操作，造成严重安全漏洞。

## 解决方案

所有自定义 API 端点继承 `APIHandler`，每个 HTTP 方法（GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS）必须添加 `@tornado.web.authenticated` 装饰器，并在 CI 中自动检查认证覆盖。

## 实现模式

### 1. Handler 实现

```python
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class MyAPIHandler(APIHandler):
    @tornado.web.authenticated  # 每个 HTTP 方法都必须有！
    def get(self):
        # GET 处理逻辑
        param = self.get_argument("key", "default")
        self.finish(json.dumps({"result": "ok"}))

    @tornado.web.authenticated
    def post(self):
        # POST 处理逻辑
        body = json.loads(self.request.body)
        self.set_status(201)
        self.finish(json.dumps({"created": True}))
```

### 2. 路由注册

```python
def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "my-extension", "endpoint")
    web_app.add_handlers(host_pattern, [(route_pattern, MyAPIHandler)])
```

### 3. 入口点注册

```python
def _jupyter_server_extension_points():
    return [{"module": "my_extension"}]

def _load_jupyter_server_extension(server_app):
    setup_route_handlers(server_app.web_app)
```

### 4. 自动认证检查（CI）

```python
# .github/scripts/check_auth.py
import ast, sys

def check_auth(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in \
                   ('get', 'post', 'put', 'delete', 'patch', 'head', 'options'):
                    has_auth = any(
                        isinstance(d, ast.Name) and d.id == 'authenticated'
                        or (isinstance(d, ast.Attribute) and d.attr == 'authenticated')
                        for d in item.decorator_list
                    )
                    if not has_auth:
                        print(f"ERROR: {node.name}.{item.name}() missing @authenticated")
                        sys.exit(1)
```

## URL 命名约定

- API 命名空间格式：`/<base_url>/<python_name>/<endpoint>`
- Python 包名中的下划线 `_` 在 URL 中转为连字符 `-`
- 使用 `url_path_join()` 拼接路径，自动处理斜杠

## 前端调用模式

```typescript
// 使用 ServerConnection.makeRequest（自动处理认证 token）
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';

async function requestAPI<T>(endPoint: string, settings: ServerConnection.ISettings, init?: RequestInit): Promise<T> {
  const url = URLExt.join(settings.baseUrl, 'my-extension', endPoint);
  const response = await ServerConnection.makeRequest(url, init || {}, settings);
  if (!response.ok) throw new ServerConnection.ResponseError(response);
  return response.json();
}
```

关键：使用 `ServerConnection.makeRequest` 而非原生 `fetch`，它自动处理：
- 认证 token（XSRF cookie）
- Base URL 前缀
- 网络错误处理

## 关键原则

1. **所有方法都要装饰**：包括 OPTIONS 和 HEAD，不能遗漏
2. **CI 强制执行**：每次 PR 自动运行认证检查脚本，遗漏则 CI 失败
3. **URL 命名空间**：所有端点必须在扩展专属路径下，不能注册到根路径
4. **使用 jupyter-server 基类**：继承 APIHandler 而非裸的 tornado.web.RequestHandler，获得 Jupyter 内置错误处理
5. **前端使用官方 API**：通过 ServerConnection 发请求，不要自己处理认证

## 反模式

- ❌ 遗漏任何一个 HTTP 方法的 `@tornado.web.authenticated`
- ❌ 让前端直接用 `fetch()` 调用后端（缺少自动认证处理）
- ❌ 将端点注册到根 URL 路径（可能与其他扩展冲突）
- ❌ 在认证端点中执行危险操作而不额外检查权限

## 适用场景

- Jupyter Server / JupyterLab 服务端扩展
- 基于 Tornado 的需要认证的 Web API
- 任何在多用户 Jupyter 环境中暴露 HTTP 端点的扩展
