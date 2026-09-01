---
title: 开发服务端扩展
type: example
bundle: jupyter-notebook
chapter: "02"
difficulty: intermediate
tags: ["extension", "backend", "server", "api", "handler"]
prerequisites: ["00-quickstart"]
sources: ["F-019", "F-020", "F-021"]
related_concepts: ["02-backend-app", "04-handlers"]
---

# 02 | 开发服务端扩展

本教程将创建一个Jupyter Notebook服务端扩展，添加自定义API端点和页面路由。你将学习如何编写Jupyter Server扩展。

## 什么是服务端扩展

服务端扩展在Notebook/Jupyter Server启动时加载，可以：
- 添加自定义HTTP API端点
- 添加自定义页面路由
- 操作服务器配置
- 添加自定义中间件
- 与前端扩展配合提供完整功能

## 前置条件

- Python 3.10+
- Jupyter Notebook v7 已安装
- 基础的Python和Tornado知识

## 方式一：简单的单文件扩展

对于简单扩展，你可以直接在配置文件中添加Handler。但更规范的方式是创建一个包。

## 方式二：创建Python扩展包（推荐）

### 第一步：创建项目结构

```
jupyter_srv_info/
├── pyproject.toml           # 包配置
├── jupyter_srv_info/
│   ├── __init__.py          # 扩展入口
│   ├── handlers.py          # 自定义Handler
│   └── _version.py          # 版本号
```

### 第二步：编写Handler

创建 `jupyter_srv_info/handlers.py`：

```python
"""自定义请求处理器"""
import json
import os
import platform
import sys
import time
from typing import Any

import psutil
from jupyter_server.base.handlers import JupyterHandler
from tornado import web


class ServerInfoHandler(JupyterHandler):
    """返回服务器信息的API端点"""

    @web.authenticated
    def get(self) -> None:
        """GET /api/srv-info"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # 内存信息
            memory = psutil.virtual_memory()

            # 磁盘信息
            disk = psutil.disk_usage(os.path.expanduser("~"))

            info = {
                "server_time": time.time(),
                "python_version": sys.version,
                "platform": platform.platform(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent,
                    "used": disk.used,
                },
                "pid": os.getpid(),
            }

            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(info))

        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"error": str(e)}))


class EnvHandler(JupyterHandler):
    """返回环境变量列表（仅KEY名，不暴露敏感值）"""

    @web.authenticated
    def get(self) -> None:
        """GET /api/srv-info/env"""
        # 只返回环境变量名，不返回值（安全考虑）
        env_keys = sorted(os.environ.keys())

        # 过滤掉可能包含敏感信息的变量
        sensitive_patterns = ("TOKEN", "PASSWORD", "SECRET", "KEY", "CREDENTIAL")
        safe_keys = [
            k for k in env_keys
            if not any(pat in k.upper() for pat in sensitive_patterns)
        ]

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"env_keys": safe_keys}))


class CustomPageHandler(JupyterHandler):
    """自定义页面Handler - 渲染一个简单的状态页面"""

    @web.authenticated
    def get(self) -> None:
        """GET /srv-info/status"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Info</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        h1 { color: #333; }
        .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .info-item { margin: 10px 0; }
        .bar { height: 20px; background: #ddd; border-radius: 10px; overflow: hidden; }
        .bar-fill { height: 100%; transition: width 0.3s; }
        .cpu-bar .bar-fill { background: #4CAF50; }
        .mem-bar .bar-fill { background: #2196F3; }
        .disk-bar .bar-fill { background: #FF9800; }
    </style>
</head>
<body>
    <h1>🖥️ Server Status</h1>
    <div class="info">
        <div class="info-item"><strong>Python:</strong> """ + sys.version.split()[0] + """</div>
        <div class="info-item"><strong>Platform:</strong> """ + platform.platform() + """</div>
        <div class="info-item"><strong>PID:</strong> """ + str(os.getpid()) + """</div>
    </div>
    <div class="info cpu-bar">
        <div class="info-item">CPU: <span id="cpu-val">--</span></div>
        <div class="bar"><div class="bar-fill" id="cpu-bar" style="width:0%"></div></div>
    </div>
    <div class="info mem-bar">
        <div class="info-item">Memory: <span id="mem-val">--</span></div>
        <div class="bar"><div class="bar-fill" id="mem-bar" style="width:0%"></div></div>
    </div>
    <div class="info disk-bar">
        <div class="info-item">Disk: <span id="disk-val">--</span></div>
        <div class="bar"><div class="bar-fill" id="disk-bar" style="width:0%"></div></div>
    </div>

    <script>
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function refresh() {
            try {
                const res = await fetch('/api/srv-info', { credentials: 'include' });
                const data = await res.json();

                document.getElementById('cpu-val').textContent = data.cpu.percent.toFixed(1) + '%';
                document.getElementById('cpu-bar').style.width = data.cpu.percent + '%';

                document.getElementById('mem-val').textContent =
                    data.memory.percent.toFixed(1) + '% (' + formatBytes(data.memory.used) + ' / ' + formatBytes(data.memory.total) + ')';
                document.getElementById('mem-bar').style.width = data.memory.percent + '%';

                document.getElementById('disk-val').textContent =
                    data.disk.percent.toFixed(1) + '% (' + formatBytes(data.disk.used) + ' / ' + formatBytes(data.disk.total) + ')';
                document.getElementById('disk-bar').style.width = data.disk.percent + '%';
            } catch(e) {
                console.error('Failed to fetch server info:', e);
            }
        }

        refresh();
        setInterval(refresh, 2000);
    </script>
</body>
</html>
"""
        self.write(html)
```

