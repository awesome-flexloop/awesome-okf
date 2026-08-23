---
type: Concept
title: "文档构建基础设施"
description: "Jupyter Server Team Compass 文档的技术栈：Sphinx + MyST Markdown + sphinx-book-theme + Read the Docs 自动部署，以及构建时的贡献者表格自动生成。"
tags: [documentation, sphinx, myst, readthedocs, automation, build, contributors]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: conf-py
    resource: /references/conf-py-source.md
    title: "Sphinx 配置信源"
  - id: gen-contributors
    resource: /references/gen-contributors-source.md
    title: "贡献者表格生成脚本信源"
---

## 技术栈概览

Team Compass 文档采用标准的 Python 文档工具链：

| 组件 | 技术选择 | 作用 |
|------|---------|------|
| 文档引擎 | Sphinx (>=3) | 核心文档构建系统 |
| Markdown支持 | MyST Parser | 支持 Markdown 格式编写 |
| 主题 | sphinx-book-theme | 现代化的书籍风格主题 |
| 代码复制 | sphinx-copybutton | 代码块一键复制按钮 |
| 数据处理 | pandas | 贡献者数据处理 |
| YAML解析 | ruamel.yaml | 成员YAML文件解析 |
| 数学公式 | sphinx.ext.mathjax | 数学公式渲染（预留） |
| 托管平台 | Read the Docs | 自动构建和在线发布 |
| CI钩子 | pre-commit | 文件末尾换行符修复 |

## 文档源格式

文档支持两种源文件格式：
- **reStructuredText (.rst)**：Sphinx 原生格式，用于主 index 和 toctree 定义
- **Markdown (.md)**：通过 MyST Parser 支持，用于团队文档内容

这种双格式支持让团队成员可以用更熟悉的 Markdown 编写内容，同时保留 Sphinx 的 toctree 等高级功能在 RST 中使用。

## Sphinx 配置要点

### 核心配置（docs/conf.py）

```python
extensions = ['sphinx.ext.mathjax', 'myst_parser']
source_suffix = ['.rst', '.md']
master_doc = 'index'
html_theme = 'sphinx_book_theme'
html_theme_options = {"logo_only": True}
```

### 自定义静态资源

- **Logo**：`_static/logo.png`
- **Favicon**：`_static/favicon.png`
- **自定义CSS**：`_static/custom.css`（贡献者表格样式）

自定义 CSS 通过 `setup(app)` 函数注册：

```python
def setup(app):
    app.add_css_file("custom.css")
```

## 构建时自动化：贡献者表格生成

文档最有特色的技术机制是**构建时自动生成贡献者 HTML 表格**：

### 触发时机

在 `conf.py` 的末尾，通过 subprocess 调用生成脚本：

```python
import subprocess
subprocess.run(['python', 'scripts/gen_contributors.py'], check=True)
```

这意味着**每次 Sphinx 构建文档时**，都会重新运行脚本生成最新的贡献者表格。

### 数据流

```
┌─────────────────────────────────────┐
│ contributors-jupyter-server.yaml    │  ← 手动维护的数据源
│ (name/handle/affiliation/team/ssc)  │
└──────────────┬──────────────────────┘
               │ ruamel.yaml 解析
               ▼
┌─────────────────────────────────────┐
│ pandas DataFrame                    │
│ (按team字段筛选active/inactive)     │
└──────────────┬──────────────────────┘
               │ _generate_contributors()
               ▼
┌─────────────────────────────────────┐
│ HTML 表格（每行4人）                  │
│ - 头像从GitHub动态获取               │
│ - 包含姓名链接和机构信息             │
└──────────────┬──────────────────────┘
               │ 包装为 reST raw:: html
               ▼
┌─────────────────────────────────────┐
│ active.txt / inactive.txt           │  ← 构建产物
│ ssc-current.txt / ssc-past.txt      │
└─────────────────────────────────────┘
               │ .. include:: 指令嵌入
               ▼
┌─────────────────────────────────────┐
│ team.md 最终页面                     │
└─────────────────────────────────────┘
```

### 生成脚本核心逻辑

脚本使用以下关键技术：
- **GitHub头像URL模式**：`https://github.com/{handle}.png?size=200` 不需要API认证
- **每行4人布局**：通过 `N_PER_ROW = 4` 和 `ix % N_PER_ROW` 控制换行
- **SSC现任判断**：检查最后一个任期是否以 `-` 结尾（无结束日期=现任）
- **reST raw指令**：生成 `.. raw:: html` 块将HTML嵌入Sphinx文档

这种自动化确保了成员列表始终与YAML数据源同步，避免手动维护HTML导致的过期问题。

## Read the Docs 自动部署

Read the Docs 配置文件（`.readthedocs.yml`）定义了云端构建设置：

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.12"
sphinx:
  configuration: docs/conf.py
python:
  install:
    - requirements: docs/requirements.txt
```

每次推送到 main 分支时，Read the Docs 会自动：
1. 创建 Ubuntu 22.04 构建环境
2. 安装 Python 3.12 和文档依赖
3. 运行 Sphinx 构建（触发 gen_contributors.py）
4. 发布到 `jupyter-server-team-compass.readthedocs.io`

## Pre-commit 钩子

仓库配置了简单但实用的 pre-commit 钩子：

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
```

`end-of-file-fixer` 确保所有文件以换行符结尾，这是 POSIX 标准要求，避免 "No newline at end of file" 警告。

## 本地构建

```bash
# 安装依赖
pip install -r docs/requirements.txt

# 构建HTML
cd docs && make html

# 或使用 Sphinx 直接构建
sphinx-build -b html docs docs/_build/html
```

## 设计理念

这套文档基础设施体现了几个设计选择：
1. **简单优先**：只用必要的Sphinx扩展，不引入复杂的自定义主题
2. **数据驱动**：成员信息存储在YAML中，展示代码自动生成，避免重复维护
3. **双格式友好**：支持RST和Markdown，降低贡献门槛
4. **自动部署**：RTD集成让文档始终与代码同步
5. **轻量CI**：仅一个pre-commit钩子，不过度工程化

## 相关概念

- [Jupyter Server Team Compass 仓库简介](/concepts/00-introduction.md)
- [团队成员体系](/concepts/01-team-membership.md)
