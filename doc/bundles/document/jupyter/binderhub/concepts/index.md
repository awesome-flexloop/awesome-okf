# 概念文档索引

本目录包含 BinderHub 项目的完整概念文档，覆盖应用架构、核心机制和部署配置。

## 入门篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [BinderHub简介](00-introduction.md) | 项目概述、核心功能、技术栈、项目结构 |
| 01 | [快速开始](01-getting-started.md) | 安装方式、pip安装、Helm部署、Docker本地运行、配置文件生成 |
| 02 | [架构概览](02-architecture-overview.md) | 六层架构模型、组件交互关系、请求生命周期详解 |

## 核心机制篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 03 | [BinderHub应用类与traitlets配置](03-app-and-traitlets.md) | BinderHub主类结构、traitlets配置体系、Tornado路由初始化、核心组件构建 |
| 04 | [构建系统](04-build-system.md) | BuildExecutor/KubernetesBuildExecutor、Pod提交与管理、日志流、安全上下文、资源限制 |
| 05 | [RepoProvider插件系统](05-repo-provider-system.md) | RepoProvider基类契约、九大内置Provider详解、spec解析与ref解析、banned/allowed_specs |
| 06 | [SSE事件流与状态机](06-event-stream.md) | Server-Sent Events协议、BuildHandler事件流、构建/启动状态机、keepalive机制、build_token验证 |
| 07 | [Docker Registry集成](07-registry-integration.md) | DockerRegistry类层次、Bearer Token认证流程、镜像manifest查询、GCR/ExternalRegistry扩展 |
| 08 | [Launcher与JupyterHub集成](08-launcher-and-jupyterhub.md) | Launcher类、临时用户创建、服务器启动SSE进度流、指数退避重试、pre_launch_hook、named server支持 |
| 09 | [健康检查、配额与限流](09-health-quota-ratelimit.md) | HealthHandler装饰器链（retry/at_most_every/false_if_raises）、KubernetesLaunchQuota Pod计数、RateLimiter固定窗口算法 |
| 10 | [事件日志与Prometheus指标](10-event-logging-metrics.md) | EventLog JSON Schema事件注册与发射、Prometheus指标定义（BUILD_TIME/LAUNCH_TIME/BUILD_COUNT等） |
| 11 | [Helm Chart部署](11-helm-deployment.md) | Helm Chart结构、values.yaml配置解析、binderhub_config.py动态加载、BinderSpawnerMixin |
| 12 | [安全认证与构建令牌](12-security-auth.md) | JWT build_token机制（HS256/aud/exp/origin）、HubOAuth认证、IP黑名单网络检查、CORS配置、User-Agent Bot拦截 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-app-and-traitlets
04-build-system
05-repo-provider-system
06-event-stream
07-registry-integration
08-launcher-and-jupyterhub
09-health-quota-ratelimit
10-event-logging-metrics
11-helm-deployment
12-security-auth
```
