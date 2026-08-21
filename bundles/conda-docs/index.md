---
okf_version: "0.2"
---

# Conda 文档门户知识库

本知识包是 [Conda Documentation Portal](https://docs.conda.io/)（conda-docs 仓库，BSD-3-Clause 许可证）的系统化中文教程，基于 conda-docs Sphinx 文档站点源码深度分析生成，覆盖文档门户架构、Sphinx 构建配置、多项目文档组织、贡献指南与社区支持等完整知识体系。内容溯源至 conda-docs 仓库的 Sphinx 配置、RST 源文件和 ReadTheDocs CI 配置，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门篇（concepts/）

* [conda-docs 简介：Conda 文档门户](concepts/00-introduction.md) — 文档门户定位、核心职责、与源码仓库的关系、技术栈概览。
* [文档门户架构：ReadTheDocs 多项目模式](concepts/01-doc-portal-arch.md) — 主项目+子项目架构、三种页面类型、隐藏 toctree 策略、reredirects 跳转机制。
* [Sphinx 构建系统配置详解](concepts/02-sphinx-config.md) — 扩展选型（sphinx-design、sphinx-reredirects 等）、主题定制、SEO、重定向、统计集成。

## 用户与生态篇（concepts/）

* [双发行版策略：Miniconda 与 Miniforge](concepts/03-installers.md) — Miniconda vs Miniforge 对比、安装命令、Docker 镜像、许可证差异、选择建议。
* [Conda 生态项目导航](concepts/04-ecosystem-projects.md) — 9个核心项目矩阵（conda/conda-build/menuinst/conda-libmamba-solver/grayskull/constructor等）、文档编排层角色、学习路径。

## 社区与合规篇（concepts/）

* [贡献指南与社区参与](concepts/05-contributing.md) — 贡献入口分类、文档/代码贡献流程、测试覆盖率要求、跨仓库路由。
* [社区支持与帮助渠道](concepts/06-community-support.md) — 多渠道支持矩阵（Discourse/GitHub/Element/Stack Overflow）、排障指南、高效提问最佳实践。
* [许可证与商业使用边界](concepts/07-license.md) — BSD 3-Clause 条款、生态组件许可证差异、defaults vs conda-forge 商业合规要点。

## 实战示例（examples/）

* [本地构建 conda-docs 文档](examples/local-build.md) — 从零克隆仓库到本地构建 HTML 文档的完整步骤，含常见问题排查和 sphinx-autobuild 开发模式。
* [搭建类 conda-docs 的多项目文档门户](examples/doc-portal-template.md) — 可复用的 Sphinx+ReadTheDocs 多项目文档门户模板，含 conf.py、requirements.txt、.readthedocs.yml、首页 RST 模板和品牌 CSS。

## 信源登记簿（references/）

* [Sphinx 配置文件 conf.py 源码解析](references/conf-py.md) — 扩展列表、主题配置、重定向规则、ReadTheDocs 集成配置源码。
* [首页文件 index.rst 结构解析](references/index-rst.md) — 导航卡片、下载按钮、项目矩阵、隐藏 toctree 结构源码。
* [贡献指南 contributing.rst 源码解析](references/contributing-rst.md) — Issue 路由、开发环境、CLA 签署流程源码。
* [帮助支持页面 help-support.rst 源码解析](references/help-support-rst.md) — 社区渠道列表、付费支持信息、排障链接源码。

## 信任与生命周期说明

* **内容来源**：全部 14 个内容文档（8 个概念 + 2 个示例 + 4 个信源登记）均基于对 `external/libs/conda-dev/conda-docs/` 仓库的 Sphinx 配置（`docs/source/conf.py`）、RST 源文件（`docs/source/*.rst`、`docs/source/user/`、`docs/source/developer/`、`docs/source/community/`）、CI 配置（`.readthedocs.yml`）和项目元数据（`README.md`、`LICENSE`、`CONTRIBUTING.md`）的逐文件阅读与事实提取生成。
* **知识定位**：本知识包聚焦于**文档门户工程**——分析 conda-docs 如何通过 Sphinx + ReadTheDocs 构建多项目聚合文档站点，其知识可迁移到其他开源项目的文档站点搭建。关于 Conda 包管理器本身的内部架构（MatchSpec、Solver、插件系统等），请参阅 [conda 知识包](../conda/concepts/00-introduction.md)。
* **stale_after 解释**：文档门户架构（Sphinx+RTD+多项目模式）变化频率较低；Sphinx 扩展版本和主题配置可能随时间更新，但核心架构模式稳定。建议在 conda-docs 仓库有重大架构变更（如迁移到 MkDocs、或 ReadTheDocs 配置格式大版本升级）时重新评估。

本知识包共收录 14 个内容文档（8 个概念 + 2 个示例 + 4 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
