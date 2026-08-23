---
type: Reference
title: Jupyter 元包源码信源登记
description: jupyter/jupyter 仓库版本信息、源码路径、核心文件清单、文档结构索引
tags: [jupyter, metapackage, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T10:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-repo
    resource: https://github.com/jupyter/jupyter
    title: Jupyter Metapackage Repository
---

# Jupyter 元包源码信源登记

## 仓库基本信息

| 属性 | 值 |
|------|-----|
| 仓库 | [jupyter/jupyter](https://github.com/jupyter/jupyter) |
| 本地路径 | `external/libs/jupyter/jupyter/` |
| 版本 | 1.2.0.dev0 |
| 性质 | 元包（metapackage）+ 文档门户 |
| Python 源码模块 | 无（`py_modules = []`） |
| 许可协议 | BSD 3-Clause |
| Python 要求 | >= 3.6（支持至 3.13） |

## 核心文件清单

### 打包与发布

| 文件 | 说明 |
|------|------|
| `setup.py` | setuptools 打包配置，声明 5 个核心依赖 |
| `setup.cfg` | bdist_wheel 配置（universal=1） |
| `tbump.toml` | tbump 版本管理配置 |
| `noxfile.py` | nox 自动化任务（docs、docs-live） |
| `MANIFEST.in` | 源码分发包文件清单 |
| `.github/workflows/release.yaml` | GitHub Actions CI/CD（构建+发布到PyPI） |

### 文档结构（docs/source/）

| 路径 | 说明 |
|------|------|
| `conf.py` | Sphinx 构建配置（pydata_sphinx_theme + MyST） |
| `index.md` | 文档首页 |
| `what_is_jupyter.md` | Jupyter 核心概念介绍（REPL、Kernel、C/S架构） |
| `install.rst` | 安装指南与各子项目链接 |
| `running.rst` | 启动 Notebook Server |
| `glossary.rst` | 术语表 |
| `releases.rst` | 版本发布历史 |
| `use/jupyter-command.rst` | jupyter 命令参考 |
| `use/config.rst` | 通用配置系统 |
| `use/jupyter-directories.rst` | 目录与文件位置规范 |
| `use/using.rst` | 使用指南与选型决策图 |
| `projects/content-projects.rst` | 子项目分类导航 |
| `projects/architecture/content-architecture.rst` | 架构深度解析 |
| `projects/core.rst` | 核心构建块（jupyter_client、jupyter_core） |
| `projects/user-interfaces.rst` | 用户界面项目 |
| `projects/kernels.rst` | 内核（编程语言支持） |
| `projects/execution.rst` | 执行工具（nbclient） |
| `projects/deployment.rst` | 部署与基础设施 |
| `projects/conversion.rst` | 格式转换（nbconvert、nbformat） |
| `projects/ipython_projects.rst` | IPython 子项目 |
| `projects/incubator.rst` | 孵化器项目 |
| `projects/education.rst` | 教育项目 |
| `projects/doc-proj-categories.rst` | 文档项目分类索引 |
| `start/index.md` | Try Jupyter 入门页 |

### 元包依赖（install_requires）

| 包名 | 作用 |
|------|------|
| `notebook` | Jupyter Notebook Web 应用 |
| `nbconvert` | Notebook 格式转换工具 |
| `ipykernel` | IPython Jupyter 内核（Python 默认内核） |
| `ipywidgets` | 交互式小部件库 |
| `jupyterlab` | JupyterLab 下一代界面 |

### 文档构建依赖（doc-requirements.txt / environment.yml）

- Sphinx 文档引擎
- MyST Parser（Markdown 支持）
- pydata-sphinx-theme（主题）
- sphinx-autobuild（实时预览）
- sphinxext-rediraffe（重定向）
- sphinx-design（设计组件）
- intersphinx-registry（跨文档引用）
- graphviz（图表渲染）

## 关键版本历史节点

| 事件 | 时间 |
|------|------|
| IPython 诞生 | 2001 年 |
| The Big Split（IPython → Jupyter） | 2015 年（IPython 4.0） |
| JupyterLab 发布 | 2018 年（1.0） |
| Notebook v7（基于 JupyterLab） | 2023 年 |
| 当前元包版本 | 1.2.0.dev0 |
