# 概念文档索引

本目录包含 xeus-lite-demo 的核心概念文档，按照从入门到进阶的学习路径排列。

## 入门概念

| 文档 | 说明 |
|------|------|
| [00-xeus-lite-demo 简介](00-introduction.md) | 项目是什么、解决什么问题、核心特性一览 |
| [01-xeus 与 JupyterLite 生态](01-xeus-jupyterlite.md) | xeus、JupyterLite、emscripten-forge 之间的关系 |
| [02-双环境模型](02-dual-environment.md) | 构建环境 vs 运行时环境，两个 yml 文件的区别 |

## 部署与配置

| 文档 | 说明 |
|------|------|
| [03-GitHub 模板三步部署](03-github-template-deploy.md) | 三步创建自己的 JupyterLite 站点 |
| [04-运行时环境配置](04-runtime-env-config.md) | environment.yml 配置、channels、dependencies 详解 |
| [05-构建环境配置](05-build-env-config.md) | build-environment.yml 配置、插件安装 |
| [06-CI/CD 流水线](06-cicd-pipeline.md) | GitHub Actions 工作流详解 |

## 进阶主题

| 文档 | 说明 |
|------|------|
| [07-多语言内核支持](07-kernel-options.md) | Python/R/C++/Lua 内核配置与选择指南 |
| [08-内容目录与 Notebook](08-content-and-notebooks.md) | content/ 目录管理、Notebook 和数据文件组织 |

```{toctree}
:hidden:

00-introduction
01-xeus-jupyterlite
02-dual-environment
03-github-template-deploy
04-runtime-env-config
05-build-env-config
06-cicd-pipeline
07-kernel-options
08-content-and-notebooks
```
