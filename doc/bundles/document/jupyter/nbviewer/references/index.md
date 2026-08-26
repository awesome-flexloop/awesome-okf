# 源码信源索引

本目录包含 nbviewer 项目的源码信源文档，所有事实描述均可溯源至实际代码。分为两大部分：**nbviewer应用源码分析**和 **nbviewer.org-deploy部署运维源码分析**。

## 第一部分：nbviewer 应用信源

基于 nbviewer 主应用源码（`external/libs/jupyter/nbviewer/`）：

| 文档 | 覆盖范围 |
|------|---------|
| [应用主类源码](app-source.md) | nbviewer/app.py — NBViewer主应用类、traitlets配置体系、Tornado初始化、缓存/线程池/模板环境构建 |
| [Handlers源码分析](handlers-source.md) | handlers.py模块深度分析，包括BaseHandler、RenderingHandler类层次结构、缓存装饰器、错误处理和路由组装机制 |
| [Providers源码分析](providers-source.md) | Provider插件系统源码分析，包括Provider契约、动态加载机制、内置Provider实现和路由组装 |
| [渲染与缓存源码分析](render-cache-source.md) | render.py渲染管线和cache.py缓存后端源码深度分析，包括Notebook四阶段渲染流程、Exporter管理、三级缓存后端和分块压缩存储 |
| [客户端与工具源码分析](client-utils-source.md) | client.py、ratelimit.py、utils.py、log.py、formats.py模块深度分析，包括HTTP缓存客户端、限流计数器、工具函数、日志定制和输出格式定义 |

## 第二部分：nbviewer.org-deploy 部署信源

基于 nbviewer.org-deploy 部署仓库源码（`external/libs/jupyter/nbviewer.org-deploy/`）：

| 文档 | 覆盖范围 |
|------|---------|
| [项目元信息源码](project-meta-source.md) | README.md、pyproject.toml、requirements.txt、.gitattributes（git-crypt规则）、.pre-commit-config.yaml等项目元文件解析 |
| [部署配置文件源码](config-source.md) | config/nbviewer.yaml（Helm values公开配置）、config/cdn.yaml（空占位文件，不被deploy.sh使用）、secrets/目录（git-crypt加密密钥）、creds凭据文件、Helm values加载链路 |
| [CI/CD工作流源码](cicd-source.md) | GitHub Actions两个工作流：cd.yml（Helm部署流水线）和watch-dependencies.yaml（自动检查nbviewer更新）、update-nbviewer.py版本更新脚本、get-prs.py辅助脚本 |
| [Invoke任务源码](tasks-source.md) | tasks.py中FastlyService类和invoke任务的完整API解析：fastly CDN后端同步、trigger-build触发Docker构建、doitall全流程、upgrade未实现抛NotImplementedError |
| [Statuspage Sidecar源码](statuspage-source.md) | statuspage/目录：独立Dockerfile（python:3.7-alpine）和statuspage.py监控脚本，作为Kubernetes sidecar监控GitHub API速率限制并上报Statuspage.io |
| [测试源码解析](tests-source.md) | tests/test_nbviewer.py冒烟测试：BeautifulSoup解析首页、参数化链接检查、无conftest.py、无重试助手、pytest直接请求https://nbviewer.org |

```{toctree}
:maxdepth: 7

app-source
cicd-source
client-utils-source
config-source
handlers-source
project-meta-source
providers-source
render-cache-source
statuspage-source
tasks-source
tests-source
```
