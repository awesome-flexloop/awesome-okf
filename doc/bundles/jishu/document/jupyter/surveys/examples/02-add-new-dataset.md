---
type: Example
title: "添加新数据集"
description: "手把手教你向Jupyter Surveys添加一个新调查数据集：创建目录、添加CSV、编写index.md、匿名化检查、本地构建验证。"
tags: ["贡献", "新数据集", "pull-request", "匿名化", "教程"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
prerequisites:
  - 已完成本地构建环境配置
  - 有GitHub账号
  - 拥有调查数据并有权公开（CC0）
sources:
  - resource: "/concepts/08-contributing-data.md"
    description: "贡献新数据集概念文档"
  - resource: "/references/dataset-readme-source.md"
    description: "README模板解析"
---

# 添加新数据集

本示例手把手演示如何向Jupyter Surveys仓库贡献一个新的调查数据集。我们将以一个虚构的"2024年Jupyter AI使用调查"为例。

## 前置准备

确认你已完成[本地构建文档](01-build-docs-locally.md)中的环境配置。

## 步骤1：Fork并克隆仓库

```bash
# 1. 在GitHub上Fork jupyter/surveys
# 2. 克隆你的fork
git clone https://github.com/YOUR_USERNAME/surveys.git
cd surveys

# 3. 创建feature分支
git checkout -b add-2024-ai-survey
```

## 步骤2：创建数据集目录

按照命名规范创建目录：

```bash
mkdir surveys/2024-03-jupyter-ai-survey
cd surveys/2024-03-jupyter-ai-survey
```

## 步骤3：准备数据文件

将清洗后的CSV数据放入目录。确保CSV满足：

```
- UTF-8编码
- 列名使用snake_case
- 第一行为表头
- 无PII（个人识别信息）
```

示例CSV（`responses.csv`）：

```csv
id,usage_freq,ai_feature_used,satisfaction,feedback
1,daily,code_completion,4,Great for boilerplate code
2,weekly,code_explanation,3,Sometimes gives wrong answers
3,daily,both,5,Significantly improved productivity
4,monthly,none,2,Not sure how to use AI features
5,daily,code_completion,4,Needs better context awareness
```

## 步骤4：编写index.md

创建数据集入口文档：

```markdown
---
title: "Jupyter AI User Survey 2024"
description: "Survey on Jupyter AI extension usage patterns and user experience"
date: "2024-03"
license: CC0-1.0
---

# Jupyter AI User Survey 2024

## Overview

This survey was conducted in March 2024 to understand how Jupyter users
interact with AI-powered features (code completion, code explanation,
error diagnosis) in their notebook workflows.

- **Target audience**: Jupyter AI extension users
- **Collection period**: March 1-31, 2024
- **Responses**: 500 complete responses (after cleaning)
- **Method**: Online survey distributed via Jupyter Discourse and Twitter

## Data Files

| File | Description | Rows |
|------|-------------|------|
| `responses.csv` | Cleaned survey responses | 500 |

## Column Definitions

### responses.csv

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Anonymous respondent ID |
| `usage_freq` | categorical | Jupyter usage: daily/weekly/monthly/rarely |
| `ai_feature_used` | categorical | AI features used: code_completion/code_explanation/both/none |
| `satisfaction` | integer | Satisfaction rating: 1 (poor) to 5 (excellent) |
| `feedback` | text | Open-ended feedback about AI features |

## Analysis

Analysis notebook coming soon. Contributions welcome!

## Citation

If you use this dataset, please cite:
> Jupyter Community. (2024). Jupyter AI User Survey 2024 [Data set].
> https://github.com/jupyter/surveys
```

## 步骤5：匿名化检查

创建简单的检查脚本并运行：

```python
# check_pii.py
import pandas as pd
import re

df = pd.read_csv('responses.csv')

# 检查邮箱
for col in df.select_dtypes(include='object').columns:
    emails = df[col].str.contains(r'[\w.-]+@[\w.-]+\.\w+', na=False)
    if emails.any():
        print(f"WARNING: Possible emails in '{col}': {df[col][emails].tolist()}")

# 检查IP
for col in df.select_dtypes(include='object').columns:
    ips = df[col].str.contains(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', na=False)
    if ips.any():
        print(f"WARNING: Possible IPs in '{col}'")

# 人工检查自由文本
print("\n=== Free text responses (review manually) ===")
for idx, text in df['feedback'].items():
    print(f"[{idx}] {text}")

print("\nDone. Review the output above for PII.")
```

```bash
python check_pii.py
# 审查输出，确认无PII
rm check_pii.py  # 清理检查脚本
```

**人工审查清单**：
- [ ] 反馈文本中无真实姓名
- [ ] 无邮箱地址
- [ ] 无IP地址
- [ ] 无公司/机构名（如可识别）
- [ ] id是匿名编号（非邮箱哈希等）

## 步骤6：本地构建验证

回到仓库根目录：

```bash
cd ../../..

# 构建文档
nox -s docs

# 或启动live preview
nox -s docs-live
```

在浏览器中验证：
1. 首页"Survey Datasets"下出现新数据集
2. 点击进入，frontmatter（title/description/date）正确渲染
3. 表格正确显示
4. 无构建错误或警告

## 步骤7：提交PR

```bash
# 检查变更
git status
# 应该只显示 surveys/2024-03-jupyter-ai-survey/ 目录

# 添加文件（显式指定，不要git add .）
git add surveys/2024-03-jupyter-ai-survey/

# 提交
git commit -m "Add 2024-03 Jupyter AI user survey dataset"

# Push到你的fork
git push origin add-2024-ai-survey
```

在GitHub上创建Pull Request，描述中包含：
- 调查目的和背景
- 数据收集方法（在线调查、访谈等）
- 样本量和时间范围
- 匿名化确认（"All PII has been removed"）
- 许可证确认（CC0-1.0）

## 步骤8：响应审查

维护者可能会要求修改：
- 补充列定义
- 修复CSV格式问题
- 添加分析notebook
- 修改README措辞

根据反馈修改后，push到同一分支即可更新PR。

## 常见问题

### Q: 我的数据不是CSV格式怎么办？

目前仓库以CSV为主。如果是Excel/JSON等格式：
1. 转换为CSV（使用pandas: `df.to_csv('data.csv', index=False)`）
2. 或在PR中说明为什么需要其他格式

### Q: 我不能用CC0许可证怎么办？

CC0是仓库的默认和推荐许可证。如果你需要使用其他许可证：
1. 在数据集目录中添加自己的LICENSE文件
2. 在index.md的frontmatter中指定许可证
3. 在PR描述中说明原因

### Q: 数据可以放多大的CSV？

建议单个CSV不超过50MB（GitHub文件大小限制）。更大的数据集考虑：
- 压缩为CSV.gz
- 或托管在外部（Zenodo、Figshare等），仓库只放元数据和摘要

### Q: 我只有分析notebook没有原始数据？

也可以贡献！将notebook放在已有数据集的`notebooks/`目录下，更新该数据集的index.md添加链接。

## 相关内容

- [数据集组织规范](../concepts/03-dataset-conventions.md)：命名和结构标准
- [贡献新数据集](../concepts/08-contributing-data.md)：贡献流程的概念说明
- [数据集README模板](../references/dataset-readme-source.md)：index.md完整模板
- [本地构建文档](01-build-docs-locally.md)：构建环境配置
