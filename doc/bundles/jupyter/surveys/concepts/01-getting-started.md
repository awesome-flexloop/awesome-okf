---
type: concept
title: "5分钟快速上手"
description: "三种使用Jupyter Surveys的方式：在线浏览文档站点、Binder零配置运行分析notebooks、本地克隆构建文档。"
tags: ["快速上手", "binder", "本地构建", "文档站点"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/README.md"
    lines: "1-47"
    description: "项目README"
  - resource: "../../../../../../external/libs/jupyter/surveys/binder/requirements.txt"
    description: "Binder环境依赖"
---

# 5分钟快速上手

根据你的需求，选择以下三种方式之一开始使用Jupyter Surveys：

## 方式一：在线浏览文档（30秒）

直接访问官方文档站点：

👉 **https://jupyter.github.io/surveys**

文档站点包含：
- 所有数据集的说明文档和数据字典
- 调查结果摘要和关键发现
- 分析notebook的HTML渲染版本

适合：只想浏览数据和分析结果的用户。

## 方式二：Binder运行分析Notebook（2分钟）

点击下方链接，在浏览器中直接打开Jupyter环境，零配置运行所有分析notebooks：

👉 **https://mybinder.org/v2/gh/jupyter/surveys/master**

Binder会自动：
1. 构建包含所有依赖的Docker环境
2. 启动Jupyter Notebook服务器
3. 你可以直接打开`surveys/`目录下的notebook运行

**注意**：Binder环境是临时的，修改不会保存。如需持久化，请在本地运行。

适合：想快速体验数据分析pipeline的用户。

## 方式三：本地克隆+构建文档（5分钟）

### 前置要求

- Python 3.8+
- Node.js 18+（mystmd需要）
- Git

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/jupyter/surveys.git
cd surveys

# 2. 安装nox（构建自动化工具）
pip install nox uv

# 3. 构建文档
nox -s docs

# 4. 打开构建结果
# 构建产物在 _build/html/ 目录
# 或启动实时预览服务器
nox -s docs-live
```

构建成功后，文档站点将在本地生成，你可以：
- 浏览所有数据集文档
- 运行Jupyter Notebook进行自定义分析
- 添加新的数据集

适合：需要深度分析、贡献数据或自定义构建的用户。

## 选择指南

| 需求 | 推荐方式 | 时间 |
|------|---------|------|
| 了解项目有什么数据 | 在线文档 | 30秒 |
| 跑一下分析notebook看看 | Binder | 2分钟 |
| 做自己的分析/贡献数据 | 本地克隆 | 5分钟 |

## 下一步

- 📁 [仓库结构](02-repository-structure.md)：了解本地克隆后的目录布局
- 🛠️ [本地构建文档](../examples/01-build-docs-locally.md)：详细的本地构建教程
- 📓 [运行分析Notebook](../examples/03-run-analysis-notebook.md)：Binder和本地运行notebook的详细步骤
