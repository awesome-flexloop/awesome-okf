---
type: Concept
title: 服务端扩展
description: 编写Python服务端扩展，注册HTTP API端点和静态文件路由，从前端扩展调用
tags: [jupyterlab, server-extension, python, tornado, APIHandler, jupyter-server]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: handlers-src
    resource: /references/examples-index.md
    title: jupyterlab_examples_server/handlers.py
  - id: server-init-src
    resource: /references/examples-index.md
    title: jupyterlab_examples_server/__init__.py
---

## 服务端扩展概述

JupyterLab前端扩展运行在浏览器中，需要访问服务端资源（文件系统、计算资源、外部API）时，可以创建Python服务端扩展（Server Extension）。服务端扩展在Jupyter Server进程中运行，可以：

- 注册自定义HTTP API端点
- 访问服务器文件系统
- 启动后台任务
- 提供静态文件服务
- 与Kernel通信

服务端扩展使用Tornado Web框架（Jupyter Server的底层框架）。

## 目录结构

server-extension示例使用了与前端扩展不同的Python包结构：

```
server-extension/
├── jupyterlab_examples_server/    # Python包
│   ├── __init__.py               # 入口点
│   ├── handlers.py               # API处理器
│   ├── labextension/             # 前端构建产物（jlpm install时填充）
│   │   └── package.json -> ../../
│   └── public/                   # 静态文件目录
│       └── index.html
├── pyproject.toml                # Python项目配置
└── setup.py                      # 兼容旧版pip
```

## 编写API处理器

handlers.py定义Tornado RequestHandler子类：

```python
import os
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from tornado.web import StaticFileHandler


class RouteHandler(APIHandler):
    # @tornado.web.authenticated 装饰器确保只有授权用户可以访问
    @tornado.web.authenticated
    def get(self):
        """GET /jupyterlab-examples-server/hello"""
        self.finish(json.dumps({
            "data": "This is /jupyterlab-examples-server/hello endpoint!"
        }))

    @tornado.web.authenticated
    def post(self):
        """POST /jupyterlab-examples-server/hello"""
        input_data = self.get_json_body()  # 解析JSON请求体
        data = {"greetings": "Hello {}, enjoy JupyterLab!".format(input_data["name"])}
        self.finish(json.dumps(data))


def setup_handlers(web_app):
    """注册路由到web_app"""
    host_pattern = ".*$"  # 允许所有主机

    base_url = web_app.settings["base_url"]  # JupyterHub兼容：加上base_url前缀

    # API路由
    route_pattern = url_path_join(base_url, "jupyterlab-examples-server", "hello")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # 静态文件路由
    doc_url = url_path_join(base_url, "jupyterlab-examples-server", "public")
    doc_dir = os.getenv(
        "JLAB_SERVER_EXAMPLE_STATIC_DIR",
        os.path.join(os.path.dirname(__file__), "public"),
    )
    handlers = [("{}/(.*)".format(doc_url), StaticFileHandler, {"path": doc_dir})]
    web_app.add_handlers(host_pattern, handlers)
```

### 关键点

1. **继承APIHandler**：使用 `from jupyter_server.base.handlers import APIHandler` 而非直接继承 `tornado.web.RequestHandler`
2. **@tornado.web.authenticated**：所有HTTP方法必须添加此装饰器，确保Jupyter认证
3. **base_url前缀**：使用 `url_path_join(base_url, ...)` 确保JupyterHub等环境下路由正确
4. **JSON响应**：使用 `self.finish(json.dumps(data))` 返回JSON
5. **JSON请求体**：POST方法使用 `self.get_json_body()` 解析请求体

## 注册服务端扩展

\_\_init\_\_.py实现Jupyter Server扩展的入口点：

```python
from .handlers import setup_handlers


def _jupyter_labextension_paths():
    """前端labextension路径声明（前后端一体化包）"""
    return [{
        "src": "labextension",
        "dest": "@jupyterlab-examples/server-extension"
    }]


def _jupyter_server_extension_points():
    """声明服务端扩展点"""
    return [{
        "module": "jupyterlab_examples_server"  # 本模块名
    }]


def _load_jupyter_server_extension(server_app):
    """Jupyter Server加载扩展时调用此函数

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    name = "jupyterlab_examples_server"
    server_app.log.info(f"Registered {name} server extension")
```

