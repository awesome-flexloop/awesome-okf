---
type: concept
title: "Jupyter Surveys 简介"
description: "Jupyter Surveys项目是什么：Jupyter/IPython社区调查数据集仓库，收录2015-2023年6轮用户调查和可用性测试数据，附带MyST文档站点和分析notebooks。"
tags: ["jupyter", "surveys", "数据集", "CC0", "社区研究"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/README.md"
    lines: "1-47"
    description: "项目README"
  - resource: "../../../../../../external/libs/jupyter/surveys/LICENSE"
    description: "CC0许可证"
---

# Jupyter Surveys 简介

Jupyter Surveys 是Jupyter官方维护的**社区调查数据集仓库**，收集并公开了2015年至2023年间Jupyter/IPython社区开展的6轮用户调查和可用性测试数据。所有数据以**CC0 1.0 Universal**（公共领域贡献）发布，任何人可自由使用、分析和二次分发。

## 项目定位

Jupyter Surveys是一个**三位一体**的仓库：

| 角色 | 内容 |
|------|------|
| 📊 **数据集仓库** | 6个调查数据集，包含原始CSV、清洗后数据和编码结果 |
| 📓 **分析平台** | Jupyter Notebook格式的分析pipeline，支持Binder零配置运行 |
| 📖 **文档站点** | 使用MyST Markdown构建的文档站点，部署在GitHub Pages |

## 核心特性

- **开放数据**：CC0许可证，无使用限制
- **可复现分析**：Binder支持，点击即可在线运行所有分析notebooks
- **结构化文档**：MyST Markdown + GitHub Pages自动部署
- **标准化贡献**：统一的数据集组织规范和README模板
- **自动化构建**：Nox + GitHub Actions实现文档CI/CD

## 收录数据集一览

| 时间 | 名称 | 类型 | 主题 |
|------|------|------|------|
| 2015-12 | notebook-ux | 调查 | Notebook用户体验 |
| 2016-05 | education-survey | 调查 | Jupyter在教育中的使用 |
| 2018-09 | jupytercon-2018 | 用户测试 | JupyterCon现场可用性测试 |
| 2020-12 | jupyter-survey | 调查 | 年度社区调查 |
| 2022-08 | notebooks-for-all | 调查 | Notebook可访问性与包容性 |
| 2023-05 | jupyterlab-accessibility | 调查 | JupyterLab可访问性评估 |

## 谁应该使用这个仓库？

- **研究人员**：分析Jupyter用户行为、需求演变趋势
- **产品决策者**：基于社区反馈制定Jupyter生态发展方向
- **数据科学学习者**：学习真实调查数据的定性+定量分析方法
- **文档贡献者**：参考数据集贡献规范添加新的调查数据

## 下一步

- 🚀 [5分钟快速上手](01-getting-started.md)：三种方式开始使用
- 📁 [仓库结构](02-repository-structure.md)：了解目录布局
- 📚 [数据集目录](06-dataset-catalog.md)：浏览所有数据集详情
