# JupyterHub 信源参考索引

本目录包含 JupyterHub v6.0.0b2 源码级参考文档，按核心模块组织，为概念文档提供事实溯源。

## 核心模块

| 参考 | 说明 |
|------|------|
| [app-source.md](app-source.md) | JupyterHub 主应用类：配置项、生命周期方法（init_db/init_hub/init_proxy/start）、CLI 入口 |
| [auth-source.md](auth-source.md) | Authenticator 基类及子类：方法签名、可配置 traitlets、认证状态管理 |
| [spawner-source.md](spawner-source.md) | Spawner 基类及 LocalProcessSpawner：生命周期方法、状态属性、资源配置 traitlets |
| [proxy-source.md](proxy-source.md) | Proxy 基类与 ConfigurableHTTPProxy：抽象方法、CHP 配置、路由数据格式 |
| [orm-source.md](orm-source.md) | ORM 数据模型：SQLAlchemy 实体类、列定义、关系映射、外键策略、自定义列类型 |

```{toctree}
:hidden:

app-source
auth-source
orm-source
proxy-source
spawner-source
```