### 第三步：编写扩展入口

创建 `jupyter_srv_info/__init__.py`：

```python
"""Jupyter Server Info Extension"""
from ._version import __version__


def _jupyter_server_extension_points():
    """Jupyter Server发现扩展时调用的入口点"""
    return [{"module": "jupyter_srv_info", "app": None}]


def _load_jupyter_server_extension(server_app):
    """注册自定义handlers"""
    web_app = server_app.web_app

    # 获取base_url前缀
    base_url = web_app.settings.get("base_url", "/")

    # 导入handlers（延迟导入，避免循环依赖）
    from .handlers import ServerInfoHandler, EnvHandler, CustomPageHandler

    # 注册路由
    web_app.add_handlers(
        ".*$",  # 匹配所有host
        [
            (base_url.rstrip("/") + "/api/srv-info", ServerInfoHandler),
            (base_url.rstrip("/") + "/api/srv-info/env", EnvHandler),
            (base_url.rstrip("/") + "/srv-info/status", CustomPageHandler),
        ],
    )

    server_app.log.info("Server Info extension loaded!")
```

创建 `jupyter_srv_info/_version.py`：

```python
__version__ = "0.1.0"
```

### 第四步：配置pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "jupyter-srv-info"
version = "0.1.0"
description = "A Jupyter Server extension providing server info API"
requires-python = ">=3.10"
dependencies = [
    "jupyter_server>=2.0",
    "psutil>=5.9",
]

[project.entry-points."jupyter_server.extensions"]
srv-info = "jupyter_srv_info"
```

### 第五步：安装和启用

```bash
# 安装扩展
pip install -e .

# 启用扩展
jupyter server extension enable jupyter_srv_info

# 验证扩展已加载
jupyter server extension list
# 应该看到 jupyter_srv_info  enabled
```

### 第六步：测试

启动Notebook：

```bash
jupyter notebook
```

测试API端点：

```bash
# 获取服务器信息（使用token认证）
curl "http://localhost:8888/api/srv-info?token=YOUR_TOKEN"