### 三个关键函数

| 函数 | 作用 | Jupyter版本 |
|------|------|-----------|
| `_jupyter_labextension_paths()` | 声明前端labextension静态文件路径 | JupyterLab 3+ |
| `_jupyter_server_extension_points()` | 声明这是一个Jupyter Server扩展 | Jupyter Server 2+ |
| `_load_jupyter_server_extension(server_app)` | 扩展加载时的初始化入口 | 所有版本 |

## pyproject.toml 配置

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab_examples_server"
version = "0.1.0"
dependencies = ["jupyter_server>=2.0.1"]

[tool.hatch.build.targets.sdist]
artifacts = ["jupyterlab_examples_server/labextension"]

[tool.hatch.build.targets.wheel]
artifacts = ["jupyterlab_examples_server/labextension"]

# Server extension discovery
[project.entry-points."jupyter_server.extension"]
jupyterlab-examples-server = "jupyterlab_examples_server"
```

关键配置：
- `jupyterlab>=4.0.0,<5`：构建时需要JupyterLab
- `jupyter_server>=2.0.1`：运行时依赖Jupyter Server 2+
- `project.entry-points."jupyter_server.extension"`：注册为Jupyter Server扩展入口点
- `artifacts`：确保构建时包含labextension静态文件

## 从前端调用API

在TypeScript中，通过ServerConnection调用服务端API：

```typescript
import { ServerConnection } from '@jupyterlab/services';

// 调用GET端点
const settings = ServerConnection.makeSettings();
const response = await ServerConnection.makeRequest(
  `${settings.baseUrl}jupyterlab-examples-server/hello`,
  { method: 'GET' },
  settings
);
const data = await response.json();
console.log(data.data);  // "This is /jupyterlab-examples-server/hello endpoint!"

// 调用POST端点
const postResponse = await ServerConnection.makeRequest(
  `${settings.baseUrl}jupyterlab-examples-server/hello`,
  {
    method: 'POST',
    body: JSON.stringify({ name: 'World' })
  },
  settings
);
const postData = await postResponse.json();
console.log(postData.greetings);  // "Hello World, enjoy JupyterLab!"
```

### ServerConnection 关键点

- `settings.baseUrl`：自动处理JupyterHub等代理环境的base URL
- `makeRequest(url, init, settings)`：与fetch API类似，但自动添加认证token
- 总是使用 `settings.baseUrl` 而非硬编码路径前缀

## 静态文件服务

handlers.py中还注册了静态文件路由：

```python
doc_dir = os.path.join(os.path.dirname(__file__), "public")
handlers = [("{}/(.*)".format(doc_url), StaticFileHandler, {"path": doc_dir})]
web_app.add_handlers(host_pattern, handlers)
```

这使得 `jupyterlab_examples_server/public/` 目录下的文件可以通过 `/jupyterlab-examples-server/public/<filename>` 访问。环境变量 `JLAB_SERVER_EXAMPLE_STATIC_DIR` 可覆盖路径（用于测试）。

## 开发模式安装

```bash
# 安装Python包（开发模式）
pip install -e .

# 安装前端依赖并构建
jlpm install
jlpm build

# 启用server extension
jupyter server extension enable jupyterlab_examples_server

# 启动JupyterLab
jupyter lab
```

启用后访问 `http://localhost:8888/jupyterlab-examples-server/hello` 应返回JSON。

## 其他服务端扩展模式

server-extension示例展示了最基础的API端点注册。其他示例演示了：

| 模式 | 示例 | 说明 |
|------|------|------|
| 基础API | server-extension | GET/POST端点 |
| 内容API | contentheader | 不包含服务端Python代码，仅前端 |
| 高级服务端 | — | 可集成数据库、外部API、定时任务 |

## 相关概念

- [项目结构与构建系统](02-project-setup.md)
- [插件基础与依赖注入](03-plugin-basics.md)
- [Kernel交互](11-kernel-interaction.md)
- [核心API与Token参考](../references/core-api-tokens.md)
