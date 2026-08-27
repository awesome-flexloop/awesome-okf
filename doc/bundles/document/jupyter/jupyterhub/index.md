---
okf_version: "0.2"
type: Bundle
title: JupyterHub OKF Wiki
description: JupyterHub 多用户 Jupyter 服务器管理平台的完整知识文档，涵盖架构、认证、Spawner、代理、ORM 和扩展开发
---

# JupyterHub

JupyterHub 是 Jupyter 生态的多用户服务器管理平台，为每个用户启动独立的 Jupyter 服务器实例，支持可插拔的认证和服务器后端，广泛应用于教学、科研和企业团队协作场景。

**版本**：6.0.0b2  
**许可证**：BSD-3-Clause  
**仓库**：https://github.com/jupyterhub/jupyterhub  
**源码路径**：`external/libs/jupyter/jupyterhub/`

## 核心特性

- **多用户隔离**：为每个用户启动独立的单用户 Jupyter 服务器进程
- **可插拔认证**：支持 PAM、OAuth、LDAP、Dummy 等多种认证方式，可自定义 Authenticator
- **可插拔 Spawner**：支持本地进程、Docker、Kubernetes、SSH、HPC 等多种服务器后端
- **反向代理**：内置 ConfigurableHTTPProxy（node-http-proxy），支持自定义 Proxy 实现
- **RBAC 权限**：基于角色的访问控制，支持 OAuth 2.0 和 API Token
- **REST API**：完整的 RESTful API 支持用户/服务/代理管理
- **异步架构**：基于 Tornado 异步框架和 asyncio，支持高并发
- **traitlets 配置**：统一的配置体系，支持配置文件、命令行参数和环境变量

## 文档索引

### 概念文档（Concepts）

| 文档 | 说明 |
|------|------|
| [整体架构概览](concepts/architecture-overview.md) | 五大核心模块、请求流程、Mermaid 架构图与设计模式 |
| [应用启动生命周期](concepts/lifecycle.md) | 10 阶段初始化流程、服务管理、优雅关闭 |
| [配置系统](concepts/configuration.md) | traitlets 配置体系、六大配置类别、entry points 机制 |
| [认证系统](concepts/authenticator.md) | Authenticator 基类、内置认证器、认证流程、白名单与管理员 |
| [Spawner 机制](concepts/spawner.md) | 服务器生命周期、状态管理、资源配置、内置与第三方 Spawner |
| [代理系统](concepts/proxy.md) | Proxy 抽象、ConfigurableHTTPProxy、路由管理与并发控制 |
| [ORM 数据模型](concepts/orm.md) | SQLAlchemy 实体模型、关系映射、Token/OAuth/共享机制 |
| [HTTP 请求处理](concepts/handlers.md) | BaseHandler、页面处理器、REST API 处理器、认证中间件 |

### 实践示例（Examples）

| 文档 | 说明 |
|------|------|
| [快速入门](examples/quickstart.md) | 环境准备、默认启动、配置示例、常见问题排查 |
| [自定义 Authenticator](examples/custom-authenticator.md) | 自定义认证器开发、密码安全、auth_state 持久化 |
| [自定义 Spawner](examples/custom-spawner.md) | 自定义 Spawner 开发、SSH Spawner 示例、SSE 进度事件 |

### 源码参考（References）

| 文档 | 说明 |
|------|------|
| [Application 源码参考](references/app-source.md) | JupyterHub 主应用类、配置项、生命周期方法 |
| [Authenticator 源码参考](references/auth-source.md) | Authenticator 类层次、核心方法、可配置 traitlets |
| [Spawner 源码参考](references/spawner-source.md) | Spawner 基类、LocalProcessSpawner、状态与配置项 |
| [Proxy 源码参考](references/proxy-source.md) | Proxy 基类、ConfigurableHTTPProxy、路由格式 |
| [ORM 源码参考](references/orm-source.md) | SQLAlchemy 模型、列定义、关系映射 |

## 快速开始

1. 阅读[整体架构概览](concepts/architecture-overview.md)理解 JupyterHub 的核心设计
2. 按照[快速入门示例](examples/quickstart.md)启动第一个 JupyterHub 实例
3. 通过[认证系统](concepts/authenticator.md)和[Spawner 机制](concepts/spawner.md)理解核心扩展点
4. 参考[自定义 Authenticator](examples/custom-authenticator.md)或[自定义 Spawner](examples/custom-spawner.md)进行二次开发
5. 查阅[源码参考](references/index.md)获取精确的 API 签名和配置项

## 源码结构

```
jupyterhub/
├── app.py              # JupyterHub 主应用类（JupyterHub/Hub）
├── auth.py             # 认证器基类及内置实现
├── spawner.py          # Spawner 基类及 LocalProcessSpawner
├── proxy.py            # Proxy 基类及 ConfigurableHTTPProxy
├── orm.py              # SQLAlchemy ORM 数据模型
├── handlers/           # HTTP 请求处理器
│   ├── base.py         # BaseHandler 基类
│   ├── pages.py        # 页面处理器（登录/首页/管理等）
│   ├── login.py        # 登录/登出处理器
│   └── static.py       # 静态资源处理器
├── apihandlers/        # REST API 处理器
│   ├── users.py        # 用户管理 API
│   ├── proxy.py        # 代理路由 API
│   ├── services.py     # 服务管理 API
│   └── ...
├── roles.py            # RBAC 角色与权限
├── scopes.py           # 权限范围定义
├── oauth.py            # OAuth 2.0 提供方
└── metrics.py          # Prometheus 指标
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
