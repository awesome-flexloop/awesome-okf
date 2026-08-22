---
okf_version: "0.2"
type: concept
title: "5分钟快速上手"
description: "安装 jupyterlab_server、启动服务、理解核心配置和使用设置/工作区API的快速入门指南。"
tags: [getting-started, installation, quickstart, configuration, api]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/pyproject.toml"
    title: "pyproject.toml"
  - id: app-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/app.py"
    title: "jupyterlab_server/app.py"
---

# 5分钟快速上手

## 安装

jupyterlab_server 通常作为 JupyterLab 的依赖自动安装，也可以独立安装：

```bash
pip install jupyterlab_server
```

安装后，jupyterlab_server 作为 Jupyter Server 的扩展自动注册。验证安装：

```bash
# 通过 jupyter-server 扩展列表查看
jupyter server extension list

# 或直接查看版本
python -c "import jupyterlab_server; print(jupyterlab_server.__version__)"
# 输出: 2.28.0
```

## 启动服务

jupyterlab_server 通过 Jupyter Server 启动。最简单的方式是直接运行：

```bash
python -m jupyterlab_server
```

或通过 Jupyter Server 启动（jupyterlab_server 作为扩展自动加载）：

```bash
jupyter lab
```

启动后，访问 `http://localhost:8888/lab` 即可看到 JupyterLab 界面。LabServerApp 的默认 `default_url` 为 `/lab`。

## 核心配置项

LabServerApp 继承自 LabConfig，所有配置可通过命令行或配置文件设置：

### 基本路径配置

```python
# jupyter_server_config.py
c.LabServerApp.app_url = "/lab"                    # 应用根URL（默认/lab）
c.LabServerApp.static_dir = "/path/to/static"      # 静态文件目录
c.LabServerApp.templates_dir = "/path/to/templates" # Jinja2模板目录
c.LabServerApp.app_settings_dir = "/path/to/settings"  # 应用设置目录
c.LabServerApp.schemas_dir = "/path/to/schemas"    # JSON Schema目录
c.LabServerApp.user_settings_dir = "/path/to/user-settings"  # 用户设置目录
c.LabServerApp.workspaces_dir = "/path/to/workspaces"  # 工作区目录
c.LabServerApp.themes_dir = "/path/to/themes"      # 主题目录
```

### 扩展配置

```python
c.LabServerApp.labextensions_path = ["/path/to/extensions"]     # 联邦扩展路径
c.LabServerApp.extra_labextensions_path = ["/extra/extensions"]  # 额外扩展路径
c.LabServerApp.blocked_extensions_uris = "https://example.com/blocked.json"  # 屏蔽扩展列表URI
c.LabServerApp.listings_refresh_seconds = 3600  # 列表刷新间隔（秒）
```

### 行为配置

```python
c.LabServerApp.cache_files = True                # 是否缓存静态文件（开发模式下设False）
c.LabServerApp.notebook_starts_kernel = True     # 打开Notebook时自动启动内核
c.LabServerApp.copy_absolute_path = False        # 复制路径时是否使用绝对路径
```

## REST API 快速体验

启动服务后，可以通过 REST API 与 jupyterlab_server 交互：

### 获取所有设置

```bash
curl -s http://localhost:8888/lab/api/settings/ | python -m json.tool
```

返回格式：
```json
{
  "settings": [
    {
      "id": "@jupyterlab/apputils-extension:themes",
      "schema": { ... },
      "version": "3.0.0",
      "raw": "{}",
      "settings": {},
      "last_modified": "2024-01-01T00:00:00",
      "created": "2024-01-01T00:00:00"
    }
  ]
}
```

### 保存设置

```bash
curl -X PUT http://localhost:8888/lab/api/settings/@jupyterlab/apputils-extension:themes \
  -H "Content-Type: application/json" \
  -d '{"raw": "{\"theme\": \"JupyterLab Dark\"}"}'
```

### 列出工作区

```bash
curl -s http://localhost:8888/lab/api/workspaces/ | python -m json.tool
```

### 保存工作区

```bash
curl -X PUT http://localhost:8888/lab/api/workspaces/my-workspace \
  -H "Content-Type: application/json" \
  -d '{"data": {"layout-restorer": {...}}, "metadata": {"id": "/my-workspace"}}'
```

### 获取语言包列表

```bash
curl -s http://localhost:8888/lab/api/translations/ | python -m json.tool
```

## CLI 工具

### 工作区管理

```bash
# 列出所有工作区
python -m jupyterlab_server.workspaces list

# 导出工作区（默认导出default工作区）
python -m jupyterlab_server.workspaces export
python -m jupyterlab_server.workspaces export my-workspace

# 导入工作区
python -m jupyterlab_server.workspaces import workspace.json
python -m jupyterlab_server.workspaces import workspace.json --name renamed-workspace
```

### 许可证报告

```bash
# Markdown格式报告
python -m jupyterlab_server.licenses

# JSON格式
python -m jupyterlab_server.licenses --json

# CSV格式，指定bundle
python -m jupyterlab_server.licenses --csv --bundles "@jupyterlab/.*"
```

## 编程方式使用

```python
from jupyterlab_server import LabServerApp

# 创建自定义Lab应用
class MyLabApp(LabServerApp):
    app_name = "My JupyterLab App"
    app_version = "1.0.0"
    static_dir = "/path/to/my/static"

if __name__ == "__main__":
    MyLabApp.launch_instance()
```

---

**下一步阅读：**
- [架构总览](02-architecture-overview.md) — 理解模块分层和请求流程
- [应用与配置](03-app-and-config.md) — 深入 LabServerApp 和配置系统
