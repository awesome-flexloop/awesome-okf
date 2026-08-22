---
okf_version: "0.2"
type: example
title: "基础使用示例"
description: "通过代码示例学习 jupyterlab_server 的基本用法：启动服务、编程方式创建自定义Lab应用、使用配置项。"
tags: [basic, startup, custom-app, configuration, programming]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: app-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/app.py"
    title: "jupyterlab_server/app.py"
  - id: config-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/config.py"
    title: "jupyterlab_server/config.py"
---

# 基础使用示例

本文档提供 jupyterlab_server 的基础使用代码示例。

## 示例1：命令行启动

最简单的启动方式：

```bash
# 方式1：通过模块入口
python -m jupyterlab_server

# 方式2：通过 jupyter-server 扩展（推荐，会加载所有扩展）
jupyter server --ServerApp.jpserver_extensions="{'jupyterlab_server': True}"

# 方式3：指定端口和不打开浏览器
python -m jupyterlab_server --ServerApp.port=8889 --no-browser
```

## 示例2：自定义Lab应用

通过继承 LabServerApp 创建自定义JupyterLab应用：

```python
from jupyterlab_server import LabServerApp
import os

class MyCustomLabApp(LabServerApp):
    """自定义JupyterLab应用"""

    # 基本标识
    app_name = "My Data Science Lab"
    app_version = "1.0.0"
    app_url = "/dslab"           # 挂载到 /dslab 而非默认的 /lab
    default_url = "/dslab"       # 默认重定向URL

    # 静态资源路径（指向你的前端构建输出目录）
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    # 扩展路径
    extra_labextensions_path = [
        os.path.join(os.path.dirname(__file__), "extensions")
    ]

    # 页面配置钩子：自定义前端配置
    def page_config_hook(self, page_config):
        """修改传递给前端的配置"""
        page_config["myCustomSetting"] = "hello-world"
        page_config["dataSources"] = [
            {"name": "LocalDB", "url": "/api/data"}
        ]
        return page_config

if __name__ == "__main__":
    MyCustomLabApp.launch_instance()
```

## 示例3：编程方式启动服务器

```python
import asyncio
from jupyterlab_server import LabServerApp

async def start_lab():
    """异步启动Lab服务器"""
    app = LabServerApp()
    app.initialize()
    # 服务器现在在后台运行
    # 可以在这里执行其他操作
    await app.start()

# 同步方式
if __name__ == "__main__":
    LabServerApp.launch_instance(
        port=8888,
        open_browser=False,
        base_url="/"
    )
```

## 示例4：使用Python配置文件

创建 `jupyter_server_config.py`：

```python
# jupyter_server_config.py

c = get_config()  # noqa

# === LabServerApp 配置 ===
c.LabServerApp.app_url = "/lab"
c.LabServerApp.default_url = "/lab"

# 路径配置
c.LabServerApp.user_settings_dir = "/custom/path/user-settings"
c.LabServerApp.workspaces_dir = "/custom/path/workspaces"
c.LabServerApp.extra_labextensions_path = ["/opt/jupyter/extensions"]

# 行为配置
c.LabServerApp.cache_files = True
c.LabServerApp.notebook_starts_kernel = True
c.LabServerApp.copy_absolute_path = False

# 扩展黑白名单（不能同时设置）
c.LabServerApp.blocked_extensions_uris = ""
# 或白名单模式：
# c.LabServerApp.allowed_extensions_uris = "https://example.com/allowed.json"
c.LabServerApp.listings_refresh_seconds = 3600  # 1小时刷新

# === Jupyter Server 配置 ===
c.ServerApp.port = 8888
c.ServerApp.open_browser = True
c.ServerApp.token = ""  # 开发模式禁用token
c.ServerApp.password = ""
c.ServerApp.allow_origin = "*"
```

使用配置文件启动：

```bash
python -m jupyterlab_server --config=jupyter_server_config.py
```

## 示例5：在测试中使用LabServerApp

```python
import pytest
from jupyterlab_server import LabServerApp
from tornado.httpclient import AsyncHTTPClient

@pytest.fixture
async def lab_server(jp_serverapp):
    """启动Lab服务器的测试fixture"""
    lab = LabServerApp()
    lab.initialize()
    return lab

async def test_lab_page(lab_server, http_server_client):
    """测试Lab页面是否可访问"""
    response = await http_server_client.fetch("/lab")
    assert response.code == 200
    assert b"jupyter-config-data" in response.body
```

## 示例6：CLI工具使用

```bash
# 工作区管理
python -m jupyterlab_server.workspaces list
python -m jupyterlab_server.workspaces export default
python -m jupyterlab_server.workspaces import my-workspace.json

# 许可证报告
python -m jupyterlab_server.licenses --json > licenses.json
python -m jupyterlab_server.licenses --csv --bundles "@jupyterlab/.*" > licenses.csv
python -m jupyterlab_server.licenses --no-full-text > licenses.md
```
