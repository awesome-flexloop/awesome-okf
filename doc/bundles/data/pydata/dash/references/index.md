# 信源登记簿

本目录包含 Dash 源码中关键模块的源码摘录与分析，所有概念文档的 `sources` 字段指向本目录。

| 信源 | 对应源码文件 | 说明 |
|------|-------------|------|
| [Dash应用初始化](dash-app-init.md) | `dash/dash.py`、`dash/backends/__init__.py`、`dash/_configs.py`、`dash/_get_app.py`、`dash/_callback.py`、`dash/dependencies.py` | Dash类__init__流程、多后端选择（Flask/FastAPI/Quart）、layout设置、callback注册机制、配置系统与应用上下文 |

```{toctree}
:hidden:

dash-app-init
```
