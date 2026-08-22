---
type: concept
title: "贡献新数据集"
description: "如何向Jupyter Surveys贡献新的调查数据集：Fork→PR流程、README模板、数据匿名化检查清单、文件组织规范。"
tags: ["贡献", "pull-request", "fork", "数据集", "匿名化", "新数据"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/README.md"
    description: "项目README（贡献指南）"
---

# 贡献新数据集

Jupyter Surveys欢迎贡献新的Jupyter/IPython社区调查数据集。本文档介绍贡献流程和要求。

## 贡献流程概述

```
1. Fork仓库
2. 创建数据集目录（YYYY-MM-topic-name/）
3. 添加数据文件
4. 编写index.md文档
5. 匿名化检查
6. 本地验证构建
7. 提交Pull Request
```

## 步骤详解

### 步骤1：Fork仓库

1. 访问 https://github.com/jupyter/surveys
2. 点击右上角"Fork"按钮
3. Clone你的fork到本地：

```bash
git clone https://github.com/YOUR_USERNAME/surveys.git
cd surveys
```

### 步骤2：创建数据集目录

按照命名规范创建目录：

```bash
# 格式：YYYY-MM-topic-name/
mkdir surveys/2024-03-jupyter-ai-survey
cd surveys/2024-03-jupyter-ai-survey
```

命名规则详见：[数据集组织规范](03-dataset-conventions.md)

### 步骤3：添加数据文件

将数据文件放入目录：

```
surveys/2024-03-jupyter-ai-survey/
├── responses.csv          # 原始/清洗后的数据
├── codes.csv              # 编码结果（如有）
└── notebooks/             # 分析notebooks（可选）
    └── analysis.ipynb
```

**CSV格式要求**：
- UTF-8编码（无BOM）
- 第一行为列名（snake_case命名）
- 逗号分隔，双引号引用
- 缺失值为空单元格

### 步骤4：编写index.md

创建数据集入口文档，使用标准模板：

```markdown
---
title: "Jupyter AI User Survey 2024"
description: "Survey on Jupyter AI extension usage and experience"
date: "2024-03"
license: CC0-1.0
---

# Jupyter AI User Survey 2024

## Overview

This survey was conducted in March 2024 to understand...
- **Target audience**: Jupyter AI extension users
- **Collection period**: March 2024
- **Responses**: N complete responses

## Data Files

| File | Description |
|------|-------------|
| `responses.csv` | Cleaned survey responses |

## Column Definitions

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Anonymous respondent ID |
| ... | ... | ... |

## Analysis

- 📓 [Analysis Notebook](notebooks/analysis.ipynb)
```

完整模板见：[数据集README模板解析](../references/dataset-readme-source.md)

### 步骤5：匿名化检查（⚠️ 关键步骤）

提交前**必须**完成匿名化检查：

- [ ] **邮箱扫描**：CSV中无`@`符号（除非是公开的机构邮箱域）
- [ ] **IP地址扫描**：无`\d+\.\d+\.\d+\.\d+`格式的IP
- [ ] **自由文本审查**：逐行检查开放回答，移除人名、机构名等PII
- [ ] **时间泛化**：时间戳精确到日期即可（不需要秒级精度）
- [ ] **小样本组合**：人口统计交叉后<10人的组合需合并或泛化

**扫描脚本参考**：

```python
import pandas as pd
import re

df = pd.read_csv('responses.csv')

# 检查邮箱
for col in df.select_dtypes(include='object').columns:
    emails = df[col].str.contains(r'@\w+\.\w+', na=False)
    if emails.any():
        print(f"⚠️ Possible emails in column '{col}'")

# 检查IP
for col in df.select_dtypes(include='object').columns:
    ips = df[col].str.contains(r'\d+\.\d+\.\d+\.\d+', na=False)
    if ips.any():
        print(f"⚠️ Possible IPs in column '{col}'")
```

### 步骤6：本地验证构建

```bash
# 回到仓库根目录
cd ../../..

# 安装依赖并构建
pip install nox uv
nox -s docs

# 检查构建输出中没有警告
# 确认新数据集出现在导航中
```

如果有分析notebook，在Binder中验证可运行：
1. Push到你的fork
2. 访问 `https://mybinder.org/v2/gh/YOUR_USERNAME/surveys/BRANCH_NAME`
3. 打开notebook，确保所有cell顺序运行无错误

### 步骤7：提交Pull Request

```bash
git add surveys/2024-03-jupyter-ai-survey/
git commit -m "Add 2024-03 Jupyter AI survey dataset"
git push origin main
```

在GitHub上创建Pull Request，PR描述中包含：
- 调查的简要说明
- 数据收集方法
- 样本量
- 匿名化确认
- 任何特殊注意事项

## PR审查标准

维护者审查PR时会检查：

1. ✅ 目录命名正确
2. ✅ index.md frontmatter完整
3. ✅ CSV格式正确（UTF-8, 逗号分隔）
4. ✅ 匿名化完成（无PII）
5. ✅ CC0许可证声明
6. ✅ 本地构建无错误
7. ✅ Notebook可在Binder运行（如有）

## 不能贡献的内容

- 含个人识别信息（PII）的数据
- 未获受访者同意公开的数据
- 非CC0许可证的数据（除非有明确说明）
- 与Jupyter生态无关的调查
- 重复或已存在的数据集

## 添加分析Notebook到已有数据集

如果你对已有数据集做了新的分析，也可以贡献：

1. 在数据集目录下添加notebook文件
2. 更新index.md的Analysis部分添加链接
3. 确保notebook在Binder中可运行
4. 提交PR

## 相关内容

- [数据集组织规范](03-dataset-conventions.md)：命名和结构标准
- [添加新数据集](../examples/02-add-new-dataset.md)：手把手实战教程
- [Binder可复现性](09-binder-reproducibility.md)：确保notebook可运行
- [数据集README模板解析](../references/dataset-readme-source.md)：index.md完整模板
