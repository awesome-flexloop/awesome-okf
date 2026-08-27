---
type: Concept
title: 服务端扩展开发
description: 掌握 Jupyter Server APIHandler 模式、路由注册、认证装饰器、前后端通信协议和服务端扩展生命周期。
tags: [server-extension, apihandler, tornado, routes, authentication, backend]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: server-routes
    resource: /references/server-routes-source.md
    title: Python 服务端模板解析
  - id: init-py
    location: template/{{python_name}}/__init__.py.jinja
    lines: "1-36"
  - id: request-ts
    location: template/src/{% if kind == 'frontend-and-server' %}request.ts{% endif %}.jinja
    lines: "1-51"
---

## 服务端扩展开发

当选择 `frontend-and-server` 类型时，模板会生成完整的服务端扩展骨架。JupyterLab 的服务端扩展基于 Jupyter Server（Jupyter 的后端服务框架），使用 Tornado 作为 Web 服务器。服务端扩展通过 REST API 与前端通信，提供文件系统访问、计算能力、外部 API 代理等功能。

## 服务端架构概览

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│  ┌──────────────┐    fetch/AJAX   ┌──────────────┐  │
│  │ JupyterLab   │ ◄──────────────►│  requestAPI  │  │
│  │ (Frontend)   │                 │   (TS)       │  │
│  └──────────────┘                 └──────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                   REST API (JSON)
                         │
┌─────────────────────────────────────────────────────┐
│               Jupyter Server (Python)               │
│  ┌──────────────────────────────────────────────┐   │
│  │  Tornado Web Server                         │   │
│  │  ┌─────────────────────────────────────────┐ │   │
│  │  │  APIHandler (your route handlers)       │ │   │
│  │  │  @tornado.web.authenticated             │ │   │
│  │  │  GET/POST/PUT/DELETE methods            │ │   │
│  │  └─────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────┐ │   │
│  │  │  Jupyter Server internals               │ │   │
│  │  │  - Session manager                      │ │   │
│  │  │  - Contents manager                     │ │   │
│  │  │  - Kernel manager                       │ │   │
│  │  └─────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Python 入口点

`__init__.py` 包含服务端扩展的入口函数：

```python
from ._version import __version__
from .routes import setup_route_handlers

# 1. 前端资源路径注册（所有类型都必须有）
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "myextension"}]

# 2. 服务端扩展点声明（仅 frontend-and-server 类型）
def _jupyter_server_extension_points():
    return [{"module": "myextension"}]

# 3. 服务端扩展加载回调
def _load_jupyter_server_extension(server_app):
    """注册 API 路由处理器"""
    setup_route_handlers(server_app.web_app)
    server_app.log.info(f"Registered myextension server extension")
```

三个入口点的作用：
- `_jupyter_labextension_paths()`：告诉 JupyterLab 在哪里找前端静态文件（返回相对路径和目标名）
- `_jupyter_server_extension_points()`：声明这是一个 Jupyter Server 扩展，返回模块路径列表
- `_load_jupyter_server_extension(server_app)`：服务器启动时调用，接收 `ServerApp` 实例，用于注册路由等初始化操作

## 路由处理器

模板生成的 `routes.py` 展示了标准的 APIHandler 模式：

```python
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class HelloRouteHandler(APIHandler):
    """处理 /myextension/hello 端点的请求"""

    @tornado.web.authenticated
    def get(self):
        """处理 GET 请求"""
        self.finish(json.dumps({
            "data": (
                "Hello, world!"
                " This is the '/myextension/hello' endpoint."
                " Try visiting me in your browser!"
            ),
        }))

def setup_route_handlers(web_app):
    """注册所有路由处理器"""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    hello_route_pattern = url_path_join(base_url, "myextension", "hello")
    handlers = [(hello_route_pattern, HelloRouteHandler)]

    web_app.add_handlers(host_pattern, handlers)
```

### APIHandler 基类要点

所有自定义处理器继承自 `jupyter_server.base.handlers.APIHandler`，它提供：
- 自动 JSON 错误处理
- 访问当前用户信息（`self.current_user`）
- Jupyter Server 配置访问（`self.settings`）
- 内置身份验证集成

### 认证装饰器（必须）

**每个 HTTP 方法都必须加 `@tornado.web.authenticated`**，这是安全红线。这个装饰器确保只有已登录的用户才能访问端点。

CI 中的 `check_auth.py` 脚本会自动检查所有处理器方法是否都有认证装饰器：

```bash
python .github/scripts/check_auth.py myextension
```

如果遗漏，CI 会失败。

### URL 命名规则

- API 路径命名空间格式：`/<base_url>/<python_name>/<endpoint>`
- Python 包名中的下划线 `_` 在 URL 中转为连字符 `-`（如 `my_extension` → `/my-extension/`）
- 使用 `url_path_join()` 拼接路径，自动处理斜杠

