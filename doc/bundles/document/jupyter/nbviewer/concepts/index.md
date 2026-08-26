# 概念文档索引

本目录包含 nbviewer 项目的完整概念文档，分为两大部分：**nbviewer应用**（应用架构和内部机制）和 **nbviewer.org-deploy部署运维**（生产环境部署和运维）。

## 第一部分：nbviewer 应用文档

以下文档基于 nbviewer 主应用源码（`external/libs/jupyter/nbviewer/nbviewer/`）分析生成，覆盖应用内部架构和机制。

### 入门篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [nbviewer简介](00-introduction.md) | 项目概述、核心功能、技术栈、项目结构和请求处理流程 |
| 01 | [快速开始](01-getting-started.md) | 安装方式、命令行参数、配置文件、环境变量和Docker部署入门 |
| 02 | [架构概览](02-architecture-overview.md) | 五层架构模型、关键设计洞察、组件关系和请求生命周期详解 |

### 核心机制篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 03 | [应用类与traitlets配置](03-app-and-traitlets.md) | NBViewer应用类结构、traitlets配置系统、Handler类替换机制、cached_property组件和启动流程 |
| 04 | [Handler继承体系](04-handler-hierarchy.md) | Handler类层次结构、BaseHandler核心功能、RenderingHandler模板方法、@cached装饰器和顶级Handlers |
| 05 | [Provider插件系统](05-provider-plugin-system.md) | Provider契约、动态加载机制、内置Provider详解和路由组装顺序 |
| 06 | [Notebook渲染管线](06-render-pipeline.md) | Notebook从JSON到HTML的四阶段渲染流程、render_notebook核心函数、格式系统和错误处理 |
| 07 | [缓存系统](07-caching-system.md) | 三级缓存后端、分块压缩存储、页面缓存机制、HTTP客户端缓存和限流计数器 |
| 08 | [URI重写机制](08-uri-rewrite.md) | transform_ipynb_uri正则替换管道、默认重写顺序、各Provider重写规则和扩展方式 |
| 09 | [输出格式系统](09-format-system.md) | 格式字典字段定义、三种内置格式（html/slides/script）、format_handlers路由复制和运行时格式过滤 |
| 10 | [GitHub客户端](10-github-client.md) | AsyncGitHubClient认证机制、API方法封装、速率限制日志监控和GitHub Enterprise支持 |
| 11 | [速率限制与安全机制](11-rate-limit-security.md) | RateLimiter的IP+UA限流算法、缓存后端复用、CSP策略、本地文件安全检查和目录遍历防护 |
| 12 | [自定义Provider扩展](12-custom-provider.md) | 开发自定义Provider的完整步骤、Provider契约、Handler继承模式和URI重写规则注册 |
| 13 | [部署指南](13-deployment.md) | nbviewer生产部署方案、Docker部署、进程/线程池配置、反向代理、Memcached缓存和环境变量参考 |

## 第二部分：nbviewer.org-deploy 部署运维文档

以下文档基于 nbviewer.org-deploy 部署仓库源码（`external/libs/jupyter/nbviewer.org-deploy/`）分析生成，覆盖生产环境的Helm部署、CI/CD、CDN管理和运维操作。

### 架构与配置篇

| 编号 | 文档 | 内容 |
|------|------|------|
| D3 | [部署配置详解](03-deployment-config.md) | Helm values完整解析、config/cdn.yaml空文件说明、secrets加密配置、statuspage sidecar配置 |
| D4 | [CI/CD与自动化](04-cicd-and-automation.md) | GitHub Actions两个工作流：cd.yml部署流水线、watch-dependencies.yaml自动更新、pre-commit和Dependabot |
| D5 | [版本更新机制](05-version-update.md) | 双位置版本号（cd.yml和config/nbviewer.yaml）、update-nbviewer.py自动检测、watch-dependencies每日开PR |

### 运维操作篇

| 编号 | 文档 | 内容 |
|------|------|------|
| D6 | [Helm部署流程](06-helm-deploy-process.md) | deploy.sh完整解析：KUBECONFIG设置、helm dep up、CI/本地双模式、helm diff、--cleanup-on-fail、kubectl rollout status |
| D7 | [Fastly CDN管理](07-fastly-cdn.md) | FastlyService类API、fastly任务同步逻辑、all_instances()硬编码IP、copy-backend模式、无lock/unlock任务 |
| D8 | [测试与密钥管理](08-testing-and-secrets.md) | 冒烟测试（test_nbviewer.py + BeautifulSoup）、git-crypt加密模式、statuspage sidecar监控、密钥文件清单 |

> **注意**：部署运维文档编号（D3-D8）与应用文档编号存在重叠，通过文件名后缀区分（如 `03-app-and-traitlets.md` vs `03-deployment-config.md`）。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-app-and-traitlets
03-deployment-config
04-cicd-and-automation
04-handler-hierarchy
05-provider-plugin-system
05-version-update
06-helm-deploy-process
06-render-pipeline
07-caching-system
07-fastly-cdn
08-testing-and-secrets
08-uri-rewrite
09-format-system
10-github-client
11-rate-limit-security
12-custom-provider
13-deployment
```
