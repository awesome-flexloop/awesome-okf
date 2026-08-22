---
type: concept
title: "调查分析Pipeline"
description: "Jupyter Surveys调查数据分析方法论：定性主题编码、定量统计、正则辅助分类、用户测试数据分析、pandas清洗Pipeline。"
tags: ["数据分析", "定性分析", "主题编码", "pandas", "用户测试", "正则"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/analysis_utils.py"
    description: "分析工具函数"
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/user_testing_data.py"
    description: "用户测试数据处理"
---

# 调查分析Pipeline

Jupyter Surveys仓库中的调查数据分析采用**定性+定量混合方法**，核心是主题编码（thematic coding）结合pandas数据处理Pipeline。本文档介绍这套分析方法论。

## 分析方法论概述

Jupyter社区调查主要包含两类数据：

| 数据类型 | 分析方法 | 典型问题 |
|---------|---------|---------|
| **结构化数据**（选择题、Likert量表） | 定量统计（频次、交叉分析） | "多少用户每天使用Notebook？" |
| **非结构化数据**（开放文本反馈） | 定性主题编码 | "用户最常抱怨的问题是什么？" |
| **用户测试数据**（操作日志、屏幕录制） | 任务完成率+行为模式分析 | "用户在哪里卡住了？" |

## 定性主题编码流程

### 第一步：开放编码（Open Coding）

两名独立编码者阅读所有自由文本回答，为每条回答分配描述性标签：

```python
# 示例：开放编码过程
# 原始回答："The notebook keeps freezing when I run large cells"
# 编码标签：performance, freezing, large-cells
```

### 第二步：编码共识（Coding Alignment）

两名编码者讨论标签差异，合并相似标签，建立统一的编码手册（codebook）：

| 最终代码 | 包含的原始标签 | 说明 |
|---------|--------------|------|
| performance | slow, lag, freeze, crash, hanging | 性能相关问题 |
| usability | confusing, hard, unclear, difficult | 可用性问题 |
| feature_request | wish, would like, need, add | 功能需求 |
| praise | love, great, awesome, easy | 正面反馈 |

### 第三步：轴向编码（Axial Coding）

将代码归类为更高级别的主题，识别主题间的关系。例如：
- **性能** + **大单元格** → 大数据集场景的性能瓶颈
- **可用性** + **扩展管理** → 扩展发现和安装困难

## 定量分析Pipeline

### 数据加载与清洗

```python
import pandas as pd
from analysis_utils import dt, cleaner, classify_feedback

# 1. 加载数据
df = pd.read_csv('survey_responses.csv')

# 2. 时间戳转换（JS毫秒→Python datetime）
df['timestamp'] = df['timestamp'].apply(dt)

# 3. 清洗：移除测试数据、空反馈
df = cleaner(df)

# 4. 自动分类（正则辅助）
df['category'] = df['feedback'].apply(classify_feedback)
```

完整工具函数见：[分析工具函数源码解析](../references/analysis-utils-source.md)

### 频次统计

```python
# 选择题统计
usage_counts = df['q1_usage_freq'].value_counts(normalize=True) * 100

# 编码类别统计
category_counts = df['category'].value_counts()

# 时间趋势（按月统计）
df['month'] = df['timestamp'].dt.to_period('M')
monthly_counts = df.groupby('month').size()
```

### 交叉分析

```python
# 使用频率 × 满意度交叉表
cross = pd.crosstab(df['q1_usage_freq'], df['q3_satisfaction'])
```

## 正则辅助分类

为提高编码效率，使用正则表达式进行**初步自动分类**，作为人工编码的辅助：

```python
CATEGORIES = {
    'performance': r'slow|lag|freeze|crash|hang',
    'usability': r'confus|hard|unclear|difficult',
    'feature_request': r'wish|would like|need|add|feature',
    'praise': r'love|great|awesome|easy|helpful',
}

def classify_feedback(text):
    import re
    for category, pattern in CATEGORIES.items():
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return 'other'
```

**重要**：正则分类只是辅助，最终编码必须经过人工验证。自动分类的准确率约为70-80%，主要用于快速排序和识别高频主题。

## 用户测试数据分析

2018年JupyterCon数据集包含用户测试（usability testing）数据，分析方法略有不同：

### Dropzone编码

用户在测试界面中的拖拽操作记录为dropzone序列，编码为工作流类型：

```python
def encode_dropzone(sequence):
    """将拖拽序列编码为工作流类别"""
    if 'notebook' in sequence and 'terminal' in sequence:
        return 'mixed_workflow'      # 混合使用Notebook和终端
    if 'notebook' in sequence:
        return 'notebook_focused'    # 专注于Notebook
    if 'file_browser' in sequence:
        return 'file_navigation'     # 文件导航频繁
    return 'other'
```

### 任务完成度量

| 指标 | 计算方式 |
|------|---------|
| 任务完成率 | 成功完成任务的用户比例 |
| 任务完成时间 | task_end - task_start |
| 错误次数 | 偏离成功路径的操作次数 |
| 帮助请求次数 | 用户请求提示的次数 |

## Notebook分析结构

仓库中的分析notebooks遵循统一结构：

```
notebooks/
├── 01-data-exploration.ipynb    # 数据加载、基本统计、分布概览
├── 02-qualitative-coding.ipynb  # 主题编码过程和结果
├── 03-quantitative-analysis.ipynb # 统计分析、交叉表、可视化
└── 04-findings-summary.ipynb    # 关键发现汇总
```

## 分析最佳实践

1. **先清洗后分析**：永远先跑`cleaner()`函数，移除测试数据和空回答
2. **编码者间信度**：两个编码者独立编码后计算Cohen's Kappa，>0.7为可接受
3. **保留原始数据**：清洗不覆盖原始CSV，另存`*_cleaned.csv`
4. **可视化先行**：先画分布图再做统计检验，避免数字误导
5. **Notebook可复现**：确保从顶部cell顺序运行能得到一致结果（Binder验证）

## 相关内容

- [分析工具函数源码解析](../references/analysis-utils-source.md)：完整工具函数源码
- [运行分析Notebook](../examples/03-run-analysis-notebook.md)：在Binder/本地运行分析
- [数据集目录](06-dataset-catalog.md)：各数据集的分析资源链接
- [Binder可复现性](09-binder-reproducibility.md)：确保notebook可复现运行
