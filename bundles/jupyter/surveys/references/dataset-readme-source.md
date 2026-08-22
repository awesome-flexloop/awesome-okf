---
type: Reference
title: "数据集README模板解析"
description: "各数据集README的frontmatter格式、章节结构、列定义表格规范、数据组织标准。"
tags: ["readme", "数据集", "frontmatter", "元数据", "文档规范"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2015-12-notebook-ux/index.md"
    description: "2015 Notebook UX数据集README"
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2016-05-education-survey/index.md"
    description: "2016教育调查数据集README"
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2023-05-jupyterlab-accessibility/index.md"
    description: "2023可访问性调查数据集README"
---

# 数据集README模板解析

## 概述

每个数据集目录下都有一个`index.md`（或README）文件，作为该数据集的入口文档。这些README遵循统一的结构：YAML frontmatter元数据 + 标准化章节。本文档解析这一模板规范。

## Frontmatter 元数据

```yaml
---
title: "Survey Name"
description: "Brief description of the survey dataset"
date: "YYYY-MM"
authors:
  - Author Name
data:
  format: csv
  files:
    - filename.csv
license: CC0-1.0
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 调查数据集的完整名称 |
| `description` | ✅ | 一句话描述调查目的和内容 |
| `date` | ✅ | 调查执行时间（YYYY-MM格式） |
| `authors` | ❌ | 调查实施者/分析者列表 |
| `data.format` | ✅ | 数据格式（csv/tsv/json等） |
| `data.files` | ✅ | 数据文件列表 |
| `license` | ✅ | 许可证（默认CC0-1.0） |

## 标准章节结构

### 1. 概述（Overview）

说明调查的背景、目的、目标受众和执行方式。

```markdown
## Overview

This survey was conducted to understand...
- **Target audience**: Jupyter Notebook users
- **Collection period**: December 2015
- **Responses**: N complete responses
- **Method**: Online survey (Google Forms/SurveyMonkey)
```

### 2. 数据文件（Data Files）

列出该数据集包含的所有数据文件及其用途：

```markdown
## Data Files

| File | Description | Rows |
|------|-------------|------|
| `responses.csv` | Raw survey responses | 1234 |
| `cleaned.csv` | Cleaned and anonymized data | 1200 |
| `codes.csv` | Thematic coding results | - |
```

### 3. 列定义（Column Definitions）

CSV数据文件中每个列的含义和取值范围：

```markdown
## Column Definitions

### responses.csv

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Anonymous respondent ID |
| `timestamp` | datetime | Response submission time |
| `q1_usage_freq` | categorical | Usage frequency: daily/weekly/monthly/rarely |
| `q2_feedback` | text | Open-ended feedback |
```

### 4. 分析资源（Analysis Resources）

指向分析notebooks和可视化资源：

```markdown
## Analysis

- 📓 [Analysis Notebook](analysis.ipynb) - Jupyter notebook with analysis
- 📊 [Summary Report](summary.md) - Key findings and visualizations
```

### 5. 引用（Citation）

如何在学术/研究工作中引用该数据集：

```markdown
## Citation

If you use this dataset, please cite:
> Author, A. (Year). Dataset Title [Data set]. Zenodo. https://doi.org/10.xxxx/zenodo.xxxxx
```

## 目录组织约定

```
surveys/YYYY-MM-topic-name/
├── index.md              # 本README（入口文档）
├── *.csv                 # 原始/清洗后的数据文件
├── notebooks/            # 分析notebooks（如有）
│   └── *.ipynb
├── images/               # 图表和可视化（如有）
│   └── *.png
└── summary.md            # 分析总结（如有）
```

## 匿名化规范

所有数据文件必须满足：
1. **移除个人标识**：姓名、邮箱、IP地址等PII必须移除
2. **时间戳泛化**：精确时间可保留，但需确认不与外部数据交叉识别
3. **自由文本审查**：开放回答中不包含可识别信息
4. **同意书**：原始调查中包含数据使用同意声明

## 相关概念

- [数据集组织规范](../concepts/03-dataset-conventions.md)：完整的数据集命名和组织规范
- [贡献新数据集](../examples/02-add-new-dataset.md)：添加新数据集的完整教程
- [数据集目录](../concepts/06-dataset-catalog.md)：现有6个数据集一览
