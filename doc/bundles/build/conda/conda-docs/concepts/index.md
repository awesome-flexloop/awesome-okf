# 概念文档

conda-docs 知识包的概念文档，按学习路径排列：

## 入门

* [conda-docs 简介：Conda 文档门户](00-introduction.md) — 什么是 conda-docs、核心定位、技术栈概览

## 文档工程

* [文档门户架构：ReadTheDocs 多项目模式](01-doc-portal-arch.md) — 主项目+子项目架构、三种页面类型、隐藏 toctree 策略
* [Sphinx 构建系统配置详解](02-sphinx-config.md) — 扩展选型、主题定制、SEO、重定向、统计集成

## 用户视角

* [双发行版策略：Miniconda 与 Miniforge](03-installers.md) — 两个官方安装器对比、平台支持、Docker 镜像、选择建议
* [Conda 生态项目导航](04-ecosystem-projects.md) — 9个核心项目、文档编排层角色、互引模式、学习路径

## 社区参与

* [贡献指南与社区参与](05-contributing.md) — 贡献入口分类、文档/代码贡献流程、测试覆盖率要求、跨仓库路由
* [社区支持与帮助渠道](06-community-support.md) — 多渠道支持矩阵、排障指南、高效提问最佳实践
* [许可证与商业使用边界](07-license.md) — BSD 3-Clause 条款、生态组件许可证差异、商业合规要点

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-doc-portal-arch
02-sphinx-config
03-installers
04-ecosystem-projects
05-contributing
06-community-support
07-license
```
