---
type: Wiki
title: JupyterLab Translate Wiki
description: JupyterLab国际化工具链的系统学习教程——从源码提取、翻译管理到编译打包
tags: [jupyterlab, i18n, translation, gettext, hatch, internationalization, l10n, po, pot, mo, jed, crowdin]
version: 1.3.7
project: jupyterlab-translate
source_repo: https://github.com/jupyterlab/jupyterlab-translate
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
---

# JupyterLab Translate Wiki

**jupyterlab-translate** 是 JupyterLab 生态系统的国际化工具链包，提供从源码字符串提取、翻译目录管理、翻译文件编译到构建时自动打包的完整流程，版本 1.3.7。

## 核心能力

- **多源字符串提取**：从 Python（Babel/pybabel）、TypeScript/TSX（gettext-extract）、JSON Schema（自定义选择器）三种源文件提取可翻译字符串
- **标准翻译格式**：基于 gettext 的 POT/PO 翻译工作流，支持 msgctxt 上下文消歧和复数形式
- **双端编译输出**：编译为 MO（Python后端gettext）和 Jed JSON（JupyterLab前端）两种格式
- **双模式分发**：支持独立扩展包自带翻译和集中式语言包仓库两种分发方式
- **构建集成**：通过 Hatch Build Hook 在构建时自动编译翻译文件
- **Crowdin集成**：自动从Crowdin下载翻译贡献者报告
- **运行时发现**：基于Python entry points机制的语言包自动发现

## 文档导航

### 📘 概念文档（12篇）

按学习路径从入门到进阶排列：

| 阶段 | 文档 |
|------|------|
| **入门** | [项目简介](/concepts/00-introduction.md) · [快速开始](/concepts/01-getting-started.md) · [架构总览](/concepts/02-architecture-overview.md) |
| **核心** | [CLI命令参考](/concepts/03-cli-commands.md) · [字符串提取流水线](/concepts/04-extraction-pipeline.md) · [翻译目录管理](/concepts/05-catalog-management.md) · [Jed JSON格式](/concepts/06-json-jed-format.md) · [Hatch构建钩子](/concepts/07-hatch-build-hook.md) · [运行时发现](/concepts/08-runtime-discovery.md) |
| **进阶** | [Schema选择器](/concepts/09-schema-i18n-selectors.md) · [Crowdin贡献者](/concepts/10-contributors-crowdin.md) · [双模式分发](/concepts/11-dual-mode-distribution.md) |

完整索引见 [概念文档索引](/concepts/index.md)。

### 🛠️ 示例文档（4篇）

| 示例 | 场景 |
|------|------|
| [扩展包国际化基础流程](/examples/01-basic-extension-i18n.md) | 从零为扩展添加i18n的6步完整流程 |
| [语言包仓库工作流](/examples/02-language-pack-workflow.md) | 维护集中式语言包仓库的批量处理和发布 |
| [自定义Schema选择器](/examples/03-custom-schema-selectors.md) | 提取非标准schema字段的翻译字符串 |
| [Hatch构建钩子配置](/examples/04-hatch-hook-integration.md) | pyproject.toml配置与构建验证 |

完整索引见 [示例文档索引](/examples/index.md)。

### 📋 信源登记（8篇）

源码到文档的映射登记，确保事实可溯源：

| 信源 | 模块 |
|------|------|
| [CLI命令源码](/references/cli-source.md) | `cli.py`（7个Click命令） |
| [API层源码](/references/api-source.md) | `api.py`（6个流程编排函数） |
| [核心工具源码](/references/utils-source.md) | `utils.py`（19个核心功能函数） |
| [格式转换源码](/references/converters-source.md) | `converters.py`（PO→JSON转换） |
| [运行时发现源码](/references/finder-source.md) | `finder.py`（entry points发现） |
| [Hatch钩子源码](/references/plugin-source.md) | `plugin.py`（构建时自动编译） |
| [贡献者模块源码](/references/contributors-source.md) | `contributors.py`（Crowdin API集成） |
| [常量与配置](/references/constants-config.md) | 版本号、依赖、翻译函数配置 |

