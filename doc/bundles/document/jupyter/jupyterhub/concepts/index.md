# JupyterHub 概念文档索引

本目录包含 JupyterHub v6.0.0b2 的核心概念文档，建议按以下顺序阅读。

## 入门与架构

| 文档 | 说明 |
|------|------|
| [architecture-overview.md](architecture-overview.md) | JupyterHub 整体架构：五大核心模块、请求流程、关键设计模式 |

## 核心子系统

| 文档 | 说明 |
|------|------|
| [lifecycle.md](lifecycle.md) | 应用启动生命周期：10 阶段初始化流程、服务管理、优雅关闭 |
| [configuration.md](configuration.md) | traitlets 配置体系：配置加载顺序、六大配置类别、子类引用机制 |
| [authenticator.md](authenticator.md) | 认证系统：Authenticator 基类、内置认证器、认证流程、自定义扩展 |
| [spawner.md](spawner.md) | Spawner 机制：服务器生命周期管理、状态转换、资源配置、内置与第三方 Spawner |
| [proxy.md](proxy.md) | 代理系统：Proxy 抽象、ConfigurableHTTPProxy 实现、路由管理、并发控制 |
| [orm.md](orm.md) | ORM 数据模型：SQLAlchemy 实体（User/Server/Group/Role/Token 等）、关系映射 |
| [handlers.md](handlers.md) | HTTP 请求处理：BaseHandler、页面处理器、API 处理器、认证中间件 |

```{toctree}
:maxdepth: 7

architecture-overview
authenticator
configuration
handlers
lifecycle
orm
proxy
spawner
```
