---
type: OKF
title: litegitpuller 教程
description: litegitpuller 是一个 JupyterLab/JupyterLite 扩展，通过 URL 参数自动从 GitHub 或 GitLab 拉取仓库内容到浏览器文件系统，适用于教学分发和JupyterLite场景。
tags: [litegitpuller, jupyterlab, jupyterlite, extension, git, github, gitlab, nbgitpuller]
version: 0.3.0
source: https://github.com/jupyterlite/litegitpuller
okf_version: "0.2"
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:58:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# litegitpuller 教程

litegitpuller 是一个 JupyterLab（>=4.0.0）扩展，通过 URL 查询参数自动从 GitHub 或 GitLab 拉取公开仓库内容到 JupyterLab/JupyterLite 的文件浏览器中。它完全在浏览器端通过 REST API 获取文件，无需服务端 git 命令，特别适合 JupyterLite 静态部署场景。

litegitpuller 的设计灵感来自 [nbgitpuller](https://github.com/jupyterhub/nbgitpuller)，参数格式与其兼容，并能自动检测 nbgitpuller 的存在以避免冲突。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门**
- [00-简介](concepts/00-introduction.md) — 什么是 litegitpuller、核心特性、与 nbgitpuller 区别
- [01-安装与快速开始](concepts/01-getting-started.md) — 安装方法、URL 参数基础、第一个示例

**核心**
- [02-整体架构](concepts/02-architecture.md) — 三层架构、模板方法模式、数据流向
- [03-GitPuller抽象基类](concepts/03-gitpuller-base.md) — clone流程、目录创建、文件上传、错误处理
- [04-平台Puller实现](concepts/04-platform-pullers.md) — GithubPuller/GitlabPuller API差异
- [05-扩展插件机制](concepts/05-extension-plugin.md) — 插件结构、激活流程、冲突检测

**高级**
- [06-URL参数完整参考](concepts/06-url-parameters.md) — 所有参数详解、编码规则
- [07-限制与注意事项](concepts/07-limitations.md) — 速率限制、文件冲突、不支持特性
- [08-自定义Provider](concepts/08-custom-provider.md) — 扩展新Git平台支持

### [实践示例](examples/index.md)
- [01-GitHub仓库拉取](examples/01-basic-github.md) — 最简GitHub拉取示例
- [02-GitLab仓库拉取](examples/02-gitlab-repo.md) — GitLab（含自建）拉取示例
- [03-自动打开Notebook](examples/03-open-notebook.md) — 一键打开教程Notebook
- [04-自定义上传路径](examples/04-custom-uploadpath.md) — 按目录组织仓库内容

### [信源参考](references/index.md)
- [插件入口源码](references/index-ts-source.md) — src/index.ts 源码信源
- [Git拉取核心源码](references/gitpuller-ts-source.md) — src/gitpuller.ts 源码信源
- [Python包源码](references/python-package-source.md) — Python包结构信源
- [构建配置源码](references/build-config-source.md) — pyproject.toml/package.json 信源

### 分析过程文档
- [事实清单](facts.md) — R阶段采集的零推测事实（66条）
- [架构洞察](insights.md) — I阶段提炼的5个核心洞察与知识地图

## 🚀 快速开始

### 安装

```bash
pip install litegitpuller
```

### 最简使用

在 JupyterLab URL 后附加 `repo` 参数：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo
```

即可自动拉取 `brichet/testing-repo` 仓库的 main 分支到文件浏览器中。

### URL 参数一览

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `repo` | ✅ | - | 仓库完整URL |
| `branch` | ❌ | `main` | 分支名 |
| `provider` | ❌ | `github` | `github` 或 `gitlab` |
| `urlpath` | ❌ | - | 拉取后自动打开的文件路径 |
| `uploadpath` | ❌ | `/` | 仓库存放目录 |

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 纯前端拉取 | 浏览器端REST API，无需服务端git |
| 🔗 URL驱动 | 零UI设计，所有配置通过URL参数 |
| 🤝 自动避让 | 检测nbgitpuller时自动禁用 |
| 📂 自动打开 | 拉取完成后自动打开指定Notebook |
| 🏗️ 可扩展 | 模板方法模式，轻松添加新平台 |
| ⚠️ 错误报告 | 控制台输出跳过文件和错误信息 |

## 📖 推荐学习路径

1. **快速上手**：阅读[00-简介](concepts/00-introduction.md)和[01-安装与快速开始](concepts/01-getting-started.md)，动手试[01-GitHub示例](examples/01-basic-github.md)
2. **理解原理**：学习[02-整体架构](concepts/02-architecture.md)和[03-GitPuller基类](concepts/03-gitpuller-base.md)
3. **掌握参数**：阅读[06-URL参数参考](concepts/06-url-parameters.md)，尝试[03-自动打开Notebook](examples/03-open-notebook.md)
4. **了解边界**：阅读[07-限制与注意事项](concepts/07-limitations.md)
5. **扩展开发**：学习[08-自定义Provider](concepts/08-custom-provider.md)添加新平台

## ⚠️ 重要限制

- GitHub未认证API限制为**每小时60个文件请求**，仅适合小型教程仓库（≤30个文件）
- 不支持私有仓库、Git LFS、Git历史记录
- 已存在的文件不会被覆盖或更新，只跳过
- 无UI进度提示，需通过浏览器控制台查看日志

## 📊 架构概览

```
URL参数 → activate() → Provider选择 → Puller.clone()
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              GitHub/GitLab API    JupyterLab Contents   FileBrowser
              (获取文件树/内容)    (创建目录)          (上传文件)
                                        │
                                        ▼
                              filebrowser:open-path（自动打开文件）
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
