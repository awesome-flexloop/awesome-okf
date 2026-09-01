---
type: bundle
okf_version: "0.2"
title: "nbviewer — Jupyter Notebook在线查看器完整文档"
description: "nbviewer项目完整知识体系：应用架构（Tornado+nbconvert+Provider插件系统）与nbviewer.org-deploy生产部署运维（Helm+Kubernetes+Fastly CDN+GitHub Actions CI/CD）"
tags: [jupyter, nbviewer, tornado, nbconvert, helm, kubernetes, fastly, cdn, ci-cd, git-crypt, ovh, provider-plugin]
bundle_name: "nbviewer"
version: "1.0"
language: zh-CN
license: CC-BY-4.0
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: nbviewer-repo
    title: "nbviewer GitHub（应用源码）"
    uri: "https://github.com/jupyter/nbviewer"
  - id: nbviewer-source
    resource: "../../../../../external/libs/jupyter/nbviewer"
    title: "nbviewer 源码目录"
  - id: deploy-repo
    title: "nbviewer.org-deploy GitHub（部署仓库）"
    uri: "https://github.com/jupyter/nbviewer.org-deploy"
  - id: deploy-source
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy"
    title: "nbviewer.org-deploy 源码目录"
---

# nbviewer — Jupyter Notebook在线查看器

