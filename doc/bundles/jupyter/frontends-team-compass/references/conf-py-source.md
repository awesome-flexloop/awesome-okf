---
type: Reference
title: "文档构建配置信源"
description: "docs/conf.py、.readthedocs.yml、docs/requirements.txt 的信源登记，包含 Sphinx 构建设置、主题、依赖和自动化脚本。"
tags: [reference, source, sphinx, documentation, build]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:35:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: conf-py
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/conf.py
    title: "docs/conf.py"
  - id: rtd-yml
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/.readthedocs.yml
    title: ".readthedocs.yml"
  - id: requirements
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/requirements.txt
    title: "docs/requirements.txt"
  - id: gen-script
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/scripts/gen_contributors.py
    title: "docs/scripts/gen_contributors.py"
---

# 文档构建配置信源

**原始文件路径**：`docs/conf.py`、`.readthedocs.yml`、`docs/requirements.txt`、`docs/scripts/gen_contributors.py`

**内容摘要**：

文档使用 Sphinx 构建，托管在 ReadTheDocs。

## Sphinx 配置（conf.py）
- **扩展**：`sphinx.ext.mathjax`、`myst_parser`（支持 Markdown）
- **源文件后缀**：`.rst` 和 `.md`（MyST 解析 Markdown）
- **主题**：`sphinx_book_theme`，logo_only 模式
- **Logo/Favicon**：使用 `_static/logo.png` 和 `_static/favicon.png`
- **自定义CSS**：通过 `setup(app)` 添加 `custom.css`
- **项目信息**：project='Team Compass', version='1.0', copyright='2024, Jupyter Frontends'
- **构建钩子**：构建时自动执行 `python scripts/gen_contributors.py`

## ReadTheDocs 配置（.readthedocs.yml）
- **构建环境**：Ubuntu 22.04 + Python 3.11
- **Sphinx 配置**：`docs/conf.py`
- **依赖安装**：通过 `docs/requirements.txt`

## 文档依赖（requirements.txt）
- `sphinx>=3`
- `sphinx_copybutton`
- `sphinx_book_theme`
- `pandas`（供 gen_contributors.py 使用）
- `ruamel.yaml`（YAML 解析）
- `myst_parser`（Markdown 支持）

## 贡献者表格生成脚本（gen_contributors.py）
- 读取 `team/contributors.yaml`
- 使用 pandas DataFrame 和 ruamel.yaml 解析
- 生成 HTML 表格（每行4人，N_PER_ROW=4）
- 头像使用 GitHub avatar URL（?size=200）
- 输出到 `team/active.txt`（raw HTML，供 Sphinx `.. raw:: html` 指令使用）

**关键事实锚点**：
- F-007: Sphinx + sphinx_book_theme + myst_parser
- F-008: 支持 .rst 和 .md 双格式
- F-009: ReadTheDocs 构建环境 Ubuntu 22.04 + Python 3.11
- F-010: 文档构建依赖清单
- F-028: gen_contributors.py 自动生成 HTML 成员表格
