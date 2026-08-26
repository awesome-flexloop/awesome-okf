# 源码信源索引

本目录包含 BinderHub 项目的源码信源文档，所有事实描述均可溯源至实际代码。

| 文档 | 覆盖范围 |
|------|---------|
| [BinderHub应用主类源码](app-source.md) | binderhub/app.py — BinderHub主应用类（Application子类）、traitlets配置体系、Tornado路由初始化、核心组件构建 |
| [构建执行器源码](build-source.md) | binderhub/build.py — BuildExecutor/KubernetesBuildExecutor类、ProgressEvent枚举、Pod提交与管理、日志流、KubernetesCleaner |
| [BuildHandler源码](builder-source.md) | binderhub/builder.py — BuildHandler核心SSE处理器、构建/启动流程编排、Prometheus指标定义 |
| [RepoProvider源码](repoproviders-source.md) | binderhub/repoproviders.py — RepoProvider基类契约、九大内置Provider（GitHub/GitLab/Gist/Git/Zenodo/Figshare/Dataverse/Hydroshare/CKAN） |
| [Launcher源码](launcher-source.md) | binderhub/launcher.py — Launcher类、JupyterHub API交互、临时用户创建、server启动SSE进度监听 |
| [Docker Registry源码](registry-source.md) | binderhub/registry.py — DockerRegistry及子类（GoogleArtifactRegistry/FakeRegistry/ExternalRegistryHelper）、Bearer Token认证 |
| [BaseHandler与Handlers源码](base-handlers-source.md) | binderhub/base.py、binderhub/main.py、binderhub/handlers/repoproviders.py — Handler基类、UI处理器、配置端点 |
| [健康/配额/限流/指标源码](health-quota-ratelimit-source.md) | binderhub/health.py、binderhub/quota.py、binderhub/ratelimit.py、binderhub/metrics.py、binderhub/events.py、binderhub/utils.py |
| [Helm Chart配置源码](helm-config-source.md) | helm-chart/binderhub/ — values.yaml、binderhub_config.py、deployment/rbac/service/ingress/pdb模板、BinderSpawnerMixin |

```{toctree}
:hidden:
:maxdepth: 7

app-source
base-handlers-source
build-source
builder-source
health-quota-ratelimit-source
helm-config-source
launcher-source
registry-source
repoproviders-source
```
