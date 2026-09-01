---
okf_version: "0.2"
type: "concept"
title: "conda-docs 简介：Conda 文档门户"
sources:
  - README.md
  - docs/source/index.rst
---

# conda-docs 简介：Conda 文档门户

**conda-docs** 是 [Conda](https://conda.io/) 包与环境管理生态系统的**文档门户仓库**（documentation portal），托管于 GitHub [conda/conda-docs](https://github.com/conda/conda-docs)，构建后部署于 [docs.conda.io](https://docs.conda.io/)。

它不是 Conda 的完整用户手册，而是一个**着陆页和导航枢纽**——扮演 Conda 文档生态系统的"前门"角色。

## 核心定位

conda-docs 承担三个核心职责：

1. **统一入口**：为 docs.conda.io 提供首页，将用户引导到正确的子项目文档
2. **共通内容**：存放 conda 和 conda-build 共享的文档页面（贡献指南、帮助支持、许可证）
3. **项目导航**：展示 Conda 生态中的核心项目矩阵和安装选项

## 与源码仓库的关系

Conda 采用**"文档靠近代码"**的组织原则：

| 仓库 | 托管内容 | 部署位置 |
|------|---------|---------|
| conda/conda-docs | 门户首页、贡献指南、帮助支持、许可证 | docs.conda.io（主项目） |
| conda/conda | Conda CLI 用户指南、命令参考、开发者指南 | docs.conda.io/projects/conda |
| conda/conda-build | conda-build 包构建工具文档 | docs.conda.io/projects/conda-build |

这种架构通过 ReadTheDocs 的**多项目（subprojects）**功能实现：conda-docs 作为主项目（primary project），conda 和 conda-build 作为子项目。各项目文档保留在各自源码仓库中，与代码同版本维护，但在 docs.conda.io 统一域名下呈现。

## 仓库内容概览

```
conda-docs/
├── docs/source/
│   ├── _static/           # 自定义 CSS 和图片
│   ├── _templates/        # Jinja2 模板覆盖
│   ├── conf.py            # Sphinx 构建配置
│   ├── index.rst          # 首页（导航卡片+下载+项目矩阵）
│   ├── contributing.rst   # 贡献指南
│   ├── help-support.rst   # 社区支持与资源
│   ├── license.rst        # BSD 许可证
│   └── *.rst              # 重定向页面
├── requirements.txt       # Sphinx 构建依赖
├── .readthedocs.yml       # ReadTheDocs CI 配置
├── Makefile               # 本地构建命令
└── README.md
```

## 构建技术栈

- **文档引擎**：Sphinx + reStructuredText
- **主题**：conda_sphinx_theme（Anaconda 定制主题 0.4.0）
- **UI 组件**：sphinx-design 0.7.0（卡片、网格、标签页）
- **SEO**：sphinx-sitemap 2.9.0
- **重定向**：sphinx-reredirects 1.1.0
- **CI/CD**：ReadTheDocs（Ubuntu 24.04 + Python 3.14）

## 与 Conda 源码知识包的区别

awesome-okf-xs 中的 [conda](../../conda/concepts/00-introduction.md) 知识包基于 Conda **源码**深度分析生成，覆盖内部架构（七层模型、MatchSpec、Solver SAT算法、插件系统等）。本 conda-docs 知识包聚焦于**文档门户工程**——分析 conda-docs 如何通过 Sphinx + ReadTheDocs 构建开源项目文档门户，其知识可迁移到其他开源项目的文档站点搭建。

## 相关概念

- [文档门户架构：ReadTheDocs 多项目模式](01-doc-portal-arch.md)
- [Sphinx 构建系统配置详解](02-sphinx-config.md)
- [双发行版策略：Miniconda 与 Miniforge](03-installers.md)
- [Conda 生态项目矩阵](04-ecosystem-projects.md)