### HTTP 方法

在 Handler 类中实现以下方法来处理对应 HTTP 动词：

```python
class MyHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        """获取数据"""
        data = self.get_argument("key", "default")  # 获取查询参数
        self.finish(json.dumps({"result": "ok"}))

    @tornado.web.authenticated
    def post(self):
        """创建资源"""
        body = json.loads(self.request.body)  # 获取请求体
        self.set_status(201)  # 设置状态码
        self.finish(json.dumps({"created": True}))

    @tornado.web.authenticated
    def put(self):
        """更新资源"""
        body = json.loads(self.request.body)
        self.finish(json.dumps({"updated": True}))

    @tornado.web.authenticated
    def delete(self):
        """删除资源"""
        resource_id = self.get_argument("id")
        self.set_status(204)
        self.finish()
```

## 前端通信封装

模板生成 `src/request.ts` 提供类型安全的 API 调用函数：

```typescript
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

export async function requestAPI<T>(
  endPoint: string,
  serverSettings: ServerConnection.ISettings,
  init: RequestInit = {}
): Promise<T> {
  const requestUrl = URLExt.join(
    serverSettings.baseUrl,
    'myextension',  // 必须与后端 namespace 一致（_ 转 -）
    endPoint
  );

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(
      requestUrl, init, serverSettings
    );
  } catch (error) {
    throw new ServerConnection.NetworkError(error as any);
  }

  let data: any = await response.text();
  if (data.length > 0) {
    try { data = JSON.parse(data); } catch (e) { console.log('Not JSON response', response); }
  }

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  return data;
}
```

关键设计要点：
- 使用 `ServerConnection.makeRequest` 而非原生 `fetch`，自动处理认证 token、base URL 和 CSRF
- URL 命名空间必须与后端一致（Python 包名 _ 转 -）
- 自动处理 JSON 解析和错误响应
- 通过泛型 `<T>` 提供类型安全的返回值

### 在 activate 中使用

```typescript
activate: (app: JupyterFrontEnd) => {
  // 简单 GET 请求
  requestAPI<any>('hello', app.serviceManager.serverSettings)
    .then(data => { console.log('Server response:', data); })
    .catch(reason => {
      console.error('Server extension appears to be missing.', reason);
    });

  // POST 请求带 body
  requestAPI<any>('my-endpoint', app.serviceManager.serverSettings, {
    method: 'POST',
    body: JSON.stringify({ key: 'value' })
  });
}
```

## 自动启用配置

模板生成 `jupyter-config/server-config/myextension.json`，安装时自动注册服务端扩展：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "myextension": true
    }
  }
}
```

这个文件安装到 Jupyter 的 `etc/jupyter/jupyter_server_config.d/` 目录，Jupyter Server 启动时自动加载，无需手动运行 `jupyter server extension enable`。

## 添加新端点的标准步骤

1. 在 `routes.py` 中创建新的 Handler 类，继承 APIHandler
2. 在每个 HTTP 方法上加 `@tornado.web.authenticated`
3. 在 `setup_route_handlers()` 中注册路由
4. 在前端 `src/` 中调用 `requestAPI()` 访问新端点
5. 重启 JupyterLab 使 Python 更改生效

## 常见服务端模式

### 访问 Jupyter 内部服务

Handler 中可以通过 `self.settings` 访问 Jupyter Server 的内部管理器：

```python
class MyHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        contents_manager = self.contents_manager  # 文件系统访问
        kernel_manager = self.kernel_manager      # 内核管理
        session_manager = self.session_manager    # 会话管理
        # 使用管理器操作文件、启动内核等
```

### 启动子进程

```python
import subprocess

class CommandHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        body = json.loads(self.request.body)
        result = subprocess.run(
            ['python', '-c', body['code']],
            capture_output=True, text=True, timeout=30
        )
        self.finish(json.dumps({"stdout": result.stdout, "stderr": result.stderr}))
```

注意：长时间运行的任务应该使用异步模式（`tornado.ioloop`），避免阻塞服务器。

### 使用 WebSocket

对于需要双向通信的场景（如流式输出），可以使用 Tornado 的 WebSocket 支持：

```python
from jupyter_server.base.handlers import APIHandler, JupyterHandler
from tornado.websocket import WebSocketHandler

class StreamHandler(APIHandler, WebSocketHandler):
    @tornado.web.authenticated
    def open(self):
        # WebSocket 连接建立
        pass

    def on_message(self, message):
        # 收到消息
        self.write_message(json.dumps({"echo": message}))

    def on_close(self):
        # 连接关闭
        pass
```

## 相关概念

- [前端扩展开发](06-frontend-extension.md)
- [四种扩展类型对比](03-four-extension-types.md)
- [三层测试策略](11-testing-strategy.md)
- [Python 服务端模板解析](../references/server-routes-source.md)
