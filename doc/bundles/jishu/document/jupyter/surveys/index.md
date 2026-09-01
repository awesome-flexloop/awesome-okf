---
okf_version: "0.2"
title: "Jupyter Surveys"
description: "Jupyter/IPython社区调查数据集仓库系统教程：数据集组织规范、MyST文档构建、定性定量分析Pipeline、Binder可复现环境、CI/CD部署。"
---

# Jupyter Surveys

> Jupyter/IPython社区调查数据集与分析资源仓库。收录2015-2023年6轮用户调查和可用性测试数据，包含原始CSV、Jupyter Notebook分析pipeline和MyST文档站点。本知识包从仓库源码出发，系统讲解数据集组织规范、文档构建方法和调查分析方法论。

## 快速导航

### [核心概念](concepts/index.md)

10篇概念文档，从入门到进阶系统讲解Jupyter Surveys：

- **入门**：[简介](concepts/00-introduction.md) → [5分钟上手](concepts/01-getting-started.md) → [仓库结构](concepts/02-repository-structure.md)
- **核心**：[数据集组织规范](concepts/03-dataset-conventions.md) · [MyST文档系统](concepts/04-myst-docs-system.md) · [调查分析Pipeline](concepts/05-survey-analysis-pipeline.md) · [数据集目录](concepts/06-dataset-catalog.md)
- **进阶**：[CI/CD部署](concepts/07-cicd-deployment.md) · [贡献新数据集](concepts/08-contributing-data.md) · [Binder可复现性](concepts/09-binder-reproducibility.md)

### [实战示例](examples/index.md)

3个可独立操作的实战示例：

- [本地构建文档](examples/01-build-docs-locally.md)
- [添加新数据集](examples/02-add-new-dataset.md)
- [运行分析Notebook](examples/03-run-analysis-notebook.md)

### [源码信源](references/index.md)

5个关键文件的源码解析文档，为概念文档中的溯源引用提供目标。

## 版本信息

| 属性 | 值 |
|------|-----|
| 仓库 | jupyter/surveys |
| 仓库地址 | https://github.com/jupyter/surveys |
| 文档站点 | https://jupyter.github.io/surveys |
| 默认许可证 | CC0 1.0 Universal |
| 文档构建 | MyST Markdown (mystmd) |
| 构建自动化 | Nox + GitHub Actions |
| Binder支持 | 是 (mybinder.org) |
| 收录数据集 | 6个（2015-2023） |
| 最早数据 | 2015年12月 |
| 源码路径 | `external/libs/jupyter/surveys/` |

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
