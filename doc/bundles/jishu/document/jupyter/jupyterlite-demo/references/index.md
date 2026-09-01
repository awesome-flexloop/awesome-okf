---
type: Index
title: 信源参考索引
description: JupyterLite Demo 信源登记目录，包含5篇信源文档，所有派生文档均可追溯到原始源码
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
---

# JupyterLite Demo 信源参考

本文档目录包含 JupyterLite Demo 仓库学习的信源登记文件，每个文件对应仓库中一类核心配置或内容的详细登记。

## 信源文档列表

| 文档 | 对应源文件 | 核心内容 |
|------|-----------|----------|
| [仓库元信源](repo-readme.md) | README.md、LICENSE、目录结构 | 项目信息、版本、许可证、目录结构、核心文件清单 |
| [依赖配置信源](requirements-source.md) | requirements.txt | 所有 Python 依赖包版本、分类、用途、禁用扩展清单 |
| [站点配置信源](config-source.md) | repl/jupyter-lite.json | 配置文件结构、字段含义、可用配置项 |
| [部署流水线信源](deploy-workflow-source.md) | .github/workflows/deploy.yml | CI/CD 工作流、构建步骤、部署机制、Actions 版本 |
| [笔记本目录信源](notebook-catalog.md) | content/ 目录 | 所有示例笔记本的内容描述、依赖包、演示技能点 |

## 信源版本

所有信源基于 JupyterLite Demo 仓库（https://github.com/jupyterlite/demo），核心版本 jupyterlite-core==0.8.0。

```{toctree}
:hidden:
:maxdepth: 7

config-source
deploy-workflow-source
notebook-catalog
repo-readme
requirements-source
```