> [nbviewer](https://nbviewer.org) 是 Jupyter 官方提供的 Notebook 在线查看服务。本文档覆盖 nbviewer **应用本身**的架构原理和 **nbviewer.org-deploy** 生产环境部署运维两大主题。

## 文档总览

本Bundle包含两个源码仓库的分析文档：

| 主题 | 源码仓库 | 文档数量 |
|------|---------|---------|
| [nbviewer应用](#一nbviewer-应用文档) | [jupyter/nbviewer](https://github.com/jupyter/nbviewer) | 14篇概念 + 4篇示例 + 5篇信源 |
| [nbviewer.org-deploy部署运维](#二nbviewerorg-deploy-部署运维文档) | [jupyter/nbviewer.org-deploy](https://github.com/jupyter/nbviewer.org-deploy) | 6篇概念 + 3篇示例 + 6篇信源 |

---

## 一、nbviewer 应用文档

> 基于 `external/libs/jupyter/nbviewer/` 源码分析生成

nbviewer 是基于 Tornado 的异步 Web 服务，将存储在 GitHub、Gist、URL 或本地文件系统中的 Jupyter Notebook（.ipynb）渲染为可交互 HTML 页面。

### 核心特性

- ✅ **多源Notebook获取**：GitHub、Gist、HTTP URL、本地文件系统
- ✅ **多格式输出**：HTML（默认）、Reveal.js幻灯片、可执行脚本
- ✅ **Provider插件系统**：通过`default_handlers()`+`uri_rewrites()`契约扩展数据源
- ✅ **多级缓存**：页面缓存（Memcached/内存）+ HTTP客户端缓存（ETag/Last-Modified）+ 并发去重
- ✅ **线程/进程池隔离**：CPU密集的nbconvert渲染与Tornado事件循环隔离
- ✅ **URI重写管道**：自动识别并转换各种URL格式为内部路由
- ✅ **IP+UA速率限制**：防止API滥用

### 应用技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Web框架 | Tornado | 异步HTTP服务器 |
| Notebook渲染 | nbconvert | Jupyter Notebook转换引擎 |
| 配置系统 | traitlets | Jupyter生态标准配置框架 |
| 模板引擎 | Jinja2 | HTML页面模板 |
| 缓存后端 | Memcached / 内存 | 页面缓存和限流计数 |
| HTTP客户端 | pycurl (CurlAsyncHTTPClient) | 高性能异步HTTP请求 |

### 应用概念文档

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [nbviewer简介](concepts/00-introduction.md) | 项目概述、核心功能、技术栈、项目结构 |
| 01 | [快速开始](concepts/01-getting-started.md) | 安装方式、命令行参数、配置文件、Docker入门 |
| 02 | [架构概览](concepts/02-architecture-overview.md) | 五层架构模型、关键设计洞察、请求生命周期 |
| 03 | [应用类与traitlets配置](concepts/03-app-and-traitlets.md) | NBViewer应用类、traitlets配置、启动流程 |
| 04 | [Handler继承体系](concepts/04-handler-hierarchy.md) | BaseHandler、RenderingHandler、@cached装饰器 |
| 05 | [Provider插件系统](concepts/05-provider-plugin-system.md) | Provider契约、动态加载、内置Provider详解 |
| 06 | [Notebook渲染管线](concepts/06-render-pipeline.md) | 四阶段渲染流程、render_notebook核心函数 |
| 07 | [缓存系统](concepts/07-caching-system.md) | 三级缓存后端、分块压缩、动态TTL |
| 08 | [URI重写机制](concepts/08-uri-rewrite.md) | transform_ipynb_uri正则替换管道 |
| 09 | [输出格式系统](concepts/09-format-system.md) | html/slides/script格式、format_handlers路由复制 |
| 10 | [GitHub客户端](concepts/10-github-client.md) | AsyncGitHubClient认证、API封装、速率监控 |
| 11 | [速率限制与安全](concepts/11-rate-limit-security.md) | IP+UA限流、CSP策略、本地文件安全 |
| 12 | [自定义Provider扩展](concepts/12-custom-provider.md) | 自定义Provider开发完整步骤 |
| 13 | [部署指南](concepts/13-deployment.md) | Docker部署、Nginx反向代理、性能调优 |

### 应用示例文档

| 示例 | 内容 |
|------|------|
| [基本配置示例](examples/01-basic-config.md) | 端口、缓存、限流、GitHub认证配置 |
| [本地文件服务配置](examples/02-local-files.md) | 本地Notebook文件服务配置 |
| [自定义Provider开发](examples/03-custom-provider.md) | 从零开发自定义Provider |
| [Docker部署示例](examples/04-docker-deploy.md) | Docker和docker-compose部署 |

### 应用信源文档

| 信源 | 覆盖范围 |
|------|---------|
| [应用主类源码](references/app-source.md) | app.py — NBViewer主应用类、traitlets配置 |
| [Handlers源码](references/handlers-source.md) | handlers.py — BaseHandler、RenderingHandler类层次 |
| [Providers源码](references/providers-source.md) | Provider插件系统契约和内置实现 |
| [渲染与缓存源码](references/render-cache-source.md) | render.py渲染管线、cache.py三级缓存 |
| [客户端与工具源码](references/client-utils-source.md) | client.py、ratelimit.py、utils.py、log.py、formats.py |

---

## 二、nbviewer.org-deploy 部署运维文档

> 基于 `external/libs/jupyter/nbviewer.org-deploy/` 源码分析生成

nbviewer.org-deploy 是 nbviewer.org 生产环境的 Helm + Kubernetes 部署仓库，负责将 nbviewer 应用部署到 OVHCloud Kubernetes 集群，并管理 Fastly CDN、自动化版本更新和线上监控。

### 部署架构

```
用户 → Cloudflare DNS → Fastly CDN → OVH Kubernetes (3副本nbviewer + Memcached + statuspage sidecar)
                                    ↑
              GitHub Actions CI/CD ──┘ (自动部署 + 冒烟测试)
```

| 组件 | 技术 | 说明 |
|------|------|------|
| 编排 | Helm v3.12.0 | Chart在nbviewer主仓库中（本地checkout） |
| 集群 | OVHCloud Kubernetes | namespace: nbviewer, 3副本 |
| CI/CD | GitHub Actions | ubuntu-24.04, Python 3.13, kubectl v1.29.15 |
| CDN | Fastly | API管理，copy-backend模式，硬编码后端IP |
| DNS | Cloudflare | cdn.jupyter.org（手动管理） |
| 加密 | git-crypt | secrets/、creds、env_*文件透明加密 |
| 监控 | Statuspage.io | GitHub API速率上报（statuspage sidecar，2分钟间隔） |
| 缓存 | Memcached | 1600MB内存限制 |

### 重要事实澄清（基于源码验证）

| 常见误解 | 源码事实 |
|---------|---------|
| deploy.sh生成helm-values.deploy.yaml合并文件 | ❌ 不生成，直接使用`-f config/nbviewer.yaml -f secrets/config/nbviewer.yaml` |
| deploy.sh使用GITHUB_REF_NAME | ❌ 不使用Git引用，版本号在cd.yml和config/nbviewer.yaml中 |
| deploy.sh部署后自动同步CDN | ❌ 不执行CDN同步，需手动`invoke fastly` |
| tasks.py有lock-cdn/unlock-cdn任务 | ❌ 不存在，只有fastly/trigger-build/doitall/upgrade |
| invoke upgrade可用于部署 | ❌ upgrade()抛NotImplementedError |
| tasks.py有SERVICE_ID等硬编码常量 | ❌ 凭据从creds文件读取，仅后端IP硬编码 |
| tests/有conftest.py和多个测试文件 | ❌ 只有test_nbviewer.py一个测试文件 |
| 测试有指数退避重试助手 | ❌ 无重试机制，单次HTTP请求 |
| statuspage是Helm Chart的一部分 | ❌ statuspage/是独立目录，有自己的Dockerfile |
| config/cdn.yaml包含CDN配置 | ❌ 文件为空，不被deploy.sh使用 |

### 部署运维概念文档

| 编号 | 文档 | 内容 |
|------|------|------|
| D3 | [部署配置详解](concepts/03-deployment-config.md) | Helm values解析、空cdn.yaml、secrets加密、statuspage配置 |
| D4 | [CI/CD与自动化](concepts/04-cicd-and-automation.md) | GitHub Actions部署流水线、自动更新、pre-commit、Dependabot |
| D5 | [版本更新机制](concepts/05-version-update.md) | 双位置版本号、update-nbviewer.py、自动更新PR流程 |
| D6 | [Helm部署流程](concepts/06-helm-deploy-process.md) | deploy.sh逐行解析、CI/本地双模式、--cleanup-on-fail |
| D7 | [Fastly CDN管理](concepts/07-fastly-cdn.md) | FastlyService类API、fastly任务、硬编码IP、copy-backend模式 |
| D8 | [测试与密钥管理](concepts/08-testing-and-secrets.md) | 冒烟测试、BeautifulSoup解析、git-crypt加密、statuspage sidecar |

> **注意**：部署运维文档编号（D3-D8）与应用文档编号（03-08）存在重叠，通过文件名后缀区分（如`03-app-and-traitlets.md` vs `03-deployment-config.md`）。详见 [概念文档索引](concepts/index.md)。

### 部署运维示例文档

| 示例 | 内容 |
|------|------|
| [使用Invoke任务管理CDN](examples/invoke-tasks.md) | invoke fastly同步CDN、trigger-build触发构建、排错指南 |
| [本地部署调试](examples/local-debug.md) | deploy.sh本地运行、helm diff预览、回滚操作 |
| [手动升级nbviewer版本](examples/manual-upgrade.md) | update-nbviewer.py使用、版本号编辑、PR创建、部署验证 |

### 部署运维信源文档

| 信源 | 覆盖范围 |
|------|---------|
| [项目元信息](references/project-meta-source.md) | README、pyproject.toml、依赖、git-crypt规则 |
| [部署配置文件](references/config-source.md) | config/nbviewer.yaml、空cdn.yaml、secrets目录、creds凭据 |
| [CI/CD工作流](references/cicd-source.md) | cd.yml、watch-dependencies.yaml、update-nbviewer.py |
| [Invoke任务](references/tasks-source.md) | FastlyService类、all_instances()硬编码IP、可用/不可用任务 |
| [Statuspage Sidecar](references/statuspage-source.md) | statuspage/目录、Dockerfile、GitHub速率监控脚本 |
| [测试源码](references/tests-source.md) | test_nbviewer.py冒烟测试、BeautifulSoup解析 |

---

## 运维命令速查

### nbviewer 应用（本地开发/运行）

```bash
pip install nbviewer
python -m nbviewer                           # 默认启动
python -m nbviewer --port=8080 --processes=4  # 生产配置
python -m nbviewer --generate-config          # 生成配置文件
docker run -p 8080:8080 jupyter/nbviewer      # Docker运行
```

### nbviewer.org-deploy（生产部署）

```bash
# 部署
bash deploy.sh                     # 本地模式（helm diff预览+确认）
CI=true bash deploy.sh             # CI模式（直接部署）

# CDN管理
invoke fastly                      # 同步Fastly后端
invoke trigger-build               # 触发Docker Hub构建

# 测试
pytest                             # 运行线上冒烟测试

# 版本更新
python3 scripts/update-nbviewer.py # 检查并更新版本号

# Kubernetes运维
kubectl get pods -l app=nbviewer
kubectl rollout status -w deployment/nbviewer
helm history nbviewer
helm rollback nbviewer <REVISION>
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
