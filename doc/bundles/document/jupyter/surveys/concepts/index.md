# 概念文档索引

本目录包含Jupyter Surveys的核心概念文档，按学习路径组织：

## 入门篇

- [00 - Jupyter Surveys 简介](00-introduction.md) — 项目是什么、核心内容、许可证、基本信息
- [01 - 5分钟快速上手](01-getting-started.md) — 在线浏览、Binder运行、本地克隆三种使用方式
- [02 - 仓库结构](02-repository-structure.md) — 目录树、各目录职责、关键文件说明

## 核心篇

- [03 - 数据集组织规范](03-dataset-conventions.md) — 命名约定、README结构、frontmatter、文件组织标准
- [04 - MyST文档系统](04-myst-docs-system.md) — mystmd CLI、配置文件、listing指令、book-theme主题
- [05 - 调查分析Pipeline](05-survey-analysis-pipeline.md) — 主题编码、用户测试分析、正则分类方法
- [06 - 数据集目录](06-dataset-catalog.md) — 6个调查数据集的详细信息、数据文件、分析资源

## 进阶篇

- [07 - CI/CD与GitHub Pages部署](07-cicd-deployment.md) — GitHub Actions工作流、BASE_URL配置、部署故障排查
- [08 - 贡献新数据集](08-contributing-data.md) — Fork→PR流程、README模板、匿名化检查清单
- [09 - Binder可复现性](09-binder-reproducibility.md) — Binder配置、依赖管理、零配置运行notebook

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-repository-structure
03-dataset-conventions
04-myst-docs-system
05-survey-analysis-pipeline
06-dataset-catalog
07-cicd-deployment
08-contributing-data
09-binder-reproducibility
```
