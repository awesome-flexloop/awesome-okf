---
type: Reference
title: "Sphinx 配置与构建基础设施信源"
description: "docs/conf.py、readthedocs.yml、docs/requirements.txt 和 docs/Makefile 的核心配置摘录。"
tags: [reference, sphinx, documentation, readthedocs, myst, build]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: conf-py
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/conf.py
    title: "docs/conf.py"
  - id: rtd-yml
    resource: https://github.com/jupyter-server/team-compass/blob/main/readthedocs.yml
    title: "readthedocs.yml"
  - id: requirements
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/requirements.txt
    title: "docs/requirements.txt"
---

## Sphinx 配置 (docs/conf.py)

- **扩展**：`sphinx.ext.mathjax`, `myst_parser`（支持 Markdown）
- **源文件后缀**：`.rst`, `.md`（MyST Markdown）
- **主文档**：`index`
- **项目信息**：project='Team Compass', copyright='2021, Jupyter Server', author='Jupyter Server Team', version='1.0'
- **HTML主题**：`sphinx_book_theme`，logo_only=True
- **Logo/Favicon**：`_static/logo.png`, `_static/favicon.png`
- **自定义CSS**：`_static/custom.css`（通过 setup(app) 函数注册）
- **构建钩子**：conf.py 末尾通过 subprocess 运行 `python scripts/gen_contributors.py`，在构建时自动生成贡献者表格

## Read the Docs 配置 (readthedocs.yml)

- **配置版本**：v2
- **构建OS**：ubuntu-22.04
- **Python版本**：3.12
- **Sphinx配置**：docs/conf.py
- **依赖安装**：docs/requirements.txt

## 构建依赖 (docs/requirements.txt)

```
sphinx>=3
sphinx_copybutton
sphinx_book_theme
pandas
ruamel.yaml
myst_parser
```

## Pre-commit 配置 (.pre-commit-config.yaml)

- 仅使用 `pre-commit-hooks` 的 `end-of-file-fixer` 钩子（rev: v6.0.0）