完整索引见 [信源登记索引](/references/index.md)。

## 快速导航

```
jupyterlab-translate/
├── index.md                 ← 你在这里
├── concepts/                ← 概念文档
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   ├── 03-cli-commands.md
│   ├── 04-extraction-pipeline.md
│   ├── 05-catalog-management.md
│   ├── 06-json-jed-format.md
│   ├── 07-hatch-build-hook.md
│   ├── 08-runtime-discovery.md
│   ├── 09-schema-i18n-selectors.md
│   ├── 10-contributors-crowdin.md
│   └── 11-dual-mode-distribution.md
├── examples/                ← 实践示例
│   ├── index.md
│   ├── 01-basic-extension-i18n.md
│   ├── 02-language-pack-workflow.md
│   ├── 03-custom-schema-selectors.md
│   └── 04-hatch-hook-integration.md
└── references/              ← 信源登记
    ├── index.md
    ├── cli-source.md
    ├── api-source.md
    ├── utils-source.md
    ├── converters-source.md
    ├── finder-source.md
    ├── plugin-source.md
    ├── contributors-source.md
    └── constants-config.md
```

## 学习路径推荐

### 路径一：扩展开发者（为自己的扩展添加国际化）

1. [快速开始](/concepts/01-getting-started.md)
2. [字符串提取流水线](/concepts/04-extraction-pipeline.md)
3. [翻译目录管理](/concepts/05-catalog-management.md)
4. [扩展包国际化基础流程](/examples/01-basic-extension-i18n.md)
5. [Hatch构建钩子配置](/examples/04-hatch-hook-integration.md)
6. （可选）[自定义Schema选择器](/examples/03-custom-schema-selectors.md)

### 路径二：语言包维护者（维护某语言的翻译）

1. [项目简介](/concepts/00-introduction.md)
2. [CLI命令参考](/concepts/03-cli-commands.md)
3. [双模式分发机制](/concepts/11-dual-mode-distribution.md)
4. [翻译目录管理](/concepts/05-catalog-management.md)
5. [语言包仓库工作流](/examples/02-language-pack-workflow.md)
6. [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
7. （可选）[Crowdin贡献者集成](/concepts/10-contributors-crowdin.md)

### 路径三：深度理解源码

1. [架构总览](/concepts/02-architecture-overview.md)
2. 从[核心工具源码映射](/references/utils-source.md)开始，对照concepts深入各模块
3. [格式转换模块](/concepts/06-json-jed-format.md) / [converters源码](/references/converters-source.md)
4. [运行时发现机制](/concepts/08-runtime-discovery.md) / [finder源码](/references/finder-source.md)
5. [Hatch构建钩子](/concepts/07-hatch-build-hook.md) / [plugin源码](/references/plugin-source.md)

## 依赖环境

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | >=3.7 | 运行时 |
| Babel | >=2.10 | Python字符串提取、PO编译 |
| polib | >=1.1.0 | PO文件读写 |
| click | >=8.0 | CLI框架 |
| hatchling | >=1.4.0 | 构建后端 |
| jupyterlab | >=4.0,<5 | JupyterLab核心依赖 |
| json5 | >=0.9.0 | TSX/JSON5文件解析 |
| tomli | >=1.2.2; python<3.11 | pyproject.toml解析 |
| importlib-metadata | >=4.8.3; python<3.10 | entry points发现 |
| crowdin-api-client | >=0.16.0,<0.18.0; extra | Crowdin API集成 |
| copier | >=7.0.1; extra | 语言包模板生成 |
| nodejs | >=14,<=16 | TypeScript字符串提取（外部依赖） |
| gettext-extract | latest | TS/TSX字符串提取（npm包） |

## 相关资源

- [GitHub仓库](https://github.com/jupyterlab/jupyterlab-translate)
- [PyPI包](https://pypi.org/project/jupyterlab-translate/)
- [语言包仓库](https://github.com/jupyterlab/language-packs)
- [语言包Cookiecutter模板](https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter)
- [JupyterLab官方文档](https://jupyterlab.readthedocs.io/)
- [Crowdin翻译平台](https://crowdin.com/project/jupyterlab)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