# 访问自定义页面
# 浏览器打开: http://localhost:8888/srv-info/status
```

你应该看到一个实时刷新的服务器状态页面。

## 与前端扩展联动

你可以将服务端API与前端扩展配合使用。前端通过fetch调用API：

```typescript
// 在前端扩展中调用后端API
async function fetchServerInfo(): Promise<any> {
  const response = await fetch(
    PageConfig.getBaseUrl() + 'api/srv-info',
    { credentials: 'include' }  // 重要：携带cookie/token认证
  );
  return response.json();
}
```

## Handler基类选择

| 基类 | 适用场景 |
|------|---------|
| `JupyterHandler` | 需要用户认证的API/页面 |
| `APIHandler` | REST API端点（提供JSON错误处理） |
| `ExtensionHandler` (from jupyter_server) | 扩展专用Handler |
| `NotebookBaseHandler` (from notebook) | 需要page_config的Notebook页面 |
| `tornado.web.RequestHandler` | 不需要Jupyter认证的公开端点（谨慎使用） |

## 高级：修改page_config

如果你需要向页面传递自定义配置数据，可以通过 `page_config_hook` 实现：

```python
def _load_jupyter_server_extension(server_app):
    web_app = server_app.web_app

    # 获取现有的page_config_hook（如果有）
    existing_hook = web_app.settings.get("page_config_hook")

    def custom_page_config_hook(handler, page_config):
        # 先执行现有hook
        if existing_hook:
            page_config = existing_hook(handler, page_config)

        # 添加自定义配置
        page_config["myExtension"] = {
            "apiUrl": "/api/srv-info",
            "version": "0.1.0"
        }
        return page_config

    web_app.settings["page_config_hook"] = custom_page_config_hook
```

前端可以通过 `PageConfig.getOption('myExtension')` 读取。

## 高级：注册自定义Jinja2模板

如果需要渲染HTML模板：

```python
from pathlib import Path
from jupyter_server.utils import url_path_join

HERE = Path(__file__).parent

def _load_jupyter_server_extension(server_app):
    # 添加模板目录
    web_app = server_app.web_app
    env = web_app.settings.get("jinja2_env")
    if env:
        env.loader.searchpath.append(str(HERE / "templates"))

    # 然后在Handler中使用
    # self.render_template("my_template.html", my_var=value)
```

## 认证与安全

### 必须使用@web.authenticated

所有API和页面Handler都应添加 `@web.authenticated` 装饰器，确保只有认证用户可以访问：

```python
from tornado import web

class MyHandler(JupyterHandler):
    @web.authenticated
    def get(self):
        # 只有认证用户能访问
        pass
```

### 不要泄露敏感信息

- 不要在API响应中返回完整环境变量（包含token/password）
- 不要暴露文件系统完整路径
- 对用户输入进行验证和清理

### CORS配置

如果API需要被其他域访问，配置CORS：

```python
# 服务端扩展中设置CORS头
self.set_header("Access-Control-Allow-Origin", "*")
self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
```

或使用Jupyter Server的CORS配置：

```python
c.ServerApp.allow_origin = "https://my-domain.com"
```

## 调试技巧

### 查看扩展日志

Notebook启动时会显示扩展加载日志：

```
[I 2026-08-21 10:00:00.000 ServerApp] Server Info extension loaded!
```

使用 `--debug` 启动获得更详细日志：

```bash
jupyter notebook --debug
```

### 手动测试API

```python
# 在Notebook中测试API
import requests
from notebook.auth import passwd
# 或直接在浏览器中访问 /api/srv-info
```

## 常见问题

### Q: 扩展不加载？

检查：
1. `pip list | grep srv-info` 确认已安装
2. `jupyter server extension list` 确认已启用
3. 检查启动日志中的错误信息
4. 确认entry_points配置正确

### Q: 403 Forbidden错误？

- 确认请求携带了有效token或cookie
- 检查 `@web.authenticated` 装饰器是否添加
- 确认请求URL包含正确的token参数

### Q: 如何同时支持Notebook和JupyterLab？

服务端扩展基于Jupyter Server，与前端无关。同一个服务端扩展在Notebook和JupyterLab下都能工作。

## 下一步

- [集成自定义认证](04-custom-auth.md) 学习替换默认认证系统
- [自定义Shell布局](03-customize-shell.md) 前端+后端联动的完整示例
