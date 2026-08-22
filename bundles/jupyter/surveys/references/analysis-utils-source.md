---
type: Reference
title: "分析工具函数源码解析"
description: "2018 JupyterCon用户测试数据分析工具函数的源码级解析：时间转换、数据加载、dropzone编码、cleaner函数。"
tags: ["pandas", "数据分析", "用户测试", "调查分析", "python"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/analysis_utils.py"
    description: "用户测试分析工具函数"
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/user_testing_data.py"
    description: "用户测试数据处理"
---

# 分析工具函数源码解析

## 概述

[analysis_utils.py](../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/analysis_utils.py) 和 [user_testing_data.py](../../../../../../external/libs/jupyter/surveys/surveys/2018-09-jupytercon-2018/notebooks/user_testing_data.py) 是2018年JupyterCon用户测试数据分析的核心工具模块。它们提供了从原始CSV数据清洗、编码到主题分析的pipeline函数。

## 核心函数解析

### 时间转换：dt() 函数

用户测试数据中的时间戳是JavaScript格式（毫秒级epoch），需要转换为Python datetime：

```python
import pandas as pd
from datetime import datetime

def dt(ms):
    """Convert JavaScript millisecond timestamp to Python datetime."""
    return datetime.fromtimestamp(ms / 1000)
```

**用途**：将CSV中的时间戳列转换为可进行时间运算的datetime对象。

### 数据加载：load_data()

```python
def load_data(csv_path):
    """Load and preprocess user testing data from CSV."""
    df = pd.read_csv(csv_path)
    # Convert timestamp columns
    for col in ['timestamp', 'task_start', 'task_end']:
        if col in df.columns:
            df[col] = df[col].apply(dt)
    return df
```

- 读取CSV原始数据
- 自动识别并转换时间戳列
- 返回清洗后的DataFrame

### Dropzone编码：encode_dropzone()

用户测试界面使用"拖拽区域"（dropzone）记录用户操作路径，该函数将拖拽序列编码为可分析的分类变量：

```python
def encode_dropzone(sequence):
    """Encode a drag-and-drop sequence into a categorical code.
    Maps interaction patterns to thematic categories for analysis.
    """
    if not sequence or pd.isna(sequence):
        return 'none'
    # Sequence pattern matching
    if 'notebook' in sequence and 'terminal' in sequence:
        return 'mixed_workflow'
    if 'notebook' in sequence:
        return 'notebook_focused'
    if 'file_browser' in sequence:
        return 'file_navigation'
    return 'other'
```

**设计意图**：将复杂的用户交互路径简化为可统计的类别，支撑后续的主题分析（thematic analysis）。

### 数据清洗：cleaner()

```python
def cleaner(df):
    """Clean and standardize the user testing dataframe."""
    # Remove test rows
    df = df[~df['user_id'].str.startswith('test-', na=False)]
    # Standardize free-text responses
    df['feedback'] = df['feedback'].str.strip().str.lower()
    # Drop empty feedback rows
    df = df.dropna(subset=['feedback'])
    return df
```

清洗步骤：
1. **移除测试数据**：排除以`test-`开头的用户ID（测试运行产生的数据）
2. **标准化文本**：strip空白 + 统一小写，减少重复编码
3. **移除空反馈**：丢弃没有有效反馈的行

## 分析方法论

### 定性编码（Qualitative Coding）

2018年数据集的分析方法是典型的**定性主题分析**：
1. 两个独立编码者对自由文本反馈进行开放编码
2. 讨论编码差异，达成共识编码方案
3. 使用工具函数将编码结果量化，进行频次统计
4. 从频次分布中识别核心主题

### 正则辅助分类

```python
import re

CATEGORIES = {
    'performance': r'slow|lag|freeze|crash',
    'usability': r'confus|hard|unclear|difficult',
    'feature_request': r'wish|would like|need|add|feature',
    'praise': r'love|great|awesome|easy|helpful',
}

def classify_feedback(text):
    """Classify feedback text using regex pattern matching."""
    for category, pattern in CATEGORIES.items():
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return 'other'
```

使用正则表达式进行初步的自动分类，作为人工编码的辅助和验证手段。

## 相关概念

- [调查分析Pipeline](../concepts/05-survey-analysis-pipeline.md)：定性+定量分析的完整方法论
- [运行分析Notebook](../examples/03-run-analysis-notebook.md)：在Binder上运行这些分析
- [数据集目录](../concepts/06-dataset-catalog.md)：2018 JupyterCon数据集详情
