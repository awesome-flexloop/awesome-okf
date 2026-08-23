---
type: concept
title: "数据集组织规范"
description: "Jupyter Surveys数据集的命名约定、README frontmatter、文件组织标准、匿名化规范和许可要求。"
tags: ["数据集", "命名规范", "frontmatter", "匿名化", "CC0"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2015-12-notebook-ux/index.md"
    description: "2015数据集README"
  - resource: "../../../../../../external/libs/jupyter/surveys/surveys/2023-05-jupyterlab-accessibility/index.md"
    description: "2023数据集README"
---

# 数据集组织规范

每个调查数据集在`surveys/`目录下以独立子目录存在，遵循统一的命名、结构和文档规范。

## 目录命名约定

```
YYYY-MM-topic-name/
```

| 部分 | 格式 | 说明 | 示例 |
|------|------|------|------|
| `YYYY` | 四位年份 | 调查执行年份 | `2018` |
| `MM` | 两位月份 | 调查执行月份 | `09` |
| `topic-name` | kebab-case | 调查主题的简短描述 | `jupytercon-2018` |

**命名原则**：
- 使用小写字母和连字符（kebab-case）
- 主题名简洁但具有描述性
- 月份使用调查开始的月份
- 避免使用版本号（v1, v2）

**示例**：
- ✅ `2016-05-education-survey/`
- ✅ `2022-08-notebooks-for-all/`
- ❌ `EducationSurvey/`（无日期、使用驼峰）
- ❌ `2018-9-jupytercon/`（月份没补零）

## 目录结构标准

```
YYYY-MM-topic-name/
├── index.md                 # 📋 必需：数据集README
├── *.csv                    # 📊 数据文件（原始/清洗/编码）
├── notebooks/               # 📓 可选：分析notebooks
│   └── *.ipynb
├── images/                  # 🖼️ 可选：图表和可视化
│   └── *.png
└── summary.md               # 📝 可选：分析摘要
```

### 文件说明

| 文件 | 必需 | 说明 |
|------|------|------|
| `index.md` | ✅ | 数据集入口文档，包含元数据、数据字典、分析链接 |
| `*.csv` | ✅ | 数据文件，UTF-8编码，逗号分隔 |
| `notebooks/*.ipynb` | ❌ | 分析notebooks，需在Binder中可运行 |
| `images/*.png` | ❌ | 静态图表，README中引用 |
| `summary.md` | ❌ | 关键发现摘要 |

## index.md 文档规范

每个数据集的`index.md`必须包含YAML frontmatter和以下标准章节。

### Frontmatter 必填字段

```yaml
---
title: "调查完整名称"
description: "一句话描述调查目的"
date: "YYYY-MM"
license: CC0-1.0
---
```

### 标准章节

1. **Overview**：调查背景、目标受众、回收量、执行方式
2. **Data Files**：数据文件清单（文件名、描述、行数）
3. **Column Definitions**：CSV列定义表格（列名、类型、描述、取值范围）
4. **Analysis**：分析notebooks和报告链接
5. **Citation**：引用格式（DOI如有）

完整模板见：[数据集README模板解析](../references/dataset-readme-source.md)

## 数据文件规范

### CSV格式要求

- **编码**：UTF-8（无BOM）
- **分隔符**：逗号（,）
- **引用**：双引号（"）包裹含特殊字符的字段
- **表头**：第一行为列名
- **缺失值**：空单元格（不使用NA、N/A、null等）

### 列命名规范

- 小写蛇形命名（snake_case）：`user_id`, `response_time`
- 问题列建议使用`qN_shortname`格式：`q1_usage_freq`, `q2_feedback`
- 元数据列使用描述性名称：`timestamp`, `user_id`

## 匿名化与隐私

### 必须移除的信息

| 类型 | 示例 |
|------|------|
| 直接标识 | 姓名、邮箱、用户名、IP地址 |
| 间接标识 | 精确地理位置（城市级以下）、精确时间戳（建议泛化到日期） |
| 自由文本PII | 回答中包含的人名、机构名（需人工审查） |

### 匿名化检查清单

提交新数据集前：
- [ ] CSV中无邮箱列（`@`符号扫描）
- [ ] CSV中无IP地址格式（正则`\d+\.\d+\.\d+\.\d+`）
- [ ] 自由文本列已人工审查，无识别信息
- [ ] 时间戳精度不高于小时级（如有跨日分析需求可保留日期）
- [ ] 任何人口统计数据组合不可识别到个体（小样本<10人的组需合并）

## 许可证

所有数据集默认使用**CC0 1.0 Universal**公共领域贡献。子目录可包含自己的LICENSE文件覆盖默认许可。

> ⚠️ **注意**：CC0意味着你明确放弃所有版权，将数据贡献给公共领域。提交数据前确认你有权这样做。

## 贡献检查清单

贡献新数据集前确认：
- [ ] 目录名遵循`YYYY-MM-topic-name/`格式
- [ ] 包含`index.md`且frontmatter完整
- [ ] CSV文件UTF-8编码，列名snake_case
- [ ] 所有PII已移除（通过匿名化检查清单）
- [ ] 数据使用CC0许可证
- [ ] 如有notebook，在Binder中可运行

## 相关内容

- [贡献新数据集](../examples/02-add-new-dataset.md)：实战教程
- [数据集README模板解析](../references/dataset-readme-source.md)：index.md完整模板
- [数据集目录](06-dataset-catalog.md)：现有数据集一览
