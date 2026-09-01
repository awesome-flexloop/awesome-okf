---
type: Example
title: "编写简单扩展"
description: "从零创建一个 Jupyter Server 扩展，添加自定义 API 端点、静态页面和配置项"
tags: [extension, custom-handler, extension-app, plugin, tutorial]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: extension
    resource: /references/extension-source.md
    title: 扩展系统源码信源
---

# 编写简单扩展

本示例展示如何创建一个完整的 Jupyter Server 扩展：添加自定义 API、提供 HTML 页面、使用配置项。

## 项目结构

```
my_jupyter_extension/
├── pyproject.toml           # 包配置
└── my_jupyter_extension/
    ├── __init__.py          # 扩展入口点
    ├── handlers.py          # 自定义 Handlers
    ├── static/              # 静态资源
    │   └── index.html
    └── templates/           # Jinja2 模板
        └── page.html
```

## Step 1: 创建包配置

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-jupyter-extension"
version = "0.1.0"
dependencies = [
    "jupyter_server>=2.0",
    "tornado>=6.1",
]

[project.entry-points."jupyter_server.extensions"]
my_extension = "my_jupyter_extension:MyExtension"
```

## Step 2: 创建扩展主类

```python
# my_jupyter_extension/__init__.py
from jupyter_server.extension.application import ExtensionApp
from traitlets import Unicode, Integer, Bool
from .handlers import HelloAPIHandler, StatusAPIHandler, MyPageHandler
import os

class MyExtension(ExtensionApp):
    """一个简单的 Jupyter Server 扩展示例"""

    name = "my_extension"
    extension_url = "/myext"
    load_other_extensions = True

    # 自定义配置项
    greeting = Unicode("Hello", help="问候语").tag(config=True)
    max_requests = Integer(100, help="最大请求数限制").tag(config=True)
    show_welcome = Bool(True, help="启动时显示欢迎信息").tag(config=True)

    # 静态资源和模板路径
    @property
    def static_paths(self):
        return [os.path.join(os.path.dirname(__file__), "static")]

    @property
    def template_paths(self):
        return [os.path.join(os.path.dirname(__file__), "templates")]

    def initialize_settings(self):
        """初始化扩展设置"""
        self.log.info(f"Initializing {self.name} extension")
        # 向 application.settings 注入共享数据
        self.settings.update({
            "my_greeting": self.greeting,
            "my_max_requests": self.max_requests,
        })

    def initialize_handlers(self):
        """注册 URL Handlers"""
        self.handlers.extend([
            # API 端点
            ("/myext/api/hello", HelloAPIHandler),
            ("/myext/api/status", StatusAPIHandler),
            # HTML 页面
            ("/myext/?", MyPageHandler),
        ])
        self.log.info(f"Registered handlers for {self.name}")

    def _log_greeting(self):
        if self.show_welcome:
            self.log.info(f"🎊 My Extension loaded! Visit {self.extension_url}")
```

## Step 3: 编写 Handlers

```python
# my_jupyter_extension/handlers.py
from jupyter_server.base.handlers import APIHandler, JupyterHandler
from tornado import web
import json
import platform
import datetime

class HelloAPIHandler(APIHandler):
    """Hello World API 端点"""

    @web.authenticated
    async def get(self):
        """GET /myext/api/hello"""
        greeting = self.settings.get("my_greeting", "Hello")
        self.finish(json.dumps({
            "message": f"{greeting} from My Extension!",
            "server_time": datetime.datetime.now().isoformat(),
            "user": self.current_user.username if self.current_user else "anonymous",
        }))

    @web.authenticated
    async def post(self):
        """POST /myext/api/hello - 回显数据"""
        body = self.get_json_body()
        if body is None:
            raise web.HTTPError(400, "JSON body required")
        name = body.get("name", "World")
        self.set_status(201)
        self.finish(json.dumps({
            "message": f"Hello, {name}!",
            "received": body,
        }))


class StatusAPIHandler(APIHandler):
    """服务器状态 API"""

    @web.authenticated
    async def get(self):
        """GET /myext/api/status"""
        self.finish(json.dumps({
            "status": "running",
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "extension_version": "0.1.0",
            "kernel_count": len(self.kernel_manager._kernels) if hasattr(self, 'kernel_manager') else 0,
        }))


class MyPageHandler(JupyterHandler):
    """HTML 页面"""

    @web.authenticated
    async def get(self):
        """GET /myext/"""
        greeting = self.settings.get("my_greeting", "Hello")
        await self.render_template(
            "page.html",
            greeting=greeting,
            title="My Extension",
            static_url=self.static_url,
        )
```

## Step 4: 创建 HTML 模板

```html
<!-- my_jupyter_extension/templates/page.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .card {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
            background: white;
        }
        button {
            background: #1976d2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #1565c0; }
        #output { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>{{ greeting }}! 👋</h1>
        <p>This page is served by <strong>My Jupyter Extension</strong>.</p>
        <button onclick="callAPI()">Call API</button>
        <pre id="output"></pre>
    </div>

    <script>
        async function callAPI() {
            const res = await fetch('/myext/api/hello');
            const data = await res.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);
        }
        // Auto-call on load
        callAPI();
    </script>
</body>
</html>
```

## Step 5: 创建静态页面（可选）

```html
<!-- my_jupyter_extension/static/index.html -->
<!DOCTYPE html>
<html>
<head><title>My Extension Static</title></head>
<body>
    <h1>Static page</h1>
    <p>This is served directly from the static directory.</p>
</body>
</html>
```

## Step 6: 安装和启用

```bash
# 开发模式安装
pip install -e .

# 验证扩展已发现
jupyter server extension list
# 应看到: my_extension  enabled

# 启动 Jupyter Server
jupyter server

# 访问扩展
# http://localhost:8888/myext
# http://localhost:8888/myext/api/hello
# http://localhost:8888/myext/api/status
```

## Step 7: 配置扩展

```python
# jupyter_server_config.py
c = get_config()
c.MyExtension.greeting = "Welcome"
c.MyExtension.show_welcome = True
c.MyExtension.max_requests = 500
```

## 测试扩展 API

```bash
# Hello API
curl http://localhost:8888/myext/api/hello?token=mytoken

# POST 测试
curl -X POST http://localhost:8888/myext/api/hello?token=mytoken \
  -H "Content-Type: application/json" \
  -d '{"name": "Jupyter"}'

# Status API
curl http://localhost:8888/myext/api/status?token=mytoken
```

## 参考

- [扩展系统](../concepts/10-extension-system.md) — ExtensionApp 完整 API
- [Handler 继承体系](../concepts/04-handler-hierarchy.md) — APIHandler/JupyterHandler 详解
- [认证授权系统](../concepts/05-auth-system.md) — @web.authenticated 装饰器
