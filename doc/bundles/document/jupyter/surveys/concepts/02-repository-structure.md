---
type: concept
title: "仓库结构"
description: "Jupyter Surveys仓库的完整目录树解析：根目录文件、docs/文档目录、surveys/数据集目录、binder/配置、.github/workflows/CI配置。"
tags: ["仓库结构", "目录布局", "文件组织"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/README.md"
    description: "项目README"
---

# 仓库结构

Jupyter Surveys仓库采用**数据与文档共存**的结构设计——数据集、分析代码和文档源文件在同一个仓库中管理。

## 目录树总览

```
surveys/
├── README.md                    # 项目说明
├── LICENSE                      # CC0 1.0许可证
├── noxfile.py                   # Nox构建自动化脚本
├── pyproject.toml               # Python项目配置
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Pages部署工作流
├── binder/
│   └── requirements.txt         # Binder环境依赖
├── docs/
│   ├── myst.yml                 # MyST站点配置
│   ├── index.md                 # 文档首页
│   └── surveys/                 # 文档中的数据集索引
│       └── logo.png             # 站点Logo
└── surveys/                     # 📊 数据集根目录
    ├── 2015-12-notebook-ux/
    ├── 2016-05-education-survey/
    ├── 2018-09-jupytercon-2018/
    ├── 2020-12-jupyter-survey/
    ├── 2022-08-notebooks-for-all/
    └── 2023-05-jupyterlab-accessibility/
```

## 各目录职责

### 根目录文件

| 文件 | 职责 |
|------|------|
| `README.md` | 项目入口，说明仓库用途、构建方式、贡献指南 |
| `LICENSE` | CC0 1.0 Universal公共领域贡献声明 |
| `noxfile.py` | Nox任务定义（docs/docs-live两个session） |
| `pyproject.toml` | Python包配置，声明构建依赖 |

### `.github/workflows/` — CI/CD配置

包含GitHub Actions部署工作流`deploy.yml`：
- 触发条件：push到master分支
- 环境：Ubuntu + Node.js 20 + Python uv
- 构建命令：`nox -s docs`
- 部署目标：GitHub Pages（`jupyter.github.io/surveys`）

详见：[CI/CD与GitHub Pages部署](07-cicd-deployment.md)

### `binder/` — 可复现环境配置

`requirements.txt`定义了Binder运行所需的Python依赖（pandas、matplotlib、jupyter等）。当用户通过mybinder.org打开仓库时，Binder读取此文件自动构建环境。

详见：[Binder可复现性](09-binder-reproducibility.md)

### `docs/` — 文档源文件

| 文件/目录 | 职责 |
|----------|------|
| `myst.yml` | MyST站点配置（元数据、TOC、主题） |
| `index.md` | 文档首页 |
| `surveys/logo.png` | 站点Logo |

MyST的TOC使用glob模式自动发现`surveys/`下各数据集的`index.md`，无需手动注册。

详见：[MyST文档系统](04-myst-docs-system.md)

### `surveys/` — 数据集根目录

每个子目录是一个独立的数据集，遵循统一的命名约定：`YYYY-MM-topic-name/`。每个数据集目录内部结构：

```
surveys/YYYY-MM-topic-name/
├── index.md              # 数据集README（入口文档）
├── *.csv                 # 原始/清洗后的数据文件
├── notebooks/            # 分析notebooks（可选）
│   └── *.ipynb
└── images/               # 图表（可选）
    └── *.png
```

详见：[数据集组织规范](03-dataset-conventions.md)

## 设计理念

### 数据与文档共存

与传统的数据仓库（只放数据）和文档仓库（只放文档）不同，Jupyter Surveys将**原始数据**、**分析代码**、**文档站点**放在同一个Git仓库中，确保：
- 文档与数据版本同步
- 分析pipeline可复现
- 贡献者一站式修改数据+文档

### 约定优于配置

通过统一的命名规范（`YYYY-MM-topic-name/`）、目录结构和README模板，新增数据集无需修改任何配置文件——MyST的glob TOC和Nox的通用构建命令自动处理新内容。

## 下一步

- [数据集组织规范](03-dataset-conventions.md)：深入了解数据集目录的命名和组织标准
- [MyST文档系统](04-myst-docs-system.md)：了解文档如何从Markdown构建为站点
