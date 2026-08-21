---
okf_version: "0.2"
type: "concept"
title: "Conda 生态项目导航"
sources:
  - README.md
  - docs/source/index.rst
  - docs/source/ecosystem.rst
---

# Conda 生态项目导航

Conda 文档门户是整个 Conda 生态系统的入口，通过 ReadTheDocs 多项目（subproject）机制将各独立项目文档聚合到统一域名 `docs.conda.io` 下。本概念梳理生态中的核心项目及其职责边界。

## 核心项目矩阵

| 项目 | 仓库 | 文档地址 | 职责 |
|---|---|---|---|
| **conda** | conda/conda | `/projects/conda/` | 核心包与环境管理器（CLI、SAT求解器、跨平台包管理） |
| **conda-build** | conda/conda-build | `/projects/conda-build/` | 包构建工具（recipe 编译、打包、上传到频道） |
| **conda-docs** | conda/conda-docs | `/`（门户本身） | 文档门户入口、安装指南、贡献指南、社区支持 |
| **menuinst** | conda/menuinst | `/projects/menuinst/` | 跨平台应用菜单快捷方式生成 |
| **conda-libmamba-solver** | conda/conda-libmamba-solver | `/projects/conda-libmamba-solver/` | libmamba 加速求解器插件 |
| **grayskull** | conda/grayskull | `/projects/grayskull/` | Recipe 自动生成工具（从 PyPI/Cran 生成 conda recipe） |
| **constructor** | conda/constructor | `/projects/constructor/` | 自定义安装器构建工具（创建类 Miniconda 的发行版） |
| **conda-smithy** | conda-forge/conda-smithy | conda-forge 文档 | conda-forge feedstock 管理工具 |
| **bioconda-utils** | bioconda/bioconda-utils | bioconda 文档 | 生物信息学频道工具链 |

## 文档门户的编排角色

conda-docs 在生态中承担**文档编排层**角色：

```
┌─────────────────────────────────────────────┐
│            docs.conda.io（门户）             │
│  ┌───────────────────────────────────────┐  │
│  │  conda-docs（本仓库）                  │  │
│  │  - 统一品牌/导航栏                     │  │
│  │  - 安装入口/贡献指南/社区支持           │  │
│  │  - 子项目聚合导航                      │  │
│  └───────────────────────────────────────┘  │
│         ↓ reredirects          ↓ subprojects│
│  ┌─────────────┐  ┌──────────────┐  ┌────┐  │
│  │ conda 文档   │  │conda-build   │  │... │  │
│  │（独立构建）  │  │（独立构建）   │  │    │  │
│  └─────────────┘  └──────────────┘  └────┘  │
└─────────────────────────────────────────────┘
```

- **非代码仓库**：conda-docs 本身不包含 Conda 功能代码，仅承载文档
- **导航枢纽**：顶部导航栏和首页卡片将用户导向正确的子项目文档
- **共享资源**：贡献指南、社区/Discourse 链接、品牌元素在门户层统一维护

## 子项目文档互引模式

子项目通过 `intersphinx` 机制实现交叉引用：
- conda 的文档可以引用 conda-build 的配置项
- conda-build 的文档可以链接回 conda 的安装指南
- 所有子项目共享门户的品牌主题 `conda_sphinx_theme`

> 📌 **学习路径建议**：入门用户从 conda-docs 门户 → conda 用户指南；开发者从 conda-docs 贡献指南 → conda/conda-build 源码；打包者关注 conda-build + grayskull + constructor。
