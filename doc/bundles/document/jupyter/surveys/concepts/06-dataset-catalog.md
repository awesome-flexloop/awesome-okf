---
type: concept
title: "数据集目录"
description: "Jupyter Surveys收录的6个调查数据集的完整目录：时间、类型、主题、数据文件、分析资源和关键信息。"
tags: ["数据集", "目录", "调查", "用户测试", "jupytercon", "education", "accessibility"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys"
    description: "数据集根目录"
  - resource: "../../../../../../external/libs/jupyter/surveys/README.md"
    description: "项目README"
---

# 数据集目录

Jupyter Surveys共收录**6个**调查数据集，时间跨度从2015年到2023年。本文档提供每个数据集的基本信息、数据文件和分析资源索引。

---

## 2015-12: Notebook UX Survey

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2015-12-notebook-ux/` |
| **类型** | 在线调查 |
| **主题** | Jupyter Notebook用户体验 |
| **时间** | 2015年12月 |
| **数据格式** | CSV |
| **许可证** | CC0-1.0 |

### 数据文件

| 文件 | 说明 |
|------|------|
| `20160115235816-SurveyExport.csv` | 原始调查导出数据 |

### 关键信息

Jupyter项目早期的大规模用户体验调查，收集了用户对Notebook界面、功能和工作流的反馈。这是仓库中最早的数据集。

---

## 2016-05: Education Survey

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2016-05-education-survey/` |
| **类型** | 在线调查 |
| **主题** | Jupyter在教育中的使用 |
| **时间** | 2016年5月 |
| **数据格式** | CSV |
| **DOI** | 10.5281/zenodo.51701 |
| **许可证** | CC0-1.0 |

### 数据文件

| 文件 | 说明 |
|------|------|
| 教育场景使用数据CSV | 教学场景下的Jupyter使用情况 |

### 关键信息

专注于教育场景的调查，收集了教师和学生使用Jupyter进行教学和学习的反馈。是唯一拥有Zenodo DOI的数据集，适合学术引用。

---

## 2018-09: JupyterCon 2018 User Testing

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2018-09-jupytercon-2018/` |
| **类型** | 现场用户测试 |
| **主题** | JupyterLab可用性测试 |
| **时间** | 2018年9月（JupyterCon会议） |
| **数据格式** | CSV + Jupyter Notebooks |
| **许可证** | CC0-1.0 |

### 数据文件

| 文件 | 说明 |
|------|------|
| `notebooks/*.ipynb` | 分析notebooks |
| `notebooks/analysis_utils.py` | 分析工具函数 |
| `notebooks/user_testing_data.py` | 数据加载模块 |

### 关键信息

在JupyterCon 2018会议现场进行的可用性测试，参会者在监督下完成指定任务并提供反馈。这是仓库中**分析资源最丰富**的数据集，包含完整的Python分析pipeline（数据加载、清洗、编码、可视化）。

👉 参见：[调查分析Pipeline](05-survey-analysis-pipeline.md)和[分析工具函数解析](../references/analysis-utils-source.md)

---

## 2020-12: Jupyter Community Survey

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2020-12-jupyter-survey/` |
| **类型** | 在线调查 |
| **主题** | Jupyter生态年度社区调查 |
| **时间** | 2020年12月 |
| **数据格式** | CSV |
| **许可证** | CC0-1.0 |

### 关键信息

COVID-19疫情期间进行的大规模社区调查，覆盖Jupyter全生态（Notebook、JupyterLab、JupyterHub等）的用户体验和需求。

---

## 2022-08: Notebooks for All

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2022-08-notebooks-for-all/` |
| **类型** | 在线调查 |
| **主题** | Notebook可访问性与包容性 |
| **时间** | 2022年8月 |
| **数据格式** | CSV |
| **许可证** | CC0-1.0 |

### 关键信息

专注于Jupyter Notebook的可访问性（accessibility）调查，收集了残障用户和不同背景用户使用Notebook的体验反馈，为JupyterLab的可访问性改进提供数据支撑。

---

## 2023-05: JupyterLab Accessibility

| 属性 | 值 |
|------|-----|
| **目录** | `surveys/2023-05-jupyterlab-accessibility/` |
| **类型** | 在线调查 |
| **主题** | JupyterLab可访问性评估 |
| **时间** | 2023年5月 |
| **数据格式** | CSV + Markdown文档 |
| **许可证** | CC0-1.0 |

### 关键信息

针对JupyterLab界面的专项可访问性评估调查，是仓库中最新的数据集。与2022年的"Notebooks for All"形成时间序列对比，追踪可访问性改进效果。

---

## 数据集演变趋势

观察6个数据集的时间线，可以发现Jupyter社区调查的演变：

1. **2015-2016**：基础体验调查（"用户怎么用Notebook？"）
2. **2018**：从调查转向用户测试（"用户实际怎么操作？"）
3. **2020**：扩展到全生态调查
4. **2022-2023**：聚焦可访问性和包容性（"所有用户都能用吗？"）

这反映了Jupyter项目从"功能优先"到"体验优先"再到"包容性优先"的关注点演变。

## 如何选择数据集

| 分析目的 | 推荐数据集 |
|---------|-----------|
| 学习调查分析方法 | 2018 JupyterCon（有完整notebook） |
| 学术引用 | 2016 Education Survey（有DOI） |
| 时间趋势分析 | 对比2015→2020→2023 |
| 可访问性研究 | 2022 + 2023两个数据集 |
| 用户体验基准 | 2015 Notebook UX |

## 相关内容

- [数据集组织规范](03-dataset-conventions.md)：了解数据集目录的标准结构
- [贡献新数据集](08-contributing-data.md)：如何添加新的调查数据
- [运行分析Notebook](../examples/03-run-analysis-notebook.md)：运行2018数据集的分析pipeline
